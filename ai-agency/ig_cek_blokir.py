#!/usr/bin/env python3
"""ig_cek_blokir.py — cek apakah blokir Meta ("API access blocked", code 200) sudah lepas.

Dipakai manual maupun oleh cron watchdog. TIDAK pernah mencetak token.

Exit code:
  0 = API normal (PULIH) — aman untuk publish
  1 = masih diblokir / token bermasalah
  2 = masalah lokal (file token / jaringan)

Pakai:
  python3 ig_cek_blokir.py          # laporan 2-3 baris
  python3 ig_cek_blokir.py --ringkas # satu baris saja
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ENV = "/home/ubuntu/ai-agency/ig_token.env"
API = "https://graph.instagram.com/v23.0/me"
RINGKAS = "--ringkas" in sys.argv


def baca_env(path: str) -> dict:
    env = {}
    if not os.path.exists(path):
        return env
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> int:
    env = baca_env(ENV)
    tok = env.get("IG_LONG_LIVED_TOKEN")
    if not tok:
        print("MASALAH LOKAL: IG_LONG_LIVED_TOKEN tidak ada di ig_token.env")
        return 2

    url = API + "?" + urllib.parse.urlencode(
        {"fields": "id,username,account_type", "access_token": tok}
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            err = json.loads(e.read().decode()).get("error", {})
        except Exception:
            err = {"message": f"HTTP {e.code}"}
        msg = err.get("message", "unknown")
        code = err.get("code")
        if RINGKAS:
            print(f"MASIH DIBLOKIR: {msg} (code={code})")
        else:
            print(f"MASIH DIBLOKIR: {msg} (code={code})")
            if code == 200:
                print("  -> blokir di sisi Meta (app/akun). Lihat CONTENT_POSTED_LOG.md "
                      "bagian 'GAGAL POSTING (blocker Meta)'.")
            elif code == 190:
                print("  -> token expired/dicabut. Ambil token baru, lalu `ig_token.py exchange`.")
            print(f"  -> token masih berlaku s.d. {env.get('IG_TOKEN_EXPIRES_AT', '?')}")
        return 1
    except Exception as e:
        print(f"MASALAH LOKAL: {type(e).__name__}: {e}")
        return 2

    user = data.get("username", "?")
    if RINGKAS:
        print(f"PULIH: @{user} — API normal, siap publish.")
    else:
        print(f"PULIH: @{user} (id {data.get('id')}, {data.get('account_type')}) — API normal.")
        print("  -> lanjutkan dengan: python3 ig_queue.py status  lalu  ig_queue.py publish")
    return 0


if __name__ == "__main__":
    sys.exit(main())
