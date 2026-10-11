# OmniSense Website — Live Instance Notes

The user's own site. Read before touching it; brand rules also live in the user's
`ai-agency/templates/OMNISENSE_BRAND_BRIEF.md` and the (user-owned) `omnisense-content` skill.

## Findings that set the direction

1. **Two existing palettes** — content/posters use locked obsidian monochrome; client-facing material
   uses navy `#0B1F3A` + teal `#14B8A6`. They are fine while separated. The website picked the obsidian
   palette as the parent instead of introducing a third one.
2. **omnisense.id does not currently serve OmniSense** — the domain serves an SPA titled "NeoSense
   Social Media Intelligence" (Vite bundle, copy about monitoring narratives/actors/risk). So this is a
   replacement, not a restyle; the old page needs a subdomain or removal (user decision).
3. **The category is a consultancy that sells measurement**, not SaaS: weighted 8-dimension assessment
   → one 0–100 score → band → roadmap. The honest visual language is score, bars, progress line.
4. Motion market is saturated on dark + glass + glow + video (see `motion-technique-selection.md`).

## Theme — LOCKED: A "Obsidian Instrument"

The user delegated the choice ("pick the best one yourself and just do it"), so it was decided and
implemented in the same turn. `index.html` now carries a single theme: the theme switcher, the
`?tema=` query plumbing and the localStorage persistence were **deleted**. Themes B and C survive only
as tokens in `TEMA_OMNISENSE.md` §3 and as screenshots in `pratinjau/arsip-tema/`.

Why A: teal reads as the *data* color — it appears only on the score arc, dimension bars, progress
rail, right-edge tick rail and the active nav link, never as decoration. B (navy) collapses into the
most common Indonesian SaaS combination; C (pure monochrome) loses the status cue that lets a reader
tell 48 from 82 without reading the numbers.

Tokens as shipped (this is the file, not a proposal):

```
--obsidian  #09090B   --obsidian-2 #0C0C0E   --glass/--panel #121215
--line      #27272A   --line-2     #3F3F46   --track #34343C
--white     #FFFFFF   --slate #94A3B8 (7.76:1)   --slate-dim #64748B (4.2:1, NON-TEXT ONLY)
--signal    #14B8A6   the single accent
radii 10 / 14 / 20 / 999px
H1 clamp(38px, 6.4vw, 74px) · H2 clamp(28px, 4.2vw, 50px) · labels JetBrains Mono 11–12.5px
```

Small text (marquee, step numbers, panel labels) was moved off `--slate-dim` to `--slate` because
4.2:1 fails AA at 11–12px. Theme B/C contrast numbers, if those tokens are ever revived: secondary text
A 7.76:1 · B 8.60:1 · C 7.76:1, teal on navy 6.64:1.

## Logo — fakta terkunci yang menentukan tone

Marka OmniSense (aset terkunci, `assets/logo-mark-white-256.png`): busur monoline
konsentris dengan celah + titik tengah, stroke rata, ujung membulat, ruang negatif besar.
Hanya ada versi PUTIH — di latar terang marka hilang, jadi tema terang butuh versi gelap
dulu sebelum dipakai. Marka paling kuat di obsidian/navy. Tone yang cocok: monoline,
tenang, gelap, busur sebagai motif, teal sebagai sinyal (bukan pendar).

## Lapisan tone (cara ganti rasa tanpa membongkar tema)

Kalau pemilik bilang halaman "terlalu AI banget / kaku", jangan tulis ulang halaman.
Tambahkan lapisan override: `tone/00-nyaman.css` (bersama) + satu berkas per kandidat,
lalu buat salinan `index-tone-<x>.html` yang menautkan lapisan itu SEBELUM `</head>`
(urutan setelah `<style>` inline = menang). Skrip: `tone/buat-pratinjau-tone.py`.

Daftar hitam penanda "template AI" yang harus dibuang lebih dulu: label huruf besar
berspasi lebar, pendar neon, medan titik canvas, watermark raksasa, penggaris tick,
pita berjalan, kartu 1px seragam, huruf bobot 800, palet 5 warna aksen.

Pitfall yang sudah kena: rule override dengan selektor lebih spesifik
(`.dcard .wbar`) menang atas rule berikutnya yang kurang spesifik (`.wbar`) —
tulis selektor selengkap mungkin di lapisan tone. `--slate-dim` dilarang untuk teks kecil.

## Riset motionsites.ai ulang (30 Sep 2026) — kandidat animasi baru

Katalog publik dibaca ulang: **541 item** (185 gratis / 356 berbayar / 417 punya preview publik) — hanya
+15 sejak riset pertama, jadi arahnya tidak berubah. Cara mengambilnya ulang tanpa browser tool:
muat `/sections` dengan Playwright, tangkap header `apikey` dari request `rest/v1/prompts`, lalu panggil
endpoint yang sama dengan `Range` (500/baris) dari dalam `page.evaluate` — curl polos kena 401.
Bahan + skrip ada di `ai-agency/referensi/motionsites-2026-09/`.

Frekuensi teknik dari judul: 3D/WebGL 22 · angka/chart/meter 18 · hover 9 · video bg 8 · glass 7 ·
scroll/pin 6 · grid/grain 6 · morph 5 · marquee 4. Bacaan: yang paling populer (3D) juga yang paling
mahal di HP; irisan yang layak untuk OmniSense justru **angka/meter/chart** — kedua terbanyak dan persis
isi layanan OmniSense.

Kandidat yang **terverifikasi bisa Canvas 2D / CSS murni** (semuanya didemokan hidup di
`website/motion-adopt.html`, terpisah dari `index.html`):

