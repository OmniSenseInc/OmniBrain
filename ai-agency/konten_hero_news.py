#!/usr/bin/env python3
"""
konten_hero_news.py — Template "hero news" OmniSense, replika gaya @cryptowaveid
(tapi palet BROWN kita, bukan hijau).

Yang ditiru dari referensi:
  1. FOTO subjek berita di-cutout (latar dihapus), ditempel di zona tengah-atas.
  2. Logo/entitas berita di kanan atas area foto.
  3. Latar gelap + glow aksen melengkung + garis sirkuit + blok 3D.
  4. Badge brand kecil ("OS") tepat di atas headline.
  5. HEADLINE besar multi-baris rata-tengah di bawah; baris TERAKHIR warna aksen.
  6. Badge akun pill di kanan bawah.

Foto WAJIB selaras berita (mis. berita Anthropic -> foto Dario Amodei).
Cari foto lisensi aman: `python3 cari_bg.py "<nama tokoh/perusahaan>" --daftar 5`.

Tidak menyentuh konten_harian.py. Teks digambar program (akurat).

CARA PAKAI
  .venv/bin/python konten_hero_news.py --file konten_hero_news_data.json \
      --foto assets/bg/xxx.jpg --png out.png --cek
"""
from __future__ import annotations

import argparse
import json
import os

from PIL import Image, ImageDraw, ImageFilter

from konten_harian import font, bungkus, teks_tracking, lebar_tracking, tempel_logo, LOGO_DEFAULT

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1350
MX0, MX1 = 64, 1016

# palet BROWN OmniSense (hangat, senada website)
BG = (14, 13, 12)
BONE = (243, 239, 230)
MUTED = (185, 178, 166)
MUTED_DIM = (138, 130, 118)
BROWN = (168, 116, 76)
BROWN_LT = (212, 165, 116)
BROWN_DK = (74, 48, 30)


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


def arc_glow(img, color, alpha=110):
    """Glow melengkung besar di kanan atas (ciri khas referensi)."""
    lapis = Image.new("RGB", img.size, color)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    for t in range(0, 180, 3):
        import math
        r = 520 + t * 1.2
        cx, cy = W + 120, -180
        a = int(alpha * (1 - t / 180))
        d.arc([cx - r, cy - r, cx + r, cy + r], start=110, end=175, fill=a, width=46)
    mask = mask.filter(ImageFilter.GaussianBlur(60))
    return Image.composite(lapis, img, mask)


def blok_3d(img, color, garis):
    """Blok isometrik sederhana di pinggir (kesan server/chip)."""
    lapis = img.convert("RGBA")
    d = ImageDraw.Draw(lapis, "RGBA")
    def satu(x, y, w, h, dalam):
        atas = [(x, y), (x + w, y - dalam), (x + w + dalam, y - dalam + dalam), (x + dalam, y)]
        # sisi depan
        d.polygon([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], fill=(*color, 60), outline=(*garis, 150))
        # atap
        d.polygon([(x, y), (x + w, y), (x + w + dalam, y - dalam), (x + dalam, y - dalam)], fill=(*color, 90), outline=(*garis, 170))
        # sisi kanan
        d.polygon([(x + w, y), (x + w + dalam, y - dalam), (x + w + dalam, y - dalam + h), (x + w, y + h)], fill=(*color, 45), outline=(*garis, 130))
    satu(60, 170, 130, 130, 34)
    satu(770, 120, 112, 112, 30)
    satu(48, 620, 104, 104, 28)
    satu(800, 700, 108, 108, 30)
    return lapis.convert("RGB")


def sirkuit(img, warna, alfa=70):
    lapis = Image.new("RGB", img.size, warna)
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    rnd = 20261007
    def r():
        nonlocal rnd
        rnd = (1103515245 * rnd + 12345) & 0x7FFFFFFF
        return rnd / 0x7FFFFFFF
    for _ in range(30):
        x = int(r() * W); y = int(r() * H)
        panjang = int(120 + r() * 380)
        if r() < 0.5:
            d.line([(x, y), (x + panjang, y)], fill=alfa, width=2)
            d.ellipse([x + panjang - 5, y - 5, x + panjang + 5, y + 5], fill=alfa)
        else:
            d.line([(x, y), (x, y + panjang)], fill=alfa, width=2)
            d.ellipse([x - 5, y + panjang - 5, x + 5, y + panjang + 5], fill=alfa)
    mask = mask.filter(ImageFilter.GaussianBlur(1.1))
    return Image.composite(lapis, img, mask)


