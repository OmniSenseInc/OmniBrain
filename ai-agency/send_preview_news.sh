#!/bin/bash
cd /home/ubuntu/ai-agency || exit 1
CAP="$(cat ig_caption_pending.txt)"
TAGS="#OmniSense #AIAgent #AIuntukBisnis #OtomatisasiAI #BisnisIndonesia"
hermes send --to whatsapp "$CAP

$TAGS

Balas 'post' untuk publish ke Instagram, 'batal' untuk tolak.
MEDIA:/home/ubuntu/ai-agency/konten_berita_id.png"
sleep 4
hermes send --to whatsapp "Versi English (poster EN, teks sama).
MEDIA:/home/ubuntu/ai-agency/konten_berita_en.png"
