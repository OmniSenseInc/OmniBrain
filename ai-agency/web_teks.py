#!/usr/bin/env python3
"""Ambil halaman web -> teks bersih. Pakai: python3 web_teks.py <url> [max_char]"""
import sys, re, urllib.request, html

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125 Safari/537.36"


def ambil(url, batas=6000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en,id"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read().decode("utf-8", "ignore")
    raw = re.sub(r"(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?is)<br\s*/?>", "\n", raw)
    raw = re.sub(r"(?is)</(p|div|li|h[1-6]|tr)>", "\n", raw)
    teks = re.sub(r"(?s)<[^>]+>", " ", raw)
    teks = html.unescape(teks)
    teks = re.sub(r"[ \t\u00a0]+", " ", teks)
    teks = re.sub(r"\n\s*\n+", "\n", teks).strip()
    return teks[:batas]


if __name__ == "__main__":
    url = sys.argv[1]
    batas = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
    try:
        print(ambil(url, batas))
    except Exception as e:
        print(f"GAGAL {url}: {type(e).__name__}: {e}")
