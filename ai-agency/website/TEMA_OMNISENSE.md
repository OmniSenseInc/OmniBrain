# Tema Website OmniSense — Keputusan & Alasan

Disusun dari data yang sudah ada di repo ini: `templates/OMNISENSE_BRAND_BRIEF.md`,
`analisis_landscape_ai_agency.md`, riset katalog motionsites.ai (`MOTION_REFERENSI.md`),
plus pengecekan langsung domain `omnisense.id`.

---

## 0. KEPUTUSAN — TERKUNCI

> **REVISI 2026-09-23 — sumbu *tone* dibuka kembali atas permintaan pemilik.** Tone B
> "Navy Lembut" dipakai (§6, §7). Isi di bawah ini berlaku untuk keputusan *struktur/tema demo
> A/B/C* yang lama dan tetap disimpan sebagai jejak; yang tidak lagi berlaku hanya kalimat
> "Tema A terkunci sebagai satu-satunya tema" — permukaan, huruf, dan sudut halaman sekarang
> navy (§7). Yang masih berlaku dari §0: teal sebagai sinyal data (bukan hiasan), aturan
> kontras teks, angka/nama kategori yang sama dengan SOP, dan logo resmi dipakai apa adanya.

**Tema A "Obsidian Instrument" dipilih dan dikunci sebagai satu-satunya tema di
`website/index.html`.** Saklar tema A/B/C sudah dihapus dari file; B dan C tinggal sebagai token
di §3 (arsip keputusan), bukan lagi kode yang hidup. Pilihan disimpan tanpa perlu reload tidak
lagi relevan — halaman hanya punya satu wajah.

Dasar pemilihan (penilaian visual ketiga demo yang sudah dirender, bukan dari deskripsi):

- **A menang karena aksen teal terbaca sebagai warna data.** Teal hanya muncul di busur skor,
  bar dimensi, rail progres 4 langkah, angka persen gulir, dan garis bawah tautan aktif. Tidak
  ada teal dekoratif, jadi mata langsung tahu mana yang angka dan mana yang hiasan.
- **B (navy) kalah karena jatuh ke pola "navy gelap + teal + grid"** — kombinasi yang paling
  umum di SaaS Indonesia; terasa premium tapi mudah tertukar dengan brand lain, dan terasa lebih
  korporat daripada target pemilik UMKM.
- **C (monokrom) kalah karena kehilangan penanda status.** Tanpa warna, skor 48 dan 82 tampak
  setara; pengguna harus membaca angka untuk tahu mana yang menghambat. Estetis, tapi menambah
  kerja kognitif pada produk yang justru menjual pembacaan cepat.

Perbaikan yang ikut masuk saat penguncian:

- Teks kecil tidak lagi memakai `--slate-dim #64748B` (kontras 4,2:1 — gagal AA untuk teks
  kecil) melainkan `--slate #94A3B8` (7,76:1) pada marquee, nomor langkah, label panel.
  `--slate-dim` tetap ada untuk elemen non-teks/dekoratif.
- Label produk ditulis "FNBSense", bukan "FNB SENSE" — tetap sebagai catatan kaki, tidak
  disejajarkan dengan OmniSense.
- **Angka dan nama di halaman harus sama dengan SOP.** 8 dimensi + bobot mengikuti
  `kalkulator_kesiapan.py` (Kesiapan data 20%, Infrastruktur 15%, Digitalisasi proses 15%, SDM 15%,
  Strategi 10%, Organisasi 10%, Tata kelola 10%, Anggaran 5%), dan nama kategori mengikuti `BANDS`
  (Siap Penuh / Layak Lanjut / Konvensional / Awal / Sangat Awal). Panel contoh: 68% = Layak Lanjut.
- **Logo resmi dipakai apa adanya** (mark spiral putih + wordmark kecil `omnisense`) dari
  `website/assets/logo-mark-white-256.png`, plus set favicon di folder yang sama. Mark tidak lagi
  digambar manual sebagai SVG di dalam halaman. Aturan lengkap: `brand/BRAND_LOGO_OMNISENSE.md`.

---

## 1. Temuan yang menentukan arah

**a. Identitas visual OmniSense saat ini terbelah dua.**

