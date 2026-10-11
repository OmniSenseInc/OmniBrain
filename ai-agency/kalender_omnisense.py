#!/usr/bin/env python3
"""
kalender_omnisense.py — Bikin gambar jadwal bulanan OmniSense (ukuran 1080x1350, rasio 4:5).

Isi gambarnya: tanggal, tema tiap pekan, dan tugas kecil tiap hari.
Warnanya sengaja ikut template konten OmniSense, jangan diubah:
latar hitam #09090B, kotak kaca #121215, garis tepi #27272A, tulisan putih #FFFFFF, abu #94A3B8.

CARA PAKAI (jalankan dari folder ini)
  .venv/bin/python kalender_omnisense.py                     # hasil: kalender_omnisense.png + prompt AI
  .venv/bin/python kalender_omnisense.py --progress-pekan 1  # tambah baris progress pekan 1
  .venv/bin/python kalender_omnisense.py --cta "JADWALKAN KONSULTASI GRATIS"
  .venv/bin/python kalender_omnisense.py --png hasil.png
  .venv/bin/python kalender_omnisense.py --prompt-only       # cuma cetak prompt AI (ID + EN)
  .venv/bin/python kalender_omnisense.py --acak-online --pekan 5 --tgl-senin 2026-10-19
  .venv/bin/python kalender_omnisense.py --font-bold /path/Inter-Bold.ttf --font-regular /path/Inter-Regular.ttf

CATATAN PENTING
  - Tanggalnya pasti benar karena digambar oleh program, bukan oleh AI gambar. AI gambar sering
    salah menulis 28 kotak tanggal. Jadi pakai PNG ini untuk jadwal resmi. Prompt AI dipakai kalau
    cuma mau versi gaya/artistik (teks tanggalnya nanti ditempel manual di Canva).
  - Tulisan kecil di dalam kotak = tugas hari itu. Arti tiap tulisan ada di KAMUS_istilah_plain.md.
  - Font bawaan = DejaVu Sans (sudah ada di sistem). Kalau mau tampilan final, arahkan
    --font-bold/--font-regular ke Inter Bold / Montserrat ExtraBold.
"""

import argparse
import json
import os
import random
import sys
from datetime import date, timedelta

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_DEFAULT = os.path.join(BASE, "kalender_data.json")

# ---- warna (disamakan dengan template konten OmniSense, jangan diubah)
OBSIDIAN = (9, 9, 11)        # #09090B
GLASS = (18, 18, 21)         # #121215
CELL = (12, 12, 14)          # #0C0C0E
BORDER = (39, 39, 42)        # #27272A
WHITE = (255, 255, 255)      # #FFFFFF
SLATE = (148, 163, 184)      # #94A3B8
SLATE_DIM = (100, 116, 139)  # #64748B

HARI = ["SEN", "SEL", "RAB", "KAM", "JUM", "SAB", "MIN"]

# ---- ukuran kanvas & posisi (bagian penting cuma di Y 135-1215)
W, H = 1080, 1350
CARD = [40, 135, 1040, 1215]      # kotak kaca utama
X0, X1 = 70, 1010                 # batas kiri-kanan area isi
Y_TAG = 160
Y_TITLE = 196
Y_SUB = 250
Y_NOTE = 278
Y_BAND0 = 300
Y_KEPALA = 356
Y_GRID = 378
TINGGI_BARIS = 176
LEBAR_LABEL = 150                 # lebar kolom PEKAN di kiri (dikecilkan biar tulisan kotak muat)
GAP = 6


def font(bold, size, path=None):
    from PIL import ImageFont
    if path:
        return ImageFont.truetype(path, size)
    dasar = "/usr/share/fonts/truetype/dejavu/"
    return ImageFont.truetype(dasar + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), size)


def garis_spiral(d, cx, cy, r_max=13, putaran=2.2, warna=WHITE, lebar=2):
    """Gambar logo spiral putih (sementara, sampai logo resmi siap)."""
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


