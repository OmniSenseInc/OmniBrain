"""Synthetic, local-only regressions for concurrent review synchronization."""
import json
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import consultation_gateway as gateway
from consultation_gateway import ACTOR, Store
from workflow_agency import read_case


class SyncRaceTests(unittest.TestCase):
    def setUp(self):
        runs = Path(__file__).resolve().parents[1] / 'test-runs'
        runs.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=runs)
        self.addCleanup(self.tmp.cleanup)
        self.now = 1800000000
        self.sequence = 0
        self.store = Store(Path(self.tmp.name) / 'data', clock=lambda: self.now)
        for text in ('/mulai', 'setuju', 'Stok gudang berbeda dari catatan penjualan.',
                     'Tolong kirim ringkasan ke tim', 'ya'):
            self.send(text)
        self.ticket = self.store.active('client', 'chat')['id']
        self.store.import_intake(self.ticket)

    def send(self, text):
        self.sequence += 1
        self.now += 8
        return self.store.receive('client', 'chat', str(self.sequence), text)

    def case(self):
        return read_case(self.store.root / 'pipeline.sqlite3', 'WA-client', self.ticket, ACTOR)

    def job(self):
        with self.store.db() as connection:
            return dict(connection.execute('SELECT * FROM review_sync_jobs WHERE ticket=?',
                                           (self.ticket,)).fetchone())

    def test_other_process_cannot_commit_before_older_worker_finishes(self):
        self.send('Koreksi, stok gudang kedua juga berbeda.')
        old_snapshot_ready = threading.Event()
        release_old_worker = threading.Event()
        errors = []
        actual = gateway.apply_event

        def pause_before_commit(*args, **kwargs):
            if args[3]['action'] == 'update' and not old_snapshot_ready.is_set():
                old_snapshot_ready.set()
                if not release_old_worker.wait(12):
                    raise TimeoutError('synthetic worker release timeout')
            return actual(*args, **kwargs)

        def old_worker():
            try:
                self.store.import_intake(self.ticket)
            except Exception as exc:
                errors.append(exc)

        marker = Path(self.tmp.name) / 'attempted'
        worker = None
        thread = threading.Thread(target=old_worker)
        try:
            with patch.object(gateway, 'apply_event', side_effect=pause_before_commit):
                thread.start()
                self.assertTrue(old_snapshot_ready.wait(5))
                self.send('Koreksi, masalah utama sekarang penjualan dari cabang ketiga.')
                worker = subprocess.Popen(
                    [sys.executable, str(Path(__file__).resolve()), '--child-sync',
                     str(self.store.root), self.ticket, str(marker)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                deadline = time.monotonic() + 8
                while not marker.exists() and worker.poll() is None and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertTrue(marker.exists(), 'second process did not start synchronization')
                # The second process has entered import_intake and must wait for
                # the older snapshot's full transaction, not just its final CAS.
                time.sleep(0.15)
                self.assertIsNone(worker.poll(), 'newer worker committed while old worker held the lock')
                release_old_worker.set()
                thread.join(6)
                self.assertFalse(thread.is_alive())
                self.assertEqual(errors, [])
                stdout, stderr = worker.communicate(timeout=8)
                self.assertEqual(worker.returncode, 0, stdout + stderr)
        finally:
            release_old_worker.set()
            if thread.ident is not None:
                thread.join(15)
            if worker is not None and worker.poll() is None:
                worker.kill()
                worker.communicate()
        snapshot = self.case()['context']['latest_client_snapshot']
        self.assertIn('cabang ketiga', snapshot['corrections'][-1]['text'])
        self.assertEqual(self.job()['status'], 'done')

    def test_incoming_update_remains_pending_during_old_sync(self):
        self.send('Koreksi, stok gudang kedua juga berbeda.')
        actual = gateway.apply_event
        changed = False

        def receive_new_generation(*args, **kwargs):
            nonlocal changed
            result = actual(*args, **kwargs)
            if not changed:
                changed = True
                self.send('Koreksi, masalah utama sekarang penjualan dari cabang ketiga.')
            return result

        with patch.object(gateway, 'apply_event', side_effect=receive_new_generation):
            self.store.import_intake(self.ticket)
        self.assertEqual(self.job()['status'], 'pending')
        self.store.import_intake(self.ticket)
        self.assertIn('cabang ketiga', self.case()['context']['latest_client_snapshot']['corrections'][-1]['text'])
        self.assertEqual(self.job()['status'], 'done')

    def test_failed_sync_releases_interprocess_lock(self):
        self.send('Koreksi, stok gudang kedua juga berbeda.')
        with patch.object(gateway, 'apply_event', side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):
                self.store.import_intake(self.ticket)
        Store(self.store.root, clock=lambda: self.now).import_intake(self.ticket)
        self.assertEqual(self.job()['status'], 'done')


if __name__ == '__main__':
    if len(sys.argv) == 5 and sys.argv[1] == '--child-sync':
        store = Store(Path(sys.argv[2]))
        Path(sys.argv[4]).write_text('attempting', encoding='utf-8')
        store.import_intake(sys.argv[3])
        print(json.dumps({'synced': True}))
    else:
        unittest.main()
