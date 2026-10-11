#!/usr/bin/env python3
"""
progress_tim.py — Pencatat progress tim OmniSense (Siklus 1).

CARA PAKAI SINGKAT
  python3 progress_tim.py init                      # bikin state awal (sekali saja)
  python3 progress_tim.py minta --pekan 1           # teks WA buat minta self-report Nathanael & Vincent
  python3 progress_tim.py add --orang Nathanael --pekan 1 --persen 40 --catatan "POS dasar jalan, stok belum"
  python3 progress_tim.py check --pekan 1 --item 3 --done    # tandai tugas Michael selesai (persen auto-hitung)
  python3 progress_tim.py angka --pekan 1 --must 1 --p0 0 --p1 2 --konten 2 --lead 1 --pilot 0
  python3 progress_tim.py status                    # lihat semua pekan
  python3 progress_tim.py status --pekan 2
  python3 progress_tim.py report --pekan 1          # tulis laporan pekan ke progress_pekan_1.md
  python3 progress_tim.py riwayat                   # tren persen tiap orang antar pekan

ATURAN:
  - Nathanael & Vincent: persen = PENILAIAN SENDIRI mereka (jangan ditakar oleh agent/Atong).
  - Michael (Atong): persen DIHITUNG OTOMATIS dari checklist berbobot di bawah.
  - Persen 0-100 per PEKAN, bukan per proyek.
"""

import argparse
import json
import os
import sys
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(BASE, "progress_tim.json")

# ---------------------------------------------------------------- definisi siklus
SIKLUS = "Siklus 1 (21 Sep - 18 Okt 2026)"
ORANG_SELF = ["Nathanael", "Vincent"]
ORANG_AUTO = "Michael"

PEKAN = {
    "1": {
        "periode": "Sen 21 - Min 27 Sep",
        "tema": "Data penjualan tersimpan terpusat (MUST-1)",
        "offline": "Sab 26 Sep 16:00",
        "online": "Rab 23 Sep 20:00 (A) & Jum 25 Sep 20:00 (B)",
    },
    "2": {
        "periode": "Sen 28 Sep - Min 4 Okt",
        "tema": "Satu laporan harian otomatis via WhatsApp (MUST-2)",
        "offline": "Min 4 Okt 19:30",
        "online": "Sel 29 Sep 20:00 (A) & Kam 1 Okt 20:00 (B)",
    },
    "3": {
        "periode": "Sen 5 - Min 11 Okt",
        "tema": "Cron stok + sekretaris 1 pertanyaan (MUST-3 & 4)",
        "offline": "Sab 10 Okt 16:00",
        "online": "Rab 7 Okt 20:00 (A) & Kam 8 Okt 20:00 (B)",
    },
    "4": {
        "periode": "Sen 12 - Min 18 Okt",
        "tema": "Hardening + siap beta (DoD fase7 6/6)",
        "offline": "Min 18 Okt 19:30",
        "online": "Sel 13 Okt 20:00 (A) & Kam 15 Okt 20:00 (B)",
    },
}

# checklist Michael per pekan (bobot total 100)
CHECKLIST_MICHAEL = {
    "1": [
        ("Bug board + skenario uji tertulis dipasang", 25),
        ("CRM lead diupdate (client_register.csv)", 15),
        ("Konten #1 (Sen 21 Sep) terpost + dicatat di log", 20),
        ("Konten #2 (Kam 24 Sep) terpost + dicatat di log", 20),
        ("Laporan bug pekanan lengkap (severity + bukti)", 20),
    ],
    "2": [
        ("Uji terima laporan WA: 3 skenario (tanggal salah, tanpa transaksi, transaksi banyak)", 30),
        ("Konten #1 terpost + dicatat di log", 20),
        ("Konten #2 terpost + dicatat di log", 20),
        ("Minimal 1 lead dari konten tercatat di CRM", 15),
        ("Ikut 3 pertemuan + kirim rangkuman/angka", 15),
    ],
    "3": [
        ("Uji sekretaris: data kosong & pertanyaan di luar scope (anti-halusinasi)", 30),
        ("Uji notifikasi stok muncul tanpa dipicu manual", 20),
        ("Konten #1 + #2 terpost + dicatat di log", 30),
        ("CRM + kalender pekan depan diupdate", 20),
    ],
    "4": [
        ("Checklist DoD fase7 6/6 diverifikasi dengan bukti", 35),
        ("Uji dari sisi orang awam (1 orang di luar tim)", 20),
        ("Materi pelatihan 1 halaman siap", 15),
        ("Konten #1 + #2 terpost + dicatat di log", 20),
        ("Minimal 3 calon kafe pilot dihubungi & tercatat", 10),
    ],
}


