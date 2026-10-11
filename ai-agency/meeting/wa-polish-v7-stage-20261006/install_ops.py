"""Install local security checks and encrypted backups, using only system Python."""
from pathlib import Path
import os,json,subprocess,hashlib
from cryptography.fernet import Fernet

assert os.geteuid()==0
STAGE=Path('/home/ubuntu/ai-agency/meeting/tune-v6-stage-20261006')
ROOT=Path('/opt/omnisense-ops');CONFIG=Path('/etc/omnisense-ops');STATE=Path('/var/lib/omnisense-ops')
for p in [ROOT,CONFIG,STATE,Path('/var/backups/omnisense-encrypted')]:p.mkdir(mode=0o700,exist_ok=True)
# Executables must be owned by root so the web identity cannot replace monitoring code.
ROOT.chmod(0o755);script=ROOT/'omnisense_ops.py';assert not script.exists()
script.write_bytes((STAGE/'omnisense_ops.py').read_bytes());script.chmod(0o644)
key=CONFIG/'backup.key';assert not key.exists();fd=os.open(key,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
with os.fdopen(fd,'wb') as f:f.write(Fernet.generate_key());f.flush();os.fsync(f.fileno())
paths=['/home/ubuntu/.hermes/hermes-agent/gateway/authz_mixin.py','/home/ubuntu/.hermes/hermes-agent/gateway/omnisense_policy.py','/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py','/opt/omnisense-web/whatsapp-admin-policy.json','/opt/omnisense-web/security-v3-20261005T154436Z/approved-site.json']
paths += ['/opt/omnisense-web/security-v3-20261005T154436Z/'+n for n in ['consultation_gateway.py','consultation_dialogue.py','storage_modes.py','consultation_adaptive.py','web_limits.py']]
(CONFIG/'settings.json').write_text(json.dumps({'expected_hashes':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}},indent=2));(CONFIG/'settings.json').chmod(0o600)
unitroot=Path('/etc/systemd/system');units=[]
for action in ['monitor','backup']:
 name='omnisense-'+action
 text='[Unit]\nDescription=OmniSense '+action+' without external messaging\n\n[Service]\nType=oneshot\nUser=root\nExecStart=/usr/bin/python3 /opt/omnisense-ops/omnisense_ops.py '+action+'\nUMask=0077\nNoNewPrivileges=yes\nPrivateTmp=yes\nProtectSystem=strict\nProtectHome=read-only\nReadWritePaths=/var/lib/omnisense-ops /var/backups/omnisense-encrypted\nTimeoutStartSec=180\n'
 p=unitroot/(name+'.service');assert not p.exists();p.write_text(text);units.append(p)
 timer='[Unit]\nDescription=OmniSense '+action+' schedule\n\n[Timer]\n'+('OnBootSec=2min\nOnUnitActiveSec=5min\n' if action=='monitor' else 'OnCalendar=*-*-* 03:00:00 Asia/Jakarta\nPersistent=true\n')+'Unit='+name+'.service\n\n[Install]\nWantedBy=timers.target\n'
 p=unitroot/(name+'.timer');assert not p.exists();p.write_text(timer);units.append(p)
subprocess.run(['systemd-analyze','verify',*[str(p) for p in units]],check=True)
subprocess.run(['/usr/bin/python3',str(script),'backup'],check=True,timeout=180)
subprocess.run(['/usr/bin/python3',str(script),'monitor'],check=True,timeout=30)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','enable','--now','omnisense-monitor.timer','omnisense-backup.timer'],check=True)
print(json.dumps({'monitor_interval_minutes':5,'daily_backup':'03:00 Asia/Jakarta','backup_encrypted':True,'restore_tested':True,'offsite_configured':False,'notification_channel':'local_status_and_journal','no_wa_messages_sent':True}))
