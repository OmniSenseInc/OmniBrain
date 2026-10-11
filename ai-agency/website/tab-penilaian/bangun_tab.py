#!/usr/bin/env python3
"""bangun_tab.py — menanam tab "Coba Penilaian" ke index.html.

Idempoten: kalau penanda '#penilaian' sudah ada, keluar tanpa mengubah apa pun.
Selalu mencadangkan index.html lebih dulu ke arsip/index-sebelum-tab-penilaian.html
(sekali saja, tidak menimpa cadangan yang sudah ada).

Sumber data: tab-penilaian/pertanyaan.json  (bobot & band wajib sama dengan
/home/ubuntu/ai-agency/kalkulator_kesiapan.py — dijaga oleh uji_paritas.js)

Jalankan: python3 tab-penilaian/bangun_tab.py
"""
import json
import os
import re
import shutil
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(BASE)
INDEX = os.path.join(WEB, "index.html")
ARSIP = os.path.join(WEB, "arsip")
CADANGAN = os.path.join(ARSIP, "index-sebelum-tab-penilaian.html")

MARK = "<!-- ================= COBA PENILAIAN"


def baca_data():
    with open(os.path.join(BASE, "pertanyaan.json"), encoding="utf-8") as f:
        return json.load(f)


CSS = r"""
/* ---------- tab penilaian langsung ---------- */
.pen{margin-top:clamp(30px,4vw,54px);border:1px solid var(--line);border-radius:var(--r-l);background:var(--panel);overflow:hidden}
.pen-head{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:16px clamp(16px,2.4vw,26px);border-bottom:1px solid var(--line);background:var(--obsidian-2)}
.pen-prog{display:flex;align-items:center;gap:14px;font-family:var(--font-mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--slate)}
.pen-bar{display:block;width:132px;height:3px;border-radius:2px;background:var(--track);overflow:hidden}
.pen-bar i{display:block;height:100%;width:0;background:var(--signal);transition:width .4s cubic-bezier(.2,.7,.2,1)}
.pen-reset{font-family:var(--font-mono);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--slate);padding:6px 2px;border-bottom:1px solid transparent;transition:color .25s ease,border-color .25s ease}
.pen-reset:hover{color:var(--white);border-bottom-color:var(--signal)}
.pen-list{counter-reset:q}
.pen-q{display:grid;grid-template-columns:auto minmax(0,1fr);gap:clamp(14px,2.6vw,30px);padding:clamp(20px,2.6vw,30px) clamp(16px,2.4vw,26px);border-bottom:1px solid var(--line)}
.pen-q:last-child{border-bottom:0}
.pen-q.jawab{background:rgba(20,184,166,.035)}
.pen-no{font-family:var(--font-mono);font-size:12px;color:var(--signal);letter-spacing:.08em;padding-top:3px}
.pen-qt{font-size:17px;font-weight:600;letter-spacing:-0.01em;line-height:1.45;max-width:52ch}
.pen-qd{margin-top:7px;font-size:14px;color:var(--slate);max-width:56ch}
.pen-qd b{color:var(--ink);font-weight:600}
.pen-dim{margin-top:9px;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--slate-dim)}
.pen-opts{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.pen-opt{display:flex;align-items:center;gap:9px;padding:9px 15px;border:1px solid var(--line-2);border-radius:999px;background:var(--obsidian-2);color:var(--slate);font-size:13.5px;font-weight:500;text-align:left;transition:color .2s ease,border-color .2s ease,background .2s ease}
.pen-opt:hover{color:var(--white);border-color:var(--slate)}
.pen-opt .pen-n{display:grid;place-items:center;width:19px;height:19px;flex:0 0 auto;border-radius:50%;border:1px solid var(--line-2);font-family:var(--font-mono);font-size:11px;line-height:1;color:var(--slate)}
.pen-opt[aria-checked="true"]{background:rgba(20,184,166,.14);border-color:var(--signal);color:var(--white)}
.pen-opt[aria-checked="true"] .pen-n{background:var(--signal);border-color:var(--signal);color:#06201D}
.pen-key{display:flex;flex-wrap:wrap;align-items:center;gap:6px;margin-top:11px}
.pen-key>span{font-size:12px;color:var(--slate);letter-spacing:.02em}
.pen-kbtn{padding:4px 11px;border:1px solid var(--line);border-radius:999px;background:transparent;color:var(--slate);font-size:12px;font-weight:500;transition:color .2s ease,border-color .2s ease,background .2s ease}
.pen-kbtn:hover{color:var(--white);border-color:var(--slate)}
.pen-kbtn[aria-pressed="true"]{background:rgba(20,184,166,.12);border-color:var(--signal);color:var(--white)}
.pen-cek{margin-top:18px;padding:15px 17px;border:1px solid var(--line-2);border-left:3px solid var(--signal);border-radius:var(--r-s);background:rgba(20,184,166,.05)}
.pen-cek h4{margin:0 0 7px;font-size:13.5px;font-weight:600;color:var(--white);letter-spacing:.01em}
.pen-cek ul{margin:0;padding-left:17px;display:grid;gap:7px}
.pen-cek li{font-size:13.5px;line-height:1.5;color:var(--slate)}
.pen-cek b{color:var(--ink);font-weight:600}
.pen-actions{display:flex;align-items:center;gap:18px;flex-wrap:wrap;padding:clamp(18px,2.4vw,26px);border-top:1px solid var(--line);background:var(--obsidian-2)}
.pen-hint{font-size:13.5px;color:var(--slate)}
.btn[disabled]{opacity:.45;cursor:not-allowed}
.btn[disabled]:hover{background:var(--signal);border-color:var(--signal)}
.pen-hasil{margin-top:clamp(22px,3vw,36px);border:1px solid var(--line);border-radius:var(--r-l);background:var(--panel);overflow:hidden}
.pen-hasil[hidden]{display:none}
.ph-top{display:grid;grid-template-columns:auto minmax(0,1fr);gap:clamp(20px,3.4vw,48px);align-items:center;padding:clamp(22px,3.2vw,40px);border-bottom:1px solid var(--line)}
.ph-disc{position:relative;width:168px;height:168px}
.ph-disc canvas{width:168px;height:168px}
.ph-num{position:absolute;inset:0;display:grid;place-items:center;font-family:var(--font-mono);font-size:40px;font-weight:600;letter-spacing:-0.03em}
.ph-num span{font-size:17px;color:var(--slate);margin-left:2px}
.ph-band{display:inline-flex;align-items:center;gap:8px;font-family:var(--font-mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--signal)}
.ph-band .pip{width:7px;height:7px;border-radius:50%;border:1px solid var(--signal);display:block}
.ph-h3{margin-top:12px;font-size:clamp(23px,3vw,34px);font-weight:800;letter-spacing:-0.03em}
.ph-arti{margin-top:12px;font-size:16px;color:var(--slate);max-width:56ch}
.ph-langkah{margin-top:16px;padding:14px 16px;border-left:2px solid var(--signal);background:var(--obsidian-2);font-size:15px}
.ph-langkah b{display:block;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--slate);margin-bottom:6px;font-weight:400}
.ph-mid{padding:clamp(22px,3.2vw,40px);border-bottom:1px solid var(--line)}
.ph-lab{font-family:var(--font-mono);font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--slate);margin-bottom:18px}
.pen-rows{display:grid}
.pen-row{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:7px 16px;align-items:center;padding:11px 0;border-bottom:1px solid var(--line)}
.pen-row:last-child{border-bottom:0}
.pen-row .rn{font-size:14.5px;font-weight:500;min-width:0}
.pen-row .rv{font-family:var(--font-mono);font-size:12.5px;color:var(--slate);font-variant-numeric:tabular-nums}
.pen-row .rb{grid-column:1/-1;height:5px;border-radius:999px;background:repeating-linear-gradient(90deg,rgba(255,255,255,.09) 0 1px,transparent 1px 25%),var(--track);overflow:hidden}
.pen-row .rb i{display:block;height:100%;width:0;background:var(--slate-dim);border-radius:999px;transition:width .7s cubic-bezier(.2,.7,.2,1)}
.pen-row .rw{grid-column:1/-1;font-family:var(--font-mono);font-size:11.5px;letter-spacing:.04em;color:var(--slate-dim)}
.pen-row.low .rb i{background:var(--signal)}
.pen-row.low .rv{color:var(--signal)}
.pen-gap{padding:clamp(22px,3.2vw,40px);border-bottom:1px solid var(--line);display:grid;gap:18px}
.pen-gcard{border:1px solid var(--line);border-radius:var(--r-m);padding:18px 20px;background:var(--obsidian-2)}
.pen-gcard .gt{font-family:var(--font-mono);font-size:11.5px;letter-spacing:.08em;text-transform:uppercase;color:var(--signal)}
.pen-gcard h4{margin-top:9px;font-size:17px;font-weight:700}
.pen-gcard p{margin-top:8px;font-size:15px;color:var(--slate)}
.ph-aksi{display:flex;align-items:center;gap:14px;flex-wrap:wrap;padding:clamp(22px,3.2vw,40px)}
.ph-note{font-size:13px;color:var(--slate);max-width:44ch}
.ph-limit{flex:0 0 100%;margin:0;font-size:13px;line-height:1.5;color:var(--slate);border-left:2px solid var(--signal);padding-left:11px;max-width:64ch}
.ph-cetak{border:1px solid var(--line-2);border-radius:999px;padding:11px 18px;font-size:13.5px;font-weight:500;color:var(--slate);transition:color .2s ease,border-color .2s ease}
.ph-cetak:hover{color:var(--white);border-color:var(--slate)}
.ph-nojs{border:1px solid var(--line);border-radius:var(--r-m);padding:20px;margin-top:26px;background:var(--panel);font-size:15px;color:var(--slate)}
@media (max-width:720px){
  .ph-top{grid-template-columns:minmax(0,1fr);justify-items:start}
  .pen-q{grid-template-columns:minmax(0,1fr)}
  .pen-no{padding-top:0}
  .pen-opt{width:100%;border-radius:var(--r-m)}
}
@media print{
  .nav,.ixbar,.pen,.ph-aksi,.hero,.cta,.sec:not(#penilaian){display:none!important}
  .pen-hasil{border:0}
  body{background:#fff;color:#000}
}
"""

