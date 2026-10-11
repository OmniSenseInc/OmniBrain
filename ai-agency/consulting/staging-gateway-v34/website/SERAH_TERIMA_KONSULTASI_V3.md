# Status gateway konsultasi — 4 Oktober 2026

Rujukan aktif: `consulting/GATEWAY_KONSULTASI_V33.md` (gateway 1.0, bank/engine 3.1, workflow 3.2). CTA preview sudah terhubung ke backend dan adapter WhatsApp. Pesan baru menggunakan kode privat OS, bukan JSON seluruh jawaban. Tes ingress menggunakan transport simulasi; domain final di host lain dan tes pesan WA klien nyata belum dicakup.

## Catatan sebelum pemasangan gateway (historis)

# Serah terima konsultasi OmniSense v3.1 —4Oktober2026

Status: pratinjau internal, belum dipublikasikan/diintegrasihomepage. Model: konsultasi awal gratis→implementasi berbayar sesuai scope disahkan tim.
Sumber: ALUR_OPERASIONAL_OMNISENSE.md; consulting/PLAYBOOK_KONSULTAN.md; pertanyaan_v3.json(version3.1,bank_revision2026-10-04-flow-1),assessment_v3.py+decision_v31.py,baca_konsultasi_v3.py,workflow_agency.py,templates dan spesifikasi.
Halaman: website/konsultasi-v3.html,assets/konsultasi-v3.js,assets/konsultasi-v3-data.js,fontslokalInter,favicon.ico,privacy.html#konsultasi-v3. Regenerasi: python3 consulting/bangun_data_v3.py.
Alur: konteksproses/masalah→16anchoratauunknown→indeks/rentang dan alasanpenahanan/klarifikasi→ringkasankirim→consent→drafWhatsApp. Payloadbaru3.1,marker[KONSULTASI-OMNISENSE v3]tetap. Payload3.0kompatibel,input_versiontercatat;pesanv1/v2parserlegacy,historistidakdiubah.
Reviewrecordsitus tidakditerima sebagaiotoritas. Engine memisahkanpilotfondasi/non-AI/AI,memeriksaproses/operator,diagnosis/alternatif/nilai/kelayakan/pilotplan,reviewrisikotinggi,NAterbatas dan pertentanganbukti. deployment_approvedfalse. Parserread-only,tidakmenulis/mengirim,sent_to_teamfalse. Isianberubah membatalkanhasil/consent. TidaklocalStorage/autosubmit.
Ledger adalah tooloperator dengan tenant/case/revision/scope_version/bank_revision dan journalevent,defaultdry-run,tidaknetwork. Identitasreviewer/operatordiperiksadi luarledger;belumterhubungotomatisgatewayatauCRMlegacy.
Verifikasi aktif3.1:34unit/workflowtests,103contractchecks termasuk89paritas,40UIchecks desktop/mobile,4payloadbrowserkeparser semuanya lulus. Ini bukan ujiWhatsAppnyata,validasiempirisinstrumen atau buktiisolasiseluruhtoolsHermes.
Buildfinal:hubungkanCTA dan adaptertepercaya,ujigatewaydatatest,otoritasreviewer,identitaskasus,handoffyangdiotorisasi,retensi/privasi sesuai perilaku aktual,nomorWA dan alasan keputusan konsisten. Janganmengaktifkanforwarding,publish/deploydari dokumen saja. Tidakada harga/SLAbaru diresmikan.

## Perluasan misi — workflow 3.2
Rujukan aktif: consulting/PENGEMBANGAN_MISI_OMNISENSE.md. Visi/misi pemilik tetap; konsultasi termasuk pendalaman gratis, pekerjaan build/install berbayar sesuai scope. Custom berarti proses/data/batas/acceptance sesuai klien, boleh memakai komponen reusable. Peta hulu-hilir dan review diagnosis menyertai roadmap.

Bank/engine/parser situs tetap 3.1. workflow_agency.py versi 3.2 menuntut agent_contract sebelum pilot AI dan agent_validation terikat kontrak/kasus/scope/bank sebelum delivery. Rencana sebelum pilot, hasil setelah pilot. Kontrak tidak mengeksekusi tool atau menjamin permission runtime.

Kasus tersimpan dibaca dengan --read memakai tenant/case dari operator/metadata tepercaya; gunakan fakta tersimpan, open_questions dan next_step, jangan mengaku ingat jika belum ada data. --read read-only. Perubahan baseline/kontrak/owner relevan memerlukan change_record dan membatalkan approval lama. Tidak ada bypass koreksi kecil. Owner adopsi dicatat sebelum onboarding.
