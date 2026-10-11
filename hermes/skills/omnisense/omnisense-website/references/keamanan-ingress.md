# Audit keamanan ingress OmniSense (web + WhatsApp)

Kelas tugas: "apakah kita aman dari troll / jailbreak / ngacak database?" — jawab dengan BUKTI
UJI LANGSUNG ke sistem, bukan kutipan dokumen, bukan pula hash paket saja. Hash cocok hanya
membuktikan berkasnya asli, bukan bahwa lubangnya tertutup.

## Peta layer (dua paket TERPISAH, jangan tertukar)
- Web: `/opt/omnisense-web/security-v3-*/` — `run_secure_web.py` (server), `consultation_web.py`
  (kunci rate-limit, CSP, integritas berkas), `web_limits.py` (ledger), `approved-site.json`.
  nginx: `/etc/nginx/sites-enabled/omnisense.conf`, `conf.d/omnisense-trusted-proxy.conf`.
  systemd: `omnisense-secure-web` (app hanya di 127.0.0.1:8080).
- WA: `~/.hermes/plugins/omnisense-consultation/` — `omnisense_wa_security.py` (gate admin),
  `wa_limits.py` (batas), `__init__.py` (lane konsultasi). Kebijakan admin root:
  `/opt/omnisense-web/whatsapp-admin-policy.json`.
- Paket versi tersimpan di `ai-agency/meeting/*.zip`: `omnisense-security-v3-patch.zip` = WEB,
  `omnisense-security-v5-wa-spam.zip` = WA. Bukti keaslian = sha256 berkas terpasang == paket.

## Resep uji (urut; semuanya read-only, tidak mengubah apa pun)
1. Header & protokol: `curl -sI https://omnisense.my.id/` → CSP ketat, X-Frame-Options DENY, HSTS.
2. Kebocoran berkas: curl `/approved-site.json`, `/consultations.sqlite3`, `/.env`, `/.git/config`
   → semua harus 404.
3. Origin langsung (kunci utama):
   `curl -sk --resolve omnisense.my.id:443:<IP-origin> https://omnisense.my.id/` → 200 = CDN
   bisa dilewati; `-H 'Host: evil.invalid'` → harus 400.
4. Pemalsuan kunci limit, kunci TETAP: loop 30x
   `curl -sk --resolve ... -H "CF-Connecting-IP: 203.0.113.77" .../api/consultation/session`
   → harus muncul 429 di ujungnya.
5. Pemalsuan kunci limit, kunci DIPUTAR: sama tapi `198.51.100.$i` tiap request → kalau 200 semua,
   batas per-pengunjung memang bisa dilewati.
6. Kontrol API: POST tanpa Origin dan dengan Origin asing → 403; DELETE → 405.
7. Listener & sandbox: `ss -ltnp` (app harus 127.0.0.1 saja), `systemctl cat omnisense-secure-web`
   (ProtectSystem, PrivateTmp, IPAddressDeny, MemoryMax), `ufw status`.
8. SSH: `sudo sshd -T | grep -Ei 'passwordauthentication|permitrootlogin|maxauthtries'`,
   `fail2ban-client status sshd`, hitung percobaan gagal di `journalctl -u ssh`.
9. Tunnel liar: `ps aux | grep cloudflared`, lalu probe URL `trycloudflare` yang muncul.
10. DB: `stat -c '%A %U:%G %n' consulting/data/*.sqlite3` → harus 600 dan di luar folder web.

## Celah yang terbukti (status paket v3/v5)
- Origin menerima koneksi langsung → CDN dilewati → kunci `CF-Connecting-IP` dipalsukan → batas
  per-pengunjung jebol; hanya batas global (240/menit) yang menahan.
- Tunnel quick trycloudflare lama masih hidup dan dipercaya penuh (`--trust-tunnel`).
- SSH masih `PasswordAuthentication yes` (root sudah `no`) + fail2ban aktif: masih bertahan,
  belum key-only.
- Tidak ada alarm ke tim saat limit/flood; tidak ada blokir permanen (web maupun WA).
- `geo $omnisense_cf_peer` sudah ditulis di nginx tapi BELUM disambungkan ke alur request.
- Jalur WA dari luar memang tool-free (terbukti di `logs/gateway.log`: baris
  `reason=omnisense_consultation_lane`), jadi jailbreak dari DM luar tidak menyentuh berkas/DB;
  risiko DB ada di nomor admin, yang sesinya memegang tool penuh.

## Bentuk laporan yang diminta pemilik
- Ringkas per VEKTOR (troll / jailbreak / ngacak DB), masing-masing ditandai
  "ketutup / ketutup sebagian / bolong".
- Sertakan daftar celah apa adanya, prioritas P1/P2/P3, lalu tawarkan eksekusi perbaikan.
- Bahasa Indonesia informal, tanpa jargon; angka batas dan nama berkas boleh disebut.
- Jangan mengklaim situs/server "aman" — sebut apa yang diuji dan apa yang belum.
