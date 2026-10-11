# Materi Meeting OmniSense — 5 Oktober 2026

Bahan diskusi untuk tim tiga orang. Ringkasan pekerjaan 3–5 Oktober 2026; disusun sebelum pemasangan maskot ke homepage VPS pada sesi ini.

## I. Tujuan meeting

Menyamakan kondisi OmniSense sekarang, memilih hambatan utama yang harus dibereskan, lalu menetapkan pekerjaan dengan PIC, output, dan bukti selesai. Target meeting: keputusan yang dapat dikerjakan, bukan sekadar daftar ide.

Visi kerja tetap: menjadikan digitalisasi dan agen AI sebagai fondasi operasional bisnis. OmniSense berperan sebagai konsultan perusahaan dan otak agency: memahami masalah, memeriksa proses/data, memilih solusi yang masuk akal, lalu membantu tim membangun dan memasangnya.

Model bisnis yang disepakati: konsultasi termasuk pendalaman gratis; pembangunan dan pemasangan berbayar sesuai lingkup yang disetujui tim. Solusi dapat berupa perbaikan proses, software biasa, otomasi aturan, atau agen AI. Produk turunan tidak menggantikan identitas OmniSense sebagai agency.

## II. Progres yang sudah dikerjakan

| Area | Perubahan dan manfaat | Status dan batas |
| --- | --- | --- |
| Otak agency | Indeks sumber, playbook, skill agency-brain, catatan keputusan dan pekerjaan. Agen diarahkan membedakan fakta, usulan, keputusan pemilik, dan hal yang belum diketahui. | Instruksi/dokumen terpasang di VPS. Ini pembekalan konteks dan tool, bukan fine-tuning bobot model. Kepatuhan model live belum konsisten. |
| Mutu konsultasi | Mulai dari keluhan/proses, contoh kejadian, pemilik proses, baseline dan bukti. Membandingkan alternatif sebelum memilih AI; manfaat kapasitas dipisahkan dari uang kas. | Panduan dan engine tersedia. Simulasi tidak membuktikan mutu seluruh konsultasi atau ROI klien. |
| Screening kesiapan | 16 pertanyaan dalam 8 dimensi; bank pendalaman 32 butir. Unknown disimpan sebagai ketidakpastian dan menghasilkan rentang. Skor tinggi tidak menghapus prasyarat data, akses, pemilik proses, review dan pemulihan. | Bank/engine 3.1 aktif. Bobot/ambang merupakan heuristik internal, belum tervalidasi empiris. |
| Workflow proyek | Alur lead → intake → discovery → diagnosis → opsi → handoff diterima tim → proposal → onboarding → pilot → delivery → adopsi → evaluasi. Catatan kasus, revisi scope, persetujuan dan kontrak agent dipisahkan. | Workflow 3.2 tersedia. Kontrak tertulis belum berarti pembatasan aksi seluruh runtime atau proyek klien selesai. |
| Website → WhatsApp | Pengunjung dapat screening atau konsultasi langsung. Pengiriman screening memerlukan persetujuan dan tindakan pengguna. WA membawa kode kasus, lalu ringkasan dikonfirmasi sebelum antrean tim. | Gateway 3.5/patch 3.5.1 terpasang di VPS. Antrean bukan tanda proyek telah diterima tim. Jalur klien WA nyata dari awal sampai handoff masih perlu uji. |
| Respons WhatsApp | Pembuka lebih mendengarkan masalah; tidak menyebut harga/skor/diagnosis terlalu dini. Pertanyaan balik dan koreksi tidak otomatis memajukan tahap. Balasan salah identitas/klaim tindakan palsu memakai fallback. | Guard/fallback terpasang; tidak menjamin semua halusinasi atau input tidak serius terdeteksi. |
| Keandalan dan privasi alur | Draft browser opsional dua jam, consent lama dibatalkan saat data berubah, kode kedaluwarsa tidak dibuka, retry/timeout, batas panggilan model per kasus, pemisahan kasus/kanal dan tools klien. | 108 tes regresi/isolasi/ingress simulasi tercatat lulus pada patch 3.5.1. Jumlah ini tidak dijumlahkan dengan suite historis dan bukan ukuran akurasi universal. |
| Website perkenalan | Struktur sederhana dengan isi tetap lengkap: Kenali, Solusi, Cara Kerja, Hasil Konsultasi, Karya, FAQ dan kontak. Tagline tim: “Where Traditional Systems end, AI Agents Begin.” Palet Matte Black #101010 / Bone White #F3EFE6. | Versi perkenalan tersedia pada preview VPS. Domain produksi final belum dipasang melalui pekerjaan ini. |
| Maskot dan motion | Tim/pemilik memilih konsep tengah “Architect”, lalu versi kedua: kepala sensor, inti dada, jaket teknis asimetris. Motion dibuat dengan kode: kepala/dada/lengan/jaket bergerak kecil, respons kursor/tap, transisi scroll. | Prototipe lokal sudah diuji desktop dan dua viewport HP. Masih 2.5D dari gambar; gerak/rotasi tubuh penuh memerlukan aset 3D ber-rig. Belum diimpor ke homepage VPS saat materi ini disusun. |

