# KOMPARASI ALUR — INDUSTRI AI AGENCY vs ALUR OMNISENSE [v1]
Dasar riset: AI-Native Agency playbook, Audit+Build+Support (ABS), SFAI Labs 14-day,
Agaro 5-phase, ConsultKit sales process & audit-first, Ancillary Delivery SOPs,
Ciela SOPs, Agency Onboarding OS (57 langkah), DigitalApplied 30-day, Metaflow ACOS,
Glyde onboarding, AAA model (hakunamatatatech).

====================================================================
1. ALUR STANDAR INDUSTRI (konsensus 5 tahap)
====================================================================
A. PRE-SALE (Sales & Qualifikasi)
   Lead -> kualifikasi AI-spesifik -> PRE-CALL INTELLIGENCE (skor kesiapan +
   kisaran budget + pain point + paket yang cocok SEBELUM call) -> DISCOVERY CALL
   diagnostik (jangan pitch; ~8-14 pertanyaan; kunci: "trigger-nya apa?", "walk me
   through workflow", "pernah coba sebelum?", "siapa pegang data?", "nilainya
   berapa dolar?", "siapa yg approve?", "budget sudah dianggarkan?", "apa yg harus
   benar agar lanjut 30 hari?") -> tutup dengan NEXT STEP berkomitmen (proposal
   review terjadwal / audit berbayar / disqualify) — TIDAK PERNAH "saya kirim info".
   Industri: banyak yang MENARIK BIAYA discovery/audit (audit-first $500-$3k,
   konversi audit->implementasi ~40% vs 10-30% discovery gratis).

B. PROPOSAL & KONTRAK
   Proposal: lead dengan OUTCOME & 3 TIER (mis. $9k/$15k/$24k; tengah = target
   margin); scope per FASE bukan jam; ROI context sebelum harga; 2-3 KPI ukur;
   risk reversal (process guarantee); proposal->closed avg 45% (terbaik 70-90%),
   proposal->closed 25-35% pipeline; kontrak: MSA/SOW dengan data ownership, IP,
   acceptance criteria, payment schedule, exit conditions.

C. ONBOARDING (kontrak -> hari 1-30)
   Welcome <2 jam-24 jam + intake form (20-27 pertanyaan) + folder workspace + kickoff
   meeting 60 menit beragenda (goal, workflow, scope/exclusions, komunikasi, timeline)
   + access requests + weekly status updates (completed/next/blockers/metrics) +
   milestone tracker + deliver pertama sebelum minggu 1 berakhir + day-30 review.

D. BUILD, QA & LAUNCH
   Baseline metrics diukur dulu (jangan klaim ROI tanpa baseline). Build: staging/
   sandbox, prompt versioned, eval harness + ground-truth set (20-50 contoh), human
   review gate, rollback plan, AI-specific failure modes (data drift, prompt
   sensitivity, API limits, dirty data, adoption). Launch: go-live protocol + training
   45 menit + 4-dokumen handoff + 48 jam check-in + day-7 update. Agen berjalan:
   weekly demo, biweekly retro, daily PR review (SFAI).

E. RETAINER & EXPANSI
   Monthly report (summary metrics, mom, wins, issues, next steps) + escalation SOP +
   expansion: monthly opportunity audit, QBR, renewal; retainer $1.5k-4k/bln; day-30
   konversi->retainer ~60%; LTV 4.4x utk model ABS; maintenance 20-30% tahunan.

====================================================================
2. ALUR OMNISENSE (SOP_Omnisense_Utama.md — 7 langkah)
====================================================================
1 Lead masuk (CRM) -> 2 Seleksi cepat -> 3 Sesi penilaian gratis (8 dimensi) ->
4 Kirim laporan gratis -> 5 Penawaran berbayar -> 6 Implementasi & on-boarding ->
7 Dukungan berkelanjutan. Pemilik: CMO/CEO+CMO/CEO/CTO; deadline: seleksi->sesi
<1 mgg; proposal <3 hari setelah laporan; deal <2 mgg.

====================================================================
3. PEMETAAN & ANALISIS GAP
====================================================================
TAHAP INDUSTRI          | OMNISENSE                | STATUS
Pre-call intelligence   | seleksi cepat 1 menit    | MINIM: belum ada skor
  (skor+budget+pain)    | (budget+decision maker)  | kesiapan/skor ke lead;
                        |                          | belum ada kisaran paket
Discovery diagnostik    | sesi 8 dimensi (sudah    | BAIK: terstruktur, berbasis
                        | divalidasi riset)        | bukti; 8 pertanyaan =
                        |                          | sweet-spot Gong (11-14)
Close-to-next-step      | P3 "ada yang ingin       | LEMAH: pasif; industri
  berkomitmen           | ditanyakan?" + handoff   | wajib NEXT STEP terjadwal
Free vs PAID audit      | semuanya gratis          | PELUANG TERBESAR: belum ada
  (tripwire $500-3k)    | 8 inti + 32 dalam        | tier audit berbayar (32
                        |                          | dalam) utk kualifikasi &
Proposal 3-tier         | belum ada template       | KOSONG: gap paling kritikal;
  outcome-first         | proposal                 | konversi proposal 25-45%
