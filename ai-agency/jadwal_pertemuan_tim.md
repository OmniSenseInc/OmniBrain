# JADWAL & AGENDA PERTEMUAN TIM OMNISENSE — SIKLUS 1
Pekan = Senin–Minggu. Siklus 1: Sen 21 Sep – Min 18 Okt 2026. Hari 0 (kickoff): Min 20 Sep 2026.
3 pertemuan per pekan: 1x OFFLINE (Sabtu atau Minggu) + 2x ONLINE (hari acak, Senin–Jumat).

ATURAN DASAR:
- Offline = pertemuan besar (90 menit): demo + angka + progress + kunci scope pekan depan.
- Online = pertemuan pendek (30 & 45 menit): cuma 2 hal — bereskan penghambat & siapkan rilis/konten.
- Setiap pertemuan WAJIB punya catatan hasil (keputusan + pemilik + tanggal) di file ini.
- Pertemuan tidak boleh dipakai untuk mengerjakan hal baru; kalau muncul ide baru -> masuk daftar TUNDA.
- Semua jam WIB. Kalau bentrok, yang dipindah adalah ONLINE, bukan OFFLINE.

=============================================================
1. JADWAL KONKRET 4 PEKAN (hari online diacak, sudah dikunci)
=============================================================
HARI 0 — Minggu 20 Sep
  19:30-21:00  OFFLINE (KICKOFF): kunci scope Siklus 1, pembagian tugas, pasang sistem
               (bug board, CRM, log konten, kalender). Output: kalender + progress kosong siap isi.

PEKAN 1 — Sen 21 Sep s/d Min 27 Sep  | tema: DATA PENJUALAN TERSIMPAN TERPUSAT (MUST-1)
  Rab 23 Sep  20:00-20:30  ONLINE-A (Triage & Blocker)
  Jum 25 Sep  20:00-20:45  ONLINE-B (Review & Konten)
  Sab 26 Sep  16:00-17:30  OFFLINE (Sinkron + Demo + Kunci Sprint)

PEKAN 2 — Sen 28 Sep s/d Min 4 Okt  | tema: SATU LAPORAN HARIAN VIA WHATSAPP (MUST-2)
  Sel 29 Sep  20:00-20:30  ONLINE-A (Triage & Blocker)
  Kam 1 Okt   20:00-20:45  ONLINE-B (Review & Konten)
  Min 4 Okt   19:30-21:00  OFFLINE (Sinkron + Demo + Kunci Sprint)

PEKAN 3 — Sen 5 Okt s/d Min 11 Okt  | tema: CRON STOK + SEKRETARIS 1 PERTANYAAN (MUST-3 & 4)
  Rab 7 Okt   20:00-20:30  ONLINE-A (Triage & Blocker)
  Kam 8 Okt   20:00-20:45  ONLINE-B (Review & Konten)
  Sab 10 Okt  16:00-17:30  OFFLINE (Sinkron + Demo + Kunci Sprint)

PEKAN 4 — Sen 12 Okt s/d Min 18 Okt  | tema: HARDENING + SIAP BETA
  Sel 13 Okt  20:00-20:30  ONLINE-A (Triage & Blocker)
  Kam 15 Okt  20:00-20:45  ONLINE-B (Review & Konten)
  Min 18 Okt  19:30-21:00  OFFLINE (Sinkron + Demo + Kunci Siklus 2)

Aturan pengacakan: hari online diundi ulang tiap pekan (bukan hari tetap), tapi TIDAK boleh
jatuh di Sabtu/Minggu dan tidak boleh sama dengan hari cut-off (Kamis) untuk ONLINE-A.
Cara bikin jadwal pekan berikutnya: `.venv/bin/python kalender_omnisense.py --acak-online --pekan N --tgl-senin YYYY-MM-DD`
(hasilnya ditempel ke bagian ini).

=============================================================
2. AGENDA TETAP — OFFLINE (90 menit, Sabtu 16:00 / Minggu 19:30)
=============================================================
Tujuan: menutup pekan + mengunci scope pekan depan. Dipimpin: Vincent (keputusan),
notulen: Michael (semua keputusan masuk kalender + progress).
  0-10   BUKA — 4 ANGKA PEKAN INI (Michael menyebutkan, bukan membahas panjang):
         item MUST selesai | bug P0/P1 terbuka | konten terpost + lead masuk | calon pilot.
  10-30  DEMO BUILD STABIL — Nathanael demo langsung di aplikasi (bukan slide/foto).
         Vincent menyebutkan apa yang BELUM ada di build itu. Tidak ada diskusi kode di sini.
  30-45  LAPORAN BUG (Michael) — daftar P0/P1 terbuka, mana yang wajib tutup sebelum fitur baru,
         mana yang jadi TUNDA. Putuskan bersama, jangan "nanti dilihat lagi".
  45-60  SELF-REPORT PROGRESS — Nathanael & Vincent menyebutkan sendiri:
         berapa persen pekerjaan mereka selesai + ALASAN + apa yang bikin tidak 100%.
         (Michael tidak menilai; angkanya dicatat apa adanya oleh Michael/agent.)
  60-75  EKSPLORASI (Vincent) — maksimal 2 kandidat fitur, masing-masing 1 halaman:
         masalah, kenapa penting, estimasi, risiko. Keputusan: MASUK (kapan) atau TUNDA.
  75-85  KUNCI SCOPE PEKAN DEPAN — 1 tema MUST + daftar tugas per orang (ditulis ke kalender).
  85-90  PENUGASAN — siapa share report ke Michael, deadline report = Sabtu/Minggu 12:00
         sebelum offline. Maksimal 3 tugas baru bertanggal.
