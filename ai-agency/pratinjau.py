#!/usr/bin/env python3
"""Buat pratinjau kecil untuk QA vision. Pakai: python3 pratinjau.py <in.jpg> <out.jpg> [lebar]"""
import sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
lebar = int(sys.argv[3]) if len(sys.argv) > 3 else 900
im = Image.open(src).convert("RGB")
r = lebar / im.width
im = im.resize((lebar, max(1, int(im.height * r))), Image.LANCZOS)
im.save(dst, "JPEG", quality=82)
print("OK", dst, im.size)
