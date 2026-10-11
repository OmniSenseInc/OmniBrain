"""Read-only live verification and synthetic regressions; no WA/model calls."""
from pathlib import Path
import hashlib,json,os,sqlite3,subprocess,urllib.request

S=Path(__file__).resolve().parent
C=Path('/home/ubuntu/ai-agency/consulting')
R=Path('/opt/omnisense-web/security-v3-20261005T154436Z')
CORE=Path('/home/ubuntu/.hermes/hermes-agent')
PY=CORE/'venv/bin/python'
hashes={'consultation_gateway.py':'99bb60f099d940b66a00d44503eea5924cbff2178881dc73391a5109e0426942','workflow_agency.py':'cab356c76450aa4885063158a510c8bf71696435ee3cf0348d806427d63542f0','review_sync.py':'617fd92f38b9e222b3ed9c612299b219d81c52a5d4dd527122997a341de89fdf'}
for name,want in hashes.items():
    for base in (C,R):
        assert hashlib.sha256((base/name).read_bytes()).hexdigest()==want
assert hashlib.sha256(Path('/opt/omnisense-ops/omnisense_ops.py').read_bytes()).hexdigest()=='e0a98337116e8f963c1a57593c347cffa81e8135ce980c7cbf0f98d4a6fe0945'
auth=(CORE/'gateway/authz_mixin.py').read_bytes()
assert hashlib.sha256(auth).hexdigest()=='643c723bd7e15974ad44ce7281a087c2a423223dc37d017b7020c34d42dbc500'
(S/'authz_mixin.py').write_bytes(auth);os.chown(S/'authz_mixin.py',1000,1000)
subprocess.run([str(PY),'-m','unittest','test_ops'],cwd=S,check=True,timeout=30)
subprocess.run(['runuser','-u','ubuntu','--',str(PY),'-m','unittest','test_wa_security','test_core_authorization','test_security'],cwd=S,check=True,timeout=45)
subprocess.run(['runuser','-u','ubuntu','--',str(PY),'test_transport.py'],cwd=S,check=True,timeout=30)
policy=json.loads(Path('/opt/omnisense-web/whatsapp-admin-policy.json').read_text())
admins=policy['admin_numbers']
assert len(admins)==len(set(admins))==3 and {n[-4:] for n in admins}=={'4609','5165','0507'}
data=C/'data'
dbs=[data/'consultations.sqlite3',data/'pipeline.sqlite3',data/'web_security.sqlite3',Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/security-state/wa_security.sqlite3')]
for p in dbs:
    with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:
        assert db.execute('PRAGMA quick_check').fetchone()[0]=='ok'
for unit in ['omnisense-secure-web.service','nginx.service','omnisense-review-sync.timer','omnisense-monitor.timer','omnisense-backup.timer']:
    assert subprocess.run(['systemctl','is-active','--quiet',unit]).returncode==0
assert subprocess.run(['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user','is-active','--quiet','hermes-gateway.service']).returncode==0
with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=5) as response:
    assert response.status==200 and json.loads(response.read())['status']=='ok'
subprocess.run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','monitor'],check=True,timeout=30)
assert json.loads(Path('/var/lib/omnisense-ops/status.json').read_text())['status']=='ok'
print(json.dumps({'version':'all-in-v11','live_hashes_match':True,'databases_quick_check':4,'admin_count':3,'admin_suffixes':sorted(n[-4:] for n in admins),'all_services_and_timers_active':True,'no_whatsapp_or_model_calls':True}))
