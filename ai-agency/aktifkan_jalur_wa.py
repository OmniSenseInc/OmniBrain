#!/usr/bin/env python3
"""Buka jalur DM untuk hasil penilaian situs, TANPA membuka bot jadi tukang balas.

Masalah: WHATSAPP_DM_POLICY=allowlist + WHATSAPP_ALLOWED_USERS hanya berisi nomor
tim, jadi pesan dari calon klien (nomor luar) TIDAK pernah sampai ke Hermes.
Akibatnya tombol kirim di situs mengirim pesan ke ruang kosong.

Skrip ini mengubah DUA baris di /home/ubuntu/.hermes/.env:
  WHATSAPP_DM_POLICY=open
  WHATSAPP_ALLOW_ALL_USERS=true
lalu mencadangkan .env sebelum menyentuh apa pun.

Isolasi tetap terjaga di lapisan peran (skill omnisense-consultant):
hanya DM yang diawali penanda [PENILAIAN-SITUS v1] yang dijawab; DM lain diam.
Jadi membuka policy TIDAK sama dengan membuat bot membalas semua orang.

Pakai:
  python3 aktifkan_jalur_wa.py            # lihat rencana, tidak mengubah apa pun
  python3 aktifkan_jalur_wa.py --terapkan # tulis perubahan (cadangan otomatis)
  python3 aktifkan_jalur_wa.py --kembalikan
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import shutil
import sys

ENV = pathlib.Path("/home/ubuntu/.hermes/.env")
KUNCI = {
    "WHATSAPP_DM_POLICY": "open",
    "WHATSAPP_ALLOW_ALL_USERS": "true",
}
NOMOR_TIM = "6281803474609,6281332005165,6289667020507,6281229012230"


def baca() -> list[str]:
    if not ENV.exists():
        sys.exit(f"tidak ada {ENV}")
    return ENV.read_text(encoding="utf-8").splitlines(keepends=True)


def nilai_saat_ini(baris: list[str], kunci: str) -> str:
    awalan = kunci + "="
    for b in baris:
        if b.startswith(awalan):
            return b.split("=", 1)[1].strip()
    return "(tidak ada)"


def terapkan(baris: list[str]) -> tuple[list[str], list[str]]:
    hasil, ubah = [], []
    terlihat: set[str] = set()
    for b in baris:
        cocok = next((k for k in KUNCI if b.startswith(k + "=")), None)
        if cocok:
            baru = f"{cocok}={KUNCI[cocok]}\n"
            if b != baru:
                ubah.append(f"  {cocok}: {b.strip().split('=',1)[1]} -> {KUNCI[cocok]}")
            hasil.append(baru)
            terlihat.add(cocok)
        else:
            hasil.append(b)
    for k, v in KUNCI.items():
        if k not in terlihat:
            hasil.append(f"{k}={v}\n")
            ubah.append(f"  {k}: (ditambahkan) -> {v}")
    return hasil, ubah


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--terapkan", action="store_true")
    p.add_argument("--kembalikan", action="store_true")
    a = p.parse_args()

    if a.kembalikan:
        cad = sorted(ENV.parent.glob(".env.cadangan-jalur-wa-*"))
        if not cad:
            sys.exit("tidak ada cadangan .env.cadangan-jalur-wa-*")
        shutil.copy2(cad[-1], ENV)
        print(f"dipulihkan dari {cad[-1].name}")
        print("JANGAN LUPA: restart gateway agar berlaku (lihat catatan di bawah).")
        return 0

    baris = baca()
    print("Setelan sekarang:")
    for k in KUNCI:
        print(f"  {k}={nilai_saat_ini(baris, k)}")
    print(f"  WHATSAPP_ALLOWED_USERS={nilai_saat_ini(baris, 'WHATSAPP_ALLOWED_USERS')}")
    print(f"\nNomor tim tetap diizinkan tanpa bergantung pada policy: {NOMOR_TIM}")

    baru, ubah = terapkan(baris)
    if not ubah:
        print("\nTidak ada yang perlu diubah — jalur sudah terbuka.")
        return 0
    print("\nPerubahan yang akan ditulis:")
    print("\n".join(ubah))

    if not a.terapkan:
        print("\n(uji-coba; tidak ada yang ditulis). Jalankan dengan --terapkan untuk menulis.")
        return 0

    cap = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    cadangan = ENV.with_name(f".env.cadangan-jalur-wa-{cap}")
    shutil.copy2(ENV, cadangan)
    ENV.write_text("".join(baru), encoding="utf-8")
    print(f"\nDitulis. Cadangan: {cadangan.name}")

    print(
        "\nLangkah wajib berikutnya (butuh keputusanmu, jangan otomatis):\n"
        "  systemctl --user restart hermes-gateway   # atau cara kamu menjalankan gateway\n"
        "  # atau dari WhatsApp, kirim: /reload-skills\n"
        "Restart memutus percakapan yang sedang berjalan — lakukan saat sepi.\n"
        "Kembalikan kapan saja: python3 aktifkan_jalur_wa.py --kembalikan"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
