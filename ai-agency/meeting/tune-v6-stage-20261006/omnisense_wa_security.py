"""Pinned admin identity and persistent consultation admission; no message bodies."""
import hashlib,json,re,os,time
from pathlib import Path
from wa_limits import RateLedger

POLICY=Path('/opt/omnisense-web/whatsapp-admin-policy.json')

def load_admins(path=POLICY):
    p=Path(path)
    if os.name=='posix':
        st=p.stat()
        if st.st_uid!=0 or st.st_mode & 0o022:raise ValueError('Unsafe admin policy ownership')
    d=json.loads(p.read_text())
    ids=d.get('admin_numbers')
    if d.get('version')!=1 or not isinstance(ids,list) or len(ids)!=3 or len(set(ids))!=3 or any(not isinstance(x,str) or not re.fullmatch(r'[1-9][0-9]{7,14}',x) for x in ids):
        raise ValueError('Exactly three approved numbers required')
    return tuple(ids)

def admin_authorized(source,numbers=None):
    if getattr(source,'profile',None) not in (None,'default'):return False
    value=getattr(source,'user_id',None)
    if not isinstance(value,str) or not value:return False
    if getattr(source,'chat_type',None) not in ('dm','group','supergroup'):return False
    from gateway.whatsapp_identity import expand_whatsapp_aliases
    candidate=expand_whatsapp_aliases(value)
    return bool(candidate and any(candidate & expand_whatsapp_aliases(n) for n in (numbers or load_admins())))

class Admission:
    def __init__(self,root,clock=time.time):
        self.root=Path(root);self.root.mkdir(mode=0o700,parents=True,exist_ok=True)
        self.ledger=RateLedger(self.root,clock)

    def allow(self,principal):
        key=hashlib.sha256(self.ledger.salt+principal.encode()).hexdigest()
        if self.ledger.limited(key,'wa_ingress',[(60,10),(3600,60)]):return False
        return not self.ledger.limited('wa_global','wa_ingress',[(60,120),(3600,1000)])
