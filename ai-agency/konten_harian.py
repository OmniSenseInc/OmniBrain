#!/usr/bin/env python3
"""
konten_harian.py — Bikin gambar konten harian OmniSense (1080x1350, rasio 4:5).

Visual system mengikuti template OmniSense yang sudah dikunci (lihat skill omnisense-content):
latar hitam obsidian #09090B, kotak kaca #121215, garis tepi #27272A,
putih #FFFFFF untuk headline & logo, slate #94A3B8 / #64748B untuk teks pendukung.
Jangan tambah warna lain (tidak ada hijau neon, tidak ada gradasi warna-warni).

Susunan gambar (atas ke bawah):
  1. header: tag kiri + logo spiral & wordmark omnisense kanan
  2. kartu kaca tengah: 1-3 poin kunci bernomor
  3. lower third kiri: headline KAPITAL tebal putih + subtitle slate
  4. tombol CTA (pill outline tipis)
  5. footer tengah: @omnisense_id • omnisense.id

CARA PAKAI
  .venv/bin/python konten_harian.py                      # baca konten_data.json -> konten_harian.png
  .venv/bin/python konten_harian.py --cek                # cetak ukuran tiap blok (buat cek kepotong/tidak)
  .venv/bin/python konten_harian.py --file lain.json --png lain.png
  .venv/bin/python konten_harian.py --caption            # cetak 3 varian caption (IG + X)

CATATAN
  Teks digambar oleh program, bukan oleh AI gambar -> tulisannya pasti benar dan tidak ngawur.
  FONT RESMI: Inter (terpasang di ~/.local/share/fonts/inter). Kalau butuh font lain, arahkan
  --font-bold / --font-regular. LOGO RESMI: logo_omnisense_white.png (dari file user) dipakai
  otomatis di header; kalau tidak ada, jatuh ke logo spiral yang digambar program.
"""

import argparse
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageStat

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DEFAULT = os.path.join(BASE, "konten_data.json")
LOGO_DEFAULT = os.path.join(BASE, "logo_omnisense_white.png")

# ---- warna (locked, jangan diubah)
OBSIDIAN = (9, 9, 11)        # #09090B
GLASS = (18, 18, 21)         # #121215
CELL = (12, 12, 14)          # #0C0C0E
BORDER = (39, 39, 42)        # #27272A
WHITE = (255, 255, 255)      # #FFFFFF
SLATE = (148, 163, 184)      # #94A3B8
SLATE_DIM = (100, 116, 139)  # #64748B
# Versi lebih terang: dipakai HANYA saat latar foto aktif, supaya teks sekunder tetap kontras.
SLATE_LATAR = (203, 213, 225)      # #CBD5E1
SLATE_DIM_LATAR = (148, 163, 184)  # #94A3B8


def terapkan_palet_latar():
    """Latar foto menurunkan kontras teks sekunder → cerahkan slate, tapi hanya kalau latar aktif."""
    global SLATE, SLATE_DIM
    if BG["path"]:
        SLATE, SLATE_DIM = SLATE_LATAR, SLATE_DIM_LATAR

W, H = 1080, 1350
SAFE_ATAS, SAFE_BAWAH = 135, 1215
X0, X1 = 70, 1010
TENGAH = (X0 + X1) / 2

FONT_DIR = "/home/ubuntu/.local/share/fonts/inter/"
FONT_CADANGAN = "/usr/share/fonts/truetype/dejavu/"
FONT_BERAT = {
    "black": ("Inter-Black.ttf", "DejaVuSans-Bold.ttf"),
    "extrabold": ("Inter-ExtraBold.ttf", "DejaVuSans-Bold.ttf"),
    "bold": ("Inter-Bold.ttf", "DejaVuSans-Bold.ttf"),
    "semibold": ("Inter-SemiBold.ttf", "DejaVuSans-Bold.ttf"),
    "medium": ("Inter-Medium.ttf", "DejaVuSans.ttf"),
    "regular": ("Inter-Regular.ttf", "DejaVuSans.ttf"),
}


