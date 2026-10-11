"""Pure, pinned ingress transformation; preserves TLS and ACME routes."""
import re,shlex

PREVIEW='https://then-farming-finding-undo.trycloudflare.com'
DOMAINS={'omnisense.my.id','www.omnisense.my.id'}
def patch_nginx(text):
    line='    server_name omnisense.my.id www.omnisense.my.id;'
    if text.count(line)!=2 or '$omnisense_cf_peer' in text:raise ValueError('Unexpected nginx baseline')
    if text.count('proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;')!=2:raise ValueError('Unexpected visitor forwarding')
    guards='\n    # Only Cloudflare peers may reach this origin. Keep real socket peer before realip.\n    if ($omnisense_cf_peer = 0) { return 403; }'
    text=text.replace(line,line+guards)
    text=text.replace('proxy_set_header CF-Connecting-IP $http_cf_connecting_ip;','proxy_set_header CF-Connecting-IP $remote_addr;\n        proxy_set_header CF-Worker $omnisense_cf_worker;')
    return text
def patch_unit(text):
    lines=text.splitlines();matches=[i for i,line in enumerate(lines) if line.startswith('ExecStart=')]
    if len(matches)!=1:raise ValueError('Unexpected ExecStart layout')
    i=matches[0];args=shlex.split(lines[i].split('=',1)[1]);out=[];removed=0;n=0
    while n<len(args):
        if args[n]=='--origin':
            value=args[n+1]
            if value==PREVIEW:removed+=1
            else:out.extend(args[n:n+2])
            n+=2
        else:out.append(args[n]);n+=1
    if removed!=1 or not all('https://'+d in out for d in DOMAINS):raise ValueError('Unexpected origin baseline')
    if any(re.search(r'[\s"\x27\\]',value) for value in out):raise ValueError('Unexpected systemd escaping')
    lines[i]='ExecStart='+' '.join(out)
    return '\n'.join(lines)+'\n'
