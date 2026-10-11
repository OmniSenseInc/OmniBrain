#!/usr/bin/env python3
"""Ubah hasil gpt-image (1024x1536, rasio 2:3) -> 1080x1350 (4:5) sesuai locked visual system.

Cara: tambah margin kiri-kanan, lalu resize ke 1080x1350. Konten tidak terpotong.

Margin dibuat dari kolom tepi gambar yang direntangkan + di-blur, supaya gradasi vignette
dan tekstur foto ikut nyambung (kalau pakai warna flat, kadang muncul garis/seam tipis).
Ada opsi --flat untuk memakai warna sudut rata.

Pakai: python3 ke_45.py <in.png> <out.png> [--flat]
"""
import sys

from PIL import Image, ImageFilter

TARGET = (1080, 1350)
EDGE = 6  # lebar kolom tepi yang dipakai sebagai sumber gradasi


def margin_strip(im, side, width):
    """Ambil kolom tepi, rentangkan ke samping, blur halus."""
    w, h = im.size
    if side == "left":
        box = (0, 0, EDGE, h)
    else:
        box = (w - EDGE, 0, w, h)
    strip = im.crop(box).resize((width, h), Image.LANCZOS)
    return strip.filter(ImageFilter.GaussianBlur(radius=8))


def main():
    src, dst = sys.argv[1], sys.argv[2]
    flat = "--flat" in sys.argv
    im = Image.open(src).convert("RGB")
    w, h = im.size
    target_w = round(h * TARGET[0] / TARGET[1])  # lebar supaya rasio jadi 4:5

    if target_w > w:
        m = (target_w - w) // 2
        canvas = Image.new("RGB", (target_w, h))
        if flat:
            px = im.load()
            corners = [px[2, 2], px[w - 3, 2], px[2, h - 3], px[w - 3, h - 3]]
            canvas.paste(Image.new("RGB", (target_w, h), tuple(sum(c[i] for c in corners) // 4 for i in range(3))), (0, 0))
        else:
            canvas.paste(margin_strip(im, "left", m), (0, 0))
            canvas.paste(margin_strip(im, "right", target_w - w - m), (m + w, 0))
        canvas.paste(im, (m, 0))
        im = canvas
    elif target_w < w:
        left = (w - target_w) // 2
        im = im.crop((left, 0, left + target_w, h))

    im = im.resize(TARGET, Image.LANCZOS)
    im.save(dst, "PNG", optimize=True)
    print(f"OK {dst} {im.size} (dari {src} {w}x{h}, margin={max(target_w - w, 0)}px)")


if __name__ == "__main__":
    main()
