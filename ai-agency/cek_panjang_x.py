import pathlib
p = pathlib.Path('/home/ubuntu/ai-agency/caption_x_pending.txt')
t = p.read_text().strip()
print('chars:', len(t))
