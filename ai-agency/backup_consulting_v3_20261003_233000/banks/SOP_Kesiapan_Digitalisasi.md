# SOP PENILAIAN KESIAPAN DIGITALISASI & AI AGENT
### Dokumen Standar — [Nama Agency]
Versi 1.0

---

## 1. TUJUAN

Menilai secara objektif tingkat kesiapan (readiness) sebuah bisnis customer untuk
memasuki program digitalisasi berbantuan AI agent. Hasilnya berupa:

1. Skor kesiapan persentase (0–100%).
2. Segmen kesiapan (band).
3. Rekomendasi roadmap yang spesifik per dimensi.
4. Bahan dasar proposal & negosiasi scope proyek.

Prinsip: JANGAN menjual solusi AI sebelum kesiapan dasar terpenuhi. Ini melindungi
customer dari proyek gagal, sekaligus melindungi reputasi agency.

---

## 2. WAKTU & PELAKSANAAN

| Item              | Keterangan                              |
|-------------------|-----------------------------------------|
| Durasi assessment | 90–150 menit (workshop/depth interview) |
| Peserta          | Founder/Direktur, kepala operasional, kepala IT, perwakilan tim operasional |
| Metode           | Kuesioner terpandu + observasi langsung + cek dokumen |
| Elemen            | 8 dimensi x 3–4 pertanyaan berskala 1–5 |

---

## 3. DELAPAN DIMENSI PENILAIAN

Setiap dimensi punya bobot. Bobot mencerminkan seberapa berpengaruh dimensi itu
terhadap keberhasilan adopsi AI agent.

| No | Dimensi                              | Bobot |
|----|--------------------------------------|-------|
| 1  | Strategi & Kepemimpinan              | 10%   |
| 2  | Kesiapan Data                        | 20%   |
| 3  | Infrastruktur & Teknologi            | 15%   |
| 4  | Digitalisasi Proses                  | 15%   |
| 5  | Organisasi & Budaya                  | 10%   |
| 6  | SDM & Keterampilan                   | 15%   |
| 7  | Tata Kelola, Keamanan & Kepatuhan    | 10%   |
| 8  | Anggaran & Finansial                 | 5%   |
|    | **Total**                            | **100%** |

SKALA SKOR per pertanyaan: 1 (buruk/tidak ada) s.d. 5 (sangat baik/terpenuhi penuh).

---

### 3.1 STATEGI & KEPEMIMPINAN (10%)
Apakah arah digitalisasi didorong dari puncak.
- Q1. Kejelasan visi digital dari pemimpin.
- Q2. Ada pemimpin/pihak yang menjadi sponsor & pendorong (champion) AI.
- Q3. Strategi digitalisasi tertulis & dikomunikasikan ke tim.
- Q4. Ekspektasi pemimpin realistis terhadap hasil AI (bukan "magic").

### 3.2 KESIAPAN DATA (20%) — bobot tertinggi, pembeda sukses/gagal
- Q1. Sejauh mana data operasional sudah digital (vs kertas/ingatan/Excel acak).
- Q2. Kualitas data: akurat, lengkap, konsisten, terpusat.
- Q3. Data terstruktur & bisa diakses sistem (database, API) untuk diolah.
- Q4. Ada tata kelola data: siapa pemilik data, standar penamaan, backup.

### 3.3 INFRASTRUKTUR & TEKNOLOGI (15%)
- Q1. Sudah ada sistem inti (ERP, CRM, POS, aplikasi manajemen).
- Q2. Tingkat integrasi antar sistem (API/otomatis vs manual export-import).
- Q3. Konektivitas & basis cloud (koneksi stabil, data tersimpan terpusat).
- Q4. Perangkat keras memadai (komputer, jaringan, hardware pendukung).

### 3.4 DIGITALISASI PROSES (15%)
- Q1. Proporsi proses bisnis yang sudah otomatis (tidak manual/ketik ulang).
- Q2. SOP proses terdokumentasi dengan jelas.
- Q3. Tingkat standardisasi (setiap orang mengerjakan dengan cara sama).
- Q4. Kecocokan antara proses saat ini dan cara kerja AI agent.

### 3.5 ORGANISASI & BUDAYA (10%)
- Q1. Keterbukaan tim terhadap perubahan & teknologi baru.
- Q2. Tingkat adopsi alat digital baru oleh karyawan sejauh ini.
- Q3. Tingkat resistensi/penolakan terhadap perubahan.
- Q4. Komunikasi internal dalam mengelola perubahan.

