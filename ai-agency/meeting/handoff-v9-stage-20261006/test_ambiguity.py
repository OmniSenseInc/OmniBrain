import unittest,json,tempfile
from pathlib import Path
from consultation_gateway import Store
from consultation_dialogue import permission_denied
from consultation_voice import closes_chat,resumes_chat

class AmbiguityTests(unittest.TestCase):
 def test_permission_statements_with_followup_still_hold(self):
  for text in ['Saya belum punya izin. Bagaimana solusinya?','Saya tidak memiliki izin, apakah tetap bisa?','Saya gak punya persetujuan, bagaimana?','Saya belum punya izin apakah tetap boleh?','Pemilik tidak mengizinkan kami menggunakan data. Saya belum diizinkan.']:
   self.assertTrue(permission_denied(text),text)
 def test_hypothetical_permission_questions_are_not_reported_denials(self):
  for text in ['Bagaimana kalau saya belum punya izin?','Kalau data belum diizinkan, bagaimana?','Apakah bisa memakai data tanpa izin?','Boleh saya kirim data pelanggan?','Jangan memakai data tanpa izin.']:
   self.assertFalse(permission_denied(text),text)
 def test_business_safety_rules_do_not_mean_access_was_denied(self):
  for text in ['Data pelanggan tidak boleh bocor.','Stok tidak boleh minus.','Laporan tidak boleh terlambat.','Barang tidak boleh keluar sebelum dicatat.']:
   self.assertFalse(permission_denied(text),text)
 def test_explicit_forbidden_data_access_is_held(self):
  for text in ['Saya tidak boleh menggunakan data pelanggan.','Manajer dilarang membagikan dokumen itu.','Pemilik melarang; kami tidak boleh mengakses database.','Pemilik tidak mengizinkan kami menggunakan data.','Manajer belum memberikan izin, bagaimana solusinya?']:
   self.assertTrue(permission_denied(text),text)
 def test_postponement_without_scheduling_claim(self):
  for text in ['nanti lanjut besok','besok kita lanjut ya','saya mau istirahat dulu','aku pamit dulu','kita sambung besok','saya mau cut dulu']:
   self.assertTrue(closes_chat(text),text)
  for text in ['Stok cukup untuk besok','Besok lanjut pengiriman barang','Kapan bisa melanjutkan pengiriman?','Kalau kurang, lanjutkan perhitungan biaya']:
   self.assertFalse(closes_chat(text),text)
  self.assertTrue(resumes_chat('ayo lanjut'))
 def test_mixed_statement_question_persists_risk_without_model_call(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=Store(Path(tmp)/'data');s.receive('fake','chat','one','/mulai');s.receive('fake','chat','two','setuju')
   r=s.receive('fake','chat','three','Saya belum punya izin. Bagaimana solusinya?')
   b=json.loads(s.active('fake','chat')['body']);self.assertTrue(b['risk_hold']);self.assertEqual(s.active('fake','chat')['status'],'risk_review');self.assertFalse(r.get('personalize'))
 def test_prevention_statement_can_continue_general_consultation(self):
  with tempfile.TemporaryDirectory() as tmp:
   s=Store(Path(tmp)/'data');s.receive('fake','chat','one','/mulai');s.receive('fake','chat','two','setuju')
   s.receive('fake','chat','three','Data pelanggan tidak boleh bocor.')
   b=json.loads(s.active('fake','chat')['body']);self.assertFalse(b.get('risk_hold'));self.assertEqual(s.active('fake','chat')['status'],'discovery')

if __name__=='__main__':unittest.main()
