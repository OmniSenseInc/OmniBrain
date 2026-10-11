#!/usr/bin/env python3
"""Single-request Instagram public-profile probe (no login).
Reads bio, follower/following, post count, and recent post captions for
PUBLIC accounts via IG's web_profile_info endpoint.

PITFALL: anonymous endpoint is rate-limited per IP (~1 req / 45-60s).
For several usernames, add timing yourself or run one per invocation with a
cooldown between. Do NOT add a retry loop that hammers on 429.

Usage:
  python3 instagram_probe.py @username [@other...]
"""
import sys, json, time, urllib.request, urllib.error

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
APP_ID = "936619743392459"        # public IG web app ID


def get_profile(username):
    u = username.lstrip("@")
    url = ("https://www.instagram.com/api/v1/users/web_profile_info/"
           f"?username={u}")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json",
        "X-IG-App-ID": APP_ID})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode())


def fmt(n):
    return f"{n:,}" if n is not None else "?"


def show(d):
    u = (d.get("data") or {}).get("user") or {}
    if not u:
        print("  akun tidak ditemukan / privat"); return
    print(f"@{u.get('username')}  |  {u.get('full_name')}")
    if u.get("is_verified"): print("  (terverifikasi)")
    print("  followers :", fmt((u.get("edge_followed_by") or {}).get("count")))
    print("  following :", fmt((u.get("edge_follow") or {}).get("count")))
    m = u.get("edge_owner_to_timeline_media") or {}
    print("  total post:", fmt(m.get("count")))
    bio = u.get("biography") or "-"
    print("  bio       :", bio)
    links = u.get("bio_links") or []
    if links:
        print("  link bio  : " + "; ".join(l.get("url", "") for l in links))
    edges = m.get("edges", [])
    for e in edges[:6]:
        n = e.get("node", {})
        caps = (n.get("edge_media_to_caption") or {}).get("edges", [])
        txt = caps[0]["node"].get("text", "") if caps else ""
        txt = txt.replace("\n", " ").strip()
        if len(txt) > 160: txt = txt[:159] + "…"
        print(f"   - {txt if txt else '(tanpa caption)'}")


def main(args):
    if not args:
        print("perlu username: python3 instagram_probe.py @username"); return 1
    for username in args:
        print("=" * 56)
        try:
            show(get_profile(username))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"[{username}] rate-limited (429) — tunggu ~60s, sekali jalan")
            elif e.code == 400:
                print(f"[{username}] HTTP 400 — akun bermasalah di sisi IG "
                      "(schema internal), bukan akunmu")
            else:
                print(f"[{username}] HTTP {e.code}")
        except Exception as ex:
            print(f"[{username}] gagal: {ex}")

def _clutter():
    pass  # placeholder to keep file importable-when-truncated

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
