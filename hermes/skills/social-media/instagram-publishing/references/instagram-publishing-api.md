# Instagram Content Publishing API — endpoints, limits, host quirks

All endpoints verified against a live BUSINESS account on `v23.0`.

## Endpoints
| Tujuan | Request |
|---|---|
| Cek token + akun | `GET /v23.0/me?fields=id,username,account_type,media_count&access_token=<tok>` |
| Short→long (Instagram Login) | `GET graph.instagram.com/access_token?grant_type=ig_exchange_token&client_secret=<secret>&access_token=<short>` |
| Short→long (Facebook Login) | `GET graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=<app_id>&client_secret=<secret>&fb_exchange_token=<short>` |
| Refresh long-lived | `GET graph.instagram.com/refresh_access_token?grant_type=ig_refresh_token&access_token=<long>` |
| Buat container | `POST /v23.0/{ig-user-id}/media` — `image_url`, `caption` |
| Cek container | `GET /v23.0/{container-id}?fields=status_code,status` |
| Publish | `POST /v23.0/{ig-user-id}/media_publish` — `creation_id` |
| Ambil permalink | `GET /v23.0/{media-id}?fields=permalink,timestamp` |
| Daftar post sendiri | `GET /v23.0/me/media?fields=id,caption,timestamp,media_type,permalink` |

Base host: `graph.instagram.com` (Instagram Login) or `graph.facebook.com`
(Facebook Login). Pin the version in the base URL — Meta ships ~3 versions/year.

## Limits & lifecycle
- Publish permission (Instagram Login) = `instagram_business_content_publish`;
  the older `instagram_content_publish` / `business_content_publish` names are
  deprecated. The Facebook Login path still uses `instagram_content_publish`.
- Personal accounts cannot publish via API at all — professional only.
- Image: JPEG only (MPO/JPS rejected), ≤8 MB, ratio between 4:5 and 1.91:1.
  A 1080×1350 poster sits exactly on the 4:5 minimum.
- Tokens: short-lived 1 h, long-lived 60 days; refresh requires age ≥24 h and a
  non-expired token; refreshed tokens get another 60 days. Changing the account
  password or losing the role invalidates tokens regardless.
- Container expires after 24 h; do not publish a container whose status is not
  `FINISHED`.
- Account cap ≈100 API-published posts / rolling 24 h.

## Error codes worth recognising
| Code | Message | Meaning / action |
|---|---|---|
| 100 | `The parameter client_secret is required.` | Exchange attempted without the app secret — ask for the App Dashboard secret. |
| 190 | `Cannot parse access token` | Truncated / mangled copy-paste, or a token from a different app. |
| 190 | `Failed to decrypt` | Token and secret do not belong to the same app pair. |
| 190 (subcode 463) | `Session has expired` | Get a fresh short-lived token, then exchange again. |
| 9007 | rate limit | Back off; the account is throttled temporarily. |

## Temporary public image hosts (for `image_url`)
- `litterbox.catbox.moe/resources/internals/api.php` with
  `-F reqtype=fileupload -F time=72h -F fileToUpload=@file.jpg` → returns a plain
  `https://litter.catbox.moe/<id>.jpg`. Most reliable; send a normal browser
  User-Agent.
- `tmpfiles.org/api/v1/upload` works but returns an HTML wrapper URL — rewrite
  `tmpfiles.org/<id>/…` to `tmpfiles.org/dl/<id>/…` for a direct file.
- `catbox.moe/user/api.php` rejects non-browser User-Agents with
  `Invalid uploader`.
- `0x0.st` currently refuses uploads outright.

## Token-without-expiry path
Facebook Login + Business Manager **System User token** (host
`graph.facebook.com`) has no expiry of its own. Requires the IG account to be
connected to a Facebook Page and a Business Manager setup; still dies if the
account password changes or the role is revoked.
