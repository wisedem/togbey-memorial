from PIL import Image, ImageDraw, ImageFont
import sys
import math

MODE = sys.argv[1] if len(sys.argv) > 1 else "gold"   # "gold" or "black"

# ---------- assets ----------
oval = Image.open("oval.png").convert("RGB")
# Whiten everything outside an inscribed ellipse to remove stray marks
# (a sliver of the original calligraphy sat in the corner of the crop)
ow0, oh0 = oval.size
mask = Image.new("L", (ow0, oh0), 0)
ImageDraw.Draw(mask).ellipse([2, 2, ow0 - 3, oh0 - 3], fill=255)
white_bg = Image.new("RGB", (ow0, oh0), (255, 255, 255))
oval = Image.composite(oval, white_bg, mask).convert("RGBA")

SCRIPT = "fonts/PinyonScript-Regular.ttf"
SERIF  = "fonts/EBGaramond.ttf"
ITAL   = "fonts/EBGaramond-Italic.ttf"

INK   = (38, 38, 40)      # message charcoal
MSGGOLD = (158, 121, 56)  # rich antique gold for the message lines
NAME  = (96, 96, 100)     # deprioritized name grey
GOLD  = (176, 142, 78)    # echoes the oval frame
HAIR  = (170, 170, 174)   # hairline rule

# ---------- canvas geometry ----------
W = 1600
SIDE = 80          # tighter margin → more room for the script
MAXW = W - 2 * SIDE        # max text width

def font(path, size):
    return ImageFont.truetype(path, size)

def text_w(draw, s, f):
    b = draw.textbbox((0, 0), s, font=f)
    return b[2] - b[0]

# probe draw
probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))

# For the marble carver: switch from delicate script to bolder italic Garamond
# Tall x-height + thick strokes = readable when chiseled.
def make_italic_bold(size):
    fnt = ImageFont.truetype(ITAL, size)
    try: fnt.set_variation_by_axes([700])   # Bold Italic
    except Exception: pass
    return fnt

# fit the longest line to MAXW to pick the base script size
long_line = "You will forever remain in our hearts."
S = 60
while True:
    if text_w(probe, long_line, font(SCRIPT, S + 2)) <= MAXW and S + 2 <= 200:
        S += 2
    else:
        break
BASE = S
EMPH = int(BASE * 1.35)   # "We love you." — closing line, emphasized

# ---------- portrait ----------
ow = 545
oh = int(ow * oval.height / oval.width)
oval_r = oval.resize((ow, oh), Image.LANCZOS)

# ---------- vertical layout (measure, then size canvas) ----------
top = 95
y = top + oh                      # portrait bottom

gap_name = 40
name_size = 72
y_name = y + gap_name             # top of name
y = y_name + name_size + 8

gap_dates = 22
date_size = 42
y_dates = y + gap_dates           # top of dates
y = y_dates + date_size + 6

gap_rule = 40
y_rule = y + gap_rule
y = y_rule + 38

gap_msg = 58
lines = [
    ("Dear Papa,", BASE),
    ("You will forever remain in our hearts.", BASE),
    ("Rest in Peace.", BASE),
    ("We love you!", EMPH),
]
y_msg = y + gap_msg

# compute heights of message lines
line_steps = []
for txt, sz in lines:
    pre = int(sz * 0.45) if sz == EMPH else 0   # extra breathing room before closing line
    step = int(sz * 1.30)
    line_steps.append((txt, sz, step, pre))

msg_total = sum(s + p for _, _, s, p in line_steps)
H = y_msg + msg_total + 80

# ---------- render ----------
img = Image.new("RGB", (W, H), (255, 255, 255))
d = ImageDraw.Draw(img)

# portrait centered
img.paste(oval_r, ((W - ow) // 2, top), oval_r)

# name — refined, tracked, deprioritized
def draw_tracked(draw, cx, top_y, s, f, fill, track):
    widths = [text_w(draw, ch, f) for ch in s]
    total = sum(widths) + track * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, top_y), ch, font=f, fill=fill)
        x += w + track