| Konteks | Palet yang dipakai sekarang |
|---|---|
| Poster IG / konten (visual system terkunci) | Obsidian monokrom — hitam pekat, putih, abu, headline ALL-CAPS, Inter |
| Desain Canva untuk klien | Navy `#0B1F3A` + teal `#14B8A6` + putih |

Dua palet ini bukan masalah selama dipisah rapi (konten vs materi klien). Masalahnya muncul
kalau website memakai palet ketiga — itu yang membuat brand terasa tidak dikelola. Maka
**website harus memilih salah satu sebagai induk**, bukan mencampur keduanya.

**b. `omnisense.id` sekarang tidak mewakili OmniSense sama sekali.**

Halaman yang dilayani domain itu berjudul **"NeoSense Social Media Intelligence"**
(deskripsi: *monitoring narratives, actors, and risk across online platforms*) — SPA Vite,
`<title>` NeoSense. Jadi ini bukan soal "ganti tema website lama", tapi **mengganti halaman
produk lain dengan wajah OmniSense yang benar**. Tidak ada warisan desain yang perlu dihormati.

**c. Kategori OmniSense bukan SaaS, tapi konsultan yang menjual pengukuran.**

Produk masuknya adalah *assessment*: 8 dimensi berbobot → satu angka 0–100 → band → roadmap.
Artinya bahasa visual yang jujur untuk OmniSense adalah **bahasa alat ukur**: skor, bar,
garis progres, angka. Bukan bahasa "dashboard SaaS".

**d. Pasar motion-nya jenuh pada satu gaya.**

Dari 526 prompt katalog motionsites.ai, 264 menyebut agensi/AI/konsultan/studio/gelap.
Resep yang paling sering muncul: latar gelap + glassmorphism + glow/gradient + video background
(lihat `MOTION_REFERENSI.md`). Mengikuti resep itu berarti **terlihat sama dengan ratusan situs
agensi AI lain** — persis risiko yang sudah dicatat di `analisis_landscape_ai_agency.md`.

---

## 2. Rekomendasi utama: "Obsidian Instrument"

Obsidian monokrom + satu aksen teal, susunan editorial, motif alat ukur.

**Kenapa ini yang saya rekomendasikan:**

1. **Menyatukan, bukan menambah.** Basis obsidian sudah jadi identitas konten yang terkunci;
   teal `#14B8A6` sudah dipakai di materi klien. Website = obsidian (induk) + teal (aksen).
   Tidak ada warna baru yang perlu dipertanggungjawabkan.
2. **Teal dipakai sebagai warna data, bukan dekorasi.** Skor, bar dimensi, garis progres, dan
   tautan. Sisanya monokrom. Ini yang membedakan dari "template gelap + glow" — aksen dibatasi
   ±5% luas halaman, jadi mata langsung tahu apa yang penting.
3. **Cocok dengan penawaran gratis-dulu.** Halaman terasa seperti instrumen yang bisa dibaca,
   bukan iklan. Itu menurunkan kecurigaan pemilik UMKM yang belum pernah beli jasa AI.
4. **Tahan lama.** Monokrom editorial tidak ikut mati saat tren "glass + gradient ungu" lewat.
5. **Murah di server & cepat di HP.** Tanpa video background, tanpa WebGL berat — penting untuk
   target UMKM Indonesia yang banyak buka dari HP di jaringan seluler.

### Token

```
Warna
  --obsidian   #09090B   latar utama
  --obsidian-2 #0C0C0E   latar section bergantian / marquee
  --panel      #121215   permukaan kartu (--glass di kode)
  --line       #27272A   garis pemisah halus
  --line-2     #3F3F46   garis tombol (lebih terlihat)
  --track      #34343C   track bar / rail
  --white      #FFFFFF   teks utama & headline
  --slate      #94A3B8   teks sekunder (kontras ±7,76:1 di atas obsidian)
  --slate-dim  #64748B   HANYA untuk elemen non-teks / dekoratif (4,2:1 — gagal AA utk teks kecil)
  --signal     #14B8A6   AKSEN TUNGGAL: skor, bar, rail, rel tick, tautan aktif

Tipografi
  Headline : Inter 900, ALL-CAPS, letter-spacing -0.02em, line-height 1.06
  Body     : Inter 400/500, 16px, line-height 1.55
  Label    : JetBrains Mono 500, 11–12.5px, uppercase, letter-spacing 0.14em
  Skala H1 : clamp(38px, 6.4vw, 74px)   H2: clamp(28px, 4.2vw, 50px)   H3: 17px

Bentuk
  Radius   : 10px (kecil) / 14px (kartu kecil) / 20px (panel, cta) / 999px (pil, tombol)
  Garis    : 1px, selalu #27272A — tidak pakai drop shadow sebagai pemisah
  Spacing  : kelipatan 8; jarak antar-section clamp(72px, 10vw, 140px) desktop, 72px mobile
```

