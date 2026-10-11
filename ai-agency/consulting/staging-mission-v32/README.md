# OmniSense agency v3.1 — snapshot 4 Oktober 2026
Salinan berkas aktif yang dipasang di VPS OmniSense. Baca ALUR_OPERASIONAL_OMNISENSE.md dan consulting/PLAYBOOK_KONSULTAN.md terlebih dahulu. Pengujian dan batasnya: consulting/EVALUASI_V31.md. Paket ini bukan seluruh VPS/profile Hermes; tidak mencakup credential, database sesi/klien, atau arsip produk.

Delapan dimensi, 16 screening, 32 discovery; bank revision 2026-10-04-flow-1. Input 3.0/3.1, output 3.1. Engine Python/JavaScript dan ledger operator. Parser situs read-only; ledger default dry-run dan --commit hanya lewat operator terotorisasi.

Preview terpisah: dari akar paket jalankan python3 -m http.server 8080 --bind 127.0.0.1 lalu buka http://127.0.0.1:8080/website/konsultasi-v3.html . Aset bank/JS/font/favicon/privasi disertakan. Link logo menuju index.html situs utama, yang sengaja tidak dibundel; ini bahan fitur konsultasi, bukan situs utama lengkap.

Pengujian mesin pada Linux: python3 -m unittest discover -s consulting -p 'test_assessment_v3.py' -v dan python3 -m unittest discover -s consulting -p 'test_decision_workflow_v31.py' -v . test_consulting_flow.py membutuhkan Node.js/Playwright dan browser runtime yang sesuai (lihat konfigurasi dalam skrip). Ringkasan hasil aktif sudah disertakan; tidak otomatis teruji pada sistem penerima paket.

Integrasi gateway/situs utama/publikasi tidak dijalankan oleh paket ini. Handoff, komersial, pilot dan go-live memerlukan penerimaan/persetujuan nyata pada scope yang sama. Instruksi/ledger bukan autentikasi reviewer atau isolasi seluruh tools Hermes. Catatan contoh bertanda SIMULATION dan bukan bukti klien. Model tidak di-fine-tune; ini peningkatan instruksi, pengetahuan dan tool. 