name_font = font(SERIF, name_size)
try: name_font.set_variation_by_axes([700])
except Exception: pass
draw_tracked(d, W / 2, y_name, "Dr. TOGBEY Kwamy Maoussi Félix",
             name_font, INK, track=3)

# dates — small, refined, beneath the name
date_font = font(SERIF, date_size)
draw_tracked(d, W / 2, y_dates, "20 November 1948  –  24 May 2026",
             date_font, (122, 122, 126), track=4)

# hairline rule with small gold lozenge centered
cx = W / 2
half = 230
d.line([(cx - half, y_rule), (cx - 26, y_rule)], fill=HAIR, width=2)
d.line([(cx + 26, y_rule), (cx + half, y_rule)], fill=HAIR, width=2)
d.polygon([(cx, y_rule - 9), (cx + 11, y_rule), (cx, y_rule + 9), (cx - 11, y_rule)],
          fill=GOLD)

# message lines, centered
cy = y_msg
for txt, sz, step, pre in line_steps:
    cy += pre
    f = font(SCRIPT, sz)
    if sz == EMPH:
        # small gold flourish dots flanking the emphasized closing line
        lw = text_w(d, txt, f)
        fcx = W / 2
        dot_y = cy + int(sz * 0.42)
        for off in (lw / 2 + 46, -(lw / 2 + 46)):
            d.ellipse([fcx + off - 6, dot_y - 6, fcx + off + 6, dot_y + 6], fill=GOLD)
    # Full-strength colors — the carver needs maximum contrast for the chisel
    msg_color = MSGGOLD if MODE == "gold" else INK
    d.text((W / 2, cy), txt, font=f, fill=msg_color, anchor="ma")
    cy += step

# ---------- floral corner sprigs (vibrant — sage + white rose + dusty rose) ----------
SAGE_DARK    = (96, 116, 86)
SAGE         = (142, 165, 128)
SAGE_LIGHT   = (180, 195, 162)
WHITE_PETAL  = (252, 248, 240)
PETAL_SHADOW = (210, 198, 178)
ROSE_PINK    = (210, 168, 158)
ROSE_PINK_D  = (172, 130, 122)
GOLD_DARK_FL = (158, 121, 56)
GOLD_PALE_FL = (224, 200, 148)

SCALE_FL = 3

def _make_leaf(length, color, edge, variation=0):
    w = max(int(length * (0.50 + variation)), 10)
    h = max(int(length), 16)
    pad = 6
    leaf = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ld = ImageDraw.Draw(leaf)
    ld.ellipse([pad, pad, pad + w, pad + h], fill=color, outline=edge, width=2)
    ld.line([(pad + w / 2, pad + 4), (pad + w / 2, pad + h - 2)], fill=edge, width=1)
    hl = tuple(min(255, int(c * 1.20)) for c in color)
    ld.arc([pad + 1, pad + 1, pad + w - 1, pad + h - 1], 200, 340, fill=hl, width=2)
    return leaf

def _paste_leaf(canvas, cx, cy, length, angle_deg, color=SAGE, edge=SAGE_DARK, var=0):
    leaf = _make_leaf(length, color, edge, var)
    rot = leaf.rotate(-angle_deg + 90, resample=Image.BICUBIC, expand=True)
    canvas.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)

def _make_petal(w, h, fill, edge):
    pad = 4
    p = Image.new("RGBA", (int(w) + pad * 2, int(h) + pad * 2), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p)
    pd.ellipse([pad, pad, pad + w, pad + h], fill=fill, outline=edge, width=2)
    hl = tuple(min(255, int(c * 1.06)) for c in fill[:3])
    pd.arc([pad + 1, pad + 1, pad + w - 1, pad + h - 1], 200, 340, fill=hl, width=1)
    return p

