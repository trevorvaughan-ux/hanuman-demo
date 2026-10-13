"""Pose-parametrised bold cards on top of bold_base (Triangle v2 look)."""
import math, random
from PIL import Image, ImageDraw, ImageFilter
from bold_base import *
import bold_base as BB
from i18n import tr, you_did

def fit_font(kind, var, text, max_w, size):
    while size > 30:
        f = font(kind, size, var)
        if f.getlength(text) <= max_w: return f
        size -= 4
    return font(kind, size, var)

def intro_card(lt, title, badge=None):
    title = tr(title); badge = tr(badge)
    im = BG.copy(); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    TFp = fit_font('p', 'Bold', title, 1700, 160)
    total_w = TFp.getlength(title); x = W / 2 - total_w / 2
    for i, ch in enumerate(title):
        w = TFp.getlength(title[:i + 1]) - TFp.getlength(title[:i])
        tt = lt - 0.15 - i * 0.06; s = spring(tt)
        if tt > 0 and ch != ' ':
            d.text((x + w / 2, 520 + (1 - s) * -420), ch, font=TFp, fill=TEAL, anchor='ms')
        x += w
    tri_icon(d, W / 2, 250, 70, ease(clamp((lt - 1.2) / 0.9)), 10)
    if lt > 1.5:
        s = spring((lt - 1.5) * 1.2); fs = max(8, int(70 * s))
        d.text((W / 2, 640), tr('with Hani'), font=font('d', fs, 'Bold'), fill=CHAR, anchor='mm')
    im.alpha_composite(lay)
    if badge and lt > 1.9:
        s = spring((lt - 1.9) * 1.3); bf = font('d', 46, 'Bold'); tw = bf.getlength(badge)
        bw, bh = int(tw + 70), 84
        b = Image.new('RGBA', (bw + 40, bh + 40), (0, 0, 0, 0)); db = ImageDraw.Draw(b)
        db.rounded_rectangle([20, 26, 20 + bw, 26 + bh], 42, fill=(0, 0, 0, 50))
        b = b.filter(ImageFilter.GaussianBlur(5)); db = ImageDraw.Draw(b)
        db.rounded_rectangle([20, 20, 20 + bw, 20 + bh], 42, fill=GOLD + (255,), outline=(255, 255, 255, 255), width=5)
        db.text((20 + bw / 2, 20 + bh / 2 + 2), badge, font=bf, fill=(255, 255, 255), anchor='mm')
        sc = max(0.05, s); b = b.resize((max(2, int(b.width * sc)), max(2, int(b.height * sc))), Image.LANCZOS).rotate(-6 * s, expand=True, resample=Image.BICUBIC)
        im.alpha_composite(b, (int(W / 2 + total_w / 2 - b.width * 0.55), int(330 - b.height / 2)))
    if lt > 2.1:
        q = lt - 2.1; r2 = random.Random(11)
        for j in range(14):
            ang = r2.uniform(0, 6.28); dist = 60 + 260 * ease(q / 1.2) * r2.uniform(.4, 1)
            sp = SPARK[r2.choice([10, 16, 24])]
            paste(im, sp, (W / 2 + dist * math.cos(ang) - sp.width / 2, 260 + dist * 0.6 * math.sin(ang) - sp.height / 2), clamp(1 - q / 1.4))
    fireflies(im, lt + 100, 0.8)
    return im

