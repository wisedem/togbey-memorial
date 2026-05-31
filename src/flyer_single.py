from PIL import Image, ImageDraw, ImageFont
import math

# Portrait format for WhatsApp — matches our previous single-page proportions
W, H = 1600, 2530

IVORY       = (251, 247, 238)
GOLD_DARK   = (158, 121, 56)
GOLD        = (196, 158, 86)
GOLD_PALE   = (224, 200, 148)
INK         = (44, 42, 42)
INK_SOFT    = (66, 64, 64)
SUBTLE      = (128, 124, 124)
SUBTLE_DARK = (95, 92, 92)

SERIF  = "fonts/EBGaramond.ttf"
ITAL   = "fonts/EBGaramond-Italic.ttf"
SCRIPT = "fonts/PinyonScript-Regular.ttf"

def f(s):  return ImageFont.truetype(SERIF, s)
def fi(s): return ImageFont.truetype(ITAL, s)
def sc(s): return ImageFont.truetype(SCRIPT, s)
def fs(s):
    fnt = ImageFont.truetype(SERIF, s)
    try: fnt.set_variation_by_axes([600])
    except Exception: pass
    return fnt
def fb(s):
    fnt = ImageFont.truetype(SERIF, s)
    try: fnt.set_variation_by_axes([700])
    except Exception: pass
    return fnt

img = Image.new("RGB", (W, H), IVORY)
d = ImageDraw.Draw(img)

# Outer gold double-rule frame
m = 60
d.rectangle((m, m, W - m, H - m), outline=GOLD_DARK, width=2)
d.rectangle((m + 12, m + 12, W - m - 12, H - m - 12), outline=GOLD_PALE, width=1)

# ---- floral corner sprigs (vibrant) ----
SAGE_DARK    = (96, 116, 86)
SAGE         = (142, 165, 128)
SAGE_LIGHT   = (180, 195, 162)
WHITE_PETAL  = (252, 248, 240)
PETAL_SHADOW = (210, 198, 178)
ROSE_PINK    = (210, 168, 158)
ROSE_PINK_D  = (172, 130, 122)

SCALE = 3

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
               fill=GOLD_PALE)

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
        w = int(max(2, base_width - (i / n) * 3))
        dd.line([pts[i], pts[i + 1]], fill=SAGE_DARK, width=w)