1. **Cakram radial berputar** (dari "Intelligent Operations") — jarum radial dari pusat, titik orbit,
   busur teal. Pengganti "orb 3D": terlihat seperti alat ukur, biaya nol.
2. **Denyut indikator status** (dari "Heart Health Dashboard") — satu denyut opasitas+scale untuk
   menandai bagian yang aktif saat gulir. Jangan bawa metafora EKG/denyut jantungnya.
3. **Bar bobot + angka berhitung naik + tangga skor** — sudah ada di index.html, tinggal ditambah
   count-up; ini dampak terbesar dengan biaya terkecil.
4. **Rel tick progres** — sudah dipakai, jangan diubah, jangan ditambah animasi kedua di elemen sama.

Ditolak ulang dengan alasan: video background (preview-nya sendiri 2–11 MB), objek 3D/WebGL,
marquee di hero, spektrum neon/aurora, image sequence/frame scrub.

**Pitfall QA yang terukur:** `verify_page.js --scroll-to "<selector>"` memotret tepat setelah
memusatkan elemen, sehingga `IntersectionObserver` belum menyala di pass itu — `--eval` pada bar/angka
kembali 0 dan itu BUKAN bug halaman. Verifikasi reveal dengan probe DOM terpisah: `scrollIntoView`,
tunggu ~2,5 s, baru baca `getBoundingClientRect().width` bar dan isi angka. Untuk canvas, buktikan
benar-benar menggambar dengan menghitung piksel alpha/teal dari `getImageData` — "canvas ada di DOM"
bukan bukti.

## Motion v4 — the whole site, with the ronde-2 motion (30 Sep 2026)

The user's complaint was **"untuk isinya masih tidak sesuai dengan yang ada di hasil web yang pertama"** —
the trial pages (`motion-adopt*.html`) were motion *audits* (sections 01–08 explaining which patterns to
adopt), so their copy had nothing to do with the site. What he actually wanted: **the full OmniSense page,
with the new motion on it.** Reading the request as "the copy drifted" sends you off diffing prose; the
real fix was to stop shipping a demo page and build the real page.

`website/adopt_index_motion.py` splices three motion changes into index.html itself. It is
**idempotent** (`if '#scoreDisc' in s: exit`) and it copies `index.html` to
`arsip/index-v2-sebelum-motion.html` before writing, so re-running it is safe. It also asserts
`out.count('<style>') == 1` and that the visible text is unchanged before it writes.

**State as shipped (30 Sep 2026): the motion lives in `index.html` — there is no twin file.**
An earlier round shipped `index-motion.html` (a separate file generated by `build_index_motion.py`)
so the user could compare it against `index.html`; once approved, the three motions were adopted
into `index.html` and both the twin file and its generator were moved to `arsip/`. Do not
reintroduce a second live HTML file: two files that must stay text-identical will drift, and the
user reads the drift as "the content changed".

**The blocker that made everything look wrong: the theme kills the very elements the motion needs.**
Theme A ends with
`/* ---- yang paling "AI": kanvas titik, penggaris gulir, marquee, watermark ---- */`
`#field, .ticks, .mq, .mq-track, .ticker { display: none !important; }`
plus a second `.marquee { display: none; }` further down. So the dot canvas, the tick rail and the marquee
were all switched OFF by the locked theme — any motion mounted on them animates invisibly. `#field` was
replaced by the score disc (so it needs no revival); `.ticks`, `.mq`, `.mq-track`, `.ticker` and
`.marquee` had to be explicitly un-killed in the motion build. **Check for `display:none !important`
before adding motion to any locked page.**

What v4 changes (and nothing else — the visible text is byte-identical to index.html, 323/323 lines):

1. **Score disc** (Canvas 2D) mounted *inside* the hero panel's score ring (`#scoreDisc` inserted before
   `.num`), replacing the `#field` dot canvas: 44 rotating radial needles at low alpha, a track ring,
   a teal arc sweeping 0→68% in 1.4 s with a cubic ease, an inner ring and 64 orbiting dots.
   `countUp()` is removed — the canvas drives `#gaugeNum` so number and arc can never disagree.
2. **Tick rail lead marker** — a 7px teal dot with a `tklead` pulse animation, `translateY`-ed to the
   last lit tick from the same scroll fraction. Rail is desktop-only (`display:none` < 900px) by design.
3. **Marquee revive + honest pause** — the strip's copy already said it stops when approached, so hover
   (`@media (hover:hover) and (pointer:fine)`) and `pointerdown` both pause it, and both paths stop under
   `prefers-reduced-motion` / motion-off (otherwise the promise is false).

Bugs found while verifying v4:

- **Double `<style>`**: `head = cut('<html lang="id">', '<body>')` already contained the whole stylesheet,
  so appending `style` again shipped two copies (117 KB). Cut head at `'<style>'` instead, then assert
  `count('<style>') == 1`. Always assert visible-text equality against the source after a splice build.
- **`getBoundingClientRect()` is the ground truth for "is it visible"** — the disc's rect was 132x132 at
  x=814, i.e. inside the ring; the earlier 1440-wide canvas was the hero `#field` still in place.
- **A vision model reported "no tick rail, no marquee" on the hero shot; both existed.** The marquee sat at
  y=1092 — exactly one viewport down — and the rail ticks were near-black-on-navy. Screenshot the element
  itself after `scrollIntoView` before believing "it isn't there".
- **Playwright's `click()` scrolls the element into view**, so a toggle test that clicks `#motionBtn`
  (fixed, bottom-right) leaves the page scrolled to the bottom — the hero is off-screen and the disc
  correctly refuses to animate. Drive toggles through `page.evaluate(() => OmniSense.applyMotion(...))`
  and pin `scrollY`, or the harness manufactures a bug.
