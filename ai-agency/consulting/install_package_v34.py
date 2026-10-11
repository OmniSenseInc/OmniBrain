from pathlib import Path
import datetime,hashlib,json,shutil,sqlite3,time,zipfile,urllib.request,sys

root=Path('/home/ubuntu/ai-agency');home=Path('/home/ubuntu/.hermes')
mode=sys.argv[1]
if mode=='install':
    log=(root/'consulting/test-all-v34.log').read_text()
    assert 'Ran 98 tests' in log and '\nOK' in log,'Unit suite must pass'
    evaluation=json.loads((root/'consulting/evaluasi-fleksibilitas-v34.json').read_text())
    assert evaluation['synthetic_cases']==12 and evaluation['all_rule_checks_passed']==12,'Review failed eval cases first'
    assert json.loads((home/'gateway_state.json').read_text()).get('active_agents')==0,'Active Hermes agents'
    with sqlite3.connect(root/'consulting/data/consultations.sqlite3') as c:
        assert c.execute("SELECT count(*) FROM replies WHERE status='pending' AND created>?",(time.time()-30,)).fetchone()[0]==0,'Recent consultation pending'
    backup=root/'consulting'/('backup_dialogue_v34_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
    backup.mkdir(mode=0o700)
    def save(p,name):
        if p.exists():
            b=backup/name;b.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,b)
    with zipfile.ZipFile(root/'consulting/gateway-v34-stage.zip') as z:
        baseline=json.loads(z.read('baseline-v33.json'))
        for name,digest in baseline.items():
            p=root/name
            assert (hashlib.sha256(p.read_bytes()).hexdigest()==digest) if digest else not p.exists(),name
            assert (root/'consulting/staging-gateway-v34'/name).read_bytes()==z.read(name),name
        plugin=home/'plugins/omnisense-consultation/__init__.py'
        assert plugin.read_bytes()==(root/'hermes-plugin/__init__.py').read_bytes(),'Plugin peer differs'
        for name in baseline:
            save(root/name,name);(root/name).write_bytes(z.read(name))
        save(plugin,'installed-plugin/__init__.py');plugin.write_bytes(z.read('hermes-plugin/__init__.py'))
    rules='''

## Respons konsultasi 1.1 — pembaruan 4 Oktober 2026
Baca /home/ubuntu/ai-agency/consulting/GATEWAY_KONSULTASI_V34.md untuk perilaku terbaru.
Pembuka mendengar keluhan dan meminta contoh kejadian, bukan harga/diagnosis atau angka baseline.
Skor hanya indikator pilihan self-report dan ditampilkan di WA bila diminta; tidak membuktikan kebenaran jawaban.
Jawaban asal yang tampak masuk akal tidak dapat dideteksi pasti. Konteks acak yang jelas perlu klarifikasi tanpa tuduhan.
Pertanyaan balik/koreksi bukan jawaban discovery; jangan memajukan tahap atau memberi izin dari teks tersebut.
Belum tahu bukan nol. Tidak disebut bukan tidak ada; penyalinan manual tidak membuktikan ketiadaan validasi.
Harga dibahas bila klien bertanya atau setelah kebutuhan/scope dibahas manusia; jangan membuka percakapan dengan harga.
Konsultasi dan pendalaman tetap gratis. Biaya operasional klien adalah topik bisnis yang berbeda dari harga jasa.
Koreksi tetap self-report, disimpan terpisah dan menahan options sampai konflik ditinjau manusia.
Model menyusun respons tanpa tools pada lane klien. Kerangka enam topik discovery masih ada; fleksibilitas giliran diuji terbatas,
bukan bukti percakapan sepenuhnya adaptif atau 100% akurat. Instruksi/SOP diperbaiki; bobot model tidak di-fine-tune.
'''
    skill_paths=[home/'skills/omnisense'/name/'SKILL.md' for name in ['omnisense-consultant','omnisense-agency-brain','omnisense-team-ops','omnisense-website']]
    skill_paths.append(home/'skills/consulting/digitalization-readiness-assessment/SKILL.md')
    for p in skill_paths:
        save(p,'skills/'+str(p.relative_to(home/'skills')))
        p.write_text(p.read_text()+rules)
    for name in ['INDEKS_OMNISENSE.md','CATATAN_KERJA_OMNISENSE.md','guardrail_consultant_whatsapp.md','website/SERAH_TERIMA_KONSULTASI_V3.md']:
        p=root/name;save(p,name)
        p.write_text(p.read_text()+'\n\nPembaruan percakapan 3.4: baca consulting/GATEWAY_KONSULTASI_V34.md (path dari ai-agency). Pembuka tanpa pricing/skor/diagnosis; pertanyaan balik tidak memajukan tahap; koreksi perlu review dan belum tahu bukan nol. Pengujian 98 unit/regression serta 12 skenario sintetis; bukan fine-tuning atau bukti akurasi universal.\n')
    print(json.dumps({'installed':True,'backup':str(backup)}))
