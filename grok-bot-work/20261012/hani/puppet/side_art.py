"""Side-view Hani art set (Oct 12, 2026) - opt-in for side mode (config side.art = "side3d").
Painted procedurally in the style of the real Triangle Hani cut-out: colours are sampled from puppet/tex_full.png
(the graded Triangle frame), soft 3D dome shading (light from the upper front), faint fur grain along each limb and a
soft darker rim like the cut-out. The profile head is DERIVED from the real Triangle art (puppet/tex_headprof.png, the
over-the-shoulder profile warp of the 3/4 Triangle head) with the smeared far ear removed and a clean near ear + round
back of the skull painted in. Output: puppet/side_art/<part>.png (straight RGBA) + parts.json (bone a/b, scale).
Every part is drawn with its bone horizontal (a = proximal on the left, b = distal on the right) except torso/head (upright).
Run: venv/bin/python puppet/side_art.py   (deterministic, seed fixed)"""
import json, math, os, sys
import numpy as np, cv2
D = '/workspace/hani/puppet/'; OUT = D + 'side_art/'
SS = 3                                     # supersampling
rng = np.random.default_rng(12)
tex = cv2.cvtColor(cv2.imread(D + 'tex_full.png', -1), cv2.COLOR_BGRA2RGBA).astype(np.float32)
def med(x0, y0, x1, y1):
    r = tex[y0:y1, x0:x1]; m = r[..., 3] > 250; return np.median(r[m][:, :3], 0)
C = dict(torso=med(935, 480, 950, 600), belly=med(975, 500, 1000, 560), thigh=med(1030, 680, 1060, 700),
         arm=med(1080, 425, 1100, 435), hand=med(1250, 380, 1280, 395), foot=med(1180, 870, 1220, 890),
         face=med(975, 385, 1000, 400), headfur=med(960, 310, 1020, 325), ear=med(926, 365, 934, 380))
FUR = (C['torso'] * 0.45 + C['thigh'] * 0.3 + C['arm'] * 0.25)          # one limb/torso fur colour (Triangle median)
LIGHT = np.array([-0.30, -0.45, 0.84]); LIGHT /= np.linalg.norm(LIGHT)

def shade(mask, base, grain_dir=0.0, grain=0.028, rim=0.80, amb=0.50, spec=0.10, R=None, flat=1.0):
    """mask: float HxW (supersampled). Returns straight RGB float (0-255)."""
    m8 = (mask > 0.5).astype(np.uint8)
    d = cv2.distanceTransform(np.pad(m8, 1), cv2.DIST_L2, 5)[1:-1, 1:-1]
    if R is None: R = max(d.max(), 1)
    u = np.clip(d / R, 0, 1); h = R * np.sqrt(1 - (1 - u) ** 2) * flat
    h = cv2.GaussianBlur(h.astype(np.float32), (0, 0), 1.2 * SS)
    gy, gx = np.gradient(h); n = np.dstack([-gx, -gy, np.ones_like(h)]); n /= np.linalg.norm(n, axis=2, keepdims=True)
    lam = np.clip(n @ LIGHT, 0, 1); nz = n[..., 2]
    hv = (LIGHT + [0, 0, 1]); hv /= np.linalg.norm(hv); sp = np.clip(n @ hv, 0, 1) ** 24
    k = amb + (1 - amb) * 1.15 * lam
    k = k * (rim + (1 - rim) * nz ** 0.6)
    noise = rng.standard_normal(mask.shape).astype(np.float32)
    L = 3 * SS; kx = cv2.getGaussianKernel(int(L * 4) | 1, L); ky = cv2.getGaussianKernel(5, 0.6 * SS)
    ker = (ky @ kx.T).astype(np.float32)
    M = cv2.getRotationMatrix2D((ker.shape[1] / 2, ker.shape[0] / 2), -math.degrees(grain_dir), 1)
    sz = max(ker.shape); kp = np.zeros((sz, sz), np.float32); kp[(sz - ker.shape[0]) // 2:(sz - ker.shape[0]) // 2 + ker.shape[0], :ker.shape[1]] = ker
    kp = cv2.warpAffine(kp, cv2.getRotationMatrix2D((sz / 2, sz / 2), -math.degrees(grain_dir), 1), (sz, sz))
    nz_ = cv2.filter2D(noise, -1, kp / kp.sum()); nz_ /= (nz_.std() + 1e-6)
    tex_k = 1 + grain * nz_
    rgb = np.asarray(base, np.float32)[None, None] * (k * tex_k)[..., None] + 255 * spec * sp[..., None]
    # warm subsurface tint in the shadow side (like the 3D render)
    rgb = rgb + (1 - lam)[..., None] * np.array([6, -2, -4], np.float32)
    return np.clip(rgb, 0, 255), d

def outline(rgb, d, w=1.6, k=0.72):
    e = np.clip(1 - (d - 0.5) / (w * SS), 0, 1); return rgb * (1 - (1 - k) * e)[..., None]

def finish(rgb, mask):
    """downsample SS -> 1x, premultiplied-safe."""
    al = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 0.5 * SS)
    h, w = mask.shape; H, W = h // SS, w // SS
    pm = cv2.resize(rgb * al[..., None], (W, H), interpolation=cv2.INTER_AREA)
    a = cv2.resize(al, (W, H), interpolation=cv2.INTER_AREA)
    rgb1 = pm / np.maximum(a[..., None], 1e-4)
    return np.dstack([np.clip(rgb1, 0, 255), np.clip(a * 255, 0, 255)]).astype(np.uint8)