- **A stale `heroVisible` flag made "motion on" a no-op** after a scroll round-trip: `canvasStart()` now
  re-measures `$('#top').getBoundingClientRect()` instead of trusting the observer's last value.
- **Scrolling past a half-drawn arc must settle, not freeze**: the hero observer now calls `discFinal()`
  when the hero leaves the viewport, so the ring length always matches the number.

v4 verification after adoption into `index.html` (`scripts/verify_page.js`, four passes plus `--click`):
zero console/page errors; disc canvas 132x132 with 2747 teal + 4553 lit pixels (it genuinely draws);
sweep 1 and `#gaugeNum` 68 at rest; 14 rail ticks, 7 lit mid-scroll; lead marker `translateY(52.4px)`;
`applyMotion(false)` → `1|block|68` (disc keeps its final frame, display restored to block, number 68),
`applyMotion(true)` → `disc()` back to 0 and replays; marquee `animationName=mq`, running at rest, paused
after a tap on the strip, `none` under reduced-motion; `scrollWidth === innerWidth` at 1440, 390 and
reduced-motion; 8 `.dcard`, weight bar 100.656px at 1440. Previews `pratinjau/v4-final-*.png`
(desktop, tengah, mobile, tanpa-gerak); the pre-adoption comparison shots are `pratinjau/v4-*.png`.

Preview link (durable systemd tunnel, see the handover section): the site root
`https://<host>/` now serves the motion build; `arsip/index-motion-pratinjau.html` is reachable at
`/<arsip>/index-motion-pratinjau.html` if the old twin needs comparing. Always re-read the hostname
from `.preview_tunnel.log` and probe with `curl -4` before sending it.

### Two QA traps hit while verifying the adoption

- **A vision model "confirmed" a rail and marquee that do not exist.** Asked to check the hero
  screenshot it answered "no tick rail" (correct — the rail is a 35px-wide desktop-only flex at
  x=1388) but also invented a whole different page: brand "KECERDASAN", nav "Cara Kerja/Produk",
  "Level 2", a "27" in the gauge, an AWS Marketplace line, an FAQ section, a partner-logo marquee.
  None of that is in the file. Cross-check every vision claim against `getBoundingClientRect()` and
  the DOM before acting on it; the numbers here said rail present (35x152, `display:flex`), subhead
  `rgb(198,214,230)` at 18.5px (i.e. the "low contrast" complaint was false), and no logo strip.
- **`display:none` on `.ticks` hides the rail on mobile by design, so "0 on" is not a bug.** A rail
  probe on the mobile pass reads 14 ticks / 0 on simply because the container is hidden; assert the
  rail only on the desktop pass.
- **An empty `--eval` result is a broken expression, not a page bug.** Two composite probes returned
  `""` in every pass — the expression threw. Re-issue it as a small `(function(){...})()` and it
  returns a real value.

## Motion v3 — structure rework (shipped; theme untouched)

The user judged v2 "terlalu monoton". Diagnosis: every section had the same shape (eyebrow → h2 →
paragraph → hairline row), so there was no variation in rhythm, scale or module type. Tokens, palette,
logo, copy rules and the single motion toggle all stayed as they were; only the section lineup changed.
Patterns came from the inspo the user supplied (`ai-agency/referensi/60fps-design/`,
`ai-agency/referensi/inspo-web-thedzianis/`):

1. Giant typographic watermark (60fps.design) — `OMNISENSE` at 300px behind the hero, opacity .055 +
   hairline, clipped by the hero edge, parallax 0.03x; repeated at 216px in the footer (footer.design).
2. Section index strip (cta.gallery sidebar, flipped horizontal) — `.ixbar`, `sticky; top:var(--navh)`,
   seven numbered items, each followed by a counted label with its unit (`4 langkah`, `5 rentang`,
   `8 dimensi`, `6 keluaran`, `6 istilah`, `2 proyek`, `1 nomor`) — a bare number reads as noise, so
   never ship counts without a unit. `overflow-x:auto` + scroll-snap on mobile (the clipped next item
   is the affordance there), fits exactly at 1440. Active item gets the teal underline. Shares the
   scrollspy with the nav, which carries labels only.
3. Numbered cards + metadata (60fps.design) — the 8 dimensions became `.dcard` in a 2-col grid:
   number, `BOBOT xx%`, title, one-liner, `.wbar i` whose width comes from `data-w` scaled to the
   largest weight (20% = full track). Cards are flex-column with `margin-top:auto` on the bar so bars
   line up across a row.
4. Score-band ladder (new module, data from `kalkulator_kesiapan.py`) — 0–100 scale in five segments
   with `.lmark` sliding to `left:68%` on reveal, then the five bands with their ranges.
5. Numbered deliverables list (unsection.com / 60fps) — six outputs, number left, kind label right.
6. Chip rail + panel (60fps chip rail + navbar.gallery filter) — glossary: six terms,
   `role="tablist"`, click or left/right arrow swaps the panel, `aria-selected` follows.
7. Case cards (60fps) — 001/002, problem/built/result rows, plus a spec chip row using only real
   numbers (12 armada, 395 pengiriman diimpor, 14 modul, 80 endpoint, 5 container).
8. CTA + footer (cta.gallery + footer.design) — full-bleed CTA with teal glow and the phone number as
   a giant teal-stroked outline (`-webkit-text-stroke`, `aria-hidden`; the readable number lives in the
   footer link). Footer is 3 columns plus the oversized wordmark at the bottom edge.

Deliberately NOT taken: light mode (60fps / supahero / 404s) and phone-mockup galleries. OmniSense
sells consulting, not an animation catalogue.

Bugs found and fixed while verifying v3 (all worth remembering):

