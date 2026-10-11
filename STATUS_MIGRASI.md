# STATUS MIGRASI OMNISENSE -> GITHUB

Diperbarui: 2026-10-11 (oleh OmniSense di VPS lama)

## Repo

- Repo  : https://github.com/OmniSenseInc/OmniBrain (PRIVAT)
- Branch: main
- Isi   : 1.824 berkas kode/konfigurasi + 26 bagian bundel terenkripsi (918 MB)
- Verifikasi: satu bagian diunduh ulang dari GitHub, hash SHA256 identik dengan
  daftar sidik jari lokal; pohon repo tidak memuat berkas rahasia apa pun.

## Sudah selesai & teruji

| # | Item | Bukti |
|---|---|---|
| 1 | Inventaris lengkap VPS | otak agent 2,1 GB, ai-agency 1,3 GB, lapisan sistem, 6 cron, 4 service, nginx+SSL |
| 2 | Bundel migrasi terenkripsi | `bundel/` 918 MB, 26 bagian @45 MB, AES-256 (PBKDF2 200k) |
| 3 | Sidik jari SHA256 | `sha256sum -c` -> OK semua bagian |
| 4 | Uji isi bundel | zip 2.274 berkas, tar 2.112 entri, `state.db` integrity OK |
| 5 | Uji PEMULIHAN nyata di folder bersih | 246 sesi, 20.715 pesan, 4 tiket konsultasi, kredensial WhatsApp, .env, cron, skill, plugin, website -> kembali semua |
| 6 | Push ke GitHub | branch `main`, commit "Otak OmniSense + bundel migrasi terenkripsi" |
| 7 | Verifikasi pasca-push | unduh ulang 1 bagian dari GitHub -> SHA256 cocok; tree bersih dari rahasia |

## Sisa langkah

1. **VPS baru** (pemilik menyiapkan sendiri). Spesifikasi: Ubuntu 22.04/24.04,
   min 2 vCPU / 4 GB RAM / 60 GB disk, port 80 & 443 dibuka di security group.
2. Pemulihan di VPS baru:

```bash
sudo apt-get update && sudo apt-get install -y git curl openssl rsync unzip
git clone https://<token>@github.com/OmniSenseInc/OmniBrain.git ~/omnisense-brain
cd ~/omnisense-brain
MIGRASI_PASS='<kata-sandi-bundel>' bash scripts/pulihkan.sh
```

3. Langkah manual setelah skrip selesai: WhatsApp restart (scan QR hanya kalau
   sesi lama ditolak), Cloudflare DNS A -> IP VPS baru (proxied ON), cek SSL,
   uji IG auto-post sekali manual.
4. **Pindah Cloudflare**: record A `omnisense.my.id` saat ini -> 43.153.194.210 (VPS lama).

## Perkiraan setelah clone di VPS baru

- repo + bundel: ~940 MB
- setelah pemulihan: otak agent ~350 MB + ai-agency ~800 MB (termasuk aset gambar)
- total ~2,1 GB

## Keamanan

- Bundel AES-256; kata sandinya dipegang pemilik (tidak ada di repo).
- Setelah migrasi selesai: **cabut token GitHub** yang dipakai untuk migrasi ini
  (token sudah pernah muncul di chat, jadi perlakukan sebagai token bekas pakai),
  lalu rotasi API key provider yang ikut di dalam bundel.
- Simpan salinan repo ini di luar GitHub juga bila perlu (mis. hard disk eksternal).

## Kalau ada perubahan penting di OmniSense sebelum VPS mati

```bash
cd /home/ubuntu/migrasi
MIGRASI_PASS='<kata-sandi>' bash buat_bundel.sh
GITHUB_TOKEN=<token> GITHUB_REPO=OmniSenseInc/OmniBrain bash push_github.sh
```
