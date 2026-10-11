# SOP UTAMA OMNISENSE — ALUR & PENILAIAN KESIAPAN
Versi 1.0 — satu dokumen otoritatif untuk menjalankan Omnisense.
Omnisense = mitra digitalisasi: konsultasi GRATIS -> menilai kesiapan -> membangun
digitalisasi penuh / AI agent custom (yang berbayar adalah membangun & memasang).

==================================================================
BAGIAN 1 — ALUR OPERASIONAL OMNISENSE (mesin harian)
==================================================================
LANGKAH 1 — LEAD MASUK
- Pintu: landing page + WhatsApp bisnis + IG + rekomendasi.
- Pemilik: CMO. Semua lead dicatat di satu CRM/spreadsheet.

LANGKAH 2 — SELEKSI CEPAT (kualifikasi, 1 menit)
- Pastikan: punya anggaran program + ada pemutus keputusan.
- Kalau "belum mikir budget" = bukan calon sekarang; catat untuk riset.

LANGKAH 3 — SESI PENILAIAN GRATIS (30-60 menit) [gunakan Bagian 2 & 3]
- CEO + CMO memimpin. Hasilkan skor kesiapan % + band (kalkulator_kesiapan.py).

LANGKAH 4 — KIRIM LAPORAN GRATIS (menjual kredibilitas)
- Kirim laporan: skor %, band, gap, langkah pertama (template laporan).
- PEMBEDA: klien dapat nilai sekarang, tanpa bayar.
- Kalau band >=40% & ada minat: TAWARKAN DEEP AUDIT BERBAYAR (32 dalam —
  paket_audit_dalam.md, biaya dikreditkan ke implementasi). Audit berbayar
  mengkualifikasi & menambah revenue (model audit-first).

LANGKAH 5 — PENAWARAN BERBAYAR
- Proposal 3-TIER (templates/proposal_3tier.md): masalah pakai kata klien +
  outcome + 3 paket (tengah = target) + KPI + jaminan. F&B & siap -> paket
  FNBSense; non-F&B / custom -> paket digitalisasi/AI.
- Jual NILAI (untuk jelas, stok aman, hemat waktu), bukan teknologi.
- Kirim kontrak minimal (templates/kontrak_minimal.md) bersama 1-2 paket
  untuk klien yang sudah serius; jangan negosiasi scope via obrolan saja.
- Pemilik: CEO. Proposal <3 hari setelah laporan.

LANGKAH 6 — IMPLEMENTASI & ON-BOARDING
- Ikuti SOP_Onboarding_Klien.md (welcome <24 jam, kickoff 60 menit, folder,
  akses, update mingguan, deliver pertama minggu 1, review hari-30) dan
  SOP_Delivery_Standard.md (baseline, staging, human review gate, go-live,
  48 jam check-in, handoff). Pemilik: CTO.

LANGKAH 7 — DUKUNGAN BERKELANJUTAN
- Ikuti SOP_Retainer_&_Laporan.md: laporan bulanan (template laporan_bulanan.md),
  escalation <24 jam, ekspansi/QBR, skor ulang 3-6 bulan untuk bukti dampak,
  minta referensi. Catat jam dukungan (penggerus margin).

ATURAN LINTAS: setiap tahap punya pemilik & update di CRM. Deadline: seleksi->sesi
<1 mgg; proposal <3 hari setelah laporan; deal <2 mgg sejak sesi.

==================================================================
BAGIAN 2 — SOP SESI PENILAIAN (tata cara menjalankan)
==================================================================
SEBELUM: siapkan kalkulator kesiapan + template penilaian; kuasai Bagian 3.
SELAMA:
  a. PEMBUKA — jalin kepercayaan, pancing kebutuhan (ulangi Q di Bagian 3.A).
  b. ISI 8 DIMENSI — tanyakan pertanyaan kunci, nilai 1-5 (Bagian 3.B).
  c. HITUNG — kalkulator_kesiapan.py -> % + band.
  d. PENUTUP — peringkat masalah, ukur kemauan bayar, ukur kemauan pasang,
     catat keberatan (Bagian 3.C). Jangan menjual; tutup dengan LANGKAH
     BERIKUT TERJADWAL: "Kalau tak ada pertanyaan lagi, saya siapkan
     [rancangan tahap pertama / jadwal bahas penawaran] dan kirim [hari];
     kita bahas [hari + jam]?" Wajib: selalu akhiri dengan tanggal konkret.
SESUDAH: kirim laporan (Langkah 4).

==================================================================
BAGIAN 3 — KEY QUESTIONS PENILAIAN KESIAPAN
(menilai apakah perusahaan SIAP untuk digitalisasi & AI agent)
==================================================================
A. PEMBUKA
 1. Ceritakan bisnis Anda singkat — sejak kapan, berapa orang, berapa cabang?
 2. Bagian operasional mana yang paling menyita perhatian Anda tiap hari?
 3. Kalau ada satu hal yang membuat hari lebih ringan, itu apa?

