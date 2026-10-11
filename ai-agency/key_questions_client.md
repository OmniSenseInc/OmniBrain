# 8 PERTANYAAN INTI — SKRINING FREE KONSULTASI (OmniSense)

> ⚠️ **MODE LEGACY (per 3 Okt 2026).** Untuk sesi BARU pakai `consulting/pertanyaan_v3.json`
> + `consulting/PLAYBOOK_KONSULTAN.md`. Bank ini tetap sebagai rujukan sejarah; **angka skor
> historis tidak diubah**. Dua hal yang TIDAK berlaku lagi di v3: (1) "tidak tahu" diperlakukan
> sebagai skor rendah/netral — di v3 itu **unknown (null)**; (2) klaim "tervalidasi" — ini
> triangulasi literatur, **bukan** validasi empiris.
Satu pertanyaan per dimensi, langsung ke inti, selesai ~10 menit.
Untuk fase dalam (32 pertanyaan) pakai key_questions_lengkap.md + kalkulator mode lengkap.
Dasar validasi: riset_validasi_kesiapan.md.

=============================================================
ATURAN (ringkas)
=============================================================
- Tanya SATU per satu. Minta BUKTI/angka, jangan percaya klaim "sudah/biasanya".
- Jawaban samar -> probe sekali; tak bisa jawab = fakta (skor rendah).
- Skor 1-5 sesuai anchor. Ragu -> pilih lebih rendah.
- HARGA/closing urusan tim; bot tutup dengan P3 ("ada yang ingin ditanyakan?")
  lalu ajukan langkah berikut terjadwal (tanggal konkret).

=============================================================
8 PERTANYAAN INTI (urutan = urutan nilai kalkulator mode inti)
=============================================================
1. STRATEGI — "Apa target bisnis 1-3 tahun ke depan, dan kenapa mau digitalisasi?
   Sebut angka atau masalah konkretnya."
   Skor: 5=target terukur+masalah nyata | 3=angan-angan | 1=ikut tren saja.

2. DATA — "Berapa persis untung bersih bulan lalu? Langsung bisa jawab?"
   Skor: 5=angka akurat seketika | 3=hitung dulu | 1=tidak tahu/ngasal.

3. INFRASTRUKTUR — "Pakai aplikasi/sistem operasional apa sekarang (kasir, stok)?
   Internet stabil berapa jam sehari?"
   Skor: 5=ada sistem inti+stabil | 3=sebagian/fluktuatif | 1=manual+rapuh.

4. PROSES — "Ada SOP tertulis yang semua orang ikuti? Bagian mana yang paling
   manual & makan waktu?"
   Skor: 5=SOP seragam+mayoritas otomatis | 3=setengah | 1=verbal/ingatan.

5. BUDAYA — "Terakhir kali diperkenalkan cara/alat baru, reaksinya? Pemilik mau
   mengubah cara lama?"
   Skor: 5=contoh adopsi cepat+pemilik memimpin | 3=netral | 1=ada penolakan.

6. SDM — "Dari [jumlah] orang, berapa yang lancar pakai perangkat digital, dan
   SIAPA yang siap belajar duluan?"
   Skor: 5=sebagian besar+siap belajar | 3=sebagian | 1=hampir tidak ada.

7. TATA KELOLA — "Data pelanggan & uang disimpan di mana, siapa yang bisa akses,
   dan kalau HP hilang besok data aman?"
   Skor: 5=kontrol akses+backup rutin | 3=informal | 1=tanpa perlindungan.

8. ANGGARAN — "Berapa NOMINAL yang siap dialokasikan per bulan untuk teknologi?"
   Skor: 5=angka jelas berkelanjutan | 3=ragu/kecil | 1=tidak ada.

=============================================================
ALUR
=============================================================
1. Konteks singkat (S) dulu: bisnis apa, sejak kapan, berapa orang/omzet—maks 2 tanya.
2. 8 pertanyaan inti di atas (1-5 tiap dimensi).
3. Hitung: kalkulator_kesiapan.py -n <8 nilai> -> % + band -> laporan ringkas.
4. Tutup P3 + NEXT STEP: "Ada yang ingin Anda tanyakan lebih dulu?" -> lalu
   jadwalkan langkah berikut konkret ("saya siapkan rancangan tahap pertama,
   kirim [hari], kita bahas [hari&jam]?"). Harga & closing = tim.
5. Catat skor ke template_skrining.csv; kalau client lanjut ke penawaran, baru
   deep-dive 32 (key_questions_lengkap.md) untuk laporan final.