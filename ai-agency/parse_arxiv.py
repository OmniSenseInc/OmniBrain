#!/usr/bin/env python3
"""Parse arXiv Atom XML -> ringkas (stdlib)."""
import sys, xml.etree.ElementTree as ET

ns = {'a': 'http://www.w3.org/2005/Atom'}
root = ET.parse(sys.argv[1]).getroot()
for i, e in enumerate(root.findall('a:entry', ns), 1):
    t = e.find('a:title', ns).text.strip().replace('\n', ' ')
    aid = e.find('a:id', ns).text.strip().split('/abs/')[-1]
    pub = e.find('a:published', ns).text[:10]
    summ = ' '.join(e.find('a:summary', ns).text.split())[:260]
    print(f'{i}. [{aid}] {t}')
    print(f'   {pub} | https://arxiv.org/abs/{aid}')
    print(f'   {summ}...')
    print()
