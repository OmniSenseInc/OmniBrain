# BANK PERTANYAAN KESIAPAN v2 — TERVALIDASI RISET (OmniSense)
32 pertanyaan (8 dimensi x 4), urutan sama dgn kalkulator_kesiapan.py & template_penilaian.csv.
Dasar validasi: riset_validasi_kesiapan.md (Forrester, Gartner, Cisco, MITRE, KPMG,
Kyndryl, Accenture, Protiviti, PwC, UST, BRIN, MDPI, studi POS kafe, DHRQ).

=============================================================
ATURAN ANTI-HALUSINASI (baca sebelum mulai)
=============================================================
1. Setiap jawaban harus FAKTA terverifikasi: angka, nama, contoh kejadian terakhir.
2. "Sudah / sering / biasanya" tanpa contoh = BELUM fakta. Minta: "Contoh terakhirnya?"
3. Jangan menuntun skor. Jangan percaya klaim — minta BUKTI (riset: klaim kesiapan
   sering berlebihan).
4. Klien tidak bisa jawab = fakta juga (belum ada) -> skor rendah, bukan dilewati.
5. Bedakan "rencana/mau" vs "sudah jalan". Skor 4-5 HANYA utk yang SUDAH jalan.
6. Kesediaan belajar (learnability) lebih menentukan dari skill saat ini (DHRQ).
7. Satu pertanyaan per pesan (format bot); catat kata persis klien di kolom catatan.

=============================================================
A. KONTEKS BISNIS (pembuka — jangan nilai sebelum ini jelas)
=============================================================
1. Bidang bisnis? (produk/jasa 3 teratas)  2. Berjalan sejak kapan?
3. Berapa total orang (sebut peran)?      4. Cabang/outlet berapa?
5. Transaksi per hari & omzet per bulan (angkanya)?
6. Jam operasional?                       7. Siapa pemutus keputusan sehari-hari?

=============================================================
B. 32 PERTANYAAN VALID (skor 1-5; anchor: 1=buruk/tak ada, 3=sebagian/klaim
tanpa bukti, 5=terbukti jalan & terstruktur)
=============================================================

---- B1. STRATEGI & KEPEMIMPINAN (10%) ----
Q1. "Apa target bisnis 1-3 tahun ke depan? Sebut angkanya."
  Verifikasi: "Target itu tertulis & dibagikan ke tim, atau di kepala?"
  Skor: 5=tertulis+terukur+disampaikan | 3=angan-angan | 1=tidak ada arah.
Q2. "Kenapa mau digitalisasi SEKARANG? Masalah bisnis konkret apa?"
  Verifikasi: "Masalah itu bisa dijelaskan dampak rupiahnya?"
  Skor: 5=masalah nyata+berdampak rupiah | 3=sadar tapi samar | 1=ikut tren saja.
Q3. "Kalau berhasil digital, SATU hal yang paling ingin berubah apa?"
  Verifikasi: "Mengapa hal itu yang paling penting?"
  Skor: 5=use case spesifik bernilai | 3=umum ("biar rapi") | 1=tidak bisa menyebut.
Q4. "Waktu & keputusan pemilik untuk proyek ini bagaimana? Ada jadwal rutin?"
  Verifikasi: bukti keputusan terakhir soal teknologi.
  Skor: 5=sponsor aktif+akuntabel | 3=dukung di mulut | 1=titip/lepas tangan.

---- B2. KESIAPAN DATA (20% — bobot tertinggi) ----
Q5. "Transaksi dicatat di mana — buku, HP, Excel, atau sistem? Alurnya sampai jadi
    angka bagaimana?"
  Skor: 5=sistem/terpusat | 3=sebagian digital terpisah | 1=buku/ingatan.
Q6. "Berapa persis untung bersih bulan lalu?"
  Verifikasi: langsung jawab? minta hitung? bisakah bukti?
  Skor: 5=angka akurat seketika | 3=bisa tapi dihitung dulu | 1=tidak tahu.
Q7. "Kalau saya minta rekap penjualan 3 bulan, berapa lama siapnya?"
  Skor: 5=menit-jam otomatis | 3=1-3 hari manual | 1=berminggu/tidak bisa.
Q8. "Laporan bisa dibuat SENDIRI tanpa bantuan orang lain? Siapa input data, rutin
    berapa kali seminggu?"
  Skor: 5=mandiri+rutin terjadwal | 3=tergantung orang tertentu | 1=tidak bisa.

---- B3. INFRASTRUKTUR & TEKNOLOGI (15%) ----
Q9. "Aplikasi/perangkat operasional yang dipakai SEKARANG namanya apa? (kasir,
    stok, akuntansi)"
  Skor: 5=ada sistem inti (POS/ERP/CRM) | 3=sebagian | 1=tidak ada, HP+buku.
Q10. "Alat-alat itu terhubung otomatis, atau tiap bagian input ulang?"
  Skor: 5=terintegrasi | 3=sebagian ekspor-impor manual | 1=serba manual.
Q11. "Internet di tempat usaha stabil berapa jam sehari? Pernah transaksi gagal
     karena jaringan?"
  Skor: 5=stabil+ada cadangan | 3=fluktuatif | 1=sering putus/gagal.
Q12. "Kalau listrik mati 2 jam, bisnis masih jalan normal?"
  Skor: 5=ada cadangan daya | 3=terganggu sebagian | 1=lumpuh.

