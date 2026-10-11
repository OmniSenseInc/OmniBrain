import io
import json
import sys
import tempfile
import unittest
import concurrent.futures
import hashlib
from unittest.mock import patch
from pathlib import Path
sys.path.insert(1,str(Path(__file__).resolve().parents[1]/'optimization-v35'/'consulting'))
from consultation_gateway import Store,CONSENT_VERSION
from consultation_web import WebApp


class SecurityTests(unittest.TestCase):
    def setUp(self):
        self.testbase=Path(__file__).resolve().parent/'test-runs'
        self.testbase.mkdir(exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(dir=self.testbase)
        self.root=Path(self.tmp.name)
        self.site=self.root/'site';self.site.mkdir()
        (self.site/'index.html').write_text('<html><script>console.log("ok")</script></html>',encoding='utf-8')
        (self.site/'assets').mkdir()
        (self.site/'assets/x.js').write_text('ok')
        (self.site/'assets/secrets.txt').write_text('private')
        self.now=[1800000000.0]
        self.store=Store(self.root/'data',clock=lambda:self.now[0])
        self.manifest={p.relative_to(self.site).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in self.site.rglob('*') if p.is_file()}
        self.app=WebApp(self.site,self.store,['https://omni.test','http://localhost:8080'],clock=lambda:self.now[0],trust_tunnel=True)
        self.app.approved_files=self.manifest
        self.payload=dict(version=self.store.bank['version'],bank_revision=self.store.bank['bank_revision'],mode='screening',answers={q['id']:{'value':3} for q in self.store.bank['screening']},context={'process':'Laporan mingguan','problem':'Pencarian laporan manual lambat','process_owner':'Operator'})
        status,headers,data=self.req('/api/consultation/session')
        self.cookie=headers['Set-Cookie'].split(';')[0]
        self.csrf=json.loads(data)['csrf']

    def tearDown(self):
        assert self.testbase in self.root.resolve().parents
        self.tmp.cleanup()

    def req(self,path,method='GET',body=None,**override):
        env={'HTTP_HOST':'omni.test','REQUEST_METHOD':method,'PATH_INFO':path,'REMOTE_ADDR':'127.0.0.1','HTTP_CF_CONNECTING_IP':'192.0.2.1','QUERY_STRING':'','wsgi.url_scheme':'https'}
        if body is not None:
            if not isinstance(body,bytes):body=json.dumps(body).encode()
            env.update({'CONTENT_TYPE':'application/json','CONTENT_LENGTH':str(len(body)),'wsgi.input':io.BytesIO(body),'HTTP_ORIGIN':'https://omni.test','HTTP_COOKIE':self.cookie,'HTTP_X_OMNI_CSRF':self.csrf})
        env.update(override)
        response=[]
        def start(status,headers):response.extend([int(status.split()[0]),dict(headers)])
        data=b''.join(self.app(env,start))
        return *response,data

    def body(self,key='x'*32):
        return dict(payload=self.payload,consent=True,consent_version=CONSENT_VERSION,request_id=key)

    def test_success_and_retry_preserve_claim(self):
        first=self.req('/api/consultation/cases','POST',self.body())
        self.assertEqual(first[0],201)
        for _ in range(6):self.assertEqual(self.req('/api/consultation/cases','POST',self.body())[2],first[2])
        self.assertNotIn('Laporan',json.loads(first[2])['whatsapp_url'])

    def test_csrf_and_origin(self):
        for overrides in [{'HTTP_ORIGIN':'https://evil.test'},{'HTTP_X_OMNI_CSRF':'bad'},{'HTTP_COOKIE':''},{'HTTP_ORIGIN':'http://omni.test'},{'HTTP_SEC_FETCH_SITE':'cross-site'}]:
            with self.subTest(overrides=overrides):self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),**overrides)[0],403)

    def test_unknown_host(self):
        self.assertEqual(self.req('/',HTTP_HOST='evil.test')[0],400)

    def test_secure_cookie_and_headers(self):
        _,headers,_=self.req('/api/consultation/session',HTTP_COOKIE='')
        for flag in ['Secure','HttpOnly','SameSite=Strict']:self.assertIn(flag,headers['Set-Cookie'])
        _,headers,_=self.req('/')
        self.assertIn("'nonce-",headers['Content-Security-Policy'])
        self.assertNotIn("'unsafe-inline'",headers['Content-Security-Policy'].split(';')[1])
        self.assertIn("frame-ancestors 'none'",headers['Content-Security-Policy'])
        self.assertEqual(headers['X-Frame-Options'],'DENY')

    def test_no_records_files_or_traversal(self):
        for path in ['/api/consultation/cases/CASE-test','/consultations.sqlite3','/.env','/assets/../index.html','/assets/%2e%2e/index.html','/assets/secrets.txt','/assets/.hidden.js','/assets/../../data/consultations.sqlite3','/assets\\x.js']:
            with self.subTest(path=path):self.assertEqual(self.req(path)[0],404)
        self.assertEqual(self.req('/assets/x.js')[0],200)

    def test_methods(self):
        self.assertEqual(self.req('/','TRACE')[0],405)
        self.assertEqual(self.req('/','HEAD')[2],b'')
        self.assertEqual(self.req('/','POST')[0],404)

    def test_size_type_and_bad_json(self):
        self.assertEqual(self.req('/api/consultation/cases','POST',b' '*50001)[0],413)
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),CONTENT_TYPE='text/plain')[0],415)
        for raw in [b'{"consent":true,"consent":false}',b'[]',b'{"a":NaN}',b'['*2000,b'\xff']:
            with self.subTest(raw=raw[:30]):self.assertEqual(self.req('/api/consultation/cases','POST',raw)[0],400)

    def test_consented_validated_server_result(self):
        p=self.body();p['consent']=False
        self.assertEqual(self.req('/api/consultation/cases','POST',p)[0],400)
        p=self.body();next(iter(p['payload']['answers'].values()))['value']=999
        self.assertEqual(self.req('/api/consultation/cases','POST',p)[0],400)

    def test_quota(self):
        for i in range(5):self.assertEqual(self.req('/api/consultation/cases','POST',self.body(str(i)*32))[0],201)
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body('q'*32))[0],429)

    def test_rate_per_client_and_expiry(self):
        for _ in range(19):self.assertEqual(self.req('/api/consultation/session')[0],200)
        self.assertEqual(self.req('/api/consultation/session')[0],429)
        self.assertEqual(self.req('/api/consultation/session',HTTP_CF_CONNECTING_IP='192.0.2.2')[0],200)
        self.now[0]+=3601
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body())[0],403)
        self.assertEqual(self.req('/api/consultation/session')[0],200)

    def test_forwarded_ip_not_trusted_from_remote_peer(self):
        self.assertEqual(self.app.client({'REMOTE_ADDR':'192.0.2.7','HTTP_HOST':'omni.test','HTTP_CF_CONNECTING_IP':'192.0.2.8'}),self.app.client({'REMOTE_ADDR':'192.0.2.7','HTTP_HOST':'omni.test','HTTP_CF_CONNECTING_IP':'192.0.2.9'}))

    def test_internal_exception_does_not_leak(self):
        self.store.create=lambda *args:(_ for _ in ()).throw(RuntimeError('SECRET-DO-NOT-LEAK'))
        status,_,data=self.req('/api/consultation/cases','POST',self.body())
        self.assertEqual(status,503);self.assertNotIn(b'SECRET',data)

    def test_expiry_rechecked_after_body_read(self):
        class ExpiringBody(io.BytesIO):
            def read(inner,n):
                self.now[0]+=1801
                return super(ExpiringBody,inner).read(n)
        raw=json.dumps(self.body()).encode()
        status,_,_=self.req('/api/consultation/cases','POST',raw,**{'wsgi.input':ExpiringBody(raw)})
        self.assertEqual(status,403)
        with self.store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],0)

    def test_ipv6_rotation_does_not_reset_client_identity(self):
        base={'REMOTE_ADDR':'127.0.0.1','HTTP_HOST':'omni.test'}
        self.assertEqual(self.app.client({**base,'HTTP_CF_CONNECTING_IP':'2001:db8:1:2::1'}),self.app.client({**base,'HTTP_CF_CONNECTING_IP':'2001:db8:1:2::999'}))
        self.assertNotEqual(self.app.client({**base,'HTTP_CF_CONNECTING_IP':'2001:db8:1:2::1'}),self.app.client({**base,'HTTP_CF_CONNECTING_IP':'2001:db8:1:3::1'}))

    def test_rate_limit_survives_restart(self):
        for _ in range(19):self.assertEqual(self.req('/api/consultation/session')[0],200)
        self.assertEqual(self.req('/api/consultation/session')[0],429)
        self.app=WebApp(self.site,self.store,['https://omni.test'],clock=lambda:self.now[0],trust_tunnel=True)
        self.assertEqual(self.req('/api/consultation/session')[0],429)

    def test_capacity_blocks_new_case_preserves_existing_retry(self):
        self.app.max_cases=1
        first=self.req('/api/consultation/cases','POST',self.body())
        self.assertEqual(first[0],201)
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body('new-case-'*4))[0],503)
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body())[2],first[2])
        with self.store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)

    def test_low_disk_space_blocks_write(self):
        from collections import namedtuple
        usage=namedtuple('usage','total used free')(100,100,0)
        with patch('consultation_web.shutil.disk_usage',return_value=usage):
            self.assertEqual(self.req('/api/consultation/cases','POST',self.body())[0],503)
        with self.store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],0)

    def test_worker_subrequest_does_not_rotate_identity(self):
        base={'REMOTE_ADDR':'127.0.0.1','HTTP_HOST':'omni.test','HTTP_CF_WORKER':'test.example'}
        self.assertEqual(self.app.client({**base,'HTTP_CF_CONNECTING_IP':'192.0.2.1'}),self.app.client({**base,'HTTP_CF_CONNECTING_IP':'192.0.2.99'}))

    def test_ledger_atomic_across_app_instances(self):
        other=WebApp(self.site,self.store,['https://omni.test'],clock=lambda:self.now[0])
        def attempt(i):return (self.app if i%2 else other).limited('test-client','concurrent',[(60,5)])
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            denied=list(pool.map(attempt,range(20)))
        self.assertEqual(denied.count(False),5)
        self.assertTrue(self.app.limited('test-client','concurrent',[(60,5)]))

    def test_strict_utf8_json(self):
        raw=json.dumps(self.body()).encode('utf-16')
        self.assertEqual(self.req('/api/consultation/cases','POST',raw)[0],400)

    def test_public_http_redirect_and_api_refusal(self):
        status,h,_=self.req('/konsultasi-v3.html',**{'wsgi.url_scheme':'http'})
        self.assertEqual(status,308);self.assertEqual(h['Location'],'https://omni.test/konsultasi-v3.html')
        self.assertEqual(self.req('/api/consultation/session',**{'wsgi.url_scheme':'http'})[0],403)
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),**{'wsgi.url_scheme':'http'})[0],403)
        status,h,_=self.req('/bad\r\nheader',QUERY_STRING='x=\r\nInjected:value',**{'wsgi.url_scheme':'http'})
        self.assertNotIn('\r',h['Location']);self.assertNotIn('\n',h['Location'])

    def test_loopback_health_keeps_working(self):
        self.assertEqual(self.req('/api/health',HTTP_HOST='localhost:8080',**{'wsgi.url_scheme':'http'})[0],200)

    def test_sql_text_is_never_executed(self):
        payload=self.body()
        payload['payload']['context']['problem']="Laporan manual lambat '; DROP TABLE tickets; --"
        self.assertEqual(self.req('/api/consultation/cases','POST',payload)[0],201)
        with self.store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],1)

    def test_altered_html_not_automatically_trusted(self):
        p=self.site/'index.html'
        p.write_text(p.read_text()+'<script src="https://spam.example/inject.js"></script>')
        self.assertEqual(self.req('/')[0],503)

    def test_new_unapproved_asset_is_not_served(self):
        (self.site/'assets/inserted.js').write_text('malicious content')
        self.assertEqual(self.req('/assets/inserted.js')[0],404)

    def test_nonce_changes_and_no_self_script_permission(self):
        _,h1,b1=self.req('/');_,h2,b2=self.req('/')
        self.assertNotEqual(h1['Content-Security-Policy'],h2['Content-Security-Policy'])
        self.assertIn(b'<script nonce=',b1)
        self.assertNotIn("'self'",h1['Content-Security-Policy'].split(';')[1])
        self.assertIn("require-trusted-types-for 'script'",h1['Content-Security-Policy'])

    def test_external_script_integrity(self):
        p=self.site/'index.html';p.write_text('<script src="assets/x.js"></script>')
        self.app.approved_files['index.html']=hashlib.sha256(p.read_bytes()).hexdigest()
        status,h,data=self.req('/')
        self.assertEqual(status,200);self.assertIn(b'integrity="sha256-',data)

    def test_large_even_approved_asset_is_bounded(self):
        data=b'x'*(4*1024*1024+1)
        p=self.site/'assets/large.js';p.write_bytes(data)
        self.app.approved_files['assets/large.js']=hashlib.sha256(data).hexdigest()
        self.assertEqual(self.req('/assets/large.js')[0],503)

if __name__=='__main__':unittest.main()
