#!/usr/bin/env python3
"""Probe public Instagram profile data without login.
Usage: python3 ig_probe.py @handle [@handle2 ...]
Only works for PUBLIC accounts. Pace at ~1 request per 60s — the anonymous
web_profile_info endpoint is heavily rate-limited (HTTP 429).
"""
import sys, json, time, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
APP_ID = "936619743392459"

def get_profile(username):
    u = username.lstrip("@")
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={u}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json", "X-IG-App-ID": APP_ID})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  [429 rate-limit, wait 45s]"); time.sleep(45); continue
            raise
    raise RuntimeError("rate-limit persisted")

def fmt(n):
    try: return f"{n:,}"
    except Exception: return str(n)

def main(args):
    if not args:
        print("need at least one username, e.g. python3 ig_probe.py @handle"); sys.exit(1)
    for username in args:
        try:
            d = get_profile(username)
            u = (d.get("data") or {}).get("user") or {}
            if not u:
                print(f"[{username}] not found / private"); continue
            print("=" * 56)
            print(f"@{u.get('username')}  |  {u.get('full_name')}")
            print(f"  followers: {fmt((u.get('edge_followed_by') or {}).get('count'))}")
            m = u.get("edge_owner_to_timeline_media") or {}
            print(f"  total posts: {fmt(m.get('count'))}")
            print(f"  bio: {u.get('biography') or '-'}")
            for e in (m.get("edges") or [])[:6]:
                n = e.get("node") or {}
                caps = (n.get("edge_media_to_caption") or {}).get("edges") or []
                txt = caps[0]["node"].get("text", "") if caps else ""
                print(" - post:", txt.replace("\n", " ").strip()[:140])
        except Exception as ex:
            print(f"[{username}] failed: {ex}")
        print("  (60s cooldown to dodge rate-limit)"); time.sleep(60)

if __name__ == "__main__":
    main(sys.argv[1:])
