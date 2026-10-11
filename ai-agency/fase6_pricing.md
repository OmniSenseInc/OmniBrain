# FASE 6 — PRICING & PAKET (berbayar tidak menempel biaya)

Prinsip inti (yang harus dipegang): HARGA DITENTUKAN OLEH NILAI UNTUK KLIEN, BUKAN
DARI BIAYAMU. Kalau harga = biaya (250k ≈ VPS+API), maka kalian tidak punya laba,
tidak bisa bayar waktu tim, tidak bisa scale. Margin itu yang menghidupi OmniSense.

## 0. KERANGKA BERPIKIR
Harga > Biaya (harus, supaya ada laba)
Harga <= Nilai yang dirasakan klien (supaya mereka mau bayar)
-> target sehat: harga 2-4x biaya langsung, atau berdasar nilai (bukan duplikasi).

## 1. BIAYA RIIL (diperbarui — angka dari tim)
Per client FNBSense:
- VPS: Rp 60.000/bulan (biaya tetap).
- API key (opencode): Rp 89.000/bulan PER AKUN. Satu akun bisa dipakai 2-3 client
  (pooling), sehingga biaya API riil per client bisa DI BAWAH 89k.
- Template (sekali, bulan pertama): Rp 250.000 (murni margin).
- Tarif bulanan FNBSense: Rp 250.000.
- HITUNGAN: biaya langsung 60k + 89k = 149k/bulan; tagihan 250k -> margin +-101k/bln
  per client (68%), PLUS template 250k saat pertama. -> POSITIF, bukan rugi.

CATATAN RISIKO MARGIN (yang sesungguhnya bisa menggerus):
- WAKTU DUKUNGAN adalah biaya tersembunyi terbesar. Jika tiap client menghabiskan
  bahkan 1 jam/bulan dukungan & on-boarding (tarif +- Rp 60k/jam), biaya jadi
  209k -> margin tinggal +- 41k/bulan. Tim hanya 2-5 jam/hari untuk SEMUA client;
  waktu ini menumpuk SEIRING jumlah client, lebih cepat dari pendapatan. Hitung
  jam dukungan riil di kalkulator_harga.py.
- POOLING API (1 akun utk 2-3 client) memang hemat, tapi konsentrasi risiko:
  kalau 1 akun opencode kena rate-limit/gagal, SEMUA client di akun itu terdampak.
  Jangan jadikan pooling satu-satunya penyangga; pertimbangkan cadangan/redundansi.

## 2. TIGA TINGKAT PAKET (proposal; validasi dgn Fase 5 nanti)
### Paket GRATIS (produk assessment) — pintu masuk / lead magnet
- Konsultasi & skor kesiapan 8-dimensi (framework kita) + rekomendasi "mulai dari mana".
- Tujuan: trust, data client, menemukan kebutuhan -> bukan untuk uang.

### FNBSense (produk, langganan bulanan)
- Starter  (1 outlet):  Rp _______/bln  (minimal di atas biaya + margin)
- Growth   (2-3 outlet): Rp _______/bln
- Multi    (4+ outlet / franchise): Rp _______/bln (custom)

### OmniSense Build & Consulting (custom, tiket lebih besar)
- Assessment mendalam + roadmap (bekas gratis, upgrade berbayar) : Rp _______
- Implementasi digitalisasi / custom AI agent : biaya sekali ________ + langganan

## 3. CARA MENENTUKAN ANGKA (jangan tebak) — 2 jalur
Jalur A (cost+margin, minimum aman):
  harga = biaya_total x (2-4x). Pastikan menutup biaya + waktu tim + margin.
Jalur B (value-based, lebih tinggi):
  nilai jam terselamatkan: mis. rekap manual 1-2 jam/hari x 25 hari x Rp 30-50rb
  (value operator) = Rp 750rb - 2,5jt/bln POTENSI NILAI. Hanya perlu ambil sebagian
  kecil dari nilai itu sbg harga. => Harga pantas di atas cost dengan leluasa.
  + mencegah kerugian stok (borong/buang) -> nilai tambah yang bisa masuk pitch.

-> HARGA PANTAS arahnya JAUH di atas 250k cost. Jangan kunci di 250k.

## 4. CONTOH ARAH (belum divalidasi; ganti dengan data kalian)
- Starter 1 outlet: Rp 500k-800k/bln (2-3x cost). Nilai argumen: jelas untung-rugi,
  hemat 1-2 jam/hari pemilik, stok aman.
- Growth: Rp 1,2-1,8jt/bln.
- Custom build: mulai Rp 5-25jt (sekali) + langganan sesuai kompleksitas.
(Catatan: angka ini HYPOTHESIS. Pengunci sebenarnya = Fase 5, yang kau skip; jadi
saat nanti kamu lakukan wawancara, ambil angka "mau bayar berapa" sebagai pengikat.)

## 5. ATURAN
- SELALU jual nilai, bukan fitur/tech. Nomor urut: untung jelas, stok aman, hemat waktu.
- Jangan diskon besar-besaran di awal; itu menurunkan nilai.
- Satu kali setting/setup (template FNBSense) bisa dipisah (biaya sekali) dari langganan.
- Perbaiki narasi: bukan "global untuk semua F&B" (agar tidak kewalahan) — tutup sebagai
  paket yang bisa naik kelas seiring pertumbuhan klien.

## 6. GERBANG FASE 6 (lolos hanya jika)
[ ] Harga tiap paket TERTULIS (bukan custom misteri).
[ ] Harga > biaya (margin positif) — cek kalkulator_harga.py.
[ ] Ada paket gratis (pintu masuk).
[ ] Narasi jual memakai nilai (untung/stok/waktu), bukan teknologi.
- (opsional tapi kuat) Angka harga mengacu nilai yang akan diambil dari Fase 5 nanti.