# ---- latar (background)
# Aturan: template & tata letak tetap milik kita; yang berganti hanya lapisan latar.
# Latar WAJIB tetap gelap & low-contrast (brand monokrom) — kalau terang, teks putih tenggelam.
BG = {"path": None, "dim": 0.62, "blur": 0.0, "pos": "center", "vignette": True}
BG_LUM_MAKS = 95.0   # ambang luminansi rata-rata latar setelah digelapkan


def siapkan_latar(w, h, path=None, dim=None, blur=None, pos=None, vignette=None):
    """Siapkan lapisan latar dari file foto/ilustrasi: cover-crop → blur → gelapkan → vignette.

    Mengembalikan (Image RGB, info) — info dipakai untuk QA otomatis.
    """
    path = path or BG["path"]
    dim = BG["dim"] if dim is None else dim
    blur = BG["blur"] if blur is None else blur
    pos = pos or BG["pos"]
    vignette = BG["vignette"] if vignette is None else vignette

    if not path or not os.path.exists(path):
        return Image.new("RGB", (w, h), OBSIDIAN), {"sumber": "polos", "luminansi": 9.0}

    bg = Image.open(path).convert("RGB")
    skala = max(w / bg.width, h / bg.height)          # cover: penuhi kanvas, tanpa distorsi
    bg = bg.resize((max(1, round(bg.width * skala)), max(1, round(bg.height * skala))), Image.LANCZOS)
    sisa_x, sisa_y = bg.width - w, bg.height - h
    kiri = {"left": 0, "center": sisa_x // 2, "right": sisa_x}.get(pos, sisa_x // 2)
    atas = {"top": 0, "center": sisa_y // 2, "bottom": sisa_y}.get(pos, sisa_y // 2)
    bg = bg.crop((kiri, atas, kiri + w, atas + h))

    if blur:
        bg = bg.filter(ImageFilter.GaussianBlur(blur))
    if dim > 0:                                        # gelapkan: kunci keterbacaan teks
        bg = Image.blend(bg, Image.new("RGB", (w, h), OBSIDIAN), dim)
    if vignette:                                       # tepi lebih gelap, tengah tetap hidup
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).ellipse([-w * 0.30, -h * 0.20, w * 1.30, h * 1.20], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.20))
        bg = Image.composite(bg, Image.new("RGB", (w, h), OBSIDIAN), mask)

    lum = round(float(ImageStat.Stat(bg.convert("L")).mean[0]), 1)
    return bg, {"sumber": os.path.basename(path), "dim": dim, "blur": blur,
                "pos": pos, "luminansi": lum}


def scrim(img, atas=205, bawah=235):
    """Gelapkan pita atas (header) & bawah (headline+footer) supaya teks sekunder tidak tenggelam."""
    w, h = img.size
    kol = Image.new("L", (1, h))
    kol.putdata([
        int(atas * (1 - y / (h * 0.17))) if y < h * 0.17 else
        int(bawah * ((y - h * 0.62) / (h * 0.38))) if y > h * 0.62 else 0
        for y in range(h)
    ])
    return Image.composite(Image.new("RGB", (w, h), (0, 0, 0)), img, kol.resize((w, h)))


def kanvas(w, h):
    """Kanvas poster: bertekstur bila BG diset, polos OBSIDIAN bila tidak."""
    if BG["path"]:
        img, info = siapkan_latar(w, h)
        return scrim(img), info
    return Image.new("RGB", (w, h), OBSIDIAN), {"sumber": "polos", "luminansi": 9.0}


def kaca(img, kotak, radius=20, alfa=145):
    """Kartu kaca sungguhan: latar di belakang kartu diblur, lalu ditimpa fill transparan."""
    x0, y0, x1, y1 = [int(v) for v in kotak]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(img.width, x1), min(img.height, y1)
    img.paste(img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(16)), (x0, y0))
    lapis = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lapis).rounded_rectangle(
        kotak, radius=radius, fill=GLASS + (alfa,), outline=(255, 255, 255, 46), width=1)
    return Image.alpha_composite(img.convert("RGBA"), lapis).convert("RGB")