Kontrak/SOW (data, IP,  | belum ada                | KOSONG: risiko data & scope
  acceptance, exit)     |                          | creep; perlu minimal 1 hlm
Onboarding detail       | Langkah 6 ringkas:       | MINIM: industri: welcome
  (welcome, intake,     | setup, latih, hypercare  | <2-24 jam, kickoff agenda,
  kickoff, akses,       | minggu 1                 | folder, access, weekly
  weekly update)        |                          | update, deliver pertama
Build/QA/launch standar | belum terdokumentasi     | KOSONG: baseline, staging,
  (baseline, eval gate, |                          | human review, rollback,
  rollout plan)         |                          | failure modes
Retainer & expansion    | Langkah 7 ringkas        | MINIM: belum ada template
  (laporan bulanan,     | (laporan bulanan, servis,| laporan bulanan, escalation
  escalation, QBR,      | minta referensi)         | SOP, expansion/renewal
  renew)                |                          |
Pengukuran dampak       | Fase 11 + skor ulang     | RENCANA ADA, SOP belum
  (baseline vs setelah) | (rencana)                | ditulis; baseline sudah di
                        |                          | 8 inti (untung bulan lalu)

KEKUATAN YANG SUDAH SESUAI INDUSTRI:
- Skor kesiapan 2-tahap (8 inti -> 32 dalam) = struktur "screen lalu deep" yang
  benar; tinggal MONETISASI tahap dalam.
- Pertanyaan berbasis bukti/angka = framework discovery yang benar (diagnosa, bukan
  jualan).
- Handoff pricing/closing ke tim = pemisahan delivery vs sales yang sehat.
- 1 grup per client = isolasi konteks per client (Metaflow: context isolation =
  fondasi).
- Laporan gratis sebagai lead magnet: valid utk volume, TAPI bukan satu-satunya cara.

====================================================================
4. BENCHMARK YANG RELEVAN (buat keputusan)
====================================================================
- Discovery call -> proposal: 60-70% (terbaik 80-90%) | proposal -> closed: 25-35%
  (avg ~15% end-to-end; terbaik 40%+ | audit berbayar -> implementasi: ~40% vs
  10-30% discovery gratis).
- 3-tier proposal: konversi 40%+ (mayoritas pilih tier tengah = margin terbaik).
- Onboarding terstruktur: churn -40%, kepuasan +25%; kickoff 60 menit mencegah 80%
  misalignment; day-30 review -> retainer ~60%; welcome <2 jam.
- Maintenance/retainer: 20-30% nilai proyek per tahun; $1.5k-4k/bln (pasar US).
- 95% pilot AI gagal memberi dampak P&L (MIT) — alasan laporan harus bawa angka
  & risk reversal.

====================================================================
5. REKOMENDASI (urut dampak)
====================================================================
1. MONETISASI AUDIT 32 — setelah 8 inti gratis, tawarkan DEEP AUDIT berbayar
   (isi 32, laporan lengkap + roadmap, kredit ke implementasi). Ini mengubah
   "laporan gratis tak pernah dikonversi" jadi pendapatan + kualifikasi, persis
   model audit-first. (Butuh keputusan harga tim; usul Rp 500k-1,5jt, dikreditkan.)
2. PROPOSAL 3-TIER — template proposal: masalah pakai kata klien + outcome +
   3 paket (Essentials/Recommended/Premium) + KPI + risk reversal. Tersedia utk
   FNBSense & digitalisasi custom. (Kita sudah tandai sejak lama; ini prioritas.)
3. KONTRak MINIMAL — 1-2 halaman: scope, deliverable, acceptance criteria,
   kepemilikan data & IP, pembayaran, exit. Mencegah scope creep & melindungi data.
4. CLOSE-TO-NEXT-STEP — ganti P3 pasif: bot/tim tutup dengan MENAWARKAN langkah
   konkreet terjadwal (mis. "mau saya siapkan rancangan tahap pertama? saya kirim
   Kamis, kita bahas Jumat?"). Industri: tanpa next step = deal mati.
5. ONBOARDING RINCI — minimal: welcome <24 jam, intake singkat, kickoff agenda,
   folder per client, weekly update (selesai/selanjutnya/blocker). Tulis SOP.
6. DELIVERY STANDAR — baseline metrics diukur di awal; build di staging; human
   review gate; rollback plan; 48 jam check-in; template laporan bulanan + escalation.
7. TETAPKAN BONUS: skor ulang 3-6 bulan (triwulan) utk bukti dampak -> case study
   & testimoni (aset pemasaran terkuat, belum ada instrumennya).

====================================================================
6. SUMBER UTAMA
====================================================================
ai-native-agency.com (3-phase; MSA/SOW), howtomakemoneywith.ai ABS roadmap,
sfailabs.com 14-day, agaro.ai 5-phase, consultkit.ai (sales process 6-stage;
audit-first; discovery framework; proposal guide), ancillary.com delivery SOPs,
ciela.ai SOPs, agencyonboardingos.com 57-step, digitalapplied.com 30-day,
metaflow.life ACOS, glydehq.com, hakunamatatatech.com AAA model.