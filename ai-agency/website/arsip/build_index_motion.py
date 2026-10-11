#!/usr/bin/env python3
# Bangun index-motion.html = SELURUH isi index.html + motion hasil eksplor motionsites
# (cakram skor Canvas 2D, rail tick + penanda berdenyut, strip bergulir berhenti saat disapa).
# Skrip ini deterministik: jalankan ulang kalau index.html berubah.
import re, sys, pathlib

SRC = pathlib.Path('/home/ubuntu/ai-agency/website/index.html')
OUT = pathlib.Path('/home/ubuntu/ai-agency/website/index-motion.html')
s = SRC.read_text()

def cut(a, b, inc_b=False):
    i = s.index(a); j = s.index(b, i)
    return s[i:(j + len(b) if inc_b else j)]

# ---------- 1. CSS tambahan ----------
CSS = r'''
/* ============================================================
   v4 — motion dari eksplor motionsites (ronde 2), dipasang ke isi situs
   1. cakram skor di panel hero (Canvas 2D) menggantikan medan titik
   2. rail tick + penanda posisi berdenyut di kanan
   3. strip bergulir berhenti saat disapa
   Isi, teks, dan struktur halaman tidak diubah.
   ============================================================ */

/* --- 1. cakram skor di dalam cincin panel hero --- */
.gauge svg .track { stroke: rgba(255,255,255,.16); }
#scoreDisc { position:absolute; inset:0; width:100%; height:100%; z-index:0; }
.gauge .num { z-index:1; pointer-events:none; }
.gauge .num b { font-variant-numeric: tabular-nums; }

/* --- 2. rail tick: penanda posisi berdenyut di ujung tick yang menyala --- */
.ticks .tklead {
  width:7px; height:7px; border-radius:50%; background:var(--signal);
  box-shadow:0 0 0 0 rgba(20,184,166,.55);
  animation: tklead 1.4s ease-out infinite;
  will-change: transform;
}
@keyframes tklead {
  0%   { box-shadow: 0 0 0 0 rgba(20,184,166,.5) }
  70%  { box-shadow: 0 0 0 7px rgba(20,184,166,0) }
  100% { box-shadow: 0 0 0 0 rgba(20,184,166,0) }
}
@media (prefers-reduced-motion: reduce){ .ticks .tklead { animation:none; box-shadow:none } }
.no-motion .ticks .tklead { animation:none; box-shadow:none }

/* --- 3. strip bergulir: berhenti saat disapa (kursor atau tap) --- */
.marquee { display:block; }
.marquee.paused .mq-track { animation-play-state: paused; }
@media (hover: hover) and (pointer: fine){
  .marquee:hover .mq-track { animation-play-state: paused; }
}
/* hormati preferensi sistem: jalur bergulir berhenti, isi tetap terbaca */
@media (prefers-reduced-motion: reduce){
  .marquee .mq-track { animation: none !important; transform: none !important; }
}
.no-motion .marquee .mq-track { animation: none !important; transform: none !important; }
'''

