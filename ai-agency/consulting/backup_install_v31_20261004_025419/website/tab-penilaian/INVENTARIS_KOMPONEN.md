# INVENTARIS KOMPONEN — TAB PENILAIAN KESIAPAN DI SITUS
Disusun: 30 Sep 2026 · Status: **SUDAH DIBANGUN** (lihat "Status akhir" di bawah)
Tujuan: pengunjung mengisi penilaian sendiri di situs dan langsung melihat skor
kesiapan bisnisnya, tanpa menunggu sesi konsultasi.

---

## STATUS AKHIR (30 Sep 2026)

Semua poin di dokumen ini sudah dikerjakan kecuali yang ditandai. Empat keputusan
yang tadinya memblokir sudah diambil (dengan kebebasan dari user) dan ditulis di
`tab-penilaian/pertanyaan.json`:

| Keputusan | Yang dipilih |
|---|---|
| K1 panjang | **8 pertanyaan** (1/dimensi, 1–2 menit). Versi 32 tetap tersedia di bank pertanyaan tim untuk sesi konsultasi. |
| K2 hasil | **Dibuka penuh di situs** (skor, band, 8 dimensi, 2 celah utama + 1 kekuatan, langkah berikutnya). Laporan lengkap tetap jualan tim. |
| K3 data | **Tidak ada data dikirim/di-simpan di server.** Jawaban hanya di `localStorage` perangkat. WhatsApp berisi skor + 8 jawaban, dan pengunjung yang menekan kirim. |
| K4 band | **20/40/60/80 dipertahankan** — identik dengan `kalkulator_kesiapan.py` dan bagian Kategori. |

Berkas jadi: `pertanyaan.json`, `bangun_tab.py` (idempoten), `uji_paritas.js`,
`uji_tab.js`, `shot_tab.js`. Skor acuan pola `4 3 5 3 2 3 3 2` = **65,0% · Layak Lanjut**.
Uji: 5/5 paritas + 23/23 interaksi lulus.

Sisa yang belum dikerjakan (opsional, butuh keputusan user): penerima data otomatis
(endpoint/notifikasi grup), versi 32 pertanyaan di situs, PDF laporan ber-kop.

---

## 0. KEPUTUSAN YANG HARUS DIAMBIL DULU (blocker, bukan pekerjaan)

| # | Keputusan | Pilihan | Dampak |
|---|-----------|---------|--------|
| K1 | **Panjang instrumen** | 8 pertanyaan (1/dimensi, mode inti) vs 32 (4/dimensi) | 8 = 1–2 menit, ramai yang selesai. 32 = 6–8 menit, banyak yang keluar di tengah. Cadangan: 8 dulu, lalu tawarkan "perdalam jadi 32" untuk yang mau laporan lengkap. |
| K2 | **Hasil dikunci di WhatsApp atau dibuka penuh di situs?** | (a) skor penuh tampil, WA opsional · (b) skor tampil, rincian + roadmap hanya via WA | (b) = prospek lebih banyak, tapi bertentangan dengan posisi "assessment gratis" dan bikin orang merasa dijebak. (a) lebih jujur, tetap dapat nomor WA dari yang serius. |
| K3 | **Data disimpan atau tidak** | Tanpa simpan (skor hilang saat tab ditutup) vs simpan (butuh backend/DB + UU PDP) | Tanpa simpan = nol risiko hukum, nol biaya server. Simpan = bisa kirim laporan otomatis & follow-up, tapi wajib kebijakan privasi + hapus data. |
| K4 | **Benar-benar gratis tanpa syarat?** | Ya, langsung dapat hasil | Konsisten dengan situs hari ini ("penilaian kesiapan gratis"). Kalau hasil dipotong, hapus kata "gratis" dari hero. |
| K5 | **Batas band** | 20/40/60/80 (sama dengan kalkulator) | Sudah selaras dengan `kalkulator_kesiapan.py` dan bagian "Kategori" di situs. Jangan diubah. |

---

## 1. MODEL DATA (sudah ada, tinggal dipakai)

Sumber tunggal kebenaran, sudah ada di repo:

