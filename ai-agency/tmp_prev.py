import sys
from PIL import Image

for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB")
    im.thumbnail((760, 760))
    out = "/tmp/prev_" + p.split("/")[-1].rsplit(".", 1)[0] + ".jpg"
    im.save(out, quality=82)
    lum = sum(Image.open(p).convert("L").resize((64, 64)).getdata()) / 4096
    print(out, im.size, "luminansi=%.1f" % lum)
