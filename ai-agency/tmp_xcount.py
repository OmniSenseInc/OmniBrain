import sys, os
HERE = "/home/ubuntu/ai-agency"
p = os.path.join(HERE, "caption_x_pending.txt")
t = open(p).read().strip()
print("panjang:", len(t))
print("kata   :", len(t.split()))
print(t)
if len(t) > 280:
    print("!! MELEBIHI 280")