def render(data, out_path, baris_progress="", cta="", fbold=None, freg=None):
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (W, H), OBSIDIAN)
    d = ImageDraw.Draw(img)

    f_tag = font(False, 15, freg)
    f_word = font(True, 22, fbold)
    f_title = font(True, 38, fbold)
    f_sub = font(True, 21, fbold)
    f_note = font(False, 14, freg)
    f_band = font(True, 14, fbold)
    f_kepala = font(True, 15, fbold)
    f_label = font(True, 14, fbold)
    f_tema = font(False, 11, freg)
    f_tgl = font(True, 21, fbold)
    f_cell = font(False, 11, freg)
    f_leg = font(False, 12, freg)
    f_leg13 = font(False, 13, freg)

    # ---- kotak kaca utama
    d.rounded_rectangle(CARD, radius=20, fill=GLASS, outline=BORDER, width=1)

    # ---- bagian atas: label di kiri, logo + nama di kanan
    d.text((X0, Y_TAG), "[ JADWAL KERJA TIM ]", font=f_tag, fill=SLATE)
    garis_spiral(d, X1 - 20, Y_TAG + 12)
    kata = "omnisense"
    d.text((X1 - 40 - d.textlength(kata, font=f_word), Y_TAG), kata, font=f_word, fill=WHITE)

    d.text((X0, Y_TITLE), "RENCANA BULANAN", font=f_title, fill=WHITE)
    d.text((X0, Y_SUB), f"{data['siklus']} · {data['periode']}", font=f_sub, fill=WHITE)
    d.text((X0, Y_NOTE), data["subjudul"], font=f_note, fill=SLATE)

    # ---- strip HARI 0
    d.rounded_rectangle([X0, Y_BAND0, X1, Y_BAND0 + 38], radius=10, fill=CELL, outline=BORDER, width=1)
    d.text((X0 + 16, Y_BAND0 + 11), data["hari0"], font=f_band, fill=WHITE)

    # ---- tabel: 1 kolom PEKAN + 7 kolom hari
    lebar_hari = (X1 - X0 - LEBAR_LABEL) / 7.0
    for i, h in enumerate(HARI):
        cx = X0 + LEBAR_LABEL + i * lebar_hari
        tw = d.textlength(h, font=f_kepala)
        d.text((cx + (lebar_hari - tw) / 2, Y_KEPALA), h, font=f_kepala, fill=SLATE_DIM)

    for baris, pekan in enumerate(data["pekan"]):
        y = Y_GRID + baris * TINGGI_BARIS
        d.rounded_rectangle([X0, y, X0 + LEBAR_LABEL - GAP, y + TINGGI_BARIS - GAP],
                            radius=10, fill=CELL, outline=BORDER, width=1)
        d.text((X0 + 14, y + 12), pekan["label"], font=f_label, fill=WHITE)
        for j, bt in enumerate(bungkus(d, pekan["tema"], f_tema, LEBAR_LABEL - 30)[:4]):
            d.text((X0 + 14, y + 34 + j * 14), bt, font=f_tema, fill=SLATE)
        # catatan rapat datang: kalau kepanjangan, turun baris sendiri (dulu kepotong)
        info = bungkus(d, pekan["offline_info"], f_tema, LEBAR_LABEL - 28)[:2]
        for j, bt in enumerate(info):
            d.text((X0 + 14, y + TINGGI_BARIS - GAP - 26 - (len(info) - 1 - j) * 14),
                   bt, font=f_tema, fill=SLATE_DIM)

        for i, hari in enumerate(pekan["hari"]):
            cx = X0 + LEBAR_LABEL + i * lebar_hari
            kotak = [cx, y, cx + lebar_hari - GAP, y + TINGGI_BARIS - GAP]
            offline = hari.get("tipe") == "offline"
            online = any(t.startswith("RAPAT ONLINE") for t in hari["tag"])
            if offline:
                d.rounded_rectangle(kotak, radius=10, fill=WHITE)
                warna_tgl, warna_tag = OBSIDIAN, OBSIDIAN
            else:
                d.rounded_rectangle(kotak, radius=10, fill=CELL,
                                    outline=WHITE if online else BORDER, width=2 if online else 1)
                warna_tgl, warna_tag = WHITE, (WHITE if online else SLATE)
            d.text((cx + 12, y + 8), hari["tgl"], font=f_tgl, fill=warna_tgl)
            for k, t in enumerate(hari["tag"][:4]):
                d.text((cx + 12, y + 40 + k * 15), t, font=f_cell, fill=warna_tag)

    # ---- keterangan simbol
    y_leg = Y_GRID + 4 * TINGGI_BARIS + 4
    x = X0
    for nama in ["RAPAT DATANG", "RAPAT ONLINE"]:
        if nama == "RAPAT DATANG":
            d.rounded_rectangle([x, y_leg, x + 16, y_leg + 16], radius=4, fill=WHITE)
        else:
            d.rounded_rectangle([x, y_leg, x + 16, y_leg + 16], radius=4, fill=CELL, outline=WHITE, width=2)
        d.text((x + 24, y_leg + 2), nama, font=f_leg, fill=SLATE)
        x += 24 + d.textlength(nama, font=f_leg) + 30
    d.text((x, y_leg + 2), "tulisan kecil di kotak = tugas hari itu", font=f_leg, fill=SLATE_DIM)

    # ---- baris progress (kalau diminta)
    y_band = y_leg + 32
    if baris_progress:
        d.rounded_rectangle([X0, y_band, X1, y_band + 40], radius=10, fill=CELL, outline=BORDER, width=1)
        d.text((X0 + 16, y_band + 12), "PROGRESS", font=f_band, fill=SLATE)
        d.text((X0 + 104, y_band + 12), baris_progress, font=f_band, fill=WHITE)
        y_band += 46

    # ---- tombol CTA (kalau diminta)
    if cta:
        tw = d.textlength(cta, font=f_band)
        px = (X0 + X1) / 2
        d.rounded_rectangle([px - tw / 2 - 26, y_band, px + tw / 2 + 26, y_band + 40],
                            radius=20, fill=GLASS, outline=SLATE_DIM, width=1)
        d.text((px - tw / 2, y_band + 12), cta, font=f_band, fill=WHITE)

    # ---- kaki halaman (tengah, abu redup)
    kaki = "@omnisense_id • omnisense.id"
    d.text(((W - d.textlength(kaki, font=f_leg13)) / 2, 1230), kaki, font=f_leg13, fill=SLATE_DIM)

    img.save(out_path)
    return out_path


