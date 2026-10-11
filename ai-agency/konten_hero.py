#!/usr/bin/env python3
"""
konten_hero.py — Template "hero news" OmniSense (gaya cryptowave, palet BROWN kita).

Gaya yang ditiru (dari referensi @cryptowaveid): elemen hero besar di bagian ATAS,
latar sirkuit bercahaya, lalu HEADLINE besar multi-baris di BAWAH — putih, dengan
baris penekanan berwarna AKSEN. Plus badge akun di kanan bawah.

BEDA dari referensi: warnanya BUKAN hijau, tapi palet brand OmniSense = brown agak
gelap (hangat), senada website omnisense.my.id (#101010 / #F3EFE6 / #B9B2A6).

Tidak menyentuh konten_harian.py. Teks digambar program (akurat, bukan AI gambar).

CARA PAKAI
  .venv/bin/python konten_hero.py --file konten_hero_data.json --png out.png --cek
"""
from __future__ import annotations

import argparse
import json
import math
import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from konten_harian import font, bungkus, teks_tracking, lebar_tracking, tempel_logo, LOGO_DEFAULT

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
MX0, MX1 = 64, 1016

# ---- palet BROWN OmniSense (hangat, senada website) ----
BG = (16, 16, 16)            # #101010 warm black
BG2 = (24, 22, 20)           # #181614 sedikit hangat
BONE = (243, 239, 230)       # #F3EFE6 bone white (dari website)
MUTED = (185, 178, 166)      # #B9B2A6
MUTED_DIM = (138, 130, 118)
LINE = (73, 70, 63)          # #49463F
BROWN = (168, 116, 76)       # #A8744C  aksen brown agak gelap (brand)
BROWN_LT = (212, 165, 116)   # #D4A574  brown lebih terang (biar teks aksen tetap terbaca)
BROWN_DK = (110, 72, 46)     # #6E482E  brown gelap (blok)


def hex_rgb(s, fb=BROWN):
    try:
        s = s.lstrip("#")
        return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))
    except Exception:
        return fb


def glow(img, cx, cy, radius, color, alpha=95, power=1.6):
    lapis = Image.new("RGB", img.size, color)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    langkah = max(1, radius // 48)
    for r in range(radius, 0, -langkah):
        a = int(alpha * (1 - r / radius) ** power)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=a)
    mask = mask.filter(ImageFilter.GaussianBlur(radius * 0.10))
    return Image.composite(lapis, img, mask)


def sirkuit(img, warna, alfa=70):
    """Garis sirkuit bergaya PCB + node, warna aksen (glow tipis)."""
    lapis = Image.new("RGB", img.size, warna)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    rnd = 20261006
    def r():
        nonlocal rnd
        rnd = (1103515245 * rnd + 12345) & 0x7FFFFFFF
        return rnd / 0x7FFFFFFF
    for _ in range(26):
        x = int(r() * W); y = int(r() * H)
        panjang = int(120 + r() * 360)
        arah = r()
        if arah < 0.5:
            d.line([(x, y), (x + panjang, y)], fill=alfa, width=2)
            d.ellipse([x + panjang - 5, y - 5, x + panjang + 5, y + 5], fill=alfa)
        else:
            d.line([(x, y), (x, y + panjang)], fill=alfa, width=2)
            d.ellipse([x - 5, y + panjang - 5, x + 5, y + panjang + 5], fill=alfa)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    return Image.composite(lapis, img, mask)


def header(img, d, tag, tanggal, aksen):
    f_tag = font(False, 15, None, weight="semibold")
    f_word = font(True, 23, None, weight="extrabold")
    f_tgl = font(False, 14, None, weight="regular")
    lebar = lebar_tracking(d, "omnisense", f_word, -0.4)
    x_word = MX1 - lebar
    if os.path.exists(LOGO_DEFAULT):
        tempel_logo(img, x_word - 12 - 28, 40, 28)
    teks_tracking(d, (x_word, 43), "omnisense", f_word, BONE, -0.4)
    teks_tracking(d, (MX0, 40), tag, f_tag, MUTED, 1.6)
    d.text((MX0, 65), tanggal, font=f_tgl, fill=MUTED_DIM)
    d.line([(MX0, 100), (MX1, 100)], fill=LINE, width=1)


def footer(d, kaki, aksen):
    f = font(False, 13, None, weight="medium")
    d.text(((W - d.textlength(kaki, font=f)) / 2, 1262), kaki, font=f, fill=MUTED_DIM)


def badge(d, teks, aksen):
    """Badge akun kanan-bawah (gaya 'TikTok & IG | @akun')."""
    f = font(True, 13, None, weight="semibold")
    tw = lebar_tracking(d, teks, f, 0.8)
    x1, y1 = W - 64, 1180
    d.rounded_rectangle([x1 - tw - 40, y1, x1, y1 + 34], radius=17,
                        fill=(30, 27, 24), outline=aksen, width=1)
    teks_tracking(d, (x1 - tw - 20, y1 + 9), teks, f, BONE, 0.8)


