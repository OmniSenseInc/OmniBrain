"""Root-owned local monitoring and authenticated encrypted SQLite snapshots."""
import argparse,hashlib,io,json,os,shutil,sqlite3,subprocess,tarfile,tempfile,time
from pathlib import Path

SETTINGS=Path('/etc/omnisense-ops/settings.json')
STATE=Path('/var/lib/omnisense-ops')
BACKUPS=Path('/var/backups/omnisense-encrypted')
KEY=Path('/etc/omnisense-ops/backup.key')
DATA=Path('/home/ubuntu/ai-agency/consulting/data')
WA=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/security-state')
SOURCES={'consultations.sqlite3':DATA/'consultations.sqlite3','pipeline.sqlite3':DATA/'pipeline.sqlite3','web_security.sqlite3':DATA/'web_security.sqlite3','wa_security.sqlite3':WA/'wa_security.sqlite3','web-rate-key':DATA/'.web-rate-key','wa-rate-key':WA/'.wa-rate-key'}
MAX_BYTES=256*1024*1024

def atomic(path,data):
    pending=path.with_suffix(path.suffix+'.pending')
    fd=os.open(pending,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
    os.replace(pending,path)

def cipher():
    from cryptography.fernet import Fernet
    st=KEY.stat()
    if st.st_uid!=0 or st.st_mode&0o077:raise PermissionError('Backup key protection invalid')
    return Fernet(KEY.read_bytes())

def restore_test(path):
    payload=cipher().decrypt(path.read_bytes())
    if len(payload)>MAX_BYTES:raise ValueError('Snapshot too large')
    checks=[]
    with tempfile.TemporaryDirectory(prefix='restore-',dir=STATE) as tmp,tarfile.open(fileobj=io.BytesIO(payload),mode='r:gz') as tar:
        members=tar.getmembers()
        if set(m.name for m in members)!=set(SOURCES)|{'manifest.json'} or not all(m.isfile() and m.size<=128*1024*1024 for m in members):raise ValueError('Snapshot members invalid')
        manifest=json.loads(tar.extractfile('manifest.json').read())
        for m in members:
            if m.name=='manifest.json':continue
            b=tar.extractfile(m).read()
            if hashlib.sha256(b).hexdigest()!=manifest['sha256'][m.name]:raise ValueError('Snapshot hash mismatch')
            if m.name.endswith('.sqlite3'):
                p=Path(tmp)/m.name;p.write_bytes(b);p.chmod(0o600)
                c=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
                try:assert c.execute('PRAGMA quick_check').fetchone()[0]=='ok'
                finally:c.close()
                checks.append(m.name)
            elif len(b)!=32:raise ValueError('Rate seed invalid')
    return {'database_checks':checks,'authenticated_decrypt':True,'sha256_checks':True,'production_restored':False}

def backup():
    STATE.mkdir(mode=0o700,exist_ok=True);BACKUPS.mkdir(mode=0o700,parents=True,exist_ok=True)
    chunks={}
    with tempfile.TemporaryDirectory(prefix='snapshot-',dir=STATE) as tmp:
        for name,source in SOURCES.items():
            if source.stat().st_size>128*1024*1024:raise ValueError('Database exceeds snapshot cap')
            if name.endswith('.sqlite3'):
                dest=Path(tmp)/name
                c=sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True,timeout=5);d=sqlite3.connect(dest)
                started=time.monotonic()
                def progress(*args):
                    if time.monotonic()-started>30:raise TimeoutError('Snapshot busy')
                try:c.backup(d,pages=128,progress=progress);assert d.execute('PRAGMA quick_check').fetchone()[0]=='ok'
                finally:c.close();d.close()
                dest.chmod(0o600);chunks[name]=dest.read_bytes()
            else:chunks[name]=source.read_bytes()
        if sum(len(b) for b in chunks.values())>MAX_BYTES:raise ValueError('Snapshot cap exceeded')
        chunks['manifest.json']=json.dumps({'version':1,'created':time.time(),'cross_database_atomic':False,'sha256':{n:hashlib.sha256(b).hexdigest() for n,b in chunks.items()}}).encode()
        stream=io.BytesIO()
        with tarfile.open(fileobj=stream,mode='w:gz') as tar:
            for name,b in chunks.items():
                info=tarfile.TarInfo(name);info.size=len(b);info.mode=0o600;tar.addfile(info,io.BytesIO(b))
        encrypted=cipher().encrypt(stream.getvalue())
        filename='snapshot-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'.fernet'
        path=BACKUPS/filename;atomic(path,encrypted)
    verification=restore_test(path)
    # Keep seven recent local snapshots; off-VPS destination is intentionally not guessed.
    files=sorted(BACKUPS.glob('snapshot-*.fernet'),key=lambda p:p.stat().st_mtime,reverse=True)
    for p in files[7:]:p.unlink()
    report={'created':time.time(),'file':filename,'bytes':path.stat().st_size,'verification':verification,'location':'same_vps','offsite_configured':False}
    atomic(STATE/'last-backup.json',json.dumps(report).encode());return report

def read_db(path,query):
    c=sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True,timeout=2)
    try:return c.execute(query).fetchall()
    finally:c.close()

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
        last=json.loads((STATE/'last-backup.json').read_text())
        if time.time()-last['created']>30*3600:issues.append('backup_stale')
    except Exception:issues.append('backup_unavailable')
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