- `kalkulator_kesiapan.py` — 8 dimensi + bobot + rumus + 5 band.
  Bobot: Data 20 · Infra 15 · Proses 15 · SDM 15 · Strategi 10 · Budaya 10 ·
  Tata kelola 10 · Anggaran 5.
- `key_questions_lengkap.md` — 32 pertanyaan tervalidasi riset + aturan anti-halusinasi.
- `template_penilaian.csv` (32 baris) & `template_skrining.csv` (8 baris) — kode Q/S,
  nama dimensi, kolom nilai 1–5, kolom catatan.
- `SOP_Kesiapan_Digitalisasi.md` — makna tiap skor, output wajib ke customer.

Rumus yang wajib dipakai di JS (sudah diuji, lihat §5):
```
skor_dimensi  = rata-rata(nilai pertanyaan dimensi itu)      // 1–5
skor_total    = Σ (skor_dimensi × bobot)                     // 0–5
persen        = skor_total / 5 × 100                         // 0–100
band          = 80 Siap Penuh | 60 Layak Lanjut | 40 Konvensional | 20 Awal | <20 Sangat Awal
```

**Penting:** 8 pertanyaan mode inti ≠ pertanyaan skrining. Teks pertanyaan
`template_skrining.csv` (S1–S7) belum ada S8, sedangkan kalkulator butuh 8 nilai
(1 per dimensi). Perlu satu pertanyaan untuk dimensi **Anggaran & Finansial**.
→ **Komponen #1 yang harus dibuat: pertanyaan S8 + versi bahasa awam untuk 8 pertanyaan inti.**

---

## 2. DAFTAR KOMPONEN

### A. Konten (tanpa ini tabnya kosong)

| # | Komponen | Isi | Sumber / cara bikin |
|---|----------|-----|---------------------|
| A1 | **8 pertanyaan inti versi awam** | 1 per dimensi, bahasa pemilik warung/kafe, bukan bahasa konsultan. Skala 1–5 dengan label kata (bukan cuma angka). | Turunkan dari `key_questions_lengkap.md` (B1–B8, ambil Q1 tiap dimensi) + `template_skrining.csv`. **Perlu ditulis & disetujui.** |
| A2 | **Pertanyaan S8 (Anggaran)** | Melengkapi 8 dimensi. Contoh: "Ada anggaran bulanan khusus untuk teknologi? Berapa?" | Baru — belum ada di skrining. |
| A3 | **Label tiap titik skala** | 1 = Belum ada · 2 = Masih manual · 3 = Sebagian · 4 = Jalan, belum rapi · 5 = Jalan & terukur | Selaras dengan anchor di `key_questions_lengkap.md` ("5 = terbukti jalan & terstruktur"). |
| A4 | **Kalimat kategori (5 band)** | Sudah ada di situs bagian "Kategori" — tinggal dipakai ulang agar tidak ada dua versi. | Ambil dari index.html `#kategori`; samakan dengan SOP §5. |
| A5 | **Rekomendasi per band** | Sudah ada (Siap Penuh → pilot besar; Layak Lanjut → pilot 1 proses; dst). | SOP §5 + `kalkulator_kesiapan.py` BANDS. |
| A6 | **Rekomendasi per dimensi lemah** | Untuk tiap dimensi, 1 kalimat "kalau skor Anda rendah di sini, langkah pertamanya…". Ini yang bikin hasil terasa berguna, bukan cuma angka. | **Belum ada. Perlu ditulis** (8 dimensi × 3 tingkat). |
| A7 | **Teks izin & privasi** | Kalimat pendek: apa yang disimpan, di mana, berapa lama, cara minta hapus. | Selaras `privacy_policy_omnisense.md`. Wajib kalau K3 = simpan. |
| A8 | **Disclaimer hasil** | "Skor ini titik awal diskusi, bukan penilaian mutu bisnis Anda." | Sudah ada di SOP §7 — pakai kalimatnya. |
| A9 | **Naskah kirim ke WhatsApp** | Isi pesan otomatis: skor, band, 2 dimensi terlemah, "minta laporan lengkap". | Bikin baru; pakai pola `wa.me/6288809640700?text=` yang sudah dipakai situs. |
| A10 | **Isi laporan (versi cetak/PDF)** | Ringkasan eksekutif, radar 8 dimensi, gap analysis, roadmap 30/60/90 hari. | SOP §6 sudah menentukan isinya. Kalau mau kirim PDF, perlu generator (lihat C4). |

