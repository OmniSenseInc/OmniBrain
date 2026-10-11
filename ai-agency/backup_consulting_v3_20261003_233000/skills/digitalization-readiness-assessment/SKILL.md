---
name: digitalization-readiness-assessment
description: Assess a company's readiness for digitalization + AI agents.
---

# Digitalization / AI Readiness Assessment

For AI consultancies advising clients on digitizing and adopting AI agents. The deliverable is an objective readiness percentage plus a band, feeding a sales funnel.

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
| SDM & Keterampilan | 10% |
| Tata Kelola, Keamanan & Kepatuhan | 10% |
| Anggaran & Finansial | 10% |

Scoring: dimension score = mean of its questions; weighted = score x weight; total = sum; percent = (total/5) x 100.

## Readiness bands
| Skor | Band | Rekomendasi |
|---|---|---|
| 80-100% | Siap Penuh | PoC besar -> deployment multi AI agent |
| 60-79% | Layak Lanjut | Pilot AI agent, perbaiki gap paralel |
| 40-59% | Konvensional | Digitalisasi dasar dulu; AI tahap lanjut |
| 20-39% | Awal | Tawarkan audit data & digitalisasi bertahap |
| <20% | Sangat Awal | Edukasi & assessment ulang; jangan jual AI |

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
Consult session flow: ask key questions per dimension -> score 1-5 -> kalkulator -> %+band -> close capturing problem rank + willing-to-pay figure + objections.

## Competitor research (inspiration, NOT copying)
PUBLIC Instagram profile data (bio, follower counts, recent post captions) IS readable WITHOUT login via Instagram's own endpoint - see the `instagram-data-access` skill; do NOT default to "Instagram is unusable". Login is still gated and private/follower-list data is not readable; the public endpoint beats wrestling the login door. Combine with: competitor websites/landing pages (positioning, features, pricing), YouTube demos, docs/blog/changelog, job postings (tech direction), product reviews (pain points to sell against), LinkedIn company pages. Mimic structure and strategy; never copy content.

See references/omnisense-context.md for the business context and deliverables built for this client.
