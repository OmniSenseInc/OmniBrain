#!/usr/bin/env python3
"""Uji endpoint refresh_access_token (TIDAK menyimpan apa pun, token tidak dicetak).
Kalau refresh jalan tapi /me diblokir -> blokir di level APP (bukan token)."""
import json, urllib.request, urllib.error

ENV = "/home/ubuntu/ai-agency/ig_token.env"
env = {}
for line in open(ENV):
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip().strip('"').strip("'")
tok = env["IG_LONG_LIVED_TOKEN"]

url = ("https://graph.instagram.com/refresh_access_token"
       f"?grant_type=ig_refresh_token&access_token={tok}")
try:
    with urllib.request.urlopen(url, timeout=30) as r:
        d = json.loads(r.read().decode())
        print("refresh_access_token: HTTP", r.status)
        print("  keys:", sorted(d.keys()))
        print("  token_type:", d.get("token_type"), "| expires_in:", d.get("expires_in"),
              f"(~{int(d.get('expires_in', 0)) // 86400} hari)")
        print("  access_token baru:", "ADA (tidak dicetak)" if d.get("access_token") else "tidak ada")
except urllib.error.HTTPError as e:
    print("refresh_access_token: HTTP", e.code)
    print(" ", e.read().decode("utf-8", "replace")[:400])
except Exception as e:
    print("refresh_access_token ERROR:", type(e).__name__, e)