### B. Antarmuka & logika di `index.html`

| # | Komponen | Keterangan | Perkiraan |
|---|----------|-----------|-----------|
| B1 | **Bagian tab baru** | `<section id="penilaian">` + 8 blok pertanyaan. Gaya mengikuti `#kamus` yang sudah ada (chips + panel), jadi tidak perlu bahasa desain baru. | 1 blok HTML |
| B2 | **Kontrol skala 1–5** | Tombol radio 5 titik (bukan slider — slider susah di HP dan tidak presisi). Aksesibel: `role="radiogroup"`, panah kiri/kanan, `aria-checked`. | JS + CSS |
| B3 | **Bilah kemajuan** | "Terjawab 5 dari 8" + bilah. Tanpa ini orang bingung sisa berapa. | JS |
| B4 | **Tombol Hitung** | Aktif hanya kalau 8 terjawab; kalau belum, tunjukkan mana yang kurang. | JS |
| B5 | **Mesin hitung** | Fungsi murni `hitung(nilai[8]) → {persen, band, per_dimensi}`. **Disalin apa adanya dari rumus kalkulator.** | ~30 baris |
| B6 | **Kartu hasil** | Angka persen besar + nama band + kalimat arti band + langkah berikutnya. Pakai cakram Canvas yang sudah ada (`drawDisc`) supaya hasil terasa menyatu dengan hero — bukan komponen baru. | pakai ulang |
| B7 | **Grafik 8 dimensi** | Batang horizontal, 8 baris, lebar = skor, sorot yang terendah. Radar SVG bisa menyusul; batang lebih mudah dibaca di HP. | SVG/CSS |
| B8 | **Blok "celah utama"** | 2 dimensi terlemah + rekomendasi A6. Ini inti nilainya. | dari A6 |
| B9 | **Panggilan lanjut** | Tombol WA dengan pesan A9 + tombol "salin hasil". | JS |
| B10 | **Simpan sementara** | `localStorage` supaya tidak hilang kalau ter-refresh. Kalau K3 = tanpa simpan, tetap pakai localStorage lokal (tidak ke server) + tombol hapus. | JS |
| B11 | **Rangka aksesibilitas** | Fokus pindah ke hasil setelah hitung, `aria-live` untuk skor, bisa dipakai keyboard penuh, kontras sesuai tema A. | JS |
| B12 | **Hormati `prefers-reduced-motion`** | Cakram & bar muncul langsung di keadaan akhir. Sudah jadi kebiasaan di halaman ini. | JS |
| B13 | **Tautan navigasi** | Tambah "Penilaian" di nav + `#penilaian` di daftar `spyIds` (penyorot bagian aktif) + tombol hero diarahkan ke tab, bukan langsung ke WA. | JS |
| B14 | **Tanpa JS tetap terbaca** | Kalau JS mati, tampilkan pesan "buka lewat WhatsApp" — jangan halaman kosong. | HTML |

### C. Kalau hasil mau dikirim / disimpan (opsional, tergantung K2 & K3)

| # | Komponen | Keterangan |
|---|----------|-----------|
| C1 | **Penerima data** | Minimal: kirim hasil ke WhatsApp tim (tidak perlu server). Lengkap: endpoint kecil (Cloudflare Worker / VPS) untuk simpan jawaban. |
| C2 | **Notifikasi tim** | Pesan ke grup tim tiap ada penilaian selesai — supaya bisa ditindaklanjuti, bukan cuma masuk lubang. |
| C3 | **Generator PDF** | Dari A10. Bisa di sisi pengunjung (cetak ke PDF dari halaman hasil) atau sisi server. Cetak dari halaman = paling murah, tanpa dependensi. |
| C4 | **Pencatatan hasil ke pipeline** | Simpan sebagai baris di `client_register.csv` / `template_penilaian.csv` supaya konsisten dengan alur manual hari ini. |

### D. Berkas & rumah kode

