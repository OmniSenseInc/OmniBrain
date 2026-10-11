# ANALISIS STRUKTUR ORGANISASI OMNISENSE
Disusun: internal riset (benchmark agensi AI + struktur startup). Sumber: fase8_sop_internal.md,
omnisense_ops.md, analisis_landscape_ai_agency.md, riset web (SFAI Labs, rubythalib.ai, belajarlagi.id).

=============================================================
1. STRUKTUR SEKARANG (dari Fase 8)
=============================================================
Flat, 3 founder:
- CEO Vincent   : keputusan akhir, deal besar, arah bisnis, klien strategis
                  + laporan pasca-konsultasi + proposal + closing.
- CTO Nathanael : SEMUA teknis — FNBSense, custom build, infrastruktur, kualitas.
- CMO Michael   : pemasaran, landing page, WA/IG, lead in-bound, konten.
- Konsultasi gratis dipimpin CEO & CMO BERSAMA; CTO hanya bila teknis.

Alur 7 langkah + pipeline P1–P8 sudah punya pemilik per tahap (tabel Fase 8).
Ritual pekanan 15–30 menit (3 angka: lead / konsultasi / deal) sudah ada.

=============================================================
2. BENCHMARK (yang normal di pasar)
=============================================================
- Startup fase awal (2–10 orang): struktur FLAT/horizontal adalah yang ideal.
  OmniSense (3 founder) sudah BENAR. Jangan bikin layer/title baru.
- rubythalib.ai (konsultan AI Indonesia, 40+ proyek, 21 perusahaan): 3 founder =
  CEO (AI fullstack) + CTO + COO. Bedanya: ada COO khusus ops/finance/HR/sales.
- AI studio senior-heavy (SFAI Labs): 12 orang bisa kalahkan 50 orang karena:
  (a) tanpa account manager/PM — engineer langsung komunikasi ke client,
  (b) ritual mingguan ber-artifact (demo), bukan deck,
  (c) "agent leverage": coding agent (Claude Code/Cursor/Codex) jadi pengali
      output, tapi efeknya cuma nempel di engineer SENIOR yang bisa review diff.
- Kesalahan umum yang harus dihindari: meniru struktur korporat, layer berlebihan,
  role tumpang tindih, founder jadi bottleneck semua keputusan, menunda fungsi ops.

=============================================================
3. TEMUAN / GAP
=============================================================
1. CEO = bottleneck. CEO pegang keputusan + delivery (laporan, proposal, closing)
   sekaligus. Ini persis risiko "founder jadi penghambat" dari benchmark.
2. CTO = single point of failure. Semua teknis di 1 orang, tanpa backup. Benchmark:
   di bawah 3 engineer = tidak ada peer review & ada titik gagal tunggal. Solusinya
   bukan hire, tapi standarkan AGENT LEVERAGE (Hermes/opencode) supaya 1 CTO =
   output beberapa engineer.
3. Fungsi OPS tidak punya pemilik eksplisit. Finance, kontrak, invoice, CRM,
   logistik on-boarding tersebar "semua orang" -> rawan terlewat (margin bocor).
4. Konsultasi "CEO & CMO bersama" = 2 orang terkunci per lead. Boros waktu di fase
   runway tipis; CEO seharusnya fokus closing strategis, bukan tiap sesi.

=============================================================
4. REKOMENDASI (tetap 3 orang, pertegas batas)
=============================================================
- PERTAHANKAN flat. Tidak ada hire baru, tidak ada gelar baru sekarang.
- Tambah "hat OPS" secara eksplisit: CMO (Michael) rangkap OPS — CRM, kontrak,
  invoice, logistik on-boarding (marketing & ops beririsan di lead-to-cash).
  CEO pegang closing & keputusan; CTO pegang delivery & kualitas.
- Kurangi beban CEO:
  * Laporan pasca-konsultasi = draft AI (OmniSense bot) + review CMO, CEO cuma approve.
  * Proposal = template + draft AI, CEO finalisasi angka & tanda tangan.
- Standarkan agent leverage CTO: SOP pakai Hermes/opencode untuk build & review,
  biar 1 orang bisa handle N klien paralel. Ini keunggulan OmniSense sendiri
  (jual AI agent, ya pakai AI agent buat internal juga = dogfooding).
- Pertahankan ritual pekanan; upgrade jadi ber-artifact (demo produk, angka pipeline),
  bukan sekadar laporan lisan.

=============================================================
5. PENUTUP
=============================================================
Struktur 3-founder OmniSense sudah sesuai fase. Masalah bukan di struktur, tapi di
BATAS PERAN yang belum tegas (ops tanpa pemilik, CEO kelebihan delivery, CTO tanpa
backup). Perbaikannya bukan restrukturisasi, tapi: (1) tetapkan pemilik OPS,
(2) delegasikan draft laporan/proposal ke AI, (3) standarkan agent leverage CTO.
