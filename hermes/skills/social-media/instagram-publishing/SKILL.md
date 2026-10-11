---
name: instagram-publishing
description: "Use when posting to Instagram via the official API."
---

# Instagram Publishing (official Content Publishing API)

For POSTING images to an Instagram professional (BUSINESS/CREATOR) account via
Meta's API — own brand account or client accounts. Reading PUBLIC profile data
without login is a different job: see `instagram-public-research` /
`instagram-data-access`.

Working helpers already on this machine: `/home/ubuntu/ai-agency/ig_token.py`
(token lifecycle) and `/home/ubuntu/ai-agency/ig_post.py` (convert → host →
container → poll → publish → log). Full endpoint table, limits and error codes:
`references/instagram-publishing-api.md`.

Poster art direction — relevant photographic backdrops under a locked template,
license filtering, and legibility checks that need no vision model:
`references/background-imagery.md`.

## Standing rules for this user
- **Agent executes end to end.** Run the token exchange, prepare the media, write
  caption + hashtags, publish, then report the permalink. Do NOT hand the user a
  list of commands to run himself unless he explicitly asks for commands.
- **Preview before live by default:** show the poster + caption, wait for an
  explicit go-ahead, then publish. Switch to unattended auto-post only after the
  user has said posting may run on its own (then still report each permalink).
- **No filler to hit a schedule.** If the content pipeline reports nothing new
  worth posting, skip the slot entirely.
- Poster generation and caption/brand rules are governed by the user's own
  OmniSense content skill — load it for the visuals and the copy.

## Approval gate (when a scheduled pipeline produces the content)

Put the gate in a STATE FILE, never in the chat: the scheduled run writes a
candidate (`status: pending` + image path + caption + hashtags + content key) and
sends the preview; a small CLI (`queue` / `status` / `publish` / `cancel` /
`guard --key`) converts one explicit user word into the live publish. The
approval usually arrives in a different session or channel than the one that
produced the content, so nothing may depend on in-conversation memory.

- Publish is idempotent on the content key: a repeated approval, or two channels
  both acting on it, must not double-post — refuse when the key is already posted.
- The same publish command takes the dry-run flag, so the whole chain (convert →
  host → container → poll) can be exercised without a live post.
- A newer candidate replaces the older pending one; say so in the preview so the
  user never approves a stale poster.
- The scheduled agent is forbidden from publishing on its own — the prompt must
  name the approve step explicitly, otherwise a capable agent will finish the job
  it can see is unfinished.

## Procedure
1. **Token: measure its lifetime before trying to convert it.** A token is not
   automatically short-lived just because someone (a dashboard hint, another AI)
   said so — a token minted through the app's own Instagram product page is often
   ALREADY long-lived, and an exchange is then pointless work. Probe first, it is
   one GET and needs no secret:
   `GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=…`
   A `200` carrying `expires_in` around 5,18x,xxx s proves the token was already
   long-lived (refresh only accepts long-lived tokens) and hands back a NEW token
   value with a fresh 60-day window — save that one, it supersedes the old.
   Only if that call fails do you need the exchange path:
   exchange needs the app secret from the App Dashboard; without it Meta answers
   `The parameter client_secret is required.` Token prefix picks the host:
   `IGAA…` → `graph.instagram.com/access_token?grant_type=ig_exchange_token`;
   `EAA…` → `graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token`
   (needs `client_id` + `client_secret`).
   Verify identity too, not just liveness: `GET /v23.0/me?fields=id,username,account_type`
   — a token can look plausible and still be expired or belong to another app.
2. **Media must be JPEG** (≤8 MB, ratio 4:5–1.91:1). Convert PNG→JPEG first —
   locally generated posters are PNG and Meta rejects them.