JS = r"""
/* ================= tab penilaian langsung =================
   Mandiri: tidak menyentuh IIFE gerak di atas. Semua perhitungan
   berjalan di perangkat pengunjung; tidak ada data yang dikirim keluar. */
(function(){
  var D = window.__PENILAIAN__;
  if (!D) return;
  var root = document.documentElement;
  var $ = function(s, c){ return (c || document).querySelector(s); };
  var list = $('#penList');
  if (!list) return;

  var JAWAB = {};
  var YAKIN = {};
  var KUNCI = 'omnisense_penilaian_v1';
  var KUNCI_Y = 'omnisense_penilaian_keyakinan_v1';
  var N = D.dimensi.length;
  var motionOn = !root.classList.contains('no-motion') &&
    !(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);

  function band(p){
    /* Bulatkan ke 1 desimal dulu: tanpa ini skor tepat di ambang (mis. 60,0)
       bisa tersimpan sebagai 59.99999999999999 dan salah jatuh ke band bawah. */
    p = Math.round(p * 10 + 1e-9) / 10;
    for (var i = 0; i < D.band.length; i++){ if (p >= D.band[i].min) return D.band[i]; }
    return D.band[D.band.length - 1];
  }
  function hitung(){
    var total = 0, per = [];
    D.dimensi.forEach(function(d){
      var v = JAWAB[d.kode] || 0;
      var t = v * d.bobot;
      total += t;
      per.push({ kode: d.kode, nama: d.nama, nilai: v, bobot: d.bobot, tertimbang: t });
    });
    /* Bulatkan ke 1 desimal: ini angka yang ditampilkan & dikirim ke bot,
       jadi harus sama persis dengan kalkulator_kesiapan.py. */
    var persen = Math.round(((total / 5) * 100) * 10 + 1e-9) / 10;
    return { persen: persen, band: band(persen), per: per };
  }
  function tingkat(n){ return n <= 2 ? 'rendah' : (n === 3 ? 'sedang' : 'tinggi'); }

  /* ---------- bangun daftar pertanyaan (dilewati kalau sudah ada di HTML) ---------- */
  if (!list.querySelector('.pen-q')) D.dimensi.forEach(function(d, i){
    var li = document.createElement('li');
    li.className = 'pen-q';
    li.setAttribute('data-kode', d.kode);

    var no = document.createElement('span');
    no.className = 'pen-no';
    no.textContent = ('0' + (i + 1)).slice(-2);

    var box = document.createElement('div');

    var qt = document.createElement('p');
    qt.className = 'pen-qt';
    qt.id = 'penqt-' + d.kode;
    qt.textContent = d.pertanyaan;

    var qd = document.createElement('p');
    qd.className = 'pen-qd';
    qd.textContent = d.petunjuk;

    var dm = document.createElement('p');
    dm.className = 'pen-dim';
    dm.textContent = d.nama + ' \u00b7 bobot ' + Math.round(d.bobot * 100) + '%';

    var opts = document.createElement('div');
    opts.className = 'pen-opts';
    opts.setAttribute('role', 'radiogroup');
    opts.setAttribute('aria-labelledby', qt.id);

    d.pilihan.forEach(function(p, j){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'pen-opt';
      b.setAttribute('role', 'radio');
      b.setAttribute('aria-checked', 'false');
      b.setAttribute('data-nilai', p.n);
      b.setAttribute('data-teks', p.teks);
      b.tabIndex = j === 0 ? 0 : -1;
      b.innerHTML = '<span class="n">' + p.n + '</span><span>' + p.teks + '</span>';
      opts.appendChild(b);
    });

    box.appendChild(qt); box.appendChild(qd); box.appendChild(dm); box.appendChild(opts);
    li.appendChild(no); li.appendChild(box);
    list.appendChild(li);
  });

  /* ---------- pasang pendengar pada semua pilihan (termasuk markup di HTML) ---------- */
  var JML_OPTS = 5;
  list.querySelectorAll('.pen-q').forEach(function(li){
    var kode = li.getAttribute('data-kode');
    var grup = li.querySelector('.pen-opts');
    if (!grup || !kode) return;
    grup.setAttribute('role', 'radiogroup');
    var qt = li.querySelector('.pen-qt');
    if (qt){ if (!qt.id) qt.id = 'penqt-' + kode; grup.setAttribute('aria-labelledby', qt.id); }
    Array.prototype.forEach.call(grup.querySelectorAll('.pen-opt'), function(b, j){
      if (!b.getAttribute('data-nilai') || !b.getAttribute('data-teks')) return;
      b.addEventListener('click', function(){ pilih(kode, +b.getAttribute('data-nilai'), b, grup); });
      b.addEventListener('keydown', function(e){
        var tombol = Array.prototype.slice.call(grup.querySelectorAll('.pen-opt'));
        var idx = tombol.indexOf(b);
        var n = null;
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (idx + 1) % tombol.length;
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (idx - 1 + tombol.length) % tombol.length;
        if (n === null) return;
        e.preventDefault();
        tombol[n].focus();
      });
    });
  });

  var optsAll = function(){ return list.querySelectorAll('.pen-opts'); };

  /* ---------- pemeriksaan konsistensi (jalan di perangkat pengunjung) ---------- */
  var ATURAN = (D.aturan_konsistensi && D.aturan_konsistensi.aturan) || [];

  function cekKonsistensi(){
    return ATURAN.filter(function(a){
      return Object.keys(a.jika).every(function(k){
        var v = JAWAB[k];
        return v && a.jika[k].indexOf(v) !== -1;
      });
    });
  }

  function gambarCek(){
    var kotak = $('#penCek');
    if (!kotak) return;
    var kena = cekKonsistensi();
    if (!kena.length){ kotak.hidden = true; kotak.innerHTML = ''; return; }
    kotak.hidden = false;
    var jumlahTeks = kena.length === 1 ? 'satu' : kena.length;
    kotak.innerHTML = '<h4>Ada ' + jumlahTeks + ' hal yang perlu ditinjau</h4><ul>' +
      kena.map(function(a){
        /* Tampilkan NAMA dimensi, bukan kode D1..D8 yang membingungkan pengunjung. */
        var dims = Object.keys(a.jika).map(function(k){
          var d = D.dimensi.filter(function(x){ return x.kode === k; })[0];
          return d ? d.nama : k;
        }).join(' &middot; ');
        return '<li><b>' + dims + '</b> &mdash; ' + a.pesan + '</li>';
      }).join('') +
      '</ul>';
  }

  /* ---------- pilihan keyakinan per dimensi ---------- */
  var KEY = D.keyakinan || [];
  list.querySelectorAll('.pen-q').forEach(function(li){
    var kode = li.getAttribute('data-kode');
    var box = li.querySelector('div');
    if (!kode || !box || box.querySelector('.pen-key')) return;
    var bar = document.createElement('div');
    bar.className = 'pen-key';
    var lab = document.createElement('span');
    lab.textContent = 'Seberapa yakin?';
    bar.appendChild(lab);
    KEY.forEach(function(k){
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'pen-kbtn';
      b.setAttribute('data-yakin', k.kode);
      b.setAttribute('aria-pressed', 'false');
      b.title = k.arti;
      b.textContent = k.label;
      b.addEventListener('click', function(){
        if (YAKIN[kode] === k.kode){ delete YAKIN[kode]; }
        else { YAKIN[kode] = k.kode; }
        Array.prototype.forEach.call(bar.querySelectorAll('.pen-kbtn'), function(x){
          x.setAttribute('aria-pressed', x.getAttribute('data-yakin') === YAKIN[kode] ? 'true' : 'false');
        });
        simpan();
        gambarCek();
      });
      bar.appendChild(b);
    });
    box.appendChild(bar);
  });

  var btnHitung = $('#penHitung');
  var btnReset = $('#penReset');
  var hint = $('#penHint');
  var count = $('#penCount');
  var bar = $('#penBar');

  function simpan(){
    try { localStorage.setItem(KUNCI, JSON.stringify(JAWAB)); } catch(e){}
    try { localStorage.setItem(KUNCI_Y, JSON.stringify(YAKIN)); } catch(e){}
  }
  function muat(){
    try {
      var s = localStorage.getItem(KUNCI);
      if (!s) return;
      var o = JSON.parse(s);
      Object.keys(o).forEach(function(k){
        var li = list.querySelector('[data-kode="' + k + '"]');
        if (!li) return;
        var b = li.querySelector('.pen-opt[data-nilai="' + o[k] + '"]');
        if (b) pilih(k, o[k], b, li.querySelector('.pen-opts'), true);
      });
      var sy = localStorage.getItem(KUNCI_Y);
      if (sy){
        YAKIN = JSON.parse(sy) || {};
        Object.keys(YAKIN).forEach(function(k){
          var li = list.querySelector('[data-kode="' + k + '"]');
          if (!li) return;
          Array.prototype.forEach.call(li.querySelectorAll('.pen-kbtn'), function(x){
            x.setAttribute('aria-pressed', x.getAttribute('data-yakin') === YAKIN[k] ? 'true' : 'false');
          });
        });
      }
    } catch(e){}
  }

  function pilih(kode, nilai, tombol, grup, diam){
    JAWAB[kode] = nilai;
    Array.prototype.forEach.call(grup.querySelectorAll('.pen-opt'), function(b){
      var on = b === tombol;
      b.setAttribute('aria-checked', on ? 'true' : 'false');
      b.tabIndex = on ? 0 : -1;
    });
    var li = tombol.closest('.pen-q');
    if (li) li.classList.add('jawab');
    if (!diam) simpan();
    perbarui();
  }

  function perbarui(){
    var jml = Object.keys(JAWAB).length;
    count.textContent = 'Terjawab ' + jml + ' dari ' + N;
    bar.style.width = (jml / N * 100) + '%';
    var sisa = N - jml;
    btnHitung.disabled = sisa > 0;
    hint.textContent = sisa > 0
      ? ('Masih ada ' + sisa + ' pertanyaan yang belum dijawab.')
      : 'Siap. Skor dihitung di perangkat Anda.';
    gambarCek();
    if (sisa === 0 && hasilTampil) tampilkanHasil();
  }

  /* ---------- cakram skor ---------- */
  var ARC = 0.75;                 /* 270 derajat, sama seperti cakram hero */
  var OFF = Math.PI * (1 - ARC) / 2 + Math.PI / 2;
  var cv, ctx, dpr, sweep = 0, target = 0, raf = null;

  function siapkanCanvas(){
    cv = $('#phCanvas');
    if (!cv) return false;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    var sisi = cv.clientWidth || 168;
    cv.width = sisi * dpr; cv.height = sisi * dpr;
    ctx = cv.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return true;
  }
  function gambar(pct){
    if (!ctx) return;
    var sisi = cv.clientWidth || 168;
    var cx = sisi / 2, cy = sisi / 2, r = sisi / 2 - 9, lw = 7;
    ctx.clearRect(0, 0, sisi, sisi);
    ctx.lineWidth = lw; ctx.lineCap = 'round';
    ctx.strokeStyle = getComputedStyle(root).getPropertyValue('--track').trim() || '#34343C';
    ctx.beginPath();
    ctx.arc(cx, cy, r, OFF, OFF + Math.PI * 2 * ARC);
    ctx.stroke();
    if (pct > 0){
      ctx.strokeStyle = getComputedStyle(root).getPropertyValue('--signal').trim() || '#14B8A6';
      ctx.beginPath();
      ctx.arc(cx, cy, r, OFF, OFF + Math.PI * 2 * ARC * (pct / 100));
      ctx.stroke();
    }
  }
  function angka(pct){
    var el = $('#phNum');
    if (el) el.innerHTML = Math.round(pct) + '<span>/100</span>';
  }
  function diamDi(pct){ sweep = pct; gambar(pct); angka(pct); }
  function jalankan(pct){
    target = pct;
    if (!motionOn){ diamDi(pct); return; }
    var t0 = null, dari = 0;
    function langkah(ts){
      if (t0 === null) t0 = ts;
      var p = Math.min(1, (ts - t0) / 900);
      var e = 1 - Math.pow(1 - p, 3);
      sweep = dari + (target - dari) * e;
      gambar(sweep); angka(sweep);
      if (p < 1) raf = requestAnimationFrame(langkah); else raf = null;
    }
    if (raf) cancelAnimationFrame(raf);
    raf = requestAnimationFrame(langkah);
  }

  /* ---------- hasil ---------- */
  var hasilTampil = false;

  function tampilkanHasil(){
    var r = hitung();
    var kotak = $('#penHasil');
    if (!kotak) return;
    kotak.hidden = false;
    hasilTampil = true;

    $('#phBand').textContent = r.band.nama;
    $('#phArtis').textContent = r.band.arti;
    $('#phLangkah').textContent = r.band.langkah;

    var naik = r.per.slice().sort(function(a, b){ return a.nilai - b.nilai; });
    var lemah = naik.slice(0, 2);

    var rows = $('#phRows');
    rows.innerHTML = '';
    r.per.slice().sort(function(a, b){ return a.nilai - b.nilai; }).forEach(function(d){
      var rendah = d.nilai <= 2;
      var row = document.createElement('div');
      row.className = 'pen-row' + (rendah ? ' low' : '');
      row.innerHTML =
        '<span class="rn">' + d.nama + '</span>' +
        '<span class="rv">' + d.nilai + '/5</span>' +
        '<span class="rb"><i data-w="' + (d.nilai / 5 * 100) + '"></i></span>' +
        '<span class="rw">bobot ' + Math.round(d.bobot * 100) + '% \u00b7 sumbang ' + d.tertimbang.toFixed(2) + ' poin</span>';
      rows.appendChild(row);
    });

    var gap = $('#phGap');
    gap.innerHTML = '';
    lemah.forEach(function(d){
      var meta = D.rekomendasi_dimensi.filter(function(x){ return x.kode === d.kode; })[0];
      if (!meta) return;
      var card = document.createElement('div');
      card.className = 'pen-gcard';
      card.innerHTML =
        '<span class="gt">Celah utama \u00b7 ' + d.nama + ' \u00b7 ' + d.nilai + '/5</span>' +
        '<h4>Langkah pertama</h4>' +
        '<p>' + meta[tingkat(d.nilai)] + '</p>';
      gap.appendChild(card);
    });

    var kuat = naik[naik.length - 1];
    var kuatMeta = D.rekomendasi_dimensi.filter(function(x){ return x.kode === kuat.kode; })[0];
    if (kuatMeta){
      var k = document.createElement('div');
      k.className = 'pen-gcard';
      k.innerHTML =
        '<span class="gt">Kekuatan \u00b7 ' + kuat.nama + ' \u00b7 ' + kuat.nilai + '/5</span>' +
        '<h4>Yang sudah bagus</h4><p>' + kuatMeta[tingkat(kuat.nilai)] + '</p>';
      gap.appendChild(k);
    }

    /* ringkasan untuk WhatsApp: baris mesin + skor + pilihan jawaban per dimensi */
    var barisMesin = r.per.map(function(d){ return d.kode + '=' + d.nilai; }).join(' ');
    var yakinTxt = Object.keys(YAKIN).map(function(k){ return k + ':' + YAKIN[k]; }).join(',');
    var baris = r.per.map(function(d){
      var li = list.querySelector('[data-kode="' + d.kode + '"]');
      var b = li && li.querySelector('.pen-opt[data-nilai="' + d.nilai + '"]');
      var teks = b ? b.getAttribute('data-teks') : '';
      var y = YAKIN[d.kode] ? ' [' + YAKIN[d.kode] + ']' : '';
      return '- ' + d.nama + ': ' + d.nilai + '/5 (' + teks + ')' + y;
    }).join('\n');
    var kena = cekKonsistensi();
    var tandaCek = kena.length
      ? '\ncatatan_situs=' + kena.map(function(a){ return a.kode; }).join(',') + ' (perlu ditinjau)'
      : '';
    var pesan = '[PENILAIAN-SITUS v1]\n' +
      barisMesin + '\n' +
      'skor_situs=' + r.persen.toFixed(1) + ' band=' + r.band.nama + '\n' +
      (yakinTxt ? 'keyakinan=' + yakinTxt + '\n' : '') +
      tandaCek + '\n\n' +
      'Halo OmniSense, saya baru mengisi penilaian kesiapan di situs.\n' +
      'Skor saya ' + r.persen.toFixed(1) + '% \u2014 ' + r.band.nama + '.\n' +
      'Jawaban saya:\n' + baris + '\n' +
      'Saya ingin membahas laporan lengkapnya.';
    var wa = $('#phWa');
    if (wa) wa.href = 'https://wa.me/6288809640700?text=' + encodeURIComponent(pesan);

    /* catatan keterbatasan hasil */
    var lim = $('#phLimit');
    if (lim){
      var ragu = Object.keys(YAKIN).filter(function(k){ return YAKIN[k] !== 'yakin'; });
      var pesanLim = [];
      if (kena.length) pesanLim.push('Ada ' + (kena.length === 1 ? 'satu' : kena.length) + ' hal yang saling bertentangan. Skornya tetap kami hitung, tetapi tim akan menanyakan buktinya lebih dulu.');
      if (ragu.length) pesanLim.push(ragu.length + ' jawaban Anda ditandai belum pasti, jadi skor ini masih bisa bergeser setelah dibahas bersama.');
      lim.hidden = pesanLim.length === 0;
      lim.textContent = pesanLim.join(' ');
    }

    if (!siapkanCanvas()) return;
    jalankan(r.persen);

    requestAnimationFrame(function(){
      Array.prototype.forEach.call(rows.querySelectorAll('.rb i'), function(el){
        el.style.width = el.getAttribute('data-w') + '%';
      });
    });

    try {
      kotak.setAttribute('tabindex', '-1');
      kotak.focus({ preventScroll: true });
      kotak.scrollIntoView({ behavior: motionOn ? 'smooth' : 'auto', block: 'start' });
    } catch(e){}
  }

  btnHitung.addEventListener('click', tampilkanHasil);
  btnReset.addEventListener('click', function(){
    JAWAB = {};
    YAKIN = {};
    try { localStorage.removeItem(KUNCI); localStorage.removeItem(KUNCI_Y); } catch(e){}
    Array.prototype.forEach.call(list.querySelectorAll('.pen-q'), function(li){ li.classList.remove('jawab'); });
    Array.prototype.forEach.call(list.querySelectorAll('.pen-opt'), function(b){
      b.setAttribute('aria-checked', 'false');
      b.tabIndex = b.getAttribute('data-nilai') === '1' ? 0 : -1;
    });
    Array.prototype.forEach.call(list.querySelectorAll('.pen-kbtn'), function(b){
      b.setAttribute('aria-pressed', 'false');
    });
    gambarCek();
    var kotak = $('#penHasil');
    if (kotak) kotak.hidden = true;
    hasilTampil = false; diamDi(0);
    perbarui();
    list.scrollIntoView({ behavior: motionOn ? 'smooth' : 'auto', block: 'start' });
  });

  /* hormati tombol gerak situs */
  if (window.OmniSense && typeof window.OmniSense.applyMotion === 'function'){
    var asli = window.OmniSense.applyMotion;
    window.OmniSense.applyMotion = function(on){
      asli(on);
      motionOn = !!on;
      if (!on && hasilTampil) diamDi(hitung().persen);
    };
  }

  window.addEventListener('resize', function(){ if (ctx) gambar(sweep); });

  diamDi(0);
  perbarui();
  muat();

  window.OmniSensePenilaian = {
    jawab: function(kode, nilai){
      var li = list.querySelector('[data-kode="' + kode + '"]');
      var b = li && li.querySelector('.pen-opt[data-nilai="' + nilai + '"]');
      if (b) pilih(kode, nilai, b, li.querySelector('.pen-opts'));
    },
    keyakinan: function(kode, kodeYakin){
      var li = list.querySelector('[data-kode="' + kode + '"]');
      var b = li && li.querySelector('.pen-kbtn[data-yakin="' + kodeYakin + '"]');
      if (b) b.click();
    },
    hitung: hitung,
    tampilkan: tampilkanHasil,
    skor: function(){ return hitung().persen; },
    band: function(){ return hitung().band.nama; },
    cek: cekKonsistensi,
    pesan: function(){ return ($('#phWa') || {}).href || ''; }
  };
})();
"""


