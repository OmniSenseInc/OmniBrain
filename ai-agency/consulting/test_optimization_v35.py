import concurrent.futures
import json
import tempfile
import unittest
from pathlib import Path
from consultation_gateway import Store
from test_consultation_gateway import fixture

class FlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.now=1800000000
        self.root=Path(self.tmp.name)/'data';self.store=Store(self.root,clock=lambda:self.now);self.n=0
    def tearDown(self):self.tmp.cleanup()
    def send(self,text,principal='P',chat='chat'):
        self.n+=1;self.now+=7
        return self.store.receive(principal,chat,'m'+str(self.n),text)
    def claim(self):
        p=fixture(self.store.bank);p['context']={'process':'Laporan mingguan','problem':'Pencatatan berulang','process_owner':''}
        self.ticket=self.store.create(p,True,'browser','a'*32);self.send(self.ticket['claim_code'])
    def finish(self):
        for i in range(6):self.send('Operator memeriksa dan mencocokkan laporan '+str(i))
    def test_paused_confirmation_resumes_same_stage_and_imports_once(self):
        self.claim();self.finish();self.send('/stop');self.send('/stop');self.send('/lanjut')
        self.assertEqual(self.store.active('P','chat')['status'],'awaiting_confirmation')
        self.assertEqual(self.store.active('P','chat')['cursor'],6)
        reply=self.send('ya');self.assertTrue(reply['import_intake'])
        first=self.store.import_intake(self.ticket['case_id']);second=self.store.import_intake(self.ticket['case_id'])
        self.assertEqual(first['case']['revision'],second['case']['revision'])
        self.send('/stop');self.send('/lanjut');self.assertEqual(self.store.active('P','chat')['status'],'ready_for_team')
        self.send('/lanjut');self.assertEqual(self.store.active('P','chat')['status'],'ready_for_team')
    def test_legacy_paused_confirmation_recovers_without_stage_hint(self):
        self.claim();self.finish()
        with self.store.db() as c:c.execute("UPDATE tickets SET status='paused' WHERE id=?",(self.ticket['case_id'],))
        self.send('/lanjut');self.assertEqual(self.store.active('P','chat')['status'],'awaiting_confirmation')
    def test_direct_conversation_requires_offer_then_consent_and_no_fake_score(self):
        self.send('[OMNISENSE-MULAI]');self.assertIsNone(self.store.active('P','chat'))
        self.send('Halo saya ingin konsultasi');self.assertIsNone(self.store.active('P','chat'))
        self.send('/setuju');self.assertEqual(self.store.active('P','chat')['status'],'discovery')
        self.assertEqual(json.loads(self.store.active('P','chat')['body'])['consent']['source'],'direct_whatsapp')
        self.assertNotIn('/100',self.send('/hasil')['text'])
        self.send('Pesanan sering hilang sebelum dicatat ke gudang')
        for i in range(5):self.send('Operator memeriksa pesanan '+str(i))
        self.assertEqual(self.store.active('P','chat')['status'],'awaiting_confirmation')
        self.send('ya');result=self.store.import_intake(self.store.active('P','chat')['id'])
        self.assertIn('Pesanan sering hilang',result['case']['data']['scope']['problem'])
        self.assertEqual(result['case']['stage'],'intake');self.assertNotIn('approvals',result['case']['data'])
    def test_consent_offer_is_chat_scoped_and_expires(self):
        self.send('/mulai');self.send('/setuju',chat='other');self.assertIsNone(self.store.active('P','other'))
        self.now+=86401;self.send('/setuju');self.assertIsNone(self.store.active('P','chat'))
    def test_budget_is_atomic_persistent_and_deleted_with_case(self):
        self.claim();ticket=self.ticket['case_id']
        with concurrent.futures.ThreadPoolExecutor(8) as pool:
            reservations=list(pool.map(lambda i:self.store.reserve_model_call(ticket,str(i)),range(24)))
        self.assertEqual(sum(reservations),16)
        new=Store(self.root,clock=lambda:self.now);self.assertFalse(new.reserve_model_call(ticket,'restart'))
        self.assertFalse(new.reserve_model_call(ticket,'0'))
        summary=new.operation_summary();self.assertEqual(summary['model_calls']['reserved'],16)
        self.assertNotIn('P',json.dumps(summary));self.assertNotIn(ticket,json.dumps(summary))
        self.send('/hapus')
        with new.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM model_calls').fetchone()[0],0)
    def test_correction_alias_does_not_advance_discovery(self):
        self.claim();r=self.send('Ralat, yang bermasalah pesanan bukan laporan')
        self.assertEqual(r['intent'],'correction');self.assertEqual(self.store.active('P','chat')['cursor'],0)
        self.assertTrue(json.loads(self.store.active('P','chat')['body'])['scope_review_required'])

    def test_http_retry_keeps_remaining_token_lifetime(self):
        p=fixture(self.store.bank);first=self.store.create(p,True,'browser','b'*32)
        self.now+=600;second=self.store.create(p,True,'browser','b'*32)
        self.assertEqual(first['case_id'],second['case_id']);self.assertEqual(second['expires_in'],6600)

    def test_direct_marker_does_not_overwrite_existing_discovery(self):
        self.claim();r=self.send('[OMNISENSE-MULAI]')
        self.assertIn('masih memiliki',r['text']);self.assertEqual(self.store.active('P','chat')['cursor'],0)
        self.assertEqual(json.loads(self.store.active('P','chat')['body'])['discovery'],{})

if __name__=='__main__':unittest.main()
