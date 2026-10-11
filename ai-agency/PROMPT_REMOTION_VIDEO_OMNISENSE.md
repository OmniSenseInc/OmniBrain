# PROMPT UNTUK AI AGENT REMOTION — VIDEO MARKETING OMNISENSE

> Cara pakai: tempel **seluruh isi dokumen ini** ke AI agent Remotion kamu.
> Bagian 1 = instruksi kerja. Bagian 2 = briefing Omnisense (materi isi video).
> Jangan minta agent mengarang angka atau testimoni — lihat §10.

---

# BAGIAN 1 — INSTRUKSI KERJA

## 1.1 Peran & tujuan
Kamu adalah motion designer + video engineer. Bangun **satu video marketing** untuk
Omnisense memakai **Remotion (React + TypeScript)**. Video menjelaskan: apa itu
Omnisense, alur kerjanya, keunggulannya, dan diakhiri ajakan bertindak.

Utamakan **kejelasan pesan** di atas efek visual. Kalau harus memilih antara efek
keren dan pesan yang jelas — pilih pesan yang jelas.

## 1.2 Spesifikasi output (WAJIB)
| Item | Nilai |
|---|---|
| Framework | Remotion, 1 project |
| Nama komposisi | `OmnisenseMarketing` |
| Aspect ratio | **9:16** (Instagram Reels / Story) |
| Resolusi | **1080 × 1920** |
| FPS | **30** |
| Durasi | **45 detik** (1.350 frame) |
| Codec | H.264 + AAC, bitrate tinggi |
| Bahasa | **Indonesia** (VO Indonesia, teks Indonesia) |
| Tone | **Profesional tapi hangat** — tenang, percaya diri, tidak hard-sell |

## 1.3 Struktur file
```
src/Root.tsx                     # registrasi komposisi
src/OmnisenseMarketing.tsx       # rangkaian scene + audio
src/config.ts                    # SCENES: nama, durasi, urutan (satu sumber kebenaran)
src/scenes/01-Hook.tsx
src/scenes/02-Problem.tsx
src/scenes/03-Intro.tsx
src/scenes/04-HowItWorks.tsx
src/scenes/05-Advantages.tsx
src/scenes/06-Readiness.tsx
src/scenes/07-CTA.tsx
src/components/Logo.tsx
src/components/ScoreBar.tsx      # bar dimensi bergaya alat ukur
src/components/TextReveal.tsx
public/logo-mark-white-1024.png  # dari brand/logo-mark-white-1024.png
public/audio/vo-*.mp3
public/audio/bgm.mp3
```
Semua durasi scene didefinisikan di `src/config.ts` supaya bisa diubah tanpa
membongkar animasi.

## 1.4 Aturan teknis Remotion
- Masuk: `spring()` untuk elemen utama, `interpolate()` untuk gerak linear.
- Transisi antar scene: **satu pola saja** untuk semua (mis. slide 12 frame + fade).
  Jangan campur 5 jenis transisi.
- Semua teks utama tampil **minimal 24 frame** supaya terbaca.
- Maksimal **2 baris teks** di layar sekaligus. Satu ide per layar.
- Kontras teks vs latar **minimal 4.5:1**.
- Animasi angka: pakai `tabular-nums` (JetBrains Mono) supaya digit tidak goyang.
- Semua aset dari `public/`, **tidak ada URL eksternal** saat render.
- Musik di-duck ke **30%** saat voice-over jalan.
- Sinkronkan pergantian scene dengan beat musik.
- Kalau data kurang, tulis `// TODO: butuh data X` dan lanjutkan. **Jangan mengarang.**

