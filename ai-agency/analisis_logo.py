#!/usr/bin/env python3
"""Analisis geometri mark logo OmniSense dari PNG (putih, latar transparan).

Keluaran: jumlah lilitan (dari profil radial), posisi celah spiral (dari profil angular),
tebal stroke, radius dalam/luar, plus gambar komposit untuk dilihat mata.
"""
import math
from PIL import Image

SRC = "/home/ubuntu/ai-agency/logo_omnisense_white.png"
OUT = "/tmp/logo_analisis.png"

im = Image.open(SRC).convert("RGBA")
w, h = im.size
alpha = im.getchannel("A")
bbox = alpha.getbbox()
print("size", im.size, "bbox", bbox)

# komposit di atas obsidian untuk dilihat
bg = Image.new("RGBA", im.size, (9, 9, 11, 255))
bg.alpha_composite(im)
bg.convert("RGB").resize((560, 560)).save(OUT)
print("composite ->", OUT)

cx, cy = w / 2, h / 2
print("center", cx, cy)

def opaque(px, py):
    if 0 <= px < w and 0 <= py < h:
        return alpha.getpixel((int(px), int(py))) > 128
    return False

# --- profil radial: hitung run opaque dari pusat ke tepi (beberapa sudut) ---
def radial_runs(angle_deg):
    a = math.radians(angle_deg)
    runs, inside, start = [], False, 0
    rmax = max(w, h)
    for r in range(0, int(rmax)):
        px, py = cx + r * math.cos(a), cy + r * math.sin(a)
        v = opaque(px, py)
        if v and not inside:
            inside, start = True, r
        elif not v and inside:
            inside = False
            runs.append((start, r - 1))
    if inside:
        runs.append((start, int(rmax)))
    return runs

for ang in (0, 45, 90, 135, 180, 225, 270, 315):
    rr = radial_runs(ang)
    widths = [b - a + 1 for a, b in rr]
    print(f"  sudut {ang:3d}: {len(rr)} run, lebar={widths}")

# --- radius dalam & luar dari semua arah ---
inner, outer = [], []
for ang in range(0, 360, 5):
    rr = radial_runs(ang)
    if rr:
        inner.append(rr[0][0]); outer.append(rr[-1][1])
print("radius dalam min/median", min(inner), sorted(inner)[len(inner)//2])
print("radius luar  max/median", max(outer), sorted(outer)[len(outer)//2])

# --- profil angular: cari celah (arah jam) pada radius tertentu ---
def angular_gaps(radius_frac):
    R = max(outer) * radius_frac
    vals = []
    for d in range(0, 360):
        a = math.radians(d)
        vals.append(opaque(cx + R * math.cos(a), cy + R * math.sin(a)))
    gaps, inside = [], False
    start = 0
    for i, v in enumerate(vals + [True]):
        if not v and not inside:
            inside, start = True, i
        elif v and inside:
            inside = False
            gaps.append((start, i - 1, i - start))
    return [(s, e, ln) for s, e, ln in gaps if ln >= 2]

for frac in (0.35, 0.5, 0.65, 0.8):
    g = angular_gaps(frac)
    print(f"celah pada radius {frac:.0%}: {g}")

# stroke width: tebal run rata-rata pada radius 60% (arah tanpa celah)
rr = radial_runs(0)
if rr:
    print("lebar stroke kandidat (sudut 0):", [b - a + 1 for a, b in rr])
