"""Install the owner's confirmed three administrators with backup and rollback."""
import hashlib,json,os,pwd,re,shutil,stat,subprocess,sys,time,zipfile
from pathlib import Path
from dotenv import dotenv_values
import yaml

assert os.geteuid()==0
assert set(sys.argv[2:])=={'4609','5165','0507'} and len(sys.argv[2:])==3
ACCOUNT=pwd.getpwnam('ubuntu')
HOME=Path('/home/ubuntu/.hermes')
CORE=HOME/'hermes-agent/gateway'
PLUGIN=HOME/'plugins/omnisense-consultation'
ENV=HOME/'.env';CONFIG=HOME/'config.yaml'
POLICY=Path('/opt/omnisense-web/whatsapp-admin-policy.json')
assert not POLICY.exists() and not (CORE/'omnisense_policy.py').exists()
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha((PLUGIN/'__init__.py').read_bytes())=='d938e4d6333b52640afc466642049f16bbbd8911dd0102fff834d7f6872acafc'
assert sha((CORE/'authz_mixin.py').read_bytes())=='861e3381488c4f53a9e9a12bbecd1d3261e20f7b6b6f84469919c658cd6ee5d3'
env_bytes=ENV.read_bytes();env_text=env_bytes.decode('utf-8')
values=dotenv_values(ENV)
numbers=[n.strip().lstrip('+') for n in values['WHATSAPP_ALLOWED_USERS'].split(',')]
assert len(numbers)==4 and len(set(numbers))==4 and all(re.fullmatch(r'[1-9][0-9]{7,14}',n) for n in numbers)
assert {n[-4:] for n in numbers}=={'4609','5165','0507','2230'}
selected=[n for n in numbers if n[-4:] in sys.argv[2:]];removed=next(n for n in numbers if n[-4:]=='2230')
assert len(selected)==3
assert values.get('WHATSAPP_ALLOW_ALL_USERS','').lower() in ('false','0','no','off','')
line=re.compile(r'^WHATSAPP_ALLOWED_USERS=.*$',re.M)
assert len(line.findall(env_text))==1
new_env=line.sub('WHATSAPP_ALLOWED_USERS='+','.join(selected),env_text).encode('utf-8')
config_bytes=CONFIG.read_bytes();config=yaml.safe_load(config_bytes)
extra=config.get('platforms',{}).get('whatsapp',{}).get('extra',{})
# This deployment has no second, conflicting configured user allowlist.
assert not extra.get('allow_from') and not extra.get('allowed_users')
assert extra.get('group_policy')=='allowlist' and extra.get('dm_policy')=='pairing'

stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
STAGE=Path('/home/ubuntu/ai-agency/meeting')/('security-v5-three-'+stamp)
STAGE.mkdir(mode=0o700);os.chown(STAGE,ACCOUNT.pw_uid,ACCOUNT.pw_gid)
names={'plugin_patch.py','omnisense_wa_security.py','wa_limits.py','omnisense_policy.py','authz_mixin.py','test_wa_security.py','test_core_authorization.py','verify_admin_live.py','core/gateway/whatsapp_identity.py','core/gateway/authz_mixin.py'}
with zipfile.ZipFile(sys.argv[1]) as z:
    assert set(z.namelist())==names
    assert sha(z.read('authz_mixin.py'))=='643c723bd7e15974ad44ce7281a087c2a423223dc37d017b7020c34d42dbc500'
    for name in names:
        p=STAGE/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(name))
for p in STAGE.rglob('*'):os.chown(p,ACCOUNT.pw_uid,ACCOUNT.pw_gid)
for name in ('omnisense_wa_security.py','wa_limits.py'):
    assert (PLUGIN/name).read_bytes()==(STAGE/name).read_bytes()
PYTHON=HOME/'hermes-agent/venv/bin/python'
for test in ('test_wa_security.py','test_core_authorization.py'):
    subprocess.run(['sudo','-u','ubuntu',str(PYTHON),str(STAGE/test)],check=True,timeout=45)
for p in STAGE.rglob('*.py'):compile(p.read_bytes(),str(p),'exec')

targets={ENV:new_env,CORE/'authz_mixin.py':(STAGE/'authz_mixin.py').read_bytes(),CORE/'omnisense_policy.py':(STAGE/'omnisense_policy.py').read_bytes(),PLUGIN/'__init__.py':(STAGE/'plugin_patch.py').read_bytes(),POLICY:json.dumps({'version':1,'admin_numbers':selected},indent=2).encode('utf-8')}
BACKUP=Path('/home/ubuntu/ai-agency/backups')/('security-v5-three-admins-'+stamp)
BACKUP.mkdir(mode=0o700)
before={}
for i,p in enumerate(targets):
    if p.exists():
        s=p.stat();b=p.read_bytes();before[p]=(b,s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))
        q=BACKUP/str(i);q.write_bytes(b);q.chmod(0o600)
    else:before[p]=None
(BACKUP/'config-before.yaml').write_bytes(config_bytes);(BACKUP/'config-before.yaml').chmod(0o600)
(BACKUP/'paths.json').write_text(json.dumps([str(p) for p in targets]))
ctl=['sudo','-u','ubuntu','env','XDG_RUNTIME_DIR=/run/user/'+str(ACCOUNT.pw_uid),'systemctl','--user']
def atomic(p,data,uid,gid,mode):
    q=p.with_name(p.name+'.omni-security-pending')
    fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
assert ENV.read_bytes()==env_bytes and CONFIG.read_bytes()==config_bytes
assert sha((PLUGIN/'__init__.py').read_bytes())=='d938e4d6333b52640afc466642049f16bbbd8911dd0102fff834d7f6872acafc'
assert sha((CORE/'authz_mixin.py').read_bytes())=='861e3381488c4f53a9e9a12bbecd1d3261e20f7b6b6f84469919c658cd6ee5d3'
try:
    subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45)
    for p,data in targets.items():
        uid,gid,mode=(0,ACCOUNT.pw_gid,0o640) if p==POLICY else (ACCOUNT.pw_uid,ACCOUNT.pw_gid,0o600 if p==ENV else 0o644)
        atomic(p,data,uid,gid,mode)
    # Run checks as the service account; full numbers never leave this process.
    verified=subprocess.run(['sudo','-u','ubuntu',str(PYTHON),str(STAGE/'verify_admin_live.py')],input=removed,check=True,capture_output=True,text=True,timeout=45)
    verification=json.loads(verified.stdout)
    subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
    for _ in range(15):
        if subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0:break
        time.sleep(1)
    else:raise RuntimeError('Gateway not active')
except Exception:
    subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45)
    for p,value in before.items():
        if value is None:p.unlink(missing_ok=True)
        else:atomic(p,*value)
    subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
    raise
report={'version':'security-v5-exact-three','backup':str(BACKUP),'synthetic_tests':23,'live_policy_verification':verification,'plugin_sha256':sha((PLUGIN/'__init__.py').read_bytes()),'core_sha256':sha((CORE/'authz_mixin.py').read_bytes()),'config_unchanged':CONFIG.read_bytes()==config_bytes,'whatsapp_messages_sent':False}
(BACKUP/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
