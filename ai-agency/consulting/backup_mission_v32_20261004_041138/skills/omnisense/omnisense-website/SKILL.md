---
name: omnisense-website
description: "Sunting/QA situs OmniSense: tema terkunci, uji, pratinjau."
---

# Situs OmniSense (`website/index.html`) — sunting, uji, buktikan

Dipakai setiap kali menyentuh `/home/ubuntu/ai-agency/website/`: teks, layout, angka,
CSS, meta, halaman baru — termasuk permintaan "kurangi yang ramai".
Skill `omnisense-consultant` mengatur percakapan WA-nya; skill ini mengatur berkas situsnya
(termasuk aturan perawatan halaman penilaian mandiri: sumber kebenaran tunggal =
`tab-penilaian/pertanyaan_situs.json`).

## Aturan tetap (jangan dilanggar)
- TEMA A: basis gelap + aksen teal. **PERIKSA DULU, jangan asumsikan.** Dulu navy
`#081726`; sejak 1 Okt 2026 pagi berkasnya memakai `--obsidian:#080808` (netral/zinc)
plus `--signal:#14B8A4`, dan `404.html`/`privacy.html` ikut berubah. Sebelum menyunting
palet, baca `:root` yang ADA di berkas dan konfirmasi ke Michael kalau ragu — jangan
mengembalikan ke navy atas inisiatif sendiri, dan jangan pula menyebar palet baru tanpa
diminta. Palet diubah lewat sesi paralel; lihat "Bahaya sesi paralel" di bawah.
- Isi & nada teks pemasaran JANGAN diubah kecuali Michael minta eksplisit.
- Michael tidak suka tampilan ramai: angka/nomor hiasan, label pengulang, ornamen
duplikat dibacanya sebagai "gapenting, terlalu ramai". Kalau dia bilang begitu,
RAPIKAN langsung — jangan tanya panjang lebar. Pilih kelompok yang paling jelas hiasan,
kerjakan, lalu tunjukkan perbandingan sebelum–sesudah. Data asli (persen bobot, nomor
pertanyaan, urutan langkah, tag "Langkah 0X") TETAP; yang dibuang hanya pengulang/ornamen.
- Mesin ini TIDAK bisa deploy (VPS `omnisense.id` = Vincent). Serahkan lewat
`SERAH_TERIMA_DEPLOY.md`; jangan pernah bilang situsnya sudah online.
- **Penilaian mandiri kini HALAMAN TERPISAH**: `penilaian.html` (dibuka di tab baru dari blok
"pintu" di `#penilaian`), gaya dari `assets/penilaian.css`, data dari
`assets/penilaian-data.js`. `index.html` TIDAK lagi memuat mesin penilaian — jangan mencari
`window.__PENILAIAN__` di sana. Sumber kebenaran tunggal = `tab-penilaian/pertanyaan_situs.json`:
ubah soal/bobot/kata kunci di situ, lalu jalankan `python3 tab-penilaian/bangun_data_situs.py`
(jangan menyunting `penilaian-data.js` dengan tangan). Setiap suntingan `index.html` MAUPUN
`penilaian.html` WAJIB diikuti uji + `verify_page.js` + regenerasi pratinjau; tanpa itu,
suntingan "kecil" bisa diam-diam merusak halaman penilaian.

## Langkah menyunting
1. Cadangkan dulu: `cp index.html arsip/index-sebelum-<perubahan>.html`. Jangan menimpa
   cadangan lama; kalau sudah ada, lewati.
2. Cek apakah elemen yang mau dibuang masih dipakai JS: grep `querySelector` untuk
   class/id terkait. Elemen yang hilang tapi masih dicari JS = error konsol.
3. Sunting dengan regex spesifik + hitung penggantian (`re.subn`) dan laporkan angkanya.
   Hasil 0 = polanya salah, jangan lanjut.