---- B4. DIGITALISASI PROSES (15%) ----
Q13. "Ada SOP tertulis? Semua orang ikut atau caranya masing-masing?"
  Skor: 5=SOP terdokumentasi+seragam | 3=ada sebagian | 1=verbal/ingatan.
Q14. "Proses mana yang paling makan waktu & masih manual? Sebut."
  Verifikasi: frekuensi & dampak (berapa jam/minggu).
  Skor: 5=mayoritas otomatis | 3=setengah-setengah | 1=serba manual.
Q15. "Siapa yang paling hafal jalan bisnis? Kalau orang itu cuti, pelayanan
     berubah?" (single-point-of-failure = target awal AI agent)
  Skor: 5=berjalan tanpa satu orang | 3=tergantung | 1=lumpuh tanpa dia.
Q16. "Stok/persediaan dicatat bagaimana? Akuratnya berapa persen kira-kira?"
  Skor: 5=real-time akurat | 3=kadang sesuai | 1=tidak tahu/kosong.

---- B5. ORGANISASI & BUDAYA (10%) ----
Q17. "Terakhir kali tim dikenalkan cara/alat baru, reaksinya? Contoh kejadiannya?"
  Skor: 5=contoh adopsi cepat | 3=netral | 1=ada penolakan nyata.
Q18. "Berapa lama tim terbiasa dengan perubahan seperti itu?"
  Skor: 5=hari | 3=minggu | 1=bulanan/menolak.
Q19. "Pemilik mau mengubah cara lama? Secepat apa keputusan mencoba hal baru?"
  Skor: 5=pemilik memimpin perubahan | 3=mau tapi pelan | 1=keras cara lama.
Q20. "Kalau ada karyawan menolak sistem baru, apa yang pemilik lakukan?"
  Skor: 5=dampingi+bicarakan | 3=memaksa/cuek | 1=mundur/membatalkan.

---- B6. SDM & KETERAMPILAN (15% — riset: workforce hambatan terbesar) ----
Q21. "Dari [jumlah] orang, berapa yang lancar pakai HP/catatan digital? Sebut siapa."
  Skor: 5=sebagian besar | 3=beberapa | 1=nyaris semua tidak.
Q22. "Kalau dipasang sistem baru, SIAPA yang siap belajar duluan?" (learnability)
  Skor: 5=ada orang jelas mau | 3=mungkin | 1=tidak ada.
Q23. "Pernah ada pelatihan / waktu khusus belajar teknologi?"
  Skor: 5=rutin terencana | 3=pernah sekali | 1=tidak pernah.
Q24. "Siapa yang bisa baca & mengerti laporan keuangan/penjualan?"
  Skor: 5=beberapa orang | 3=hanya pemilik | 1=tidak ada.

---- B7. TATA KELOLA, KEAMANAN & KEPATUHAN (10%) ----
Q25. "Data pelanggan & keuangan disimpan di mana? Siapa saja yang bisa akses?"
  Skor: 5=kontrol akses jelas | 3=informal | 1=terbuka/sembarangan.
Q26. "Kalau HP/komputer hilang besok, data masih aman?"
  Skor: 5=backup rutin otomatis | 3=copy kadang | 1=ikut hilang.
Q27. "Kalau sistem salah hitung/rugi, siapa yang bertanggung jawab & prosedurnya?"
  Skor: 5=prosedur & human-in-the-loop | 3=baru kalau terjadi | 1=tidak ada.
Q28. "Password/keamanan akun gimana (berbagi akun?) & paham aturan data (UU PDP)?"
  Skor: 5=akun terkelola+kepatuhan | 3=sebagian | 1=berbagi akun/sembarangan.

---- B8. ANGGARAN & FINANSIAL (5%) ----
Q29. "Berapa NOMINAL yang bisa dialokasikan per bulan untuk teknologi? Angkanya."
  Skor: 5=angka jelas memadai | 3=ragu/kecil | 1=tidak ada.
Q30. "Angka itu sekali jalan atau berkelanjutan tiap bulan?"
  Skor: 5=berkelanjutan | 3=belum pasti | 1=sekali jalan.
Q31. "Pernah menghitung berapa yang HILANG karena manual — salah catat, stok
     basi, lembur?" (visibilitas biaya = 5x ROI)
  Skor: 5=pernah hitung angka | 3=minus dasar | 1=belum pernah.
Q32. "Riwayat belanja teknologi: pernah bayar aplikasi/jasa digital? Sebut."
  Skor: 5=rutin berlangganan | 3=pernah | 1=belum pernah bayar.

=============================================================
C. PENUTUP (prioritas + kemauan; HARGA = urusan tim)
=============================================================
1. "Masalah mana yang PALING ingin dibereskan duluan?" (paksa peringkat).
2. "Kalau ada solusi yang cocok, apa syarat utama agar Anda mau lanjut?"
3. "Ada yang ingin Anda tanyakan lebih dulu?" (P3) -> tim menindaklanjuti.
4. Verifikasi kontak: "Nomor WhatsApp/email untuk kirim laporan?"

=============================================================
D. DISIPLIN SKORING (wajib setelah sesi)
=============================================================
1. Isi 32 nilai ke template_penilaian.csv HANYA dari fakta; tanpa fakta = "?" +
   skor netral 3 + catatan "belum terverifikasi".
2. Jalankan kalkulator_kesiapan.py (bobot: Data 20, Infra 15, Proses 15, SDM 15,
   Strategi 10, Budaya 10, Tata kelola 10, Anggaran 5) -> % + band -> laporan.
3. Ragu antara dua skor -> pilih LEBIH RENDAH. Tulis kata persis klien sebagai bukti.