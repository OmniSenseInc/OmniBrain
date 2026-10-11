# Referensi Motion dari motionsites.ai — Apa yang Layak Dibawa ke OmniSense

Riset dilakukan dengan membaca **katalog publik** motionsites.ai (tabel `prompts_public`) —
metadata saja: judul, kategori, tipe, kata kunci, status gratis/berbayar. Tidak ada isi prompt
berbayar yang diambil. Preview animasi yang diunduh adalah preview publik yang memang ditampilkan
di halaman katalog.

---

## 1. Isi katalog (angka hasil hitung, bukan perkiraan)

- **526 item** di katalog; **179 gratis**, **347 berbayar**.
- Kategori terbanyak: `Landing Page` 60 · `Hero` 57 · `SaaS` 47 · `Hero Section` 33 · `Agency` 16 ·
  `Portfolio` 13 · `Creative` 13 · `AI` 12 · `Features` 10 · `Technology` 10 · `Fintech` 9.
- Tipe: `hero` 388 · `mobile` 40 · `features` 38 · `cta` 9 · `footer` 7 · `about` 7.
- Artinya: katalog ini **didominasi hero section**. Untuk OmniSense, nilai terbesarnya ada di
  hero + cara kerja, bukan di halaman kompleks.

### Frekuensi teknik (jumlah kemunculan kata kunci)

| Teknik | Frek. | Catatan |
|---|---|---|
| Framer Motion / `motion/react` | 103 | Standar industri React |
| Video background | 92 | Populer, tapi paling berat |
| Scroll-driven / sticky / parallax | 78 | Inti pengalaman modern |
| WebGL / Three.js / canvas / shader | 78 | Paling mahal secara performa |
| Gradient / glow / aurora / mesh | 48 | Penanda gaya "AI generik" |
| Glassmorphism / backdrop-blur | 38 | Aman dipakai tipis-tipis |
| GSAP / Lenis / smooth scroll | 22 | Overkill untuk 1 halaman |
| Grid pattern / noise / grain | 18 | Murah, menaikkan kelas tampilan |
| Marquee / ticker | 9 | Cocok untuk strip kapabilitas |
| 3D tilt card | 7 | Gimmick |
| Custom cursor | 6 | Desktop saja |
| Kinetic typography | 4 | Jarang dipakai — jadi pembeda |

**264 item** menyebut agensi/AI/konsultan/studio/gelap. Jadi resep "gelap + glass + glow + video"
sudah dipakai ratusan kali. Menirunya = tenggelam.

---

## 2. Template yang saya periksa visual (preview publik, 4 frame per template)

Tersimpan di `/tmp/ms_prev/` (`sheet_<nama>.png` untuk tiap template, `GRID.png` contact sheet):
`obsidian-hero`, `neon-logic`, `layered-depth`, `scroll-marquee`, `glitch-pulse`, `orbis-cta`,
`velorix-iic`, `mythic-naturecore`.

Dua yang paling relevan dibaca ulang secara detail:

**Obsidian Hero** (kategori Hero, berbayar) — monokrom nyaris tanpa warna: latar ±`#0A0B0D`, teks
putih tulang, satu objek gelap besar yang berubah bentuk dari frame ke frame. Layout asimetris:
teks 35–40% di kiri, objek visual besar di kanan-bawah, dua kartu melayang di depan sebagai
lapisan teratas. Ada **deretan tick mark di tepi bawah** sebagai penanda progres scroll, plus
tekstur **grain halus**. Kesimpulan: hero di-*pin* dan divisualkan ulang sepanjang scroll,
kombinasi reveal + parallax antar-lapisan (digerakkan video atau render 3D).

→ **Yang layak diambil:** (a) layout asimetris teks-kiri / visual-kanan, (b) grain halus,
(c) tick mark progres scroll, (d) kartu melayang sebagai lapisan kedalaman.
→ **Yang tidak perlu ditiru:** objek 3D besar yang berubah bentuk — butuh video/WebGL, berat di
jaringan seluler.

**Velorix IIC** (kategori Hero, berbayar, positioning "AI defense") — hitam pekat, semua serba
terpusat, objek 3D neon ungu–magenta dengan partikel dan *point cloud*.

