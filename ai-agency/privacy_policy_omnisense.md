# Draf Kebijakan Privasi OmniSense (versi teks, untuk Meta App Dashboard)

> Dipakai untuk mengisi field **Privacy Policy URL** dan **User Data Deletion** di
> App Settings → Basic. Isi `{{EMAIL}}` dan `{{WHATSAPP}}` dulu sebelum dipakai.
> Versi HTML siap-upload: `/home/ubuntu/ai-agency/privacy_policy_omnisense.html`

## Yang dibutuhkan Meta (2 field, beda isi)

1. **Privacy Policy URL** — URL halaman kebijakan privasi yang bisa dibuka publik.
   Contoh target: `https://omnisense.id/privacy`
2. **User Data Deletion** — pilih opsi **Instructions URL** (paling sederhana, tanpa server callback).
   URL-nya boleh halaman yang sama, asalkan di situ ada instruksi cara minta hapus data.
   Contoh: `https://omnisense.id/privacy#hapus-data`

---

## TEKS KEBIJAKAN (ID)

Kebijakan Privasi OmniSense
Berlaku sejak: 21 September 2026

OmniSense adalah layanan konsultasi dan implementasi AI untuk bisnis, beroperasi di omnisense.id
dan mengelola akun Instagram resmi @omnisense_id.

1. DATA YANG KAMI PROSES
Kami memakai API resmi Instagram hanya untuk mengelola akun Instagram milik kami sendiri:
- informasi akun kami sendiri (ID akun, nama pengguna, jenis akun, jumlah media);
- token akses (access token) untuk akun kami, disimpan di server kami dengan izin file terbatas;
- konten yang kami publikasikan sendiri (gambar, caption, metadata publikasi: waktu, ID media, tautan).
Kami TIDAK mengakses data pengguna Instagram lain, tidak mengirim DM, tidak melakukan follow/like,
dan tidak mengumpulkan data pribadi pihak ketiga melalui API ini.

2. TUJUAN
- mempublikasikan konten edukasi milik OmniSense ke akun Instagram kami;
- memeriksa status akun dan status publikasi konten kami sendiri;
- menjaga keamanan integrasi (memperbarui token, mencatat log publikasi).

3. PEMBAGIAN DATA
Kami tidak menjual atau menyewakan data. Data diproses oleh kami dan penyedia infrastruktur
(server, penyimpanan file) yang kami pakai untuk menjalankan layanan.

4. PENYIMPANAN & RETENSI
- token akses disimpan sampai dicabut pemilik akun atau diperbarui berkala;
- log publikasi disimpan untuk audit internal;
- berkas gambar poster disimpan selama diperlukan untuk publikasi dan arsip brand.

5. CARA MEMINTA PENGHAPUSAN DATA
- Kirim email ke {{EMAIL}} dengan subjek "Hapus Data Instagram", sebutkan akun Instagram terkait.
- Kami menghapus token akses dan data terkait dari sistem kami dalam 7 hari kerja, lalu mengirim
  konfirmasi lewat email.
- Kamu juga bisa mencabut akses sendiri: Instagram → Settings and activity → Apps and websites →
  pilih aplikasi → Remove.

6. KEAMANAN
Kredensial hanya disimpan di server kami dengan izin akses terbatas, tidak ditulis di dalam kode
sumber, dan tidak dibagikan lewat kanal publik. Akses internal dibatasi pada tim inti OmniSense.

7. PERUBAHAN
Jika kebijakan berubah, tanggal di bagian atas diperbarui dan versi terbaru tampil di alamat ini.

8. KONTAK
Email {{EMAIL}} · WhatsApp {{WHATSAPP}} · omnisense.id

---

## TEKS KEBIJAKAN (EN, ringkas)

Privacy Policy — OmniSense (effective 21 September 2026)

We use the official Instagram Platform APIs solely to manage our own Instagram account
(@omnisense_id). We process only our own account information (account ID, username, account type,
media count), the access token issued for our own account (stored on our servers with restricted
file permissions), and the content we publish ourselves (image, caption, publication metadata).
We do not access other users' data, send direct messages, follow or like on behalf of anyone, or
collect third-party personal data through these APIs. We do not sell or rent data.

Data deletion: email {{EMAIL}} with subject "Instagram data deletion". We remove the access token
and related records within 7 business days and confirm by email. You may also revoke app access via
Instagram → Settings and activity → Apps and websites → Remove.

Contact: {{EMAIL}} · {{WHATSAPP}} · omnisense.id
