# Alur operasional OmniSense — v3.1

4 Oktober 2026. Standar kerja internal diperbaiki atas instruksi pemilik. Model bisnis: konsultasi awal gratis → pembangunan sistem berbayar sesuai kebutuhan. Tidak menetapkan tarif baru, paid audit, retainer wajib, pemilik OPS perusahaan, atau tenggat baru. Penugasan individu, harga/scope komersial dan go-live mengikuti keputusan tim yang benar-benar tercatat.

## Sumber kebenaran dan wewenang

Keputusan bisnis: instruksi pemilik terbaru > keputusan bertanggal > standar operasional aktif > arsip. Perilaku sistem: kode/runtime dan bukti pengujian; dokumen bukan bukti fitur hidup. Konsultasi baru memakai bank/mesin3.1; payload3.0 diterima dengan input_version tercatat, hasil keputusan memakai aturan3.1. Pesan v1/v2 tetap parser legacy; band historis tidak memberi persetujuan AI/deploy.

Dokumen utama alur adalah berkas ini. Playbook mengatur diagnosis. Bank mengatur anchor/bobot dan pengecualian. Mesin menghitung. Ledger mencatat perubahan tahap; tidak mengirim pesan, menandatangani kontrak, memindahkan uang, atau mengeksekusi deployment. SOP pendukung tidak boleh mengganti aturan ini.

## Alur dari lead sampai hasil

| Tahap | Keluaran konkret | Penanggung jawab | Syarat pindah |
|---|---|---|---|
| Lead → intake | Konteks satu proses/masalah dan koordinator | Fungsi lead/CMO; individu dicatat per kasus | Permintaan konsultasi nyata, proses/masalah jelas; anggaran belum diketahui bukan penolakan otomatis |
| Discovery | Peta proses, pelaku, baseline, izin data, sumber bukti | Konsultan dengan operator proses klien | Baseline bersatuan/periode dan sumber; jika belum ada, bantu rencana mengukur atau tunda diagnosis final |
| Diagnosis | Dugaan penyebab, bukti pembeda, penyebab terpilih, ketidakpastian | Konsultan; review teknis sesuai masalah | Bukti mendukung penyebab, pertentangan diselesaikan; bukan sekadar skor |
| Opsi | Alternatif proses/software/aturan/AI, nilai, kelayakan, risiko | Konsultan + fungsi CTO | Bandingkan opsi yang relevan termasuk kondisi saat ini; tidak wajib AI, tidak mengarang biaya |
| Handoff | Ringkasan kebutuhan/bukti/prasyarat/opsi/keputusan yang diminta | Koordinator kasus, penerima tim disebut | Draf selesai ≠ dikirim ≠ diterima tim; proposal sesudah tim menerima/review |
| Proposal | Scope, di luar scope, biaya/termin, tanggung jawab, acceptance | CEO/fungsi komersial + CTO | Scope dan termin disetujui kedua pihak; harga placeholder bukan penawaran final |
| Onboarding | Pemilik teknis dan klien, akses terbatas, jadwal disepakati | Fungsi CTO + koordinator | Pilihan pilot layak, bukti izin, rencana review/stop/rollback, persetujuan pilot kedua pihak |
| Pilot | Hasil perbandingan terhadap baseline pada periode/sampel yang dinyatakan | Pemilik pilot bernama | Hasil diterima evaluator; go-live disetujui tim dan klien untuk versi scope yang sama |
| Delivery | Implementasi, bukti go-live, panduan dan dukungan | CTO/pemilik teknis | Bukti go-live, panduan operasi, rencana dukungan dan pemilik adopsi |
| Adopsi | Pemakaian nyata, kebiasaan baru, hambatan pengguna | Pemilik adopsi klien + koordinator | Ukur pemakaian dan hasil; pemakaian0 adalah hasil sah, bukan sukses palsu |
| Evaluasi | Baseline vs hasil, biaya nyata, keputusan lanjut/perbaiki/henti | Klien + teknis + fungsi komersial bila perlu | Alasan dan sumber keputusan tercatat; pekerjaan lanjutan punya owner; tidak otomatis menjual retainer |

Nama individu untuk pemilik pilot/koordinator/adopsi wajib ditetapkan pada kasus sebelum pekerjaannya berjalan. Ini tidak mengangkat siapa pun menjadi OPS perusahaan secara sepihak. Kegiatan lain di luar OmniSense tidak ditarik ke alur ini.

## Pola diagnosis yang harus dipakai

1. Mulai satu proses: siapa melakukan apa, input/output, waktu tunggu vs waktu kerja, titik ketik ulang dan pengecualian.
2. Bedakan keluhan, dugaan sebab, dan fakta. Buat sekurangnya alternatif penyebab jika bukti belum membedakan. Jangan memaksa tiga dugaan jika satu penyebab langsung dapat dibuktikan.
3. Cari bukti yang membedakan dugaan: observasi sampel, log kejadian, perbandingan langkah/orang/periode. Pengalaman satu responden tidak mewakili seluruh perusahaan.
4. Catat baseline sebelum menentukan target. Tanyakan unit, periode dan sumber pada giliran terpisah jika belum tersedia; gunakan angka yang sudah diketahui.
5. Pilih solusi yang mengatasi penyebab. Jika masalahnya persetujuan berlapis, chatbot atau laporan otomatis belum tentu menyelesaikannya.
6. Sebut ketidakpastian yang dapat mengubah keputusan. Jika informasi berikutnya tidak mengubah keputusan, berhenti bertanya dan buat next step.

