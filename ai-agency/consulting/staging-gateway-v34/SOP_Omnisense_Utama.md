# SOP utama OmniSense — workflow 3.2

Rujukan tunggal alur: ALUR_OPERASIONAL_OMNISENSE.md.
Rujukan diagnosis: consulting/PLAYBOOK_KONSULTAN.md; bank/engine3.1.
Konsultasi, termasuk pendalaman, gratis → tim merumuskan penawaran pembangunan sistem sesuai kebutuhan.
Paid Deep Audit dan retainer bukan tahapan wajib tanpa keputusan komersial yang sah. Jangan mengambil tarif dari produk/template lama sebagai harga agency.
Skor tidak menyetujui deploy. Pilih solusi dan jenis pilot dari diagnosis, bukti, nilai dan kelayakan. Handoff diterima tim sebelum proposal; pilot/go-live memerlukan persetujuan berbeda pada scope yang sama. Setelah delivery, ukur adopsi dan dampak terhadap baseline; lanjut/perbaiki/henti sesuai bukti.
Dokumen sebelum revisi adalah arsip dalam backup, bukan aturan aktif.

## Perluasan misi — workflow 3.2
Rujukan aktif: consulting/PENGEMBANGAN_MISI_OMNISENSE.md. Visi/misi pemilik tetap; konsultasi termasuk pendalaman gratis, pekerjaan build/install berbayar sesuai scope. Custom berarti proses/data/batas/acceptance sesuai klien, boleh memakai komponen reusable. Peta hulu-hilir dan review diagnosis menyertai roadmap.

Bank/engine/parser situs tetap 3.1. workflow_agency.py versi 3.2 menuntut agent_contract sebelum pilot AI dan agent_validation terikat kontrak/kasus/scope/bank sebelum delivery. Rencana sebelum pilot, hasil setelah pilot. Kontrak tidak mengeksekusi tool atau menjamin permission runtime.

Kasus tersimpan dibaca dengan --read memakai tenant/case dari operator/metadata tepercaya; gunakan fakta tersimpan, open_questions dan next_step, jangan mengaku ingat jika belum ada data. --read read-only. Perubahan baseline/kontrak/owner relevan memerlukan change_record dan membatalkan approval lama. Tidak ada bypass koreksi kecil. Owner adopsi dicatat sebelum onboarding.
