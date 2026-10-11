# SERAH TERIMA DEPLOY — Situs OmniSense

Disusun: 30 September 2026 · Untuk: Vincent (nginx VPS `168.231.118.144`)
Status: **berkas siap, belum diunggah.** Mesin agent tidak punya akses ke VPS.

---

## 1. Apa yang diunggah

Dari folder `/home/ubuntu/ai-agency/website/` — **hanya ini**:

```
index.html              134 KB  (satu berkas, CSS+JS inline)
privacy.html             11 KB  (Kebijakan Privasi, 2 bahasa)
404.html                  4 KB
robots.txt
sitemap.xml
site.webmanifest
assets/
  favicon.ico  favicon-16.png  favicon-32.png
  apple-touch-icon-180.png  apple-touch-icon-192.png
  logo-mark-white-64.png  logo-mark-white-128.png  logo-mark-white-256.png
  og-omnisense.png        (kartu pratinjau tautan 1200x630)
```

**Jangan diunggah** (folder kerja, bukan bagian situs):
`arsip/`, `pratinjau/`, `tab-penilaian/`, `scripts/`, `*.py`, `*.md`, `*.log`.

Tidak ada berkas eksternal lain yang diminta halaman. Font (Outfit, Inter) dari Google Fonts
lewat `<link>` di `<head>` — tidak ada `@import` di dalam `<style>`.

---

## 2. Unggah

Dari mesin ini (butuh kunci SSH Vincent):

```bash
cd /home/ubuntu/ai-agency/website
scp -r index.html privacy.html 404.html robots.txt sitemap.xml site.webmanifest assets \
    USER@168.231.118.144:/tmp/omnisense-situs/
```

Lalu di VPS:

```bash
sudo mkdir -p /var/www/omnisense.id
sudo rsync -a --delete /tmp/omnisense-situs/ /var/www/omnisense.id/
sudo chown -R www-data:www-data /var/www/omnisense.id
```

`--delete` aman di sini karena tujuan hanya berisi berkas situs. **Jangan** pakai `--delete`
kalau root nginx-nya dipakai bersama aplikasi lain — cek dulu `grep -r root /etc/nginx/sites-enabled/`.

---

## 3. Blok nginx

Cari blok `server_name omnisense.id` (kemungkinan masih memuat halaman NeoSense), lalu
samakan bagian berikut:

```nginx
server {
    listen 443 ssl http2;
    server_name omnisense.id www.omnisense.id;

    root /var/www/omnisense.id;
    index index.html;

    # halaman 404 sendiri (bukan halaman default nginx)
    error_page 404 /404.html;
    location = /404.html { internal; }

    # privasi & berkas statis
    location = /privacy.html { try_files $uri =404; }
    location = /privacy { return 301 /privacy.html; }

    location / {
        try_files $uri $uri/ $uri.html =404;
    }

    # aset & berkas teks: cache panjang, html: selalu segar
    location ~* \.(png|jpg|jpeg|webp|svg|ico|woff2?)$ {
        expires 30d;
        add_header Cache-Control "public, max-age=2592000, immutable";
        access_log off;
    }
    location ~* \.(css|js)$ {
        expires 7d;
        add_header Cache-Control "public, max-age=604800";
    }
    location = /sitemap.xml { add_header Cache-Control "public, max-age=3600"; }
    location = /robots.txt  { add_header Cache-Control "public, max-age=3600"; }

    gzip on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/javascript application/json
               application/xml image/svg+xml application/manifest+json;

    # header keamanan dasar (situs statis, tanpa backend)
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# http -> https, dan www -> tanpa www
server {
    listen 80;
    server_name omnisense.id www.omnisense.id;
    return 301 https://omnisense.id$request_uri;
}
server {
    listen 443 ssl http2;
    server_name www.omnisense.id;
    return 301 https://omnisense.id$request_uri;
}
```

Catatan:
- Halaman memuat font dari `fonts.googleapis.com` — kalau nanti mau CSP ketat, izinkan
  `style-src 'self' fonts.googleapis.com` dan `font-src fonts.gstatic.com`.
- Halaman penilaian **tidak mengirim apa pun ke server**. Tidak perlu aturan khusus,
  tidak ada endpoint, tidak ada database.
- Tautan WhatsApp mengarah ke `wa.me/6288809640700` — nomor sudah final di halaman.

---

## 4. Sesudah pasang — periksa ini

