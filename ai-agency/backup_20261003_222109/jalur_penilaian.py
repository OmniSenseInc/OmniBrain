#!/usr/bin/env python3
"""Jalur penilaian situs -> tim: catat klien + teruskan ringkasan ke grup tim.

Dipakai bot WhatsApp ketika ada pesan DM berawalan penanda `[PENILAIAN-SITUS v1]`
(dikirim pengunjung dari tombol di situs). Skrip ini mengerjakan tiga hal yang
sebelumnya tidak ada, supaya hasil penilaian tidak berhenti di percakapan pribadi:

  1. Hitung ulang skor lewat kalkulator resmi (delegasi ke baca_penilaian.py —
     satu sumber kebenaran, jangan menyalin rumus di sini).
  2. Catat satu baris ke client_register.csv (status: penilaian-situs).
  3. Kirim ringkasan satu pesan ke grup tim lewat `hermes send`.

Skrip ini TIDAK membalas klien — balasan ke klien tetap tugas bot/LLM (skill
omnisense-consultant). Yang dikeluarkan skrip adalah DRAF balasan siap pakai,
supaya bot tidak perlu menyusun sendiri dari nol.

Pakai:
  python3 jalur_penilaian.py --uji                 # uji offline, tidak mengirim apa pun
  python3 jalur_penilaian.py --teks "<pesan>" --pengirim 628123456789
  cat pesan.txt | python3 jalur_penilaian.py --pengirim 628123456789
  ... --tanpa-kirim      # hitung + catat saja, jangan kirim ke grup tim (uji aman)

Keluaran: JSON (dikenali, skor, ringkas, pesan_klien, pesan_tim, terkirim_tim).
Keluar dengan kode 1 kalau pesan bukan dari tab penilaian -> bot harus DIAM.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
REGISTER = BASE / "client_register.csv"
GRUP_TIM = "whatsapp:120363411213386519"
NAMA_GRUP_TIM = "grup tim OmniSense"

sys.path.insert(0, str(BASE))
from baca_penilaian import baca  # noqa: E402  (satu sumber kebenaran: jangan salin rumus)


# ---------------------------------------------------------------- pesan keluar
def pesan_klien(h: dict, pengirim: str | None) -> str:
    """Draf balasan ke klien. Aturan skill: langsung, ringkas, satu pertanyaan
    per pesan, harga/closing = tim."""
    skor = h["skor_hitung_ulang"]
    band = h["band"]
    baris = [
        "Terima kasih sudah mengisi penilaian di situs.",
        "",
        "Skor kesiapan Anda {}% — {}.".format(
            ("{:.1f}".format(skor)).replace(".", ","), band),
    ]

    if h["selisih"] is not None and abs(h["selisih"]) >= 0.1:
        baris.append(
            "Catatan: hitung ulang kami menghasilkan {}%, beda {:+.1f} poin dari "
            "angka yang tampil di situs. Kami pakai angka hitung ulang.".format(
                ("{:.1f}".format(skor)).replace(".", ","), h["selisih"]))

    if h["catatan_situs"]:
        jumlah = len([k for k in h["catatan_situs"].split(",") if k.strip()])
        baris.append(
            "Ada {} hal yang tampak saling bertentangan, jadi saya perlu "
            "memastikan dulu sebelum membahas solusi.".format(
                "satu" if jumlah == 1 else jumlah))

    lemah_nama = [NAMA_DIMENSI[k] for k in h["dua_terlemah"] if k in NAMA_DIMENSI]
    if lemah_nama:
        baris.append("Dua yang paling menahan: " + " dan ".join(lemah_nama) + ".")

    tanya = None
    if h["belum_pasti"]:
        k = h["belum_pasti"][0]
        tanya = "Untuk {} — boleh diceritakan keadaan sebenarnya hari ini?".format(
            NAMA_DIMENSI.get(k, k))
    elif h.get("dimensi_bentrok"):
        k = h["dimensi_bentrok"][0]
        tanya = "Boleh saya tanya soal {} lebih dulu?".format(
            NAMA_DIMENSI.get(k, k))
    elif h["catatan_situs"]:
        k = h["dua_terlemah"][0]
        tanya = "Boleh saya tanya soal {} lebih dulu?".format(
            NAMA_DIMENSI.get(k, k))
    else:
        k = h["dua_terlemah"][0] if h["dua_terlemah"] else None
        if k:
            tanya = "Boleh saya tanya lebih dulu soal {}?".format(
                NAMA_DIMENSI.get(k, k))

    if tanya:
        baris += ["", tanya]
    baris += ["", "Konsultasi awal tetap gratis dan tanpa kewajiban."]
    return "\n".join(baris)


def pesan_tim(h: dict, pengirim: str | None, cap: str) -> str:
    skor = h["skor_hitung_ulang"]
    baris = [
        "[PENILAIAN SITUS] {}".format(cap),
        "Nomor: {}".format(pengirim or "(tidak diketahui)"),
        "Skor hitung ulang: {:.1f}% ({})".format(skor, h["band"]),
    ]
    if h["skor_klaim"] is not None:
        baris.append("Klaim situs: {:.1f}%  selisih {:+.1f}".format(
            h["skor_klaim"], h["selisih"] if h["selisih"] is not None else 0.0))
    if h["belum_pasti"]:
        baris.append("Belum pasti: " + ", ".join(
            NAMA_DIMENSI.get(k, k) + " (" + h["keyakinan"][k] + ")"
            for k in h["belum_pasti"]))
    if h["catatan_situs"]:
        baris.append("Perlu ditinjau: " + h["catatan_situs"])
        if h.get("dimensi_bentrok"):
            baris.append("Dimensi bertentangan: " + ", ".join(
                NAMA_DIMENSI.get(k, k) + " " + str(h["nilai"][k]) + "/5"
                for k in h["dimensi_bentrok"]))
    baris.append("Terlemah: " + ", ".join(
        NAMA_DIMENSI.get(k, k) + " " + str(h["nilai"][k]) + "/5"
        for k in h["dua_terlemah"]))
    baris.append("Terkuat: " + ", ".join(
        NAMA_DIMENSI.get(k, k) + " " + str(h["nilai"][k]) + "/5"
        for k in h["dua_terkuat"]))
    baris.append("Rincian D1..D8: " + " ".join(
        k + "=" + str(h["nilai"][k]) for k in h["urut"]))
    baris.append("Tercatat di client_register.csv (status: penilaian-situs).")
    baris.append("Harga & closing tetap tim. Lanjutkan bila klien berminat.")
    return "\n".join(baris)


NAMA_DIMENSI = {
    "D1": "Strategi & Kepemimpinan",
    "D2": "Kesiapan Data",
    "D3": "Infrastruktur & Teknologi",
    "D4": "Digitalisasi Proses",
    "D5": "Organisasi & Budaya",
    "D6": "SDM & Keterampilan",
    "D7": "Tata Kelola, Keamanan & Kepatuhan",
    "D8": "Anggaran & Finansial",
}


# ---------------------------------------------------------------- catatan klien
def catat(pengirim: str | None, h: dict, cap: str) -> bool:
    """Tambah satu baris ke client_register.csv.

    Identitas v2 (bisnis/kontak/pengisi/jenis) ikut disimpan bila ada, agar data
    yang dikumpulkan situs tidak hilang. Idempoten per (identitas, hari) berbasis
    KOLOM — bukan pencocokan substring yang bisa salah tangkap. Tetap kompatibel
    dengan baris lama (7 kolom yang sama; kolom kosong tidak apa-apa).
    """
    ident = h.get("identitas") or {}
    bisnis = (ident.get("bisnis") or "").strip()
    kontak = (ident.get("kontak") or "").strip()
    pengisi = (ident.get("pengisi") or "").strip()
    jenis = (ident.get("jenis") or "").strip()

    # Kunci identitas: kontak yang diketik pengunjung (v2) -> fallback nomor pengirim.
    kunci = kontak or (pengirim or "")

    ada_kepala = REGISTER.exists() and REGISTER.stat().st_size > 0
    if REGISTER.exists() and kunci:
        try:
            with REGISTER.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    if (row.get("tanggal") == cap
                            and (row.get("nomor") or "").strip() == kunci):
                        return False  # sudah tercatat hari ini untuk identitas ini
        except Exception:
            pass  # berkas lama/rusak tidak boleh menghentikan pencatatan

    catatan = "penilaian situs, skor {:.1f}% {}".format(
        h["skor_hitung_ulang"], h["band"])
    if pengisi:
        catatan += ", pengisi " + pengisi
    if h["catatan_situs"]:
        catatan += ", perlu ditinjau " + h["catatan_situs"]

    with REGISTER.open("a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if not ada_kepala:
            w.writerow(["tanggal", "nama", "nomor", "tipe_bisnis",
                        "grup_jid", "status", "catatan"])
        # nama = nama bisnis; nomor = kontak (atau nomor pengirim); tipe = jenis usaha
        w.writerow([cap, bisnis, kontak or (pengirim or ""), jenis,
                    "dm", "penilaian-situs", catatan])
    return True


def kirim_grup(teks: str) -> tuple[bool, str]:
    """Kirim ke grup tim lewat hermes send (tanpa LLM)."""
    p = subprocess.run(["hermes", "send", "--to", GRUP_TIM, teks],
                       capture_output=True, text=True, timeout=120)
    ok = p.returncode == 0
    return ok, (p.stdout or p.stderr).strip()[-300:]


# ---------------------------------------------------------------- uji offline
CONTOH = "[PENILAIAN-SITUS v1]\nD1=4 D2=3 D3=5 D4=3 D5=2 D6=3 D7=3 D8=2\n" \
         "skor_situs=65.0 band=Layak Lanjut\nkeyakinan=D2:ragu,D8:tidak_tahu"
CONTOH_BENTROK = "[PENILAIAN-SITUS v1]\nD1=3 D2=5 D3=1 D4=3 D5=3 D6=3 D7=3 D8=3\n" \
                 "skor_situs=62.0 band=Layak Lanjut\ncatatan_situs=R1"


def uji() -> int:
    gagal = 0
    for nama, teks in (("normal", CONTOH), ("bentrok", CONTOH_BENTROK)):
        h = baca(teks)
        ok = h["dikenali"] and h["skor_hitung_ulang"] in (65.0, 62.0)
        gagal += 0 if ok else 1
        print(("OK   " if ok else "GAGAL") + "  " + nama +
              "  ->  {:.1f}% {}".format(h["skor_hitung_ulang"], h["band"]))
        print("  --- pesan tim ---")
        for b in pesan_tim(h, "628111222333", "2026-09-30").splitlines():
            print("  " + b)
        print("  --- draf balasan klien ---")
        for b in pesan_klien(h, "628111222333").splitlines():
            print("  " + b)
        print()
    h = baca("Halo, saya mau tanya harga")
    ok = h["dikenali"] is False
    gagal += 0 if ok else 1
    print(("OK   " if ok else "GAGAL") + "  bukan penilaian  ->  DIAM (kode keluar 1)")
    print("Uji offline selesai. Tidak ada yang dikirim ke WhatsApp." if not gagal
          else "ADA UJI GAGAL.")
    return 1 if gagal else 0


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--teks")
    p.add_argument("--pengirim", default=None)
    p.add_argument("--tanpa-kirim", action="store_true")
    p.add_argument("--tanpa-catat", action="store_true")
    p.add_argument("--uji", action="store_true")
    p.add_argument("--uji-kirim", action="store_true",
                   help="kirim SATU pesan uji ke grup tim (diberi label UJI, tidak dicatat)")
    a = p.parse_args()

    if a.uji:
        return uji()

    if a.uji_kirim:
        a.teks, a.pengirim, a.tanpa_catat = CONTOH, "628000000000 (uji)", True

    teks = a.teks if a.teks else sys.stdin.read()
    h = baca(teks)
    if not h["dikenali"]:
        print(json.dumps({"dikenali": False, "alasan": h.get("alasan")},
                         ensure_ascii=False))
        return 1

    cap = dt.date.today().isoformat()
    isi_tim = pesan_tim(h, a.pengirim, cap)
    if a.uji_kirim:
        isi_tim = ("[UJI JALUR — abaikan pesan ini]\n"
                   "Ini pesan uji otomatis jalur penilaian situs, bukan klien nyata.\n"
                   "Kalau pesan ini sampai, penerusan hasil penilaian ke grup tim berfungsi.\n"
                   "---\n" + isi_tim)

    dicatat = False if a.tanpa_catat else catat(a.pengirim, h, cap)
    kirim = {"dicoba": not a.tanpa_kirim, "ok": None, "keluaran": ""}
    if not a.tanpa_kirim:
        ok, kel = kirim_grup(isi_tim)
        kirim.update(ok=ok, keluaran=kel)

    print(json.dumps({
        "dikenali": True,
        "skor_hitung_ulang": h["skor_hitung_ulang"],
        "skor_klaim": h["skor_klaim"],
        "selisih": h["selisih"],
        "band": h["band"],
        "belum_pasti": h["belum_pasti"],
        "catatan_situs": h["catatan_situs"],
        "dimensi_bentrok": h.get("dimensi_bentrok", []),
        "ringkas": h["ringkas"],
        "dicatat_ke_register": dicatat,
        "terkirim_ke_tim": kirim,
        "pesan_klien": pesan_klien(h, a.pengirim),
        "pesan_tim": isi_tim,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