# ---------------------------------------------------------------- state
def state_baru():
    st = {"siklus": SIKLUS, "pekan": {}, "angka": {}}
    for p, info in PEKAN.items():
        st["pekan"][p] = {
            "periode": info["periode"],
            "tema": info["tema"],
            "orang": {
                ORANG_AUTO: {
                    "persen": 0,
                    "sumber": "auto",
                    "items": [
                        {"label": lbl, "bobot": bob, "selesai": False}
                        for lbl, bob in CHECKLIST_MICHAEL[p]
                    ],
                },
            },
        }
        for o in ORANG_SELF:
            st["pekan"][p]["orang"][o] = {"persen": None, "sumber": "self", "catatan": "", "diisi": None}
        st["angka"][p] = {"must": None, "p0": None, "p1": None, "konten": None, "lead": None, "pilot": None}
    return st


def muat():
    if not os.path.exists(STATE):
        st = state_baru()
        simpan(st)
        return st
    with open(STATE, encoding="utf-8") as f:
        return json.load(f)


def simpan(st):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=2, ensure_ascii=False)


def hitung_auto(orang):
    total = sum(i["bobot"] for i in orang["items"]) or 1
    dapat = sum(i["bobot"] for i in orang["items"] if i["selesai"])
    return round(dapat * 100 / total)


def auto_ada_isi(orang):
    return any(i["selesai"] for i in orang["items"])


def persen_orang(st, pekan, orang):
    o = st["pekan"][pekan]["orang"].get(orang)
    if not o:
        return None
    if o.get("sumber") == "auto":
        # belum ada satu pun tugas ditandai -> dianggap belum mulai, bukan 0%
        return hitung_auto(o) if auto_ada_isi(o) else None
    return o.get("persen")


# ---------------------------------------------------------------- perintah
def cmd_init(args):
    simpan(state_baru())
    print("State progress dibuat:", STATE)


def cmd_status(args):
    st = muat()
    pekan_list = [args.pekan] if args.pekan else list(PEKAN.keys())
    for p in pekan_list:
        info = st["pekan"][p]
        print("=" * 66)
        print(f"PEKAN {p} | {info['periode']} | {info['tema']}")
        print(f"  offline: {PEKAN[p]['offline']}   online: {PEKAN[p]['online']}")
        print("-" * 66)
        for o in [ORANG_SELF[0], ORANG_SELF[1], ORANG_AUTO]:
            data = info["orang"][o]
            pc = persen_orang(st, p, o)
            if data.get("sumber") == "auto":
                label = f"{pc}%" if pc is not None else "belum ada yang ditandai"
                print(f"  {o:<10} {label:>5}  (otomatis dari checklist)")
                for i, item in enumerate(data["items"], 1):
                    tanda = "[x]" if item["selesai"] else "[ ]"
                    print(f"      {tanda} {i}. {item['label']} ({item['bobot']}%)")
            else:
                if pc is None:
                    print(f"  {o:<10} {'--':>5}  BELUM LAPOR (self-report, tunggu dia sendiri)")
                else:
                    print(f"  {o:<10} {str(pc)+'%':>5}  (self-report {data.get('diisi','?')}) {data.get('catatan','')}")
        a = st["angka"][p]
        print("-" * 66)
        print(f"  angka: MUST selesai={a['must']} | bug P0={a['p0']} P1={a['p1']} | konten={a['konten']} "
              f"| lead={a['lead']} | calon pilot={a['pilot']}")
    print("=" * 66)


