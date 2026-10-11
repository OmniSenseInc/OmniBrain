# Mesin baca jawaban tulis-sendiri (Bahasa Indonesia)

Konteks: `penilaian.html` membolehkan pengunjung menulis jawaban dengan kata-kata sendiri;
mesin harus memetakan tulisan itu ke skor 1–5 (dan menampilkan hasil bacaan agar bisa dikoreksi).

## Tiga lapis pencocokan
1. **Frasa kunci** per pilihan (kunci `k` di `pertanyaan_situs.json`) — dicocokkan setelah normalisasi.
2. **Fallback kemiripan kata** terhadap teks pilihan itu sendiri.
3. **Penguat (boost) ke 5** kalau ada frasa level-5 yang sah.

## Aturan yang wajib ada
- **Negasi harus dihitung.** "belum / tidak / nggak / ga / belum pernah" membalik makna frasa.
  Tanpa ini, "belum punya rencana tertulis" terbaca 5/5 — persis kebalikan artinya.
  Ini kesalahan paling mahal di mesin ini.
- **Frasa terpanjang menang**, dan **setiap kata hanya boleh dipakai sekali**; kalau tidak,
  frasa umum menelan frasa spesifik yang lebih tepat.
- **Buang kata pengisi sebelum mencocokkan**: yang, yg, itu, tuh, sih, deh, mah, kok, loh, dong,
  nih, pun. Kata pengisi memecah frasa sehingga frasa kunci tidak lagi cocok
  ("banyak yang terlewat" ≠ "banyak terlewat").
- **Jangan menebak kalau ragu.** Fallback kemiripan hanya dipakai kalau skor teratas ≥ 0,34 DAN
  selisihnya dengan peringkat kedua ≥ 0,15. Kalau tidak, kembalikan "tidak terbaca" dan minta
  pengunjung memilih sendiri. Lebih jujur mengaku tidak paham daripada salah menilai.
- **Penguat harus bisa dijangkau.** Kalau level 4 dan level 5 nilainya seri, urutan pengurutan
  membuat boost tidak pernah menyala. Pastikan level-5 berada di depan saat syarat penguat terpenuhi.
- **Kata kunci terlalu umum merusak.** Frasa seperti "tetap jalan" di pilihan level 4 menyerobot
  jawaban pilihan lain — buang atau ganti di sumber, jangan ditambal di mesin.

## Cara mengukur (jangan mengira-ngira)
- Tulis baterai **kalimat nyata ala pemilik usaha** (bukan kalimat template) di
  `tab-penilaian/uji_baca.js`, lalu ukur akurasinya. Beberapa contoh tidak cukup untuk
  menyimpulkan mesinnya benar.
- Kalau akurasi rendah, perbaiki **kosakata di `pertanyaan_situs.json`** lalu regenerasi —
  bukan menambal logika mesin.
- **Sebelum "memperbaiki" mesin, baca teks pilihan soalnya.** Sebagian "kegagalan" ternyata
  ekspektasi uji yang salah (mis. soal menanyakan jumlah orang, bukan kalimat). Perbaiki ujinya
  dan catat alasannya di dalam uji.
- Soal yang meminta ANGKA ("berapa orang", "berapa lama") tidak cocok dibaca dari tulisan bebas;
  sediakan pilihan untuk soal jenis itu.

## Kode soal vs kode dimensi
Aturan konsistensi di sumber ditulis dengan kode DIMENSI (`D2`, `D3`), sedangkan jawaban situs
ber-kode SOAL (`D2a`, `D2b`). Generator `bangun_data_situs.py` harus menerjemahkan dimensi → soal
saat membangun data. Kalau tidak, peringatan "perlu ditinjau" tidak akan pernah menyala — dan
tidak ada error apa pun yang menunjukkannya.

## Paritas skor
`kalkulator_kesiapan.py` punya mode `-n <jumlah soal>`. Skor situs WAJIB sama persis dengan
`python3 kalkulator_kesiapan.py -n <jumlah soal> ...` — persen DAN band. Kalau jumlah soal berubah,
tambahkan mode baru di kalkulator dulu, baru ubah situsnya.
