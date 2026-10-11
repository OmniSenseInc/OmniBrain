# Perencanaan & Progress Siklus Tim OmniSense

Semua file di `/home/ubuntu/ai-agency/`. Siklus = 4 pekan (Pekan = Senin-Minggu).

| File | Isi |
|---|---|
| `kalender_perencanaan_siklus1.md` | kalender kerja: peran, cut-off Kamis 12:00, rilis 1x/pekan, target per pekan (tema + gerbang), WIP, risiko, gerbang akhir siklus |
| `jadwal_pertemuan_tim.md` | jadwal 3 pertemuan/pekan + agenda tetap tiap pertemuan + format share report |
| `progress_tim.py` + `progress_tim.json` | pencatat progress (Nathanael & Vincent self-report; Michael dihitung otomatis dari checklist berbobot) |
| `kalender_data.json` + `kalender_omnisense.py` | gambar kalender PNG 1080x1350 (warna/tata letak = template konten OmniSense) + cetak prompt AI |
| `.venv/` | venv berisi Pillow (dibuat via `uv venv .venv && uv pip install --python .venv/bin/python pillow`) |

## Irama pertemuan
- 3x per pekan: 1 OFFLINE (Sabtu 16:00 atau Minggu 19:30, 90 menit) + 2 ONLINE (hari acak Sen-Jum,
  20:00; ONLINE-A Triage & Blocker 30 menit, ONLINE-B Review & Konten 45 menit).
- Offline = tutup pekan: 4 angka -> demo build stabil -> laporan bug -> self-report progress ->
  eksplorasi Vincent (MASUK/TUNDA) -> kunci scope pekan depan -> maks 3 tugas bertanggal.
- Hari online diundi ulang tiap pekan: `--acak-online --pekan N --tgl-senin YYYY-MM-DD`.

## Aturan progress (jangan dilanggar)
- Persen Nathanael & Vincent = SELF-REPORT, jangan ditakar agent/Atong. Yang dibaca: tren antar pekan + alasan.
- Persen Michael = otomatis dari checklist berbobot pekan itu; jangan dikira-kira manual.
- Persen 0-100 per PEKAN. "100%" harus berarti "bisa ditunjukkan di demo".
- Laporan tim masuk dulu ke Atong -> dicatat -> setelah Atong konfirmasi, roadmap + kalender harian dibagikan ke tim.

## Perintah progress
```
python3 progress_tim.py init
python3 progress_tim.py add --orang Nathanael --pekan 1 --persen 40 --catatan "..."
python3 progress_tim.py check --pekan 1 --item 3
python3 progress_tim.py status --pekan 1     # atau: riwayat
python3 progress_tim.py minta --pekan 2      # teks siap tempel ke grup tim
python3 progress_tim.py report --pekan 1     # simpan rekap jadi file
python3 progress_tim.py angka --pekan 1 --must 1 --p0 0 --p1 2 --konten 2 --lead 1 --pilot 0
```

## Gambar kalender
```
.venv/bin/python kalender_omnisense.py --progress-pekan 1 --cta "JADWALKAN KONSULTASI GRATIS"
```
- Palet terkunci: obsidian #09090B, glass #121215, border 1px #27272A, putih #FFFFFF, slate #94A3B8/#64748B;
  radius kartu 20px; area vital Y 135-1215; footer tengah `@omnisense_id • omnisense.id`.
- Tanggal digambar program (akurat). Prompt AI hanya untuk gaya/latar — model gambar sering salah menulis tanggal.
- Kalau ada font Inter Tight/Montserrat: `--font-bold` / `--font-regular`.
