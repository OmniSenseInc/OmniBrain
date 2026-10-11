#!/usr/bin/env python3
"""Cek dimensi & mode poster."""
from PIL import Image

for f in ["konten_berita_id.png", "konten_berita_en.png"]:
    im = Image.open(f)
    print(f, im.size, im.mode)