### Aturan pakai

**Lakukan**
- Headline pendek, huruf besar, bahasa sehari-hari (target pemilik usaha, bukan CTO).
- Tunjukkan angka lebih dulu, jelaskan setelahnya (skor → celah → langkah).
- Satu aksen saja. Kalau butuh warna kedua untuk grafik, pakai putih + opasitas teal, bukan hue baru.
- Foto/visual nyata (potret pemilik usaha, layar kasir, buku catatan) lebih dipercaya daripada ilustrasi 3D abstrak.

**Jangan**
- Gradient ungu–biru, aurora blob, atau glow berlebih — itu penanda "situs AI generik".
- Tiga kartu fitur sejajar dengan ikon outline. Kalau ada 3 hal, tulis sebagai daftar bernomor.
- Jargon: "digitalisasi", "transformasi", "solusi end-to-end", "leverage AI".
- Menonjolkan FNBSense sejajar dengan OmniSense — FNBSense tetap produk, bukan wajah perusahaan.

---

## 3. Alternatif (kalau ingin arah lain)

**B — "Navy Blueprint":** navy `#0B1F3A` jadi latar, teal aksen, garis-garis seperti cetak biru.
*Untuk:* kalau pasar digeser ke korporat/BUMN yang menganggap hitam "kurang resmi".
*Risiko:* biru gelap + teal adalah kombinasi paling umum di SaaS Indonesia; mudah terlihat seperti template.

**C — "Monokrom Murni":** tanpa aksen warna sama sekali; angka & bar hanya putih/abu.
*Untuk:* kesan paling mahal dan paling editorial, sangat konsisten dengan poster IG.
*Risiko:* grafik skor kehilangan penanda warna; pengguna sulit membedakan "data" dari "dekorasi".

### Token tema B & C (yang benar-benar dipakai di demo)

```
B — Navy Blueprint          C — Monokrom Murni
  --obsidian  #0B1F3A         --obsidian  #09090B   (sama seperti A)
  --obsidian-2 #08182E        --signal    #FFFFFF   (aksen = putih)
  --glass     #0F2A4C         --signal-soft rgba(255,255,255,.10)
  --slate     #A9BDD6         sisanya identik dengan A
  --slate-dim #93AAC7
  --line      #1C3D63
  --line-2    #2C5585
  --track     #3F72A8
  --bg-rgb    11,31,58
  --panel-rgb 15,42,76
  + motif grid cetak biru: garis teal rgba(20,184,166,.10) tiap 44px
```

Rasio kontras yang sudah dihitung (bukan perkiraan):

| Tema | teks sekunder / latar | aksen / latar | aksen / panel |
|---|---|---|---|
| A | 7,76:1 | 7,99:1 | — |
| B | 8,60:1 | 6,64:1 | 5,79:1 |
| C | 7,76:1 | 19,9:1 (putih) | — |

Teks kecil tema B memakai `--slate-dim #93AAC7` (6,93:1 di atas navy), bukan `#7C93B0`
(5,24:1) yang semula dipakai — nilai pertama sudah diganti setelah uji visual.

**Status token B & C: arsip.** Keduanya sudah tidak dipakai di `index.html` (lihat §0). Token di
atas disimpan hanya supaya keputusan bisa ditelusuri dan supaya B/C bisa dihidupkan lagi tanpa
riset ulang kalau positioning bergeser (misalnya menyasar korporat/BUMN).

---

## 4. Yang perlu dikerjakan berikutnya

