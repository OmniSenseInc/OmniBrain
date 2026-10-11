# RISET VALIDASI — INSTRUMEN KESJAPAN DIGITALISASI & AI OMNISENSE [v1]

> ⚠️ **MODE LEGACY (per 3 Okt 2026).** Dokumen ini = **triangulasi literatur**, BUKAN validasi
> empiris. Jangan sebut instrumen ini "tervalidasi" di sesi baru. Bobot/ambang = heuristik internal
> untuk dikalibrasi (rujukan NIST AI RMF Map/Measure/Manage & OECD SME = proses, bukan penentu bobot).
> Untuk sesi baru pakai `consulting/pertanyaan_v3.json` + `consulting/PLAYBOOK_KONSULTAN.md`.
> **Angka skor historis tidak diubah.**
Dasar: riset web (Juli-Ags 2026) terhadap kerangka kedewasaan digital/AI, survei
adopsi AI global, dan studi kesiapan UMKM Indonesia + F&B. Tujuan: memastikan
8 dimensi + pertanyaan OmniSense valid, tidak menebak, dan menangkap faktor yang
BENAR-BENAR menentukan keberhasilan digitalisasi/AI.

====================================================================
1. TRIANGULASI KERANGKA (dimensi yang muncul di semua model besar)
====================================================================
Model besar sepakat: kesiapan = >1 dimensi, bukan sekadar "punya teknologi".

| Sumber | Dimensi |
| Forrester DMM 4.0 | Culture, Organization, Technology, Insights/Data |
| Gartner | Strategy&Leadership, Technology, Customer, Ops&Process, Data&Analytics, Talent&Culture |
| BCG | Strategy&Leadership, Capabilities&Talent, Technology&Data, CX, Ops&Process, Innovation |
| MITRE AI Maturity | 6 pilar: Responsible Use, Strategy&Resources, Organization, Technology, Data, Performance |
| Cisco AI Readiness Index | Strategy, Infra, Data, Governance, Talent, Culture |
| AI Architecture Audit (berat) | Data 25%, Tech 20%, Skills&Culture 20%, Strategy&Governance 15%, Process 10%, Financial 10% |
| Umbrex (10 domain) | Strategy, Governance, Data, Tech&Arch, Talent, Culture, Risk/Compliance, Ops, Financial, Ecosystem |
| BRIN (UMKM RI) | Kepemimpinan, Kapasitas usaha, Operasional, Tenaga kerja&budaya, Teknologi, Ekosistem |

=> 8 dimensi OmniSense (Strategi, Data, Infra, Proses, Budaya, SDM, Tata kelola,
Anggaran) SUDAH tercakup semua. Tidak ada model besar yang memakai dimensi di luar itu.
BOBOT kita (Data 20, Infra 15, Proses 15, SDM 15, Strategi 10, Budaya 10, Tata
kelola 10, Anggaran 5) sejalan dengan literatur: Data selalu paling berat (20-25),
Infra 15-20, SDM/Budaya 10-20, Strategic/Governance 10-15, Proses/Keuangan 10.

====================================================================
2. TEMUAN KUANTITATIF (buat "mengapa" di laporan & advice)
====================================================================
- 73% kegagalan AI perusahaan dapat ditelусuri ke gap kesiapan yang SUDAH TERLIHAT
  sebelum uang pertama dikeluarkan (AI Advisory Practice White Paper).
- 85% pemimpin bilang data infra siap, TAPI data quality (44%) & security/privacy
  (42%) adalah penghambat #1; kesiapan yang dilaporkan sendiri SANGAT sering
  berlebihan (UST Thinking Ahead 2026). => "jangan percaya klaim, minta bukti angka".
- Perusahaan dengan akuntabilitas jelas utk hasil AI punya ROI established 3x lebih
  tinggi (KPMG Global AI Pulse Q2 2026); visibilitas biaya => 5x lebih mungkin ROI.
- Hanya 23% organisasi merasa workforcenya siap AI, turun 6 poin; 79% setuju laju AI
  > laju persiapan workforce/governance (Kyndryl 2026). Gap skill terbesar ada di
  manajemen menengah (Accenture 2026).
