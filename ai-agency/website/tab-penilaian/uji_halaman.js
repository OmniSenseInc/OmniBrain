/* Uji halaman penilaian mandiri (penilaian.html).
   Menjalankan alur sungguhan seperti pengunjung: isi identitas -> jawab 15 soal
   (campur pilih + tulis sendiri) -> lihat skor -> periksa pesan yang dikirim ke bot.

   Pakai:
     PW_CORE=/tmp/camofox/node_modules/playwright-core \
     CHROME_PATH=/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome \
     node uji_halaman.js [--url http://127.0.0.1:8080/penilaian.html]
*/
const { chromium } = require(process.env.PW_CORE);

const URL_HALAMAN = (process.argv.includes('--url')
  ? process.argv[process.argv.indexOf('--url') + 1]
  : 'http://127.0.0.1:8080/penilaian.html');

let lulus = 0, gagal = 0;
function cek(nama, syarat, info) {
  if (syarat) { lulus++; console.log('  OK    ' + nama + (info ? '  ' + info : '')); }
  else { gagal++; console.log('  GAGAL ' + nama + (info ? '  ' + info : '')); }
}

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  const err = [];
  p.on('console', m => { if (m.type() === 'error') err.push(m.text()); });
  p.on('pageerror', e => err.push('PAGEERROR ' + e.message));

  await p.goto(URL_HALAMAN, { waitUntil: 'networkidle' });
  await p.waitForTimeout(600);

  /* ---------- 1. jumlah soal & data ---------- */
  const jml = await p.evaluate(() => ({
    soal: window.__PENILAIAN_SITUS__.soal.length,
    dimensi: window.__PENILAIAN_SITUS__.dimensi.length,
    bobot: window.__PENILAIAN_SITUS__.dimensi.reduce((a, d) => a + d.bobot, 0),
    kode: window.__PENILAIAN_SITUS__.soal.map(s => s.kode),
    aturan: window.__PENILAIAN_SITUS__.aturan_konsistensi.aturan.map(a => a.kode + ':' + Object.keys(a.jika).join('+')),
  }));
  cek('15 soal', jml.soal === 15, '(' + jml.soal + ')');
  cek('8 dimensi', jml.dimensi === 8, '(' + jml.dimensi + ')');
  cek('total bobot 1.0', Math.abs(jml.bobot - 1) < 1e-9, '(' + jml.bobot + ')');
  cek('kode soal unik', new Set(jml.kode).size === jml.kode.length, jml.kode.join(','));
  cek('3 aturan konsistensi pakai kode soal',
    jml.aturan.length === 3 && jml.aturan.every(x => /D\d[a-z]?/.test(x)),
    jml.aturan.join(' | '));

  /* ---------- 2. identitas wajib ---------- */
  const kosong = await p.evaluate(() => {
    const btn = document.querySelector('#btnMulai');
    return { disabled: btn.disabled, sesiTampil: !document.querySelector('#kartu-sesi').hidden };
  });
  cek('tombol mulai terkunci sebelum identitas diisi', kosong.disabled === true);
  cek('sesi belum terbuka sebelum identitas diisi', kosong.sesiTampil === false);

  await p.fill('#inBisnis', 'Kopi Senja');
  await p.waitForTimeout(120);
  const belum = await p.evaluate(() => document.querySelector('#btnMulai').disabled);
  cek('masih terkunci kalau nomor belum diisi', belum === true);

  await p.fill('#inKontak', '0812-3456-7890');
  await p.waitForTimeout(150);
  const siap = await p.evaluate(() => document.querySelector('#btnMulai').disabled);
  cek('terbuka setelah nama bisnis + nomor diisi', siap === false);

  /* ---------- 3. validasi nomor ---------- */
  await p.fill('#inKontak', 'abc');
  await p.waitForTimeout(150);
  const jelek = await p.evaluate(() => ({
    disabled: document.querySelector('#btnMulai').disabled,
    err: (document.querySelector('#errKontak').textContent || '').trim(),
  }));
  cek('nomor ngawur ditolak', jelek.disabled === true && jelek.err.length > 0, jelek.err.slice(0, 60));

  await p.fill('#inKontak', '081234567890');
  await p.waitForTimeout(150);

  /* ---------- 4. buka sesi ---------- */
  await p.click('#btnMulai');
  await p.waitForTimeout(500);
  const sesi = await p.evaluate(() => ({
    soal: document.querySelectorAll('#qList .q').length,
    sesiId: (document.querySelector('#sesiId').textContent || '').trim(),
    kartu: !document.querySelector('#kartu-sesi').hidden,
  }));
  cek('15 soal terbuka setelah mulai', sesi.soal === 15, '(' + sesi.soal + ')');
  cek('nomor sesi tampil', /OS-\d{8}-[0-9A-F]{4}/.test(sesi.sesiId), sesi.sesiId);
  cek('kartu sesi muncul', sesi.kartu === true);

  /* ---------- 5. skor terkunci sebelum lengkap ---------- */
  const awal = await p.evaluate(() => ({
    disabled: document.querySelector('#btnHitung').disabled,
    count: (document.querySelector('#penCount').textContent || '').trim(),
  }));
  cek('tombol skor terkunci di awal', awal.disabled === true, awal.count);

  /* ---------- 6. isi 15 soal: 3 tulis sendiri + 12 pilih ---------- */
  const tulis = [
    ['D1a', 'belum kepikiran mau dibawa ke mana 3 tahun ke depan'],
    ['D2a', 'kalau ditanya untung bersih harus hitung manual dulu, bisa 2-3 hari'],
    ['D6b', 'cuma saya sendiri yang bisa pakai aplikasi'],
  ];
  for (const [kode, teks] of tulis) {
    await p.evaluate(([k, t]) => window.OmniSenseSitus.tulis(k, t), [kode, teks]);
    await p.waitForTimeout(90);
  }
  const bacaHasil = await p.evaluate((t) => t.map(([k, teks]) => {
    const h = window.OmniSenseSitus.baca(k, teks);
    return k + '=' + (h ? h.nilai : '?');
  }), tulis);
  cek('tulisan bebas terbaca jadi angka',
    bacaHasil.join(' ') === 'D1a=1 D2a=2 D6b=2', bacaHasil.join(' '));

  const pilih = [['D1b',2],['D2b',2],['D2c',3],['D3a',2],['D3b',2],['D4a',3],['D4b',3],['D5a',2],['D5b',4],['D6a',3],['D7',3],['D8',3]];
  for (const [kode, nilai] of pilih) {
    await p.evaluate(([k, v]) => window.OmniSenseSitus.jawab(k, v), [kode, nilai]);
    await p.waitForTimeout(60);
  }
  await p.waitForTimeout(300);

  const lengkap = await p.evaluate(() => ({
    disabled: document.querySelector('#btnHitung').disabled,
    count: (document.querySelector('#penCount').textContent || '').trim(),
  }));
  cek('tombol skor terbuka setelah 15 terjawab', lengkap.disabled === false, lengkap.count);

  /* ---------- 7. hitung & hasil ---------- */
  await p.click('#btnHitung');
  await p.waitForTimeout(1500);
  const hasil = await p.evaluate(() => {
    const kotak = document.querySelector('#penHasil');
    const rows = Array.from(document.querySelectorAll('#phRows .row')).map(r => ({
      nama: (r.querySelector('.rn') || {}).textContent || '',
      nilai: parseFloat((r.querySelector('.rv') || {}).textContent || '0'),
    }));
    return {
      tampil: !kotak.hidden,
      skor: window.OmniSenseSitus.skor(),
      band: window.OmniSenseSitus.band(),
      rows: rows.length,
      urutNaik: rows.every((r, i) => i === 0 || rows[i - 1].nilai <= r.nilai),
      pesan: window.OmniSenseSitus.pesan(),
      wa: document.querySelector('#phWa').href,
      gcard: document.querySelectorAll('#phGap .gcard').length,
      salin: !!document.querySelector('#btnSalin'),
    };
  });
  cek('kartu hasil tampil', hasil.tampil === true);
  cek('8 baris dimensi', hasil.rows === 8, '(' + hasil.rows + ')');
  cek('urut dari yang paling lemah', hasil.urutNaik === true);
  cek('2 langkah + 1 kekuatan disarankan', hasil.gcard === 3, '(' + hasil.gcard + ')');
  cek('skor wajar 0-100', hasil.skor > 0 && hasil.skor <= 100, hasil.skor.toFixed(1) + '% ' + hasil.band);
  cek('tombol salin ringkasan ada', hasil.salin === true);

  /* ---------- 8. pesan ke bot ---------- */
  const m = hasil.pesan;
  cek('penanda v2 ada', m.startsWith('[PENILAIAN-SITUS v2]'));
  cek('nama bisnis di pesan', /^bisnis=Kopi Senja$/m.test(m));
  cek('nomor di pesan', /^kontak=081234567890$/m.test(m));
  cek('15 nilai soal di pesan', (m.match(/\bD[1-8][a-z]?=[1-5]\b/g) || []).length === 15,
    '(' + (m.match(/\bD[1-8][a-z]?=[1-5]\b/g) || []).length + ')');
  cek('skor_situs ada', /skor_situs=[\d.]+ band=/.test(m));
  cek('tulisan pengunjung ikut dikirim', m.includes('Catatan yang saya tulis sendiri'));
  cek('tautan WA terisi', hasil.wa.startsWith('https://wa.me/6288809640700?text='));
  cek('tautan WA memuat pesan', decodeURIComponent(hasil.wa).includes('bisnis=Kopi Senja'));

  /* ---------- 9. muat ulang: jawaban tersimpan ---------- */
  await p.reload({ waitUntil: 'networkidle' });
  await p.waitForTimeout(900);
  const setelah = await p.evaluate(() => ({
    soal: document.querySelectorAll('#qList .q').length,
    terjawab: Object.keys(JSON.parse(localStorage.getItem('omnisense_situs_jawab_v2') || '{}')).length,
    kartuSesi: !document.querySelector('#kartu-sesi').hidden,
  }));
  cek('jawaban tersimpan setelah halaman dimuat ulang', setelah.terjawab === 15, '(' + setelah.terjawab + ')');
  cek('sesi lama dikenali', setelah.kartuSesi === true);

  /* ---------- 10. reset ---------- */
  await p.click('#btnReset');
  await p.waitForTimeout(400);
  const reset = await p.evaluate(() => ({
    count: (document.querySelector('#penCount').textContent || '').trim(),
    disabled: document.querySelector('#btnHitung').disabled,
    tersimpan: Object.keys(JSON.parse(localStorage.getItem('omnisense_situs_jawab_v2') || '{}')).length,
  }));
  cek('reset mengosongkan jawaban', reset.tersimpan === 0, reset.count);
  cek('tombol skor terkunci lagi', reset.disabled === true);

  /* ---------- 11. tampilan ---------- */
  const tampil = await p.evaluate(() => {
    const sw = document.documentElement.scrollWidth, cw = document.documentElement.clientWidth;
    return { overflow: sw > cw + 1 ? sw - cw : 0, err: 0 };
  });
  cek('tidak ada luapan horizontal', tampil.overflow === 0, '(' + tampil.overflow + 'px)');
  cek('tanpa error konsol', err.length === 0, err.slice(0, 3).join(' | '));

  await b.close();
  console.log('\nHasil: ' + lulus + ' lulus, ' + gagal + ' gagal');
  process.exit(gagal ? 1 : 0);
})();