def baris_progress_dari_state(pekan):
    """Baca progress_tim.json, ubah jadi satu baris teks untuk ditampilkan di gambar."""
    path = os.path.join(BASE, "progress_tim.json")
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
        info = st["pekan"].get(str(pekan))
        if not info:
            return ""
        bagian = []
        for orang, data in info["orang"].items():
            if data.get("sumber") == "auto":
                total = sum(i["bobot"] for i in data["items"]) or 1
                dapat = sum(i["bobot"] for i in data["items"] if i["selesai"])
                pc = round(dapat * 100 / total) if dapat else None
            else:
                pc = data.get("persen")
            bagian.append(f"{orang} {str(pc) + '%' if pc is not None else '--'}")
        urut = ["Nathanael", "Vincent", "Michael"]
        bagian.sort(key=lambda s: urut.index(s.split()[0]) if s.split()[0] in urut else 99)
        return f"PEKAN {pekan} — " + "  ·  ".join(bagian)
    except Exception:
        return ""


PROMPT_ID = """PROMPT GAMBAR (Bahasa Indonesia) — tempel ke generator gambar AI kamu:
Poster kalender bulanan vertikal 4:5 (1080x1350), gaya editorial premium minimalis Swiss tech, gelap monokrom.
Latar hitam obsidian #09090B (dark obsidian), 85% komposisi. Kartu kaca gelap #121215 (glass card) di tengah
dengan sudut membulat 20px dan garis tepi tipis 1px #27272A (dark border), isi vital hanya di area aman
Y 135-1215px. Header: label kecil kurung siku "[ KALENDER SIKLUS ]" warna slate #94A3B8 (slate) di kiri atas,
logo spiral putih #FFFFFF (white) + wordmark huruf kecil "omnisense" di kanan atas. Judul ALL-CAPS extra-bold
putih: "RENCANA BULANAN", lalu subjudul putih lebih kecil "{periode}" dan satu baris penjelas slate. Satu strip
kaca gelap berisi satu baris teks putih kecil. Isi utama: grid 8 kolom x 4 baris — kolom kiri label "PEKAN 1..4"
putih dengan tema kecil slate, 7 kolom hari SEN sampai MIN; sel kotak membulat gelap berangka tanggal putih
tebal, satu sel per baris penuh putih #FFFFFF dengan angka tanggal hitam (rapat offline), sel rapat online
bergaris tepi putih tipis. Tanpa warna lain: hanya hitam, putih, abu slate. Tanpa glow, tanpa gradasi
warna-warni, tanpa ornamen 3D. Tipografi sans-serif geometris modern (Inter Tight Bold / Montserrat ExtraBold),
letter-spacing rapat. Footer tengah kecil abu redup: "@omnisense_id • omnisense.id".
Bersih, tenang, profesional, banyak ruang kosong."""

