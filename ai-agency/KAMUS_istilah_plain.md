# Kamus Istilah: versi gampang vs versi teknis

Dibuat supaya tim (Andik, Vincent, Michael) tidak perlu nanya-nanya lagi.
Kalau di kalender/dokumen lama ketemu istilah kiri, artinya yang kanan.

## Di gambar kalender (tulisan kecil di dalam kotak)

| Tulisan di kalender | Istilah teknis lama | Artinya gampangnya |
|---|---|---|
| KONTEN 1 | KONTEN #1 | Hari posting konten pertama pekan ini (jam 19:00) |
| KONTEN 2 | KONTEN #2 | Hari posting konten kedua pekan ini (jam 19:00) |
| RAPAT ONLINE 1 · 20:00 | ONLINE-A 20:00 | Rapat lewat internet, 30 menit. Isinya bahas hambatan/blocker |
| RAPAT ONLINE 2 · 20:00 | ONLINE-B 20:00 | Rapat lewat internet, 45 menit. Isinya review hasil kerja + rencana konten |
| RAPAT DATANG · jam | OFFLINE | Rapat datang ke tempat, ketemu langsung |
| BATAS 12:00 | CUT-OFF 12:00 | Batas terakhir kode/pekerjaan boleh dikirim hari itu. Lewat jam ini, tunggu pekan depan |
| VERSI UJI | RILIS KANDIDAT | Hari kumpulan hasil kerja pekan ini dibungkus jadi 1 versi buat diuji. Belum resmi, masih calon |
| VERSI JADI | BUILD STABIL | Versi uji tadi sudah lolos pengujian, jadi versi resmi pekan ini |
| CEK AKHIR | GERBANG SIKLUS | Pemeriksaan terakhir di akhir siklus 1 (tanggal 18 Oktober) |

## Di dokumen rencana (kalender_perencanaan_siklus1.md)

| Istilah di dokumen | Artinya gampangnya |
|---|---|
| Gerbang | Syarat yang harus terpenuhi. Kalau tidak terpenuhi, jangan lanjut ke pekan berikutnya |
| Sprint | Rentang kerja 1 pekan |
| PR (Pull Request) | Permintaan gabung kode. Nathanael kirim kode, Vincent periksa, baru digabung |
| Merge | Menggabungkan kode ke versi utama |
| Uji terima | Pengujian terakhir sebelum versi dianggap resmi. Dilakukan Michael pakai daftar skenario uji |
| DoD (Definition of Done) | Daftar syarat sebuah pekerjaan dianggap benar-benar selesai |
| Blocker / hambatan | Sesuatu yang bikin kerjaan tidak bisa lanjut |
| Bug P0 | Kerusakan paling parah. Kalau ada ini, kerjaan lain ditaruh dulu |
| Bug board | Papan catatan daftar kerusakan yang ditemukan |
| Triage | Rapat singkat memilah mana yang penting dikerjakan dulu |
| CRM | Daftar calon klien (client_register.csv) |
| Self-report | Laporan progress yang ditulis orangnya sendiri, bukan dinilai orang lain |

## Catatan

- Tanggal di kalender PASTI benar karena digambar oleh program (kalender_omnisense.py),
  bukan oleh AI gambar. AI gambar sering salah menulis angka tanggal.
- Kalau mau ubah isi kalender: edit `kalender_data.json`, lalu jalankan
  `.venv/bin/python kalender_omnisense.py`
- File asli sebelum diterjemahkan ke bahasa gampang disimpan sebagai
  `kalender_data.json.bak` dan `kalender_omnisense.py.bak`.
