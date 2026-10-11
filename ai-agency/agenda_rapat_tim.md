# AGENDA RAPAT TIM OMNISENSE — Topik Diskusi & Daftar Celah
Dibuat dari audit internal (config bot WhatsApp, kode adapter Hermes, SOP, struktur tim).
Tujuan: bahas satu per satu, ambil keputusan, tunjuk pemilik & deadline.

Urutan = prioritas (paling rawan reputasi/keamanan duluan).

=============================================================
1. PROSES ON-BOARD CLIENT & AKSES BOT  (paling urgent)
=============================================================
Topik: cara standar memasukkan client ke konsultasi.
CELAH:
- Dokumen lama (guardrail/skill/kontrak) masih tulis `/whitelist <nomor>` — command itu
  TIDAK ADA. Tim yang ikut dokumen pasti bingung (sudah dialami Vincent).
- Alur "bikin grup = whitelist" belum tertulis resmi di mana pun.
EVIDENSI: `.env` — GROUP_POLICY=open, ALLOW_ALL_USERS=true, REQUIRE_MENTION=true;
  tidak ada fitur `/whitelist` di Hermes.
KEPUTUSAN yang perlu diambil:
- Standarkan: client baru = TIM bikin grup (bot + client) → client/team @mention bot.
- Ubah semua dokumen yang masih nyebut `/whitelist`.
PEMILIK usulan: Michael (proses) + Nathanael (validasi teknis).

=============================================================
2. KEAMANAN AKSES BOT  (celah teknis terbesar)
=============================================================
Topik: siapa yang benar-benar boleh trigger bot.
CELAH:
- GROUP_POLICY=open + ALLOW_ALL_USERS=true → SIAPA PUN yang menambahkan nomor bot ke
  grup bisa memicu konsultasi. Tidak ada gerbang "client asli vs orang asing".
- TEMBOK tim-vs-client (team vs client) hanya dibedakan oleh COCOKAN NOMOR + prompt —
  pengamanan lunak, bukan teknis. Nomor bisa dipalsukan/disalahgunakan.
EVIDENSI: kode `_is_group_allowed()` -> group_policy open = selalu True;
  `_open_dm_opted_in()` pakai ALLOW_ALL_USERS.
KEPUTUSAN:
- Terima risiko (bot bisnis, jualan terbuka) ATAU ubah GROUP_POLICY ke allowlist (daftar
  JID grup per client) untuk kontrol penuh.
- Tentukan: DM policy tetap allowlist tim, atau buka untuk client?
PEMILIK: Nathanael (keputusan teknis).

=============================================================
3. PEMISAHAN DATA ANTAR CLIENT  (celah reputasi)
=============================================================
Topik: mencegah data client A bocor ke grup/client B.
CELAH:
- Satu bot = satu memori/session. Data client tersimpan di memori agent & session, bukan
  per-client terisolasi teknis.
- Aturan "cross-contamination" (dilarang mencampur) saat ini HANYA di prompt/guardrail.
EVIDENSI: profil konsultan berbagi memory & session store yang sama antar grup.
KEPUTUSAN:
- Prinsip "1 client = 1 grup" wajib, dan tim harus disiplin tidak menempel data client.
- Opsional: pakai session per-client / pencatatan skor ke file terpisah per client.
PEMILIK: semua (kedisiplinan) + Nathanael (mekanisme).

=============================================================
4. ANTI-HALUSINASI & ANTI-PROMPT-INJECTION  (celah kualitas + keamanan)
=============================================================
Topik: pastikan asesmen berdasar fakta, bukan karangan.
CELAH:
- Karena akses terbuka, "client" jahat bisa coba jailbreak / suruh bot bocorkan data
  internal, strategi, atau harga.
- Skor kesiapan bisa meleset kalau konsultan menilai dari kesan, bukan fakta.
EVIDENSI: guardrail sudah menolak harga/closing, tapi itu pagar lunak (prompt-level).
KEPUTUSAN:
- Pakai bank pertanyaan anti-halusinasi (key_questions_client.md, sudah di-update).
- Disiplin: tanpa fakta = skor netral + catatan "belum terverifikasi".
PEMILIK: Vincent & Michael (jalankan sesi) + saya/AI (pegang aturan).

=============================================================
5. STRUKTUR & BEBAN KERJA  (celah operasional)
=============================================================
Topik: batas peran 3 founder.
CELAH:
- CEO bottleneck: Vincent pegang keputusan + delivery (laporan/proposal/closing).
- CTO = single point of failure: semua teknis di Nathanael tanpa backup.
- Fungsi OPS (finance, kontrak, invoice, CRM) tanpa pemilik eksplisit.
KEPUTUSAN:
- Tetapkan pemilik OPS (usulan: Michael rangkap CRM/kontrak/invoice).
- Delegasikan draft laporan/proposal ke AI, CEO cukup approve.
- Standarkan agent-leverage buat CTO.
PEMILIK: Vincent (keputusan akhir).

=============================================================
6. MARGIN & RUNWAY  (celah keuangan — bahas singkat)
=============================================================
Topik: struktur harga vs biaya vs waktu.
CELAH:
- Margin tipis: tagih ~250k/bln vs biaya ~149k + JAM DUKUNGAN (penggerus utama).
- Runway ~3 bulan; komitmen 2-5 jam/hari. Waktu dukungan menumpuk lebih cepat dari
  pendapatan seiring client bertambah.
KEPUTUSAN:
- Kunci harga paket final (butuh angka "mau bayar berapa" dari validasi/beta).
- Tetapkan batas jam dukungan per client & catat real.
PEMILIK: Vincent + Michael.

=============================================================
7. REKAM JEJAK CLIENT (CRM)  (celah data)
=============================================================
Topik: satu tempat kebenaran untuk lead/klien/skor.
CELAH:
- Belum ada CRM: data lead, stage pipeline (P1-P8), skor, keberatan tersebar di file &
  obrolan. Rawan hilang & sulit ukur.
EVIDENSI: pipeline P1-P8 sudah didefinisikan di fase8, tapi tidak ada tools pencatatnya.
KEPUTUSAN:
- Pilih tools minimal (spreadsheet bersama / Airtable / Notion) & WAJIB diupdate.
PEMILIK: Michael (usulan) + semua (isi).

=============================================================
CATATAN
=============================================================
- Item 1-4 (akses & data) paling rawan reputasi — prioritaskan di awal rapat.
- Item 5-7 bisa dibahas lanjutan; 5 & 6 sudah punya rekomendasi dari riset struktur.
- Setelah rapat: tunjuk pemilik + deadline per item, lalu update SOP biar tidak nyasar lagi.
