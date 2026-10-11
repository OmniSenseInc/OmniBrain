#!/usr/bin/env python3
"""Cek apakah poster lolos filter media delivery cron (tidak dibuang diam-diam)."""
import sys

sys.path.insert(0, "/home/ubuntu/.hermes/hermes-agent")

from gateway.platforms.base import BasePlatformAdapter  # noqa: E402

paths = [
    "/home/ubuntu/ai-agency/konten_berita_id.png",
    "/home/ubuntu/ai-agency/konten_berita_en.png",
]
text = "uji\n" + "\n".join(f"MEDIA:{p}" for p in paths)
media, cleaned = BasePlatformAdapter.extract_media(text)
print("extract :", media)
kept = BasePlatformAdapter.filter_media_delivery_paths(media)
print("kept    :", kept)
print("dibuang :", [m for m in media if m not in kept])
