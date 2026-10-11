#!/usr/bin/env python3
"""Kirim preview poster ID + EN ke grup home WhatsApp (satu MEDIA per pesan)."""
import subprocess
import sys
import time

FILES = [
    "/home/ubuntu/ai-agency/wa_msg_id.txt",
    "/home/ubuntu/ai-agency/wa_msg_en.txt",
]

for path in FILES:
    with open(path, encoding="utf-8") as fh:
        pesan = fh.read()
    print(f"--- kirim {path} ({len(pesan)} char)")
    hasil = subprocess.run(
        ["hermes", "send", "--to", "whatsapp", pesan],
        capture_output=True,
        text=True,
        timeout=180,
    )
    print("exit:", hasil.returncode)
    print("stdout:", (hasil.stdout or "").strip()[:1500])
    print("stderr:", (hasil.stderr or "").strip()[:1500])
    if hasil.returncode != 0:
        sys.exit(hasil.returncode)
    time.sleep(3)

print("SELESAI")
