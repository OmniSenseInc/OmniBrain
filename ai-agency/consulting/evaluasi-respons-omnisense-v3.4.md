# Respons dan fleksibilitas OmniSense — 4 Oktober 2026

Perbaikan dipasang di VPS OmniSense berdasarkan contoh pesan WA yang dikirim pemilik. Pesan tersebut menunjukkan pembuka sampai ke WA, tetapi bukan bukti seluruh pendalaman/review tim telah teruji dengan klien nyata.

**Bukan fine-tuning model.** Yang diperbaiki: instruksi, SOP/skill, pengelolaan percakapan, pemeriksaan balasan dan pengujian. Bobot kuis tetap heuristik. Isi asal yang terlihat masuk akal tidak bisa diketahui niatnya; diperlukan klarifikasi, contoh dan bukti.

- Pembuka baru mendengar proses/keluhan dan meminta contoh kejadian. Skor ditampilkan jika diminta, tanpa menyimpulkan penyebab atau kesiapan proyek dari angka. Harga tidak disebut di pembuka.
- Jawaban acak yang jelas diminta klarifikasi. Pertanyaan balik, koreksi, pricing, privasi dan beberapa permintaan di luar topik tidak dicatat sebagai jawaban discovery atau memajukan tahap. Belum tahu dicatat sebagai ketidakpastian, bukan nol.
- Pricing dijawab bila ditanya: konsultasi gratis, biaya pengerjaan mengikuti scope manusia tanpa nominal rekaan. Biaya operasional yang dikeluhkan klien tetap boleh dianalisis.
- Model menanggapi pesan terbaru dan konteks kasus sendiri. Jika respons tidak layak/gagal, fallback tetap mengakui isi keluhan dan melanjutkan pertanyaan. Beberapa klaim negatif tanpa dukungan sumber ditolak; pemeriksaan ini terbatas dan tidak menjamin semua isi model benar.
- Koreksi disimpan terpisah dan menjadi konflik yang perlu review manusia sebelum options; tidak hilang saat riwayat pertanyaan bergulir. Tidak ada pemberian izin tools, approval atau harga dari teks klien.

**Pengukuran:** 98 uji unit/regresi lulus (69 assessment/workflow/mission, 12 gateway dan 17 dialogue). Dalam uji akhir 12 kasus sintetis, 12 memenuhi pemeriksaan alur serta proksi relevansi; 5 panggilan model berhasil dan 3 responsnya dipakai. Respons lain memakai template/fallback. Semua memakai database sementara dan transport simulasi, tanpa pesan ke klien.

Evaluasi awal menemukan asumsi bahwa penyalinan jadwal manual berarti validasi tidak ada. Instruksi dan guard diperbaiki; fallback yang semula terlalu umum dibuat merujuk penjelasan klien. Respons aktual dan fixture ada dalam evaluasi JSON paket.

**Batas hasil:** kata kunci bukan ukuran akurasi; sampel kecil belum membuktikan fleksibilitas lintas semua sektor, stabilitas seluruh model, deteksi semua input ngawur atau manfaat bisnis. Pendalaman masih memakai kerangka enam topik, dengan ruang pertanyaan balik/koreksi di antaranya. Perlu evaluasi berlabel dan engagement nyata untuk kalibrasi. Domain final tidak dideploy dalam pekerjaan ini.

Layanan gateway/preview aktif dan bridge WA connected. Kasus lama mempertahankan arti pertanyaan lama; pembuka baru dapat diuji lewat screening baru. Gateway/API 1.0, dialogue 1.1, paket 3.4; bank/engine 3.1 dan workflow 3.2 tetap.
