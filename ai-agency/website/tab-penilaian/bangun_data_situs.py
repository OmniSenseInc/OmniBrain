#!/usr/bin/env python3
"""Bangun assets/penilaian-data.js untuk halaman penilaian mandiri (penilaian.html).

Sumber (jangan disunting hasilnya — sunting sumbernya):
  - pertanyaan_situs.json : 15 pertanyaan + pilihan + peta kata kunci pembaca tulisan bebas
  - pertanyaan.json       : bobot dimensi, band, rekomendasi, keyakinan, aturan konsistensi

Aturan: bobot, rumus, dan ambang band WAJIB sama dengan kalkulator_kesiapan.py
mode SITUS. Kalau salah satu diubah, jalankan uji_paritas_situs.js.

Pakai:  python3 bangun_data_situs.py
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
TUJUAN = HERE.parent / "assets" / "penilaian-data.js"
WA = "6288809640700"

URUT_DIM = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
URUT_BAND = ["SIAP_PENUH", "LAYAK_LANJUT", "KONVENSIONAL", "AWAL", "SANGAT_AWAL"]


def muat(nama):
    p = HERE / nama
    if not p.exists():
        sys.exit(f"Berkas sumber tidak ada: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    src = muat("pertanyaan_situs.json")
    inti = muat("pertanyaan.json")

    soal = src["pertanyaan"]
    if len(soal) != src.get("jumlah", len(soal)):
        sys.exit(f"jumlah di berkas ({src.get('jumlah')}) tidak sama dengan jumlah soal ({len(soal)})")

    # --- dimensi: bobot & nama dari pertanyaan.json, daftar soal dari pertanyaan_situs.json
    bobot = {d["kode"]: d for d in inti["dimensi"]}
    dimensi = []
    for kode in URUT_DIM:
        anak = [s["kode"] for s in soal if s["dim"] == kode]
        if not anak:
            continue
        meta = bobot.get(kode)
        if meta is None:
            sys.exit(f"Dimensi {kode} ada di pertanyaan_situs.json tapi tidak ada di pertanyaan.json")
        dimensi.append({
            "kode": kode,
            "nama": meta["nama"],
            "bobot": meta["bobot"],
            "soal": anak,
        })

    total_bobot = round(sum(d["bobot"] for d in dimensi), 6)
    if total_bobot != 1.0:
        sys.exit(f"Total bobot {total_bobot} — harus tepat 1.0")

    # --- soal: rapikan jadi bentuk ringkas untuk halaman
    keluaran_soal = []
    for s in soal:
        if len(s["o"]) != 5:
            sys.exit(f"Soal {s['kode']} punya {len(s['o'])} pilihan — harus 5")
        if set(s["k"]) != {"1", "2", "3", "4", "5"}:
            sys.exit(f"Soal {s['kode']} peta kata kuncinya tidak lengkap (butuh kunci 1..5)")
        keluaran_soal.append({
            "kode": s["kode"],
            "dim": s["dim"],
            "nama": s["nama"],
            "t": s["t"],
            "p": s["p"],
            "o": s["o"],
            "k": s["k"],
        })

    # --- aturan konsistensi: terjemahkan kode DIMENSI -> kode SOAL.
    # pertanyaan.json mendefinisikan aturan memakai kode dimensi (D2, D3, ...),
    # sedangkan halaman baru menjawab per soal (D2a, D2b, ...). Tanpa terjemahan
    # ini, peringatan "perlu ditinjau" tidak akan pernah muncul.
    peta_dim_soal = src.get("aturan_soal", {})
    aturan = []
    for a in inti["aturan_konsistensi"]["aturan"]:
        peta = peta_dim_soal.get(a["kode"], {})
        jika = {}
        for dim, nilai in a["jika"].items():
            kode_soal = peta.get(dim)
            if kode_soal is None:
                sys.exit(f"Aturan {a['kode']}: dimensi {dim} belum dipetakan ke kode soal "
                         f"(tambahkan di pertanyaan_situs.json -> aturan_soal)")
            if kode_soal not in {s["kode"] for s in soal}:
                sys.exit(f"Aturan {a['kode']}: kode soal {kode_soal} tidak ada di daftar pertanyaan")
            jika[kode_soal] = nilai
        aturan.append({"kode": a["kode"], "jika": jika, "pesan": a["pesan"]})
    if not aturan:
        sys.exit("Tidak ada aturan konsistensi yang bisa diterjemahkan")

    # --- band: pastikan lengkap & urut menurun
    band = sorted(inti["band"], key=lambda b: -b["min"])
    if [b["kode"] for b in band] != URUT_BAND:
        sys.exit(f"Kode band tidak sesuai: {[b['kode'] for b in band]}")
    if band[0]["min"] != 80 or band[-1]["min"] != 0:
        sys.exit("Ambang band tidak sesuai (harus 80..0)")

    data = {
        "versi": "2.0",
        "diperbarui": inti.get("diperbarui", src.get("diperbarui", "")),
        "catatan": (
            "Data halaman penilaian mandiri (penilaian.html). Bobot, rumus, dan band WAJIB "
            "sama dengan kalkulator_kesiapan.py mode SITUS. Jangan disunting tangan — "
            "jalankan tab-penilaian/bangun_data_situs.py."
        ),
        "rumus": (
            "skor_dimensi = rata-rata nilai soal dimensi itu. skor_total = jumlah(skor_dimensi x bobot). "
            "persen = skor_total/5*100, dibulatkan 1 desimal."
        ),
        "wa": WA,
        "urut": [s["kode"] for s in keluaran_soal],
        "dimensi": dimensi,
        "soal": keluaran_soal,
        "band": band,
        "rekomendasi_dimensi": inti["rekomendasi_dimensi"],
        "keyakinan": inti["keyakinan"],
        "aturan_konsistensi": {
            "catatan": inti["aturan_konsistensi"]["catatan"],
            "aturan": aturan,
        },
    }

    teks = (
        "/* Dibuat dari tab-penilaian/pertanyaan_situs.json + pertanyaan.json "
        "— jangan disunting tangan.\n   Jalankan: python3 tab-penilaian/bangun_data_situs.py */\n"
        "window.__PENILAIAN_SITUS__ = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n"
    )
    TUJUAN.write_text(teks, encoding="utf-8")

    print(f"OK  {TUJUAN}")
    print(f"    {len(keluaran_soal)} soal · {len(dimensi)} dimensi · total bobot {total_bobot}")
    for d in dimensi:
        print(f"    {d['kode']} {d['nama']:<30} bobot {int(d['bobot']*100):>3}%  soal {','.join(d['soal'])}")


if __name__ == "__main__":
    main()
