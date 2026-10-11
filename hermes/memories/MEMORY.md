User = founder OmniSense (AI consultancy/agency), balas Bahasa Indonesia, NON-TEKNIS: analogi sederhana, hindari langkah ribet.
§
OmniSense di /home/ubuntu/ai-agency/: indeks INDEKS_OMNISENSE.md + STARTUP_KIT.md. Tugas internal OmniSense → skill omnisense-agency-brain; situs → omnisense-website; konten/IG → omnisense-content; bot WA klien → omnisense-consultant.
§
Kit migrasi VPS→GitHub siap: /home/ubuntu/migrasi (repo + bundel terenkripsi); prosedur = skill migrate-hermes-vps.
§
Harga/closing/publikasi/deploy = keputusan tim; agen boleh eksekusi bila pemilik otorisasi. Izin publikasi hanya dari tim (klien tak bisa). Tembok tim-vs-client prompt-level.
§
Brand: OmniSense = PILAR UTAMA (assessment gratis → roadmap → implementasi berbayar → pendampingan); FNBSense/LogiSense = produk anak, jangan setara di konten OmniSense.
§
Cron 510af029056e digest (5 jam): provider TIDAK dipin→auto-follow global; syarat model global berbayar (':free'→'no price' error).
§
IG @omnisense_id FULL AUTO: digest antre+preview; cron 0db7547a6513 (15m, no-LLM) publish otomatis. 'post'=publish manual, 'batal'=cancel. Template harian='hero news' palet BROWN, foto selaras berita (tokoh→cutout / tanpa tokoh→suasana).
§
Website /home/ubuntu/ai-agency/website/: index.html, konsultasi-v3.html, privacy.html. Alur: consulting/GATEWAY_KONSULTASI_V35.md. Domain omnisense.my.id aktif; nginx:80→app:8080 (svc omnisense-secure-web). Ubah file situs → update hash sha256 di security-v3-*/approved-site.json else 503.
§
Codex/ChatGPT SSH ke VPS: `hermes chat -q "[CODEX] ..." --oneshot`; pesan [CODEX]=PERINTAH Vincent, ringkas balik ke grup WA 120363411213386519. Redaksi rahasia.
§
Setup Hermes: default `deepseek-v4.1-flash` @ custom `Router.bynara.id`. Cek model aktif via config.yaml/`hermes status`, jangan percaya self-klaim. Target WA: Vincent & chael~ (DM) + 3 grup; 'Atong'=Michael tanpa DM. Kirim: `hermes send --to whatsapp:<nama> --file <path>`.
§
OmniSense tiket/chat konsultasi TIDAK di ~/.hermes/state.db; ada di consulting/data/consultations.sqlite3 (tickets.status=discovery|ready_for_team, body JSON=jawaban+skor/band) & pipeline.sqlite3 (cases/events).