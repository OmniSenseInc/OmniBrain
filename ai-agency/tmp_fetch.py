#!/usr/bin/env python3
"""Fetch URLs and print stripped text (first N chars each)."""
import sys, re, html, subprocess

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36")

def fetch(url):
    try:
        p = subprocess.run(['curl', '-sL', '--max-time', '30', '-A', UA, url],
                           capture_output=True, text=True, timeout=40)
        return p.stdout
    except Exception as e:
        return f'ERR {e}'

def strip(raw):
    raw = re.sub(r'(?is)<(script|style|noscript|svg|head)[^>]*>.*?</\1>', ' ', raw)
    raw = re.sub(r'(?is)<br\s*/?>', '\n', raw)
    raw = re.sub(r'(?is)</(p|div|li|h[1-6]|tr)>', '\n', raw)
    txt = re.sub(r'(?s)<[^>]+>', ' ', raw)
    txt = html.unescape(txt)
    txt = re.sub(r'[ \t\xa0]+', ' ', txt)
    txt = re.sub(r'\n\s*\n+', '\n', txt)
    return txt.strip()

limit = 5000
args = sys.argv[1:]
for a in args:
    if a.startswith('--limit='):
        limit = int(a.split('=')[1]); continue
    raw = fetch(a)
    txt = strip(raw)
    print(f'===== {a}  ({len(raw)} raw / {len(txt)} text) =====')
    print(txt[:limit])
    print()
