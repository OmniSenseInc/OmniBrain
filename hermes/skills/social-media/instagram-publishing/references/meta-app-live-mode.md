# Meta app: getting it to Live (required fields + why a valid URL is rejected)

Depth for the App Mode / required-fields side of a Meta app that posts to
Instagram. Read this when the dashboard refuses a URL, when the app is stuck in
Development, or when a block survives every client-side check.

## Required before Development → Live
`App Settings → Basic` needs three fields, then the App Mode switch accepts:

| Field | What to put | Note |
|---|---|---|
| Privacy Policy URL | URL of a page that really contains the policy | Must be publicly reachable, no login |
| User Data Deletion | choose **Instructions URL**, same page is fine | Avoids hosting a callback endpoint |
| Category | e.g. Business and Pages / Utilities | Cosmetic to the block |

Also fill **App Domains** and **Website/Site URL** with the same domain — several
dashboard rejections clear once the domain is consistent across every field.

## Diagnose a rejected URL in this order
1. **Sharing Debugger first** — `https://developers.facebook.com/tools/debug`, paste
the URL, read **Kode Tanggapan / Response code** and the Open Graph block.
   - `200` + `og:title`/`og:description` populated → Meta's crawler fetched AND read
     the page. Crawler-blocked, SSL-invalid and domain-blocklist are now ruled out;
     the cause is dashboard-side.
   - "Bad Response Code" / "Can't validate SSL Certificate" → that IS the cause;
     fix hosting/SSL/WAF before anything else.
   - "og:image not available yet" → cosmetic link-preview warning, does NOT block
     validation. Do not chase it while the field still refuses to save.
2. **Isolation tests, each under a minute:**
   - *Field vs URL:* enter Meta's own `https://www.facebook.com/privacy/policy`.
     Rejected too → the field/account/dashboard is broken, not your URL.
   - *Casing pattern:* enter a short all-lowercase URL. Accepted → the validator
     dislikes uppercase in the path; republish the page with a lowercase slug.
   - *Stale state / invisible characters:* clear the field → Save → refresh →
     retype MANUALLY (never paste) → Save.
3. **If all three fail**, it is a dashboard bug (the symptom is reported on Meta's
   developer forum without a working answer): file it at
   `https://developers.facebook.com/support/bugs/` and
   `https://developers.facebook.com/support/`, attaching the debugger output as
   proof the URL is healthy. Present the ladder to the user as an elimination
   sequence, never as a fix you can guarantee.

Note which fields complain: if the data-deletion field accepts the same domain
that the policy field rejects, the domain is not the problem — say so instead of
rewriting the page.

## Publishing a policy page when you control no hosting
`telegra.ph` has an anonymous JSON API — no account, permanent page, editable later
without changing the URL.
- `POST https://api.telegra.ph/createAccount` once; store `access_token`.
- `POST .../createPage` with `title`, `author_name`, `content` = array of nodes:
  `{"tag":"h3","children":["..."]}`, `{"tag":"p","children":["..."]}`,
  `{"tag":"a","attrs":{"href":"..."},"children":["label"]}`. Supported tags:
  h3/h4 (no h1/h2), p, ul/ol+li, a, b, i, hr, figure. Form-encode it, JSON-encode
  the array/dict values.
- **The slug comes from `title` and preserves its casing** — a lowercase title is
  the only way to get a lowercase slug; taken slugs get a numeric suffix.
- `editPage` updates the body without changing the URL — use it to add a contact
  email later, after the URL is already sitting in the dashboard.

## Verify a public URL before it goes into a form or a review
```
curl -s -o /dev/null -w 'HTTP %{http_code} | %{content_type} | redirect=%{num_redirects}\n' -L "<url>"
curl -sL "<url>" | grep -ciE '<keyword that must be present>'
curl -s -o /dev/null -w '%{http_code}\n' -A 'facebookexternalhit/1.1' -L "<url>"
```
Require `200`, `text/html`, zero redirects, and the keyword actually present.
**A 200 alone proves nothing:** some paste services answer 200 while serving their
own viewer page instead of your file, so a code-only check passes on an empty
shell. Free file hosts also reject datacenter IPs outright; when one or two
refuse, stop shopping hosts and move to your own domain.

## The permanent home
Serve the page from a domain the user owns. If the site runs nginx on a VPS the
user controls, a single static file is enough (`/privacy.html` plus
`/privacy/index.html`), then `nginx -t` and reload, then re-check with the debugger
before pasting the final URL into the dashboard.

Concrete for this user: `omnisense.id` is served by nginx on a VPS whose SSH port
is open, but no deploy credentials exist on the agent machine, so the agent cannot
install the file itself. A ready script sits at
`/home/ubuntu/ai-agency/deploy_privacy.sh` next to
`privacy_policy_omnisense.html`: it locates the nginx document root for the site,
drops `privacy.html` + `privacy/index.html`, reloads nginx and prints the HTTP
check. Either hand the user the two commands (scp to `/tmp`, then `sudo bash`) or
ask for SSH access — then re-run the debugger check on the final URL before filling
the dashboard fields.
