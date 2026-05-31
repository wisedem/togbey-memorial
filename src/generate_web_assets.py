"""Generate web assets for the memorial site, reusing the established
floral engine and palette so the website matches the print materials.

Outputs (into ../togbey-memorial/img/):
  oval.png          clean gold-framed oval portrait, transparent outside the ellipse
  floral-corner.png single transparent eucalyptus+rose corner sprig (top-left orientation)
  share.png         1200x630 WhatsApp / Open Graph share card
"""
from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = os.path.join(os.path.dirname(__file__), "..", "img")
os.makedirs(OUT, exist_ok=True)

# ---------- palette (from README) ----------
IVORY        = (251, 247, 238)
GOLD_DARK    = (158, 121, 56)
GOLD         = (196, 158, 86)
GOLD_PALE    = (224, 200, 148)
INK          = (44, 42, 42)
INK_SOFT     = (66, 64, 64)
SUBTLE       = (128, 124, 124)
SAGE_DARK    = (96, 116, 86)
SAGE         = (142, 165, 128)
SAGE_LIGHT   = (180, 195, 162)
WHITE_PETAL  = (252, 248, 240)
PETAL_SHADOW = (210, 198, 178)
ROSE_PINK    = (210, 168, 158)
ROSE_PINK_D  = (172, 130, 122)

SERIF  = os.path.join(os.path.dirname(__file__), "fonts", "EBGaramond.ttf")
ITAL   = os.path.join(os.path.dirname(__file__), "fonts", "EBGaramond-Italic.ttf")
SCRIPT = os.path.join(os.path.dirname(__file__), "fonts", "PinyonScript-Regular.ttf")

SCALE = 3

# ================= floral engine (lifted from flyer_single.py) =================
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
        _paste_petal(canvas, cx + size * 0.60 * math.cos(rad), cy + size * 0.60 * math.sin(rad),
                     size * 0.55, size * 0.80, ang + 90, fill, edge)
    for ang in range(30, 360 + 30, 60):
        rad = math.radians(ang)
        _paste_petal(canvas, cx + size * 0.38 * math.cos(rad), cy + size * 0.38 * math.sin(rad),
                     size * 0.46, size * 0.62, ang + 90, fill, edge)
    inner_fill = tuple(int(c * 0.96) for c in fill)
    for ang in range(0, 360, 72):
        rad = math.radians(ang)
        _paste_petal(canvas, cx + size * 0.20 * math.cos(rad), cy + size * 0.20 * math.sin(rad),
                     size * 0.34, size * 0.44, ang + 90, inner_fill, edge)
    dd = ImageDraw.Draw(canvas)
    bud_fill = tuple(int(c * 0.90) for c in fill)
    dd.ellipse([cx - size * 0.22, cy - size * 0.22, cx + size * 0.22, cy + size * 0.22],
               fill=bud_fill, outline=edge, width=2)
    dd.ellipse([cx - size * 0.14, cy - size * 0.14, cx + size * 0.14, cy + size * 0.14],
               fill=center, outline=center_edge, width=2)
    dd.ellipse([cx - size * 0.06, cy - size * 0.06, cx + size * 0.06, cy + size * 0.06],
               fill=GOLD_PALE)

def _paste_bud(canvas, cx, cy, size, fill=ROSE_PINK, edge=ROSE_PINK_D):
    dd = ImageDraw.Draw(canvas)
    dd.ellipse([cx - size, cy - size, cx + size, cy + size], fill=fill, outline=edge, width=2)
    hl = tuple(min(255, int(c * 1.18)) for c in fill)
    dd.arc([cx - size + 2, cy - size + 2, cx + size - 2, cy + size - 2], 200, 320, fill=hl, width=2)

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
        w = int(max(2, base_width - (i / n) * 3))
        dd.line([pts[i], pts[i + 1]], fill=SAGE_DARK, width=w)

