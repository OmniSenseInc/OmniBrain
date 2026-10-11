#!/usr/bin/env node
'use strict';
/* uji_data.js — uji paritas DATA antara sumber dan yang benar-benar jalan di situs.
 *
 * uji_paritas.js membandingkan RUMUS (skor JS vs kalkulator Python).
 * Berkas ini membandingkan ISI: apakah window.__PENILAIAN__ di index.html
 * masih sama dengan tab-penilaian/pertanyaan.json (sumbernya).
 *
 * Ini menangkap bug yang tidak terlihat oleh uji lain:
 *   - pesan aturan konsistensi diedit di satu tempat saja (situs vs bot)
 *   - bobot / ambang band / daftar aturan berubah di salah satu sisi
 *   - generator bangun_tab.py tidak dijalankan ulang setelah pertanyaan.json diubah
 *
 * Jalankan dari folder website/:
 *   CHROME_PATH=/path/to/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core node tab-penilaian/uji_data.js
 */
const path = require('path');
const fs = require('fs');

const chromium = (() => {
  for (const c of [process.env.PW_CORE, '/tmp/camofox/node_modules/playwright-core', 'playwright-core']) {
    if (!c) continue;
    try { return require(c).chromium; } catch (e) {}
  }
  throw new Error('playwright-core tidak ditemukan. Set PW_CORE.');
})();

const WEB = path.resolve(__dirname, '..');
const KALK = path.resolve(WEB, '..', 'kalkulator_kesiapan.py');
const PY = process.env.PYTHON || 'python3';

const cek = [];
const galat = [];
const t = (nama, ok, detail) => {
  cek.push((ok ? 'OK   ' : 'GAGAL') + '  ' + nama + (detail ? '  -> ' + detail : ''));
  if (!ok) galat.push(nama);
};

