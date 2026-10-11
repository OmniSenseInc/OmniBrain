#!/usr/bin/env python3
"""Parse cached RSS/Atom XML files -> compact list of recent entries."""
import sys, glob, os, re, html
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta

NS = {'a': 'http://www.w3.org/2005/Atom', 'dc': 'http://purl.org/dc/elements/1.1/'}

def strip(s):
    if not s: return ''
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()

def parse(path):
    out = []
    try:
        root = ET.parse(path).getroot()
    except Exception as e:
        print(f'!! {path}: {e}'); return out
    # Atom
    for e in root.findall('.//a:entry', NS):
        t = strip(e.findtext('a:title', '', NS))
        link = ''
        for l in e.findall('a:link', NS):
            link = l.get('href') or ''
            if l.get('rel') in (None, 'alternate'): break
        d = e.findtext('a:published', '', NS) or e.findtext('a:updated', '', NS)
        s = strip(e.findtext('a:summary', '', NS) or e.findtext('a:content', '', NS))
        src = ''
        sc = e.find('a:source', NS)
        if sc is not None: src = strip(sc.findtext('a:title', '', NS))
        out.append((d, t, link, s[:400], src))
    # RSS
    for e in root.findall('.//item'):
        t = strip(e.findtext('title', ''))
        link = strip(e.findtext('link', ''))
        d = strip(e.findtext('pubDate', ''))
        iso = ''
        if d:
            try: iso = parsedate_to_datetime(d).astimezone(timezone.utc).isoformat()
            except Exception: iso = d
        s = strip(e.findtext('description', ''))
        src = strip(e.findtext('source', '')) or strip(e.findtext('dc:creator', '', NS))
        out.append((iso, t, link, s[:400], src))
    return out

def key(d):
    try:
        return datetime.fromisoformat(d.replace('Z', '+00:00')).astimezone(timezone.utc)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

files = sys.argv[1:] or sorted(glob.glob('/tmp/*.xml'))
since = datetime.now(timezone.utc) - timedelta(hours=48)
rows = []
for f in files:
    for r in parse(f):
        rows.append((key(r[0]), os.path.basename(f), r))
rows.sort(key=lambda x: x[0], reverse=True)
n = 0
for k, f, r in rows:
    if k < since: continue
    n += 1
    print(f'[{k.strftime("%Y-%m-%d %H:%M")}Z] ({f}) {r[1]}')
    if r[4]: print(f'   src: {r[4]}')
    print(f'   {r[2]}')
    if r[3]: print(f'   {r[3]}')
    print()
print(f'== {n} entries within 48h ==')
