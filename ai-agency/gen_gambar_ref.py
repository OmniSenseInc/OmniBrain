#!/usr/bin/env python3
"""Coba generate gambar via endpoint Api.b.ai (model gpt-image-2).

Dua mode:
  1. probe  : cek endpoint mana yang hidup (generations / edits)
  2. edits  : kirim gambar REFERENSI + prompt -> gambar baru (image-to-image)

Pemakaian:
  python3 gen_gambar_ref.py probe
  python3 gen_gambar_ref.py edits <ref.png> <out.png> <prompt_file.txt>
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.error

BASE = "https://api.b.ai/v1"


def key():
    k = os.environ.get("HERMES_CUSTOM_API_B_AI_API_KEY", "")
    if not k:
        # baca langsung dari .env
        with open("/home/ubuntu/.hermes/.env", encoding="utf-8") as fh:
            for line in fh:
                if line.startswith("HERMES_CUSTOM_API_B_AI_API_KEY="):
                    k = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
    return k


def post_json(path, payload, timeout=180):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key()}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:800]
    except Exception as e:  # noqa: BLE001
        return -1, f"{type(e).__name__}: {e}"


def post_multipart(path, fields, files, timeout=300):
    """files: list of (field, filename, bytes)"""
    boundary = "----omnisenseboundary7f3a"
    body = b""
    for k, v in fields.items():
        body += (f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n").encode()
    for field, fname, data in files:
        body += (
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"; "
            f"filename=\"{fname}\"\r\nContent-Type: image/png\r\n\r\n"
        ).encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        BASE + path,
        data=body,
        headers={
            "Authorization": f"Bearer {key()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:800]
    except Exception as e:  # noqa: BLE001
        return -1, f"{type(e).__name__}: {e}"


def simpan(resp, out):
    d = json.loads(resp)
    items = d.get("data") or []
    if not items:
        print("respons tanpa data:", resp[:400])
        return False
    it = items[0]
    if it.get("b64_json"):
        with open(out, "wb") as fh:
            fh.write(base64.b64decode(it["b64_json"]))
    elif it.get("url"):
        with urllib.request.urlopen(it["url"], timeout=120) as r, open(out, "wb") as fh:
            fh.write(r.read())
    else:
        print("format tak dikenal:", list(it.keys()))
        return False
    print("OK ->", out, os.path.getsize(out), "bytes")
    return True


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "probe"
    if cmd == "probe":
        for path, payload in [
            ("/images/generations", {"model": "gpt-image-2", "prompt": "a plain dark grey square", "n": 1, "size": "1024x1024"}),
        ]:
            st, body = post_json(path, payload)
            print(f"{path}: HTTP {st} -> {body[:300]}")
        return
    if cmd == "edits":
        ref, out, pf = sys.argv[2], sys.argv[3], sys.argv[4]
        prompt = open(pf, encoding="utf-8").read().strip()
        with open(ref, "rb") as fh:
            data = fh.read()
        for field in ("image", "image[]"):
            st, body = post_multipart(
                "/images/edits",
                {"model": "gpt-image-2", "prompt": prompt, "n": "1", "size": "1024x1536"},
                [(field, os.path.basename(ref), data)],
            )
            print(f"field={field}: HTTP {st} -> {body[:200]}")
            if st == 200:
                simpan(body, out)
                return
        return


if __name__ == "__main__":
    main()
