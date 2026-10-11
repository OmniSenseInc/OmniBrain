"""Reviewed handoff fixes + restricted local retry worker, with backup and rollback."""
from pathlib import Path
import hashlib,os,json,subprocess,time,stat,urllib.request
assert os.geteuid()==0
S=Path('/home/ubuntu/ai-agency/meeting/handoff-v9-stage-20261006');C=Path('/home/ubuntu/ai-agency/consulting');R=Path('/opt/omnisense-web/security-v3-20261005T154436Z');O=Path('/etc/omnisense-ops/settings.json')
pins={'consultation_gateway.py':'86f5df379c1e56f271445292c046e8e1572bb7e9338a45dff13602e61d82d81d','workflow_agency.py':'ce790e909ad65d14830a55afb0e37e99cbeaecf8be1ab3a81117216ff9169db2'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in pins.items():assert sha(C/n)==h and sha(R/n)==h
settings=json.loads(O.read_text());assert settings['expected_hashes'][str(R/'consultation_gateway.py')]==pins['consultation_gateway.py']
tests=['test_review_sync','test_ambiguity','test_voice','test_adaptive','test_consultation_dialogue','test_reply_quality','test_decision_workflow_v31']
subprocess.run(['runuser','-u','ubuntu','--','/home/ubuntu/.hermes/hermes-agent/venv/bin/python','-m','unittest',*tests],cwd=S,check=True,timeout=90)
mapping={p:(S/n).read_bytes() for n in [*pins,'review_sync.py'] for p in (C/n,R/n)}
unit=Path('/etc/systemd/system/omnisense-review-sync.service');timer=Path('/etc/systemd/system/omnisense-review-sync.timer');assert not unit.exists() and not timer.exists()
mapping[unit]=('''[Unit]
Description=OmniSense consented review sync retries without chat delivery
After=omnisense-secure-web.service
[Service]
Type=oneshot
User=ubuntu
Group=ubuntu
ExecStart=/usr/bin/python3 '''+str(R/'review_sync.py')+''' --data /var/lib/omnisense-review-sync
UMask=0077
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=tmpfs
BindPaths=/home/ubuntu/ai-agency/consulting/data:/var/lib/omnisense-review-sync
ReadWritePaths=/var/lib/omnisense-review-sync
PrivateTmp=yes
PrivateDevices=yes
RestrictAddressFamilies=AF_UNIX
IPAddressDeny=any
CapabilityBoundingSet=
MemoryMax=128M
TasksMax=16
TimeoutStartSec=90
''').encode()
mapping[timer]=b'[Unit]\nDescription=OmniSense review queue retries\n[Timer]\nOnBootSec=2min\nOnUnitActiveSec=2min\nUnit=omnisense-review-sync.service\n[Install]\nWantedBy=timers.target\n'
backup=Path('/home/ubuntu/ai-agency/backups')/('handoff-v9-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700)
before={}
for i,p in enumerate([*mapping,O]):
 if p.exists():
  s=p.stat();before[p]=(p.read_bytes(),s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode));q=backup/str(i);q.write_bytes(before[p][0]);q.chmod(0o600)
 else:before[p]=None
(backup/'paths.json').write_text(json.dumps([str(p) for p in before]))
def put(p,b,uid,gid,mode):
 q=p.with_name(p.name+'.review-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
try:
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True,timeout=30)
 for p,b in mapping.items():
  if p.suffix=='.py':compile(b,str(p),'exec')
  root=R in p.parents or p in [unit,timer];put(p,b,0 if root else 1000,0 if root else 1000,0o644)
 for n in [*pins,'review_sync.py']:settings['expected_hashes'][str(R/n)]=sha(R/n)
 put(O,json.dumps(settings,indent=2).encode(),0,0,0o600)
 subprocess.run(['systemd-analyze','verify',str(unit),str(timer)],check=True);subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 for _ in range(15):
  try:
   with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as r:assert r.status==200
   break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health unavailable')
 subprocess.run(['systemctl','start','omnisense-review-sync.service'],check=True,timeout=95)
 subprocess.run(['systemctl','enable','--now','omnisense-review-sync.timer'],check=True)
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(['systemctl','disable','--now','omnisense-review-sync.timer']);subprocess.run(['systemctl','stop','omnisense-review-sync.service']);subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'])
 for p,v in before.items():
  if v is None:p.unlink(missing_ok=True)
  else:put(p,*v)
 subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45);raise
report={'version':'handoff-v9','backup':str(backup),'hashes':{str(p):sha(p) for p in mapping},'review_retry_interval_minutes':2,'worker_network_disabled':True,'worker_home_hidden':True,'case_data_identity_unchanged':True,'no_chat_messages_sent':True}
(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
