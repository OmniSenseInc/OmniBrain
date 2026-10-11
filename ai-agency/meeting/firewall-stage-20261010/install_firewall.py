"""CF-only TCP web ports with unchanged SSH and a five-minute root rollback timer."""
from pathlib import Path
import fcntl,hashlib,http.client,ipaddress,json,os,re,stat,subprocess,sys,time
from fw_rules import parse,baseline,validate,ssh,global_web
from rollback_firewall import restore

S=Path(__file__).resolve().parent;CFG=Path('/etc/omnisense-ops/settings.json')
FILES=[Path('/etc/ufw/user.rules'),Path('/etc/ufw/user6.rules'),Path('/etc/ufw/ufw.conf'),CFG]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,timeout=30):return subprocess.run(args,check=True,capture_output=True,text=True,timeout=timeout).stdout
def rows():return parse(run(['ufw','status','numbered']))
def health():
    checks=[]
    for host,path in [('omnisense.my.id','/'),('www.omnisense.my.id','/'),('omnisense.my.id','/api/consultation/session')]:
        c=http.client.HTTPSConnection(host,timeout=15)
        try:
            c.request('GET',path);r=c.getresponse();body=r.read(1000000)
            if r.status!=200 or not r.getheader('CF-Ray'):raise RuntimeError('Public Cloudflare health failed')
            if path.endswith('/session'):
                payload=json.loads(body);cookie=r.getheader('Set-Cookie','')
                if not isinstance(payload.get('csrf'),str) or not all(v in cookie for v in ['Secure','HttpOnly','SameSite=Strict']):raise RuntimeError('Session verification failed')
            checks.append({'host':host,'path':path,'status':r.status})
        finally:c.close()
    return checks
def atomic(p,b,uid,gid,mode):
    q=p.with_name(p.name+'.firewall-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
    with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
assert os.geteuid()==0
snapshot=S/'cloudflare-ip-snapshot.json';assert sha(snapshot)=='ffcb145c84a179b43278491fe9fd6f229383961ea72d1da8b2bfbc462ba068c6'
networks={str(ipaddress.ip_network(n)) for n in json.loads(snapshot.read_text())['networks']};assert len(networks)==22
if len(sys.argv)==3 and sys.argv[1]=='--commit':
    B=Path(sys.argv[2]);assert B.parent==Path('/home/ubuntu/ai-agency/backups') and B.name.startswith('firewall-20261010-')
    with (B/'transaction.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX);report=json.loads((B/'candidate.json').read_text())
        if (B/'rolled-back').exists() or time.time()>=report['rollback_deadline']-30:raise RuntimeError('Rollback expired or too close')
        assert all(sha(Path(p))==h for p,h in report['file_hashes'].items())
        original={tuple(x) for x in report['ssh_before']};validate(rows(),networks,original)
        assert run(['systemctl','is-active',report['rollback_unit']+'.timer']).strip()=='active'
        checks=health()
        run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','monitor'])
        assert json.loads(Path('/var/lib/omnisense-ops/status.json').read_text())['status']=='ok'
        (B/'committed').write_text('confirmed by fresh SSH after external web-port tests\n')
        run(['systemctl','stop',report['rollback_unit']+'.timer'])
        report.update(committed=True,fresh_ssh_login_confirmed=True,final_health=checks)
        (B/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps({'committed':True,'backup':str(B),'cf_network_count':22,'ssh_preserved':True,'monitor':'ok','public_routes_200':3}))
    raise SystemExit(0)
if len(sys.argv)!=1:raise ValueError('Unexpected arguments')
initial=rows();baseline(initial)
defaults=Path('/etc/default/ufw').read_text()
assert re.search(r'^DEFAULT_INPUT_POLICY="DROP"',defaults,re.M) and re.search(r'^IPV6=yes',defaults,re.M)
settings=json.loads(CFG.read_text())
for p in FILES[:3]:
    if str(p) in settings['expected_hashes']:assert settings['expected_hashes'][str(p)]==sha(p)
health()
for version in [4,6]:
    n=next(n for n in sorted(networks) if ipaddress.ip_network(n).version==version)
    run(['ufw','--dry-run','allow','proto','tcp','from',n,'to','any','port','80,443','comment','OmniSense Cloudflare web'])
subprocess.run(['/usr/bin/python3','-m','unittest','test_fw_rules'],cwd=S,check=True,timeout=30)
B=Path('/home/ubuntu/ai-agency/backups')/('firewall-20261010-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));B.mkdir(mode=0o700);metadata={}
for i,p in enumerate(FILES):
    st=p.stat();q=B/str(i);q.write_bytes(p.read_bytes());q.chmod(0o600)
    metadata[str(p)]={'file':str(i),'uid':st.st_uid,'gid':st.st_gid,'mode':stat.S_IMODE(st.st_mode)}
(B/'before.json').write_text(json.dumps(metadata));(B/'rollback_firewall.py').write_bytes((S/'rollback_firewall.py').read_bytes());(B/'rollback_firewall.py').chmod(0o700)
unit='omnisense-fw-rollback-'+str(int(time.time()))
run(['systemd-run','--unit='+unit,'--on-active=300s','--timer-property=AccuracySec=1s','/usr/bin/python3',str(B/'rollback_firewall.py'),str(B)])
deadline=time.time()+300
try:
    for n in sorted(networks):run(['ufw','allow','proto','tcp','from',n,'to','any','port','80,443','comment','OmniSense Cloudflare web'])
    # Re-read after each deletion; never rely on indices after any rule removal.
    for _ in range(4):
        current=rows();assert ssh(current)==ssh(initial)
        indices=global_web(current)
        if not indices:break
        run(['ufw','--force','delete',str(max(indices))])
    validate(rows(),networks,ssh(initial));checks=health()
    for p in FILES[:3]:settings['expected_hashes'][str(p)]=sha(p)
    st=CFG.stat();atomic(CFG,json.dumps(settings,indent=2).encode(),st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))
    run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','monitor'])
    assert json.loads(Path('/var/lib/omnisense-ops/status.json').read_text())['status']=='ok'
except Exception:
    restore(B);run(['systemctl','stop',unit+'.timer']);raise
report={'version':'firewall-20261010','backup':str(B),'rollback_unit':unit,'rollback_deadline':deadline,'ssh_before':sorted(ssh(initial)),'file_hashes':{str(p):sha(p) for p in FILES},'candidate_health':checks,'cf_network_count':22,'committed':False,'no_ssh_auth_or_client_data_changes':True}
(B/'candidate.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'await_external_verification':True,'backup':str(B),'rollback_unit':unit,'rollback_in_seconds':int(deadline-time.time()),'public_routes_200':len(checks),'cf_network_count':22,'ssh_rules_preserved':True}))