def _paste_petal(canvas, cx, cy, w, h, angle_deg, fill, edge):
    p = _make_petal(w, h, fill, edge)
    rot = p.rotate(-angle_deg + 90, resample=Image.BICUBIC, expand=True)
    canvas.paste(rot, (int(cx - rot.width / 2), int(cy - rot.height / 2)), rot)

def _paste_rose(canvas, cx, cy, size, fill=WHITE_PETAL, edge=PETAL_SHADOW,
                center=ROSE_PINK, center_edge=ROSE_PINK_D):
    for ang in range(0, 360, 60):
        rad = math.radians(ang)
        px = cx + size * 0.60 * math.cos(rad)
        py = cy + size * 0.60 * math.sin(rad)
        _paste_petal(canvas, px, py, size * 0.55, size * 0.80, ang + 90, fill, edge)
    for ang in range(30, 360 + 30, 60):
        rad = math.radians(ang)
        px = cx + size * 0.38 * math.cos(rad)
        py = cy + size * 0.38 * math.sin(rad)
        _paste_petal(canvas, px, py, size * 0.46, size * 0.62, ang + 90, fill, edge)
    inner_fill = tuple(int(c * 0.96) for c in fill)
    for ang in range(0, 360, 72):
        rad = math.radians(ang)
        px = cx + size * 0.20 * math.cos(rad)
        py = cy + size * 0.20 * math.sin(rad)
        _paste_petal(canvas, px, py, size * 0.34, size * 0.44, ang + 90, inner_fill, edge)
    dd = ImageDraw.Draw(canvas)
    bud_fill = tuple(int(c * 0.90) for c in fill)
    dd.ellipse([cx - size * 0.22, cy - size * 0.22, cx + size * 0.22, cy + size * 0.22],
               fill=bud_fill, outline=edge, width=2)
    dd.ellipse([cx - size * 0.14, cy - size * 0.14, cx + size * 0.14, cy + size * 0.14],
               fill=center, outline=center_edge, width=2)
    dd.ellipse([cx - size * 0.06, cy - size * 0.06, cx + size * 0.06, cy + size * 0.06],
               fill=GOLD_PALE_FL)

def _paste_bud(canvas, cx, cy, size, fill=ROSE_PINK, edge=ROSE_PINK_D):
    dd = ImageDraw.Draw(canvas)
    dd.ellipse([cx - size, cy - size, cx + size, cy + size], fill=fill, outline=edge, width=2)
    hl = tuple(min(255, int(c * 1.18)) for c in fill)
    dd.arc([cx - size + 2, cy - size + 2, cx + size - 2, cy + size - 2], 200, 320,
           fill=hl, width=2)

def _stem_curve(start, ang_deg, length, curve=0.10, n=50):
    pts = []
    ang_rad = math.radians(ang_deg)
    perp = ang_rad + math.pi / 2
    for i in range(n):
        u = i / (n - 1)
        offset = curve * length * math.sin(u * math.pi)
        x = start[0] + length * u * math.cos(ang_rad) + offset * math.cos(perp)
        y = start[1] + length * u * math.sin(ang_rad) + offset * math.sin(perp)
        pts.append((x, y))
    return pts

def _draw_stem(canvas, pts, base_width=6):
    dd = ImageDraw.Draw(canvas)
    n = len(pts)
    for i in range(n - 1):
        w_ = int(max(2, base_width - (i / n) * 3))
        dd.line([pts[i], pts[i + 1]], fill=SAGE_DARK, width=w_)

