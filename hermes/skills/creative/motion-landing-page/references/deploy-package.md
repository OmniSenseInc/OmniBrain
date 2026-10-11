# Deploy package — from a finished single-file page to a site someone can upload

Companion to SKILL.md's "Shipping the page as a real site". The page is done and verified; this is the
last mile that makes it survivable on a real server without you having deploy access.

## File inventory

```
index.html            the site (theme locked, motion built in)
privacy.html          required the moment any page collects visitor input
404.html              dark-themed, links back to the main sections
robots.txt            Disallow: /pratinjau/  /arsip/  (screenshot + backup folders)
sitemap.xml           absolute URLs on the real domain
site.webmanifest      name, theme_color = page background, icon set
assets/               logo mark, favicon.ico + 16/32 + apple-touch-icon, og-<brand>.png
```

Keep working material (`pratinjau/`, `arsip/`, build scripts) in the tree — it is auditable history —
and block it in `robots.txt` rather than deleting it.

## Meta tags the head must carry

`canonical`, `og:type`, `og:url`, `og:title`, `og:description`, `og:image` + `og:image:width/height` +
`og:image:alt`, `og:locale`, `og:site_name`, `twitter:card=summary_large_image`. Plus JSON-LD
`ProfessionalService` (name, url, logo, areaServed, the free offer) when the business has a concrete
entry offer — it is what makes the free assessment show up as a service rather than a paragraph.

**Insertion pitfall:** a hand-written single-file page may be missing `</head>`. Assert the marker
exists before splicing anything "before `</head>`"; if the stylesheet runs straight into `<body>`,
close the head at the insertion point first, then re-assert `count('<style>') == 1` and visible-text
equality against the backup.

## OG card (1200×630) — generate it, do not hand-place text

A script (PIL/ImageMagick) that draws: brand background color, the wordmark composited from the master
logo PNG, the headline in the site's font, and a thin accent rule. Reasons: it re-renders when the
headline changes, it never ships clipped text, and it is reviewable in the repo.
Save as `assets/og-<brand>.png` and verify by opening it with the vision tool — check nothing is
clipped at the edges and the composition still reads at thumbnail size (that is how it appears in chat
previews).

## Server block (nginx)

`try_files $uri $uri/ =404;` with `error_page 404 /404.html;`, cache headers split between
immutable `assets/` (long) and HTML (short/none), and `charset utf-8;`. Put the real domain in both
`server_name` and the sitemap. The handover doc should state the copy command
(`rsync -av --delete <dir>/ user@host:/var/www/<site>/`) and that the owner restarts/reloads nginx.

## Privacy page content that actually covers a client-side assessment

- What is collected (nothing leaves the device by default), the `localStorage` key and its purpose.
- How the visitor's own hand-off works: they press a link that carries their answers to WhatsApp/email;
  the site itself does not transmit them.
- No analytics/cookies — say it explicitly if true, because the absence of a tracker is a selling point
  for a consultancy that sells readiness assessments.
- How to erase it (clear site data) and a contact address for questions.
- Mirror the ID and EN versions on the same page when the site is bilingual.

## Pre-handover checklist

1. `verify_page.js` on the shipped default — zero console/page errors, no horizontal overflow at 1440
   and 390.
2. The assessment/scored-form harnesses green (parity against the canonical calculator, plus the
   interaction suite).
3. Every `assets/` reference resolves on disk, including the manifest icons.
4. Every `tel:` / `wa.me` / `mailto:` href holds real digits (see SKILL.md pitfall — a masked placeholder
   is invisible in the rendered text).
5. Refresh the official preview screenshots from the final build and archive the previous set.
6. Report what you verified with the actual numbers, and name the step you cannot perform (upload).
