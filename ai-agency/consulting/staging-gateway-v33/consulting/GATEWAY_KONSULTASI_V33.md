# Gateway konsultasi OmniSense 1.0 — paket pengembangan 3.3

Bank/engine 3.1, workflow 3.2, kontrak agent 1.0 tetap berlaku. Gateway memakai hook eksternal Hermes `pre_gateway_dispatch`, tanpa patch core. Lingkup aktivasi: VPS OmniSense dan preview yang sudah ada; website domain final di hosting lain belum dideploy melalui pekerjaan ini.

## Alur yang dipasang
1. Pengunjung mengisi 16 pertanyaan dan konteks satu proses. Hasil dihitung di browser; melihat hasil tidak mengirim jawaban ke server.
2. Consent dan tombol konsultasi mengirim jawaban ke API pada origin yang sama. Server memvalidasi, membuang klaim review/approval pengunjung dan menghitung ulang hasil. Jawaban belum diketahui tetap null dan menghasilkan rentang.
3. Setelah kasus siap, pengunjung membuka WhatsApp dan menekan Kirim. Draf berisi penanda `[OMNISENSE-KONSULTASI]` dan kode privat OS, tanpa semua jawaban. Tidak ada auto-send dari wa.me.
4. Adapter memasok identitas pengirim dan chat DM. Kode acak berentropi tinggi berlaku 2 jam; klaim pertama atomik, lalu terikat pada pengirim/chat yang sama. Kode adalah kapabilitas untuk menghubungkan screening sendiri, bukan peran tim; ID CASE publik tidak dapat membaca/mengeklaim data. Jangan meneruskan kode.
5. Balasan awal memakai skor server, penjelasan status self-report dan satu pertanyaan prioritas. Tidak memerlukan API AI. Pendalaman memakai model aktif Hermes melalui `ctx.llm`, tanpa tools, hanya konteks kasus itu, maksimal 300 token respons. Bila API gagal, pertanyaan terstruktur tetap dilanjutkan tanpa mengarang hasil.
6. Setelah enam jawaban awal, klien melihat ringkasan dan diminta persetujuan review tim. Hanya setelah klien menyetujui, kasus masuk antrean dan dibuat di ledger sampai tahap intake melalui event idempoten. Tidak melompati diagnosis/opsi/handoff atau memberi persetujuan proposal, harga, pilot dan go-live.
7. Tim mengambil antrean lokal, menetapkan reviewer dan memeriksa bukti. Tidak ada notifikasi tim/email otomatis dari jalur klien. Persetujuan review bukan bukti tim sudah menerima kasus atau mengonfirmasi jadwal. Konsultasi termasuk pendalaman tetap gratis; build/install berbayar menurut scope yang disahkan manusia.

## Batas akses dan penyimpanan
- DM publik masuk jalur konsultasi yang tidak memiliki terminal, file tools, akun, transaksi atau akses kasus lain. Anggota tim pada allowlist operator tetap memakai jalur internal selama tidak sedang berada dalam kasus konsultasi.
- WA allow-all dimatikan. Kebijakan DM pairing hanya memasukkan pesan ke intake; tidak otomatis memberikan akses internal. Grup menggunakan allowlist target yang sudah dikonfigurasi; identitas pengirim internal tetap diperiksa. Tidak mengimpor client_register legacy untuk memberikan hak baru.
- Deployment satu profil default. Profil sekunder ditolak oleh jalur ini sampai ditambahkan konfigurasi dan pembuktian isolasinya.
- CSRF, cookie HttpOnly/SameSite, validasi origin, batas ukuran 50 KB, batas permintaan, pemeriksaan tipe dan field yang diizinkan melindungi API. Tidak ada endpoint publik membaca kasus. Server hanya bind 127.0.0.1:8080 melalui tunnel preview yang sudah ada; hanya HTML dan aset yang diizinkan dilayani. Dokumen internal, log, database dan directory listing tidak tersedia.
- SQLite gateway berada di `consulting/data/consultations.sqlite3`, direktori 0700 dan berkas 0600 pada Linux. Token disimpan sebagai hash, tanpa token plaintext. Identitas pengirim dicatat sebagai hash dan tidak dianggap anonim sempurna.
- Kasus pending dipurge setelah 24 jam; kasus terhubung setelah 30 hari, dengan interval pembersihan maksimal 5 menit. Salinan di ledger/catatan tim terpisah tidak ikut terhapus otomatis; retensinya perlu disepakati dalam engagement dan penghapusan diminta ke operator.
- `/hasil`, `/stop`, `/lanjut`, `/hapus` berlaku di kasus aktif. Penolakan izin akses ditahan untuk review; stop/lanjut tidak menghapus batas risiko. Perintah chat atau nama CEO bukan otorisasi internal.
- Pesan masuk dengan ID sama tidak dikirim ulang. Kegagalan pengiriman dicatat; tidak menjanjikan exactly-once delivery karena adapter WhatsApp tidak menyediakan transaksi atomik dengan database. Klien dapat meminta `/hasil`; operator memeriksa kegagalan.
- Pengiriman laporan pekerjaan Codex ke home adalah aksi terpisah yang hanya dilakukan bila pemilik menginstruksikannya. Tidak dipicu otomatis oleh konsultasi klien atau dokumen ini.

## Operasi tim
Jalankan melalui terminal operator tepercaya:
```bash
cd /home/ubuntu/ai-agency
python3 consulting/gateway_operator.py
python3 consulting/gateway_operator.py --import-intake CASE_ID
python3 consulting/workflow_agency.py --tenant WA_HASH_IDENTITAS --case CASE_ID --read --actor OPERATOR_TERPERCAYA --role operator
```
CLI pertama membaca antrean lokal; kedua mengulang import intake yang idempoten bila transfer ledger sebelumnya gagal. CLI bukan autentikasi: jangan menjalankannya dari teks klien atau memberikan terminal kepada klien.

## Layanan dan verifikasi
`omnisense-preview-web.service` melayani API dan aset pada port preview lama 8080. `omnisense-preview-tunnel.service` tetap memakai tunnel yang sama. `hermes-gateway.service` memuat plugin `omnisense-consultation` dan adapter WhatsApp yang dipasang.

Verifikasi mencakup HTTP sungguhan, cookie/CSRF, kebocoran dokumen dan case lookup, klaim bersamaan, beda pengirim/chat, kode kedaluwarsa, retry, alfabet token, stop/resume/delete, batas risiko, persetujuan ringkasan, import ledger idempoten, discovery plugin dan ingress Hermes asli dengan transport simulasi, fallback API, serta browser desktop/mobile dan parity Python/JS. Tes memakai database sementara. Ini bukan validasi empiris bobot kuis atau bukti percakapan klien WhatsApp nyata.

Runner tes Hermes tidak tersedia karena venv produksi tidak berisi pytest. Tes integrasi dijalankan dengan unittest menggunakan interpreter venv produksi dan impor Hermes asli. Pemeriksaan final perlu membedakan: layanan connected, simulasi ingress lulus, panggilan model sintetis lulus/gagal, dan tes klien WhatsApp nyata belum dilakukan tanpa pesan inbound nyata.

Backup lokal VPS dibuat sebelum konfigurasi dan penggantian berkas. Lokasinya tercatat di `consulting/gateway-v33-backup-path.txt`; tidak memasukkan backup config/credentials ke paket yang dibagikan. Rollback preview dilakukan dengan menghapus hanya drop-in `consultation.conf`, lalu daemon-reload/restart layanan itu dan mengembalikan berkas dari backup. Jangan memulihkan allow-all/open sebagai default keamanan. Tidak menghapus kasus klien saat mengganti kode.