elif mode=='package':
    with zipfile.ZipFile(root/'consulting/omnisense-gateway-v3.3.zip') as old:
        names=set(json.loads(old.read('MANIFEST_SHA256.json')))-{'README.md','PROGRES_V33.md','VERIFIKASI_GATEWAY.json'}
    names.update(['consulting/consultation_dialogue.py','consulting/test_consultation_dialogue.py','consulting/evaluate_dialogue_v34.py','consulting/GATEWAY_KONSULTASI_V34.md'])
    files={}
    for n in sorted(names):
        p=home/n if n.startswith('skills/') else root/n
        assert p.is_file() and p.suffix not in {'.db','.sqlite3','.log'} and '.env' not in p.parts and 'data' not in p.parts,n
        files[n]=p.read_bytes()
    assert files['hermes-plugin/__init__.py']==(home/'plugins/omnisense-consultation/__init__.py').read_bytes()
    health=json.load(urllib.request.urlopen('http://127.0.0.1:8080/api/health',timeout=10));assert health['status']=='ok'
    bridge=json.load(urllib.request.urlopen('http://127.0.0.1:3000/health',timeout=10));assert bridge['status']=='connected'
    eval_data=json.loads((root/'consulting/evaluasi-fleksibilitas-v34.json').read_text())
    source_hashes={n:hashlib.sha256(files[n]).hexdigest() for n in ['consulting/consultation_gateway.py','consulting/consultation_dialogue.py','hermes-plugin/__init__.py']}
    eval_data['evaluated_source_sha256']=source_hashes
    files['consulting/evaluasi-fleksibilitas-v34.json']=(json.dumps(eval_data,ensure_ascii=False,indent=2)+'\n').encode()
    report=f'''# Respons dan fleksibilitas OmniSense — 4 Oktober 2026

Perbaikan dipasang di VPS OmniSense berdasarkan contoh pesan WA yang dikirim pemilik. Pesan tersebut menunjukkan pembuka sampai ke WA, tetapi bukan bukti seluruh pendalaman/review tim telah teruji dengan klien nyata.

**Bukan fine-tuning model.** Yang diperbaiki: instruksi, SOP/skill, pengelolaan percakapan, pemeriksaan balasan dan pengujian. Bobot kuis tetap heuristik. Isi asal yang terlihat masuk akal tidak bisa diketahui niatnya; diperlukan klarifikasi, contoh dan bukti.

- Pembuka baru mendengar proses/keluhan dan meminta contoh kejadian. Skor ditampilkan jika diminta, tanpa menyimpulkan penyebab atau kesiapan proyek dari angka. Harga tidak disebut di pembuka.
- Jawaban acak yang jelas diminta klarifikasi. Pertanyaan balik, koreksi, pricing, privasi dan beberapa permintaan di luar topik tidak dicatat sebagai jawaban discovery atau memajukan tahap. Belum tahu dicatat sebagai ketidakpastian, bukan nol.
- Pricing dijawab bila ditanya: konsultasi gratis, biaya pengerjaan mengikuti scope manusia tanpa nominal rekaan. Biaya operasional yang dikeluhkan klien tetap boleh dianalisis.
- Model menanggapi pesan terbaru dan konteks kasus sendiri. Jika respons tidak layak/gagal, fallback tetap mengakui isi keluhan dan melanjutkan pertanyaan. Beberapa klaim negatif tanpa dukungan sumber ditolak; pemeriksaan ini terbatas dan tidak menjamin semua isi model benar.
- Koreksi disimpan terpisah dan menjadi konflik yang perlu review manusia sebelum options; tidak hilang saat riwayat pertanyaan bergulir. Tidak ada pemberian izin tools, approval atau harga dari teks klien.

**Pengukuran:** 98 uji unit/regresi lulus (69 assessment/workflow/mission, 12 gateway dan 17 dialogue). Dalam uji akhir 12 kasus sintetis, {eval_data['all_rule_checks_passed']} memenuhi pemeriksaan alur serta proksi relevansi; {eval_data['model_successes']} panggilan model berhasil dan {eval_data['personalized_replies']} responsnya dipakai. Respons lain memakai template/fallback. Semua memakai database sementara dan transport simulasi, tanpa pesan ke klien.

Evaluasi awal menemukan asumsi bahwa penyalinan jadwal manual berarti validasi tidak ada. Instruksi dan guard diperbaiki; fallback yang semula terlalu umum dibuat merujuk penjelasan klien. Respons aktual dan fixture ada dalam evaluasi JSON paket.

**Batas hasil:** kata kunci bukan ukuran akurasi; sampel kecil belum membuktikan fleksibilitas lintas semua sektor, stabilitas seluruh model, deteksi semua input ngawur atau manfaat bisnis. Pendalaman masih memakai kerangka enam topik, dengan ruang pertanyaan balik/koreksi di antaranya. Perlu evaluasi berlabel dan engagement nyata untuk kalibrasi. Domain final tidak dideploy dalam pekerjaan ini.

Layanan gateway/preview aktif dan bridge WA connected. Kasus lama mempertahankan arti pertanyaan lama; pembuka baru dapat diuji lewat screening baru. Gateway/API 1.0, dialogue 1.1, paket 3.4; bank/engine 3.1 dan workflow 3.2 tetap.
'''
    (root/'consulting/evaluasi-respons-omnisense-v3.4.md').write_text(report)
    files['PROGRES_V34.md']=report.encode()
    files['README.md']=b'# OmniSense 3.4\n\nRead PROGRES_V34.md and consulting/GATEWAY_KONSULTASI_V34.md for current behavior, tests and limitations.\nThis is a source snapshot, not an automatic installer. No credentials, customer database, config backups or raw client logs.\nEarlier documents preserve historical results. No model fine-tuning or final-domain deployment.\n'
    hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}
    files['MANIFEST_SHA256.json']=(json.dumps(hashes,indent=2)+'\n').encode()
    out=root/'consulting/omnisense-respons-v3.4.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for n,b in sorted(files.items()):z.writestr(n,b)
    with zipfile.ZipFile(out) as z:assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in hashes.items())
    print(json.dumps({'package':str(out),'entries':len(files),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tests':98,'evaluation':{k:v for k,v in eval_data.items() if k not in ('results','evaluated_source_sha256')}}))
else:raise ValueError('Expected install or package')
