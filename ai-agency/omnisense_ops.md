# Operasional OmniSense — v3.1

Standar aktif: [ALUR_OPERASIONAL_OMNISENSE.md](ALUR_OPERASIONAL_OMNISENSE.md).
Model tetap konsultasi gratis, termasuk pendalaman → implementasi berbayar sesuai scope yang disahkan tim.
Alur: lead → intake → discovery → diagnosis → opsi → handoff → proposal → onboarding → pilot → delivery → adopsi → evaluasi.
Tidak punya angka anggaran atau bukan pemilik usaha tidak otomatis menolak konsultasi; pahami masalah/peran/akses pemilik keputusan dahulu. Kemampuan membayar dan prioritas investasi dibahas untuk scope komersial, bukan bagian skor kesiapan.
Konsultasi baru memakai playbook/bank/engine3.1. Indeks fondasi bukan keputusan solusi, penawaran atau deployment. Evaluasi pemakaian dan hasil berlaku juga untuk engagement tanpa retainer. Jadwal/SLA/paket/biaya mengikuti keputusan yang benar-benar disepakati.
Versi alur lama tersimpan dalam backup; angka dan usulan komersial lama bukan kebijakan baru.

## Perluasan misi — workflow 3.2
Rujukan aktif: consulting/PENGEMBANGAN_MISI_OMNISENSE.md. Visi/misi pemilik tetap; konsultasi termasuk pendalaman gratis, pekerjaan build/install berbayar sesuai scope. Custom berarti proses/data/batas/acceptance sesuai klien, boleh memakai komponen reusable. Peta hulu-hilir dan review diagnosis menyertai roadmap.

Bank/engine/parser situs tetap 3.1. workflow_agency.py versi 3.2 menuntut agent_contract sebelum pilot AI dan agent_validation terikat kontrak/kasus/scope/bank sebelum delivery. Rencana sebelum pilot, hasil setelah pilot. Kontrak tidak mengeksekusi tool atau menjamin permission runtime.

Kasus tersimpan dibaca dengan --read memakai tenant/case dari operator/metadata tepercaya; gunakan fakta tersimpan, open_questions dan next_step, jangan mengaku ingat jika belum ada data. --read read-only. Perubahan baseline/kontrak/owner relevan memerlukan change_record dan membatalkan approval lama. Tidak ada bypass koreksi kecil. Owner adopsi dicatat sebelum onboarding.


## Alur konsultasi aktif — 3.5 (5 Oktober 2026)
Rujukan runtime terbaru: consulting/GATEWAY_KONSULTASI_V35.md; menggantikan deskripsi gateway 3.3/percakapan 3.4 yang historis. Operasi agency tetap workflow 3.2, bank/engine 3.1, revisi 2026-10-04-flow-1.
Website menyediakan screening bertahap atau konsultasi WhatsApp langsung. Draft browser bersifat opt-in, dua jam, tanpa menyimpan consent/kode kasus. Jalur langsung meminta persetujuan sebelum membuat kasus dan tidak mengarang skor. /stop dan /lanjut mempertahankan tahap; risk hold tetap berlaku. Batas panggilan model tersimpan per kasus, dengan timeout dan fallback; ringkasan operator hanya agregat. Intake tetap memerlukan konfirmasi klien dan review tim untuk tahap selanjutnya.
106 tes terisolasi/regresi/ingress simulasi lulus. Browser desktop/mobile dan pemulihan kegagalan API lokal diperiksa; bukan bukti pesan WhatsApp klien nyata, akurasi universal, benchmark performa, atau hasil bisnis. Preview VPS terpasang; domain final belum dipasang.
