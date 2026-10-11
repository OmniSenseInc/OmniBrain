"""Root-owned rollback helper; never disables UFW or alters an SSH policy."""
from pathlib import Path
import json,os,sys,subprocess,fcntl

ALLOWED={'/etc/ufw/user.rules','/etc/ufw/user6.rules','/etc/ufw/ufw.conf','/etc/omnisense-ops/settings.json'}
def restore(backup,force=False):
    if os.geteuid()!=0:raise PermissionError('Root required')
    backup=Path(backup)
    with (backup/'transaction.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if (backup/'committed').exists() and not force:return
        _restore_locked(backup)
def _restore_locked(backup):
    meta=json.loads((backup/'before.json').read_text())
    if set(meta)!=ALLOWED:raise ValueError('Unexpected backup paths')
    for target,item in meta.items():
        p=Path(target);q=p.with_name(p.name+'.fw-restore-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,item['mode'])
        with os.fdopen(fd,'wb') as f:f.write((backup/item['file']).read_bytes());f.flush();os.fsync(f.fileno())
        os.chown(q,item['uid'],item['gid']);q.chmod(item['mode']);os.replace(q,p)
    subprocess.run(['ufw','reload'],check=True,capture_output=True,timeout=30)
    (backup/'rolled-back').write_text('restored\n')
if __name__=='__main__':restore(sys.argv[1],force='--force' in sys.argv[2:])