| # | Komponen | Keterangan |
|---|----------|-----------|
| D1 | **Berkas pertanyaan terpisah** | `tab-penilaian/pertanyaan.json` — 8 pertanyaan + label skala + bobot + band + rekomendasi. Satu sumber, supaya HTML dan Python tidak bisa berbeda. |
| D2 | **Skrip pembangun** | `tab-penilaian/bangun_tab.py` — menyisipkan bagian tab ke `index.html`, **idempoten**, mencadangkan dulu ke `arsip/`. Pola sama dengan `adopt_index_motion.py` yang sudah dipakai. |
| D3 | **Uji paritas** | `tab-penilaian/uji_paritas.js` — **sudah dibuat & lulus** (lihat §5). |
| D4 | **Skrip QA render** | Pakai `motion-landing-page/scripts/verify_page.js` yang sudah ada + tambahan: isi 8 jawaban, tekan Hitung, periksa skor tampil. |
| D5 | **Jalur deploy** | **SELESAI 30 Sep** — `website/SERAH_TERIMA_DEPLOY.md`: daftar berkas yang diunggah, perintah `scp`/`rsync`, blok nginx lengkap (404, cache, gzip, header keamanan), daftar periksa sesudah pasang. Deploy tetap dijalankan Vincent — mesin agent tak punya akses VPS. |

### E. Tema & konsistensi

| # | Komponen | Keterangan |
|---|----------|-----------|
| E1 | **Palet** | Obsidian + teal (Tema A terkunci). Jangan tambah warna; pakai token `cssVar` yang sudah ada. |
| E2 | **Istilah** | Ikuti bagian "Kamus" — tulis untuk pemilik usaha, bukan tim teknis. |
| E3 | **Tidak menyalin kompetitor** | Instrumen sendiri sudah tervalidasi riset (`riset_validasi_kesiapan.md`). Jangan mengadopsi kuesioner pihak lain. |
| E4 | **Konsistensi angka** | Angka contoh di hero (68) dan di bagian Kategori harus tetap cocok dengan hasil tab. |

---

## 3. YANG SUDAH ADA vs BELUM

**Sudah ada (dipakai ulang, tidak perlu dibuat)**
- Rumus, bobot, 5 band, rekomendasi band → `kalkulator_kesiapan.py`
- 32 pertanyaan tervalidasi + anchor skor → `key_questions_lengkap.md`
- 8 pertanyaan skrining (kurang 1) → `template_skrining.csv`
- Kalimat kategori di situs → `index.html` bagian `#kategori`
- Cakram skor Canvas → `drawDisc` di `index.html`
- Pola chips/tab aksesibel → `selectTab` di `index.html`
- Skrip verifikasi render headless → skill `motion-landing-page`
- Kebijakan privasi → `privacy_policy_omnisense.md`

**Belum ada (perlu dibuat)**
- Pertanyaan S8 (Anggaran) + 8 pertanyaan versi bahasa awam (A1, A2)
- Label tiap titik skala (A3)
- Rekomendasi per dimensi lemah (A6) ← yang paling menentukan hasil terasa berguna
- Teks izin/privasi khusus tab (A7)
- Naskah pesan WhatsApp berisi hasil (A9)
- Seluruh antarmuka tab (B1–B14)
- Berkas pertanyaan bersama + skrip pembangun + QA (D1–D4)
- Penerima data & notifikasi tim (C1, C2) — hanya kalau hasil mau ditindaklanjuti

---

## 4. URUTAN PENGERJAAN YANG DISARANKAN

1. **Putuskan K1–K4.** Tanpa ini, komponen A tidak bisa ditulis dan B bisa salah bentuk.
2. Tulis A1, A2, A3, A6 → jadi `tab-penilaian/pertanyaan.json`. Minta kamu tinjau isinya
   sebelum ada kode tampilan (ini wajah OmniSense ke calon klien).
3. Bangun B1–B6 dengan data contoh → tampilkan skor benar. Uji paritas lawan Python (D3).
4. Tambah B7, B8, B9 → hasil jadi berguna, bukan cuma angka.
5. B10–B14 → ketahanan & aksesibilitas.
6. A7, A9 + C1, C2 kalau hasil mau dikirim ke tim.
7. QA: `verify_page.js` (desktop 1440, HP 390, keyboard, gerak mati, JS mati) + tinjauan visual.
8. Serah terima deploy ke Vincent.