1. ~~Putuskan A / B / C~~ **SELESAI** — A dikunci (§0). Demo tiga tema diarsipkan di
   `pratinjau/arsip-tema/`; token B & C ada di §3 dokumen ini bila suatu saat perlu dihidupkan lagi.
2. Ganti isi `omnisense.id` — saat ini masih halaman "NeoSense". Perlu keputusan: NeoSense
   dipindah ke subdomain (mis. `neosense.omnisense.id`) atau dihapus dari domain utama.
3. Isi yang masih kosong dan harus disiapkan: nomor WhatsApp tujuan CTA, satu studi kasus nyata
   (walau kecil), dan 3–5 logo/klien bila ada.
4. Produksi: demo ini HTML satu file tanpa dependensi; untuk produksi bisa dipindah ke
   Next.js/Astro dengan struktur section yang sama.

---

## 5. Struktur halaman v3 (2026-09-22)

Token dan tema tidak berubah (A "Obsidian Instrument" tetap terkunci). Yang berubah hanya
susunan section, supaya halaman tidak lagi monoton — semua section v2 berbentuk sama.

Urutan section: nav → hero (watermark raksasa + panel skor) → marquee → **strip indeks bagian**
→ cara kerja (4 langkah, angka raksasa di belakang) → **tangga kategori skor** → dimensi
(8 kartu bernomor + bar bobot) → **keluaran penilaian** (6 kartu bernomor) → **kamus istilah**
(6 chip + panel) → hasil (2 kasus, 001/002 + chip spesifikasi) → kontak (CTA full-bleed +
nomor telepon bergaris) → footer 3 kolom + wordmark raksasa.

Modul baru yang perlu diketahui kalau halaman diedit lagi:

- `.ixbar` — strip indeks, `position:sticky; top:var(--navh)`, ikut scrollspy.
- `.ladder` — tangga kategori; penanda `.lmark` bergerak ke `left:68%` saat masuk viewport.
- `.dcard` — kartu dimensi; bar `.wbar i` lebarnya dari `data-w`, diskalakan terhadap bobot
  terbesar (20% = 100% track).
- `#tabs` — tab kamus, `role="tablist"` + panah kiri/kanan.
- `.foot-wm` — wordmark footer; jangan pernah dikasih selector `.foot p`, pernah menimpanya.

Detail lengkap + asal tiap pola ada di `MOTION_REFERENSI.md` §7. Pratinjau: `pratinjau/v3-*.png`.

---

## 6. Kandidat tone v4 — "kurangi rasa AI & kaku" (2026-09-22)

Keluhan pemilik: versi v3 "terlalu AI banget dan kaku". Diagnosa dari halaman sendiri
(terukur, bukan kesan): 11 label huruf besar berspasi lebar, pendar teal di 5 tempat,
medan titik canvas, watermark 300px, penggaris tick, pita berjalan, kartu 1px seragam,
huruf bobot 800. Semua itu penanda gaya "template AI", bukan identitas OmniSense.

Dasar pemilihan tone = bentuk logo, bukan selera: logo = busur monoline konsentris
dengan celah + titik tengah, stroke rata, ujung membulat, ruang negatif besar, hanya ada
versi putih. Karena itu tema terang ditolak (logo hilang) dan arahnya: gelap, tenang,
monoline, busur sebagai motif, teal sebagai sinyal — bukan pendar.

Tiga kandidat, semuanya memakai halaman yang sama (isi/JS tidak diubah):

| kode | nama | permukaan | huruf | sudut | catatan |
|---|---|---|---|---|---|
| A | Editorial Tenang | near-hitam hangat #100F0D | Instrument Serif + Inter | 4/8/12px | rasa konsultan yang menulis; paling tidak "mesin" |
| B | Navy Lembut | navy #0B1F3A | Outfit + Inter | 18px | busur konsentris dari bentuk logo; paling nyambung ke marka |
| C | Studio Presisi | #0A0A0B | Inter tegas + mono | 3px | buku kerja studio; paling tenang, paling dekat ke v3 |

Lapisan bersama `tone/00-nyaman.css` yang membuang penanda AI (label huruf besar, pendar,
medan titik, watermark, tick, pita) — dipakai ketiganya. Berkas: `tone/00-nyaman.css`,
`tone/a-editorial.css`, `tone/b-navy.css`, `tone/c-studio.css`; pratinjau `index-tone-*.html`
(dibuat oleh `tone/buat-pratinjau-tone.py`); banding: `pratinjau/tone-banding.html`.

