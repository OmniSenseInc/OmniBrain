"""Stage v2 with synthetic data; never changes client ownership or gateway code."""
from pathlib import Path
from datetime import datetime,timezone
import os,sys,json,hashlib,shutil,subprocess,zipfile,pwd
old=Path('/opt/omnisense-web/release-20261005T143129Z')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
release=Path('/opt/omnisense-web')/('security-v2-'+stamp)
backup=Path('/home/ubuntu/ai-agency/backups')/('security-v2-'+stamp)
names={'consultation_web.py','run_secure_web.py','web_limits.py','test_security.py'}
with zipfile.ZipFile(sys.argv[1]) as z:
 assert set(z.namelist())==names|{'patch-manifest.json'}
 manifest=json.loads(z.read('patch-manifest.json'))
 for name,sha in manifest['baseline'].items():assert hashlib.sha256((old/name).read_bytes()).hexdigest()==sha,name
 assert set(manifest['files'])==names
 release.mkdir(mode=0o755);backup.mkdir(mode=0o700)
 for name in names:
  data=z.read(name);assert hashlib.sha256(data).hexdigest()==manifest['files'][name]
  (release/name).write_bytes(data);(release/name).chmod(0o644)
 for name in ['consultation_gateway.py','consultation_dialogue.py','baca_konsultasi_v3.py','assessment_v3.py','decision_v31.py','workflow_agency.py','agent_contract.py','pertanyaan_v3.json']:
  shutil.copy2(old/name,release/name)
 subprocess.run(['/opt/omnisense-web/venv/bin/python',str(release/'test_security.py'),'-v'],check=True)
 unit=Path('/etc/systemd/system/omnisense-secure-web.service')
 text=unit.read_text();assert str(old) in text and 'User=ubuntu\n' in text
 shutil.copy2(unit,backup/'omnisense-secure-web.service')
 production=text.replace(str(old),str(release))
 production=production.replace('TimeoutStopSec=15\n','TimeoutStopSec=15\nLogRateLimitIntervalSec=30s\nLogRateLimitBurst=100\n')
 (release/'omnisense-secure-web.service').write_text(production)
 testdata=Path('/home/ubuntu/ai-agency/consulting')/('security-v2-test-'+stamp)
 testdata.mkdir(mode=0o700);user=pwd.getpwnam('ubuntu');os.chown(testdata,user.pw_uid,user.pw_gid)
 staging=production.replace('--port 8080','--port 8082').replace('http://127.0.0.1:8080','http://127.0.0.1:8082').replace('/home/ubuntu/ai-agency/consulting/data:',str(testdata)+':')
 stageunit=Path('/etc/systemd/system/omnisense-security-v2-stage.service');stageunit.write_text(staging)
 subprocess.run(['systemd-analyze','verify',str(stageunit)],check=True)
 subprocess.run(['systemctl','daemon-reload'],check=True)
 subprocess.run(['systemctl','start','omnisense-security-v2-stage.service'],check=True)
 report={'version':'security-v2','release':str(release),'backup':str(backup),'test_data':str(testdata),'files':manifest['files'],'status':'staged'}
 (backup/'deployment.json').write_text(json.dumps(report,indent=2));(backup/'deployment.json').chmod(0o600)
 print(json.dumps(report))
