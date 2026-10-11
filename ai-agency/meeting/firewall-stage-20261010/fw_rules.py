"""Fail-closed interpretation of UFW inbound rules; no shell string construction."""
import ipaddress,re

def parse(text):
    if not text.startswith('Status: active'):raise ValueError('UFW inactive')
    rows=[]
    for line in text.splitlines():
        if not line.startswith('['):continue
        m=re.fullmatch(r'\[\s*(\d+)\]\s+(.*?)\s+(ALLOW|LIMIT|DENY|REJECT)\s+IN\s+(.*?)(?:\s+#.*)?',line)
        if not m:raise ValueError('Unsupported rule layout')
        n,dest,action,src=m.groups();v6='(v6)' in dest or '(v6)' in src
        source=src.replace('(v6)','').strip()
        if source!='Anywhere':
            family=ipaddress.ip_network(source).version
            if v6 and family!=6:raise ValueError('Conflicting family marker')
            v6=family==6
        rows.append({'n':int(n),'dest':dest.replace('(v6)','').strip(),'action':action,'source':source,'v6':v6})
    return rows
def ssh(rows):return {(r['dest'],r['action'],r['source'],r['v6']) for r in rows if r['dest']=='22/tcp'}
def global_web(rows):return [r['n'] for r in rows if r['dest'] in ('80/tcp','443/tcp','80,443/tcp') and r['action']=='ALLOW' and r['source']=='Anywhere']
def baseline(rows):
    wanted={('22/tcp','LIMIT','Anywhere',False),('22/tcp','LIMIT','Anywhere',True)}
    if len(rows)!=6 or len(global_web(rows))!=4 or ssh(rows)!=wanted:raise ValueError('Unexpected firewall baseline')
def validate(rows,networks,original_ssh):
    if ssh(rows)!=original_ssh or global_web(rows):raise ValueError('SSH changed or web still global')
    seen=set()
    for r in rows:
        if r['dest']=='22/tcp':continue
        if r['dest']!='80,443/tcp' or r['action']!='ALLOW':raise ValueError('Unexpected extra rule')
        net=ipaddress.ip_network(r['source']);cidr=str(net)
        if cidr not in networks or (net.version==6)!=r['v6'] or cidr in seen:raise ValueError('Unexpected network or duplicate')
        seen.add(cidr)
    if seen!=networks:raise ValueError('Missing Cloudflare network')
