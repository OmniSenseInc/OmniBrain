#!/usr/bin/env python3
"""buat_og.py — bikin kartu pratinjau tautan (og:image) OmniSense 1200x630.

Motif: busur konsentris monoline (bentuk logo) + titik sinyal teal di atas navy.
Huruf: DejaVu (font sistem) — ini kartu pratinjau, bukan tipografi utama situs.

Jalankan dari folder website/:
    python3 scripts/buat_og.py
Hasil: assets/og-omnisense.png
"""
import pathlib

from PIL import Image, ImageDraw, ImageFont

BASE = pathlib.Path(__file__).resolve().parent.parent
OUT = BASE / "assets" / "og-omnisense.png"

W, H = 1200, 630
NAVY = (8, 8, 8)      # obsidian logo OmniSense
NAVY_2 = (16, 16, 16)  # panel
TEAL = (20, 184, 164)  # teal logo persis
WHITE = (250, 250, 250)
SLATE = (161, 161, 170)

F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def busur(d, cx, cy, r, sudut_awal, sudut_akhir, warna, lebar):
    """Busur dengan celah (meniru motif logo)."""
    d.arc([cx - r, cy - r, cx + r, cy + r], sudut_awal, sudut_akhir, fill=warna, width=lebar)


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img, "RGBA")

    # bidang miring halus supaya tidak rata
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)], fill=(
            int(NAVY[0] + (NAVY_2[0] - NAVY[0]) * t),
            int(NAVY[1] + (NAVY_2[1] - NAVY[1]) * t),
            int(NAVY[2] + (NAVY_2[2] - NAVY[2]) * t),
        ))

    # busur konsentris (motif logo) di kanan, dengan celah
    cx, cy = 1000, 315
    for r, lebar, alpha in ((250, 2, 46), (190, 2, 60), (130, 2, 76), (70, 2, 96)):
        busur(d, cx, cy, r, -118, 118, TEAL + (alpha,), lebar)
    # titik sinyal
    d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=TEAL + (255,))
    d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], outline=TEAL + (70,), width=2)

    # garis teal vertikal di tepi kiri
    d.rectangle([0, 0, 5, H], fill=TEAL + (255,))

    x = 86
    # brand
    f_brand = font(F_REG, 30)
    d.text((x, 84), "omnisense", font=f_brand, fill=SLATE)

    # judul
    f_h1 = font(F_BOLD, 70)
    d.text((x, 152), "Seberapa siap", font=f_h1, fill=WHITE)
    d.text((x, 236), "bisnis Anda", font=f_h1, fill=WHITE)
    d.text((x, 320), "memakai AI?", font=f_h1, fill=WHITE)

    # garis pemisah
    d.rectangle([x, 428, x + 72, 431], fill=TEAL + (255,))

    # subjudul
    f_sub = font(F_REG, 30)
    d.text((x, 458), "Penilaian kesiapan 8 dimensi berbobot — gratis.", font=f_sub, fill=SLATE)
    d.text((x, 500), "Skor, kategori, dan dua celah utama langsung di situs.", font=f_sub, fill=SLATE)

    # kaki
    f_kaki = font(F_REG, 24)
    d.text((x, 566), "omnisense.id", font=f_kaki, fill=TEAL)

    img.save(OUT, "PNG", optimize=True)
    print("ditulis:", OUT, img.size, OUT.stat().st_size, "bytes")


if __name__ == "__main__":
    main()
