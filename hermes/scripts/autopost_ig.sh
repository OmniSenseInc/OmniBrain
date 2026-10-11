#!/usr/bin/env bash
# autopost_ig.sh — FULL AUTO publish kandidat IG OmniSense yang pending.
#
# Script-only (no LLM): TIDAK butuh provider/kredit AI sama sekali, jadi tetap
# jalan walau user ganti-ganti provider. Dipanggil cron tiap beberapa menit.
#
# Pola watchdog: stdout KOSONG = tidak ada yang perlu dilaporkan (cron diam).
# stdout BERISI = cron mengirimkan teks ini verbatim ke grup home WhatsApp.
#
# Perilaku: publish kandidat pending yang umurnya sudah lewat jendela tenggang
# (default 30 menit, supaya user masih sempat 'batal').
set -uo pipefail

cd /home/ubuntu/ai-agency || { echo "⚠️ AUTO-POST: folder ai-agency tidak ada"; exit 2; }

GRACE_MIN="${AUTOPOST_GRACE_MIN:-30}"

OUT="$(python3 ig_queue.py autopost --min-age-minutes "$GRACE_MIN" --verbose 2>&1)"
RC=$?

if printf '%s' "$OUT" | grep -q "BERHASIL"; then
    LINK="$(printf '%s' "$OUT" | grep -oE 'https://www\.instagram\.com/p/[A-Za-z0-9_-]+/' | head -1)"
    KEY="$(printf '%s' "$OUT" | grep -oE "mempublikasikan '[^']+'" | sed "s/mempublikasikan '//;s/'//" | head -1)"
    printf '✅ AUTO-POST tayang di @omnisense_id\nTopik : %s\nLink  : %s\n\nTayang otomatis (full auto). Balas "batal" kalau mau hentikan gaya ini.\n' \
        "${KEY:-?}" "${LINK:-lihat ig_queue.py status}"
    exit 0
fi

if printf '%s' "$OUT" | grep -qiE "GAGAL|error|Traceback"; then
    printf '⚠️ AUTO-POST GAGAL — kandidat IG masih menunggu.\n%s\n\nCek: cd /home/ubuntu/ai-agency && python3 ig_queue.py status\n' \
        "$(printf '%s' "$OUT" | tail -3)"
    exit 1
fi

# Tidak ada kandidat / masih dalam jendela tenggang -> diam.
exit 0
