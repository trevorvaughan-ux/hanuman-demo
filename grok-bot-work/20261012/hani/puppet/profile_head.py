"""Build a profile-ish 'looking over the shoulder' head from the 3/4 Triangle head art:
horizontal warp (features slide toward the turn side, muzzle pushed past the skull line, back of head widens)
+ pupils repainted looking away from the camera. Output: puppet/tex_headprof.png (upright, turned to image-left)."""
import sys, numpy as np, cv2
sys.path.insert(0, '/workspace/hani/puppet'); import rig
P = rig.Puppet()
ROT = float(sys.argv[1]) if len(sys.argv) > 1 else 14.0
KW = float(sys.argv[2]) if len(sys.argv) > 2 else 0.48
EW = float(sys.argv[3]) if len(sys.argv) > 3 else 0.30
S = 3.0                          # work at 3x for clean pupils
Wc, Hc = 600, 600; ax, ay = 300, 470   # neck anchor in the work canvas
def upright(part):
    acc = np.zeros((Hc, Wc, 4), np.float32)
    vs = part.b - part.a; L = np.linalg.norm(vs); us = vs / L
    Rs = np.array([[us[0], us[1]], [-us[1], us[0]]]); Rt = np.array([[0, 1], [-1, 0]])   # local u -> up
    M = S * Rt @ Rs; t = np.array([ax, ay]) - M @ part.a
    return cv2.warpAffine(part.img, np.hstack([M, t[:, None]]), (Wc, Hc), flags=cv2.INTER_CUBIC), M, t
img, M, t = upright(P.P['head34L'])
R = cv2.getRotationMatrix2D((ax, ay), ROT, 1.0); img = cv2.warpAffine(img, R, (Wc, Hc), flags=cv2.INTER_CUBIC)
al = img[..., 3]
ys, xs = np.where(al > 0.5); cx = (xs.min() + xs.max()) / 2; hw = (xs.max() - xs.min()) / 2
y0, y1 = ys.min(), ys.max(); print('head box', xs.min(), xs.max(), y0, y1)
# --- horizontal warp ---
k = KW          # features slide left
e = EW          # muzzle protrusion (fraction of half-width) in the muzzle band
my0, my1 = y0 + 0.50 * (y1 - y0), y0 + 0.95 * (y1 - y0)
mapx = np.zeros((Hc, Wc), np.float32); mapy = np.repeat(np.arange(Hc, dtype=np.float32)[:, None], Wc, 1)
us = np.linspace(-1.4, 1.4, 2000)
for y in range(Hc):
    band = 0.0
    if my0 < y < my1: band = np.sin(np.pi * (y - my0) / (my1 - my0)) ** 1.2
    f = us - k * np.clip(1 - us ** 2, 0, None) - e * band * np.clip(-us, 0, None) ** 1.5 * (us < 0) * 1.0
    f = np.maximum.accumulate(f)            # keep monotonic
    ud = (np.arange(Wc) - cx) / hw
    mapx[y] = cx + hw * np.interp(ud, f, us, left=-9, right=9)
