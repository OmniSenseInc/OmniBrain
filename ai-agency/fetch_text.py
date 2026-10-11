import sys, re, urllib.request

def strip_html(h):
    h = re.sub(r'(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>', ' ', h)
    h = re.sub(r'(?is)<br\s*/?>', '\n', h)
    h = re.sub(r'(?is)</(p|div|li|h[1-6]|tr)>', '\n', h)
    h = re.sub(r'(?s)<[^>]+>', ' ', h)
    h = re.sub(r'&nbsp;', ' ', h)
    h = re.sub(r'&amp;', '&', h)
    h = re.sub(r'&#8217;|&#8216;', "'", h)
    h = re.sub(r'&#8220;|&#8221;', '"', h)
    h = re.sub(r'&quot;', '"', h)
    h = re.sub(r'[ \t]+', ' ', h)
    h = re.sub(r'\n\s*\n+', '\n', h)
    return h.strip()

limit = int(sys.argv[1])
for url in sys.argv[2:]:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36'})
        raw = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')
    except Exception as e:
        print('=== ERR', url, e)
        continue
    txt = strip_html(raw)
    print('===', url)
    print(txt[:limit])
    print()
