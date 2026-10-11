/* Uji mesin pembaca tulisan bebas (penilaian.html).

   Kenapa ada: pengunjung boleh MENULIS jawabannya sendiri, bukan hanya
   memilih. Uji ini menjaga mesin tetap "paham kata-kata" — tiap kalimat
   punya nilai yang diharapkan, dan uji gagal kalau bacaan meleset.

   Cara jalan: butuh server lokal di 127.0.0.1:8080 (python3 -m http.server).
   Env: PW_CORE=<playwright-core> CHROME_PATH=<chrome>

   Ambang: >= 95% benar. Kalau turun, tambah frasa kunci di
   tab-penilaian/pertanyaan_situs.json lalu jalankan bangun_data_situs.py. */
const { chromium } = require(process.env.PW_CORE);

const KASUS = {
  D1a: [
    ['belum kepikiran arahnya', 1],
    ['jalani aja dulu belum ada tujuan', 1],
    ['ada di kepala saya saja', 2],
    ['masih angan-angan belum ditulis', 2],
    ['sudah saya ceritakan ke tim', 3],
    ['sudah saya sampaikan ke karyawan', 3],
    ['sudah tertulis ada targetnya', 5],
    ['tertulis dan ada target angka', 5],
    ['ada dokumen dan target', 5],
  ],
  D1b: [
    ['nggak pernah ngecek', 1],
    ['tidak ada cara mengecek', 1],
    ['kadang-kadang lihat kalau ingat', 2],
    ['jarang kami bahas', 2],
    ['cuma lihat laporan bulanan sekilas', 3],
    ['kadang saya cek catatannya', 3],
    ['evaluasi rutin tiap bulan', 4],
    ['setiap bulan kami bandingkan dengan target', 5],
    ['rutin dibandingkan target dan tercatat', 5],
  ],
  D2a: [
    ['tidak tahu angkanya', 1],
    ['belum pernah hitung untung bersih', 1],
    ['harus hitung manual dulu bisa 2-3 hari', 2],
    ['perlu rekap dulu beberapa jam', 2],
    ['harus tunggu istri saya yang pegang catatan', 3],
    ['tanya admin dulu', 3],
    ['buka catatan dulu sebentar', 4],
    ['lihat pembukuan', 4],
    ['bisa saya sebutkan saat ini juga', 5],
    ['sudah tahu angkanya akurat', 5],
  ],
  D2b: [
    ['tidak tahu', 1],
    ['belum pernah cek menunya', 1],
    ['kira-kira aja biasanya kopi susu', 2],
    ['hanya perkiraan saya', 2],
    ['harus tanya admin dulu', 3],
    ['tunggu kasir yang pegang catatan', 3],
    ['lihat catatan penjualan', 4],
    ['buka laporan dulu', 4],
    ['sudah tahu ada laporannya', 5],
    ['ada data menunya', 5],
  ],
  D2c: [
    ['tidak pernah dicatat', 1],
    ['tidak dicatat', 1],
    ['baru dicatat kalau sempat, kadang seminggu sekali', 2],
    ['sering menumpuk catatannya', 2],
    ['dicatat di akhir hari setelah tutup', 3],
    ['saya tulis di buku nanti sore', 3],
    ['langsung dicatat saat transaksi', 4],
    ['langsung saya catat waktu transaksi', 4],
    ['otomatis tercatat di sistem', 5],
    ['terekam sendiri tidak perlu diisi', 5],
  ],
  D3a: [
    ['masih pakai buku tulis dan HP pribadi', 1],
    ['serba kertas dan manual', 1],
    ['sebagian pakai HP sebagian masih kertas', 2],
    ['campur-campur belum semua digital', 2],
    ['sudah pakai aplikasi sederhana', 3],
    ['pakai excel untuk catat', 3],
    ['sudah pakai sistem kasir', 4],
    ['pakai mesin kasir', 4],
    ['semua sudah terhubung jadi satu sistem', 5],
    ['terintegrasi dalam satu aplikasi', 5],
  ],
  D3b: [
    ['cuma ada HP pribadi', 1],
    ['belum ada komputer', 1],
    ['ada komputer lama yang sering rusak', 2],
    ['perangkatnya lambat dan lemot', 2],
    ['cukup tapi hanya saya yang bisa pakai', 3],
    ['perangkatnya cukup memadai', 3],
    ['cukup lancar dipakai bergantian', 4],
    ['perangkatnya sudah bagus dan lancar', 4],
    ['lengkap tiap bagian punya sendiri', 5],
    ['perangkat modern dan lengkap', 5],
  ],
  D4a: [
    ['kalau saya tidak masuk semuanya kacau', 1],
    ['semua tergantung saya', 1],
    ['agak kacau kalau saya tidak ada', 2],
    ['pelayanan agak terganggu', 2],
    ['bisa jalan karena ada yang hafal', 3],
    ['pelayanan tetap jalan tapi lambat', 3],
    ['tetap normal tidak masalah', 4],
    ['jalan lancar walau saya tidak ada', 4],
    ['sudah ada panduan jadi siapa pun bisa', 5],
    ['terdokumentasi rapi', 5],
  ],
  D4b: [
    ['masih ikut kebiasaan saja', 1],
    ['belum ada panduannya', 1],
    ['ada catatan lepas tidak lengkap', 2],
    ['hanya diomongkan lisan', 2],
    ['sebagian sudah tertulis', 3],
    ['ada sebagian catatannya', 3],
    ['hampir semua tertulis', 4],
    ['ada sop tapi belum konsisten', 4],
    ['tertulis lengkap dan diperbarui', 5],
    ['tertulis dipakai dan diperbarui', 5],
  ],
  D5a: [
    ['banyak yang menolak dan tetap pakai cara lama', 1],
    ['ada penolakan akhirnya tidak jadi', 1],
    ['dipakai sebentar lalu ditinggalkan', 2],
    ['mereka ragu dan takut', 2],
    ['biasa saja netral', 3],
    ['jalan apa adanya', 3],
    ['mereka semangat dan mau coba', 4],
    ['diterima perlu waktu menyesuaikan', 4],
    ['sangat antusias sampai mengajari yang lain', 5],
    ['cepat terbiasa dan minta tambahan', 5],
  ],
  D5b: [
    ['berdasarkan perasaan saya saja', 1],
    ['feeling pemilik', 1],
    ['pengalaman dan ingatan saja', 2],
    ['kadang lihat catatan kadang feeling', 3],
    ['kadang lihat catatan kalau ada waktu', 3],
    ['saya pertimbangkan dulu', 3],
    ['sering pakai catatan atau angka', 4],
    ['lihat data penjualan dulu', 4],
    ['selalu pakai angka dan dibahas bersama tim', 5],
    ['berdasarkan data lengkap dan dianalisis', 5],
  ],
  D6a: [
    ['belum ada yang siap', 1],
    ['tidak ada sama sekali', 1],
    ['cuma saya sendiri', 2],
    ['saya sendiri yang belajar', 2],
    ['ada satu orang yang mau belajar', 3],
    ['satu dua orang', 3],
    ['banyak yang siap belajar', 4],
    ['lumayan banyak yang bisa', 4],
    ['semua siap belajar', 5],
    ['seluruh tim mau', 5],
  ],
  D6b: [
    ['tidak ada yang bisa pakai aplikasi', 1],
    ['semua serba kertas', 1],
    ['cuma saya sendiri', 2],
    ['satu orang saja', 2],
    ['sebagian kecil', 3],
    ['satu dua orang saja', 3],
    ['sebagian besar sudah nyaman', 4],
    ['banyak yang bisa', 4],
    ['hampir semua nyaman dan bisa mengajari', 5],
    ['semua bisa pakai aplikasi', 5],
  ],
  D7: [
    ['kalau HP hilang data ikut hilang', 1],
    ['tidak ada backup sama sekali', 1],
    ['disimpan di komputer tapi tidak ada backup', 1],
    ['hanya di komputer saja', 2],
    ['kadang backup tidak rutin', 3],
    ['jarang dicadangkan', 3],
    ['sudah rutin dicadangkan setiap minggu', 4],
    ['ada backup rutin', 4],
    ['backup otomatis dan aman', 5],
    ['tersalin otomatis dan aksesnya terbatas', 5],
  ],
  D8: [
    ['tidak ada anggaran khusus', 1],
    ['belum ada sama sekali', 1],
    ['kalau perlu baru beli', 2],
    ['ada tapi hanya kalau mendesak', 2],
    ['ada sisihan kecil untuk teknologi', 3],
    ['ada tapi tidak menentu jumlahnya', 3],
    ['ada anggaran tapi baru sekali jalan', 4],
    ['ada khusus tapi baru sekali', 4],
    ['ada anggaran tiap bulan', 5],
    ['rutin tiap bulan dan berkelanjutan', 5],
  ],
};

