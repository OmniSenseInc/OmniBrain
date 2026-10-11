"""Deploy admission protection without guessing which administrator to remove."""
from pathlib import Path
import hashlib,json,zipfile,shutil,subprocess,os,pwd,sys

PLUGIN=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation')
BACKUP=Path('/home/ubuntu/ai-agency/backups/security-v5-wa-spam-20261006')
STAGE=Path('/home/ubuntu/ai-agency/meeting/security-v5-stage-20261006')
BASE=Path('/home/ubuntu/ai-agency/meeting/security-audit-20261006')
BASELINE='7fa239e5bd1ff787ab9e89d30af87f752b51a56fbfa725922634271b3a5f37dd'
FINAL='d938e4d6333b52640afc466642049f16bbbd8911dd0102fff834d7f6872acafc'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert os.geteuid()==0
old=(PLUGIN/'__init__.py').read_bytes();assert sha(old)==BASELINE
STAGE.mkdir(mode=0o700,exist_ok=True);account=pwd.getpwnam('ubuntu');os.chown(STAGE,account.pw_uid,account.pw_gid)
for p in BASE.iterdir():
    if p.is_file() and p.suffix in ('.py','.json'):shutil.copy2(p,STAGE/p.name)
with zipfile.ZipFile(sys.argv[1]) as z:
    names={'plugin_patch.py','omnisense_wa_security.py','wa_limits.py','test_wa_security.py','core/gateway/whatsapp_identity.py','omnisense_policy.py'}
    assert set(z.namelist())==names
    assert sha(z.read('plugin_patch.py'))==FINAL
    for n in names:
        p=STAGE/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(z.read(n))
for p in STAGE.rglob('*'):
    os.chown(p,account.pw_uid,account.pw_gid)
subprocess.run(['sudo','-u','ubuntu','/opt/omnisense-web/venv/bin/python',str(STAGE/'test_wa_security.py')],check=True)
subprocess.run(['sudo','-u','ubuntu','/opt/omnisense-web/venv/bin/python',str(STAGE/'test_outbound.py')],check=True)
assert sha((PLUGIN/'__init__.py').read_bytes())==BASELINE
assert not (PLUGIN/'omnisense_wa_security.py').exists() and not (PLUGIN/'wa_limits.py').exists()
BACKUP.mkdir(mode=0o700);(BACKUP/'plugin-before.py').write_bytes(old)
env=dict(os.environ,XDG_RUNTIME_DIR='/run/user/'+str(account.pw_uid))
restart=['sudo','-u','ubuntu','env','XDG_RUNTIME_DIR='+env['XDG_RUNTIME_DIR'],'systemctl','--user','restart','hermes-gateway.service']
try:
    for n in ['omnisense_wa_security.py','wa_limits.py']:
        shutil.copy2(STAGE/n,PLUGIN/n);os.chown(PLUGIN/n,account.pw_uid,account.pw_gid);(PLUGIN/n).chmod(0o640)
    state=PLUGIN/'security-state';state.mkdir(mode=0o700);os.chown(state,account.pw_uid,account.pw_gid)
    pending=PLUGIN/'__init__.pending';pending.write_bytes((STAGE/'plugin_patch.py').read_bytes());pending.chmod(0o644);os.chown(pending,account.pw_uid,account.pw_gid)
    os.replace(pending,PLUGIN/'__init__.py')
    subprocess.run(restart,check=True)
except Exception:
    (PLUGIN/'__init__.py').write_bytes(old)
    subprocess.run(restart,check=True)
    raise
report={'version':'security-v5-wa-spam','backup':str(BACKUP),'plugin_sha256':sha((PLUGIN/'__init__.py').read_bytes()),'wa_simulation_tests':16,'outbound_tests':4,'admin_whitelist_unchanged':True,'exact_three_admin_lock':'pending_user_selection','no_whatsapp_test_messages_sent':True}
(BACKUP/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
