# KALENDER PERENCANAAN OMNISENSE — SIKLUS 1
Periode: Senin 21 Sep 2026 – Minggu 18 Okt 2026 (4 pekan; Minggu 20 Sep = HARI 0, rapat offline kickoff)
Pekan = Senin–Minggu. Tim: 3 orang — Nathanael (panggilan "Andik"), Vincent, Michael (panggilan "Atong")
Pemilik kalender: Michael (Atong). Diperbarui tiap pertemuan OFFLINE (Sabtu/Minggu).
Sumber scope: fase7_mvp.md (kolom A = MUST, kolom B = TUNDA) — JANGAN tambah fitur di luar kolom A.
File pendamping:
  - jadwal_pertemuan_tim.md -> jadwal 3 pertemuan/pekan + agenda tetap tiap pertemuan + format laporan
  - progress_tim.py         -> pencatat progress (Nathanael & Vincent isi % sendiri; Michael dihitung otomatis)
  - kalender_omnisense.py   -> gambar kalender PNG 1080x1350 (sewarna template konten) + prompt AI

=============================================================
0. CARA PAKAI (baca ini dulu)
=============================================================
1. Kalender ini mengulang 4-minggu. Tiap minggu punya TEMA + GERBANG (target yang harus
   lulus sebelum minggu berikutnya jalan). Satu fitur = satu tema, tidak campur.
2. Rilis hanya SATU kali per minggu: build stabil ditandai Sabtu. Tidak ada "rilis dadakan"
   kecuali hotfix bug P0.
3. Urutan kerja selalu satu arah: NATHAANEL bikin -> VINCENT review+merge -> MICHAEL uji & laporkan bug.
   Supaya tidak saling nunggu, Nathanael mengerjakan fitur minggu ini sementara Vincent masih
   menutup PR minggu lalu, dan Michael menguji build hasil minggu lalu (bukan kerjaan setengah jadi).
4. Setiap akhir minggu isi 4 angka (bagian 8). Kalau salah satu macet 2 minggu berturut,
   giliran kerja minggu depan diubah — bukan ditambah jam.

=============================================================
1. PERAN & BATAS KERJA
=============================================================
| Orang            | Peran inti                                   | Output yang diharapkan |
|------------------|----------------------------------------------|------------------------|
| NATHAANEL (Andik)| Kode murni / build fitur (penanggung jawab)  | Fitur jalan + PR siap review, tiap Kamis 12:00 |
| VINCENT          | Revisi kode Nathanael + eksplorasi fitur FNBSense | PR di-merge + 1 catatan fitur eksplorasi/minggu |
| MICHAEL (Atong)  | Debugging/QA + sosmed OmniSense (promo & edu)| Laporan bug ber-evidence + 2 konten terpost/minggu |

ATURAN ANTI-BLOCKING (ini yang bikin perencanaan jelas, bukan cuma daftar tugas):
- R1. Cut-off Kamis 12:00: semua PR fitur sprint wajib dibuka Nathanael sebelum jam itu.
  Lewat cut-off = fitur otomatis pindah sprint depan, tidak dikejar malam.
- R2. Review maksimal 1 hari kerja. Kalau Vincent tidak bisa review 2 hari berturut,
  Nathanael boleh merge sendiri ASAL lulus uji dasar (input transaksi + laporan tidak error).
- R3. Eksplorasi Vincent = timebox 2 jam, maksimal 2x/minggu. Output wajib catatan
  1 halaman (masalah, ide, estimasi, keputusan masuk/tunda). Fitur baru dari eksplorasi
  masuk kolom B fase7 (TUNDA) kecuali disetujui di sinkron Minggu.
- R4. Prioritas Michael: bug P0/P1 dulu, baru konten. Kalau bentrok, tunda 1 konten —
  jangan tunda QA.
- R5. Maksimal 2 fitur in-flight di Nathanael. Satu fitur di-review Vincent, satu di-QA Michael.

