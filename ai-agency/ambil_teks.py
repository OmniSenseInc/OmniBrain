#!/usr/bin/env python3
"""Ambil halaman web dan cetak teks bersih (stdlib saja)."""
import sys, re, html, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def teks(url, n=4000):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=45) as r:
        raw = r.read()
    t = raw.decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|nav|footer|svg|noscript|aside).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"\s+", " ", t)
    return t[:n]


if __name__ == "__main__":
    for u in sys.argv[1:]:
        print("=" * 20, u)
        try:
            print(teks(u))
        except Exception as e:
            print("ERROR:", e)
        print()
