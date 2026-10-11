# Serah terima konsultasi OmniSense v3 — 4 Oktober 2026

Status: prototipe internal, belum dipublikasikan, belum menggantikan halaman utama. Berkas lama dan indeks skor historis tetap jalur legacy. Tujuan agency: konsultasi awal gratis, menentukan kebutuhan, kemudian tim menawarkan pembangunan sistem sesuai scope.

## Sumber dan berkas
- Bank kanonis: `consulting/pertanyaan_v3.json` (kontrak3.0, revision2026-10-04-preproduction-3), 16 screening/32 discovery, 8 dimensi, anchor1–5 dan null untuk unknown.
- Instruksi: `consulting/PLAYBOOK_KONSULTAN.md`, `SPESIFIKASI_WEBSITE_KONSULTASI.md`, templates handoff/pilot; skill consultant/agency-brain/readiness telah dirujukkan ke v3.
- Mesin Python: `consulting/assessment_v3.py`; parser literal read-only `consulting/baca_konsultasi_v3.py`.
- Halaman: `website/konsultasi-v3.html`; aset `assets/konsultasi-v3.js`, `assets/konsultasi-v3-data.js`, `assets/fonts/inter-*.woff2`, `assets/favicon.ico`, serta `privacy.html#konsultasi-v3`.
- Regenerasi dari root ai-agency: `python3 consulting/bangun_data_v3.py`. Jangan menjalankan generator tab legacy untuk v3.

## Alur yang harus dipertahankan
Konteks proses/masalah → 16 jawaban berjangkar atau belum tahu → indeks/rentang dan prioritas → consent → draf WhatsApp berpenanda `[KONSULTASI-OMNISENSE v3]`. Seluruh klaim situs self_reported; parser menolak klaim reviewed dari situs. Tidak ada auto-submit, localStorage, forwarding otomatis, atau persetujuan deploy dari skor. Pengubahan isian membatalkan hasil dan consent. Teks bebas diperlakukan literal, tidak diinterpolasi ke shell.

## Bukti pengujian internal
11 unit tests lulus; 96 contract checks (termasuk82kasus paritas Python/JS),40pemeriksaan UI desktop/mobile,4pesan yang benar-benar dihasilkan browser dan dibaca parser. `test-output/summary.json` menyimpan jumlah tepat. Uji sesi Hermes baru12kasus menunjukkan11respons memenuhi rubrik;1frasa unknown/fakta dikoreksi, kemudian uji fokus3kasus lulus. Tidak merupakan pengujian gateway WhatsApp end-to-end atau kalibrasi empiris.

## Saat tim melakukan build final
1. Integrasikan CTA halaman utama menuju alur v3, gunakan aset/warna/font asli OmniSense. Jangan menanam bank v1/v2 pada tampilan v3.
2. Lakukan smoke test dari pesan WhatsApp nyata sampai respons gateway memakai parser v3, dengan data simulasi; pastikan identitas kanal, mode DM/grup, penanganan riwayat dan handoff benar. Jangan mengklaim diteruskan sebelum ada bukti pengiriman.
3. Bila backend lead/handoff dipilih tim, tetapkan persetujuan, minimal data, akses, retensi dan kebijakan privasi sesuai perilaku sebenarnya. Tidak menambah pelacakan diam-diam.
4. Uji ulang perubahan final dengan unit tests dan `test_consulting_flow.py`; verifikasi tampilan mobile dan privasi. Nomor draf saat ini6288809640700, konfirmasi konfigurasi kanal ketika integrasi.
5. Harga/paket/scope komersial dan publikasi disahkan tim. Jangan deploy dari dokumen ini; arahan ini adalah bahan build.
6. Kalibrasi instrumen memakai dua penilai independen dan bukti kasus lintas industri. Bobot10/20/15/15/10/15/10/5 masih heuristik internal, bukan sertifikasi atau peluang sukses.

## Batas yang masih terbuka
Belum uji gateway aktual, belum integrasi CTA produksi, belum validasi empiris, belum mapping otomatis semua kontradiksi lintas-butir. Konsultan wajib meminta klarifikasi bila jawaban bertentangan. Angka dan contoh dalam paket adalah simulasi, bukan testimoni/hasil klien.

## Revisi3.1 —4Oktober2026
Alur induk ALUR_OPERASIONAL_OMNISENSE.md,playbook3.1,engine assessment_v3.py+decision_v31.py. Bankversion3.1 revisionflow-1;markerWA v3 tetap;3.0kompatibel. Rute pilotdibedakan,reviewrecord/proses/operator/kelayakan/NA/kontradiksi diperiksa. Browser memakai next_questions dari engine. Ledgerworkflow tersedia untuk operator, defaultdry-run, belum terintegrasi gateway dan tidak auto-forward. Bukti3.0 di atas adalah riwayat; hasiluji3.1 dilaporkan terpisah. Buildfinal perlu smoke test gateway, otoritasreviewer/identitaskasus,CTA dan persetujuan/retensi sesuai implementasi sebenarnya.