# ------------------------------------------------ fact illustrations (drawn 2x then downsampled)
def _ill_canvas(): return Image.new('RGBA', (2000, 900), (0, 0, 0, 0))
def ill_dog(prog, lt):
    c = _ill_canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    stretch = 0.5 + 0.5 * math.sin(lt * 2.0)
    ox, oy = 1000, 560
    brown = (196, 132, 80); dk = (150, 95, 55)
    # front legs stretched forward, bottom up
    d.line([(ox - 120, oy - 40), (ox - 330 - 40 * stretch, oy + 160)], fill=dk, width=60)
    d.line([(ox + 200, oy - 150), (ox + 230, oy + 160)], fill=dk, width=62)
    d.line([(ox - 150, oy - 30), (ox + 210, oy - 170)], fill=brown, width=170)          # body
    d.ellipse([ox - 470 - 40 * stretch, oy - 120, ox - 230 - 40 * stretch, oy + 90], fill=brown)    # head low
    d.ellipse([ox - 520 - 40 * stretch, oy - 30, ox - 400 - 40 * stretch, oy + 50], fill=(230, 190, 150))  # snout
    d.ellipse([ox - 520 - 40 * stretch, oy - 10, ox - 490 - 40 * stretch, oy + 16], fill=(60, 50, 45))
    d.ellipse([ox - 330 - 40 * stretch, oy - 120, ox - 250 - 40 * stretch, oy + 40], fill=dk)        # ear
    d.ellipse([ox - 400 - 40 * stretch, oy - 60, ox - 370 - 40 * stretch, oy - 30], fill=(40, 40, 40))
    d.line([(ox - 380 - 40 * stretch, oy + 30), (ox - 420 - 40 * stretch, oy + 40)], fill=(60, 50, 45), width=8)
    wag = math.sin(lt * 9) * 40
    d.line([(ox + 260, oy - 200), (ox + 360, oy - 330 + wag)], fill=brown, width=40)          # wagging tail
    for x in (ox - 370 - 40 * stretch, ox - 290 - 40 * stretch, ox + 200, ox + 260):
        d.ellipse([x - 45, oy + 140, x + 45, oy + 185], fill=dk)
    d.line([(200, oy + 190), (1800, oy + 190)], fill=(120, 175, 190), width=10)
    c.putalpha(c.getchannel('A').point(lambda v: int(v * k)))
    return c.resize((1000, 450), Image.LANCZOS)
