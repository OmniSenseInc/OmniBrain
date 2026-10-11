# ON-BOARDING CLIENT — ATURAN SEDERHANA (WhatsApp) [v2]
TIDAK ADA LAGI whitelist / registrasi / perintah khusus. Cukup aturan komposisi.

=============================================================
ATURAN: OTOMATIS BERDASARKAN ISI GRUP
=============================================================
Kalau OmniSense (bot) DI DALAM sebuah grup WhatsApp yang berisi:
- MINIMAL 1 anggota tim (Vincent 6281803474609 / Nathanael 6281332005165 /
  Michael 6289667020507), DAN
- minimal 1 nomor client (bukan tim),
=> OMNISENSE OTOMATIS menjadi konsultan di grup itu. Client bisa langsung chat,
   bot menjawab & menjalankan konsultasi. Tanpa daftar, tanpa whitelist.

Di luar itu:
- Grup hanya tim          -> bot = asisten internal tim (diam kecuali ditag).
- Grup tanpa anggota tim  -> bot tidak merespons.

=============================================================
CARA MEMULAI CLIENT BARU (cuma 2 langkah)
=============================================================
1. BUAT GRUP:  Konsul-[NamaClient]  → isi: client + bot + min. 1 tim.
   (Jangan campur 2 client dalam satu grup.)
2. LANGSUNG JALAN: client (atau tim) cukup mengirim pesan di grup — bot otomatis
   membuka konsultasi karena syarat komposisi (tim + client) terpenuhi.
   - (Opsional catat client ke CRM/scorecard — isi fase5_scorecard.csv / Google
     Sheets, atau bilang ke bot "onboard <Nama> <nomor>" di grup tim.)

=============================================================
PERINTAH (opsional; di grup tim, tag bot lalu tulis; JANGAN awalan "/")
=============================================================
- "status"                    -> ringkas pipeline
- "onboard <Nama> <nomor>"    -> catat client baru ke CRM
- "note <x>"                  -> catatan internal
- "handoff"                   -> serahan tim diterima

=============================================================
PEMILIK
=============================================================
- Buat grup & isi : CMO (pemilik lead); boleh anggota tim mana pun.
- Harga & closing : TIM (bukan bot).
- Catat client    : siapa pun tim / bot via onboard.

=============================================================
CATATAN
=============================================================
- Dokumen v1 (whitelist/registrasi) usang; abaikan.
- script wa_*.py tidak lagi bagian alur utama (opsional administratif).