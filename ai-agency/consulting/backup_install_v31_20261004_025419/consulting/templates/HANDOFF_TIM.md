# TEMPLATE HANDOFF — KONSULTAN → TIM

> Isi semua 9 item. Kirim SATU pesan ringkas. Data antar klien terpisah.
> Bot tidak menutup deal; harga/scope/go-live = keputusan tim.

```
[HANDOFF KONSULTASI] <nama bisnis / kode sesi>
Mode: screening | discovery   ·   Tanggal: <tanggal>   ·   Pengisi: <nama/peran>

1. KEBUTUHAN
   Proses sasaran : <proses>
   Masalah        : <masalah, kata klien>
   Dampak/baseline: <nilai + unit + periode, mis. 2,5 jam/hari>

2. BUKTI
   - "<kutipan persis klien>"
   - Contoh terakhir: <kejadian/tanggal>

3. SKOR TERVERIFIKASI (mode <screening|discovery>)
   Skor hitung ulang : <xx,x>% (<band>)
   Klaim klien      : <xx,x>%  selisih <+/- x,x>   (bila ada)

4. KETIDAKPASTIAN (unknown — belum terverifikasi)
   - <dimensi/soal>: <alasan belum pasti>   (atau: tidak ada)

5. DATA & AKSES (kritis)
   Kualitas : <...>   Ekspor mandiri : ya/tidak   Pemilik data : <siapa>
   Backup/pemulihan : <jadwal + pernah diuji?>   Prasyarat? : ya/tidak

6. ALTERNATIF DIPERTIMBANGKAN
   - Proses/manual : <cocok/biaya/risiko>
   - Alat siap pakai (non-AI) : <...>
   - Otomasi sederhana : <...>
   - AI agent : <...>   Alasan pilih/tunda: <...>

7. ROI BERBASIS ASUMSI (rentang, bukan janji)
   Manfaat  : <jam/kejadian + nilai>   Biaya : <operasional + jam review>
   Asumsi   : <daftar eksplisit>       Sensitivitas : <bila manfaat -50%>
   Titik impas : <...>

8. PERTANYAAN TERBUKA
   - <...>

9. KEPUTUSAN YANG DIPERLUKAN DARI TIM
   - Harga/scope : <...>   Go-live : <...>   Lain : <...>
```

**Bukti terkirim:** `terkirim_ke_tim.ok=true` hanya = bridge menerima pesan, **bukan** jaminan dibaca. Jangan klaim "sudah dibaca".