def ill_sponge(prog, lt):
    c = _ill_canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    tw = 0.5 + 0.5 * math.sin(lt * 2.2)           # wringing twist amount
    cx, cy = 1000, 420
    # sponge as two halves twisting in opposite directions
    for side in (-1, 1):
        a = side * (0.15 + 0.35 * tw)
        pts = []
        for (x, y) in ((-260, -150), (0, -150), (0, 150), (-260, 150)):
            x2 = x * side; ca, sa = math.cos(a), math.sin(a)
            pts.append((cx + x2 * ca - y * sa * 0.35, cy + x2 * sa * 0.35 + y * ca))
        d.polygon(pts, fill=(250, 214, 92), outline=(205, 160, 40))
        for j in range(9):
            px = cx + side * (40 + (j % 3) * 70) ; py = cy - 90 + (j // 3) * 80
            d.ellipse([px - 14, py - 10, px + 14, py + 10], fill=(222, 178, 60))
    # hands
    for side in (-1, 1):
        d.ellipse([cx + side * 300 - 70, cy - 110, cx + side * 300 + 70, cy + 110], fill=(31, 138, 138))
        d.ellipse([cx + side * 300 - 40, cy - 70, cx + side * 300 + 40, cy + 70], fill=(253, 248, 240))
    # droplets
    r = random.Random(4)
    for j in range(10):
        ph = (lt * 0.9 + j / 10) % 1
        x = cx + r.uniform(-200, 200); y = cy + 170 + ph * 280
        a = int(255 * (1 - ph) * tw)
        d.ellipse([x - 16, y - 22, x + 16, y + 22], fill=(110, 185, 225, a))
    c.putalpha(c.getchannel('A').point(lambda v: int(v * k)))
    return c.resize((1000, 450), Image.LANCZOS)
def ill_bridge(prog, lt):
    c = Image.new('RGBA', (1000, 450), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    x0, x1, yd, yt, n = 100, 900, 300, 120, 6; pw = (x1 - x0) / n
    d.rectangle([x0 - 50, yd, x1 + 50, yd + 22], fill=TEAL2)
    m = int(prog * n * 1.0001)
    for i in range(min(m, n)):
        a, b2, cc = (x0 + i * pw, yd), (x0 + (i + 0.5) * pw, yt), (x0 + (i + 1) * pw, yd)
        d.polygon([a, b2, cc], fill=(255, 226, 170)); d.line([a, b2, cc], fill=GOLD, width=9)
    d.line([(20, yd + 120), (980, yd + 120)], fill=(120, 175, 190), width=6)
    return c
def ill_warrior(prog, lt):
    """rising sun behind a teal Warrior 2 figure with a glowing fingertip beam (locked palette)."""
    c = _ill_canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    cx, gy = 1000, 760
    sun_r = 230 + 12 * math.sin(lt * 2.0)
    for j in range(16):   # rays
        a = lt * 0.3 + j * math.pi / 8; r0, r1 = sun_r + 30, sun_r + 150 + (25 if j % 2 else 0)
        w = 0.07
        d.polygon([(cx + r0 * math.cos(a - w), 470 + r0 * math.sin(a - w)), (cx + r1 * math.cos(a), 470 + r1 * math.sin(a)),
                   (cx + r0 * math.cos(a + w), 470 + r0 * math.sin(a + w))], fill=(250, 200, 90, 200 if j % 2 else 140))
    d.ellipse([cx - sun_r, 470 - sun_r, cx + sun_r, 470 + sun_r], fill=(255, 205, 120, 255))
    d.ellipse([cx - sun_r * 0.8, 470 - sun_r * 0.8, cx + sun_r * 0.8, 470 + sun_r * 0.8], fill=(255, 236, 190, 255))
    teal = (19, 107, 107); wv = 46
    hip = (cx, 520); sh = (cx, 330)
    d.line([sh, hip], fill=teal, width=78)                                           # torso
    d.line([hip, (cx + 200, 560), (cx + 210, gy)], fill=teal, width=wv, joint='curve')   # bent front leg
    d.line([hip, (cx - 260, gy)], fill=teal, width=wv)                                  # straight back leg
    d.line([(cx + 210, gy), (cx + 290, gy)], fill=teal, width=34); d.line([(cx - 260, gy), (cx - 320, gy - 10)], fill=teal, width=34)
    d.line([(cx - 470, 335), (cx + 470, 335)], fill=(255, 205, 120, 160), width=60)    # beam glow
    d.line([(cx - 440, 335), (cx + 440, 335)], fill=teal, width=wv)                     # arms
    d.line([(cx - 520, 335), (cx + 520, 335)], fill=(255, 245, 220, 230), width=10)     # beam core
    d.line([(cx, 300), (cx + 30, 250)], fill=teal, width=40); d.ellipse([cx - 5, 150, cx + 125, 268], fill=teal)   # head, gazing at the front hand
    d.ellipse([cx - 60, gy + 30, cx + 60, gy + 60], fill=(0, 0, 0, 0))
    d.line([(200, gy + 40), (1800, gy + 40)], fill=(217, 154, 78), width=10)
    c.putalpha(c.getchannel('A').point(lambda v: int(v * k)))
    return c.resize((1000, 450), Image.LANCZOS)
ILL = {'dog': ill_dog, 'sponge': ill_sponge, 'bridge': ill_bridge, 'warrior': ill_warrior}

def fact_card(lt, lines, ill='bridge', heading='Fun fact!'):
    lines = [tr(x) for x in lines]; heading = tr(heading)
    im = BG.copy(); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = spring(lt * 1.1)
    d.text((W / 2, 150 + (1 - s) * -250), heading, font=font('p', 120, 'Bold'), fill=TEAL, anchor='mm')
    im.alpha_composite(lay)
    il = ILL.get(ill, ill_bridge)(clamp((lt - 0.3) / 1.2), lt)
    im.alpha_composite(il, (W // 2 - il.width // 2, 250))
    a2 = ease((lt - 1.4) / 0.6)
    tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(tl)
    f2 = font('d', 58, 'Bold')
    for i, ln in enumerate(lines):
        d2.text((W / 2, 790 + i * 80), ln, font=fit_font('d', 'Bold', ln, 1700, 58), fill=CHAR, anchor='mm')
    paste(im, tl, (0, 0), a2)
    if 1.8 < lt < 3.2:
        q = (lt - 1.8) / 1.4; r2 = random.Random(5)
        for j in range(16):
            x = r2.uniform(500, 1420); y = 300 + r2.uniform(-40, 300) - 60 * q; sp = SPARK[r2.choice([10, 16])]
            paste(im, sp, (x - sp.width / 2, y - sp.height / 2), math.sin(math.pi * q))
    return im

def outro_card(lt, pose_name, clear_text=False, confetti='classic'):
    """confetti='classic' (default, unchanged: thin corner sprinkle) | 'full' (opt-in via config celebrate.card:
    dense rain over the whole card behind the text + a soft cream glow under the text + foreground pieces off the text)."""
    if confetti == 'full': return _outro_full(lt, pose_name)
    im = BG.copy(); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = spring(lt * 1.0); sc = max(0.05, s)
    tri_icon(d, W / 2, 250, 45 * sc, 1.0, 7)
    d.text((W / 2, 440), tr('Nice work!'), font=font('p', max(10, int(140 * sc)), 'Bold'), fill=TEAL, anchor='mm')
    a2 = ease((lt - 0.5) / 0.6); a3 = ease((lt - 0.9) / 0.6)
    l2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
    txt = you_did(pose_name)
    d2.text((W / 2, 590), txt, font=fit_font('d', 'Bold', txt, 1700, 70), fill=CHAR, anchor='mm')
    l3 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d3 = ImageDraw.Draw(l3)
    d3.line([(W / 2 - 140, 690), (W / 2 + 140, 690)], fill=GOLD, width=5)
    d3.text((W / 2, 770), 'HudsonSeed · Hani', font=font('d', 46, 'Medium'), fill=TEAL2, anchor='mm')
    im.alpha_composite(lay); paste(im, l2, (0, 0), a2); paste(im, l3, (0, 0), a3)
    # reuse the official confetti from the base outro by rendering its confetti only
    cl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cl)
    for (side, vx, vy, rot, rs, col, sz, dl) in BB.CONF:
        tt = lt - 0.3 - dl
        if tt <= 0: continue
        drag = 1.3
        x = (0 if side == 0 else W) + vx * (1 - math.exp(-drag * tt)) / drag
        y = H + vy * (1 - math.exp(-drag * tt)) / drag + 380 * tt + 260 * tt * tt * 0.5 * math.exp(-0.5 * tt)
        if y > H + 40: continue
        ang = rot + rs * tt; w2 = sz * abs(math.cos(rs * tt * 0.7)) + 2; h2 = sz * 0.55
        ca, sa = math.cos(ang), math.sin(ang)
        dc.polygon([(x + ca * px - sa * py, y + sa * px + ca * py) for px, py in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))], fill=col + (235,))
    if clear_text:   # keep confetti off the 'Nice work' text block
        global _CLEAR
        if '_CLEAR' not in globals():
            m = Image.new('L', (W, H), 255); ImageDraw.Draw(m).rounded_rectangle([W / 2 - 640, 175, W / 2 + 640, 815], 90, fill=0)
            _CLEAR = m.filter(ImageFilter.GaussianBlur(40))
        r, g_, b, a_ = cl.split(); from PIL import ImageChops; cl = Image.merge('RGBA', (r, g_, b, ImageChops.multiply(a_, _CLEAR)))
    im.alpha_composite(cl)
    return im


_GLOW = None
def _outro_full(lt, pose_name):
    import celebrate as CEL
    global _GLOW
    im = BG.copy()
    CEL.comp(im, CEL.card_back(lt))                       # dense confetti over the whole card, behind the text
    if _GLOW is None:                                     # soft cream glow so the text always reads
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).rounded_rectangle([W / 2 - 560, 180, W / 2 + 560, 810], 120, fill=175)
        _GLOW = Image.new('RGBA', (W, H), CREAM + (0,)); _GLOW.putalpha(m.filter(ImageFilter.GaussianBlur(55)))
    im.alpha_composite(_GLOW)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = spring(lt * 1.0); sc = max(0.05, s)
    tri_icon(d, W / 2, 250, 45 * sc, 1.0, 7)
    d.text((W / 2, 440), tr('Nice work!'), font=font('p', max(10, int(140 * sc)), 'Bold'), fill=TEAL, anchor='mm')
    a2 = ease((lt - 0.5) / 0.6); a3 = ease((lt - 0.9) / 0.6)
    l2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
    txt = you_did(pose_name)
    d2.text((W / 2, 590), txt, font=fit_font('d', 'Bold', txt, 1700, 70), fill=CHAR, anchor='mm')
    l3 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d3 = ImageDraw.Draw(l3)
    d3.line([(W / 2 - 140, 690), (W / 2 + 140, 690)], fill=GOLD, width=5)
    d3.text((W / 2, 770), 'HudsonSeed · Hani', font=font('d', 46, 'Medium'), fill=TEAL2, anchor='mm')
    im.alpha_composite(lay); paste(im, l2, (0, 0), a2); paste(im, l3, (0, 0), a3)
    # foreground pieces (in front of everything) kept off the text block
    fr = CEL.card_front(lt); a_ = fr[..., 3].astype('float32') * (np.asarray(_clear_mask(), 'float32') / 255)
    fr = (fr.astype('float32') * (a_ / np.maximum(fr[..., 3:4].astype('float32')[..., 0], 1))[..., None]).astype('uint8')
    CEL.comp(im, fr)
    return im

