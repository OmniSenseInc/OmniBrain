import tempfile,unittest,json,copy
from pathlib import Path
from unittest.mock import patch
from consultation_gateway import Store,ACTOR
from workflow_agency import read_case,transition,gate

class ReviewSyncTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.now=[1800000000];self.s=Store(Path(self.tmp.name)/'data',clock=lambda:self.now[0]);self.n=0
  self.send('/mulai');self.send('setuju');self.send('Stok gudang berbeda dari catatan penjualan.');self.send('Tolong kirim ringkasan ke tim');self.send('ya');self.t=self.s.active('client','chat')['id'];self.tenant='WA-client';self.path=self.s.root/'pipeline.sqlite3'
 def send(self,text):
  self.n+=1;self.now[0]+=8;return self.s.receive('client','chat','m'+str(self.n),text)
 def case(self):return read_case(self.path,self.tenant,self.t,ACTOR)
 def job(self):
  with self.s.db() as c:return dict(c.execute('SELECT * FROM review_sync_jobs WHERE ticket=?',(self.t,)).fetchone())
 def test_initial_sync_is_durable_idempotent_and_no_approval(self):
  self.assertEqual(self.job()['status'],'pending');self.s.import_intake(self.t);rev=self.case()['revision'];self.s.import_intake(self.t)
  self.assertEqual(self.case()['revision'],rev);self.assertEqual(self.job()['status'],'done');self.assertEqual(self.case()['recorded_approval_parties']['pilot'],[])
 def test_correction_arrives_without_overwriting_formal_scope(self):
  self.s.import_intake(self.t);old=self.case()['context']['scope'];r=self.send('Koreksi, kendalanya sekarang pada tindak lanjut penjualan.')
  self.assertTrue(r['import_intake']);self.s.import_intake(self.t);record=self.case()
  self.assertEqual(record['context']['scope'],old);self.assertTrue(record['context']['client_update_review']['pending']);self.assertIn('penjualan',str(record['context']['latest_client_snapshot']['corrections']))
 def test_new_information_after_confirmation_is_not_waiting_for_old_consent(self):
  self.s.import_intake(self.t);r=self.send('Tambahan, ada gudang kedua yang mencatat terpisah.')
  self.assertIn('Tambahan',r['text']);self.assertTrue(r['import_intake']);self.s.import_intake(self.t);self.assertIn('gudang kedua',str(self.case()['context']['latest_client_snapshot']['updates']))
 def test_permission_hold_reaches_reviewer_after_confirmation(self):
  self.s.import_intake(self.t);r=self.send('Saya belum punya izin. Bagaimana solusinya?');self.assertTrue(r['import_intake']);self.s.import_intake(self.t)
  self.assertTrue(self.case()['context']['latest_client_snapshot']['risk_hold']);self.assertEqual(self.s.active('client','chat')['status'],'ready_for_team')
 def test_worker_recovers_failure_without_sending_chat(self):
  with patch.object(self.s,'import_intake',side_effect=OSError('synthetic')):r=self.s.retry_review_sync()
  self.assertEqual(r['retry_pending'],1);self.assertEqual(self.job()['last_error_type'],'OSError');self.assertFalse(r['chat_messages_sent'])
  self.now[0]+=901;s=Store(self.s.root,clock=lambda:self.now[0]);self.assertEqual(s.retry_review_sync()['done'],1);self.assertEqual(self.case()['stage'],'intake')
 def test_partial_initial_commit_is_recovered(self):
  import consultation_gateway as module
  actual=module.apply_event
  def fail_advance(*args,**kw):
   if args[3]['action']=='advance':raise OSError('simulate crash after first commit')
   return actual(*args,**kw)
  with patch.object(module,'apply_event',side_effect=fail_advance):
   with self.assertRaises(OSError):self.s.import_intake(self.t)
  self.assertEqual(self.case()['stage'],'lead');self.s.import_intake(self.t);self.assertEqual(self.case()['stage'],'intake')
 def test_newer_job_is_not_cleared_by_old_processing(self):
  import consultation_gateway as module
  actual=module.apply_event;trigger=[False]
  def race(*args,**kw):
   result=actual(*args,**kw)
   if not trigger[0]:trigger[0]=True;self.send('Koreksi, stok gudang kedua juga berbeda.')
   return result
  with patch.object(module,'apply_event',side_effect=race):self.s.import_intake(self.t)
  self.assertEqual(self.job()['status'],'pending');self.s.import_intake(self.t);self.assertEqual(self.job()['status'],'done');self.assertIn('gudang kedua',str(self.case()['context']['latest_client_snapshot']['corrections']))
 def test_operator_cannot_clear_pending_review(self):
  record={'tenant_id':'T','case_id':'C','stage':'diagnosis','revision':1,'scope_version':1,'data':{'client_update_review':{'pending':True,'fingerprint':'latest','source_ref':'client'}}}
  event={'expected_revision':1,'action':'update','data':{'client_update_review':{'pending':False,'fingerprint':'latest','source_ref':'review','reviewed_by':'reviewer','reason':'checked'}}}
  with self.assertRaises(ValueError):transition(record,event,ACTOR,self.s.bank)
  new=transition(record,event,{'id':'reviewer','role':'team'},self.s.bank);self.assertFalse(new['data']['client_update_review']['pending'])
  event['data']['client_update_review']['fingerprint']='stale'
  with self.assertRaises(ValueError):transition(record,event,{'id':'reviewer','role':'team'},self.s.bank)
 def test_review_hold_blocks_advancement_and_revokes_current_approvals(self):
  record={'tenant_id':'T','case_id':'C','stage':'proposal','revision':1,'scope_version':1,'data':{'approvals':{'commercial':{'team':{'approved':True}}}}}
  event={'expected_revision':1,'action':'update','data':{'client_update_review':{'pending':True,'fingerprint':'new','source_ref':'client'}}}
  new=transition(record,event,ACTOR,self.s.bank);self.assertNotIn('approvals',new['data'])
  with self.assertRaises(ValueError):gate(new,'onboarding',self.s.bank)
 def test_closing_keeps_sync_job_and_queue(self):
  self.send('cukup dulu');self.assertEqual(self.job()['status'],'pending');self.s.retry_review_sync();self.assertEqual(len(self.s.queue()),1)

if __name__=='__main__':unittest.main()
