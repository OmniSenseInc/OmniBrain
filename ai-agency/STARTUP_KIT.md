# OMNISENSE — STARTUP KIT (Index Pusat)
Satu dokumen untuk memegang seluruh fondasi OmniSense. Versi 1.0.

==================================================================
1. IDENTITAS (ringkas)
==================================================================
- VISI  : "Menjadikan digitalisasi dan AI agent sebagai fondasi operasional setiap
          bisnis — menggantikan cara kerja tradisional yang sudah tidak relevan."
- MISI  : "Mengukur kesiapan bisnis, menemukan titik di mana sistem tradisional
          berhenti berfungsi, lalu membangun digitalisasi penuh dan AI agent custom
          yang mengambil alih."
- SLOGAN: "Where Traditional Systems end, AI Agents Begin."
- BRAND : OmniSense (wajah). FNBSense = salah satu produk (F&B).
- LOGO  : brand/BRAND_LOGO_OMNISENSE.md (aset resmi LOCKED; jangan gambar ulang mark-nya).
- WEB   : website/index.html (tema "Obsidian Instrument" terkunci) — status build ada di
          website/TEMA_OMNISENSE.md.
- MODEL : Konsultasi GRATIS -> menilai kesiapan -> MEMBANGUN & MEMASANG (berbayar).
- CAKUPAN: seluruh bisnis; F&B = beachhead pertama (lewat FNBSense).

==================================================================
2. 11 FASE ROADMAP — STATUS
==================================================================
F0 Kebenaran dasar      DONE (fase0_hasil.md)
F1 Bisnis inti          DONE (fase1_bisnis_inti.md)
F2 Pelanggan & masalah  DONE (fase2_pelanggan_masalah.md)
F3 Visi-misi-nilai      DONE (fase3_visi_misi.md)
F4 Positioning          DONE (fase4_positioning.md)
F5 Validasi             DILEWATI sementara (rencana&alat siap; perannya diambil F9)
F6 Pricing              DONE (fase6_pricing.md + kalkulator_harga.py)
F7 MVP scope            DONE (fase7_mvp.md) — build = kerja tim/CTO
F8 SOP internal         DONE (fase8_sop_internal.md)
F9 Soft launch          RENCANA SIAP (fase9_soft_launch.md) — eksekusi+klien
F10 Publikasi           DIPERSIAPKAN (kerangka landing page dsb)
F11 Ukur & ulangi       DIMULAI saat F9/10 jalan

==================================================================
3. CARA MENJALANKAN BISNIS (operasional)
==================================================================
- SOP UTAMA (alur + penilaian kesiapan): SOP_Omnisense_Utama.md
- Alur 7 langkah (lead->support) & publikasi: omnisense_ops.md
- SOP internal + peran + SOP sesi: fase8_sop_internal.md
- Key questions client (per dimensi): key_questions_client.md
- Konsultasi grup WhatsApp (bot): SOP_Konsultasi_WhatsApp_Group.md
- Laporan klien (3 varian + contoh): templates/

==================================================================
4. PERALATAN / TOOLS
==================================================================
- Skor kesiapan : kalkulator_kesiapan.py (32 nilai -> % + band)
- Margin harga  : kalkulator_harga.py (cek untung per client)
- Template nilai: template_penilaian.csv
- Riset IG (publik, no login): ig_probe.py | parse_ig.py

==================================================================
5. PROFIL GANDA & TEMBOK (identitas AI)
==================================================================
- Profile INTERNAL  (Telegram, tim) : guardrail_internal_telegram.md
- Profile KONSULTAN (WhatsApp, client): guardrail_consultant_whatsapp.md
- Setup WhatsApp (Baileys, tanpa API key): setup_whatsapp_cto.md

==================================================================
6. STRATEGI & RISET (referensi)
==================================================================
- Analytics kompetitor RICE: analisis_riceai.md
- Landscape agensi AI Indonesia: analisis_landscape_ai_agency.md

==================================================================
7. DAFTAR SEMUA BERKAS (di /home/ubuntu/ai-agency/)
==================================================================
fase0_hasil, fase1_bisnis_inti, fase2_pelanggan_masalah, fase3_visi_misi,
fase4_positioning, fase5_validasi, fase5_alt_tempur, fase5_scorecard,
fase6_pricing, fase7_mvp, fase8_sop_internal, fase9_soft_launch,
roadmap_status, omnisense_ops, SOP_Omnisense_Utama, SOP_Kesiapan_Digitalisasi,
SOP_Konsultasi_WhatsApp_Group, key_questions_client, guardrail_internal_telegram,
guardrail_consultant_whatsapp, setup_whatsapp_cto, analisis_riceai,
analisis_landscape_ai_agency, kalkulator_kesiapan.py, kalkulator_harga.py,
template_penilaian.csv, template_skrining.csv, ig_probe.py, parse_ig.py,
templates/ (4 laporan + proposal_3tier + kontrak_minimal + laporan_bulanan),
paket_audit_dalam.md, SOP_Onboarding_Klien.md, SOP_Delivery_Standard.md,
SOP_Retainer_&_Laporan.md, key_questions_lengkap.md, riset_validasi_kesiapan.md,
komparasi_alur_ai_agency.md, tetapkan_logo.py, logo_sumber.jpg, logo_omnisense_white.png,
brand/ (aset logo resmi + BRAND_LOGO_OMNISENSE.md), website/ (index.html, assets/, pratinjau/)

==================================================================
8. LANGKAH BERIKUTNYA (prioritas tim)
==================================================================
1. Tim: putuskan HARGA Deep Audit (usulan Rp 500rb-1,5jt, dikreditkan) -> isi
   SOP Langkah 4-5; paket_audit_dalam.md siap dipakai.
2. Tim/CEO: isi angka di templates/proposal_3tier.md & kontrak_minimal.md.
3. Buat kerangka LANDING PAGE (prep F10) — aktif tersedia.
4. CTO: setup profile internal (Telegram) + konsultan (WhatsApp Baileys, nomor
   khusus) + tempel guardrail (bot WhatsApp sudah LIVE — verifikasi alur
   on-boarding & tutup sisa kekosongan config).
5. Tim: hitung angka biaya riil -> kunci harga final (Fase 6).
6. Tim/CTO: selesaikan build FNBSense MVP v1 (Fase 7).
7. Fase 9: jalankan beta 3-5 klien pilot alur OmniSense.
8. Setelah beta: publik (F10) + ukur (F11).