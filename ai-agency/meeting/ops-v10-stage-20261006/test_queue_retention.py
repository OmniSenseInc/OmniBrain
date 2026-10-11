"""Keep consented reviews available when a client starts a new consultation."""
import json
import tempfile
import unittest
from pathlib import Path

from consultation_gateway import ACTOR, Store
from workflow_agency import read_case


class QueueRetentionTests(unittest.TestCase):
    def setUp(self):
        runs = Path(__file__).resolve().parents[1] / 'test-runs'
        runs.mkdir(exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=runs)
        self.addCleanup(self.tmp.cleanup)
        self.now = 1800000000
        self.sequence = 0
        self.requests = 0
        self.store = Store(Path(self.tmp.name) / 'data', clock=lambda: self.now)
        for text in ('/mulai', 'setuju', 'Stok gudang berbeda dari catatan penjualan.',
                     'Tolong kirim ringkasan ke tim', 'ya'):
            self.send(text)
        row = self.store.active('client', 'chat')
        self.previous = row['id']
        self.payload = json.loads(row['body'])['payload']

    def send(self, text):
        self.sequence += 1
        self.now += 8
        return self.store.receive('client', 'chat', str(self.sequence), text)

    def claim_new(self):
        self.requests += 1
        ticket = self.store.create(self.payload, True, 'synthetic-browser',
                                   'synthetic_request_' + str(self.requests))
        self.send(ticket['claim_code'])
        return ticket

    def job(self, ticket=None):
        with self.store.db() as connection:
            return dict(connection.execute('SELECT * FROM review_sync_jobs WHERE ticket=?',
                                           (ticket or self.previous,)).fetchone())

    def test_new_claim_before_sync_keeps_review_and_finishes_job(self):
        current = self.claim_new()
        self.assertEqual(self.store.active('client', 'chat')['id'], current['case_id'])
        queue = self.store.queue()
        self.assertEqual([(row['case_id'], row['status']) for row in queue],
                         [(self.previous, 'queued_previous')])
        self.assertEqual(self.job()['status'], 'pending')
        self.assertEqual(self.store.retry_review_sync()['done'], 1)
        self.assertEqual(self.job()['status'], 'done')
        record = read_case(self.store.root / 'pipeline.sqlite3', 'WA-client', self.previous, ACTOR)
        self.assertEqual(record['stage'], 'intake')

    def test_new_claim_after_sync_keeps_review_idempotent(self):
        initial = self.store.import_intake(self.previous)
        self.claim_new()
        self.assertEqual(self.store.queue()[0]['status'], 'queued_previous')
        result = self.store.import_intake(self.previous)
        self.assertTrue(result['idempotent'])
        self.assertEqual(result['case']['revision'], initial['case']['revision'])
        self.assertEqual(self.job()['status'], 'done')

    def test_deleting_new_case_never_reactivates_previous_review(self):
        current = self.claim_new()
        self.assertEqual(self.send('/hapus')['ticket'], None)
        self.assertIsNone(self.store.active('client', 'chat'))
        reply = self.send('/hasil')
        self.assertIsNone(reply['ticket'])
        self.assertNotIn(self.previous, reply['text'])
        self.assertNotIn(current['case_id'], reply['text'])
        self.assertEqual(self.store.queue()[0]['case_id'], self.previous)
        self.assertEqual(self.store.retry_review_sync()['done'], 1)

    def test_more_new_claims_preserve_all_previously_consented_reviews(self):
        second = self.claim_new()
        self.send('Tolong kirim ringkasan ke tim')
        self.send('ya')
        third = self.claim_new()
        queue = self.store.queue()
        self.assertEqual({row['case_id'] for row in queue},
                         {self.previous, second['case_id']})
        self.assertEqual({row['status'] for row in queue}, {'queued_previous'})
        self.assertEqual(self.store.active('client', 'chat')['id'], third['case_id'])
        self.assertEqual(self.store.retry_review_sync()['done'], 2)
        self.assertEqual(self.job()['status'], 'done')
        self.assertEqual(self.job(second['case_id'])['status'], 'done')

    def test_previous_claim_code_cannot_reopen_queued_review(self):
        second = self.claim_new()
        self.send('Tolong kirim ringkasan ke tim')
        self.send('ya')
        third = self.claim_new()
        reply = self.send(second['claim_code'])
        self.assertIsNone(reply['ticket'])
        self.assertIn('Kode tidak tersedia', reply['text'])
        self.assertEqual(self.store.active('client', 'chat')['id'], third['case_id'])


if __name__ == '__main__':
    unittest.main()