- `.foot p` (specificity 0,1,1) silently overrode `.foot-wm` (0,1,0) and collapsed the footer wordmark
  to 11px. Scope the tagline rule to `.foot-grid p`.
- `</main>` was closing after `<footer>`.
- Mono labels at 10–11.5px were bumped to 12px; `--slate-dim` remains non-text only.
- The CTA phone number at `rgba(244,244,245,.09)` was unreadable; it is now an outline, not text.

v3 verification (`scripts/verify_page.js`, 6 passes): `ok true`, zero console/page errors, no
horizontal overflow at 1440 or 390, score 68, weight bars 502.5/376.9/376.9/376.9/251.3/251.3/251.3/125.6px
(= 100/75/75/75/50/50/50/25 of track), reduced-motion and motion-toggle passes both end in final
states, glossary tabs switch by click and by arrow key. Previews: `pratinjau/v3-*.png`.

## Motion v2 — shipped

Entry (no preloader): headline word-by-word out of a mask at 55 ms stagger → subhead → CTA → hint →
score panel; gauge arc to 68% with a count-up, four dimension bars staggered 90 ms.
Scroll: three-layer hero parallax (text 0.14x / canvas 0.08x / panel 0.05x), hero copy fading at
0.95x, 4-step progress rail with step dots lit from the same value, right-edge tick rail plus scroll
percentage, nav blur + scrollspy, per-section reveals, 8-row dimension stagger.
Detail: canvas node/line field (white nodes, teal links, cursor-reactive, DPR ≤ 2, pauses on hidden tab
and off-screen hero), cursor radial spotlight with 0.09 lerp (pointer: fine only), 5% grain, teal left
edge on dimension-row hover.
Controls: a single "Gerak: Nyala/Mati" toggle (◎, bottom right). The theme switcher is gone — do not
reintroduce it without the user asking.

## Verified headlessly (Chromium)

Zero console errors and zero page errors. Score 68 · arc offset 104.55 · bars 82/74/61/48%.
At 420px scroll: canvas +33.6px, hero copy opacity 0.56. Rail 13% (1 step) → 69% (3 steps) → 100%
(4 steps); tick rail 000% → 100%. Mobile 390: `scrollWidth` 390/390, spotlight off. Motion off: canvas
`none`, spotlight 0, score and bars already final, rail 100%; switching motion back on replays cleanly.
Reduced motion: canvas `none`, score 68, bars filled, 4 steps lit, tick rail hidden.

## Files

```
ai-agency/website/index.html                 THE site: theme A locked + motion v4 (disc, rail lead, marquee)
ai-agency/website/adopt_index_motion.py      idempotent splicer that produced it; re-run = no-op; backs up first
ai-agency/website/arsip/index-v2-sebelum-motion.html   the pre-motion page (rollback target)
ai-agency/website/arsip/index-motion-pratinjau.html    the old twin file (kept only as evidence)
ai-agency/website/arsip/build_index_motion.py          generator for that twin file (superseded)
ai-agency/website/pratinjau/v4-final-*.png   post-adoption previews (desktop, tengah, mobile, tanpa-gerak)
ai-agency/website/privacy.html               halaman kebijakan privasi (ID+EN)
ai-agency/website/404.html · robots.txt · sitemap.xml · site.webmanifest
ai-agency/website/assets/og-omnisense.png    kartu pratinjau tautan 1200×630
ai-agency/website/scripts/buat_og.py         generator kartu OG
ai-agency/website/scripts/shot_final.js      pratinjau resmi situs (01–07)
ai-agency/website/scripts/shot_legal.js      pratinjau halaman privasi (08–10)
ai-agency/website/SERAH_TERIMA_DEPLOY.md     dokumen serah terima untuk Vincent (nginx)
ai-agency/website/pratinjau/v4-*.png         pre-adoption comparison shots
ai-agency/website/TEMA_OMNISENSE.md          §0 the locked decision, §2–3 tokens, archive status of B/C
ai-agency/website/MOTION_REFERENSI.md        motion research + the v2 spec + the test numbers
ai-agency/website/pratinjau/v3-*.png             v3 section previews (hero, cara-kerja, kategori-skor,
                                                dimensi, output, kamus, hasil, kontak, footer, mobile)
ai-agency/website/pratinjau/final-*.png      older v2 screenshots: hero, proses, dimensi, cta, mobile x2, tanpa-gerak
ai-agency/website/pratinjau/arsip-tema/      the three-theme comparison previews (B/C evidence)
```

## Hasil / case-study section (shipped)

`[ HASIL NYATA ]` was rewritten from one `div.note` into two `.prod` cards in a `.prods.stagger` grid
(1 col < 900px, 2 cols above; cards are equal height because `.tagline` uses `margin-top:auto`).
One card per system: FNBSense (`Produk OmniSense · F&B`) and LogiSense (`Proyek klien · Logistik`).
LogiSense is client work, so it is labelled as a client project, not as an OmniSense product. Both are
evidence of the consultancy's work, never a co-equal brand next to OmniSense.

Rule: write problem → what was built → result, and **no invented metrics**. Qualitative outcomes only
("laporan datang sendiri", "jarak tempuh lebih pendek"); if the user wants numbers, ask for the real ones.

## Contact wiring (shipped)

WhatsApp `088809640700` → `https://wa.me/6288809640700?text=Halo%20OmniSense%2C...` on all four CTAs
(nav pill, hero, contact box) plus a plain `wa.me` link in the footer. `target="_blank" rel="noopener"`.
The nav "Kontak" anchor still points to `#kontak` — that is intentional, not a missed CTA.
A `data:image/svg+xml` favicon was first added to kill the `favicon.ico` 404 in the console, then
replaced by the real files: `assets/favicon.ico` + `favicon-32.png` + `favicon-16.png` + apple-touch.
`index.html` therefore depends on the `assets/` folder — it is no longer a single self-contained file.

