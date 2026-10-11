#!/usr/bin/env node
'use strict';
/* uji_cetak.js — uji mode cetak/simpan-PDF pada tab penilaian.
 *
 * Yang diuji: setelah 8 jawaban diisi, menekan "Cetak / simpan PDF" harus
 * menghasilkan dokumen PDF yang memuat hasil (skor, kategori, langkah), tanpa
 * elemen antarmuka (nav, rail, form) yang ikut tercetak.
 *
 * Jalankan dari folder website/:
 *   CHROME_PATH=... PW_CORE=... node tab-penilaian/uji_cetak.js
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

function loadChromium() {
  for (const c of [process.env.PW_CORE, '/tmp/camofox/node_modules/playwright-core', 'playwright-core']) {
    if (!c) continue;
    try { return require(c).chromium; } catch (e) {}
  }
  throw new Error('playwright-core tidak ditemukan. Set PW_CORE.');
}
function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = path.join(os.homedir(), '.cache/ms-playwright');
  if (!fs.existsSync(base)) return undefined;
  for (const d of fs.readdirSync(base)) {
    const p = path.join(base, d, 'chrome-linux64/chrome');
    if (fs.existsSync(p)) return p;
  }
  return undefined;
}

const FILE = path.resolve(process.argv[2] || 'index.html');
const OUT = path.resolve('pratinjau');
const JAWAB = { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 };
let gagal = 0;
function cek(nama, syarat, info) {
  if (syarat) console.log('OK     ' + nama + (info ? '  -> ' + info : ''));
  else { console.log('GAGAL  ' + nama + (info ? '  -> ' + info : '')); gagal++; }
}

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e)));

  await page.goto('file://' + FILE, { waitUntil: 'load' });
  await page.waitForTimeout(1800);

  for (const [k, v] of Object.entries(JAWAB)) {
    await page.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
  }
  await page.click('#penHitung');
  await page.waitForTimeout(3000);

  const skor = await page.$eval('#phNum', el => el.textContent.trim());
  const band = await page.$eval('#phBand', el => el.textContent.trim());
  cek('hasil tampil setelah hitung', skor.indexOf('65') === 0, skor + ' / ' + band);

  // mode cetak: elemen antarmuka harus disembunyikan, hasil tetap tampak
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(400);
  const tampil = async (sel) => {
    const el = await page.$(sel);
    if (!el) return false;
    return await el.evaluate(n => {
      const s = getComputedStyle(n);
      return s.display !== 'none' && s.visibility !== 'hidden';
    });
  };
  cek('cetak: nav disembunyikan', !(await tampil('.nav')));
  cek('cetak: rail peta bagian disembunyikan', !(await tampil('.ixbar')));
  cek('cetak: form penilaian disembunyikan', !(await tampil('.pen')));
  cek('cetak: hasil skor tetap tampak', await tampil('.pen-hasil'));
  cek('cetak: tombol aksi disembunyikan', !(await tampil('.ph-aksi')));

  // PDF nyata (Chromium headless: media cetak)
  const pdfPath = path.join(OUT, 'hasil-03-hasil-cetak.pdf');
  await page.pdf({ path: pdfPath, format: 'A4', printBackground: true });
  const ukuran = fs.statSync(pdfPath).size;
  cek('PDF terbentuk', ukuran > 8000, ukuran + ' byte -> ' + pdfPath);

  cek('tanpa error JS', errs.length === 0, errs.join(' | ') || 'bersih');

  await browser.close();
  console.log('\n' + (gagal === 0 ? 'Ringkas: semua lulus' : 'Ringkas: ' + gagal + ' GAGAL'));
  process.exit(gagal === 0 ? 0 : 1);
})();
