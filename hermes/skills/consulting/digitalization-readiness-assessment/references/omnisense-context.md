# OmniSense context

Startup by the user, an AI consultancy/AI agency (respond in Indonesian when they write Indonesian). Team: CEO Vincent, CTO Nathanael, CMO Michael. Free consultation session is led by CEO+CMO.

## Business model (corrected this session)
- Consultation is FREE (always). From it the team maps the client's digitalization path and where to start.
- The PAID part is BUILDING & INSTALLING the system (FNBSense deploy or a custom digitalization/AI-agent build) - NOT the consult itself.
- Scope = ALL businesses ("bisnis", NOT "kecil", not only F&B). F&B is the beachhead via FNBSense.

## Locked strategy
- Vision: "Menjadikan digitalisasi dan AI agent sebagai fondasi operasional setiap bisnis — menggantikan cara kerja tradisional yang sudah tidak relevan."
- Mission: "Kami mengukur kesiapan bisnis, menemukan titik di mana sistem tradisional berhenti berfungsi, lalu membangun digitalisasi penuh dan AI agent custom yang mengambil alih."
- Slogan: "Where Traditional Systems end, AI Agents Begin." (closing tagline)
- Positioning (no word "kecil"): "Omnisense adalah mitra digitalisasi untuk bisnis Indonesia yang sistem lamanya sudah tidak relevan — mulai dari mengukur kesiapan, lalu membangun digitalisasi penuh dan AI agent custom yang mengambil alih."

## Products
- OmniSense = consulting/assessment layer; free readiness assessment (diagnosis) -> paid build/install (treatment).
- FNBSense = per-cafe/FNB web POS; backend is a Hermes agent running cron jobs (daily sales recap, low-stock alerts, weekly P&L, reminders) plus a "personal secretary" chat interface. Differentiator = the Hermes/cron/secretary layer. Secretary channel decision pending (WhatsApp vs web).

## Pricing facts (as stated)
- FNBSense: template 250k (one-time) + 250k/month per client.
- Direct cost: VPS 60k + API key 89k = 149k/month -> margin ~101k/mo (68%) best-case; BUT thin once support time counts (~41k at 1h support @60k). Support hours are the real margin killer.
- API pooling: one opencode account serves 2-3 clients (per-client API cost below 89k), but single-point-of-failure risk.
- Runway ~3 months; team 2-5h/day.

## Deliverables (machine paths)
/home/ubuntu/ai-agency/: SOP_Kesiapan_Digitalisasi.md, kalkulator_kesiapan.py, template_penilaian.csv, key_questions_client.md, SOP_Omnisense_Utama.md, fase0..fase9 docs, omnisense_ops.md, roadmap_status.md, analisis_*.md, kalkulator_harga.py, templates/ (report templates incl. contoh terisi), ig_probe.py.

FNBSense cron ideas that sell: daily sales recap to WhatsApp, low-stock alerts + reorder suggestions, weekly/monthly P&L, supplier/rent/tax reminders, same-period sales comparison.
