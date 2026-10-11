# MASTER BRIEF: OMNISENSE CONTENT TEMPLATE ENGINE

> **STATUS: LOCKED** — patokan wajib untuk semua konten visual OmniSense (Instagram & X).

## 1. Core Specifications & Safe Zone

- **Format:** Single Image Feed Post (Instagram & X).
- **Dimensi & Rasio:** 1080 x 1350 piksel (Rasio 4:5 Portrait).
- **Safe Zone Grid (1:1 Feed Instagram):** Y: 135 px sampai Y: 1215 px. Semua elemen vital (logo, isi frame, dan hook teks) wajib berada di dalam area ini agar tidak terpotong saat audiens melihat *profile feed grid*.
- **Aesthetic Direction:** *Swiss tech editorial*, *minimalist dark mode*, terinspirasi dari kurasi berita cepat ala CryptoWave namun dengan visual kontemporer yang orisinal.

---

## 2. Color Palette & Material Lock

- **Deep Obsidian (Base)** `#09090B`–`#0C0C0E` — 85% — background utama kanvas
- **Pure Contrast (White)** `#FFFFFF` — 12% — logo spiral Omnisense, teks Hook Utama baris 1–2
- **Muted Slate Grey** `#94A3B8` / `#64748B` — 3% — subtitle, bracket category tag, border card
- **Card Surface (Glass)** `#121215` (Opacity 80-90%) — background kontainer frame gambar tengah

> **Prohibited:** Dilarang menggunakan warna hijau neon, gradasi warna-warni, atau ornamen visual 3D yang ramai. Seluruh komposisi wajib berpegang pada estetika monokromatis gelap.

> **AMANDEM (dikunci user):** **DIIZINKAN** latar **skyline kota malam + garis network/node + glow biru-cyan** serta **mockup HP** berisi chat contoh. Tetap wajib dark/premium, logo resmi kanan atas, font Inter/Neue Haas/SF Pro, headline ALL-CAPS, CTA elegant, footer `@omnisense_id`. Contoh live: `assets/contoh-post-news-ai-agent.jpg`.

---

## 3. Layout Grid & Spatial Hierarchy

```
+-------------------------------------------------------------+  Y: 0px
| [CUT-OFF AREA FEED GRID INSTAGRAM: 0 - 135px]               |
|                                                             |
| [CATEGORY TAG]                                (•) omnisense |  Y: 150px
| (Kiri Atas, Muted Grey)                       (Kanan Atas)  |
|                                                             |
|           +-------------------------------------+           |
|           |       FLOATING VIEWPORT CARD        |           |  Y: 280px - 860px
|           |   (Container 1:1 atau 4:3 untuk     |           |  (Area Fokus Visual)
|           |   screenshot / chart / grafis info) |           |
|           +-------------------------------------+           |
|                                                             |
| [HEADLINE HOOK UTAMA BARIS 1]                               |  Y: 920px (Bold White)
| [HEADLINE HOOK UTAMA BARIS 2]                               |
| [Subtitle penjelasan / data pendukung ringkas]              |  Y: 1080px (Muted Grey)
|                                                             |
| [CUT-OFF AREA FEED GRID INSTAGRAM: 1215 - 1350px]           |
| @omnisense_id • omnisense.id                                 |  Y: 1240px (Footer)
+-------------------------------------------------------------+  Y: 1350px
```

- **Header:** Kiri = tag kategori dalam kurung siku `[TAG KATEGORI]` (grey `#94A3B8`, 22–24pt). Kanan = logo spiral konsentris Omnisense + wordmark `omnisense` putih `#FFFFFF`.
- **Middle (Floating Viewport Card):** rounded rectangle (radius 16–24px), outline 1px `#27272A`. Drop zone untuk screenshot, chart, atau ilustrasi headline. **Tanpa mockup HP.**
- **Lower Third:** left-aligned. Headline 1–2 baris sans bold kapital putih `#FFFFFF`; subtitle 1–2 baris `#94A3B8`.
- **Footer:** handle `@omnisense_id` minimalis di bawah.

---

## 4. Typography System

- **Primary Headline / Hook:** Modern Geometric Sans-serif (Syne Bold, Clash Display, Inter Tight Bold, atau Montserrat ExtraBold). Tight letter spacing (-0.02em).
- **Category & Tags:** Clean Monospace atau Medium Sans-serif (Space Grotesk, DM Sans Medium).
- **Body / Subtitle:** Regular Sans-serif (Inter Regular).

---

## 5. System Prompt untuk AI Agent (Copy-Paste Ready)

```text
[SYSTEM INSTRUCTION: OMNISENSE VISUAL ENGINE]

Role: Chief Brand & Visual Layout Architect for Omnisense.

Brand Mandate:
Generate and maintain a consistent, high-impact editorial social media post template for Omnisense tailored for Instagram and X. The aesthetic is clean Swiss tech, dark mode minimalism, data-driven, and strictly monochrome.

Canvas Dimensions:
- Aspect Ratio: 4:5 Portrait (1080 x 1350 px).
- Vital content must strictly remain within the 1080 x 1080 px central square safe zone.

Color System:
- Base Background: 85% Matte Obsidian Black (#09090B).
- Primary Contrast: 12% Crisp Pure White (#FFFFFF) for Omnisense concentric spiral logo and Headline Hook text.
- Secondary Accent: 3% Slate Grey (#94A3B8 to #27272A) for subheadings, category brackets, and 1px container borders.
- Absolute Rule: Never introduce bright multi-colors, greens, or heavy gradients.

Composition Rules:
1. Top Section:
   - Upper-Left: Minimalist bracketed category label (e.g., [OMNISENSE RADAR], [MARKET BRIEF]) in muted grey sans-serif.
   - Upper-Right: Crisp solid white Omnisense concentric spiral circle logo mark paired with lowercase wordmark 'omnisense'.
2. Center Hero:
   - Floating dark glass container card (rounded corners, subtle 1px border) functioning as the dedicated viewport for news graphics, data charts, or feature screenshots. No handheld phone mockups.
3. Lower Third:
   - Left-aligned high-impact typography hierarchy.
   - Line 1 & 2: Ultra-bold sans-serif hook headline in pure white (#FFFFFF), uppercase, compact line-height.
   - Line 3: Concise contextual explainer in slate grey (#94A3B8).
4. Footer:
   - Minimalist handle text '@omnisense_id' anchored cleanly at the bottom.
```
