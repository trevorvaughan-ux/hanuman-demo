import sys, math, random, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

V = sys.argv[1]            # v1 | v2
B = V == 'v2'
OUTRAW = sys.argv[2]       # intermediate video path
WAV = sys.argv[3]
W, H, FPS = 1920, 1080, 25
D = '/workspace/hani/'
TEAL = (19, 107, 107); TEAL2 = (47, 107, 110); CREAM = (253, 248, 240)
GOLD = (217, 154, 78); CHAR = (58, 58, 58)
src = np.memmap(D + ('src_graded_v2.rgb' if B else 'src_graded.rgb'), dtype=np.uint8, mode='r', shape=(175, H, W, 3))

def font(kind, size, var):
    f = ImageFont.truetype(D + 'fonts/' + ('Playfair.ttf' if kind == 'p' else 'DMSans.ttf'), size)
    f.set_variation_by_name(var); return f

ease = lambda x: 0.5 - 0.5 * math.cos(math.pi * min(1, max(0, x)))
clamp = lambda x, a=0, b=1: max(a, min(b, x))
def spring(t):  # 0->1 with overshoot
    return 0 if t <= 0 else 1 - math.exp(-5.5 * t) * math.cos(11 * t)

# ---------------- timeline ----------------
XF = 0.6
SIDE = 38.75
segs = [('intro', 3.6 if B else 3.0), ('side', SIDE, 0)]
if B: segs.append(('fact', 4.8))
segs += [('side', SIDE, 1), ('outro', 4.2 if B else 3.4)]
starts = []; t = 0
for s in segs:
    starts.append(t); t += s[1] - XF
TOTAL = t + XF
NF = int(round(TOTAL * FPS))

def side_src_t(lt):
    if lt < 5: return 4.5 + lt if lt < 2.5 else 7.0 - (lt - 2.5)
    if lt < 8: return 4.5 - (lt - 5) / 2
    if lt < 35:
        k = int((lt - 8) / 2.7); u = (lt - 8) - k * 2.7
        return 3.0 - u if k % 2 == 0 else 0.3 + u
    if lt < 37.25: return 3.0 + (lt - 35) / 1.5
    return 4.5 + (lt - 37.25)

def srcframe(st, flip):
    f = clamp(st * FPS, 0, 174); i = int(f); a = f - i
    if a < 0.08 or i >= 174: fr = np.asarray(src[i])
    else:
        fr = (src[i].astype(np.uint16) * int(256 * (1 - a)) + src[i + 1].astype(np.uint16) * int(256 * a)) >> 8
        fr = fr.astype(np.uint8)
    if flip: fr = fr[:, ::-1]
    return Image.fromarray(np.ascontiguousarray(fr)).convert('RGBA')

def caps_for(side):
    c = [(0, 2.5, 'Stand tall, feet wide' if side == 0 else 'Other side! Stand tall, feet wide'),
         (2.5, 5, 'Arms out like a T'), (5, 8, 'Reach long to the side'),
         (8, 11, 'Hand down, other arm up to the sky')]
    for k in range(3):
        c += [(11 + 8 * k, 15 + 8 * k, 'Breathe in...'), (15 + 8 * k, 19 + 8 * k, 'Breathe out...')]
    c += [(35, SIDE, 'Come back up')]
    return c

