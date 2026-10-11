"""Pin trusted Cloudflare peers; headers from direct visitors confer no trust."""
from pathlib import Path
import hashlib,json,os,subprocess,time

SITE=Path('/etc/nginx/sites-available/omnisense.conf')
TRUST=Path('/etc/nginx/conf.d/omnisense-trusted-proxy.conf')
BACKUP=Path('/home/ubuntu/ai-agency/backups/security-v5-proxy-20261006')
BASELINE='5896b0834fa4df7ec840b67118150fc15aea538c0b3a0b0f23e738a433bfb952'
CIDRS='''173.245.48.0/20 103.21.244.0/22 103.22.200.0/22 103.31.4.0/22
141.101.64.0/18 108.162.192.0/18 190.93.240.0/20 188.114.96.0/20
197.234.240.0/22 198.41.128.0/17 162.158.0.0/15 104.16.0.0/13
104.24.0.0/14 172.64.0.0/13 131.0.72.0/22
2400:cb00::/32 2606:4700::/32 2803:f800::/32 2405:b500::/32
2405:8100::/32 2a06:98c0::/29 2c0f:f248::/32'''.split()
assert os.geteuid()==0 and not TRUST.exists()
old=SITE.read_bytes();assert hashlib.sha256(old).hexdigest()==BASELINE,'Nginx changed since review'
text=old.decode()
assert text.count('proxy_set_header X-Forwarded-Proto $forwarded_proto;')==2
assert text.count('proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;')==2
text=text.replace('proxy_set_header X-Forwarded-Proto $forwarded_proto;','proxy_set_header X-Forwarded-Proto $scheme;')
text=text.replace('proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;','proxy_set_header CF-Connecting-IP $remote_addr;')
text=text.replace('proxy_set_header X-Real-IP $remote_addr;', 'proxy_set_header X-Real-IP $remote_addr;\n        proxy_set_header CF-Worker $omnisense_cf_worker;\n        proxy_set_header X-Forwarded-For "";\n        proxy_set_header Forwarded "";')
trust='# Reviewed official Cloudflare ranges, 6 October 2026.\n'+''.join('set_real_ip_from '+c+';\n' for c in CIDRS)
trust+='real_ip_header CF-Connecting-IP;\nreal_ip_recursive off;\n'
trust+='geo $realip_remote_addr $omnisense_cf_peer {\n    default 0;\n'+''.join('    '+c+' 1;\n' for c in CIDRS)+'}\n'
trust+='map "$omnisense_cf_peer:$http_cf_worker" $omnisense_cf_worker {\n    default "";\n    ~^1:.+ $http_cf_worker;\n}\n'
BACKUP.mkdir(mode=0o700);(BACKUP/'nginx-before.conf').write_bytes(old)
try:
    TRUST.write_text(trust);TRUST.chmod(0o644)
    pending=SITE.with_suffix('.pending');pending.write_text(text);pending.chmod(0o644);os.replace(pending,SITE)
    subprocess.run(['nginx','-t'],check=True)
    subprocess.run(['systemctl','reload','nginx'],check=True)
    # Public Cloudflare HTTPS must remain usable; never hide a Flexible-mode loop.
    result=subprocess.check_output(['curl','--resolve','omnisense.my.id:443:104.21.70.148','--max-time','15','-sS','-o','/dev/null','-w','%{http_code}','https://omnisense.my.id/?security-proxy-check=20261006'],text=True).strip()
    assert result=='200','Cloudflare HTTPS returned '+result+'; rollback and inspect encryption mode'
    rejected=subprocess.check_output(['curl','--max-time','5','-sS','-o','/dev/null','-w','%{http_code}','-H','Host: omnisense.my.id','-H','X-Forwarded-Proto: https','http://127.0.0.1/api/consultation/session'],text=True).strip()
    assert rejected=='403','Forged HTTP protocol still accepted'
except Exception:
    SITE.write_bytes(old);TRUST.unlink(missing_ok=True)
    subprocess.run(['nginx','-t'],check=True);subprocess.run(['systemctl','reload','nginx'],check=True)
    raise
report={'version':'security-v5-proxy','backup':str(BACKUP),'nginx_sha256':hashlib.sha256(SITE.read_bytes()).hexdigest(),'trusted_cidrs':len(CIDRS),'public_https_status':result,'forged_http_status':rejected,'ssl_dns_firewall_unchanged':True}
(BACKUP/'deployment.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
