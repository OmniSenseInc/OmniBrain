import unittest
from fw_rules import parse,baseline,validate,ssh,global_web
BASE='Status: active\n[ 1] 22/tcp LIMIT IN Anywhere # SSH\n[ 2] 80/tcp ALLOW IN Anywhere\n[ 3] 443/tcp ALLOW IN Anywhere\n[ 4] 22/tcp (v6) LIMIT IN Anywhere (v6) # SSH\n[ 5] 80/tcp (v6) ALLOW IN Anywhere (v6)\n[ 6] 443/tcp (v6) ALLOW IN Anywhere (v6)\n'
NEW='Status: active\n[1] 22/tcp LIMIT IN Anywhere # SSH\n[2] 22/tcp (v6) LIMIT IN Anywhere (v6)\n[3] 80,443/tcp ALLOW IN 173.245.48.0/20 # Cloudflare\n[4] 80,443/tcp (v6) ALLOW IN 2400:cb00::/32 (v6) # Cloudflare\n'
NETS={'173.245.48.0/20','2400:cb00::/32'}
class RulesTests(unittest.TestCase):
    def test_actual_ufw_explicit_ipv6_without_v6_marker(self):
        text=NEW.replace('80,443/tcp (v6) ALLOW IN 2400:cb00::/32 (v6)','80,443/tcp ALLOW IN 2400:cb00::/32')
        validate(parse(text),NETS,ssh(parse(BASE)))
    def test_contradictory_v6_marker_on_ipv4_rejected(self):
        with self.assertRaises(ValueError):parse(NEW.replace('80,443/tcp ALLOW IN 173.245.48.0/20','80,443/tcp (v6) ALLOW IN 173.245.48.0/20'))
    def test_original_ipv4_ipv6_ssh_and_global_indices(self):
        rows=parse(BASE);baseline(rows);self.assertEqual(global_web(rows),[2,3,5,6])
    def test_cf_only_both_families_with_original_ssh(self):validate(parse(NEW),NETS,ssh(parse(BASE)))
    def test_unsafe_extra_public_rule_rejected(self):
        with self.assertRaises(ValueError):validate(parse(NEW+'[5] 443/tcp ALLOW IN Anywhere\n'),NETS,ssh(parse(BASE)))
    def test_missing_v6_network_rejected(self):
        with self.assertRaises(ValueError):validate(parse(NEW.rsplit('[4]',1)[0]),NETS,ssh(parse(BASE)))
    def test_changed_ssh_or_source_network_rejected(self):
        for text in [NEW.replace('LIMIT','ALLOW'),NEW.replace('173.245.48.0/20','0.0.0.0/0')]:
            with self.assertRaises(ValueError):validate(parse(text),NETS,ssh(parse(BASE)))
    def test_unexpected_baseline_or_inactive_rejected(self):
        for text in [BASE.replace('Status: active','Status: inactive'),BASE+'[7] 8080/tcp ALLOW IN Anywhere\n']:
            with self.assertRaises(ValueError):baseline(parse(text))
if __name__=='__main__':unittest.main()