```bash
nginx -t && sudo systemctl reload nginx
```

- [ ] `https://omnisense.id/` memuat halaman OmniSense (bukan NeoSense lagi).
- [ ] `https://omnisense.id/privacy.html` terbuka; tautan "Kebijakan Privasi" di footer berfungsi.
- [ ] `https://omnisense.id/alamat-ngawur` menampilkan halaman 404 sendiri, bukan halaman nginx.
- [ ] `https://omnisense.id/robots.txt` dan `/sitemap.xml` terbaca.
- [ ] Tab penilaian: isi 8 jawaban → skor keluar di tempat → tombol WhatsApp membuka chat berisi skor.
- [ ] Uji pratinjau tautan: tempel `https://omnisense.id/` di WhatsApp/Telegram → muncul kartu
      navy-teal dengan judul "Seberapa siap bisnis Anda memakai AI?".
- [ ] `curl -I https://omnisense.id/` → ada `strict-transport-security`, `x-content-type-options`.

---

## 5. Yang belum ada di paket ini (bukan penghalang)

- **Testimoni** — menunggu klien pilot (Fase 9). Studi kasus di halaman masih proyek sendiri.
- **Halaman terpisah per layanan** (mis. `/penilaian-kesiapan`) — belum perlu selama masih satu halaman.
- **Google Search Console / Bing** — setelah situs hidup, daftarkan `sitemap.xml` supaya terindeks.
  Ini langkah tim, bukan berkas.
- **Analitik** — sengaja tidak ada; kebijakan privasi menyatakan tidak ada pelacak.

---

## 6. Arsip & berkas kerja (jangan ikut diunggah, tapi jangan dihapus)

- `arsip/index-sebelum-paket-deploy.html` — salinan `index.html` tepat sebelum paket ini dipasang.
- `arsip/index-tab-penilaian-v11.html` — versi saat tab penilaian selesai.
- `pratinjau/final-*.png` — 7 pratinjau resmi (hero, penilaian kosong, hasil skor, mobile hero,
  mobile penilaian, tanpa gerak, 404).
- `pratinjau/arsip-set-sebelum-deploy/` — set pratinjau lama (23 Sep).
- `tab-penilaian/` — sumber data + skrip uji tab penilaian (paritas, interaksi, rangkaian).
- `scripts/buat_og.py` — pembuat kartu pratinjau tautan.
- `scripts/shot_final.js` — pembuat pratinjau resmi.

## 10. Perbaikan bug setelah serah terima (30 Sep 2026)

`index.html` diubah lagi SETELAH paket ini disusun. Kalau Vincent sudah menyalin
berkas lebih awal, salin ulang `index.html` (dan `tab-penilaian/pertanyaan.json`).

Yang diperbaiki:
- **Skor tepat di ambang salah band.** Skor 60,0% tampil "Konvensional", seharusnya
  "Layak Lanjut" (sama untuk 80/40/20). Penyebab: galat floating point
  (`59.99999999999999 >= 60` = salah). Diperbaiki di `index.html`, `bangun_tab.py`,
  `kalkulator_kesiapan.py`, `uji_paritas.js` dengan pembulatan 1 desimal sebelum
  membandingkan.
- **Pesan peringatan tidak cocok dengan jawaban.** Aturan R1/R3/R4 memicu untuk nilai
  4 ATAU 5, tetapi teksnya hanya menggambarkan nilai 5. Ketiga pesan ditulis ulang agar
  akurat untuk seluruh rentang (disinkronkan di `index.html` + `pertanyaan.json`).
- **Kode aturan tampil ke pengunjung.** Kotak peringatan dulu menulis "D2, D3"; sekarang
  memakai nama dimensi.
- **Hitungan salah label.** "Ada 2 jawaban" -> "Ada 2 hal" (yang dihitung aturan, bukan
  jawaban); angka 1 ditulis "satu".

Verifikasi: 6/6 rangkaian uji browser lulus (`uji_paritas`, `uji_data`, `uji_tab`,
`uji_rangkaian`, `uji_tepi`, `uji_pesan_bentrok`), `verify_page.js` 0 error konsol &
tanpa overflow di desktop/mobile/reduced-motion, `baca_penilaian.py --uji` OK,
`jalur_penilaian.py --uji` OK.

Catatan: uji browser butuh `CHROME_PATH=~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`
dan `PW_CORE=/tmp/camofox/node_modules/playwright-core`.