Perbaikan isi yang berlaku di semua tone (sudah masuk `index.html`): garis bobot punya
skala 10% yang kelihatan (satu garis penuh = 100%), gutter grid dimensi dilebarkan,
angka bobot ditebalkan, kontrol gerak pindah ke baris footer, nav "Output/Hasil" →
"Yang Anda terima/Studi kasus", judul hero "mengerjakan AI" → "memakai AI".

**DIPUTUSKAN 2026-09-23: tone B "Navy Lembut" dipakai.** Lapisan `tone/00-nyaman.css` +
`tone/b-navy.css` sudah dipindah ke dalam `index.html` (satu file, tanpa permintaan berkas
eksternal lagi), dan semua berkas kandidat dipindah ke
`pratinjau/arsip-tema/kandidat-tone-20260923/` (`index-tone-a/b/c.html`, `tone/`, `tone-*.png`,
`tone-banding.html`). Rincian apa yang ikut berubah saat pemasangan: §7.

Alasan yang menang bukan "navy lebih bagus", tapi **kesamaan palet**: materi klien OmniSense
(desain Canva) sudah memakai navy + teal + putih, sedangkan website saat itu memakai palet
ketiga (obsidian monokrom). Dengan B, website dan materi klien memakai satu induk palet yang
sama — navy `#0B1F3A` untuk permukaan, teal `#14B8A6` untuk sinyal.

---

## 7. Tone B terpasang di `index.html` (2026-09-23)

Isi dan JS tidak diubah; yang berubah hanya lapisan tampilan. Lapisan `00-nyaman.css` +
`b-navy.css` kini berada di **akhir blok `<style>`** di dalam `index.html` (urutan cascade
sama seperti saat jadi kandidat: paling akhir = paling menang). `@import` font Outfit diubah
jadi `<link>` di `<head>` — `@import` di dalam `<style>` yang tidak berada di baris pertama
diabaikan browser, jadi ikon hurufnya tidak akan pernah termuat kalau dibiarkan.

Token yang berlaku sekarang: permukaan `--obsidian:#081726` (biru malam), `--obsidian-2:#0A1D30`,
`--panel:rgba(255,255,255,.035)`, garis `rgba(255,255,255,.10)`, `--track:rgba(255,255,255,.10)`;
huruf judul `Outfit`, badan `Inter`, dan `--font-mono` juga `Inter` (angka disejajarkan dengan
`tabular-nums`, bukan huruf mono lagi); sudut `--r-s:8px` / `--r-m:14px` / `--r-l:18px`.

### Yang ikut dibetulkan saat pemasangan (temuan QA, bukan bagian dari kandidat)

Kandidat B mewarisi warna **literal** tema lama yang tidak lewat token, sehingga di atas navy
terbaca sebagai tambalan hitam. Terukur lewat pemindaian `getComputedStyle` seluruh elemen
(bukan dikira-kira): `header.nav` + `.nav.is-stuck` `rgba(9,9,11,…)`, `.eyebrow`
`rgba(18,18,21,.6)` (8 buah), `.step .out`, `.case .spec span`, `.vignette`, dan `--obsidian-2`
yang dipakai `.cta`, `.scale .seg`, `.marquee`. Semua disamakan ke keluarga navy di blok
`PENYELESAIAN PERMUKAAN` di akhir `<style>`; `.marquee` dimatikan (sisa pita setinggi 2px).
Setelah perbaikan: 0 permukaan near-black pada 1440px dan 390px, di 4 posisi scroll.

Dua hal lagi yang ketahuan dari QA dan langsung dibetulkan:

- **Nomor telepon besar di CTA** tadinya murni hiasan (garis teal 42% → kontras 2,30:1, di bawah
  ambang 3:1 untuk teks besar) dan tidak bisa diketuk. Sekarang jadi `<a href="tel:…">`
  (tampilan sama), garis dinaikkan ke 60% → 3,41:1, plus keadaan hover/focus.
