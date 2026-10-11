# Progres OmniSense — 4 Oktober 2026

Pekerjaan yang terputus karena limit dilanjutkan dan perubahan gateway dipasang di VPS OmniSense serta preview yang sudah ada. Website pada domain final di hosting lain belum dideploy melalui pekerjaan ini.

- **Konsultan dan penilaian:** visi/misi digitalisasi dan AI agent custom tetap menjadi acuan. Konsultasi termasuk pendalaman tetap gratis; build/install mengikuti scope yang disahkan manusia. Bank berisi 16 pertanyaan screening dan 32 pertanyaan discovery dalam delapan dimensi. Jawaban belum diketahui menghasilkan rentang, bukan nilai palsu. Klaim klien tidak otomatis menjadi bukti terverifikasi. Diagnosis membandingkan perbaikan proses, software biasa dan AI.
- **Operasi agency:** ledger per kasus/tenant, revisi dan event idempoten, pemilik proses, handoff, perubahan scope dan gerbang persetujuan manusia. Kontrak agent memuat batas aksi, eskalasi, stop/rollback serta rencana dan bukti evaluasi pilot. Ini bukan bukti bahwa seluruh runtime agent klien sudah dibangun.
- **Gateway website → WA:** melihat hasil tidak mengirim jawaban. Consent dan tombol konsultasi menyimpan screening tervalidasi di backend. WhatsApp membawa kode privat yang berlaku dua jam; pengunjung tetap harus menekan Kirim. Kode terikat pada pengirim/chat pertama, tanpa memberikan hak operator.
- **Pendalaman dan antrean:** hasil awal memakai skor server dan satu pertanyaan prioritas. Setelah enam jawaban, klien menyetujui ringkasan sebelum kasus masuk antrean dan ledger intake. Antrean tidak berarti tim sudah menerima atau menyetujui proyek. Jika model gagal, pertanyaan terstruktur tetap berjalan.
- **Perbaikan terakhir:** kode privat mendukung seluruh alfabet token; ringkasan tidak lagi memicu intake sebelum persetujuan; kasus lama yang digantikan tidak terbuka lagi setelah kasus baru dihapus. `/stop`, `/lanjut`, `/hasil`, `/hapus` tersedia; melanjutkan chat tidak menghapus batas risiko.
- **Akses dan privasi:** WA allow-all dimatikan, empat identitas tepercaya dipertahankan dan grup dibatasi ke allowlist yang sudah dikonfigurasi. Jalur konsultasi DM tidak memiliki tools terminal/file/akun. API menggunakan validasi field, CSRF dan batas permintaan; dokumen internal, log, database dan pembacaan kasus tidak tersedia melalui endpoint publik. Data gateway punya retensi dan pembersihan; salinan WA/ledger perlu penanganan terpisah.

**Verifikasi:** 81 uji unit/integrasi lulus: 11 assessment, 23 decision/workflow, 35 mission dan 12 gateway. Pemeriksaan kontrak 103 dan browser 42 lulus; 89 parity Python–JavaScript termasuk dalam kategori tersebut, bukan tambahan semuanya. Empat kasus browser-ke-API lulus. Smoke test HTTPS publik membuktikan satu POST setelah tindakan konsultasi dan draf WA siap, tanpa membuka/mengirim WA. Data sintetis itu telah dibersihkan. Layanan preview, tunnel dan gateway aktif; bridge WhatsApp connected. Integrasi Hermes diuji dengan ingress asli dan transport simulasi.

**Status setelah top-up:** panggilan model yang sebelumnya gagal terkait pembayaran/kredit sudah berhasil kembali menggunakan provider aktif. Hermes/Omni juga berhasil membaca dan mereview dua dokumen progres lewat sesi `[CODEX]` dengan `--oneshot`. Fallback terstruktur tetap tersedia. Saldo akun dan kredensial fallback belum diperiksa ulang.

**Sisa validasi:** percakapan masuk dari klien WA nyata dan deployment domain final belum diuji. Omni menyoroti bobot/prioritas yang masih heuristik; hasilnya perlu dikalibrasi dari engagement nyata dan tidak boleh diperlakukan sebagai jaminan manfaat bisnis. Persetujuan ringkasan saat model gagal sudah tercakup dalam uji integrasi.

**Temuan setelah model pulih:** metadata skor server sebelumnya ikut dilabeli sebagai bahan klien tidak tepercaya dan memicu penolakan yang keliru. Metadata kini diberikan terpisah, instruksi menegaskan bahwa bahan klien boleh dianalisis tanpa menjalankan instruksi tersisip, dan balasan yang membahas aturan internal atau menolak konsultasi diganti fallback terstruktur. Batas satu paragraf singkat dan maksimal tiga kalimat diterapkan sebelum pertanyaan aplikasi ditambahkan.

Preview: https://then-farming-finding-undo.trycloudflare.com/konsultasi-v3.html

Versi: paket pengembangan 3.3, gateway 1.0, bank/engine 3.1, workflow 3.2 dan kontrak agent 1.0. Paket sumber tidak menyertakan credential, database klien, backup konfigurasi atau log percakapan mentah.
