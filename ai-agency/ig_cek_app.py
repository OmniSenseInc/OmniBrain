#!/usr/bin/env python3
"""ig_cek_app.py — Tes 1: apakah yang diblokir APP-nya atau AKUN-nya?

Cara pakai:
  python3 ig_cek_app.py <APP_SECRET>

Yang dilakukan: membentuk app access token (APP_ID|APP_SECRET) dari IG_APP_ID di
ig_token.env, lalu memanggil info app di graph.facebook.com. Tidak menyentuh
Instagram dan tidak menyentuh token IG. Secret TIDAK pernah dicetak.

Baca hasil:
  - "API access blocked"  -> blokir di level APP  (kejar: App Mode / appeal)
  - data app (nama, kategori) -> app SEHAT, blokir di level AKUN/token
  - "Invalid OAuth access token signature" -> APP_SECRET salah (bukan app ini)
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ENV = "/home/ubuntu/ai-agency/ig_token.env"


def baca_env(path: str) -> dict:
    env = {}
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> int:
    if len(sys.argv) < 2:
        print("Pakai: python3 ig_cek_app.py <APP_SECRET>")
        print("(APP_SECRET ada di App Settings -> Basic -> App Secret, tombol Show)")
        return 2
    secret = sys.argv[1].strip()

    env = baca_env(ENV)
    app_id = env.get("IG_APP_ID")
    if not app_id:
        print("MASALAH LOKAL: IG_APP_ID tidak ada di ig_token.env")
        return 2
    if len(secret) != 32 or not all(c in "0123456789abcdef" for c in secret.lower()):
        print(f"PERINGATAN: panjang secret {len(secret)}, biasanya 32 karakter hex. "
              "Pastikan kamu menyalin App Secret (bukan App ID / client token).")

    token = f"{app_id}|{secret}"
    url = f"https://graph.facebook.com/v23.0/{app_id}?" + urllib.parse.urlencode(
        {"fields": "id,name,category,link", "access_token": token}
    )
    print(f"APP_ID : {app_id}")
    print(f"secret : {secret[:4]}…{secret[-2:]} ({len(secret)} char) — tidak dicetak penuh\n")

    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            data = json.loads(r.read().decode())
        print("HASIL: APP SEHAT — API menjawab normal.")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        print("\nARTI: app-nya tidak diblokir. Blokir 'API access blocked' ada di level "
              "AKUN (akun developer / akun Instagram), bukan di app.")
        return 0
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            err = json.loads(body).get("error", {})
        except Exception:
            err = {"message": body[:300]}
        msg, code = err.get("message", "?"), err.get("code")
        print(f"HASIL: HTTP {e.code} — {msg} (code={code})")
        if msg.strip().lower().startswith("api access blocked"):
            print("\nARTI: blokirnya di level APP. Kejar App Mode (Development -> Live), "
                  "lalu appeal di developers.facebook.com/support kalau perlu.")
        elif code == 190:
            print("\nARTI: APP_SECRET salah / bukan milik app ini. Ambil ulang di "
                  "App Settings -> Basic -> App Secret (Show).")
        else:
            print("\nARTI: balasan tak terduga — tempel output ini apa adanya ke agent.")
        return 1
    except Exception as e:
        print(f"MASALAH LOKAL: {type(e).__name__}: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
