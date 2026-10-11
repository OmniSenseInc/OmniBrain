# Pengembangan OmniSense sesuai visi dan misi — operasi 3.2

4 Oktober 2026. Visi/misi/positioning pemilik dipertahankan. Sumber: fase3_visi_misi.md, fase1_bisnis_inti.md, fase4_positioning.md. Bank dan mesin penilaian tetap 3.1; perluasan ini adalah workflow 3.2 dan protokol kontrak agent 1.0.

## Makna yang mengendalikan keputusan
- Digitalisasi menjadi fondasi: proses, sumber data yang berwenang, input/output, penanggung jawab, integrasi dan penanganan kesalahan harus jelas.
- Menemukan titik sistem tradisional berhenti berfungsi: buktikan batas dengan kejadian/angka, bukan menganggap Excel, manusia atau sistem lama selalu buruk. Bila masih memadai, jelaskan manfaat/biaya perubahan dan alternatif.
- AI agent custom mengambil alih tugas yang didelegasikan: tentukan hasil, aksi, batas, pengecualian, dan akuntabilitas. Otonomi meningkat berdasarkan bukti, bukan skor kesiapan. Manusia tidak perlu menyetujui setiap aksi rutin yang sudah didelegasikan dan benar-benar dibatasi runtime.
- Custom adalah kesesuaian proses/data/integrasi/batas/acceptance dengan klien. Komponen reusable boleh dipakai; solusi bisnis tidak disalin tanpa diagnosis. Tidak harus membuat semua kode dari nol atau menggunakan vendor tertentu.
- Jujur dan independen: konsultasi tetap gratis, termasuk pendalaman. Pembangunan/pemasangan sistem sesuai scope adalah pekerjaan berbayar. Kedalaman/jadwal mengikuti kapasitas dan kesepakatan, bukan mengubah konsultasi menjadi fee. Tidak menjanjikan pembangunan gratis.
- Data-driven berarti angka dengan unit/periode/sumber, alternatif sebab dan bukti pembeda. Skor dapat dihitung tanpa berarti bobotnya sudah divalidasi. Klaim pembeda terhadap pesaing perlu sumber, bukan judul positioning saja.

## Peta sistem sebelum roadmap
Mulai satu proses agar percakapan fokus, lalu petakan hubungan hulu-hilir: pemicu, pelaku, input, sumber resmi, proses inti, pengecualian, output dan sistem penerima. Tanyakan apakah perbaikan di satu titik menambah pekerjaan/errors di titik lain. Bentuk roadmap dari dependensi, bukan daftar tools: fondasi yang diperlukan → kandidat pilot dengan nilai terukur → adopsi → perluasan proses berikutnya. Target scope sekarang dan visi sistem akhir dicatat terpisah.

Periksa pekerjaan yang dihentikan/diganti, kapan sistem lama bisa dinonaktifkan, siapa menerima hasil baru, dan kapan perlu operasi paralel. Jangan menggandakan beban pengguna tanpa rencana akhir. Pemilik engagement menetapkan acceptance dan waktu yang masuk akal; tidak ada tenggat/sampel universal yang dikarang.

Template: templates/PETA_TRANSFORMASI.md dan templates/REVIEW_DIAGNOSIS.md. Ini artefak review manusia, bukan algoritma yang membuktikan sebab secara otomatis.

## Kontrak kerja AI agent
Simpan agent_contract pada kasus operator sebelum pilot AI. Rujukan kode: agent_contract.py; contoh synthetic: fixtures_agent.py. Kontrak memuat versi 1.0, proses/objective/owner, sumber delegasi, hash baseline kasus, lingkungan pilot sandbox/shadow, scope/minimisasi/izin/retensi data, aksi, eskalasi dan rollback.

Mode aksi: observe, draft, execute_bounded, human_required, forbidden. execute_bounded wajib effect_limit, authorization_ref dan idempotency_ref. Aksi yang ditandai requires_human tidak boleh sekaligus autonomous. Batas harus diterapkan pada tool/runtime oleh tim saat build, bukan hanya ditulis dalam JSON. Ledger dan validator tidak mengubah permission atau mengeksekusi aksi.

Kontrak mencakup penanganan ambigu, data kurang, kegagalan tool, instruksi berbahaya dalam data, dan di luar scope. Suite evaluasi memuat kasus normal serta lima kategori tersebut. Kegagalan skenario blocking tidak boleh disembunyikan dalam rata-rata.