def _clear_mask():
    global _CLEAR
    if '_CLEAR' not in globals():
        m = Image.new('L', (W, H), 255); ImageDraw.Draw(m).rounded_rectangle([W / 2 - 640, 175, W / 2 + 640, 815], 90, fill=0)
        _CLEAR = m.filter(ImageFilter.GaussianBlur(40))
    return _CLEAR


def title_overlay(im, lt, title, badge, dur):
    """Bouncy title on a cream panel across the top of the live scene (used for the idle opening)."""
    title = tr(title); badge = tr(badge)
    a = clamp((dur + 0.6 - lt) / 0.6) if lt > dur else 1.0
    if a <= 0: return
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pin = spring(lt * 1.4)
    pw, ph = 1060, 230; px = W / 2 - pw / 2; py = 30 - (1 - pin) * 300
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([px, py + 8, px + pw, py + ph + 8], 50, fill=(0, 0, 0, 60))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([px, py, px + pw, py + ph], 50, fill=CREAM + (242,), outline=GOLD + (255,), width=5)
    TFp = fit_font('p', 'Bold', title, pw - 120, 120)
    total_w = TFp.getlength(title); x = W / 2 - total_w / 2
    for i, ch in enumerate(title):
        w = TFp.getlength(title[:i + 1]) - TFp.getlength(title[:i])
        tt = lt - 0.25 - i * 0.06; s = spring(tt)
        if tt > 0 and ch != ' ':
            d.text((x + w / 2, py + 140 + (1 - s) * -160), ch, font=TFp, fill=TEAL, anchor='ms')
        x += w
    if lt > 1.3:
        s = spring((lt - 1.3) * 1.2); fs = max(8, int(52 * s))
        d.text((W / 2, py + 190), tr('with Hani'), font=font('d', fs, 'Bold'), fill=CHAR, anchor='mm')
    im.alpha_composite(with_alpha(lay, a))
    if badge and lt > 1.7:
        s = spring((lt - 1.7) * 1.3); bf = font('d', 40, 'Bold'); tw = bf.getlength(badge)
        bw, bh = int(tw + 60), 74
        b = Image.new('RGBA', (bw + 40, bh + 40), (0, 0, 0, 0)); db = ImageDraw.Draw(b)
        db.rounded_rectangle([20, 20, 20 + bw, 20 + bh], 37, fill=GOLD + (255,), outline=(255, 255, 255, 255), width=5)
        db.text((20 + bw / 2, 20 + bh / 2 + 2), badge, font=bf, fill=(255, 255, 255), anchor='mm')
        sc = max(0.05, s); b = b.resize((max(2, int(b.width * sc)), max(2, int(b.height * sc))), Image.LANCZOS).rotate(-7 * s, expand=True, resample=Image.BICUBIC)
        paste(im, b, (W / 2 + pw / 2 - b.width * 0.6, 40 - b.height * 0.25), a)
    if 1.9 < lt < 3.4:
        q = (lt - 1.9) / 1.5; r2 = random.Random(12)
        for j in range(16):
            ang = r2.uniform(0, 6.28); dist = 80 + 420 * ease(q) * r2.uniform(.4, 1)
            sp = SPARK[r2.choice([10, 16, 24])]
            paste(im, sp, (W / 2 + dist * math.cos(ang) - sp.width / 2, 140 + dist * 0.3 * math.sin(ang) - sp.height / 2), clamp(1 - q) * a)

# side-mode fact illustrations (new keys only; nothing above changes)
try:
    import ills_side as _IS
    for _k, _f in _IS.ILL.items(): ILL.setdefault(_k, _f)
except ImportError:
    pass
