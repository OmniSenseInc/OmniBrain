from pathlib import Path
import hashlib,json,shutil,os
stage=Path(__file__).resolve().parent
plan=json.loads((stage/'patch351-plan.json').read_text())
allowed={'/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py','/home/ubuntu/ai-agency/website/assets/konsultasi-ui-v35.js'}
assert len(plan)==2 and {p['target'] for p in plan}==allowed
for p in plan:
 assert hashlib.sha256(Path(p['target']).read_bytes()).hexdigest()==p['before'], 'Live file changed; inspect first'
 assert hashlib.sha256((stage/p['source']).read_bytes()).hexdigest()==p['after'], 'Unexpected staged content'
backup=Path('/home/ubuntu/ai-agency/consulting/backup_optimization_v35_20261004T190755Z/patch351')
backup.mkdir(mode=0o700,exist_ok=True)
for i,p in enumerate(plan):
 target=Path(p['target'])
 old=backup/str(i)
 if not old.exists():
  shutil.copy2(target,old)
  old.chmod(0o600)
 tmp=target.with_name(target.name+'.patch351.tmp')
 shutil.copyfile(stage/p['source'],tmp)
 tmp.chmod(0o644)
 os.replace(tmp,target)
print('Installed 2 verified files; private backups kept; no service/config/database mutations.')