---

## 11. Penyederhanaan tampilan — angka hiasan dibuang (30 Sep, lanjutan)

Permintaan pemilik: halaman terasa terlalu ramai karena elemen bernomor yang tidak menambah arti.
Total **25 penanda angka** dibuang, tanpa mengubah satu kata pun pada isi/teks:

| Bagian | Dibuang | Tetap |
|---|---|---|
| Rail peta bagian | 8 label kecil ("4 langkah", "5 rentang", "8 bobot", "1-2 menit", "6 keluaran", "6 istilah", "2 proyek", "1 nomor") | nomor 01-08 + nama bagian |
| Bagian "Cara kerja" | 4 angka raksasa di latar (duplikat tag "Langkah 01-04") | tag "Langkah 01-04" |
| Bagian "Yang Anda terima" | 6 nomor di kartu | judul + isi kartu |
| Footer | 7 nomor di daftar tautan (01-07) | label IG / PR |

Sengaja **tidak** diubah: nomor 01-08 pada daftar pertanyaan penilaian (menolong orientasi di form
panjang), nomor di kartu Dimensi, dan persen bobot (itu data, bukan hiasan).

CSS mati yang ikut dibersihkan: `.ix .c`, `.step .ghost`. Rule `.foot li span` **dipertahankan**
karena masih dipakai label "IG"/"PR" — jangan dihapus.

Bukti visual: `pratinjau/rapikan-angka-{rail,proses,output,footer}.png` (panel atas = sebelum,
bawah = sesudah). Cadangan versi lama: `arsip/index-sebelum-rapikan-angka.html`.

Uji setelah perubahan: 6 rangkaian browser hijau (paritas PASS, data 44/44, tab OK, rangkaian 8/8,
tepi 59/59, pesan-bentrok OK), `verify_page` 0 error console + tanpa overflow desktop/HP/tanpa-gerak.


---

## 12. Rapikan keramaian visual (1 Okt 2026)

Permintaan pemilik: halaman masih terasa ramai karena angka/label yang tumpang tindih arti.
Empat hal dirapikan, **tanpa mengubah satu kata pun pada isi/teks** (kecuali satu catatan ringkas):

| # | Bagian | Sebelum | Sesudah |
|---|---|---|---|
| A | Rail peta bagian (sticky) | nomor 01-08 di tiap tautan | titik kecil (6px) penanda posisi; aktif = teal |
| B | Label pil tiap bagian | 6 pil ("Proses", "Kategori", "Penilaian", "Yang Anda terima", "Kamus", "Studi kasus") | dihapus — duplikat nama bagian yang sudah ada di rail |
| C | Bagian "Cara kerja" | 4 pil "Keluaran: ..." berulang | satu catatan ringkas di kepala bagian |
| D | Rail kanan | angka persen tanpa keterangan ("013%") | label "POSISI" + persen 2 digit ("13%") |

Alasan: nomor 01-08 di rail bertabrakan makna dengan tag "LANGKAH 01-04" di isi (rail = daftar
bagian, bukan langkah), dan pil label mengulang apa yang sudah tertulis di rail tepat di atasnya.

Tetap dibiarkan (sengaja): nomor 01-08 pada daftar pertanyaan penilaian (menolong orientasi di
form panjang), nomor + persen bobot di kartu Dimensi (itu data), sumbu 0-100 di bagian Kategori
(pembanding visual tabel rentang), dan tag metrik LogiSense (12 armada, 395 pengiriman, dst.).

Bukti visual: `pratinjau/audit-ramai/` (sebelum, per bagian) vs `pratinjau/audit-ramai-sesudah/`
(sesudah, per bagian). Cadangan: `arsip/index-sebelum-rapikan-ramai.html`.

Uji setelah perubahan: 6 rangkaian browser hijau (paritas PASS, data 44/44, tab OK, rangkaian OK,
tepi 59/59, pesan-bentrok OK), `verify_page.js` 0 error konsol + tanpa overflow 1440/390/tanpa-gerak,
skor uji tetap 65/100 (Layak Lanjut) dan pesan WA tetap berpenanda `[PENILAIAN-SITUS v1]`.

Catatan cara ambil bukti per bagian: `node scripts/shot_seksi.js index.html <folder-keluar>`.

### 12b. Tindak lanjut (1 Okt 2026, lanjutan)

Dikerjakan setelah tabel 12:

