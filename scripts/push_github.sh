#!/usr/bin/env bash
# push_github.sh — Unggah otak OmniSense ke GitHub (repo privat).
#
# Pakai:
#   GITHUB_TOKEN=ghp_xxx GITHUB_REPO=akun/omnisense-brain bash push_github.sh
#
# Isi yang diunggah: kode + konfigurasi + skill + cron + website (repo/),
# dan bundel terenkripsi (repo/bundel/*.part). Token TIDAK disimpan di repo.
set -euo pipefail

BASE="/home/ubuntu/migrasi"
REPO="$BASE/repo"
BUNDEL="$BASE/bundel"
: "${GITHUB_TOKEN:?set GITHUB_TOKEN}"
: "${GITHUB_REPO:?set GITHUB_REPO, contoh: vincent/omnisense-brain}"

echo "[1/4] Susun isi repo dari sumber terkini ..."
bash "$BASE/siapkan_repo.sh" >/dev/null
cp "$BASE/README_MIGRASI.md" "$REPO/README.md"
mkdir -p "$REPO/scripts"
cp "$BASE/buat_bundel.sh" "$BASE/siapkan_repo.sh" "$BASE/pulihkan.sh" "$REPO/scripts/"

echo "[2/4] Salin bundel terenkripsi (bagian + sidik jari) ..."
mkdir -p "$REPO/bundel"
rm -f "$REPO/bundel"/*.enc 2>/dev/null || true   # jangan ikutkan bundel mentah (>100 MB, ditolak GitHub)
cp -f "$BUNDEL"/*.part "$REPO/bundel/"
cp -f "$BUNDEL/SHA256SUMS" "$BUNDEL/MANIFEST.txt" "$REPO/bundel/"
du -sh "$REPO" "$REPO/bundel"

echo "[3/4] Commit ..."
cd "$REPO"
[[ -d .git ]] || git init -q
git config user.email "omnisense@local"; git config user.name "OmniSense Agent"
git add -A
git commit -q -m "OmniSense brain + bundel migrasi ($(date -u +%Y-%m-%dT%H:%MZ))" || echo "(tidak ada perubahan baru)"
git branch -M main

echo "[4/4] Push ke $GITHUB_REPO ..."
git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" main --force
# simpan remote tanpa token (token tidak tertinggal di .git/config)
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/${GITHUB_REPO}.git"

echo "SELESAI. Verifikasi: https://github.com/${GITHUB_REPO}"
