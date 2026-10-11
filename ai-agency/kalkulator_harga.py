#!/usr/bin/env python3
"""Kalkulator margin harga FNBSense per client.
Isi biaya riil, lalu lihat margin & rekomendasi harga.

Pemakaian:
  python3 kalkulator_harga.py                         # mode tanya-jawab
  python3 kalkulator_harga.py -c 150 120 2 60000 100  # vps api_juta? lihat help
opsional argumen posisi:
  python3 kalkulator_harga.py <vps_ribuan> <api_ribuan> <jam_dukungan> <tarif_per_jam> <overhead_ribuan>
Semua satuan RUPIAH kecuali jam_dukungan.
"""

import sys

def main():
    args = sys.argv[1:]
    if len(args) >= 5:
        vps = float(args[0]) * 1000
        api = float(args[1]) * 1000
        jam = float(args[2])
        tarif = float(args[3])
        overhead = float(args[4]) * 1000
    else:
        def tanya(label, default=None):
            v = input(f"{label}{f' [default {default}]' if default else ''}: ").strip()
            return float(v) if v else (default or 0)
        vps = tanya("Biaya VPS per bulan (Rupiah)", 150000)
        api = tanya("Biaya API key/LLM per bulan (Rupiah)", 100000)
        jam = tanya("Jam dukungan/pemeliharaan per bulan", 2)
        tarif = tanya("Tarif jam tim (Rupiah)", 60000)
        overhead = tanya("Overhead (lisensi, marketing, alokasi) per bulan", 100000)

    biaya_dukungan = jam * tarif
    total = vps + api + biaya_dukungan + overhead

    print("\n" + "=" * 56)
    print("RINCIAN BIAYA PER CLIENT / BULAN")
    print("-" * 56)
    print(f"  VPS              : Rp {vps:,.0f}")
    print(f"  API/LLM          : Rp {api:,.0f}")
    print(f"  Dukungan ({jam:.0f} jam x Rp {tarif:,.0f}) : Rp {biaya_dukungan:,.0f}")
    print(f"  Overhead         : Rp {overhead:,.0f}")
    print("  " + "-" * 40)
    print(f"  TOTAL BIAYA      : Rp {total:,.0f}")
    print("=" * 56)
    print("TITIK IMPAS: harga minimal = Rp {:,}".format(round(total, -3)))
    for mul in (2, 3, 4):
        print(f"  harga x{mul} (target margin sehat) = Rp {total*mul:,.0f}/bln")
    print("-" * 56)
    print("CATATAN:")
    print("  - Harga < total = RUGI. Tutup di atas sini.")
    print("  - Target harga di 2-4x biaya memberi laba + biaya hidup tim.")
    print("  - Nilai ke klien (hemat 1-2 jam/hari + stok aman) biasanya jauh lebih")
    print("    tinggi dari ini; ambil sebagian sebagai harga yang pantas.")

if __name__ == "__main__":
    main()