(async () => {
  const sumber = JSON.parse(fs.readFileSync(path.join(__dirname, 'pertanyaan.json'), 'utf8'));

  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH,
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  await page.goto('file://' + path.join(WEB, 'index.html'), { waitUntil: 'load' });
  await page.waitForTimeout(500);
  const situs = await page.evaluate(() => window.__PENILAIAN__);

  /* ---------- 1. struktur utama ---------- */
  t('jumlah dimensi sama', situs.dimensi.length === sumber.dimensi.length,
    `${situs.dimensi.length} vs ${sumber.dimensi.length}`);
  t('kode & nama dimensi sama (urut)',
    situs.dimensi.every((d, i) => d.kode === sumber.dimensi[i].kode && d.nama === sumber.dimensi[i].nama));
  t('bobot dimensi sama',
    situs.dimensi.every((d, i) => Math.abs(d.bobot - sumber.dimensi[i].bobot) < 1e-12),
    situs.dimensi.map((d) => d.bobot).join(','));
  t('bobot berjumlah 1.0', Math.abs(situs.dimensi.reduce((a, d) => a + d.bobot, 0) - 1) < 1e-9);
  t('teks pilihan jawaban sama',
    situs.dimensi.every((d, i) => JSON.stringify(d.pilihan) === JSON.stringify(sumber.dimensi[i].pilihan)));

  /* ---------- 2. band ---------- */
  t('daftar band sama', JSON.stringify(situs.band) === JSON.stringify(sumber.band),
    situs.band.map((b) => b.min).join(','));

  /* ---------- 3. aturan konsistensi: pemicu DAN pesan ---------- */
  const aSitus = situs.aturan_konsistensi.aturan;
  const aSumber = sumber.aturan_konsistensi.aturan;
  t('jumlah aturan sama', aSitus.length === aSumber.length, `${aSitus.length} vs ${aSumber.length}`);
  t('kode aturan sama (urut)', aSitus.every((a, i) => a.kode === aSumber[i].kode),
    aSitus.map((a) => a.kode).join(','));
  t('pemicu aturan sama', aSitus.every((a, i) => JSON.stringify(a.jika) === JSON.stringify(aSumber[i].jika)));
  /* inilah pemeriksaan yang menangkap pesan R1/R4 yang tadi menyimpang */
  aSitus.forEach((a, i) => {
    t(`pesan ${a.kode} identik di situs & sumber`, a.pesan === aSumber[i].pesan,
      a.pesan === aSumber[i].pesan ? '' : 'situs: ' + a.pesan.slice(0, 70));
  });

  /* ---------- 4. kata-kata pesan harus cocok untuk SEMUA nilai pemicu ---------- */
  /* Aturan yang terpicu untuk nilai 4 DAN 5 tidak boleh berbunyi seolah jawabannya 5.
     Contoh salah: "bisa disebutkan cepat" padahal pemicunya juga D2=4
     ("bisa, perlu saya buka beberapa catatan"). */
  const FRASA_NILAI_5 = [
    'saat ini juga', 'sebutkan cepat', 'sebut sekarang', 'tersalin otomatis',
    'otomatis dan ada', 'minta tambahan', 'terhubung otomatis', 'terdokumentasi',
  ];
  aSitus.forEach((a) => {
    const nilaiPemicu = Object.keys(a.jika).flatMap((k) => a.jika[k]);
    const ada4 = nilaiPemicu.indexOf(4) !== -1;
    const ada5 = nilaiPemicu.indexOf(5) !== -1;
    if (ada4 && ada5) {
      const kena = FRASA_NILAI_5.filter((f) => a.pesan.toLowerCase().indexOf(f) !== -1);
      t(`${a.kode}: kata-kata tidak mengandaikan jawaban 5`, kena.length === 0,
        kena.length ? 'frasa khusus nilai 5: ' + kena.join(', ') : '');
    }
  });

  /* ---------- 5. keyakinan, skala, rekomendasi ---------- */
  t('daftar keyakinan sama', JSON.stringify(situs.keyakinan) === JSON.stringify(sumber.keyakinan));
  t('skala sama', JSON.stringify(situs.skala) === JSON.stringify(sumber.skala));
  t('rekomendasi per dimensi sama',
    JSON.stringify(situs.rekomendasi_dimensi) === JSON.stringify(sumber.rekomendasi_dimensi));
  t('urutan nilai sama', situs.urutan_nilai === sumber.urutan_nilai, situs.urutan_nilai);
  t('penanda pesan sama', situs.format_pesan.penanda === sumber.format_pesan.penanda);

  /* ---------- 6. band di kalkulator python harus sama ambangnya ---------- */
  const pyBand = fs.readFileSync(KALK, 'utf8');
  const ambang = [...pyBand.matchAll(/^\s*\((\d+),\s*"([^"]+)"/gm)].map((m) => Number(m[1]));
  const ambangSitus = situs.band.map((b) => b.min);
  t('ambang band python = situs',
    JSON.stringify(ambang.slice(0, 5)) === JSON.stringify(ambangSitus),
    `py ${ambang.slice(0, 5).join(',')} vs situs ${ambangSitus.join(',')}`);

  /* ---------- 7. skor tepat di ambang harus masuk band ATAS (bug floating point) ----------
     PENTING: uji ini lewat API asli situs (OmniSensePenilaian), bukan menyalin
     ulang rumusnya di uji. Menyalin rumus membuat uji menguji dirinya sendiri. */
  const HARAP = { 1: 'Awal', 2: 'Konvensional', 3: 'Layak Lanjut', 4: 'Siap Penuh', 5: 'Siap Penuh' };
  const lewatApi = await page.evaluate(() => {
    const O = window.OmniSensePenilaian;
    const out = {};
    [1, 2, 3, 4, 5].forEach((v) => {
      ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8'].forEach((k) => O.jawab(k, v));
      out[v] = { skor: O.skor(), band: O.band() };
    });
    return out;
  });
  Object.keys(HARAP).forEach((v) => {
    const r = lewatApi[v];
    t(`API situs: semua ${v} -> ${HARAP[v]}`, r.band === HARAP[v],
      `${r.skor}% ${r.band} (harus ${HARAP[v]})`);
    t(`API situs: semua ${v} -> ${v * 20}%`, Math.round(r.skor) === v * 20, String(r.skor));
  });

  /* ---------- 8. pesan aturan konsistensi harus akurat untuk SEMUA nilai yang memicunya ----------
     Aturan memicu untuk rentang nilai (mis. R1: D2 in [4,5] + D3 in [1,2]), tetapi teksnya
     dulu hanya menggambarkan nilai tertinggi (mis. "bisa keluar tanpa menunggu orang lain"
     = jawaban 5), sehingga pengunjung yang menjawab 4 membaca kalimat yang bukan jawabannya.
     Uji ini menolak kata yang hanya cocok untuk satu ujung rentang. */
  const TERLARANG = ['tanpa menunggu orang lain', 'tersalin otomatis', 'mudah beradaptasi'];
  situs.aturan_konsistensi.aturan.forEach((a) => {
    TERLARANG.forEach((kata) => {
      t(`pesan ${a.kode}: tidak memakai kata khusus nilai tertinggi ("${kata}")`,
        a.pesan.indexOf(kata) === -1, a.pesan.slice(0, 90));
    });
  });
  /* Tiap aturan yang menyebut satu sisi rentang harus menyebut sisi lainnya juga,
     supaya pembaca nilai mana pun merasa kalimatnya cocok. */
  const PASANGAN = { R1: ['catatan', 'buku atau HP pribadi'], R3: ['cara baru', 'siap'], R4: ['salinan', 'sistem'] };
  Object.keys(PASANGAN).forEach((kode) => {
    const a = situs.aturan_konsistensi.aturan.find((x) => x.kode === kode);
    if (!a) return;
    const kurang = PASANGAN[kode].filter((kata) => a.pesan.indexOf(kata) === -1);
    t(`pesan ${kode}: menyebut kedua sisi rentang`, kurang.length === 0, 'kurang: ' + kurang.join(', '));
  });

  t('tanpa error JS', errs.length === 0, errs.join(' | '));

  console.log(cek.join('\n'));
  console.log('\nRingkas: ' + (cek.length - galat.length) + '/' + cek.length + ' lulus');
  if (galat.length) console.log('GAGAL: ' + galat.join(' | '));
  await browser.close();
  process.exit(galat.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
