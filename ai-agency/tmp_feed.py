import sys, re, html, urllib.request

url = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
d = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
items = re.findall(r"<item>(.*?)</item>", d, re.S)
if not items:
    items = re.findall(r"<entry>(.*?)</entry>", d, re.S)
for it in items[:n]:
    t = re.search(r"<title[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", it, re.S)
    l = re.search(r'<link[^>]*href="([^"]+)"', it) or re.search(r"<link>(.*?)</link>", it, re.S)
    pd = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S) or re.search(r"<updated>(.*?)</updated>", it, re.S)
    desc = re.search(r"<description>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</description>", it, re.S) or re.search(r"<content[^>]*>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</content>", it, re.S)
    print("TITLE:", html.unescape(t.group(1)).strip() if t else "")
    print("LINK:", l.group(1).strip() if l else "")
    print("DATE:", pd.group(1).strip() if pd else "")
    if desc:
        txt = re.sub(r"<[^>]+>", " ", desc.group(1))
        print("DESC:", html.unescape(re.sub(r"\s+", " ", txt)).strip()[:1000])
    print("-" * 70)
