"""Realistic regressions for origin configuration mistakes; synthetic data only."""
import unittest,io,json
from test_security import SecurityTests

class TransportTests(SecurityTests):
    # Run only new tests here, without duplicating the inherited baseline suite.
    def test_public_http_session_refused_even_when_origin_configured_http(self):
        self.app.origins=frozenset(['http://omni.test','http://localhost:8080'])
        status,headers,_=self.req('/api/consultation/session',**{'wsgi.url_scheme':'http'})
        self.assertEqual(status,403)
        self.assertNotIn('Set-Cookie',headers)

    def test_public_http_cannot_store_case_even_with_valid_csrf(self):
        self.app.origins=frozenset(['http://omni.test'])
        status,_,_=self.req('/api/consultation/cases','POST',self.body(),HTTP_ORIGIN='http://omni.test',**{'wsgi.url_scheme':'http'})
        self.assertEqual(status,403)
        with self.store.db() as c:self.assertEqual(c.execute('SELECT count(*) FROM tickets').fetchone()[0],0)

    def test_https_cookie_secure_independent_of_origin_configuration(self):
        status,h,_=self.req('/api/consultation/session',HTTP_HOST='localhost:8080',HTTP_COOKIE='')
        self.assertEqual(status,200)
        self.assertIn('; Secure',h['Set-Cookie'])

    def test_public_https_requires_explicit_https_origin(self):
        self.app.origins=frozenset(['http://omni.test'])
        status,h,_=self.req('/api/consultation/session',HTTP_COOKIE='')
        self.assertEqual(status,403)
        self.assertNotIn('Set-Cookie',h)

    def test_http_origin_cannot_authorize_https_case_write(self):
        self.app.origins=frozenset(['http://omni.test','https://omni.test'])
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),HTTP_ORIGIN='http://omni.test')[0],403)

    def test_private_loopback_http_test_flow_preserved(self):
        _,h,b=self.req('/api/consultation/session',HTTP_HOST='localhost:8080',HTTP_COOKIE='',**{'wsgi.url_scheme':'http'})
        self.cookie=h['Set-Cookie'].split(';')[0];self.csrf=json.loads(b)['csrf']
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),HTTP_HOST='localhost:8080',HTTP_ORIGIN='http://localhost:8080',**{'wsgi.url_scheme':'http'})[0],201)

    def test_loopback_host_is_not_exception_for_nonlocal_peer(self):
        self.assertEqual(self.req('/api/consultation/session',HTTP_HOST='localhost:8080',REMOTE_ADDR='192.0.2.90',**{'wsgi.url_scheme':'http'})[0],403)

    def test_empty_origin_cannot_authorize_case_write(self):
        self.assertEqual(self.req('/api/consultation/cases','POST',self.body(),HTTP_ORIGIN='')[0],403)

NAMES=[n for n in TransportTests.__dict__ if n.startswith('test_')]
if __name__=='__main__':
    result=unittest.TextTestRunner().run(unittest.TestSuite(TransportTests(n) for n in NAMES))
    raise SystemExit(not result.wasSuccessful())
