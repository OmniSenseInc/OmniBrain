#!/usr/bin/env python3
"""Probe PUBLIC Instagram profile data without login (bio, followers, counts, captions).
Pace: ~1 request per 60s to avoid anonymous quota (429).
Usage: python3 ig_probe.py @handle [@handle2 ...]
Private accounts won't resolve — do not try to bypass.
"""
import sys, json, time, urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
APP_ID = "936619743392459"


def get_profile(username):
    u = username.lstrip("@")
    url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={u}"
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/json", "X-IG-App-ID": APP_ID,
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  [429 rate-limit, menunggu 45s]")
                time.sleep(45)
                continue
            raise
    raise RuntimeError("rate-limit bertahan setelah retry")


def fmt(n):
    return f"{n:,}" if isinstance(n, int) else str(n)


def main(args):
    for username in args or ["instagram"]:
        try:
            u = (get_profile(username).get("data") or {}).get("user") or {}
            if not u:
                print(f"[{username}] tidak ditemukan / bukan akun publik")
                continue
            print("=" * 56)
            print(f"@{u.get('username')} | {u.get('full_name')}")
            print(f"  followers: {fmt(u.get('edge_followed_by', {}).get('count'))}")
            print(f"  following: {fmt(u.get('edge_follow', {}).get('count'))}")
            m = u.get("edge_owner_to_timeline_media") or {}
            print(f"  total post: {fmt(m.get('count'))}")
            print(f"  bio: {u.get('biography')}")
            for e in m.get("edges", [])[:5]:
                n = e.get("node", {})
                c = (n.get("edge_media_to_caption") or {}).get("edges", [])
                t = c[0]["node"].get("text", "") if c else ""
                print("  POST:", t.replace("\n", " ")[:140])
        except Exception as ex:
            print(f"[{username}] gagal: {ex}")
        print("  (jeda 60s untuk menghindari rate-limit…)")
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1:])