→ Ini justru contoh **apa yang harus dihindari OmniSense**: gradasi neon, objek 3D abstrak di
tengah, semua elemen center. Terlihat mahal untuk brand teknologi tinggi, tapi untuk konsultan
yang menjual pengukuran, tampilannya tidak menjelaskan apa pun dan berat saat dibuka di HP.

**Scroll Marquee** — deretan kartu hero bergeser horizontal tanpa henti, konten diduplikasi untuk
loop mulus. Menarik, tapi untuk OmniSense **marquee bukan untuk hero** — teks di dalamnya tidak
terbaca di layar HP dan mengalihkan dari nilai jual. Pakai marquee hanya sebagai **strip tipis**
di bawah hero (kapabilitas/klien).

---

## 3. Keputusan: teknik mana yang dipakai, mana yang dibuang

**DIPAKAI**

| Teknik | Alasan |
|---|---|
| Scroll-linked reveal (IntersectionObserver + stagger) | Memberi urutan baca; ringan, tanpa library |
| Kinetic headline (kata muncul satu-satu dari balik mask) | Hanya 4 dari 526 prompt memakainya → pembeda |
| Canvas jaringan titik-garis | Menggantikan video background: efek "hidup" tanpa unduh MB |
| Count-up skor + bar dimensi yang mengisi saat masuk layar | Menggerakkan angka produk, bukan sekadar hiasan |
| Garis rail yang tumbuh mengikuti progres scroll | Menjelaskan urutan 4 langkah tanpa teks tambahan |
| Marquee strip kapabilitas | Cepat, hemat ruang, berhenti saat di-hover |
| Glass card (blur tipis, 1–2 tempat saja) | Kedalaman tanpa berat |
| Grain/noise overlay | Murah, langsung menaikkan kelas tampilan |
| Spotlight kursor (hanya desktop, nonaktif di sentuh) | Sentuhan premium terakhir |
| Preloader pendek < 1 detik | Hanya kalau tidak menghambat; wajib bisa dilewati |

**DIBUANG**

| Teknik | Alasan |
|---|---|
| Video background (92 prompt memakainya) | 3–6 MB sekali buka; target kita HP di jaringan seluler |
| WebGL/Three.js penuh | Baterai & GPU HP kelas bawah; manfaatnya kecil untuk penjelasan produk |
| Glitch / RGB split / scramble teks | Bertabrakan dengan kesan konsultan yang bisa dipercaya |
| Page transition ala SPA | Situsnya satu halaman; biaya besar, manfaat nol |
| 3D tilt card & smooth-scroll library | Gimmick; menambah JS tanpa menambah pemahaman |
| Gradient aurora / mesh ungu-biru | Penanda paling jelas dari "situs AI generik" |

---

## 4. Yang sudah diimplementasikan di `website/index.html` (motion v2 — terkunci)

Demo nyata (bukan mockup): HTML satu file, **tanpa dependensi apa pun**. Semua animasi di bawah
ini adalah satu sistem, bukan tambalan — setiap elemen punya peran dalam urutan baca.

**Masuk (0–2,5 detik)**
1. Judul muncul kata per kata dari balik mask (stagger 55 ms), lalu subjudul → tombol → baris
   kecil → panel skor naik berurutan. Tanpa preloader: tidak ada layar tunggu yang menghambat.
2. Panel skor: busur gauge mengisi ke 68%, angka berhitung naik (easing kubik), 4 bar dimensi
   mengisi dengan jeda bertingkat 90 ms. Angka produk yang bergerak, bukan hiasan.

**Sepanjang gulir**
3. Parallax tiga lapis di hero: teks 0,14×, canvas 0,08×, panel skor 0,05×. Kecepatan berbeda
   inilah yang membuat hero terasa punya kedalaman tanpa video/WebGL.
4. Teks hero memudar halus saat hero ditinggalkan (habis di ujung hero) — tidak ada elemen yang
   "menempel" mengganggu bagian berikutnya.
5. Rail progres 4 langkah tumbuh mengikuti posisi gulir, dan titik 01–04 menyala bertahap
   mengikuti panjang rail (ambang 6% / 32% / 58% / 84%), jadi urutan langkah dijelaskan gerakan.
6. Rel tick di tepi kanan (desktop ≥1100px) mengisi sepanjang halaman + angka persen gulir.
   Ini motif alat ukur — hal yang sama yang dijual OmniSense.
