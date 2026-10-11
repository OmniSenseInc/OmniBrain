---
name: web-domain-ingress
description: "Point a domain at a VPS site; fix DNS/port issues."
---

# Menghubungkan domain ke situs yang jalan di VPS

Dipakai saat: mengarahkan domain publik ke situs yang dilayani di sebuah server (VPS ini atau
VPS lain); atau saat domain "tidak nyambung" — belum resolve, `SERVFAIL`, atau `REFUSED`.
Bukan untuk menyunting isi situs (itu skill `omnisense-website`).

## Prinsip: verifikasi dulu, baru rencanakan
Jangan menyusun rencana bertingkat (buka port → pasang web server → HTTPS → DNS) SEBELUM
mengecek apa yang sudah beres. Port yang tampak perlu dibuka di konsol cloud sering sudah
terbuka dari sisi provider; satu-satunya cara tahu adalah mengukurnya. Sebut hanya langkah
yang benar-benar tersisa. Untuk pengguna non-teknis: sajikan SATU keputusan per giliran,
bahasa sehari-hari, analogi sederhana (domain = alamat rumah, nameserver = kantor pos,
A record = "rumahnya di jalan mana"). Jangan menyebut nama konsol/istilah teknis sebelum
terbukti perlu — daftar pilihan yang tak dipahami membuat pengguna merasa dipersulit.

## Langkah
1. **Temukan endpoint.** Cari di mana situs benar-benar dilayani — jangan asumsikan:
   `ss -tlnp`, `systemctl list-units --type=service | grep -iE 'web|site'`,
   `ps aux | grep -E 'nginx|apache|node|python|cloudflared'`. Catat alamat:port (mis.
   `127.0.0.1:8080`). IP publik: `curl -s ifconfig.me`.
2. **Temukan pengelola domain.** `whois <domain>` → Registrar + Name Server; `dig +short NS <domain>`.
   Domain `.my.id` bisa didaftarkan lewat reseller (WHOIS menunjuk reseller, bukan provider hosting).
3. **Diagnosa DNS dengan `dig`** — lihat `references/dns-diagnosis.md`. Kunci: query NS
   otoritatif LANGSUNG, jangan cuma resolver publik.
4. **Verifikasi keterjangkauan port DARI LUAR** — resep di `references/dns-diagnosis.md`.
   Tes dari host yang sama tidak sah (kena NAT/hairpin).
5. **Ingress (bila perlu web server di depan app).** Salin `templates/nginx-reverse-proxy.conf`,
   sesuaikan `server_name` + `proxy_pass`, pasang ke `/etc/nginx/sites-available/`, symlink ke
   `sites-enabled/`, hapus `default`, `nginx -t`, lalu `systemctl reload nginx`.
6. **Daftarkan domain di app (bila app memvalidasi Host/origin).** Banyak app yang dikeraskan
   menolak `Host` tak dikenal dan memeriksa daftar origin eksplisit. Tambah domain di konfigurasi
   app (mis. argumen `--origin` pada `ExecStart` systemd), `daemon-reload`, restart unit. Tanpa
   ini, DNS + proxy benar pun tetap `400/403`.
7. **Uji rantai penuh lewat proxy lokal sebelum DNS:**
   `curl -H "Host: <domain>" -H "X-Forwarded-Proto: https" http://127.0.0.1/` → harap 200,
   dan `.../api/health`. Uji juga tanpa `X-Forwarded-Proto` bila app harus redirect ke HTTPS.
8. **HTTPS.** Pilih sesuai kemampuan pengguna (tabel di bawah).

## Dua lapis firewall
Cloud provider punya **security group** (di konsol provider) yang TERPISAH dari firewall host
(`ufw`/`iptables`). Satu port bisa diblok di salah satu atau keduanya. Uji dari luar untuk tahu
lapis mana yang menutup — jangan langsung menyuruh pengguna membuka konsol.

## Pilihan HTTPS
| Cara | Butuh | Catatan |
|---|---|---|
| Cloudflare Tunnel (named) | pindah NS domain ke Cloudflare; **TIDAK** perlu buka port | paling mulus bila pengguna tak bisa/enggan sentuh konsol cloud |
| Reverse proxy + Certbot | port 80 & 443 terbuka (2 lapis) | "resmi", domain langsung ke VPS |
| Quick tunnel (`cloudflared tunnel --url`) | tak perlu apa pun | URL acak `trycloudflare.com`, **TIDAK** bisa pakai domain sendiri — hanya pratinjau sementara |

## Jebakan
- **`REFUSED` ≠ `SERVFAIL`.** `SERVFAIL` dari resolver = tak bisa dapat jawaban (masalah
  delegasi/zone). `REFUSED` dari NS otoritatif = NS hidup tapi tidak punya zone itu — artinya
  zone belum dibuat/di-deploy di provider DNS, walau panel DNS menampilkan record. Perbaikannya
  di provider (aktifkan zone) atau pindah NS ke provider lain, bukan di record A.
- **Panel menampilkan record ≠ zone dilayani.** Selalu konfirmasi lewat query NS otoritatif.
- **Jangan menilai keterjangkauan port dari host yang sama.** NAT hairpin memberi hasil palsu
  (self-test bilang tertutup padahal dari luar terbuka).
- **Utamakan metode ingress yang sudah pernah berhasil dipakai pengguna.** Tunnel keluar dari
  dalam VPS tidak butuh port dibuka — kalau itu yang dipakai sebelumnya, tawarkan itu lebih dulu.
- **Jangan menawarkan daftar registrar/konsol ke pengguna non-teknis.** Tanya satu hal paling
  menentukan saja, sisanya cari sendiri dari WHOIS/dig.
