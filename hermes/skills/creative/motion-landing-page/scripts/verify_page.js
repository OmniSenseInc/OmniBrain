#!/usr/bin/env node
'use strict';
/*
 * Headless verification for a local HTML artifact (landing page, prototype, deck).
 *
 * Usage:
 *   node verify_page.js <file.html> [outdir] [--eval "<js expression>"]...
 *                       [--scroll-to "<selector>"] [--click "<selector>"]
 *
 * Runs four passes: desktop, desktop-scrolled, mobile 390px, prefers-reduced-motion.
 * --scroll-to adds a pass with that element centred (scroll-linked rail and step state).
 * --click adds a pass that clicks a control first, then probes the state it produced
 *   (e.g. the motion on/off toggle).
 * Collects console errors, page errors, horizontal overflow, --eval values, screenshots.
 * Writes <outdir>/report.json and prints a compact JSON summary to stdout.
 *
 * Variants: this harness loads a plain file:// URL, so a page whose variant is chosen by query
 *   string or by clicking a control needs one pass per variant — extend this script (add a query
 *   option or a page.click on the variant control) instead of writing a separate throwaway
 *   verifier somewhere under /tmp.
 *
 * Env:
 *   PW_CORE=/path/to/playwright-core   (defaults to a few known install locations)
 *   CHROME_PATH=/path/to/chrome        (defaults to auto-discovery under ~/.cache/ms-playwright)
 */
const fs = require('fs');
const path = require('path');
const os = require('os');

const CORE_CANDIDATES = [
  process.env.PW_CORE,
  '/tmp/camofox/node_modules/playwright-core',
  'playwright-core',
];

function loadChromium() {
  const tried = [];
  for (const c of CORE_CANDIDATES) {
    if (!c) continue;
    tried.push(c);
    try { return require(c).chromium; } catch (e) { /* try next */ }
  }
  throw new Error('playwright-core not found. Set PW_CORE=/path/to/playwright-core. Tried: ' + tried.join(', '));
}

function findChrome() {
  if (process.env.CHROME_PATH) return process.env.CHROME_PATH;
  const bases = [path.join(os.homedir(), '.cache/ms-playwright'), '/ms-playwright'];
  const rels = [
    'chrome-linux64/chrome',
    'chrome-linux/chrome',
    'chrome-headless-shell-linux64/chrome-headless-shell',
    'chrome-mac/Chromium.app/Contents/MacOS/Chromium',
  ];
  for (const base of bases) {
    if (!fs.existsSync(base)) continue;
    for (const d of fs.readdirSync(base)) {
      for (const rel of rels) {
        const p = path.join(base, d, rel);
        if (fs.existsSync(p)) return p;
      }
    }
  }
  return undefined; // let playwright resolve its own browser
}

async function probe(page) {
  return page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
    docHeight: document.documentElement.scrollHeight,
    h1: (document.querySelector('h1') || {}).innerText || null,
    textHead: document.body.innerText.slice(0, 2000),
  }));
}