- Hambatan terbesar adopsi AI = WORKFORCE & ALIGNMENT, bukan teknoloği (Protiviti
  AI Pulse: penetrasi AI di IT 57% vs HR 11%).
- 70%+ data governance hanya ~1/3 yg "sangat jelas"; banyak review governance berhenti
  setelah go-live (<2/5 lanjutkan) (PwC Making AI deliver 2026). Agent AI menyusul
  governance: <1/2 punya kerangka formal utk sistem otonom.
- "Culture, not tech, menentukan scaling AI" (PwC); upskilling hanya 4% dari biaya
  tapi human review 50% — perusahaan salah alokasi.
- UMKM Indonesia: kesiapan digital masih RENDAH, mayoritas di "learner" (BRIN 2023,
  600 UMKM; skor level: Basic 1-1.75, Learner 1.76-2.5, Intermediate 2.51-3.25,
  Advanced 3.26-4). Sebagian besar hanya pakai medsos/e-commerce utk pemasaran,
  TIDAK untuk inovasi/operasi. Hambatan: biaya investasi tinggi, kurang budaya &
  pelatihan digital, infra, dukungan pemerintah, manajemen perubahan (Norman &
  Alamsjah 2020; Economies 2023). "People" justru dimensi dgn kesiapan TERTINGGI
  (Rafiah et al. 2022, 113 UMKM Jabar).
- Sektor otomotif UMKM: 56% baru level adopsi awal, 30% tak punya rencana (Tama 2021).
- F&B/kafe (studi POS PH & Malang): POS dipakai untuk transaksi dasar saja;
  fitur lanjut (inventory, analytics, CRM) jarang; hambatan: internet tidak stabil,
  downtime, biaya langganan, staff kurang training. Keputusan adopsi = persepsi
  manfaat + kemudahan + kesiapan karyawan & infrastruktur.
- Instrumen tervalidasi DHRQ (Cronbach α>.7): dimensi "learnability" (motivasi/kesiapan
  belajar teknologi) memprediksi adopsi — TANYAKAN KESEDIAAN BELAJAR, bukan hanya
  keterampilan saat ini.

====================================================================
3. IMPLIkASI UNTUK PERTANYAAN OMNISENSE (perbaikan validitas)
====================================================================
Prinsip inti dari seluruh riset: (a) ukur PERILAKU/BUKTI, bukan OPINI/klaim diri;
(b) tanya kesediaan belajar, bukan cuma skill saat ini; (c) gap kecil yang "menyumbat"
(data/gov) = prediktor kegagalan.

Per dimensi — pertanyaan tambahan/pengganti yang LEBIH valid (probe):

B1 STRATEGI (10%)
- "Kenapa mau digitalisasi sekarang?" → driver internal (kebutuhan sendiri) vs
  eksternal (ikut tren/dipaksa pasar). Riset UMKM RI: driver internal > eksternal utk
  kesiapan nyata. Skor tinggi bila ada MASALAH BISNIS konkret, bukan "biar kekinian".
- "Kalau berhasil, apa yang paling mau berubah?" → tanpa use case jelas = beli alat
  tanpa tujuan (pola gagal paling umum).

B2 DATA (20%) — paling berat, jangan percaya klaim
- "Berapa persis untung bulan kemarin? Berapa stok bahan tersisa di gudang sekarang?"
  → tidak bisa jawab angka = data tidak siap; klaim "data sudah ada" palsu.
- "Laporan penjualan bisa dibuat sendiri tanpa bantuan orang lain?" → data plumbing.
- "Data pelanggan/transaksi disimpan di mana? Siapa saja yang bisa akses?" → security
  & privacy (42% blocker; governance).

B3 INFRASTRUKTUR (15%)
- "Internet stabil berapa jam sehari? Pernah transaksi gagal karena jaringan?"
  → hambatan #1 kafe (internet/downtime/listrik).
- "Perangkat apa yang dipakai? (HP pribadi? tablet? komputer?)" & "kalau listrik
  mati 2 jam, bisnis masih jalan?" → ketergantungan & cadangan.

B4 PROSES (15%)
- "Ada prosedur tetap atau semuanya verbal/ingatan?" → proses tertulis = fondasi
  otomasi; tanpa SOP, AI agent tak punya "aturan" utk diotomasikan.