B. DELAPAN DIMENSI (pertanyaan kunci + cara menilai skor 1-5)
 B1 STRATEGI & KEPEMIMPINAN (bobot 10%)
   Q: Apakah ada visi/arah 1-3 tahun & apakah digital masuk rencana itu?
   1-2: tak ada visi | 3: angan belum tertulis | 4-5: visi jelas + sponsor aktif.
 B2 KESIAPAN DATA (bobot 20% — terpenting)
   Q: Bagaimana pencatatan penjualan, stok, biaya — buku/HP/Excel/sistem?
   Q: Bisa langsung sebut untung bulan lalu secara akurat?
   1-2: data belum digital/tersebar | 3: sebagian digital, tak terpusat |
   4-5: terpusat, akurat, bisa diambil sistem.
 B3 INFRASTRUKTUR & TEKNOLOGI (15%)
   Q: Sistem/perangkat apa yang dipakai? Saling terhubung atau terpisah?
   1-2: tak ada/dasar | 3: sebagian, terpisah | 4-5: terintegrasi.
 B4 DIGITALISASI PROSES (15%)
   Q: Mana yang masih diketik ulang/manual? Ada SOP tertulis yang diikuti semua?
   1-2: serba manual, tak terdokumentasi | 3: campur | 4-5: terotomasi + terstandar.
 B5 ORGANISASI & BUDAYA (10%)
   Q: Bagaimana reaksi tim saat ada cara/alat baru?
   1-2: menolak | 3: netral | 4-5: terbuka.
 B6 SDM & KETERAMPILAN (15%)
   Q: Seberapa nyaman tim pakai aplikasi? Ada yang paham IT/data?
   1-2: literasi rendah | 3: ada dasar | 4-5: ada talent + siap latihan.
 B7 TATA KELOLA, KEAMANAN & KEPATUHAN (10%)
   Q: Data pelanggan/keuangan disimpan di mana? Ada aturan akses/backup?
   1-2: tak ada kebijakan | 3: sebagian | 4-5: ada prosedur.
 B8 ANGGARAN & FINANSIAL (5%)
   Q: Ada anggaran teknologi? Berani invest berapa/bulan? Sifatnya berkelanjutan?
   1-2: tak ada alokasi | 3: terbatas | 4-5: ada & jangka panjang.

C. PENUTUP (arah ke tawaran + ukur kemauan)
 1. Mau bereskan yang mana dulu? (peringkat masalah -> urutan tawaran)
 2. Kalau ada sistem yang merapikan data&stok jadi laporan harian, pantas berapa/bln?
    (ANGKA, jangan dituntun — input pricing)
 3. Kalau bulan ini bisa dipasang, mau? (Ya/Coba/Tidak; kalau tidak: harga? waktu?
    kepercayaan? cara lama cukup?) — catat keberatan.
 4. Nomor WhatsApp/email untuk saya kirim ringkasan.

D. CARA MENILAI "APAKAH SUDAH SIAP AI AGENT"
- Hitung skor: tiap dimensi = rata-rata pertanyaan; kali bobot; jumlah -> /5 -> %.
- BAND & ARTI (membimbing tawaran):
  80-100% SIAP PENUH  -> bisa langsung deploy AI agent / solusi luas.
  60-79%  LAYAK LANJUT -> mulai pilot (pasang FNBSense / 1 use case AI).
  40-59%  KONVENSIONAL -> digitalisasi dasar DULU (data & proses); AI nanti.
  20-39%  AWAL        -> audit data + digitalisasi bertahap; jangan jual AI.
  <20%    SANGAT AWAL -> edukasi + penilaian ulang; jangan tawarkan solusi dulu.
- PRINSIP: JANGAN menjual AI agent ke perusahaan yang datanya belum siap.
  Skor rendah bukan kegagalan — itu peta jalan jujur yang membangun kepercayaan.

==================================================================
BAGIAN 4 — OUTPUT & PERANGKAT
==================================================================
- Kalkulator skor : kalkulator_kesiapan.py (mode inti 8 / lengkap 32 -> %+band).
- Bank pertanyaan : key_questions_client.md (8 inti, free) &
                     key_questions_lengkap.md (32 dalam, audit berbayar).
- Template nilai  : template_skrining.csv (8) / template_penilaian.csv (32).
- Laporan klien   : templates/laporan_eksekutif.md, _lengkap.md, _whatsapp.md,
                    _contoh_terisi.md; laporan bulanan: templates/laporan_bulanan.md.
- Penawaran       : templates/proposal_3tier.md + templates/kontrak_minimal.md.
- Operasional     : paket_audit_dalam.md, SOP_Onboarding_Klien.md,
                    SOP_Delivery_Standard.md, SOP_Retainer_&_Laporan.md.
- Kalkulator margin: kalkulator_harga.py (cek untung tiap client).
- Rujukan metode  : SOP_Kesiapan_Digitalisasi.md, riset_validasi_kesiapan.md,
                    komparasi_alur_ai_agency.md.

==================================================================
GERBANG KELAYAKAN (satu sesi dianggap baik jika)
==================================================================
[ ] Skor 8 dimensi terisi (32 nilai) & %/band dihitung.
[ ] Laporan terkirim ke klien.
[ ] Peringkat masalah, angka mau bayar, & kemauan pasang tercatat.
[ ] Tawaran sesuai band (jangan jual AI ke band rendah).