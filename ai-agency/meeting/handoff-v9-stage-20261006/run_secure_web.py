"""Single bounded Waitress process; sessions are intentionally invalidated on restart."""
import argparse
import logging
import json
from pathlib import Path
import threading
import time
from waitress import serve
from consultation_gateway import Store
from consultation_web import WebApp

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--site',required=True)
    p.add_argument('--data',required=True)
    p.add_argument('--port',type=int,default=8080)
    p.add_argument('--origin',action='append',required=True)
    p.add_argument('--trust-tunnel',action='store_true')
    p.add_argument('--manifest',required=True)
    a=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(name)s %(levelname)s %(message)s')
    store=Store(a.data)
    def cleanup():
        while True:
            try:
                store.cleanup()
            except Exception:
                logging.getLogger('omnisense.security').error('retention_cleanup_failed')
            time.sleep(300)
    threading.Thread(target=cleanup,daemon=True).start()
    manifest=json.loads(Path(a.manifest).read_text())
    if not manifest.get('files'):raise ValueError('Approved site manifest required')
    app=WebApp(a.site,store,a.origin,trust_tunnel=a.trust_tunnel,approved_files=manifest['files'])
    serve(app,host='127.0.0.1',port=a.port,threads=8,ident='OmniSense',connection_limit=64,backlog=64,channel_timeout=30,cleanup_interval=5,max_request_header_size=8192,max_request_body_size=50000,inbuf_overflow=65536,outbuf_high_watermark=1048576,expose_tracebacks=False,log_socket_errors=False,clear_untrusted_proxy_headers=True,channel_request_lookahead=0,trusted_proxy='127.0.0.1' if a.trust_tunnel else None,trusted_proxy_headers={'x-forwarded-proto'} if a.trust_tunnel else set())
