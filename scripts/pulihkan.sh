#!/usr/bin/env bash
# pulihkan.sh — Kembalikan OmniSense utuh di VPS baru dari repo GitHub + bundel.
#
# Jalankan dari dalam repo yang sudah di-clone (mis. ~/omnisense-brain):
#   MIGRASI_PASS='kata-sandi-bundel' bash scripts/pulihkan.sh
#
# Tahapan bisa dijalankan sebagian:  bash scripts/pulihkan.sh 5   (mulai dari tahap 5)
set -euo pipefail

STAGE_START="${1:-1}"
PASS="${MIGRASI_PASS:-}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${MIGRASI_WORK:-/home/ubuntu/migrasi}"
HOME_DIR="${MIGRASI_HOME:-/home/ubuntu}"   # boleh diarahkan untuk uji coba

# Sumber bundel: folder bundel di dalam repo (hasil clone), atau ~/migrasi/bundel
if [[ -n "${MIGRASI_BUNDEL:-}" ]]; then BUNDEL="$MIGRASI_BUNDEL"
elif ls "$ROOT/bundel"/*.part >/dev/null 2>&1; then BUNDEL="$ROOT/bundel"
else BUNDEL="$WORK/bundel"; fi
PLAIN="$WORK/isi"   # bundel yang sudah dibuka sandinya

say(){ printf '\n\033[1m== %s ==\033[0m\n' "$*"; }
step(){ local n="$1"; [[ "$n" -ge "$STAGE_START" ]] || return 1; say "TAHAP $n: $2"; }

say "OmniSense — pemulihan di VPS baru"
echo "Repo    : $ROOT"
echo "Bundel  : $BUNDEL"
echo "Hasil   : $PLAIN"
echo "Mulai   : tahap $STAGE_START"
[[ -n "$PASS" ]] || { echo "FATAL: set MIGRASI_PASS dulu"; exit 2; }

if step 1 "Buka bundel (periksa sidik jari, gabung bagian, buka sandi AES-256)"; then
  mkdir -p "$PLAIN"
  ( cd "$BUNDEL" && sha256sum -c SHA256SUMS --ignore-missing --quiet ) \
    && echo "sidik jari bagian bundel: OK" || echo "PERINGATAN: ada bagian yang tidak cocok SHA256 — periksa dulu"
  # Gabungkan kembali bagian-bagian yang terpecah (kalau yang ada hanya *.part)
  for prefix in 01-hermes-home.zip 02-ai-agency-data.tar.gz 03-sistem.tar.gz \
                03-unit-user.tar.gz 03-hermes-code-custom.tar.gz 04-9router.tar.gz; do
    if ls "$BUNDEL/$prefix.enc."*.part >/dev/null 2>&1 && [[ ! -f "$BUNDEL/$prefix.enc" ]]; then
      cat "$BUNDEL/$prefix.enc."*.part > "$BUNDEL/$prefix.enc"
      echo "  gabung: $prefix.enc"
    fi
  done
  for f in "$BUNDEL"/*.enc; do
    [[ -e "$f" ]] || continue
    out="$PLAIN/$(basename "${f%.enc}")"
    [[ -f "$out" ]] && continue
    echo "  buka: $(basename "$f")"
    openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in "$f" -out "$out" -pass env:MIGRASI_PASS
  done
  ls -lh "$PLAIN" || true
fi

# Berhenti kalau bundel yang dibutuhkan tidak ada (jangan memulihkan setengah jalan)
require(){ [[ -f "$PLAIN/$1" ]] || { echo "FATAL: $1 tidak ada di $PLAIN — pemulihan dihentikan"; exit 3; }; }

if step 2 "Pasang Hermes (kalau belum ada)"; then
  if ! command -v hermes >/dev/null; then
    curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
    export PATH="$HOME/.local/bin:$PATH"
  fi
  hermes --version
fi

if step 3 "Kembalikan otak agent ke ~/.hermes"; then
  require 01-hermes-home.zip
  mkdir -p "$HOME_DIR/.hermes"
  unzip -o -q "$PLAIN/01-hermes-home.zip" -d "$HOME_DIR/.hermes"
  # GitHub = acuan untuk kode/skill/cron; timpa yang ada di repo
  rsync -a "$ROOT/hermes/config.yaml" "$HOME_DIR/.hermes/config.yaml"
  rsync -a --delete "$ROOT/hermes/skills/" "$HOME_DIR/.hermes/skills/"
  rsync -a --delete "$ROOT/hermes/memories/" "$HOME_DIR/.hermes/memories/"
  rsync -a --delete "$ROOT/hermes/plugins/" "$HOME_DIR/.hermes/plugins/"
  rsync -a --delete "$ROOT/hermes/scripts/" "$HOME_DIR/.hermes/scripts/"
  rsync -a "$ROOT/hermes/cron/jobs.json" "$HOME_DIR/.hermes/cron/jobs.json"
  # Izin ketat untuk berkas rahasia (zip tidak menyimpan permission)
  chmod 700 "$HOME_DIR/.hermes" "$HOME_DIR/.hermes/sessions" "$HOME_DIR/.hermes/whatsapp" "$HOME_DIR/.hermes/cron" 2>/dev/null || true
  chmod 600 "$HOME_DIR/.hermes/.env" "$HOME_DIR/.hermes/auth.json" "$HOME_DIR/.hermes/state.db" \
            "$HOME_DIR/.hermes/cron/jobs.json" "$HOME_DIR/.hermes/config.yaml" 2>/dev/null || true
  rm -f "$HOME_DIR/.hermes"/*.lock "$HOME_DIR/.hermes/gateway.sock" "$HOME_DIR/.hermes/state/gateway.loop-tick."*.sock 2>/dev/null || true
  ls -la "$HOME_DIR/.hermes" | head -12
fi

if step 4 "Kembalikan ai-agency (data bisnis, konsultasi, website, konten)"; then
  require 02-ai-agency-data.tar.gz
  tar xzf "$PLAIN/02-ai-agency-data.tar.gz" -C "$HOME_DIR"
  chmod 700 "$HOME_DIR/ai-agency/consulting/data" 2>/dev/null || true
  chmod 600 "$HOME_DIR/ai-agency/consulting/data/"*.sqlite3 2>/dev/null || true
  chmod 600 "$HOME_DIR/ai-agency/ig_token.env" 2>/dev/null || true
  du -sh "$HOME_DIR/ai-agency"
fi

if step 5 "Kembalikan lapisan sistem (nginx, SSL, systemd, ops) + kode kustom Hermes"; then
  require 03-sistem.tar.gz
  sudo tar xzf "$PLAIN/03-sistem.tar.gz" -C /
  sudo mkdir -p /srv/omnisense-web /var/lib/omnisense-web /var/lib/omnisense-ops /var/backups/omnisense-encrypted
  if [[ -f "$PLAIN/03-hermes-code-custom.tar.gz" ]]; then
    tar xzf "$PLAIN/03-hermes-code-custom.tar.gz" -C "$WORK"
    cp -a "$WORK/hermes-code-custom/gateway/"*.py "$HOME_DIR/.hermes/hermes-agent/gateway/" 2>/dev/null || true
    ( cd "$HOME_DIR/.hermes/hermes-agent" && git apply "$WORK/hermes-code-custom/patch.diff" 2>/dev/null \
      && echo "patch kode gateway diterapkan" ) || echo "catatan: patch dilewati (versi kode berbeda); berkas custom tetap dipasang"
  fi
  sudo systemctl daemon-reload
  echo "unit sistem terpasang:"; ls /etc/systemd/system/ | grep omnisense || true
fi

if step 6 "Bangun ulang venv + pasang paket"; then
  sudo apt-get update -qq
  command -v nginx >/dev/null || sudo apt-get install -y -qq nginx
  command -v fail2ban-server >/dev/null || sudo apt-get install -y -qq fail2ban
  command -v certbot >/dev/null || sudo apt-get install -y -qq certbot python3-certbot-nginx
  if [[ -s "$PLAIN/03-pip-freeze-web.txt" ]]; then
    sudo python3 -m venv /opt/omnisense-web/venv
    sudo /opt/omnisense-web/venv/bin/pip install -q -r "$PLAIN/03-pip-freeze-web.txt" || true
  fi
  if [[ -s "$PLAIN/03-pip-freeze-agency.txt" ]]; then
    python3 -m venv "$HOME_DIR/ai-agency/.venv"
    "$HOME_DIR/ai-agency/.venv/bin/python" -m pip install -q -r "$PLAIN/03-pip-freeze-agency.txt" || true
  fi
fi

if step 7 "Pasang firewall (UFW) + fail2ban"; then
  sudo ufw --force reset >/dev/null
  sudo ufw default deny incoming >/dev/null
  sudo ufw default allow outgoing >/dev/null
  sudo ufw limit 22/tcp comment 'OmniSense SSH rate limit' >/dev/null
  for net in $(grep -oE '^[0-9.]+/[0-9]+' "$PLAIN/03-ufw-rules.txt" 2>/dev/null | sort -u); do
    sudo ufw allow from "$net" to any port 80,443 proto tcp comment 'OmniSense Cloudflare web' >/dev/null
  done
  sudo ufw --force enable >/dev/null
  sudo systemctl enable --now fail2ban >/dev/null 2>&1 || true
  sudo ufw status verbose | head -8
fi

if step 8 "Pasang 9router (router model lokal) — opsional"; then
  tar xzf "$PLAIN/04-9router.tar.gz" -C "$HOME_DIR"
  npm i -g 9router@0.5.99 better-sqlite3 sql.js systray2 pm2 @xdevplatform/xurl 2>&1 | tail -3
  mkdir -p "$HOME_DIR/.9router/bin"
  curl -fsSL -o "$HOME_DIR/.9router/bin/cloudflared" \
    https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
  chmod +x "$HOME_DIR/.9router/bin/cloudflared"
  echo "jalankan 9router: tmux new -s 9router lalu ketik 9router"
fi

if step 9 "Nyalakan layanan"; then
  sudo systemctl enable --now nginx omnisense-secure-web.service >/dev/null 2>&1 || true
  sudo systemctl enable --now omnisense-backup.timer omnisense-monitor.timer omnisense-review-sync.timer >/dev/null 2>&1 || true
  mkdir -p "$HOME_DIR/.config/systemd/user"
  systemctl --user daemon-reload
  systemctl --user enable --now hermes-gateway.service >/dev/null 2>&1 || true
  sudo loginctl enable-linger ubuntu >/dev/null 2>&1 || true
fi

if step 10 "Verifikasi"; then
  echo "--- status layanan ---"
  systemctl is-active nginx omnisense-secure-web.service || true
  systemctl --user is-active hermes-gateway.service || true
  echo "--- website (lokal) ---"
  curl -sS -o /dev/null -w 'localhost:8080 -> %{http_code}\n' http://127.0.0.1:8080/ || true
  echo "--- otak agent ---"
  hermes status 2>&1 | head -12 || true
  echo "--- cron ---"
  hermes cron list 2>&1 | head -15 || true
  echo "--- riwayat sesi ---"
  python3 - <<'EOF' || true
import sqlite3
c=sqlite3.connect('file:/home/ubuntu/.hermes/state.db?mode=ro',uri=True)
print("sesi:", c.execute("select count(*) from sessions").fetchone()[0],
      "| pesan:", c.execute("select count(*) from messages").fetchone()[0])
EOF
fi

say "SELESAI — langkah manual yang tersisa"
cat <<'TXT'
1) WhatsApp : systemctl --user restart hermes-gateway ; cek log. Kalau diminta,
              scan QR: hermes whatsapp (sesi hasil restore biasanya langsung jalan).
2) Cloudflare: arahkan record A omnisense.my.id ke IP VPS baru (proxied ON).
3) SSL       : sudo certbot renew --dry-run  (sertifikat hasil restore biasanya sudah valid)
4) Uji       : kirim pesan tes dari WhatsApp, cek grup, cek IG auto-post sekali manual
              (cd ~/ai-agency && python3 ig_queue.py status).
TXT