4. Buang CSS mati setelah elemennya hilang (lihat `references/merapikan-elemen-hias.md`).
5. Uji, dari `website/`, dengan
   `CHROME_PATH=~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome` dan
   `PW_CORE=/tmp/camofox/node_modules/playwright-core`:
   `node tab-penilaian/uji_halaman.js` (alur penilaian penuh: identitas → 15 jawaban → skor → pesan)
   dan `node tab-penilaian/uji_baca.js` (baca tulisan bebas, ratusan kalimat nyata);
   paritas skor dicek dengan membandingkan skor situs ke `python3 kalkulator_kesiapan.py -n 15 ...`.
   Baterai 8-soal lama ada di `arsip/uji-tab-lama/` — JANGAN dijalankan, itu desain lama.
   Lalu `node /home/ubuntu/.hermes/skills/creative/motion-landing-page/scripts/verify_page.js index.html /tmp/v`
   (`verify_page.js` milik skill `motion-landing-page`, bukan berkas proyek — jalankan dari sana).
6. Regenerasi pratinjau resmi: `node scripts/shot_final.js` dan `node scripts/shot_legal.js`.
7. Kirim bukti visual ke Michael: komposit sebelum–sesudah per bagian
   (`scripts/gabung_sebelum_sesudah.py` di skill ini) sebagai `MEDIA:<path>`.

Pratinjau ke Michael: `python3 -m http.server` di `website/` + cloudflared quick tunnel;
sebutkan bahwa linknya sementara dan jangan dipakai di materi promosi.

## Bahaya sesi paralel (WAJIB dibaca sebelum menyunting)
`website/index.html` bisa sedang disunting oleh sesi Hermes LAIN pada saat yang sama
(sesi WhatsApp/gateway milik Michael berjalan bersamaan dengan sesi CLI). Gejalanya:
mtime berkas berubah tanpa kita menyentuhnya, tema/isi tiba-tiba berbeda dari cadangan
kita, atau `uji_*.js` gagal dengan sebab yang tidak kita buat.

Protokol:
1. **Sebelum menyunting**, catat sidik jari: `md5sum` + mtime + `stat`. Ulangi setelah
   jeda ~10 detik. Kalau berubah sendiri = sesi lain sedang menulis. JANGAN menimpa;
   tunggu sampai stabil (md5 sama 2-3 kali berturut-turut) baru lanjut.
2. **Setelah menyunting**, verifikasi ulang bahwa hasil kita masih ada (grep penanda
   hasil) — sesi lain bisa menimpa suntingan kita. Kalau hilang, pasang ulang, lalu
   sebutkan ke Michael bahwa ada dua penulis di berkas yang sama.
3. Kalau tema/palet berbeda dari yang kita ingat, itu kemungkinan besar permintaan
   Michael di sesi lain — jangan "perbaiki" balik tanpa bertanya.

## Jebakan
- **CSS bisa rusak total tanpa error JS.** Kesalahan khas: deklarasi `rgba(...)` atau
  fungsi lain kehilangan tanda `)`, sehingga parser CSS membuang SEMUA rule setelahnya.
  Halaman masih tampil (font/warna default) tapi layout, grid, dan tombol hilang — dan
  `uji_*.js` gagal dengan sebab membingungkan (mis. `@media print` tidak berlaku).
  **Penjaga wajib** setiap selesai menyunting:
  `python3 -c "s=open('index.html').read(); print(s.count('(')-s.count(')'))"` harus `0`,
  dan hitung rule ter-parse dari browser:
  `document.styleSheets[0].cssRules.length` harus ratusan (≥300), bukan belasan.
  Kalau angkanya kecil, cari pola `rgba\([^();{}]*[;}]` — kurung tutupnya hilang.
- **Penyebab tersering kerusakan itu: sapuan warna dengan regex.** Pola seperti
  `rgba\(([^()]*?)(;)` (atau `[^()]*` yang "malas") bisa menyeberangi batas aturan CSS dan
  MENELAN `)` di dekatnya — sekali jalan, 37 deklarasi rusak dan 400+ rule terbuang.
  Aturan: mengganti warna/nilai = **`str.replace` literal**, satu nilai per penggantian.
  Kalau perlu daftar pasangan lama→baru, pakai dict + `for lama,baru in pasangan: s=s.replace(...)`.
  Jangan pernah memakai regex lintas-batas untuk mengganti nilai CSS.
