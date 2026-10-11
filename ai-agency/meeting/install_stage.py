from pathlib import Path
from datetime import datetime,timezone
import json,zipfile,hashlib,shutil,subprocess,pwd,os,sys
base=Path('/home/ubuntu/ai-agency')
old=Path('/opt/omnisense-web/security-v2-20261005T150901Z')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
release=Path('/opt/omnisense-web')/('security-v3-'+stamp)
backup=base/'backups'/('security-v3-'+stamp)
names={'consultation_web.py','run_secure_web.py','web_limits.py','consultation_gateway.py','consultation_dialogue.py','plugin_patch.py','approved-site.json','test_security.py','test_outbound.py'}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
plugin=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py')
with zipfile.ZipFile(sys.argv[1]) as z:
 assert set(z.namelist())==names|{'patch-manifest.json'}
 patch=json.loads(z.read('patch-manifest.json'));assert set(patch['files'])==names
 for name,wanted in patch['baseline'].items():
  path=plugin if name=='plugin_patch.py' else base/'consulting'/name if name in ('consultation_gateway.py','consultation_dialogue.py') else old/name
  assert sha(path)==wanted,name
 approved=json.loads(z.read('approved-site.json'))
 for name,wanted in approved['files'].items():
  p=(base/'website'/name).resolve();assert (base/'website').resolve() in p.parents
  assert sha(p)==wanted,'Website differs from reviewed local version: '+name
 release.mkdir(mode=0o755);backup.mkdir(mode=0o700)
 for name in names:
  blob=z.read(name);assert hashlib.sha256(blob).hexdigest()==patch['files'][name]
  (release/name).write_bytes(blob);(release/name).chmod(0o644)
 for name in ['baca_konsultasi_v3.py','assessment_v3.py','decision_v31.py','workflow_agency.py','agent_contract.py','pertanyaan_v3.json']:
  shutil.copy2(old/name,release/name)
 for name in ['test_security.py','test_outbound.py']:
  subprocess.run(['/opt/omnisense-web/venv/bin/python',str(release/name)],check=True)
 site=release/'stage-site';site.mkdir(mode=0o755)
 for name in approved['files']:
  target=site/name;target.parent.mkdir(parents=True,exist_ok=True)
  shutil.copy2(base/'website'/name,target)
 unit=Path('/etc/systemd/system/omnisense-secure-web.service')
 text=unit.read_text();assert str(old) in text and 'User=ubuntu\n' in text
 shutil.copy2(unit,backup/'omnisense-secure-web.service')
 for name in ['consultation_gateway.py','consultation_dialogue.py']:
  shutil.copy2(base/'consulting'/name,backup/name)
 shutil.copy2(plugin,backup/'plugin_patch.py')
 production=text.replace(str(old),str(release)).replace('--trust-tunnel','--trust-tunnel --manifest '+str(release/'approved-site.json'))
 (release/'omnisense-secure-web.service').write_text(production)
 testdata=base/'consulting'/('security-v3-test-'+stamp);testdata.mkdir(mode=0o700)
 account=pwd.getpwnam('ubuntu');os.chown(testdata,account.pw_uid,account.pw_gid)
 staging=production.replace('--port 8080','--port 8083').replace('http://127.0.0.1:8080','http://127.0.0.1:8083').replace('/home/ubuntu/ai-agency/consulting/data:',str(testdata)+':').replace('/home/ubuntu/ai-agency/website:',str(site)+':')
 stage=Path('/etc/systemd/system/omnisense-security-v3-stage.service');stage.write_text(staging)
 subprocess.run(['systemd-analyze','verify',str(stage)],check=True)
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','start','omnisense-security-v3-stage.service'],check=True)
 report={'version':patch['version'],'release':str(release),'backup':str(backup),'test_data':str(testdata),'files':patch['files'],'baseline':patch['baseline'],'status':'staged'}
 (backup/'deployment.json').write_text(json.dumps(report,indent=2));(backup/'deployment.json').chmod(0o600)
 print(json.dumps({'release':str(release),'backup':str(backup),'approved_files':len(approved['files'])}))