Layanan gateway Hermes, web preview dan tunnel terlihat aktif pada pemeriksaan VPS sesi ini. Kondisi layanan aktif tidak membuktikan kualitas semua percakapan atau kesiapan produksi.

## III. Hambatan yang perlu dibahas

**P0 — Jalur model belum dapat diandalkan untuk mematuhi instruksi.** Audit langsung dan pemeriksaan setelah penggantian API key menunjukkan kontrak pesan system/developer masih sering gagal, sementara beberapa instruksi di user berhasil. Identitas model upstream belum terbukti; tidak cukup bukti untuk menyimpulkan model palsu atau menyalahkan satu vendor model. Fokus teknis: periksa penerusan pesan, prioritas instruksi, format keluaran dan reproduksi request. Jangan memasarkan konsultasi otonom yang “100% akurat” dari kondisi ini.

**P0 — Uji perjalanan klien WhatsApp nyata belum lengkap.** Tes kode, ingress dan transport simulasi sudah ada, tetapi masih perlu satu skenario data sintetis melalui browser → WA → pendalaman → koreksi → konfirmasi ringkasan → antrean → penerimaan tim. Bedakan pesan terkirim, pesan dibaca, handoff masuk, dan tim menerima.

**P1 — Penawaran komersial, kapasitas dan owner operasional perlu keputusan tim.** Harga final belum disahkan melalui pekerjaan ini. Tentukan satu lingkup penawaran yang sempit, jam kerja, biaya tools/hosting, dukungan, batas revisi dan acceptance. Siapa yang memegang tindak lanjut harian dan kapasitas pendalaman perlu dipastikan.

**P1 — Kuis belum terkalibrasi dengan perusahaan nyata.** Isian jelas ngawur dapat diminta klarifikasi; isian palsu yang terlihat wajar tidak bisa diketahui niatnya hanya dari form. Konsultasi perlu contoh/bukti. Gunakan beberapa kasus nyata dengan dua penilai untuk menguji konsistensi, bukan menambah bobot angka tanpa data.

**P1 — Domain final dan bukti pemasaran.** Pilih hosting/domain final, siapa yang memegang akses dan kapan review rilis dilakukan. Karya, testimoni, hasil proyek dan janji manfaat harus mengikuti bukti. Jangan menyajikan demo atau rancangan sebagai hasil klien.

**P2 — Motion dan UI harus mendukung pemahaman.** Maskot sudah dipilih; jangan mengulang pencarian karakter terus-menerus sebelum menguji calon klien. Fokus berikutnya: hero tidak menutupi teks/CTA, isi lengkap tetap mudah dipindai, navigasi tepat, mobile terbaca, mode jeda/reduced motion, dan fallback gambar. Penomoran dekoratif bagian diganti I, II, III, dst.; angka faktual skor/form tetap mengikuti kontrak mesin.

## IV. Keputusan yang sebaiknya keluar dari meeting

| Keputusan | Bahan pertimbangan | Output meeting |
| --- | --- | --- |
| Satu penawaran awal untuk diuji | Pilih masalah yang sering terjadi dan dapat diukur; contoh follow-up lead, booking, penagihan, atau laporan operasional. AI dipakai bila memang dibutuhkan. | Satu halaman scope: siapa targetnya, masalah, hasil, batas dan acceptance. |
| Harga uji dan struktur biaya | Angka diskusi sebelumnya hanya usulan: sekitar Rp1–1,5 juta alur sederhana; Rp1,5–3 juta alur lebih kompleks; Rp3–5 juta pilot AI terawasi. Belum berdasarkan biaya tiap proyek dan belum menjadi harga resmi. | Harga/scoping yang disahkan tim, biaya berulang dipisahkan, margin minimum dan batas revisi. Tidak dipublikasikan sebelum disahkan. |
| Perbaikan jalur model | Tuntut hasil uji system/persona/JSON/kasus bisnis yang berulang dan konsisten. Harga API atau nama alias bukan bukti kualitas. | PIC teknis, endpoint yang akan diuji dan kriteria lulus sebelum konsultasi model diandalkan. |
| Penanggung jawab kasus | Peran yang tercatat: Vincent CEO/komersial, Nathanael CTO/teknis, Michael CMO/lead/konten/QA. Pembagian tugas spesifik berikut masih usulan untuk disahkan. | Satu koordinator operasional dan owner tiap kasus; aturan penerimaan dan eskalasi. |
| Website dan peluncuran | Architect v2, palet dan tagline sudah dipilih. Layanan preview bukan domain final. | Persetujuan visual tim, daftar koreksi singkat, owner hosting/domain dan checklist rilis. |
| Validasi awal bisnis | Tetapkan calon perusahaan, masalah dan bukti keberhasilan. Jadwal/jumlah target diputuskan sesuai kapasitas. | Daftar engagement yang akan diuji beserta PIC, metrik, periode, dan izin data. |