def _floral_corner(canvas, cx, cy, sx, sy):
    # Horizontal branch: arches gently *into* the page interior on every corner.
    # When stem angle flips (sx=-1 → 180°), the perpendicular also flips,
    # so we multiply by sx*sy to keep the curve direction visually consistent.
    pts_h = _stem_curve((cx, cy), 0 if sx > 0 else 180, 380 * SCALE_FL,
                        curve=0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_h, base_width=6 * SCALE_FL)
    for k, (t, length, side, var) in enumerate([(0.13, 64, 1, 0.0), (0.27, 82, -1, 0.05),
                                                 (0.42, 98, 1, -0.05), (0.58, 92, -1, 0.0),
                                                 (0.74, 80, 1, 0.05), (0.90, 58, -1, -0.05)]):
        idx = int(t * (len(pts_h) - 1))
        lx, ly = pts_h[idx]
        nxp = pts_h[min(idx + 1, len(pts_h) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        leaf_ang = stem_ang + side * 65 * sy
        color = SAGE if k % 2 == 0 else SAGE_LIGHT
        _paste_leaf(canvas, lx, ly, length * SCALE_FL, leaf_ang, color=color, var=var)
    # Vertical branch: same logic but with sign flipped (since rotation axis differs)
    pts_v = _stem_curve((cx, cy), 90 if sy > 0 else -90, 290 * SCALE_FL,
                        curve=-0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_v, base_width=6 * SCALE_FL)
    for k, (t, length, side, var) in enumerate([(0.16, 66, -1, 0.05), (0.34, 86, 1, -0.05),
                                                 (0.52, 92, -1, 0.0), (0.72, 78, 1, 0.05),
                                                 (0.90, 56, -1, -0.05)]):
        idx = int(t * (len(pts_v) - 1))
        lx, ly = pts_v[idx]
        nxp = pts_v[min(idx + 1, len(pts_v) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        leaf_ang = stem_ang + side * 65 * sx
        color = SAGE_LIGHT if k % 2 == 0 else SAGE
        _paste_leaf(canvas, lx, ly, length * SCALE_FL, leaf_ang, color=color, var=var)
    _paste_rose(canvas, cx + sx * 28 * SCALE_FL, cy + sy * 28 * SCALE_FL, 54 * SCALE_FL)
    bx, by = pts_h[int(0.42 * len(pts_h))]
    _paste_rose(canvas, bx, by - sy * 12 * SCALE_FL, 38 * SCALE_FL)
    vx, vy = pts_v[int(0.46 * len(pts_v))]
    _paste_rose(canvas, vx + sx * 12 * SCALE_FL, vy, 34 * SCALE_FL,
                fill=ROSE_PINK, edge=ROSE_PINK_D, center=GOLD_DARK_FL,
                center_edge=tuple(int(c * 0.7) for c in GOLD_DARK_FL))
    bx, by = pts_h[int(0.75 * len(pts_h))]
    _paste_bud(canvas, bx + sx * 6 * SCALE_FL, by + sy * -20 * SCALE_FL, 14 * SCALE_FL)
    bx, by = pts_v[int(0.72 * len(pts_v))]
    _paste_bud(canvas, bx + sx * -12 * SCALE_FL, by + sy * 4 * SCALE_FL, 14 * SCALE_FL)
    bx, by = pts_h[int(0.92 * len(pts_h))]
    _paste_bud(canvas, bx, by - sy * 14 * SCALE_FL, 11 * SCALE_FL,
               fill=WHITE_PETAL, edge=PETAL_SHADOW)

# Build the floral layer at 3x and composite onto the memorial
W_img, H_img = img.size
inset_fl = 90
fl_layer = Image.new("RGBA", (W_img * SCALE_FL, H_img * SCALE_FL), (0, 0, 0, 0))
for (cx_, cy_, sx_, sy_) in [
    (inset_fl,         inset_fl,          1,  1),
    (W_img - inset_fl, inset_fl,         -1,  1),
    (inset_fl,         H_img - inset_fl,  1, -1),
    (W_img - inset_fl, H_img - inset_fl, -1, -1),
]:
    _floral_corner(fl_layer, cx_ * SCALE_FL, cy_ * SCALE_FL, sx_, sy_)
fl_layer = fl_layer.resize((W_img, H_img), Image.LANCZOS)
img.paste(fl_layer, (0, 0), fl_layer)

out = "memorial_redesign_en.png" if MODE == "gold" else "memorial_redesign_black_en.png"
img.save(out, dpi=(300, 300))
print("size", img.size, "mode", MODE, "->", out)
