import importlib.util,json,tempfile,unittest
from pathlib import Path
from consultation_dialogue import safe_outgoing,contains_link,TRUSTED_PRIVACY
from consultation_gateway import Store

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('candidate_plugin',HERE/'plugin_patch.py')
plugin=importlib.util.module_from_spec(spec);spec.loader.exec_module(plugin)

class OutboundTests(unittest.TestCase):
    def test_model_links_rejected_in_all_forms(self):
        for link in ['HTTPS://spam.example/promo','www.spam.example','spam.example/promo','[promo](https://spam.example)','h\u200bttps://spam.example','ｈｔｔｐｓ://spam.example','javascript:alert(1)','data:text/html,hello','192.0.2.3/promo']:
            with self.subTest(link=link):
                self.assertTrue(contains_link(link));self.assertFalse(plugin.usable_reply('Silakan kunjungi '+link))
                self.assertNotIn('spam.example',safe_outgoing('Masukan: '+link))

    def test_business_text_and_security_complaint_preserved(self):
        for text in ['Laporan manual memperlambat pencarian data.','Website saya disisipi iklan judol; saya ingin mengamankannya.','Waktu proses 3.5 menit dan biaya Rp1.000.000.']:
            self.assertEqual(safe_outgoing(text),text)
        self.assertTrue(plugin.usable_reply('Periksa jalur perubahan file situs dan akses administrator.'))

    def test_only_exact_agency_privacy_link_allowed(self):
        self.assertIn(TRUSTED_PRIVACY,safe_outgoing('Rincian: '+TRUSTED_PRIVACY))
        for text in [TRUSTED_PRIVACY+'?redirect=https://spam.example','https://omnisense.id.evil.example/privacy','https://omnisense.id/other']:
            self.assertNotIn('https://',safe_outgoing(text))

    def test_opening_and_discovery_do_not_repeat_untrusted_links(self):
        base=HERE/'test-runs';base.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as folder:
            store=Store(Path(folder)/'data');bank=store.bank
            p=dict(version=bank['version'],bank_revision=bank['bank_revision'],mode='screening',answers={q['id']:{'value':3} for q in bank['screening']},context={'process':'Laporan operasional','problem':'Pencarian lambat. HTTPS://spam.example/promo','process_owner':'QA'})
            case=store.create(p,True,'synthetic-browser','test-link-protection-001')
            first=store.receive('synthetic-client','synthetic-chat','claim-001',case['claim_code'])
            self.assertNotIn('spam.example',first['text']);self.assertIn('Pencarian lambat',first['text'])
            reply=store.receive('synthetic-client','synthetic-chat','answer-001','Admin menyalin data manual dari www.spam.example')
            self.assertNotIn('www.spam.example',reply['text'])
            # Preserve the original statement as private unverified evidence.
            self.assertIn('www.spam.example',json.loads(store.active('synthetic-client','synthetic-chat')['body'])['discovery']['problem_example']['answer'])

if __name__=='__main__':unittest.main()
