import unittest
from ingress_patch import patch_nginx,patch_unit,PREVIEW

class PatchTests(unittest.TestCase):
    def setUp(self):
        self.site=('server {\n    listen 80;\n    server_name omnisense.my.id www.omnisense.my.id;\n    location /.well-known/acme-challenge/ { root /var/www/letsencrypt; }\n    location / {\n        proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;\n    }\n}\n')*2
        self.unit='[Service]\nUser=ubuntu\nExecStart=/opt/venv/bin/python /opt/run_secure_web.py --origin '+PREVIEW+' --origin https://omnisense.my.id --origin https://www.omnisense.my.id --origin http://localhost:8080 --trust-tunnel\nProtectSystem=strict\n'
    def test_both_ingresses_gate_actual_socket_peer_and_normalize_client(self):
        out=patch_nginx(self.site)
        self.assertEqual(out.count('if ($omnisense_cf_peer = 0) { return 403; }'),2)
        self.assertEqual(out.count('CF-Connecting-IP $remote_addr;'),2)
        self.assertEqual(out.count('CF-Worker $omnisense_cf_worker;'),2)
        self.assertNotIn('$http_cf_connecting_ip',out)
    def test_acme_and_other_content_preserved(self):
        out=patch_nginx(self.site)
        self.assertEqual(out.count('location /.well-known/acme-challenge/ { root /var/www/letsencrypt; }'),2)
        self.assertEqual(out.count('listen 80;'),2)
    def test_changed_baselines_and_rerun_refused(self):
        for source in [self.site.replace('www.omnisense.my.id','other.test'),self.site.replace('$http_cf_connecting_ip','$remote_addr'),patch_nginx(self.site)]:
            with self.assertRaises(ValueError):patch_nginx(source)
    def test_preview_origin_removed_without_touching_identity_sandbox_localhealth(self):
        out=patch_unit(self.unit)
        self.assertNotIn(PREVIEW,out)
        for part in ['User=ubuntu','ProtectSystem=strict','http://localhost:8080','--trust-tunnel','https://omnisense.my.id','https://www.omnisense.my.id']:self.assertIn(part,out)
    def test_missing_canonical_origin_and_multiple_execstart_refused(self):
        for source in [self.unit.replace('https://www.omnisense.my.id','https://else.test'),self.unit+'ExecStart=/bad\n',self.unit.replace(PREVIEW,'https://wrong.test')]:
            with self.assertRaises(ValueError):patch_unit(source)

if __name__=='__main__':unittest.main()
