#!/usr/bin/env python3
"""
siapkan_foto.py — pilih & siapkan foto untuk poster "hero news" OmniSense.

Dua mode (otomatis pilih berdasar argumen):
  --tokoh   "Dario Amodei"        foto ORANG -> di-cutout (latar dihapus), tampil besar
  --suasana "data center server"  foto SUASANA/objek -> mode panel (latar penuh, digelapkan)

Aturan: HANYA pakai foto lisensi aman komersial (CC0/PD/CC BY) dari Wikimedia Commons
(dipakai ulang dari cari_bg.py). Kalau tidak ketemu -> keluar dengan kode 1 (jangan maksa).

Output: cetak JSON {ok, mode, berkas, siap, lisensi, kredit, halaman, judul}
  - mode=cutout : berkas = PNG transparan siap tempel
  - mode=panel  : berkas = JPG siap jadi latar panel

Pakai:
  .venv/bin/python siapkan_foto.py --tokoh "Sam Altman" --nama openai-sam
  .venv/bin/python siapkan_foto.py --suasana "data center server room" --nama ai-datacenter
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE, "assets", "bg")
VENV_PY = os.path.join(BASE, ".venv", "bin", "python")
PY = VENV_PY if os.path.exists(VENV_PY) else sys.executable


def slug(s: str) -> str:
    return "".join(c if c.isalnum() else "-" for c in s.lower()).strip("-")[:44]


def cari_unduh(kueri: str, nama: str, potret: bool = False):
    """Cari & unduh foto terbaik (lisensi aman) dari Commons. Return meta atau None.
    potret=True -> utamakan foto POTRET satu orang (hindari foto grup/berdua)."""
    r = subprocess.run([PY, os.path.join(BASE, "cari_bg.py"), kueri, "--daftar", "8", "--json"],
                       capture_output=True, text=True, timeout=120)
    out = (r.stdout or "").strip()
    if not out:
        return None
    try:
        kandidat = json.loads(out)
    except Exception:
        return None
    if not isinstance(kandidat, list) or not kandidat:
        return None

    if potret:
        # hindari judul yang menandakan banyak orang / acara / pertemuan
        tolak = ("with ", " and ", "meeting", "summit", "conference", "panel", "group",
                 "delegation", "visit", "handshake", "ceremony", "signing", "photo")
        skor = []
        for k in kandidat:
            jl = k.get("judul", "").lower()
            penalti = sum(1 for t in tolak if t in jl)
            # "cropped"/"portrait" biasanya potret tunggal -> bonus
            bonus = 1 if ("portrait" in jl or "cropped" in jl) else 0
            skor.append((penalti - bonus, -min(k["lebar"], k["tinggi"]), k))
        skor.sort(key=lambda x: (x[0], x[1]))
        urut = [s[2] for s in skor]
    else:
        urut = kandidat

    for meta in urut:
        if not meta.get("aman_komersial"):
            continue
        # unduh kandidat ini
        r2 = subprocess.run([PY, os.path.join(BASE, "cari_bg.py"), kueri, "--nama", nama,
                             "--pilih", str(kandidat.index(meta) + 1), "--json"],
                            capture_output=True, text=True, timeout=120)
        try:
            hasil = json.loads((r2.stdout or "").strip())
            if hasil.get("aman_komersial"):
                return hasil
        except Exception:
            continue
    return None


def cutout(masuk: str, keluar: str) -> bool:
    r = subprocess.run([PY, os.path.join(BASE, "cutout.py"), masuk, keluar, "--ulang"],
                       capture_output=True, text=True, timeout=400)
    return r.returncode == 0 and os.path.exists(keluar)


def main():
    ap = argparse.ArgumentParser(description="Siapkan foto poster hero-news (tokoh cutout / suasana panel).")
    ap.add_argument("--tokoh", help="nama orang/pejabat untuk cutout (mis. 'Sam Altman')")
    ap.add_argument("--suasana", help="kata kunci suasana/objek (mis. 'data center server room')")
    ap.add_argument("--nama", default=None, help="slug nama berkas")
    ap.add_argument("--kredit-json", default=None, help="tulis meta ke file ini (opsional)")
    a = ap.parse_args()

    if not a.tokoh and not a.suasana:
        print(json.dumps({"ok": False, "alasan": "butuh --tokoh atau --suasana"}, ensure_ascii=False))
        return 2

    if a.tokoh:
        nama = a.nama or slug(a.tokoh)
        # coba beberapa variasi kueri (nama saja kadang kosong; tambah konteks membantu)
        variasi = [a.tokoh]
        kata = a.tokoh.split()
        if len(kata) >= 2:
            variasi.append(" ".join(kata[:2]))          # mis. "Jensen Huang"
        if len(kata) >= 3:
            variasi.append(" ".join(kata[:3]))
        meta = None
        for v in variasi:
            meta = cari_unduh(v, nama, potret=True)
            if meta:
                break
        if not meta:
            print(json.dumps({"ok": False, "alasan": f"tidak ada foto aman untuk tokoh '{a.tokoh}'"},
                             ensure_ascii=False))
            return 1
        masuk = meta["berkas"]
        keluar = os.path.splitext(masuk)[0] + "-cut.png"
        if not os.path.exists(keluar):
            if not cutout(masuk, keluar):
                # cutout gagal -> pakai mode panel saja
                hasil = {"ok": True, "mode": "panel", "berkas": masuk, "siap": masuk,
                         "lisensi": meta["lisensi"], "kredit": meta.get("kredit", ""),
                         "halaman": meta.get("halaman", ""), "judul": meta.get("judul", ""),
                         "catatan": "cutout gagal, jatuh ke panel"}
                print(json.dumps(hasil, ensure_ascii=False, indent=2))
                return 0
        hasil = {"ok": True, "mode": "cutout", "berkas": masuk, "siap": keluar,
                 "lisensi": meta["lisensi"], "kredit": meta.get("kredit", ""),
                 "halaman": meta.get("halaman", ""), "judul": meta.get("judul", "")}
    else:
        nama = a.nama or slug(a.suasana)
        meta = cari_unduh(a.suasana, nama)
        if not meta:
            print(json.dumps({"ok": False, "alasan": f"tidak ada foto aman untuk '{a.suasana}'"},
                             ensure_ascii=False))
            return 1
        hasil = {"ok": True, "mode": "panel", "berkas": meta["berkas"], "siap": meta["berkas"],
                 "lisensi": meta["lisensi"], "kredit": meta.get("kredit", ""),
                 "halaman": meta.get("halaman", ""), "judul": meta.get("judul", "")}

    if a.kredit_json:
        with open(a.kredit_json, "w", encoding="utf-8") as fh:
            json.dump(hasil, fh, ensure_ascii=False, indent=2)
    print(json.dumps(hasil, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