def cmd_add(args):
    st = muat()
    if args.pekan not in st["pekan"]:
        sys.exit(f"Pekan {args.pekan} tidak ada.")
    if args.orang == ORANG_AUTO:
        sys.exit(f"{ORANG_AUTO} dihitung otomatis — pakai `check`, bukan `add`.")
    if not 0 <= args.persen <= 100:
        sys.exit("Persen harus 0-100.")
    o = st["pekan"][args.pekan]["orang"][args.orang]
    o["persen"] = args.persen
    o["catatan"] = args.catatan or ""
    o["diisi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    simpan(st)
    print(f"Tersimpan: {args.orang} pekan {args.pekan} = {args.persen}% ({o['catatan']})")


def cmd_check(args):
    st = muat()
    items = st["pekan"][args.pekan]["orang"][ORANG_AUTO]["items"]
    if not 1 <= args.item <= len(items):
        sys.exit(f"Item harus 1-{len(items)} (lihat `status --pekan {args.pekan}`).")
    items[args.item - 1]["selesai"] = not args.undo
    simpan(st)
    pc = hitung_auto(st["pekan"][args.pekan]["orang"][ORANG_AUTO])
    tanda = "BATAL" if args.undo else "SELESAI"
    print(f"{tanda}: item {args.item} — {items[args.item-1]['label']}")
    print(f"Progress otomatis {ORANG_AUTO} pekan {args.pekan} sekarang: {pc}%")


def cmd_angka(args):
    st = muat()
    a = st["angka"][args.pekan]
    for k in ["must", "p0", "p1", "konten", "lead", "pilot"]:
        v = getattr(args, k)
        if v is not None:
            a[k] = v
    simpan(st)
    print(f"Angka pekan {args.pekan}: {a}")


def cmd_minta(args):
    p = args.pekan
    print("--- TEMPEL KE GRUP TIM (minta self-report) ---")
    print(f"Laporan pekan {p} ({PEKAN[p]['periode']}) — deadline sebelum offline {PEKAN[p]['offline']}.")
    print("Isi maksimal 5 baris, jangan lebih:")
    print("1) Selesai pekan ini: ...")
    print("2) Mandek + kenapa: ...")
    print("3) Rencana pekan depan: ...")
    print("4) PROGRESS versi gw sendiri: __% — alasan: ...")
    print("5) Butuh bantuan: ...")
    print("(Vincent tambah: PR yang di-review/merge + hasil eksplorasi MASUK/TUNDA)")
    print("--- END ---")


def cmd_report(args):
    st = muat()
    p = args.pekan
    info = st["pekan"][p]
    a = st["angka"][p]
    L = []
    L.append(f"# LAPORAN PROGRESS PEKAN {p} — {info['periode']}")
    L.append(f"Tema: {info['tema']}")
    L.append(f"Pertemuan: offline {PEKAN[p]['offline']} | online {PEKAN[p]['online']}")
    L.append("")
    L.append("## Persen progress")
    for o in [ORANG_SELF[0], ORANG_SELF[1], ORANG_AUTO]:
        pc = persen_orang(st, p, o)
        d = info["orang"][o]
        ket = d.get("catatan", "") if d.get("sumber") == "self" else "otomatis dari checklist"
        L.append(f"- {o}: {'belum lapor' if pc is None else str(pc)+'%'} ({ket})")
    L.append("")
    L.append("## Angka pekan")
    L.append(f"- Item MUST fase7 selesai: {a['must']}")
    L.append(f"- Bug P0: {a['p0']} | Bug P1: {a['p1']}")
    L.append(f"- Konten terpost: {a['konten']} | Lead dari konten: {a['lead']} | Calon pilot: {a['pilot']}")
    L.append("")
    L.append("## Checklist Michael (otomatis)")
    for i, item in enumerate(info["orang"][ORANG_AUTO]["items"], 1):
        L.append(f"- [{'x' if item['selesai'] else ' '}] {i}. {item['label']} ({item['bobot']}%)")
    out = os.path.join(BASE, f"progress_pekan_{p}.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    print(f"\nDitulis ke: {out}")


def cmd_riwayat(args):
    st = muat()
    orang = ORANG_SELF + [ORANG_AUTO]
    print(f"{'Orang':<11}" + "".join(f"{'P'+p:>8}" for p in PEKAN) + "   tren")
    for o in orang:
        row, vals = [], []
        for p in PEKAN:
            pc = persen_orang(st, p, o)
            vals.append(pc)
            row.append("--" if pc is None else f"{pc}%")
        bersih = [v for v in vals if v is not None]
        if len(bersih) >= 2:
            tren = "naik" if bersih[-1] > bersih[0] else ("turun" if bersih[-1] < bersih[0] else "datar")
        else:
            tren = "belum cukup data"
        print(f"{o:<11}" + "".join(f"{r:>8}" for r in row) + f"   {tren}")
    print("\nCatatan: angka Nathanael & Vincent = penilaian mereka sendiri. Yang dibaca tren + alasannya.")


def main():
    ap = argparse.ArgumentParser(description="Pencatat progress tim OmniSense")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help="bikin state awal"); s.set_defaults(func=cmd_init)

    s = sub.add_parser("status", help="lihat progress"); s.add_argument("--pekan"); s.set_defaults(func=cmd_status)

    s = sub.add_parser("add", help="catat self-report Nathanael/Vincent")
    s.add_argument("--orang", required=True, choices=ORANG_SELF)
    s.add_argument("--pekan", required=True)
    s.add_argument("--persen", type=int, required=True)
    s.add_argument("--catatan", default="")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("check", help="tandai tugas Michael selesai (persen auto)")
    s.add_argument("--pekan", required=True)
    s.add_argument("--item", type=int, required=True)
    s.add_argument("--done", action="store_true", help="(default: tandai selesai)")
    s.add_argument("--undo", action="store_true", help="batalkan tanda selesai")
    s.set_defaults(func=cmd_check)

    s = sub.add_parser("angka", help="catat 4 angka pekan")
    s.add_argument("--pekan", required=True)
    for k in ["must", "p0", "p1", "konten", "lead", "pilot"]:
        s.add_argument(f"--{k}", type=int)
    s.set_defaults(func=cmd_angka)

    s = sub.add_parser("minta", help="teks WA minta self-report")
    s.add_argument("--pekan", required=True); s.set_defaults(func=cmd_minta)

    s = sub.add_parser("report", help="tulis laporan pekan ke file")
    s.add_argument("--pekan", required=True); s.set_defaults(func=cmd_report)

    s = sub.add_parser("riwayat", help="tren persen antar pekan"); s.set_defaults(func=cmd_riwayat)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
