# Interactive scored form inside a single-file page

For an assessment/quiz/score widget embedded in a hand-written one-file landing page: the visitor
answers N questions and the page computes a score locally. The failure modes are all in the render
path and in the numbers, not in the styling.

## Build order that works

1. **One data file is the source of truth** (e.g. `tab-penilaian/pertanyaan.json`): per item — code,
   dimension name, weight, question text, the five scale points as `{n, teks}`, and the recommendation
   text per level. Keep weights and band thresholds in the same file, with a comment naming the
   canonical script they must match.
2. **A generator script that plants the section into the page** (`bangun_tab.py`-style):
   - backs the page up to `arsip/` first,
   - is idempotent — detect its own marker (`if '#penilaian' in s: exit`) and exit untouched,
   - injects markup **and** the JSON as a `window.__DATA__` script **and** the behaviour script,
   - asserts every anchor string it replaces actually exists before replacing (a silent no-op looks
     exactly like success in the log).
3. **Markup carries the questions; the script carries only behaviour.** Markup-first is what makes the
   section readable when JS is off. The script must therefore *not* rebuild the list when it is already
   present, and must attach listeners in a pass over the existing nodes.

## The two-path render trap (the one that costs the most time)

```js
// builder: only when markup is absent
if (!list.querySelector('.pen-q')) DATA.dimensi.forEach(function(d, i){ /* create nodes */ });

// listeners: ALWAYS, over whatever nodes exist
list.querySelectorAll('.pen-q').forEach(function(li){
  var kode = li.getAttribute('data-kode');
  var grup = li.querySelector('.pen-opts');
  Array.prototype.forEach.call(grup.querySelectorAll('.pen-opt'), function(b){
    b.addEventListener('click', function(){ pilih(kode, +b.getAttribute('data-nilai'), b, grup); });
    b.addEventListener('keydown', /* arrow-key roving tabindex */);
  });
});
```

Symptom when only the builder branch attaches listeners: every control renders, hovers and focuses
correctly, and clicking does nothing at all — with no console error. The disabled submit button then
never enables, so a click-based test times out on `#submit` and the cause looks like the disabled logic.

## Scoring parity harness

When a team script (Python, spreadsheet) computes the same score, prove the page agrees.

```js
// uji_paritas.js — same answer vectors through the page's scorer and the canonical script
const VEKTOR = [[4,3,5,3,2,3,3,2],[5,5,5,5,5,5,5,5],[1,1,1,1,1,1,1,1],[3,3,3,3,3,3,3,3],[5,4,3,2,1,5,4,3]];
// also probe the band BOUNDARIES: threshold-1, threshold, threshold+1
```

- Compare to 1 decimal place, and compare the band label as a string.
- Record the reference score in the UI test as a literal (pattern `4 3 5 3 2 3 3 2` → `65.0% / Layak
  Lanjut` in this project) so a weight refactor cannot pass silently.
- Re-run it on every change to weights, bands, or the scorer.

## Making a self-assessment result trustworthy (validity layer)

A self-serve score is only as good as its weakest answer. Before handing the result to a human or a
backend, add these three, all still client-side (no data leaves the device):

1. **Confidence per item.** Each question carries a second small control (`Yakin / Ragu / Belum tahu`)
   in the same card, stored under its own versioned key, and echoed in the hand-off as
   `keyakinan=D2:ragu,D8:tidak_tahu`. The result panel then says which dimensions are uncertain instead
   of presenting a guess as a measurement. Do not gate or down-weight the score on this — it is a
   caveat, not a fudge factor the visitor cannot see.
2. **Consistency rules that flag, never punish.** Pairs of answers that are almost impossible together
   (high data readiness + no infrastructure; strong culture + no governance) are declared **in the data
   file** as `{kode, bila: {...}, pesan}` and evaluated after the score. On a hit, keep the score, show
   an inline notice, and put `catatan_situs=R1` in the hand-off. New rules = data edit, no JS change.
   Evaluate per rule (each has its own message); do not collapse them into one generic "answers look
   inconsistent".
3. **A machine-readable hand-off, not just prose.** The message the visitor sends becomes:

```
[MARKER v1]
D1=4 D2=3 D3=5 D4=3 D5=2 D6=3 D7=3 D8=2
skor_situs=65.0 band=Layak Lanjut
keyakinan=D2:ragu,D8:tidak_tahu
catatan_situs=R1
<prose summary for the human>
```

   Marker line so the receiving agent can branch on intent; then fixed key order, one line per group,
   spaces (not commas) between `Dn=v`; prose last. The `Dn` order MUST equal the canonical dimension
   order in the team's calculator — if the site reorders or inserts a dimension, weights silently map
   to the wrong question and no error is raised anywhere.