# ---------- 2. JS pengganti blok 1 (medan titik -> cakram skor) ----------
JS_DISC = r'''  /* ---------- 1. cakram skor (menggantikan medan titik) ---------- */
  var cv = $('#scoreDisc'), ctx = cv.getContext('2d');
  var W = 132, H = 132, DPR = 1, raf = null, heroVisible = true, tabVisible = !doc.hidden;
  var discSweep = 0, discT0 = 0, discDone = false;
  var LINE = 'rgba(255,255,255,.16)', NTICK = 44, DOTS = [], di;
  for (di = 0; di < 64; di++){
    DOTS.push({
      a: Math.random() * Math.PI * 2, r: 48 * (0.60 + Math.random() * 0.36),
      s: 0.00035 + Math.random() * 0.0009, o: 0.22 + Math.random() * 0.5, sz: 0.5 + Math.random() * 0.9
    });
  }

  function sizeCanvas(){
    var r = cv.getBoundingClientRect();
    W = r.width || 132; H = r.height || 132;
    DPR = Math.min(2, window.devicePixelRatio || 1);
    cv.width = Math.max(1, Math.round(W * DPR));
    cv.height = Math.max(1, Math.round(H * DPR));
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }

  function drawDisc(t){
    var R = Math.min(W, H) / 2, i;
    ctx.clearRect(0, 0, W, H);
    ctx.save(); ctx.translate(W / 2, H / 2);
    /* jarum radial berputar — latar, opasitas rendah */
    ctx.strokeStyle = LINE;
    for (i = 0; i < NTICK; i++){
      var a = i / NTICK * Math.PI * 2 + t * 0.00005;
      var inner = R * 0.46, outer = R * (0.74 + 0.1 * Math.sin(t * 0.00035 + i));
      ctx.globalAlpha = 0.12 + 0.3 * Math.abs(Math.sin(t * 0.00028 + i * 0.5));
      ctx.lineWidth = 1.1; ctx.lineCap = 'round';
      ctx.beginPath();
      ctx.moveTo(Math.cos(a) * inner, Math.sin(a) * inner);
      ctx.lineTo(Math.cos(a) * outer, Math.sin(a) * outer);
      ctx.stroke();
    }
    /* cincin: track + busur teal yang membaca skor 0 -> 68 */
    ctx.globalAlpha = 1; ctx.lineWidth = 8; ctx.lineCap = 'butt';
    ctx.strokeStyle = LINE;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.92, 0, Math.PI * 2); ctx.stroke();
    ctx.strokeStyle = SIG; ctx.lineWidth = 8; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.arc(0, 0, R * 0.92, -Math.PI / 2, -Math.PI / 2 + discSweep * 0.68 * Math.PI * 2); ctx.stroke();
    /* cincin dalam + titik orbit */
    ctx.globalAlpha = .35; ctx.strokeStyle = SIG; ctx.lineWidth = 1.2;
    ctx.beginPath(); ctx.arc(0, 0, R * 0.36, 0, Math.PI * 2); ctx.stroke();
    for (i = 0; i < DOTS.length; i++){
      var o = DOTS[i]; o.a += o.s * 16;
      var x = Math.cos(o.a) * o.r, y = Math.sin(o.a) * o.r * 0.66;
      ctx.globalAlpha = o.o; ctx.fillStyle = (i % 7 === 0) ? SIG : '#FFFFFF';
      ctx.beginPath(); ctx.arc(x, y, o.sz, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }

  function loop(ts){
    raf = null;
    if (!motion || !heroVisible || !tabVisible) return;
    if (discSweep < 1){
      discSweep = Math.min(1, (ts - discT0) / 1400);
      discSweep = 1 - Math.pow(1 - discSweep, 3);
      if (discSweep >= 1){ discSweep = 1; discDone = true; gaugeNum.textContent = String(FINAL_SCORE); }
      else gaugeNum.textContent = String(Math.round(discSweep * FINAL_SCORE));
    }
    drawDisc(ts);
    raf = requestAnimationFrame(loop);
  }
  function discFinal(){
    discSweep = 1; discDone = true; discT0 = performance.now();
    gaugeNum.textContent = String(FINAL_SCORE);
    arc.style.transition = 'none'; arc.style.strokeDashoffset = String(ARC_OFF);
    sizeCanvas(); drawDisc(performance.now());
  }
  function canvasStart(){
    cv.style.display = ''; sizeCanvas();
    /* ukur langsung: bendera heroVisible bisa basi kalau observer tak melihat perubahan */
    var hr = $('#top').getBoundingClientRect();
    heroVisible = hr.bottom > 0 && hr.top < window.innerHeight;
    if (discSweep === 0) discT0 = performance.now();
    if (reduced) return;            /* reduced-motion: busur tetap digambar, hanya tidak berputar */
    if (!raf) raf = requestAnimationFrame(loop);
  }
  function canvasStop(){
    if (raf){ cancelAnimationFrame(raf); raf = null; }
    /* keluar layar saat busur belum penuh: selesaikan, jangan bekukan setengah jalan */
    if (!discDone) discFinal();
    ctx.clearRect(0, 0, W, H);
    cv.style.display = 'none';
  }
  /* gerak mati -> animasi berhenti, gambar terakhir tetap ada */
  function discSettle(){ canvasStop(); cv.style.display = ''; sizeCanvas(); discFinal(); }

'''

# ---------- 3. rangkai ----------
style = cut('<style>', '</style>', inc_b=True)
head  = cut('<html lang="id">', '<style>')
body  = cut('<body>', '<script>')
js    = cut('<script>\n(function(){', '</script>', inc_b=True)

# 3a. canvas hero (medan titik) -> cakram di DALAM cincin skor panel hero
assert '<canvas id="field" aria-hidden="true"></canvas>\n' in body
body = body.replace('  <canvas id="field" aria-hidden="true"></canvas>\n', '')
assert '<div class="num">' in body
body = body.replace('<div class="num">',
                    '<canvas id="scoreDisc" aria-hidden="true"></canvas>\n            <div class="num">', 1)

