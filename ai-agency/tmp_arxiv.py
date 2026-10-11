import sys, urllib.request, xml.etree.ElementTree as ET, re

ns = {"a": "http://www.w3.org/2005/Atom"}
url = "https://export.arxiv.org/api/query?id_list=" + sys.argv[1]
raw = urllib.request.urlopen(url, timeout=30).read()
root = ET.fromstring(raw)
for e in root.findall("a:entry", ns):
    print("TITLE:", " ".join(e.find("a:title", ns).text.split()))
    print("ID:", e.find("a:id", ns).text.strip())
    print("DATE:", e.find("a:published", ns).text[:10])
    print("ABS:", " ".join(e.find("a:summary", ns).text.split())[:900])
    print("-" * 70)
