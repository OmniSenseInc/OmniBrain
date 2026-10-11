"""Execute the installed authorization method against hostile grants, without a gateway."""
import ast,enum,sys,unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch
from test_wa_security import ADMINS,CLIENT,FakePolicy,core_policy,source

HERE=Path(__file__).resolve().parent
sys.modules['gateway.omnisense_policy']=core_policy
class Platform(enum.Enum):
    WHATSAPP='whatsapp';HOMEASSISTANT='ha';WEBHOOK='webhook';TELEGRAM='telegram'

def method(path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='_is_user_authorized')
    g={'Platform':Platform,'SessionSource':NS,'_GROUP_CHAT_TYPES':{'group'},'_GROUP_FORUM_TYPES':{'group'},'_ALLOWED_USERS_ENV':{Platform.WHATSAPP:'WHATSAPP_ALLOWED_USERS'},'_ALLOW_ALL_ENV':{Platform.WHATSAPP:'WHATSAPP_ALLOW_ALL_USERS'},'_GROUP_USER_ENV':{},'_GROUP_CHAT_ENV':{},'_env_truthy':lambda k:False}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),g)
    return g['_is_user_authorized'],g

class AuthorizationTests(unittest.TestCase):
    def setUp(self):
        self.fn,self.globals=method(HERE/'authz_mixin.py')
        self.runner=NS(_adapter_profile_for_source=lambda s:None,_chat_scoped_grant=lambda *a:False,_pairing_store_for=lambda s:NS(is_approved=lambda *a:True))
        self.person=source();self.person.platform=Platform.WHATSAPP;self.person.role_authorized=False
        self.policy=patch.object(core_policy,'POLICY',FakePolicy());self.policy.start();self.addCleanup(self.policy.stop)
    def test_pairing_approval_is_not_administrator(self):
        self.assertFalse(self.fn(self.runner,self.person))
    def test_group_chat_grant_is_not_administrator(self):
        self.person.chat_type='group';self.runner._chat_scoped_grant=lambda *a:True
        self.assertFalse(self.fn(self.runner,self.person))
    def test_platform_allow_all_is_not_administrator(self):
        self.globals['_env_truthy']=lambda k:True
        self.assertFalse(self.fn(self.runner,self.person))
    def test_role_flag_is_not_administrator(self):
        self.person.role_authorized=True
        self.assertFalse(self.fn(self.runner,self.person))
    def test_exact_three_admins_in_dm_and_group(self):
        for number in ADMINS:
            for chat_type in ['dm','group']:
                self.person.user_id=number;self.person.chat_type=chat_type
                self.assertTrue(self.fn(self.runner,self.person))
    def test_missing_policy_denies_admin_even_without_plugin(self):
        self.person.user_id=ADMINS[0]
        with patch.object(core_policy,'POLICY',HERE/'missing-policy.json'):
            self.assertFalse(self.fn(self.runner,self.person))
    def test_original_code_accepted_historical_bypass(self):
        fn,g=method(HERE/'core/gateway/authz_mixin.py')
        self.person.chat_type='group';self.runner._chat_scoped_grant=lambda *a:True
        self.assertTrue(fn(self.runner,self.person))

if __name__=='__main__':unittest.main()