3. **The image must be at a public URL** — Meta downloads it itself; a local file
   path cannot be published. Upload to a temporary host and verify the URL serves
   `image/*` — not merely that it answers 200. A host that wraps the file in an
   HTML landing page (tmpfiles.org's `/dl/` path does exactly this) returns 200
   with `text/html`, and the container then fails with a Meta-side error that
   looks like an API fault. Check with
   `curl -s -o /dev/null -w '%{http_code} %{content_type}' -L <url>` and require
   `2xx` + `image/…` before creating the container. Host verified to serve the raw
   bytes: **uguu.se** — `curl -s -A 'Mozilla/5.0' -F 'files[]=@<file>' 'https://uguu.se/upload?output=text'`
   returns a plain URL. `litterbox.catbox.moe` is a workable fallback but answers
   500 in bursts; other hosts vary, which is why the content-type check matters
   more than any host allowlist.
4. **Container:** `POST /{ig-user-id}/media` with `image_url` + `caption`, then
   poll `GET /{container-id}?fields=status_code` until `FINISHED` (typically
   <10 s). Never call publish while the status is still `IN_PROGRESS`.
5. **Publish:** `POST /{ig-user-id}/media_publish` with `creation_id`, then read
   back `GET /{media-id}?fields=permalink,timestamp` and report the permalink —
   a successful publish call is not proof the post is live.
6. **Record it:** write the dedup key, media id, permalink and caption head to the
   posted log, and check that log before choosing the next topic.
7. **Dry run when unsure:** create the container and stop there. It proves token,
   media and account are fine, never appears in the feed, and expires in 24 h.
8. **Schedule the refresh.** Long-lived ≠ permanent: 60 days. Refresh works only
   for a token ≥24 h old and not yet expired, and returns another 60 days — so a
   monthly refresh job keeps an auto-poster alive indefinitely.

## Pitfalls
- **Long-lived is not permanent.** An auto-poster with no refresh job dies on day
  60. If the user wants a token with no expiry of its own, that is the Facebook
  Login + Business Manager **System User token** path (still invalidated if the
  account password changes or the role is revoked).
- **App secret ≠ token.** Exchange, not publish, is what needs `client_secret`;
  keep it in a 600-perm file next to the token, never in a repo or a chat log.
- **`code 190` has three meanings** — `Cannot parse access token` (truncated or
  wrong app), `Failed to decrypt` (token and secret are not a matching pair),
  expired (subcode 463). Diagnose before asking the user for a new token.
- **`code 200 "API access blocked"` is an app/account-level block, not a bad
  token.** Localize it in two calls: `GET /me` and the `refresh_access_token`
  probe. If BOTH answer `code 200` while the token still has weeks of life, the
  block sits on the app or the account — no token exchange, new image host, or
  regenerated poster changes it, so stop swapping those. Nothing client-side
  clears it: the account owner must check the app's status/warnings in the App
  Dashboard and the IG account's Account status (appeal from there); such blocks
  are usually temporary. Meanwhile keep the queued candidate `pending` (do NOT
  cancel — one publish runs the moment access returns) and hand the poster +
  caption to the user for a manual post from the app so the content still ships.
  Ready probes on this machine: `/home/ubuntu/ai-agency/diag_ig_api.py`
  (`/me`, `/<ig-user-id>`, `debug_token`) and `diag_ig_refresh.py`
  (`refresh_access_token`) — both read the token from `ig_token.env` and never
  print it.
- **A block that survives every client-side check usually means App Mode.** An
  app sitting in Development carries restrictions that no token or image-host
  change removes; switching it to Live drops a whole class of them. Meta gates
  that switch on three Basic-Settings fields: **Privacy Policy URL**, **User Data
  Deletion** (pick the *Instructions URL* option — no callback server needed), and
  **Category**. Do not promise the user the block is fixed until the fields
  actually SAVE and the switch takes.
- **A URL that loads in a browser can still be rejected by the dashboard**
  ("Provide a valid URL" on the policy / terms / data-deletion fields). Diagnose
  in the right order instead of rewriting the page: run the URL through Meta's
  Sharing Debugger first — `200` plus parsed `og:` properties prove Meta's own
  crawler fetched and read the page, which eliminates crawler-blocked, SSL and
  domain-blocklist theories in one step, and leaves only field-state, an invisible
  character in the pasted value, the URL's casing pattern, or a dashboard bug.
  Ladder, isolation tests, how to publish a policy page with no hosting, and the
  content-type/keyword verification a public URL needs before it goes into a form:
  `references/meta-app-live-mode.md`. Never satisfy a required field with a URL
  whose page does not actually contain the policy — Platform Term 4.f wants a
  real, publicly reachable policy.
- **Temporary image hosts are fine for publishing but not archival:** the host
  deletes the file after its window while the Instagram post keeps Meta's own
  copy. Do not use a temp host when the image must stay available elsewhere.
- **A rendered poster can be wrong in a way no status code catches.** The publish
  chain proving FINISHED says nothing about the artwork. Verify the finished file
  itself (vision pass, plus a text-free/legibility check) before it enters the
  approval queue, and re-check the numbers printed on it against the source — a
  truncated stat on a live post damages credibility permanently.
- **One image per container.** Carousel and reels use different endpoints; do not
  stuff multiple images into `image_url`.
- **Rate/account limits are per account:** a burst of publishes can return
  `code 9007` — back off instead of retrying in a loop.
- **`code 100 "Error validating client secret"` on exchange** means the secret does
  not belong to the app that issued the token (a second app in the same dashboard,
  or the plain App secret instead of the Instagram product's own secret). Do not
  send the user hunting for it before checking whether refresh already works — the
  refresh path needs no secret at all, so a rejected secret is often irrelevant.
- **Two token levels, two failure smells:** the token can be perfectly valid for
  reading (`/me` returns the handle) while the write permission is missing. Check
  the granted scopes include `instagram_business_content_publish` before blaming
  the media or the container.