=============================================================
2. IRAMA MINGGUAN TETAP (jam WIB, asumsi komitmen 2-5 jam/hari)
=============================================================
3 PERTEMUAN PER PEKAN (detail lengkap + agenda tetap: jadwal_pertemuan_tim.md)
  OFFLINE  : Sabtu 16:00 atau Minggu 19:30, 90 menit -> SINKRON: demo build stabil, isi 4 angka,
             self-report progress, kunci scope pekan depan. Keputusan dicatat di file ini.
  ONLINE-A : hari acak (Sen-Jum) 20:00, 30 menit -> TRIAGE & BLOCKER.
  ONLINE-B : hari acak (Sen-Jum) 20:00, 45 menit -> REVIEW fitur ter-merge + rencana konten.

LAPORAN PROGRESS (sebelum pertemuan offline, maks 12:00 hari itu)
  Nathanael & Vincent : kirim 5 baris ke Michael (format di jadwal_pertemuan_tim.md bagian 4),
                        termasuk % progress VERSI MEREKA SENDIRI + alasan. Jangan dinilai Michael.
  Michael (Atong)     : dicatat otomatis oleh progress_tim.py dari checklist; tinggal tandai yang selesai.
                        Laporan diterima Michael -> dicatat -> setelah Atong konfirmasi, roadmap +
                        kalender harian dibagikan ke tim.

SENIN
  NATHAANEL   : mulai fitur #1 sprint (spesifikasi sudah beku dari sinkron).
  VINCENT : review + merge PR yang masih terbuka dari minggu lalu; mulai eksplorasi 2 jam.
  MICHAEL   : POST KONTEN #1 (19:00) + triage bug board + tulis laporan bug baru.

SELASA
  NATHAANEL   : build lanjut.
  VINCENT : review PR + diskusi cepat ke Nathanael (maks 20 menit, jangan jadi meeting).
  MICHAEL   : uji awal fitur yang baru di-merge (uji cepat), catat temuan.

RABU
  NATHAANEL   : build sampai fitur #1 selesai (siap PR).
  VINCENT : eksplorasi sesi ke-2 -> tulis catatan fitur (masuk/tunda).
  MICHAEL   : uji regresi area inti (input transaksi, laporan, sekretaris).

KAMIS
  12:00    CUT-OFF: PR fitur sprint wajib sudah dibuka Nathanael.
  VINCENT  : review final PR hari ini (maks 1 hari kerja, lihat R2).
  MICHAEL    : POST KONTEN #2 (19:00) + rapikan bug board + log konten.

JUMAT
  VINCENT : merge + tulis catatan rilis (versi + apa yang berubah) -> rilis kandidat.
  NATHAANEL   : hanya hotfix P0/P1; sisanya baca spesifikasi sprint depan.
  MICHAEL   : uji terima rilis kandidat pakai skenario uji tertulis (bagian 5).

SABTU
  MICHAEL   : verifikasi hasil uji, tandai "BUILD STABIL", update checklist DoD fase7.
  OFFLINE 16:00 (kalau offline pekan ini hari Sabtu): demo + 4 angka + self-report + kunci scope.
  SEMUA   : bebas. Kalau ada bug P0 -> bug bash bersama maks 1 jam, lalu stop.

MINGGU
  MICHAEL   : tandai item checklist yang selesai di progress_tim.py, lalu kirim ringkasannya.
  OFFLINE 19:30 (kalau offline pekan ini hari Minggu): demo + 4 angka + self-report + kunci scope.

=============================================================
3. TARGET PER MINGGU (tema + tugas + gerbang)
=============================================================
--- PEKAN 1 | 21-27 Sep | TEMA: DATA PENJUALAN TERSIMPAN TERPUSAT (fase7 MUST-1)
  NATHAANEL   : POS web dasar — input transaksi (produk, qty, total) + daftar menu (tambah/edit)
            + penyimpanan data terpusat per client. Ini fondasi, tidak ada fitur lain.
  VINCENT : siapkan lingkungan kerja (repo/branch, cara deploy, cara Nathanael lihat hasil),
            lalu review kode POS begitu PR pertama masuk. Eksplorasi mulai minggu depan
            (fokus minggu ini: jalur review tidak boleh macet).
  MICHAEL   : pasang sistem QA — bug board (1 sheet, kolom: ID, severity, status, pemilik,
            build, tanggal), skenario uji tertulis untuk POS, CRM lead (perbarui
            client_register.csv). Konten: 2 post (lihat bagian 6).
  GERBANG : (a) transaksi bisa diinput & datanya tetap ada setelah refresh/logout,
            (b) tidak ada bug P0 terbuka, (c) 2 konten terpost + tercatat di log,
            (d) bug board & CRM sudah dipakai (bukan cuma dibuat).

