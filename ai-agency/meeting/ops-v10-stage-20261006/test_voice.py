import json,tempfile,unittest
from pathlib import Path
from consultation_gateway import Store
from consultation_voice import closes_chat,context_for_model,messages_for_model,explicit_start
from consultation_dialogue import intent

class VoiceTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.now=[1800000000]
  self.s=Store(Path(self.tmp.name)/'data',clock=lambda:self.now[0]);self.n=0
 def send(self,text):
  self.n+=1;self.now[0]+=8;return self.s.receive('synthetic-client','chat','m'+str(self.n),text)
 def start(self):
  self.send('Saya mau konsultasi bisnis');self.send('setuju')
 def body(self):return json.loads(self.s.active('synthetic-client','chat')['body'])
 def test_natural_entry_and_explicit_consent(self):
  r=self.send('Saya mau konsultasi bisnis');self.assertIn('setuju',r['text']);self.assertIsNone(self.s.active('synthetic-client','chat'))
  self.send('ya');self.assertIsNone(self.s.active('synthetic-client','chat'))
  self.send('saya setuju');self.assertIsNotNone(self.s.active('synthetic-client','chat'))
 def test_consent_word_without_offer_is_not_consent(self):
  self.send('setuju');self.assertIsNone(self.s.active('synthetic-client','chat'))
 def test_close_once_then_ack_is_silent(self):
  self.start();r=self.send('oke cukup dulu, makasih')
  self.assertNotIn('?',r['text']);self.assertFalse(r.get('personalize'));self.assertTrue(self.body()['conversation_closed'])
  self.assertEqual(self.s.active('synthetic-client','chat')['status'],'paused')
  for text in ['iya','makasih','oke','cukup dulu']:self.assertIsNone(self.send(text))
  self.assertEqual(self.s.active('synthetic-client','chat')['cursor'],0)
 def test_resume_reopens_same_case_and_not_team_approval(self):
  self.start();tid=self.s.active('synthetic-client','chat')['id'];self.send('cukup dulu');r=self.send('lanjut')
  self.assertEqual(self.s.active('synthetic-client','chat')['id'],tid);self.assertFalse(self.body().get('conversation_closed'))
  self.assertEqual(self.s.active('synthetic-client','chat')['status'],'discovery');self.assertNotIn('approve',r)
 def test_closing_preserves_team_queue(self):
  self.start();r=self.send('tolong kirim ringkasan ke tim');self.assertIn('review tim',r['text'])
  self.send('ya');self.assertEqual(self.s.active('synthetic-client','chat')['status'],'ready_for_team')
  self.send('cukup sampai sini');self.assertEqual(self.s.active('synthetic-client','chat')['status'],'ready_for_team');self.assertEqual(len(self.s.queue()),1)
 def test_handoff_request_is_not_a_success_goal(self):
  self.start();self.send('mau kamu kirim ringkasan ke atasan biar saya berdiskusi langsung')
  self.assertNotIn('success_owner',self.body()['discovery']);self.assertEqual(self.s.active('synthetic-client','chat')['status'],'awaiting_confirmation');self.assertFalse((self.s.root/'pipeline.sqlite3').exists())
 def test_direct_context_contains_actual_complaint_and_no_quiz(self):
  self.start();r=self.send('Selisih stok gudang berbeda dengan data supply.')
  data=context_for_model(r['case']);self.assertIn('Selisih stok',data['context']['problem']);self.assertNotIn('belum disebut',json.dumps(data['context']));self.assertFalse(data['has_screening'])
  messages=messages_for_model('SYSTEM',data);self.assertIn('tanpa kuis',messages[0]['content']);self.assertNotIn('HASIL PERHITUNGAN',str(messages))
 def test_correction_and_expense_question_understood(self):
  self.assertEqual(intent('Eh, maksudku bukan stok, tapi penjualan.'),'correction')
  self.assertEqual(intent('Bagaimana mengurangi biaya operasional?'),'followup')
  self.assertEqual(intent('Berapa biaya implementasinya?'),'pricing')
 def test_reference_resolves_prior_attempt_not_literal_reference(self):
  self.start()
  for text in ['Stok supply berbeda dengan catatan gudang.','Operator menerima barang lalu mencatatnya di spreadsheet.','Selisih terlihat minus pada laporan akhir.','Data dipegang manager dan saya hanya menerima laporan.']:self.send(text)
  self.send('Saya sudah coba menanyai manager dan karyawan, jawabannya bertentangan. Apa yang bisa dibantu?')
  self.send('saya suda jelaskan diatas itu');item=self.body()['discovery']['previous_attempts']
  self.assertIn('menanyai manager',item['answer']);self.assertEqual(item['supplied_via'],'client_reference');self.assertNotIn('verified',item)
 def test_unresolved_reference_does_not_advance(self):
  self.start();self.send('saya sudah jelaskan di atas');self.assertEqual(self.s.active('synthetic-client','chat')['cursor'],0)
 def test_followup_does_not_repeat_discovery_question(self):
  self.start();r=self.send('Apa yang bisa kamu bantu?');self.assertEqual(r['question'],'');self.assertEqual(self.s.active('synthetic-client','chat')['cursor'],0)
 def test_count_alone_is_not_process_description(self):
  self.start();self.send('2 orang');self.assertEqual(self.s.active('synthetic-client','chat')['cursor'],0);self.assertNotIn('problem_example',self.body()['discovery'])
 def test_closing_phrases_and_business_negations(self):
  for text in ['cukup','cukup dulu','cukup sampai sini','udah dulu','oke cukup ya','makasih','cukup dulu, terima kasih','nanti lanjut lagi']:
   self.assertTrue(closes_chat(text),text)
  for text in ['stoknya sudah cukup','data belum cukup','makasih, tapi saya mau tanya lagi','cukup 2 orang untuk gudang?']:
   self.assertFalse(closes_chat(text),text)
 def test_admin_task_not_natural_consultation_entry(self):
  self.assertFalse(explicit_start('Perbaiki sistem konsultasi dan restart layanan'))
  self.assertTrue(explicit_start('aku mau konsultasi soal bisnis'))
 def test_risk_hold_survives_natural_closing_and_resume(self):
  self.start();self.send('Saya belum punya izin penggunaan data pelanggan');self.send('cukup dulu');r=self.send('lanjut')
  self.assertTrue(self.body()['risk_hold']);self.assertNotIn('personalize',r);self.assertEqual(self.s.active('synthetic-client','chat')['status'],'paused')

if __name__=='__main__':unittest.main()