## 1.5 Struktur video (7 scene, total 1.350 frame @30fps)
| # | Scene | Frame | Detik | Isi |
|---|---|---|---|---|
| 1 | HOOK | 0–120 | 0–4s | Pertanyaan tajam soal masalah. Tanpa logo. Tujuan: stop scroll. |
| 2 | PROBLEM | 120–330 | 4–11s | 3 gejala masalah bisnis, muncul cepat berurutan. |
| 3 | INTRO | 330–510 | 11–17s | Nama + slogan + 1 kalimat "apa itu Omnisense". Logo muncul di sini. |
| 4 | HOW IT WORKS | 510–840 | 17–28s | Alur 4 langkah, animasi bernomor. Ini scene inti. |
| 5 | KEUNGGULAN | 840–1080 | 28–36s | 3 kartu keunggulan + manfaatnya. |
| 6 | KESIAPAN | 1080–1230 | 36–41s | Tunjukkan 8 dimensi + skor contoh 68% = "Layak Lanjut". |
| 7 | CTA | 1230–1350 | 41–45s | Logo, slogan, ajakan konsultasi gratis, URL. Tahan min. 3 detik. |

---

# BAGIAN 2 — BRIEFING OMNISENSE (materi isi video)

## 2.1 Apa itu Omnisense — satu paragraf
Omnisense adalah **mitra yang membereskan sistem bisnis** — mulai dari mengukur
kesiapan, lalu membangun sistem digital dan **AI agent custom yang mengambil alih**
pekerjaan yang selama ini manual.

Omnisense **bukan** penjual software kotak-kotak, **bukan** SaaS. Yang dijual adalah
**pengukuran + pembangunan sistem**. Pintu masuknya *assessment* (penilaian kesiapan);
pendapatannya dari **membangun & memasang sistem**.

**Slogan:** *"Where Traditional Systems end, AI Agents Begin."*
(Boleh diterjemahkan di layar: *"Di titik sistem lama berhenti, AI agent mulai bekerja."*)

## 2.2 Identitas inti
**Visi**
> Menjadikan digitalisasi dan AI agent sebagai fondasi operasional setiap bisnis —
> menggantikan cara kerja tradisional yang sudah tidak relevan.

**Misi**
> Kami mengukur kesiapan bisnis, menemukan titik di mana sistem tradisional berhenti
> berfungsi, lalu membangun digitalisasi penuh dan AI agent custom yang mengambil alih.

**Nilai (4)**
1. **Custom, bukan template** — dibuat untuk bisnis itu, bukan disalin.
2. **Jujur & independen** — tegas kapan data belum siap, kapan sudah.
3. **Penerus, bukan pembantu** — menggantikan yang mentok, bukan menambal.
4. **Berbasis data** — keputusan dari angka, bukan perasaan.

**Pernyataan positioning**
> Omnisense adalah mitra digitalisasi untuk bisnis Indonesia yang sistem lamanya sudah
> tidak relevan — mulai dari mengukur kesiapan, lalu membangun digitalisasi penuh dan
> AI agent custom yang mengambil alih.

## 2.3 Model bisnis & alur (INI INTI VIDEO)
```
1. KONSULTASI GRATIS  ← selalu gratis, termasuk pendalaman
   → memetakan: mulai dari mana, langkahnya apa
2. PILIH JALUR
   → pasang FNBSense (standar F&B, cepat)  ATAU  bangun sistem custom
3. PEMBANGUNAN & PEMASANGAN  ← di sini nilai ekonominya (berbayar)
4. DUKUNGAN BERKELANJUTAN
```
Aturan tegas:
- Konsultasi **gratis, selalu gratis**. Ini pesan yang harus jelas di video.
- Yang **berbayar** = membangun & memasang sistem, sesuai scope yang disepakati.
- Harga/scope final = keputusan tim manusia. **Video tidak menyebut angka harga.**

## 2.4 Produk
| Produk | Peran |
|---|---|
| **Omnisense** | Wajah utama / payung brand |
| **FNBSense** | Produk standar untuk F&B (cafe/resto): web POS per outlet + backend agent |
| **LogiSense** | Anak produk (logistik) — masih dalam pengembangan |

**Aturan:** FNBSense & LogiSense adalah **anak produk**. Di video, keduanya disebut
paling banyak **sekali**, sebagai catatan kaki — jangan disejajarkan dengan Omnisense.

