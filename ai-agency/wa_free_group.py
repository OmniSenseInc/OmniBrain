#!/usr/bin/env python3
"""Dijalankan BOT (agen OmniSense) utk /whitelist — TANPA restart gateway.
Hanya menambah JID grup ke WHATSAPP_FREE_RESPONSE_CHATS supaya bot free-response
di grup itu (client tak perlu men-tag). Tidak menyentuh key env lain & tidak restart
(soalnya bot berjalan di dalam gateway; restart akan memutus dirinya sendiri).

Dipanggil bot:  python3 wa_free_group.py --current
  (--current = deteksi grup WhatsApp terakhir aktif dari log gateway; cocok saat
  /whitelist diketik di dalam grup konsultasi.)

Opsional utk admin (tanpa restart): python3 wa_free_group.py <chatJid>

Catatan: efek diterapkan pada pesan berikutnya jika gateway membaca env live; jika
belum, lakukan sekali `hermes gateway restart` oleh admin.
"""

import sys
import os
import re

ENV = os.path.expanduser("~/.hermes/.env")
KEY = "WHATSAPP_FREE_RESPONSE_CHATS"
LOG = os.path.expanduser("~/.hermes/logs/gateway.log")


def detect_current_group_jid():
    if not os.path.exists(LOG):
        return None
    jids = re.findall(r"chat=([0-9]+@g\.us)", open(LOG, encoding="utf-8", errors="ignore").read())
    return jids[-1] if jids else None


def update_env(jid):
    vals = {}
    if os.path.exists(ENV):
        for line in open(ENV):
            line = line.rstrip("\n")
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                vals[k.strip()] = v.strip()
    existing = [c for c in vals.get(KEY, "").split(",") if c.strip()]
    if jid not in existing:
        existing.append(jid)
    vals[KEY] = ",".join(existing)

    lines = []
    for line in open(ENV):
        if line.rstrip("\n").startswith(KEY + "="):
            continue
        lines.append(line.rstrip("\n"))
    lines.append(f"{KEY}={vals[KEY]}".rstrip(","))
    open(ENV, "w").write("\n".join(lines) + "\n")
    return vals[KEY]


def main():
    args = sys.argv[1:]
    if "--current" in args:
        jid = detect_current_group_jid()
        if not jid:
            print("ERR: tidak dapat mendeteksi grup aktif dari log.")
            sys.exit(1)
        print(f"(grup aktif: {jid})")
    elif args:
        jid = args[0].strip()
    else:
        print("Pakai: python3 wa_free_group.py --current   (atau <chatJid>)")
        sys.exit(1)
    val = update_env(jid)
    print(f"OK: grup {jid} diaktifkan free-response (WHATSAPP_FREE_RESPONSE_CHATS={val}).")
    print("TANPA restart; jika belum aktif di pesan berikutnya, admin restart sekali.")


if __name__ == "__main__":
    main()