Metrik outcome dan guardrail terpisah: definisi, satuan, metode, baseline bila outcome, target dan sumber kesepakatan. Ambang mengikuti kasus; tidak ada persentase/model/vendor universal. Angka baru diuji pada sampel yang dinyatakan, tidak menjamin semua transaksi mendatang.

## Gerbang pilot dan hasil
Sebelum masuk pilot: rencana/kontrak/suite, kelayakan dan approval pilot sudah ada; hasil belum diwajibkan. Pilot awal sandbox/shadow tidak membuat aksi produksi. Setelah pilot: agent_validation berisi trace/reviewer tiap skenario, hasil metrik, periode, sumber dataset, cakupan sampel dan review. Hasil terikat hash kontrak, tenant/kasus/scope_version/bank_revision; satuan/periode sesuai metode yang disepakati. Nilai metrik dibanding target; skenario blocking gagal menahan delivery meski status ditulis accepted.

Delivery/go-live tetap memerlukan persetujuan terpisah tim dan klien. Kelulusan record bukan autentikasi reviewer/trace atau izin semua tools. Operator meninjau artefak nyata. Stage delivery berarti pekerjaan implementasi boleh dimulai; bukti go-live baru dituntut sebelum adoption.

Perubahan kontrak, baseline, diagnosis, scope, owner relevan dan peta proses membatalkan approval/hasil lama. Koreksi fakta material memerlukan change_record berisi reason/source_ref/recorded_by dan tetap memicu review ulang. Jangan menjadikan label koreksi kecil sebagai bypass. Metadata nonmaterial seperti next_step/open_questions tidak membatalkan scope; journal menjaga riwayat event.

## Kesinambungan antar sesi
Untuk kasus yang sudah ada, operator memberi tenant/case dari metadata tepercaya lalu membaca:
python3 consulting/workflow_agency.py --tenant ID_TENANT --case ID_KASUS --actor ID_OPERATOR --role operator --read

--read tidak membuat database, mengubah state atau mengirim pesan. Keluaran berisi stage/revision/scope_version, konteks faktual yang tersimpan, diagnosis, pertanyaan terbuka, next_step, koreksi terakhir dan ringkasan approval tercatat. Tidak membaca kasus lain. Ini pembatasan tool ledger, bukan isolasi seluruh Hermes. Jangan mengambil ID otoritatif dari teks pelanggan.

Jika found=false atau field belum ada, nyatakan konteks belum tersimpan; jangan mengaku ingat. Tidak meminta ulang fakta yang sudah ada tanpa alasan (misalnya periode berubah). Koreksi total durasi versus waktu aktif harus memengaruhi baseline/ROI; jangan menciptakan angka biaya, FTE, atau kas. Penetapan sumber resmi data dan perubahan source-of-truth perlu keputusan klien.

## Gaya konsultasi dan mutu penalaran
Balasan awal biasanya 2–4 kalimat, satu kebutuhan informasi paling menentukan. Diagnosis adalah hipotesis sampai bukti membedakan; pertanyaan diarahkan pada yang bisa mengubah keputusan. Status gratis/paid, rencana/hasil, format input, biaya aktual dan kewenangan klien tidak boleh ditebak.

Audit teknis membaca rantai pemanggil dan uji reproduksi sebelum mengklaim bug: helper yang tidak dipanggil satu fungsi bisa dipanggil modul sebelumnya. Catat asumsi, lokasi dan bukti. Reviewer dapat salah; koreksi audit dipertahankan dalam evaluasi.

Indikator agency: keputusan konsultasi yang dapat ditelusuri, handoff diterima, scope stabil, pilot memenuhi mutu, sistem dipakai, net manfaat hulu-hilir, biaya operasi/review dan insiden. Bangun pengetahuan lintas klien dari pola anonim dengan izin yang relevan; tidak memasukkan data mentah/identitas klien lain ke memori global.

## Batas rollout ini
Perluasan dipasang pada kode ledger, validator, template dan skill. Tidak mengaktifkan runtime agent klien, gateway otomatis, deployment publik, provider API baru, registri autentikasi reviewer, atau isolasi semua tools. Harga/OPS global tetap keputusan manusia yang belum ditetapkan oleh tugas ini. Tidak mengubah skor historis atau bobot bank 3.1.
