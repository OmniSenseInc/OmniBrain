# SOP delivery OmniSense — v3.1

Alur induk: ALUR_OPERASIONAL_OMNISENSE.md. Pemilik teknis mengikuti penugasan tim pada kasus.
1. Mulai dari scope/acceptance/baseline versi yang disetujui. Bedakan pilot fondasi,non-AI,AI.
2. Bangun di lingkungan uji; data minimum berizin, akses terbatas, catatan perubahan, uji fungsi dan kondisi gagal. Dataset/sampel/periode dipilih sesuai proses dan risiko; angka20–50 bukan jaminan cukup.
3. Evaluasi dengan kasus baru dan baseline pembanding, termasuk kondisi normal, kosong, salah format, pengecualian, volume dan ketergantungan. Untuk AI, ukur ketepatan, abstain/eskalasi, retrieval/sumber,biaya,latensi dan kebocoran konteks bila relevan.
4. Kontrol manusia sesuai risiko dan review yang disepakati; jangan mengganti dengan sampling30persen hanya karena template. Keputusan berisiko memerlukan penanggung jawab yang benar-benar berwenang.
5. Pilot diterima berdasarkan hasil tertulis. Go-live adalah keputusan terpisah, disetujui tim dan klien pada scope yang sama, dengan rencana rollback/pemantauan/penanganan insiden.
6. Bukti deployment harus nyata, bukan persetujuan atau berkas selesai. Catat sistem yang aktif,versi,hasil smoke test dan sumber bukti.
7. Serahkan panduan operasi,troubleshooting,owneradopsi,rencana dukungan dan batas tanggung jawab. Jadwal dukungan/SLA ditetapkan per engagement, bukan janji otomatis24jam/day7.
8. Delivery tidak sama dengan berhasil: ukur pemakaian dan hasil terhadap baseline. Bila tidak dipakai/hasil memburuk, catat lalu perbaiki atau hentikan; jangan mengirim semua hijau tanpa angka.