--- PEKAN 2 | 28 Sep - 4 Okt | TEMA: SATU LAPORAN OTOMATIS HARIAN VIA WHATSAPP (MUST-2)
  NATHAANEL   : rekap penjualan harian otomatis terkirim ke WhatsApp (format ringkas, 1 pesan),
            + pintu masuk skor kesiapan (kalkulator_kesiapan dipakai di alur).
  VINCENT : review + merge laporan; mulai eksplorasi 2x2 jam -> 2 catatan fitur.
            Eksplorasi dipakai untuk memilih 1 fitur terbaik jadi kandidat SIKLUS 2.
  MICHAEL   : uji terima laporan (uji: tanggal salah, tidak ada transaksi, transaksi banyak),
            laporan bug, konten 2 post. Mulai catat lead masuk dari konten ke CRM (P1).
  GERBANG : (a) laporan terkirim otomatis tanpa disentuh manual 1 hari penuh,
            (b) angka laporan cocok dengan data yang diinput (uji silang manual),
            (c) 2 konten + minimal 1 lead tercatat (kalau 0, ganti pilar konten minggu 3).

--- PEKAN 3 | 5-11 Okt | TEMA: CRON STOK + SEKRETARIS 1 PERTANYAAN (MUST-3 & MUST-4)
  NATHAANEL   : notifikasi stok hampir habis / saran belanja ulang + sekretaris menjawab
            1 pertanyaan ("berapa penjualan kemarin?"). Satu jalur saja: WhatsApp.
  VINCENT : review + merge keduanya; finalisasi 1 kandidat fitur untuk siklus 2
            (tulis 1 halaman: masalah, kenapa penting, estimasi, risiko).
  MICHAEL   : uji jawaban sekretaris terhadap data asli (uji pertanyaan yang datanya kosong
            dan pertanyaan di luar scope -> harus menjawab jujur "belum ada data",
            bukan mengarang). Konten 2 post.
  GERBANG : (a) notifikasi stok muncul tanpa dipicu manual, (b) sekretaris menjawab benar
            dari data client & tidak berhalusinasi saat data kosong,
            (c) tidak ada bug P0/P1 terbuka lebih dari 3 hari.

--- PEKAN 4 | 12-18 Okt | TEMA: HARDENING + SIAP BETA (gerbang ke fase9)
  NATHAANEL   : bug bash hasil minggu 1-3, perbaiki semua P1, rapikan hal teknis yang
            bikin client bingung saat dipakai. TIDAK menambah fitur baru.
  VINCENT : uji coba internal end-to-end (peran owner: login -> input -> laporan ->
            tanya sekretaris), siapkan cara pasang untuk kafe pilot + data awal.
  MICHAEL   : jalankan checklist DoD fase7 (6 poin) sampai tuntas, uji dari sisi orang awam
            (bukan tester), siapkan materi pelatihan 1 halaman, konten 2 post
            (termasuk 1 konten promo assessment gratis).
  GERBANG : (a) 6/6 checklist DoD fase7 tercentang, (b) minimal 3 calon kafe pilot
            dihubungi & tercatat di CRM, (c) siklus 2 sudah punya scope tertulis
            (dari catatan eksplorasi Vincent).

=============================================================
4. ALUR SERAH TERIMA (biar bug tidak "hilang di obrolan")
=============================================================
SIAP DIKERJAKAN (sebelum Nathanael mulai):
  - Tujuan fitur 1 kalimat + cara mengujinya + batas scope (apa yang TIDAK dikerjakan).
  - Sudah masuk kolom A fase7. Kalau tidak ada di situ = tunda.
SIAP DI-REVIEW (sebelum Vincent review):
  - Kode jalan di mesin Nathanael, ada catatan singkat "apa yang berubah & cara mencoba".
  - PR kecil (maks ~300 baris perubahan). PR besar = dipotong, bukan direview borongan.
SIAP DIRILIS (sebelum build stabil):
  - Tidak ada bug P0/P1 terbuka, catatan rilis ditulis, Michael sudah uji terima.