## LogiSense facts (source: github.com/OmniSenseInc/LogiSense, public repo)

Read the repo, don't invent. Public facts usable on the site: client **YES-Logistics** (12 armada, 20
karyawan, 395 pengiriman diimpor), 14 agent modules + dashboard + data migration, Python/FastAPI
microservices (core-api, financials, fleet-gps, intelligence + nginx gateway), 80 endpoints, 5
containers healthy, PostgreSQL/Neon, Docker + GitHub Actions, Baileys WA bot, MiniMax M3 via
OpenRouter, built by OmniSense (Vincent, Andi, Atong, OmniSense AI).

**Do NOT publish client financials** (revenue Rp 6.955.000.000, margin 8.6%) — public in the repo but
they are the client's numbers; the landing page describes the build, not the client's books. Also
never claim savings percentages that are not measured.

**The user's standing call:** on the public site LogiSense is written as an unnamed client ("Klien kami
di bidang logistik"), no client financials, and the result is phrased as delivered ("saat serah terima") —
LogiSense is stalled/"mangkrak" and functions as portfolio proof only, so never assert it is currently
running or promise further work on it.

**Sudah ditanyakan dan dijawab pemilik — jangan tanyakan lagi.** Namanya tetap tidak disebut di
situs, dan framing "Proyek klien · Logistik" dipertahankan apa adanya meskipun dealing-nya tidak
closing; angka spesifikasi (12 armada, 395 pengiriman, 14 modul, 80 endpoint, 5 container) tetap
tayang karena klien sudah menyetujui datanya. Alasan pemilik: datanya akurat dan sesuai keinginan
klien, yang gagal hanya dealing-nya. Sudah disisir — tidak ada nama perusahaan di mana pun di
`website/`, dan angka-angka itu tidak bisa dilacak balik ke perusahaan tertentu. Repo says the WA bot
is code-ready but not yet deployed, so phrase it as built, not as running.

## Logo (LOCKED — never hand-draw it)

The OmniSense mark is an official asset (white spiral with a solid core, ~2 turns, round caps).
Canonical source `logo_sumber.jpg`; derivatives in `brand/` (regenerate with `tetapkan_logo.py`);
doc `brand/BRAND_LOGO_OMNISENSE.md`. The website header uses `website/assets/logo-mark-white-256.png`
at 26x26 with the lowercase wordmark `omnisense` (Inter 600, -0.01em); the favicon set lives in
`website/assets/` too.

**Do not approximate the mark with a hand-written inline SVG** — that is the mistake the user called
out. Need a new size or colour? Derive it from the master PNG, never redraw.

## Copy rules (bahasa) — the page must match the SOP, not invent a model

The landing page describes a *measurement* service, so its numbers and names have to match what the
client will actually receive. Source of truth: `ai-agency/SOP_Kesiapan_Digitalisasi.md` and
`ai-agency/kalkulator_kesiapan.py` (the tool that prints the real score).

- **8 dimensions and weights come from the calculator**: Strategi & Kepemimpinan 10, Kesiapan Data 20,
  Infrastruktur & Teknologi 15, Digitalisasi Proses 15, Organisasi & Budaya 10, SDM & Keterampilan 15,
  Tata Kelola/Keamanan 10, Anggaran & Finansial 5. The site shows them sorted by weight, and its
  descriptions are plain-language one-liners. Do not ship a friendlier-but-different set (an earlier
  version listed `Pelanggan & pemasaran` and `Biaya & anggaran` with 18/16/14/14/12/10/8/8 — that
  contradicted the calculator and had to be fixed).
- **Band names come from `BANDS`**: Siap Penuh / Layak Lanjut / Konvensional / Awal / Sangat Awal.
  `Siap Bertahap` was invented and did not exist anywhere in the methodology; 68% is `Layak Lanjut`.
  On the page the label is `Kategori:`, never `Band:` (in Indonesian "band" reads as a music band).
- **The example panel is a subset, and says so**: 4 of 8 rows, footer `Contoh 4 dari 8 dimensi · skor
  akhir dihitung berbobot`. Without that line a reader sees 8 dimensions claimed and 4 shown.
- **The free-session duration is a business promise, not a fact you can derive**: the SOP's free
  assessment is a 90–150 minute workshop, the page said "12 menit". Left as "Percakapan awal lewat
  WhatsApp · rata-rata 12 menit" — ask the user which one is true before changing the number.
- **FNBSense deployment is unverified**: the tagline reads `Dibuat untuk kafe & outlet F&B`, not
  `Berjalan di ...`, because nothing in the working files proves live outlets.
- Write for a non-technical owner: `dashboard web dengan peta`, not `berpeta`; `asisten WhatsApp untuk
  pemilik`, not `owner`; `kontrol keuangan`, not `financial controller`. Keep hard numbers (80 endpoint,
  5 container) but drop decorative jargon (`+ gateway`, `container sehat` → `berjalan normal`).
- No em dashes as parenthetical wrappers, no tailing negations ("skor, bukan opini"), no meta-commentary
  about the UI ("garis di bawah bergerak mengikuti seberapa jauh Anda membaca halaman ini" — cut it),
  no redundant pairs ("gratis, tanpa biaya"). See the `humanizer` skill for the full checklist.

## Handing over a preview link (systemd, not a session-bound process)

A quick tunnel started as a background shell command dies with the session, and its
`trycloudflare.com` hostname CHANGES on every restart — so a link already sent to the team goes
`530` the moment the tunnel is bounced. Make it durable:

- `~/.config/systemd/user/omnisense-preview-web.service` — `python3 -m http.server 8080 --bind
  127.0.0.1`, `WorkingDirectory=/home/ubuntu/ai-agency/website`, `Restart=always`.