- **Ikon tombol WhatsApp** masih gelembung obrolan generik. Diganti mark WhatsApp yang benar
  (gelembung padat + gagang telepon sebagai ruang negatif) dari `tabler-icons` (MIT), dipakai di
  dua tombol. Diukur dari piksel: cakupan gelap 50,6% dan piksel tengah gelap — artinya benar
  terisi, bukan versi garis.

### Verifikasi

`verify_page.js` (desktop 1440, mobile 390, reduced-motion, scroll-to, after-click):
`ok:true`, 0 error konsol, 0 overflow horizontal. Perbandingan computed style 37 selektor ×
12 properti × 2 viewport antara `index.html` hasil pemasangan dan kandidat `index-tone-b.html`
**identik** (0 selisih) sebelum perbaikan permukaan — jadi yang dipasang memang B, bukan
tafsiran ulang.

### Berkas

- Pratinjau resmi halaman terpasang: `pratinjau/final-01-hero.png` … `final-07-tanpa-gerak.png`
  (set lama dipindah ke `pratinjau/arsip-tema/tema-sebelum-navy/`).
- Arsip kandidat + generator + halaman banding: `pratinjau/arsip-tema/kandidat-tone-20260923/`.
- Tidak ada lagi berkas `index-tone-*.html`, folder `tone/`, atau saklar tema di root `website/`.
  Halaman tetap satu file: `index.html` (78 KB) + `assets/`.

---

## 8. Paket deploy & penyelesaian halaman (2026-09-30)

Setelah tab penilaian hidup, halaman dilengkapi supaya layak naik ke `omnisense.id`.
Yang berubah (isi & nada halaman **tidak** diubah):

- **Bug lama ditemukan:** `</head>` hilang — `<style>` langsung diikuti `<body>`. Browser
  memaafkan, validator tidak. Sudah ditutup.
- **Meta berbagi:** `og:url`, `og:site_name`, `og:locale`, `og:image` (+ ukuran & alt),
  `twitter:card`, `canonical`. Kartu pratinjau tautan dibuat oleh `scripts/buat_og.py`
  (busur konsentris + titik teal di atas navy, 1200x630 → `assets/og-omnisense.png`).
- **JSON-LD** `ProfessionalService` (nama, url, area, telepon, IG, `makesOffer` penilaian gratis).
- **Ikon & manifest:** ikon 192px, `site.webmanifest` (nama, warna tema `#081726`).
- **CTA hero** sudah mengarah ke `#penilaian` dengan ikon clipboard-centang (bukan ikon
  WhatsApp lagi) — tombol WhatsApp tetap ada di nav, bagian penilaian, dan CTA penutup.
- **`privacy.html`** di dalam `website/` — diselaraskan ke tema A (navy-teal, Outfit/Inter)
  dan ditambah bagian **"Penilaian kesiapan di situs"**: jawaban hanya di `localStorage`,
  tidak dikirim ke server, tidak ada pelacak. Versi Inggris ikut diperbarui. Tautan
  "Kebijakan Privasi" ditambahkan di kolom footer.
- **Berkas situs baru:** `robots.txt`, `sitemap.xml`, `404.html` (halaman 404 sendiri dengan
  tautan ke bagian utama), `SERAH_TERIMA_DEPLOY.md` (instruksi unggah + blok nginx + daftar periksa).
- **Pratinjau resmi diperbarui:** `pratinjau/final-01..10*.png` (hero, penilaian kosong, hasil
  skor, mobile hero, mobile penilaian, tanpa gerak, 404, privasi atas/penuh/mobile).
  Set lama dipindah ke `pratinjau/arsip-set-sebelum-deploy/`. Pembuat: `scripts/shot_final.js`
  dan `scripts/shot_legal.js`.

Verifikasi setelah perubahan: `verify_page.js` `ok:true` 0 error & tanpa overflow 1440/390;
`uji_tab.js` 35/35; `uji_rangkaian.js` 8/8 (skor situs = hitung ulang bot, selisih 0);
`privacy.html` 0 error, tanpa overflow. Cadangan sebelum paket ini:
`arsip/index-sebelum-paket-deploy.html`.

**Belum:** unggah ke VPS (mesin agent tak punya akses) — instruksinya sudah siap di
`SERAH_TERIMA_DEPLOY.md`.
