# SETUP WHATSAPP UNTUK KONSULTAN — CATATAN UNTUK CTO
Sumber: dokumentasi resmi Hermes (messaging/whatsapp).

## PILIHAN
- BAILEYS bridge (tidak resmi, TANPA API key) -> REKOMENDASI untuk mulai konsultan.
  - Tidak butuh Meta API key / verifikasi bisnis / webhook publik.
  - Meniru sesi WhatsApp Web via scan QR; sesi tersimpan otomatis.
- WhatsApp Cloud API (resmi Meta) -> untuk stabilitas nanti saat volume naik;
  butuh Meta Business account + token + webhook publik. Simpan sebagai migrasi.

Keduanya bisa jalan PARALEL di nomor berbeda (internal Telegram + konsultan WhatsApp).

## LANGKAH (Baileys) — jalankan di install Hermes perangkat tim
1. Pastikan Node.js v18+ & npm terpasang.
2. Jalankan: `hermes whatsapp` (dipandu).
3. Pilih mode:  bot  (nomor khusus -> REKOMENDASI)  atau  self-chat  (nomor sendiri,
   uji).
4. Perintah mengunduh bridge dependencies.
5. Tampilkan QR di terminal -> scan dari HP (Settings -> Linked Devices -> Link a
   Device -> arahkan kamera ke QR).
6. Setelah paired, wizard konfirmasi & simpan sesi.

## SARAN (Baileys)
- Gunakan NOMOR KHUSUS untuk bot konsultan (bukan nomor pribadi) — mengurangi ban risk.
- Jangan spam/bulk; hanya balas; jangan otomatis DM yang belum pernah kontak duluan.
- Jika WhatsApp update putus bridge: `hermes` update + pair ulang.

## HUBUNGKAN KE PROFILE
- Buat profile "omnisense-internal" -> gateway Telegram.
- Buat profile "omnisense-consultant" -> gateway WhatsApp (Baileys, nomor khusus).
- Tempel: guardrail_consultant_whatsapp.md sebagai instruksi/persona profile konsultan.
- WhatsApp butuh gateway background berjalan (sama seperti platform lain).

## CATATAN
- Setup ini dilakukan di PERANGKAT TIM (install Hermes), bukan di environment terminal
  yang dipakai untuk menyusun dokumen.
- Untuk rilis publik/volume: migrasi ke WhatsApp Cloud API (resmi) direkomendasikan.