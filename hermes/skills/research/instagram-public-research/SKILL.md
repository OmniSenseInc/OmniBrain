---
name: instagram-public-research
description: "Get public Instagram profile/post data without login."
---

# Public Instagram Research (no login)

Objective: pull PUBLIC profile data (bio, followers, recent post captions/likes) for
competitive research WITHOUT scam-login and WITHOUT a Meta API key. This is the
reliable path. Do not promise/log-in automation — that path is anti-bot-gated and
usually fails from host environments.

## The working method (no login, no key)
Instagram serves public profile JSON to an unauthenticated GET:

  https://www.instagram.com/api/v1/users/web_profile_info/?username=<handle>

Headers that matter:
  User-Agent: a normal browser UA
  Accept: application/json
  X-IG-App-ID: 936619743392459

Response: JSON with `data.user`: biography, bio_links, edge_followed_by.count
(followers), edge_follow.count, edge_owner_to_timeline_media.count + .edges
(recent posts with captions + like/comment counts). One request returns ~12 posts.

A ready probe script lives at scripts/ig_probe.py (run one handle per invocation).

## Rate limiting (CRITICAL — this endpoint throttles hard)
- The /api/v1/web_profile_info endpoint is anonymous and heavily rate-limited.
  Observed safe cadence: ONE request per ~60 seconds. Back-to-back requests and
  loops hit HTTP 429 'rate limited' immediately.
- On 429, wait ~45s and retry sparingly; do NOT hammer with long retry loops —
  that extends the block and burns the window.
- Add a cooldown after each handle. Batch = very slow; prefer one careful call
  over an aggressive loop.

## Symptom / error mapping
- 429         -> rate-limited; wait + retry once, then move on.
- 400 with    -> Instagram-internal schema bug for that specific account ("Asset
  error text    asset://laser.provider/... has been deleted"). NOT the request's
  "message")    fault and sometimes transient; try again later or skip.
- 400 / empty  -> private or nonexistent account. Private pages are unreadable
  user:null     without auth — accept and move on.
- HTTP 302 on  -> modern IG redirects the raw page; the API endpoint above bypasses
  bare profile   this, which is why it is preferred over scraping the HTML.

## Less reliable alternatives (try only if the API is dead)
- https://www.instagram.com/<h>/embed/captioned/ — sometimes works, sometimes 404s
  per account. Not dependable.
- Third-party mirrors (picuki, imginn, etc.) — frequently 403/Cloudflare-blocked.
  Not dependable.

## Pitfalls
- Do not try to auto-log-in with a dummy account: IG anti-bot rejects automated
  browsers; repeated attempts risk flagging the account. State this honestly and
  pivot to the public endpoint.
- Public endpoint only; respect that private accounts are not meant to be read.
- The endpoint costs real latency; one handle at a time, keep the pacing.
