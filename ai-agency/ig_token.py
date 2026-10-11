#!/usr/bin/env python3
"""ig_token.py — kelola token Instagram (short-lived -> long-lived -> auto-refresh).

Dua jalur login Instagram yang didukung (deteksi otomatis dari bentuk token):
  * Instagram Login  -> host graph.instagram.com   (token pendek: IGAA... / "IGQV...")
  * Facebook Login   -> host graph.facebook.com    (token pendek: EAA...)

Perintah:
  python3 ig_token.py exchange <short_lived_token>      # 1 jam -> 60 hari (butuh app secret)
  python3 ig_token.py refresh                           # perpanjang 60 hari lagi (long-lived)
  python3 ig_token.py status                            # cek token valid + sisa hari
  python3 ig_token.py save <token> [--days N]           # simpan token yang sudah long-lived
  python3 ig_token.py show                              # tampilkan token penuh (untuk copy-paste)

App secret dibaca berurutan dari: --secret, env IG_APP_SECRET / FB_APP_SECRET,
lalu file state di bawah. Token & secret disimpan di STATE_FILE (chmod 600).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ig_token.env")
TIMEOUT = 30
IG_HOST = "https://graph.instagram.com"
FB_HOST = "https://graph.facebook.com"
FB_OAUTH = "https://graph.facebook.com/oauth/access_token"
API_VERSION = "v23.0"

FIELDS = (
    "IG_LONG_LIVED_TOKEN",
    "IG_TOKEN_EXPIRES_AT",
    "IG_APP_ID",
    "IG_APP_SECRET",
    "IG_USER_ID",
    "IG_USERNAME",
    "IG_LOGIN_TYPE",
    "IG_UPDATED_AT",
)


# ---------------------------------------------------------------- state file
def load_state() -> dict:
    data = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def save_state(data: dict) -> None:
    merged = load_state()
    merged.update({k: v for k, v in data.items() if v})
    with open(STATE_FILE, "w") as fh:
        fh.write("# state token Instagram — JANGAN di-commit / di-share\n")
        for k in FIELDS:
            if merged.get(k):
                fh.write(f"{k}={merged[k]}\n")
    os.chmod(STATE_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 600


def mask(tok: str | None) -> str:
    if not tok:
        return "(kosong)"
    if len(tok) <= 14:
        return tok[:4] + "…"
    return f"{tok[:8]}…{tok[-4:]} ({len(tok)} char)"


# ---------------------------------------------------------------- http
def get_json(url: str, params: dict) -> dict:
    full = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(full, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        try:
            return json.loads(body)
        except Exception:
            return {"error": {"message": f"HTTP {e.code}: {body[:300]}", "code": e.code}}
    except Exception as e:  # network dll
        return {"error": {"message": f"{type(e).__name__}: {e}", "code": -1}}


def die_on_error(payload: dict) -> None:
    err = payload.get("error")
    if not err:
        return
    msg = err.get("message", "unknown error")
    code = err.get("code")
    hint = ""
    if code == 190 and "parse access token" in msg.lower():
        hint = "\n  -> token tidak terbaca: cek copy-paste (jangan kepotong) & pakai token dari app yang sama."
    elif code == 190 and ("expired" in msg.lower() or err.get("error_subcode") == 463):
        hint = "\n  -> token SUDAH EXPIRED. Ambil token baru dari App Dashboard, lalu jalankan `exchange` lagi."
    elif code == 190:
        hint = "\n  -> token invalid/expired, atau app secret bukan milik app penerbit token."
    elif code == 100:
        hint = "\n  -> parameter salah (grant_type / client_secret / access_token)."
    print(f"GAGAL: {msg} (code={code}){hint}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------- core ops
def login_type_of(token: str) -> str:
    """IGAA/IGQV -> Instagram Login; EAA -> Facebook Login."""
    if token.startswith("EAA"):
        return "facebook"
    return "instagram"


def exchange(short_token: str, app_id: str | None, app_secret: str) -> dict:
    kind = login_type_of(short_token)
    if kind == "facebook":
        if not app_id:
            print("GAGAL: jalur Facebook Login butuh IG_APP_ID (client_id).", file=sys.stderr)
            sys.exit(1)
        payload = get_json(FB_OAUTH, {
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": short_token,
        })
    else:
        payload = get_json(f"{IG_HOST}/access_token", {
            "grant_type": "ig_exchange_token",
            "client_secret": app_secret,
            "access_token": short_token,
        })
    die_on_error(payload)
    return payload


def refresh(long_token: str) -> dict:
    payload = get_json(f"{IG_HOST}/refresh_access_token", {
        "grant_type": "ig_refresh_token",
        "access_token": long_token,
    })
    die_on_error(payload)
    return payload


def whoami(token: str, kind: str = "instagram", fatal: bool = True) -> dict:
    if kind == "facebook":
        payload = get_json(f"{FB_HOST}/{API_VERSION}/me", {
            "fields": "id,name",
            "access_token": token,
        })
    else:
        payload = get_json(f"{IG_HOST}/{API_VERSION}/me", {
            "fields": "id,username,account_type",
            "access_token": token,
        })
    if payload.get("error") and fatal:
        die_on_error(payload)
    return payload


def days_left(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return (dt - datetime.now(timezone.utc)).total_seconds() / 86400


def persist(payload: dict, login_type: str, app_id=None, app_secret=None) -> str:
    tok = payload["access_token"]
    expires_in = int(payload.get("expires_in") or 0)
    exp_at = (datetime.now(timezone.utc) + timedelta(seconds=expires_in)).isoformat(timespec="seconds") if expires_in else ""
    info = whoami(tok, login_type, fatal=False) if tok else {}
    save_state({
        "IG_LONG_LIVED_TOKEN": tok,
        "IG_TOKEN_EXPIRES_AT": exp_at,
        "IG_LOGIN_TYPE": login_type,
        "IG_APP_ID": app_id or "",
        "IG_APP_SECRET": app_secret or "",
        "IG_USER_ID": str(info.get("id", "")),
        "IG_USERNAME": info.get("username", ""),
        "IG_UPDATED_AT": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    return tok


# ---------------------------------------------------------------- commands
def cmd_exchange(args) -> None:
    st = load_state()
    app_secret = args.secret or os.getenv("IG_APP_SECRET") or os.getenv("FB_APP_SECRET") or st.get("IG_APP_SECRET")
    app_id = args.app_id or os.getenv("IG_APP_ID") or os.getenv("FB_APP_ID") or st.get("IG_APP_ID")
    if not app_secret:
        print("GAGAL: app secret belum ada. Pakai --secret <app_secret>, atau isi IG_APP_SECRET di "
              f"{STATE_FILE}.", file=sys.stderr)
        sys.exit(1)
    short = args.token.strip().strip('"')
    payload = exchange(short, app_id, app_secret)
    kind = login_type_of(short)
    persist(payload, kind, app_id, app_secret)
    exp = days_left(load_state().get("IG_TOKEN_EXPIRES_AT"))
    print(f"OK — token long-lived tersimpan di {STATE_FILE}")
    print(f"  jenis login : {kind} ({'graph.facebook.com' if kind == 'facebook' else 'graph.instagram.com'})")
    print(f"  token       : {mask(payload['access_token'])}")
    print(f"  berlaku     : {payload.get('expires_in', '?')} detik"
          + (f" (~{exp:.0f} hari, s/d {load_state().get('IG_TOKEN_EXPIRES_AT')})" if exp else ""))
    st2 = load_state()
    if st2.get("IG_USERNAME"):
        print(f"  akun        : @{st2['IG_USERNAME']} (id {st2.get('IG_USER_ID')})")


def cmd_refresh(args) -> None:
    st = load_state()
    tok = args.token or os.getenv("IG_LONG_LIVED_TOKEN") or st.get("IG_LONG_LIVED_TOKEN")
    if not tok:
        print(f"GAGAL: belum ada long-lived token. Jalankan `exchange` dulu, atau isi IG_LONG_LIVED_TOKEN di {STATE_FILE}.",
              file=sys.stderr)
        sys.exit(1)
    payload = refresh(tok)
    persist(payload, st.get("IG_LOGIN_TYPE") or "instagram")
    exp = days_left(load_state().get("IG_TOKEN_EXPIRES_AT"))
    print("OK — token diperpanjang 60 hari.")
    print(f"  token   : {mask(payload['access_token'])}")
    print(f"  expired : {load_state().get('IG_TOKEN_EXPIRES_AT')}" + (f" (~{exp:.0f} hari lagi)" if exp else ""))


def cmd_save(args) -> None:
    st = load_state()
    seconds = args.expires_in if args.expires_in else (args.days or 60) * 86400
    payload = {"access_token": args.token.strip(), "expires_in": seconds}
    persist(payload, st.get("IG_LOGIN_TYPE") or login_type_of(args.token), st.get("IG_APP_ID"), st.get("IG_APP_SECRET"))
    print(f"OK — token disimpan (berlaku {seconds} detik).")
    st2 = load_state()
    if st2.get("IG_USERNAME"):
        print(f"  akun : @{st2['IG_USERNAME']} (id {st2.get('IG_USER_ID')})")


def cmd_status(args) -> None:
    st = load_state()
    tok = args.token or os.getenv("IG_LONG_LIVED_TOKEN") or st.get("IG_LONG_LIVED_TOKEN")
    print(f"state file : {STATE_FILE} ({'ada' if os.path.exists(STATE_FILE) else 'BELUM ada'})")
    if not tok:
        print("token      : (belum ada) — jalankan `exchange <short_lived_token>` dulu.")
        return
    print(f"token      : {mask(tok)}")
    print(f"jenis login: {st.get('IG_LOGIN_TYPE', '?')}")
    print(f"diperbarui : {st.get('IG_UPDATED_AT', '?')}")
    exp = st.get("IG_TOKEN_EXPIRES_AT")
    left = days_left(exp)
    print(f"expired    : {exp or 'tidak diketahui'}" + (f" (~{left:.0f} hari lagi)" if left is not None else ""))
    info = whoami(tok, st.get("IG_LOGIN_TYPE") or "instagram", fatal=False)
    if info.get("error"):
        err = info["error"]
        print(f"status API : TIDAK VALID — {err.get('message')} (code={err.get('code')})")
        if err.get("code") == 190:
            print("             -> token expired/dicabut. Ambil token baru dari App Dashboard, lalu `exchange` lagi.")
        sys.exit(2)
    label = f"@{info.get('username')}" if info.get("username") else info.get("name", "?")
    print(f"status API : VALID — {label} (id {info.get('id')}, {info.get('account_type', st.get('IG_LOGIN_TYPE', '?'))})")
    if left is not None and left < 7:
        print("PERINGATAN  : sisa < 7 hari — segera jalankan `refresh`.")


def cmd_show(args) -> None:
    st = load_state()
    tok = args.token or st.get("IG_LONG_LIVED_TOKEN")
    if not tok:
        print("(kosong)", file=sys.stderr)
        sys.exit(1)
    print(tok)


def main() -> None:
    p = argparse.ArgumentParser(description="Kelola token Instagram (short-lived -> long-lived -> refresh).")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("exchange", help="tukar short-lived (1 jam) jadi long-lived (60 hari)")
    e.add_argument("token")
    e.add_argument("--secret", help="app secret (kalau tidak lewat env/state file)")
    e.add_argument("--app-id", help="client_id (wajib untuk token Facebook Login EAA...)")
    e.set_defaults(func=cmd_exchange)

    r = sub.add_parser("refresh", help="perpanjang long-lived token 60 hari lagi")
    r.add_argument("--token", help="token eksplisit (default: dari state file)")
    r.set_defaults(func=cmd_refresh)

    s = sub.add_parser("save", help="simpan token yang sudah long-lived (mis. dari System User)")
    s.add_argument("token")
    s.add_argument("--days", type=int, default=60)
    s.add_argument("--expires-in", type=int, help="masa berlaku dalam detik (presisi, mis. dari refresh_access_token)")
    s.set_defaults(func=cmd_save)

    t = sub.add_parser("status", help="cek token masih valid + sisa hari")
    t.add_argument("--token")
    t.set_defaults(func=cmd_status)

    v = sub.add_parser("show", help="tampilkan token penuh")
    v.add_argument("--token")
    v.set_defaults(func=cmd_show)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
