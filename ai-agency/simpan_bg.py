#!/usr/bin/env python3
"""Simpan latar terpilih (webp -> jpg) + tulis atribusi. Pakai: python3 simpan_bg.py <src> <nama> <judul> <lisensi> <kredit> <halaman>"""
import json
import os
import sys

from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE, "assets", "bg")

src, nama, judul, lisensi, kredit, halaman = sys.argv[1:7]
os.makedirs(BG_DIR, exist_ok=True)
out = os.path.join(BG_DIR, nama + ".jpg")

img = Image.open(src)
if img.mode != "RGB":
    img = img.convert("RGB")
img.save(out, "JPEG", quality=92)

meta = {
    "judul": judul,
    "berkas": out,
    "lebar": img.width,
    "tinggi": img.height,
    "lisensi": lisensi,
    "kredit": kredit,
    "halaman": halaman,
    "aman_komersial": True,
    "wajib_kredit": not lisensi.lower().startswith(("cc0", "public domain")),
    "byte": os.path.getsize(out),
}
with open(os.path.join(BG_DIR, nama + ".json"), "w", encoding="utf-8") as fh:
    json.dump(meta, fh, ensure_ascii=False, indent=2)
print(f"OK {out} {img.width}x{img.height} {lisensi}")
