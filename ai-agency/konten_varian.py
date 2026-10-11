#!/usr/bin/env python3
"""
konten_varian.py — Template visual BARU OmniSense (alternatif gaya lama).

Latar belakang: user bilang template lama "bosen gitu-gitu doang" dan minta gaya
yang lebih menarik (contoh referensi: akun IG crypto/fintech — bold, angka besar,
aksen warna, komposisi dinamis).

Script ini TIDAK mengubah konten_harian.py (template lama tetap utuh). Ini
generator terpisah dengan 3 varian:

  A "stat-hero"  : angka/stat BESAR jadi bintang, aksen teal, glow radial.
  B "bold-block" : blok warna aksen penuh di atas, headline di dalamnya.
  C "glow-grid"  : latar grid + glow, headline tengah besar, poin jadi chip.

Semua teks digambar program (bukan AI gambar) -> teks pasti akurat.

CARA PAKAI
  .venv/bin/python konten_varian.py --varian A --file konten_varian_data.json --png out.png --cek
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from konten_harian import font, bungkus, teks_tracking, lebar_tracking, tempel_logo, LOGO_DEFAULT

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
SAFE_ATAS, SAFE_BAWAH = 135, 1215
MX0, MX1 = 70, 1010

# palet dasar (gelap) + aksen
OBSIDIAN = (9, 9, 11)
PANEL = (16, 17, 20)
BORDER = (45, 46, 52)
WHITE = (255, 255, 255)
MUTED = (148, 163, 184)
MUTED_DIM = (100, 116, 139)
TEAL = (20, 184, 166)        # #14B8A6 aksen brand
TEAL_SOFT = (45, 212, 191)
NAVY = (11, 31, 58)          # #0B1F3A


def hex_to_rgb(s: str, fallback=TEAL):
    try:
        s = s.lstrip("#")
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return fallback


def radial_glow(base: Image.Image, cx, cy, radius, color, alpha=90):
    """Glow radial lembut: makin dekat pusat makin terang."""
    lapis = Image.new("RGB", base.size, color)
    mask = Image.new("L", base.size, 0)
    d = ImageDraw.Draw(mask)
    langkah = max(1, radius // 40)
    for r in range(radius, 0, -langkah):
        a = int(alpha * (1 - r / radius) ** 1.6)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(radius * 0.08))
    return Image.composite(lapis, base, mask)


def grid_lines(img, warna, langkah=90, alfa=26):
    lapis = Image.new("RGB", img.size, warna)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    for x in range(0, W, langkah):
        d.line([(x, 0), (x, H)], fill=alfa, width=1)
    for y in range(0, H, langkah):
        d.line([(0, y), (W, y)], fill=alfa, width=1)
    return Image.composite(lapis, img, mask)


def header(img, d, tag, tanggal, word="omnisense"):
    f_tag = font(False, 15, None, weight="semibold")
    f_word = font(True, 23, None, weight="extrabold")
    f_tgl = font(False, 14, None, weight="regular")
    lebar = lebar_tracking(d, word, f_word, -0.4)
    x_word = MX1 - lebar
    if os.path.exists(LOGO_DEFAULT):
        tempel_logo(img, x_word - 12 - 28, 40, 28)
    teks_tracking(d, (x_word, 43), word, f_word, WHITE, -0.4)
    teks_tracking(d, (MX0, 40), tag, f_tag, MUTED, 1.6)
    d.text((MX0, 65), tanggal, font=f_tgl, fill=MUTED_DIM)
    d.line([(MX0, 100), (MX1, 100)], fill=BORDER, width=1)


def footer(d, kaki, y=1258):
    f = font(False, 13, None, weight="medium")
    d.text(((W - d.textlength(kaki, font=f)) / 2, y), kaki, font=f, fill=MUTED_DIM)


def cta_pill(d, teks, x, y, aksen, tinggi=52):
    f = font(True, 16, None, weight="semibold")
    tw = lebar_tracking(d, teks, f, 1.2)
    d.rounded_rectangle([x, y, x + tw + 64, y + tinggi], radius=tinggi / 2, fill=aksen)
    teks_tracking(d, (x + 32, y + (tinggi - 20) / 2), teks, f, (9, 9, 11), 1.2)
    return y + tinggi


def wrap_c(d, teks, f, lebar_maks):
    return bungkus(d, teks, f, lebar_maks)


def tengah_x(d, teks, f, tracking=0.0):
    return (W - lebar_tracking(d, teks, f, tracking)) / 2


# ---------------------------------------------------------------- varian A
def varian_stat_hero(data, out, cek=False):
    aksen = hex_to_rgb(data.get("aksen", "#14B8A6"))
    img = Image.new("RGB", (W, H), OBSIDIAN)
    img = radial_glow(img, W * 0.5, H * 0.40, int(W * 0.85), aksen, alpha=70)
    d = ImageDraw.Draw(img)
    lapor = []

    header(img, d, data.get("tag", "[ OMNISENSE ]"), data.get("tanggal", ""))
    d = ImageDraw.Draw(img)

    # kicker
    f_kick = font(True, 18, None, weight="bold")
    kick = data.get("kicker", "").upper()
    if kick:
        teks_tracking(d, (tengah_x(d, kick, f_kick, 3.0), 250), kick, f_kick, aksen, 3.0)

    # STAT besar
    stat = data.get("stat", "")
    f_stat = font(True, 230, None, weight="black")
    while stat and lebar_tracking(d, stat, f_stat, -6) > (MX1 - MX0) and f_stat.size > 90:
        f_stat = font(True, f_stat.size - 10, None, weight="black")
    ys = 300
    teks_tracking(d, (tengah_x(d, stat, f_stat, -6), ys), stat, f_stat, WHITE, -6)
    tinggi_stat = f_stat.size
    lapor.append(f"  stat '{stat}' @{f_stat.size}px")

    # label stat
    label = data.get("stat_label", "")
    f_lab = font(False, 22, None, weight="regular")
    y = ys + tinggi_stat + 14
    for bt in wrap_c(d, label, f_lab, MX1 - MX0 - 120):
        d.text((tengah_x(d, bt, f_lab), y), bt, font=f_lab, fill=MUTED)
        y += 30
    lapor.append(f"  label stat berakhir y={y}")

    # garis pemisah aksen
    y += 22
    d.rounded_rectangle([W / 2 - 40, y, W / 2 + 40, y + 5], radius=3, fill=aksen)

    # poin ringkas (maks 3) sebagai baris aksen
    y += 44
    f_j = font(True, 21, None, weight="bold")
    f_i = font(False, 17, None, weight="regular")
    for p in data.get("poin", [])[:3]:
        d.ellipse([MX0 + 4, y + 7, MX0 + 16, y + 19], fill=aksen)
        d.text((MX0 + 34, y), p.get("judul", ""), font=f_j, fill=WHITE)
        y += 30
        for bt in wrap_c(d, p.get("isi", ""), f_i, MX1 - MX0 - 34):
            d.text((MX0 + 34, y), bt, font=f_i, fill=MUTED)
            y += 25
        y += 18
    lapor.append(f"  poin berakhir y={y}")

    # CTA
    cta = data.get("cta", "")
    if cta:
        f_c = font(True, 16, None, weight="semibold")
        tw = lebar_tracking(d, cta, f_c, 1.2)
        x = (W - (tw + 64)) / 2
        y = min(y + 10, 1150)
        cta_pill(d, cta, x, y, aksen)
        lapor.append(f"  CTA y={y}")

    footer(d, data.get("kaki", "@omnisense_id • omnisense.my.id"))
    img.save(out)
    if cek:
        print(f"[A stat-hero] {W}x{H}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out}")
    return out


# ---------------------------------------------------------------- varian B
def varian_bold_block(data, out, cek=False):
    aksen = hex_to_rgb(data.get("aksen", "#0B1F3A"))
    img = Image.new("RGB", (W, H), OBSIDIAN)
    d = ImageDraw.Draw(img)
    lapor = []

    # blok aksen atas
    blok_bawah = 620
    d.rectangle([0, 0, W, blok_bawah], fill=aksen)
    # garis halus
    lapis = Image.new("RGB", (W, blok_bawah), (255, 255, 255))
    mask = Image.new("L", (W, blok_bawah), 0)
    md = ImageDraw.Draw(mask)
    for x in range(0, W, 60):
        md.line([(x, 0), (x, blok_bawah)], fill=16, width=1)
    img.paste(Image.composite(lapis, img.crop((0, 0, W, blok_bawah)), mask), (0, 0))
    d = ImageDraw.Draw(img)

    # header di atas blok (putih)
    f_tag = font(False, 15, None, weight="semibold")
    f_word = font(True, 23, None, weight="extrabold")
    f_tgl = font(False, 14, None, weight="regular")
    lebar = lebar_tracking(d, "omnisense", f_word, -0.4)
    x_word = MX1 - lebar
    if os.path.exists(LOGO_DEFAULT):
        tempel_logo(img, x_word - 12 - 28, 40, 28)
    teks_tracking(d, (x_word, 43), "omnisense", f_word, WHITE, -0.4)
    teks_tracking(d, (MX0, 40), data.get("tag", "[ OMNISENSE ]"), f_tag, (255, 255, 255), 1.6)
    d.text((MX0, 65), data.get("tanggal", ""), font=f_tgl, fill=(220, 235, 245))

    # headline besar di dalam blok
    f_h = font(True, 92, None, weight="black")
    baris = data.get("headline", [])
    while baris and max(lebar_tracking(d, b, f_h, -2) for b in baris) > (MX1 - MX0) and f_h.size > 40:
        f_h = font(True, f_h.size - 4, None, weight="black")
    y = 200
    for b in baris:
        teks_tracking(d, (MX0, y), b, f_h, WHITE, -2)
        y += int(f_h.size * 1.10)
    lapor.append(f"  headline @{f_h.size}px berakhir y={y}")

    # subjudul di dalam blok
    sub = data.get("subjudul", "")
    f_s = font(False, 22, None, weight="regular")
    y += 14
    for bt in wrap_c(d, sub, f_s, MX1 - MX0):
        d.text((MX0, y), bt, font=f_s, fill=(226, 240, 246))
        y += 31
    lapor.append(f"  subjudul berakhir y={y}")

    # area bawah gelap: poin
    y = blok_bawah + 60
    f_j = font(True, 23, None, weight="bold")
    f_i = font(False, 17, None, weight="regular")
    f_n = font(True, 24, None, weight="bold")
    for i, p in enumerate(data.get("poin", [])[:3], 1):
        d.text((MX0, y), f"{i:02d}", font=f_n, fill=aksen)
        d.text((MX0 + 50, y + 2), p.get("judul", ""), font=f_j, fill=WHITE)
        y += 32
        for bt in wrap_c(d, p.get("isi", ""), f_i, MX1 - MX0 - 50):
            d.text((MX0 + 50, y), bt, font=f_i, fill=MUTED)
            y += 25
        y += 20
    lapor.append(f"  poin berakhir y={y}")

    cta = data.get("cta", "")
    if cta:
        f_c = font(True, 16, None, weight="semibold")
        tw = lebar_tracking(d, cta, f_c, 1.2)
        cta_pill(d, cta, (W - (tw + 64)) / 2, min(y + 6, 1150), aksen)

    footer(d, data.get("kaki", "@omnisense_id • omnisense.my.id"))
    img.save(out)
    if cek:
        print(f"[B bold-block] {W}x{H}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out}")
    return out


# ---------------------------------------------------------------- varian C
def varian_glow_grid(data, out, cek=False):
    aksen = hex_to_rgb(data.get("aksen", "#14B8A6"))
    img = Image.new("RGB", (W, H), OBSIDIAN)
    img = grid_lines(img, aksen, langkah=90, alfa=22)
    img = radial_glow(img, W * 0.5, H * 0.52, int(W * 0.9), aksen, alpha=60)
    d = ImageDraw.Draw(img)
    lapor = []

    header(img, d, data.get("tag", "[ OMNISENSE ]"), data.get("tanggal", ""))
    d = ImageDraw.Draw(img)

    # headline tengah besar
    baris = data.get("headline", [])
    f_h = font(True, 96, None, weight="black")
    while baris and max(lebar_tracking(d, b, f_h, -2) for b in baris) > (MX1 - MX0) and f_h.size > 44:
        f_h = font(True, f_h.size - 4, None, weight="black")
    tinggi = len(baris) * int(f_h.size * 1.10)
    y = 300
    for b in baris:
        teks_tracking(d, (tengah_x(d, b, f_h, -2), y), b, f_h, WHITE, -2)
        y += int(f_h.size * 1.10)
    lapor.append(f"  headline @{f_h.size}px berakhir y={y}")

    sub = data.get("subjudul", "")
    f_s = font(False, 21, None, weight="regular")
    y += 16
    for bt in wrap_c(d, sub, f_s, MX1 - MX0 - 80):
        d.text((tengah_x(d, bt, f_s), y), bt, font=f_s, fill=MUTED)
        y += 30
    lapor.append(f"  subjudul berakhir y={y}")

    # chip poin
    y += 30
    f_j = font(True, 19, None, weight="bold")
    for p in data.get("poin", [])[:3]:
        teks = f"{p.get('judul','')} — {p.get('isi','')}"
        f_isi = font(False, 16, None, weight="regular")
        baris_c = wrap_c(d, teks, f_isi, MX1 - MX0 - 70)
        tinggi_c = 24 + len(baris_c) * 24
        d.rounded_rectangle([MX0, y, MX1, y + tinggi_c], radius=14,
                            fill=(20, 21, 25), outline=(*aksen, ), width=1)
        yy = y + 14
        for bt in baris_c:
            d.text((MX0 + 26, yy), bt, font=f_isi, fill=(226, 232, 240))
            yy += 24
        y += tinggi_c + 14
    lapor.append(f"  chip berakhir y={y}")

    cta = data.get("cta", "")
    if cta:
        f_c = font(True, 16, None, weight="semibold")
        tw = lebar_tracking(d, cta, f_c, 1.2)
        cta_pill(d, cta, (W - (tw + 64)) / 2, min(y + 6, 1150), aksen)

    footer(d, data.get("kaki", "@omnisense_id • omnisense.my.id"))
    img.save(out)
    if cek:
        print(f"[C glow-grid] {W}x{H}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out}")
    return out


VARIAN = {"A": varian_stat_hero, "B": varian_bold_block, "C": varian_glow_grid}


def main():
    ap = argparse.ArgumentParser(description="Template visual baru OmniSense (varian A/B/C).")
    ap.add_argument("--varian", default="A", choices=list(VARIAN))
    ap.add_argument("--file", default=os.path.join(BASE, "konten_varian_data.json"))
    ap.add_argument("--png", default=None)
    ap.add_argument("--cek", action="store_true")
    a = ap.parse_args()
    data = json.load(open(a.file))
    out = a.png or os.path.join(BASE, f"konten_varian_{a.varian}.png")
    VARIAN[a.varian](data, out, cek=a.cek)


if __name__ == "__main__":
    main()