- **Ekspor PDF dibereskan.** `@media print` dulu menyisakan nav, rail, footer, dan tautan
  antarmuka di dalam PDF. Sekarang yang tercetak hanya bagian hasil: kop OmniSense di atas
  (nama, "8 dimensi berbobot", omnisense.id, nomor WA), skor, kategori, 8 dimensi, celah, dan
  langkah berikutnya. Kartu yang berlatar gelap dipaksa putih saat cetak supaya hemat tinta dan
  kontras aman; kanvas cakram disembunyikan (angka skor tetap tercetak sebagai teks).
  Uji baru: `tab-penilaian/uji_cetak.js` (8 pemeriksaan, termasuk PDF nyata via `page.pdf`).
  Bukti: `pratinjau/hasil-03-hasil-cetak.pdf`, `pratinjau/hasil-04-tampilan-cetak.png`.
- **Versi 32 pertanyaan jadi tautan funnel, bukan form kedua.** Baris aksi hasil kini punya
  tautan "Minta versi lengkap (32 pertanyaan)" ke WhatsApp. Alasan: 32 pertanyaan di situs
  membuat orang keluar di tengah (lihat catatan K1 di INVENTARIS), sementara versi 32 sudah
  tersedia sebagai bank pertanyaan tim untuk sesi konsultasi. Jadi tawarkan, bukan paksa.
  Bukti tampilan: `pratinjau/hasil-05-aksi.png`.

**Masih terbuka (bukan pekerjaan berkas):** endpoint + notifikasi grup saat ada penilaian
masuk, dan testimoni klien (menunggu klien pilot). Keduanya butuh keputusan/backend, bukan
suntingan halaman.

### 12c. Catatan penting: tema & dua penulis (1 Okt 2026, 02:45)

- **Tema berkas kini basis gelap netral `#080808`** (dulu navy `#081726`). Perubahan ini
  datang dari sesi lain, bukan dari sesi ini; `404.html`, `privacy.html`, dan
  `theme-color` sudah ikut konsisten. Sebelum menyebar materi promosi, konfirmasi ke
  Michael warna mana yang final.
- **`index.html` pernah punya dua penulis sekaligus.** Pada 02:38–02:43 berkas ditulis
  ulang oleh sesi paralel, dan sempat muncul kerusakan CSS (37 deklarasi `rgba(...)`
  kehilangan `)`) yang membuat 420+ rule terbuang — halaman tampil tanpa layout.
  Sudah pulih (385 rule ter-parse, `(`/`)` seimbang, tanpa error JS). Penjaga cepat
  sebelum deploy:
  `python3 -c "s=open('index.html').read(); print(s.count('(')-s.count(')'))"` harus `0`.
- Sebelum menimpa `index.html`, pastikan tidak ada sesi lain yang sedang menulis
  (md5 stabil beberapa detik berturut-turut).

---

## 13. Ronde malam 1 Okt 2026 (02:20–03:00) — palet logo, font lokal, Kamus, FAQ

Semua dikerjakan mandiri atas izin Michael ("bebas eksplor, selesai jam 5").
Cadangan sebelum ronde ini: `arsip/index-sebelum-palet-logo.html` (kondisi bersih)
dan `arsip/index-palet-logo-BAGUS.html` (setelah palet benar).

### 13a. Palet dikunci ke warna logo OmniSense
Diambil dari berkas logo asli (`brand/logo-mark-teal-512.png`, `logo-mark-obsidian-512.png`),
bukan dikira-kira:

| Peran | Nilai final | Nilai lama di situs |
|---|---|---|
| Aksen teal | `#14B8A4` | `#14B8A6` |
| Latar obsidian | `#080808` | `#09090B`, dan sisa navy `#081726` |
| Teks putih | `#FAFAFA` | `#F4F4F5` |

Yang dibersihkan: 83 penggantian warna literal di `index.html` (termasuk sisa tema navy
`#081726`, `#0a1d30`, `#b6c7d8`, `#90a6bc`, `#c6d6e6`, `#04211e`), lalu `privacy.html`
dan `404.html` disamakan, dan `assets/og-omnisense.png` dibuat ulang dari latar `#080808`.

