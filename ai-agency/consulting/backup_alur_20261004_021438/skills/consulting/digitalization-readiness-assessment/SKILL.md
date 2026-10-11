---
name: digitalization-readiness-assessment
description: Assess a company's readiness for digitalization + AI agents.
---

# Digitalization / AI Readiness Assessment

For AI consultancies advising clients on digitizing and adopting AI agents. The deliverable is an objective readiness percentage plus a band, feeding a sales funnel.

## v3 package (use for NEW sessions)
Working package: `/home/ubuntu/ai-agency/consulting/` — `PLAYBOOK_KONSULTAN.md` (adaptive discovery, 1 question/turn; problem/process/baseline+unit+period; stakeholder & decision owner; data quality/access; alternatives non-AI/off-the-shelf/AI; value vs running+review cost; pilot/acceptance/stop/rollback; 9-item handoff; assumptions & evidence), `pertanyaan_v3.json` (screening 16 = 2/dim, discovery 32 = 4/dim; official weights 10/20/15/15/10/15/10/5; each item has anchors 1-5, evidence, probe, critical; 13 `critical_ids`), `SPESIFIKASI_WEBSITE_KONSULTASI.md` (build + 12 eval scenarios + engine API).
Website v3 messages carry the marker `[KONSULTASI-OMNISENSE v3]`; read them read-only with `python3 consulting/baca_konsultasi_v3.py --file <file>` (save the client text literally with a file tool; never interpolate client text into the shell). The parser does not send/save anything: all website claims are treated as `self_reported` (never proves reviewed evidence), and it emits `draft_client` + a `handoff` with `sent_to_team=false` — do NOT claim it was forwarded. `[PENILAIAN-SITUS v1/v2]` still uses the old path (`baca_penilaian.py`).
Engine (do not modify): `consulting/assessment_v3.py` — `assess()` for score/range/route, `--roi scenario.json` for value split (capacity vs cash). ROI must be built only from client-given or explicitly-labeled assumptions; never invent numbers.
Binding v3 rules: **unknown = null, NOT 1/3** — if any answer is unknown the single score is **null** plus a 20-100 scenario range; **never force a final score from unknowns**. **Tech value is NOT device count, revenue, or tool price.** Weak `critical_ids` (data relevance+quality, owner, permission, human review/fallback) = prerequisite that changes the RECOMMENDATION, not the score; **an aggregate — however high — never approves deployment** (top route is only "design a limited pilot"). Never call a screening score "validated"; a number is not a certification.
Weights/bands are an **internal heuristic to be calibrated**, not an empirically validated instrument. NIST AI RMF Map/Measure/Manage and the OECD SME brief are process references (context/process), not the source of the weights; **verbatim quotes from them are not required** and would not validate the weights anyway. The old bank (key_questions_*, SOP_Kesiapan_Digitalisasi.md, riset_validasi_kesiapan.md) is **legacy mode** — its "don't know = low" rule and "RESEARCH-VALIDATED" claim are retired; historical scores unchanged.
Calibration & versioning (see `PLAYBOOK_KONSULTAN.md` §11): two independent raters, inter-rater agreement on a sample, revise ambiguous items, version the bank, cross-industry samples. Proposed sample sizes are a plan, **not a validation claim**.

## Golden rule
Do NOT sell AI to a client whose data/process foundations are missing. A failed AI project destroys agency reputation. Assess first; sell the fixing of real gaps, not "magic AI".

## The sales funnel (free-diagnosis / paid-treatment)
- FREE = diagnosis only: 90-150 min structured assessment, deliver the readiness % + band + name the top gaps. STOP there.
- PAID = treatment: the detailed roadmap, 30/60/90-day plan, scope + price. Never give the full recipe free or the client has no reason to pay.
- Tell them the PROBLEM free; sell the SOLUTION.
- QUALIFY before spending time (per-deal: budget amount, decision authority, real gaps).
- Always end with ONE specific paid next-step (e.g. full data audit Rp X, or AI-agent pilot Rp Y). Free with no conversion = wasted effort.
- Free assessment also collects market intel: aggregate gap data into marketing content (e.g. "retail businesses average 45% readiness").