def bagian_html(data):
    """Bagian HTML + data JSON untuk tab penilaian."""
    opsi_html = ""
    for i, d in enumerate(data["dimensi"]):
        opts = "".join(
            f'<button type="button" class="pen-opt" role="radio" aria-checked="false" '
            f'data-nilai="{p["n"]}" data-teks="{p["teks"]}" tabindex="{0 if j == 0 else -1}">'
            f'<span class="pen-n">{p["n"]}</span><span>{p["teks"]}</span></button>'
            for j, p in enumerate(d["pilihan"])
        )
        opsi_html += (
            f'<li class="pen-q" data-kode="{d["kode"]}">'
            f'<span class="pen-no">{i + 1:02d}</span><div>'
            f'<p class="pen-qt" id="penqt-{d["kode"]}">{d["pertanyaan"]}</p>'
            f'<p class="pen-qd">{d["petunjuk"]}</p>'
            f'<p class="pen-dim">{d["nama"]} &middot; bobot {round(d["bobot"] * 100)}%</p>'
            f'<div class="pen-opts" role="radiogroup" aria-labelledby="penqt-{d["kode"]}">{opts}</div>'
            f"</div></li>"
        )

    return f"""
  {MARK} ================= -->
  <section class="sec" id="penilaian">
    <div class="wrap">
      <div class="shead">
        <div class="reveal">
          <span class="eyebrow"><span class="pip"></span>Penilaian langsung</span>
          <h2>Delapan pertanyaan, <span class="accent">skor bisnis Anda</span></h2>
        </div>
        <div class="reveal">
          <p>Jawab apa adanya, bukan yang Anda harapkan. Skornya keluar di tempat, dan seluruh perhitungan berjalan di perangkat Anda sendiri &mdash; tidak ada jawaban yang dikirim ke kami.</p>
          <p class="shead-note">1&ndash;2 menit &middot; tanpa daftar &middot; tanpa biaya</p>
        </div>
      </div>

      <noscript>
        <div class="ph-nojs">Tab penilaian ini butuh JavaScript aktif. Kalau tidak memungkinkan,
        sampaikan saja kondisi usaha Anda lewat WhatsApp, dan tim kami yang menghitungkannya bersama Anda.</div>
      </noscript>

      <div class="pen" id="pen">
        <div class="pen-head">
          <span class="pen-prog"><span id="penCount">Terjawab 0 dari 8</span>
            <span class="pen-bar" aria-hidden="true"><i id="penBar"></i></span></span>
          <button class="pen-reset" type="button" id="penReset">Ulangi dari awal</button>
        </div>
        <ol class="pen-list" id="penList">{opsi_html}</ol>
        <div class="pen-cek" id="penCek" hidden aria-live="polite"></div>
        <div class="pen-actions">
          <button class="btn btn-primary" type="button" id="penHitung" disabled>Lihat skor saya</button>
          <span class="pen-hint" id="penHint">Masih ada 8 pertanyaan yang belum dijawab.</span>
        </div>
      </div>

      <div class="pen-hasil" id="penHasil" hidden aria-live="polite">
        <div class="ph-top">
          <div class="ph-disc">
            <canvas id="phCanvas" width="168" height="168" role="img"
              aria-label="Cakram skor kesiapan"></canvas>
            <div class="ph-num" id="phNum">0<span>/100</span></div>
          </div>
          <div>
            <span class="ph-band"><span class="pip"></span><span id="phBand">&mdash;</span></span>
            <p class="ph-h3">Hasil penilaian Anda</p>
            <p class="ph-arti" id="phArtis">&mdash;</p>
            <div class="ph-langkah"><b>Langkah berikutnya</b><span id="phLangkah">&mdash;</span></div>
          </div>
        </div>
        <div class="ph-mid">
          <p class="ph-lab">Delapan dimensi, urut dari yang paling lemah</p>
          <div id="phRows"></div>
        </div>
        <div class="ph-gap" id="phGap"></div>
        <div class="ph-aksi">
          <a class="btn btn-primary" id="phWa" href="https://wa.me/6288809640700" target="_blank" rel="noopener">Kirim hasil ke tim OmniSense</a>
          <button class="ph-cetak" type="button" onclick="window.print()">Cetak / simpan PDF</button>
          <p class="ph-note">Hasil ini titik awal diskusi, bukan penilaian mutu bisnis Anda. Yang paling berguna justru membahas celah yang paling mahal.</p>
          <p class="ph-limit" id="phLimit" hidden></p>
        </div>
      </div>
    </div>
  </section>
"""