7. Reveal per-section saat masuk viewport, dengan stagger sampai 8 baris untuk daftar 8 dimensi.
8. Navbar: blur + garis setelah 24px, dan tautan bagian aktif ditandai garis teal (scrollspy).
9. Marquee strip kapabilitas: loop mulus, berhenti saat hover.

**Detail kecil yang menaikkan kelas**
10. Canvas jaringan titik-garis: titik putih, garis teal, bereaksi ke kursor, DPR dibatasi 2,
    jumlah titik menyesuaikan lebar layar, berhenti saat tab tidak aktif **dan** saat hero keluar
    viewport.
11. Lampu radial mengikuti kursor dengan lerp 0,09 (desktop ber-pointer presisi saja; mati di
    perangkat sentuh).
12. Grain halus di seluruh halaman (5% opasitas) — murah, menghilangkan kesan "template polos".
13. Baris 8 dimensi: garis teal tipis muncul di tepi saat baris disorot.

**Guardrail performa & aksesibilitas**
- `prefers-reduced-motion` → seluruh animasi mati, konten langsung tampil dalam keadaan final
  (canvas & lampu kursor disembunyikan, skor 68, bar terisi, rail penuh, 4 langkah menyala).
- Saklar manual "Gerak: Nyala/Mati" di kanan bawah (tersisa satu kontrol; pemilih tema sudah
  dihapus karena temanya terkunci) — perilakunya identik dengan reduced-motion, dan bisa
  dinyalakan ulang tanpa reload.
- Tanpa horizontal scroll di 1440px maupun 390px. Kontras teks sekunder ≥ 7:1.
- Nol error konsol, nol error JavaScript (diuji Chromium headless).

**Hasil uji terakhir** (`/tmp/qa/verify_final.js`, Chromium headless)

```
console: []            errors: []
desktop hero      skor 68 · busur 104.55 · bar 82/74/61/48% · lampu kursor aktif · rel tick 000%
gulir 420px       parallax canvas +33,6px · teks hero opasitas 0,56 · nav blur aktif
proses masuk      rail 13% · 1 langkah menyala
proses tengah     rail 69% · 3 langkah menyala
dimensi           rail 100% · 4 langkah · nav "Penilaian" aktif
bawah halaman     rel tick 100% · nav "Kontak" aktif
gerak dimatikan   canvas none · lampu kursor 0 · skor & bar langsung final · rail 100%
gerak dinyalakan  animasi jalan lagi, nol error
mobile 390px      scroll width 390/390 · lampu kursor mati (sentuh) · rail 60% saat di tengah
reduced-motion    canvas none · skor 68 · bar terisi · 4 langkah menyala · rel tick disembunyikan
```

---

## 5. Cara membuka demo

```
Buka langsung:  /home/ubuntu/ai-agency/website/index.html
Pratinjau:      /home/ubuntu/ai-agency/website/pratinjau/final-01-hero.png (…02-proses, 03-dimensi,
                04-cta, 05-mobile-hero, 06-mobile-proses, 07-tanpa-gerak)
Uji ulang:      node /tmp/qa/verify_final.js   (butuh playwright-core di /tmp/camofox)
```

Satu-satunya kontrol yang tersisa adalah saklar "Gerak: Nyala/Mati" (tombol ◎ kanan bawah) —
untuk membandingkan versi beranimasi dengan versi tenang, bukan lagi untuk memilih tema.


## 6. Kalau diteruskan ke produksi

- Pindah ke Next.js/Astro dengan struktur section yang sama; animasi bisa langsung ke Framer Motion
  (103 dari 526 prompt memakainya, jadi dokumentasinya banyak) atau tetap vanilla seperti demo.
- Tambahkan: satu studi kasus nyata, nomor WhatsApp CTA, logo klien bila ada.
- Ganti isi `omnisense.id` yang saat ini masih halaman "NeoSense Social Media Intelligence".

---

## 7. Redesign v3 — pola yang diambil dari inspo

Sumber inspo: post X `@Osmbproduction` (video → 60fps.design) dan `@thedzianis`
(7 situs: getlayers.ai, navbar.gallery, supahero.io, 404s.design, footer.design, cta.gallery,
unsection.com). Aset mentah di `referensi/60fps-design/` dan `referensi/inspo-web-thedzianis/`.

