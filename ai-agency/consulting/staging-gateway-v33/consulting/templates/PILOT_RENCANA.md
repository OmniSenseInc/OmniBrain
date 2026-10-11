# Rencana pilot OmniSense v3.1

Tenant/clientID · caseID · scope_version · bank_revision · tanggal.
Jenis: fondasi/non-AI/AI. Satu proses,ownerteknis,pemilikkeputusanklien dan operator/adoptionowner.
1. Masalah dan sebab terpilih; bukti pembeda dan ketidakpastian.
2. Baseline nilai/unit/periode/sumber/cakupan; target dan batas mutu yang disepakati.
3. Alternatif yang dibandingkan; nilai dan kelayakan; asumsi/biaya/risiko/dependensi.
4. Scope dan di luar scope; remediates untuk pilotfondasi; data berizin dan review sumber.
5. Periode/sampel/titikcek yang disepakati; metrik sukses,maksimumkesalahan,biaya dan kapasitasreviewmanusia. Angka sampel atau sampling persentase bukan default keamanan.
6. Stop: kondisi gagal,ownerkeputusan dan eskalasi. Rollback: langkah pemulihan,cadangan dan verifikasi.
7. Persetujuanpilot tim+klien: sumber/approved_by/tenant_id/case_id/scope_version/bank_revision. Persetujuanpilot bukan izin go-live.
8. Hasil nyata vs baseline,periode/sampel,evaluator,error/pengecualian,adopsi,biayaaktual. Simulasi diberi label.
9. Keputusan diterima/perbaiki/henti. Go-live perlu keputusan tersendiri; handover dan dukungan punya owner.
Jadwal/SLA/harga hanya yang disepakati; jangan otomatis menjanjikan24jam/30hari atau retainer.

## Kontrak agent dan hasil AI — workflow 3.2
Sebelum pilot AI: agent_contract (lihat agent_contract.py dan fixtures_agent.py, contoh SIMULATION) terikat proses/owner/hash baseline; lingkungan sandbox/shadow, scope data, delegasi, aksi terbatas, pengecualian, escalation/rollback, suite normal/adversarial, outcome dan guardrail. Target/metode/satuan disepakati, tidak dipilih dari bobot kesiapan.
Sesudah pilot dan sebelum delivery: pilot_result.agent_validation memuat tenant_id/case_id/scope_version/bank_revision/contract_sha256, sumber dataset/periode/sample_count/reviewer/review_ref, trace tiap skenario dan nilai metrik dengan satuan/periode/sumber. Skenario blocking gagal atau metrik tidak memenuhi target menahan delivery. Hasil diterima tidak otomatis izin go-live.
