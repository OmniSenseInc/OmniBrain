#!/usr/bin/env python3
"""cari_bg.py — cari background relevan untuk poster OmniSense dari Wikimedia Commons.

Aturan:
- Template & tata letak poster TETAP milik OmniSense; skrip ini hanya menyiapkan LAPISAN LATAR.
- Lisensi WAJIB aman untuk konten komersial: prioritas CC0 / Public Domain, lalu CC BY (wajib kredit).
  CC BY-SA & NC DITOLAK — poster promosi = karya turunan, share-alike/NC akan mengunci brand kita.
- Hasil unduhan disimpan di assets/bg/ bersama berkas .json berisi atribusi.

Pakai:
    python3 cari_bg.py "data center server room"            # cari & unduh kandidat terbaik
    python3 cari_bg.py "server room" --daftar 5             # lihat 5 kandidat dulu
    python3 cari_bg.py --json                               # cetak hasil sebagai JSON (untuk agen)
"""
import argparse
import json
import os
import sys
import urllib.parse
import urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
BG_DIR = os.path.join(BASE, "assets", "bg")
UA = {"User-Agent": "OmniSenseBot/1.0 (https://omnisense.id)"}

LISENSI_BEBAS = ("cc0", "public domain", "pd-", "pdm")                       # tanpa syarat
LISENSI_KREDIT = ("cc by 2.0", "cc by 3.0", "cc by 4.0")                    # wajib kredit, boleh komersial
LISENSI_TOLAK = ("nc", "nd", "fair use", "gfdl", "by-sa")                   # NC/ND/share-alike: JANGAN


def cari(kueri, jumlah=8):
    """Cari gambar (bukan PDF/SVG/ikon) di Commons, urut relevansi."""
    p = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": f"{kueri} filetype:bitmap", "gsrnamespace": "6", "gsrlimit": str(jumlah),
        "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
        data = json.loads(r.read())

    hasil = []
    for pg in (data.get("query", {}).get("pages") or {}).values():
        ii = (pg.get("imageinfo") or [{}])[0]
        md = ii.get("extmetadata", {})
        lisensi = (md.get("LicenseShortName") or {}).get("value", "?")
        w, h = ii.get("width") or 0, ii.get("height") or 0
        if (ii.get("mime") or "") not in ("image/jpeg", "image/png", "image/webp"):
            continue
        if w < 700 or h < 700:                       # cukup untuk poster 1080px (potret bisa lebih kecil)
            continue
        if any(t in lisensi.lower() for t in LISENSI_TOLAK):
            continue
        judul = (pg.get("title") or "").replace("File:", "")
        # buang ilustrasi/vektor/diagram — kita cari FOTO nyata
        judul_low = judul.lower()
        if any(t in judul_low for t in ("diagram", "illustration", "drawing", "vector",
                                        "logo", "icon", "map", "chart", "graph", "render",
                                        "clipart", "sketch", "poster", "banner")):
            continue
        hasil.append({
            "judul": judul,
            "url": ii.get("url"), "lebar": w, "tinggi": h,
            "lisensi": lisensi,
            "kredit": (md.get("Artist") or {}).get("value", ""),
            "halaman": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(pg.get("title", "")),
            "aman_komersial": any(t in lisensi.lower() for t in LISENSI_BEBAS + LISENSI_KREDIT),
            "wajib_kredit": any(t in lisensi.lower() for t in LISENSI_KREDIT),
            "foto": (ii.get("mime") == "image/jpeg"),   # JPEG = hampir pasti foto
        })
    # aman komersial dulu, lalu FOTO (jpeg) diutamakan, lalu paling besar
    hasil.sort(key=lambda x: (not x["aman_komersial"], not x["foto"], -min(x["lebar"], x["tinggi"])))
    return hasil


def unduh(item, nama):
    os.makedirs(BG_DIR, exist_ok=True)
    ext = os.path.splitext(urllib.parse.urlparse(item["url"]).path)[1] or ".jpg"
    jalur = os.path.join(BG_DIR, nama + ext)
    with urllib.request.urlopen(urllib.request.Request(item["url"], headers=UA), timeout=90) as r:
        blob = r.read()
    with open(jalur, "wb") as fh:
        fh.write(blob)
    meta = dict(item, berkas=jalur, byte=len(blob))
    with open(os.path.join(BG_DIR, nama + ".json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, ensure_ascii=False, indent=2)
    return meta


def main():
    p = argparse.ArgumentParser(description="Cari background relevan (Wikimedia Commons, lisensi aman)")
    p.add_argument("kueri", nargs="?", help="kata kunci latar, mis. 'data center server room'")
    p.add_argument("--daftar", type=int, default=0, help="cetak N kandidat, tidak mengunduh")
    p.add_argument("--jumlah", type=int, default=8, help="berapa kandidat dicari (default 8)")
    p.add_argument("--nama", default=None, help="nama berkas simpan (default: dari kueri)")
    p.add_argument("--pilih", type=int, default=0, help="unduh kandidat ke-N dari daftar (1-based)")
    p.add_argument("--json", action="store_true", help="cetak JSON (untuk dipakai agen)")
    a = p.parse_args()
    if not a.kueri:
        p.error("butuh kata kunci")

    hasil = cari(a.kueri, a.jumlah)
    if not hasil:
        print(json.dumps({"ok": False, "alasan": "tidak ada kandidat layak"}, ensure_ascii=False))
        return 1

    if a.daftar:
        if a.json:
            print(json.dumps(hasil[: a.daftar], ensure_ascii=False, indent=2))
        else:
            for i, it in enumerate(hasil[: a.daftar], 1):
                print(f"{i}. {it['judul'][:62]}")
                print(f"   {it['lebar']}x{it['tinggi']} | {it['lisensi']} | aman komersial: {it['aman_komersial']}")
        return 0

    nama = a.nama or "".join(c if c.isalnum() else "-" for c in a.kueri.lower())[:40].strip("-")
    idx = (a.pilih - 1) if a.pilih else 0
    if idx < 0 or idx >= len(hasil):
        idx = 0
    meta = unduh(hasil[idx], nama)
    if a.json:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(f"TERUNDUH: {meta['berkas']}")
        print(f"  {meta['judul'][:70]}")
        print(f"  {meta['lebar']}x{meta['tinggi']} | lisensi: {meta['lisensi']} | aman komersial: {meta['aman_komersial']}")
        if not meta["aman_komersial"]:
            print("  PERINGATAN: lisensi tidak aman untuk konten komersial — jangan dipakai")
    return 0


if __name__ == "__main__":
    sys.exit(main())
