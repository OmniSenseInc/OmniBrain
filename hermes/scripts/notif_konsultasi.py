#!/usr/bin/env python3
"""Notifikasi otomatis: setiap klien SELESAI konsultasi (status ready_for_team)
dicetak ke stdout -> cron mengirimkannya ke grup. Dedupe via file state.

Script-only (tanpa LLM). Aman ganti provider.
"""
import json
import os
import sqlite3
import sys
import datetime

DATA_DIR = "/home/ubuntu/ai-agency/consulting/data"
DB = os.path.join(DATA_DIR, "consultations.sqlite3")
STATE = os.path.join(DATA_DIR, ".notif_konsultasi_sent.json")
WIB = datetime.timezone(datetime.timedelta(hours=7))


def load_sent():
    try:
        with open(STATE) as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_sent(sent):
    try:
        tmp = STATE + ".tmp"
        with open(tmp, "w") as f:
            json.dump(sorted(sent), f)
        os.replace(tmp, STATE)
    except Exception as e:
        print(f"[warn] gagal simpan state: {e}", file=sys.stderr)


def fmt_ts(ts):
    try:
        return datetime.datetime.fromtimestamp(float(ts), WIB).strftime("%d %b %H:%M WIB")
    except Exception:
        return "?"


def _ambil(v):
    """Jawaban discovery bisa berupa string atau dict {answer,...}. Ambil teksnya."""
    if isinstance(v, dict):
        return v.get("answer") or v.get("value") or ""
    return v or ""


def ringkas(tid, body):
    try:
        d = json.loads(body)
    except Exception:
        return f"📥 *KLIEN SELESAI KONSULTASI* — {tid}\n(detail tidak terbaca)"
    r = d.get("result", {}) or {}
    disc = d.get("discovery", {}) or {}
    ctx = r.get("context_reported", {}) or {}

    problem = _ambil(disc.get("problem_example")) or _ambil(ctx.get("problem")) or "-"
    impact = _ambil(disc.get("impact")) or "-"
    proses = ctx.get("process") or _ambil(disc.get("process_steps")) or "-"
    score = r.get("score")
    band = r.get("band") or "-"
    verified = r.get("verified_evidence_coverage_percent")

    dims = r.get("dimensions") or []
    lemah = sorted([x for x in dims if x.get("score") is not None],
                   key=lambda x: x.get("score"))[:2]
    lemah_txt = ", ".join(f"{x.get('name')} ({x.get('score'):.0f})" for x in lemah) or "-"

    created = None
    try:
        import sqlite3 as _s
        c = _s.connect(DB)
        cur = c.cursor()
        cur.execute("SELECT created FROM tickets WHERE id=?", (tid,))
        row = cur.fetchone()
        if row:
            created = row[0]
        c.close()
    except Exception:
        pass

    lines = [
        "📥 *KLIEN SELESAI KONSULTASI* — siap review tim",
        "",
        f"• Kasus: {tid}",
        f"• Proses: {proses}",
        f"• Keluhan: {str(problem)[:200]}",
        f"• Dampak: {str(impact)[:150]}",
    ]
    if score is not None:
        lines.append(f"• Skor awal: *{score}/100* — {band}")
    lines.append(f"• Dimensi terlemah: {lemah_txt}")
    if verified is not None:
        lines.append(f"• Bukti terverifikasi: {verified:.0f}% (sisanya self-report)")
    if created:
        lines.append(f"• Waktu masuk: {fmt_ts(created)}")
    lines += [
        "",
        "➡️ Sinyal: *handoff, lanjut ke penawaran* (harga & closing tetap di tim).",
    ]
    return "\n".join(lines)


def main():
    if not os.path.exists(DB):
        return 0
    sent = load_sent()
    try:
        c = sqlite3.connect(DB)
        c.row_factory = sqlite3.Row
        cur = c.cursor()
        cur.execute("SELECT id, body FROM tickets WHERE status='ready_for_team' ORDER BY created ASC")
        rows = cur.fetchall()
        c.close()
    except Exception as e:
        print(f"[warn] gagal baca DB: {e}", file=sys.stderr)
        return 0

    baru = [r for r in rows if r["id"] not in sent]
    if not baru:
        return 0  # stdout kosong -> cron tidak mengirim apa pun

    out = []
    for r in baru:
        out.append(ringkas(r["id"], r["body"]))
    print("\n\n".join(out))

    sent.update(r["id"] for r in baru)
    save_sent(sent)
    return 0


if __name__ == "__main__":
    sys.exit(main())
