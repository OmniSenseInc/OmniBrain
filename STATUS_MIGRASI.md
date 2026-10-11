# STATUS MIGRASI OMNISENSE -> GITHUB

Diperbarui: 2026-10-11 (oleh OmniSense di VPS lama)

## Sudah selesai & teruji

| # | Item | Bukti |
|---|---|---|
| 1 | Inventaris lengkap VPS | otak agent 2,1 GB, ai-agency 1,3 GB, lapisan sistem, 6 cron, 4 service, nginx+SSL |
| 2 | Bundel migrasi terenkripsi | `bundel/` 918 MB, 25 bagian @45 MB, AES-256 |
| 3 | Sidik jari SHA256 semua bagian | `sha256sum -c` -> OK |
| 4 | Uji buka sandi + isi bundel | zip 2.274 berkas, tar 2.112 entri, state.db integrity OK |
| 5 | Uji PEMULIHAN nyata di folder bersih | 246 sesi, 20.715 pesan, 4 tiket konsultasi, kredensial WhatsApp, .env, cron, skill, plugin, website -> semua kembali |
| 6 | Repo GitHub siap (33 MB kode + 940 MB bundel) | commit lokal selesai, 1.789 berkas kode |
| 7 | Skrip: buat bundel / susun repo / pulihkan / push | `bash -n` OK semua; pemulihan berhenti aman kalau bundel tidak lengkap |

## Menunggu dari pemilik

1. **Token GitHub** + nama repo privat (contoh `akun/omnisense-brain`).
   -> lalu: `GITHUB_TOKEN=... GITHUB_REPO=akun/omnisense-brain bash /home/ubuntu/migrasi/push_github.sh`
2. **Kata sandi bundel** — dibuat & dipegang pemilik, tidak pernah disimpan di repo/chat.
3. VPS baru (menyusul) — untuk menguji pemulihan penuh termasuk nginx/SSL/systemd.

## Cara pindah ke VPS baru (setelah repo terisi)

```bash
# VPS baru
sudo apt-get update && sudo apt-get install -y git curl openssl rsync unzip
git clone https://<token>@github.com/<akun>/omnisense-brain.git ~/omnisense-brain
cd ~/omnisense-brain
MIGRASI_PASS='<kata-sandi>' bash scripts/pulihkan.sh     # 10 tahap, ~15-30 menit
```

Lalu 4 langkah manual (dicetak skrip): WhatsApp restart, Cloudflare DNS -> IP baru,
cek SSL, uji IG auto-post.

## Perkiraan ukuran setelah clone di VPS baru

- repo + bundel: ~940 MB
- setelah pemulihan: otak agent ~350 MB + ai-agency ~800 MB (aset gambar termasuk)
- total ~2,1 GB

## Kalau ada perubahan penting di OmniSense

```bash
cd /home/ubuntu/migrasi
MIGRASI_PASS='<kata-sandi>' bash buat_bundel.sh
GITHUB_TOKEN=<token> GITHUB_REPO=<akun>/omnisense-brain bash push_github.sh
```