def font(bold, size, path=None, weight=None):
    """bold=True -> tebal (ExtraBold), False -> Regular; weight= pilih berat spesifik."""
    if path:
        return ImageFont.truetype(path, size)
    kunci = weight or ("extrabold" if bold else "regular")
    utama, cadangan = FONT_BERAT[kunci]
    for p in (FONT_DIR + utama, FONT_CADANGAN + cadangan):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def lebar_tracking(d, teks, f, tracking=0.0):
    """Lebar teks kalau digambar huruf-per-huruf dengan jarak antar huruf (tracking) tertentu."""
    if not teks:
        return 0.0
    return sum(d.textlength(k, font=f) for k in teks) + tracking * (len(teks) - 1)


def teks_tracking(d, xy, teks, f, fill, tracking=0.0):
    """Gambar teks dengan tracking (huruf-per-huruf). tracking negatif = rapat, positif = renggang."""
    x, y = xy
    for k in teks:
        d.text((x, y), k, font=f, fill=fill)
        x += d.textlength(k, font=f) + tracking
    return x


def tempel_logo(img, x, y, tinggi, path=LOGO_DEFAULT):
    """Tempel logo resmi (PNG putih transparan) dengan tinggi tertentu; return lebar hasil."""
    lg = Image.open(path).convert("RGBA")
    skala = tinggi / lg.height
    lg = lg.resize((max(1, round(lg.width * skala)), tinggi), Image.LANCZOS)
    img.paste(lg, (round(x), round(y)), lg)
    return lg.width


def garis_spiral(d, cx, cy, r_max=13, putaran=2.2, warna=WHITE, lebar=2):
    """Logo spiral putih (sementara, sampai logo resmi siap) — sama dengan kalender_omnisense.py."""
    import math
    titik = []
    langkah = 240
    for i in range(langkah + 1):
        t = i / langkah
        sudut = t * putaran * 2 * math.pi
        r = r_max * t
        titik.append((cx + r * math.cos(sudut), cy + r * math.sin(sudut)))
    d.line(titik, fill=warna, width=lebar, joint="curve")


def bungkus(d, teks, f, lebar_maks):
    baris, buf = [], ""
    for k in teks.split():
        uji = (buf + " " + k).strip()
        if d.textlength(uji, font=f) <= lebar_maks:
            buf = uji
        else:
            baris.append(buf)
            buf = k
    baris.append(buf)
    return baris


def tinggi_baris(d, baris, f, jarak):
    return len(baris) * jarak


