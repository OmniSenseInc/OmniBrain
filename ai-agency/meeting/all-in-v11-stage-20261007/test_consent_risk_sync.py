"""Local synthetic cases: permission review, deletion ordering and retry CAS."""
import copy
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

import consultation_gateway as gateway
from consultation_gateway import ACTOR, Store
from workflow_agency import apply_event, gate, read_case, transition


class ConsentRiskSyncTests(unittest.TestCase):
    def setUp(self):
        runs=Path(__file__).resolve().parents[1]/'test-runs'
        runs.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=runs)
        self.addCleanup(self.tmp.cleanup)
        self.now=1800000000
        self.seq=0
        self.store=Store(Path(self.tmp.name)/'data',clock=lambda:self.now)
        self.send('/mulai');self.send('setuju')
        self.ticket=self.store.active('client','chat')['id']
        self.path=self.store.root/'pipeline.sqlite3'

    def send(self,text):
        self.seq+=1;self.now+=8
        return self.store.receive('client','chat',str(self.seq),text)

    def consent(self):
        self.send('Tolong kirim ringkasan ke tim');self.send('ya')

    def case(self):
        return read_case(self.path,'WA-client',self.ticket,ACTOR)

    def job(self):
        with self.store.db() as c:
            row=c.execute('SELECT * FROM review_sync_jobs WHERE ticket=?',(self.ticket,)).fetchone()
        return dict(row) if row else None

    def risk_record(self):
        return {'tenant_id':'T','case_id':'C','stage':'discovery','revision':2,'scope_version':1,
                'data':{'latest_client_snapshot':{'risk_hold':True,'fingerprint':'current'},
                        'client_update_review':{'pending':True,'fingerprint':'current','source_ref':'gateway-case:C'}}}

    def review_event(self,permission=True):
        review={'pending':False,'fingerprint':'current','source_ref':'review:1','reviewed_by':'reviewer','reason':'Evidence checked'}
        if permission:review['permission_evidence_ref']='permission-record:1'
        return {'expected_revision':2,'action':'update','data':{'client_update_review':review}}

    def test_initial_permission_hold_enters_review_queue_and_ledger_hold(self):
        self.send('Saya belum punya izin menggunakan datanya.')
        self.assertEqual(self.store.active('client','chat')['status'],'risk_review')
        self.consent();self.store.import_intake(self.ticket)
        case=self.case()
        self.assertEqual(case['stage'],'intake')
        self.assertTrue(case['context']['client_update_review']['pending'])
        self.assertTrue(case['context']['latest_client_snapshot']['risk_hold'])
        record={'data':case['context']}
        gate(record,'discovery',self.store.bank)
        with self.assertRaises(ValueError):gate(record,'diagnosis',self.store.bank)

    def test_initial_correction_requires_review_without_scope_overwrite(self):
        self.send('Koreksi, kendalanya penjualan, bukan stok.')
        self.consent();self.store.import_intake(self.ticket)
        case=self.case()
        self.assertTrue(case['context']['client_update_review']['pending'])
        self.assertIn('penjualan',str(case['context']['latest_client_snapshot']['corrections']))

    def test_paused_permission_hold_can_resume_for_human_handoff(self):
        self.send('Saya belum punya izin menggunakan datanya.')
        self.send('cukup dulu')
        self.assertEqual(self.store.active('client','chat')['status'],'paused')
        reply=self.send('lanjut')
        self.assertIn('review manusia',reply['text'])
        self.assertEqual(self.store.active('client','chat')['status'],'paused')
        self.assertTrue(json.loads(self.store.active('client','chat')['body'])['risk_hold'])
        self.consent();self.store.import_intake(self.ticket)
        self.assertTrue(self.case()['context']['client_update_review']['pending'])

    def test_unreviewed_legacy_risk_snapshot_also_blocks_decisions(self):
        record=self.risk_record();record['data'].pop('client_update_review')
        for target in ('diagnosis','options','proposal','pilot','delivery'):
            with self.subTest(target=target),self.assertRaises(ValueError):gate(record,target,self.store.bank)

    def test_team_requires_permission_evidence_to_clear_risk_review(self):
        record=self.risk_record()
        with self.assertRaises(ValueError):transition(record,self.review_event(False),{'id':'reviewer','role':'team'},self.store.bank)
        resolved=transition(record,self.review_event(),{'id':'reviewer','role':'team'},self.store.bank)
        # This only removes the review hold; ordinary stage evidence remains required.
        with self.assertRaisesRegex(ValueError,'Belum lengkap'):gate(resolved,'diagnosis',self.store.bank)

    def test_clearing_already_resolved_review_still_requires_team(self):
        record=transition(self.risk_record(),self.review_event(),{'id':'reviewer','role':'team'},self.store.bank)
        event=self.review_event();event['expected_revision']=record['revision']
        with self.assertRaises(ValueError):transition(record,event,ACTOR,self.store.bank)

    def test_stale_permission_evidence_does_not_resolve_new_snapshot(self):
        record=self.risk_record();record['data']['latest_client_snapshot']['fingerprint']='new'
        with self.assertRaises(ValueError):transition(record,self.review_event(),{'id':'reviewer','role':'team'},self.store.bank)

    def test_resuming_deferred_delivery_cannot_skip_permission_hold(self):
        record=self.risk_record();record['stage']='deferred';record['resume_stage']='delivery'
        record['data']['client_update_review']['pending']=False
        with self.assertRaises(ValueError):transition(record,{'expected_revision':2,'action':'resume'},ACTOR,self.store.bank)
        record['resume_stage']='discovery'
        self.assertEqual(transition(record,{'expected_revision':2,'action':'resume'},ACTOR,self.store.bank)['stage'],'discovery')

    def test_failed_old_job_does_not_delay_new_client_correction(self):
        self.consent();generation=self.job()['generation']
        def old_failure(_):
            self.send('Koreksi, penjualan cabang kedua yang terlambat.')
            raise OSError('old worker failure')
        with patch.object(self.store,'import_intake',side_effect=old_failure):self.store.retry_review_sync()
        job=self.job()
        self.assertGreater(job['generation'],generation)
        self.assertEqual(job['attempts'],0)
        self.assertEqual(job['next_attempt'],0)
        self.assertIsNone(job['last_error_type'])
        self.assertEqual(self.store.retry_review_sync()['done'],1)

    def test_delete_then_worker_never_creates_team_copy(self):
        self.consent();self.send('/hapus')
        with self.assertRaises(ValueError):self.store.import_intake(self.ticket)
        self.assertFalse(self.path.exists())
        self.assertIsNone(self.job())

    def test_delete_waits_for_inflight_sync_then_leaves_no_gateway_recreation(self):
        self.consent()
        snapshot=threading.Event();release=threading.Event();deleted=threading.Event()
        errors=[];actual=gateway.apply_event
        def pause(*args,**kwargs):
            if not snapshot.is_set():
                snapshot.set()
                if not release.wait(8):raise TimeoutError('synthetic release')
            return actual(*args,**kwargs)
        def sync():
            try:self.store.import_intake(self.ticket)
            except Exception as exc:errors.append(exc)
        def delete():
            try:self.send('/hapus');deleted.set()
            except Exception as exc:errors.append(exc)
        worker=threading.Thread(target=sync);remover=threading.Thread(target=delete)
        try:
            with patch.object(gateway,'apply_event',side_effect=pause):
                worker.start();self.assertTrue(snapshot.wait(3));remover.start()
                self.assertFalse(deleted.wait(.15))
                release.set();worker.join(5);remover.join(5)
        finally:
            release.set()
            for t in (worker,remover):
                if t.ident:t.join(10)
        self.assertEqual(errors,[]);self.assertTrue(deleted.is_set())
        self.assertIsNone(self.store.active('client','chat'));self.assertIsNone(self.job())
        # /hapus explicitly concerns the gateway. Existing team review is not destroyed.
        self.assertTrue(self.case()['found'])
        with self.assertRaises(ValueError):self.store.import_intake(self.ticket)

    def test_retention_cleanup_finishes_without_reviving_review(self):
        self.consent();self.now+=31*86400;self.store.cleanup()
        self.assertIsNone(self.job())
        with self.assertRaises(ValueError):self.store.import_intake(self.ticket)


if __name__=='__main__':unittest.main()
