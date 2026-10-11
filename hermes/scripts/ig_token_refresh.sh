#!/usr/bin/env bash
# Jaga token Instagram OmniSense tetap hidup (long-lived 60 hari).
# Refresh dilakukan kalau sisa masa berlaku < 15 hari. Exit != 0 kalau ada masalah
# supaya Hermes mengirim notifikasi kegagalan.
set -uo pipefail
cd /home/ubuntu/ai-agency || { echo "GAGAL: folder /home/ubuntu/ai-agency tidak ada"; exit 1; }

STATUS="$(python3 ig_token.py status 2>&1)"
if [ $? -ne 0 ]; then
  echo "MASALAH TOKEN IG: status tidak bisa dibaca / token tidak valid."
  echo "$STATUS"
  exit 1
fi

LEFT="$(printf '%s\n' "$STATUS" | grep -oE '\(~[0-9]+ hari lagi\)' | head -1 | grep -oE '[0-9]+')"
if [ -z "${LEFT:-}" ]; then
  echo "MASALAH TOKEN IG: tidak bisa membaca sisa hari dari status."
  echo "$STATUS"
  exit 1
fi

if [ "$LEFT" -lt 15 ]; then
  echo "Sisa $LEFT hari — menjalankan refresh..."
  if ! OUT="$(python3 ig_token.py refresh 2>&1)"; then
    echo "REFRESH TOKEN IG GAGAL (sisa $LEFT hari):"
    echo "$OUT"
    exit 1
  fi
  echo "$OUT"
  python3 ig_token.py status 2>&1 | grep -E 'expired|status API'
  echo "Token IG berhasil diperpanjang."
else
  echo "Token IG sehat: sisa $LEFT hari. Belum perlu refresh."
fi
