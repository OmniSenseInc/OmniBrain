import importlib.util,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('new_guard',Path(__file__).parent/'plugin_patch.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class ReplyQualityTests(unittest.TestCase):
 def test_unavailable_followup_action_rejected(self):
  self.assertFalse(p.usable_reply('Kami akan menindaklanjuti dengan pengecekan pada alur penjadwalan.'))
  self.assertTrue(p.usable_reply('Tim perlu memeriksa alur penjadwalan sebelum menentukan penyebab.'))
 def test_self_report_never_becomes_verification(self):
  self.assertFalse(p.usable_reply('Hasil verifikasi stok perlu dianggap belum final.'))
  self.assertTrue(p.usable_reply('Hasil kuis perlu dicocokkan dengan catatan selisih harian.'))
 def test_current_client_statement_is_grounding_material(self):
  self.assertTrue(p.usable_reply('Saat ini belum ada catatan berapa kali pesanan tertunda.',{'latest_message':'Saya belum tahu; belum pernah dicatat.'}))
  self.assertFalse(p.usable_reply('Saat ini belum ada validasi ketersediaan.',{'latest_message':'Saya belum tahu; belum pernah dicatat.'}))
 def test_unmentioned_standardization_is_unknown(self):
  self.assertFalse(p.usable_reply('Sumber data belum terstandarisasi.'))
  self.assertTrue(p.usable_reply('Perlu memeriksa format sumber data sebelum memilih pendekatan.'))
 def test_generic_causal_assertion_does_not_replace_diagnosis(self):
  self.assertFalse(p.usable_reply('Laporan lama biasanya karena prosesnya manual.'))
  self.assertTrue(p.usable_reply('Salah satu kemungkinan adalah pengerjaan berulang. Perlu memeriksa catatan tahapan untuk membedakannya dari keterlambatan data.'))
if __name__=='__main__':unittest.main()
