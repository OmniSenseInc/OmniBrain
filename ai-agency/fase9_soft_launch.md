> CATATAN REVISI4Oktober2026: Kerangka historis; publikasi/go-live tetap keputusan tim. Gerbang lama bukan pekerjaan wajib baru dari revisi ini.

# FASE 9 — SOFT LAUNCH / BETA (uji dengan klien percontohan kecil)

Tujuan: buktikan bahwa alur OmniSense (lead -> konsultasi -> pasang -> dipakai)
benar-benar jalan dengan orang sungguhan, sebelum membuka ke publik luas.
CATATAN PENTING: karena Fase 5 (validasi wawancara) di-skip, beta ini SEKALIGUS
menjadi validasi — feedback di sini menggantikan sebagian data Fase 5. Jadi jangan
terburu-buru; hasil beta menentukan rilis publik (Fase 10).

## 1. PILIH KLIEN PERCONTOHAN (3-5 bisnis)
- Target: pemilik F&B (beachhead FNBSense) yang sudah hangat dan bisa ditemui cepat
  (kenalan, komunitas, mutual di WA).
- Ragamkan: 1 yang cepat "ya", 1 yang sedang, 1 yang agak skeptis — biar lihat
  reaksi bermacam.
- JANGAN: orang yang pasti "iya" semua (teman dekat) — supaya tidak bias hasil.

## 2. JALANKAN ALUR OMNISENSE UTUH (jangan memotong)
Untuk tiap klien pilot, jalankan langkah di omnisense_ops (A1-A7):
1. Booking konsultasi gratis (CEO+CMO pelaksana).
2. Sesi -> isi 32 pertanyaan -> hitung skor + band (kalkulator_kesiapan.py).
3. Kirim laporan (pakai template: eksekutif/WA versi pendek dulu).
4. Tawaran: FNBSense Starter untuk yang siap / build untuk yang custom.
5. On-board: setup FNBSense, input data awal, latih. (CTO)
6. Hipercare minggu pertama + catatan dukungan.

## 3. PENGUMPULAN FEEDBACK (yang paling penting)
Setiap klien pilot diberi SIMPEL tracking:
- Apakah mereka MEMAKAI tiap hari (berapa transaksi) vs berhenti?
- Faktor "wow" (yang membuat mereka bilang bagus) — catat kata mereka.
- Pain/hambatan (apa yang bikin mereka kesal / tidak selesai).
- Satu permintaan fitur paling mendesak (jangan build semua; catat saja).
- Kesediaan lanjut membayar / berlangganan setelah masa beta.

## 4. KESUKSESAN BETA (Definisi — gerbang Fase 9 lolos jika):
[ ] >=3 klien pilot benar-benar memakai (transaksi harian, bukan cuma pasang)
[ ] Tidak ada bug/blok yang membuat mereka berhenti memakai.
[ ] Sebagian besar klien (>=60%) mau lanjut membayar setelah beta.
[ ] Kamu tahu 1-3 "fungsi yang paling disukai" dan 1-3 hal paling menghambat.
Jika belum: JANGAN lanjut publik luas — perbaiki dulu yang menghambat, ulang pada
klien yang tersisa / ganti.

## 5. PERBAIKAN SEBELUM RILIS PUBLIK
- Fokus hanya pada hambatan yang membuat klien berhenti / mau kabur.
- Jangan garap yang "nice-to-have" — biar ke Fase 10 tidak memuat produk mentah.

## 6. TIMELINE
- Minggu 1: pilih 3-5 klien pilot + booking konsultasi pertama.
- Minggu 1-2: jalankan alur, pasang FNBSense, hypercare.
- Minggu 2-4: ukur pemakaian & rasa; kumpulkan feedback.
- Akhir minggu 4: putuskan (lolos ke Fase 10) atau perbaiki + ulang.

## CATATAN
- Beta bisa "bayar kecil" atau "gratis sementara" — yang penting ukur kemauan BAYAR
  setelahnya. Catat angka mau bayar dari percakapan (input Fase 6 final).
- Jaga margin: catat jam dukungan tim tiap klien (bidang Fase 6 — jangan sampai
  beta bikin rugi waktu tanpa sadar).
- Klien beta yang sukses = aset untuk testimoni di Fase 10.

## GERBANG FASE 9 — LULUS HANYA JIKA semuanya di bagian 4 terpenuhi.