def potong_latar(path):
    """Cutout subjek (hapus latar). Prioritas: PNG cutout yang sudah ada (cache),
    lalu rembg langsung, terakhir None (fallback panel)."""
    # 1) pakai cache kalau ada (mis. assets/bg/nama-cut.png)
    akar, ext = os.path.splitext(path)
    kandidat = [akar + "-cut.png", akar + "_cut.png"]
    for c in kandidat:
        if os.path.exists(c):
            return Image.open(c).convert("RGBA")
    # 2) coba rembg langsung
    try:
        from rembg import remove
        src = Image.open(path).convert("RGB")
        if max(src.size) > 1600:
            skala = 1600 / max(src.size)
            src = src.resize((round(src.width * skala), round(src.height * skala)), Image.LANCZOS)
        hasil = remove(src)
        return hasil.convert("RGBA")
    except Exception as e:
        print(f"  [info] cutout rembg tidak tersedia ({e.__class__.__name__}) — pakai mode panel.")
        return None


def tempel_foto(img, path, warna_aksen, mode="auto"):
    """Tempel foto subjek.
      mode 'cutout' -> wajib cutout (latar dihapus), besar di tengah.
      mode 'panel'  -> foto suasana jadi panel latar atas (digelapkan + fade).
      mode 'auto'   -> cutout kalau ada/bisa, kalau tidak -> panel.
    """
    potong = None
    if mode in ("auto", "cutout"):
        potong = potong_latar(path)
    if potong is not None:
        # skala supaya tinggi ~ 1050px (dominan, headline menimpa bagian bawah)
        target_h = 1060
        skala = target_h / potong.height
        potong = potong.resize((max(1, round(potong.width * skala)), target_h), Image.LANCZOS)
        if potong.width > 1000:
            skala2 = 1000 / potong.width
            potong = potong.resize((1000, max(1, round(potong.height * skala2))), Image.LANCZOS)
        # fade tepi BAWAH foto supaya menyatu (tidak ada garis potong keras)
        import numpy as np
        a = np.array(potong.getchannel("A")).astype(np.float32)
        tinggi = a.shape[0]
        mulai = int(tinggi * 0.70)
        ramp = np.ones(tinggi, dtype=np.float32)
        for yy in range(mulai, tinggi):
            t = (yy - mulai) / max(1, (tinggi - mulai))
            ramp[yy] = 1.0 - (t ** 1.3)
        a = a * ramp[:, None]
        potong.putalpha(Image.fromarray(a.astype("uint8")))
        x = (W - potong.width) // 2
        y = 120
        img.paste(potong, (x, y), potong)
        return "cutout", (x, y, x + potong.width, y + potong.height)
    if mode == "cutout":
        return "gagal-cutout", None
    # panel: foto suasana jadi latar atas penuh, digelapkan + fade ke bawah
    src = Image.open(path).convert("RGB")
    tinggi_panel = 940
    skala = max(W / src.width, tinggi_panel / src.height)
    src = src.resize((max(1, round(src.width * skala)), max(1, round(src.height * skala))), Image.LANCZOS)
    x = (src.width - W) // 2
    src = src.crop((x, 0, x + W, tinggi_panel))
    src = Image.blend(src, Image.new("RGB", (W, tinggi_panel), BG), 0.42)
    # vignette kiri-kanan supaya teks tepi tetap terbaca
    mask = Image.new("L", (W, tinggi_panel), 255)
    md = ImageDraw.Draw(mask)
    for yy in range(tinggi_panel):
        if yy > 640:
            md.line([(0, yy), (W, yy)], fill=max(0, int(255 * (1 - (yy - 640) / 300))))
    img.paste(src, (0, 0), mask)
    return "panel", (0, 0, W, tinggi_panel)


def header(img, d, tag, tanggal):
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


def entitas(img, d, nama, aksen):
    """Nama entitas berita (mis. ANTHROPIC) — pil di kanan, sejajar dada subjek."""
    if not nama:
        return
    f = font(True, 24, None, weight="extrabold")
    tw = lebar_tracking(d, nama.upper(), f, 3.0)
    x1 = MX1
    x0 = x1 - tw - 32
    y = 452
    d.rounded_rectangle([x0, y - 8, x1, y + 36], radius=18,
                        fill=(28, 24, 20), outline=aksen, width=1)
    teks_tracking(d, (x0 + 16, y), nama.upper(), f, BONE, 3.0)


def badge_brand(d, teks, aksen):
    """Badge brand kecil tepat di atas headline (gaya 'CW' di referensi).
    Teks + label kecil, dibingkai pil tipis supaya terlihat disengaja."""
    f = font(True, 17, None, weight="extrabold")
    f_k = font(False, 12, None, weight="semibold")
    label = "OMNISENSE"
    tw = lebar_tracking(d, label, f, 2.2)
    kw = lebar_tracking(d, "RADAR AI", f_k, 1.6)
    total = tw + 18 + kw + 44
    x = (W - total) / 2
    y = 946
    d.rounded_rectangle([x, y - 6, x + total, y + 30], radius=18,
                        fill=(26, 22, 19), outline=aksen, width=1)
    teks_tracking(d, (x + 18, y + 1), label, f, BONE, 2.2)
    d.rectangle([x + 18 + tw + 9, y + 3, x + 18 + tw + 19, y + 19], fill=aksen)
    teks_tracking(d, (x + 18 + tw + 27, y + 4), "RADAR AI", f_k, MUTED, 1.6)


