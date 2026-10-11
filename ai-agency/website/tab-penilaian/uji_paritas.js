#!/usr/bin/env node
/* Uji paritas: skoring tab penilaian (JS) HARUS sama dengan kalkulator_kesiapan.py.
   Kalau tidak sama, situs bisa menampilkan angka berbeda dari yang tim pakai
   saat sesi konsultasi — itu merusak kepercayaan.
   Jalankan: node tab-penilaian/uji_paritas.js
*/
const DIM = [
  ["Strategi & Kepemimpinan", 0.10],
  ["Kesiapan Data", 0.20],
  ["Infrastruktur & Teknologi", 0.15],
  ["Digitalisasi Proses", 0.15],
  ["Organisasi & Budaya", 0.10],
  ["SDM & Keterampilan", 0.15],
  ["Tata Kelola, Keamanan & Kepatuhan", 0.10],
  ["Anggaran & Finansial", 0.05],
];
const BANDS = [
  [80, "SIAP PENUH"], [60, "LAYAK LANJUT"], [40, "KONVENSIONAL"],
  [20, "AWAL"], [0, "SANGAT AWAL"],
];
/* Bulatkan ke 1 desimal dulu, sama seperti situs & kalkulator python. Tanpa ini
   skor tepat di ambang (mis. 60,0) bisa jatuh ke band bawah. */
const band = p => BANDS.find(([t]) => Math.round(p * 10 + 1e-9) / 10 >= t)[1];

function hitung(nilai) {
  if (nilai.length !== 8) throw new Error("butuh 8 nilai");
  nilai.forEach(v => { if (v < 1 || v > 5) throw new Error("nilai di luar 1-5: " + v); });
  const per = DIM.map(([nama, bobot], i) => [nama, nilai[i], bobot, nilai[i] * bobot]);
  const total = per.reduce((s, r) => s + r[3], 0);
  const percent = Math.round((total / 5) * 100 * 10 + 1e-9) / 10;
  return { percent, band: band(percent), per };
}

// --- kasus uji: nilai 8 dimensi + persen DAN band yang dikeluarkan python3 kalkulator_kesiapan.py
const KASUS = [
  { n: [4, 3, 5, 3, 2, 3, 3, 2], py: 65.0, band: "LAYAK LANJUT" },
  { n: [5, 5, 5, 5, 5, 5, 5, 5], py: 100.0, band: "SIAP PENUH" },
  { n: [1, 1, 1, 1, 1, 1, 1, 1], py: 20.0, band: "AWAL" },
  { n: [3, 3, 3, 3, 3, 3, 3, 3], py: 60.0, band: "LAYAK LANJUT" },
  { n: [2, 2, 2, 2, 2, 2, 2, 2], py: 40.0, band: "KONVENSIONAL" },
  { n: [4, 4, 4, 4, 4, 4, 4, 4], py: 80.0, band: "SIAP PENUH" },
  { n: [5, 4, 3, 2, 1, 5, 4, 3], py: null, band: null },
];

let gagal = 0;
for (const k of KASUS) {
  const r = hitung(k.n);
  /* Band ikut diperiksa: dulu uji ini mencetak "60.0% KONVENSIONAL" sambil
     melaporkan OK, karena hanya angka yang dibandingkan. */
  const okAngka = k.py === null || Math.abs(r.percent - k.py) < 0.05;
  const okBand = k.band === null || r.band === k.band;
  const ok = okAngka && okBand;
  if (!ok) gagal++;
  console.log(
    (ok ? "OK  " : "BEDA") + "  [" + k.n.join(",") + "]  ->  " +
    r.percent.toFixed(1) + "%  " + r.band +
    (k.py === null ? "" : "  (py " + k.py.toFixed(1) + " " + k.band + ")")
  );
}

// batas band harus persis: 79.9 -> Layak Lanjut, 80 -> Siap Penuh
console.log("\nCek batas band:");
[[39.9, "AWAL"], [40, "KONVENSIONAL"], [59.9, "KONVENSIONAL"], [60, "LAYAK LANJUT"],
 [79.9, "LAYAK LANJUT"], [80, "SIAP PENUH"],
 [19.9, "SANGAT AWAL"], [20, "AWAL"]]
  .forEach(([p, harap]) => {
    const dapat = band(p);
    const ok = dapat === harap;
    if (!ok) gagal++;
    console.log("  " + (ok ? "OK  " : "BEDA") + "  " + p + "% -> " + dapat + " (harus " + harap + ")");
  });
console.log("\nHasil: " + (gagal ? gagal + " KASUS BEDA" : "semua cocok dengan kalkulator python"));
process.exit(gagal ? 1 : 0);