def render_x(data, out_path, fbold=None, freg=None, cek=False):
    """Versi X/Twitter: 1200x675 (16:9). Dua kolom: kiri headline+subjudul+CTA, kanan kartu 3 poin."""
    WX, HX = 1200, 675
    MX0, MX1 = 60, 1140
    KIRI_A, KIRI_B = MX0, 600          # kolom kiri
    KANAN_A, KANAN_B = 640, MX1        # kolom kanan (kartu kaca)
    img, info_latar = kanvas(WX, HX)
    d = ImageDraw.Draw(img)
    lapor = []

    f_tag = font(False, 15, freg, weight="semibold")
    f_word = font(True, 22, fbold, weight="extrabold")
    f_tgl = font(False, 14, freg, weight="regular")
    f_label = font(True, 14, fbold, weight="bold")
    f_nomor = font(True, 22, fbold, weight="bold")
    f_judul_poin = font(True, 17, fbold, weight="bold")
    f_isi_poin = font(False, 15, freg, weight="regular")
    f_sub = font(False, 16, freg, weight="regular")
    f_cta = font(True, 14, fbold, weight="semibold")
    f_kaki = font(False, 13, freg, weight="medium")

    TRACK_TAG, TRACK_LABEL, TRACK_CTA, TRACK_WORD = 1.5, 1.3, 1.1, -0.4
    JARAK_ISI = 21
    JARAK_SUB = 23

    # ---- header
    kata = "omnisense"
    lebar_word = lebar_tracking(d, kata, f_word, TRACK_WORD)
    x_word = MX1 - lebar_word
    if os.path.exists(LOGO_DEFAULT):
        tempel_logo(img, x_word - 12 - 28, 40, 28)
    else:
        garis_spiral(d, x_word - 12 - 14, 55)
    teks_tracking(d, (x_word, 43), kata, f_word, WHITE, TRACK_WORD)
    teks_tracking(d, (MX0, 40), data["tag"], f_tag, SLATE, TRACK_TAG)
    d.text((MX0, 65), data.get("tanggal", ""), font=f_tgl, fill=SLATE_DIM)
    d.line([(MX0, 100), (MX1, 100)], fill=BORDER, width=1)

    # ---- kartu kaca kanan (dihitung dulu: tinggi kartu jadi acuan keseimbangan kolom kiri)
    kartu_atas = 136
    PAD = 30
    lebar_isi = (KANAN_B - KANAN_A) - PAD * 2 - 46
    blok = []
    y = kartu_atas + PAD + 34
    for poin in data["poin"]:
        baris = bungkus(d, poin["isi"], f_isi_poin, lebar_isi)
        blok.append({"judul": poin["judul"], "baris": baris, "y": y})
        y += 30 + len(baris) * JARAK_ISI + 28
    kartu_bawah = y - 28 + PAD
    if BG["path"]:
        img = kaca(img, [KANAN_A, kartu_atas, KANAN_B, kartu_bawah], radius=18)
        d = ImageDraw.Draw(img)
    else:
        d.rounded_rectangle([KANAN_A, kartu_atas, KANAN_B, kartu_bawah], radius=18, fill=GLASS, outline=BORDER, width=1)
    teks_tracking(d, (KANAN_A + PAD, kartu_atas + PAD), data.get("label_kartu", "POIN KUNCI"),
                  f_label, SLATE_DIM, TRACK_LABEL)
    for i, b in enumerate(blok):
        if i:
            d.line([(KANAN_A + PAD, b["y"] - 18), (KANAN_B - PAD, b["y"] - 18)], fill=BORDER, width=1)
        d.text((KANAN_A + PAD, b["y"] + 1), f"{i + 1:02d}", font=f_nomor, fill=SLATE)
        d.text((KANAN_A + PAD + 46, b["y"]), b["judul"], font=f_judul_poin, fill=WHITE)
        for j, bt in enumerate(b["baris"]):
            d.text((KANAN_A + PAD + 46, b["y"] + 28 + j * JARAK_ISI), bt, font=f_isi_poin, fill=SLATE)
        lapor.append(f"  poin {i + 1}: {len(b['baris'])} baris, y={b['y']}")
    lapor.append(f"  kartu: {kartu_atas}-{kartu_bawah} (isi berakhir y={y})")

    # ---- kolom kiri: headline + subjudul + CTA, dipusatkan terhadap tinggi kartu (kolom seimbang)
    lebar_kolom = KIRI_B - KIRI_A
    baris_sub = bungkus(d, data["subjudul"], f_sub, lebar_kolom)
    ukuran_head = 64
    while ukuran_head > 28:
        f_uji = font(True, ukuran_head, fbold, weight="black")
        if max(lebar_tracking(d, b, f_uji, -ukuran_head * 0.02) for b in data["headline"]) <= lebar_kolom:
            break
        ukuran_head -= 2
    f_head = font(True, ukuran_head, fbold, weight="black")
    track_head = -ukuran_head * 0.02
    jarak_head = round(ukuran_head * 1.14)
    tinggi_cta = 44
    tinggi_blok = len(data["headline"]) * jarak_head + 16 + len(baris_sub) * JARAK_SUB + 26 + tinggi_cta
    y = kartu_atas + max(0, int((kartu_bawah - kartu_atas - tinggi_blok) / 2))
    for baris_teks in data["headline"]:
        teks_tracking(d, (KIRI_A, y), baris_teks, f_head, WHITE, track_head)
        y += jarak_head
    lapor.append(f"  headline: {len(data['headline'])} baris @{ukuran_head}px, berakhir y={y}")
    y += 16
    for bt in baris_sub:
        d.text((KIRI_A, y), bt, font=f_sub, fill=SLATE)
        y += JARAK_SUB
    lapor.append(f"  subtitle: berakhir y={y}")

    cta = data.get("cta", "")
    if cta:
        y += 26
        tw = lebar_tracking(d, cta, f_cta, TRACK_CTA)
        d.rounded_rectangle([KIRI_A, y, KIRI_A + tw + 56, y + tinggi_cta],
                            radius=tinggi_cta / 2, fill=GLASS, outline=SLATE_DIM, width=1)
        teks_tracking(d, (KIRI_A + 28, y + 14), cta, f_cta, WHITE, TRACK_CTA)
        lapor.append(f"  CTA: y={y}-{y + tinggi_cta}")

    kaki = data.get("kaki", "@omnisense_id • omnisense.id")
    d.text(((WX - d.textlength(kaki, font=f_kaki)) / 2, 628), kaki, font=f_kaki, fill=SLATE_DIM)

    img.save(out_path)
    if cek:
        print(f"kanvas {WX}x{HX} (16:9, X/Twitter), margin {MX0}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out_path}")
    return out_path