- "Siapa yang paling hafal jalannya bisnis? Kalau orang itu cuti, apa pelayanan
  berubah?" → single-point-of-failure: target AI agent.

B5 BUDAYA (10%)
- "Pemilik sendiri mau mengubah cara lama? Seberapa cepat keputusan dicoba-coba?"
  → sponsor vs akuntabilitas (3x ROI), manajemen perubahan (hambatan UMKM).
- "Kalau karyawan menolak sistem baru, apa yang pemilik lakukan?" → budaya belajar.

B6 SDM (10%) — naikkan bobot ke 15 (lihat rekomendasi)
- "Berapa dari [jumlah] karyawan yang bisa pakai HP/catatan digital dengan lancar?"
- "Kalau ada sistem baru, siapa yang siap belajar duluan?" → LEARNABILITY (DHRQ),
  bukan skill saat ini.
- "Pernah ada pelatihan/atur waktu utk belajar teknologi?" → gap skill terbesar ada
  di manajemen menengah & pelatihan (Accenture/Protiviti).

B7 TATA KELOLA (10%)
- "Kalau sistem salah hitung/merugikan, siapa yang bertanggung jawab & prosedurnya?"
  → governance/human-in-the-loop. Riset: governance sering berhenti setelah go-live.
- "Ada aturan tentang data pelanggan? SOP darurat kalau sistem error?" → risk &
  escalation.

B8 ANGGARAN (10%)
- "Berapa nominal yang BISA dialokasikan per bulan untuk teknologi?" (pisahkan dari
  "mau") → kesediaan bayar riil; tanpa angka = tidak siap.
- "Pernah menghitung berapa yang hilang karena cara manual (salah catat, stok
  basi, jam lembur)?" → ROI literacy; visibilitas biaya = 5x ROI.

====================================================================
4. REKOMENDASI BOBOT (berdasar bukti)
====================================================================
Literatur menempatkan SDM/workforce sebagai hambatan TERBESAR (Protiviti, Kyndryl,
Accenture) dan "People" adalah dimensi kesiapan TERTINGGI di UMKM RI (Rafiah) —
artinya SDM adalah "pintu" yang biasanya sudah setengah terbuka: tanya dulu, jangan
lewatkan. Usulan: SDM 10 → 15, Anggaran 10 → 5 (total tetap 100):
  Data 20, Infra 15, Proses 15, SDM 15, Strategi 10, Budaya 10, Tata kelola 10,
  Anggaran 5.
=> PERLU KEPUTUSAN KAMU sebelum saya update kalkulator.

====================================================================
5. SUMBER UTAMA
====================================================================
- Forrester Digital Maturity Model 4.0 (forrester.com)
- Cisco AI Readiness Index (cisco.com) — 6 pilar
- MITRE AI Maturity Model (mitre.org) — 6 pilar, 20 dimensi, 5 level
- AI Advisory Practice AI Readiness Framework (aiadvisorypractice.com) — 73% klaim
- AI Architecture Audit — bobot 6 dimensi + level detail
- Umbrex AI Transformation Readiness Framework — 10 domain + gating constraints
- Best-AI.org AI Readiness Framework — 7 dimensi
- KPMG Global AI Pulse Q2 2026 — akuntabilitas 3x ROI; cost visibility 5x ROI
- Kyndryl People Readiness Report 2026 — 23% workforce siap; Pacesetters
- Accenture Pulse of Change 2026 — gap skill menengah; leader-employee gap
- Protiviti AI Pulse Survey 2026 — workforce/alignment = hambatan terbesar
- PwC "Making AI deliver" 2026 — data plumbing; governance pasca-go-live; culture
- UST "The great [shift]" 2026 — data quality/security top blockers; self-report bias
- BRIN 2023 Indeks Kesiapan Digital UMKM (600 UMKM, 4 level) — antaranews/kompas
- MDPI Economies 2023 (MSME Readiness RI) — 5 variabel, people tertinggi; hambatan
- Tama et al. 2021 (otonomotif UMKM RI) — 56% adopsi awal
- Studi POS kafe (JIP 2568, San Pablo CBA, Baliwag IJRPR, Malang SWOT) — hambatan F&B
- DHRQ (Scherrenberg 2023, JMIR) — instrumen tervalidasi; learnability