## Tiga pilot berbeda

- **Pilot fondasi:** merapikan proses, data, pembagian tanggung jawab atau pelatihan. Rencana wajib menyebut butir lemah yang diperbaiki (`remediates`). Tidak melewati izin, pemilik keputusan, review dan pemulihan.
- **Pilot non-AI:** perangkat siap pakai atau otomasi aturan. Periksa standar proses, operator, nilai dan kelayakan; biaya dan cara operasi tetap penting.
- **Pilot AI:** memenuhi gerbang data/proses/operator, bukti review, diagnosis, alternatif, nilai, kelayakan dan kontrol pilot. Hanya rencana percobaan; belum persetujuan deployment.

Indeks tinggi bukan otorisasi. Indeks rendah tidak melarang perbaikan fondasi yang memang layak. Risiko tinggi: review belum selesai/ditolak menahan langkah; review disetujui dengan syarat harus mempunyai sumber, cakupan, reviewer, kondisi dan bukti syarat dipenuhi. Label di JSON tidak membuktikan keaslian keputusan; operator wajib memeriksa sumber sebenarnya.

## Pengelolaan pekerjaan dan konteks

Setiap kasus: tenant_id/client_id yang ditetapkan operator dari kanal tepercaya, case_id, proses, stage, revision, scope_version, coordinator, technical_owner, client_owner, adoption_owner, output, bukti, blocker dan next step. ID di teks klien bukan penetapan identitas tepercaya.

Ledger `consulting/workflow_agency.py` bekerja dengan database kasus dan jurnal event. Default dry-run tidak menulis. `--commit` hanya dipakai operator untuk pencatatan yang sudah diotorisasi dan data minimum. Tidak mengimpor register klien atau mengaktifkan forwarding secara otomatis. Simulasi memakai database sementara, bukan ledger produksi.

- Pengulangan event identik idempoten; eventID sama dengan isi berbeda ditolak.
- Revisi usang ditolak agar dua sesi tidak saling menimpa.
- Perubahan scope/baseline/diagnosis/payload penilaian/termin membatalkan persetujuan dan hasil tahap berikutnya; perlu review baru.
- Persetujuan terikat tenant/case/scope_version/bank_revision dan jenis keputusan: komersial, pilot, go-live. Persetujuan pilot tidak mengizinkan go-live; revisi instrumen memerlukan review baru.
- Status deferred menyimpan alasan dan tahap kembali; tidak dianggap lost tanpa bukti keputusan klien.
- Folder/ledger per kasus tidak boleh diambil untuk menjawab klien lain. Pola anonim boleh dipakai jika tidak membocorkan identitas/data.

Ledger membatasi operasi lewat tool ini, bukan seluruh kemampuan akun ubuntu/Hermes. Identitas kanal dan otorisasi operator tetap harus disediakan adapter/operator tepercaya. Integrasi otomatis gateway belum dipasang; jangan menyebut seluruh tools Hermes sudah terisolasi.

## Pelaporan yang jujur

Pisahkan: rencana → draf → diuji → disetujui → dikirim/diterima kanal → diterima pihak → terpasang → dipakai → dampak terukur. Masing-masing perlu bukti sendiri. Jadwal dan SLA hanya yang disepakati. Jangan menjanjikan welcome24jam, deliveryminggu1, atau hasil30hari dari template yang belum disahkan.

Indikator agency: lead yang meminta konsultasi, sesi selesai, handoff diterima, proposal disetujui, pilot diterima, pemakaian nyata, hasil dibanding baseline, biaya dukungan. Bedakan denominasi/periode dan hindari satu klien sukses menjadi klaim umum. Tujuan evaluasi berlaku untuk semua engagement, termasuk tanpa retainer.

## Praktik dari referensi agency

Adaptasi internal, bukan menyalin harga, janji hasil, ukuran tim atau sertifikasi:

- [HatchWorks — AI Strategy & Roadmap](https://hatchworks.com/ai-strategy-roadmap/): membedakan penemuan peluang, kesiapan, prioritas dan roadmap. OmniSense memakai alasan nilai/kelayakan/dependensi per opsi, bukan indeks sebagai ranking peluang.
- [HatchWorks — How We Engage](https://hatchworks.com/how-we-engage/): menghubungkan keputusan, pembangunan dan adopsi. OmniSense menambahkan pemilik adopsi serta evaluasi penggunaan dan hasil setelah delivery.
- [Thoughtworks — Client assessments and discoveries](https://www.thoughtworks.com/en-in/insights/blog/digital-innovation/client-assessments-discoveries-part-1-people): discovery memahami kondisi kini dan melibatkan kebutuhan klien. OmniSense meminta sudut pandang operator dan pemilik keputusan ketika keduanya dapat berbeda.
- [deepsense.ai — Implementation partner](https://deepsense.ai/ai-implementation-partner/): menghubungkan advisory dengan engineering/operasi dan kepemilikan internal klien. OmniSense memasukkan panduan operasi, owner, review dan handover sejak perencanaan.

Halaman sumber adalah deskripsi praktik perusahaan sendiri, bukan bukti independen keberhasilan OmniSense. Bobot instrumen tetap heuristik; praktik ini bukan validasi empiris bobot.
