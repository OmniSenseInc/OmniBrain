from pathlib import Path
import subprocess,pwd,grp,os,hashlib,json,shutil
base=Path('/home/ubuntu/ai-agency')
release=Path('/opt/omnisense-web/release-20261005T143129Z')
backup=base/'backups/security-20261005T143129Z'
group='omnisense-client-data'
try:grp.getgrnam(group)
except KeyError:subprocess.run(['groupadd','--system',group],check=True)
try:pwd.getpwnam('omnisense-web')
except KeyError:subprocess.run(['useradd','--system','--no-create-home','--gid',group,'--home-dir','/nonexistent','--shell','/usr/sbin/nologin','omnisense-web'],check=True)
account=pwd.getpwnam('omnisense-web');gid=grp.getgrnam(group).gr_gid
assert account.pw_shell=='/usr/sbin/nologin' and account.pw_uid!=1000
original=base/'consulting/consultation_gateway.py'
assert hashlib.sha256(original.read_bytes()).hexdigest()=='f4bcbaa5d1edc1c07fc24d327fe8195330ae8a3193be1c146fb7742f746a4c23'
shutil.copy2(original,backup/'consultation_gateway.py')
text=original.read_text()
old="        if os.name=='posix':\n            self.root.chmod(0o700)"
new="        shared = False\n        if os.name=='posix':\n            import grp\n            shared = grp.getgrgid(self.root.stat().st_gid).gr_name == 'omnisense-client-data'\n            self.root.chmod(0o2770 if shared else 0o700)"
assert old in text and 'self.path.chmod(0o600)' in text
text=text.replace(old,new).replace('self.path.chmod(0o600)','self.path.chmod(0o660 if shared else 0o600)')
original.write_text(text);original.chmod(0o644)
(release/'consultation_gateway.py').write_text(text);(release/'consultation_gateway.py').chmod(0o644)
data=base/'consulting/data'
report={'previous_data_gid':data.stat().st_gid,'previous_data_mode':oct(data.stat().st_mode&0o7777),'db_mode':oct((data/'consultations.sqlite3').stat().st_mode&0o7777)}
os.chown(data,1000,gid);data.chmod(0o2770)
for name in ['consultations.sqlite3','consultations.sqlite3-journal','consultations.sqlite3-wal','consultations.sqlite3-shm']:
 p=data/name
 if p.exists():os.chown(p,1000,gid);p.chmod(0o660)
unit=Path('/etc/systemd/system/omnisense-secure-web.service')
shutil.copy2(unit,backup/'secure-web-before-identity.service')
text=unit.read_text().replace('User=ubuntu','User=omnisense-web').replace('Group=ubuntu','Group=omnisense-client-data').replace('UMask=0077','UMask=0007')
unit.write_text(text);(release/'omnisense-secure-web.service').write_text(text)
subprocess.run(['systemd-analyze','verify',str(unit)],check=True)
subprocess.run(['systemctl','daemon-reload'],check=True)
subprocess.run(['systemctl','restart','omnisense-secure-web.service'],check=True)
report.update(web_user='omnisense-web',group=group,gateway_sha256=hashlib.sha256(original.read_bytes()).hexdigest())
(backup/'identity-isolation.json').write_text(json.dumps(report,indent=2));(backup/'identity-isolation.json').chmod(0o600)
print('Web now uses a locked system account; only designated consultation data group is shared')
