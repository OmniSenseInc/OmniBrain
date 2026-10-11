#!/usr/bin/env node
'use strict';
/* shot_final.js — pratinjau resmi situs OmniSense (setelah paket deploy).
 *
 * Jalankan dari folder website/:
 *   CHROME_PATH=/path/to/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core node scripts/shot_final.js
 *
 * Hasil: pratinjau/final-01..07*.png  (menimpa set lama — set lama sudah diarsipkan
 *        di pratinjau/arsip-tema/tema-sebelum-navy/)
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

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const shots = [];

  async function shot(page, name, opsi) {
    const f = path.join(OUT, name + '.png');
    await page.screenshot(Object.assign({ path: f }, opsi || {}));
    shots.push(name + ' -> ' + f);
  }

  // 1. desktop: hero
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    await page.goto('file://' + FILE, { waitUntil: 'load' });
    await page.waitForTimeout(2600);            // biar animasi hero selesai
    await shot(page, 'final-01-hero');

    // 2. desktop: bagian penilaian (kosong)
    await page.evaluate(() => document.querySelector('#penilaian').scrollIntoView({ block: 'start' }));
    await page.waitForTimeout(900);
    await shot(page, 'final-02-penilaian-kosong');

    // 3. desktop: hasil setelah 8 jawaban
    for (const [k, v] of Object.entries(JAWAB)) {
      await page.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
    }
    await page.click('#penHitung');
    await page.waitForTimeout(4200);            // tunggu animasi angka cakram selesai (65,0)
    await page.evaluate(() => document.querySelector('#penHasil').scrollIntoView({ block: 'start' }));
    await page.waitForTimeout(700);
    await shot(page, 'final-03-hasil-skor');
    await ctx.close();
  }

  // 4. mobile: hero + hasil
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true });
    const page = await ctx.newPage();
    await page.goto('file://' + FILE, { waitUntil: 'load' });
    await page.waitForTimeout(2600);
    await shot(page, 'final-04-mobile-hero');
    await page.evaluate(() => document.querySelector('#penilaian').scrollIntoView({ block: 'start' }));
    await page.waitForTimeout(900);
    await shot(page, 'final-05-mobile-penilaian');
    await ctx.close();
  }

  // 5. reduced motion
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, reducedMotion: 'reduce' });
    const page = await ctx.newPage();
    await page.goto('file://' + FILE, { waitUntil: 'load' });
    await page.waitForTimeout(700);
    await shot(page, 'final-06-tanpa-gerak');
    await ctx.close();
  }

  // 6. halaman 404
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    await page.goto('file://' + path.resolve('404.html'), { waitUntil: 'load' });
    await page.waitForTimeout(900);
    await shot(page, 'final-07-404');
    await ctx.close();
  }

  await browser.close();
  console.log(shots.join('\n'));
})();
