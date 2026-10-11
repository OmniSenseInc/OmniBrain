# LOGO OMNISENSE — ASET RESMI (LOCKED)

> **Status: LOCKED.** Semua pemakaian logo OmniSense (website, poster IG, deck, dokumen)
> wajib memakai berkas di dokumen ini. Dilarang menggambar ulang mark secara manual
> (inline SVG buatan sendiri) — itu sumber ketidakkonsistenan.

## 1. Sumber resmi

| Peran | Berkas |
| --- | --- |
| Sumber mentah dari user | `logo_sumber.jpg` (1254x1254, mark putih di atas hitam) |
| Mark putih + alpha (transparan) | `logo_omnisense_white.png` (682x687, dipakai pipeline poster) |
| Master turunan rapi | `brand/logo-mark-white-1024.png` (684x690, alpha bersih) |
| Skrip pembuat turunan | `tetapkan_logo.py` (Pillow di `.venv`) |

Satu sumber kebenaran: **`logo_sumber.jpg`**. Semua berkas lain adalah turunan —
kalau logo resmi berubah, jalankan ulang `tetapkan_logo.py`, jangan edit turunannya.

## 2. Bentuk mark

- Spiral putih: **inti padat** di tengah + **lengan spiral ~2 lilitan**, ujung membulat (round cap).
- Warna resmi: putih `#FFFFFF` di atas latar gelap (obsidian `#09090B`).
- Varian aksen: teal `#14B8A6` — hanya untuk aksen kecil, bukan warna default mark.
- Varian gelap `#09090B` untuk latar terang (dokumen, invoice, slide putih).
- Wordmark: huruf kecil **`omnisense`**, Inter SemiBold 600, letter-spacing -0.01em.

## 3. Berkas turunan (`brand/`)

| Berkas | Pakai untuk |
| --- | --- |
| `logo-mark-white-1024.png` | master, cetak besar, sumber turunan baru |
| `logo-mark-white-512.png` | poster IG/4:5, deck |
| `logo-mark-white-256.png` | header website (retina 2x), dokumen |
| `logo-mark-white-128.png`, `-64.png`, `-32.png` | ikon kecil, favicon, watermark |
| `logo-mark-teal-512.png` | aksen/branding khusus |
| `logo-mark-obsidian-512.png` | latar terang |
| `favicon.ico`, `favicon-32.png`, `favicon-16.png` | tab browser |
| `website/assets/apple-touch-icon-180.png` | ikon iOS/shortcut |

## 4. Aturan pakai

- Ukuran minimum mark: **20 px** (digital), 8 mm (cetak). Di bawah itu spiral mulai menggumpal.
- Ruang bebas (clear space) minimum: **25% tinggi mark** di semua sisi.
- Jangan: regangkan (non-uniform scale), ganti warna jadi warna di luar palet, tambah
  bayangan/glow/outline, atau menaruh mark putih di latar terang tanpa varian gelap.
- Mark tanpa wordmark untuk ruang sempit (favicon, avatar). Mark + wordmark untuk header,
  poster, dan dokumen resmi.

## 5. Pemakaian saat ini

| Tempat | Berkas |
| --- | --- |
| Website `website/index.html` header | `website/assets/logo-mark-white-256.png` (tampil 26x26) |
| Favicon website | `website/assets/favicon.ico` + `-32.png` + `-16.png` + apple-touch-icon |
| Pipeline poster IG (`prompt_kalender_ai.py`, `kalender_omnisense.py`, `konten_harian.py`) | `logo_omnisense_white.png` |

## 6. Cara bikin turunan baru

```bash
cd /home/ubuntu/ai-agency
.venv/bin/python tetapkan_logo.py          # regenerasi semua berkas di brand/
```

Untuk ukuran lain, pakai Pillow dari master:

```python
from PIL import Image
m = Image.open("brand/logo-mark-white-1024.png")
m.resize((N, round(N * m.height / m.width)), Image.LANCZOS).save("keluaran.png")
```
