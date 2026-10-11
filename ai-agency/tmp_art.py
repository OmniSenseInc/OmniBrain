import sys, re, html, urllib.request

for url in sys.argv[1:]:
    print("=" * 78)
    print("URL:", url)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        raw = urllib.request.urlopen(req, timeout=35).read().decode("utf-8", "ignore")
    except Exception as e:
        print("ERR:", e)
        continue
    raw = re.sub(r"(?is)<(script|style|nav|footer|header|svg)[^>]*>.*?</\1>", " ", raw)
    m = re.search(r"(?is)<article[^>]*>(.*?)</article>", raw)
    body = m.group(1) if m else raw
    txt = re.sub(r"(?is)<(p|h1|h2|h3|li|br)[^>]*>", "\n", body)
    txt = re.sub(r"<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    print(txt.strip()[:4000])
