#!/usr/bin/env python3
"""Google News RSS search -> resolve each item to its real publisher URL via curl -L."""
import sys, subprocess, urllib.parse, xml.etree.ElementTree as ET

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

def rss(query, n=8):
    url = ("https://news.google.com/rss/search?q=" + urllib.parse.quote(query) +
           "&hl=en-US&gl=US&ceid=US:en")
    out = subprocess.run(['curl', '-s', '--max-time', '25', '-A', UA, url],
                         capture_output=True, text=True, timeout=35).stdout
    root = ET.fromstring(out)
    items = []
    for it in root.findall('.//item')[:n]:
        items.append((it.findtext('title', ''), it.findtext('link', ''),
                      it.findtext('pubDate', ''), it.findtext('source', '')))
    return items

def resolve(link):
    p = subprocess.run(['curl', '-sL', '--max-time', '20', '-A', UA, '-o', '/dev/null',
                        '-w', '%{url_effective}', link], capture_output=True, text=True, timeout=30)
    return p.stdout.strip()

for q in sys.argv[1:]:
    print(f'##### QUERY: {q}')
    for title, link, date, src in rss(q):
        real = resolve(link)
        print(f'- {title}\n  src={src} | {date}\n  real={real[:160]}')
    print()
