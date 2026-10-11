---
name: motion-landing-page
description: "Use when building an animated or motion web page/site."
---

# Motion Landing Pages — Build and Verify

Use when the user wants a website/landing page **with motion**, or iterates on one they already have.

## Always-on rules

- **Deliverable = one self-contained HTML file.** Embedded CSS/JS, no build step, no CDN dependency, openable by double-click. State the absolute path in the reply. Port to a framework only when the user asks for production code — never start there.
- **Assume the visitor is on a phone on cellular data.** A background video or a full WebGL scene to explain a business is a fail, no matter how good it looks on your machine. A canvas point/line field, grain overlay, and CSS transforms give the same "alive" feeling at a fraction of the weight.
- **Every non-trivial animation collapses under `prefers-reduced-motion`** to its final state — content fully visible, loops stopped. Verify by emulating the media feature, never by reading your own CSS.
- **One accent color, used as the data/attention color** (score, bars, links, active rail) at roughly ≤5% of the page; everything else monochrome. Two accents or an aurora gradient is the fastest way to look like every other AI-agency template.
- **Ship a Tweaks panel** (small, unobtrusive, hideable) exposing at minimum accent on/off and motion on/off. This user decides by looking at live variants, not by reading a description of them.
- **Motion must be earned.** Each animation either reveals structure (scroll-linked progress rail, staggered list reveal), shows state (count-up score, gauge fill), or gives tactility (hover, cursor spotlight). Looping decoration with no informational job gets cut.
- **Commit to a surface archetype before styling.** A landing page is a Decide/Learn surface — a hero is correct there and almost nowhere else. Do not reuse the composition for dashboards or tools.

## Workflow

1. **Read the brand system before designing.** If the user has locked tokens (palette, fonts, ratios) in their own repo, those win; do not invent a palette next to an existing one. Note any *conflict* between two existing palettes and ask which is the parent rather than blending them into a third.
2. **Choose motion techniques and write the list with reasons** before coding — see `references/motion-technique-selection.md` for the technique frequency data and the use/avoid split.
3. **Build the single file:** CSS variables for tokens, grid layout, semantic HTML, `IntersectionObserver` for scroll reveals, `requestAnimationFrame` for canvas/cursor work, DPR capped at 2, particle/node counts scaled by viewport width, loops paused when the tab is hidden.
4. **Verify headlessly** with `scripts/verify_page.js` (see below).
5. **Visual QA the screenshots with the vision tool**, fix the concrete defects it names, then re-run the harness. Screenshots catch what computed-value assertions cannot: invisible tracks, low-contrast small text, elements below the fold on mobile.
6. **Report:** artifact path, techniques implemented, the verification numbers you actually got, and the open decisions for the user.

## Verification harness

```
node scripts/verify_page.js /path/index.html /tmp/qa \
  --eval "document.querySelector('#score').textContent" \
  --eval "getComputedStyle(document.querySelector('.bar i')).width" \
  --scroll-to "#steps" --click "[data-motion='off']"
```

- Needs `playwright-core`; point `PW_CORE` at an installed copy if it is not on the default resolve path. Chromium is auto-discovered under `~/.cache/ms-playwright` (override with `CHROME_PATH`).
- It runs four passes — desktop, desktop-scrolled, mobile 390px, and a `prefers-reduced-motion: reduce` pass — collecting console errors, page errors, horizontal overflow, `--eval` values, and screenshots into `report.json`. `--scroll-to "<selector>"` adds a pass with that element centred (scroll-linked rail and step state) and `--click "<selector>"` adds a pass that clicks a control first and then probes the state it produced (the motion on/off toggle). Those two flags are the difference between using this harness and re-writing it under /tmp.

### Pitfalls that cost real time here

