# Poster backdrops: relevant photography without breaking a locked template

For brand posters that must not look flat ("jangan polos") while the layout,
fonts and palette stay locked. Only the backdrop layer changes; the template is
never re-authored to accommodate the photo.

## Sourcing
- Wikimedia Commons search API, bitmap files only:
  `action=query&generator=search&gsrsearch=<kw> filetype:bitmap&prop=imageinfo&iiprop=url|extmetadata`.
  Google Images and screenshots of other people's posters are NOT usable sources.
- **Keywords must be concrete objects** ("keyboard keys close", "server room data
  center", "warehouse shelves"), not abstract concepts ("efficiency", "growth") —
  abstract queries return diagrams and clip-art that read as noise.
- **License filter: accept only CC0 / public domain / CC BY. Reject CC BY-SA, NC
  and ND automatically.** A promo poster is a derivative work, so share-alike would
  encumber the brand's own artwork and NC forbids the commercial use outright.
  Filter on the license string, and keep the metadata that proves it.
- CC BY requires attribution: append a small credit line at the end of the caption
  (`Photo: <title> (<license>) — Wikimedia Commons`). CC0/PD need none.
- Save the downloaded file plus its attribution JSON so the credit can be rebuilt
  later without re-querying.

## Compositing order (each step is load-bearing)
1. cover-crop the photo to the poster ratio (no letterboxing, no distortion).
2. blur — the backdrop must not compete with the text.
3. darken by an explicit dim factor.
4. vignette, then **dark scrim bands across the header and headline/footer zones**.
5. glass card = blur the backdrop region behind the card + translucent fill.

- **Re-create the draw object after any step that returns a new canvas** (blur,
  resize, paste). A draw handle bound to the old object silently writes nothing
  from that point on — the symptom is every element after the card disappearing.
- Draw the card rectangle BEFORE the text inside it, and compute the card height
  from measured wrapped text rather than a fixed value.

## Legibility on a photo (the recurring QA complaint)
- A photo raises the backdrop's floor luminance, so secondary slate-grey text that
  is comfortable on flat dark canvas sinks into busy areas. Reviewers flag the
  date line, card body, sub-headline and footer over and over.
- Fix: brighten the secondary-text tone and add a 1px dark shadow to the
  sub-headline **only when a backdrop is active**; keep the flat-canvas palette
  exactly as it was.
- **Regression-test both modes after touching the palette**: render with and
  without a backdrop and confirm the flat version is byte-for-byte the old look.
- Too-bright backdrop: print the backdrop's mean luminance during render and warn
  above a ceiling, then re-render with a higher dim factor (0.62 → 0.70 → 0.78)
  instead of guessing.

## Verification when vision QA is unavailable
- Vision analysis is rate-limited in bursts (HTTP 429) exactly when iterating on
  renders. Keep an objective check that needs no model:
  `python -c "from PIL import Image, ImageStat; im=Image.open('out.png').convert('L'); print(ImageStat.Stat(im).mean[0], ImageStat.Stat(im).stddev[0])"`
  — high stddev = textured backdrop really composited; near-zero = flat render.
- Also assert the render log line naming the backdrop file, its luminance and dim.
- Re-run the vision pass for the final candidate when the limit clears.

## Pitfalls
- **Never use a screenshot of another outlet's poster as a backdrop.** Its text
  stays legible through the blur/dim and collides with your message, plus it is a
  copyright problem. The backdrop must be text- and logo-free.
- **No clean, relevant image → render flat.** A mismatched photo is worse than a
  plain canvas; never force one to satisfy a visual checklist.
- AI image generation is an alternative source but must be verified live before it
  is written into a pipeline — a provider listing models does not mean an image
  endpoint is served.
