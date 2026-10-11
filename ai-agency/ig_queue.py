#!/usr/bin/env python3
"""ig_queue.py — alur persetujuan posting Instagram OmniSense (preview dulu, baru live).

Kenapa ada file ini: cron digest menghasilkan poster + caption tiap 5 jam, tapi user mau
ME-REVIEW dulu sebelum sesuatu masuk ke akun @omnisense_id. Jadi digest hanya MENARUH
kandidat di antrean (queue); posting benar-benar terjadi saat user menyetujui.

State: /home/ubuntu/ai-agency/ig_pending.json  (status: pending | published | cancelled)

Perintah:
  queue   --image konten_berita_id.png --caption-file cap.txt --key slug-topik [--note "..."]
  status  [--json]                 # apa yang sedang menunggu persetujuan
  guard   --key slug-topik         # exit 1 kalau topik sudah diposting / sedang pending
  publish [--dry]                  # setujui -> posting live (--dry = container saja)
  cancel  [--why "..."]            # tolak

Semua kredensial/token ditangani ig_post.py (baca ig_token.env). File ini stdlib saja.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
PENDING = os.path.join(HERE, "ig_pending.json")
POSTED_STATE = os.path.join(HERE, "ig_posted.json")
POSTER = os.path.join(HERE, "ig_post.py")
VENV_PY = os.path.join(HERE, ".venv", "bin", "python")
HASHTAG_DEFAULT = "#OmniSense #AIAgent #AIuntukBisnis #KonsultanAI #OmniSenseID"
ARCHIVE_DIR = os.path.join(HERE, "ig_arsip")
ARCHIVE_LOG = os.path.join(ARCHIVE_DIR, "arsip.json")


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_pending() -> dict:
    if not os.path.exists(PENDING):
        return {}
    try:
        return json.load(open(PENDING))
    except Exception:
        return {}


def save_pending(data: dict) -> None:
    with open(PENDING, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def posted_keys() -> list:
    if not os.path.exists(POSTED_STATE):
        return []
    try:
        return json.load(open(POSTED_STATE)).get("keys", [])
    except Exception:
        return []


def age_hours(iso: str) -> float:
    try:
        t = datetime.fromisoformat(iso)
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 3600.0
    except Exception:
        return -1.0


def archive_pending(st: dict, reason: str) -> None:
    """Simpan kandidat pending ke arsip (gambar + caption + metadata) supaya
    tidak hilang saat antrean ditimpa/dibatalkan/dipublikasikan."""
    if not st or not st.get("key"):
        return
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    entry = dict(st)
    entry["archived_at"] = now_iso()
    entry["archive_reason"] = reason
    # salin gambarnya supaya poster lama tidak tertimpa render berikutnya
    img = st.get("image")
    if img and os.path.exists(img):
        ext = os.path.splitext(img)[1] or ".png"
        dest = os.path.join(ARCHIVE_DIR, f"{st['key'][:60]}{ext}")
        try:
            shutil.copy2(img, dest)
            entry["image_archive"] = dest
        except Exception:
            pass
    log = []
    if os.path.exists(ARCHIVE_LOG):
        try:
            log = json.load(open(ARCHIVE_LOG))
        except Exception:
            log = []
    log.append(entry)
    with open(ARCHIVE_LOG, "w") as fh:
        json.dump(log, fh, indent=2, ensure_ascii=False)


def python_bin() -> str:
    return VENV_PY if os.path.exists(VENV_PY) else sys.executable


# ------------------------------------------------------------------ perintah
def cmd_queue(args) -> None:
    image = os.path.abspath(args.image)
    if not os.path.exists(image):
        print(f"GAGAL: gambar {image} tidak ada.", file=sys.stderr)
        sys.exit(1)

    caption = (args.caption or "").strip()
    if args.caption_file:
        with open(args.caption_file) as fh:
            caption = fh.read().strip()
    if not caption:
        print("GAGAL: caption kosong (pakai --caption-file atau --caption).", file=sys.stderr)
        sys.exit(1)

    hashtags = args.hashtags if args.hashtags is not None else HASHTAG_DEFAULT
    # caption disimpan TANPA hashtag; hashtag ditambahkan ig_post.py saat posting
    if hashtags:
        caption = caption.replace(hashtags, "").rstrip()

    if args.key in posted_keys():
        print(f"LEWAT: '{args.key}' sudah pernah diposting — tidak diantrekan ulang.")
        return

    old = load_pending()
    if old.get("status") == "pending":
        print(f"PERINGATAN: kandidat sebelumnya ('{old.get('key')}', "
              f"{age_hours(old.get('created_at', '')):.1f} jam lalu) DIGANTI oleh '{args.key}' "
              f"— disimpan ke arsip (ig_arsip/).")
        archive_pending(old, f"ditimpa oleh '{args.key}'")

    state = {
        "status": "pending",
        "key": args.key,
        "image": image,
        "image_name": os.path.basename(image),
        "caption": caption,
        "hashtags": hashtags,
        "note": args.note or "",
        "created_at": now_iso(),
        "created_by": args.by or "cron",
        "queued_count": int(old.get("queued_count", 0)) + 1,
    }
    save_pending(state)

    # simpan juga salinan caption supaya gampang dibaca/diedit manusia
    with open(os.path.join(HERE, "ig_caption_pending.txt"), "w") as fh:
        fh.write(caption + ("\n\n" + hashtags if hashtags else "") + "\n")

    print("DIANTREKAN (belum live — menunggu persetujuan user)")
    print(f"  kunci   : {args.key}")
    print(f"  gambar  : {image}")
    print(f"  caption : {len(caption)} karakter (+{len(hashtags)} kar hashtag)")
    print("  Setujui : balas 'post' di grup home WhatsApp (atau jalankan ig_queue.py publish)")


def cmd_status(args) -> None:
    st = load_pending()
    if not st:
        print("Tidak ada kandidat posting (antrean kosong).")
        return
    if args.json:
        print(json.dumps(st, indent=2, ensure_ascii=False))
        return
    status = st.get("status")
    print(f"status  : {status}")
    print(f"kunci   : {st.get('key')}")
    print(f"gambar  : {st.get('image')}")
    if status == "pending":
        print(f"umur    : {age_hours(st.get('created_at', '')):.1f} jam (dibuat {st.get('created_at')})")
        print(f"oleh    : {st.get('created_by')}")
        if st.get("note"):
            print(f"catatan : {st.get('note')}")
        print(f"caption : {st.get('caption', '')[:300]}...")
        print("aksi    : balas 'post' untuk live, atau 'batal' untuk tolak")
    else:
        print(f"selesai : {st.get('published_at') or st.get('cancelled_at')}")
        if st.get("permalink"):
            print(f"permalink: {st.get('permalink')}")


def cmd_guard(args) -> None:
    if args.key in posted_keys():
        print(f"SUDAH POSTED: '{args.key}'")
        sys.exit(1)
    st = load_pending()
    if st.get("status") == "pending" and st.get("key") == args.key:
        print(f"SEDANG MENUNGGU PERSETUJUAN: '{args.key}' (jangan diantrekan ulang)")
        sys.exit(1)
    print(f"AMAN: '{args.key}' belum pernah diposting dan tidak sedang menunggu.")


def cmd_cancel(args) -> None:
    st = load_pending()
    if st.get("status") != "pending":
        print("Tidak ada kandidat pending untuk dibatalkan.")
        return
    st["status"] = "cancelled"
    st["cancelled_at"] = now_iso()
    st["cancel_reason"] = args.why or ""
    save_pending(st)
    print(f"DIBATALKAN: '{st.get('key')}' tidak akan diposting.")


def cmd_publish(args) -> None:
    st = load_pending()
    if st.get("status") != "pending":
        print("GAGAL: tidak ada kandidat yang menunggu persetujuan (jalankan `ig_queue.py status`).",
              file=sys.stderr)
        sys.exit(1)

    image = st["image"]
    if not os.path.exists(image):
        print(f"GAGAL: gambar {image} sudah tidak ada. Antrekan ulang.", file=sys.stderr)
        sys.exit(1)

    cap_path = os.path.join(tempfile.gettempdir(), f"ig_cap_{st['key'][:40]}.txt")
    with open(cap_path, "w") as fh:
        fh.write(st["caption"])

    cmd = [python_bin(), POSTER, "--image", image, "--caption-file", cap_path,
           "--key", st["key"]]
    if st.get("hashtags"):
        cmd += ["--hashtags", st["hashtags"]]
    if not args.dry:
        cmd += ["--publish"]
    if args.force:
        cmd += ["--force"]

    print(f"{'UJI KERING' if args.dry else 'PUBLISH'} via ig_post.py (kunci: {st['key']})")
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=280)
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.strip())

    if proc.returncode != 0:
        print("GAGAL: ig_post.py mengembalikan error — kandidat TETAP menunggu (bisa dicoba lagi).",
              file=sys.stderr)
        sys.exit(proc.returncode)

    if args.dry:
        print("UJI KERING selesai — tidak ada yang live, kandidat tetap menunggu persetujuan.")
        return

    m = re.search(r"media id\s*:\s*(\S+)", out)
    p = re.search(r"permalink\s*:\s*(\S+)", out)
    st["status"] = "published"
    st["published_at"] = now_iso()
    st["media_id"] = m.group(1) if m else ""
    st["permalink"] = p.group(1) if p else ""
    save_pending(st)
    print("SELESAI: kandidat ditandai published.")
    if st["permalink"]:
        print(f"  permalink: {st['permalink']}")


def cmd_autopost(args) -> None:
    """FULL AUTO: publish kandidat pending tanpa perlu persetujuan.
    Dipanggil oleh cron script-only (tanpa LLM). Idempotent: kalau antrean
    kosong / sudah published, keluar tenang tanpa error (watchdog pattern)."""
    st = load_pending()
    if not st:
        if args.verbose:
            print("AUTOPOST: antrean kosong — tidak ada yang diposting.")
        return
    if st.get("status") != "pending":
        if args.verbose:
            print(f"AUTOPOST: tidak ada kandidat pending (status={st.get('status')}) — lewat.")
        return

    key = st.get("key", "?")
    umur = age_hours(st.get("created_at", ""))

    # Opsional: tunggu minimal N menit supaya tidak tabrakan dengan jendela
    # revisi manual (mis. user mau 'batal' dulu).
    if args.min_age_minutes and umur * 60 < args.min_age_minutes:
        if args.verbose:
            print(f"AUTOPOST: '{key}' baru {umur*60:.0f} menit — belum {args.min_age_minutes} menit, tunda.")
        return

    if key in posted_keys():
        archive_pending(st, "sudah ada di ig_posted.json (skip)")
        st["status"] = "published"
        st["published_at"] = now_iso()
        st["note_autopost"] = "sudah pernah diposting, dilewati"
        save_pending(st)
        print(f"AUTOPOST: '{key}' sudah pernah diposting — dilewati.")
        return

    print(f"AUTOPOST: mempublikasikan '{key}' (umur {umur:.1f} jam)...")
    try:
        cmd_publish(argparse.Namespace(dry=False, force=False))
    except SystemExit as e:
        if e.code not in (0, None):
            print(f"AUTOPOST: publish GAGAL untuk '{key}' — kandidat tetap pending, coba lagi nanti.",
                  file=sys.stderr)
            sys.exit(1)
        return

    st2 = load_pending()
    if st2.get("status") == "published":
        archive_pending(st2, "dipublikasikan via autopost")
        print(f"AUTOPOST: BERHASIL — {st2.get('permalink', '(permalink tak terbaca)')}")


def cmd_arsip(args) -> None:
    """Lihat kandidat yang pernah diarsipkan (tidak hilang saat antrean ditimpa)."""
    if not os.path.exists(ARCHIVE_LOG):
        print("Arsip kosong — belum ada kandidat yang diarsipkan.")
        return
    try:
        log = json.load(open(ARCHIVE_LOG))
    except Exception:
        print("Arsip tidak terbaca.")
        return
    if args.json:
        print(json.dumps(log, indent=2, ensure_ascii=False))
        return
    print(f"ARSIP: {len(log)} kandidat")
    for e in log:
        print(f"- {e.get('key')} | {e.get('archived_at')} | {e.get('archive_reason')}")
        print(f"    caption: {str(e.get('caption',''))[:80]}...")
        if e.get("image_archive"):
            print(f"    gambar : {e['image_archive']}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Antrean persetujuan posting Instagram OmniSense.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    q = sub.add_parser("queue", help="antrekan kandidat posting (belum live)")
    q.add_argument("--image", required=True)
    q.add_argument("--caption")
    q.add_argument("--caption-file")
    q.add_argument("--key", required=True)
    q.add_argument("--hashtags", default=None)
    q.add_argument("--note", default="")
    q.add_argument("--by", default="cron")
    q.set_defaults(func=cmd_queue)

    s = sub.add_parser("status", help="lihat kandidat yang menunggu")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_status)

    g = sub.add_parser("guard", help="exit 1 kalau topik sudah posted / sedang pending")
    g.add_argument("--key", required=True)
    g.set_defaults(func=cmd_guard)

    c = sub.add_parser("cancel", help="tolak kandidat")
    c.add_argument("--why", default="")
    c.set_defaults(func=cmd_cancel)

    p = sub.add_parser("publish", help="setujui -> posting live")
    p.add_argument("--dry", action="store_true", help="container saja, tidak live")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_publish)

    a = sub.add_parser("autopost", help="FULL AUTO: publish kandidat pending tanpa persetujuan")
    a.add_argument("--min-age-minutes", type=int, default=0,
                   help="tunda kalau kandidat lebih baru dari N menit (jendela revisi)")
    a.add_argument("--verbose", action="store_true")
    a.set_defaults(func=cmd_autopost)

    ar = sub.add_parser("arsip", help="lihat kandidat yang diarsipkan (tidak hilang saat ditimpa)")
    ar.add_argument("--json", action="store_true")
    ar.set_defaults(func=cmd_arsip)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
