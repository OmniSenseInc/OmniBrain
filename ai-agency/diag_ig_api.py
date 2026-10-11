#!/usr/bin/env python3
"""Diagnosa cepat kenapa IG Graph API menolak (tanpa pernah mencetak token)."""
import json, os, urllib.request, urllib.parse, urllib.error, re

ENV = "/home/ubuntu/ai-agency/ig_token.env"
env = {}
for line in open(ENV):
    line = line.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

tok = None
for k in ("IG_LONG_LIVED_TOKEN", "IG_ACCESS_TOKEN", "IG_TOKEN", "ACCESS_TOKEN", "INSTAGRAM_TOKEN", "TOKEN"):
    if env.get(k):
        tok = env[k]
        break
print("var token:", [k for k in env if "TOKEN" in k.upper()])
print("panjang token:", len(tok) if tok else None, "| awalan:", (tok[:6] + "…") if tok else None)
uid = None
for k in ("IG_USER_ID", "IG_ID", "INSTAGRAM_USER_ID", "USER_ID", "IG_ACCOUNT_ID"):
    if env.get(k):
        uid = env[k]
        break
print("ig user id:", uid)


def call(url, label):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body = r.read().decode("utf-8", "replace")
            print(f"\n[{label}] HTTP {r.status}\n{body[:900]}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"\n[{label}] HTTP {e.code}\n{body[:900]}")
    except Exception as e:
        print(f"\n[{label}] ERROR {type(e).__name__}: {e}")


q = urllib.parse.urlencode({"fields": "id,username,account_type", "access_token": tok})
call("https://graph.instagram.com/v23.0/me?" + q, "v23.0 /me")
call("https://graph.instagram.com/me?" + q, "unversioned /me")
q2 = urllib.parse.urlencode({"fields": "id,username", "access_token": tok})
call(f"https://graph.instagram.com/v23.0/{uid}?" + q2, "v23.0 /<ig-user-id>")
q3 = urllib.parse.urlencode({"input_token": tok, "access_token": tok})
call("https://graph.instagram.com/v23.0/debug_token?" + q3, "debug_token")
