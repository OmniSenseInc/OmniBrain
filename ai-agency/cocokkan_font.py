#!/usr/bin/env python3
"""Identifikasi font referensi secara OBJEKTIF: cocokkan glif di gambar referensi
dengan render kandidat font (IoU setelah dinormalkan tinggi).

Cara kerja:
  1. Ambil pita teks dari gambar referensi, binarisasi (teks = piksel terang).
  2. Cari connected component (huruf) -> bbox masing-masing.
  3. Untuk tiap glif referensi: render semua huruf a-z A-Z 0-9 dari tiap kandidat font,
     normalkan tinggi bbox ke 64 px, hitung IoU di kanvas 96x96 setelah dipusatkan.
  4. Skor font = rata-rata IoU terbaik tiap glif (tidak perlu tahu teksnya).

Pakai: .venv/bin/python cocokkan_font.py <gambar> <y0> <y1> <x0> <x1>
"""
import os
import sys
from collections import deque

from PIL import Image, ImageDraw, ImageFont

KANDIDAT = {
    "Inter": "/home/ubuntu/.local/share/fonts/inter/Inter-Regular.ttf",
    "Inter-Medium": "/home/ubuntu/.local/share/fonts/inter/Inter-Medium.ttf",
    "Poppins-400": "/tmp/fontuji/poppins-400.ttf",
    "Poppins-500": "/tmp/fontuji/poppins-500.ttf",
    "PlusJakartaSans-var": "/tmp/fontuji/jakarta-var.ttf",
    "Manrope-var": "/tmp/fontuji/manrope-var.ttf",
    "Montserrat-var": "/tmp/fontuji/montserrat-var.ttf",
    "DMSans-var": "/tmp/fontuji/dmsans-var.ttf",
    "DejaVuSans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
}
HURUF = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
BERAT = {
    "PlusJakartaSans-var": 400,
    "Manrope-var": 400,
    "Montserrat-var": 400,
    "DMSans-var": 400,
}
TINGGI = 64
KANVAS = 96


def komponen(mask, w, h):
    """Cari connected component (8-konektivitas) -> daftar bbox."""
    lihat = [[False] * w for _ in range(h)]
    hasil = []
    for y0 in range(h):
        for x0 in range(w):
            if mask[y0][x0] and not lihat[y0][x0]:
                q = deque([(x0, y0)])
                lihat[y0][x0] = True
                xa = xb = x0
                ya = yb = y0
                n = 0
                while q:
                    x, y = q.popleft()
                    n += 1
                    xa, xb = min(xa, x), max(xb, x)
                    ya, yb = min(ya, y), max(yb, y)
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h and mask[ny][nx] and not lihat[ny][nx]:
                                lihat[ny][nx] = True
                                q.append((nx, ny))
                hasil.append((xa, ya, xb + 1, yb + 1, n))
    return hasil


def normalkan(mask_crop):
    """Crop mask -> citra biner di kanvas KANVAS x KANVAS dengan tinggi TINGGI, dipusatkan."""
    w = len(mask_crop[0])
    h = len(mask_crop)
    if w < 2 or h < 4:
        return None
    skala = TINGGI / h
    nw, nh = max(1, round(w * skala)), TINGGI
    im = Image.new("L", (w, h))
    im.putdata([255 if v else 0 for baris in mask_crop for v in baris])
    im = im.resize((nw, nh), Image.LANCZOS).point(lambda v: 255 if v > 127 else 0)
    kanvas = Image.new("L", (KANVAS, KANVAS), 0)
    kanvas.paste(im, ((KANVAS - nw) // 2, (KANVAS - nh) // 2))
    return [1 if v else 0 for v in kanvas.getdata()]


def iou(a, b):
    inter = sum(1 for i in range(len(a)) if a[i] and b[i])
    union = sum(1 for i in range(len(a)) if a[i] or b[i])
    return inter / union if union else 0.0


def render_huruf(font_path, huruf, berat=400):
    f = ImageFont.truetype(font_path, 80)
    if berat and hasattr(f, "set_variation_by_axes"):
        try:
            f.set_variation_by_axes([berat])
        except Exception:  # noqa: BLE001
            try:
                f.set_variation_by_name(str(berat))
            except Exception:  # noqa: BLE001
                pass
    im = Image.new("L", (200, 200), 0)
    ImageDraw.Draw(im).text((40, 40), huruf, font=f, fill=255)
    px = im.load()
    xs = [x for x in range(200) for y in range(200) if px[x, y] > 127]
    ys = [y for x in range(200) for y in range(200) if px[x, y] > 127]
    if not xs:
        return None
    x0, x1, y0, y1 = min(xs), max(xs) + 1, min(ys), max(ys) + 1
    mask = [[px[x, y] > 127 for x in range(x0, x1)] for y in range(y0, y1)]
    return normalkan(mask)


def main():
    path, y0, y1, x0, x1 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    im = Image.open(path).convert("L").crop((x0, y0, x1, y1))
    w, h = im.size
    px = im.load()
    mask = [[px[x, y] > 150 for x in range(w)] for y in range(h)]

    komp = [k for k in komponen(mask, w, h) if k[4] >= 25 and (k[3] - k[1]) >= 8]
    komp.sort(key=lambda k: k[0])
    print(f"glif terdeteksi: {len(komp)}")

    # pra-render semua huruf kandidat
    pustaka = {}
    for nama, fp in KANDIDAT.items():
        if not os.path.exists(fp):
            print(f"  (lewat) {nama} tidak ada")
            continue
        pustaka[nama] = {hh: render_huruf(fp, hh, BERAT.get(nama, 400)) for hh in HURUF}

    skor = {nama: [] for nama in pustaka}
    for (xa, ya, xb, yb, n) in komp:
        sub = [[mask[y][x] for x in range(xa, xb)] for y in range(ya, yb)]
        ref = normalkan(sub)
        if ref is None:
            continue
        for nama, tab in pustaka.items():
            terbaik = 0.0
            for hh, cand in tab.items():
                if cand is None:
                    continue
                v = iou(ref, cand)
                if v > terbaik:
                    terbaik = v
            skor[nama].append(terbaik)

    print("\nPeringkat (rata-rata IoU terbaik per glif):")
    for nama, vals in sorted(skor.items(), key=lambda kv: -(sum(kv[1]) / max(1, len(kv[1])))):
        if not vals:
            continue
        print(f"  {nama:22s} {sum(vals) / len(vals):.3f}  (n={len(vals)})")


if __name__ == "__main__":
    main()
