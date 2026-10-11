# ROADMAP OMNISENSE — STATUS & POSISI
Diperbarui: [tanggal]. Centang (✓) = selesai/terkunci. ☐ = belum/perlu dikerjakan.

Legend: [SELESAI] = keputusan/kerangka selesai | [DILANJUTKAN] = rencana siap, eksekusi oleh tim | [MENUNGGU] = menunggu data/keputusan lain

==================================================================
FASE & STATUS
==================================================================

✓ FASE 0 — Kebenaran dasar (ground truth)
   File: fase0_hasil.md
   Sudah: kondisi keuangan, siapa bos (CEO/CTO/CMO), model, komitmen, runway ~3 bln.
   Sisa: (tidak wajib) jam riil & jembatan keuangan dipertegas tiap bulan.

✓ FASE 1 — Bisnis inti
   File: fase1_bisnis_inti.md
   Sudah: brand=Omnisense, FNBSense = produk, konsultasi gratis -> bangun sistem
   (pemasangan berbayar). Corong jelas.

✓ FASE 2 — Pelanggan & masalah
   File: fase2_pelanggan_masalah.md
   Sudah: beachhead F&B (cafe/resto); masalah inti = "data berantakan & manual"
   (akar dari untung/rugi, stok, waktu, keputusan); solusi = AI agent custom per client.

✓ FASE 3 — Visi, misi, nilai
   File: fase3_visi_misi.md
   Sudah: visi, misi, 4 nilai, slogan.

✓ FASE 4 — Positioning
   File: fase4_positioning.md
   Sudah: positioning 1 kalimat (tanpa kata "kecil"); slogan sebagai penutup;
   cakupan lestari SELURUH bisnis, F&B = beachhead produk.

⏭ FASE 5 — Validasi pelanggan (DI-SKIP sementara — keputusan tim)
   File: fase5_validasi.md (plan) & fase5_alt_tempur.md (alat)
   Status: rencana & alat SIAP. "Skipped" = belum dikerjakan; beta (Fase 9) akan
   menggantikan sebagian perannya. Disarankan tetap jalan sendiri nanti sebelum
   rilis luas penuh.

✓ FASE 6 — Pricing
   File: fase6_pricing.md + kalkulator_harga.py
   Sudah: prinsip harga berbasis nilai; paket Starter/Growth/Multi + custom;
   margin calculator (terbukti: biaya per client ~149k -> harga 250k = margin positif;
   tapi rentan waktu dukungan).
   Sisa: ISI biaya riil tim (VPS, API, jam dukungan) -> angka paket final.

✓ FASE 7 — MVP (scope terkunci; build = kerja tim)
   File: fase7_mvp.md
   Sudah: scope MUST (POS + data + 1 laporan + 1 cron stok + 1 sekretaris), TUNDA,
   Definition of Done, timeline.
   Sisa: Build FNBSense v1 (CTA kerja — kode ada di perangkat kalian).

✓ FASE 8 — SOP internal & alur penjualan
   File: fase8_sop_internal.md + templates/ (laporan eksekutif/lengkap/WA/contoh)
   Sudah: peran & pemilik tiap tahap (konsultasi = CEO+CMO); pipeline P1-P8;
   SOP konsultasi & on-boarding; template laporan.
   Sisa: TEMPLATE PROPOSAL/KONTRAK (belum dibuat).

☐→ FASE 9 — Soft launch / beta — RENCANA SIAP, MENUNGGU EKSEKUSI+KLIEN
   File: fase9_soft_launch.md
   Status: plan siap (3-5 pilot, alur penuh, feedback, gerbang). Butuh klien nyata.
   (Ini juga menutup peran Fase 5 yang di-skip.)

☐ FASE 10 — Publikasi ke publik — BELUM, TAPI BISA DIPERSIAPKAN SEKARANG
   Siap sekarang (tanpa klien): landing page, konten, checklist setup kanal.
   Menunggu: testimoni dari beta.

☐ FASE 11 — Ukur & ulangi — BELUM (butuh data dari Fase 9/10)

==================================================================
PEKERJAAN TANPA KLIEN YANG TERSISA (prioritas)
==================================================================
1. [CERDAS] Template proposal/kontrak — gap Fase 8. (bisa saya buat sekarang)
2. [CERDAS] Kerangka landing page + konten + checklist kanal — prep Fase 10.
3. [TIM] Isi biaya riil & kunci harga final (Fase 6).
4. [TIM/CTO] Build FNBSense MVP v1 (Fase 7).
5. [OPSIONAL] README/fondasi repo OmniSenseInc dari dokumen OmniSense.

==================================================================
PEKERJAAN YANG BUTUH KLIEN (menunggu)
==================================================================
- Validasi wawancara (Fase 5, bila tetap jalan)
- Jalankan beta 3-5 klien pilot (Fase 9) & pengukuran (Fase 11)
- Testimoni untuk Fase 10

==================================================================
CATATAN BERKAS
==================================================================
Semua dokumen berada di /home/ubuntu/ai-agency/:
fase0_hasil, fase1_bisnis_inti, fase2_pelanggan_masalah, fase3_visi_misi,
fase4_positioning, fase5_validasi, fase5_alt_tempur, fase5_scorecard,
fase6_pricing, fase7_mvp, fase8_sop_internal, fase9_soft_launch,
omnisense_ops, analisis_riceai, analisis_landscape_ai_agency,
SOP_Kesiapan_Digitalisasi, kalkulator_kesiapan, kalkulator_harga,
template_penilaian, ig_probe, parse_ig, templates/