"""Check installed admin routes using real identity mappings, without sending messages."""
import json,sys
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from dotenv import dotenv_values

CORE=Path('/home/ubuntu/.hermes/hermes-agent')
PLUGIN=Path('/home/ubuntu/.hermes/plugins/omnisense-consultation')
sys.path[:0]=[str(CORE),str(PLUGIN)]
from gateway import omnisense_policy as policy
from gateway.whatsapp_identity import expand_whatsapp_aliases
from gateway.authz_mixin import GatewayAuthorizationMixin
from gateway.config import Platform
from omnisense_wa_security import load_admins,admin_authorized

admins=load_admins();assert len(admins)==3
env=dotenv_values('/home/ubuntu/.hermes/.env')
assert set(env['WHATSAPP_ALLOWED_USERS'].split(','))==set(admins)
assert env.get('WHATSAPP_ALLOW_ALL_USERS','').lower() in ('false','0','no','off','')
assert {n[-4:] for n in admins}=={'4609','5165','0507'}
sets=[expand_whatsapp_aliases(n) for n in admins]
assert all(sets) and all(not sets[i]&sets[j] for i in range(3) for j in range(i))

fn=GatewayAuthorizationMixin._is_user_authorized
runner=NS(_chat_scoped_grant=lambda *a:True,_pairing_store_for=lambda *a:NS(is_approved=lambda *a:True))
def source(sender,chat='dm'):
    return NS(platform=Platform.WHATSAPP,user_id=sender,chat_type=chat,profile=None,role_authorized=True,user_name='Owner')

checks=0
for number,aliases in zip(admins,sets):
    for alias in aliases|{number+':4@s.whatsapp.net'}:
        for chat in ('dm','group'):
            s=source(alias,chat)
            assert fn(runner,s) and admin_authorized(s)
            checks+=1
removed=sys.stdin.read().strip()
assert removed.endswith('2230')
for sender in ('628999999999','999000000000@lid','',removed):
    for chat in ('dm','group'):
        s=source(sender,chat)
        assert not fn(runner,s) and not admin_authorized(s)
        checks+=1
with patch.object(policy,'POLICY',Path('/opt/omnisense-web/nonexistent-admin-policy.json')):
    assert not fn(runner,source(admins[0]));checks+=1
print(json.dumps({'installed_authorization_checks':checks,'admin_count':3,'admin_suffixes':sorted(n[-4:] for n in admins),'removed_2230_denied':True,'pairing_group_role_cannot_elevate':True,'missing_policy_denied':True,'whatsapp_messages_sent':False}))
