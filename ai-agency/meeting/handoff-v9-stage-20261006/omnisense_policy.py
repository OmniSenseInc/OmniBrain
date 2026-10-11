"""Final WhatsApp administrative gate; pairing/group/global grants cannot bypass it."""
import json,os,re
from pathlib import Path

POLICY=Path('/opt/omnisense-web/whatsapp-admin-policy.json')

def whatsapp_admin_authorized(source):
    try:
        if getattr(source,'profile',None) not in (None,'default'):return False
        if getattr(source,'chat_type',None) not in ('dm','group','supergroup'):return False
        sender=getattr(source,'user_id',None)
        if not isinstance(sender,str) or not sender:return False
        st=POLICY.stat()
        if os.name=='posix' and (st.st_uid!=0 or st.st_mode & 0o022):return False
        data=json.loads(POLICY.read_text())
        numbers=data.get('admin_numbers')
        if data.get('version')!=1 or not isinstance(numbers,list) or len(numbers)!=3 or len(set(numbers))!=3 or any(not isinstance(n,str) or not re.fullmatch(r'[1-9][0-9]{7,14}',n) for n in numbers):return False
        from gateway.whatsapp_identity import expand_whatsapp_aliases
        actual=expand_whatsapp_aliases(sender)
        return bool(actual and any(actual & expand_whatsapp_aliases(n) for n in numbers))
    except Exception:
        # No plugin, corrupt policy, invalid identity, unreadable file: deny admin access.
        return False
