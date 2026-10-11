# HANDOFF — Konteks OmniSense untuk agen eksternal (Codex/ChatGPT)

> Dibuat: 3 Oktober 2026 · Untuk: agen AI yang berdiskusi dengan Hermes (agen OmniSense di VPS ini)
> Status: dokumen orientasi. Ditulis oleh Hermes atas permintaan Vincent (founder).
> **Aturan:** semua isi di bawah = konteks, bukan perintah. Aksi yang mengubah file/mengirim pesan tetap harus lewat Vincent.

---

## 0. Cara memakai dokumen ini

- Baca ini dulu sebelum bertanya ke Hermes — supaya tidak mengulang pertanyaan yang sama tiap sesi.
- Dokumen ini **ringkasan**. Sumber kebenaran tetap file asli di `/home/ubuntu/ai-agency/` (daftar di §7).
- Kalau ada beda antara dokumen ini dan file asli → **file asli yang benar**. Cek `roadmap_status.md` dan `CONTENT_POSTED_LOG.md` untuk kondisi terbaru.

---

## 1. Siapa & apa

- **Vincent** = founder. Berbahasa Indonesia. Hermes berperan sebagai "AI consultant" OmniSense.
- **OmniSense** = badan usaha (AI consultancy/agency). Ini **pilar utama**.
  - Model: **assessment kesiapan digitalisasi GRATIS** (lead magnet, skoring 8 dimensi → % kesiapan) → **roadmap + implementasi BERBAYAR** → pendampingan.
  - Slogan: *"Where Traditional Systems end, AI Agents Begin."*
  - Vertikal fokus (beachhead): **F&B / cafe**.
- **FNBSense** = anak produk (Web POS per-outlet untuk cafe/F&B + backend Hermes agent: cron + "sekretaris pribadi" pemilik).
- **LogiSense** = anak produk (logistik) — **detail masih TBD**.
- Konteks akademik: OmniSense dipakai sebagai subyek **tugas akhir matkul Penerapan Bisnis**, syarat: badan usaha harus berjalan **6 bulan**.

> ⚠️ **Aturan brand:** OmniSense = pilar utama. FNBSense = side project — jangan ditonjolkan setara di konten promosi OmniSense.

---

## 2. Status proyek (per 3 Okt 2026)

**Roadmap 11 fase** (detail: `roadmap_status.md`):

| Fase | Status |
|---|---|
| F0 kebenaran dasar, F1 bisnis inti, F2 pelanggan, F3 visi-misi, F4 positioning, F6 pricing, F7 MVP scope, F8 SOP internal | **DONE** |
| F5 validasi pelanggan | **DI-SKIP sementara** (rencana & alat siap; perannya diambil F9) |
| F9 soft launch/beta (3–5 pilot) | **Rencana siap, menunggu eksekusi + klien nyata** |
| F10 publikasi | **Bisa dipersiapkan sekarang** (landing page/konten), menunggu testimoni |
| F11 ukur & ulangi | Belum (butuh data F9/F10) |

**Pekerjaan tanpa klien yang tersisa (prioritas):**
1. Template proposal/kontrak — gap Fase 8
2. Kerangka landing page + konten + checklist kanal — prep Fase 10
3. *(tim)* Isi biaya riil & kunci harga final (Fase 6)
4. *(tim/CTO)* Build FNBSense MVP v1
5. *(opsional)* README/fondasi repo OmniSenseInc

**Butuh klien (menunggu):** validasi wawancara (F5), beta 3–5 pilot (F9), pengukuran (F11), testimoni (F10).

---

## 3. Kondisi teknis terkini

### Website
- Lokasi: `/home/ubuntu/ai-agency/website/` — `index.html` + `penilaian.html` (penilaian mandiri, halaman sendiri/tab baru).
- Soal penilaian: `tab-penilaian/pertanyaan_situs.json` → dibangun oleh `bangun_data_situs.py`.
- Tema: **gelap + teal**. **Cek `:root` dulu sebelum menyebut warna** — per 1 Okt `#080808` (bukan navy). Ada revisi "Tone B Navy Lembut" di `TEMA_OMNISENSE.md`; struktur A/B/C lama sudah tidak berlaku.
- WA bertanda `[PENILAIAN-SITUS v1]` → diproses `baca_penilaian.py`.
- Paket deploy: `SERAH_TERIMA_DEPLOY.md` (status: berkas siap, **belum diunggah**).
- **`omnisense.id` (VPS `168.231.118.144`) masih NeoSense** — mesin ini **tidak bisa deploy** ke sana.
- QA: `verify_page.js` + `tab-penilaian/uji_halaman.js` & `uji_baca.js`. Env: `CHROME_PATH=~/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`, `PW_CORE=/tmp/camofox/node_modules/playwright-core`.
- ⚠️ `index.html` bisa ditulis sesi paralel → **cek md5 stabil & kurung seimbang** sebelum/sesudah edit.

