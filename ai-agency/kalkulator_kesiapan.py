#!/usr/bin/env python3
"""Kalkulator Kesiapan Digitalisasi & AI Agent
Gunakan: python3 kalkulator_kesiapan.py  atau  beri nilai 1-5 per pertanyaan.

DUA MODE:
  Mode INTI (8 nilai, free konsultasi — satu per dimensi):
    python3 kalkulator_kesiapan.py -n 4 3 5 3  2 3 3 2
  Mode SITUS (15 nilai, tab penilaian di situs — jumlah soal per dimensi berbeda):
    python3 kalkulator_kesiapan.py -n 4 3 3 5 3 2 2 3 3 2 3 3 2 4 2
  Mode LENGKAP (32 nilai, assessment dalam/fase lanjut):
    python3 kalkulator_kesiapan.py -n 4 4 5 ... (8 dimensi x 4 = 32 angka)

Bobot: Data 20% | Infra 15% | Proses 15% | SDM 15% | Strategi 10% | Budaya 10%
       | Tata kelola 10% | Anggaran 5%
"""

import sys
import argparse

# (nama_dimensi, bobot, jumlah_pertanyaan)
DIMENSI = [
    ("Strategi & Kepemimpinan",           0.10, 4),
    ("Kesiapan Data",                     0.20, 4),
    ("Infrastruktur & Teknologi",         0.15, 4),
    ("Digitalisasi Proses",               0.15, 4),
    ("Organisasi & Budaya",               0.10, 4),
    ("SDM & Keterampilan",                0.15, 4),
    ("Tata Kelola, Keamanan & Kepatuhan", 0.10, 4),
    ("Anggaran & Finansial",              0.05, 4),
]
# Mode SITUS: 15 pertanyaan, jumlah soal per dimensi berbeda-beda.
# Dipakai tab penilaian di situs (penilaian.html). Bobot TETAP sama dengan
# mode inti/lengkap — yang berubah hanya jumlah soal per dimensi, supaya
# dimensi berbobot besar (Data 20%) diwakili lebih banyak pertanyaan.
SOAL_SITUS = {
    "Strategi & Kepemimpinan":           2,
    "Kesiapan Data":                     3,
    "Infrastruktur & Teknologi":         2,
    "Digitalisasi Proses":               2,
    "Organisasi & Budaya":               2,
    "SDM & Keterampilan":                2,
    "Tata Kelola, Keamanan & Kepatuhan": 1,
    "Anggaran & Finansial":              1,
}
SITUS_Q = sum(SOAL_SITUS.values())       # 15 (mode situs)

TOTAL_Q = sum(n for _, _, n in DIMENSI)  # 32 (mode lengkap)
INTI_Q = len(DIMENSI)                    # 8 (mode inti)

BANDS = [
    (80, "SIAP PENUH",      "Lanjut PoC besar -> deployment multi AI agent"),
    (60, "LAYAK LANJUT",    "Mulai pilot AI agent, perbaiki gap paralel"),
    (40, "KONVENSIONAL",    "Digitalisasi dasar dulu, AI sebagai tahap lanjut"),
    (20, "AWAL",            "Tawarkan audit data & digitalisasi bertahap"),
    (0,  "SANGAT AWAL",     "Edukasi & assessment ulang; jangan jual AI dulu"),
]


def band(percent):
    # Bulatkan ke 1 desimal dulu. Tanpa ini, skor tepat di ambang (mis. 60,0)
    # bisa tersimpan sebagai 59.99999999999999 dan salah jatuh ke band bawah.
    percent = round(percent + 1e-9, 1)
    for threshold, nama, rekom in BANDS:
        if percent >= threshold:
            return nama, rekom
    return BANDS[-1][1], BANDS[-1][2]


def hitung(nilai, verbose=True):
    if len(nilai) == INTI_Q:
        dims = [(nama, bobot, 1) for nama, bobot, _ in DIMENSI]  # 1 pertanyaan/dimensi
    elif len(nilai) == SITUS_Q:
        dims = [(nama, bobot, SOAL_SITUS[nama]) for nama, bobot, _ in DIMENSI]
    elif len(nilai) == TOTAL_Q:
        dims = DIMENSI
    else:
        raise SystemExit(
            f"Harus {INTI_Q} (mode inti), {SITUS_Q} (mode situs), atau {TOTAL_Q} "
            f"(mode lengkap) nilai; diberi {len(nilai)}")
    for v in nilai:
        assert 1 <= v <= 5, f"Nilai di luar 1-5: {v}"

    skor_total = 0.0
    baris_dim = []
    i = 0
    for nama, bobot, n in dims:
        qs = nilai[i:i+n]
        i += n
        skor_dim = sum(qs) / n
        tertimbang = skor_dim * bobot
        skor_total += tertimbang
        baris_dim.append((nama, skor_dim, bobot, tertimbang))

    # Bulatkan ke 1 desimal di satu tempat: ini angka yang dilihat klien, dan
    # tanpa pembulatan skor tepat di ambang (60,0) tersimpan sebagai 59,999...
    percent = round((skor_total / 5) * 100.0 + 1e-9, 1)
    nama_band, rekom = band(percent)

    if verbose:
        print("=" * 62)
        print("KALKULATOR KESIAPAN DIGITALISASI & AI AGENT")
        print("=" * 62)
        print(f"{'Dimensi':<34}{'Skor':>6}{'Bobot':>7}{'Tertim':>8}")
        print("-" * 62)
        for nama, s, b, t in baris_dim:
            print(f"{nama:<34}{s:>6.2f}{b:>7.0%}{t:>8.3f}")
        print("-" * 62)
        print(f"Skor Total tertimbang : {skor_total:.3f} / 5")
        print(f"KESIAPAN              : {percent:>5.1f}%")
        print(f"Segmen                : {nama_band}")
        print(f"Rekomendasi           : {rekom}")
        print("=" * 62)

    return {
        "percent": percent,
        "band": nama_band,
        "rekomendasi": rekom,
        "per_dimensi": baris_dim,
    }


def interaktif():
    nilai = []
    urutan = 1
    for nama, _, n in DIMENSI:
        print(f"\n--- {nama} ---")
        for q in range(1, n + 1):
            while True:
                try:
                    v = int(input(f"  Q{urutan}. nilai (1-5): "))
                    if 1 <= v <= 5:
                        break
                    print("   Masukkan 1-5.")
                except (ValueError, EOFError):
                    print("   Masukkan angka 1-5.")
            nilai.append(v)
            urutan += 1
    hitung(nilai)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Kalkulator kesiapan digitalisasi")
    p.add_argument("-i", "--interaktif", action="store_true", help="mode tanya-jawab")
    p.add_argument("-n", "--nilai", nargs="+", type=int,
                   help=f"8 (inti) atau {TOTAL_Q} (lengkap) nilai 1-5 sesuai urutan dimensi")
    args = p.parse_args()

    if args.interaktif or not args.nilai:
        interaktif()
    else:
        hitung(args.nilai)