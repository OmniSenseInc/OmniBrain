# Scroll-linked motion — verified recipes

The numbers below were measured in a headless Chromium pass on a 1440x900 viewport against a
single-file site with a 4-step rail, a hero panel, and a canvas background. They are starting points
that already behaved well, not guesses — assert them with the harness rather than eyeballing.

## Progress rail for a multi-step section

Two failure modes: the rail hits ~90% while the section is merely centred (mapping too aggressive), or
it never completes before the section leaves (too shy).

```js
// r = section.getBoundingClientRect(), vh = window.innerHeight
const p = Math.max(0, Math.min(1, (vh * 0.95 - r.top) / (r.height + vh * 0.6)));
rail.style.width = (p * 100) + '%';
```

Do NOT use `(vh * 0.85 - r.top) / (r.height + vh * 0.25)` — measured 90% fill with the section only
centred, so the last step lit up before the reader got there.

Drive the step dots from the same `p`, never from a second observer, so the number and the line agree:

```js
const STEP_AT = [0.06, 0.32, 0.58, 0.84];
stepEls.forEach((el, i) => el.classList.toggle('on', !motion || p >= STEP_AT[i]));
```

Measured with the formula above: **13% / 1 step on entry -> 69% / 3 steps centred -> 100% / 4 steps**
once the section passes. With `!motion` every step is lit immediately.

## Hero parallax — three layers, one scroll handler

```
text 0.14x    canvas 0.08x    score panel 0.05x
```

Different rates are what read as depth; equal rates just look like the page scrolls wrong. Write all
three inside the same rAF-throttled handler that updates the rail (one `passive` scroll listener, a
`ticking` flag) and keep `will-change: transform` on those three elements only.

Fade the hero copy out with `1 - (y / heroH) * 0.95`. A factor near 1.35 makes the subhead and CTA
unreadable while they are still on screen (measured 0.37 opacity at 420px of a 900px hero).

Give the hero `overflow: clip` so the translated canvas cannot create horizontal overflow.

## Right-edge tick rail (desktop only)

Reads as "instrument" for anything that sells measurement: a fixed column of 1px ticks at the right
edge, `display: none` below ~1100px, plus a mono percentage of page progress.

```css
.ticks::before, .ticks i {
  background-image: repeating-linear-gradient(to bottom, var(--track) 0 1px, transparent 1px 13px);
}
.ticks i {
  background-image: repeating-linear-gradient(to bottom, var(--signal) 0 1px, transparent 1px 13px);
  height: 0; transition: height .15s linear;
}
```

Set `i.style.height = (pageProgress * 100) + '%'` from the scroll handler. Hide the whole rail in the
motion-off / reduced-motion state — it is decoration, and a frozen half-filled gauge looks broken.

## Scrollspy without the sticky-link bug

```js
const active = {};
new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) active[e.target.id] = 1; else delete active[e.target.id]; });
  const current = Object.keys(active)[0];
  navLinks.forEach(a => a.classList.toggle('is-active', !!current && a.hash === '#' + current));
}, { rootMargin: '-45% 0px -50% 0px' });
```

The set is the point: entries only arrive on change, so a per-entry callback leaves the last section's
link highlighted forever once the visitor scrolls back above every section.

## Canvas background gating

Stop and start the loop on three signals — `document.hidden`, an IntersectionObserver on the hero, and
the motion flag — and re-read the accent token inside the draw path (`getComputedStyle` at draw time),
not once at module load. Cap `devicePixelRatio` at 2 and scale node count with viewport width.

## Contract for the motion-off state

One function should own "the final state" and be called from every path that turns motion off
(reduced-motion at boot, the manual toggle, and a re-run of the intro). It sets: score to its final
value, gauge arc offset to its target, every bar to its final width, every reveal and stagger element
to `.in`, all steps lit, the rail at 100%, and the decorative layers hidden. Skipping it on the
reduced-motion path is the defect that ships to exactly the users the guardrail was written for.
