#!/usr/bin/env python3
import re, html, json, glob, sys

# Cek file hasil curl; cari payload profil (bio, post, caption) di HTML/JSON
for path in glob.glob('/tmp/rice_*.html') + ['/tmp/rice_ig.json']:
    try:
        raw = open(path, encoding='utf-8', errors='ignore').read()
    except Exception as e:
        continue
    print("=" * 60)
    print("FILE:", path, "size", len(raw))
    # apakah JSON murni?
    try:
        data = json.loads(raw)
        u = (data.get('data') or {}).get('user')
        if u:
            print("username:", u.get('username'))
            print("bio     :", u.get('biography'))
            m = u.get('edge_owner_to_timeline_media', {})
            print("total posts:", m.get('count'))
            for e in m.get('edges', [])[:12]:
                n = e.get('node', {})
                caps = n.get('edge_media_to_caption', {}).get('edges', [])
                txt = caps[0]['node'].get('text', '') if caps else ''
                print(f"\nPOST:\n{txt}")
        continue
    except Exception:
        pass
    # cari kata kunci
    for kw in ['username', 'biography', 'full_name', '__additionalDataModel', 'edge_owner_to_timeline_media']:
        if kw in raw:
            print(f"  mengandung '{kw}'")