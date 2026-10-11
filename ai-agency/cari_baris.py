#!/usr/bin/env python3
"""Cari baris-baris teks (band horizontal berisi piksel terang) di sebuah gambar,
lalu simpan crop baris tertentu dalam versi diperbesar untuk inspeksi tipografi.

Pakai: .venv/bin/python cari_baris.py <gambar> <y_awal> <y_akhir> [--simpan N --out file.png --zoom 3]
"""
import sys

from PIL import Image


def main():
    path = sys.argv[1]
    y0, y1 = int(sys.argv[2]), int(sys.argv[3])
    simpan = None
    out = "/tmp/baris.png"
    zoom = 3
    if "--simpan" in sys.argv:
        simpan = int(sys.argv[sys.argv.index("--simpan") + 1])
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    if "--zoom" in sys.argv:
        zoom = int(sys.argv[sys.argv.index("--zoom") + 1])

    im = Image.open(path).convert("L")
    w, h = im.size
    px = im.load()
    baris, mulai = [], None
    for y in range(y0, min(y1, h)):
        ada = any(px[x, y] > 150 for x in range(0, w, 2))
        if ada and mulai is None:
            mulai = y
        elif not ada and mulai is not None:
            if y - mulai >= 3:
                baris.append((mulai, y))
            mulai = None
    if mulai is not None:
        baris.append((mulai, min(y1, h)))

    for i, (a, b) in enumerate(baris):
        print(f"baris {i}: y {a}-{b} (tinggi {b - a})")
    if simpan is not None and 0 <= simpan < len(baris):
        a, b = baris[simpan]
        crop = im.crop((0, max(0, a - 6), w, min(h, b + 6))).convert("RGB")
        crop = crop.resize((crop.width * zoom, crop.height * zoom), Image.LANCZOS)
        crop.save(out)
        print(f"tersimpan {out} {crop.size}")


if __name__ == "__main__":
    main()
