#!/usr/bin/env python3
"""
prompt_kalender_ai.py — Cetak PROMPT LENGKAP (siap tempel) untuk AI image generator,
dibaca dari kalender_data.json. Bedanya dengan --prompt-only di kalender_omnisense.py:
prompt di sini sudah memuat isi aslinya (tanggal + tugas tiap hari, tema tiap pekan),
bukan cuma gambaran gaya.

  .venv/bin/python prompt_kalender_ai.py            # ID + EN
  .venv/bin/python prompt_kalender_ai.py --en       # cuma English
  .venv/bin/python prompt_kalender_ai.py --id       # cuma Indonesia
  .venv/bin/python prompt_kalender_ai.py --gaya-saja  # tanpa blok data (untuk Midjourney/dll)
"""

import argparse
import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "kalender_data.json")

HARI = ["SEN", "SEL", "RAB", "KAM", "JUM", "SAB", "MIN"]

GAYA_ID = """Poster kalender bulanan vertikal rasio 4:5 (1080x1350 px), gaya editorial premium
minimalis Swiss tech, gelap monokrom, banyak ruang kosong. Latar hitam obsidian #09090B.
Kartu kaca gelap #121215 di tengah, sudut membulat 20px, garis tepi tipis 1px #27272A.
Isi penting hanya di area aman Y 135-1215 px. Tipografi sans-serif geometris modern
(Inter Tight Bold / Montserrat ExtraBold), letter-spacing rapat, huruf tajam dan bersih.
Header kiri atas: label kecil dalam kurung siku "[ KALENDER SIKLUS ]" warna abu slate #94A3B8.
Header kanan atas: logo spiral putih #FFFFFF + wordmark huruf kecil "omnisense" warna putih.
Judul ALL-CAPS extra-bold putih: "RENCANA BULANAN". Di bawahnya subjudul putih lebih kecil,
lalu satu baris penjelas abu slate. Satu strip kaca gelap memuat satu baris teks putih kecil.
Isi utama: grid 8 kolom x 4 baris — kolom paling kiri label pekan (putih) dengan tema kecil
abu slate di bawahnya, 7 kolom hari SEN SEL RAB KAM JUM SAB MIN. Tiap sel: kotak membulat
gelap berisi angka tanggal putih tebal; sel rapat offline diisi penuh putih #FFFFFF dengan
angka tanggal hitam; sel rapat online bergaris tepi putih tipis 2px. Di bawah grid ada baris
legenda kecil (kotak putih = OFFLINE, kotak garis putih = ONLINE) dan keterangan abu redup.
Footer tengah bawah kecil abu redup: "@omnisense_id • omnisense.id".
PALET TERKUNCI: hanya hitam #09090B, kaca #121215, putih #FFFFFF, abu slate #94A3B8 dan
#64748B. TANPA warna lain, TANPA glow, TANPA gradasi warna-warni, TANPA ornamen 3D,
TANPA foto orang, TANPA ikon ramai. Bersih, tenang, profesional.
Legenda di bawah tabel: "RAPAT DATANG" (kotak putih), "RAPAT ONLINE" (kotak garis putih),
dan tulisan kecil "tulisan kecil di kotak = tugas hari itu"."""

GAYA_EN = """Vertical monthly-calendar poster, 4:5 ratio (1080x1350 px), premium minimalist
Swiss-tech editorial, dark monochrome, generous whitespace. Obsidian black background #09090B.
Centered dark glass card #121215, 20px rounded corners, 1px border #27272A. Vital content only
inside the safe area Y 135-1215 px. Modern geometric sans-serif typography (Inter Tight Bold /
Montserrat ExtraBold), tight letter-spacing, crisp clean letterforms. Top-left header: small
bracketed label "[ KALENDER SIKLUS ]" in slate grey #94A3B8. Top-right header: white spiral
logo #FFFFFF with lowercase wordmark "omnisense" in white. Ultra-bold ALL-CAPS white headline:
"RENCANA BULANAN". Below it a smaller white subtitle, then one slate-grey explainer line.
One dark glass strip holding a single small white line of text. Main body: 8-column x 4-row
grid — leftmost column holds week labels (white) with small slate theme text beneath, then
seven day columns SEN SEL RAB KAM JUM SAB MIN. Each cell: dark rounded rectangle with bold
white date number; offline-meeting cells are solid white #FFFFFF with a black date number;
online-meeting cells have a thin 2px white outline. Below the grid a small legend row
(white swatch = OFFLINE, white-outline swatch = ONLINE) plus dim grey note text. Small dim
grey centered footer: "@omnisense_id • omnisense.id".
LOCKED PALETTE: only black #09090B, glass #121215, white #FFFFFF, slate grey #94A3B8 and
#64748B. NO other colors, NO glow, NO colorful gradients, NO 3D ornaments, NO people,
NO busy icons. Clean, calm, professional.
Legend below the grid: "RAPAT DATANG" (white swatch), "RAPAT ONLINE" (white-outline swatch),
and small text "tulisan kecil di kotak = tugas hari itu"."""


