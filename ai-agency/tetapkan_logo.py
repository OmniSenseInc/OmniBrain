#!/usr/bin/env python3
"""Tetapkan aset logo OmniSense dari sumber resmi (logo_sumber.jpg).

Sumber : logo_sumber.jpg (1254x1254, mark putih di atas hitam)
Keluaran (folder brand/):
  - logo-mark-white-1024.png   master transparan, mark putih #FFFFFF
  - logo-mark-white-{512,256,128,64,32}.png  ukuran siap pakai
  - logo-mark-teal-512.png     varian aksen teal #14B8A6
  - logo-mark-obsidian-512.png varian gelap #09090B (untuk latar terang)
  - favicon-32.png / favicon-16.png / favicon.ico
Alpha diambil dari luminance sumber (anti-alias ikut terbawa), lalu di-trim rapat.
"""
import os
from PIL import Image, ImageFilter

SRC = "/home/ubuntu/ai-agency/logo_sumber.jpg"
OUT = "/home/ubuntu/ai-agency/brand"
AMBANG = 18

os.makedirs(OUT, exist_ok=True)
src = Image.open(SRC).convert("RGB")
lum = src.convert("L")

# alpha dari luminance: hitam -> 0, putih -> 255, dengan ramp untuk tepi anti-alias
alpha = lum.point(lambda v: 0 if v < AMBANG else min(255, int((v - AMBANG) * 255 / (255 - AMBANG))))
alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))
bbox = alpha.getbbox()
print("bbox mark:", bbox, "dari", src.size)


def tint(color, size=None):
    im = Image.new("RGBA", src.size, color + (0,))
    im.putalpha(alpha)
    im = im.crop(bbox)
    if size:
        im = im.resize((size, size), Image.LANCZOS)
    return im


master = tint((255, 255, 255))
master.save(f"{OUT}/logo-mark-white-1024.png")
print("master:", master.size)

for s in (512, 256, 128, 64, 32):
    tint((255, 255, 255), s).save(f"{OUT}/logo-mark-white-{s}.png")
tint((20, 184, 166), 512).save(f"{OUT}/logo-mark-teal-512.png")
tint((9, 9, 11), 512).save(f"{OUT}/logo-mark-obsidian-512.png")

# favicon: mark putih di atas obsidian (kotak) supaya terlihat di tab browser terang/gelap
for s in (32, 16):
    icon = Image.new("RGBA", (s, s), (9, 9, 11, 255))
    m = tint((255, 255, 255), int(s * 0.82))
    icon.alpha_composite(m, ((s - m.width) // 2, (s - m.height) // 2))
    icon.save(f"{OUT}/favicon-{s}.png")
    if s == 32:
        icon.save(f"{OUT}/favicon.ico", sizes=[(32, 32), (16, 16)])
print("selesai ->", OUT)
print(sorted(os.listdir(OUT)))
