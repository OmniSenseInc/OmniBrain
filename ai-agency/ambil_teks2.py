#!/usr/bin/env python3
"""Ambil halaman web, cetak teks bersih dengan jendela offset (stdlib saja)."""
import sys, re, html, urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def teks(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=45) as r:
        t = r.read().decode("utf-8", "ignore")
    t = re.sub(r"(?is)<(script|style|nav|footer|svg|noscript|aside).*?</\1>", " ", t)
    t = re.sub(r"(?s)<[^>]+>", " ", t)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t)


if __name__ == "__main__":
    url = sys.argv[1]
    mulai = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 4000
    try:
        t = teks(url)
        print(f"[total {len(t)} chars]")
        print(t[mulai:mulai + n])
    except Exception as e:
        print("ERROR:", e)
