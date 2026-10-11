# OmniSense — revisi website perkenalan

4 Oktober 2026. Revisi tim: tagline persis “Where Traditional Systems end, AI Agents Begin.” dan penyajian sederhana dengan isi utama tetap tersedia. HTML/CSS/JavaScript tanpa build step, logo asli, font lokal, dan orbit SVG/CSS.

Preview: https://then-farming-finding-undo.trycloudflare.com/
Homepage: /home/ubuntu/ai-agency/website/index.html
SHA256 homepage terkini: ab27bd601da8efbca3bbb8f5a2914b01c0d18b1be00006701f5c4d7450f8972a
Cadangan sebelum revisi: /home/ubuntu/ai-agency/consulting/backup_intro_menu_20261004T163753Z/index.html
Cadangan homepage awal: /home/ubuntu/ai-agency/consulting/backup_intro_20261004T151058Z/index.html

Isi: hero, Kenali OmniSense, tiga solusi, empat langkah kerja, delapan aspek penilaian, enam topik hasil konsultasi, dua karya, delapan FAQ, dua belas istilah, CTA konsultasi/WhatsApp, dan privasi. Penjelasan metode dan kamus memakai accordion. Kenali OmniSense berada dalam section dan dicapai melalui anchor dari hero/menu; hanya menu mobile memakai dialog. Screening tetap pada halaman konsultasi terpisah. Tidak ada harga, ROI atau jaminan hasil yang disimpulkan dari skor.

Layout lokal dan live diperiksa pada 320×740, 390×844, 768×1024, 1280×720 dan 1440×900: tidak ditemukan clipping horizontal pada elemen utama. Menu mobile menutup dan memindahkan fokus ke tujuan. FAQ dan penjelasan screening terbuka dengan benar. Tautan konsultasi menuju konsultasi-v3.html. Tidak ada error console tercatat. Ini pemeriksaan browser, bukan benchmark performa atau pengujian perangkat fisik. Screenshot dan JSON pemeriksaan ada pada folder outputs induk.

Homepage live HTTP 200 dengan hash sesuai source. Empat berkas konsultasi, privasi, dan mesin frontend diverifikasi identik sebelum/sesudah pemasangan. Backend tidak diubah dan tidak ada formulir atau pesan WhatsApp yang dikirim dalam pengujian revisi ini.

Paket berisi aset serta halaman konsultasi/privasi yang sudah ada. Konsultasi membutuhkan backend gateway v3.4 di origin yang sama untuk menyimpan dan menghubungkan hasil. python -m http.server dapat menampilkan desain, tetapi tidak menjalankan API konsultasi. Backend tersebut sudah berjalan pada preview VPS.

Preview memakai noindex. Domain final belum dipasang. Paket tidak memuat kredensial, konfigurasi provider, database atau data klien.

## Revisi animasi dan keterbacaan

Teks isi 14–16 px; label umumnya 10–12 px. Kontras teks isi ditingkatkan, judul dipertahankan. Section dan kartu muncul satu kali dengan stagger pendek. Desktop memakai hover lift, cahaya pada kartu dan gerak ikon/panah. Orbit memakai pulsa sinyal, cincin berputar, dan perubahan opacity logo. Mobile memakai jarak reveal lebih pendek dan pulsa lebih lambat; hover dibatasi pada pointer presisi.

Gerak memakai CSS opacity/transform dan IntersectionObserver; tanpa pustaka atau video tambahan. Animasi hero dipause saat tidak terlihat dan semua animasi dipause saat tab tersembunyi. Reduced-motion dan tombol Animasi menampilkan konten tanpa gerak, termasuk pseudo-elements. Konten terlihat tanpa JavaScript; focus keyboard membuka item yang belum direveal.

Reveal, tombol matikan animasi, pause offscreen dan menu mobile diuji lewat browser lokal. Lima ukuran layar juga diperiksa live, tanpa clipping horizontal atau error console. Pengaturan reduced-motion diimplementasikan melalui media query dan matchMedia; emulasi OS/perangkat fisik dan benchmark FPS belum dilakukan. Bukti: omnisense-motion-checks.json dan screenshot omnisense-motion-*.jpg pada folder outputs induk.

## Audit navigasi

Tombol hero Kenali OmniSense, menu Kenali dan Kenali lebih jauh menuju #kenali-omnisense. Section perkenalan menggantikan popup Tentang. Menu mengikuti urutan Kenali, Solusi, Cara Kerja, Karya; mobile menambahkan FAQ. Indikator aria-current mengikuti hash tujuan. Fokus anchor diarahkan ke section; penutupan menu, Escape dan resize ke desktop memulihkan scroll/fokus tanpa meninggalkan overlay.

Menu desktop/live dan lima tujuan mobile/lokal diperiksa melalui browser. Halaman konsultasi dan privasi dapat dibuka serta kembali ke beranda. Screening live diuji dengan konteks contoh dan 16 jawaban belum tahu: hasil 20–100, pengiriman tanpa persetujuan nonaktif, reset menghapus jawaban dan menyembunyikan hasil. Tidak ada data dikirim ke server atau WhatsApp. Pengiriman gateway/WA belum diuji pada audit ini.

Tiga HTML dalam paket lolos pemeriksaan ID duplikat, referensi file internal dan fragment. Dua ikon privasi yang sebelumnya tertinggal pada paket lokal sudah disalin dari aset publik VPS; versi live sebelumnya sudah mempunyai ikon tersebut. Homepage, konsultasi, privasi dan kedua ikon merespons HTTP 200 di VPS. Lima ukuran viewport live tidak memiliki clipping horizontal pada elemen utama. Screenshot dan JSON: omnisense-navigation-* pada folder outputs induk.

Angka urutan pada menu desktop/mobile dihapus sesuai revisi pemilik. Teks menu dan tujuan tautan tetap sama. Label nomor di isi section bukan bagian perubahan ini.


## Palet Matte Black × Bone White — 5 Oktober 2026

Pilihan pemilik nomor 1 telah dipasang pada homepage, konsultasi dan privasi di preview VPS. Latar #101010, teks/tombol #F3EFE6, permukaan #1C1B19, teks sekunder #B9B2A6, garis #49463F. Dekorasi SVG, orbit, glow, menu, fokus keyboard, form dan status pilihan memakai warna netral yang selaras. Warna error tetap dibedakan untuk fungsi validasi.

Cadangan tiga halaman sebelum perubahan: /home/ubuntu/ai-agency/consulting/backup_matte_bone_20261005/. Hash ketiga halaman VPS sesuai paket lokal. Seluruh script serta konten di luar deklarasi warna identik dengan versi sebelum perubahan. Backend dan mesin scoring tidak berubah.

Browser memverifikasi warna computed style, desktop, HP 390×844 dan HP kecil 320×740. Tidak ada overflow horizontal pada homepage, konsultasi dan privasi yang diperiksa. Menu mobile ke Solusi berfungsi, memilih jawaban kuis memperbarui status dan warna pilihan, dan tidak ada error console tercatat. Form tidak dikirim. Ini pemeriksaan browser, bukan perangkat fisik atau benchmark performa.

Screenshot: omnisense-matte-bone-desktop.jpg, omnisense-matte-bone-mobile.jpg, omnisense-matte-bone-consult-mobile.jpg pada folder outputs induk. Tangkapan HP lengkap dari sesi sebelumnya memperlihatkan palet lama.
