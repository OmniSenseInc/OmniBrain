"""Close direct origin/preview ingress; pinned files, root backup and rollback."""
from pathlib import Path
import hashlib,http.client,ipaddress,json,os,re,ssl,stat,subprocess,time,urllib.request
from ingress_patch import patch_nginx,patch_unit,PREVIEW

assert os.geteuid()==0
S=Path(__file__).resolve().parent
SITE=Path('/etc/nginx/sites-available/omnisense.conf');TRUST=Path('/etc/nginx/conf.d/omnisense-trusted-proxy.conf');UNIT=Path('/etc/systemd/system/omnisense-secure-web.service');CFG=Path('/etc/omnisense-ops/settings.json')
sha=lambda b:hashlib.sha256(b).hexdigest()
pins={SITE:'3c73c9fb87971214d88375ea8bdaf54aa2f8e6b94416b90c75a03311143123c9',TRUST:'82ad46ca83cfbc78ec6cc967eb67923cab06c766b214ee7c592f88034173b0ac',UNIT:'e101343955e438a1f5a99e3cb9753e407bbad71b8dfd9c4d94a7f7fb2cb26497'}
assert all(len(h)==64 for h in pins.values())
for p,h in pins.items():assert sha(p.read_bytes())==h
# Verified against both official Cloudflare endpoints in the Codex web tool.
# VPS endpoint returned 403; do not weaken TLS or infer a list from that response.
snapshot=(S/'cloudflare-ip-snapshot.json').read_bytes()
assert sha(snapshot)=='ffcb145c84a179b43278491fe9fd6f229383961ea72d1da8b2bfbc462ba068c6'
published=json.loads(snapshot)
assert published['verified_client_date']=='2026-10-10'
official={str(ipaddress.ip_network(line)) for line in published['networks']}
assert len(official)>=20 and len(official)<=40
trusted={str(ipaddress.ip_network(n)) for n in re.findall(r'set_real_ip_from\s+([^;]+);',TRUST.read_text())}
geo={str(ipaddress.ip_network(n)) for n in re.findall(r'^\s*([\da-fA-F:./]+)\s+1;',TRUST.read_text(),re.M)}
assert trusted==geo==official and 'geo $realip_remote_addr $omnisense_cf_peer' in TRUST.read_text()
subprocess.run(['/usr/bin/python3','-m','unittest','test_ingress_patch'],cwd=S,check=True,timeout=20)
subprocess.run(['nginx','-t'],check=True,capture_output=True)
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
tunnel='omnisense-preview-tunnel.service'
was_active=subprocess.run(ctl+['is-active','--quiet',tunnel]).returncode==0
was_enabled=subprocess.run(ctl+['is-enabled','--quiet',tunnel]).returncode==0
mapping={SITE:patch_nginx(SITE.read_text()).encode(),UNIT:patch_unit(UNIT.read_text()).encode()}
settings=json.loads(CFG.read_text())
for p in mapping:
    if str(p) in settings['expected_hashes']:assert settings['expected_hashes'][str(p)]==sha(p.read_bytes());settings['expected_hashes'][str(p)]=sha(mapping[p])
# Existing local monitor also watches reviewed ingress and origin allowlist drift.
for p in [SITE,UNIT]:settings['expected_hashes'][str(p)]=sha(mapping[p])
settings['expected_hashes'][str(TRUST)]=pins[TRUST]
mapping[CFG]=json.dumps(settings,indent=2).encode()
backup=Path('/home/ubuntu/ai-agency/backups')/('ingress-20261010-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime()));backup.mkdir(mode=0o700);before={}
for i,p in enumerate(mapping):
    st=p.stat();before[p]=(p.read_bytes(),st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode));q=backup/str(i);q.write_bytes(before[p][0]);q.chmod(0o600)
(backup/'paths.json').write_text(json.dumps([str(p) for p in before]))
def put(p,b,uid,gid,mode):
    q=p.with_name(p.name+'.ingress-pending');fd=os.open(q,os.O_WRONLY|os.O_CREAT|os.O_EXCL,mode)
    with os.fdopen(fd,'wb') as f:f.write(b);f.flush();os.fsync(f.fileno())
    os.chown(q,uid,gid);q.chmod(mode);os.replace(q,p)
