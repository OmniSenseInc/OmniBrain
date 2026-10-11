"""Run as root on the authorized VPS. Stages first; cutover is a separate step."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os,shutil,subprocess,sys,zipfile

base=Path('/home/ubuntu/ai-agency')
stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
release=Path('/opt/omnisense-web')/('release-'+stamp)
backup=base/'backups'/('security-'+stamp)
allowed={'consultation_web.py','run_secure_web.py','test_security.py','omnisense-secure-web.service','source-baseline.json'}
with zipfile.ZipFile(sys.argv[1]) as z:
    assert set(z.namelist())==allowed
    manifest=json.loads(z.read('source-baseline.json'))
    for name,sha in manifest.items():
        assert '/' not in name and '\\' not in name
        assert hashlib.sha256((base/'consulting'/name).read_bytes()).hexdigest()==sha, 'Runtime source changed: '+name
    release.mkdir(parents=True,mode=0o755)
    backup.mkdir(parents=True,mode=0o700)
    for name in allowed:
        (release/name).write_bytes(z.read(name));(release/name).chmod(0o644)
    for name in manifest:
        shutil.copy2(base/'consulting'/name,release/name);(release/name).chmod(0o644)
    unit=release/'omnisense-secure-web.service'
    text=unit.read_text().replace('/opt/omnisense-web/app',str(release))
    unit.write_text(text)
    testdata=base/'consulting'/('security-test-'+stamp)
    testdata.mkdir(mode=0o700);os.chown(testdata,1000,1000)
    for path in ['/srv/omnisense-web','/var/lib/omnisense-web']:
        Path(path).mkdir(parents=True,exist_ok=True)
    olduser=Path('/home/ubuntu/.config/systemd/user')
    for rel in ['omnisense-preview-web.service','omnisense-preview-web.service.d/consultation.conf']:
        dest=backup/rel;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(olduser/rel,dest)
    subprocess.run(['/opt/omnisense-web/venv/bin/python',str(release/'test_security.py'),'-v'],check=True)
    # Restrict the test service exactly as production, while using an empty DB.
    stage=text.replace('--port 8080','--port 8081').replace('http://127.0.0.1:8080','http://127.0.0.1:8081').replace('/home/ubuntu/ai-agency/consulting/data:',str(testdata)+':')
    Path('/etc/systemd/system/omnisense-security-stage.service').write_text(stage)
    subprocess.run(['systemd-analyze','verify','/etc/systemd/system/omnisense-security-stage.service'],check=True)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','start','omnisense-security-stage.service'],check=True)
    report={'release':str(release),'backup':str(backup),'test_data':str(testdata),'old_service_enabled':subprocess.run(['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user','is-enabled','omnisense-preview-web.service'],capture_output=True,text=True).stdout.strip()}
    (backup/'deployment.json').write_text(json.dumps(report,indent=2));(backup/'deployment.json').chmod(0o600)
    print(json.dumps(report))
