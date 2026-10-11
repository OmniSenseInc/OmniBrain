#!/usr/bin/env bash
# Watchdog API Instagram OmniSense — berbasis PERUBAHAN STATUS (bukan status mutlak).
# Diam kalau status sama seperti cek terakhir (biar tidak spam WA tiap 3 jam).
# Bersuara hanya saat status berubah:
#   ok -> blocked : peringatan, API baru saja diblokir (jangan retry publish berulang)
#   blocked -> ok : blokir lepas, antrean siap dipublikasikan (balas 'post')
set -uo pipefail
cd /home/ubuntu/ai-agency || exit 0

STATE_FILE="/home/ubuntu/ai-agency/.ig_api_state"
OUT="$(python3 ig_cek_blokir.py --ringkas 2>&1)"

if printf '%s' "$OUT" | grep -q '^PULIH:'; then
  NOW="ok"
else
  NOW="blocked"
fi

PREV="$(cat "$STATE_FILE" 2>/dev/null || echo 'unknown')"
printf '%s\n' "$NOW" > "$STATE_FILE"

[ "$PREV" = "$NOW" ] && exit 0   # tidak ada perubahan -> diam

if [ "$NOW" = "ok" ]; then
  KUNCI="$(python3 -c "import json;print(json.load(open('ig_pending.json')).get('key','-'))" 2>/dev/null || echo '-')"
  echo "✅ BLOKIR META LEPAS — API Instagram @omnisense_id normal lagi."
  echo ""
  if [ "$KUNCI" != "-" ]; then
    echo "Kandidat yang menunggu: $KUNCI"
    echo "Balas 'post' di grup ini untuk publish, atau 'batal' untuk tolak."
  else
    echo "Antrean kosong — tidak ada yang menunggu."
  fi
else
  echo "⚠️ API Instagram @omnisense_id DIBLOKIR lagi."
  echo ""
  printf '%s\n' "$OUT" | head -5
  echo ""
  echo "Jangan retry publish berulang. Cek: mode app di developers.facebook.com (harus Live), lalu lapor."
fi
exit 0