def _floral_corner(canvas, cx, cy, sx, sy):
    pts_h = _stem_curve((cx, cy), 0 if sx > 0 else 180, 380 * SCALE,
                        curve=0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_h, base_width=6 * SCALE)
    for k, (t, length, side, var) in enumerate([(0.13, 64, 1, 0.0), (0.27, 82, -1, 0.05),
                                                 (0.42, 98, 1, -0.05), (0.58, 92, -1, 0.0),
                                                 (0.74, 80, 1, 0.05), (0.90, 58, -1, -0.05)]):
        idx = int(t * (len(pts_h) - 1))
        lx, ly = pts_h[idx]
        nxp = pts_h[min(idx + 1, len(pts_h) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        leaf_ang = stem_ang + side * 65 * sy
        color = SAGE if k % 2 == 0 else SAGE_LIGHT
        _paste_leaf(canvas, lx, ly, length * SCALE, leaf_ang, color=color, var=var)
    pts_v = _stem_curve((cx, cy), 90 if sy > 0 else -90, 290 * SCALE,
                        curve=-0.10 * sx * sy, n=50)
    _draw_stem(canvas, pts_v, base_width=6 * SCALE)
    for k, (t, length, side, var) in enumerate([(0.16, 66, -1, 0.05), (0.34, 86, 1, -0.05),
                                                 (0.52, 92, -1, 0.0), (0.72, 78, 1, 0.05),
                                                 (0.90, 56, -1, -0.05)]):
        idx = int(t * (len(pts_v) - 1))
        lx, ly = pts_v[idx]
        nxp = pts_v[min(idx + 1, len(pts_v) - 1)]
        stem_ang = math.degrees(math.atan2(nxp[1] - ly, nxp[0] - lx))
        leaf_ang = stem_ang + side * 65 * sx
        color = SAGE_LIGHT if k % 2 == 0 else SAGE
        _paste_leaf(canvas, lx, ly, length * SCALE, leaf_ang, color=color, var=var)
    _paste_rose(canvas, cx + sx * 28 * SCALE, cy + sy * 28 * SCALE, 54 * SCALE)
    bx, by = pts_h[int(0.42 * len(pts_h))]
    _paste_rose(canvas, bx, by - sy * 12 * SCALE, 38 * SCALE)
    vx, vy = pts_v[int(0.46 * len(pts_v))]
    _paste_rose(canvas, vx + sx * 12 * SCALE, vy, 34 * SCALE,
                fill=ROSE_PINK, edge=ROSE_PINK_D, center=GOLD_DARK,
                center_edge=tuple(int(c * 0.7) for c in GOLD_DARK))
    bx, by = pts_h[int(0.75 * len(pts_h))]
    _paste_bud(canvas, bx + sx * 6 * SCALE, by + sy * -20 * SCALE, 14 * SCALE)
    bx, by = pts_v[int(0.72 * len(pts_v))]
    _paste_bud(canvas, bx + sx * -12 * SCALE, by + sy * 4 * SCALE, 14 * SCALE)
    bx, by = pts_h[int(0.92 * len(pts_h))]
    _paste_bud(canvas, bx, by - sy * 14 * SCALE, 11 * SCALE,
               fill=WHITE_PETAL, edge=PETAL_SHADOW)

def make_sprig_layer(W_, H_, anchors):
    layer = Image.new("RGBA", (W_ * SCALE, H_ * SCALE), (0, 0, 0, 0))
    for (cx, cy, sx, sy) in anchors:
        _floral_corner(layer, cx * SCALE, cy * SCALE, sx, sy)
    return layer.resize((W_, H_), Image.LANCZOS)

inset = m + 30
sprig_layer = make_sprig_layer(W, H, [
    (inset,     inset,      1,  1),
    (W - inset, inset,     -1,  1),
    (inset,     H - inset,  1, -1),
    (W - inset, H - inset, -1, -1),
])
img.paste(sprig_layer, (0, 0), sprig_layer)

# helpers
def tw(draw, s, fn):
    b = draw.textbbox((0, 0), s, font=fn)
    return b[2] - b[0]

def tracked(draw, cx, top, s, fn, fill, track):
    widths = [tw(draw, ch, fn) for ch in s]
    total = sum(widths) + track * (len(s) - 1)
    x = cx - total / 2
    for ch, w in zip(s, widths):
        draw.text((x, top), ch, font=fn, fill=fill)
        x += w + track

def divider(cx, y, half=200, fill=GOLD_DARK):
    d.line([(cx - half, y), (cx - 26, y)], fill=fill, width=2)
    d.line([(cx + 26, y), (cx + half, y)], fill=fill, width=2)
    d.polygon([(cx, y - 9), (cx + 11, y), (cx, y + 9), (cx - 11, y)], fill=fill)

def cross(cx, cy, h=58, thick=5, color=GOLD_DARK):
    w = int(h * 0.52)
    hy = cy - h // 2 + int(h * 0.32)
    d.rectangle((cx - thick // 2, cy - h // 2, cx + thick // 2 + 1, cy + h // 2), fill=color)
    d.rectangle((cx - w // 2, hy - thick // 2, cx + w // 2, hy + thick // 2 + 1), fill=color)
    d.rectangle((cx - w // 2 + 2, hy - thick // 2 + 1,
                 cx + w // 2 - 2, hy - thick // 2 + 2), fill=GOLD_PALE)

def wrap(text, fn, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(d, t, fn) <= max_w:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w_
    if cur: lines.append(cur)
    return lines

CX = W // 2
y = m + 60

# ---- tagline (italic) ----
d.text((CX, y), "En Mémoire de Notre Très Cher et Regretté",
       font=fi(42), fill=INK_SOFT, anchor="ma")
y += 70

# ---- portrait (vignette into ivory, no frame) ----
rect = Image.open("crop_clean_v7.png").convert("RGB")
ph = 680
pw = int(ph * rect.width / rect.height)
rect_r = rect.resize((pw, ph), Image.LANCZOS).convert("RGBA")
alpha = Image.new("L", (pw, ph), 255)
adraw = ImageDraw.Draw(alpha)
fade_h = int(ph * 0.22)
for j in range(fade_h):
    t = j / fade_h
    eased = 0.5 * (1 + math.cos(math.pi * t))
    a = int(255 * eased)
    adraw.line([(0, ph - fade_h + j), (pw, ph - fade_h + j)], fill=a)
rect_r.putalpha(alpha)
img.paste(rect_r, (CX - pw // 2, y), rect_r)
y += ph + 12

# ---- name + dates ----
tracked(d, CX, y, "Dr. TOGBEY Kwamy Maoussi Félix", fb(50), INK, track=4)
y += 72
dates_text = "Rappelé à Dieu le 24 mai 2026 au CHU Sylvanus Olympio dans sa 78ᵉ année."
df = fi(34)
for ln in wrap(dates_text, df, 1300):
    d.text((CX, y), ln, font=df, fill=SUBTLE, anchor="ma")
    y += 46
y += 20

# ---- divider ----
divider(CX, y, half=200)
y += 48

# ---- tribute pair (echoes the plaque) ----
d.text((CX, y), "Tu resteras à jamais dans nos cœurs.",
       font=sc(50), fill=INK_SOFT, anchor="ma")
y += 72
d.text((CX, y), "Repose en paix.", font=sc(64), fill=GOLD_DARK, anchor="ma")
y += 110

# ---- cross (introduces religious programme) ----
cross(CX, y + 30)
y += 80

# ---- Programme de Salutation ----
d.text((CX, y), "Programme des Salutations",
       font=sc(60), fill=GOLD_DARK, anchor="ma")
y += 80

intro = "Les salutations de compassion seront reçues de 16h00 à 20h00 :"
for line in wrap(intro, f(30), 1300):
    d.text((CX, y), line, font=f(30), fill=INK_SOFT, anchor="ma")
    y += 44
y += 10

d.text((CX, y), "Tous les jeudis, vendredis et samedis",
       font=f(32), fill=INK_SOFT, anchor="ma")
y += 46
d.text((CX, y), "du 28 mai au 20 juin 2026",
       font=f(32), fill=INK_SOFT, anchor="ma")
y += 58
d.text((CX, y), "Du lundi 22 au mercredi 24 juin 2026",
       font=f(32), fill=INK_SOFT, anchor="ma")
y += 64

tracked(d, CX, y, "LIEU", f(24), SUBTLE, track=12)
y += 40
d.text((CX, y), "Maison TOGBEY Félix",
       font=fb(36), fill=INK, anchor="ma")
y += 48
d.text((CX, y), "Quartier Tokoin Kodomé · 3ème von à droite · en face du marché",
       font=f(26), fill=SUBTLE_DARK, anchor="ma")
y += 60

# ---- divider between programmes ----
divider(CX, y, half=170)
y += 46

# ---- Programme des Obsèques ----
d.text((CX, y), "Programme des Obsèques",
       font=sc(60), fill=GOLD_DARK, anchor="ma")
y += 80

events_by_day = [
    ("Vendredi 26 juin 2026", [
        ("18h30",
         "Veillée de prières et de chants à l'**Église Baptiste "
         "Biblique de Tokoin-Solidarité**, suivie de l'exposition du corps "
         "**au domicile du défunt**."),
    ]),
    ("Samedi 27 juin 2026", [
        ("07h00",
         "Levée du corps, suivie de la messe d'enterrement et de "
         "remerciements à la même église."),
        ("13h00",
         "Enterrement à **Agomé-Glozou** (Bas-Mono)."),
    ]),
]
SEMI = "fonts/EBGaramond.ttf"
def fb(s):
    fnt = ImageFont.truetype(SEMI, s)
    try: fnt.set_variation_by_axes([700])
    except Exception: pass
    return fnt

def tokenize_bold(s):
    parts = s.split("**")
    return [(t, i % 2 == 1) for i, t in enumerate(parts) if t]

def render_mixed_line(draw, cx, y, tokens, regular_font, bold_font, regular_color, bold_color):
    widths = []
    for txt, is_bold in tokens:
        f_ = bold_font if is_bold else regular_font
        widths.append(tw(draw, txt, f_))
    total = sum(widths)
    x = cx - total / 2
    for (txt, is_bold), w_ in zip(tokens, widths):
        f_ = bold_font if is_bold else regular_font
        col = bold_color if is_bold else regular_color
        draw.text((x, y), txt, font=f_, fill=col)
        x += w_

def wrap_mixed(tokens, regular_font, bold_font, max_w, draw):
    words = []
    for txt, is_bold in tokens:
        for i, w_ in enumerate(txt.split(" ")):
            if i > 0:
                words.append((" ", is_bold))
            if w_:
                words.append((w_, is_bold))
    lines = []
    cur = []
    cur_w = 0
    for w_, is_bold in words:
        f_ = bold_font if is_bold else regular_font
        ww = tw(draw, w_, f_)
        if cur and cur_w + ww > max_w and w_ != " ":
            lines.append(cur)
            cur = []
            cur_w = 0
            if w_ == " ":
                continue
        cur.append((w_, is_bold))
        cur_w += ww
    if cur:
        lines.append(cur)
    cleaned = []
    for line in lines:
        while line and line[0][0] == " ":
            line = line[1:]
        while line and line[-1][0] == " ":
            line = line[:-1]
        if line:
            cleaned.append(line)
    return cleaned

COL_W_ = 1300
BODY_SIZE_ = 34

for di, (date, events) in enumerate(events_by_day):
    if di > 0:
        y += 28
    d.text((CX, y), date, font=fs(42 if 1300 < 1200 else 46), fill=GOLD_DARK, anchor="ma")
    y += 64 if 1300 < 1200 else 68
    for ei, (time_str, sentence) in enumerate(events):
        if ei > 0:
            y += 22
        sent_tokens = tokenize_bold(sentence)
        prefix_tokens = [(time_str + " : ", True)]
        all_tokens = prefix_tokens + sent_tokens
        rf, bf = f(BODY_SIZE_), fb(BODY_SIZE_)
        wrapped = wrap_mixed(all_tokens, rf, bf, COL_W_, d)
        for line in wrapped:
            render_mixed_line(d, CX, y, line, rf, bf, INK_SOFT, INK)
            y += 50
        y += 4

# ---- closing ----
y += 14
divider(CX, y, half=140)
y += 50
d.text((CX, y), "We love you!", font=sc(72), fill=GOLD_DARK, anchor="ma")

# ---- QR code (bottom-right corner) linking to this flyer online ----
QR_URL = "https://drtogbeyfelix.com/"
try:
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2)
    qr.add_data(QR_URL)
    qr.make(fit=True)
    modules = qr.modules_count + 2 * qr.border          # total modules incl. quiet zone
    box = max(1, 176 // modules)                         # integer px/module → crisp grid
    qr_img = qr.make_image(fill_color=INK, back_color=IVORY).convert("RGB")
    qr_img = qr_img.resize((modules * box, modules * box), Image.NEAREST)
    qs = qr_img.width
    pad = 26
    qx = W - m - 12 - pad - qs                           # inside the inner gold frame
    qy = H - m - 12 - pad - qs
    # ivory card masks the floral corner so the QR reads as an intentional badge
    card = 14
    d.rounded_rectangle((qx - card, qy - card, qx + qs + card, qy + qs + card),
                        radius=10, fill=IVORY, outline=GOLD_DARK, width=2)
    img.paste(qr_img, (qx, qy))
except Exception as e:
    print("QR skipped:", e)

img.save("flyer_single.png", dpi=(300, 300))
print("single", img.size, "final y", y)