def _floral_corner(canvas, cx, cy, sx, sy):
    pts_h = _stem_curve((cx, cy), 0 if sx > 0 else 180, 380 * SCALE, curve=0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_h, base_width=6 * SCALE)
    for k, (t, length, side, var) in enumerate([(0.13, 64, 1, 0.0), (0.27, 82, -1, 0.05),
                                                 (0.42, 98, 1, -0.05), (0.58, 92, -1, 0.0),
                                                 (0.74, 80, 1, 0.05), (0.90, 58, -1, -0.05)]):
        idx = int(t * (len(pts_h) - 1)); lx, ly = pts_h[idx]
        nxp = pts_h[min(idx + 1, len(pts_h) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        color = SAGE if k % 2 == 0 else SAGE_LIGHT
        _paste_leaf(canvas, lx, ly, length * SCALE, stem_ang + side * 65 * sy, color=color, var=var)
    pts_v = _stem_curve((cx, cy), 90 if sy > 0 else -90, 290 * SCALE, curve=-0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_v, base_width=6 * SCALE)
    for k, (t, length, side, var) in enumerate([(0.16, 66, -1, 0.05), (0.34, 86, 1, -0.05),
                                                 (0.52, 92, -1, 0.0), (0.72, 78, 1, 0.05),
                                                 (0.90, 56, -1, -0.05)]):
        idx = int(t * (len(pts_v) - 1)); lx, ly = pts_v[idx]
        nxp = pts_v[min(idx + 1, len(pts_v) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        color = SAGE_LIGHT if k % 2 == 0 else SAGE
        _paste_leaf(canvas, lx, ly, length * SCALE, stem_ang + side * 65 * sx, color=color, var=var)
    _paste_rose(canvas, cx + sx * 28 * SCALE, cy + sy * 28 * SCALE, 54 * SCALE)
    bx, by = pts_h[int(0.42 * len(pts_h))]; _paste_rose(canvas, bx, by - sy * 12 * SCALE, 38 * SCALE)
    vx, vy = pts_v[int(0.46 * len(pts_v))]
    _paste_rose(canvas, vx + sx * 12 * SCALE, vy, 34 * SCALE,
                fill=ROSE_PINK, edge=ROSE_PINK_D, center=GOLD_DARK,
                center_edge=tuple(int(c * 0.7) for c in GOLD_DARK))
    bx, by = pts_h[int(0.75 * len(pts_h))]; _paste_bud(canvas, bx + sx * 6 * SCALE, by + sy * -20 * SCALE, 14 * SCALE)
    bx, by = pts_v[int(0.72 * len(pts_v))]; _paste_bud(canvas, bx + sx * -12 * SCALE, by + sy * 4 * SCALE, 14 * SCALE)
    bx, by = pts_h[int(0.92 * len(pts_h))]; _paste_bud(canvas, bx, by - sy * 14 * SCALE, 11 * SCALE,
                                                        fill=WHITE_PETAL, edge=PETAL_SHADOW)

# ---------------- 1. clean transparent oval portrait ----------------
oval = Image.open("oval.png").convert("RGBA")
ow, oh = oval.size
mask = Image.new("L", (ow, oh), 0)
ImageDraw.Draw(mask).ellipse([2, 2, ow - 3, oh - 3], fill=255)
oval.putalpha(mask)
oval.save(os.path.join(OUT, "oval.png"))
print("oval.png", oval.size)

# ---------------- 2. transparent corner sprig (top-left orientation) ----------------
FW, FH = 640, 560
layer = Image.new("RGBA", (FW * SCALE, FH * SCALE), (0, 0, 0, 0))
_floral_corner(layer, 120 * SCALE, 120 * SCALE, 1, 1)
layer = layer.resize((FW, FH), Image.LANCZOS)
bbox = layer.getbbox()
pad = 6
bbox = (max(0, bbox[0] - pad), max(0, bbox[1] - pad),
        min(FW, bbox[2] + pad), min(FH, bbox[3] + pad))
layer.crop(bbox).save(os.path.join(OUT, "floral-corner.png"))
print("floral-corner.png", layer.crop(bbox).size)

# ---------------- 3. WhatsApp / Open Graph share card (1200x630) ----------------
SW, SH = 1200, 630
card = Image.new("RGB", (SW, SH), IVORY)
cd = ImageDraw.Draw(card)
# double gold frame
mm = 26
cd.rectangle((mm, mm, SW - mm, SH - mm), outline=GOLD_DARK, width=2)
cd.rectangle((mm + 10, mm + 10, SW - mm - 10, SH - mm - 10), outline=GOLD_PALE, width=1)
# small floral sprig in the two left corners
sl = Image.new("RGBA", (FW * SCALE, FH * SCALE), (0, 0, 0, 0))
_floral_corner(sl, 120 * SCALE, 120 * SCALE, 1, 1)
sl = sl.resize((int(FW * 0.7), int(FH * 0.7)), Image.LANCZOS)
card.paste(sl, (mm - 30, mm - 30), sl)
sl2 = sl.transpose(Image.FLIP_TOP_BOTTOM)
card.paste(sl2, (mm - 30, SH - mm - sl2.height + 30), sl2)
# oval portrait on the left
ph = 430
pw = int(ph * oval.width / oval.height)
ov = oval.resize((pw, ph), Image.LANCZOS)
ox = 150
oy = (SH - ph) // 2
card.paste(ov, (ox, oy), ov)

def fnt(path, size, axis=None):
    fo = ImageFont.truetype(path, size)
    if axis is not None:
        try: fo.set_variation_by_axes([axis])
        except Exception: pass
    return fo

def center_text(draw, cx, y, text, font, fill, anchor="mm"):
    draw.text((cx, y), text, font=font, fill=fill, anchor=anchor)

# right-side text block
tx = ox + pw + 90
right_w = SW - tx - mm - 30
tcx = tx + right_w // 2
cd.text((tcx, 215), "En Mémoire de Notre Très Cher et Regretté",
        font=fnt(ITAL, 26), fill=INK_SOFT, anchor="mm")
cd.text((tcx, 285), "Dr. TOGBEY", font=fnt(SERIF, 58, 700), fill=INK, anchor="mm")
cd.text((tcx, 343), "Kwamy Maoussi Félix", font=fnt(SERIF, 46, 700), fill=INK, anchor="mm")
cd.text((tcx, 400), "1948  –  2026", font=fnt(SERIF, 34, 600), fill=GOLD_DARK, anchor="mm")
cd.text((tcx, 455), "Repose en paix.", font=fnt(SCRIPT, 48), fill=GOLD_DARK, anchor="mm")
card.save(os.path.join(OUT, "share.png"))
print("share.png", card.size)
