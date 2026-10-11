#!/usr/bin/env python3
"""Baca pesan penilaian dari situs dan hitung ulang dengan kalkulator resmi.

Dipakai bot WhatsApp saat pengunjung mengirim pesan dari halaman penilaian
(penilaian.html). Jangan percaya angka yang dikirim pengunjung — hitung ulang,
lalu bandingkan.

Mendukung dua format:
  v1 — 8 jawaban, satu per dimensi (tab lama di index.html)
  v2 — 15 jawaban per soal (D1a, D1b, D2a, ... D8) + identitas bisnis & nomor

Contoh:
    python3 baca_penilaian.py --uji
    python3 baca_penilaian.py --teks "[PENILAIAN-SITUS v2]
    sesi=OS-20261001-94F8
    bisnis=Kopi Senja
    kontak=0812-3456-7890
    D1a=1 D1b=2 D2a=2 D2b=2 D2c=3 ...
    skor_situs=52.8 band=Konvensional"

Keluaran: JSON ringkas untuk dipakai bot (skor, band, cocok/tidak, jawaban
belum pasti, catatan konsistensi, tulisan pengunjung, dan ringkasan).
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
KALK = BASE / "kalkulator_kesiapan.py"
DATA_SITUS = BASE / "website" / "assets" / "penilaian-data.js"

PENANDA_RE = re.compile(r"\[PENILAIAN-SITUS v([12])\]")
URUT = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8"]
NAMA = {
    "D1": "Strategi & Kepemimpinan",
    "D2": "Kesiapan Data",
    "D3": "Infrastruktur & Teknologi",
    "D4": "Digitalisasi Proses",
    "D5": "Organisasi & Budaya",
    "D6": "SDM & Keterampilan",
    "D7": "Tata Kelola, Keamanan & Kepatuhan",
    "D8": "Anggaran & Finansial",
}
BOBOT = {"D1": 0.10, "D2": 0.20, "D3": 0.15, "D4": 0.15,
         "D5": 0.10, "D6": 0.15, "D7": 0.10, "D8": 0.05}

# Cadangan kalau berkas data situs tidak ada. Harus sama dengan
# tab-penilaian/pertanyaan_situs.json.
PETA_SOAL_CADANGAN = {
    "D1": ["D1a", "D1b"],
    "D2": ["D2a", "D2b", "D2c"],
    "D3": ["D3a", "D3b"],
    "D4": ["D4a", "D4b"],
    "D5": ["D5a", "D5b"],
    "D6": ["D6a", "D6b"],
    "D7": ["D7"],
    "D8": ["D8"],
}


# --------------------------------------------------------------------------
# data situs (satu sumber kebenaran: assets/penilaian-data.js)
# --------------------------------------------------------------------------
def _data_situs():
    """Baca __PENILAIAN_SITUS__ dari berkas data halaman penilaian."""
    try:
        teks = DATA_SITUS.read_text(encoding="utf-8")
        m = re.search(r"window\.__PENILAIAN_SITUS__\s*=\s*(\{.*\})\s*;", teks, re.S)
        if not m:
            return {}
        return json.loads(m.group(1))
    except Exception:
        return {}


def peta_soal():
    """Dimensi -> daftar kode soal, urut D1..D8."""
    data = _data_situs()
    if data.get("dimensi"):
        peta = {}
        for d in data["dimensi"]:
            peta[d["kode"]] = list(d.get("soal", []))
        if peta:
            return peta
    return dict(PETA_SOAL_CADANGAN)


def urut_soal():
    """Urutan kode soal sesuai berkas data situs (dipakai untuk kalkulator)."""
    data = _data_situs()
    if data.get("urut"):
        return list(data["urut"])
    hasil = []
    peta = peta_soal()
    for d in URUT:
        hasil.extend(peta.get(d, []))
    return hasil


def aturan_dari_situs():
    """Peta kode aturan -> dimensi yang terlibat.

    Aturan konsistensi didefinisikan di situs (aturan_konsistensi). Kunci `jika`
    berisi kode soal (D2a, D3a, ...). Kalau berkas situs tidak ada, kembalikan {}
    dan bot turun ke perilaku lama — jangan sampai bot mati karenanya.
    """
    try:
        data = _data_situs()
        if not data:
            teks = (BASE / "website" / "index.html").read_text(encoding="utf-8")
            m = re.search(r"window\.__PENILAIAN__\s*=\s*(\{.*?\});", teks, re.S)
            if not m:
                return {}
            data = json.loads(m.group(1))
        peta_s = peta_soal()
        kode_ke_dim = {}
        for dim, daftar in peta_s.items():
            for k in daftar:
                kode_ke_dim[k] = dim
            kode_ke_dim[dim] = dim  # format lama (v1) memakai kode dimensi langsung
        peta = {}
        for a in data.get("aturan_konsistensi", {}).get("aturan", []):
            kode = a.get("kode")
            dims = sorted({kode_ke_dim[k] for k in a.get("jika", {}) if k in kode_ke_dim},
                          key=URUT.index)
            if kode and dims:
                peta[kode] = dims
        return peta
    except Exception:
        return {}


# --------------------------------------------------------------------------
# hitung
# --------------------------------------------------------------------------
def hitung_ulang(nilai):
    """Panggil kalkulator resmi; satu sumber kebenaran angka."""
    out = subprocess.run(
        [sys.executable, str(KALK), "-n"] + [str(v) for v in nilai],
        capture_output=True, text=True, check=True,
    ).stdout
    m = re.search(r"([0-9]+\.[0-9])%", out)
    if not m:
        raise SystemExit("kalkulator tidak mengeluarkan skor:\n" + out)
    persen = float(m.group(1))
    # Ambang band HANYA ada di kalkulator. Jangan disalin ke sini, nanti bisa
    # menyimpang saat ambang diubah. Cukup pakai band yang dilaporkan kalkulator.
    seg = re.search(r"Segmen\s*:\s*(.+)", out)
    nama_band = ""
    if seg:
        mentah = seg.group(1).strip().upper()
        nama_band = {"LAYAK LANJUT": "Layak Lanjut", "SIAP PENUH": "Siap Penuh",
                     "KONVENSIONAL": "Konvensional", "AWAL": "Awal",
                     "SANGAT AWAL": "Sangat Awal"}.get(mentah, seg.group(1).strip().title())
    return persen, nama_band, out


def nilai_per_dimensi(nilai_soal):
    """Rata-rata nilai soal per dimensi (rumus sama dengan situs)."""
    peta = peta_soal()
    hasil = {}
    for dim in URUT:
        angka = [nilai_soal[k] for k in peta.get(dim, []) if k in nilai_soal]
        hasil[dim] = round(sum(angka) / len(angka), 2) if angka else 0.0
    return hasil


def dimensi_bentrok(catatan, peta_aturan):
    """Dimensi yang terlibat dalam aturan yang terpicu, urut D1..D8.

    Dimensi yang muncul di SEMUA aturan terpicu ditaruh di depan, karena itulah
    titik yang paling mungkin jadi akar pertentangannya (mis. D3 pada R1+R4).
    """
    kode = [k.strip() for k in (catatan or "").split(",") if k.strip()]
    kumpulan = [peta_aturan.get(k, []) for k in kode if peta_aturan.get(k)]
    if not kumpulan:
        return []
    hitung = {}
    for dims in kumpulan:
        for d in dims:
            hitung[d] = hitung.get(d, 0) + 1
    return sorted(hitung, key=lambda d: (-hitung[d], URUT.index(d)))


# --------------------------------------------------------------------------
# baca pesan
# --------------------------------------------------------------------------
def _ambil(teks, nama):
    m = re.search(r"^" + nama + r"\s*=\s*(.+)$", teks, re.M)
    return m.group(1).strip() if m else ""


def baca(teks):
    m_penanda = PENANDA_RE.search(teks)
    if not m_penanda:
        return {"dikenali": False,
                "alasan": "Pesan bukan dari halaman penilaian situs (penanda tidak ada)."}
    versi = m_penanda.group(1)

    # blok baris mesin: rangkaian "kode=nilai" dipisah spasi
    blok = re.search(r"((?:\bD[1-8][a-z]?\s*=\s*[1-5]\b\s*)+)", teks)
    if not blok:
        return {"dikenali": False, "alasan": "Baris nilai tidak ditemukan."}
    nilai = {k: int(v) for k, v in re.findall(r"\b(D[1-8][a-z]?)\s*=\s*([1-5])\b", blok.group(1))}

    if versi == "1":
        if sorted(nilai) != URUT:
            return {"dikenali": False,
                    "alasan": "Nilai tidak lengkap: " + ", ".join(sorted(nilai))}
        nilai_soal = {k: nilai[k] for k in URUT}
        urut = URUT
    else:
        urut = urut_soal()
        kurang = [k for k in urut if k not in nilai]
        if kurang:
            return {"dikenali": False,
                    "alasan": "Nilai belum lengkap, kurang: " + ", ".join(kurang)}
        nilai_soal = {k: nilai[k] for k in urut}

    m_skor = re.search(r"skor_situs\s*=\s*([0-9]+(?:\.[0-9]+)?)", teks)
    skor_klaim = float(m_skor.group(1)) if m_skor else None

    yakin = {}
    m_yakin = re.search(r"keyakinan\s*=\s*([^\n]+)", teks)
    if m_yakin:
        for pasangan in m_yakin.group(1).split(","):
            if ":" in pasangan:
                k, v = pasangan.split(":", 1)
                yakin[k.strip()] = v.strip()

    m_cek = re.search(r"catatan_situs\s*=\s*([A-Z0-9,]+)", teks)
    catatan = m_cek.group(1).strip() if m_cek else ""

    # tulisan bebas pengunjung (sesi tulis sendiri)
    tulisan = ""
    m_tulis = re.search(r"Catatan yang saya tulis sendiri:\s*\n(.+?)(?:\n\s*\n|\Z)", teks, re.S)
    if m_tulis:
        tulisan = m_tulis.group(1).strip()

    ident = {k: _ambil(teks, k) for k in ("sesi", "bisnis", "kontak", "pengisi", "jenis")}

    urut_nilai = [nilai_soal[k] for k in urut]
    persen, nama_band, keluaran = hitung_ulang(urut_nilai)

    per_dim = nilai_per_dimensi(nilai_soal)
    selisih = None if skor_klaim is None else round(persen - skor_klaim, 1)

    peta_s = peta_soal()
    kode_ke_dim = {k: d for d, daftar in peta_s.items() for k in daftar}
    belum_pasti = [k for k, v in yakin.items() if v != "yakin"]
    lemah = sorted(URUT, key=lambda k: per_dim[k])[:2]
    kuat = sorted(URUT, key=lambda k: -per_dim[k])[:2]

    def label(kode):
        dim = kode_ke_dim.get(kode, kode)
        nama = NAMA.get(dim, dim)
        return nama if kode == dim else "{} ({})".format(nama, kode)

    ringkas = []
    if ident.get("bisnis"):
        ringkas.append("Bisnis: {}{}".format(
            ident["bisnis"],
            " · pengisi {}".format(ident["pengisi"]) if ident.get("pengisi") else ""))
    if ident.get("kontak"):
        ringkas.append("Nomor: " + ident["kontak"])
    ringkas.append("Skor dari situs: {:.1f}% ({})".format(
        skor_klaim if skor_klaim is not None else persen, nama_band))
    ringkas.append("Hitung ulang tim: {:.1f}%".format(persen))
    if selisih is not None and abs(selisih) >= 0.1:
        ringkas.append("Beda {:+.1f} poin — sebutkan apa adanya ke klien.".format(selisih))
    if belum_pasti:
        ringkas.append("Belum pasti: " + ", ".join(
            label(k) + " (" + yakin[k] + ")" for k in belum_pasti))
    peta_aturan = aturan_dari_situs()
    if catatan:
        ringkas.append("Perlu ditinjau (jawaban bertentangan): " + catatan)
        bentrok = dimensi_bentrok(catatan, peta_aturan)
        if bentrok:
            ringkas.append("Dimensi yang bertentangan: " + ", ".join(
                NAMA[k] + " " + str(per_dim[k]) + "/5" for k in bentrok))
    ringkas.append("Dua dimensi terlemah: " + ", ".join(
        NAMA[k] + " " + str(per_dim[k]) + "/5" for k in lemah))
    ringkas.append("Dua dimensi terkuat: " + ", ".join(
        NAMA[k] + " " + str(per_dim[k]) + "/5" for k in kuat))
    if tulisan:
        ringkas.append("Ada catatan yang ditulis sendiri pengunjung — baca sebelum membalas.")

    return {
        "dikenali": True,
        "versi": versi,
        "identitas": ident,
        "nilai": nilai_soal,
        "nilai_dimensi": per_dim,
        "urut": urut,
        "skor_klaim": skor_klaim,
        "skor_hitung_ulang": persen,
        "selisih": selisih,
        "band": nama_band,
        "keyakinan": yakin,
        "belum_pasti": belum_pasti,
        "catatan_situs": catatan,
        "dimensi_bentrok": dimensi_bentrok(catatan, peta_aturan),
        "dua_terlemah": lemah,
        "dua_terkuat": kuat,
        "tulisan_pengunjung": tulisan,
        "ringkas": ringkas,
        "keluaran_kalkulator": keluaran.strip(),
    }


CONTOH_V2 = """[PENILAIAN-SITUS v2]
sesi=OS-20261001-94F8
bisnis=Kopi Senja
kontak=0812-3456-7890
pengisi=Rina
jenis=kafe
D1a=1 D1b=2 D2a=2 D2b=2 D2c=3 D3a=2 D3b=2 D4a=3 D4b=3 D5a=2 D5b=4 D6a=3 D6b=4 D7=3 D8=3
skor_situs=52.8 band=Konvensional
keyakinan=D2a:ragu,D5b:yakin,D8:tidak_tahu

