"""Deploy reviewed WA voice/routing updates with pins and rollback; keep three-admin policy."""
from pathlib import Path
import os,pwd,hashlib,json,stat,subprocess,time,urllib.request
assert os.geteuid()==0
S=Path('/home/ubuntu/ai-agency/meeting/wa-polish-v7-stage-20261006');C=Path('/home/ubuntu/ai-agency/consulting');R=Path('/opt/omnisense-web/security-v3-20261005T154436Z');P=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py');SOUL=Path('/home/ubuntu/.hermes/SOUL.md');OPS=Path('/etc/omnisense-ops/settings.json')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins={'consultation_gateway.py':'1c6b0ef6a5c9204578e74a5221ac74ea16810a8d3dc5aef96262d238d793982e','consultation_dialogue.py':'abc607b173b034d74671badba5db8e8a94626c2c13bcf790f9a8799278065fb6','consultation_adaptive.py':'67a21ce9009c5270f98be280531e9e2193b63b53bea0031bf21e2d7b0a2654d3'}
for n,h in pins.items():assert sha(C/n)==h and sha(R/n)==h
assert sha(P)=='8a9c3e05b80cc538d29968ea00bc96bf402bf3767ba5c239132d3327746e7b77';assert sha(SOUL)=='1dd5a2fd0ff34e7d9974eebc639b5ae5c9a82c1f2fdb60e291428bb218811ec5'
settings=json.loads(OPS.read_text())
for p in [P,*[R/n for n in pins]]:assert settings['expected_hashes'][str(p)]==sha(p)
python='/home/ubuntu/.hermes/hermes-agent/venv/bin/python'
subprocess.run(['runuser','-u','ubuntu','--',python,'-m','unittest','test_voice','test_adaptive','test_consultation_dialogue','test_reply_quality'],cwd=S,check=True,timeout=60)
mapping={}
for n in [*pins,'consultation_voice.py']:
 mapping[C/n]=(S/n).read_bytes();mapping[R/n]=(S/n).read_bytes()
mapping[P]=(S/'plugin_patch.py').read_bytes()
style='''\n\n## OmniSense WhatsApp consultation voice (2026-10-06)\nFor business consultation, use clear, warm, professional Indonesian. Start with the client's current concern or question. Keep ordinary turns to one short paragraph plus at most one useful follow-up; do not attach a question mechanically to every answer. Avoid labels such as "previous attempts", "success owner", "self-report", "gate", and "pengamatan bisnisnya" in client-facing messages. Summaries may use short Indonesian labels and readable spacing.\nUse the latest clarification and correction instead of repeating an obsolete initial context. If the client says they already explained something, check that case's previous statements before asking them to repeat it. Distinguish a request to speak to a human from a business target. Do not infer employee misconduct, loss causes, or decision authority from conflicting reports; seek supporting records. Describe what OmniSense can propose without claiming a system was built or a reviewer received the case.\nWhen the user says cukup dulu, udah dulu, or a clear farewell, acknowledge once, add no discovery question, and stop pushing the discussion. Do not cancel an already requested human review solely because the chat ended. Resume when the user clearly wants to continue. Preserve existing consent, privacy, command authorization and commercial review requirements; conversational cues never grant operator access. For an authorized internal admin asking for technical work, retain the needed technical detail and established operator powers.\n'''
assert '## OmniSense WhatsApp consultation voice (2026-10-06)' not in SOUL.read_text();mapping[SOUL]=SOUL.read_bytes()+style.encode()
for p,b in mapping.items():
 if p.suffix=='.py':compile(b,str(p),'exec')
backup=Path('/home/ubuntu/ai-agency/backups')/('wa-polish-v7-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700)
before={}
for i,p in enumerate([*mapping,OPS]):
 if p.exists():
  st=p.stat();before[p]=(p.read_bytes(),st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode));q=backup/str(i);q.write_bytes(before[p][0]);q.chmod(0o600)
 else:before[p]=None
(backup/'paths.json').write_text(json.dumps([str(p) for p in before]))
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
def atomic(p,b,uid,gid,mode):
 q=p.with_name(p.name+'.voice-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
 with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
 os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
try:
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True,timeout=30)
 for p,b in mapping.items():
  root_owned=R in p.parents;prior=before[p]
  atomic(p,b,0 if root_owned else 1000,0 if root_owned else 1000,prior[3] if prior else 0o644)
 for p in [P,*[R/n for n in [*pins,'consultation_voice.py']]]:settings['expected_hashes'][str(p)]=sha(p)
 atomic(OPS,json.dumps(settings,indent=2).encode(),0,0,0o600)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True,timeout=30);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 for _ in range(15):
  try:
   with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as r:assert r.status==200
   break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health failed')
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],timeout=30)
 for p,v in before.items():
  if v is None:p.unlink(missing_ok=True)
  else:atomic(p,*v)
 subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45);raise
report={'version':'wa-polish-v7','backup':str(backup),'source_hashes':{str(p):sha(p) for p in mapping},'three_admin_policy_unchanged':True,'model_provider_unchanged':True,'no_real_whatsapp_messages_sent':True,'unix_identity_unchanged':True}
(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
