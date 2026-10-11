# Temuan Celah Keamanan Website OmniSense — Bahan Fix Bareng Codex

Tanggal verifikasi: 2026-10-09 ~23:45 CST
Metode: uji langsung ke sistem live (curl ke origin & domain, cek config nginx/ufw/sshd, cek izin file, cek log). Bukan dari dokumen.
Sumber bukti mentah ada di transkrip sesi CLI 2026-10-09.

Konteks: security-v3 = layer WEBSITE (5 Okt, dibuat bareng ChatGPT + OmniSense).
Anti-troll WA = paket terpisah v5 (6 Okt) — TIDAK dibahas di sini, sudah terpasang & terverifikasi.

## CELAH (prioritas atas ke bawah)

### C1. Cloudflare bisa dilewati total (KRITIS)
- Origin 43.153.194.210 buka port 443 (nginx) langsung ke publik; ufw allow 443 dari Anywhere.
- Bukti: `curl --resolve omnisense.my.id:443:43.153.194.210 https://omnisense.my.id/` -> 200 dari IP kita (non-Cloudflare).
- Tidak ada pembatasan "hanya IP Cloudflare boleh masuk ke origin".

### C2. Rem per-pengunjung JEBOL karena C1 (KRITIS, turunan C1)
- App menghitung batas per-pengunjung dari header `CF-Connecting-IP`
  (consultation_web.py: `client()` -> `HTTP_CF_CONNECTING_IP`).
- Karena origin bisa diakses langsung, header itu bisa ditulis penyerang.
- Bukti uji:
  - GET session, kunci SAMA (CF-Connecting-IP tetap): 20x 200, ke-21 -> 429. (rem jalan)
  - GET session, kunci DIPUTAR (beda tiap request): 30x 200 semua, 0 rem.
  - POST cases, kunci tetap: 12x 403, ke-13 -> 429 (rem jalan).
  - POST cases, kunci diputar: 30x 403 (batas per-IP dilewati).
- Yang masih nahan: rem GLOBAL (240/menit requests, 120/menit post). Jadi tidak flood tanpa batas,
  tapi pembatasan per-orang sia-sia lewat origin langsung.

### C3. Tunnel trycloudflare lama MASIH HIDUP & publik (TINGGI)
- `https://then-farming-finding-undo.trycloudflare.com` masih balas 200 (GET / dan /api/consultation/session).
- Tunnel ini dipercaya penuh oleh app (service ExecStart memuat `--trust-tunnel` + origin tunnel ini).
- cloudflared jalan: pid 3341046 `cloudflared tunnel --url http://127.0.0.1:8080`.
- Ini pintu kedua ke app yang sama, di luar kontrol domain.

### C4. SSH masih boleh login pakai password (SEDANG-TINGGI)
- `sshd -T`: passwordauthentication yes, permitrootlogin no, maxauthtries 3, pubkey yes.
- Ada 302 IP unik nyerang; 5.512 "Failed password" dalam 3 hari.
- fail2ban aktif (jail sshd, total banned 1707, currently banned 3). ufw limit 22.
- Jadi ketahanan sedang, tapi pintu password sebaiknya ditutup (key-only).

### C5. Tidak ada ALARM di layer web (SEDANG)
- Tidak ada notifikasi ke tim saat ada yang kena rate limit / flood. Sama seperti WA.
- Tim tidak akan tahu ada serangan kecuali buka log manual.

### C6. Cek "peer beneran Cloudflare" sudah ditulis tapi BELUM disambung (SEDANG)
- `/etc/nginx/conf.d/omnisense-trusted-proxy.conf` punya `set_real_ip_from` + `geo $realip_remote_addr $omnisense_cf_peer` + `map ... $omnisense_cf_worker`.
- Tapi `$omnisense_cf_peer` / `$omnisense_cf_worker` TIDAK dipakai di `sites-enabled/omnisense.conf`.
- Niat ada, eksekusi belum. Kalau disambung, pemalsuan CF-Connecting-IP dari non-CF ikut mati.

## YANG SUDAH BAIK (hasil cek, jangan diubah sembarangan)
- File sensitif via web: /approved-site.json, /consultations.sqlite3, /web_security.sqlite3, /.web-rate-key, /.env, /.git/config -> semua 404.
- Header keamanan lengkap: CSP ketat (default-src none, nonce, trusted-types none), X-Frame-Options DENY,
  frame-ancestors none, HSTS, X-Content-Type-Options nosniff, COOP/CORP, Referrer-Policy no-referrer, Permissions-Policy.
- DB izin 600 (ubuntu:ubuntu), di luar folder web. App listen 127.0.0.1:8080 saja.
- systemd sandbox ketat: ProtectSystem=strict, ProtectHome=tmpfs, PrivateTmp, NoNewPrivileges, IPAddressDeny=any
  + IPAddressAllow=localhost, MemoryMax=256M, TasksMax=32, CapabilityBoundingSet kosong.
- whatsapp-admin-policy.json: milik root:ubuntu, mode 640, plugin tolak kalau bukan root / mode group-writable.
- Origin cert Let's Encrypt valid (omnisense.my.id, s/d 3 Jan 2027); nginx 80 -> 308 redirect ke https.
- API: POST tanpa Origin -> 403; Origin jahat -> 403; DELETE -> 405. (CORS/origin gate jalan)
- Rate limit web (dari consultation_web.py): requests 240/menit & 3000/jam; session 20/menit & 80/jam (global 240/menit);
  post 12/menit & 40/jam (global 120/menit).

## RENCANA PERBAIKAN (usulan)
- P1: Batasi origin hanya dari IP range Cloudflare (nginx allow/deny atau ufw) -> tutup C1, C2 otomatis.
- P1: Matikan tunnel trycloudflare lama (stop cloudflared pid 3341046; hapus origin tunnel dari ExecStart service).
- P2: SSH key-only (PasswordAuthentication no), restart sshd. Pastikan kunci akses sudah ada dulu.
- P2: Sambungkan $omnisense_cf_peer / $omnisense_cf_worker ke sites-enabled (C6).
- P3: Alarm otomatis ke grup WA tim saat rate limit kena (web & WA).

## CATATAN OPERASIONAL
- Ubah file situs -> WAJIB update hash sha256 di security-v3-*/approved-site.json, kalau tidak -> 503.
- Port 443 di firewall Tencent Lighthouse: TIDAK diblok (terverifikasi: 443 dari publik -> 400/nginx).
  (Catatan lama di memori menyebut 443 diblok — itu sudah tidak akurat untuk kondisi 2026-10-09.)
- Jangan pernah tampilkan isi .env / kredensial verbatim.