- **Never trust a vision model's text transcription of a screenshot.** It silently mangles lowercase brand text and invents typos that are not in the file. Before editing any string it flags, grep the file for that exact string (`search_files`) — patch only if the file genuinely contains it. Fixing a hallucinated typo "corrects" correct text.
- **Vision calls rate-limit (429) when several screenshot analyses are fired in parallel.** Analyze one screenshot per turn and retry the same call later in the session instead of dropping the QA step.
- **Assert computed values, not impressions.** A page can screenshot beautifully while its JS never ran. Read the DOM after the animation settles — counter text, bar widths, arc `stroke-dashoffset`, number of revealed items.
- **Check horizontal overflow at both 1440 and 390.** Long mono labels, `white-space: nowrap` pills, and fixed-width cards are the usual culprits; `scrollWidth > innerWidth` is the assertion.
- **Kill low-contrast tracks.** A gauge or progress-bar track that is nearly the same value as the card behind it reads as a broken chart. Give tracks their own visible step in the ramp (e.g. `#34343C` behind a teal fill on a `#121215` card) and 4px+ height.
- **Center the number inside its ring.** A ring with the value sitting next to it, top-aligned to a text block, looks like two unrelated elements. Put the value in the ring's center via `display:grid; place-items:center`.
- **Small mono text needs a lighter slate than you think.** A dim grey that passes at 16px fails at 11px on near-black — use the lighter slate token and keep tiny labels at 12px minimum.
- **A motion-off / reduced-motion path must reach the same final state, not skip the intro.** If the entry function early-returns when motion is disabled, everything it would have triggered — score count-up, gauge arc, bar fills — never runs, and the users that guardrail exists for get a page showing `0%` and empty bars. Call the final-state setter explicitly on that path, and assert the values in the reduced-motion pass instead of only asserting "canvas is hidden".
- **Copy and behavior must match on the marquee pause.** Writing "stops when the cursor is over it" while only `pointerdown` sets `.paused` means hover does nothing and the promise is false. Use `.strip:hover .strip-track{animation-play-state:paused}` for pointer devices and keep the `pointerdown`/`pointerup` class for touch, then assert both: hover→paused, leave→running, tap→paused.
- **Fixed-width children in a flex row need a count derived from the container.** A tick rail built as a fixed 96 ticks overflows a 390px viewport and leaves a gap at 1440. Compute `n = floor((clientWidth + gap) / (tickW + gap))` on build and on resize, then assert the last child's right edge is within ~3px of the container's right edge — do not accept a vision model's "there is a gap at the right" without measuring the boxes.
- **A wide comparison table is the usual horizontal-overflow culprit, not the animated parts.** Isolate it by hiding each candidate element in turn and reading `document.documentElement.scrollWidth`. Fix below ~560px by collapsing the table to stacked blocks (`display:block` on `tr`/`td`, `thead` hidden) rather than shrinking the font.
- **A viewport-gated canvas must finish, not freeze.** If an `IntersectionObserver` stops a canvas that is mid-entry (score arc at 30%), the visitor who scrolls past quickly sees a half-filled gauge forever — the ring's length no longer matches the number. In `stop()`, if the entry sweep is incomplete, call the final-state setter before cancelling the frame. Assert it by scrolling past the canvas fast and reading the number back.
- **`white-space: nowrap` labels only fit where you tested them.** A row of five small mono category labels looked even at 1440 and pushed `scrollWidth` to 451 at 390. Fix with `flex-wrap: wrap` plus a smaller font under ~520px, then re-assert `scrollWidth === innerWidth` at 390 *and* 360.
- **A motion toggle must land on the same final state both ways.** After off→on the disc number, ladder number and bar values must all read their final values — if `start()` early-returns on an already-final sweep, the replay silently shows `0`.
- **Never put parallax on the same element as a reveal class.** An inline `transform` written by the scroll handler overrides the class's `translateY(0)` end state, so the element stays offset or the reveal silently never resolves. Wrap it: outer element takes the scroll transform, inner element takes the reveal.
- **Gate JS-set initial hidden states behind a `js` class on `<html>`** (one inline script in `<head>`), so a JS failure leaves the content visible rather than permanently at `opacity: 0`; mirror the same rules in the reduced-motion and motion-off blocks so all three paths land on the final state.
- **An IntersectionObserver scrollspy only fires on change.** Scroll back to the top and the last section's nav link stays highlighted forever, because no new entry arrives. Track a set of intersecting sections and clear every active link when the set empties.
- **Stagger slots must cover the real child count.** A delay list written for four children (`:nth-child(1..4)`) makes items five through eight appear simultaneously — count the list in the markup before writing the delays.
- **Make the motion toggle re-runnable.** Turning motion back on after off should replay the entry, so reset the animated properties to their start values with `transition: none`, force a reflow, then animate. Also expose the canvas as an object with `start()/stop()/clear()` — a loop started inside a closure with no handle cannot be restarted without a reload.
- **Before adding motion to an existing locked page, grep the theme for kill-blocks.** The user's locked theme may already switch off exactly the elements the motion needs (`#field, .ticks, .marquee { display: none !important }` was sitting in the theme's "turn off the most AI-looking things" section). The animation then runs perfectly and is invisible — and the result reads to the user as "the content doesn't match the first page", not as "the CSS hid it". `grep -n 'display: *none' index.html` and check for `!important` before writing a single line of motion, and delete only the rules covering elements you are reviving (leave watermark/grain rules alone).
- **When the user says "the content doesn't match the first page", diff the text, not the visuals.** Extract visible text from both files (strip `<script>`/`<style>`, tags to newlines, unescape, drop blanks) and assert the lists are equal. A build that appends CSS/JS around the original body must come out text-identical; if it doesn't, the pipeline is splicing the wrong region — here `head = cut('<html lang="id">', '<body>')` double-included `<style>` and quietly shipped a 117KB file with two stylesheets.
- **A vision model will report a sticky bar "covering" content in a full-element screenshot.** Screenshotting a long `#section` captures the fixed nav and sticky sub-bar *at their viewport position inside the tall image*, which reads as overlap that does not exist. Confirm with `getBoundingClientRect()` after the anchor click — if the section top is at or below `navHeight + stickyBarHeight`, the layout is fine and the complaint is an artifact of the capture method.
- **A vision model will describe a marquee as absent when it is merely below the fold.** It reported "no tick rail, no marquee" on a hero screenshot; both existed — the marquee sat at y=1092 (exactly one viewport down) and the rail's ticks were near-black-on-navy at that zoom. Read `getBoundingClientRect()` for the element and screenshot *that* element scrolled into view before believing "it isn't there".
- **Audit every `tel:` / `wa.me` / `mailto:` href for masked placeholders before shipping.** The rendered text can read perfectly (`+62 888-0964-0700`) while the href carries a redacted string (`tel:+628****0700`) — the page looks right and the tap silently does nothing. Grep the file for `tel:`, `wa.me`, `mailto:` and assert each one holds real digits. If the masking predates your edits, report it and ask before rewriting it: on a content-locked page the owner may have redacted it deliberately.
- **A preview screenshot of an animated number needs a wait on the final state, not a fixed timeout.** Capturing 1.8 s after clicking a "hitung" button caught the disc mid-count and the preview shipped a wrong score. Poll the DOM (`page.waitForFunction`) for the final value, or size the timeout to the longest animation in the sequence, then re-shoot the whole preview set — a preview with a stale number is what the user reviews and quotes.
- **Assert `</head>` and `</body>` both exist before inserting into a hand-written single-file page.** A page whose `<style>` runs straight into `<body>` (no `</head>`) swallows any meta/link injected "before `</head>`" — the splice reports success and the tags land nowhere or inside the body. Check the markers, and close the head once at the point of insertion if it is missing.
- **Do not hand-roll a throwaway verifier in /tmp when this skill ships one.** Extend `scripts/verify_page.js` (per-variant pass, query-string option, `page.click` on the variant control) — a one-off script dies with the temp directory and the next session re-invents it. Copy any screenshot the user is meant to open into the project directory, never leave it in `/tmp`.