PROMPT_EN = """IMAGE PROMPT (English) — paste into your AI image generator:
Vertical monthly-calendar poster, 4:5 (1080x1350), premium minimalist Swiss-tech editorial, dark monochrome.
Obsidian black background #09090B (dark obsidian), 85% of the composition. Centered dark glass card #121215
(glass card), 20px rounded corners, 1px border #27272A (dark border); vital content inside the safe area
Y 135-1215px. Header: small bracketed slate label "[ KALENDER SIKLUS ]" (#94A3B8 slate) top-left, white spiral
logo #FFFFFF (white) with lowercase wordmark "omnisense" top-right. Ultra-bold ALL-CAPS white headline
"RENCANA BULANAN", smaller white subtitle "{periode}" and one slate explainer line below. One dark glass strip
holding a single small white line of text. Main body: 8-column x 4-row grid — leftmost column labels
"PEKAN 1..4" in white with small slate theme text, seven day columns SEN to MIN; cells are dark rounded
rectangles with bold white date numbers, one cell per row is solid white #FFFFFF with black date number
(offline meeting), online-meeting cells have a thin white outline. No other colors: black, white, slate grey
only. No glow, no colorful gradients, no busy 3D ornaments. Modern geometric sans-serif typography
(Inter Tight Bold / Montserrat ExtraBold), tight letter-spacing. Small dim grey centered footer:
"@omnisense_id • omnisense.id". Clean, calm, professional, generous whitespace."""


def cetak_prompt(data):
    print(PROMPT_ID.format(periode=data["periode"]))
    print()
    print("-" * 70)
    print()
    print(PROMPT_EN.format(periode=data["periode"]))
    print()
    print("-" * 70)
    print("CATATAN: prompt di atas bagus untuk GAYA/latar (sewarna template konten). Untuk tanggal yang")
    print("AKURAT, pakai PNG hasil script ini (digambar program) — model gambar AI sering salah menulis")
    print("28 kotak tanggal. Kalau mau versi AI, pakai hasil AI sebagai latar lalu tempel teksnya di Canva.")


def acak_online(pekan_ke, tgl_senin):
    random.seed()
    s = date.fromisoformat(tgl_senin)
    pilih = sorted(random.sample([s + timedelta(days=i) for i in range(5)], 2))
    print(f"PEKAN {pekan_ke} (Senin {s.strftime('%d %b %Y')}) — hasil undian hari ONLINE:")
    print(f"  RAPAT ONLINE 1 (bahas hambatan, 30 menit) : {pilih[0].strftime('%A %d %b %Y')} 20:00")
    print(f"  RAPAT ONLINE 2 (review hasil + rencana konten, 45 menit) : {pilih[1].strftime('%A %d %b %Y')} 20:00")
    print("  (rapat datang tetap Sabtu 16:00 atau Minggu 19:30 — tempel hasil ini ke jadwal_pertemuan_tim.md)")


def main():
    ap = argparse.ArgumentParser(description="Bikin gambar jadwal bulanan OmniSense (1080x1350)")
    ap.add_argument("--data", default=DATA_DEFAULT)
    ap.add_argument("--png", default=os.path.join(BASE, "kalender_omnisense.png"))
    ap.add_argument("--prompt-only", action="store_true", help="cuma cetak prompt AI")
    ap.add_argument("--acak-online", action="store_true", help="pilih acak 2 hari rapat online (Senin-Jumat)")
    ap.add_argument("--progress-pekan", default=None,
                    help="tampilkan baris progress pekan N (dibaca dari progress_tim.json)")
    ap.add_argument("--cta", default="", help='teks CTA gaya template, mis. "JADWALKAN KONSULTASI GRATIS"')
    ap.add_argument("--font-bold", default=None, help="path font bold (mis. Inter-Bold.ttf)")
    ap.add_argument("--font-regular", default=None, help="path font regular")
    ap.add_argument("--pekan", default="baru")
    ap.add_argument("--tgl-senin", default=None, help="tanggal Senin pekan itu, format YYYY-MM-DD")
    args = ap.parse_args()

    with open(args.data, encoding="utf-8") as f:
        data = json.load(f)

    if args.acak_online:
        if not args.tgl_senin:
            sys.exit("--acak-online butuh --tgl-senin YYYY-MM-DD (tanggal Senin pekan itu).")
        acak_online(args.pekan, args.tgl_senin)
        return

    if not args.prompt_only:
        baris = baris_progress_dari_state(args.progress_pekan) if args.progress_pekan else ""
        try:
            out = render(data, args.png, baris, args.cta, args.font_bold, args.font_regular)
            print("Gambar jadwal sudah dibuat:", out)
        except ImportError:
            print("Pillow belum ada. Pasang dulu:  uv pip install --python .venv/bin/python pillow")
            print("lalu jalankan:  .venv/bin/python kalender_omnisense.py")

    cetak_prompt(data)


if __name__ == "__main__":
    main()
