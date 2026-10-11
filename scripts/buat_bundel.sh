#!/usr/bin/env bash
# buat_bundel.sh — Bangun bundel migrasi OmniSense (VPS lama -> VPS baru).
#
# Menghasilkan, di $OUT:
#   01-hermes-home.zip            : otak agent (config, .env, memori, skill, cron, sesi, state.db, sesi WhatsApp)
#   02-ai-agency-data.tar.gz      : seluruh isi /home/ubuntu/ai-agency kecuali .venv & __pycache__
#   03-sistem.tar.gz              : nginx, SSL, systemd unit, fail2ban, /opt/omnisense-web, /opt/omnisense-ops
#   04-9router.tar.gz             : router model lokal (tanpa binary cloudflared)
#   03-ufw-rules.txt, 03-iptables.txt, 03-apt-manual.txt, 03-pip-freeze-*.txt : keadaan sistem
#   *.enc + *.part                : salinan terenkripsi (AES-256) yang aman diunggah ke GitHub
#   SHA256SUMS, MANIFEST.txt      : pemeriksaan utuh + daftar isi
#
# Pemakaian:  MIGRASI_PASS='kata-sandi-kuat' bash buat_bundel.sh
set -euo pipefail

BASE="/home/ubuntu/migrasi"
OUT="${BASE}/bundel"
PASS="${MIGRASI_PASS:-}"
HOST="$(hostname)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

if [[ -z "$PASS" ]]; then echo "FATAL: set MIGRASI_PASS dulu"; exit 2; fi
mkdir -p "$OUT"; rm -f "$OUT"/*.part "$OUT"/*.enc "$OUT/SHA256SUMS" 2>/dev/null || true
echo "== Mulai bundel $STAMP (host $HOST) =="

echo "[1/9] Backup Hermes (~/.hermes) ..."
hermes backup -o "$OUT/01-hermes-home.zip" 2>&1 | tail -6

echo "[2/9] Tar /home/ubuntu/ai-agency (tanpa .venv) ..."
tar czf "$OUT/02-ai-agency-data.tar.gz" \
  --exclude='ai-agency/.venv' --exclude='*/__pycache__' --exclude='*.pyc' \
  --warning=no-file-changed --ignore-failed-read \
  -C /home/ubuntu ai-agency

echo "[3/9] Tar lapisan sistem (butuh sudo) ..."
sudo tar czf "$OUT/03-sistem.tar.gz" --ignore-failed-read -C / \
  etc/nginx/sites-available/omnisense.conf \
  etc/nginx/sites-enabled/omnisense.conf \
  etc/nginx/conf.d/omnisense-trusted-proxy.conf \
  etc/letsencrypt \
  etc/fail2ban \
  etc/sudoers.d/90-cloud-init-users \
  opt/omnisense-web \
  opt/omnisense-ops \
  etc/systemd/system/omnisense-backup.service \
  etc/systemd/system/omnisense-backup.timer \
  etc/systemd/system/omnisense-monitor.service \
  etc/systemd/system/omnisense-monitor.timer \
  etc/systemd/system/omnisense-review-sync.service \
  etc/systemd/system/omnisense-review-sync.timer \
  etc/systemd/system/omnisense-secure-web.service \
  etc/systemd/system/omnisense-security-v3-stage.service \
  2>/dev/null || echo "  (catatan: sebagian berkas sistem tidak ada, dilewati)"
tar czf "$OUT/03-unit-user.tar.gz" -C /home/ubuntu .config/systemd/user 2>/dev/null || true

echo "[4/9] Tar 9router (tanpa binary cloudflared) ..."
tar czf "$OUT/04-9router.tar.gz" --exclude='.9router/bin' --exclude='.9router/runtime/node_modules' \
  -C /home/ubuntu .9router 2>/dev/null || true

