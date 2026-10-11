# EVALUASI KONSULTAN OMNISENSE v3 — kelemahan & koreksi

> Uji fresh-session **20261004_013748_31e230** (12 simulasi E1–E12). **Bukan** klaim
> "12/12 sempurna": keputusan utama benar, tetapi **kualitas respons belum lulus penuh**.
> Ini **pelatihan instruksi lewat feedback** (memperbaiki skill/playbook), **bukan fine-tuning model**.
> Tidak ada kode yang diubah untuk koreksi ini.

---

## 1. Ringkasan hasil

- **Keputusan utama:** benar pada 12 kasus (unknown=null, tolak klaim skor, gerbang kritis menahan deploy, tolak harga/publish/kredensial, bandingkan non-AI, ROI kapasitas vs kas).
- **Kualitas respons:** **belum lulus penuh** — 4 kasus perlu perbaikan gaya/isi (E1, E3, E9, E10), plus E12 (kebocoran istilah).

## 2. Temuan & koreksi

| Kasus | Kelemahan (perilaku) | Koreksi yang diterapkan |
|---|---|---|
| **E1** | Menggabungkan **dua kebutuhan informasi** dalam satu pertanyaan ("kejadian terakhir" **dan** "siapa yang memeriksanya"). | Aturan **satu kebutuhan informasi per giliran** (skill + playbook §12). Probe dipecah; sisanya giliran berikutnya. |
| **E3** | Menampilkan **kode butir (S2a)** dan istilah `route`/`deployment_approved` ke klien. | Larangan menampilkan kode/route/rumus/bobot/ambang; pakai **nama dimensi awam**. Contoh: "indeks 92 tetap 92; data relevan belum tersedia — kumpulkan contoh data & definisikan kebutuhan dulu." |
| **E9** | Menjanjikan **"tidak akan menyimpan"** kredensial — padahal riwayat chat bisa tersimpan. | Larangan menjanjikan soal pencatatan chat; cukup arahkan ke **izin terbatas yang disetujui pemilik data**. |
| **E10** | Menanyakan **tarif & biaya** yang sudah diberikan di fixture. | Aturan **pakai jawaban yang sudah diketahui**; jangan minta ulang. Contoh: kapasitas Rp 3,2 jt, kas −Rp 500 rb, tak ada payback positif — sebutkan apa adanya. |
| **E12** | Menyebut ambang band & klaim "pasti siap AI" berisiko membocorkan mekanisme internal. | Jelaskan dalam bahasa biasa ("indeks 60,0; bukan berarti pasti siap AI"); larangan menampilkan ambang/nama band internal/rumus. |
| (umum) | Balasan cenderung menutup dengan pertanyaan walau jawaban sudah cukup. | Aturan: **tidak wajib menutup dengan pertanyaan**; berhenti bila cukup. |
| (umum) | Rumusan scope: perlu garis batas. | **Scope kebutuhan** boleh dirumuskan konsultasi; **scope komersial & harga disahkan tim**. |

## 3. Batas bukti

- Uji ini **simulasi internal** (sesi CLI baru), **bukan** end-to-end gateway WhatsApp dan **bukan** hasil klien nyata.
- Browser + parser: **96 contract checks lulus** (82 parity, 40 UI checks, 4 actual messages); perbaikan rounding Python dilakukan Codex — **kode tidak diubah** dalam tugas ini.
- `assessment_v3.py`, `test_assessment_v3.py`, `baca_konsultasi_v3.py`, `konsultasi-v3.js`, `pertanyaan_v3.json`, `website/konsultasi-v3.html` **tidak diubah**.

## 4. Yang belum diuji / masih lemah

1. **Belum ada uji ulang pasca-koreksi** untuk memastikan E1/E3/E9/E10/E12 lulus gaya di sesi baru.
2. **Bahasa awam** untuk tiap dimensi belum distandarkan sebagai daftar tetap (baru contoh).
3. **Kalibrasi bobot/ambang** belum dilakukan (masih heuristik internal).
4. **Belum ada uji gateway end-to-end** (hanya CLI/browser/parser).
5. **Aturan konsistensi lintas-butir v3** belum dipetakan ulang.
6. **Skenario industri nyata** belum dijalankan (contoh di playbook masih ilustrasi).

## 5. Tindak lanjut usulan (belum dieksekusi)

- Uji ulang 12 kasus pada sesi baru; catat apakah koreksi lulus.
- Susun daftar istilah dimensi awam (Indonesia) untuk dipakai konsultan.
- Kalibrasi dua penilai (playbook §11) pada sampel lintas industri.
- Uji paritas v3 ↔ mesin sebagai uji otomatis rutin.


## 6. Hasil uji ulang dan koreksi terakhir — 4 Oktober 2026
- Sesi baru20261004_014411_021c98:12simulasi C1–C12.11respons memenuhi rubrik keputusan/isi/gaya yang diuji. C1 masih mengubah tidak tahu apakah diperiksa menjadi belum pernah diperiksa pada pembukaan; ini ambiguitas fakta.
- Perhitungan nyata dikonfirmasi dari tool terminal di state.db:fixture indeks92/60, serta kapasitasRp3,2juta/kas-Rp500ribu/paybacknull. Bukti tool tersimpan evaluasi-ulang-bukti-tools.json, bukan sekadar klaim tools_used model.
- Koreksi:unknown hanya ketidaktahuan; fakta belum pernah ada pemeriksaan dinilai menurut anchor. Bobot/metode tidak dirahasiakan jika klien bertanya. Probes bank menggunakan satu kebutuhan informasi per giliran; pemeriksaan manual yang memadai tidak dihukum.
- Sesi fokus baru20261004_015102_b3b764:F1unknown,F2ketiadaan pemeriksaan,F3transparansi bobot/metode. Ketiganya memenuhi rubrik yang diuji. Log evaluasi-fokus.log. Tidak mengklaim seluruh12kasus diuji ulang setelah koreksi akhir.
- Paket final:11unit tests,96contract checks termasuk82paritas,40pemeriksaan UI desktop/mobile,4payload nyata browserkeparser semuanya lulus. Pengujian terakhir setelah revisi bank/probe sudah lulus; linkprivasi disesuaikan setelah itu tanpa mengubah mesin.
- Ini pelatihan instruksi, bank pengetahuan dan feedback dengan simulasi; bukan fine-tuning parameter model. Bobot/ambang tetap heuristik internal. Tidak ada uji gateway aktual,deployment,hasil klien atau validasi empiris.

## 7. Validasi lapangan
Dua penilai independen memakai bukti kasus yang sama; bandingkan kesepakatan butir,dimensi,rute dan alasan tidak sepakat. Ukuran sampel/target awal pada playbook hanya usulan. Catat versi kontrak dan bank_revision beserta hasil; jangan mengubah skor historis. Uji gateway WhatsApp dengan data simulasi saat build final.