## 2.5 Target pasar & masalah inti
**Sasaran awal:** pemilik cafe & resto skala kecil–menengah (1–3 outlet).
Jangka panjang: seluruh bisnis.

**Satu akar masalah** (semua keluhan adalah gejalanya):
> Operasional berjalan tanpa data yang bersih, tersambung, dan otomatis.

Gejalanya (dipakai untuk Scene 2 — PROBLEM):
1. Tidak tahu untung/rugi harian yang akurat (data tercecer di buku kas, WhatsApp, Excel).
2. Stok bahan sering habis atau telat diisi saat jam ramai.
3. Habis 1–2 jam sehari hanya untuk rekap laporan manual.
4. Keputusan menu/stok/ekspansi berdasar tebakan, bukan data.

**Solusinya:** AI agent custom yang **dibangun khusus per customer**, membereskan akar
(data) sesuai cara kerja masing-masing bisnis — bukan solusi seragam untuk semua.

## 2.6 Framework kesiapan — 8 dimensi (untuk Scene 6)
Penilaian gratis → skor 0–100 → kategori.

| Dimensi | Bobot |
|---|---|
| Kesiapan data | 20% |
| Infrastruktur | 15% |
| Digitalisasi proses | 15% |
| SDM | 15% |
| Strategi | 10% |
| Organisasi | 10% |
| Tata kelola | 10% |
| Anggaran | 5% |

**Kategori:** Siap Penuh · Layak Lanjut · Konvensional · Awal · Sangat Awal
Contoh di layar: **skor 68% = "Layak Lanjut"** (pakai angka ini, sudah sesuai SOP).

**Wajib jujur:** indeks menilai **fondasi**, bukan jaminan sukses. Skor **tidak**
menyetujui deploy. Bobot masih heuristik internal, belum kalibrasi empiris —
jangan diklaim sebagai bukti ROI.

## 2.7 Identitas visual
**Latar:** Obsidian `#09090B` (konten/poster) · Navy `#081726` (permukaan website)
**Aksen tunggal:** Teal `#14B8A6` — **hanya** untuk data/sinyal (skor, bar, rail,
angka). Maksimal ±5% luas frame. **Bukan hiasan.**
**Teks utama:** Putih `#FFFFFF` · **Teks sekunder:** Slate `#94A3B8`

**Tipografi:**
- Headline: Outfit (atau Inter 900 ALL-CAPS untuk gaya konten)
- Body: Inter 400/500
- Angka/label: JetBrains Mono, `tabular-nums`
- Sudut: 8px / 14px / 18px

**Logo (LOCKED — pakai file, jangan gambar ulang):**
`brand/logo-mark-white-1024.png` — mark spiral putih + wordmark `omnisense`
huruf kecil, Inter SemiBold 600, letter-spacing -0.01em.
Ruang bebas min. 25% tinggi mark. Ukuran minimum 20 px.

**Tone visual:** gelap, tenang, monoline, editorial, presisi — rasa "laporan cetak
yang bagus", bukan "landing page SaaS". Motif: **bahasa alat ukur** (skor, bar,
garis progres, angka).

## 2.8 Nada komunikasi
**LAKUKAN:**
- Bahasa sehari-hari untuk **pemilik usaha**, bukan untuk CTO.
- **Tunjukkan angka lebih dulu**, jelaskan setelahnya (skor → celah → langkah).
- Kalimat pendek. Premium, tenang, tanpa hard-sell.
- Sebut angka kalau memang ada angkanya.

**JANGAN:**
- ❌ Kata "usaha kecil" / "UMKM kecil" (merendahkan) → pakai **"bisnis"** / "bisnis lokal".
- ❌ Jargon: "transformasi", "solusi end-to-end", "leverage AI", "revolusioner".
- ❌ Gradient ungu–biru, aurora blob, glow berlebihan (penanda "situs AI generik").
- ❌ Glitch / RGB split, emoji berlebihan, hard-sell, klaim absolut.
- ❌ Menonjolkan FNBSense sejajar dengan Omnisense.

