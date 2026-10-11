#!/usr/bin/env python3
"""Probe status Instagram profil PUBLIK tanpa login.
Gunakan untuk riset kompetitor: bio, jumlah follower/following, jumlah post,
dan beberapa caption post terbaru.

Pemakaian:
  python3 ig_probe.py @username [@username2 ...]
Catatan:
- Hanya bekerja untuk akun PUBLIK. Akun privat tidak bisa dibaca.
- Ambil beberapa akun sekaligus dengan pisah spasi.
- Respon diambil dari endpoint publik web_profile_info Instagram.
"""

import sys
import json
import time
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
APP_ID = "936619743392459"


def get_profile(username):
    u = username.lstrip("@")
    url = (f"https://www.instagram.com/api/v1/users/web_profile_info/"
           f"?username={u}")
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "application/json",
        "X-IG-App-ID": APP_ID,
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 45
                print(f"  [429 rate-limit, menunggu {wait}s]")
                time.sleep(wait)
                continue
            raise
    else:
        raise RuntimeError("rate-limit bertahan setelah retry")


def fmt(n):
    try:
        return f"{n:,}"
    except Exception:
        return str(n)


def main(args):
    if not args:
        print("perlu minimal satu username, contoh: python3 ig_probe.py @moka")
        sys.exit(1)
    for username in args:
        try:
            d = get_profile(username)
            u = d.get("data", {}).get("user") or {}
            if not u:
                print(f"[{username}] tidak ditemukan / bukan akun publik")
                continue
            print("=" * 56)
            print(f"@{u.get('username')}  |  {u.get('full_name')}")
            if u.get("is_verified"):
                print("  (akun terverifikasi)")
            stat = u.get("edge_followed_by", {}).get("count")
            foll = u.get("edge_follow", {}).get("count")
            posts = (u.get("edge_owner_to_timeline_media") or {}).get("count")
            print(f"  followers : {fmt(stat) if stat is not None else '?'}")
            print(f"  following : {fmt(foll) if foll is not None else '?'}")
            print(f"  total post: {fmt(posts) if posts is not None else '?'}")
            bio = u.get("biography") or "-"
            print(f"  bio       : {bio}")
            links = u.get("bio_links") or []
            if links:
                print("  link bio  : " + "; ".join(l.get("url", "") for l in links))
            media = (u.get("edge_owner_to_timeline_media") or {}).get("edges", [])
            if media:
                print("  -- post terbaru --")
                for e in media[:5]:
                    node = e.get("node", {})
                    cap = (node.get("edge_media_to_caption") or {})
                    cts = cap.get("edges", [])
                    txt = cts[0]["node"].get("text", "") if cts else ""
                    short = txt.replace("\n", " ").strip()
                    if len(short) > 140:
                        short = short[:139] + "…"
                    likes = (node.get("edge_liked_by") or {}).get("count")
                    n_com = (node.get("edge_media_to_comment") or {}).get("count")
                    kind = "VIDEO" if node.get("is_video") else ("REEL" if node.get("__typename") and "Clip" in node.get("__typename") else "FOTO")
                    print(f"   [{kind}] like={fmt(likes) if likes else '?'} "
                          f"komentar={fmt(n_com) if n_com else '?'}")
                    print(f"      {short if short else '(tanpa caption)'}")
        except urllib.error.HTTPError as e:
            print(f"[{username}] HTTP {e.code} — akun privat / dihapus / diblokir")
        except Exception as e:
            print(f"[{username}] gagal: {e}")
        print("  (jeda 60s untuk menghindari rate-limit…)")
        time.sleep(60)


if __name__ == "__main__":
    main(sys.argv[1:])