TINGKAT BUG & BATAS WAKTU:
  P0 = data hilang / transaksi gagal / app tidak bisa dibuka -> lapor < 1 jam,
       hotfix < 24 jam, Nathanael stop semua kerjaan lain.
  P1 = fitur MUST salah (laporan salah hitung, sekretaris salah jawab) -> < 3 hari.
  P2 = kosmetik/enhancement -> masuk backlog, dibahas di pertemuan offline (jangan kerjakan
       diam-diam, itu yang bikin rilis molor).

FORMAT LAPORAN BUG (Michael, wajib lengkap — bug tanpa ini akan ditolak Nathanael):
  [P?] Judul singkat | tanggal & jam | versi build
  1) Langkah reproduksi: 1-2-3
  2) Yang diharapkan vs yang terjadi
  3) Bukti: screenshot / log / angka
  4) Perangkat & browser

=============================================================
5. KALENDER KONTEN (Michael) — 2 post/minggu, Senin & Kamis 19:00
=============================================================
WAJIB sebelum tiap post: cek /home/ubuntu/ai-agency/CONTENT_POSTED_LOG.md (jangan ulang topik),
pakai sistem visual terkunci (4:5, monokrom gelap, footer @omnisense_id • omnisense.id),
dan tiap post sertakan CTA ke action ("DM / buka profil -> lanjut ke WhatsApp").
Setelah post: catat di log (tanggal | platform | judul | topik). OmniSense = pilar utama;
FNBSense maksimal 1 baris footnote, jangan ditonjolkan setara.

| Tanggal           | Pilar    | Isi                                                                 |
|-------------------|----------|---------------------------------------------------------------------|
| Sen 21 Sep        | RADAR AI | Berita AI terbaru dari riset berkala -> poster + prompt ID & EN       |
| Kam 24 Sep        | EDU      | "AI agent itu apa, dan apa kerjanya untuk bisnis" (bahasa awam)      |
| Sen 28 Sep        | RADAR AI | Berita AI terbaru                                                    |
| Kam 1 Okt         | PROMO    | "Konsultasi kesiapan gratis: apa yang kamu dapat" (8 dimensi, 1 sesi)|
| Sen 5 Okt         | RADAR AI | Berita AI terbaru                                                    |
| Kam 8 Okt         | EDU      | "3 tanda data bisnis berantakan & cara merapikannya"                 |
| Sen 12 Okt        | RADAR AI | Berita AI terbaru                                                    |
| Kam 15 Okt        | EDU/CASE | Pelajaran dari uji coba nyata di lapangan (FNBSense cukup 1 footnote)|
| Min 18 Okt (opsi) | REKAP    | Rekap/tanya-jawab DM — penutup siklus                                 |

Target siklus 1: 8-9 konten terpost, minimal 3 lead masuk dari konten (tercatat di CRM).

=============================================================
6. BATAS BEBAN (WIP) — jangan lewat, walau "tinggal dikit"
=============================================================
NATHAANEL : maks 2 fitur in-flight; 70% build, 20% hotfix, 10% rapi teknis.
VINCENT  : maks 2 PR di meja + 1 eksplorasi; 40% review/merge, 30% eksplorasi (timebox),
           30% keputusan & klien (peran CEO di fase8 — lihat risiko R-A di bagian 8).
MICHAEL  : maks 3 bug P0/P1 aktif + 2 konten/minggu; 40% QA, 35% konten, 25% OPS
           (CRM, log konten, kalender ini).
Kalau ada yang lewat batas: pekerjaan berikutnya TIDAK diambil, tapi dipindah ke sprint depan.

=============================================================
7. 4 ANGKA YANG DIISI TIAP PERTEMUAN OFFLINE
=============================================================
1. Item MUST fase7 selesai minggu ini (target: 1 per minggu).
2. Bug P0/P1: berapa terbuka, rata-rata berapa hari sampai tutup.
3. Konten terpost (target 2) + lead masuk dari konten (P1 di CRM).
4. Calon pilot/beta yang dihubungi (mulai diisi minggu 3, target 3 di akhir siklus).
Kalau angka 1 atau 3 nol dua minggu berturut-turut -> ubah cara kerja, bukan tambah jam.