## Variant systems (themes, tweak panels)

- **Build every option before asking the user to choose.** A variant that exists only as prose in a spec document is not a comparable option — implement it in the artifact first, then ask. Say which variants are live and how to open each.
- **Tokenize before adding a variant.** A live switch is impossible while colors are hardcoded: search the file for hex literals and `rgba(` and move each to a custom property on `:root`, with per-variant blocks overriding only tokens. A token that gets an alpha must hold channels, not a whole color (`--panel-rgb: 18,18,21` → `rgb(var(--panel-rgb) / .82)`).
- **`var()` is ignored in SVG presentation attributes.** `stroke="#34343C"` and friends never resolve custom properties — write `style="stroke:var(--line-2)"`, or the graphic keeps the default theme's color forever.
- **Canvas reads its color at draw time.** Pull the token with `getComputedStyle(...).getPropertyValue('--signal')` inside the draw/init path, not once at module load, or the canvas stays on the old accent after a switch.
- **Make variants addressable and sticky — both.** `index.html?tema=b` for the link you send and for screenshots, localStorage so a reload keeps the choice.
- **Variants are a decision instrument, not a shipping feature — lock the winner.** The moment the user picks one, or hands you the choice ("you pick the best, just do it"), delete the switcher: hard-code the winning tokens, strip the query-string/localStorage plumbing and the per-variant override blocks, and keep only the motion on/off control (that is an accessibility preference, not a design decision). Archive the losing tokens in the spec doc and their screenshots in `pratinjau/arsip-*/` so the decision stays auditable and reversible without redoing the research. A live theme switcher on a real site reads as unfinished work, and every later edit then has to be checked against variants nobody ships.
- **When the user delegates the choice, decide and execute in the same turn.** Rank the options by what they do for the product (does the accent carry meaning or decorate?), state the reason in one line each, then build it. Do not come back with a shortlist and a request for confirmation — that is the outcome they delegated away from.
- **Re-run the harness on the default variant after adding a variant.** The default is the regression baseline; a token refactor that breaks the theme nobody was re-checking is the usual failure.
- **Contrast-check strokes and small labels per variant, not just body text.** A track/rail/gauge stroke that melts into the card reads as a broken chart while the code looks fine — compute the WCAG ratio of each stroke against that variant's card color and lighten it for dark navy/blue surfaces.
- **Report the decision, not the diff.** File path, how to open each variant, the verification numbers actually returned, and the single decision left for the user.