def headline(d, baris, aksen_lt):
    """Headline besar rata-tengah di zona bawah; baris terakhir warna aksen.
    Headline DITUMPUK di atas bagian bawah foto (seperti referensi)."""
    if not baris:
        return
    atas, bawah = 1010, 1272
    f = font(True, 96, None, weight="black")
    while f.size > 40:
        jarak = int(f.size * 1.06)
        if max(lebar_tracking(d, b, f, -2) for b in baris) <= (MX1 - MX0) and len(baris) * jarak <= (bawah - atas):
            break
        f = font(True, f.size - 2, None, weight="black")
    jarak = int(f.size * 1.06)
    tinggi = len(baris) * jarak
    y = atas + max(0, (bawah - atas - tinggi) // 2)
    for i, b in enumerate(baris):
        warna = aksen_lt if i == len(baris) - 1 else BONE
        bw = lebar_tracking(d, b, f, -2)
        # drop shadow tebal biar terbaca di atas foto
        for dx, dy in ((3, 3), (2, 2)):
            teks_tracking(d, ((W - bw) / 2 + dx, y + dy), b, f, (0, 0, 0), -2)
        teks_tracking(d, ((W - bw) / 2, y), b, f, warna, -2)
        y += jarak
    return f.size


def scrim_bawah(img, atas=880, tebal=470):
    """Gradasi gelap dari transparan -> pekat, supaya headline terbaca di atas foto."""
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    for yy in range(atas, min(H, atas + tebal)):
        t = (yy - atas) / tebal
        md.line([(0, yy), (W, yy)], fill=int(235 * min(1, t * 1.25)))
    return Image.composite(Image.new("RGB", (W, H), BG), img, mask)


def badge_akun(d, teks, aksen):
    f = font(True, 13, None, weight="semibold")
    tw = lebar_tracking(d, teks, f, 0.8)
    x1, y1 = W - 54, 1288
    d.rounded_rectangle([x1 - tw - 36, y1, x1, y1 + 32], radius=16,
                        fill=(28, 25, 22), outline=aksen, width=1)
    teks_tracking(d, (x1 - tw - 18, y1 + 8), teks, f, BONE, 0.8)


def render(data, foto, out, cek=False):
    aksen = hex_rgb(data.get("aksen", "#A8744C"))
    aksen_lt = hex_rgb(data.get("aksen_terang", "#D4A574"))
    img = Image.new("RGB", (W, H), BG)
    img = arc_glow(img, aksen, alpha=105)
    img = glow(img, W * 0.30, H * 0.22, int(W * 0.7), aksen, alpha=55, power=1.8)
    img = blok_3d(img, BROWN_DK, aksen)
    img = sirkuit(img, aksen_lt, alfa=58)
    d = ImageDraw.Draw(img)
    lapor = []

    mode, kotak = "tanpa-foto", None
    mode_minta = data.get("mode_foto", "auto")
    if foto and os.path.exists(foto):
        mode, kotak = tempel_foto(img, foto, aksen, mode=mode_minta)
        if mode == "cutout":
            img = scrim_bawah(img, atas=860, tebal=500)
        d = ImageDraw.Draw(img)
    lapor.append(f"  foto: {os.path.basename(foto) if foto else '-'} | mode={mode} | kotak={kotak}")

    header(img, d, data.get("tag", "[ RADAR AI ]"), data.get("tanggal", ""))
    d = ImageDraw.Draw(img)
    entitas(img, d, data.get("entitas", ""), aksen)

    badge_brand(d, data.get("badge_brand", "OS"), aksen)
    uk = headline(d, data.get("headline", []), aksen_lt)
    lapor.append(f"  headline @{uk}px ({len(data.get('headline', []))} baris)")

    badge_akun(d, data.get("badge_akun", "IG | @omnisense_id"), aksen)
    img.save(out)
    if cek:
        print(f"[hero-news] {W}x{H}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out}")
    return out


def main():
    ap = argparse.ArgumentParser(description="Template hero-news OmniSense (gaya cryptowave, palet brown).")
    ap.add_argument("--file", default=os.path.join(BASE, "konten_hero_news_data.json"))
    ap.add_argument("--foto", default=None, help="file foto subjek berita (cutout otomatis kalau rembg ada)")
    ap.add_argument("--png", default=os.path.join(BASE, "konten_hero_news.png"))
    ap.add_argument("--cek", action="store_true")
    a = ap.parse_args()
    data = json.load(open(a.file))
    foto = a.foto or data.get("foto")
    render(data, foto, a.png, cek=a.cek)


if __name__ == "__main__":
    main()