- `~/.config/systemd/user/omnisense-preview-tunnel.service` —
  `/home/ubuntu/.local/bin/cloudflared tunnel --url http://127.0.0.1:8080 --no-autoupdate`,
  `StandardOutput/StandardError=append:/home/ubuntu/ai-agency/website/.preview_tunnel.log`,
  `Restart=always` (copy cloudflared out of `/tmp` first — `/tmp` does not survive a reboot).
- `loginctl enable-linger ubuntu` is already set, so the units come back after logout/reboot.
- **Never hard-code the hostname**: grep the last `https://[a-z0-9-]+\.trycloudflare\.com` out of
  `.preview_tunnel.log` at use time. Any script or message that reuses the tunnel reads it live.
- PITFALL: this box resolves quick-tunnel hostnames to IPv6 first and has no working IPv6, so plain
  `curl <url>` returns `HTTP 000`. Always probe with `curl -4` before concluding the tunnel is down.
- PITFALL: `pkill -f "http.server 8080"` also matches the terminal wrapper whose command line
  contains that string, killing your own shell mid-script (SIGTERM, remaining commands never run).
  Kill by explicit PID from `pgrep`.

## Nagging the team for a score (bounded, self-muting)

The right shape for "spam the group until someone looks" is a `no_agent` cron job whose stdout IS the
message: zero LLM cost, and empty stdout sends nothing, so the script can mute itself. Working setup:
`~/.hermes/scripts/nag_preview_skor.py`, schedule `*/15 10-21 * * *` (host local = UTC+8, so
09:00–20:45 WIB), `repeat=12` (3 hours max), `deliver=whatsapp` (home channel = the team group),
`failure_deliver=local` (a dead tunnel must not spam the group with error notices).

- Mute signal = a HUMAN reply, not the bot's own output: any row in `state.db` `messages` joined to
  `sessions` where `source='whatsapp'`, `chat_id=<group>`, `role='user'`, `platform_message_id IS NOT
  NULL` and `timestamp > <frozen start epoch>`. Requiring `platform_message_id` excludes compaction
  artifacts and outbound/cron deliveries, which would otherwise mute the job instantly.
- PITFALL: with `WHATSAPP_REQUIRE_MENTION=true` an untagged group reply is DROPPED and never stored, so
  the nag would keep firing at people who already answered. Say it in the nag text: "balas sambil tag
  bot ya, biar pengingat ini berhenti sendiri", and keep the fire cap low.
- Do not promise @mentions: the bridge sends text only (no Baileys `mentions`), so "tag" in the message
  is an instruction to the humans, not something the bot performs.

## Tab penilaian (dibangun 30 Sep 2026)

Bangunan: `website/tab-penilaian/` — `pertanyaan.json` (satu sumber: 8 dimensi, 5 titik
skala, bobot, band, rekomendasi), `bangun_tab.py` (penanam idempoten, mencadangkan
`arsip/index-sebelum-tab-penilaian.html`), `uji_paritas.js`, `uji_data.js`, `uji_tab.js`,
`uji_rangkaian.js`, `uji_tepi.js`, `uji_pesan_bentrok.js`, `shot_tab.js`.

PITFALL yang memakan waktu — baca sebelum mengubah:
- **Markup ditanam di HTML, JS tetap merender.** Kalau pertanyaan sudah ada sebagai
  markup (supaya terbaca tanpa JS), jalur pembuat DOM harus dilewati
  (`if (!list.querySelector('.pen-q'))`) DAN pendengar klik/keydown harus dipasang di
  satu lintasan terpisah yang selalu jalan. Kalau pendengar hanya menempel di jalur
  pembuat DOM, tombolnya tampak normal tapi tidak bereaksi sama sekali.
- **Jangan pasang kelas pendek `.n`, `.bar`, `.rb` sebagai selektor baru** — halaman
  sudah punya `.n` (nomor peta bagian) dan `.bar` (halaman lain). Pakai awalan `.pen-`
  dan periksa `grep -c` sebelum/sesudah agar tidak menabrak gaya lama.
- **`index.html` tidak punya `</body>`/`</html>`** di ujung berkas. Penanaman apa pun
  harus menambahkannya sekali; jangan `replace("</body>")` yang jadi no-op senyap.
- Selektor atribut angka di Playwright wajib dikutip: `[data-nilai="5"]`, bukan `=5`.
- Verifikasi perubahan skor wajib lewat `uji_paritas.js` (JS vs `kalkulator_kesiapan.py`)
  **dan** `uji_tab.js` (23 pemeriksaan: kunci tombol, simpanan perangkat, muat ulang,
  ulangi, reduced-motion, HP). Skor acuan pola `4 3 5 3 2 3 3 2` = **65,0% · Layak Lanjut**.
- Ambang "rendah" satu tempat saja: `tingkat()` (1–2 rendah, 3 sedang, ≥4 tinggi).
  Jangan tulis `<= 3` di tempat lain — itu membuat penyorotan tak cocok dengan
  rekomendasi.

Keputusan yang diambil sendiri (bisa diubah user): 8 pertanyaan (bukan 32), hasil
dibuka penuh di situs, **tidak ada data yang dikirim/disimpan di server** (jawaban
hanya di `localStorage` perangkat; WhatsApp berisi skor + 8 jawaban yang dikirim oleh
pengunjung sendiri), band 20/40/60/80 dipertahankan.

### Hasil penilaian sampai ke tim lewat WhatsApp

- **Nomor di tombol hasil (`6288809640700`) adalah nomor bot Hermes itu sendiri** — cek
  identitas terhubung di `~/.hermes/whatsapp/session/` sebelum menjawab pertanyaan "hasilnya
  masuk ke mana". Artinya pengunjung yang menekan kirim masuk ke chat yang sama tempat Hermes
  bertugas; tidak perlu inbox atau nomor kedua.
