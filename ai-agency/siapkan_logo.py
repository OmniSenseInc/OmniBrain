#!/usr/bin/env python3
"""Siapkan aset logo OmniSense dari file yang dikirim user (putih di atas hitam).

Masukan : JPG/PNG logo apa pun (mark putih, latar gelap)
Keluaran: PNG RGBA dengan mark PUTIH #FFFFFF dan latar TRANSPARAN (alpha = luminance),
          plus versi trim (dipotong rapat ke batas mark) supaya penempatan di poster presisi.

Pakai: .venv/bin/python siapkan_logo.py <sumber.jpg> <keluaran.png>
"""
import sys

from PIL import Image

AMBANG = 24  # di bawah ini dianggap latar hitam


def main():
    src, dst = sys.argv[1], sys.argv[2]
    im = Image.open(src).convert("RGB")
    # alpha dari luminance: hitam -> transparan, putih -> pekat
    lum = im.convert("L")
    alpha = lum.point(lambda v: 0 if v < AMBANG else min(255, int((v - AMBANG) * 255 / (255 - AMBANG))))
    putih = Image.new("RGBA", im.size, (255, 255, 255, 0))
    putih.putalpha(alpha)
    bbox = alpha.getbbox()
    if bbox:
        putih = putih.crop(bbox)
    putih.save(dst)
    print(f"OK {dst} {putih.size} (dari {im.size}, bbox={bbox})")


if __name__ == "__main__":
    main()