**Where the notice goes matters more than how it looks.** The consistency warning belongs directly
under the question list (where the visitor is still looking), not in the result panel far below the
fold — a warning nobody scrolls to is the same as no warning.

## Recompute the claim on the receiving side

The hand-off link is a **claim**, not a fact. Ship a small parser on the receiving side (Python is
fine) that reads the marker, re-runs the canonical scorer on the `Dn` values, and returns JSON:
`{skor_klaim, skor_hitung_ulang, selisih, band, belum_pasti, catatan_situs, dua_terlemah, dua_terkuat,
ringkas}`. The agent then reports any `selisih` out loud rather than echoing the visitor's number, and
spends its follow-up questions only on the dimensions flagged uncertain or inconsistent. Return
`dikenali=false` for a body without the marker so the caller falls back to normal conversation
instead of guessing a score.

Then test the real artifact across the language boundary, not a hand-written fixture: a node script
drives the page, reads the **actual `href` of the hand-off button** after answering, feeds the decoded
text into the parser, and asserts the parser's recomputed score equals the page's. This is the only
test that catches a message-format change made on one side only.

## Headless interaction checklist

A screenshot proves none of these. Drive the real controls with Playwright and assert:

| Check | Assertion |
|---|---|
| items rendered | `#list .pen-q` count === expected |
| options rendered | `.pen-opt` count === items × scale points |
| submit gated | `#submit.disabled === true` before answering |
| progress | counter text `0 dari 8` → `8 dari 8`; bar width `100%` |
| selection state | `aria-checked="true"` count === items; answered-class count === items |
| persistence | `localStorage[<versioned key>]` non-null after answering |
| reload | after `page.reload()` counter and checks are restored |
| reset | after reset: counter 0, submit disabled, checks 0, storage key null |
| result | result container `hidden === false`; score text matches the literal |
| ordering | weakest-first list: first row is the expected dimension |
| highlight | emphasised row count equals what the classifier produces |
| bars | every bar `style.width` non-empty and not `0%` |
| hand-off | `decodeURIComponent(href.split('text=')[1])` contains the score and the per-item answers |
| hand-off machine block | decoded text starts with the marker, then `Dn=v` in canonical order, `skor_situs`, `keyakinan`, optional `catatan_situs` |
| confidence control | one active confidence button per item; its choice survives reload under its own key |
| consistency rule | an answer vector chosen to trip a rule shows the notice, keeps the score, and adds the rule code to the hand-off |
| claim round-trip | the real `href` text fed to the receiving-side parser yields `selisih === 0` against the canonical script |
| reduced motion | final score identical to the animated run |
| mobile 390px | final score identical |
| console | zero page errors and zero console errors across all passes |

Playwright notes: numeric attribute selectors must be quoted (`[data-nilai="5"]`); size
`waitForTimeout` to the entry animation before reading an animated number, and keep it short on the
reduced-motion pass; screenshot the *section element* (`locator('#section').screenshot()`) rather than
the page — a full-element shot of a long section pastes the fixed nav and sticky sub-bar into the
middle of the image and reads as phantom overlap.

## Class-naming and integration pitfalls

- Prefix every new class (`.pen-*`); `grep -c` the class name before and after the insert so a
  collision with an existing `.n`, `.bar`, `.row`, `.card` shows up immediately.
- Anchor-scroll offset: if the page already has `scroll-margin-top: calc(var(--navh) + Npx)` on
  sections, the new section inherits it. Verify by clicking the nav link and reading the section's
  `getBoundingClientRect().top` against `navHeight + stickyBarHeight` — never judge it from a
  screenshot.
- Add the new section to the section-map bar and to the scrollspy id list in the same edit, and
  renumber the map's step labels — an unlisted section silently never highlights.
- Adding a section mid-page means renumbering the surrounding `01…08` eyebrows and updating hero
  button/hint copy to match the new flow ("starts on WhatsApp, ~12 min" is false once a self-serve
  form exists). Then diff the visible text against the pre-change backup, list exactly which strings
  changed, and tell the user those changed on purpose — otherwise it reads as content loss.
- Privacy default: answers stay in `localStorage`, nothing is posted, the hand-off is a link the
  visitor presses. State this explicitly as a reversible decision.
