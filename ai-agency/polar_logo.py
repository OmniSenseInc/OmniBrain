#!/usr/bin/env python3
"""Analisis polar mark OmniSense (origin = centroid): jumlah lilitan, celah, tebal stroke."""
import math
from PIL import Image

SRC = "/home/ubuntu/ai-agency/logo_omnisense_white.png"
im = Image.open(SRC).convert("RGBA")
alpha = im.getchannel("A")
mask = alpha.point(lambda v: 255 if v > 110 else 0)
w, h = im.size
px = mask.load()

# centroid
sx = sy = n = 0
for y in range(h):
    for x in range(w):
        if px[x, y]:
            sx += x; sy += y; n += 1
cx, cy = sx / n, sy / n
print(f"centroid = ({cx:.1f}, {cy:.1f})  opaque = {n}px")

def runs_at(angle_deg, rmax=420):
    a = math.radians(angle_deg)
    out, inside, start = [], False, 0
    for r in range(0, rmax):
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        v = 0 <= x < w and 0 <= y < h and px[int(x), int(y)] > 0
        if v and not inside:
            inside, start = True, r
        elif not v and inside:
            inside = False; out.append((start, r - 1))
    if inside:
        out.append((start, rmax))
    return out

print("\n-- run sepanjang radius (derajat 0 = kanan/timur, 90 = bawah) --")
for ang in (0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330):
    rr = runs_at(ang)
    desc = ", ".join(f"{a}-{b}({b-a+1})" for a, b in rr)
    print(f"  {ang:3d}deg: {len(rr)} run -> {desc}")

# celah angular per radius
print("\n-- celah angular (derajat) pada beberapa radius --")
outer = max(b for ang in range(0, 360, 3) for a, b in runs_at(ang)[-1:]) if True else 0
print("radius luar ~", outer)
for frac in (0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.95):
    R = outer * frac
    vals = []
    for d in range(360):
        a = math.radians(d)
        x, y = cx + R * math.cos(a), cy + R * math.sin(a)
        vals.append(0 <= x < w and 0 <= y < h and px[int(x), int(y)] > 0)
    gaps, inside, start = [], False, 0
    for i, v in enumerate(vals + [True]):
        if not v and not inside:
            inside, start = True, i
        elif v and inside:
            inside = False
            if i - start >= 3:
                gaps.append((start, i - 1, i - start))
    print(f"  r={frac:.2f} ({R:.0f}px): {gaps}")
