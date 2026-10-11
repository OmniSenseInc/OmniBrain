"""Read-only security probes for the production domain; no case or WA submission."""
import http.client,json,datetime
from pathlib import Path

rows=[]
def probe(host,path,expected,method='GET',headers=None,origin=False):
    c=(http.client.HTTPConnection('43.153.194.210',80,timeout=12) if origin else http.client.HTTPSConnection(host,timeout=12))
    row={'host':host,'path':path,'method':method,'origin_http':origin,'expected':expected}
    try:
        c.request(method,path,headers={'Host':host,**(headers or {})})
        r=c.getresponse(); h={k.lower():v for k,v in r.getheaders()}; r.read(1500000)
        row.update(status=r.status,passed=r.status in expected)
        if path=='/' and r.status==200:
            row['browser_guards']=all(["'nonce-" in h.get('content-security-policy',''),h.get('x-frame-options')=='DENY',h.get('x-content-type-options')=='nosniff',h.get('cache-control')=='no-store'])
            row['passed'] &= row['browser_guards']
        if path.endswith('/session') and r.status==200:
            row['secure_session']=all(x in h.get('set-cookie','') for x in ['Secure','HttpOnly','SameSite=Strict']) and h.get('cache-control')=='no-store'
            row['passed'] &= row['secure_session']
        if r.status in (301,302,307,308):row['location']=h.get('location')
    except Exception as e:row.update(error_type=type(e).__name__,passed=False)
    finally:c.close()
    rows.append(row)

for host in ['omnisense.my.id','www.omnisense.my.id']:
    for path in ['/','/konsultasi-v3.html','/privacy.html']:
        probe(host,path,[200])
    probe(host,'/api/consultation/session',[200])
for path in ['/.env','/.git/config','/consultations.sqlite3','/web_security.sqlite3','/approved-site.json','/assets/.web-rate-key','/pratinjau/','/assets/../../consultations.sqlite3','/wp-admin/','/shell.php']:
    probe('omnisense.my.id',path,[400,404])
probe('omnisense.my.id','/api/consultation/cases',[400,403],method='POST',headers={'Origin':'https://evil.invalid','Content-Type':'application/json'})
probe('omnisense.my.id','/api/consultation/cases',[403,405],method='DELETE')
probe('omnisense.my.id','/api/consultation/session',[403],origin=True)
probe('omnisense.my.id','/api/consultation/session',[403],origin=True,headers={'X-Forwarded-Proto':'https','CF-Connecting-IP':'192.0.2.88','Forwarded':'proto=https'})
probe('omnisense.my.id','/api/consultation/cases',[403],method='POST',origin=True)
probe('evil.invalid','/',[400,403,404,421],origin=True)
probe('localhost:8080','/api/consultation/session',[400,403,404],origin=True)
out=Path(__file__).resolve().parents[2]/'outputs'/'omnisense-wa-polish-v7-public-checks.json'
report={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':rows,'passed':sum(r['passed'] for r in rows),'total':len(rows),'client_case_submitted':False,'whatsapp_messages_sent':False}
out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
