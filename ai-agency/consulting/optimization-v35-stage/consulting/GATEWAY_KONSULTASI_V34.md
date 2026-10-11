# Respons konsultasi OmniSense 1.1 — pengembangan 3.4

4 Oktober 2026. Berlaku untuk plugin DM konsultasi di VPS OmniSense. Protokol gateway/API tetap 1.0, bank/engine 3.1, workflow 3.2, kontrak agent 1.0. Dokumen 3.3 menyimpan desain transport dan hasil terdahulu; dokumen ini memperbarui perilaku percakapan. Tidak ada perubahan bobot model/fine-tuning, bobot kuis, harga layanan atau deployment domain final.

## Koreksi alur

- Pembuka baru mendengar proses dan keluhan klien lalu menanyakan contoh kejadian. Tidak menampilkan CASE/skor sebagai fokus, menyebut harga, menyimpulkan prasyarat atau meminta angka baseline sebagai pertanyaan pertama. `/hasil` tetap menampilkan skor server dengan batas interpretasinya. Kasus yang sudah aktif mempertahankan arti pertanyaan awal lama ketika dilanjutkan; pesan WA yang sudah terkirim tidak dapat diubah oleh penggantian kode.
- Konteks acak yang jelas, kosong makna, atau instruksi menyimpang diminta klarifikasi. Tidak menyatakan klien bohong. Pilihan kuis seragam atau valid secara tipe tidak membuktikan kejujuran maupun kecurangan. Skor hanya menghitung pilihan dan tetap self-report; jawaban asal yang tampak masuk akal tidak dapat dipastikan tanpa contoh dan bukti.
- Pertanyaan balik, permintaan harga, privasi, koreksi dan penyimpangan yang dikenali tidak menjadi jawaban discovery dan tidak memajukan cursor. Pertanyaan balik dapat dijawab model tanpa kehilangan pertanyaan yang sedang dibahas. Koreksi dicatat sebagai self-report dan menjadi konflik yang harus ditinjau sebelum tahap options; bukan perubahan scope terverifikasi atau approval.
- “Belum tahu/belum diukur” dicatat sebagai ketidakpastian, bukan nol atau metrik rekaan. Dampak bisa mulai dari contoh kualitatif. Baseline terukur tetap diperlukan ketika keputusan bisnis/pilot menuntut pembuktian, bukan syarat menyambut klien.
- Pricing reaktif: bila ditanya, jelaskan konsultasi gratis dan biaya implementasi mengikuti scope manusia. Tidak memberi nominal dari kuis. Jangan menyamakan biaya operasional yang dikeluhkan klien dengan pertanyaan harga jasa.
- Pertanyaan soal mengirim data pelanggan/password/token dijawab tanpa model dengan batas privasi. Pernyataan penolakan izin yang eksplisit menahan pendalaman dari tahap mana pun; lanjut chat tidak menghapus hold. Matcher tetap heuristik, bukan verifikasi izin; jawaban positif tidak pernah memberikan tools/akses.
- Model memakai latest_message, intent aplikasi, konteks, jawaban dan koreksi kasus sendiri. Maksimal 16 panggilan per kasus dalam proses berjalan, dua panggilan serentak, timeout dan tanpa tools. Aplikasi tetap mengatur pertanyaan, cursor, token, persetujuan dan ledger. Batas panggilan ini bukan estimasi biaya atau kuota provider dan tidak persisten setelah restart.
- Tidak disebut berarti belum diketahui, bukan tidak ada. Contoh: penyalinan manual tidak membuktikan ketiadaan validasi. Guard output menolak beberapa klaim negatif tanpa dukungan literal sumber serta harga yang tidak diminta; ini pemeriksaan terbatas, bukan pemeriksa fakta menyeluruh. Balasan buruk/gagal diganti fallback yang mengutip penjelasan klien dan melanjutkan satu pertanyaan tanpa mengarang penyebab.

## Pengukuran

`test_consultation_dialogue.py` menambah 17 uji terhadap 12 uji gateway dan 69 uji assessment/workflow/mission. `evaluate_dialogue_v34.py` memakai 12 kasus sintetis, model provider aktif, database sementara dan transport WhatsApp simulasi. Mencakup stok, penjadwalan, kuis acak, angka belum diketahui, pertanyaan balik, koreksi keluhan, pilihan non-AI, harga, privasi, injection dan topik menyimpang.

Pemeriksaan otomatis menilai cursor, pencatatan jawaban, timing harga/skor, satu pertanyaan, angka yang tidak direka dan proksi relevansi kata. Baca respons aktual untuk menilai makna. Pada evaluasi awal ditemukan asumsi ketiadaan validasi yang belum didukung; instruksi dan guard dikoreksi, lalu diuji kembali. Respons fallback juga diperbaiki karena terlalu umum. Lihat evaluasi JSON dan ringkasan hasil versi ini untuk hasil terakhir, termasuk apakah respons model dipakai atau diganti fallback.

Tidak mengklaim persentase akurasi klinis/bisnis, kemampuan mendeteksi semua kebohongan, fleksibilitas seluruh domain atau kesempurnaan model dari sampel kecil. Belum ada dataset engagement terkalibrasi, holdout klien nyata, pengukuran stabilitas lintas model, atau pengujian pendalaman WA nyata lengkap. Contoh pembuka yang dikirim pemilik membuktikan pesan awal pernah diterima; bukan bukti seluruh jalur review tim/delivery selesai. Pengujian model tidak mengirim pesan kepada klien maupun home.

## Operasi dan pemasangan

Pemasangan menambah modul dialogue dan mengganti store/plugin yang telah diuji, tanpa mengubah core Hermes atau menghapus database kasus. Hash baseline dibandingkan dengan sumber aktif dan backup dibuat terlebih dahulu. Restart dilakukan setelah tidak ada agent aktif; health API/bridge diperiksa. Persetujuan ringkasan, idempotensi, isolasi pengirim/chat dan reviewer manusia tetap berlaku.

Konteks kuis yang tidak bermakna disimpan sebagai konteks awal; klarifikasi klien dipisahkan, dan intake meminta reviewer mengidentifikasi proses yang sebenarnya. Metadata koreksi/konflik dibawa ke ledger, sehingga scope/handoff tidak diam-diam diperlakukan sebagai sudah benar. Tim tetap perlu menyelaraskan scope, penilaian dan bukti sebelum melanjutkan gerbang berikutnya.
