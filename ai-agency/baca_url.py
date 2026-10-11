#!/usr/bin/env python3
"""Ambil halaman web -> teks bersih PENUH ke file (stdlib saja).
Pakai: python3 baca_url.py <url> <out.txt>
"""
import sys, re, html, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def teks(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                              "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=60) as r:
        raw = r.read()
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|nav|footer|svg|noscript|aside).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t


if __name__ == "__main__":
    url, out = sys.argv[1], sys.argv[2]
    try:
        t = teks(url)
    except Exception as e:
        t = "ERROR: %s" % e
    open(out, "w", encoding="utf-8").write(t)
    print("OK %s -> %s (%d chars)" % (url, out, len(t)))