## Interactive sections in a single-file page (scored forms, quizzes, assessment tabs)

When the page must *do* something — an assessment the visitor fills in and gets a score from — the
work is not the animation, it is the double-path render and the number parity. Full recipe and test
checklist: `references/interactive-scored-form.md`.

- **Markup in HTML *and* a JS renderer is a two-path trap.** Shipping the questions as real markup (so
they are readable with JS off) while the script also builds them produces either duplicated lists or — worse — a page whose 40 controls look normal and do nothing, because the click/keydown listeners were attached only inside the DOM-builder branch. Guard the builder (`if (!list.querySelector('.q'))`) and attach all listeners in a separate pass that always runs, over `list.querySelectorAll('.q')`.
- **Namespace every new class with the section prefix.** A page that already has `.n` (section-map numbers) or `.bar` will silently restyle them when a new widget reuses those names. Use `.pen-*`-style prefixes for the new block, and `grep -c` the class before and after the insert to prove you did not touch an existing selector.
- **`replace('</body>', …)` can be a silent no-op.** Hand-written single-file pages are often missing `</body>`/`</html>`. Assert the marker exists before replacing, or append the new script and close the document once at the end — otherwise the injection reports success and nothing is in the file.
- **When the page reimplements a number the team also computes elsewhere, prove parity.** Score, band, and rounding must match the canonical script exactly, or the site contradicts what the team says on a call. Write a small node script that runs the same answer vectors through both and compares, including the band *boundaries* (below, at, and above each threshold) — see the reference for the harness shape. Assert the reference score in the UI test too, not just "a number appeared".
- **One classifier function, one threshold.** If `tingkat(n)` already defines low/medium/high, do not write `n <= 3` again in the highlight logic — the two drift and the emphasised rows stop matching the recommendations. Derive emphasis by calling the classifier.
- **A self-serve score needs a validity layer before it is worth anything to the receiving team.** Three parts, all client-side: a confidence control per item ("yakin/ragu/belum tahu"), consistency rules declared in the data file that flag contradictory pairs without changing the score, and a machine-readable hand-off block (marker line, fixed `Dn=v` order matching the canonical calculator, claimed score, flags) ahead of the prose. Put the consistency notice directly under the question list — the visitor does not scroll to the result panel. The receiving side must RECOMPUTE the claim from the `Dn` values and report any difference rather than echoing it; test that round-trip by feeding the button's real `href` into the parser.
- **Keep the visitor's data on the device by default.** Answers in `localStorage` under a versioned key, nothing posted to a server, and the hand-off (WhatsApp/email) is a link the visitor presses carrying score + their own answers. State this to the user as a decision they can reverse; it is what makes the feature shippable with no backend and no personal-data exposure.
- **Assert the interactive states headlessly, not visually.** Disabled-until-complete button, progress counter, persistence across reload, reset, `prefers-reduced-motion`, and a 390px pass — a green screenshot proves none of these.
- **Playwright attribute selectors with numeric values need quotes:** `[data-nilai="5"]`, never `[data-nilai=5]` — the unquoted form is a selector syntax error, not a fallback match.

