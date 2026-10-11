"""Root-owned local monitoring and authenticated encrypted SQLite snapshots."""
import argparse,contextlib,gzip,hashlib,io,json,os,shutil,sqlite3,stat,subprocess,tarfile,tempfile,time,uuid
from pathlib import Path

SETTINGS=Path('/etc/omnisense-ops/settings.json')
STATE=Path('/var/lib/omnisense-ops')
BACKUPS=Path('/var/backups/omnisense-encrypted')
KEY=Path('/etc/omnisense-ops/backup.key')
DATA=Path('/home/ubuntu/ai-agency/consulting/data')
WA=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/security-state')
SOURCES={'consultations.sqlite3':DATA/'consultations.sqlite3','pipeline.sqlite3':DATA/'pipeline.sqlite3','web_security.sqlite3':DATA/'web_security.sqlite3','wa_security.sqlite3':WA/'wa_security.sqlite3','web-rate-key':DATA/'.web-rate-key','wa-rate-key':WA/'.wa-rate-key'}
# Fernet is a whole-message cipher. Keep its allocations bounded on a small VPS.
MAX_BYTES=64*1024*1024
MAX_MEMBER_BYTES=64*1024*1024
MAX_MANIFEST_BYTES=64*1024
ARCHIVE_OVERHEAD_BYTES=1024*1024
KEEP_SNAPSHOTS=7

def _sync_directory(path):
    if os.name=='posix':
        fd=os.open(path,os.O_RDONLY|getattr(os,'O_DIRECTORY',0))
        try:os.fsync(fd)
        finally:os.close(fd)

def atomic(path,data):
    path=Path(path)
    fd,name=tempfile.mkstemp(prefix='.'+path.name+'.',suffix='.pending',dir=path.parent)
    pending=Path(name)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        for attempt in range(5):
            try:os.replace(pending,path);break
            except PermissionError:
                # Windows file watchers can briefly deny replace after a closed write.
                if os.name=='posix' or attempt==4:raise
                time.sleep(0.01*(2**attempt))
        _sync_directory(path.parent)
    finally:
        if pending.exists():pending.unlink()

@contextlib.contextmanager
def _backup_lock():
    # The OS releases this lock on a crash; no stale marker can block tomorrow's run.
    path=STATE/'backup.lock'
    fd=os.open(path,os.O_RDWR|os.O_CREAT|getattr(os,'O_NOFOLLOW',0),0o600)
    locked=False
    try:
        if os.name=='posix':
            import fcntl
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB);locked=True
        else:
            import msvcrt
            if os.fstat(fd).st_size==0:os.write(fd,b'0')
            os.lseek(fd,0,os.SEEK_SET)
            msvcrt.locking(fd,msvcrt.LK_NBLCK,1);locked=True
        yield
    finally:
        if locked:
            if os.name=='posix':fcntl.flock(fd,fcntl.LOCK_UN)
            else:
                os.lseek(fd,0,os.SEEK_SET);msvcrt.locking(fd,msvcrt.LK_UNLCK,1)
        os.close(fd)

def _archive_cap():return MAX_BYTES+ARCHIVE_OVERHEAD_BYTES