def blok_data_id(d):
    b = []
    b.append("TEKS YANG HARUS TERTULIS PERSIS (jangan diterjemahkan, jangan diubah, "
             "ejaan huruf demi huruf harus sama):")
    b.append(f'- Subjudul: "{d["siklus"]} · {d["periode"]}"')
    b.append(f'- Baris penjelas: "{d["subjudul"]}"')
    b.append(f'- Strip kaca di bawah judul: "{d["hari0"]}"')
    b.append("")
    b.append("ISI GRID (8 kolom x 4 baris). Kolom 1 = label pekan + tema; "
             "kolom 2-8 = hari SEN..MIN. Isi tiap sel:")
    for p in d["pekan"]:
        b.append("")
        b.append(f'  {p["label"]} | tema: "{p["tema"]}" | catatan kaki kolom: "{p["offline_info"]}"')
        for i, h in enumerate(p["hari"]):
            tag = ", ".join(h["tag"]) if h["tag"] else "(kosong, hanya angka tanggal)"
            jenis = "KOTAK PUTIH PENUH (rapat datang)" if h.get("tipe") == "offline" else (
                "KOTAK BERGARIS TEPI PUTIH (rapat online)" if any(t.startswith("RAPAT ONLINE") for t in h["tag"])
                else "kotak gelap biasa")
            b.append(f'    {HARI[i]:>3} tgl {h["tgl"]:>2} -> {jenis}; tulisan kecil: {tag}')
    b.append("")
    b.append('Legenda di bawah tabel: "RAPAT DATANG" (kotak putih) · "RAPAT ONLINE" (kotak garis putih) · '
             '"tulisan kecil di kotak = tugas hari itu"')
    return "\n".join(b)


def blok_data_en(d):
    b = []
    b.append("TEXT THAT MUST APPEAR EXACTLY AS WRITTEN (do not translate, do not paraphrase, "
             "spell every letter exactly):")
    b.append(f'- Subtitle: "{d["siklus"]} · {d["periode"]}"')
    b.append(f'- Explainer line: "{d["subjudul"]}"')
    b.append(f'- Glass strip under the headline: "{d["hari0"]}"')
    b.append("")
    b.append("GRID CONTENT (8 columns x 4 rows). Column 1 = week label + theme; "
             "columns 2-8 = days SEN..MIN. Cell contents:")
    for p in d["pekan"]:
        b.append("")
        b.append(f'  {p["label"]} | theme: "{p["tema"]}" | column footnote: "{p["offline_info"]}"')
        for i, h in enumerate(p["hari"]):
            tag = ", ".join(h["tag"]) if h["tag"] else "(empty, date number only)"
            jenis = "SOLID WHITE CELL (onsite meeting)" if h.get("tipe") == "offline" else (
                "WHITE-OUTLINED CELL (online meeting)" if any(t.startswith("RAPAT ONLINE") for t in h["tag"])
                else "plain dark cell")
            b.append(f'    {HARI[i]:>3} date {h["tgl"]:>2} -> {jenis}; small text: {tag}')
    b.append("")
    b.append('Legend below the grid: "RAPAT DATANG" (white swatch) · "RAPAT ONLINE" (white-outline swatch) · '
             '"tulisan kecil di kotak = tugas hari itu"')
    return "\n".join(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DATA)
    ap.add_argument("--id", action="store_true", dest="hanya_id")
    ap.add_argument("--en", action="store_true", dest="hanya_en")
    ap.add_argument("--gaya-saja", action="store_true",
                    help="tanpa blok data (untuk generator yang muak teks panjang, mis. Midjourney)")
    a = ap.parse_args()

    with open(a.data, encoding="utf-8") as f:
        d = json.load(f)

    bar = "=" * 72
    if not a.hanya_en:
        print(bar)
        print("PROMPT 1 — BAHASA INDONESIA (tempel utuh ke image generator)")
        print(bar)
        print(GAYA_ID)
        if not a.gaya_saja:
            print()
            print(blok_data_id(d))
        print()
        print('NEGATIF: warna selain hitam/putih/abu, glow, gradasi warna, foto orang, '
              'teks tanggal salah, teks blur/typo, watermark, tanda tangan, mockup perangkat.')
        print()
    if not a.hanya_id:
        print(bar)
        print("PROMPT 2 — ENGLISH (same prompt, paste as-is)")
        print(bar)
        print(GAYA_EN)
        if not a.gaya_saja:
            print()
            print(blok_data_en(d))
        print()
        print("NEGATIVE: colors other than black/white/slate, glow, colorful gradients, "
              "photos of people, wrong date numbers, blurred or misspelled text, watermark, "
              "signature, device mockups.")
        print()


if __name__ == "__main__":
    main()
