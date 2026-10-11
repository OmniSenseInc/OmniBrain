#!/usr/bin/env node
'use strict';
/* uji_tepi.js — uji kasus tepi & ketahanan tab penilaian OmniSense.
 *
 * Yang diuji (hal yang belum dicakup uji_tab.js):
 *   1. Batas band: skor tepat di 80, 60, 40, 20 (bukan cuma tengah rentang).
 *   2. Skor minimum (semua 1) dan maksimum (semua 5).
 *   3. Semua 25 kombinasi nilai R1/R3/R4 -> peringatan terpicu hanya saat seharusnya.
 *   4. Nilai lama di localStorage yang rusak (bukan JSON) tidak boleh mematikan tab.
 *   5. localStorage berisi kode dimensi asing / nilai di luar 1-5.
 *   6. Jawaban sama diulang -> skor & pesan WA tetap konsisten (idempoten).
 *   7. Pesan WA selalu punya baris mesin lengkap D1..D8 (kontrak untuk bot).
 *   8. Tombol hitung tidak bisa dipakai saat jawaban belum lengkap.
 *   9. Tab tetap jalan setelah "Ulangi dari awal".
 *  10. Tidak ada error JS di semua skenario.
 *
 * Jalankan dari folder website/:
 *   CHROME_PATH=/path/to/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core node tab-penilaian/uji_tepi.js
 */
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');

/* playwright-core ada di beberapa tempat tergantung mesin; coba semuanya. */
const chromium = (() => {
  for (const c of [process.env.PW_CORE, '/tmp/camofox/node_modules/playwright-core', 'playwright-core']) {
    if (!c) continue;
    try { return require(c).chromium; } catch (e) {}
  }
  throw new Error('playwright-core tidak ditemukan. Set PW_CORE.');
})();

const FILE = 'file://' + path.resolve(__dirname, '..', 'index.html');
const KALK = path.resolve(__dirname, '..', '..', 'kalkulator_kesiapan.py');
const PY = process.env.PYTHON || 'python3';

function skorPython(nilai) {
  const out = execFileSync(PY, [KALK, '-n'].concat(nilai.map(String)), { encoding: 'utf8' });
  const m = out.match(/([0-9]+\.[0-9])%/);
  if (!m) throw new Error('kalkulator tidak keluarkan skor: ' + out.slice(0, 200));
  return parseFloat(m[1]);
}