def probe(host,path,connect=None,headers=None):
    c=http.client.HTTPSConnection(host,timeout=15)
    if connect:
        import socket
        c.sock=ssl.create_default_context().wrap_socket(socket.create_connection((connect,443),timeout=15),server_hostname=host)
    try:
        c.request('GET',path,headers={'Host':host,**(headers or {})});r=c.getresponse();body=r.read(1500000)
        return r.status,dict((k.lower(),v) for k,v in r.getheaders())
    finally:c.close()
checks=[]
try:
    for p,b in mapping.items():put(p,b,*before[p][1:])
    subprocess.run(['nginx','-t'],check=True,capture_output=True)
    subprocess.run(['systemd-analyze','verify',str(UNIT)],check=True,capture_output=True)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    subprocess.run(['systemctl','reload','nginx.service'],check=True)
    subprocess.run(ctl+['disable','--now',tunnel],check=True,timeout=45)
    subprocess.run(['systemctl','restart','omnisense-secure-web.service'],check=True,timeout=45)
    for _ in range(15):
        try:
            with urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=2) as r:assert r.status==200
            break
        except Exception:time.sleep(1)
    else:raise RuntimeError('Loopback health failed')
    for host in ['omnisense.my.id','www.omnisense.my.id']:
        status,h=probe(host,'/');assert status==200 and 'cf-ray' in h;checks.append({'check':'public_home','host':host,'status':status})
    for path in ['/konsultasi-v3.html','/privacy.html','/api/consultation/session']:
        status,h=probe('omnisense.my.id',path);assert status==200;checks.append({'check':'public_path','path':path,'status':status})
    for headers in [{},{'CF-Connecting-IP':'203.0.113.77','CF-Ray':'forged','X-Forwarded-Proto':'https'},{'CF-Connecting-IP':'198.51.100.55','CF-Worker':'omnisense.my.id'}]:
        status,h=probe('omnisense.my.id','/api/consultation/session',connect='43.153.194.210',headers=headers);assert status==403;checks.append({'check':'origin_rejected','status':status})
    c=http.client.HTTPConnection('43.153.194.210',80,timeout=10)
    try:
        c.request('GET','/api/consultation/session',headers={'Host':'omnisense.my.id','CF-Connecting-IP':'203.0.113.88','CF-Ray':'forged'});r=c.getresponse();r.read();assert r.status==403;checks.append({'check':'http_origin_rejected','status':r.status})
    finally:c.close()
    assert subprocess.run(ctl+['is-active','--quiet',tunnel]).returncode!=0
    assert subprocess.run(ctl+['is-enabled','--quiet',tunnel]).returncode!=0
    subprocess.run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','monitor'],check=True,timeout=30)
    assert json.loads(Path('/var/lib/omnisense-ops/status.json').read_text())['status']=='ok'
except Exception:
    for p,v in before.items():put(p,*v)
    subprocess.run(['systemctl','daemon-reload'],check=True);subprocess.run(['nginx','-t'],check=True,capture_output=True);subprocess.run(['systemctl','reload','nginx.service'],check=True);subprocess.run(['systemctl','restart','omnisense-secure-web.service'],check=True)
    if was_enabled:subprocess.run(ctl+['enable',tunnel],check=True)
    if was_active:subprocess.run(ctl+['start',tunnel],check=True)
    raise
report={'version':'ingress-20261010','backup':str(backup),'hashes':{str(p):sha(p.read_bytes()) for p in [SITE,UNIT]},'official_cloudflare_networks':len(official),'checks':checks,'old_preview_disabled':True,'preview_origin_removed':PREVIEW not in UNIT.read_text(),'ingress_hashes_monitored':True,'ssh_and_firewall_unchanged':True,'no_client_cases_or_whatsapp_messages':True}
(backup/'deployment.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
