#!/usr/bin/env bash
# deploy_privacy.sh — pasang halaman Kebijakan Privasi OmniSense ke server omnisense.id
# Pakai: dari mesin ini ->  scp privacy_policy_omnisense.html deploy_privacy.sh USER@168.231.118.144:/tmp/
#        lalu di server   ->  sudo bash /tmp/deploy_privacy.sh
# Aman: hanya menambah 1 berkas statis; tidak menyentuh konfigurasi/berkas lain.

set -euo pipefail

SRC="/tmp/privacy_policy_omnisense.html"
[ -f "$SRC" ] || { echo "ERROR: $SRC tidak ada. scp berkasnya dulu."; exit 1; }

echo "== 1. Cari document root untuk omnisense.id =="
ROOTS=$(grep -rhiE '^\s*root\s+' /etc/nginx/sites-enabled/ /etc/nginx/conf.d/ 2>/dev/null | awk '{print $2}' | tr -d ';' | sort -u)
if [ -z "$ROOTS" ]; then
  echo "Tidak ada directive 'root' di nginx. Kemungkinan situs dilayani app Node/Vite."
  echo "Cari manual:  grep -rn 'proxy_pass\|root\|server_name' /etc/nginx/sites-enabled/"
  exit 2
fi
printf 'Kandidat root:\n%s\n' "$ROOTS"

echo
echo "== 2. Cari root yang cocok dengan omnisense.id =="
TARGET=""
for f in /etc/nginx/sites-enabled/* /etc/nginx/conf.d/*; do
  [ -f "$f" ] || continue
  if grep -qiE 'omnisense\.id|neosense' "$f"; then
    R=$(grep -hiE '^\s*root\s+' "$f" | awk '{print $2}' | tr -d ';' | head -1)
    [ -n "$R" ] && { TARGET="$R"; echo "Cocok: $f  ->  root=$R"; break; }
  fi
done
[ -n "$TARGET" ] || { echo "Tidak ketemu root untuk omnisense.id. Cek manual blok server-nya."; exit 3; }

echo
echo "== 3. Salin halaman =="
mkdir -p "$TARGET/privacy"
cp -v "$SRC" "$TARGET/privacy.html"
cp -v "$SRC" "$TARGET/privacy/index.html"
echo "-> $TARGET/privacy.html  (dan /privacy/index.html)"

echo
echo "== 4. Uji konfigurasi & reload =="
nginx -t && systemctl reload nginx && echo "nginx reload OK"

echo
echo "== 5. Verifikasi dari dalam server =="
sleep 1
curl -s -o /dev/null -w "https://omnisense.id/privacy.html -> HTTP %{http_code} (%{content_type})\n" -L https://omnisense.id/privacy.html || true
curl -s -o /dev/null -w "https://omnisense.id/privacy/     -> HTTP %{http_code} (%{content_type})\n" -L https://omnisense.id/privacy/ || true

echo
echo "SELESAI. Kalau dua baris di atas HTTP 200 + text/html, isi di Meta:"
echo "  Privacy policy URL      : https://omnisense.id/privacy.html"
echo "  Terms of Service URL    : https://omnisense.id/privacy.html"
echo "  User Data Deletion      : Instructions URL -> https://omnisense.id/privacy.html"