(async () => {
  const argv = process.argv.slice(2);
  const evals = [];
  const positional = [];
  let scrollToSel = null;
  let clickSel = null;
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--eval') evals.push(argv[++i]);
    else if (argv[i] === '--scroll-to') scrollToSel = argv[++i];
    else if (argv[i] === '--click') clickSel = argv[++i];
    else positional.push(argv[i]);
  }
  const file = positional[0];
  if (!file) {
    console.error('usage: node verify_page.js <file.html> [outdir] [--eval "<js>"]...');
    process.exit(2);
  }
  const abs = path.resolve(file);
  if (!fs.existsSync(abs)) {
    console.error(`verify_page: berkas tidak ada: ${abs}`);
    process.exit(2);
  }
  if (fs.statSync(abs).isDirectory()) {
    console.error(
      `verify_page: ${abs} itu DIREKTORI, bukan berkas HTML.\n` +
      `  Chromium akan merender daftar isi folder, h1 jadi "Index of …", dan pemeriksaan lolos palsu.\n` +
      `  Berikan path berkasnya, mis. ${path.join(abs, 'index.html')}`
    );
    process.exit(2);
  }
  if (!/\.(html?|svg)$/i.test(abs)) console.error(`verify_page: peringatan — ${abs} bukan .html/.htm/.svg`);
  const outdir = positional[1] || '/tmp/page-qa';
  fs.mkdirSync(outdir, { recursive: true });
  const url = 'file://' + abs;

  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});

  const report = {
    file: path.resolve(file),
    exe: exe || '(playwright default)',
    console: [],
    errors: [],
    passes: {},
    shots: [],
  };

  async function pass(name, viewport, opts = {}) {
    const ctx = await browser.newContext({
      viewport,
      deviceScaleFactor: 1,
      reducedMotion: opts.reduced ? 'reduce' : 'no-preference',
      isMobile: !!opts.mobile,
      hasTouch: !!opts.mobile,
    });
    const page = await ctx.newPage();
    page.on('console', (m) => {
      if (m.type() === 'error' || m.type() === 'warning') report.console.push(name + ': ' + m.type() + ': ' + m.text());
    });
    page.on('pageerror', (e) => report.errors.push(name + ': ' + e.message));

    await page.goto(url, { waitUntil: 'load' });
    await page.waitForTimeout(opts.waitMs || 2200);
    if (opts.click) {
      await page.click(opts.click);
      await page.waitForTimeout(opts.clickWaitMs || 1800);
    }
    if (opts.scrollTo) {
      await page.evaluate((sel) => {
        const el = document.querySelector(sel);
        if (el) el.scrollIntoView({ block: 'center' });
      }, opts.scrollTo);
      await page.waitForTimeout(900);
    } else if (opts.scroll) {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.45));
      await page.waitForTimeout(1200);
    }

    const data = await probe(page);
    const extras = {};
    for (const expr of evals) {
      try { extras[expr] = await page.evaluate(expr); }
      catch (e) { extras[expr] = 'ERROR: ' + e.message; }
    }

    const shot = path.join(outdir, name + '.png');
    await page.screenshot({ path: shot, fullPage: !opts.viewportOnly });

    report.passes[name] = { viewport, reducedMotion: !!opts.reduced, ...data, extras };
    report.shots.push(shot);
    await ctx.close();
  }

  await pass('01-desktop', { width: 1440, height: 900 });
  await pass('02-desktop-mid', { width: 1440, height: 900 }, { scroll: true, viewportOnly: true });
  await pass('03-mobile', { width: 390, height: 844 }, { mobile: true });
  await pass('04-reduced-motion', { width: 1440, height: 900 }, { reduced: true, waitMs: 1500 });
  if (scrollToSel) await pass('05-scroll-to', { width: 1440, height: 900 }, { scrollTo: scrollToSel, viewportOnly: true, waitMs: 1800 });
  if (clickSel) await pass('06-after-click', { width: 1440, height: 900 }, { click: clickSel, viewportOnly: true, waitMs: 1800 });

  // Jaring pengaman: kalau yang termuat ternyata daftar isi folder, hasilnya tidak sah walau tanpa error.
  for (const [name, p] of Object.entries(report.passes)) {
    if (typeof p.h1 === 'string' && /^Index of /.test(p.h1)) {
      report.errors.push(`${name}: yang dimuat adalah daftar isi folder (h1="${p.h1}") — path berkas salah, pemeriksaan tidak sah.`);
    }
  }

  report.ok = report.errors.length === 0 && !Object.values(report.passes).some((p) => p.overflowX);

  await browser.close();
  fs.writeFileSync(path.join(outdir, 'report.json'), JSON.stringify(report, null, 1));

  console.log(JSON.stringify({
    ok: report.ok,
    errors: report.errors,
    console: report.console.slice(0, 10),
    overflow: Object.fromEntries(Object.entries(report.passes).map(([k, v]) => [k, v.scrollWidth + '/' + v.innerWidth])),
    extras: Object.fromEntries(Object.entries(report.passes).map(([k, v]) => [k, v.extras])),
    shots: report.shots,
  }, null, 1));
})().catch((e) => { console.error(e); process.exit(1); });
