#!/usr/bin/env node
'use strict';
/* Uji interaksi tab penilaian: isi 8 jawaban, tekan "Lihat skor saya", lalu
 * periksa skornya benar-benar 65,0% / Layak Lanjut (sama dengan
 * kalkulator_kesiapan.py untuk pola jawaban 4 3 5 3 2 3 3 2).
 *
 * Jalankan:
 *   CHROME_PATH=/home/ubuntu/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome \
 *   node tab-penilaian/uji_tab.js [index.html]
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
/* pola jawaban + skor yang dikeluarkan kalkulator_kesiapan.py */
const JAWAB = { D1: 4, D2: 3, D3: 5, D4: 3, D5: 2, D6: 3, D7: 3, D8: 2 };
const HARAP = { persen: 65.0, band: 'Layak Lanjut' };
/* pilihan keyakinan per dimensi untuk uji */
const YAKIN = { D2: 'ragu', D5: 'yakin', D8: 'tidak_tahu' };
/* pola yang sengaja bertentangan: D2 tinggi + D3 rendah -> aturan R1 harus terpicu */
const JAWAB_BENTROK = { D1: 3, D2: 5, D3: 1, D4: 3, D5: 3, D6: 3, D7: 3, D8: 3 };
const KALK = path.resolve(__dirname, '../../kalkulator_kesiapan.py');
const PY = process.env.PYTHON || 'python3';

function skorPython(nilai) {
  const out = execFileSync(PY, [KALK, '-n'].concat(nilai.map(String)), { encoding: 'utf8' });
  const m = out.match(/([0-9]+\.[0-9])%/);
  if (!m) throw new Error('tidak bisa membaca skor dari kalkulator: ' + out.slice(0, 200));
  return m[1];
}

