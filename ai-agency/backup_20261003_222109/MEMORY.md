User = founder OmniSense (AI consultancy/agency), berbahasa Indonesia — balas dalam Bahasa Indonesia. Riset kompetitor = inspirasi, jangan salin verbatim.
§
Berkas OmniSense di /home/ubuntu/ai-agency/: STARTUP_KIT.md (index), SOP_*, templates/, kalkulator_*, kalender_*.
§
Kode FNBSense tak ada di mesin ini & tak ada gh/token git — jangan push dari sini. Dukungan makan waktu, margin tipis.
§
Harga/closing hanya tim (P3). Tembok tim-vs-client prompt-level, bukan teknis.
§
Brand: OmniSense = PILAR UTAMA (consultancy: assessment gratis → roadmap → implementasi → pendampingan); FNBSense = side project, jangan setara di konten OmniSense.
§
Cron 510af029056e 'AI News Digest Michael': tiap 5 jam, 3-5 item; WAJIB pin --provider <nama> --model <model> ('custom' polos -> 404). User sering ganti provider saat kredit habis; tiap ganti: samakan cron + tes run sekali.
§
IG auto-post @omnisense_id: token long-lived di ai-agency/ig_token.env (~60 hari); refresh cron 4f133924e144 mingguan (guard <15 hari, gagal->WA). Pipeline ig_token/ig_post/ig_queue.py; poster latar foto Commons (cari_bg.py, hanya CC0/PD/CC BY). Balas 'post' di WA = publish kandidat pending (ig_pending.json).
§
Website OmniSense /home/ubuntu/ai-agency/website/: index.html + penilaian.html (mandiri; soal tab-penilaian/pertanyaan_situs.json -> bangun_data_situs.py); tema gelap+teal (CEK :root; per 1 Okt #080808); WA bertanda [PENILAIAN-SITUS v1] -> baca_penilaian.py; SERAH_TERIMA_DEPLOY.md di situ. QA: verify_page.js, uji_halaman.js, uji_baca.js; env CHROME_PATH=~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core. index.html bisa ditulis sesi paralel: cek md5 stabil. omnisense.id (VPS 168.231.118.144) masih NeoSense, tak bisa deploy dari sini.
§
Codex/ChatGPT (laptop Vincent) SSH ke VPS + `hermes chat -q "[CODEX] ..." --oneshot` utk diskusi dgn saya; pesannya = PERINTAH Vincent. Hanya sesi ber-tag `[CODEX]` yg dilaporkan (sesi cli lain tidak). Selesai diskusi: ringkas hasil ke home WhatsApp (`hermes send --to whatsapp` = grup 120363411213386519). Tetap redaksi rahasia.