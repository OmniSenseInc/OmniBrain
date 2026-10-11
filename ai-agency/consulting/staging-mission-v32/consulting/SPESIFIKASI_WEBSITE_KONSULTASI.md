# Spesifikasi konsultasi website OmniSense v3.1

Pratinjau internal: website/konsultasi-v3.html. Belum integrasihomepage atau publish. Tujuan alur: mulai kebutuhan proses → screening opsional → konsultasi adaptif dan bukti → keputusan tim. CTA bukan janji implementasi AI dari skor.
Bankkanonis consulting/pertanyaan_v3.json,version3.1,revision2026-10-04-flow-1. Generator consulting/bangun_data_v3.py. Kontrakbrowser Python/JS sama, band/bobot tetapheuristik. PenandaWA v3 dipertahankan, payload3.0 kompatibel dengan keputusan3.1; input_version/bank_revision dicatat.
Halaman: konteksproses/masalah,16anchoratauunknown,hasilindeks/rentang,penjelasankeputusan paling penting,prioritaspertanyaan,ringkasanyangmudahdibaca,consent,drafWA. Isianberubahmembatalkanhasil/consent. TidaklocalStorage/autosubmit/backendlead.
Parserliteral: --file pathterkendali; ukuran50KB,duplicateJSONditolak; source/reviewklaimsitusditurunkan menjadi self_reported; expert_review,consistency_resolutions,use_case tidak dipercaya dari situs; tidak relevan hanya discoveryterreview. sent_to_teamfalse.
Mesin3.1: reviewrecordlengkap;minimumproses/operator;diagnosis/alternatif/nilai/kelayakan/pilotplan;pilotfondasi/non-AI/AI;reviewrisikotinggidengansyarat;unknownrange;NAterbatas;konflikmemintaklarifikasi. deployment_approvedfalse.
Buildfinal harus menghubungkan CTA,adaptergatewaytepercaya,pencatatankasus/handoff yangdiotorisasi,otoritasreviewer,retensi/hakaksesdanprivasis sesuai perilaku sebenarnya. Jangan menampilkan field/kodemesin ke pengunjung. Jangan mengklaim gateway/ledgerterintegrasi jika belum diuji.
QA: unittest assessment+decision+workflow; Python/JSparitytermasukNA/review/usecase/highrisk; parserklaimpalsu; browserdesktop/mobile; lalu smoke test gatewaydatatest saatintegrasi. Uji teknis bukan validasiempiris instrumen. Kasusevalpercakapanbaru tidak membocorkankuncijawaban.

## Perluasan misi — workflow 3.2
Rujukan aktif: consulting/PENGEMBANGAN_MISI_OMNISENSE.md. Visi/misi pemilik tetap; konsultasi termasuk pendalaman gratis, pekerjaan build/install berbayar sesuai scope. Custom berarti proses/data/batas/acceptance sesuai klien, boleh memakai komponen reusable. Peta hulu-hilir dan review diagnosis menyertai roadmap.

Bank/engine/parser situs tetap 3.1. workflow_agency.py versi 3.2 menuntut agent_contract sebelum pilot AI dan agent_validation terikat kontrak/kasus/scope/bank sebelum delivery. Rencana sebelum pilot, hasil setelah pilot. Kontrak tidak mengeksekusi tool atau menjamin permission runtime.

Kasus tersimpan dibaca dengan --read memakai tenant/case dari operator/metadata tepercaya; gunakan fakta tersimpan, open_questions dan next_step, jangan mengaku ingat jika belum ada data. --read read-only. Perubahan baseline/kontrak/owner relevan memerlukan change_record dan membatalkan approval lama. Tidak ada bypass koreksi kecil. Owner adopsi dicatat sebelum onboarding.