### 3.6 SDM & KETERAMPILAN (15%)
- Q1. Literasi digital karyawan secara umum.
- Q2. Ada talent/personel teknis (IT, data, automasi) internal atau terencana.
- Q3. Kemampuan & rencana pelatihan (reskilling) tim.
- Q4. Kapasitas tim untuk menjalankan & memelihara solusi AI.

### 3.7 TATA KELOLA, KEAMANAN & KEPATUHAN (10%)
- Q1. Kebijakan IT & keamanan siber dasar ada.
- Q2. Pengelolaan & perlindungan data pelanggan (kesesuaian UU PDP Indonesia).
- Q3. Kontrol akses & prosedur jika ada insiden.
- Q4. Kesiapan mengelola vendor/penyedia teknologi eksternal.

### 3.8 ANGGARAN & FINANSIAL (5%)
- Q1. Ada alokasi anggaran khusus IT/digitalisasi.
- Q2. Kejelasan ekspektasi ROI & target biaya.
- Q3. Keberlanjutan keputusan investasi (bukan proyek sekali jalan).
- Q4. Kapasitas membayar langganan (subscription) / biaya operasional AI lanjutan.

---

## 4. PERHITUNGAN SKOR

1. Setiap pertanyaan diberi nilai 1–5.
2. Skor dimensi = rata-rata nilai pertanyaan dalam dimensi tersebut (rentang 1–5).
3. Skor tertimbang dimensi = skor dimensi x bobot.
4. Skor total = jumlah seluruh skor tertimbang, lalu dinormalisasi ke 0–100%:

   Percent = (SkorTotal / 5) x 100%

Contoh ringkas:
- Dimensi Data: rata-rata 3.0, bobot 20% → 3.0 x 0.20 = 0.60
- Dimensi Proses: rata-rata 2.5, bobot 15% → 2.5 x 0.15 = 0.375
- dst. SkorTotal = jumlah, Percent = (SkorTotal/5) x 100%.

---

## 5. SEGMEN KESIAPAN (BAND) & REKOMENDASI

| Skor        | Band            | Arti                                        | Rekomendasi |
|-------------|-----------------|---------------------------------------------|-------------|
| 80–100%     | Siap Penuh      | Fondasi lengkap, siap implementasi luas     | Lanjut Proof-of-Concept besar → full deployment multi AI agent |
| 60–79%      | Layak Lanjut    | Layak mulai, ada gap yang bisa diatasi      | Mulai pilot AI agent (1 proses), perbaiki gap paralel |
| 40–59%      | Konvensional    | Digitalisasi dasar belum merata             | Fokus digitalisasi/fondasi dulu; AI sebagai tahap lanjutan |
| 20–39%      | Awal            | Masih banyak manual & data belum terpusat   | Sesuaikan ekspektasi; tawarkan audit data & digitalisasi bertahap |
| <20%        | Sangat Awal     | Fondasi belum ada                            | Edukasi & assessment ulang; jangan jual solusi AI dulu |

---

## 6. OUTPUT YANG WAJIB DIKIRIM KE CUSTOMER

1. Ringkasan eksekutif: skor total % + band.
2. Radar/heatmap per dimensi (visualkan kekuatan & kelemahan).
3. Gap analysis: dimensi dengan skor terendah.
4. Rekomendasi roadmap bertahap (30/60/90 hari dst).
5. Rupiah/scope indikatif berdasarkan band.
6. Catatan asumsi & data apa yang diobservasi langsung.

Ini juga jadi modal proposal: tunjukkan bahwa rekomendasi berdasar data, bukan
menjual "magic AI".

---

## 7. ETIKA & LIMITASI

- Skor adalah titik awal diskusi, bukan penilaian harga diri customer.
- Kejujuran itu penting: hasil rendah bukan kegagalan, tapi peta jalan.
- Data yang dikumpulkan bersifat rahasia klien; wajib dijaga.
- Assessment tidak menjamin proyek sukses; tetap ada risiko implementasi.

---

## 8. TEMPLATE / TOOLS PENDUKUNG

Gunakan kalkulator di file `kalkulator_kesiapan.py` (CLI) untuk hitung otomatis,
dan `template_penilaian.csv` untuk pengumpulan data lapangan.