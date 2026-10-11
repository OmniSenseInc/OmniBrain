# OmniSense — Pindah VPS & Pemulihan

Repo ini adalah **otak OmniSense**: kode, konfigurasi, skill, cron, website, dan
sistem konsultasi. Rahasia (API key, token IG, sesi WhatsApp), database klien,
riwayat chat, dan aset gambar **tidak** ada di sini — semuanya ada di
**bundel terenkripsi** (lihat `bundel/`).

## Isi repo

| Folder | Isi |
|---|---|
| `ai-agency/` | Skrip bisnis, sistem konsultasi (`consulting/`), website, konten & IG, dokumen |
| `hermes/config.yaml` | Konfigurasi agent (model, gateway, toolset) |
| `hermes/skills/` | 40+ skill (omnisense-*, konten, konsultasi, dll) |
| `hermes/memories/` | Memori & profil pemilik |
| `hermes/cron/jobs.json` | 6 cron job (digest berita, auto-post IG, notif konsultasi, dll) |
| `hermes/plugins/` | Plugin konsultasi WhatsApp |
| `hermes/code-custom/` | Perubahan lokal pada kode Hermes (policy admin WhatsApp 3 nomor) |
| `hermes/scripts/` | Skrip yang dipanggil cron |
| `scripts/` | `pulihkan.sh` (pemulihan satu perintah), `buat_bundel.sh`, `siapkan_repo.sh`, `push_github.sh` |
| `bundel/` | Bundel terenkripsi (rahasia + riwayat + aset), terpecah <95 MB |

## Memperbarui salinan di GitHub (dari VPS lama)

```bash
cd /home/ubuntu/migrasi
MIGRASI_PASS='<kata-sandi-bundel>' bash buat_bundel.sh          # bundel baru
GITHUB_TOKEN=ghp_xxx GITHUB_REPO=<akun>/omnisense-brain bash push_github.sh
```

Jalankan ini lagi setiap kali ada perubahan penting, supaya GitHub selalu
menjadi salinan terbaru OmniSense.

## Pindah ke VPS baru (ringkas)

```bash
# 1. di VPS baru
sudo apt-get update && sudo apt-get install -y git curl openssl
git clone https://<token>@github.com/<akun>/omnisense-brain.git ~/omnisense-brain
cd ~/omnisense-brain

# 2. buka bundel & pulihkan semuanya
MIGRASI_PASS='<kata-sandi-bundel>' bash scripts/pulihkan.sh

# 3. langkah manual terakhir (dicetak skrip): Cloudflare DNS, WhatsApp, uji IG
```

Perkiraan waktu: 15–30 menit (paling lama: pasang paket + venv).

## Yang perlu disiapkan di VPS baru

- Ubuntu 22.04/24.04, min 2 vCPU / 4 GB RAM / 60 GB disk
- Port 80 & 443 dibuka di security group provider (jangan ulangi masalah VPS lama
  yang memblok 443 di level firewall cloud)
- DNS omnisense.my.id di Cloudflare diarahkan ke IP baru (mode proxied ON)
- Sertifikat SSL ikut terpulihkan dari bundel; kalau perlu terbit ulang:
  `sudo certbot --nginx -d omnisense.my.id -d www.omnisense.my.id`

## Kalau pindah lagi nanti

Semua sudah otomatis: di VPS lama jalankan `bash scripts/buat_bundel.sh` lalu
`bash scripts/siapkan_repo.sh`, commit + push. Di VPS baru cukup clone + `pulihkan.sh`.

## Catatan keamanan

- Bundel dienkripsi AES-256 (`openssl enc -pbkdf2 -iter 200000`). Kata sandinya
  **hanya** dipegang pemilik; jangan simpan di repo, jangan kirim lewat chat.
- Setelah migrasi selesai: cabut token GitHub yang dipakai, dan pertimbangkan
  mengganti API key provider (semuanya ada di `~/.hermes/.env`).
- Repo wajib **privat**.