## Decluttering a locked page (presentation edits)

"Terlalu ramai" / "too many numbers" is a **presentation** request: change the chrome, not a word of
the copy. This user decides by looking, so the deliverable is a before/after image pair, not a
description.

1. **Inventory before editing.** Count the numbered elements and group them by job (section map,
   step tags, card indices, weight percentages, footer list). Report the groups and the count, then
   ask which groups to cut — one multi-select question, recommended option first.
2. **Keep the numbers that orient, cut the ones that decorate.** Question numbering in a long form
   ("I am on 5 of 8"), per-card indices on data cards, and weight percentages (that is data) stay.
   Ornamental repeats go: small count labels beside a nav item ("4 langkah"), oversized ghost
   numerals that duplicate a visible tag, indices on a card grid nobody reads in order, and numbered
   footer link lists.
3. **Back up first** to `arsip/index-sebelum-<perubahan>.html` without overwriting an older backup, and
   edit with a script that reports the replacement count per group (`re.subn`), not by hand.
4. **Verify: test battery → harness → regenerated previews → the live link.** The last one is the one
   people skip: `curl -s <tunnel>/index.html | grep -c '<old pattern>'` must return 0, or the URL you
   are about to re-send is still serving the previous build.
5. **Build the before/after image** (red SEBELUM panel over teal SESUDAH panel, Pillow) and read it
   with the vision tool.

Pitfalls that cost time here:

- **Before deleting a CSS rule, grep for the selector's other users.** One rule can serve both the
  markup you are removing and markup that stays: `.foot li span` gave the footer link numbers their
  gap *and* spaced the "IG"/"PR" labels, so deleting it shipped "IG@omnisense_id". `grep -c 'class="<kelas>"'`
  across the file first; if a surviving element still uses it, drop only the markup and keep the rule.
- **A compositing step that fails silently leaves the previous image on disk, and vision then reports a
  defect you already fixed.** Run the image build as its own command, confirm it printed the output
  path, and check the file's mtime before interpreting what the vision model sees. Screenshot the
  element itself (`element.screenshot()`), not the full page, when judging a small component.
- **An automated suite can stay green through a real visual regression** (the removed-gap case above
  passed every test). The vision read of the before/after image is the layer that catches it — it is
  not optional polish.
- **A rail that scrolls horizontally on mobile is not "cut off".** Check the CSS for `overflow-x:auto`
  before treating a clipped edge item in a 390px screenshot as a bug you introduced.

