# TEMPLATE PILOT — RENCANA & ACCEPTANCE

> Dipakai setelah discovery + opsi dipilih. Satu pilot = satu proses.
> Tanpa baseline, klaim perbaikan tidak sah.

```
PILOT: <nama>   ·   Klien: <bisnis>   ·   Proses: <satu proses>

A. BASELINE (sebelum)         nilai + unit + periode
   - <mis. waktu rekap: 2,5 jam/hari>
   - <mis. akurasi stok: ~85%>

B. METRIK SUKSES (target)     dari baseline, terukur
   - <mis. waktu rekap < 10 menit/hari>
   - <mis. akurasi stok >= 98%>

C. ACCEPTANCE CRITERIA        disetujui klien TERTULIS
   - <kriteria 1>   - <kriteria 2>

D. PERIODE EVALUASI           <mis. 30 hari>
   Titik cek: <tanggal 1> · <tanggal 2> · review akhir <tanggal>

E. HUMAN REVIEW GATE
   - Keluaran ke pelanggan / keputusan uang: 100% review manusia
   - Tugas rutin internal: sampling <x>% lalu auto

F. KRITERIA HENTI (STOP)
   - Metrik tak tercapai / data tidak layak / adopsi gagal -> berhenti, tanpa memaksa.
   - Keputusan henti diambil oleh: <pemilik keputusan>

G. ROLLBACK
   - Cara mematikan sistem & kembali ke cara lama: <langkah>
   - Kontak darurat: <...>

H. FAILURE MODE (khusus AI, bila relevan)
   - Data bergeser / prompt melenceng -> versikan + rollback
   - API/VPS down -> fallback + info ke klien < 24 jam
```