## V. Rencana kerja yang diusulkan

| Prioritas | Usulan PIC | Pekerjaan / output | Bukti selesai |
| --- | --- | --- | --- |
| P0 | Nathanael + pemilik akses provider | Reproduksi kegagalan kontrak pesan; benahi router atau evaluasi endpoint lain. | Uji persona, system/developer, JSON, koreksi dan kasus bisnis lulus berulang; hasil tercatat tanpa secret. |
| P0 | Michael untuk QA; Nathanael untuk perbaikan | Satu uji WhatsApp nyata memakai kasus sintetis yang disetujui tim. | Jejak dari form sampai handoff diterima; kode kadaluarsa, retry, stop/lanjut dan koreksi tidak merusak tahap. |
| P1 | Vincent, dengan input biaya dari Nathanael | Putuskan penawaran pilot dan harga menurut scope. | Scope, biaya, acceptance, dukungan dan batas revisi tertulis/disahkan. |
| P1 | Michael; tim menerima kasus | Uji konsultasi dengan beberapa perusahaan dan kumpulkan bukti keluhan. | Catatan discovery, baseline dan evaluasi dua penilai; hindari klaim ROI tanpa pengukuran. |
| P1 | Codex pada sesi ini; review visual oleh tim | Import Architect ke homepage VPS, refine tata letak dan label Romawi, selaraskan konsultasi/privasi. | Backup, aset lengkap, desktop/mobile, anchor/menu, jeda/fallback dan API alur utama diperiksa. |
| P1 | Tim menetapkan koordinator | Atur penerimaan lead, PIC, tindak lanjut dan serah-terima. | Setiap kasus memiliki owner, next step dan status penerimaan yang nyata. |
| P2 | Michael + Nathanael | Finalisasi domain/hosting, analitik yang sesuai dan bukti karya. | Persetujuan rilis, kontak berfungsi, bukti klaim dan rencana pemulihan. |

Semua PIC dan tenggat spesifik dalam tabel ini adalah **usulan meeting**, bukan penugasan yang otomatis disahkan. Tim perlu mengisi owner dan tanggal target.

## VI. Agenda usulan 60 menit

- 5 menit: sepakati tujuan dan model bisnis.
- 15 menit: demo alur konsultasi serta website/maskot; bedakan demo dari produksi.
- 15 menit: putuskan perbaikan model dan skenario WhatsApp nyata.
- 15 menit: pilih penawaran awal, biaya, target klien dan owner operasional.
- 10 menit: tetapkan PIC/output/bukti selesai dan jadwal review berikutnya.

Pertanyaan penutup: “Apa tiga hasil yang harus sudah bisa ditunjukkan pada review berikutnya, siapa pemiliknya, dan bukti apa yang membuat kita menyebutnya selesai?”

## VII. Catatan keputusan untuk diisi saat meeting

| Topik | Keputusan | PIC | Target waktu | Bukti selesai |
| --- | --- | --- | --- | --- |
| Jalur model | — | — | — | — |
| Uji WA nyata | — | — | — | — |
| Penawaran & harga | — | — | — | — |
| Owner operasional | — | — | — | — |
| Website & domain | — | — | — | — |
| Validasi klien | — | — | — | — |

## VIII. Acuan dan batas materi

Ringkasan mengacu pada laporan pembekalan/konsultan, workflow 3.1–3.2, gateway 3.3–3.5.1, audit/recheck router, review website, serta checkpoint maskot yang tersimpan dalam proyek. Status historis lama tidak menimpa patch terbaru. Jangan menjumlahkan semua kategori tes menjadi satu angka.

Materi ini tidak berisi credential, database klien atau percakapan pribadi. Tidak ada perubahan harga resmi, model bisnis, bobot kuis atau visi/misi baru. Belum ada bukti cukup untuk menyatakan seluruh respons model akurat, sistem siap berjalan tanpa review manusia, atau manfaat bisnis sudah terjamin.

