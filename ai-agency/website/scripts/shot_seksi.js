#!/usr/bin/env node
'use strict';
// Tangkap tiap section index.html (untuk audit tampilan ramai).
// CHROME_PATH=... PW_CORE=... node scripts/shot_seksi.js
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
const OUT = path.resolve(process.argv[3] || '/tmp/audit-seksi');
fs.mkdirSync(OUT, { recursive: true });
const SEKSI = ['top', 'proses', 'kategori', 'dimensi', 'penilaian', 'output', 'kamus', 'hasil', 'kontak'];

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  await page.goto('file://' + FILE, { waitUntil: 'load' });
  await page.waitForTimeout(2600);
  for (const id of SEKSI) {
    const el = await page.$('#' + id);
    if (!el) { console.log('LEWAT (tidak ada): #' + id); continue; }
    await el.scrollIntoViewIfNeeded();
    await page.waitForTimeout(700);
    const f = path.join(OUT, id + '.png');
    await el.screenshot({ path: f });
    console.log(id + ' -> ' + f);
  }
  await browser.close();
})();