# 3b. ganti blok 1 di JS (medan titik) dengan cakram
a1 = js.index('  /* ---------- 1. canvas node field ---------- */')
a2 = js.index('  /* ---------- 2. spotlight kursor ---------- */')
js = js[:a1] + JS_DISC + js[a2:]

# 3c. gaugeRun tidak lagi menghitung angka sendiri (cakram yang menggerakkannya)
js = js.replace("""    arc.style.strokeDashoffset = String(ARC_OFF);
    countUp();""",
"""    arc.style.strokeDashoffset = String(ARC_OFF);""", 1)

# 3d. resetAnim: kembalikan cakram ke nol supaya "gerak nyala" bisa diulang
js = js.replace("""    arc.style.transition = 'none';
    arc.style.strokeDashoffset = String(ARC_C);
    gaugeNum.textContent = '0';""",
"""    arc.style.transition = 'none';
    arc.style.strokeDashoffset = String(ARC_C);
    gaugeNum.textContent = '0';
    discSweep = 0; discDone = false;""", 1)

# 3e. penanda posisi di rail tick + strip bergulir
js = js.replace("""  var tickEls = $$('.tk', ticks);""",
"""  var tickEls = $$('.tk', ticks);
  var leadEl = doc.createElement('span');
  leadEl.className = 'tklead';
  ticks.appendChild(leadEl);
  var TK_STEP = 8; /* 1px tick + 7px gap */""", 1)

js = js.replace("""    tickEls.forEach(function(el, i){ el.classList.toggle('on', i < lit); });
    pcEl.textContent = String(Math.round(p * 100)).padStart(3, '0') + '%';""",
"""    tickEls.forEach(function(el, i){ el.classList.toggle('on', i < lit); });
    pcEl.textContent = String(Math.round(p * 100)).padStart(3, '0') + '%';
    /* penanda "kamu di sini": satu titik berdenyut di ujung tick yang menyala */
    var nTk = tickEls.length, frac = p * nTk, ly;
    if (frac <= 0) ly = 0;
    else if (frac >= nTk) ly = nTk * TK_STEP;
    else ly = frac * TK_STEP - 4;
    leadEl.style.transform = 'translateY(' + ly + 'px)';""", 1)

js = js.replace("""  /* ---------- 7. kamus: chip + panel ---------- */""",
"""  /* ---------- 6b. strip bergulir: berhenti saat disapa (tap di HP) ---------- */
  var mq = $('.marquee');
  if (mq){
    mq.addEventListener('pointerdown', function(){ mq.classList.add('paused'); });
    ['pointerup', 'pointercancel', 'pointerleave'].forEach(function(ev){
      mq.addEventListener(ev, function(){ mq.classList.remove('paused'); });
    });
  }

  /* ---------- 7. kamus: chip + panel ---------- */""", 1)

# 3f. ekspos cakram untuk QA + jalur "gerak mati" memakai discSettle
js = js.replace("""      toFinal();
      canvasStop();
      spotStop();""",
"""      toFinal();
      discSettle();
      spotStop();""", 1)

js = js.replace("gauge: function(){ return gaugeNum.textContent; }",
                "gauge: function(){ return gaugeNum.textContent; }, disc: function(){ return discSweep; }")

# 3g. TEMA A mematikan justru elemen yang kita hidupkan (#field, .ticks, marquee).
#     Di berkas motion, buang aturan pemadam itu; sisanya (watermark) dibiarkan.
KILL = """
/* ---- yang paling "AI": kanvas titik, penggaris gulir, marquee, watermark ---- */
#field,
.ticks,
.mq,
.mq-track,
.ticker { display: none !important; }
"""
assert KILL in style, 'blok pemadam TEMA A tidak ditemukan'
style = style.replace(KILL, """
/* ---- v4: elemen "paling AI" dihidupkan kembali (lihat blok motion di bawah) ---- */
""", 1)
assert '.marquee { display: none; }' in style
style = style.replace('.marquee { display: none; }', '', 1)

# 3h. hero keluar layar saat busur belum penuh -> selesaikan (jangan tinggalkan busur separuh)
js = js.replace("""      heroVisible = e.isIntersecting;
      if (motion && !reduced){ if (heroVisible && !raf) raf = requestAnimationFrame(loop); }""",
"""      heroVisible = e.isIntersecting;
      if (!heroVisible && !discDone) discFinal();
      if (motion && !reduced){ if (heroVisible && !raf) raf = requestAnimationFrame(loop); }""", 1)

out = head + style.replace('</style>', CSS + '</style>') + body + js
OUT.write_text(out)
print('tulis', OUT, len(out), 'bytes')
