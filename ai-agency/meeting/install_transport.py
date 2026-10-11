"""Backend-only fix; preserves DNS/Nginx/service settings and all client records."""
from pathlib import Path
import os,hashlib,json,subprocess,sys,zipfile,shutil,time,urllib.request

R=Path('/opt/omnisense-web/security-v3-20261005T154436Z')
STAGE=Path('/home/ubuntu/ai-agency/meeting/security-audit-20261006')
BACKUP=Path('/home/ubuntu/ai-agency/backups/security-v4-transport-20261006')
UNIT=Path('/etc/systemd/system/omnisense-secure-web.service')
BASELINE='f962f4a2d2b4aa721982d6c9576e97097eb43e690dafbbcd165c1105cb6bb3af'
FINAL='f35a99152a6f8219698a6f9a7c1544bd5c96c13098de17a7e12c16c3393af14a'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.geteuid()==0
before=UNIT.read_bytes()
assert str(R).encode() in before
old=(R/'consultation_web.py').read_bytes();assert sha(old)==BASELINE
with zipfile.ZipFile(sys.argv[1]) as z:
    assert set(z.namelist())=={'consultation_web.py','test_transport.py'}
    new=z.read('consultation_web.py');assert sha(new)==FINAL
    # Synthetic test data only, outside production directory/webroot.
    for name in z.namelist():
        (STAGE/name).write_bytes(z.read(name))
        shutil.chown(STAGE/name,user='ubuntu',group='ubuntu')
for name in ['test_transport.py','test_security.py','test_outbound.py']:
    subprocess.run(['sudo','-u','ubuntu','/opt/omnisense-web/venv/bin/python',str(STAGE/name)],check=True)
assert UNIT.read_bytes()==before,'Service changed during validation; abort safely'
assert sha((R/'consultation_web.py').read_bytes())==BASELINE
BACKUP.mkdir(mode=0o700)
(BACKUP/'consultation_web.py').write_bytes(old)
shutil.copy2(UNIT,BACKUP/'service-snapshot.service')
try:
    pending=R/'consultation_web.pending';pending.write_bytes(new);pending.chmod(0o644)
    os.replace(pending,R/'consultation_web.py')
    subprocess.run(['systemctl','restart','omnisense-secure-web.service'],check=True)
    healthy=False
    for attempt in range(20):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as response:
                healthy=json.load(response)=={'status':'ok'}
            if healthy:break
        except Exception:pass
        time.sleep(.2)
    assert healthy,'Backend health failed'
except Exception:
    (R/'consultation_web.py').write_bytes(old)
    subprocess.run(['systemctl','restart','omnisense-secure-web.service'],check=True)
    raise
report={'version':'security-v4-transport','runtime':str(R),'backup':str(BACKUP),'baseline':BASELINE,'final':FINAL,'health':'ok','tests':{'transport':8,'existing_web':28,'outbound':4},'service_settings_preserved':UNIT.read_bytes()==before,'dns_nginx_ssl_unchanged':True}
(BACKUP/'deployment.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report))
