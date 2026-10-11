#!/usr/bin/env python3
"""Registrasi grup konsultasi client → free-response WhatsApp (pengganti "/whitelist").

MEKANISME NYATA:
Client "di-whitelist" untuk konsultasi = MEREGISTRASI JID grup konsultasinya ke
WHATSAPP_FREE_RESPONSE_CHATS, supaya bot bebas merespons di grup itu (client tak perlu
men-tag). Group lain (termasuk grup TIM) tetap tag-only.

Cara pakai (oleh admin/CTO):
  python3 wa_register_group.py <chatJid>
contoh:
  python3 wa_register_group.py 120363411213386519@g.us

BAIK UTK MODE "--current" (dipakai bot utk /whitelist):
  python3 wa_register_group.py --current
-> Mendeteksi grup WhatsApp "terakhir aktif" dari log gateway dan mendaftarkannya utk
   free-response. Dipakai ketika command /whitelist diketik DI DALAM grup konsultasi.

Bagaimana dapat JID grup: lihat di log gateway ("chat=...@g.us") saat grup dibuat,
atau gunakan --current, atau tanyakan ke bot.

Setelah registrasi, gateway otomatis di-restart agar diterapkan.
Untuk MENGECUALIKAN (hapus grup dari free-response):
  python3 wa_register_group.py --remove <chatJid>
"""

import sys
import os
import re
import subprocess

ENV = os.path.expanduser("~/.hermes/.env")
KEY = "WHATSAPP_FREE_RESPONSE_CHATS"
LOG = os.path.expanduser("~/.hermes/logs/gateway.log")


def detect_current_group_jid():
    """Grup WhatsApp (…@g.us) paling terakhir aktif dari log gateway."""
    if not os.path.exists(LOG):
        return None
    jids = re.findall(r"chat=([\d]+@g\.us)", open(LOG, encoding="utf-8", errors="ignore").read())
    return jids[-1] if jids else None


def read_env():
    vals = {}
    if os.path.exists(ENV):
        for line in open(ENV):
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    return vals


def write_env(vals):
    lines = []
    for line in open(ENV):
        line = line.rstrip("\n")
        if line.strip().startswith(KEY + "="):
            continue
        lines.append(line)
    lines.append(f"{KEY}={vals.get(KEY,'')}".rstrip(","))
    open(ENV, "w").write("\n".join(lines) + "\n")


def restart_gateway():
    subprocess.run(["hermes", "gateway", "restart"], check=False)


def main():
    args = sys.argv[1:]
    remove = "--remove" in args
    current = "--current" in args
    args = [a for a in args if a not in ("--remove", "--current")]
    if current:
        jid = detect_current_group_jid()
        if not jid:
            print("Tidak dapat mendeteksi grup aktif dari log gateway.")
            sys.exit(1)
        print(f"(dideteksi grup aktif: {jid})")
    elif args:
        jid = args[0].strip()
    else:
        print("Pakai: python3 wa_register_group.py <chatJid> | --current | --remove <chatJid>")
        sys.exit(1)
    vals = read_env()
    existing = [c for c in vals.get(KEY, "").split(",") if c.strip()]
    if remove:
        existing = [c for c in existing if c != jid]
        print(f"Dihapus dari free-response: {jid}")
    else:
        if jid in existing:
            print(f"Sudah terdaftar: {jid}")
        else:
            existing.append(jid)
            print(f"Didaftarkan utk free-response: {jid}")
    vals[KEY] = ",".join(existing)
    write_env(vals)
    print(f"WHATSAPP_FREE_RESPONSE_CHATS = {vals[KEY]}")
    print("Restart gateway untuk menerapkan...")
    restart_gateway()
    print("Selesai.")


if __name__ == "__main__":
    main()