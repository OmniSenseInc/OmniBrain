import re, html, difflib, sys
# Bandingkan TEKS TERLIHAT index.html dengan cadangan sebelum motion.
# Tujuan: membuktikan penanaman motion tidak mengubah satu kata pun.
def t(p):
    x = open(p).read()
    x = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', x, flags=re.S)
    y = re.sub(r'<[^>]+>', '\n', x)
    return [l.strip() for l in html.unescape(y).split('\n') if l.strip()]
a = t('/home/ubuntu/ai-agency/website/arsip/index-v2-sebelum-motion.html')
b = t('/home/ubuntu/ai-agency/website/index.html')
print('teks identik:', a == b, len(a), len(b))
if a != b:
    for l in list(difflib.unified_diff(a, b, 'sebelum', 'sesudah', lineterm='', n=1))[:40]:
        print(l)
    sys.exit(1)