Halo OmniSense, saya baru mengisi penilaian kesiapan di situs.
Bisnis: Kopi Senja
Skor saya 52.8% — Konvensional.

Catatan yang saya tulis sendiri:
- D1a: "belum kepikiran mau dibawa ke mana 3 tahun ke depan"
"""

CONTOH_V1 = """[PENILAIAN-SITUS v1]
D1=4 D2=3 D3=5 D4=3 D5=2 D6=3 D7=3 D8=2
skor_situs=65.0 band=Layak Lanjut
keyakinan=D2:ragu,D5:yakin,D8:tidak_tahu"""

CONTOH_BENTROK = """[PENILAIAN-SITUS v2]
sesi=OS-20261001-AAAA
bisnis=Warung Bakso
kontak=081234567890
D1a=1 D1b=2 D2a=5 D2b=5 D2c=4 D3a=1 D3b=2 D4a=3 D4b=3 D5a=3 D5b=3 D6a=3 D6b=3 D7=3 D8=3
skor_situs=50.0 band=Konvensional
catatan_situs=R1 (perlu ditinjau)"""


def main():
    p = argparse.ArgumentParser(description="Baca pesan penilaian situs untuk bot WhatsApp")
    p.add_argument("--teks", help="isi pesan; kalau kosong dibaca dari stdin")
    p.add_argument("--uji", action="store_true", help="jalankan contoh uji")
    a = p.parse_args()

    if a.uji:
        gagal = 0
        h = baca(CONTOH_V2)
        ok = (h["dikenali"] and abs(h["skor_hitung_ulang"] - 52.8) < 0.05
              and h["selisih"] == 0.0 and h["identitas"]["bisnis"] == "Kopi Senja"
              and h["identitas"]["kontak"] == "0812-3456-7890"
              and h["versi"] == "2"
              and "D1a" in h["tulisan_pengunjung"])
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  v2 normal  ->  {:.1f}%  {}  selisih={}".format(
            h["skor_hitung_ulang"], h["band"], h["selisih"]))
        for b in h["ringkas"]:
            print("        " + b)

        h = baca(CONTOH_V1)
        ok = (h["dikenali"] and abs(h["skor_hitung_ulang"] - 65.0) < 0.05
              and h["versi"] == "1" and h["belum_pasti"] == ["D2", "D8"])
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  v1 lama    ->  {:.1f}%  {}".format(
            h["skor_hitung_ulang"], h["band"]))

        h = baca(CONTOH_BENTROK)
        ok = (h["dikenali"] and h["catatan_situs"].startswith("R1")
              and h["dimensi_bentrok"] == ["D2", "D3"])
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  v2 bentrok ->  {:.1f}%  bentrok={}".format(
            h["skor_hitung_ulang"], h["dimensi_bentrok"]))

        h = baca("Halo, saya mau tanya harga")
        ok = h["dikenali"] is False
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  bukan pesan penilaian  ->  " + h.get("alasan", ""))

        h = baca(CONTOH_V2.replace("D8=3", ""))
        ok = h["dikenali"] is False
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  v2 tidak lengkap  ->  " + h.get("alasan", ""))

        sys.exit(1 if gagal else 0)

    teks = a.teks if a.teks else sys.stdin.read()
    h = baca(teks)
    print(json.dumps(h, ensure_ascii=False, indent=2))
    sys.exit(0 if h["dikenali"] else 1)


if __name__ == "__main__":
    main()
