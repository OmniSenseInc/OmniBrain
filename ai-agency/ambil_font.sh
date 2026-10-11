#!/usr/bin/env bash
# Ambil file font TTF dari Google Fonts (via CSS API dengan UA lama -> dapat TTF).
# Pakai: bash ambil_font.sh <keluarga-slug> <keluarga-google> <berat...>
set -u
slug="$1"; fam="$2"; shift 2
out="/tmp/fontuji"
mkdir -p "$out"
for w in "$@"; do
  url=$(curl -s -A "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)" \
        "https://fonts.googleapis.com/css?family=${fam}:${w}" | grep -oE "https://fonts\.gstatic\.com/[^)]+" | head -1)
  if [ -z "$url" ]; then echo "GAGAL cari url: $fam $w"; continue; fi
  f="$out/${slug}-${w}.ttf"
  curl -sL -o "$f" "$url"
  echo "$slug-$w -> $(stat -c%s "$f") bytes, $(file -b "$f" | cut -c1-30)"
done