- **Setiap temuan "kopong"/layout pincang WAJIB diukur ulang setelah CSS dipulihkan.**
  Saat CSS rusak, halaman tampil tanpa layout: bagian tampak melompong, ikon SVG melar ke
  1440x1440 px, dan angka "tinggi 1599 px / 39 kata" itu artefak, bukan desain. Semua
  diagnosis densitas dari kondisi CSS rusak = tidak sah. Ukur ulang setelah rule ≥300.
- **Hapus nomor, kartu jadi keropos.** Setelah membuang nomor di kartu, periksa grid-nya
  (`getBoundingClientRect` atau screenshot): ruang kosong sisa di atas judul = tinggi kartu
  dulu ditahan nomor itu, jadi padding/jaraknya perlu disesuaikan.
- **Laporan "teks terpotong" dari pemeriksa visual sering salah.** Rail `.ixbar` memang
  `overflow-x:auto` + `scroll-snap-type`; terpotong di tepi layar HP itu DESAIN, bukan bug.
  Konfirmasi ke CSS/DOM (`scrollWidth > clientWidth`, ada `overflow-x`) sebelum memperbaiki.
- **Pemeriksa visual tidak bisa dipercaya untuk teks kecil.** Untuk memastikan isi kotak
  peringatan/label, baca DOM (`innerText`) atau tangkap elemen itu saja.
- **Jangan menjalankan generator lama sebagai "penyegar".** `bangun_tab.py` menanam blok
  `#penilaian` versi 8-soal; sejak pemisahan tab blok itu sudah diganti pintu tautan, jadi
  menjalankannya bisa mengembalikan markup usang. Regenerasi yang sah hanya
  `bangun_data_situs.py` (data) dan skrip pratinjau.
- **Baca tulisan bebas: lihat `references/mesin-baca-tulisan-bebas.md`.** Ringkasnya: negasi
  wajib dihitung, frasa terpanjang menang, kata pengisi dibuang, dan mesin harus MENOLAK
  menebak saat ragu. Aturan konsistensi di sumber ditulis dengan kode DIMENSI sementara jawaban
  ber-kode SOAL — terjemahkan di generator, kalau tidak peringatan "perlu ditinjau" tak akan
  pernah menyala dan tak ada error apa pun sebagai petunjuk.
- **Saat uji gagal, periksa dulu apakah ujinya yang salah.** Berulang kali "kegagalan" ternyata
  selector keliru, kode soal yang tidak ada, atau ekspektasi uji yang tidak sesuai teks pilihan —
  situsnya benar. Baca teks pilihan soal dan DOM sebenarnya sebelum menyentuh berkas situs;
  kalau ujinya yang salah, perbaiki uji itu dan tulis alasan koreksinya di dalam uji.
- **Uji jangan menyalin rumus/logika situs** — panggil API aslinya, kalau tidak ujinya
  menguji dirinya sendiri.

## Konsultasi v3 — 4 Oktober 2026
Untuk build konsultasi baru baca `/home/ubuntu/ai-agency/website/SERAH_TERIMA_KONSULTASI_V3.md`, playbook dan spesifikasi dalam consulting. Halaman `konsultasi-v3.html` telah dibuat/diuji internal, belum deploy atau terhubung CTA homepage. Generator v3 `consulting/bangun_data_v3.py`; sumber bank tunggal `consulting/pertanyaan_v3.json`. Jalur legacy terpisah. Jangan menjanjikan integrasi gateway atau hasil empiris yang belum diuji.

## Revisi3.1
Baca ALUR_OPERASIONAL_OMNISENSE.md dan SERAH_TERIMA_KONSULTASI_V3.md bagian3.1. Bankversion3.1,markerWA v3,enginebaru disertai decision_v31.py,asetregenerasi bangun_data_v3.py. Konsultasi diawali konteks, bukan skor sebagai kesimpulan. Keputusan/next_questions mengikuti mesin. Jangan mengaktifkan gateway/publish/handoff otomatis dari dokumen saja.