def render(data, out, cek=False):
    aksen = hex_rgb(data.get("aksen", "#A8744C"))
    aksen_lt = hex_rgb(data.get("aksen_terang", "#D4A574"))
    img = Image.new("RGB", (W, H), BG)
    # gradasi hangat halus dari atas
    grad = Image.new("RGB", (W, H), BG)
    gd = ImageDraw.Draw(grad)
    for y in range(H):
        t = y / H
        gd.line([(0, y), (W, y)], fill=(
            int(BG[0] + (BG2[0] - BG[0]) * t),
            int(BG[1] + (BG2[1] - BG[1]) * t),
            int(BG[2] + (BG2[2] - BG[2]) * t)))
    img = grad
    # glow aksen besar di area hero (atas)
    img = glow(img, W * 0.50, H * 0.30, int(W * 0.80), aksen, alpha=80, power=1.7)
    img = sirkuit(img, aksen_lt, alfa=64)
    d = ImageDraw.Draw(img)
    lapor = []

    header(img, d, data.get("tag", "[ OMNISENSE ]"), data.get("tanggal", ""), aksen)
    d = ImageDraw.Draw(img)

    # ---------- ZONA HERO (atas): kicker + stat besar ----------
    kick = data.get("kicker", "").upper()
    f_kick = font(True, 20, None, weight="bold")
    if kick:
        kw = lebar_tracking(d, kick, f_kick, 4.0)
        xk = (W - kw) / 2
        d.rounded_rectangle([xk - 22, 178, xk + kw + 22, 178 + 44], radius=22,
                            fill=(38, 30, 24), outline=aksen, width=1)
        teks_tracking(d, (xk, 189), kick, f_kick, aksen_lt, 4.0)
        lapor.append(f"  kicker '{kick}' y=178")

    stat = data.get("stat", "")
    if stat:
        f_stat = font(True, 300, None, weight="black")
        while lebar_tracking(d, stat, f_stat, -8) > (MX1 - MX0) and f_stat.size > 100:
            f_stat = font(True, f_stat.size - 12, None, weight="black")
        sw = lebar_tracking(d, stat, f_stat, -8)
        sy = 300
        # glow kedua di belakang stat
        img = glow(img, W / 2, sy + f_stat.size * 0.5, int(W * 0.5), aksen_lt, alpha=70, power=1.5)
        d = ImageDraw.Draw(img)
        teks_tracking(d, ((W - sw) / 2, sy), stat, f_stat, BONE, -8)
        lapor.append(f"  stat '{stat}' @{f_stat.size}px y={sy}")
        y_hero = sy + f_stat.size
    else:
        y_hero = 300

    stat_label = data.get("stat_label", "")
    f_sl = font(False, 24, None, weight="regular")
    y = y_hero + 18
    for bt in bungkus(d, stat_label, f_sl, MX1 - MX0 - 160):
        d.text(((W - d.textlength(bt, font=f_sl)) / 2, y), bt, font=f_sl, fill=MUTED)
        y += 32
    lapor.append(f"  label hero berakhir y={y}")

    # garis pemisah aksen
    y += 22
    d.rounded_rectangle([W / 2 - 46, y, W / 2 + 46, y + 5], radius=3, fill=aksen)
    y += 6

    # ---------- ZONA HEADLINE (bawah): headline besar + aksen di baris terakhir ----------
    baris = data.get("headline", [])
    hl_akhir = data.get("highlight_baris_terakhir", True)
    hl_semua = data.get("highlight_semua", False)
    f_h = font(True, 92, None, weight="black")
    while baris and max(lebar_tracking(d, b, f_h, -2) for b in baris) > (MX1 - MX0) and f_h.size > 42:
        f_h = font(True, f_h.size - 4, None, weight="black")
    jarak_h = int(f_h.size * 1.06)
    tinggi_h = len(baris) * jarak_h
    yh = y + 26
    for i, b in enumerate(baris):
        warna = BONE
        if hl_semua or (hl_akhir and i == len(baris) - 1):
            warna = aksen_lt
        bw = lebar_tracking(d, b, f_h, -2)
        teks_tracking(d, ((W - bw) / 2, yh), b, f_h, warna, -2)
        yh += jarak_h
    lapor.append(f"  headline {len(baris)} baris @{f_h.size}px berakhir y={yh}")

    # subjudul
    sub = data.get("subjudul", "")
    f_s = font(False, 20, None, weight="regular")
    yh += 12
    for bt in bungkus(d, sub, f_s, MX1 - MX0 - 120):
        d.text(((W - d.textlength(bt, font=f_s)) / 2, yh), bt, font=f_s, fill=MUTED)
        yh += 29
    lapor.append(f"  subjudul berakhir y={yh}")

    # CTA pill
    cta = data.get("cta", "")
    if cta:
        f_c = font(True, 16, None, weight="semibold")
        tw = lebar_tracking(d, cta, f_c, 1.2)
        cy = min(yh + 18, 1120)
        x = (W - (tw + 64)) / 2
        d.rounded_rectangle([x, cy, x + tw + 64, cy + 52], radius=26, fill=aksen)
        teks_tracking(d, (x + 32, cy + 16), cta, f_c, (16, 12, 8), 1.2)
        lapor.append(f"  CTA y={cy}")

    badge(d, data.get("badge", "IG & TikTok | @omnisense_id"), aksen)
    footer(d, data.get("kaki", "@omnisense_id • omnisense.my.id"), aksen)

    img.save(out)
    if cek:
        print(f"[hero brown] {W}x{H}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Template hero news OmniSense (palet brown).")
    ap.add_argument("--file", default=os.path.join(BASE, "konten_hero_data.json"))
    ap.add_argument("--png", default=os.path.join(BASE, "konten_hero.png"))
    ap.add_argument("--cek", action="store_true")
    a = ap.parse_args()
    render(json.load(open(a.file)), a.png, cek=a.cek)


if __name__ == "__main__":
    main()
