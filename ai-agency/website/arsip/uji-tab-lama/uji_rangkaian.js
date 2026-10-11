#!/usr/bin/env node
'use strict';
/* Uji rangkaian penuh: pesan yang benar-benar dihasilkan tombol WhatsApp di situs
 * diumpankan ke baca_penilaian.py (jalur bot), lalu dicocokkan dengan kalkulator.
 *
 * Jalankan:
 *   CHROME_PATH=... PW_CORE=... node tab-penilaian/uji_rangkaian.js
 */
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFileSync } = require('child_process');

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
  return undefined;
}

const FILE = path.resolve(process.argv[2] || 'index.html');
const SKRIP = path.resolve(__dirname, '../../baca_penilaian.py');
const JAWAB = { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 };
const YAKIN = { D2: 'ragu', D8: 'tidak_tahu' };

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
  page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });

  await page.goto('file://' + FILE, { waitUntil: 'load' });
  await page.waitForTimeout(500);
  for (const [k, v] of Object.entries(JAWAB)) {
    await page.click(`#penList .pen-q[data-kode="${k}"] .pen-opt[data-nilai="${v}"]`);
  }
  for (const [k, y] of Object.entries(YAKIN)) {
    await page.click(`#penList .pen-q[data-kode="${k}"] .pen-kbtn[data-yakin="${y}"]`);
  }
  await page.click('#penHitung');
  await page.waitForTimeout(1500);

  const href = await page.evaluate(() => document.querySelector('#phWa').href);
  const pesan = decodeURIComponent(href.split('text=')[1] || '');
  await browser.close();

  /* jalur bot: hitung ulang dari teks yang benar-benar dikirim pengunjung */
  const out = execFileSync('python3', [SKRIP, '--teks', pesan], { encoding: 'utf8' });
  const h = JSON.parse(out);

  const cek = [];
  const t = (nama, ok, detail) => cek.push((ok ? 'OK   ' : 'GAGAL') + '  ' + nama + (detail ? '  ->  ' + detail : ''));
  t('nomor tujuan tetap 6288809640700', href.indexOf('https://wa.me/6288809640700') === 0, href.slice(0, 42));
  t('bot mengenali pesan', h.dikenali === true);
  t('bot membaca 8 nilai', Object.keys(h.nilai).length === 8, JSON.stringify(h.nilai));
  t('bot menghitung ulang 65.0', Math.abs(h.skor_hitung_ulang - 65.0) < 0.05, String(h.skor_hitung_ulang));
  t('tidak ada selisih situs vs bot', h.selisih === 0.0, String(h.selisih));
  t('bot tahu 2 jawaban belum pasti', JSON.stringify(h.belum_pasti) === JSON.stringify(['D2', 'D8']), JSON.stringify(h.belum_pasti));
  t('bot tahu 2 dimensi terlemah', h.dua_terlemah[0] === 'D5', h.dua_terlemah.join(','));
  t('tanpa error halaman', errs.length === 0, errs.join(' | '));

  console.log(cek.join('\n'));
  console.log('\n--- pesan yang diterima bot ---');
  console.log(pesan.split('\n').slice(0, 5).join('\n'));
  console.log('--- ringkasan untuk bot ---');
  console.log(h.ringkas.join('\n'));
  process.exit(cek.some((x) => x.indexOf('GAGAL') === 0) ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