def tube(L, r0, r1, cap0=True, cap1=True, pad=8, bulge=0.0, bpos=0.4):
    """mask of a tapered limb along +x from (pad+r0, cy) to (pad+r0+L, cy). returns mask, a, b (1x coords)."""
    W = int(pad * 2 + r0 + L + r1 + 2); Hh = int(pad * 2 + 2 * max(r0, r1) * (1 + bulge) + 2); cy = Hh / 2
    ax = pad + r0
    yy, xx = np.mgrid[0:Hh * SS, 0:W * SS].astype(np.float32) / SS
    t = np.clip((xx - ax) / L, 0, 1); r = r0 + (r1 - r0) * t + bulge * r0 * np.exp(-((t - bpos) / 0.28) ** 2)
    inside = (np.abs(yy - cy) <= r) & (xx >= ax) & (xx <= ax + L)
    if cap0: inside |= (xx - ax) ** 2 + (yy - cy) ** 2 <= r0 ** 2
    if cap1: inside |= (xx - ax - L) ** 2 + (yy - cy) ** 2 <= r1 ** 2
    return inside.astype(np.float32), (ax, cy), (ax + L, cy)

def poly_mask(shape1x, pts):
    m = np.zeros((shape1x[0] * SS, shape1x[1] * SS), np.uint8)
    cv2.fillPoly(m, [np.round(np.array(pts) * SS).astype(np.int32)], 1, lineType=cv2.LINE_AA); return m.astype(np.float32)

def ellipse_mask(shape1x, c, ax, ang=0.0):
    m = np.zeros((shape1x[0] * SS, shape1x[1] * SS), np.uint8)
    cv2.ellipse(m, (int(c[0] * SS), int(c[1] * SS)), (int(ax[0] * SS), int(ax[1] * SS)), ang, 0, 360, 1, -1, cv2.LINE_AA)
    return m.astype(np.float32)

