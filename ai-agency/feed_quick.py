import sys, urllib.request, xml.etree.ElementTree as ET

NS = {'a': 'http://www.w3.org/2005/Atom', 'rss': 'http://purl.org/rss/1.0/'}

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (feed reader)'})
    return urllib.request.urlopen(req, timeout=30).read()

def show(url, limit=12):
    try:
        raw = get(url)
    except Exception as e:
        print('ERR', url, e)
        return
    try:
        root = ET.fromstring(raw)
    except Exception as e:
        print('PARSE ERR', url, e)
        return
    items = root.findall('.//item') or root.findall('a:entry', NS)
    print('===', url)
    for it in items[:limit]:
        t = it.findtext('title') or it.findtext('a:title', '', NS)
        d = (it.findtext('pubDate') or it.findtext('a:published', '', NS)
             or it.findtext('a:updated', '', NS) or '')
        lk = it.findtext('link') or ''
        if not lk:
            le = it.find('a:link', NS)
            lk = le.get('href') if le is not None else ''
        print('-', (t or '').strip().replace('\n', ' '))
        print('  ', d.strip(), lk.strip())
    print()

for u in sys.argv[1:]:
    show(u)
