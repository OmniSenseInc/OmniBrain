#!/usr/bin/env python3
"""Gabungkan tangkapan 'sebelum' dan 'sesudah' satu bagian situs jadi satu PNG berlabel.

Pakai:
  python3 gabung_sebelum_sesudah.py --judul "Peta bagian (rail)" \
      --sebelum /tmp/banding-sebelum-rail.png \
      --sesudah /tmp/banding-sesudah-rail.png \
      --keluar pratinjau/rapikan-angka-rail.png
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont


LABEL_TINGGI = 46
WARNA_LATAR = (8, 23, 38)
WARNA_SEBELUM = (120, 40, 40)
WARNA_SESUDAH = (16, 100, 90)


def font(ukuran):
    for jalur in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if os.path.exists(jalur):
            try:
                return ImageFont.truetype(jalur, ukuran)
            except OSError:
                pass
    return ImageFont.load_default()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--sebelum", required=True)
    p.add_argument("--sesudah", required=True)
    p.add_argument("--keluar", required=True)
    p.add_argument("--judul", default="")
    p.add_argument("--label-atas", default="SEBELUM")
    p.add_argument("--label-bawah", default="SESUDAH")
    a = p.parse_args()

    atas = Image.open(a.sebelum).convert("RGB")
    bawah = Image.open(a.sesudah).convert("RGB")
    lebar = max(atas.width, bawah.width)

    def samakan(im):
        if im.width != lebar:
            r = lebar / im.width
            im = im.resize((lebar, int(im.height * r)), Image.LANCZOS)
        return im

    atas, bawah = samakan(atas), samakan(bawah)
    tinggi = LABEL_TINGGI + atas.height + LABEL_TINGGI + bawah.height + 8
    kanvas = Image.new("RGB", (lebar, tinggi), WARNA_LATAR)
    d = ImageDraw.Draw(kanvas)
    f = font(26)
    judul = f" \u2014 {a.judul}" if a.judul else ""

    y = 0
    d.rectangle([0, y, lebar, y + LABEL_TINGGI], fill=WARNA_SEBELUM)
    d.text((18, y + 10), a.label_atas + judul, font=f, fill=(255, 255, 255))
    y += LABEL_TINGGI
    kanvas.paste(atas, (0, y))
    y += atas.height

    d.rectangle([0, y, lebar, y + LABEL_TINGGI], fill=WARNA_SESUDAH)
    d.text((18, y + 10), a.label_bawah + judul, font=f, fill=(255, 255, 255))
    y += LABEL_TINGGI
    kanvas.paste(bawah, (0, y))

    induk = os.path.dirname(os.path.abspath(a.keluar))
    os.makedirs(induk, exist_ok=True)
    kanvas.save(a.keluar, optimize=True)
    print(a.keluar, kanvas.size, f"{os.path.getsize(a.keluar) / 1024:.0f} KB")


if __name__ == "__main__":
    main()
