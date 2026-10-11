---
name: instagram-data-access
description: "Access public Instagram profile data without login."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Instagram, SocialMedia, CompetitorResearch, WebScraping, PublicData]
    related_skills: [blocked-page-recovery, xurl]
---

# Instagram Data Access (public profiles, no login)

For competitor research and market intelligence on PUBLIC Instagram accounts,
you do NOT need login, a bot, or a mirror site. Instagram exposes a public
JSON endpoint. This is the fastest, most reliable, and most legitimate route
for reading a public profile's core data: biography, bio links, follower /
following counts, total post count, and the latest post captions.

## The working method

One clean `curl` per account:

```bash
curl -s -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36" \
  -H "Accept: application/json" \
  -H "X-IG-App-ID: 936619743392459" \
  "https://www.instagram.com/api/v1/users/web_profile_info/?username={USERNAME}"
```

Response is JSON at `.data.user` with fields: `biography`, `bio_links`,
`full_name`, `edge_followed_by.count`, `edge_follow.count`,
`edge_owner_to_timeline_media.count` (+ `.edges[]` = recent posts with
`.node.edge_media_to_caption.edges[].node.text` captions).

## Pacing — the one rule that makes or breaks it

This anonymous endpoint is aggressively rate-limited per IP. It works ONCE,
then a cooldown is required.

- ONE request per ~45-60s across the whole session. Back-to-back requests ->
  `429` even when spaced 45s apart (the retries themselves reset the window).
- Reliable pattern observed: wait ~45-60s with NO requests, then fire ONE
  clean request. That single request returns `200`.
- Do NOT write a retry loop that hammers on 429 — it makes things worse and
  eats the request budget. A single probe after cooldown beats 5 fast retries.

## Error-code interpretation (don't misread these)

| Code | Meaning | Action |
|------|---------|--------|
| `200` | Hit. Parse `.data.user`. | Done. |
| `429` | Rate-limited. | Wait ~45-60s, ONE clean request. |
| `400` + body `{"message":"Asset asset://... "schema has been deleted"..."}` | Instagram INTERNAL schema bug for that specific account — not "user not found" and not your fault. | Retry later; not fixable client-side. |
| `302` (0-byte) on GET of the profile page | Not readable this way. | Use the API endpoint above, not the page. |

## Walled-garden reality: don't fight the login door

From automated / datacenter-hosted browsers, Instagram refuses login and
returns the GENERIC message "The login information you entered is incorrect"
even for valid credentials — deliberately, to hide that the block is the bot/
IP, not the password. Consequences:

- Several different (correct) accounts all show the same error from one such
  environment. Do not conclude the credentials are wrong, and DO NOT hammer
  login retries / cycle accounts — repeated attempts risk flagging the dummy
  accounts. Stop after ~2 tries.
- Login flow variations (Instagram Lite `web/lite/`, `i.instagram.com`,
  session resets, cookie clears) do not help; the block is at the IP/anti-bot
  level. Prefer the public API above — it needs NO login at all.

## Dead ends to skip (tested, do not retry these for public data)

- Legacy `?__a=1&__d=dis` JSON on the profile page: blocked.
- `/{username}/embed/captioned/`: 404s for some accounts.
- Mirror sites (picuki.com, imginn.com): 403 / Cloudflare-challenged.
- Browser-driven navigation to `instagram.com/{username}/`: intermittent
  `NS_ERROR_NET_EMPTY_RESPONSE` (first nav resets; a single retry usually
  works), and heavy profiles still fall over. The API is cheaper and steadier.

## Logged-in-only data (be honest)

Private accounts and follower lists are NOT readable this way — correctly
so. If the user needs that, the honest route is: the user opens the account
on their own device (unblocked IP) and pastes/screenshots; do not attempt to
break privacy.

## Script

`scripts/instagram_probe.py` — single-request probe; prints bio, follower /
following, posts, and recent post captions for one or more usernames.

```bash
python3 scripts/instagram_probe.py @username [@other]
```
