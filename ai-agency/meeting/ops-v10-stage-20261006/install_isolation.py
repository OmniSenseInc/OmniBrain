"""Separate web UID using the tested shared-storage implementation, with rollback."""
from pathlib import Path
import os,pwd,grp,subprocess,time,json,stat,hashlib,tempfile,shutil
assert os.geteuid()==0
R=Path('/opt/omnisense-web/security-v3-20261005T154436Z');S=Path('/home/ubuntu/ai-agency/meeting/tune-v6-stage-20261006')
DATA=Path('/home/ubuntu/ai-agency/consulting/data');UNIT=Path('/etc/systemd/system/omnisense-secure-web.service')
assert all((R/n).read_bytes()==(S/n).read_bytes() for n in ['storage_modes.py','web_limits.py','consultation_gateway.py'])
oldunit=UNIT.read_bytes();assert b'User=ubuntu\n' in oldunit and b'Group=ubuntu\n' in oldunit
ubuntu=pwd.getpwnam('ubuntu')
try:group=grp.getgrnam('omnisense-client-data')
except KeyError:
 subprocess.run(['groupadd','--system','omnisense-client-data'],check=True);group=grp.getgrnam('omnisense-client-data')
try:web=pwd.getpwnam('omnisense-web')
except KeyError:
 subprocess.run(['useradd','--system','--no-create-home','--gid','omnisense-client-data','--home-dir','/nonexistent','--shell','/usr/sbin/nologin','omnisense-web'],check=True);web=pwd.getpwnam('omnisense-web')
assert web.pw_shell=='/usr/sbin/nologin' and web.pw_uid!=ubuntu.pw_uid and web.pw_gid==group.gr_gid
# Synthetic cross-UID SQLite writes must work before touching production ownership.
fixture=Path(tempfile.mkdtemp(prefix='omni-isolation-',dir='/var/lib'));fixture.chmod(0o755)
root=fixture/'data';root.mkdir(mode=0o2770);os.chown(root,ubuntu.pw_uid,group.gr_gid);root.chmod(0o2770)
code="import sys;sys.path.insert(0,"+repr(str(R))+ ");from consultation_gateway import Store;from pathlib import Path;s=Store(Path("+repr(str(root))+"));c=s.db();\nwith c as db:db.execute(\"INSERT INTO replies VALUES(?,?,?,?,?,?)\",('synthetic',str(__import__('os').getuid()),None,'test','sent',0))\nprint('cross_uid_sqlite_write_ok')"
try:
 for who in ['ubuntu','omnisense-web','ubuntu']:
  # Last pass reads and updates, rather than duplicating the same synthetic primary key.
  text=code if who=='omnisense-web' or not (root/'consultations.sqlite3').exists() else code.replace('INSERT INTO replies VALUES(?,?,?,?,?,?)','INSERT OR REPLACE INTO replies VALUES(?,?,?,?,?,?)')
  subprocess.run(['runuser','-u',who,'--',str(Path('/opt/omnisense-web/venv/bin/python')),'-c',text],check=True,timeout=15)
finally:shutil.rmtree(fixture)

backup=Path('/home/ubuntu/ai-agency/backups')/('web-identity-v6-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700)
(backup/'unit-before.service').write_bytes(oldunit)
paths=[DATA]+[DATA/n for n in ['consultations.sqlite3','web_security.sqlite3','.web-rate-key']]
before={p:(p.stat().st_uid,p.stat().st_gid,stat.S_IMODE(p.stat().st_mode)) for p in paths}
(backup/'data-modes.json').write_text(json.dumps({str(p):v for p,v in before.items()}))
newunit=oldunit.decode().replace('User=ubuntu\n','User=omnisense-web\n').replace('Group=ubuntu\n','Group=omnisense-client-data\n').replace('UMask=0077','UMask=0007')
newunit=newunit.replace('InaccessiblePaths=/proc','InaccessiblePaths=/proc /var/lib/omnisense-web/pipeline.sqlite3')
assert 'User=omnisense-web' in newunit
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/'+str(ubuntu.pw_uid),'systemctl','--user']
try:
 subprocess.run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','backup'],check=True,timeout=180)
 subprocess.run(ctl+['stop','hermes-gateway.service'],check=True,timeout=45);subprocess.run(['systemctl','stop','omnisense-secure-web.service'],check=True)
 for p in paths:
  os.chown(p,ubuntu.pw_uid,group.gr_gid);p.chmod(0o2770 if p==DATA else 0o640 if p.name=='.web-rate-key' else 0o660)
 UNIT.write_text(newunit);subprocess.run(['systemd-analyze','verify',str(UNIT)],check=True)
 subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True)
 import urllib.request
 for _ in range(15):
  try:
   assert json.loads(urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2).read())['status']=='ok';break
  except Exception:time.sleep(1)
 else:raise RuntimeError('Web health failed')
 pid=subprocess.check_output(['systemctl','show','omnisense-secure-web.service','-p','MainPID','--value'],text=True).strip()
 code="import os,sqlite3;assert os.getuid()!="+str(ubuntu.pw_uid)+";assert not os.access('/home/ubuntu/.hermes/.env',os.R_OK);assert not os.access('/var/lib/omnisense-web/pipeline.sqlite3',os.R_OK);assert not os.access('/srv/omnisense-web/index.html',os.W_OK);sqlite3.connect('/var/lib/omnisense-web/consultations.sqlite3').execute('SELECT 1');print('dedicated_web_namespace_isolation_ok')"
 subprocess.run(['nsenter','-t',pid,'-m','--','runuser','-u','omnisense-web','--','/usr/bin/python3','-c',code],check=True,timeout=15)
 subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
except Exception:
 subprocess.run(['systemctl','stop','omnisense-secure-web.service']);subprocess.run(ctl+['stop','hermes-gateway.service'],timeout=45)
 for p,(uid,gid,mode) in before.items():os.chown(p,uid,gid);p.chmod(mode)
 UNIT.write_bytes(oldunit);subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['systemctl','start','omnisense-secure-web.service'],check=True);subprocess.run(ctl+['start','hermes-gateway.service'],check=True,timeout=45)
 raise
report={'web_user':'omnisense-web','uid':web.pw_uid,'shared_group':'omnisense-client-data','backup':str(backup),'pipeline_hidden_from_web':True,'hermes_env_inaccessible_to_web':True,'synthetic_cross_uid_sqlite_passed':True,'data_group_modes':'2770 directory, 660 shared databases, 640 seed; pipeline remains private','admin_whitelist_unchanged':True}
(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
