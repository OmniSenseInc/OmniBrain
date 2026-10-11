#!/usr/bin/env node
'use strict';
/* shot_legal.js — pratinjau halaman Kebijakan Privasi + kartu tautan (og:image).
 * Jalankan dari folder website/:
 *   CHROME_PATH=/path/to/chrome PW_CORE=/tmp/camofox/node_modules/playwright-core node scripts/shot_legal.js
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

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const out = path.resolve('pratinjau');
  const hasil = [];

  // privacy.html — penuh (fullPage) + layar pertama
  {
    const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    await page.goto('file://' + path.resolve('privacy.html'), { waitUntil: 'load' });
    await page.waitForTimeout(1200);
    await page.screenshot({ path: path.join(out, 'final-08-privasi-atas.png') });
    await page.screenshot({ path: path.join(out, 'final-09-privasi-penuh.png'), fullPage: true });
    const overflow = await page.evaluate(() => [document.documentElement.scrollWidth, window.innerWidth]);
    hasil.push('privasi: error=' + errs.length + ' overflow=' + overflow.join('/'));
    await ctx.close();
  }

  // mobile privacy
  {
    const ctx = await browser.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    await page.goto('file://' + path.resolve('privacy.html'), { waitUntil: 'load' });
    await page.waitForTimeout(1000);
    await page.screenshot({ path: path.join(out, 'final-10-privasi-mobile.png') });
    await ctx.close();
  }

  await browser.close();
  console.log(hasil.join('\n'));
})();