def _ciphertext_cap():
    # Fernet carries padded AES blocks, a 57-byte envelope and base64 expansion.
    return 4*((57+(_archive_cap()//16+1)*16+2)//3)

def _read_bounded(path,limit):
    with Path(path).open('rb') as f:
        if os.fstat(f.fileno()).st_size>limit:raise ValueError('Snapshot file exceeds cap')
        b=f.read(limit+1)
    if len(b)>limit:raise ValueError('Snapshot file exceeds cap')
    return b

class _BoundedReader:
    def __init__(self,stream,limit):self.stream=stream;self.remaining=limit
    def read(self,size=-1):
        request=self.remaining+1 if size<0 else min(size,self.remaining+1)
        b=self.stream.read(request)
        if len(b)>self.remaining:raise ValueError('Snapshot expanded size exceeds cap')
        self.remaining-=len(b);return b

def cipher():
    from cryptography.fernet import Fernet
    fd=os.open(KEY,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0))
    with os.fdopen(fd,'rb') as f:
        st=os.fstat(f.fileno())
        if st.st_uid!=0 or st.st_mode&0o077 or not stat.S_ISREG(st.st_mode) or st.st_size!=44:raise PermissionError('Backup key protection invalid')
        key=f.read(45)
    return Fernet(key)

def restore_test(path):
    payload=cipher().decrypt(_read_bounded(path,_ciphertext_cap()))
    if len(payload)>_archive_cap():raise ValueError('Snapshot too large')
    checks=[];seen=set();digests={};manifest=None;total=0
    expected=set(SOURCES)|{'manifest.json'}
    with tempfile.TemporaryDirectory(prefix='restore-',dir=STATE) as tmp,gzip.GzipFile(fileobj=io.BytesIO(payload),mode='rb') as gz:
        bounded=_BoundedReader(gz,MAX_BYTES+MAX_MANIFEST_BYTES+ARCHIVE_OVERHEAD_BYTES)
        with tarfile.open(fileobj=bounded,mode='r|') as tar:
            for m in tar:
                cap=MAX_MANIFEST_BYTES if m.name=='manifest.json' else MAX_MEMBER_BYTES
                if m.name not in expected or m.name in seen or not m.isfile() or m.sparse is not None or m.size<0 or m.size>cap:raise ValueError('Snapshot members invalid')
                seen.add(m.name)
                if m.name!='manifest.json':
                    total+=m.size
                    if total>MAX_BYTES:raise ValueError('Snapshot total size exceeds cap')
                member=tar.extractfile(m)
                if member is None:raise ValueError('Snapshot member unavailable')
                if m.name=='manifest.json':
                    manifest=json.loads(member.read(MAX_MANIFEST_BYTES+1));continue
                digest=hashlib.sha256()
                if m.name.endswith('.sqlite3'):
                    p=Path(tmp)/m.name
                    with p.open('xb') as out:
                        while True:
                            b=member.read(1024*1024)
                            if not b:break
                            digest.update(b);out.write(b)
                    p.chmod(0o600)
                    c=sqlite3.connect(p.as_uri()+'?mode=ro',uri=True)
                    try:
                        if c.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Snapshot database integrity invalid')
                    finally:c.close()
                    checks.append(m.name)
                else:
                    b=member.read(33)
                    if m.size!=32 or len(b)!=32:raise ValueError('Rate seed invalid')
                    digest.update(b)
                digests[m.name]=digest.hexdigest()
        # Complete gzip validation and bound any data hidden beyond the tar terminator.
        while bounded.read(1024*1024):pass
    if seen!=expected or not isinstance(manifest,dict) or manifest.get('version')!=1 or manifest.get('sha256')!=digests:raise ValueError('Snapshot manifest or hash invalid')
    return {'database_checks':checks,'authenticated_decrypt':True,'sha256_checks':True,'production_restored':False}

def backup():
    STATE.mkdir(mode=0o700,exist_ok=True);BACKUPS.mkdir(mode=0o700,parents=True,exist_ok=True)
    with _backup_lock():return _backup_locked()

def _backup_locked():
    files={};digests={};total=0
    sizes=[p.stat().st_size for p in SOURCES.values()]
    if any(size>MAX_MEMBER_BYTES for size in sizes) or sum(sizes)>MAX_BYTES:raise ValueError('Snapshot source cap exceeded')
    with tempfile.TemporaryDirectory(prefix='snapshot-',dir=STATE) as tmp:
        for name,source in SOURCES.items():
            if source.stat().st_size>MAX_MEMBER_BYTES:raise ValueError('Database exceeds snapshot cap')
            dest=Path(tmp)/name
            if name.endswith('.sqlite3'):
                c=sqlite3.connect(source.resolve().as_uri()+'?mode=ro',uri=True,timeout=5);d=sqlite3.connect(dest)
                page_size=c.execute('PRAGMA page_size').fetchone()[0]
                started=time.monotonic()
                def progress(status,remaining,pages):
                    if time.monotonic()-started>30:raise TimeoutError('Snapshot busy')
                    if pages*page_size>min(MAX_MEMBER_BYTES,MAX_BYTES-total):raise ValueError('Snapshot cap exceeded')
                try:
                    c.backup(d,pages=128,progress=progress)
                    if d.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('Snapshot database integrity invalid')
                finally:c.close();d.close()
            else:
                b=_read_bounded(source,32)
                if len(b)!=32:raise ValueError('Rate seed invalid')
                dest.write_bytes(b)
            dest.chmod(0o600);size=dest.stat().st_size;total+=size
            if size>MAX_MEMBER_BYTES or total>MAX_BYTES:raise ValueError('Snapshot cap exceeded')
            digest=hashlib.sha256()
            with dest.open('rb') as f:
                for block in iter(lambda:f.read(1024*1024),b''):digest.update(block)
            digests[name]=digest.hexdigest();files[name]=dest
        manifest=json.dumps({'version':1,'created':time.time(),'cross_database_atomic':False,'sha256':digests}).encode()
        if len(manifest)>MAX_MANIFEST_BYTES:raise ValueError('Manifest exceeds cap')
        archive=Path(tmp)/'snapshot.tar.gz'
        with tarfile.open(archive,mode='w:gz',format=tarfile.USTAR_FORMAT) as tar:
            for name,p in files.items():
                info=tarfile.TarInfo(name);info.size=p.stat().st_size;info.mode=0o600
                with p.open('rb') as f:tar.addfile(info,f)
            info=tarfile.TarInfo('manifest.json');info.size=len(manifest);info.mode=0o600;tar.addfile(info,io.BytesIO(manifest))
        encrypted=cipher().encrypt(_read_bounded(archive,_archive_cap()))
        filename='snapshot-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex+'.fernet'
        path=BACKUPS/filename;atomic(path,encrypted)
    try:verification=restore_test(path)
    except Exception:
        path.unlink();_sync_directory(BACKUPS);raise
    # Keep seven recent local snapshots; off-VPS destination is intentionally not guessed.
    report={'created':time.time(),'file':filename,'bytes':path.stat().st_size,'verification':verification,'location':'same_vps','offsite_configured':False}
    atomic(STATE/'last-backup.json',json.dumps(report).encode())
    files=sorted((p for p in BACKUPS.glob('snapshot-*.fernet') if not p.is_symlink() and p.is_file()),key=lambda p:(p==path,p.stat().st_mtime_ns,p.name),reverse=True)
    for p in files[KEEP_SNAPSHOTS:]:p.unlink()
    _sync_directory(BACKUPS);return report

def read_db(path,query):
    c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True,timeout=2)
    try:return c.execute(query).fetchall()
    finally:c.close()

def review_health(data=DATA,now=None):
    now=time.time() if now is None else now
    row=read_db(data/'consultations.sqlite3',"SELECT count(*),min(updated),sum(CASE WHEN attempts>0 THEN 1 ELSE 0 END),max(attempts) FROM review_sync_jobs WHERE status='pending'")[0]
    metrics={'pending':row[0],'seconds_since_oldest_update':max(0,now-row[1]) if row[1] is not None else 0,'retrying':row[2] or 0,'max_attempts':row[3] or 0}
    issues=['review_sync_backlog'] if metrics['pending'] and metrics['seconds_since_oldest_update']>600 else []
    if metrics['max_attempts']>=3:issues.append('review_sync_repeated_failures')
    return metrics,issues

def backup_health(now=None):
    now=time.time() if now is None else now;metrics={};issues=[]
    try:
        result=subprocess.check_output(['systemctl','show','omnisense-backup.service','--property=Result','--value'],text=True,timeout=5).strip()
        metrics['worker_result']=result
        if result!='success':issues.append('backup_worker_failed')
        if subprocess.run(['systemctl','is-active','--quiet','omnisense-backup.timer'],timeout=5).returncode:issues.append('backup_timer_inactive')
    except Exception:issues.append('backup_worker_unavailable')
    try:
        last=json.loads((STATE/'last-backup.json').read_text())
        metrics['seconds_since_success']=max(0,now-last['created'])
        if metrics['seconds_since_success']>30*3600:issues.append('backup_stale')
        filename=last['file']
        if not isinstance(filename,str) or Path(filename).name!=filename or not filename.startswith('snapshot-') or not filename.endswith('.fernet'):raise ValueError('Snapshot report path invalid')
        snapshot=BACKUPS/filename
        if snapshot.is_symlink() or not snapshot.is_file() or snapshot.stat().st_size!=last['bytes']:issues.append('backup_snapshot_unavailable')
    except Exception:issues.append('backup_unavailable')
    return metrics,issues

def monitor():
    settings=json.loads(SETTINGS.read_text());issues=[];metrics={}
    for name,digest in settings['expected_hashes'].items():
        try:
            if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=digest:issues.append('integrity_mismatch')
        except OSError:issues.append('integrity_file_unavailable')
    for unit in ('nginx.service','omnisense-secure-web.service'):
        if subprocess.run(['systemctl','is-active','--quiet',unit]).returncode:issues.append('service_down:'+unit)
    result=subprocess.run(['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user','is-active','--quiet','hermes-gateway.service'])
    if result.returncode:issues.append('service_down:hermes-gateway')
    try:
        review_result=subprocess.check_output(['systemctl','show','omnisense-review-sync.service','--property=Result','--value'],text=True,timeout=5).strip()
        metrics['review_worker_result']=review_result
        if review_result!='success':issues.append('review_sync_worker_failed')
        if subprocess.run(['systemctl','is-active','--quiet','omnisense-review-sync.timer'],timeout=5).returncode:issues.append('review_sync_timer_inactive')
    except Exception:issues.append('review_sync_worker_unavailable')
    free=shutil.disk_usage(STATE).free;metrics['free_disk_bytes']=free
    if free<1024*1024*1024:issues.append('low_disk')
    try:
        import urllib.request
        with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=3) as r:
            if r.status!=200:issues.append('web_health_failure')
    except Exception:issues.append('web_health_failure')
    try:
        metrics['model_outcomes_last_hour']=dict(read_db(DATA/'consultations.sqlite3',"SELECT outcome,count(*) FROM model_telemetry WHERE created>strftime('%s','now')-3600 GROUP BY outcome"))
        metrics['usage_last_hour']=list(read_db(DATA/'consultations.sqlite3',"SELECT sum(total_tokens),sum(cost_usd),count(cost_usd),count(*) FROM model_telemetry WHERE created>strftime('%s','now')-3600")[0])
        total=sum(metrics['model_outcomes_last_hour'].values());bad=sum(metrics['model_outcomes_last_hour'].get(k,0) for k in ('fallback','provider_error'))
        if total>=5 and bad/total>=0.5:issues.append('high_model_fallback_rate')
        metrics['failed_replies_last_hour']=read_db(DATA/'consultations.sqlite3',"SELECT count(*) FROM replies WHERE status='failed' AND created>strftime('%s','now')-3600")[0][0]
        if metrics['failed_replies_last_hour']>=3:issues.append('whatsapp_delivery_failures')
        for n in ('consultations.sqlite3','pipeline.sqlite3','web_security.sqlite3'):
            if read_db(DATA/n,'PRAGMA quick_check')[0][0]!='ok':issues.append('database_check_failed')
    except Exception:issues.append('metrics_unavailable')
    try:
        metrics['review_sync'],review_issues=review_health(DATA)
        issues.extend(review_issues)
    except Exception:issues.append('review_sync_metrics_unavailable')
    metrics['backup'],backup_issues=backup_health();issues.extend(backup_issues)
    report={'checked_at':time.time(),'status':'degraded' if issues else 'ok','issues':sorted(set(issues)),'metrics':metrics,'notification_channel':'local_status_and_journal'}
    STATE.mkdir(mode=0o700,exist_ok=True);atomic(STATE/'status.json',json.dumps(report).encode())
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['backup','monitor','restore-test']);parser.add_argument('--snapshot',type=Path);args=parser.parse_args()
    if os.geteuid()!=0:raise PermissionError('Run as root')
    try:result=backup() if args.action=='backup' else monitor() if args.action=='monitor' else restore_test(args.snapshot)
    except Exception as e:
        print(json.dumps({'status':'failed','exception_type':type(e).__name__}));raise SystemExit(1)
    print(json.dumps(result))