warped = cv2.remap(img, mapx, mapy, cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
warped = np.clip(warped, 0, None)
cv2.imwrite('/workspace/hani/puppet/prof_dbg_a.png', cv2.cvtColor(np.clip(np.dstack([img[..., :3] / np.maximum(img[..., 3:], 1e-3), img[..., 3:] * 255]) , 0, 255).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
# --- repaint pupils looking away (toward image-left = over the shoulder) ---
a_ = warped[..., 3]; rgbw = warped[..., :3] / np.maximum(a_[..., None], 1e-3)
lum = rgbw @ np.array([0.3, 0.59, 0.11]); sat = rgbw.max(2) - rgbw.min(2)
eyeband = np.zeros_like(a_, bool); eyeband[int(y0 + 0.18 * (y1 - y0)):int(y0 + 0.50 * (y1 - y0)), int(cx - hw):int(cx + 0.35 * hw)] = True
white = eyeband & (a_ > 0.9) & (lum > 175) & (sat < 90)
nl, lab, st, cen = cv2.connectedComponentsWithStats(white.astype(np.uint8))
eyes = sorted([i for i in range(1, nl) if st[i, 4] > 60], key=lambda i: -st[i, 4])[:2]
print('eye whites', [(tuple(cen[i].round()), st[i, :]) for i in eyes])
sclera = np.median(rgbw[white], 0)
newp = []
for i in eyes:
    x, y, w, h, _ = st[i]
    bx0, by0, bx1, by1 = int(x - 0.35 * w), int(y - 0.4 * h), int(x + w * 1.35), int(y + h * 1.4)
    box = np.zeros_like(white); box[by0:by1, bx0:bx1] = True
    hull = cv2.convexHull(np.column_stack(np.where(lab == i)[::-1]).astype(np.int32))
    hm = np.zeros(white.shape, np.uint8); cv2.fillConvexPoly(hm, hull, 1)
    hm = cv2.dilate(hm, np.ones((9, 9), np.uint8)) > 0
    pm = hm & (lum < 120) & (a_ > 0.9)
    if pm.sum() < 20: continue
    yy, xx = np.where(pm); r = 0.5 * min(xx.max() - xx.min(), yy.max() - yy.min()) + 1
    rgbw[cv2.dilate(pm.astype(np.uint8), np.ones((3, 3), np.uint8)) > 0] = sclera
    hx = np.where(hm)[1]
    nx = hx.min() + r * 1.15; ny = yy.mean() + 0.1 * r
    newp.append((nx, ny, r))
print('new pupils', newp)
can = (rgbw * 1).astype(np.float32)
for nx, ny, r in newp:
    cv2.circle(can, (int(round(nx * 4)), int(round(ny * 4))), int(round(r * 1.05 * 4)), (58, 34, 22), -1, cv2.LINE_AA, 2)
    cv2.circle(can, (int(round((nx - 0.35 * r) * 4)), int(round((ny - 0.35 * r) * 4))), int(round(r * 0.3 * 4)), (255, 250, 240), -1, cv2.LINE_AA, 2)
warped = np.dstack([can * a_[..., None], a_]).astype(np.float32)
np.save('/workspace/hani/puppet/prof_warped.npy', warped)
cv2.imwrite('/workspace/hani/puppet/tex_headprof.png', cv2.cvtColor(np.dstack([can, a_ * 255]).clip(0, 255).astype(np.uint8), cv2.COLOR_RGBA2BGRA))
open('/workspace/hani/puppet/headprof_anchor.txt', 'w').write(f'{ax} {ay} {S}')
rgb = warped[..., :3] / np.maximum(warped[..., 3:], 1e-3)
out = np.dstack([rgb, warped[..., 3:] * 255]).clip(0, 255).astype(np.uint8)
cv2.imwrite('/workspace/hani/puppet/prof_dbg_b.png', cv2.cvtColor(out, cv2.COLOR_RGBA2BGRA))
bg = np.full((Hc, Wc * 2, 3), (200, 230, 200), np.float32)
for i, im in enumerate([img, warped]):
    bg[:, i * Wc:(i + 1) * Wc] = bg[:, i * Wc:(i + 1) * Wc] * (1 - im[..., 3:]) + im[..., :3]
cv2.imwrite('/workspace/hani/puppet/prof_cmp.png', cv2.cvtColor(bg.clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)[150:500])
bg = np.full((Hc, Wc * 2, 3), (200, 230, 200), np.float32)
for i, im in enumerate([img, warped]):
    bg[:, i * Wc:(i + 1) * Wc] = bg[:, i * Wc:(i + 1) * Wc] * (1 - im[..., 3:]) + im[..., :3]
import time; fn = f'/workspace/hani/puppet/prof_cmp_{int(time.time())}.png'
cv2.imwrite(fn, cv2.cvtColor(bg.clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)[130:520]); print(fn)
