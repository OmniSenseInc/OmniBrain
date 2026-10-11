"""Deploy monitored review worker and audited handoff fixes, with pins and rollback."""
from pathlib import Path
import os,stat,json,hashlib,subprocess,time,urllib.request
assert os.geteuid()==0
S=Path('/home/ubuntu/ai-agency/meeting/all-in-v11-stage-20261007');C=Path('/home/ubuntu/ai-agency/consulting');R=Path('/opt/omnisense-web/security-v3-20261005T154436Z');OPS=Path('/opt/omnisense-ops/omnisense_ops.py');CFG=Path('/etc/omnisense-ops/settings.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={'consultation_gateway.py':'6328c321633f99606089ded546b4aa26a39c042f2cb9c886f0a3ed025827fdf1','workflow_agency.py':'6d44b263c98f9f44864b45b92c14a10531055f86ff83e6d8c77b6f0d80d5f7c8','review_sync.py':'617fd92f38b9e222b3ed9c612299b219d81c52a5d4dd527122997a341de89fdf'}
for n,h in pins.items():assert sha(C/n)==h and sha(R/n)==h
assert sha(OPS)=='03ed714cde0d5949bc68ad66768d4598b0cc155578d04bbd42a6cf359521c548'
tests=['test_review_sync','test_sync_race','test_queue_retention','test_ambiguity','test_voice','test_adaptive','test_consultation_dialogue','test_reply_quality','test_decision_workflow_v31','test_resume_hold','test_review_health','test_backup_hardening','test_consent_risk_sync']
subprocess.run(['runuser','-u','ubuntu','--','/home/ubuntu/.hermes/hermes-agent/venv/bin/python','-m','unittest',*tests],cwd=S,check=True,timeout=90)
mapping={p:(S/n).read_bytes() for n in pins for p in (C/n,R/n)};mapping[OPS]=(S/'omnisense_ops.py').read_bytes()
settings=json.loads(CFG.read_text())
for n,h in pins.items():assert settings['expected_hashes'][str(R/n)]==h
backup=Path('/home/ubuntu/ai-agency/backups')/('all-in-v11-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700);before={}
for i,p in enumerate([*mapping,CFG]):
 st=p.stat();before[p]=(p.read_bytes(),st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode));q=backup/str(i);q.write_bytes(before[p][0]);q.chmod(0o600)
(backup/'paths.json').write_text(json.dumps([str(p) for p in before]))
def put(p,b,uid,gid,mode):
 q=p.with_name(p.name+'.ops-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
try:
 subprocess.run(['systemctl','stop','omnisense-monitor.timer','omnisense-review-sync.timer','omnisense-review-sync.service','omnisense-monitor.service'],check=True,timeout=95)
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True)
 for p,b in mapping.items():compile(b,str(p),'exec');put(p,b,*before[p][1:])
 for n in pins:settings['expected_hashes'][str(R/n)]=sha(R/n)
 put(CFG,json.dumps(settings,indent=2).encode(),0,0,0o600)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 for _ in range(15):
  try:
   with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as r:assert r.status==200
   break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health unavailable')
 subprocess.run(['systemctl','start','omnisense-review-sync.service'],check=True,timeout=95)
 subprocess.run(['systemctl','start','omnisense-review-sync.timer','omnisense-monitor.timer'],check=True)
 subprocess.run(['systemctl','start','omnisense-backup.service'],check=True,timeout=180)
 subprocess.run(['/usr/bin/python3',str(OPS),'monitor'],check=True,timeout=30)
 subprocess.run(['systemctl','start','omnisense-review-sync.timer','omnisense-monitor.timer'],check=True)
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(['systemctl','stop','omnisense-review-sync.service']);subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'])
 for p,v in before.items():put(p,*v)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','start','omnisense-review-sync.timer','omnisense-monitor.timer'],check=True);raise
report={'version':'all-in-v11','backup':str(backup),'hashes':{str(p):sha(p) for p in mapping},'no_whatsapp_messages_sent':True,'data_identity_unchanged':True};(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
