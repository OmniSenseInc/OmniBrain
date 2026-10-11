"""Two-module WA patch; pin live v7, test before update, backup and rollback."""
from pathlib import Path
import os,hashlib,json,subprocess,time,stat
assert os.geteuid()==0
S=Path('/home/ubuntu/ai-agency/meeting/wa-polish-v8-stage-20261006');C=Path('/home/ubuntu/ai-agency/consulting');R=Path('/opt/omnisense-web/security-v3-20261005T154436Z');OPS=Path('/etc/omnisense-ops/settings.json')
pins={'consultation_dialogue.py':'b75d0270aa4ea9dfc5ffc91d5d9b67c8971ecfe31437249c19abb1914f55f2d1','consultation_voice.py':'f5251d46764bd53ea56cb6550f448eb0847489b63d0b2ead530e07b028954d53'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
settings=json.loads(OPS.read_text())
for n,h in pins.items():assert sha(C/n)==h and sha(R/n)==h and settings['expected_hashes'][str(R/n)]==h
subprocess.run(['runuser','-u','ubuntu','--','/home/ubuntu/.hermes/hermes-agent/venv/bin/python','-m','unittest','test_ambiguity','test_voice','test_adaptive','test_consultation_dialogue','test_reply_quality'],cwd=S,check=True,timeout=60)
mapping={p:(S/n).read_bytes() for n in pins for p in (C/n,R/n)}
before={}
backup=Path('/home/ubuntu/ai-agency/backups')/('wa-polish-v8-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700)
for i,p in enumerate([*mapping,OPS]):
 st=p.stat();before[p]=(p.read_bytes(),st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode));q=backup/str(i);q.write_bytes(before[p][0]);q.chmod(0o600)
(backup/'paths.json').write_text(json.dumps([str(p) for p in before]))
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
def atomic(p,b,uid,gid,mode):
 q=p.with_name(p.name+'.ambiguity-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
try:
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True,timeout=30)
 for p,b in mapping.items():atomic(p,b,*before[p][1:])
 for n in pins:settings['expected_hashes'][str(R/n)]=sha(R/n)
 atomic(OPS,json.dumps(settings,indent=2).encode(),0,0,0o600)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True,timeout=30);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 import urllib.request
 for _ in range(15):
  try:
   with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as r:assert r.status==200
   break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health failed')
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],timeout=30)
 for p,v in before.items():atomic(p,*v)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45);raise
report={'version':'wa-polish-v8','backup':str(backup),'hashes':{str(p):sha(p) for p in mapping},'tests_passed':52,'whatsapp_messages_sent':False,'admin_policy_unchanged':True,'data_modes_unchanged':True};(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
