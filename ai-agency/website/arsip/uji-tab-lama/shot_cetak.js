#!/usr/bin/env node
'use strict';
// Tangkap tampilan mode cetak (apa yang benar-benar tercetak jadi PDF).
const fs = require('fs'), path = require('path'), os = require('os');
function loadChromium() {
  for (const c of [process.env.PW_CORE, '/tmp/camofox/node_modules/playwright-core', 'playwright-core']) {
    if (!c) continue;
    try { return require(c).chromium; } catch (e) {}
  }
  throw new Error('playwright-core tidak ditemukan.');
}
function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const base = path.join(os.homedir(), '.cache/ms-playwright');
  if (!fs.existsSync(base)) return undefined;
  for (const d of fs.readdirSync(base)) {
    const p = path.join(base, d, 'chrome-linux64/chrome');
    if (fs.existsSync(p)) return p;
  }
}
const FILE = path.resolve(process.argv[2] || 'index.html');
const JAWAB = { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 };
(async () => {
  const browser = await loadChromium().launch({ executablePath: findChrome() });
  const ctx = await browser.newContext({ viewport: { width: 900, height: 1400 } });
  const page = await ctx.newPage();
  await page.goto('file://' + FILE, { waitUntil: 'load' });
  await page.waitForTimeout(1800);
  for (const [k, v] of Object.entries(JAWAB)) {
    await page.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
  }
  await page.click('#penHitung');
  await page.waitForTimeout(3200);
  await page.emulateMedia({ media: 'print' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'pratinjau/hasil-04-tampilan-cetak.png', fullPage: true });
  console.log('pratinjau/hasil-04-tampilan-cetak.png');
  await browser.close();
})();