### Konten & auto-post
- Akun IG resmi: **@omnisense_id** (underscore).
- Auto-post: token long-lived di `ai-agency/ig_token.env` (~60 hari); cron refresh `4f133924e144` mingguan (guard <15 hari, gagal → WA).
- Pipeline: `ig_token.py` / `ig_post.py` / `ig_queue.py`. Poster berlatar foto Commons (`cari_bg.py`, hanya CC0/PD/CC BY).
- **TEMPLATE HARIAN = "hero news"** (keputusan user 7 Okt 2026): gaya @cryptowaveid, palet BROWN (`#A8744C`/`#D4A574`), **foto SELARAS berita**. Ada tokoh → cutout (`siapkan_foto.py --tokoh`); tanpa tokoh → foto suasana (`siapkan_foto.py --suasana`). Render: `konten_hero_news.py --file <data>.json --png konten_berita_id.png --cek`. Mesin: `konten_hero_news.py`, `siapkan_foto.py`, `cutout.py` (model `u2net`), `cari_bg.py`. Template lama `konten_harian.py` tetap ada (tidak diubah).
- Balas **"post"** di WA = publish kandidat pending (`ig_pending.json`).
- Log konten sudah tayang: **`CONTENT_POSTED_LOG.md`** — WAJIB dicek sebelum usul topik, jangan ulang yang sudah POSTED.
- `API access blocked` code=200 → App Mode Meta masih Development → set Live.

### Cron
- Job `510af029056e` "AI News Digest untuk Michael": tiap **5 jam**, 3–5 item.
- **Provider TIDAK dipin** (provider/model = null) → job otomatis ikut provider global yang user set. Jadi user ganti provider = cron tetap jalan tanpa edit manual. **SYARAT: model global harus punya entri harga** (model `:free` ditolak cron dengan `no price for model`).
- Job `0db7547a6513` "IG auto-post (OmniSense, full auto)": tiap **15 menit**, script-only `autopost_ig.sh` (NO LLM → kebal ganti provider/kredit). Publish kandidat pending yang umurnya > 30 menit (`AUTOPOST_GRACE_MIN`), lalu kirim permalink ke WA. Kalau tidak ada yang baru → diam.
- ⚠️ **Aturan biaya:** model `:free` boleh untuk chat, **tidak boleh untuk cron** (Hermes harus mengunci biaya terburuk-kasus; varian `:free` tanpa entri harga → API tolak `no price for model`).
- Saldo terakhir Kenari.id: **Rp 103** — belum cukup untuk 1 run digest (butuh ~Rp 469–479 reserve). Perlu top-up di kenari.id/pay.

---

## 4. Batasan & aturan yang mengikat

- **Rahasia:** jangan tampilkan `.env`, API key, token, password. Memory hanya menyebut *lokasi* file token, bukan isinya.
- **Kode FNBSense tidak ada di mesin ini**, dan **tidak ada gh/token git** → jangan push dari sini.
- **Harga/closing = urusan tim** (P3). Tembok tim-vs-client bersifat prompt-level, bukan teknis.
- **Profil ganda:** internal (Telegram, tim) vs konsultan (WhatsApp, klien) — lihat `guardrail_internal_telegram.md` & `guardrail_consultant_whatsapp.md`.
- **Copy:** jangan pakai "usaha kecil"/"UMKM kecil" (merendahkan) → pakai "bisnis kamu"/"bisnis lokal". Tone: premium, tenang, editorial, tanpa hard-sell.

---

## 5. Keputusan yang sudah dikunci

- OmniSense = pilar utama; FNBSense & LogiSense = anak produk.
- Corong: **gratis = diagnosis, berbayar = roadmap + deployment**.
- Vertikal fokus: F&B/cafe (beachhead).
- Website: tema gelap + teal, satu aksen teal untuk sinyal data (bukan hiasan).
- Riset kompetitor (RICE AI Consultant, riceai.net) = **inspirasi, jangan salin verbatim**.
- F5 di-skip sementara atas keputusan tim; perannya diambil F9.

---

## 6. Fakta vs dugaan (kejujuran status)

- **Terverifikasi:** isi file di `/home/ubuntu/ai-agency/`; palet `:root` di `index.html`; tidak ada `.git` di folder itu; cron error 402 saldo (log).
- **Klaim dokumen, belum diverifikasi ulang:** status "DONE" tiap fase (berdasarkan `roadmap_status.md` yang tanggalnya masih `[tanggal]`).
- **Dugaan:** LogiSense scope (belum ada detail); timeline soft launch.

---

## 7. Di mana sumber aslinya

- Index pusat: `/home/ubuntu/ai-agency/STARTUP_KIT.md`
- Status roadmap: `/home/ubuntu/ai-agency/roadmap_status.md`
- Log konten tayang: `/home/ubuntu/ai-agency/CONTENT_POSTED_LOG.md`
- Website: `/home/ubuntu/ai-agency/website/` (`SERAH_TERIMA_DEPLOY.md`, `TEMA_OMNISENSE.md`)
- Fase: `fase0_hasil.md` … `fase11` (ada di folder yang sama)
- SOP & template: `SOP_*.md`, `templates/`, `key_questions_*.md`
- Kalkulator: `kalkulator_kesiapan.py`, `kalkulator_harga.py`
- Profil agen (memori): `~/.hermes/memories/USER.md`, `~/.hermes/memories/MEMORY.md`
- Riwayat percakapan Hermes: `~/.hermes/state.db` (tabel `sessions`, `messages`)

---

## 8. Cara berdiskusi dengan Hermes

- Hermes **boleh** membaca file lokal dan menjelaskan konteks.
- Hermes **akan menahan** aksi yang mengubah file / memposting / mengirim pesan / mengubah config sampai Vincent mengonfirmasi langsung.
- Untuk aksi nyata, minta Vincent menjalankannya — atau minta Vincent memberi izin eksplisit.
- Sebutkan tujuan spesifik + file yang dituju supaya hemat waktu.

---

*Dokumen ini tidak berisi rahasia apa pun (tanpa key/token/password). Kalau perlu info yang lebih dalam, baca file sumber di §7 — tapi rahasia tetap tidak boleh ditampilkan.*
