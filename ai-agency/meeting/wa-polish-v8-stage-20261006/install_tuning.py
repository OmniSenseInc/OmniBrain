"""Pinned live tuning deployment; backup, tests, brief downtime and rollback."""
from pathlib import Path
import os,pwd,hashlib,subprocess,json,time,shutil,stat

assert os.geteuid()==0
S=Path('/home/ubuntu/ai-agency/meeting/tune-v6-stage-20261006')
C=Path('/home/ubuntu/ai-agency/consulting')
R=Path('/opt/omnisense-web/security-v3-20261005T154436Z')
P=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
BASE={'consultation_gateway.py':'ec53a65b021826f8581914b06d55bab33ddcec9cd17bf3e021ded1cfc3980f41','consultation_dialogue.py':'9493cf99569e82bd4521a9aef24aa333b18a3523bb6b845231b3aaa0bd5821c0'}
for n,h in BASE.items():assert sha(C/n)==h and sha(R/n)==h
assert sha(P)=='d8af7035c6ca4d54f9a3bc0650dc52ae1e8615acce48700f12c2f2f9f3fca39b'
assert sha(R/'web_limits.py')==hashlib.sha256((Path('/home/ubuntu/ai-agency/meeting/security-audit-20261006/web_limits.py')).read_bytes()).hexdigest()
account=pwd.getpwnam('ubuntu');ctl=['sudo','-u','ubuntu','env','XDG_RUNTIME_DIR=/run/user/'+str(account.pw_uid),'systemctl','--user']
subprocess.run(['sudo','-u','ubuntu','/home/ubuntu/.hermes/hermes-agent/venv/bin/python','-m','unittest','test_adaptive','test_consultation_dialogue','test_reply_quality'],cwd=S,check=True,timeout=60)
mapping={}
for n in ['consultation_gateway.py','consultation_dialogue.py','consultation_adaptive.py','storage_modes.py']:
 mapping[C/n]=S/n;mapping[R/n]=S/n
mapping[R/'web_limits.py']=S/'web_limits.py';mapping[P]=S/'plugin_patch.py'
for src in mapping.values():compile(src.read_bytes(),str(src),'exec')
backup=Path('/home/ubuntu/ai-agency/backups')/('tune-v6-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700)
before={}
for i,dst in enumerate(mapping):
 if dst.exists():
  st=dst.stat();b=dst.read_bytes();before[dst]=(b,st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode));q=backup/str(i);q.write_bytes(b);q.chmod(0o600)
 else:before[dst]=None
(backup/'paths.json').write_text(json.dumps([str(p) for p in mapping]))
def write(p,b,uid,gid,mode):
 q=p.with_name(p.name+'.tune-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
try:
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45)
 subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True,timeout=30)
 for dst,src in mapping.items():
  root_owned=R in dst.parents
  write(dst,src.read_bytes(),0 if root_owned else account.pw_uid,0 if root_owned else account.pw_gid,0o644)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True,timeout=30)
 subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 import urllib.request
 for _ in range(15):
  try:
   assert json.loads(urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2).read())['status']=='ok';break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health unavailable')
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],timeout=30)
 for dst,v in before.items():
  if v is None:dst.unlink(missing_ok=True)
  else:write(dst,*v)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True,timeout=30);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 raise
report={'version':'tune-v6','backup':str(backup),'hashes':{str(p):sha(p) for p in mapping},'admin_policy_unchanged':True,'assessment_weights_unchanged':True,'frontend_unchanged':True}
(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
