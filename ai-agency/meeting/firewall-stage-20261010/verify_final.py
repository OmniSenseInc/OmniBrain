"""Read-only final status and synthetic auth regressions; no messages or PII."""
from pathlib import Path
import hashlib,ipaddress,json,subprocess
from fw_rules import parse,validate

B=Path('/home/ubuntu/ai-agency/backups/firewall-20261010-20261009T203748Z')
S=Path(__file__).resolve().parent
report=json.loads((B/'deployment.json').read_text())
assert report['committed'] and (B/'committed').exists() and not (B/'rolled-back').exists()
assert subprocess.run(['systemctl','is-active','--quiet',report['rollback_unit']+'.timer']).returncode!=0
networks={str(ipaddress.ip_network(n)) for n in json.loads((S/'cloudflare-ip-snapshot.json').read_text())['networks']}
current=parse(subprocess.check_output(['ufw','status','numbered'],text=True));validate(current,networks,{tuple(x) for x in report['ssh_before']})
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in report['file_hashes'].items())
policy=json.loads(Path('/opt/omnisense-web/whatsapp-admin-policy.json').read_text());numbers=policy['admin_numbers']
assert len(set(numbers))==len(numbers)==3 and {n[-4:] for n in numbers}=={'4609','5165','0507'}
CORE=Path('/home/ubuntu/.hermes/hermes-agent')
auth=CORE/'gateway/authz_mixin.py'
assert hashlib.sha256(auth.read_bytes()).hexdigest()=='643c723bd7e15974ad44ce7281a087c2a423223dc37d017b7020c34d42dbc500'
tests=Path('/home/ubuntu/ai-agency/meeting/all-in-v11-stage-20261007')
assert (tests/'authz_mixin.py').read_bytes()==auth.read_bytes()
subprocess.run(['runuser','-u','ubuntu','--',str(CORE/'venv/bin/python'),'-m','unittest','test_wa_security','test_core_authorization'],cwd=tests,check=True,timeout=45)
for unit in ['nginx.service','omnisense-secure-web.service','fail2ban.service','omnisense-monitor.timer']:
    assert subprocess.run(['systemctl','is-active','--quiet',unit]).returncode==0
ctl=['runuser','-u','ubuntu','--','env','XDG_RUNTIME_DIR=/run/user/1000','systemctl','--user']
assert subprocess.run(ctl+['is-active','--quiet','hermes-gateway.service']).returncode==0
assert subprocess.run(ctl+['is-active','--quiet','omnisense-preview-tunnel.service']).returncode!=0
subprocess.run(['/usr/bin/python3','/opt/omnisense-ops/omnisense_ops.py','monitor'],check=True,timeout=30)
assert json.loads(Path('/var/lib/omnisense-ops/status.json').read_text())['status']=='ok'
print(json.dumps({'firewall_committed':True,'rollback_timer_stopped':True,'cf_networks':len(networks),'ufw_rule_count':len(current),'admin_suffixes':sorted(n[-4:] for n in numbers),'auth_source_unchanged':True,'synthetic_auth_tests':23,'services_active':True,'old_preview_inactive':True,'monitor':'ok','whatsapp_messages_sent':False}))
