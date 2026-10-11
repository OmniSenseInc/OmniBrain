# Alur konsultasi dan operasi OmniSense — 3.5

5 Oktober 2026. Melanjutkan perilaku 3.4. Visi/misi, bank penilaian 3.1, bobot, engine, protokol API dan workflow engagement 3.2 tetap berlaku. Ini perbaikan aplikasi dan instruksi operasional, bukan fine-tuning bobot model.

## Dua pintu masuk

Website konsultasi menawarkan chat kebutuhan tanpa kuis atau screening. Chat langsung membuka draf `[OMNISENSE-MULAI]`; pengunjung sendiri mengirimkannya. Jalur DM terbatas meminta persetujuan pencatatan melalui `/setuju`. Tanpa persetujuan belum ada kasus/discovery yang dibuat; penanda maupun persetujuan ini tidak memberi akses tool atau peran tim. Tawaran persetujuan hanya menyimpan identitas hash dan waktu, dibatasi chat dan 24 jam. Percakapan baru bertanya konteks bisnis; skor kuis tidak dibuat-buat. `/hasil` menjelaskan belum ada skor jika masuk tanpa kuis. Angka null di payload internal hanya merepresentasikan belum diketahui, tidak berarti klien mengisi kuis.

Screening memakai lima langkah: konteks lalu empat kelompok berisi empat pertanyaan. Semua 16 butir, opsi belum tahu, bobot dan engine asli dipertahankan. Progress mengikuti isian; validasi dekat kolom/pertanyaan dan fokus ke isian bermasalah. Baseline opsional harus lengkap jika dipakai. Draft tab opsional menggunakan sessionStorage, schema/bank version dan batas 2 jam sejak terakhir disimpan; bukan penyimpanan lintas perangkat. Persetujuan, private code dan hasil kirim tidak disimpan dalam draft. Refresh memulihkan isian untuk dihitung ulang. Mulai ulang menghapus draft.

Hasil lokal tidak dikirim sebelum persetujuan dan klik. API fetch memiliki timeout; retry mempertahankan request_id pada sesi browser yang sama. Perhitungan baru membatalkan persetujuan/tautan sebelumnya. Server mengembalikan sisa umur kode asli pada retry. WhatsApp tetap memerlukan klik dan Kirim pengunjung.

## Pendalaman dan tim

Penjelasan tetap self-report. Koreksi tidak otomatis memvalidasi scope; ralat/yang saya maksud/sebenarnya bukan turut dikenali sebagai koreksi. `/stop` menyimpan tahap sebelumnya. `/lanjut` kembali ke tahap tersebut, termasuk menunggu persetujuan dan antrean tim, tanpa mundur diam-diam ke discovery. Legacy paused di cursor akhir dipulihkan ke konfirmasi. Hold izin tidak hilang karena /lanjut.

Setelah ringkasan, klien menyetujui review tim; baru intake diimpor secara idempotent ke ledger. Tim menetapkan reviewer, memeriksa scope/koreksi/bukti dan menjalankan gerbang diagnosis, alternatif, proposal, pilot, go-live serta adopsi. Jangan menyatakan tim menerima, proyek berjalan, jadwal, harga atau izin telah disetujui hanya karena antrean tersimpan.

## Keandalan

Reservasi panggilan model disimpan atomik di database gateway, maksimal 16 percobaan per kasus sejak versi ini dipasang. Failed attempt turut dihitung, restart tidak menghapus batas. Outcome reserved/accepted/fallback/provider_error dicatat tanpa isi provider. Dua slot model, timeout total 25 detik termasuk antrean slot, tanpa tools. Batas ini bukan anggaran rupiah atau quota provider. Pemakaian sebelum upgrade tidak dapat direkonstruksi dari data lama dan tidak diimpor sebagai estimasi.

Provider gagal atau hasil tidak layak memakai respons terstruktur; scoring, pertanyaan dan gerbang aplikasi tetap berjalan. Status pengiriman gagal dicatat; jangan mengirim ulang otomatis karena hasil kirim ambigu dapat menyebabkan duplikasi. Operator meninjau failed/pending sebelum menentukan recovery. Tidak ada mekanisme otomatis yang menjamin pengiriman WhatsApp berhasil.

Operator dapat menjalankan `python3 gateway_operator.py --summary` untuk jumlah tahap kasus, status pengiriman, outcome model dan usia antrean tim tertua, tanpa menampilkan isi kasus/nomor/kode privat. Perintah antrean lengkap tetap untuk operator berwenang dan tidak boleh dicetak ke chat klien. `/hapus` serta retensi kasus membersihkan catatan model per kasus; catatan engagement terpisah tetap mengikuti aturan sebelumnya.

## Validasi

Suite assessment/decision/workflow/contract/gateway/dialogue serta regresi 3.5 memakai database sementara. Integrasi memakai plugin loader dan hook Hermes aktual, tetapi transport WhatsApp serta provider gagal disimulasikan. Browser memakai kasus sintetis pada API lokal; pengujian live tidak mengirim pesan WhatsApp atau membuat kasus klien. Pengujian sintetik tidak membuktikan akurasi diagnosis semua bidang atau hasil delivery bisnis nyata.


## Patch 3.5.1 — 5 Oktober 2026
108 tes regresi/isolasi/ingress simulasi lulus. Filter kandidat menolak pola salah identitas serta klaim tindakan eksternal yang tidak tersedia dan memakai fallback. Browser lokal diuji dengan kode kedaluwarsa: hasil tetap terlihat, consent dibatalkan, href WhatsApp kosong dan fokus ke hitung ulang. Sisa masa berlaku kode aktif mengikuti API. Dua berkas runtime terpasang; layanan dan API health terverifikasi. Filter bukan jaminan akurasi universal. Lihat tambahan patch pada consulting/GATEWAY_KONSULTASI_V35.md.
