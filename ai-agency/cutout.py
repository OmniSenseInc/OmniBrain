#!/usr/bin/env python3
"""cutout.py — potong latar foto, kualitas RAPI (cache PNG transparan).

Perbaikan dibanding versi pertama:
  - model lebih baik (default u2net; bisa diganti lewat REMBG_MODEL)
  - hanya komponen terbesar yang dipertahankan (buang sisa kursi/panggung)
  - tepi dihaluskan (feather) supaya tidak bergerigi

Pakai:
    .venv/bin/python cutout.py <foto_masuk> <png_keluar> [--ulang]
"""
import sys
import os

from PIL import Image, ImageFilter


def bersihkan_alpha(img):
    """Buang bercak kecil (sisa latar) — pertahankan komponen terbesar + ambang halo tipis."""
    alpha = img.getchannel("A")
    try:
        import numpy as np
        from scipy import ndimage
        a = np.array(alpha)
        biner = a > 40
        lbl, n = ndimage.label(biner)
        if n > 1:
            ukuran = ndimage.sum(biner, lbl, range(1, n + 1))
            terbesar = int(np.argmax(ukuran)) + 1
            simpan = lbl == terbesar
            # tutup lubang kecil di dalam subjek
            simpan = ndimage.binary_fill_holes(simpan)
            a = np.where(simpan, a, 0).astype("uint8")
            img.putalpha(Image.fromarray(a))
            print(f"  [bersih] {n} komponen -> sisakan 1 terbesar")
        # ambang halo: alpha < 90 dibuang (sisa latar tipis seperti logo/tepi berwarna)
        a2 = np.array(img.getchannel("A")).astype(np.float32)
        a2[a2 < 90] = 0
        a2[a2 > 200] = 255
        img.putalpha(Image.fromarray(a2.astype("uint8")))
    except Exception as e:
        print(f"  [info] pembersih komponen dilewati ({e.__class__.__name__})")
    return img


def netralkan_hijau(img, ambang=6):
    """Buang fringe hijau / hijau-kuning (sisa logo/chroma latar).
    Manusia tidak pernah hijau-dominan. Dua pola ditangkap:
      (a) hijau murni: G jelas > R dan > B.
      (b) hijau-kuning (fringe di tepi): R≈G, keduanya jelas > B (kulit punya R-G besar,
          jadi tidak ikut kena)."""
    try:
        import numpy as np
        a = np.array(img).astype(np.int16)
        r, g, b, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
        hijau_murni = (g > r + ambang) & (g > b + ambang) & (al > 0)
        hijau_kuning = (np.abs(r - g) <= 30) & (g > b + 22) & (r > b + 22) & (al > 0)
        kena = hijau_murni | hijau_kuning
        n = int(kena.sum())
        if n:
            lum = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.int16)
            r[kena] = lum[kena]; g[kena] = lum[kena]; b[kena] = lum[kena]
            a[..., 0], a[..., 1], a[..., 2] = r, g, b
            print(f"  [netral] {n} piksel hijau/hijau-kuning -> abu netral")
        return Image.fromarray(a.astype("uint8"), "RGBA")
    except Exception as e:
        print(f"  [info] netral hijau dilewati ({e.__class__.__name__})")
        return img


def buang_bercak_atas(img, batas_tinggi=0.28):
    """Buang komponen kecil yang 'nyangkut' di area atas kepala (sisa logo/panggung).
    Simpan hanya komponen terbesar dari potongan atas; buang sisanya."""
    try:
        import numpy as np
        from scipy import ndimage
        a = np.array(img)
        al = a[..., 3]
        h = al.shape[0]
        batas = int(h * batas_tinggi)
        atas = al[:batas] > 40
        lbl, n = ndimage.label(atas)
        if n > 1:
            ukuran = ndimage.sum(atas, lbl, range(1, n + 1))
            terbesar = int(np.argmax(ukuran)) + 1
            # hapus komponen atas yang bukan terbesar
            for i in range(1, n + 1):
                if i != terbesar and ukuran[i - 1] > 40:   # abaikan bercak sangat kecil
                    ys, xs = np.where(lbl == i)
                    a[ys, xs, 3] = 0
                    print(f"  [buang-bercak] komponen atas #{i} ({int(ukuran[i-1])}px) dihapus")
            img = Image.fromarray(a, "RGBA")
        return img
    except Exception as e:
        print(f"  [info] buang bercak atas dilewati ({e.__class__.__name__})")
        return img


def haluskan_tepi(img, radius=0.8, erode=0):
    """Erosi alpha (opsional) lalu feather lembut. erode=0 -> hanya feather
    (hindari artefak 'bolong' pada detail halus seperti rambut/gestur)."""
    from PIL import ImageFilter as F
    alpha = img.getchannel("A")
    if erode > 0:
        alpha = alpha.filter(F.MinFilter(erode * 2 + 1))
    alpha = alpha.filter(F.GaussianBlur(radius))
    img.putalpha(alpha)
    return img


def decontaminate(img):
    """Buang warna latar yang menempel di tepi: warna tepi ditarik ke warna dalam."""
    try:
        import numpy as np
        arr = np.array(img).astype(np.float32)
        a = arr[..., 3:4] / 255.0
        # warna tepi (alpha rendah) dicampur ke warna tetangga dalam (alpha tinggi)
        rgb = arr[..., :3]
        # blur warna, lalu campur berdasar alpha
        from PIL import Image as I
        blur = np.array(img.filter(ImageFilter.GaussianBlur(3))).astype(np.float32)[..., :3]
        campur = rgb * a + blur * (1 - a)
        arr[..., :3] = campur
        return I.fromarray(arr.astype("uint8"), "RGBA")
    except Exception:
        return img


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ulang = "--ulang" in sys.argv
    if len(args) < 2:
        print("pakai: cutout.py <masuk> <keluar> [--ulang]")
        return 2
    masuk, keluar = args[0], args[1]
    if not os.path.exists(masuk):
        print(f"GAGAL: {masuk} tidak ada")
        return 1
    if os.path.exists(keluar) and not ulang:
        print(f"SUDAH ADA: {keluar}")
        return 0

    from rembg import remove, new_session
    model = os.environ.get("REMBG_MODEL", "u2net")
    print(f"memotong latar: {masuk} (model {model}) ...", flush=True)
    src = Image.open(masuk).convert("RGB")
    if max(src.size) > 1600:
        skala = 1600 / max(src.size)
        src = src.resize((round(src.width * skala), round(src.height * skala)), Image.LANCZOS)
    sesi = new_session(model)
    hasil = remove(src, session=sesi).convert("RGBA")
    hasil = decontaminate(hasil)
    hasil = netralkan_hijau(hasil)
    hasil = buang_bercak_atas(hasil)
    hasil = bersihkan_alpha(hasil)
    hasil = haluskan_tepi(hasil, radius=0.8, erode=0)
    os.makedirs(os.path.dirname(keluar) or ".", exist_ok=True)
    hasil.save(keluar)
    print(f"SELESAI: {keluar} ({hasil.width}x{hasil.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