## 2.9 Naskah voice-over (draf — sesuaikan, max 12 kata/kalimat)
**Scene 1 — HOOK**
> "Kalau kamu masih menebak untung-rugi harian, masalahnya bukan di menunya."

**Scene 2 — PROBLEM**
> "Data tercecer di buku, chat, dan Excel."
> "Stok habis justru saat jam ramai."
> "Dua jam sehari habis cuma untuk rekap."

**Scene 3 — INTRO**
> "Omnisense. Kami membereskan sistem bisnis kamu — sampai datanya bisa dipercaya."

**Scene 4 — HOW IT WORKS**
> "Mulai dari konsultasi gratis." → "Kami ukur kesiapan bisnis kamu."
> → "Kami bangun sistem dan AI agent khusus." → "Agent-nya yang mengambil alih kerja manual."

**Scene 5 — KEUNGGULAN**
> "Dibuat khusus untuk bisnis kamu, bukan template."
> "Kami bilang jujur kalau datanya belum siap."
> "Kami menggantikan yang mentok, bukan sekadar menambal."

**Scene 6 — KESIAPAN**
> "Delapan dimensi, satu angka. Contohnya, enam puluh delapan persen — layak lanjut."

**Scene 7 — CTA**
> "Konsultasi pertama gratis. Cek kesiapan bisnis kamu di omnisense.id."

## 2.10 JANGAN DIKLAIM (penting — ini belum terbukti)
Data berikut **belum ada** dan **tidak boleh dikarang** di video:
- ❌ Jumlah klien, jumlah user, logo klien, testimoni — belum ada bukti validasi pelanggan.
- ❌ Angka ROI, "meningkatkan profit X%", "hemat Y jam" sebagai **hasil nyata**.
- ❌ Klaim "sudah dipakai ratusan bisnis".
- ❌ Harga, paket, atau besaran diskon apa pun.
- ❌ "Terbaik", "nomor 1", "satu-satunya di Indonesia".
- ❌ Nama tim (Vincent/Nathanael/Michael) dan detail internal apa pun.

Yang **boleh** diklaim (karena memang faktual): slogan, nilai, cara kerja 4 langkah,
8 dimensi + bobotnya, konsultasi gratis, dan contoh skor ilustratif (68% = Layak
Lanjut) selama ditandai sebagai **contoh**.

## 2.11 Aset yang harus disiapkan
| Aset | Sumber |
|---|---|
| Logo putih 1024px | `ai-agency/brand/logo-mark-white-1024.png` |
| Voice-over Indonesia | TTS / rekaman manusia, tone hangat profesional |
| Musik latar | Bebas royalti, instrumental, tempo sedang, tidak ramai |
| Font | Outfit, Inter, JetBrains Mono (self-host di `public/fonts/`) |

## 2.12 Deliverable yang diminta dari agent
1. Tabel ringkasan scene + durasi.
2. Daftar file yang dibuat.
3. Kode lengkap semua file, siap `npm run build` + render.
4. Naskah VO final + teks on-screen per scene.
5. Checklist verifikasi sebelum render.

---

## CATATAN KONFLIK (perlu diputuskan tim)
1. **Warna aksen:** dokumen brand resmi menyebut teal `#14B8A6`; indeks internal
   menyebut `#14B8A4`. Prompt ini pakai `#14B8A6` (dokumen brand = sumber resmi logo).
2. **Kata "digitalisasi":** masuk daftar jargon yang dilarang untuk konten publik,
   tapi dipakai di visi/misi/positioning. Untuk **voice-over video**, pakai bahasa
   awam ("membereskan sistem", "sistem yang ambil alih kerja manual") dan simpan
   kata "digitalisasi" hanya untuk teks resmi jika diperlukan.
3. **Konsultasi 32** (mode pendalaman berbayar) — tarifnya belum ditetapkan.
   Jangan disinggung di video.