Output wajib: kalender pekan depan terisi, progress_log terisi, 3 keputusan bertanggal.

=============================================================
3. AGENDA TETAP — ONLINE-A: TRIAGE & BLOCKER (30 menit)
=============================================================
  0-5    Cek cepat 4 angka (hanya yang berubah sejak offline terakhir).
  5-15   BUG P0/P1: status, siapa pegang, kapan tutup. Kalau ada P0 -> agenda lain ditunda.
  15-25  PENGHAMBAT REVIEW: PR yang nunggu Vincent > 1 hari, keputusan teknis nyangkut,
         cut-off Kamis 12:00 masih aman? Kalau tidak -> potong scope sekarang, bukan Kamis.
  25-30  TUGASKAN maksimal 3 hal: apa + siapa + tanggal. Tidak ada tugas tanpa tanggal.
Output: bug board diperbarui, 3 tugas bertanggal, catatan di file ini.

=============================================================
4. AGENDA TETAP — ONLINE-B: REVIEW & KONTEN (45 menit)
=============================================================
  0-15   DEMO CEPAT fitur yang sudah di-merge Vincent (yang bakal dirilis Jumat/Sabtu) —
         Michael menyebutkan skenario uji apa yang akan dia pakai.
  15-25  RENCANA KONTEN PEKAN DEPAN (Michael): 2 topik + pilar (RADAR AI / EDU / PROMO).
         WAJIB cek CONTENT_POSTED_LOG.md biar tidak mengulang. Tentukan siapa review copy
         sebelum post (Vincent cek positioning, Nathanael cek klaim teknis).
  25-35  FUNNEL: lead masuk dari konten pekan ini, mana yang harus di-follow-up Vincent
         (P1->P3 pipeline fase8). Kalau nol lead 2 pekan berturut -> ganti pilar konten.
  35-45  PERSIAPAN RILIS: skenario uji Michael (tertulis), catatan rilis Vincent,
         dan daftar hal yang TIDAK jadi dirilis pekan ini.
Output: daftar uji rilis, kalender konten pekan depan fix, lead yang harus di-follow-up.

=============================================================
5. FORMAT SHARE REPORT (dikirim ke Michael, deadline Sabtu/Minggu 12:00)
=============================================================
Dikirim via chat/WhatsApp grup tim, MAKSIMAL 5 baris. Ini yang bikin progress bisa dicatat.

NATHAANEL:
  1) Selesai pekan ini: ...
  2) Mandek + kenapa: ...
  3) Rencana pekan depan: ...
  4) PROGRESS versi gw: __% — alasan: ...
  5) Butuh bantuan/blocker: ...

VINCENT:
  1) PR yang gw review & merge pekan ini: ...
  2) Hasil eksplorasi: fitur apa + rekomendasi MASUK/TUNDA: ...
  3) Mandek + kenapa: ...
  4) PROGRESS versi gw: __% — alasan: ...
  5) Butuh bantuan/blocker: ...

MICHAEL (tidak perlu lapor manual):
  Persentasenya DIHITUNG OTOMATIS oleh progress_tim.py dari checklist pekan itu
  (konten terpost, uji terima, laporan bug, log konten, CRM). Yang belum tercatat
  tinggal ditandai: `python3 progress_tim.py check --pekan 1 --item 3 --done`

ATURAN ANGKA PROGRESS:
- Persen = penilaian SENDIRI orangnya, bukan nilai dari Michael/agent. Yang dibaca adalah
  TREN antar pekan (naik/turun) + alasannya, bukan angka absolutnya.
- Persen 0-100 per PEKAN (bukan per proyek). 100% = semua tugas yang dia ambil pekan itu selesai.
- Kalau ada yang menulis 100% tapi demo build-nya tidak jalan, itu bahan diskusi di offline —
  bukan hukuman, tapi patokan bahwa "selesai" harus berarti "bisa ditunjukkan".

=============================================================
6. CATATAN KEPUTUSAN (diisi tiap pertemuan)
=============================================================
Format: [tanggal | pertemuan] KEPUTUSAN -> pemilik -> deadline
- (contoh) [20 Sep | OFFLINE kickoff] Scope Siklus 1 = MUST-1..4 fase7, fitur lain TUNDA -> Vincent -> 26 Sep
- (kosongkan sampai pertemuan pertama)
