#!/usr/bin/env python3
"""Nag-DM Michael & Nathanael (cron, no_agent).
Print pesan -> dikirim sebagai DM ke target. Print kosong -> tidak ada yang dikirim.
Auto-stop: begitu ada pesan WhatsApp masuk berisi STOP/BERHENTI setelah
START_TS, script menulis flag & diam selamanya.
"""
import os
import pathlib
import re
import sqlite3
import sys
import time

HOME = pathlib.Path(os.path.expanduser("~/.hermes"))
FLAG = HOME / "nag_stop.flag"
STATE = HOME / "state.db"
START_TS = 1789524000.0  # 2026-09-16 09:00 WIB

NAG = (
    "\U0001F514 Pengingat otomatis OmniSense.\n\n"
    "Michael & Nathanael \u2014 tolong cek & respon di grup ya.\n\n"
    "Pesan ini terkirim berkala dan HANYA berhenti kalau salah satu dari kalian "
    "balas *STOP* di chat ini."
)

STOP_RE = re.compile(r"^\s*(stop|berhenti)\b", re.IGNORECASE)


def already_stopped():
    if FLAG.exists():
        return True
    if not STATE.exists():
        return False
    try:
        con = sqlite3.connect("file:" + str(STATE) + "?mode=ro", uri=True)
        try:
            rows = con.execute(
                "SELECT m.content FROM messages m JOIN sessions s ON s.id = m.session_id "
                "WHERE m.role = 'user' AND s.source = 'whatsapp' AND m.timestamp > ? "
                "ORDER BY m.id DESC LIMIT 200",
                (START_TS,),
            ).fetchall()
        finally:
            con.close()
    except Exception:
        return False
    for row in rows:
        content = row[0] if row else None
        if content and STOP_RE.match(str(content)):
            try:
                FLAG.write_text("stopped at " + str(time.time()) + "\n", encoding="utf-8")
            except Exception:
                pass
            return True
    return False


if already_stopped():
    sys.exit(0)

print(NAG)