**Pelajaran (penting):** sapuan warna dulu dilakukan dengan regex
`rgba\(([^()]*?)(;)` yang bisa menyeberangi batas aturan CSS dan MENELAN kurung tutup —
37 deklarasi rusak, 420+ rule terbuang, halaman tampil tanpa layout. Sekarang
penggantian selalu **literal** (`str.replace`), bukan regex lintas-batas.
Penjaga wajib sebelum deploy:
`python3 -c "s=open('index.html').read(); print(s.count('(')-s.count(')'))"` → harus `0`,
dan jumlah rule ter-parse di browser harus **> 380** (kalau 18, CSS sedang rusak).

### 13b. Font di-host sendiri (tanpa Google Fonts)
`assets/fonts/inter-{400..900}.woff2` — Inter disubset ke latin, total **180 KB**
(dari 840 KB sebelum subset). Tiga baris `<link>` ke `fonts.googleapis.com` /
`fonts.gstatic.com` dihapus. `--font-mono` dan `--font-display` kini juga Inter
(sebelumnya menunjuk JetBrains Mono / Outfit yang tidak pernah di-host — jadi font
itu memang tidak pernah termuat; sekarang konsisten).
Diperiksa: 0 permintaan keluar ke Google, 6 bobot `loaded`, tanpa error.

### 13c. Bagian yang tipis diisi
- **Kamus: 6 → 12 istilah.** Tambahan: Migrasi data, Dashboard, Integrasi, Cloud,
  Hak akses, Proyek percontohan. Tiap entri punya "Contoh"/"Batasnya"/"Alasan" agar
  tidak terasa seperti kamus teknis kosong.
- **Bagian FAQ baru (`id="faq"`)**: 8 pertanyaan yang paling sering ditanya pemilik
  usaha (gratis?, berapa lama?, data aman?, skor rendah?, siapkan bahan?, sudah pakai
  kasir lain?, harus paket besar?, ada jaminan?). Jawabannya jujur — termasuk yang
  menolak klaim berlebihan ("tidak ada jaminan proyek berhasil").
  Memakai `<details>` asli, jadi **tanpa JavaScript** dan tetap jalan kalau JS mati.
- FAQ juga ditambahkan ke menu atas dan peta bagian.
- **JSON-LD `FAQPage`** ditambahkan di `<head>` (8 pertanyaan, rata-rata 250 karakter)
  supaya berpeluang muncul di hasil pencarian Google. Blok `ProfessionalService` lama
  tetap utuh.

### 13d. Temuan yang perlu diketahui Michael (jujur, belum diperbaiki)
1. **Angka rail 01–08 hilang.** Dulu rail berisi `<span class="n">01</span>Cara kerja`,
   ikut terhapus pada ronde "rapikan angka" (laporan waktu itu menyebut "rail 01–08
   dipertahankan" — itu keliru). Kini rail hanya menampilkan titik teal penanda posisi.
   Secara tampilan lebih bersih dan sesuai keluhan "terlalu ramai", jadi **dibiarkan**
   sampai Michael memutuskan. Kalau ingin dikembalikan: ambil markup dari
   `arsip/index-sebelum-rapikan-angka.html`.
2. **Bagian "Studi kasus" masih menyebut "Proyek klien · Logistik"** — sudah dikonfirmasi
   aman (tanpa nama klien, angka tak bisa dilacak), dan Michael memilih membiarkannya.
   Perlu diingat: dealing proyek itu tidak jadi, jadi framing "proyek klien" adalah klaim
   yang tidak bisa dibuktikan kalau ada yang menanyakan detailnya.

### 13e. Status verifikasi ronde ini
- `uji_paritas` cocok · `uji_data` 44/44 · `uji_tab` skor 65.0 Layak Lanjut ·
  `uji_rangkaian` 8/8 · `uji_tepi` 59/59 · `verify_page` 0 error, tanpa luapan
  di desktop/HP/`prefers-reduced-motion`.
- CSS 398 rule ter-parse, kurung seimbang, 0 error konsol.
- Tunnel: `/`, `index.html`, `privacy.html`, `robots.txt`, `sitemap.xml`,
  `assets/fonts/inter-400.woff2`, `assets/og-omnisense.png` → semua HTTP 200.


## 14. Konsultasi v3 (4 Oktober 2026)
Bagian awal dokumen adalah riwayat paket legacy. Build konsultasi baru harus membaca `SERAH_TERIMA_KONSULTASI_V3.md`. V3 masih pratinjau internal, belum masuk homepage/publik. Aset/font lokal dan perilaku privasi v3 dirinci di dokumen tersebut; jangan memakai daftar berkas/font lama sebagai daftar final v3.
