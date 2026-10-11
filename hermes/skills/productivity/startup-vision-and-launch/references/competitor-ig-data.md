# Public Instagram data without login (competitor intel)

Get PUBLIC account profile data (bio, bio links, follower/following counts, total posts, latest post captions) via Instagram's OWN JSON endpoint — no login, no browser automation.

## Endpoint
    GET https://www.instagram.com/api/v1/users/web_profile_info/?username=<handle>
    Headers: User-Agent (a real browser UA), Accept: application/json, X-IG-App-ID: 936619743392459

## HTTP semantics (verified)
- 200 : JSON with data.user. Fields: username, full_name, biography, bio_links, category_name, is_verified, edge_followed_by.count (followers), edge_follow.count (following), edge_owner_to_timeline_media.count (posts) and .edges[].node (latest 12) with edge_media_to_caption (caption) and edge_liked_by (likes).
- 429 : rate limited (anonymous quota exhausted). Fix: wait (cooldown ~45-60s) between requests; pace ~1 account per ~60s; back off and retry on 429. Do NOT hammer — the anonymous endpoint throttles quickly.
- 400 : often Instagram-internal schema/backend error (e.g. "Asset asset://laser.provider/ig_business_category_subvertical has been deleted") for a specific account, NOT a login/user-not-found signal. May be transient/specific to that account.
- 404 via /embed/captioned/ : account may be private, different handle, or embed disabled.
- 301/403 from third-party mirrors (picuki, imginn): mirrors block datacenter IPs; not a reliable path.

## Method
Use it for PUBLIC accounts only (competitors' marketing accounts are public by design). Private accounts are intentionally unreadable — do not try to bypass. For an account Instagram keeps erroring on, the honest fallback is to have the user open it on their own device and paste key posts.

## Cadence (important)
The endpoint returns real data but throttles fast (single call works, rapid calls -> 429). Pace one request per ~60s, or a few per minute max, and add 429 retry-with-wait. The bundled `scripts/ig_probe.py` takes one or more handles, prints bio/followers/posts/latest captions, and backoff-waits on 429. If run multi-handle, it sleeps 60s between accounts to avoid throttling.

## Ethics
Competitor data = inspiration for positioning, never copied verbatim.
