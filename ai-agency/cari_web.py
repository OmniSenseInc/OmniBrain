#!/usr/bin/env python3
"""Cari di DuckDuckGo (lite) -> daftar judul + URL. Pakai: python3 cari_web.py "query" [n]"""
import sys, re, html, urllib.parse, urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128 Safari/537.36"


def cari(q, n=8):
    url = "https://lite.duckduckgo.com/lite/?q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        raw = r.read().decode("utf-8", "ignore")
    # hasil lite: <a rel="nofollow" href="URL" class="result-link">TITLE</a>
    hasil = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*class="result-link"[^>]*>(.*?)</a>', raw, re.S | re.I):
        u, t = m.group(1), re.sub(r"<[^>]+>", "", m.group(2))
        u = html.unescape(u)
        if u.startswith("//duckduckgo.com/l/?uddg="):
            u = urllib.parse.unquote(u.split("uddg=")[1].split("&")[0])
        hasil.append((html.unescape(t).strip(), u))
        if len(hasil) >= n:
            break
    return hasil


if __name__ == "__main__":
    q = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    res = cari(q, n)
    if not res:
        print("TIDAK ADA HASIL")
    for i, (t, u) in enumerate(res, 1):
        print(f"{i}. {t}\n   {u}")
