# BACKTEST CHECKLIST — ALUR OMNISENSE HULU→HILIR (Dry-Run Sebelum Beta)
Tujuan: uji seluruh alur lead→support dengan SIMULASI sebelum klien nyata, supaya
blok ketahuan lebih dulu. Status: [✓ siap] [⚠️ gap/butuh] [☐ belum].

Cara pakai: jalankan sekali penuh pakai data dummy/scenario, tandai tiap item,
lalu ambil keputusan di bagian GATE. Item status ⚠️/☐ tanpa bahan harus dibereskan dulu.

=============================================================
A. FONDASI — BRAND & PRODUK
=============================================================
[✓] Positioning 1 kalimat final (F4) + slogan "Where Traditional Systems end, AI Agents Begin."
[✓] Visi, misi, nilai final (F3).
[✓] Sketch: model = konsultasi GRATIS -> penilaian -> bangun & pasang (berbayar).
[⚠️] Harga paket FINAL (F6): Starter/Growth/Multi + OmniSense Build masih kosong angkanya.
     Butuh angka riil biaya tim + "mau bayar berapa" dari validasi/beta.
[⚠️] Scope MVP FNBSense (F7) terkunci, tapi BUILD belum selesai (progress ~90%, CTO).
[☐] Template PROPOSAL & KONTRAK klien (belum dibuat) — wajib untuk langkah 5.

=============================================================
B. INFRASTRUKTUR BOT & KANAL
=============================================================
[✓] Bot WhatsApp konsultan LIVE (Baileys), bisa menerima pesan.
[⚠️] Alur client baru: "bikin grup konsultasi = whitelist" — SOP belum dirapikan
     (dokumen lama masih nyebut /whitelist yang tidak ada). UJI: buat grup percobaan
     berisi bot + tester, pastikan bot merespons saat ditag.
[✓] Guardrail TEMBOK tim-vs-client aktif (no pricing, no data internal, no cross-client).
[☐] Landing page / halaman kontak + WhatsApp bisnis + IG aktif. (F10 — belum)
[☐] CRM / satu spreadsheet pipeline (P1-P8) — belum ada.

=============================================================
C. ALAT ASSESSMENT
=============================================================
[✓] Framework kesiapan 8 dimensi + bobot (SOP_Kesiapan_Digitalisasi.md).
[✓] kalkulator_kesiapan.py — UJI: input 32 nilai dummy, pastikan % + band benar.
[✓] template_penilaian.csv (32 nilai 1-5) siap diisi.
[✓] key_questions_client.md (anti-halusinasi, sudah di-upgrade).
[✓] template laporan klien: eksekutif / lengkap / WA / contoh terisi (templates/).

=============================================================
D. BACKTEST ALUR 7 LANGKAH (simulasi penuh, data dummy)
=============================================================
L1. LEAD MASUK
[✓] Ada pintu masuk (rencana: landing + WA bisnis + IG).
[⚠️] Standar "siapa catat lead & jawab" jelas — belum ada CRM fisik.
L2. SELEKSI CEPAT
[✓] Kriteria jelas: punya anggaran + ada pemutus keputusan.
L3. SESI KONSULTASI GRATIS (30-60 mnt)
[✓] Bot & tim kuasai alur pembuka -> 8 dimensi -> skor -> penutup.
[✓] Disiplin anti-halusinasi: skor cuma dari fakta; jawaban samar -> probe/mark.
[✓] kalkulator skor jalan.
L4. LAPORAN PASCA-KONSULTASI
[✓] Template siap; isi: skor %, band, 2-3 kuat, 2-3 gap, langkah pertama.
[✓] Bisa dikirim lewat WA bisnis/bot.
L5. PROPOSAL & HARGA
[⚠️] Harga final belum terisi (lih. A).
[☐] Template proposal/kontrak belum dibuat.
[✓] Aturan: PERAN CLOSING = tim (CEO) saja; konsultan/bot tidak menutup.
L6. IMPLEMENTASI & ON-BOARDING
[⚠️] Build FNBSense belum selesai (A).
[⚠️] SOP on-boarding ada (F8), tapi butuh produk yang bisa di-deploy.
[✓] Konsep hipercare minggu pertama (nilai jual).
L7. DUKUNGAN & MARGIN
[✓] kalkulator_harga.py ada — UJI: hitung margin 1 contoh client -> harus positif.
[⚠️] Aturan batas jam dukungan per client belum ditetapkan (penggerus margin).

=============================================================
E. PERAN & PEMILIK PER TAHAP
=============================================================
[✓] Pemilik L1-L7 tercatat (F8: CMO lead, CEO laporan/proposal/closing, CTO teknis).
[⚠️] Fungsi OPS (kontrak, invoice, CRM) tanpa pemilik eksplisit.
[⚠️] CEO bottleneck: delegasikan draft laporan/proposal ke AI, CEO cukup approve.

=============================================================
F. GATE: BACKTEST LULOS HANYA JIKA (semua di bawah terpenuhi)
=============================================================
[ ] 1 simulasi penuh lead->support jalan tanpa blok (data dummy/scenario nyata).
[ ] Bot konsultasi merespons dengan benar di grup percobaan (tag/free-response).
[ ] Laporan + proposal bisa dibuat & terkirim (draft oleh AI, final by CEO).
[ ] kalkulator_kesiapan menghasilkan % + band yang konsisten & masuk akal.
[ ] kalkulator_harga menunjukkan margin positif utk contoh client.
[ ] Daftar 1-2 hal yang masih mentok tertulis + ada pemilik & deadline perbaikannya.

=============================================================
G. TINDAKAN WAJIB SEBELUM BACKTEST/BETA  (gap yang menghambat)
=============================================================
1. Rapikan SOP "bikin grup konsultasi = whitelist" (hapus /whitelist palsu). -> AI/CEO
2. Selesaikan template proposal & kontrak. -> AI draft, CEO final
3. Kunci harga paket final (F6). -> tim (butuh angka biaya riil + mau-bayar)
4. Selesaikan build FNBSense MVP v1. -> CTO
5. Siapkan CRM minimal (1 spreadsheet: lead, stage P1-P8, kontak, biaya, jam).
   -> CMO ops
6. Tetapkan batas jam dukungan & cara catat margin bulanan. -> CEO+CMO

Benang: barang ⚠️/☐ di A/B/D/E yang TIDAK punya bahan = blok. Fokus ganti-garap dulu
item G 1-6, setelah itu jalankan backtest penuh (D) dan baru buka beta (F9).