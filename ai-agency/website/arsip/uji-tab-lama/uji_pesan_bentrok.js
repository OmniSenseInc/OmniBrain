#!/usr/bin/env node
'use strict';
/* uji_pesan_bentrok.js — bukti apa yang DILIHAT pengunjung saat aturan konsistensi terpicu.
 *
 * Menjawab persis seperti laporan klien (D1=2 D2=4 D3=2 D4=2 D5=1 D6=2 D7=4 D8=3),
 * lalu mencetak: kotak peringatan (#penCek), pesan keterbatasan (#phLimit), dan isi pesan WA.
 *
 * Jalankan dari folder website/:
 *   CHROME_PATH=/path/to/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core node tab-penilaian/uji_pesan_bentrok.js
 */
const { chromium } = require(process.env.PW_CORE || 'playwright-core');
const path = require('path');

const JAWABAN = { D1: 2, D2: 4, D3: 2, D4: 2, D5: 1, D6: 2, D7: 4, D8: 3 };

(async () => {
  const browser = await chromium.launch({
    executablePath: process.env.CHROME_PATH,
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const err = [];
  page.on('pageerror', e => err.push(String(e)));
  await page.goto('file://' + path.resolve(__dirname, '..', 'index.html'));
  await page.waitForTimeout(1200);

  // buka tab penilaian
  const tab = await page.$('a[href="#penilaian"], [data-buka-penilaian]');
  if (tab) { await tab.click(); await page.waitForTimeout(600); }

  for (const [kode, nilai] of Object.entries(JAWABAN)) {
    const sel = `[data-kode="${kode}"] .pen-opt[data-nilai="${nilai}"]`;
    const el = await page.$(sel);
    if (!el) { console.log('TIDAK KETEMU: ' + sel); continue; }
    await el.click();
    await page.waitForTimeout(80);
  }

  await page.click('#penHitung');
  await page.waitForTimeout(4200);

  const out = await page.evaluate(() => {
    const cek = document.querySelector('#penCek');
    const lim = document.querySelector('#phLimit');
    const wa = document.querySelector('#phWa');
    const skor = document.querySelector('#phNum');
    const band = document.querySelector('#phBand');
    const jawaban = {};
    document.querySelectorAll('[data-kode]').forEach(li => {
      const aktif = li.querySelector('.pen-opt.aktif, .pen-opt[aria-checked="true"]');
      if (aktif) jawaban[li.getAttribute('data-kode')] = aktif.getAttribute('data-nilai');
    });
    return {
      peringatan_terlihat: cek ? !cek.hidden : null,
      peringatan_teks: cek ? cek.innerText.trim() : '',
      limit_terlihat: lim ? !lim.hidden : null,
      limit_teks: lim ? lim.innerText.trim() : '',
      skor_teks: skor ? skor.innerText.trim() : '',
      band_teks: band ? band.innerText.trim() : '',
      jawaban_terpilih: jawaban,
      wa_href: wa ? wa.getAttribute('href') : '',
    };
  });

  console.log(JSON.stringify(out, null, 2));
  if (err.length) console.log('ERROR JS: ' + err.join(' | '));

  // bukti visual untuk tim (kotak peringatan + keterbatasan)
  const kotak = await page.$('#penHasil');
  if (kotak) {
    await kotak.screenshot({ path: path.resolve(__dirname, '..', 'pratinjau', 'final-11-peringatan-bentrok.png') });
    console.log('screenshot: pratinjau/final-11-peringatan-bentrok.png');
  }
  await browser.close();
})();
