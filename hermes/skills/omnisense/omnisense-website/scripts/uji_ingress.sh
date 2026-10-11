#!/usr/bin/env bash
# Probe read-only keamanan ingress OmniSense. Tidak mengubah apa pun di server.
# Pakai: bash uji_ingress.sh [IP-ORIGIN]   (default: IP publik VPS)
set -u
ORIGIN_IP="${1:-$(curl -s --max-time 8 https://api.ipify.org)}"
DOMAIN=omnisense.my.id
R="--resolve $DOMAIN:443:$ORIGIN_IP"

echo "== origin IP: $ORIGIN_IP =="

echo; echo "== 1. header & protokol (via CDN) =="
curl -sI --max-time 12 "https://$DOMAIN/" | grep -iE "^(HTTP|content-security-policy|x-frame-options|strict-transport|referrer-policy)" | head

echo; echo "== 2. kebocoran berkas (harus 404) =="
for p in /approved-site.json /consultations.sqlite3 /.env /.git/config /.web-rate-key; do
  printf '%s  %s\n' "$(curl -s -o /dev/null -w '%{http_code}' --max-time 8 "https://$DOMAIN$p")" "$p"
done

echo; echo "== 3. origin langsung (200 = CDN bisa dilewati) =="
printf 'GET /            -> %s\n' "$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 $R "https://$DOMAIN/")"
printf 'GET / (Host jahat)-> %s\n' "$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 $R -H 'Host: evil.invalid' "https://$DOMAIN/")"

echo; echo "== 4. kunci limit TETAP (harus muncul 429 di ujung) =="
for i in $(seq 1 30); do
  curl -sk -o /dev/null -w '%{http_code} ' --max-time 8 $R \
    -H 'CF-Connecting-IP: 203.0.113.77' "https://$DOMAIN/api/consultation/session"
done; echo

echo; echo "== 5. kunci limit DIPUTAR (200 semua = batas per-pengunjung jebol) =="
for i in $(seq 1 30); do
  curl -sk -o /dev/null -w '%{http_code} ' --max-time 8 $R \
    -H "CF-Connecting-IP: 198.51.100.$i" "https://$DOMAIN/api/consultation/session"
done; echo

echo; echo "== 6. kontrol API (harus 403 / 405) =="
printf 'POST tanpa Origin   -> %s\n' "$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 $R -X POST "https://$DOMAIN/api/consultation/cases" -H 'Content-Type: application/json' -d '{}')"
printf 'POST Origin asing   -> %s\n' "$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 $R -X POST "https://$DOMAIN/api/consultation/cases" -H 'Origin: https://evil.invalid' -H 'Content-Type: application/json' -d '{}')"
printf 'DELETE              -> %s\n' "$(curl -sk -o /dev/null -w '%{http_code}' --max-time 10 $R -X DELETE "https://$DOMAIN/api/consultation/cases")"

echo; echo "== 7. listener lokal (app harus 127.0.0.1 saja) =="
ss -ltnp 2>/dev/null | grep -E ':8080|:80 |:443 ' || echo '(perlu hak akses untuk nama proses)'

echo; echo "== 8. SSH efektif =="
sudo -n sshd -T 2>/dev/null | grep -Ei '^(passwordauthentication|permitrootlogin|maxauthtries)' || echo '(sshd -T butuh sudo)'
sudo -n fail2ban-client status sshd 2>/dev/null | head -6

echo; echo "== 9. tunnel liar (trycloudflare) =="
ps aux 2>/dev/null | grep -i 'cloudflared' | grep -v grep || echo 'tidak ada cloudflared jalan'

echo; echo "== 10. izin DB konsultasi (harus 600) =="
stat -c '%A %U:%G %n' /home/ubuntu/ai-agency/consulting/data/*.sqlite3 2>/dev/null

echo; echo "== selesai: tidak ada perubahan yang dilakukan =="
