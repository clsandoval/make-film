import sys
from PIL import Image
out, *fs = sys.argv[1:]
W, H = 960, 540
rows = (len(fs) + 1) // 2
sheet = Image.new("RGB", (W * 2, H * rows), "black")
for i, f in enumerate(fs):
    sheet.paste(Image.open(f).resize((W, H)), ((i % 2) * W, (i // 2) * H))
sheet.save(out, quality=75)