def render(data, out_path, fbold=None, freg=None, cek=False, rasio="ig"):
    if rasio == "x":
        return render_x(data, out_path, fbold, freg, cek=cek)
    return render_ig(data, out_path, fbold, freg, cek=cek)


def render_ig(data, out_path, fbold=None, freg=None, cek=False):
    img, info_latar = kanvas(W, H)
    d = ImageDraw.Draw(img)
    lapor = [f"  latar: {info_latar['sumber']} | luminansi {info_latar['luminansi']}" +
             (f" | dim {info_latar.get('dim')}" if info_latar["sumber"] != "polos" else "")]

    f_tag = font(False, 15, freg, weight="semibold")
    f_word = font(True, 23, fbold, weight="extrabold")
    f_tgl = font(False, 14, freg, weight="regular")
    f_label = font(True, 14, fbold, weight="bold")
    f_nomor = font(True, 28, fbold, weight="bold")
    f_judul_poin = font(True, 23, fbold, weight="bold")
    f_isi_poin = font(False, 17, freg, weight="regular")
    f_sub = font(False, 20, freg, weight="regular")
    f_cta = font(True, 15, fbold, weight="semibold")
    f_kaki = font(False, 13, freg, weight="medium")

    # tracking sesuai locked brief: headline rapat (-0.02em), tag/label/CTA renggang
    TRACK_TAG, TRACK_LABEL, TRACK_CTA, TRACK_WORD = 1.6, 1.4, 1.2, -0.4

    # ---- 1. header: tag kiri + logo resmi & wordmark kanan (rata kanan di X1)
    kata = "omnisense"
    lebar_word = lebar_tracking(d, kata, f_word, TRACK_WORD)
    x_word = X1 - lebar_word
    tinggi_logo = 32
    if os.path.exists(LOGO_DEFAULT):
        tempel_logo(img, x_word - 14 - tinggi_logo, 157, tinggi_logo)
    else:
        garis_spiral(d, x_word - 14 - tinggi_logo / 2, 173)
    teks_tracking(d, (x_word, 160), kata, f_word, WHITE, TRACK_WORD)
    teks_tracking(d, (X0, 160), data["tag"], f_tag, SLATE, TRACK_TAG)
    d.text((X0, 190), data.get("tanggal", ""), font=f_tgl, fill=SLATE_DIM)

    # ---- 2. kartu kaca tengah (tingginya mengikuti isi, tidak ada ruang kosong menganggur)
    kartu_atas = 240
    lebar_isi = (X1 - X0) - 34 * 2 - 56
    # pass 1: ukur dulu (bungkus teks) supaya tinggi kartu diketahui sebelum kotak digambar
    blok = []
    y = kartu_atas + 74
    for poin in data["poin"]:
        baris = bungkus(d, poin["isi"], f_isi_poin, lebar_isi)
        blok.append({"judul": poin["judul"], "baris": baris, "y": y})
        y += 36 + len(baris) * 23 + 34
    kartu_bawah = y + 6
    # pass 2: gambar kotak kaca, baru isinya (urutan ini penting — kalau dibalik, teks tertimpa kotak)
    if BG["path"]:
        img = kaca(img, [X0, kartu_atas, X1, kartu_bawah])   # kartu kaca tembus latar
        d = ImageDraw.Draw(img)                              # WAJIB: kanvas baru setelah composite
    else:
        d.rounded_rectangle([X0, kartu_atas, X1, kartu_bawah], radius=20, fill=GLASS, outline=BORDER, width=1)
    teks_tracking(d, (X0 + 34, kartu_atas + 30), data.get("label_kartu", "POIN KUNCI"),
                  f_label, SLATE_DIM, TRACK_LABEL)
    for i, b in enumerate(blok):
        if i:
            d.line([(X0 + 34, b["y"] - 20), (X1 - 34, b["y"] - 20)], fill=BORDER, width=1)
        d.text((X0 + 34, b["y"] + 2), f"{i + 1:02d}", font=f_nomor, fill=SLATE)
        d.text((X0 + 34 + 56, b["y"]), b["judul"], font=f_judul_poin, fill=WHITE)
        for j, bt in enumerate(b["baris"]):
            d.text((X0 + 34 + 56, b["y"] + 36 + j * 23), bt, font=f_isi_poin, fill=SLATE)
        lapor.append(f"  poin {i + 1}: {len(b['baris'])} baris, y={b['y']}")
    lapor.append(f"  kartu: {kartu_atas}-{kartu_bawah} (isi berakhir y={y})")

    # ---- 3. lower third kiri: headline + subtitle (dipusatkan di antara kartu dan tombol)
    baris_sub = bungkus(d, data["subjudul"], f_sub, X1 - X0)
    # ukuran headline menyesuaikan otomatis supaya tidak pernah lewat batas kanan
    ukuran_head = 54
    while ukuran_head > 34:
        f_uji = font(True, ukuran_head, fbold, weight="black")
        if max(lebar_tracking(d, b, f_uji, -ukuran_head * 0.02) for b in data["headline"]) <= X1 - X0:
            break
        ukuran_head -= 2
    f_head = font(True, ukuran_head, fbold, weight="black")
    track_head = -ukuran_head * 0.02
    jarak_head = round(ukuran_head * 1.16)
    tinggi_blok = len(data["headline"]) * jarak_head + 16 + len(baris_sub) * 28
    y_cta = 1108
    y = max(kartu_bawah + 56, int((kartu_bawah + y_cta - tinggi_blok) / 2))
    for baris_teks in data["headline"]:
        teks_tracking(d, (X0, y), baris_teks, f_head, WHITE, track_head)
        y += jarak_head
    lapor.append(f"  headline: {len(data['headline'])} baris @{ukuran_head}px, berakhir y={y}")
    y += 16
    for bt in baris_sub:
        if BG["path"]:                     # latar foto: beri bayangan tipis supaya tidak tenggelam
            d.text((X0 + 1, y + 1), bt, font=f_sub, fill=(0, 0, 0))
        d.text((X0, y), bt, font=f_sub, fill=SLATE)
        y += 28
    lapor.append(f"  subtitle: berakhir y={y}")

    # ---- 4. tombol CTA
    cta = data.get("cta", "")
    if cta:
        tw = lebar_tracking(d, cta, f_cta, TRACK_CTA)
        d.rounded_rectangle([TENGAH - tw / 2 - 28, y_cta, TENGAH + tw / 2 + 28, y_cta + 42],
                            radius=21, fill=GLASS, outline=SLATE_DIM, width=1)
        teks_tracking(d, (TENGAH - tw / 2, y_cta + 13), cta, f_cta, WHITE, TRACK_CTA)
        lapor.append(f"  CTA: y={y_cta}-{y_cta + 42}")

    # ---- 5. footer
    kaki = data.get("kaki", "@omnisense_id • omnisense.id")
    d.text(((W - d.textlength(kaki, font=f_kaki)) / 2, 1230), kaki, font=f_kaki, fill=SLATE_DIM)

    img.save(out_path)
    if info_latar["luminansi"] > BG_LUM_MAKS:
        print(f"PERINGATAN: latar terlalu terang (luminansi {info_latar['luminansi']} > "
              f"{BG_LUM_MAKS}) — naikkan --bg-dim supaya teks tetap kontras")
    if cek:
        print(f"kanvas {W}x{H}, zona aman Y {SAFE_ATAS}-{SAFE_BAWAH}")
        for b in lapor:
            print(b)
        print(f"  tersimpan: {out_path}")
    return out_path


