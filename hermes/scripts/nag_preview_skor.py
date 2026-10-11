#!/usr/bin/env python3
"""Pengingat skor landing page OmniSense — job cron no_agent (tanpa LLM).

stdout dicetak apa adanya ke grup home WhatsApp. stdout KOSONG = tidak ada yang
dikirim (jadi job ini berhenti sendiri begitu tim membalas).

Aturan main:
- Berhenti permanen kalau sudah ada balasan manusia di grup setelah START_EPOCH
  (pesan masuk WhatsApp tersimpan di state.db dengan platform_message_id terisi).
- Link diambil LIVE dari log tunnel, jadi kalau cloudflared restart (URL quick
  tunnel berubah) pengingat tetap mengirim link yang benar.
- Kalau tunnel mati: service-nya direstart sekali, URL dibaca ulang; kalau masih
  mati keluar exit 1 supaya kegagalan tercatat di riwayat cron.
"""
import os
import re
import sqlite3
import subprocess
import sys
import time

GROUP = "120363411213386519@g.us"
START_EPOCH = 1790043949.0          # dibekukan saat job dibuat (2026-09-22 10:25 CST)
FLAG = "/home/ubuntu/ai-agency/.nag_preview_skor_stopped"
LOG = "/home/ubuntu/ai-agency/website/.preview_tunnel.log"
DB = os.path.expanduser("~/.hermes/state.db")
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")

TEXT = """Pengingat skor landing page OmniSense (masih nunggu dari kalian):

{url}

Buka di HP dan di laptop, lalu balas di grup ini: skor 1-10 + bagian mana yang paling lemah.
Sekalian cek bahasanya, masuk akal nggak kalau dibaca orang biasa.

Balas sambil tag bot ya, biar pengingat ini berhenti sendiri. Ketik STOP juga bisa."""


def mute(reason):
    try:
        with open(FLAG, "w") as fh:
            fh.write("%s %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
    except OSError:
        pass
    sys.exit(0)


if os.path.exists(FLAG):
    sys.exit(0)                                   # sudah dibisukan

# 1) Sudah ada balasan manusia di grup? -> bisukan diri sendiri.
try:
    con = sqlite3.connect("file:%s?mode=ro" % DB, uri=True)
    cur = con.execute(
        "SELECT COUNT(*) FROM messages m JOIN sessions s ON s.id = m.session_id "
        "WHERE s.source = 'whatsapp' AND s.chat_id = ? AND m.role = 'user' "
        "AND m.platform_message_id IS NOT NULL AND m.timestamp > ?",
        (GROUP, START_EPOCH),
    )
    hits = cur.fetchone()[0]
    con.close()
except Exception:
    hits = 0                                      # DB tak terbaca -> jangan berhenti nagging

if hits:
    mute("ada %d balasan tim di grup" % hits)

# 2) URL tunnel terkini (baca LIVE dari log, bukan konstanta).
def baca_url():
    try:
        with open(LOG, "r", errors="ignore") as fh:
            urls = URL_RE.findall(fh.read())
    except OSError:
        urls = []
    return urls[-1] if urls else ""


def hidup(url):
    # -4 wajib: mesin ini lebih suka IPv6 dan gagal connect kalau AAAA dipakai.
    r = subprocess.run(
        ["curl", "-s", "-4", "-o", "/dev/null", "-w", "%{http_code}",
         "--max-time", "12", url + "/"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() == "200"


url = baca_url()
if url and not hidup(url):
    env = dict(os.environ)
    env.setdefault("XDG_RUNTIME_DIR", "/run/user/%d" % os.getuid())
    env.setdefault("DBUS_SESSION_BUS_ADDRESS",
                   "unix:path=/run/user/%d/bus" % os.getuid())
    try:
        subprocess.run(["systemctl", "--user", "restart", "omnisense-preview-tunnel.service"],
                       env=env, capture_output=True, text=True, timeout=60)
    except Exception:
        pass
    time.sleep(14)                                # tunggu DNS quick tunnel siap
    url = baca_url()                              # URL bisa berubah setelah restart

if not url:
    sys.stderr.write("URL tunnel tidak ditemukan di %s\n" % LOG)
    sys.exit(1)
if not hidup(url):
    sys.stderr.write("tunnel preview tidak merespons: %s\n" % url)
    sys.exit(1)

print(TEXT.format(url=url))
