# -*- coding: utf-8 -*-
"""Generate the London-themed social/link preview (preview.jpg).

Background is an accurate Union Jack drawn to the official 2:1 construction
grid (same geometry as the hero SVG), with a translucent card carrying the
Hebrew title, a small-caps latin line and London area chips."""
import os
from PIL import Image, ImageDraw, ImageFont
from bidi.algorithm import get_display

FONTS = "C:/Windows/Fonts"
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Union Jack colours (site palette)
RED   = (200, 16, 46)     # #C8102E
WHITE = (255, 255, 255)
BLUE  = (1, 33, 105)      # #012169
PAPER = (246, 238, 220)   # cream
LEMON = (232, 180, 58)    # gold
INK_BLUE = (1, 20, 73)    # blue-deep

def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)

FRANK = "FrankRuhlHofshi-Bold.otf"       # Hebrew + latin serif, heavy
DAVID = "DavidLibre-Bold.ttf"
SERIF = "timesbd.ttf"

def he(s):
    """Reorder Hebrew for correct visual (RTL) rendering in PIL."""
    return get_display(s)

def union_jack(target_w, target_h):
    """Draw the Union Jack on the official 60x30 grid, then center-crop to
    the target size the way CSS `background-size:cover` would (no distortion).
    Red St George cross = 6/30 (1/5 H) with 2/30 white fimbriation each side;
    St Andrew white saltire = 6/30, St Patrick red saltire = 4/30 (drawn
    counterchanged via alternating triangular quadrants)."""
    scale = max(target_w / 60.0, target_h / 30.0)
    W, H = int(round(60 * scale)), int(round(30 * scale))
    img = Image.new("RGB", (W, H), BLUE)
    d = ImageDraw.Draw(img)

    def sx(u): return u * scale
    def line(p0, p1, colour, w):
        d.line([sx(p0[0]), sx(p0[1]), sx(p1[0]), sx(p1[1])], fill=colour,
               width=int(round(w * scale)))

    # --- white St Andrew saltire (full), then red St Patrick counterchanged ---
    line((0, 0), (60, 30), WHITE, 6)
    line((60, 0), (0, 30), WHITE, 6)
    # counterchange: red saltire hugs opposite sides of centre in each quadrant.
    # Draw the red diagonals clipped to alternating triangles (the pinwheel).
    tri = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(tri)
    # four triangles selecting the halves that carry the offset red bar
    c = (sx(30), sx(15))
    td.polygon([(sx(30), sx(15)), (sx(60), sx(15)), (sx(60), sx(30))], fill=255)   # lower-right
    td.polygon([(sx(30), sx(15)), (sx(0), sx(15)), (sx(0), sx(0))], fill=255)      # upper-left
    td.polygon([(sx(30), sx(15)), (sx(0), sx(15)), (sx(0), sx(30))], fill=255)     # lower-left
    td.polygon([(sx(30), sx(15)), (sx(60), sx(15)), (sx(60), sx(0))], fill=255)    # upper-right
    red = Image.new("RGB", (W, H), BLUE)
    rd = ImageDraw.Draw(red)
    def rline(p0, p1, w):
        rd.line([sx(p0[0]), sx(p0[1]), sx(p1[0]), sx(p1[1])], fill=RED,
                width=int(round(w * scale)))
    rline((0, 0), (60, 30), 4)
    rline((60, 0), (0, 30), 4)
    # composite the red diagonals only where they fall (over the white saltire)
    red_mask = Image.new("L", (W, H), 0)
    rmd = ImageDraw.Draw(red_mask)
    rmd.line([sx(0), sx(0), sx(60), sx(30)], fill=255, width=int(round(4 * scale)))
    rmd.line([sx(60), sx(0), sx(0), sx(30)], fill=255, width=int(round(4 * scale)))
    img.paste(red, (0, 0), red_mask)

    # --- upright St George cross: white fimbriation then red ---
    line((30, 0), (30, 30), WHITE, 10)
    line((0, 15), (60, 15), WHITE, 10)
    line((30, 0), (30, 30), RED, 6)
    line((0, 15), (60, 15), RED, 6)

    # center-crop to the requested aspect (cover)
    left = (W - target_w) // 2
    top = (H - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))

def make_preview(path):
    W, H = 1200, 630
    img = union_jack(W, H).convert("RGBA")
    # subtle darkening so the card/text reads over the flag
    img = Image.alpha_composite(img, Image.new("RGBA", (W, H), (6, 14, 40, 90)))
    d = ImageDraw.Draw(img)

    # centred translucent card
    cw, ch = 780, 512
    cx, cy = (W - cw) // 2, (H - ch) // 2
    card = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, cw, ch], radius=28, fill=(1, 20, 49, 165),
                         outline=(246, 238, 220, 95), width=2)
    img.alpha_composite(card, (cx, cy))
    d = ImageDraw.Draw(img)

    midx = W // 2
    d.text((midx, cy + 72), "L O N D O N  ·  2 0 2 6", font=font(SERIF, 40),
           fill=LEMON, anchor="mm")
    d.text((midx, cy + 188), he("לונדון"), font=font(FRANK, 165),
           fill=PAPER, anchor="mm")

    sub_txt = he("החופשה המושלמת מתחילה כאן")
    sub_sz = 42
    while sub_sz > 20:
        f_sub = font(DAVID, sub_sz)
        b = d.textbbox((0, 0), sub_txt, font=f_sub)
        if (b[2] - b[0]) <= cw - 90:
            break
        sub_sz -= 1
    d.text((midx, cy + 282), sub_txt, font=f_sub, fill=PAPER, anchor="mm")

    # London area chips
    chips = ["Westminster", "Soho", "Camden", "Notting Hill",
             "Shoreditch", "Greenwich"]
    f_chip = font(SERIF, 28)
    padx = 20
    gap = 14
    star_w = 18
    ch_h = 48
    row_gap = 15
    max_w = cw - 56
    raw = [(d.textbbox((0, 0), c, font=f_chip)[2] - d.textbbox((0, 0), c, font=f_chip)[0]) + padx * 2 for c in chips]
    uw = max(raw)
    widths = [uw] * len(chips)

    rows, cur, cur_w = [], [], 0
    for c, w in zip(chips, widths):
        add = w + (gap * 2 + star_w if cur else 0)
        if cur and cur_w + add > max_w:
            rows.append(cur); cur, cur_w = [], 0
            add = w
        cur.append((c, w)); cur_w += add
    if cur:
        rows.append(cur)

    total_h = len(rows) * ch_h + (len(rows) - 1) * row_gap
    region_c = (cy + 318 + cy + ch - 28) / 2
    chy = region_c - total_h / 2 + ch_h / 2
    for row in rows:
        row_w = sum(w for _, w in row) + (len(row) - 1) * (gap * 2 + star_w)
        x = midx - row_w / 2
        for j, (c, w) in enumerate(row):
            d.rounded_rectangle([x, chy - ch_h / 2, x + w, chy + ch_h / 2],
                                radius=ch_h / 2, outline=(246, 238, 220, 160), width=2)
            d.text((x + w / 2, chy), c, font=f_chip, fill=PAPER, anchor="mm")
            x += w
            if j < len(row) - 1:
                x += gap
                sx_, sy, s = x + star_w / 2, chy, 8
                d.polygon([(sx_, sy - s), (sx_ + s, sy), (sx_, sy + s), (sx_ - s, sy)], fill=LEMON)
                x += star_w + gap
        chy += ch_h + row_gap

    img.convert("RGB").save(path, "JPEG", quality=90)
    print("wrote", path)

make_preview(os.path.join(OUT, "preview.jpg"))
