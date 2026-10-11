#!/usr/bin/env python3
"""Render mask logo OmniSense jadi ASCII + analisis polar berbasis centroid."""
import math
from PIL import Image

SRC = "/home/ubuntu/ai-agency/logo_omnisense_white.png"
im = Image.open(SRC).convert("RGBA")
alpha = im.getchannel("A")
w, h = im.size

# binarisasi
mask = alpha.point(lambda v: 255 if v > 110 else 0)
bbox = mask.getbbox()
print("bbox alpha>110:", bbox, "ukuran:", im.size)

# centroid
px = mask.load()
sx = sy = n = 0
for y in range(h):
    for x in range(w):
        if px[x, y]:
            sx += x; sy += y; n += 1
print("piksel opaque:", n, "centroid:", (round(sx / n, 1), round(sy / n, 1)))

# ASCII render
W = 72
Hh = int(W * h / w / 2.05)
step_x, step_y = w / W, h / Hh
print("+" + "-" * W + "+")
for j in range(Hh):
    row = ""
    for i in range(W):
        cnt = 0; tot = 0
        for yy in range(int(j * step_y), min(h, int((j + 1) * step_y))):
            for xx in range(int(i * step_x), min(w, int((i + 1) * step_x))):
                tot += 1
                if px[xx, yy]:
                    cnt += 1
        row += "#" if tot and cnt / tot > 0.45 else ("+" if tot and cnt / tot > 0.15 else " ")
    print("|" + row + "|")
print("+" + "-" * W + "+")