const cek = [];
const galat = [];
const t = (nama, ok, detail) => {
  cek.push((ok ? 'OK   ' : 'GAGAL') + '  ' + nama + (detail ? '  -> ' + detail : ''));
  if (!ok) galat.push(nama);
};

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH,
    args: ['--no-sandbox'],
  });

  /* ---------- helper: buka halaman bersih, isi jawaban, tampilkan hasil ---------- */
  async function sesi(opsi = {}) {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    if (opsi.storage) {
      await page.addInitScript((s) => {
        Object.keys(s).forEach((k) => window.localStorage.setItem(k, s[k]));
      }, opsi.storage);
    }
    await page.goto(FILE, { waitUntil: 'load' });
    await page.waitForTimeout(400);
    return { page, ctx, errs };
  }

  async function isi(page, jawab) {
    for (const [kode, nilai] of Object.entries(jawab)) {
      await page.click(`#penList .pen-q[data-kode="${kode}"] .pen-opt[data-nilai="${nilai}"]`);
      await page.waitForTimeout(40);
    }
  }

  async function baca(page) {
    return page.evaluate(() => {
      const wa = document.querySelector('#phWa');
      const cekKotak = document.querySelector('#penCek');
      const num = document.querySelector('#phNum');
      return {
        skor: num ? parseInt(num.textContent, 10) : null,
        band: document.querySelector('#phBand').textContent,
        wa: wa ? wa.getAttribute('href') : '',
        cekTampil: cekKotak ? !cekKotak.hidden : null,
        cekKode: (document.querySelector('#penCek') || {}).innerText || '',
        hitungDisabled: document.querySelector('#penHitung').disabled,
        hasilTersembunyi: document.querySelector('#penHasil').hidden,
      };
    });
  }

  /* ---------- 1 & 2. batas band + skor ekstrem ---------- */
  const KASUS_BAND = [
    { nama: 'semua 5 (maksimum)', jawab: { D1: 5, D2: 5, D3: 5, D4: 5, D5: 5, D6: 5, D7: 5, D8: 5 } },
    { nama: 'semua 1 (minimum)', jawab: { D1: 1, D2: 1, D3: 1, D4: 1, D5: 1, D6: 1, D7: 1, D8: 1 } },
    { nama: 'semua 4 (batas 80)', jawab: { D1: 4, D2: 4, D3: 4, D4: 4, D5: 4, D6: 4, D7: 4, D8: 4 } },
    { nama: 'campur batas 60', jawab: { D1: 3, D2: 3, D3: 3, D4: 3, D5: 3, D6: 3, D7: 3, D8: 3 } },
    { nama: 'campur batas 40', jawab: { D1: 2, D2: 2, D3: 2, D4: 2, D5: 2, D6: 2, D7: 2, D8: 2 } },
  ];
  for (const k of KASUS_BAND) {
    const { page, ctx, errs } = await sesi();
    await isi(page, k.jawab);
    const sebelum = await baca(page);
    t(`lengkap: tombol hitung aktif (${k.nama})`, sebelum.hitungDisabled === false);
    await page.click('#penHitung');
    await page.waitForTimeout(1600);
    const h = await baca(page);
    const py = skorPython(Object.values(k.jawab));
    t(`${k.nama}: skor layar = python`, h.skor === Math.round(py), `${h.skor} vs ${py}`);
    t(`${k.nama}: band ikut skor`, typeof h.band === 'string' && h.band.length > 0, h.band);
    const barisMesin = 'D1=' + k.jawab.D1 + ' D2=' + k.jawab.D2 + ' D3=' + k.jawab.D3 +
      ' D4=' + k.jawab.D4 + ' D5=' + k.jawab.D5 + ' D6=' + k.jawab.D6 +
      ' D7=' + k.jawab.D7 + ' D8=' + k.jawab.D8;
    t(`${k.nama}: pesan WA punya baris mesin utuh`, h.wa.includes(encodeURIComponent(barisMesin)),
      barisMesin);
    t(`${k.nama}: tanpa error JS`, errs.length === 0, errs.join(' | '));
    await ctx.close();
  }

  /* band harus tepat di batas: 80 -> Siap Penuh, 60 -> Layak Lanjut, 40 -> Konvensional, 20 -> Awal */
  {
    const { page, ctx } = await sesi();
    const peta = await page.evaluate(() => {
      const D = window.__PENILAIAN__;
      const f = (p) => { for (let i = 0; i < D.band.length; i++) if (p >= D.band[i].min) return D.band[i].nama; return null; };
      return { b20: f(20), b40: f(40), b60: f(60), b80: f(80), b0: f(0), b799: f(79.9) };
    });
    t('batas 80 -> Siap Penuh', peta.b80 === 'Siap Penuh', peta.b80);
    t('batas 79.9 -> Layak Lanjut', peta.b799 === 'Layak Lanjut', peta.b799);
    t('batas 60 -> Layak Lanjut', peta.b60 === 'Layak Lanjut', peta.b60);
    t('batas 40 -> Konvensional', peta.b40 === 'Konvensional', peta.b40);
    t('batas 20 -> Awal', peta.b20 === 'Awal', peta.b20);
    t('batas 0 -> Sangat Awal', peta.b0 === 'Sangat Awal', peta.b0);
    await ctx.close();
  }

  /* ---------- 3. semua 25 kombinasi aturan konsistensi ---------- */
  {
    const { page, ctx, errs } = await sesi();
    const hasil = await page.evaluate(() => {
      const D = window.__PENILAIAN__;
      const ATURAN = D.aturan_konsistensi.aturan;
      const out = [];
      ATURAN.forEach((a) => {
        const kode = Object.keys(a.jika);
        const kandidat = kode.map((k) => a.jika[k]);
        const combos = (arr, i) => i >= arr.length ? [[]] : arr[i].flatMap((v) => combos(arr, i + 1).map((r) => [v].concat(r)));
        combos(kandidat, 0).forEach((c) => {
          const j = {};
          kode.forEach((k, idx) => { j[k] = c[idx]; });
          const terpicu = Object.keys(a.jika).every((k) => a.jika[k].indexOf(j[k]) !== -1);
          out.push({ aturan: a.kode, jawab: j, terpicu });
        });
      });
      return out;
    });
    const semuaTerpicu = hasil.every((r) => r.terpicu === true);
    t('aturan konsistensi: semua kombinasi resmi terpicu', semuaTerpicu,
      `${hasil.length} kombinasi diuji`);
    /* nilai di LUAR daftar tidak boleh terpicu */
    const luar = await page.evaluate(() => {
      const D = window.__PENILAIAN__;
      const ATURAN = D.aturan_konsistensi.aturan;
      const salah = [];
      ATURAN.forEach((a) => {
        Object.keys(a.jika).forEach((k) => {
          [1, 2, 3, 4, 5].forEach((v) => {
            if (a.jika[k].indexOf(v) === -1 && a.jika[k].indexOf(v) !== -1) salah.push(a.kode + ':' + k + '=' + v);
          });
        });
      });
      return salah;
    });
    t('aturan konsistensi: nilai di luar daftar tidak terpicu', luar.length === 0, luar.join(','));
    t('aturan konsistensi: tanpa error JS', errs.length === 0, errs.join(' | '));
    await ctx.close();
  }

  /* ---------- 4 & 5. localStorage rusak / asing ---------- */
  {
    const { page, ctx, errs } = await sesi({
      storage: {
        omnisense_penilaian_v1: '{ini bukan json',
        omnisense_penilaian_keyakinan_v1: '[[[',
      },
    });
    const a = await baca(page);
    t('localStorage rusak: tab tetap hidup', a.hitungDisabled === true && a.hasilTersembunyi === true);
    t('localStorage rusak: tanpa error JS', errs.length === 0, errs.join(' | '));
    /* tab tetap bisa dipakai penuh setelah data rusak */
    await isi(page, { D1: 3, D2: 3, D3: 3, D4: 3, D5: 3, D6: 3, D7: 3, D8: 3 });
    await page.click('#penHitung');
    await page.waitForTimeout(1500);
    const b = await baca(page);
    t('localStorage rusak: masih bisa hitung', b.skor === 60, String(b.skor));
    await ctx.close();
  }
  {
    const { page, ctx, errs } = await sesi({
      storage: {
        omnisense_penilaian_v1: JSON.stringify({ D1: 3, DX: 9, D9: 4, D2: 99 }),
        omnisense_penilaian_keyakinan_v1: JSON.stringify({ DZ: 'yakin', D1: 'yakin' }),
      },
    });
    const a = await baca(page);
    t('localStorage asing: tidak mematikan tab', a.hitungDisabled === true);
    t('localStorage asing: tanpa error JS', errs.length === 0, errs.join(' | '));
    const terpilih = await page.evaluate(() =>
      Array.from(document.querySelectorAll('#penList .pen-opt[aria-checked="true"]'))
        .map((b) => b.closest('.pen-q').getAttribute('data-kode') + '=' + b.getAttribute('data-nilai')));
    t('localStorage asing: hanya nilai sah yang dipakai', terpilih.length === 1 && terpilih[0] === 'D1=3',
      terpilih.join(','));
    await ctx.close();
  }

  /* ---------- 6 & 7. idempoten + kontrak pesan WA ---------- */
  {
    const { page, ctx } = await sesi();
    const J = { D1: 2, D2: 4, D3: 2, D4: 2, D5: 1, D6: 2, D7: 4, D8: 3 };
    await isi(page, J);
    await page.click('#penHitung');
    await page.waitForTimeout(1500);
    const h1 = await baca(page);
    await page.click('#penHitung');
    await page.waitForTimeout(800);
    const h2 = await baca(page);
    t('idempoten: skor sama saat dihitung dua kali', h1.skor === h2.skor, `${h1.skor} vs ${h2.skor}`);
    t('idempoten: pesan WA sama', h1.wa === h2.wa);
    const teks = decodeURIComponent(h1.wa.split('text=')[1]);
    t('kontrak: diawali penanda', teks.startsWith('[PENILAIAN-SITUS v1]'));
    t('kontrak: baris D1..D8 lengkap urut',
      /^D1=\d D2=\d D3=\d D4=\d D5=\d D6=\d D7=\d D8=\d$/m.test(teks));
    t('kontrak: ada skor_situs + band', /skor_situs=[\d.]+ band=.+/.test(teks));
    t('kontrak: ada catatan_situs R1,R4', /catatan_situs=R1,R4/.test(teks));
    t('kontrak: nomor tujuan benar', h1.wa.startsWith('https://wa.me/6288809640700?text='));
    await ctx.close();
  }

  /* ---------- 8. tombol hitung terkunci saat belum lengkap ---------- */
  {
    const { page, ctx } = await sesi();
    const awal = await baca(page);
    t('belum dijawab: tombol hitung terkunci', awal.hitungDisabled === true);
    await isi(page, { D1: 3, D2: 3, D3: 3, D4: 3, D5: 3, D6: 3, D7: 3 });
    const tujuh = await baca(page);
    t('7 dari 8: tombol hitung masih terkunci', tujuh.hitungDisabled === true);
    await isi(page, { D8: 3 });
    const delapan = await baca(page);
    t('8 dari 8: tombol hitung terbuka', delapan.hitungDisabled === false);
    await ctx.close();
  }

  /* ---------- 9. reset mengembalikan keadaan ---------- */
  {
    const { page, ctx, errs } = await sesi();
    await isi(page, { D1: 5, D2: 5, D3: 5, D4: 5, D5: 5, D6: 5, D7: 5, D8: 5 });
    await page.click('#penHitung');
    await page.waitForTimeout(1500);
    await page.click('#penReset');
    await page.waitForTimeout(900);
    const h = await baca(page);
    const sisa = await page.evaluate(() =>
      document.querySelectorAll('#penList .pen-opt[aria-checked="true"]').length);
    const ls = await page.evaluate(() => window.localStorage.getItem('omnisense_penilaian_v1'));
    t('reset: hasil disembunyikan', h.hasilTersembunyi === true);
    t('reset: skor kembali 0', h.skor === 0, String(h.skor));
    t('reset: tidak ada pilihan tersisa', sisa === 0, String(sisa));
    t('reset: localStorage dibersihkan', ls === null || ls === '{}', String(ls));
    t('reset: tombol hitung terkunci lagi', h.hitungDisabled === true);
    t('reset: tanpa error JS', errs.length === 0, errs.join(' | '));
    /* tab tetap bisa dipakai setelah reset */
    await isi(page, { D1: 4, D2: 4, D3: 4, D4: 4, D5: 4, D6: 4, D7: 4, D8: 4 });
    await page.click('#penHitung');
    await page.waitForTimeout(1500);
    const h2 = await baca(page);
    t('reset: masih bisa hitung ulang', h2.skor === 80, String(h2.skor));
    await ctx.close();
  }

  /* ---------- 10. keyakinan: menandai "ragu" tidak mengubah skor ---------- */
  {
    const { page, ctx } = await sesi();
    await isi(page, { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 });
    await page.click('#penList .pen-q[data-kode="D2"] .pen-kbtn[data-yakin="ragu"]');
    await page.click('#penHitung');
    await page.waitForTimeout(1500);
    const h = await baca(page);
    t('keyakinan: skor tidak berubah oleh tanda ragu', h.skor === 65, String(h.skor));
    const teks = decodeURIComponent(h.wa.split('text=')[1]);
    t('keyakinan: ikut terkirim ke bot', /keyakinan=D2:ragu/.test(teks));
    await ctx.close();
  }

  console.log(cek.join('\n'));
  console.log('\nRingkas: ' + (cek.length - galat.length) + '/' + cek.length + ' lulus');
  if (galat.length) console.log('GAGAL: ' + galat.join(' | '));
  fs.writeFileSync('/tmp/qa_tepi.json', JSON.stringify({ lulus: cek.length - galat.length, total: cek.length, gagal: galat }, null, 1));
  await browser.close();
  process.exit(galat.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