## Assessment model (8 dimensions, each 3-4 questions scored 1-5)
Weights:
| Dimensi | Bobot |
|---|---|
| Strategi & Kepemimpinan | 10% |
| Kesiapan Data | 20% (highest - the success/failure differentiator) |
| Infrastruktur & Teknologi | 15% |
| Digitalisasi Proses | 15% |
| Organisasi & Budaya | 10% |
| SDM & Keterampilan | 15% |
| Tata Kelola, Keamanan & Kepatuhan | 10% |
| Anggaran & Finansial | 5% |

Scoring: dimension score = mean of its questions; weighted = score x weight; total = sum; percent = (total/5) x 100.

## Readiness bands (v3 wording — do NOT auto-recommend AI)
| Skor | Band v3 | Arti (bukan perintah jual) |
|---|---|---|
| 80-100 | Fondasi kuat untuk ditinjau | Layak ditinjau untuk pilot 1 proses; tetap butuh opsi & data siap |
| 60-79 | Fondasi berkembang | Perbaiki gap paralel; pilot terbatas mungkin, bukan otomatis |
| 40-59 | Fondasi perlu diperkuat | Rapikan fondasi dulu; AI tahap lanjut |
| <40 | Fondasi awal | Edukasi & digitalisasi dasar; jangan jual AI |
Note: the old band table ("Siap Penuh -> deployment multi AI agent") is retired. An aggregate score never approves deployment; `deployment_approved` is always false and the top route is "rancang pilot terbatas". Weak critical items override any high aggregate (prerequisite).

## Referenced OmniSense working files (on that machine)
/home/ubuntu/ai-agency/
- SOP_Kesiapan_Digitalisasi.md - full methodology & 32 questions
- kalkulator_kesiapan.py - CLI scorer (interactive `-i`, or `-n` with 32 values)
- template_penilaian.csv - field collection form (import to Excel/GSheets)
- key_questions_client.md - client key-question bank organized by the 8 dimensions; use inside the free consult
- SOP_Omnisense_Utama.md - master operating SOP: flow (lead->ship), consult sesi, key questions, readiness-for-AI gates
- templates/ - post-consult report templates (eksekutif / lengkap / WhatsApp / contoh terisi)
- fase8_sop_internal.md - roles & owners (free consult led by CEO+CMO), sales pipeline, onboarding
- fase9_soft_launch.md - beta pilot plan (3-5 clients; also backfills a skipped Fase 5)
Consult session flow (v3): context (no score) -> screening (triage) -> discovery 1 question/turn with evidence -> engine `assessment_v3.py` for score/range/route -> compare non-AI vs AI options -> baseline/KPI + pilot plan -> handoff to team. Unknown answers stay null (no forced final score). Do NOT capture a "willing-to-pay figure" as a readiness signal; price/closing belong to the team and are not part of the assessment.

## Competitor research (inspiration, NOT copying)
PUBLIC Instagram profile data (bio, follower counts, recent post captions) IS readable WITHOUT login via Instagram's own endpoint - see the `instagram-data-access` skill; do NOT default to "Instagram is unusable". Login is still gated and private/follower-list data is not readable; the public endpoint beats wrestling the login door. Combine with: competitor websites/landing pages (positioning, features, pricing), YouTube demos, docs/blog/changelog, job postings (tech direction), product reviews (pain points to sell against), LinkedIn company pages. Mimic structure and strategy; never copy content.

See references/omnisense-context.md for the business context and deliverables built for this client.

### Rentang unknown harus mengikuti mesin
Jika ada unknown, skor tunggal null. Rentang ditentukan dari jawaban yang sudah diketahui dan batas1–5 pada yang belum diketahui, memakai bobot asli. Skala indeks20–100 tidak berarti selalu melaporkan rentang20–100: rentang penuh20–100 hanya jika seluruh butir unknown. Gunakan range aktual dari assessment_v3.py, jangan mengarang/menyalin angka20–100 untuk jawaban sebagian.
