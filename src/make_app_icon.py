# -*- coding: utf-8 -*-
"""Turn the Gemini London dachshund image into the PWA / iPhone app icons.
Trims the white margin around the artwork, squares it, and rounds the corners
(transparent) like an iOS app icon."""
import os
from PIL import Image, ImageDraw, ImageChops

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Gemini_Generated_Image_nt2dbbnt2dbbnt2d.jpg")

src = Image.open(SRC).convert("RGB")

# --- trim the near-white background margin around the rounded tile ---
# Build a white reference and diff; the bounding box of the non-white pixels
# is the artwork. A small threshold ignores JPEG noise in the white border.
bg = Image.new("RGB", src.size, (255, 255, 255))
diff = ImageChops.difference(src, bg).convert("L")
mask = diff.point(lambda p: 255 if p > 12 else 0)
bbox = mask.getbbox()
if bbox:
    src = src.crop(bbox)

src = src.convert("RGBA")

# make it square (center-crop just in case the trim left it slightly off)
s = min(src.size)
left = (src.width - s) // 2
top = (src.height - s) // 2
src = src.crop((left, top, left + s, top + s))

def rounded(size, radius_frac=0.2237, out=None):
    ss = 4  # supersample for a smooth, anti-aliased corner
    big = src.resize((size * ss, size * ss), Image.LANCZOS)
    mask = Image.new("L", (size * ss, size * ss), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [0, 0, size * ss, size * ss], radius=int(size * ss * radius_frac), fill=255)
    big.putalpha(mask)
    img = big.resize((size, size), Image.LANCZOS)
    img.save(os.path.join(ROOT, out), "PNG")
    print("wrote", out, size)

# iOS home-screen icon + PWA icons (rounded corners)
rounded(180, out="apple-touch-icon.png")
rounded(192, out="icon-192.png")
rounded(512, out="icon-512.png")

# maskable: full-bleed square (the platform applies its own mask/safe-zone)
square = src.resize((512, 512), Image.LANCZOS)
square.save(os.path.join(ROOT, "icon-maskable-512.png"), "PNG")
print("wrote icon-maskable-512.png 512")