**Diagnosis halaman v2:** semua section berbentuk sama (eyebrow → h2 → paragraf → baris
bergaris). Tidak ada variasi ritme, skala, atau jenis modul — itu sumber kesan monoton.

Pola yang dipakai, dan asalnya:

1. **Watermark tipografi raksasa** (60fps.design) — "OMNISENSE" 300px di belakang hero,
   opasitas 0,055 + garis tipis, terpotong tepi, parallax laju 0,03. Diulang di footer
   (footer.design) pada 216px.
2. **Strip indeks bagian** (sidebar cta.gallery, dipindah jadi horizontal) — menempel di bawah
   nav, 7 item bernomor + label berunit (`4 langkah`, `5 rentang`, `8 dimensi`, `6 keluaran`,
   `6 istilah`, `2 proyek`, `1 nomor`); angka telanjang tanpa satuan terbaca sebagai noise. Di 1440
   pas tanpa terpotong, di mobile digeser dengan snap (item terpotong = petunjuk geser).
3. **Kartu bernomor + metadata** (60fps.design) — 8 dimensi jadi kartu 2 kolom: nomor,
   `BOBOT xx%`, judul, deskripsi, bar relatif terhadap bobot terbesar (20%).
4. **Tangga kategori skor** (modul baru, dari `kalkulator_kesiapan.py`) — skala 0–100 lima
   segmen + penanda teal yang bergerak ke 68%, lalu daftar 5 kategori beserta rentangnya.
5. **Daftar keluaran bernomor** (unsection.com / 60fps) — 6 hal yang diterima klien, nomor di
   kiri, jenis keluaran di kanan.
6. **Chip scroll-snap + panel** (chip rail 60fps + filter navbar.gallery) — kamus istilah:
   6 chip, klik atau panah kiri-kanan menukar panel.
7. **Kartu kasus bernomor + chip spesifikasi** (60fps) — 001/002, tiga baris Masalah / Yang
   dibangun / Hasil, plus baris angka nyata (12 armada, 395 pengiriman diimpor, 14 modul,
   80 endpoint, 5 container).
8. **CTA dan footer** (cta.gallery + footer.design) — CTA full-bleed dengan glow teal dan nomor
   telepon raksasa bergaris (`-webkit-text-stroke` teal 0,42, `aria-hidden`), footer 3 kolom
   dengan wordmark raksasa di tepi bawah.

**Sengaja tidak diambil:** mode terang (60fps, supahero, 404s), galeri mockup ponsel, dan grid
kartu untuk daftar layanan. OmniSense menjual jasa konsultasi, bukan katalog animasi.

**Perubahan gerak:** rel tick kanan tetap; rail 4 langkah diganti titik per langkah yang menyala
bertahap; bar bobot dan penanda tangga mengisi saat masuk viewport.

**Bug yang ketemu saat uji dan sudah diperbaiki:**

- `.foot p` (spesifisitas 0,1,1) menimpa `.foot-wm` → wordmark footer hanya 11px. Diganti
  `.foot-grid p`.
- `</main>` menutup setelah `<footer>`; dipindah ke sebelum footer.
- Teks mono kecil 10–11,5px dinaikkan ke 12px agar tetap terbaca.
- Nomor telepon CTA awalnya `rgba(244,244,245,.09)` (nyaris tak terbaca) → jadi garis teal
  `-webkit-text-stroke` dan ditandai dekoratif.

**Hasil uji terakhir** (`scripts/verify_page.js`, Chromium headless, 6 lintasan)

```
ok true · console [] · errors []
overflow 1440/1440 di semua lintasan desktop · 390/390 di mobile
skor 68 · bar bobot 502,5/376,9/376,9/376,9/251,3/251,3/251,3/125,6 px (100/75/75/75/50/50/50/25)
reduced-motion: bar + penanda langsung final, rel tick disembunyikan
tanpa-gerak → nyala lagi: animasi berjalan ulang, nol error
tab kamus: klik dan panah kiri/kanan menukar panel, aria-selected ikut berubah
```

Pratinjau: `pratinjau/v3-*.png` (hero, cara kerja, kategori, dimensi, output, kamus, hasil,
kontak, footer, mobile).