def captions(data):
    """3 varian caption sesuai aturan di skill omnisense-content."""
    head = data.get("headline_caption") or " ".join(data["headline"])
    poin = "\n".join(f"- {p['judul']}: {p['isi']}" for p in data["poin"])
    tag = data.get("hashtag", "#OmniSense #AIAgent #KecerdasanBuatan #BisnisIndonesia #AIuntukBisnis")
    ig = (
        f"{head}\n\n"
        f"{data['subjudul']}\n\n"
        f"{poin}\n\n"
        "Kalau kamu mau tahu bagian mana dari bisnismu yang paling cepat terbantu, "
        "mulai dari konsultasi gratis — hasilnya peta prioritas, bukan jualan.\n\n"
        "DM / buka profil → lanjut chat ke WhatsApp.\n\n"
        f"{tag}"
    )
    x_pendek = (
        f"{head}. {data['subjudul']}\n\n"
        "Konsultasi gratis dulu, keputusan belakangan. "
        "DM / buka profil → lanjut chat ke WhatsApp. @omnisense_id"
    )
    minimal = (
        f"{head}\n\n{data['subjudul']}\n\n"
        "Konsultasi gratis: DM / buka profil → lanjut chat ke WhatsApp.\n\n"
        "@omnisense_id • omnisense.id"
    )
    return {"instagram": ig, "x": x_pendek, "minimal": minimal}


