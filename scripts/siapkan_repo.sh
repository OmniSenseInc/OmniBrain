#!/usr/bin/env bash
# siapkan_repo.sh — Susun isi repo GitHub "otak OmniSense" di /home/ubuntu/migrasi/repo
#
# Prinsip: repo GitHub = kode + konfigurasi + dokumen + skill + cron + website.
# Rahasia, database klien, riwayat chat, dan aset besar TIDAK masuk repo
# (semuanya sudah ada di bundel terenkripsi).
set -euo pipefail

REPO="/home/ubuntu/migrasi/repo"
BASE="/home/ubuntu/migrasi"
SRC_AGENCY="/home/ubuntu/ai-agency"
SRC_HERMES="/home/ubuntu/.hermes"

rm -rf "$REPO"; mkdir -p "$REPO/ai-agency" "$REPO/hermes"

echo "[1/3] Salin ai-agency (tanpa rahasia, .venv, aset besar, cache) ..."
rsync -a --delete \
  --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc' \
  --exclude='.git/' \
  --exclude='backups/' --exclude='staging/' \
  --exclude='assets/' --exclude='referensi/' \
  --exclude='website/pratinjau/' \
  --exclude='*.env' --exclude='.env*' \
  --exclude='ig_token.env' --exclude='.telegraph_privacy_token.txt' \
  --exclude='*.sqlite3' --exclude='*.sqlite3-wal' --exclude='*.sqlite3-shm' \
  --exclude='*.zip' --exclude='*.log' --exclude='.preview_tunnel.log' \
  --exclude='*.png' --exclude='*.jpg' --exclude='*.jpeg' --exclude='*.mp4' \
  --exclude='client_register.csv' \
  "$SRC_AGENCY/" "$REPO/ai-agency/"

echo "[2/3] Salin inti Hermes (tanpa rahasia & sesi) ..."
mkdir -p "$REPO/hermes"
cp -a "$SRC_HERMES/config.yaml" "$REPO/hermes/config.yaml"
cp -a "$SRC_HERMES/SOUL.md" "$REPO/hermes/SOUL.md" 2>/dev/null || true
rsync -a --delete "$SRC_HERMES/skills/" "$REPO/hermes/skills/" \
  --exclude='.curator_backups/' --exclude='.curator_ledger.jsonl' --exclude='.usage.json'
rsync -a --delete "$SRC_HERMES/memories/" "$REPO/hermes/memories/"
rsync -a --delete "$SRC_HERMES/plugins/" "$REPO/hermes/plugins/" --exclude='__pycache__/' --exclude='security-state/'
rsync -a --delete "$SRC_HERMES/scripts/" "$REPO/hermes/scripts/" --exclude='__pycache__/'
mkdir -p "$REPO/hermes/cron"
cp -a "$SRC_HERMES"/cron/jobs.json "$REPO/hermes/cron/" 2>/dev/null || true
cp -a "$SRC_HERMES"/cron/jobs.json.bak_* "$REPO/hermes/cron/" 2>/dev/null || true
cp -a "$SRC_HERMES"/cron/notepad.db "$REPO/hermes/cron/" 2>/dev/null || true
mkdir -p "$REPO/hermes/code-custom"
cp -a "$BASE/hermes-code-custom/." "$REPO/hermes/code-custom/" 2>/dev/null || true

echo "[3/3] Tulis penjaga rahasia + README repo ..."
cat > "$REPO/.gitignore" <<'EOF'
# Rahasia & data pribadi TIDAK pernah masuk repo
.env
*.env
.env.*
**/ig_token.env
**/.telegraph_privacy_token.txt
*.sqlite3
*.sqlite3-wal
*.sqlite3-shm
state.db*
auth.json
whatsapp/session/
**/*.pem
**/*.key
**/credentials*
# Besar / bisa dipasang ulang
.venv/
node_modules/
__pycache__/
*.pyc
backups/
*.zip
*.tar.gz
*.enc
*.part
!bundel/*.part
!bundel/SHA256SUMS
*.log
EOF

echo "[4/4] Salin skrip migrasi + dokumen + bundel terenkripsi ..."
mkdir -p "$REPO/scripts" "$REPO/bundel"
cp -f "$BASE"/buat_bundel.sh "$BASE"/siapkan_repo.sh "$BASE"/pulihkan.sh "$BASE"/push_github.sh "$REPO/scripts/"
cp -f "$BASE"/README_MIGRASI.md "$REPO/README.md"
cp -f "$BASE"/README_MIGRASI.md "$REPO/scripts/"
[[ -f "$BASE/STATUS_MIGRASI.md" ]] && cp -f "$BASE/STATUS_MIGRASI.md" "$REPO/"
if ls "$BASE/bundel"/*.part >/dev/null 2>&1; then
  cp -f "$BASE/bundel"/*.part "$BASE/bundel/SHA256SUMS" "$BASE/bundel/MANIFEST.txt" "$REPO/bundel/"
  echo "  bundel: $(ls "$REPO/bundel"/*.part | wc -l) bagian"
else
  echo "  (belum ada bundel — jalankan buat_bundel.sh dulu)"
fi
# Keadaan sistem (ufw/iptables/apt/pip/versi) TIDAK ikut terenkripsi, jadi harus
# disalin terpisah. Tanpa 03-ufw-rules.txt, pemulihan di VPS baru akan mengunci 80/443.
if ls "$BASE/bundel"/03-*.txt >/dev/null 2>&1; then
  cp -f "$BASE/bundel"/03-*.txt "$REPO/bundel/"
  echo "  keadaan sistem: $(ls "$REPO/bundel"/03-*.txt | wc -l) berkas"
else
  echo "  PERINGATAN: tidak ada berkas 03-*.txt di bundel — jalankan buat_bundel.sh dulu"
fi

du -sh "$REPO"/* 2>/dev/null ; echo; echo "Jumlah berkas repo: $(find "$REPO" -type f -not -path '*/.git/*' | wc -l)"