## Anti-slop list for this class

Cut outright: background video, 3D orb/WebGL hero, glitch or RGB-split text, SPA page transitions on a one-pager, 3D tilt cards, smooth-scroll libraries. Marquee is allowed only as a thin strip below the hero, never as the hero itself (the text inside is unreadable on a phone). Kinetic headline reveals and grain/noise overlays are cheap and rare enough to be distinctive.

## Handing over a preview link

When the user asks for a "link preview" of a local file (no deploy access to their VPS), serve the
directory and tunnel it — do not hand over a `file://` path or `localhost`:

```
terminal(background=true)  cd <dir> && python3 -m http.server 8080 --bind 0.0.0.0
terminal(background=true)  /tmp/cloudflared tunnel --url http://localhost:8080 --no-autoupdate
# read the assigned https://<words>.trycloudflare.com from the process log
curl -s -o /tmp/t.html -w '%{http_code} %{size_download}\n' https://<words>.trycloudflare.com/
```

- Fetch the tunnel URL back with `curl` before sending it: a URL that appears in the log can still be
  unreachable, and a 200 with the expected byte count is the only proof it works.
- A raw inbound port on the agent machine is firewalled (verify with an external fetch proxy, e.g.
  `https://r.jina.ai/http://<ip>:8080/` → 422/timeout). Tunnel or nothing.
- Quick tunnels are ephemeral: the URL dies when the process stops. Say so when you send it.
- cloudflared binary if missing: `curl -sL -o /tmp/cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 && chmod +x /tmp/cloudflared`.

## Shipping the page as a real site (deploy package)

A single-file landing page is not yet a site. Before handing it to whoever owns the server, complete
it to a deployable package and write the handover doc — the page alone will 404 its own assets and
have no privacy page to point at.

1. **Inventory the package:** `index.html`, plus `privacy.html`, `404.html`, `robots.txt`,
   `sitemap.xml`, `site.webmanifest`, `assets/` (logo, favicons, `og-<brand>.png`).
2. **Generate the OG card as a real PNG (1200×630) with a script, not by hand** — brand background,
   wordmark from the master logo PNG, the site's headline, no clipped text.
3. **`robots.txt` disallows the working folders** (`/pratinjau/`, `/arsip/`) so preview screenshots and
   pre-change backups never get indexed.
4. **Any page that collects visitor input needs a privacy page**, linked from the footer. Disclose the
   storage mechanism explicitly (e.g. answers stay in `localStorage`, nothing posted to a server, no
   trackers) — that disclosure is what makes a client-side-only feature defensible.
5. **Verify every local reference resolves** (`grep -o 'assets/[^"]*'` against the filesystem, plus the
   manifest's icons) — an `index.html` that depends on `assets/` is no longer self-contained, and the
   missing file only shows up as a console 404 on the server.
6. **Write the handover doc** (file list, copy command, the server block, checklist) and say plainly
   which step you cannot do from this machine (uploading) and who owns it.

Detail — file inventory, the nginx block, the OG-card recipe and the pre-handover checklist:
`references/deploy-package.md`.

## Files

- `references/motion-technique-selection.md` — technique frequency data from a public motion-template catalog, the research method, and the use/avoid decision table.
- `references/scroll-linked-motion.md` — verified formulas for scroll-linked motion: progress-rail mapping and step thresholds, hero parallax layers and fade, right-edge tick rail, scrollspy, canvas gating.
- `references/omnisense-website.md` — the user's live OmniSense site: chosen tokens, file paths, the assessment-tab build, open decisions. Read this before touching that site.
- `references/interactive-scored-form.md` — adding a scored form/assessment section to a single-file page: dual-path render, scoring parity harness, state checklist, hand-off link.
- `references/deploy-package.md` — turning the finished single-file page into a deployable package: file inventory, OG card recipe, nginx block, privacy page, handover checklist.
- `scripts/verify_page.js` — the headless verification harness described above.
