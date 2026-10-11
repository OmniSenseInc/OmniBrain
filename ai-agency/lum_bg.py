#!/usr/bin/env python3
"""Cetak luminansi rata-rata (0-255) semua berkas di assets/bg/ untuk memilih latar gelap."""
import glob
import os
from PIL import Image, ImageStat

for f in sorted(glob.glob("assets/bg/*")):
    if os.path.splitext(f)[1].lower() not in (".jpg", ".jpeg", ".png", ".webp"):
        continue
    try:
        im = Image.open(f).convert("L")
        im.thumbnail((400, 400))
        lum = ImageStat.Stat(im).mean[0]
        print(f"{lum:6.1f}  {f}")
    except Exception as e:  # noqa: BLE001
        print(f"  ERROR  {f}: {e}")
