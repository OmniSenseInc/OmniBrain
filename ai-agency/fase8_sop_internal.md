# FASE 8 — SOP INTERNAL & ALUR PENJUALAN OMNISENSE

Tujuan: tim tahu persis SIAPA mengerjakan APA, dari lead sampai klien bertahan.
Bukan dokumen untuk dipajang — ini rujukan operasional dijalankan tiap hari.

=============================================================
1. PERAN & TANGGUNG JAWAB (3 orang)
=============================================================
- CEO (Vincent): keputusan akhir, deal besar, arah bisnis, klien strategis.
- CTO (Nathanael): semua teknis — FNBSense, custom build, infrastruktur, kualitas.
- CMO (Michael): pemasaran, landing page, WhatsApp/IG, lead in-bound, konten.
- SESI KONSULTASI GRATIS dipimpin CEO & CMO BERSAMA (keputusan tim): CEO menangani
  nilai bisnis & closing, CMO menangani kebutuhan & penyampaian. CTO terlibat bila
  ada pertanyaan teknis (bisa dipanggil, tidak wajib hadir tiap sesi).

TAHAPAN & PEMILIK (siapa paling bertanggung jawab):
| Langkah (dari omnisense_ops A)        | Pemilik utama |
|---------------------------------------|---------------|
| 1 Lead masuk                          | CMO          |
| 2 Seleksi cepat (kualifikasi)         | CMO (+CEO utk besar) |
| 3 Sesi konsultasi gratis              | CEO & CMO (bersama) |
| 4 Laporan pasca-konsultasi (kirim)    | CEO          |
| 5 Proposal berbayar / deal            | CEO          |
| 6 Implementasi & on-boarding          | CTO          |
| 7 Dukungan & margin bulanan           | CTO (teknis), CEO (nilai) |

=============================================================
2. PIPELINE PENJUALAN (stage + kelulusan)
=============================================================
P1. Lead baru — masuk, belum dikualifikasi.
P2. Terkualifikasi — lolos seleksi cepat (anggaran + pemutus keputusan ada).
P3. Konsultasi jalan — sesi gratis selesai, skor+band tercatat.
P4. Laporan terkirim — klien menerima skor+gap+roadmap.
P5. Proposal terkirim — penawaran (FNBSense / custom) + harga.
P6. Menang — klien setuju; masuk on-boarding.
P7. Aktif — terpasang, bayar, dipakai.
P8. Bertahan — berjalan bulanan; target churn rendah.

ATURAN:
- Jangan lompati P5 ke P7 tanpa "menang" (P6) yang jelas.
- Setiap stage punya pemilik (tabel di atas) & catatan terbaru di CRM/spreadsheet.
- Deadline: P2->P3 < 1 minggu; P5 kirim < 3 hari setelah P4; P6 < 2 minggu sejak P3.

=============================================================
3. SOP SESI KONSULTASI GRATIS (standar pelaksanaan)
=============================================================
SEBELUM:
- Siapkan akun/nomor konsultasi, siapkan kalkulator kesiapan, template penilaian.
- Baca: framework (SOP_Kesiapan_Digitalisasi.md) + template_penilaian.csv.
- Kuasai BANK PERTANYAAN KUNCI CLIENT: key_questions_client.md (acuan sesi; jangan
  dibaca kaku seperti daftar hafalan).
SELAMA (30-60 menit):
- (a) PEMBUKA: jalin kepercayaan, pancing kebutuhan (key_questions bagian A).
- (b) ISI 8 DIMENSI: tanyakan key questions per dimensi (bagian B1-B8) dan nilai
  1-5 (template_penilaian.csv). Jangan tuntun; catat apa adanya.
- (c) Hitung skor + band via kalkulator_kesiapan.py.
- (d) PENUTUP: peringkat masalah, ukur angka mau bayar, ukur kemauan pasang,
  catat keberatan (bagian C). Jangan menjual di sesi ini; tutup dengan "akan saya
  kirim ringkasan + langkah pertama".
SESUDAH:
- Langkah 4 Omnisense: kirim laporan skor+gap+roadmap (template, lihat bagian 5).

=============================================================
4. SOP ON-BOARDING KLIEN (setelah "menang")
=============================================================
1. Tinjau kontrak/proposal & tandai scope. (CEO)
2. Setup teknis: deploy/pasang, isi data awal, jag file/config per client. (CTO)
3. Pelatihan: pemilik & yang memakai (kasir dst) — cara input, cara lihat laporan. (CTO/CEO)
4. Hipercare minggu pertama: pantau harian, komentar cepat, perbaiki bug. (CTO)
5. Tagih: pastikan invoice & alur bayar (template 250k dst) jalan. (CEO & CMO)
6. Catat di CRM: kontak, stage, biaya, catatan dukungan (untuk cek margin). (semua)

=============================================================
5. TEMPLATE YANG PERLU DIISI (belum ada) — prioritas
- Template laporan pasca-konsultasi (skor % + band + gap + langkah pertama). [PALING GUN]
- Template proposal/kontrak (scope, harga, jadwal, hypercare, dukungan).
- Track margin bulanan (pakai kalkulator_harga.py; isi jam dukungan riil).

=============================================================
6. ATURAN TEAM & TOOLS
- Satu tempat kebenaran (CRM/spreadsheet) untuk lead, stage, biaya — WAJIB diupdate
  supaya tahap (P2..P8) selalu jujur. Jangan simpan requirement hanya diobrolan.
- Komitmen waktu 2-5 jam/hari: alokasikan —X jam untuk "operasional menjual" (A1-A3)
  dan sisanya untuk "membangun" (FNBSense/teknis). Keputusan di awal minggu.
- Setiap minggu (pekanan 15-30 menit): 3 angka — berapa lead, berapa konsultasi,
  berapa deal. Kalau salah satu macet, fokus di situ.

## GERBANG FASE 8 (lolos hanya jika)
[ ] Peran & pemilik tiap tahap disepakati (tabel 1).
[ ] Pipeline (P1..P8) dipakai & stage diupdate di CRM.
[ ] SOP konsultasi gratis standar (3) + on-boarding (4) dipakai.
[ ] Template laporan pasca-konsultasi & proposal tersedia (atau dalam pembuatan).