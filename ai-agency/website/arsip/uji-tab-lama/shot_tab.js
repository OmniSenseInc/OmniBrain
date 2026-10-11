#!/usr/bin/env node
'use strict';
/* Tangkap gambar bagian penilaian: kondisi awal, hasil, dan HP. */
const fs = require('fs');
const path = require('path');
const os = require('os');
function loadChromium() {
  for (const c of ['/tmp/camofox/node_modules/playwright-core', 'playwright-core']) {
    try { return require(c).chromium; } catch (e) {}
  }
  throw new Error('playwright-core tidak ditemukan');
}
function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = path.join(os.homedir(), '.cache/ms-playwright');
  for (const d of fs.readdirSync(base)) {
    const p = path.join(base, d, 'chrome-linux64/chrome');
    if (fs.existsSync(p)) return p;
  }
}
const FILE = path.resolve(process.argv[2] || 'index.html');
const JAWAB = { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 };
(async () => {
  const browser = await loadChromium().launch({ executablePath: findChrome() });
  fs.mkdirSync('/tmp/shot_tab', { recursive: true });
  for (const [nama, vp, isMob] of [['desktop', { width: 1440, height: 950 }, false], ['mobile', { width: 390, height: 844 }, true]]) {
    const ctx = await browser.newContext({ viewport: vp, isMobile: isMob, hasTouch: isMob, deviceScaleFactor: 1 });
    const page = await ctx.newPage();
    await page.goto('file://' + FILE, { waitUntil: 'load' });
    await page.waitForTimeout(700);
    const sec = page.locator('#penilaian');
    await sec.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    await sec.screenshot({ path: `/tmp/shot_tab/${nama}-soal.png` });
    for (const [k, v] of Object.entries(JAWAB)) await page.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
    await page.waitForTimeout(200);
    await page.click('#penHitung');
    await page.waitForTimeout(1800);
    await sec.screenshot({ path: `/tmp/shot_tab/${nama}-hasil.png` });
    await ctx.close();
  }
  await browser.close();
  console.log('ok');
})();
