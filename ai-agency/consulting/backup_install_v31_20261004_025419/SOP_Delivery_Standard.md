# SOP DELIVERY STANDAR (build, QA, launch) — OmniSense
Agar tiap deliverable konsisten & tidak improvisasi. Pemilik: CTO.
Prinsip (riset): baseline dulu, bangun di staging, ada human review gate,
punya rollback, dan komunikasi failure mode dengan jujur.

=============================================================
1. BASELINE SEBELUM BANGUN (wajib)
=============================================================
[ ] Catat metrik awal yang jadi KPI proposal: halaman transaksi/hari, jam
    input manual/minggu, akurasi stok, waktu persiapan laporan.
- Tanpa baseline, klaim "menjadi lebih baik" tidak punya pembanding.
- Baseline diambil saat sesi/onboarding; simpan di folder klien.

=============================================================
2. BUILD DI STAGING
=============================================================
[ ] Kerjakan di lingkungan uji (label "[TEST]"), JANGAN langsung produksi.
[ ] Akses/credential tersimpan aman & teruji.
[ ] Tiap langkah diuji dulu sebelum ditumpuk: trigger -> aksi -> output.
[ ] Error handling di tiap titik eksternal: kalau API/VPS mati, ada fallback
    (retry, notifikasi manusia, pesan gagal yang sopan).
[ ] Dokumentasikan build (trigger, alur, kondisi, output) — buat orang lain
    bisa audit dalam 20 menit.

=============================================================
3. QA & HUMAN REVIEW GATE (wajib)
=============================================================
[ ] Uji dengan data nyata 20-50 contoh (bukan 1 contoh).
[ ] Uji kasus tepi: data kosong/salah format/instruksi konflik.
[ ] GATE SEPERTI INI (pilih sesuai risiko):
    - Keluaran ke pelanggan / keputusan uang: 100% review manusia dulu.
    - Tugas rutin internal: review sampling (mis. 30%) lalu auto.
[ ] Persetujuan klien TERTULIS sebelum go-live ("approved" di email/WA cukup).

=============================================================
4. FAILURE MODE KHUSUS AI (deteksi & balas)
=============================================================
- Data drift / data kotor -> deteksi: monitor akurasi mingguan; balas jujur:
  "datanya bergeser, kami perbaiki sumber dulu" (jangan diam).
- Prompt sensitif (hasil melenceng) -> versikan prompt + rollback.
- Limit API / VPS down -> fallback (lihat no.2) + info ke klien dalam 24 jam.
- Tim tidak pakai -> SOP retainer: pelatihan ulang + nilai yang terlihat.

=============================================================
5. GO-LIVE PROTOKOL
=============================================================
[ ] Persetujuan klien tertulis + jadwal launch (hari kerja, bukan Jumat sore).
[ ] Aktifkan produksi, matikan test; update endpoint.
[ ] 30 menit pertama: pantau log langsung; minta klien uji live.
[ ] Kirim email go-live: apa yang live, cara pantau, kontak darurat, jadwal
    check-in pertama (48 jam).
[ ] 48 JAM CHECK-IN: review log 2 hari, jumlah trigger vs ekspektasi, sampel
    output, spike error; kirim "semua hijau" + angka.
[ ] DAY-7 UPDATE tertulis (hasil minggu pertama).

=============================================================
6. SERAH TERIMA (handoff)
=============================================================
Dokumen yang diserahkan (4 item minimum):
1. Ringkasan sistem (apa yang dibangun & cara kerjanya)
2. Panduan operasional harian (siapa melakukan apa)
3. Panduan troubleshooting (gejala -> langkah -> kontak)
4. Rencana pemeliharaan/dukungan (jadwal, biaya, kontak)
[ ] Training tim klien (45 menit, rekam): demo skenario nyata lalu edge case.
[ ] Rollback plan: cara mematikan sistem aman kalau terjadi masalah besar.

=============================================================
GAGAL UMUM
=============================================================
- Langsung produksi tanpa staging -> koreksi mahal.
- QA 1 contoh -> lolos lalu rusak di minggu pertama.
- Tidak ada rollback -> panik saat error.
- Klien tidak diberi tahu saat masalah -> hilang trust (laporkan <24 jam).