const AMBANG = 0.95;

(async () => {
  const b = await chromium.launch({ executablePath: process.env.CHROME_PATH });
  const p = await b.newPage({ viewport: { width: 1280, height: 900 } });
  await p.goto('http://127.0.0.1:8080/penilaian.html', { waitUntil: 'networkidle' });
  await p.waitForTimeout(500);

  const hasil = await p.evaluate((K) => {
    const out = { total: 0, benar: 0, salah: [], takTerbaca: [] };
    for (const kode of Object.keys(K)) {
      for (const [teks, harap] of K[kode]) {
        out.total++;
        const h = window.OmniSenseSitus.baca(kode, teks);
        const dapat = h ? h.nilai : null;
        if (dapat === harap) out.benar++;
        else if (dapat === null) out.takTerbaca.push({ kode, teks, harap });
        else out.salah.push({ kode, teks, harap, dapat });
      }
    }
    return out;
  }, KASUS);

  const persen = (hasil.benar / hasil.total * 100);
  console.log('Bacaan benar: ' + hasil.benar + '/' + hasil.total +
              '  (' + persen.toFixed(1) + '%)');
  if (hasil.salah.length) {
    console.log('\n-- SALAH NILAI (' + hasil.salah.length + ') --');
    hasil.salah.forEach(s => console.log('  ' + s.kode + '  harap ' + s.harap +
      ' dapat ' + s.dapat + '   "' + s.teks + '"'));
  }
  if (hasil.takTerbaca.length) {
    console.log('\n-- TIDAK TERBACA (' + hasil.takTerbaca.length +
                ') -> pengunjung diminta memilih sendiri --');
    hasil.takTerbaca.forEach(s => console.log('  ' + s.kode + '  harap ' + s.harap +
      '   "' + s.teks + '"'));
  }
  console.log('\n' + (persen >= AMBANG * 100 ? 'LULUS' : 'GAGAL') +
              ' (ambang ' + (AMBANG * 100) + '%)');
  await b.close();
  process.exit(persen >= AMBANG * 100 ? 0 : 1);
})();