=============================================================
8. RISIKO & PENANGKALNYA
=============================================================
R-A. Vincent jadi bottleneck (review + keputusan klien sekaligus).
     -> cut-off Kamis 12:00, review maks 1 hari, aturan eskalasi R2 (Nathanael boleh merge
        sendiri kalau lulus uji dasar).
R-B. Eksplorasi Vincent membengkak jadi fitur liar yang bikin rilis molor.
     -> timebox 2 jam x2/minggu, output catatan 1 halaman, default TUNDA sampai disetujui.
R-C. Michael single point (QA + konten) -> salah satu pasti bolong.
     -> QA pakai skenario uji tertulis (bukan ad-hoc), prioritas QA > konten (R4).
R-D. Rilis mingguan diisi fitur kolom B fase7 -> MUST tidak selesai.
     -> gerbang mingguan hanya menerima item kolom A.
R-E. Konten jalan tapi nol lead.
     -> ukur lead tiap minggu; 2 minggu nol = ganti pilar (tambah promo/edu, kurangi berita).

=============================================================
9. GERBANG AKHIR SIKLUS 1 (Minggu 18 Okt) — lanjut ke SIKLUS 2 (mulai 19 Okt)
=============================================================
[ ] Checklist DoD fase7: 6/6 tercentang.
[ ] Minimal 3 calon kafe pilot siap dipasang (bahan beta fase9).
[ ] Bug P0 = 0, P1 = 0 (atau sudah ada rencana perbaikan bertanggal).
[ ] 8-9 konten terpost, log konten & CRM jujur terisi.
[ ] Scope siklus 2 tertulis (1 halaman dari eksplorasi Vincent) + tema per minggu.
Kalau ada yang belum: siklus 2 dimulai dengan item itu sebagai tema minggu 1, bukan
ditumpuk sambil mulai fitur baru.

=============================================================
10. YANG PERLU DIKONFIRMASI TIM (biar kalender tidak salah asumsi)
=============================================================
1. Jam komitmen riil per orang (kalender ini pakai asumsi 2-5 jam/hari).
2. Vincent masih ikut memimpin sesi konsultasi gratis (fase8: CEO & CMO bersama)?
   Kalau ya, beban review-nya harus dipotong, bukan ditambah.
3. Rilis mingguan Sabtu cocok dengan jadwal kerja kalian? Kalau tidak, geser cut-off-nya
   (yang penting tetap 1 cut-off + 1 rilis per minggu).

=============================================================
11. LAPORAN PROGRESS & GAMBAR KALENDER (cara teknisnya)
=============================================================
ALUR LAPORAN (Atong yang pegang):
  1. Nathanael & Vincent kirim laporan 5 baris ke Atong sebelum pertemuan offline (format bagian 4
     di jadwal_pertemuan_tim.md), termasuk % progress versi mereka sendiri + alasan.
  2. Atong catat:  python3 progress_tim.py add --orang Nathanael --pekan 1 --persen 40 --catatan "..."
  3. Item kerja Atong sendiri ditandai:  python3 progress_tim.py check --pekan 1 --item 3
     (persentase Atong dihitung otomatis dari checklist berbobot, tidak dikira-kira).
  4. Lihat rekap:  python3 progress_tim.py status --pekan 1   /   riwayat
  5. Minta laporan ke tim (teks siap tempel ke grup):  python3 progress_tim.py minta --pekan 2
  6. Simpan rekap jadi file:  python3 progress_tim.py report --pekan 1
  ATURAN: persen Nathanael & Vincent TIDAK ditakar Atong — mereka yang mengisi. Yang dibaca adalah
  tren antar pekan + alasan di catatan, bukan angka absolutnya.

GAMBAR KALENDER (buat dibagikan / ditempel):
  .venv/bin/python kalender_omnisense.py --progress-pekan 1 --cta "JADWALKAN KONSULTASI GRATIS"
  -> kalender_omnisense.png (1080x1350, warna & tata letak SAMA dengan template konten OmniSense)
  -> plus cetakan prompt gambar AI (ID + EN) kalau mau versi artistik.
  Data kalender (tanggal, tag, tema) ada di kalender_data.json — ubah di situ kalau ada perubahan.
  Undian hari online pekan berikutnya:
  .venv/bin/python kalender_omnisense.py --acak-online --pekan 5 --tgl-senin 2026-10-19