echo "[5/9] Catat keadaan sistem ..."
sudo ufw status numbered > "$OUT/03-ufw-rules.txt" 2>&1 || true
# Penjaga: tanpa aturan web Cloudflare, pemulihan di VPS baru akan mengunci 80/443.
if ! grep -q 'OmniSense Cloudflare web' "$OUT/03-ufw-rules.txt"; then
  echo "  PERINGATAN: 03-ufw-rules.txt tidak memuat aturan 'OmniSense Cloudflare web'."
  echo "  Pemulihan nanti akan MEMBLOKIR 80/443. Pasang dulu aturan CF, lalu ulangi bundel."
fi
sudo iptables-save > "$OUT/03-iptables.txt" 2>&1 || true
apt-mark showmanual 2>/dev/null | sort > "$OUT/03-apt-manual.txt" || true
/opt/omnisense-web/venv/bin/pip freeze 2>/dev/null | sort > "$OUT/03-pip-freeze-web.txt" || true
{ /home/ubuntu/ai-agency/.venv/bin/python -m pip freeze 2>/dev/null \
  || /home/ubuntu/.hermes/bin/uv pip freeze --python /home/ubuntu/ai-agency/.venv/bin/python 2>/dev/null; } \
  | grep -v '^Using Python' | sort > "$OUT/03-pip-freeze-agency.txt" || true
/home/ubuntu/.hermes/hermes-agent/venv/bin/python -m pip freeze 2>/dev/null | sort > "$OUT/03-pip-freeze-hermes.txt" || true
# Perubahan lokal pada kode Hermes sendiri (policy admin WhatsApp, dll)
mkdir -p "$OUT/hermes-code-custom/gateway"
( cd /home/ubuntu/.hermes/hermes-agent && git diff HEAD -- gateway/ > "$OUT/hermes-code-custom/patch.diff" 2>/dev/null || true )
cp -a /home/ubuntu/.hermes/hermes-agent/gateway/authz_mixin.py \
      /home/ubuntu/.hermes/hermes-agent/gateway/omnisense_policy.py \
      "$OUT/hermes-code-custom/gateway/" 2>/dev/null || true
tar czf "$OUT/03-hermes-code-custom.tar.gz" -C "$OUT" hermes-code-custom 2>/dev/null || true
npm ls -g --depth=0 2>/dev/null > "$OUT/03-npm-global.txt" || true
python3 - <<'EOF' > "$OUT/03-versi.txt" 2>&1 || true
import platform, subprocess
print("python:", platform.python_version())
print("hermes:", subprocess.run(["hermes","--version"],capture_output=True,text=True).stdout.strip())
print("node:", subprocess.run(["node","--version"],capture_output=True,text=True).stdout.strip())
print("nginx:", subprocess.run(["nginx","-v"],capture_output=True,text=True).stderr.strip())
EOF

echo "[6/9] Enkripsi AES-256 (rahasia + riwayat + data klien) ..."
for f in "$OUT"/*.zip "$OUT"/*.tar.gz; do
  [[ -e "$f" ]] || continue
  openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -in "$f" -out "$f.enc" -pass env:MIGRASI_PASS
done

echo "[7/9] Pecah jadi bagian <95 MB (batas GitHub) ..."
for f in "$OUT"/*.enc; do
  [[ -e "$f" ]] || continue
  split -b 45m -d -a 3 --additional-suffix=".part" "$f" "$f."
done

echo "[8/9] Sidik jari (SHA256) ..."
( cd "$OUT" && sha256sum *.part > SHA256SUMS 2>/dev/null || true )

echo "[9/9] MANIFEST ..."
{
  echo "MANIFEST BUNDEL MIGRASI OMNISENSE"
  echo "Host asal : $HOST"
  echo "Dibuat    : $STAMP (UTC)"
  echo
  echo "== Isi =="
  ls -lh "$OUT" | awk '{print $5, $9}'
  echo
  echo "== Cara pakai di VPS baru =="
  echo "1) git clone <repo> && cd repo"
  echo "2) gabungkan bagian: cat *.part > bundel.enc"
  echo "3) buka sandi   : openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in bundel.enc -out bundel.zip -pass env:MIGRASI_PASS"
  echo "4) jalankan pulihkan.sh (lihat README_MIGRASI.md)"
} > "$OUT/MANIFEST.txt"

echo "== Selesai. Isi $OUT: =="
du -sh "$OUT"/* | sort -h
