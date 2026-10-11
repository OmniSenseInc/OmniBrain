from pathlib import Path
import hashlib,json,zipfile,urllib.request

root=Path('/home/ubuntu/ai-agency')
manifest=json.loads((root/'consulting/manifest-installed-mission-v32.json').read_text())
names={n for n in manifest if not n.startswith('consulting/test-output/')}
names.update(['consulting/consultation_gateway.py','consulting/consultation_server.py',
    'consulting/gateway_operator.py','consulting/test_consultation_gateway.py',
    'consulting/GATEWAY_KONSULTASI_V33.md','hermes-plugin/__init__.py',
    'hermes-plugin/plugin.yaml','website/index.html'])
files={}
for n in sorted(names):
    p=Path('/home/ubuntu/.hermes')/n if n.startswith('skills/') else root/n
    assert p.is_file(),n
    assert not any(part in {'data','.env','config.yaml'} for part in Path(n).parts),n
    assert p.suffix not in {'.sqlite3','.db','.log'},n
    files[n]=p.read_bytes()
assert files['hermes-plugin/__init__.py']==Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/__init__.py').read_bytes()
assert files['hermes-plugin/plugin.yaml']==Path('/home/ubuntu/.hermes/plugins/omnisense-consultation/plugin.yaml').read_bytes()
for n,count in [('assessment',11),('workflow',23),('mission',35),('final',12)]:
    log=(root/f'consulting/test-gateway-v33-{n}.log').read_text()
    assert f'Ran {count} tests' in log and '\nOK' in log,n
flow=(root/'consulting/test-gateway-v33-final-flow.log').read_text()
result=json.loads(flow.split('RESULT ')[-1].strip())
assert result=={'contract_checks':103,'browser_checks':42,'parity_cases':89,'real_browser_messages':4}
smoke=json.loads((root/'consulting/public-browser-smoke-v33.json').read_text())
assert smoke['synthetic_case_cleaned'] and not smoke['whatsapp_opened'] and not smoke['whatsapp_sent']
health=json.load(urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=10))
assert health['status']=='ok'
assert json.load(urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=10))['status']=='connected'
verification={'date':'2026-10-04','unit_integration_tests':81,'flow_checks':result,
    'gateway_health':health,'whatsapp_bridge':'connected',
    'public_https_smoke':{'post_after_consult_action':1,'wa_draft_ready':True,'wa_opened':False,'wa_sent':False,'synthetic_case_cleaned':True},
    'hermes_ingress':'real ingress, simulated transport','client_whatsapp_e2e':'not tested',
    'model_probe':'active provider recovered after owner top-up; live tool-free completion passed',
    'final_domain_deployment':'not performed','hermes_full_runner':'pytest unavailable in production venv'}
live=json.loads((root/'consulting/live-lane-after-topup-v33.json').read_text())
assert all(live[k] for k in ['model_success','personalized_reply_used','application_question_appended','reply_quality_guard'])
verification['live_consultation_lane']={k:v for k,v in live.items() if k!='reply'}
verification['omni_review']='Hermes chat --oneshot with [CODEX]; two progress documents read; no changes or home send in that session'
files['VERIFIKASI_GATEWAY.json']=(json.dumps(verification,ensure_ascii=False,indent=2)+'\n').encode()
files['PROGRES_V33.md']=(root/'consulting/progres-omnisense-v3.3.md').read_bytes()
files['README.md']=('''# OmniSense — paket pengembangan 3.3

Sumber aktif setelah melanjutkan pekerjaan yang terputus. Baca PROGRES_V33.md dan
consulting/GATEWAY_KONSULTASI_V33.md untuk status terkini dan batas verifikasinya.
Bank/engine tetap 3.1, workflow 3.2, kontrak agent 1.0; gateway baru 1.0.
Dokumen evaluasi versi terdahulu menyimpan hasil historis, bukan status gateway terkini.

Paket bukan installer otomatis. Plugin berada di ~/.hermes/plugins/omnisense-consultation;
folder hermes-plugin berisi salinan sumber yang identik. Skills berasal dari ~/.hermes/skills.
Server preview memakai loopback 8080 melalui tunnel yang sudah ada; konfigurasi layanan,
allowlist, kredensial dan backup tidak dibundel. Jangan membuka akses tools internal untuk klien.
Database, case/token klien, log mentah dan konfigurasi privat tidak disertakan.

Lihat VERIFIKASI_GATEWAY.json. Model aktif berhasil kembali setelah top-up dan diuji
melalui jalur konsultasi dengan transport simulasi; fallback terstruktur tersedia.
Domain final dan inbound WhatsApp klien nyata belum diverifikasi.
Manifest SHA256 memeriksa byte sumber paket, bukan menjamin hasil bisnis atau kelayakan go-live.
''').encode()
hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}
files['MANIFEST_SHA256.json']=(json.dumps(hashes,indent=2)+'\n').encode()
out=root/'consulting/omnisense-gateway-v3.3.zip'
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for n,b in sorted(files.items()):z.writestr(n,b)
with zipfile.ZipFile(out) as z:
    assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hashes.items())
print(json.dumps({'file':str(out),'entries':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
