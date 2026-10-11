# Motion Technique Selection (with data)

Use this when choosing which motion techniques to build. The numbers come from counting technique
keywords across the public catalog of a motion-template gallery (motionsites.ai, table
`prompts_public`) — 526 items, 179 free / 347 paid, dominated by hero sections (`hero` 388,
`mobile` 40, `features` 38).

## Research method (repeatable, metadata-only)

- Read the **public catalog metadata** (title, category, type, keywords, free/paid). Do **not** scrape
  or reproduce paid prompt bodies; the point is to count what the market does, not to lift content.
- Count technique keyword hits across the whole keyword blob to get a frequency table — this is how
  you tell a real trend from a hunch.
- To judge *look*, download the **public previews** and stack each one's frames into a contact sheet,
  then read the sheet with the vision tool (composition, dominant color, what changes between frames).
- Cross-check the conclusion against the user's own locked brand rules; popularity is not a reason to
  adopt something that fights the brand.

## Frequency observed (out of 526 items)

| Technique | Hits | Read |
|---|---|---|
| Framer Motion / `motion/react` | 103 | industry default for React builds |
| Video background | 92 | most popular *and* heaviest |
| Scroll-driven / sticky / parallax | 78 | the core of the modern feel |
| WebGL / Three.js / canvas / shader | 78 | most expensive per device |
| Gradient / glow / aurora / mesh | 48 | the "generic AI site" marker |
| Glassmorphism / backdrop-blur | 38 | fine in small doses |
| GSAP / Lenis / smooth scroll | 22 | overkill for one page |
| Grid pattern / noise / grain | 18 | cheap, high perceived quality |
| Marquee / ticker | 9 | strip only |
| 3D tilt cards | 7 | gimmick |
| Custom cursor | 6 | desktop only |
| Kinetic typography | 4 | rare — therefore a differentiator |

Roughly half the catalog targets agency/AI/consultant/studio/dark positioning. The dark + glass +
glow + video recipe is saturated; following it means blending into hundreds of near-identical pages.

## Two reference archetypes worth understanding

**Monochrome dark editorial** ("obsidian" style hero) — near-zero saturation, bone-white type, one
large visual mass, asymmetric layout (text 35–40% left, visual right/lower), floating cards as the
front layer, a tick-mark scroll progress indicator, fine grain texture. The hero is pinned and
re-rendered along scroll (reveal + inter-layer parallax).

- Take: asymmetric text/visual split, grain, tick-mark progress, layered floating cards.
- Leave: the morphing 3D mass — it needs video or WebGL.

**Neon 3D tech hero** — pure black, everything centered, glowing violet/magenta 3D object, particle
field, point-cloud morph, "watch it unfold" play button.

- This is the look to *avoid* for a consultancy that sells measurement: it explains nothing, reads as
  expensive-but-vague, and is the heaviest option on a phone. Note also that "everything centered"
  is the compositional tell — the composition is the problem, not the color.

## Decision table

**Use**

| Technique | Why |
|---|---|
| Scroll-linked reveal (IntersectionObserver + stagger) | Gives reading order; no library |
| Kinetic headline (word-by-word mask reveal) | Rare in the market, cheap to build |
| Canvas point/line field | The "alive" feeling of a video hero at a fraction of the bytes |
| Count-up number + bars filling on entry | Animates the actual product claim, not decoration |
| Progress rail that grows with scroll | Explains a sequence with no extra copy |
| Marquee strip (capabilities/clients) | Compact, pauses on hover |
| Thin glass card (1–2 places) | Depth without weight |
| Grain/noise overlay | Cheap, immediately raises perceived quality |
| Cursor spotlight (desktop, off on touch) | Last touch of premium |
| Preloader under ~1s, skippable | Only if it never delays reading |

**Avoid**

| Technique | Why |
|---|---|
| Video background | Multi-MB on first load; target audience is on cellular |
| Full WebGL / Three.js scene | Battery and GPU cost on mid/low-end phones for little explanatory gain |
| Glitch / RGB split / text scramble | Fights the credibility a consultant sells |
| SPA page transitions | One-page site: large cost, zero benefit |
| 3D tilt cards, smooth-scroll libraries | Gimmick; adds JS without adding understanding |
| Aurora/mesh violet gradients | The clearest "AI-generated site" marker |
