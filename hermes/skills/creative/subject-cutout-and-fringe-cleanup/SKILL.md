---
name: subject-cutout-and-fringe-cleanup
description: "Cut a subject out of a photo; clean alpha & color fringe."
---

# Subject cutout & fringe cleanup

Cutting a person/product out of a photo so it can sit on a designed background. The
generated alpha is never clean on the first pass — the work is in alpha cleanup and
color-fringe removal, then verifying it objectively instead of by eye.

## Procedure

1. **Cut once, cache the transparent PNG.** Run the matte model a single time and save the
   RGBA result; every later render reuses the cache (instant) instead of re-running the model.
2. **Clean the alpha.** Keep the largest connected component (scipy `label`) to drop stray
   blobs the model grabbed — a chair, a stage, another person in frame. Then feather the edge.
3. **Decontaminate the edge.** Where the subject met the old background, the old color bleeds
   into semi-transparent pixels. Neutralize it before compositing or it shows as a halo.
4. **Neutralize background-hue fringe** (see below) — the step most often skipped.
5. **Verify objectively** (see below) — do not trust a vision QA pass alone.
6. **Composite and re-render.**

## Model choice

- Use **`u2net`** for production quality, **`u2netp`** only for fast/rough tests.
- **Do NOT use very large models (≈1 GB, e.g. `bria-rmbg`) on CPU** — they exceed 200 s and
  time out. u2net/u2netp finish in ~10–30 s. (rembg lets you pick via env, e.g. `REMBG_MODEL`.)
- The cache (step 1) solves repeat renders, but not the first cutout — budget for the first one.

## Edge handling

- **Avoid aggressive erosion.** Eroding alpha to kill a halo punches holes in fine detail
  (hair, thin edges). Prefer a thin neutralization pass over erosion.
- Feather after cleaning, not before — feathering a dirty mask smears the artifacts.

## Color fringe (the recurring killer)

A colored background element (a logo, neon sign, colored wall) leaves a **thin tinted halo**
that survives the cutout and sticks to hair/edges. Neutralize it by hue: any pixel where the
background hue dominates is not skin/hair, so replace it with neutral luminance.

For a green background, catch **two** patterns — the second is the one that gets missed:
- **Pure green:** `G > R + k` and `G > B + k`.
- **Yellow-green fringe:** `|R - G| <= 30` and `G > B + 22` and `R > B + 22`.

The pale yellow-green fringe is the most common survivor and the most visible at the hairline;
a pure-green-only test lets it through. The `R > B` / `G > B` guards keep skin (which has a
large R−G gap) from being caught. Generalize the same idea to any background hue.

## Verification — count pixels, don't just look

Vision QA **miscounts color artifacts**: it reports "still green" on a clean cutout, or "clean"
while a pale fringe remains. Do not loop regenerating on a vision verdict alone.

- **Count objectively:** load the RGBA with numpy and count pixels matching the fringe patterns.
  Zero = clean. If the count and the vision verdict disagree, trust the count.
- **Inspect on a white background:** composite the cutout over solid white before visual review —
fringe is far more visible against white than against a dark/designed background.
- **Zoom the suspect region** (e.g. the head/hairline) at 2–3× before declaring it clean.

## Pitfalls

- **Single-pattern fringe test:** only checking pure hue dominance misses the pale fringe; always
  include the second (low-saturation) pattern.
- **Regenerating on a vision "still dirty" verdict without measuring:** wastes runs when the
  cutout is already clean. Measure first.
- **Eroding to hide a halo:** creates holes in hair; neutralize the fringe instead.
- **No cache:** re-running the model on every render is what makes cutout pipelines feel slow.
