#!/usr/bin/env python3
"""ig_post.py — posting poster OmniSense ke Instagram (@omnisense_id) via API resmi.

Alur (terverifikasi):
  1. PNG -> JPEG (Meta HANYA menerima JPEG; poster generator kita keluarkan PNG)
  2. upload JPEG ke host publik sementara (litterbox 72 jam, fallback tmpfiles.org)
     karena Meta men-download sendiri gambar dari URL publik
  3. POST /{ig-user-id}/media  -> container
  4. poll status_code sampai FINISHED
  5. (--publish) POST /{ig-user-id}/media_publish -> live + ambil permalink
  6. catat ke CONTENT_POSTED_LOG.md + state dedup ig_posted.json

Contoh:
  # uji kering (upload + container, TIDAK live)
  .venv/bin/python ig_post.py --image konten_berita_id.png --caption-file cap.txt
  # benar-benar posting
  .venv/bin/python ig_post.py --image konten_berita_id.png --caption-file cap.txt \
      --hashtags "#AIAgent #OmniSense" --publish

Token dibaca dari ig_token.env (dibuat oleh ig_token.py). Jalankan dengan python venv
ai-agency supaya PIL tersedia untuk konversi JPEG.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(HERE, "ig_token.env")
POSTED_STATE = os.path.join(HERE, "ig_posted.json")
POSTED_LOG = os.path.join(HERE, "CONTENT_POSTED_LOG.md")
API = "https://graph.instagram.com/v23.0"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
HASHTAG_DEFAULT = "#OmniSense #AIAgent #AIuntukBisnis #KonsultanAI #OmniSenseID"


# ------------------------------------------------------------------ helpers
def load_token() -> str:
    tok = os.getenv("IG_LONG_LIVED_TOKEN")
    if tok:
        return tok.strip()
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as fh:
            for line in fh:
                if line.startswith("IG_LONG_LIVED_TOKEN="):
                    return line.split("=", 1)[1].strip()
    print(f"GAGAL: token tidak ditemukan. Jalankan `python3 ig_token.py exchange <token>` "
          f"atau isi IG_LONG_LIVED_TOKEN di {STATE_FILE}.", file=sys.stderr)
    sys.exit(1)


def state_get(key: str) -> str:
    if not os.path.exists(STATE_FILE):
        return ""
    with open(STATE_FILE) as fh:
        for line in fh:
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip()
    return ""


def http(method: str, url: str, params: dict) -> dict:
    if method == "POST":
        req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(),
                                     headers={"Accept": "application/json"})
    else:
        req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params),
                                     headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        try:
            return json.loads(body)
        except Exception:
            return {"error": {"message": f"HTTP {e.code}: {body[:300]}", "code": e.code}}
    except Exception as e:
        return {"error": {"message": f"{type(e).__name__}: {e}", "code": -1}}


def fail(payload: dict) -> None:
    err = payload.get("error", {})
    msg, code = err.get("message", "unknown"), err.get("code")
    print(f"GAGAL: {msg} (code={code})", file=sys.stderr)
    if code == 190:
        print("  -> token expired/dicabut. Ambil token baru dari App Dashboard, lalu `ig_token.py exchange`.",
              file=sys.stderr)
    elif code == 9007:
        print("  -> rate limit / akun dibatasi sementara.", file=sys.stderr)
    sys.exit(1)


def to_jpeg(src: str) -> str:
    """PNG (atau format lain) -> JPEG. Return path JPEG."""
    if src.lower().endswith((".jpg", ".jpeg")):
        return src
    try:
        from PIL import Image
    except ImportError:
        print("GAGAL: butuh PIL untuk konversi PNG->JPEG. Jalankan dengan .venv/bin/python.", file=sys.stderr)
        sys.exit(1)
    dst = os.path.join(tempfile.gettempdir(), os.path.splitext(os.path.basename(src))[0] + "_ig.jpg")
    im = Image.open(src).convert("RGB")
    im.save(dst, quality=92, optimize=True)
    w, h = im.size
    ratio = w / h
    if not (0.79 <= ratio <= 1.92):
        print(f"PERINGATAN: rasio {w}x{h} ({ratio:.2f}) di luar rentang Meta 4:5–1.91:1.", file=sys.stderr)
    print(f"  JPEG siap: {dst} ({w}x{h}, {os.path.getsize(dst)//1024} KB)")
    return dst


def cek_url_gambar(url: str) -> bool:
    """Pastikan URL publik benar-benar menyajikan GAMBAR, bukan halaman HTML.
    Meta yang mengunduh gambar; kalau yang datang HTML, container langsung gagal."""
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{content_type}",
             "-L", "-m", "60", "-A", UA, url],
            capture_output=True, text=True, timeout=90).stdout.strip()
    except Exception:
        return False
    print(f"  cek URL: {out}")
    code, _, ctype = out.partition(" ")
    return code.startswith("2") and ctype.startswith("image/")


def upload_public(path: str) -> str:
    """Upload ke host publik sementara. Return URL publik yang SUDAH diverifikasi menyajikan gambar."""
    tries = [
        ("uguu", ["curl", "-s", "-m", "120", "-A", UA, "-F", f"files[]=@{path}",
                  "https://uguu.se/upload?output=text"]),
        ("litterbox", ["curl", "-s", "-m", "120", "-A", UA,
                       "-F", "reqtype=fileupload", "-F", "time=72h",
                       "-F", f"fileToUpload=@{path}",
                       "https://litterbox.catbox.moe/resources/internals/api.php"]),
    ]
    for name, cmd in tries:
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=150).stdout.strip()
        except Exception as e:
            print(f"  upload {name} gagal: {e}", file=sys.stderr)
            continue
        if not out.startswith("http"):
            print(f"  upload {name} gagal: {out[:150]}", file=sys.stderr)
            continue
        if cek_url_gambar(out):
            print(f"  URL publik ({name}): {out}")
            return out
        print(f"  upload {name}: URL tidak menyajikan gambar (bukan image/*) — coba host lain", file=sys.stderr)
    print("GAGAL: semua host gambar publik gagal. Cek koneksi/rate limit.", file=sys.stderr)
    sys.exit(1)


def already_posted(key: str) -> bool:
    if not os.path.exists(POSTED_STATE):
        return False
    try:
        data = json.load(open(POSTED_STATE))
    except Exception:
        return False
    return key in data.get("keys", [])


def mark_posted(key: str, media_id: str, permalink: str, caption: str) -> None:
    data = {"keys": [], "items": []}
    if os.path.exists(POSTED_STATE):
        try:
            data = json.load(open(POSTED_STATE))
        except Exception:
            pass
    data.setdefault("keys", []).append(key)
    data.setdefault("items", []).append({
        "key": key, "media_id": media_id, "permalink": permalink,
        "posted_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "caption_head": caption[:120],
    })
    data["keys"] = data["keys"][-300:]
    data["items"] = data["items"][-300:]
    with open(POSTED_STATE, "w") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def append_log(key: str, media_id: str, permalink: str, caption: str) -> None:
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    block = (f"\n## {stamp} — POSTED ke Instagram\n"
             f"- Topik/kunci: {key}\n"
             f"- Media ID: {media_id}\n"
             f"- Permalink: {permalink}\n"
             f"- Caption (potongan): {caption[:200].replace(chr(10), ' ')}\n")
    if not os.path.exists(POSTED_LOG):
        with open(POSTED_LOG, "w") as fh:
            fh.write("# Log konten OmniSense yang sudah diposting\n")
    with open(POSTED_LOG, "a") as fh:
        fh.write(block)


# ------------------------------------------------------------------ main
def main() -> None:
    p = argparse.ArgumentParser(description="Posting poster OmniSense ke Instagram via API resmi.")
    p.add_argument("--image", required=True, help="file poster (PNG/JPG)")
    p.add_argument("--caption", help="teks caption")
    p.add_argument("--caption-file", help="file teks caption (alternatif --caption)")
    p.add_argument("--hashtags", default=HASHTAG_DEFAULT, help="hashtag ditambahkan di akhir caption")
    p.add_argument("--key", help="kunci dedup (default: nama file tanpa ekstensi)")
    p.add_argument("--publish", action="store_true", help="benar-benar publikasikan (default: uji kering)")
    p.add_argument("--force", action="store_true", help="abaikan penjagaan dedup")
    args = p.parse_args()

    if not os.path.exists(args.image):
        print(f"GAGAL: file {args.image} tidak ada.", file=sys.stderr)
        sys.exit(1)

    caption = args.caption or ""
    if args.caption_file:
        with open(args.caption_file) as fh:
            caption = fh.read().strip()
    if args.hashtags:
        caption = (caption.rstrip() + "\n\n" + args.hashtags.strip()).strip()
    if not caption:
        print("GAGAL: caption kosong (pakai --caption atau --caption-file).", file=sys.stderr)
        sys.exit(1)

    # Instagram menolak caption > 2200 karakter (code 36004). Potong rapi di
    # batas kalimat/kata supaya tidak pernah gagal karena kepanjangan.
    # Hashtag (ekor caption) dipertahankan; yang dipotong isi tengahnya.
    LIMIT = 2200
    if len(caption) > LIMIT:
        asli = len(caption)
        ekor = ""
        if args.hashtags and caption.rstrip().endswith(args.hashtags.strip()):
            ekor = "\n\n" + args.hashtags.strip()
            badan = caption.rstrip()[: -len(ekor)].rstrip()
        else:
            badan = caption.rstrip()
        sisa = LIMIT - len(ekor)
        if len(badan) > sisa:
            potong = badan[:sisa]
            for sep in ("\n\n", ". ", "\n", " "):
                pos = potong.rfind(sep)
                if pos > sisa - 200:
                    potong = potong[:pos]
                    break
            badan = potong.rstrip()
        caption = (badan + ekor).strip()
        print(f"[caption] dipotong dari {asli} -> {len(caption)} karakter (limit {LIMIT}).")

    key = args.key or os.path.splitext(os.path.basename(args.image))[0]
    if not args.force and already_posted(key):
        print(f"LEWAT: '{key}' sudah pernah diposting (cek {POSTED_STATE}). Pakai --force kalau memang mau ulang.")
        return

    token = load_token()
    ig_id = state_get("IG_USER_ID")
    if not ig_id:
        me = http("GET", f"{API}/me", {"fields": "id,username", "access_token": token})
        if me.get("error"):
            fail(me)
        ig_id = me["id"]
    print(f"Target akun: {state_get('IG_USERNAME') or ig_id} ({ig_id})")

    print("[1/4] siapkan gambar")
    jpg = to_jpeg(args.image)

    print("[2/4] upload ke host publik")
    url = upload_public(jpg)

    print("[3/4] buat container")
    c = http("POST", f"{API}/{ig_id}/media",
             {"image_url": url, "caption": caption, "access_token": token})
    if c.get("error"):
        fail(c)
    cid = c["id"]
    print(f"  container: {cid}")
    status = ""
    for i in range(15):
        s = http("GET", f"{API}/{cid}", {"fields": "status_code,status", "access_token": token})
        if s.get("error"):
            fail(s)
        status = s.get("status_code", "")
        if status in ("FINISHED", "ERROR", "EXPIRED"):
            break
        time.sleep(4)
    print(f"  status container: {status}")
    if status != "FINISHED":
        print(f"GAGAL: container tidak FINISHED (status={status}). Gambar tidak dipublikasikan.", file=sys.stderr)
        sys.exit(1)

    if not args.publish:
        print("[4/4] UJI KERING — media_publish TIDAK dipanggil, tidak ada yang live.")
        print(f"      container {cid} akan kedaluwarsa sendiri dalam 24 jam.")
        print("      Tambahkan --publish untuk benar-benar posting.")
        return

    print("[4/4] publish")
    pub = http("POST", f"{API}/{ig_id}/media_publish",
               {"creation_id": cid, "access_token": token})
    if pub.get("error"):
        fail(pub)
    media_id = pub["id"]
    info = http("GET", f"{API}/{media_id}", {"fields": "permalink,timestamp", "access_token": token})
    permalink = info.get("permalink", "(permalink belum tersedia)")
    print("BERHASIL DIPOSTING")
    print(f"  media id  : {media_id}")
    print(f"  permalink : {permalink}")
    mark_posted(key, media_id, permalink, caption)
    append_log(key, media_id, permalink, caption)


if __name__ == "__main__":
    main()
