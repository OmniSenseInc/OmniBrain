# FASE 7 — MVP TERKECIL (yang layak dijual pertama)

Prinsip: MVP BUKAN "versi dengan semua fitur minim" — itu versi paling kecil yang
membuat client MERASA nilai & MAU BAYAR. Fitur yang tidak diuji tidak dipakai.
Kalau belum, rilis bisa molor. Semua "nice-to-have" ditaruh di belakang gerbang.

Karena Fase 5 (validasi) di-skip sementara, scope MVP di bawah memakai asumsi masalah
inti (untung-rugi jelas + stok aman). Jika nanti validasi menunjukkan masalah lain,
prioritasnya digeser — struktur tetap sama.

## A. YANG WAJIB ADA DI RILIS PERTAMA (MUST — menjadi "Definition of Done")
1. FNBSense POS web (dasar):
   - Input transaksi penjualan (menu/produk, qty, total).
   - Daftar menu/produk sederhana (tambah/edit).
   - Data penjualan TERSIMPAN TERPUSAT per client (bagian paling penting: data jadi rapi).
2. SATU laporan otomatis yang paling dirasa nilainya (pilih, default = rekap penjualan
   harian terkirim via WhatsApp):
   - rekap penjualan hari ini / laba kotor harian.
3. SATU cron job AI agent yang paling menyentuh stok:
   - notifikasi stok hampir habis / saran belanja ulang.
4. SATU jalur sekretaris (conversational):
   - tanya "berapa penjualan kemarin?" -> jawab dari data client.
   (Opsi jalur: WhatsApp disarankan sebagai jalur pertama — pemilik F&B tidak buka
   laptop terus.)
5. Pintu masuk: skor kesiapan (framework assessment) yang sudah ada.

## B. YANG DITUNDA (SHOULD / COULD — setelah stabil, jangan dulu)
- Dashboard laporan lengkap (grafik) — cukup 1 laporan dulu.
- Integrasi payment gateway / QRIS / e-wallet.
- Multi-outlet & analitik lanjutan.
- Sekretaris dengan banyak kemampuan (laporan bulanan, dll) — mulai SATU saja.
- Onboarding alur penuh, pelatihan, fitur manajemen peran tingkat lanjut.
Ekuitas: TAMBAHAN FITUR = TUNDA RILIS. Setiap fitur "kalau sempat" = musuh MVP.

## C. DEFINITION OF DONE (rilis lolos KALAU semua terpenuhi)
[ ] Client bisa input transaksi & data tersimpan terpusat.
[ ] Laporan penjualan harian terkirim otomatis (WhatsApp).
[ ] Notifikasi stok hampir habis aktif.
[ ] Sekretaris menjawab minimal 1 pertanyaan umum.
[ ] Skor kesiapan bisa dipakai konsultan (pintu masuk).
[ ] Ada minimal 1 "calon client nyata" (dari Fase 5/beta) yang akan pasang.

## D. TIMELINE (tim 2-5 jam/hari, 3 orang)
- Minggu 1-2: selesaikan bagian MUST yang belum (POS - data - 1 laporan).
- Minggu 3: 1 cron stok + 1 jalur sekretaris.
- Minggu 4: gelombang beta kecil + perbaikan; jadwal soft launch (Fase 9).
(Jangan mulai fitur dari kolom B sebelum MUST & beta klien stabil.)

## E. ATURAN KERAS
- Jangan menambah fitur ke kolom A setelah scope dikunci tanpa keputusan bersama.
- Setiap tugas harus jelas MASUK SCOPE, bukan sekadar "pekerjaan yang bagus". Buang
  yang tidak dipakai client pilot.
- Scope MVP terhubung ke paket (Fase 6): yang dijual adalah paket "Starter" sesuai
  pricing yang dibuat.

## GERBANG FASE 7 (lolos hanya jika)
[ ] Daftar MUST tertulis tegas (A).
[ ] Daftar TUNDA jelas (B); ya tidak masuk scope MVP.
[ ] Definition of Done check-list jelas (C).
[ ] Semua setuju dengan scope (tidak ada yang diam-diam mengerjakan fitur B).