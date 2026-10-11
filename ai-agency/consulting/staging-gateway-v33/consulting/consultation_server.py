"""Same-origin quiz API and allowlisted preview assets; loopback bind only."""
import argparse
import http.cookies
import json
import mimetypes
import secrets
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit, unquote, urlencode
from consultation_gateway import Store, CONSENT_VERSION, digest
from baca_konsultasi_v3 import unique


def make_handler(site, store, phone='6288809640700'):
    site = Path(site).resolve()
    sessions, rates = {}, {}
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        server_version = 'OmniSense'
        protocol_version = 'HTTP/1.0'

        def log_message(self, *args):
            pass  # No claim tokens, bodies, phone numbers or cookie headers in logs.

        def json(self, status, value, cookie=None):
            blob = json.dumps(value, ensure_ascii=False, allow_nan=False).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(blob)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            if cookie:
                self.send_header('Set-Cookie',cookie)
            self.end_headers()
            self.wfile.write(blob)

        def session(self):
            cookie=http.cookies.SimpleCookie()
            try:
                cookie.load(self.headers.get('Cookie',''))
            except http.cookies.CookieError:
                return None
            sid=cookie.get('omni_session')
            with lock:
                s=sessions.get(sid.value) if sid else None
                return (sid.value,s) if s and s['expires']>time.time() else None

        def limited(self):
            # One loopback tunnel origin shares a ceiling; nonce adds per-browser cap.
            # Do not trust spoofable client-IP headers from a public request.
            key=self.client_address[0];now=time.time()
            with lock:
                events=[t for t in rates.get(key,[]) if t>now-60]
                if len(events)>=60:
                    return True
                rates[key]=events+[now]
                return False

        def do_GET(self):
            path=urlsplit(self.path).path
            if path=='/api/health':
                return self.json(200,{'status':'ok','gateway_version':'1.0','bank_revision':store.bank['bank_revision']})
            if path=='/api/consultation/session':
                if self.headers.get('Sec-Fetch-Site','')=='cross-site' or self.limited():
                    return self.json(429,{'error':'Coba lagi sebentar'})
                found=self.session()
                if found:
                    return self.json(200,{'csrf':found[1]['csrf'],'consent_version':CONSENT_VERSION})
                sid,csrf=secrets.token_urlsafe(32),secrets.token_urlsafe(32)
                with lock:
                    for k,v in list(sessions.items()):
                        if v['expires']<time.time():
                            del sessions[k]
                    if len(sessions)>=2000:
                        return self.json(429,{'error':'Coba lagi sebentar'})
                    sessions[sid]={'csrf':csrf,'expires':time.time()+1800,'count':0}
                host=urlsplit('//'+self.headers.get('Host','')).hostname
                secure='' if host in ('localhost','127.0.0.1','::1') else '; Secure'
                return self.json(200,{'csrf':csrf,'consent_version':CONSENT_VERSION},'omni_session='+sid+'; HttpOnly; SameSite=Strict; Path=/api/consultation; Max-Age=1800'+secure)
            if path.startswith('/api/'):
                return self.json(404,{'error':'Tidak tersedia'})
            decoded=unquote(path)
            relative=decoded.lstrip('/') or 'index.html'
            allowed=(relative in ['index.html','privacy.html','konsultasi-v3.html','robots.txt','sitemap.xml'] or relative.startswith('assets/'))
            target=(site/relative).resolve()
            if not allowed or site not in target.parents or not target.is_file() or target.suffix.lower() not in ['.html','.css','.js','.ico','.png','.jpg','.jpeg','.svg','.webp','.woff','.woff2','.txt','.xml']:
                return self.json(404,{'error':'Tidak tersedia'})
            data=target.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type',(mimetypes.guess_type(target)[0] or 'application/octet-stream')+('; charset=utf-8' if target.suffix in ['.html','.js','.css','.txt','.xml'] else ''))
            self.send_header('Content-Length',str(len(data)))
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Referrer-Policy','no-referrer')
            self.send_header('Cache-Control','no-store' if target.suffix=='.html' else 'public, max-age=300')
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if urlsplit(self.path).path!='/api/consultation/cases':
                return self.json(404,{'error':'Tidak tersedia'})
            found=self.session()
            origin=urlsplit(self.headers.get('Origin',''))
            host=self.headers.get('Host','')
            if not found or origin.netloc!=host or origin.scheme not in ('https','http') or not secrets.compare_digest(self.headers.get('X-Omni-CSRF',''),found[1]['csrf']):
                return self.json(403,{'error':'Sesi berubah; muat ulang lalu coba lagi'})
            if self.headers.get('Content-Type','').split(';')[0].strip()!='application/json' or self.headers.get('Transfer-Encoding'):
                return self.json(415,{'error':'Format permintaan tidak valid'})
            try:
                length=int(self.headers.get('Content-Length','0'))
            except ValueError:
                length=0
            if not 0<length<=50000:
                return self.json(413,{'error':'Permintaan melebihi batas'})
            if self.limited():
                return self.json(429,{'error':'Terlalu banyak permintaan; coba lagi sebentar'})
            with lock:
                if found[1]['count']>=5:
                    return self.json(429,{'error':'Batas sesi tercapai; coba lagi nanti'})
                found[1]['count']+=1
            self.connection.settimeout(10)
            try:
                raw=self.rfile.read(length)
                if len(raw)!=length:
                    raise ValueError('Permintaan tidak lengkap')
                p=json.loads(raw,object_pairs_hook=unique,parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Angka tidak valid')))
                if not isinstance(p,dict) or p.get('consent_version')!=CONSENT_VERSION:
                    raise ValueError('Persetujuan perlu diperbarui')
                result=store.create(p.get('payload'),p.get('consent'),found[0],p.get('request_id'))
                message='Halo OmniSense, saya ingin membahas hasil screening. [OMNISENSE-KONSULTASI] '+result['claim_code']
                result['whatsapp_url']='https://wa.me/'+phone+'?'+urlencode({'text':message})
                return self.json(201,result)
            except (ValueError,TypeError,KeyError,UnicodeError):
                return self.json(400,{'error':'Isian atau versi tidak valid. Periksa isian dan muat ulang halaman jika perlu.'})
            except Exception:
                return self.json(503,{'error':'Konsultasi belum tersedia. Jawaban tetap bisa dilihat di halaman ini; coba lagi nanti.'})

    return Handler


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--site',required=True);p.add_argument('--data',required=True)
    p.add_argument('--port',type=int,default=8080)
    a=p.parse_args()
    store=Store(a.data)
    def maintenance():
        while True:
            store.cleanup()
            time.sleep(300)
    threading.Thread(target=maintenance,daemon=True).start()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),make_handler(a.site,store))
    server.daemon_threads=True
    server.serve_forever()
