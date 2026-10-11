# OmniSense — paket pengembangan 3.3

Sumber aktif setelah melanjutkan pekerjaan yang terputus. Baca PROGRES_V33.md dan
consulting/GATEWAY_KONSULTASI_V33.md untuk status terkini dan batas verifikasinya.
Bank/engine tetap 3.1, workflow 3.2, kontrak agent 1.0; gateway baru 1.0.
Dokumen evaluasi versi terdahulu menyimpan hasil historis, bukan status gateway terkini.

Paket bukan installer otomatis. Plugin berada di ~/.hermes/plugins/omnisense-consultation;
folder hermes-plugin berisi salinan sumber yang identik. Skills berasal dari ~/.hermes/skills.
Server preview memakai loopback 8080 melalui tunnel yang sudah ada; konfigurasi layanan,
allowlist, kredensial dan backup tidak dibundel. Jangan membuka akses tools internal untuk klien.
Database, case/token klien, log mentah dan konfigurasi privat tidak disertakan.

Lihat VERIFIKASI_GATEWAY.json. Model aktif berhasil kembali setelah top-up dan diuji
melalui jalur konsultasi dengan transport simulasi; fallback terstruktur tersedia.
Domain final dan inbound WhatsApp klien nyata belum diverifikasi.
Manifest SHA256 memeriksa byte sumber paket, bukan menjamin hasil bisnis atau kelayakan go-live.