# ---------------- caption rendering ----------------
CF = font('d', 62, 'Bold')
_capcache = {}
def capimg(text):
    if text in _capcache: return _capcache[text]
    bb = CF.getbbox(text); tw = bb[2] - bb[0]
    bw, bh = tw + 110, 112
    pad = 24
    im = Image.new('RGBA', (bw + 2 * pad, bh + 2 * pad), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([pad, pad + 6, pad + bw, pad + bh + 6], 40, fill=(0, 0, 0, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(9))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([pad, pad, pad + bw, pad + bh], 40, fill=TEAL + (240,), outline=GOLD + (255,), width=4)
    tx = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(tx).text((pad + bw / 2, pad + bh / 2 + 2), text, font=CF, fill=CREAM, anchor='mm')
    _capcache[text] = (im, tx)
    return im, tx

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); al = im.getchannel('A').point(lambda v: int(v * a)); im.putalpha(al); return im

def paste(base, im, xy, a=1.0):
    if a <= 0.003: return
    base.alpha_composite(with_alpha(im, a), (int(xy[0]), int(xy[1])))

def draw_caps(base, lt, caps):
    act = []
    for i, (s, e, txt) in enumerate(caps):
        if s <= lt < e + 0.3:
            nxt = caps[i + 1] if i + 1 < len(caps) else None
            contiguous_next = nxt is not None and abs(nxt[0] - e) < 1e-6
            if lt >= e: a = 1.0 if contiguous_next else 1 - (lt - e) / 0.3
            else: a = clamp((lt - s) / 0.3)
            prev_contig = i > 0 and abs(caps[i - 1][1] - s) < 1e-6 and lt < s + 0.3
            act.append((txt, a, prev_contig))
    if not act: return
    if len(act) == 2 and act[1][2]:  # transition: boxes stacked, texts cross-dissolve
        (t0, _, _), (t1, a1, _) = act
        b0, x0 = capimg(t0); b1, x1 = capimg(t1)
        pos = lambda im: (W / 2 - im.width / 2, 1048 - im.height + 24)
        paste(base, b0, pos(b0), 1 - a1); paste(base, b1, pos(b1), a1)
        paste(base, x0, pos(x0), clamp(1 - 2 * a1)); paste(base, x1, pos(x1), clamp(2 * a1 - 1))
        return
    for txt, a, _ in act:
        b, x = capimg(txt); p = (W / 2 - b.width / 2, 1048 - b.height + 24)
        paste(base, b, p, a); paste(base, x, p, a)

# ---------------- breathing circle ----------------
BF = font('d', 64, 'Bold'); SF = font('d', 30, 'Bold')
def breath_layer(lt):
    if not (10.4 < lt < 35.6): return None, 0
    vis = clamp((lt - 10.4) / 0.6) * clamp((35.6 - lt) / 0.6)
    rmin, rmax = 46, 98
    if lt < 11: r, k, phase = rmin, 0, 'in'
    elif lt >= 35: r, k, phase = rmin, 2, 'out'
    else:
        p = (lt - 11) % 8; k = int((lt - 11) // 8)
        if p < 4: r = rmin + (rmax - rmin) * ease(p / 4); phase = 'in'
        else: r = rmax - (rmax - rmin) * ease((p - 4) / 4); phase = 'out'
    S = 300; c = S / 2
    im = Image.new('RGBA', (S, S + 50), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([c - 118, c - 118, c + 118, c + 118], fill=CREAM + (200,), outline=TEAL + (230,), width=5)
    g = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse([c - r - 12, c - r - 12, c + r + 12, c + r + 12], fill=GOLD + (120,))
    g = g.filter(ImageFilter.GaussianBlur(12))
    im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
    d.ellipse([c - r, c - r, c + r, c + r], fill=GOLD + (245,))
    d.text((c, c + 2), str(k + 1), font=BF, fill=CHAR, anchor='mm')
    lbl = 'breathe in' if phase == 'in' else 'breathe out'
    bb = SF.getbbox(lbl); tw = bb[2] - bb[0]
    d.rounded_rectangle([c - tw / 2 - 18, S + 2, c + tw / 2 + 18, S + 46], 22, fill=TEAL + (235,))
    d.text((c, S + 24), lbl, font=SF, fill=CREAM, anchor='mm')
    return im, vis

# ---------------- v2 extras ----------------
def star_poly(cx, cy, R, r, n=5, rot=-math.pi / 2):
    pts = []
    for i in range(2 * n):
        rr = R if i % 2 == 0 else r; a = rot + i * math.pi / n
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    return pts

def sparkle_sprite(size, col=(255, 236, 190)):
    S = size * 4; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    d.ellipse([c - size * .9, c - size * .9, c + size * .9, c + size * .9], fill=GOLD + (150,))
    im = im.filter(ImageFilter.GaussianBlur(size * .6)); d = ImageDraw.Draw(im)
    d.polygon(star_poly(c, c, size * 1.3, size * .28, 4, 0), fill=col + (255,))
    return im
SPARK = {s: sparkle_sprite(s) for s in (6, 10, 16, 24)}
def glowdot(r):
    S = r * 8; im = Image.new('RGBA', (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = S / 2
    d.ellipse([c - r * 2.2, c - r * 2.2, c + r * 2.2, c + r * 2.2], fill=(255, 214, 140, 110))
    im = im.filter(ImageFilter.GaussianBlur(r * 1.3)); d = ImageDraw.Draw(im)
    d.ellipse([c - r, c - r, c + r, c + r], fill=(255, 246, 215, 235)); return im
DOTS = [glowdot(r) for r in (3, 4, 6)]

rng = random.Random(7)
FLIES = []
while len(FLIES) < 30:
    x, y = rng.uniform(40, 1880), rng.uniform(40, 820)
    if 600 < x < 1320 and 230 < y < 930: continue
    FLIES.append((x, y, rng.uniform(0, 6.28), rng.uniform(.15, .4), rng.uniform(18, 46), rng.choice(range(3)), rng.uniform(.5, 1.4)))
def fireflies(base, t, vis=1.0):
    for (x, y, ph, sp, amp, sz, tw) in FLIES:
        px = x + amp * math.sin(t * sp + ph) + 12 * math.sin(t * 0.7 + ph * 2)
        py = y + amp * 0.7 * math.cos(t * sp * 1.3 + ph)
        a = (0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * tw * 2.2 + ph * 3))) * vis
        if 600 < px < 1320 and 230 < py < 930: a *= 0.2
        im = DOTS[sz]; paste(base, im, (px - im.width / 2, py - im.height / 2), a)

TRI = [(765, 893), (958, 650), (1175, 882)]
def tri_layer(lt):
    # draw-on 8.2-9.8, sparkle burst 9.8-10.8, hold glow until 35, fade to 35.7
    if not (8.2 <= lt < 35.7): return None
    ox, oy = 560, 480; CW, CH = 820, 560
    P = [(x - ox, y - oy) for x, y in TRI] + [(TRI[0][0] - ox, TRI[0][1] - oy)]
    lens = [math.dist(P[i], P[i + 1]) for i in range(3)]; tot = sum(lens)
    prog = ease((lt - 8.2) / 1.6)
    L = prog * tot; pts = [P[0]]; tip = P[0]
    for i in range(3):
        if L >= lens[i]: pts.append(P[i + 1]); L -= lens[i]; tip = P[i + 1]
        else:
            f = L / lens[i]; tip = (P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)
            pts.append(tip); break
    if lt < 9.8: alpha = 1.0
    else:
        p = (lt - 11) % 8 if lt > 11 else 0
        br = ease(p / 4) if p < 4 else 1 - ease((p - 4) / 4)
        alpha = max(0.55 + 0.35 * br, 1 - (lt - 9.8) / 1.2 * 0.45) if lt < 35 else (0.55) * (1 - (lt - 35) / 0.7)
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    g = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
    ImageDraw.Draw(g).line(pts, fill=GOLD + (230,), width=30, joint='curve')
    g = g.filter(ImageFilter.GaussianBlur(12))
    im = Image.alpha_composite(im, g); d = ImageDraw.Draw(im)
    d.line(pts, fill=(255, 205, 120, 255), width=10, joint='curve')
    d.line(pts, fill=(255, 245, 220, 255), width=4, joint='curve')
    im = with_alpha(im, alpha)
    if lt < 9.8:
        sp = SPARK[24]; im.alpha_composite(sp, (int(tip[0] - sp.width / 2), int(tip[1] - sp.height / 2)))
    elif lt < 11.0:
        q = (lt - 9.8) / 1.2; r = rng2 = random.Random(3)
        for vx, vy in P[:3]:
            for j in range(7):
                ang = rng2.uniform(0, 6.28); dist = 20 + 110 * ease(q) * rng2.uniform(.5, 1)
                sp = SPARK[rng2.choice([10, 16])]; a = 1 - q
                x = vx + dist * math.cos(ang) - sp.width / 2; y = vy + dist * math.sin(ang) - sp.height / 2
                if 0 <= x < CW - sp.width and 0 <= y < CH - sp.height:
                    im.alpha_composite(with_alpha(sp, a), (int(x), int(y)))
    return im, (ox, oy)

STF = font('d', 30, 'Bold')
def stars_layer(lt):
    if not (10.4 < lt < 38.0): return None, 0
    vis = clamp((lt - 10.4) / 0.6) * clamp((38.0 - lt) / 0.6)
    CW, CH = 400, 170
    im = Image.new('RGBA', (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([10, 10, CW - 10, CH - 10], 36, fill=CREAM + (215,), outline=TEAL + (230,), width=4)
    d.text((CW / 2, 40), '3 big breaths', font=STF, fill=TEAL, anchor='mm')
    for k in range(3):
        cx, cy = 100 + k * 100, 105
        done_t = 19 + 8 * k
        if lt >= done_t:
            s = 1 + 0.45 * math.exp(-6 * (lt - done_t)) * math.cos(14 * (lt - done_t)) if lt - done_t < 1 else 1
            if lt - done_t < 0.6:
                gl = Image.new('RGBA', (CW, CH), (0, 0, 0, 0))
                ImageDraw.Draw(gl).ellipse([cx - 50, cy - 50, cx + 50, cy + 50], fill=(255, 220, 140, int(200 * (1 - (lt - done_t) / 0.6))))
                im = Image.alpha_composite(im, gl.filter(ImageFilter.GaussianBlur(10))); d = ImageDraw.Draw(im)
            d.polygon(star_poly(cx, cy, 36 * s, 15 * s), fill=GOLD, outline=CHAR)
        else:
            cur = 11 + 8 * k <= lt < done_t
            d.polygon(star_poly(cx, cy, 34, 14), fill=(255, 240, 210) if cur else CREAM, outline=TEAL)
            if cur:  # partial fill from bottom as the breath progresses
                f = (lt - (11 + 8 * k)) / 8
                m = Image.new('L', (CW, CH), 0); ImageDraw.Draw(m).polygon(star_poly(cx, cy, 34, 14), fill=255)
                ImageDraw.Draw(m).rectangle([0, 0, CW, cy + 34 - 68 * f], fill=0)
                fill = Image.new('RGBA', (CW, CH), GOLD + (200,)); im.paste(fill, (0, 0), m); d = ImageDraw.Draw(im)
                d.polygon(star_poly(cx, cy, 34, 14), outline=TEAL)
    return im, vis

# ---------------- cards ----------------
def card_bg(warm=False):
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.45) / H) ** 2)
    c0 = np.array(CREAM, float); c1 = np.array((247, 230, 205) if warm else (244, 236, 222), float)
    k = np.clip(r / 0.75, 0, 1)[..., None] ** 1.6
    img = (c0 * (1 - k) + c1 * k).astype(np.uint8)
    return Image.fromarray(img).convert('RGBA')
BG = card_bg(B)

TF = font('p', 160, 'Bold'); SUBF = font('d', 66, 'Medium')
def tri_icon(d, cx, cy, s, prog=1.0, width=8, col=GOLD):
    P = [(cx, cy - s), (cx + s * 1.1, cy + s * .75), (cx - s * 1.1, cy + s * .75), (cx, cy - s)]
    lens = [math.dist(P[i], P[i + 1]) for i in range(3)]; L = prog * sum(lens); pts = [P[0]]
    for i in range(3):
        if L >= lens[i]: pts.append(P[i + 1]); L -= lens[i]
        else:
            f = L / lens[i]; pts.append((P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f)); break
    if len(pts) > 1: d.line(pts, fill=col, width=width, joint='curve')

def intro(lt):
    im = BG.copy()
    if not B:
        a = ease(lt / 0.9); rise = (1 - a) * 30
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        tri_icon(d, W / 2, 300 + rise, 55, ease(lt / 1.2))
        d.text((W / 2, 500 + rise), 'Triangle Pose', font=TF, fill=TEAL, anchor='mm')
        d.text((W / 2, 650 + rise), 'with Hani', font=SUBF, fill=CHAR, anchor='mm')
        d.line([(W / 2 - 120, 720 + rise), (W / 2 + 120, 720 + rise)], fill=GOLD, width=5)
        paste(im, lay, (0, 0), a); return im
    # v2: bouncy letters
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text = 'Triangle Pose'; total_w = TF.getlength(text); x = W / 2 - total_w / 2
    for i, ch in enumerate(text):
        w = TF.getlength(text[:i + 1]) - TF.getlength(text[:i])
        tt = lt - 0.15 - i * 0.06; s = spring(tt)
        if tt > 0 and ch != ' ':
            yoff = (1 - s) * -420
            squash = 1 + 0.25 * math.exp(-8 * max(0, tt - 0.25)) * math.sin(max(0, tt - 0.25) * 20) if tt > 0.25 else 1
            d.text((x + w / 2, 520 + yoff), ch, font=TF, fill=TEAL, anchor='ms')
        x += w
    p = clamp((lt - 1.2) / 0.9)
    tri_icon(d, W / 2, 250, 70, ease(p), 10)
    if lt > 1.5:
        s = spring((lt - 1.5) * 1.2); fs = max(8, int(70 * s))
        d.text((W / 2, 640), 'with Hani', font=font('d', fs, 'Bold'), fill=CHAR, anchor='mm')
    im.alpha_composite(lay)
    if lt > 2.1:  # sparkles around the triangle icon
        q = lt - 2.1; r2 = random.Random(11)
        for j in range(14):
            ang = r2.uniform(0, 6.28); dist = 60 + 260 * ease(q / 1.2) * r2.uniform(.4, 1)
            sp = SPARK[r2.choice([10, 16, 24])]
            paste(im, sp, (W / 2 + dist * math.cos(ang) - sp.width / 2, 260 + dist * 0.6 * math.sin(ang) - sp.height / 2), clamp(1 - q / 1.4))
    fireflies(im, lt + 100, 0.8)
    return im

FF1 = font('p', 120, 'Bold'); FF2 = font('d', 58, 'Bold')
def fact(lt):
    im = BG.copy(); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    s = spring(lt * 1.1)
    d.text((W / 2, 150 + (1 - s) * -250), 'Fun fact!', font=FF1, fill=TEAL, anchor='mm')
    # truss bridge drawing itself
    x0, x1, yd, yt, n = 460, 1460, 600, 400, 6
    pw = (x1 - x0) / n
    prog = clamp((lt - 0.4) / 1.6)
    d.rectangle([x0 - 60, yd, x1 + 60, yd + 26], fill=TEAL2)
    d.rectangle([x0 - 90, yd + 26, x0 - 30, yd + 120], fill=(200, 190, 175)); d.rectangle([x1 + 30, yd + 26, x1 + 90, yd + 120], fill=(200, 190, 175))
    d.line([(x0 - 140, yd + 140), (x1 + 140, yd + 140)], fill=(120, 175, 190), width=6)
    m = int(prog * n * 1.0001)
    for i in range(n):
        a, b2, c = (x0 + i * pw, yd), (x0 + (i + 0.5) * pw, yt), (x0 + (i + 1) * pw, yd)
        if i < m:
            d.polygon([a, b2, c], fill=(255, 226, 170, 255), outline=None)
            d.line([a, b2, c], fill=GOLD, width=10, joint='curve')
        elif i == m:
            f = prog * n - m
            d.line([a, (a[0] + (b2[0] - a[0]) * f, a[1] + (b2[1] - a[1]) * f)], fill=GOLD, width=10)
    if prog > 0.15: d.line([(x0 + 0.5 * pw, yt), (x0 + 0.5 * pw + (n - 1) * pw * clamp((prog - .15) / .85), yt)], fill=TEAL2, width=12)
    a2 = ease((lt - 1.6) / 0.6)
    t1 = 'Triangles are the strongest shape —'; t2 = "that's why bridges use them!"
    tl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(tl)
    d2.text((W / 2, 820), t1, font=FF2, fill=CHAR, anchor='mm'); d2.text((W / 2, 900), t2, font=FF2, fill=CHAR, anchor='mm')
    im.alpha_composite(lay); paste(im, tl, (0, 0), a2)
    if 2.0 < lt < 3.4:
        q = (lt - 2.0) / 1.4; r2 = random.Random(5)
        for j in range(16):
            x = r2.uniform(x0, x1); y = yt + r2.uniform(-40, 200) - 60 * q; sp = SPARK[r2.choice([10, 16])]
            paste(im, sp, (x - sp.width / 2, y - sp.height / 2), math.sin(math.pi * q))
    return im

OF1 = font('p', 140, 'Bold'); OF2 = font('d', 70, 'Bold'); OF3 = font('d', 46, 'Medium')
crng = random.Random(21)
CONF = []
for side in (0, 1):
    for j in range(110):
        ang = math.radians(crng.uniform(58, 84)); sp = crng.uniform(1500, 2700)
        vx = sp * math.cos(ang) * (1 if side == 0 else -1); vy = -sp * math.sin(ang)
        CONF.append((side, vx, vy, crng.uniform(0, 6.28), crng.uniform(-9, 9),
                     crng.choice([TEAL, GOLD, (240, 120, 100), (120, 190, 170), (250, 200, 90), TEAL2]),
                     crng.uniform(10, 18), crng.uniform(0, 0.25)))
def outro(lt):
    im = BG.copy(); lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if not B:
        a = ease(lt / 0.8); rise = (1 - a) * 30
        tri_icon(d, W / 2, 250 + rise, 45, 1.0, 7)
        d.text((W / 2, 440 + rise), 'Nice work!', font=OF1, fill=TEAL, anchor='mm')
        d.text((W / 2, 590 + rise), 'You did Triangle Pose.', font=OF2, fill=CHAR, anchor='mm')
        d.line([(W / 2 - 140, 690 + rise), (W / 2 + 140, 690 + rise)], fill=GOLD, width=5)
        d.text((W / 2, 770 + rise), 'HudsonSeed · Hani', font=OF3, fill=TEAL2, anchor='mm')
        paste(im, lay, (0, 0), a); return im
    s = spring(lt * 1.0); sc = max(0.05, s)
    f1 = font('p', max(10, int(140 * sc)), 'Bold')
    tri_icon(d, W / 2, 250, 45 * sc, 1.0, 7)
    d.text((W / 2, 440), 'Nice work!', font=f1, fill=TEAL, anchor='mm')
    a2 = ease((lt - 0.5) / 0.6); a3 = ease((lt - 0.9) / 0.6)
    l2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
    d2.text((W / 2, 590), 'You did Triangle Pose.', font=OF2, fill=CHAR, anchor='mm')
    l3 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d3 = ImageDraw.Draw(l3)
    d3.line([(W / 2 - 140, 690), (W / 2 + 140, 690)], fill=GOLD, width=5)
    d3.text((W / 2, 770), 'HudsonSeed · Hani', font=OF3, fill=TEAL2, anchor='mm')
    im.alpha_composite(lay); paste(im, l2, (0, 0), a2); paste(im, l3, (0, 0), a3)
    # confetti
    cl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(cl)
    for (side, vx, vy, rot, rs, col, sz, dl) in CONF:
        tt = lt - 0.3 - dl
        if tt <= 0: continue
        drag = 1.3
        x = (0 if side == 0 else W) + vx * (1 - math.exp(-drag * tt)) / drag
        vt = 380  # terminal-ish fall
        y = H + vy * (1 - math.exp(-drag * tt)) / drag + vt * tt + 260 * tt * tt * 0.5 * math.exp(-0.5 * tt)
        if y > H + 40: continue
        ang = rot + rs * tt; w2 = sz * abs(math.cos(rs * tt * 0.7)) + 2; h2 = sz * 0.55
        ca, sa = math.cos(ang), math.sin(ang)
        pts = [(x + ca * px - sa * py, y + sa * px + ca * py) for px, py in ((-w2, -h2), (w2, -h2), (w2, h2), (-w2, h2))]
        dc.polygon(pts, fill=col + (235,))
    im.alpha_composite(cl)
    return im

def side_frame(lt, side):
    im = srcframe(side_src_t(lt), side == 1)
    if B:
        fireflies(im, lt + side * 50)
        tl = tri_layer(lt)
        if tl:
            lay, (ox, oy) = tl
            if side == 1: lay = ImageOps.mirror(lay); ox = W - ox - lay.width
            im.alpha_composite(lay, (ox, oy))
        sl, sv = stars_layer(lt)
        if sl: paste(im, sl, (W - 40 - sl.width, 40), sv)
    bl, bv = breath_layer(lt)
    if bl: paste(im, bl, (50, 40), bv)
    draw_caps(im, lt, CAPS[side])
    return im
CAPS = {0: caps_for(0), 1: caps_for(1)}

def render_seg(i, lt):
    s = segs[i]
    if s[0] == 'intro': return intro(lt)
    if s[0] == 'outro': return outro(lt)
    if s[0] == 'fact': return fact(lt)
    return side_frame(lt, s[2])

# ---------------- events + audio ----------------
ev = {'total': TOTAL, 'chimes': [], 'inhale': [], 'sparkle': [], 'confetti': [], 'boops': [], 'breath_windows': []}
for i, s in enumerate(segs):
    ev['chimes'].append(starts[i] + (0.2 if i == 0 else XF * 0.5))
    if s[0] == 'side':
        st = starts[i]
        for k in range(3): ev['inhale'].append(st + 11 + 8 * k)
        ev['breath_windows'].append(st + 11)
        for c in (2.5, 5, 8, 35): ev['chimes'].append(st + c)
        if B: ev['sparkle'].append(st + 9.8)
    if s[0] == 'outro' and B: ev['confetti'].append(starts[i] + 0.3)
    if s[0] == 'intro' and B:
        for j, ch in enumerate('Triangle Pose'):
            if ch != ' ': ev['boops'].append(starts[i] + 0.15 + j * 0.06 + 0.12)
    if s[0] == 'fact' and B: ev['sparkle'].append(starts[i] + 2.0)
json.dump(ev, open(WAV + '.json', 'w'), indent=1)
subprocess.run(['python3', D + 'build/audio.py', WAV + '.json', WAV, V], check=True)

# ---------------- render ----------------
only = sys.argv[4] if len(sys.argv) > 4 else None
if only:  # debug: render single times
    for tt in [float(x) for x in only.split(',')]:
        act = [(i, tt - starts[i]) for i in range(len(segs)) if starts[i] <= tt < starts[i] + segs[i][1]]
        fr = render_seg(*act[-1]).convert('RGB'); fr.save(D + f'build/dbg_{V}_{tt:06.2f}.png')
    sys.exit()
ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS),
                       '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', OUTRAW], stdin=subprocess.PIPE)
for n in range(NF):
    tt = n / FPS
    act = [(i, tt - starts[i]) for i in range(len(segs)) if starts[i] <= tt < starts[i] + segs[i][1]]
    if len(act) == 1: fr = render_seg(*act[0])
    else:
        a = ease((tt - starts[act[1][0]]) / XF)
        fr = Image.blend(render_seg(*act[0]).convert('RGB'), render_seg(*act[1]).convert('RGB'), a)
    if n == 0 or n == NF - 1: pass
    ff.stdin.write(fr.convert('RGB').tobytes())
    if n % 250 == 0: print(V, n, NF, flush=True)
ff.stdin.close(); ff.wait()
print('done', TOTAL)