def main():
    p = argparse.ArgumentParser(description="Gambar konten harian OmniSense (IG 1080x1350 / X 1200x675)")
    p.add_argument("--file", default=DATA_DEFAULT)
    p.add_argument("--png", default=os.path.join(BASE, "konten_harian.png"))
    p.add_argument("--font-bold", default=None)
    p.add_argument("--font-regular", default=None)
    p.add_argument("--rasio", default="ig", choices=["ig", "x"],
                   help="ig = 1080x1350 (4:5, feed Instagram); x = 1200x675 (16:9, X/Twitter)")
    p.add_argument("--cek", action="store_true", help="cetak ukuran tiap blok")
    p.add_argument("--bg", default=None, help="file gambar latar (foto/ilustrasi relevan berita)")
    p.add_argument("--bg-dim", type=float, default=0.62,
                   help="0-1, seberapa gelap latar (default 0.62; naikkan kalau teks kurang kontras)")
    p.add_argument("--bg-blur", type=float, default=0.0, help="blur latar (px)")
    p.add_argument("--bg-pos", default="center",
                   choices=["left", "center", "right", "top", "bottom"], help="titik potong latar")
    p.add_argument("--no-vignette", action="store_true", help="matikan penggelapan tepi")
    p.add_argument("--caption", action="store_true", help="cetak 3 varian caption")
    a = p.parse_args()

    BG.update({"path": a.bg, "dim": a.bg_dim, "blur": a.bg_blur,
               "pos": a.bg_pos, "vignette": not a.no_vignette})
    terapkan_palet_latar()

    with open(a.file, encoding="utf-8") as fh:
        data = json.load(fh)

    render(data, a.png, a.font_bold, a.font_regular, cek=a.cek, rasio=a.rasio)

    if a.caption:
        for nama, teks in captions(data).items():
            print(f"\n===== CAPTION: {nama.upper()} =====\n{teks}")
        print(f"\n(X versi pendek: {len(captions(data)['x'])} karakter — batas 280)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
