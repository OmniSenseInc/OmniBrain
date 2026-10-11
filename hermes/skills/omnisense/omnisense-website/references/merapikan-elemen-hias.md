# Merapikan elemen hias di situs OmniSense

## Kelompok angka di `index.html` — hiasan vs data
| Kelompok | Selektor | Status |
|---|---|---|
| Nomor rail 01–08 | `.ix .n` | PERTAHANKAN (urutan bagian) |
| Label kanan rail ("4 langkah", "8 bobot", "1–2 menit", …) | `.ix .c` | hiasan — buang |
| Angka raksasa latar tiap langkah | `.step .ghost` | hiasan, duplikat tag "Langkah 0X" — buang |
| Nomor kartu "Yang Anda terima" | `.ocard .no` | hiasan — buang |
| Nomor kartu Dimensi | `.dcard .no` | PERTAHANKAN |
| Persen bobot dimensi | `.dcard` | PERTAHANKAN (data) |
| Nomor pertanyaan 01–08 | `.pen-no` | PERTAHANKAN (orientasi di form panjang) |
| Tag "Langkah 0X" | `.tag` | PERTAHANKAN |

Jangan hapus kelompok "PERTAHANKAN": nomornya fungsional (orientasi/urutan) dan bobotnya data.

## Pola regex yang dipakai (Python, `re.subn`)
```python
# label kanan rail
h, n = re.subn(r'(<a class="ix" href="#[a-z]+"><span class="n">\d\d</span>[^<]+)<span class="c">[^<]+</span>(</a>)', r'\1\2', h)
# angka raksasa latar
h, n = re.subn(r'\n\s*<span class="ghost" aria-hidden="true">\d\d</span>', '', h)
# nomor kartu, hanya di dalam grid tertentu (batasi dengan blok id-nya)
blok, k = re.subn(r'\n\s*<span class="no">\d\d</span>(?=\n\s*<h3>)', '', blok)
```
Batasi regex ke blok `id`-nya (mis. `#outGrid`) supaya nomor kartu lain tidak ikut terhapus.

## Cek CSS mati setelah elemen hilang
1. Hitung dulu: `len(re.findall(r'class="X"', h))` — kalau 0, aturan CSS-nya boleh dibuang.
2. Cari induk yang masih memakai class itu:
   `re.findall(r'class="(\w+)"[^>]*>\s*<span class="no"', h)`.
3. Hapus aturan CSS-nya dengan `re.subn(r'\n\s*\.ix \.c\{[^}]*\}', '', h)`.
4. Setelah itu pastikan aturan yang HARUS tetap ada masih ada
   (`.dcard .no`, `.case .no`) dan rujukan lama sudah 0.

## Komposit sebelum–sesudah
Tangkap dulu versi lama dari cadangan (`/tmp/before.html`), lalu tiap bagian
(`.ixbar`, `#proses`, `#output`) di dua halaman, dan gabung:
```bash
python3 scripts/gabung_sebelum_sesudah.py --judul "Peta bagian (rail)" \
  --sebelum /tmp/banding-sebelum-rail.png --sesudah /tmp/banding-sesudah-rail.png \
  --keluar pratinjau/rapikan-angka-rail.png
```
Simpan hasilnya di `pratinjau/` supaya bisa dikirim sebagai `MEDIA:` ke WhatsApp.

## Verifikasi akhir yang murah
- `curl -s <link pratinjau>/index.html | grep -c 'class="ghost"'` -> 0 = versi baru sudah tampil.
- `curl -s -o /dev/null -w '%{http_code}' <link>` -> 200 sebelum mengirim link ke Michael.