- **Aturan tag hanya berlaku di grup.** Di DM, bot menjawab selama kebijakannya membuka DM
  (lihat `WHATSAPP_REQUIRE_MENTION` / `DM_POLICY` di `~/.hermes/config.yaml` dan
  `gateway/platforms/whatsapp_common.py`). Jangan menulis instruksi "tag bot dulu" untuk
  alur yang sebenarnya DM.
- **PITFALL yang bisa merusak skor klien: urutan dimensi di situs ≠ urutan yang dipakai
  bot saat mengalikan bobot.** Pesan hasil tidak boleh hanya berisi label prosa ("Strategi 4,
  Data 3, …") karena bot harus menebak pemetaannya. Kirim kunci mesin-terbaca yang stabil —
  `D1=4 D2=3 … D8=2` — bersama skor akhir, supaya bot bisa menghitung ulang dengan
  `kalkulator_kesiapan.py` tanpa menebak.
- **Skor dari situs adalah klaim, bukan bukti.** Alur yang benar untuk bot: terima skornya,
  hitung ulang, sebutkan selisihnya dengan jujur kalau ada, tanyakan 1–2 hal pembukti, lalu
  tutup ringkas (skor · band · 2 kekuatan · 2 celah · langkah pertama). Harga dan closing
  tetap milik tim.

Pratinjau yang dipakai saat membangun tab: `python3 -m http.server 8080 --bind 127.0.0.1`
plus cloudflared quick tunnel (proses sesi, bukan unit systemd) — hostnamenya berganti tiap
proses dijalankan ulang, jadi baca URL terakhir dari `/tmp/cf2.log` dan `curl` dulu
(cocokkan `md5sum` dengan `index.html`) sebelum dikirim ke user. Kalau user masih memakai
link itu setelah sesi ini, alihkan ke unit systemd di bagian handover.

### v1.1 — validitas hasil (dibangun 30 Sep 2026)

Tiga lapis yang membuat skor lebih bisa dipercaya, semuanya tetap jalan di perangkat
pengunjung (nol data ke server):

1. **Keyakinan per dimensi.** Tiap kartu pertanyaan punya baris "Seberapa yakin?" dengan
   `yakin` / `ragu` / `tidak_tahu` (definisi di `pertanyaan.json` → `keyakinan`). Disimpan
   di `localStorage` terpisah (`omnisense_penilaian_keyakinan_v1`), ikut ke pesan WA sebagai
   `keyakinan=D2:ragu,D8:tidak_tahu`, dan menyalakan catatan `#phLimit` di panel hasil.
2. **Pemeriksaan konsistensi.** `pertanyaan.json` → `aturan_konsistensi.aturan` memuat
   pasangan yang hampir mustahil terjadi bersama (R1: D2 tinggi + D3 rendah; R3: D5 tinggi +
   D6 rendah; R4: D7 tinggi + D3 rendah). Kalau terpicu, kotak `#penCek` muncul **di bawah
   daftar soal** (bukan di panel hasil — panel hasil ada di bawah, pengunjung tidak akan
   melihatnya), skor tetap dihitung, dan pesan WA menyertakan `catatan_situs=R1`.
   Tambah aturan baru = tambah entri di `pertanyaan.json`, tidak perlu ubah JS.
3. **Pesan mesin-terbaca.** Pesan WA kini diawali `[PENILAIAN-SITUS v1]` + baris
   `D1=.. D8=..` + `skor_situs=.. band=..` + `keyakinan=..` + opsional `catatan_situs=..`,
   baru ringkasan prosa. Urutan `D1..D8` WAJIB sama dengan `DIMENSI` di
   `kalkulator_kesiapan.py`; ini yang menghilangkan risiko bot salah memetakan jawaban.

Sisi bot: `/home/ubuntu/ai-agency/baca_penilaian.py` (`--teks "<pesan>"`, `--uji`) mem-parse
pesan itu, memanggil `kalkulator_kesiapan.py` untuk hitung ulang, lalu mengeluarkan JSON
(`skor_hitung_ulang`, `selisih`, `belum_pasti`, `catatan_situs`, `dua_terlemah/terkuat`,
`ringkas`). Aturan konsultan untuk DM berpenanda ada di skill `omnisense-consultant`.

Uji: baterai lengkap — `uji_paritas.js` (skor JS == `kalkulator_kesiapan.py`), `uji_data.js`
(data & aturan situs == `pertanyaan.json`, termasuk keakuratan teks aturan untuk SETIAP nilai
pemicu), `uji_tab.js` (perilaku tab), `uji_rangkaian.js` (mengambil `href` tombol WA **nyata**
dari browser, mengumpankannya ke `baca_penilaian.py`, mencocokkan skor), `uji_tepi.js` (ambang
band 20/40/60/80 tepat di batas, localStorage rusak, klik ganda, kirim ulang), `uji_pesan_bentrok.js`
(kotak peringatan). **Jangan menuliskan jumlah pemeriksaan di dokumen ini** — angkanya berubah
tiap kali suite ditambah dan yang tertinggal di sini menyesatkan; sebut nama suite-nya saja.
Semua harus hijau plus `verify_page.js` 0 error dan tanpa overflow 1440/390.

**Blocker yang masih terbuka (per 30 Sep 2026): jalur WA publik tertutup.**
`WHATSAPP_DM_POLICY=allowlist` di `~/.hermes/.env` (hanya 4 nomor tim) berarti DM dari calon
klien tidak pernah sampai ke Hermes — tombol kirim di situs mengirim ke ruang kosong. Perbaikan
satu baris + restart gateway; aktivator `ai-agency/aktifkan_jalur_wa.py` (default = rencana,
`--terapkan` menulis + mencadangkan `.env`, `--kembalikan` membatalkan). Jangan terapkan sendiri
tanpa persetujuan user: restart gateway memutus percakapan yang sedang jalan. Aturan isolasi tetap
aman karena persona `omnisense-consultant` hanya menjawab DM berpenanda `[PENILAIAN-SITUS v1]`.

## Paket deploy (30 Sep 2026)

`index.html` sekarang punya seluruh head untuk berbagi: `canonical`, `og:url`, `og:image`
(+width/height/alt), `og:locale`, `og:site_name`, `twitter:card`, JSON-LD `ProfessionalService`,
ikon 192px + `site.webmanifest`, dan tautan *Kebijakan Privasi* di kolom footer. Tautan footer dulu
mati karena `</head>` **hilang** dari berkas — `<style>` langsung menempel ke `<body>`; penutup itu
sudah ditambahkan, jadi penanaman berikutnya tidak boleh mengulang kesalahan itu.

Berkas baru di `website/`: `privacy.html` (ID+EN, tema A, memuat bagian "Penilaian kesiapan di situs"
yang menyebut jawaban hanya di `localStorage` perangkat, tanpa pelacak), `404.html`, `robots.txt`
(`Disallow: /pratinjau/` dan `/arsip/`), `sitemap.xml`, `site.webmanifest`,
`assets/og-omnisense.png` (1200×630, dibuat `scripts/buat_og.py`), `SERAH_TERIMA_DEPLOY.md` (daftar
berkas + perintah `rsync` + blok nginx + daftar periksa), dan skrip pratinjau `scripts/shot_final.js`
(situs) + `scripts/shot_legal.js` (privasi). Pratinjau resmi = `pratinjau/final-01..10*.png`; set lama
di `pratinjau/arsip-set-sebelum-deploy/`.

Yang tidak diubah: isi dan nada halaman. Ikon tombol hero diganti dari ikon WhatsApp ke
clipboard-centang (penilaian kini bisa diisi sendiri di situs), sedangkan tombol WhatsApp tetap ada di
nav, tab penilaian, dan CTA penutup.

- **KOREKSI (jangan ulangi klaim lama):** `tel:` di CTA **tidak** bertopeng. Berkasnya memuat 13 digit
  bersih (`tel:+6288809640700`) — tanda bintang yang terlihat di keluaran grep/terminal adalah
  penyaring privasi alat, bukan isi berkas. Klaim "tombol telepon tidak berfungsi" pernah ditulis di
  sini dan **salah**; sebelum melaporkan href rusak, buktikan dari byte mentah (`re.finditer(rb'\+62[0-9*]+')`
  atas `read_bytes()` + hash), jangan dari teks yang ditampilkan alat.
- **PITFALL pratinjau beranimasi:** `shot_final.js` dulu menunggu 1,8 s setelah klik `#penHitung`,
  sehingga cakram terpotret di tengah animasi dan pratinjau menunjukkan skor yang salah. Tunggu sampai
  keadaan akhir (≥4 s, atau `waitForFunction`), lalu render ulang seluruh set.
- **PITFALL vision di halaman ini:** model vision pernah melaporkan "tombol kembali tidak ada" pada
  tangkapan layar yang hanya memuat bagian atas halaman. Potret seluruh halaman atau periksa DOM dulu
  sebelum mengubah apa pun.

## Penyederhanaan tampilan — angka hiasan dibuang (30 Sep 2026)

Pemilik menilai halaman "terlalu ramai" karena elemen bernomor yang tidak menambah arti. Total **25
penanda** dibuang, tanpa mengubah satu kata pun pada isi:

| Bagian | Dibuang | Tetap |
|---|---|---|
| Rail peta bagian (`.ixbar`) | 8 label kecil ("4 langkah", "5 rentang", "8 bobot", "1-2 menit", "6 keluaran", "6 istilah", "2 proyek", "1 nomor") | nomor 01-08 + nama bagian |
| `#proses` | 4 angka raksasa latar (`.ghost`, duplikat tag "Langkah 01-04") | tag "Langkah 01-04" |
| `#output` | 6 nomor di kartu `.ocard` | judul + isi kartu |
| Footer | 7 nomor di daftar tautan | label "IG" / "PR" |

Sengaja TIDAK diubah: nomor 01-08 pada daftar pertanyaan penilaian (orientasi di form panjang), nomor
kartu Dimensi, dan persen bobot (itu data). CSS mati yang dibuang: `.ix .c`, `.step .ghost`.
**`.foot li span` DIPERTAHANKAN** — rule itu juga memberi jarak pada label "IG"/"PR"; membuangnya
membuat teks menempel jadi "IG@omnisense_id" (uji otomatis tetap hijau, hanya gambar banding yang
menangkapnya).

Cadangan: `arsip/index-sebelum-rapikan-angka.html`. Bukti: `pratinjau/rapikan-angka-{rail,proses,output,footer}.png`
(panel SEBELUM merah / SESUDAH teal). Catatan lengkap ada di `SERAH_TERIMA_DEPLOY.md` §11.

## Open decisions — ask, do not assume

1. ~~NeoSense on omnisense.id~~ — user keeps the domain as-is; **Vincent will move/replace it himself**.
   Do not re-raise it; build only.
2. ~~WhatsApp number / case study~~ — both supplied (see above).
3. Deploy: the agent machine has no access to the site's VPS — prepare the files and hand them over.
4. Do not re-open the theme decision. It is locked; B/C tokens stay archived unless the positioning
   changes (e.g. targeting corporate/BUMN accounts).