Perkiraan: langkah 2–5 = satu blok kerja penuh. Langkah 1 = keputusan kamu, cepat tapi wajib.

---

## 5. SUDAH DIVERIFIKASI HARI INI

`tab-penilaian/uji_paritas.js` dijalankan dengan node v26.8.1, dibandingkan langsung
ke keluaran `kalkulator_kesiapan.py`:

```
OK    [4,3,5,3,2,3,3,2]  ->  65.0%  LAYAK LANJUT  (py 65.0)
OK    [5,5,5,5,5,5,5,5]  -> 100.0%  SIAP PENUH    (py 100.0)
OK    [1,1,1,1,1,1,1,1]  ->  20.0%  AWAL          (py 20.0)
OK    [3,3,3,3,3,3,3,3]  ->  60.0%  KONVENSIONAL  (py 60.0)
OK    [5,4,3,2,1,5,4,3]  ->  69.0%  LAYAK LANJUT  (py 69.0)
```

Batas band juga diperiksa: 39→Awal, 40→Konvensional, 59→Konvensional,
60→Layak Lanjut, 79→Layak Lanjut, 80→Siap Penuh. Cocok.

Artinya: rumus yang akan ditanam di situs sudah terbukti menghasilkan angka yang
sama persis dengan alat yang dipakai tim saat sesi konsultasi. Sisa pekerjaan
adalah isi pertanyaan + tampilan, bukan matematikanya.

Catatan temuan: `template_skrining.csv` hanya punya 7 baris (S1–S7) sementara
kalkulator butuh 8 nilai. Satu pertanyaan (Anggaran & Finansial) belum pernah ada.

---

## v1.1 — lapisan validitas (30 Sep 2026)

Tujuan: skor yang keluar dari situs lebih bisa dipercaya, dan bot WhatsApp tidak perlu
menebak apa pun saat klien mengirim hasilnya. Semua tetap jalan di perangkat pengunjung.

Yang ditambahkan:

1. `pertanyaan.json` → `keyakinan` (yakin / ragu / tidak_tahu) + `aturan_konsistensi`
   (R1, R3, R4) + `format_pesan`. Aturan baru cukup ditambah di JSON, JS tidak diubah.
2. Baris "Seberapa yakin?" di tiap kartu soal (`#penList .pen-key`, kelas `.pen-kbtn`),
   disimpan di `localStorage` kunci `omnisense_penilaian_keyakinan_v1`.
3. Kotak peringatan `#penCek` di bawah daftar soal saat ada pasangan jawaban bertentangan.
   Skor tetap dihitung — peringatan hanya menandai, tidak menghukum.
4. Catatan keterbatasan `#phLimit` di panel hasil: menyebut jumlah jawaban belum pasti
   dan/atau jumlah jawaban bertentangan.
5. Pesan WhatsApp kini diawali blok mesin: `[PENILAIAN-SITUS v1]`, `D1=.. D8=..`,
   `skor_situs=.. band=..`, `keyakinan=..`, opsional `catatan_situs=R1`.
   Nomor tujuan tetap `6288809640700` (tidak diubah).
6. `../baca_penilaian.py` (sisi bot): parse pesan → hitung ulang lewat
   `kalkulator_kesiapan.py` → JSON (`skor_hitung_ulang`, `selisih`, `belum_pasti`,
   `catatan_situs`, `dua_terlemah`, `dua_terkuat`, `ringkas`).
7. Aturan konsultan di skill `omnisense-consultant`: DM berpenanda `[PENILAIAN-SITUS v1]`
   dijawab tanpa ditag; skor situs diperlakukan sebagai klaim, wajib dihitung ulang.

Uji:

```
uji_paritas.js    5/5   JS vs Python, termasuk batas band
uji_tab.js       37/37  interaksi + keyakinan + konsistensi + pola bertentangan
uji_rangkaian.js  8/8   href tombol WA nyata -> baca_penilaian.py -> skor cocok
verify_page.js   0 error, tanpa overflow 1440/390
```

Skor acuan tetap `4 3 5 3 2 3 3 2` = **65,0% · Layak Lanjut**. Pola sengaja bertentangan
`3 5 1 3 3 3 3 3` = 62,0% dan harus memicu R1.