def tanam_data_js(teks, data):
    """Sisipkan data JSON sebagai skrip. Dipakai bersama penanaman skrip tab."""
    return (
        "\n<script>\n/* data tab penilaian — sumber: tab-penilaian/pertanyaan.json */\n"
        "window.__PENILAIAN__ = "
        + json.dumps(data, ensure_ascii=False, separators=(",", ":"))
        + ";\n</script>\n"
    )


def main():
    if not os.path.exists(INDEX):
        sys.exit("index.html tidak ditemukan: " + INDEX)
    s = open(INDEX, encoding="utf-8").read()

    if MARK in s or 'id="penilaian"' in s:
        print("sudah tertanam — tidak ada perubahan (idempoten).")
        return

    data = baca_data()
    assert len(data["dimensi"]) == 8, "butuh 8 dimensi"
    assert abs(sum(d["bobot"] for d in data["dimensi"]) - 1.0) < 1e-9, "bobot harus berjumlah 1.0"
    assert len(data["band"]) == 5, "butuh 5 band"
    assert len(data["rekomendasi_dimensi"]) == 8, "butuh 8 rekomendasi dimensi"
    for d in data["dimensi"]:
        assert len(d["pilihan"]) == 5, d["kode"] + ": butuh 5 pilihan"

    # 1) cadangkan lebih dulu (jangan timpa cadangan yang sudah ada)
    os.makedirs(ARSIP, exist_ok=True)
    if not os.path.exists(CADANGAN):
        shutil.copy2(INDEX, CADANGAN)
        print("cadangan dibuat:", CADANGAN)
    else:
        print("cadangan sudah ada, dibiarkan:", CADANGAN)

    awal = len(s)

    # 2) CSS sebelum </style>
    assert s.count("</style>") == 1, "harus ada satu </style>"
    s = s.replace("</style>", CSS + "\n</style>", 1)

    # 3) bagian HTML setelah bagian #dimensi (sebelum OUTPUT)
    penanda = "<!-- ================= OUTPUT"
    assert s.count(penanda) == 1, "penanda bagian OUTPUT harus ada satu"
    s = s.replace(penanda, bagian_html(data).strip() + "\n\n  " + penanda, 1)

    # 4) item peta bagian (ixbar) + penomoran ulang
    lama_ix = (
        '<a class="ix" href="#dimensi"><span class="n">03</span>Penilaian<span class="c">8 dimensi</span></a>\n'
    )
    baru_ix = (
        '<a class="ix" href="#dimensi"><span class="n">03</span>Dimensi<span class="c">8 bobot</span></a>\n'
        '    <a class="ix" href="#penilaian"><span class="n">04</span>Coba penilaian<span class="c">1&ndash;2 menit</span></a>\n'
    )
    assert lama_ix in s, "item ixbar #dimensi tidak ditemukan seperti dugaan"
    s = s.replace(lama_ix, baru_ix, 1)
    for lama, baru in [
        ('<span class="n">04</span>Yang Anda terima', '<span class="n">05</span>Yang Anda terima'),
        ('<span class="n">05</span>Kamus', '<span class="n">06</span>Kamus'),
        ('<span class="n">06</span>Studi kasus', '<span class="n">07</span>Studi kasus'),
        ('<span class="n">07</span>Kontak', '<span class="n">08</span>Kontak'),
        ('\u00b7 rata-rata 12 menit', '\u00b7 skor keluar di tempat'),
    ]:
        assert lama in s, "penomoran ixbar tidak ditemukan: " + lama
        s = s.replace(lama, baru, 1)

    # 5) tautan nav: "Penilaian" -> bagian #dimensi, tambah tautan ke tab
    nav_lama = '<a class="nav-link" href="#dimensi">Penilaian</a>\n'
    nav_baru = ('<a class="nav-link" href="#dimensi">Dimensi</a>\n'
                '      <a class="nav-link" href="#penilaian">Penilaian</a>\n')
    assert nav_lama in s, "nav #dimensi tidak ditemukan"
    s = s.replace(nav_lama, nav_baru, 1)

    # 6) scrollspy: kenali bagian baru
    spy_lama = "var spyIds = ['top', 'proses', 'kategori', 'dimensi', 'output', 'kamus', 'hasil', 'kontak'];"
    spy_baru = "var spyIds = ['top', 'proses', 'kategori', 'dimensi', 'penilaian', 'output', 'kamus', 'hasil', 'kontak'];"
    assert spy_lama in s, "spyIds tidak ditemukan seperti dugaan"
    s = s.replace(spy_lama, spy_baru, 1)

    # 7) CTA hero utama -> tab penilaian (WhatsApp tetap ada di bagian kontak & hasil)
    cta_lama = ('<a class="btn btn-primary" href="https://wa.me/6288809640700?text=Halo%20OmniSense%2C%20saya%20ingin%20penilaian%20kesiapan%20gratis" target="_blank" rel="noopener">')
    cta_baru = '<a class="btn btn-primary" href="#penilaian">'
    assert s.count(cta_lama) >= 1, "CTA WhatsApp hero tidak ditemukan"
    s = s.replace(cta_lama, cta_baru, 1)
    # label tombol hero: dulu ke WhatsApp, sekarang ke tab penilaian
    assert "            Mulai penilaian\n" in s, "label tombol hero tidak ditemukan"
    s = s.replace("            Mulai penilaian\n", "            Isi penilaian sekarang\n", 1)

    # 8) data + skrip tab: disisipkan di akhir dokumen
    s = s.rstrip()
    s += tanam_data_js(s, data)
    s += "<script>" + JS + "</script>\n</body>\n</html>\n"

    open(INDEX, "w", encoding="utf-8").write(s)
    print(f"index.html: {awal} -> {len(s)} byte (+{len(s) - awal})")
    print("tab penilaian tertanam.")


if __name__ == "__main__":
    main()
