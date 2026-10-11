"""Bounded WSGI consultation ingress. Never exposes a client-record read endpoint."""
import base64
import hashlib
import http.cookies
import ipaddress
import json
import logging
import mimetypes
import re
import secrets
import shutil
import threading
import time
from http import HTTPStatus
from pathlib import Path
from urllib.parse import urlsplit, urlencode, quote
from consultation_gateway import CONSENT_VERSION, sanitize
from baca_konsultasi_v3 import unique
from web_limits import RateLedger

LOG = logging.getLogger('omnisense.security')
MAX_BODY = 50000
MAX_ASSET_BYTES = 4*1024*1024


class WebApp:
    def __init__(self, site, store, origins, phone='6288809640700', clock=time.time, trust_tunnel=False, approved_files=None):
        self.site = Path(site).resolve()
        self.approved_files=dict(approved_files or {})
        if any(not re.fullmatch(r'[a-f0-9]{64}',value) for value in self.approved_files.values()):
            raise ValueError('Invalid approved-file hash')
        self.store, self.phone, self.clock = store, phone, clock
        self.origins = frozenset(origins)
        if not self.origins or any(urlsplit(o).scheme not in ('http', 'https') or urlsplit(o).path or urlsplit(o).username for o in self.origins):
            raise ValueError('Explicit origins required')
        self.hosts = {urlsplit(o).netloc for o in self.origins}
        self.trust_tunnel = trust_tunnel
        self.sessions = {}
        self.lock = threading.RLock()
        self.ledger=RateLedger(store.root,clock)
        self.salt = self.ledger.salt
        self.next_prune = 0
        self.max_cases=10000
        self.max_db_bytes=128*1024*1024
        self.min_free_bytes=200*1024*1024

    def client(self, env):
        remote = env.get('REMOTE_ADDR', '')
        # Only the private loopback listener behind our tunnel may supply this.
        # X-Forwarded-For is never used. A same-host/root compromise is out of scope.
        if self.trust_tunnel and remote in ('127.0.0.1', '::1') and env.get('HTTP_HOST', '') in self.hosts:
            supplied = env.get('HTTP_CF_CONNECTING_IP', '')
            try:
                remote = str(ipaddress.ip_address(supplied))
            except ValueError:
                pass
        try:
            address=ipaddress.ip_address(remote)
            remote=str(ipaddress.ip_network(str(address)+'/64',strict=False)) if address.version==6 else str(address)
        except ValueError:
            remote='unknown'
        # Worker requests share a budget; do not use their variable client header.
        if env.get('HTTP_CF_WORKER'):
            remote='worker-subrequest'
        return hashlib.sha256(self.salt + remote.encode()).hexdigest()

    def limited(self, key, category, rules):
        now = self.clock()
        with self.lock:
            if now >= self.next_prune:
                self.sessions = {k:v for k,v in self.sessions.items() if v['expires'] > now}
                self.next_prune = now+60
        return self.ledger.limited(key,category,rules)

    def session(self, env):
        cookie = http.cookies.SimpleCookie()
        try:
            cookie.load(env.get('HTTP_COOKIE',''))
        except http.cookies.CookieError:
            return None
        item = cookie.get('omni_session')
        with self.lock:
            found = self.sessions.get(item.value) if item else None
            return (item.value, found) if found and found['expires'] > self.clock() else None

    def csp(self, nonce=None):
        scripts="'nonce-"+nonce+"'" if nonce else "'none'"
        return "; ".join(["default-src 'none'", "script-src "+scripts, "script-src-attr 'none'", "style-src 'self' 'unsafe-inline'", "img-src 'self' data:", "font-src 'self' data:", "connect-src 'self'", "media-src 'self'", "object-src 'none'", "base-uri 'none'", "frame-ancestors 'none'", "form-action 'self'", "require-trusted-types-for 'script'", "trusted-types 'none'"])

    def protected_html(self,data):
        nonce=secrets.token_urlsafe(32)
        def tag(match):
            attrs=match.group(1)
            src=re.search(rb'\bsrc\s*=\s*([\"\x27])(.*?)\1',attrs,re.I)
            integrity=b''
            if src:
                url=urlsplit(src.group(2).decode('utf-8'))
                path=url.path
                expected=self.approved_files.get(path)
                if url.scheme or url.netloc or not expected or not path.endswith('.js'):
                    raise ValueError('Unapproved script reference')
                sri=base64.b64encode(bytes.fromhex(expected))
                integrity=b' integrity="sha256-'+sri+b'"'
            return b'<script nonce="'+nonce.encode()+b'"'+integrity+attrs+b'>'
        return re.sub(rb'<script\b([^>]*)>',tag,data,flags=re.I),nonce

    def response(self, env, start, status, value=None, data=None, mime='application/json; charset=utf-8', extra=None, html=False):
        if data is None:
            data = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
        nonce=None
        if html:data,nonce=self.protected_html(data)
        headers = [('Content-Type',mime),('Content-Length',str(len(data))),('Cache-Control','no-store' if value is not None or html else 'public, max-age=300'),('X-Content-Type-Options','nosniff'),('Referrer-Policy','no-referrer'),('X-Frame-Options','DENY'),('Content-Security-Policy',self.csp(nonce)),('Permissions-Policy','camera=(), microphone=(), geolocation=(), payment=(), usb=()'),('Cross-Origin-Opener-Policy','same-origin'),('Cross-Origin-Resource-Policy','same-origin')]
        if 'https://'+env.get('HTTP_HOST','') in self.origins:
            headers.append(('Strict-Transport-Security','max-age=86400'))
        headers += extra or []
        start(str(status)+' '+HTTPStatus(status).phrase, headers)
        return [b'' if env.get('REQUEST_METHOD')=='HEAD' else data]

    def error(self, env, start, status, message):
        extra = [('Retry-After','60')] if status==429 else []
        # Fixed status only: no query strings, client IDs, tokens or submitted text.
        if status in (403,413,415,429,503):
            LOG.info('request_rejected status=%s', status)
        return self.response(env,start,status,{'error':message},extra=extra)

    def __call__(self, env, start):
        try:
            return self.dispatch(env,start)
        except Exception:
            LOG.error('request_failed')
            return self.error(env,start,503,'Konsultasi sementara belum tersedia; coba lagi nanti.')

    def dispatch(self, env, start):
        host, method, path = env.get('HTTP_HOST',''), env.get('REQUEST_METHOD',''), env.get('PATH_INFO','')
        if host not in self.hosts:
            return self.error(env,start,400,'Alamat situs tidak valid')
        if method not in ('GET','HEAD','POST'):
            return self.response(env,start,405,{'error':'Metode tidak tersedia'},extra=[('Allow','GET, HEAD, POST')])
        if len(env.get('QUERY_STRING',''))>2048 or len(path)>2048:
            return self.error(env,start,414,'Alamat terlalu panjang')
        local_peer=env.get('REMOTE_ADDR') in ('127.0.0.1','::1')
        local_host=urlsplit('http://'+host).hostname in ('localhost','127.0.0.1','::1')
        private_host=local_peer and local_host
        private_http=private_host and env.get('wsgi.url_scheme')=='http' and 'http://'+host in self.origins
        if path.startswith('/api/') and not private_host and (env.get('wsgi.url_scheme')!='https' or 'https://'+host not in self.origins):
            return self.error(env,start,403,'Konsultasi memerlukan HTTPS dan domain yang terdaftar. Hubungi tim jika belum tersedia.')
        if 'https://'+host in self.origins and env.get('wsgi.url_scheme')!='https':
            if path.startswith('/api/') or method=='POST':
                return self.error(env,start,403,'Gunakan alamat HTTPS untuk konsultasi')
            destination='https://'+host+quote(path or '/',safe='/')
            query=env.get('QUERY_STRING','')
            if query:destination+='?'+quote(query,safe='=&%+:,;/?!@')
            return self.response(env,start,308,{'status':'https_required'},extra=[('Location',destination)])
        if path=='/api/health' and method in ('GET','HEAD'):
            return self.response(env,start,200,{'status':'ok'})
        if path.startswith('/api/') and env.get('HTTP_SEC_FETCH_SITE')=='cross-site':
            return self.error(env,start,403,'Permintaan lintas situs ditolak')
        key = self.client(env)
        if self.limited(key,'requests',[(60,240),(3600,3000)]):
            return self.error(env,start,429,'Terlalu banyak permintaan; coba lagi sebentar')
        if path=='/api/consultation/session' and method=='GET':
            if self.limited(key,'session',[(60,20),(3600,80)]) or self.limited('global','session',[(60,240)]):
                return self.error(env,start,429,'Terlalu banyak permintaan; coba lagi sebentar')
            found = self.session(env)
            if found:
                return self.response(env,start,200,{'csrf':found[1]['csrf'],'consent_version':CONSENT_VERSION})
            sid,csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
            with self.lock:
                if len(self.sessions)>=2000:
                    return self.error(env,start,429,'Coba lagi sebentar')
                self.sessions[sid] = {'csrf':csrf,'expires':self.clock()+1800,'requests':set()}
            secure = '' if private_http else '; Secure'
            cookie = 'omni_session='+sid+'; HttpOnly; SameSite=Strict; Path=/api/consultation; Max-Age=1800'+secure
            return self.response(env,start,200,{'csrf':csrf,'consent_version':CONSENT_VERSION},extra=[('Set-Cookie',cookie)])
        if path=='/api/consultation/cases' and method=='POST':
            if self.limited(key,'post',[(60,12),(3600,40)]) or self.limited('global','post',[(60,120)]):
                return self.error(env,start,429,'Terlalu banyak permintaan; coba lagi sebentar')
            found = self.session(env)
            expected_origin=('http://' if private_http else 'https://')+host
            if not found or env.get('HTTP_ORIGIN')!=expected_origin or expected_origin not in self.origins or not secrets.compare_digest(env.get('HTTP_X_OMNI_CSRF',''),found[1]['csrf']):
                return self.error(env,start,403,'Sesi berubah; muat ulang lalu coba lagi')
            if env.get('CONTENT_TYPE','').split(';')[0].strip().lower()!='application/json' or env.get('HTTP_TRANSFER_ENCODING'):
                return self.error(env,start,415,'Format permintaan tidak valid')
            try:
                length=int(env.get('CONTENT_LENGTH','0'))
            except ValueError:
                length=0
            if not 0<length<=MAX_BODY:
                return self.error(env,start,413,'Permintaan melebihi batas')
            try:
                raw = env['wsgi.input'].read(length)
                if len(raw)!=length:
                    raise ValueError()
                p = json.loads(raw.decode('utf-8'),object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                if not isinstance(p,dict) or set(p)!={'payload','consent','consent_version','request_id'} or p['consent_version']!=CONSENT_VERSION or not isinstance(p['request_id'],str) or not re.fullmatch(r'[A-Za-z0-9_-]{16,80}',p['request_id']):
                    raise ValueError()
                with self.lock:
                    if self.sessions.get(found[0]) is not found[1] or found[1]['expires']<=self.clock():
                        return self.error(env,start,403,'Sesi kedaluwarsa; muat ulang lalu coba lagi')
                    if p['consent'] is not True:raise ValueError()
                    sanitize(p['payload'],self.store.bank)
                    requests = found[1]['requests']
                    if p['request_id'] not in requests and len(requests)>=5:
                        return self.error(env,start,429,'Batas sesi tercapai; coba lagi nanti')
                    if p['request_id'] not in requests:
                        if self.store.path.stat().st_size>=self.max_db_bytes or shutil.disk_usage(self.store.root).free<self.min_free_bytes:
                            return self.error(env,start,503,'Penyimpanan konsultasi sementara penuh; coba lagi nanti.')
                        with self.store.db() as c:
                            if c.execute('SELECT count(*) FROM tickets').fetchone()[0]>=self.max_cases:
                                return self.error(env,start,503,'Kapasitas konsultasi sementara penuh; coba lagi nanti.')
                    result = self.store.create(p['payload'],p['consent'],found[0],p['request_id'])
                    requests.add(p['request_id'])
                message='Halo OmniSense, saya ingin membahas hasil screening. [OMNISENSE-KONSULTASI] '+result['claim_code']
                result['whatsapp_url']='https://wa.me/'+self.phone+'?'+urlencode({'text':message})
                return self.response(env,start,201,result)
            except (ValueError,TypeError,KeyError,UnicodeError,RecursionError,OverflowError):
                return self.error(env,start,400,'Isian atau versi tidak valid. Periksa isian dan muat ulang halaman jika perlu.')
        if path.startswith('/api/') or method=='POST':
            return self.error(env,start,404,'Tidak tersedia')
        # WSGI PATH_INFO is already decoded once. Do not decode a second time.
        relative = path[1:] if path.startswith('/') else ''
        relative = relative or 'index.html'
        parts = Path(relative).parts
        allowed = relative in ('index.html','privacy.html','konsultasi-v3.html','robots.txt','sitemap.xml') or (relative.startswith('assets/') and Path(relative).suffix.lower() in ('.css','.js','.ico','.png','.jpg','.jpeg','.svg','.webp','.woff','.woff2'))
        if not allowed or any(part.startswith('.') for part in parts) or '\\' in relative or '\x00' in relative:
            return self.error(env,start,404,'Tidak tersedia')
        expected=self.approved_files.get(relative)
        if expected is None:
            return self.error(env,start,404,'Tidak tersedia')
        target = self.site/relative
        if any((self.site/Path(*parts[:i])).is_symlink() for i in range(1,len(parts)+1)):
            return self.error(env,start,404,'Tidak tersedia')
        target = target.resolve()
        if self.site not in target.parents or not target.is_file():
            return self.error(env,start,404,'Tidak tersedia')
        if target.stat().st_size>MAX_ASSET_BYTES:
            return self.error(env,start,503,'Aset situs melebihi batas keamanan')
        with target.open('rb') as f:data=f.read(MAX_ASSET_BYTES+1)
        if len(data)>MAX_ASSET_BYTES:
            return self.error(env,start,503,'Aset situs melebihi batas keamanan')
        if not secrets.compare_digest(hashlib.sha256(data).hexdigest(),expected):
            LOG.error('asset_integrity_failed')
            return self.error(env,start,503,'Halaman sementara tidak tersedia; tim sedang memeriksa integritas situs.')
        mime=mimetypes.guess_type(target)[0] or 'application/octet-stream'
        if target.suffix in ('.html','.css','.js','.txt','.xml'):
            mime+='; charset=utf-8'
        return self.response(env,start,200,data=data,mime=mime,html=target.suffix=='.html')