def smooth_curve(pts, n=200):
    """Catmull-Rom closed curve through pts."""
    P = np.array(pts, float); out = []
    for i in range(len(P)):
        p0, p1, p2, p3 = P[i - 1], P[i], P[(i + 1) % len(P)], P[(i + 2) % len(P)]
        for t in np.linspace(0, 1, n // len(P), endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return np.array(out)

parts = {}
def save(name, img, a, b, scale=1.0):
    cv2.imwrite(OUT + name + '.png', cv2.cvtColor(img, cv2.COLOR_RGBA2BGRA))
    parts[name] = dict(a=[float(a[0]), float(a[1])], b=[float(b[0]), float(b[1])], scale=scale)

# ---------------- limbs (fur) ----------------
def cyl_shade(m, a, b, r0, r1, col, grain=0.022):
    """cylinder shading around the bone (no dome at the caps, so overlapping joints read as one continuous limb)."""
    Hh, W = m.shape; yy, xx = np.mgrid[0:Hh, 0:W].astype(np.float32) / SS
    L = b[0] - a[0]; t = np.clip((xx - a[0]) / L, 0, 1); r = r0 + (r1 - r0) * t
    ny = np.clip((yy - a[1]) / r, -1, 1); nz = np.sqrt(np.clip(1 - ny ** 2, 0, 1))
    n = np.dstack([np.zeros_like(ny), ny, nz])
    lam = np.clip(n @ LIGHT, 0, 1); hv = (LIGHT + [0, 0, 1]); hv /= np.linalg.norm(hv); sp = np.clip(n @ hv, 0, 1) ** 24
    k = (0.50 + 0.575 * lam) * (0.80 + 0.20 * nz ** 0.6)
    noise = cv2.GaussianBlur(rng.standard_normal(m.shape).astype(np.float32), (0, 0), sigmaX=3 * SS, sigmaY=0.6 * SS)
    noise /= noise.std() + 1e-6
    rgb = np.asarray(col, np.float32)[None, None] * (k * (1 + grain * noise))[..., None] + 255 * 0.10 * sp[..., None]
    rgb = rgb + (1 - lam)[..., None] * np.array([6, -2, -4], np.float32)
    # soft outline on the long sides only (fades out over the proximal cap)
    e = np.clip((np.abs(ny) - 0.86) / 0.14, 0, 1) * np.clip((xx - a[0]) / (0.6 * r0) + 1, 0, 1)
    return np.clip(rgb * (1 - 0.26 * e)[..., None], 0, 255)
def limb(name, L, r0, r1, col, bulge=0.0, bpos=0.4, cap1=True):
    m, a, b = tube(L, r0, r1, bulge=bulge, bpos=bpos, cap1=cap1)
    rgb = cyl_shade(m, a, b, r0 * (1 + bulge * 0.5), r1, col); save(name, finish(rgb, m), a, b)
limb('ua', 103, 19, 16, C['arm'] * 0.97, bulge=0.08, bpos=0.25)
limb('fa', 94, 16, 12.5, C['arm'] * 0.97, bulge=0.06, bpos=0.3)
limb('th', 138, 31, 23, FUR * 1.06, bulge=0.06, bpos=0.3)
limb('sh', 143, 23, 16, FUR * 1.06, bulge=0.10, bpos=0.28)
m, a, b = tube(0.2, 21, 21); rgb = cyl_shade(m, a, b, 21, 21, C['arm'] * 0.97); save('delt', finish(rgb, m), a, b)

# ---------------- side hand (mitten profile: palm, finger block with grooves, thumb on the palm side) ----------------
def hand():
    W, H = 92, 70; ax, cy = 14, 35; L = 58
    pts = [(ax - 4, cy - 14), (ax + 18, cy - 17), (ax + 40, cy - 15), (ax + 54, cy - 11), (ax + 61, cy - 3), (ax + 60, cy + 6),
           (ax + 52, cy + 11), (ax + 34, cy + 12), (ax + 26, cy + 20), (ax + 16, cy + 22), (ax + 8, cy + 17), (ax - 4, cy + 13)]
    cur = smooth_curve(pts, 240); m = poly_mask((H, W), cur)
    rgb, d = shade(m, C['hand'], R=14 * SS)
    # finger grooves + thumb crease
    lines = np.zeros_like(m)
    for k_, (x0, y0, x1, y1) in enumerate([(ax + 32, cy - 2, ax + 58, cy - 4), (ax + 32, cy + 5, ax + 55, cy + 5)]):
        cv2.line(lines, (int(x0 * SS), int(y0 * SS)), (int(x1 * SS), int(y1 * SS)), 1, int(1.3 * SS), cv2.LINE_AA)
    cv2.ellipse(lines, (int((ax + 25) * SS), int((cy + 11) * SS)), (int(9 * SS), int(5 * SS)), 20, 200, 330, 1, int(1.3 * SS), cv2.LINE_AA)
    lines = cv2.GaussianBlur(lines, (0, 0), 0.8 * SS)
    rgb = rgb * (1 - 0.28 * lines)[..., None]
    # fur cuff at the wrist
    cuff = (np.mgrid[0:H * SS, 0:W * SS][1] / SS < ax + 5).astype(np.float32) * m
    cuff = cv2.GaussianBlur(cuff, (0, 0), 1.5 * SS)
    rgbf, _ = shade(m, C['arm'] * 0.97, R=14 * SS)
    rgb = rgb * (1 - cuff[..., None]) + rgbf * cuff[..., None]
    save('hand', finish(outline(rgb, d), m), (ax, cy), (ax + L, cy))
hand()

# ---------------- side foot (long monkey foot: round heel, flat sole at +y, toes with grooves at b) ----------------
def foot():
    W, H = 120, 66; ax, cy = 22, 26; L = 61         # a = ankle, b = toe; sole on the +y side (like the T-stand left foot)
    pts = [(ax - 14, cy - 14), (ax + 2, cy - 18), (ax + 14, cy - 12), (ax + 34, cy - 4), (ax + 56, cy + 0), (ax + 70, cy + 6),
           (ax + 72, cy + 15), (ax + 64, cy + 22), (ax + 40, cy + 24), (ax + 10, cy + 25), (ax - 12, cy + 23), (ax - 20, cy + 12), (ax - 20, cy - 2)]
    cur = smooth_curve(pts, 300); m = poly_mask((H, W), cur)
    rgb, d = shade(m, C['foot'], R=13 * SS)
    lines = np.zeros_like(m)
    for (x0, y0, x1, y1) in [(ax + 52, cy + 8, ax + 70, cy + 11), (ax + 50, cy + 15, ax + 66, cy + 18)]:
        cv2.line(lines, (int(x0 * SS), int(y0 * SS)), (int(x1 * SS), int(y1 * SS)), 1, int(1.3 * SS), cv2.LINE_AA)
    lines = cv2.GaussianBlur(lines, (0, 0), 0.8 * SS); rgb = rgb * (1 - 0.25 * lines)[..., None]
    # fur at the ankle (top-back of the foot), sole a touch lighter
    yy, xx = np.mgrid[0:H * SS, 0:W * SS] / SS
    cuff = np.clip(1 - np.hypot((xx - (ax - 2)) / 17, (yy - (cy - 8)) / 14), 0, 1) ** 0.6 * m
    rgbf, _ = shade(m, FUR * 1.06, R=13 * SS)
    rgb = rgb * (1 - cuff[..., None]) + rgbf * cuff[..., None]
    sole = np.clip((yy - (cy + 17)) / 6, 0, 1) * m; rgb = rgb * (1 + 0.06 * sole[..., None])
    save('foot', finish(outline(rgb, d), m), (ax, cy), (ax + L, cy))
foot()

# ---------------- side torso (upright: neck a at top, hip b at bottom, belly/front = +x) ----------------
def torso():
    W, H = 190, 300; cx = 95; ny, hy = 40, 240           # neck / hip joint (bone 200)
    s = lambda f: ny + f * (hy - ny)
    front = [(cx + 28, s(-0.10)), (cx + 44, s(0.10)), (cx + 54, s(0.30)), (cx + 62, s(0.55)), (cx + 62, s(0.76)), (cx + 50, s(0.96)), (cx + 28, s(1.12))]
    back = [(cx - 24, s(1.18)), (cx - 50, s(1.06)), (cx - 56, s(0.86)), (cx - 47, s(0.62)), (cx - 44, s(0.40)), (cx - 47, s(0.18)), (cx - 36, s(0.0)), (cx - 26, s(-0.10))]
    pts = front + back + [(cx, s(-0.14))]
    cur = smooth_curve(pts, 400); m = poly_mask((H, W), cur)
    rgb, d = shade(m, C['torso'] * 1.04, grain_dir=math.pi / 2, grain=0.018, R=52 * SS)
    # belly patch on the front (rounded oval, like the front art's patch seen from the side)
    yy, xx = np.mgrid[0:H * SS, 0:W * SS] / SS
    e = ((xx - (cx + 54)) / 34) ** 2 + ((yy - s(0.55)) / 80) ** 2
    bm = np.clip((1.0 - e) / 0.10, 0, 1) * m
    bm = cv2.GaussianBlur(bm.astype(np.float32), (0, 0), 0.7 * SS)
    rgbb, _ = shade(m, C['belly'] * 1.02, grain=0.012, R=52 * SS, amb=0.74, rim=0.88)
    rgb = rgb * (1 - bm[..., None]) + rgbb * bm[..., None]
    # soft shadow line at the patch edge (the 3D render has a slight step)
    edge = np.clip(1 - np.abs(e - 1.0) / 0.06, 0, 1) * m * (xx < cx + 54)
    rgb = rgb * (1 - 0.10 * cv2.GaussianBlur(edge.astype(np.float32), (0, 0), 0.8 * SS))[..., None]
    rgb = outline(rgb, d, 1.8)
    img = finish(rgb, m)
    # bead collar (side arc), colours sampled from the Triangle necklace
    beads = [(224, 120, 40), (240, 170, 60), (196, 70, 40), (230, 140, 50)]
    can = img.astype(np.float32)
    for i in range(7):
        u = i / 6; x = cx + 34 - 66 * u + 6 * math.sin(u * math.pi); y = s(0.02) + 16 * math.sin(u * math.pi) * 0.8 + 10 * u
        if x < cx - 30: continue
        r = 6.2 if i % 2 == 0 else 5.0; col = np.array(beads[i % 4], np.float32)
        bm_ = np.zeros((H * SS, W * SS), np.float32); cv2.circle(bm_, (int(x * SS), int(y * SS)), int(r * SS), 1, -1, cv2.LINE_AA)
        brgb, bd = shade(bm_, col, grain=0.0, spec=0.35, R=r * SS)
        bi = finish(outline(brgb, bd, 1.2, 0.6), bm_).astype(np.float32)
        al = bi[..., 3:] / 255; can[..., :3] = can[..., :3] * (1 - al) + bi[..., :3] * al; can[..., 3:] = np.maximum(can[..., 3:], bi[..., 3:])
    save('torso', np.clip(can, 0, 255).astype(np.uint8), (cx, ny), (cx, hy))
torso()

# ---------------- profile head (derived from the real Triangle art) ----------------
def head():
    hp = cv2.cvtColor(cv2.imread(D + 'tex_headprof.png', -1), cv2.COLOR_BGRA2RGBA).astype(np.float32)   # 600x600, 3x, faces image-left
    ax, ay, S = [float(v) for v in open(D + 'headprof_anchor.txt').read().split()]
    H, W = hp.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    al = hp[..., 3] / 255
    fx = np.zeros((H, W), np.uint8); fx[292:334, 112:142] = 1
    pale = (fx > 0) & (hp[..., :3].min(2) > 150)
    pale = cv2.dilate(pale.astype(np.uint8), np.ones((5, 5), np.uint8))
    hp[..., :3] = cv2.inpaint(np.clip(hp[..., :3], 0, 255).astype(np.uint8), pale, 6, cv2.INPAINT_TELEA).astype(np.float32)
    rgb0 = hp[..., :3]; lum = rgb0 @ np.array([.3, .59, .11]); sat = rgb0.max(2) - rgb0.min(2)
    # the art's own fur colour (top/back of the real head)
    fm = (al > 0.95) & (xx > 230) & (xx < 330) & (yy > 195) & (yy < 270) & (sat > 60) & (lum < 140)
    furc = np.median(rgb0[fm], 0)
    # remove cream matte fringe + pale junk at the neck, feather the art into the painted skull toward the back
    inside = (al > 0.5).astype(np.uint8); dist = cv2.distanceTransform(inside, cv2.DIST_L2, 5)
    fringe = (dist < 14) & (lum > 150) & (sat < 95)
    al = np.where(fringe | ((yy > 440) & (sat < 80)), 0, al)
    al = cv2.erode(al, np.ones((3, 3), np.uint8))
    fade = np.clip((345 - xx) / 55, 0, 1) ** 1.3
    topf = np.clip((yy - 172) / 26, 0, 1)
    al = al * np.where(xx > 250, np.minimum(fade, np.maximum(topf, (xx < 250))), 1)
    global SS
    ss0 = SS; SS = 1
    sk = np.zeros((H, W), np.float32); cv2.ellipse(sk, (268, 300), (150, 138), 0, 0, 360, 1, -1, cv2.LINE_AA)
    nk = np.zeros((H, W), np.float32); cv2.ellipse(nk, (296, 420), (70, 58), 0, 0, 360, 1, -1, cv2.LINE_AA)
    skm = np.clip(sk + nk, 0, 1)
    srgb, sd = shade(skm, furc * 1.02, grain=0.03, R=130, amb=0.62, spec=0.05)
    srgb = outline(srgb, sd, 4.0, 0.80)
    em = np.zeros((H, W), np.float32); cv2.ellipse(em, (360, 298), (36, 46), -10, 0, 360, 1, -1, cv2.LINE_AA)
    erg, ed = shade(em, C['ear'] * 1.03, R=30, grain=0.0, amb=0.62)
    im_ = np.zeros((H, W), np.float32); cv2.ellipse(im_, (364, 301), (22, 31), -10, 0, 360, 1, -1, cv2.LINE_AA)
    im_ = cv2.GaussianBlur(im_, (0, 0), 3.0)
    irg = np.ones((H, W, 3), np.float32) * C['face'][None, None] * 0.97
    irg = irg * (0.80 + 0.20 * np.clip((xx[..., None] - 345) / 35, 0, 1))
    erg = erg * (1 - im_[..., None]) + irg * im_[..., None]
    erg = outline(erg, ed, 3.0, 0.72)
    SS = ss0
    out = srgb * skm[..., None]; oa = skm.copy()
    a2 = cv2.GaussianBlur(al.astype(np.float32), (0, 0), 1.2)
    out = out * (1 - a2[..., None]) + hp[..., :3] * a2[..., None]; oa = np.maximum(oa, a2)
    ea = cv2.GaussianBlur(em, (0, 0), 0.8)
    out = out * (1 - ea[..., None]) + erg * ea[..., None]; oa = np.maximum(oa, ea)
    img = np.dstack([out / np.maximum(oa[..., None], 1e-4), oa * 255]); img = np.clip(img, 0, 255).astype(np.uint8)
    save('head', img, (ax, ay), (ax, ay - 128 * S), scale=S)
head()
json.dump(dict(parts=parts, colours={k: [round(float(x)) for x in v] for k, v in C.items()}, fur=[round(float(x)) for x in FUR]), open(OUT + 'parts.json', 'w'), indent=1)
print('wrote', sorted(parts))