(async () => {
  const chromium = loadChromium();
  const exe = findChrome();
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  const galat = [];        /* asersi yang gagal */
  const galatHalaman = []; /* error JS di halaman */
  const hasil = {};

  async function jalankan(nama, opsi) {
    const ctx = await browser.newContext(Object.assign({
      viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1,
    }, opsi));
    const page = await ctx.newPage();
    const errs = [];
    page.on('pageerror', (e) => errs.push('pageerror: ' + e.message));
    page.on('console', (m) => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    await page.goto('file://' + FILE, { waitUntil: 'load' });
    await page.waitForTimeout(600);

    const awal = await page.evaluate(() => ({
      q: document.querySelectorAll('#penList .pen-q').length,
      o: document.querySelectorAll('#penList .pen-opt').length,
      disabled: document.querySelector('#penHitung').disabled,
      hint: document.querySelector('#penHint').textContent,
      count: document.querySelector('#penCount').textContent,
      hasilTersembunyi: document.querySelector('#penHasil').hidden,
    }));

    for (const [kode, nilai] of Object.entries(opsi && opsi.jawab ? opsi.jawab : JAWAB)) {
      await page.click(`#penList .pen-q[data-kode="${kode}"] .pen-opt[data-nilai="${nilai}"]`);
    }
    if (!(opsi && opsi.jawab)){
      for (const [kode, y] of Object.entries(YAKIN)) {
        await page.click(`#penList .pen-q[data-kode="${kode}"] .pen-kbtn[data-yakin="${y}"]`);
      }
    }
    await page.waitForTimeout(250);

    const setelahIsi = await page.evaluate(() => ({
      count: document.querySelector('#penCount').textContent,
      disabled: document.querySelector('#penHitung').disabled,
      hint: document.querySelector('#penHint').textContent,
      bar: document.querySelector('#penBar').style.width,
      terjawab: document.querySelectorAll('#penList .pen-q.jawab').length,
      tercentang: document.querySelectorAll('#penList .pen-opt[aria-checked="true"]').length,
      simpanan: (function(){ try { return localStorage.getItem('omnisense_penilaian_v1'); } catch(e){ return null; } })(),
    }));

    await page.click('#penHitung');
    await page.waitForTimeout(opsi && opsi.reducedMotion === 'reduce' ? 300 : 1600);

    const akhir = await page.evaluate(() => {
      const num = document.querySelector('#phNum');
      const wa = document.querySelector('#phWa');
      const bars = Array.from(document.querySelectorAll('#phRows .pen-row .rb i'));
      return {
        tersembunyi: document.querySelector('#penHasil').hidden,
        angka: num ? num.textContent : null,
        band: document.querySelector('#phBand').textContent,
        arti: (document.querySelector('#phArtis').textContent || '').slice(0, 40),
        langkah: (document.querySelector('#phLangkah').textContent || '').slice(0, 40),
        baris: document.querySelectorAll('#phRows .pen-row').length,
        urutTerlemah: (document.querySelector('#phRows .pen-row .rn') || {}).textContent || null,
        barisLemah: document.querySelectorAll('#phRows .pen-row.low').length,
        kartuCelah: document.querySelectorAll('#penGapWrap, #phGap .pen-gcard').length,
        waTeks: wa ? decodeURIComponent(wa.href.split('text=')[1] || '') : null,
        lebarBar: bars.map((b) => b.style.width),
        keyakinanAktif: document.querySelectorAll('#penList .pen-kbtn[aria-pressed="true"]').length,
        cekTampil: document.querySelector('#penCek').hidden === false,
        cekTeks: (document.querySelector('#penCek').textContent || '').slice(0, 90),
        limitTampil: document.querySelector('#phLimit').hidden === false,
        limitTeks: (document.querySelector('#phLimit').textContent || '').slice(0, 120),
      };
    });

    await page.screenshot({ path: '/tmp/qa_tab/hasil-' + nama + '.png', fullPage: false });
    await ctx.close();
    hasil[nama] = { awal, setelahIsi, akhir, errs };
    if (errs.length) galatHalaman.push(nama + ': ' + errs.join(' | '));
  }

  fs.mkdirSync('/tmp/qa_tab', { recursive: true });
  await jalankan('desktop', {});
  await jalankan('reduced', { reducedMotion: 'reduce' });
  await jalankan('mobile', { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await jalankan('bentrok', { jawab: JAWAB_BENTROK });

  const p = hasil.desktop;
  const cek = [];
  const t = (nama, ok, detail) => { cek.push((ok ? 'OK   ' : 'GAGAL') + '  ' + nama + (detail ? '  -> ' + detail : '')); if (!ok) galat.push(nama); };

  t('8 pertanyaan dirender', p.awal.q === 8, String(p.awal.q));
  t('40 pilihan dirender', p.awal.o === 40, String(p.awal.o));
  t('tombol terkunci sebelum lengkap', p.awal.disabled === true);
  t('penghitung awal benar', p.awal.count === 'Terjawab 0 dari 8', p.awal.count);
  t('penghitung jadi 8/8', p.setelahIsi.count === 'Terjawab 8 dari 8', p.setelahIsi.count);
  t('tombol terbuka setelah lengkap', p.setelahIsi.disabled === false);
  t('bilah progres penuh', p.setelahIsi.bar === '100%', p.setelahIsi.bar);
  t('8 kartu ditandai terjawab', p.setelahIsi.terjawab === 8, String(p.setelahIsi.terjawab));
  t('8 pilihan tercentang', p.setelahIsi.tercentang === 8, String(p.setelahIsi.tercentang));
  t('jawaban disimpan di perangkat', !!p.setelahIsi.simpanan && p.setelahIsi.simpanan.indexOf('D2') > -1, (p.setelahIsi.simpanan || '').slice(0, 40));
  t('hasil terbuka', p.akhir.tersembunyi === false);
  t('skor 65/100', /^65/.test(p.akhir.angka || ''), String(p.akhir.angka));
  t('band Layak Lanjut', p.akhir.band === HARAP.band, p.akhir.band);
  t('8 baris dimensi', p.akhir.baris === 8, String(p.akhir.baris));
  t('urut dari terlemah', p.akhir.urutTerlemah === 'Organisasi & Budaya', String(p.akhir.urutTerlemah));
  t('dimensi lemah disorot', p.akhir.barisLemah === 2, String(p.akhir.barisLemah));
  t('3 kartu celah/kekuatan', p.akhir.kartuCelah === 3, String(p.akhir.kartuCelah));
  t('baris bar terisi', p.akhir.lebarBar.filter((w) => w && w !== '0%').length === 8, JSON.stringify(p.akhir.lebarBar));
  t('tautan WA memuat skor', (p.akhir.waTeks || '').indexOf('65.0%') > -1, (p.akhir.waTeks || '').slice(0, 60));
  t('tautan WA memuat jawaban', (p.akhir.waTeks || '').indexOf('Kesiapan Data: 3/5') > -1);
  /* --- validitas: baris mesin, keyakinan, konsistensi --- */
  t('pesan diawali penanda mesin', (p.akhir.waTeks || '').indexOf('[PENILAIAN-SITUS v1]') === 0, (p.akhir.waTeks || '').split('\n')[0]);
  t('baris mesin urut D1..D8', (p.akhir.waTeks || '').indexOf('D1=4 D2=3 D3=5 D4=3 D5=2 D6=3 D7=3 D8=2') > -1);
  t('baris mesin sama dgn kalkulator', (p.akhir.waTeks || '').indexOf('skor_situs=' + skorPython(Object.values(JAWAB))) > -1, 'py ' + skorPython(Object.values(JAWAB)));
  t('keyakinan ikut terkirim', (p.akhir.waTeks || '').indexOf('keyakinan=D2:ragu,D5:yakin,D8:tidak_tahu') > -1);
  t('3 pilihan keyakinan tersimpan', p.akhir.keyakinanAktif === 3, String(p.akhir.keyakinanAktif));
  t('catatan keterbatasan tampil', p.akhir.limitTampil === true);
  t('catatan sebut 2 jawaban belum pasti', (p.akhir.limitTeks || '').indexOf('2 jawaban Anda ditandai belum pasti') > -1, p.akhir.limitTeks);
  t('pola konsisten: tanpa peringatan', p.akhir.cekTampil === false);
  /* pola yang sengaja bertentangan harus terpicu */
  const b = hasil.bentrok;
  /* Kotak peringatan harus memakai NAMA dimensi, bukan kode D2/D3 yang
     membingungkan pengunjung. */
  t('bentrok: aturan R1 terpicu', b.akhir.cekTampil === true, b.akhir.cekTeks);
  t('bentrok: peringatan sebut nama dimensi',
    (b.akhir.cekTeks || '').indexOf('Kesiapan Data') > -1 &&
    (b.akhir.cekTeks || '').indexOf('Infrastruktur & Teknologi') > -1, b.akhir.cekTeks);
  t('bentrok: peringatan tidak tampilkan kode D1..D8',
    !/\bD[1-8]\b/.test(b.akhir.cekTeks || ''), b.akhir.cekTeks);
  t('bentrok: kode R1 di pesan WA', (b.akhir.waTeks || '').indexOf('catatan_situs=R1') > -1);
  t('bentrok: skor tetap dihitung', (b.akhir.waTeks || '').indexOf('skor_situs=' + skorPython(Object.values(JAWAB_BENTROK))) > -1, 'py ' + skorPython(Object.values(JAWAB_BENTROK)));
  t('bentrok: skor sama di layar & kalkulator', /^[0-9]+\/100$/.test(b.akhir.angka || '') && b.akhir.angka.split('/')[0] === String(Math.round(+skorPython(Object.values(JAWAB_BENTROK)))), b.akhir.angka + ' vs ' + skorPython(Object.values(JAWAB_BENTROK)));
  t('reduced-motion: skor final langsung', hasil.reduced.akhir.angka === p.akhir.angka, hasil.reduced.akhir.angka);
  t('mobile: skor sama', hasil.mobile.akhir.angka === p.akhir.angka, hasil.mobile.akhir.angka);
  t('tanpa error halaman', galatHalaman.length === 0, galatHalaman.join(' | '));

  console.log(cek.join('\n'));
  console.log('\nSkor: ' + p.akhir.angka + ' · ' + p.akhir.band);
  console.log('Pesan WA: ' + (p.akhir.waTeks || '').split('\n').slice(0, 3).join(' / '));
  fs.writeFileSync('/tmp/qa_tab/hasil.json', JSON.stringify(hasil, null, 1));
  await browser.close();
  process.exit(galat.length ? 1 : 0);
})().catch((e) => { console.error(e); process.exit(1); });
