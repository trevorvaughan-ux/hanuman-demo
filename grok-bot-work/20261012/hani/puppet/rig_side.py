"""Side-view / floor mode for the cut-out Hani puppet (config "mode": "side").
Same Triangle cut-out art as rig.py / rig3.py (limbs, hands, feet, torso, 3/4 head); nothing is redrawn.
The body is seen from the side: every segment takes Julie's segment DIRECTION (smoothed, rate limited, joint limited)
and Hani's own segment LENGTH, so proportions stay Hani's. Then the whole body is grounded: the lowest point of the
drawn body sits exactly on the floor line and the horizontal position follows whatever Julie has on the floor
(knees, feet, hands, hips), so planted parts don't skate.
- Joint limits (signed, relative to the facing direction): knees flex one way only (-3..165 deg), elbows one way only
  (-5..150 deg), neck +-80 deg, wrist +-55 deg. No backward knees/elbows.
- Optional "attach" targets: hands to heels (Camel), hands holding ankles (Bow), hands planted on the floor
  (Sun A folds / plank / down dog). Arm IK keeps the elbow on the anatomical side.
- Far-side limbs are drawn behind the torso, slightly darker and offset for depth; near-side limbs in front.
- Torso = the twisted torso variant (belly slid toward the front, far-side shading) narrowed to a side width.
- Head = the 3/4 Triangle head turned to the facing direction (or the front head when 'look_cam' > 0.5).
Nothing here runs unless a config says "mode": "side"."""
import math, sys
import numpy as np, cv2, cairo
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '/workspace/hani/puppet')
import rig as R
import rig3 as R3
from rig import Part, put, smooth, SRC_T

def wrap(a): return (a + np.pi) % (2 * np.pi) - np.pi
def dirv(a): return np.stack([np.cos(a), np.sin(a)], -1)

def _dark(part, k):
    p = Part.__new__(Part); p.img = part.img.copy(); p.img[..., :3] *= k; p.a = part.a.copy(); p.b = part.b.copy(); return p

def put_bent(canvas, part, H, th0, beta, chord, sp):
    """Draw the torso part along a circular arc (spine arch). H = hip point, th0 = spine tangent angle at the hip
    (pointing to the neck), beta = signed total bend (rad, screen angle), chord = hip->shoulder chord length.
    Straight case = rig.put(part, neck, hip). Premultiplied compositing like rig.put."""
    if abs(beta) < 1e-3:
        d = np.array([math.cos(th0), math.sin(th0)]); put(canvas, part, H + d * chord, H, sp); return
    Lt = chord / (math.sin(beta / 2) / (beta / 2))                 # arc length
    a, b = part.a, part.b; ls = float(np.linalg.norm(a - b)); us = (a - b) / ls; ns = np.array([-us[1], us[0]])
    sa = Lt / ls; k = beta / Lt; rho = 1 / k
    C = H + rho * np.array([-math.sin(th0), math.cos(th0)])
    h, w = part.img.shape[:2]; pad = (max(h, w) * max(sa, sp)) + 10
    Hc, Wc = canvas.shape[:2]
    end = H + np.array([math.cos(th0 + beta / 2), math.sin(th0 + beta / 2)]) * chord
    x0 = int(max(0, min(H[0], end[0]) - 0.8 * pad)); x1 = int(min(Wc, max(H[0], end[0]) + 0.8 * pad))
    y0 = int(max(0, min(H[1], end[1]) - 0.8 * pad)); y1 = int(min(Hc, max(H[1], end[1]) + 0.8 * pad))
    if x1 <= x0 or y1 <= y0: return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    dx = xx - C[0]; dy = yy - C[1]; r = np.sqrt(dx * dx + dy * dy) + 1e-6
    sgn = 1.0 if rho > 0 else -1.0
    nx, ny = -sgn * dx / r, -sgn * dy / r                       # unit normal (-sin th, cos th)
    th = np.arctan2(-nx, ny)
    sarc = ((th - th0 + np.pi) % (2 * np.pi) - np.pi) / k        # arc length from the hip
    v = rho - sgn * r                                            # lateral offset along the normal
    srcx = b[0] + us[0] * sarc / sa + ns[0] * v / sp
    srcy = b[1] + us[1] * sarc / sa + ns[1] * v / sp
    bad = (sarc < -0.4 * Lt) | (sarc > 1.4 * Lt)
    srcx[bad] = -10; srcy[bad] = -10
    wimg = cv2.remap(part.img, srcx.astype(np.float32), srcy.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = wimg[..., 3:4]; reg = canvas[y0:y1, x0:x1]
    reg *= (1 - al); reg += wimg[..., :3]

def defringe(part, rim=2.5, edge_dark=0.88):
    """Side-mode copy of a part: the thin cream rim left by the Triangle matte (visible when limbs overlap the body in
    side view) is replaced by the fur colour from just inside, and the outermost pixels are darkened a little
    (soft cartoon outline). The original parts used by the other modes are not touched."""
    img = part.img; al = img[..., 3]; rgb = img[..., :3] / np.maximum(al[..., None], 1e-3)
    inside = (al > 0.5).astype(np.uint8)
    dist = cv2.distanceTransform(np.pad(inside, 1), cv2.DIST_L2, 3)[1:-1, 1:-1]
    good = (dist > rim + 1).astype(np.float32); col = rgb * good[..., None]; acc = good.copy()
    k = np.ones((3, 3), np.float32)
    for _ in range(int(rim) + 4):
        c2 = cv2.filter2D(col, -1, k); a2 = cv2.filter2D(acc, -1, k)
        fill = (acc < 0.5) & (a2 > 0)
        col[fill] = c2[fill] / a2[fill][:, None]; acc[fill] = 1.0
    rimm = (dist <= rim + 1) & (acc > 0.5)
    rgb = np.where(rimm[..., None], col, rgb)
    shade = 1 - (1 - edge_dark) * np.clip(1 - (dist - 0.5) / 2.0, 0, 1)
    rgb = rgb * shade[..., None]
    p = Part.__new__(Part); p.img = np.dstack([rgb * al[..., None], al]).astype(np.float32); p.a = part.a.copy(); p.b = part.b.copy(); return p

class PuppetSide(R3.Puppet3):
    SEGS = ('ua', 'fa', 'hand', 'th', 'sh', 'ft', 'delt')
    def __init__(self, scfg=None):
        super().__init__()
        self.scfg = scfg or {}
        k = self.scfg.get('far_dark', 0.80)
        if self.scfg.get('defringe', True):
            for s in 'LR':
                for sg in self.SEGS: self.P[s + sg] = defringe(self.P[s + sg])
            self.torso_var = {kk: defringe(v) for kk, v in self.torso_var.items()}
        self.P['footS'] = self.P['Lft']; self.P['footSm'] = self.P['Lft'].mirrored()
        self.art = self.scfg.get('art')                  # opt-in side-view art set (Oct 12): "side3d"
        if self.art == 'side3d': self._load_side_art()
        self.P['DfootS'] = _dark(self.P['footS'], k); self.P['DfootSm'] = _dark(self.P['footSm'], k)
        for s in 'LR':
            for sg in self.SEGS: self.P['D' + s + sg] = _dark(self.P[s + sg], k)
        if self.art == 'side3d':
            self.P['DhandS'] = _dark(self.P['handS'], k); self.P['DhandSm'] = _dark(self.P['handSm'], k)
        self.lf = float(np.linalg.norm(self.SJ['Ltoe'] - self.SJ['Lan']))
        self.l1 = (float(np.linalg.norm(self.SJ['Lkn'] - self.SJ['Lhip'])) + float(np.linalg.norm(self.SJ['Rkn'] - self.SJ['Rhip']))) / 2
        self.l2 = (float(np.linalg.norm(self.SJ['Lan'] - self.SJ['Lkn'])) + float(np.linalg.norm(self.SJ['Ran'] - self.SJ['Rkn']))) / 2

    def _load_side_art(self):
        """Side-view Hani art set built by puppet/side_art.py (profile head from the real Triangle head art, painted side
        torso with belly patch + bead collar, side limbs/hands/feet in the Triangle colours). Only used when side.art == 'side3d'."""
        import json
        Dd = R.D + 'side_art/'; meta = json.load(open(Dd + 'parts.json'))['parts']
        def load(name):
            im = cv2.cvtColor(cv2.imread(Dd + name + '.png', -1), cv2.COLOR_BGRA2RGBA).astype(np.float32)
            al = im[..., 3:] / 255
            p = Part.__new__(Part); p.img = np.dstack([im[..., :3] * al, al]).astype(np.float32)
            p.a = np.array(meta[name]['a'], float); p.b = np.array(meta[name]['b'], float); return p, meta[name]['scale']
        for sg in ('ua', 'fa', 'th', 'sh', 'delt'):
            pt, _ = load(sg)
            for s in 'LR': self.P[s + sg] = pt
        hand, _ = load('hand')
        self.P['handS'] = hand; self.P['handSm'] = hand.mirrored()
        for s in 'LR': self.P[s + 'hand'] = hand
        ft, _ = load('foot'); self.P['footS'] = ft; self.P['footSm'] = ft.mirrored()
        to, _ = load('torso'); self.side_torso = {1: to, -1: to.mirrored()}
        hd, hs = load('head'); self.P['headSL'] = hd; self.P['headSR'] = hd.mirrored(); self.head_scale = hs

    # ------------------------------------------------------------------ whole-scene plan
    def plan_side(self, Js, phases, Tpx, cal, fps, scfg):
        n = len(Js); g = Tpx / SRC_T
        q = lambda J, k: np.array(J[k], float)
        A = lambda key: np.array([q(J, key) for J in Js])
        F = scfg['F']; back = -F                       # F: +1 facing image-right; back: angle sign of a backbend
        near = scfg.get('near', 'R')
        hip = (A('Lhip') + A('Rhip')) / 2; sh = (A('Lsh') + A('Rsh')) / 2; ear = A('ear')
        ang = lambda v: np.unwrap(np.arctan2(v[:, 1], v[:, 0]))
        th = {}
        th['t'] = ang(sh - hip)
        th['h'] = ang(ear - sh)
        for s in 'LR':
            th[s + 'th'] = ang(A(s + 'kn') - A(s + 'hip')); th[s + 'sh'] = ang(A(s + 'an') - A(s + 'kn'))
            th[s + 'ft'] = ang(A(s + 'toe') - A(s + 'heel'))
            th[s + 'ua'] = ang(A(s + 'el') - A(s + 'sh')); th[s + 'fa'] = ang(A(s + 'wr') - A(s + 'el'))
            th[s + 'hd'] = ang(A(s + 'idx') - A(s + 'wr'))
        def mirror(keys):
            for k in keys:
                d_ = wrap(th['L' + k] - th['R' + k]); m = th['R' + k] + d_ / 2
                th['L' + k] = th['R' + k] = m
        if scfg.get('mirror_legs'): mirror(('th', 'sh', 'ft'))     # legs move together in this pose (removes L/R noise)
        if scfg.get('mirror_arms'): mirror(('ua', 'fa', 'hd'))
        if scfg.get('arm_front'):
            # side view cannot show arms swept out to the SIDES (foreshortened): such sweeps read as arms flung behind the back.
            # Reflect any upper arm that points behind the torso plane to the front (|angle| from the torso axis); the
            # elbow bend and hand stay relative to the upper arm.
            for s in 'LR':
                rel = wrap(th[s + 'ua'] - th['t']) * F
                rfa = wrap(th[s + 'fa'] - th[s + 'ua']); rhd = wrap(th[s + 'hd'] - th[s + 'fa'])
                ua = th['t'] + np.abs(rel) * F
                th[s + 'ua'] = np.unwrap(ua); th[s + 'fa'] = th[s + 'ua'] + rfa; th[s + 'hd'] = th[s + 'fa'] + rhd
        for k, v in scfg.get('fixed', {}).items():                   # optional fixed segment angles (deg, F-relative)
            th[k] = np.full(n, math.radians(v) if F > 0 else math.pi - math.radians(v))
        FRONT = bool(scfg.get('front'))                            # (Oct 12 b2, opt-in) front-view floor/seated mode
        if FRONT: fsig = self._front_pre(th, hip, sh, ear, n, fps, scfg)
        vmax = math.radians(scfg.get('max_deg_per_frame', 5.0))
        sg_s = scfg.get('angle_sigma', 0.10)
        for k in th: th[k] = R3.rate_limit(gaussian_filter1d(th[k], max(0.5, sg_s * fps), mode='nearest'), vmax)
        L = dict(t=Tpx * scfg.get('torso_k', 1.0) * (fsig if FRONT else 1.0), h=128 * g, th=self.l1 * g, sh=self.l2 * g, ft=self.lf * g,
                 ua=self.len['ua'] * g, fa=self.len['fa'] * g, hd=58 * g)
        floor_y = scfg.get('floor_y', 902.0)
        # ---- spine arch (beta, signed; + = backbend): chord keeps Julie's hip->shoulder angle, the arc bends the chest
        lean = wrap(th['t'] + math.pi / 2) * back                                    # >0: leaning back
        bmag = scfg.get('arch_k', 0.0) * np.clip(lean - math.radians(scfg.get('arch_from', 10)), 0, math.radians(scfg.get('arch_max', 60)))
        if scfg.get('arch_prone'):   # lying on the belly: chest lifts = arch ~ k * lift angle of the chord above the floor
            lift = np.abs(wrap(th['t'] - (0 if F > 0 else math.pi)))
            bmag = np.maximum(bmag, scfg['arch_prone'] * np.clip(lift, 0, math.radians(45)))
        def lim(child, parent, lo, hi, sign):
            rel = wrap(th[child] - th[parent]) * sign
            rel = np.clip(rel, math.radians(lo), math.radians(hi))
            th[child] = th[parent] + rel * sign
        def fk(th, beta):
            P = {}
            b = np.asarray(beta) * back
            P['hm'] = np.zeros((n, 2))
            th0 = th['t'] - b / 2; th1 = th['t'] + b / 2
            hb = np.where(np.abs(b) < 1e-4, 1.0, np.sin(b / 2 + 1e-9) / (b / 2 + 1e-9))
            P['sm'] = P['hm'] + dirv(th['t']) * (L['t'] * hb)[:, None]
            ax1 = dirv(th1)
            P['neck'] = P['sm'] + ax1 * 6 * g; P['crown'] = P['neck'] + dirv(th['h']) * L['h']
            for s in 'LR':
                P[s + 'hip'] = P['hm'].copy(); P[s + 'sh'] = P['sm'] - ax1 * 4 * g
                if FRONT:   # front view: hips / shoulders spread sideways (perpendicular to the torso axis)
                    pv = np.stack([-ax1[:, 1], ax1[:, 0]], 1) * np.sign(ax1[:, 1:2] * -1 + 1e-9)
                    P[s + 'hip'] = P['hm'] + pv * self._fw[s + 'hip'] * g; P[s + 'sh'] = P[s + 'sh'] + pv * self._fw[s + 'sh'] * g
                P[s + 'kn'] = P[s + 'hip'] + dirv(th[s + 'th']) * L['th']; P[s + 'an'] = P[s + 'kn'] + dirv(th[s + 'sh']) * L['sh']
                P[s + 'toe'] = P[s + 'an'] + dirv(th[s + 'ft']) * L['ft']
                P[s + 'el'] = P[s + 'sh'] + dirv(th[s + 'ua']) * L['ua']; P[s + 'wr'] = P[s + 'el'] + dirv(th[s + 'fa']) * L['fa']
                P[s + 'tip'] = P[s + 'wr'] + dirv(th[s + 'hd']) * L['hd']
            P['_th0'] = th0; P['_th1'] = th1; P['_beta'] = b
            return P
        rad = dict(th=30, sh=24, ft=15, ua=17, fa=15, hd=12)
        def bottom(P, feet=True):
            b = np.full(n, -1e9)
            segs = [('hm', 'sm', scfg.get('torso_half', 0.72) * 50)]
            for s in 'LR':
                segs += [(s + 'hip', s + 'kn', rad['th']), (s + 'kn', s + 'an', rad['sh']),
                         (s + 'sh', s + 'el', rad['ua']), (s + 'el', s + 'wr', rad['fa']), (s + 'wr', s + 'tip', rad['hd'])]
                if feet: segs.append((s + 'an', s + 'toe', rad['ft']))
            for a_, b_, r in segs:
                for u in (0, 0.25, 0.5, 0.75, 1.0):
                    y = P[a_][:, 1] + (P[b_][:, 1] - P[a_][:, 1]) * u + r * g
                    b = np.maximum(b, y)
            hc = P['neck'] + (P['crown'] - P['neck']) * 0.45
            return np.maximum(b, hc[:, 1] + 62 * g)
        def limits():
            if FRONT: return                                         # front view: Julie's 2D directions, no side-view sign limits
            lim('h', 't', -scfg.get('neck_back', 80) - 40, scfg.get('neck_fwd', 80) + 40, F)
            for s in 'LR':
                lim(s + 'sh', s + 'th', -3, scfg.get('knee_max', 165), F)        # knee flexes toward the back only
                lim(s + 'fa', s + 'ua', -5, 150, -F)                              # elbow flexes toward the front only
                lim(s + 'hd', s + 'fa', -55, 55, 1)
        limits()
        # ---- feet: flat on the floor when the ankle is down (toes away from the knee when the shin lies on the floor,
        #      pointing forward when the shin stands up); Julie's foot angle otherwise
        P = fk(th, bmag); SOLE = {}
        dy0 = floor_y - bottom(P, feet=False)
        for s in 'LR':
            an_y = P[s + 'an'][:, 1] + dy0
            down = np.clip(((an_y - (floor_y - 0.30 * Tpx)) / (0.15 * Tpx)), 0, 1)
            sv = P[s + 'an'] - P[s + 'kn']; hor = np.abs(sv[:, 0]) / (np.linalg.norm(sv, axis=1) + 1e-9)
            away = np.sign(sv[:, 0]); away[away == 0] = -F
            fx = np.where(hor > scfg.get('foot_hor', 0.70), away, F)
            fx = np.where(np.isnan(fx), F, fx)
            tilt = np.arcsin(np.clip((floor_y - scfg.get('foot_gap', 14) * g - an_y) / L['ft'], -0.9, 0.9))
            flat = np.where(fx > 0, tilt, math.pi - tilt)
            flat = th[s + 'ft'] + wrap(flat - th[s + 'ft'])
            w = gaussian_filter1d(down * scfg.get('foot_flat', 1.0), 0.15 * fps, mode='nearest')
            th[s + 'ft'] = R3.rate_limit(gaussian_filter1d(th[s + 'ft'] * (1 - w) + flat * w, 0.12 * fps, mode='nearest'), vmax)
            lying = (hor > scfg.get('foot_hor', 0.70)) & (down > 0.5)
            soleN = np.where(lying[:, None], np.array([0.0, -1.0]), sv / (np.linalg.norm(sv, axis=1)[:, None] + 1e-9))
            SOLE[s] = gaussian_filter1d(soleN, 0.2 * fps, axis=0, mode='nearest')
        P = fk(th, bmag)
        # ---- hand attachments: hands to the heels (Camel) / around the ankles (Bow); the spine arches as needed
        att = scfg.get('attach', {})
        Tj = float(np.median(np.linalg.norm(sh - hip, axis=1)))
        info = {}; reach = (L['ua'] + L['fa']) * 0.985
        if att.get('heel') or att.get('ankle'):
            key = 'heel' if att.get('heel') else 'an'
            W = {}; T = {}
            for s in 'LR':
                jw = A(s + 'wr')
                d = np.minimum(np.linalg.norm(jw - A('L' + key), axis=1), np.linalg.norm(jw - A('R' + key), axis=1))
                r0, r1 = att.get('r0', 0.30), att.get('r1', 0.55)
                w = np.clip((r1 * Tj - d) / ((r1 - r0) * Tj), 0, 1)
                W[s] = gaussian_filter1d(w, 0.25 * fps, mode='nearest')
                fdir = dirv(th[s + 'ft'])
                T[s] = P[s + 'an'] + fdir * att.get('along', 0.15) * L['ft'] + np.array([0, -att.get('lift', 0.10) * L['sh']])
            if scfg.get('mirror_arms'): W['L'] = W['R'] = np.maximum(W['L'], W['R'])
            # minimal arch so that the shoulders can reach the targets
            grid = np.radians(np.arange(0, scfg.get('arch_need_max', 80) + 0.1, 2.0))
            need = np.full(n, grid[-1])
            for bg in grid[::-1]:
                Pb = fk(th, np.full(n, bg))
                ok = np.ones(n, bool)
                for s in 'LR': ok &= np.linalg.norm(T[s] - Pb[s + 'sh'], axis=1) <= reach
                need = np.where(ok, bg, need)
            wmax = np.maximum(W['L'], W['R'])
            bmag = bmag + wmax * np.maximum(need - bmag, 0)
            bmag = R3.rate_limit(gaussian_filter1d(bmag, 0.25 * fps, mode='nearest'), math.radians(2.0))
            P = fk(th, bmag)
            for s in 'LR':
                T[s] = P[s + 'an'] + dirv(th[s + 'ft']) * att.get('along', 0.15) * L['ft'] + np.array([0, -att.get('lift', 0.10) * L['sh']])
                a1n = np.zeros(n); a2n = np.zeros(n)
                for i in range(n): a1n[i], a2n[i] = self._ik(P[s + 'sh'][i], T[s][i], L['ua'], L['fa'], -F)
                a1n = th[s + 'ua'] + wrap(a1n - th[s + 'ua']); a2n = th[s + 'fa'] + wrap(a2n - th[s + 'fa'])
                w = W[s]
                th[s + 'ua'] = th[s + 'ua'] * (1 - w) + a1n * w
                th[s + 'fa'] = th[s + 'fa'] * (1 - w) + a2n * w
                hd_t = a2n + back * math.radians(att.get('hand_curl', 30))     # fingers wrap around the heel
                th[s + 'hd'] = th[s + 'hd'] * (1 - w) + (th[s + 'hd'] + wrap(hd_t - th[s + 'hd'])) * w
                info[s + 'attw'] = w
        if att.get('floor'):
            # hands planted on the floor (folds, plank, down dog, cobra): the torso hinges a little at the hip so that
            # Hani's own arm length reaches the floor with Julie's arm straightness, then 2-bone IK puts the hands down
            fr0, fr1 = att.get('fr0', 0.10), att.get('fr1', 0.28); FJ_ = scfg['FJ']
            Wf = {}
            for s in 'LR':
                jw = A(s + 'wr'); w = np.clip((jw[:, 1] - (FJ_ - fr1 * Tj)) / ((fr1 - fr0) * Tj), 0, 1)
                Wf[s] = gaussian_filter1d(w, 0.2 * fps, mode='nearest')
            if scfg.get('mirror_arms'): Wf['L'] = Wf['R'] = np.maximum(Wf['L'], Wf['R'])
            wmax = np.maximum(Wf['L'], Wf['R'])
            def bottom_legs(P):
                b = np.full(n, -1e9)
                segs = [('hm', 'sm', scfg.get('torso_half', 0.72) * 50)]
                for s in 'LR': segs += [(s + 'hip', s + 'kn', rad['th']), (s + 'kn', s + 'an', rad['sh']), (s + 'an', s + 'toe', rad['ft'])]
                for a_, b_, r in segs:
                    for u in (0, 0.25, 0.5, 0.75, 1.0):
                        b = np.maximum(b, P[a_][:, 1] + (P[b_][:, 1] - P[a_][:, 1]) * u + r * g)
                return b
            P0 = fk(th, bmag)
            ext0 = {s: np.linalg.norm(P0[s + 'wr'] - P0[s + 'sh'], axis=1) for s in 'LR'}
            hoff = {s: P0[s + 'wr'][:, 0] - P0[s + 'sh'][:, 0] for s in 'LR'}
            hgap = att.get('hand_gap', 13) * g
            best = np.zeros(n); bestc = np.full(n, 1e9)
            for d in np.radians(np.arange(-40, 40.1, 2.5)):
                th2 = dict(th); th2['t'] = th['t'] + d; th2['h'] = th['h'] + d
                Pd = fk(th2, bmag); dyl = floor_y - bottom_legs(Pd)
                cost = np.abs(d) / math.radians(40) * 0.5
                for s in 'LR':
                    shp = Pd[s + 'sh'] + np.stack([np.zeros(n), dyl], 1)
                    tx = hoff[s]; ty = (floor_y - hgap) - shp[:, 1]
                    dist = np.hypot(tx, ty)
                    bad = (dist > 0.97 * reach) | (ty < 0.0)
                    cost = cost + np.abs(np.minimum(dist, 0.97 * reach) - ext0[s]) / reach * 2 + bad * 50 + np.maximum(dist - 0.97 * reach, 0) / reach * 50
                upd = cost < bestc; best[upd] = d; bestc[upd] = cost[upd]
            dlt = R3.rate_limit(gaussian_filter1d(best * wmax, 0.25 * fps, mode='nearest'), math.radians(2.0))
            th['t'] = th['t'] + dlt; th['h'] = th['h'] + dlt
            P = fk(th, bmag); dyl = floor_y - bottom_legs(P)
            for s in 'LR':
                Tg = np.stack([P[s + 'sh'][:, 0] + hoff[s], (floor_y - hgap) - dyl], 1)
                a1n = np.zeros(n); a2n = np.zeros(n)
                for i in range(n): a1n[i], a2n[i] = self._ik(P[s + 'sh'][i], Tg[i], L['ua'], L['fa'], -F)
                a1n = th[s + 'ua'] + wrap(a1n - th[s + 'ua']); a2n = th[s + 'fa'] + wrap(a2n - th[s + 'fa'])
                w = Wf[s]
                th[s + 'ua'] = th[s + 'ua'] * (1 - w) + a1n * w; th[s + 'fa'] = th[s + 'fa'] * (1 - w) + a2n * w
                flat = np.full(n, 0.0 if F > 0 else math.pi) + F * math.radians(att.get('hand_tilt', 8))
                flat = th[s + 'hd'] + wrap(flat - th[s + 'hd'])
                th[s + 'hd'] = th[s + 'hd'] * (1 - w) + flat * w
                info[s + 'floorw'] = w
            info['hinge'] = np.degrees(dlt)
        if att.get('heart'):
            # hands together at the heart (prayer): Julie's wrists near her chest -> Hani's hands on the front of the chest, fingers up
            hd_ = att.get('heart_down', 0.25); r0, r1 = att.get('hr0', 0.25), att.get('hr1', 0.50)
            jc = sh + (hip - sh) * hd_
            P = fk(th, bmag)
            ax = P['sm'] - P['hm']; ax = ax / (np.linalg.norm(ax, axis=1)[:, None] + 1e-9)
            fwd = np.stack([-ax[:, 1] * F, ax[:, 0] * F], 1)
            Tg = P['sm'] + (P['hm'] - P['sm']) * hd_ + fwd * att.get('heart_front', 0.20) * Tpx
            Wh = {}
            for s in 'LR':
                d = np.linalg.norm(A(s + 'wr') - jc, axis=1)
                Wh[s] = gaussian_filter1d(np.clip((r1 * Tj - d) / ((r1 - r0) * Tj), 0, 1), 0.25 * fps, mode='nearest')
            if scfg.get('mirror_arms'): Wh['L'] = Wh['R'] = np.maximum(Wh['L'], Wh['R'])
            up = np.arctan2(ax[:, 1], ax[:, 0])
            for s in 'LR':
                a1n = np.zeros(n); a2n = np.zeros(n)
                for i in range(n): a1n[i], a2n[i] = self._ik(P[s + 'sh'][i], Tg[i], L['ua'], L['fa'], -F)
                a1n = th[s + 'ua'] + wrap(a1n - th[s + 'ua']); a2n = th[s + 'fa'] + wrap(a2n - th[s + 'fa'])
                w = Wh[s]
                th[s + 'ua'] = th[s + 'ua'] * (1 - w) + a1n * w; th[s + 'fa'] = th[s + 'fa'] * (1 - w) + a2n * w
                hu = th[s + 'hd'] + wrap(up - th[s + 'hd'])
                th[s + 'hd'] = th[s + 'hd'] * (1 - w) + hu * w
                info[s + 'heartw'] = w
        for k in th: th[k] = R3.rate_limit(gaussian_filter1d(th[k], max(0.5, 0.05 * fps), mode='nearest'), vmax)
        bmag = gaussian_filter1d(bmag, 0.05 * fps, mode='nearest')
        # head limit relative to the upper chest (after the arch)
        th1 = th['t'] + bmag * back / 2
        rel = wrap(th['h'] - th1) * F; rel = np.clip(rel, -math.radians(scfg.get('neck_back', 80)), math.radians(scfg.get('neck_fwd', 80)))
        if not FRONT: th['h'] = th1 + rel * F
        limits()
        P = fk(th, bmag)
        # ---- grounding: lowest point of the drawn body on the floor line; x follows Julie's planted parts
        dy = floor_y - bottom(P)
        dys = gaussian_filter1d(dy, 0.10 * fps, mode='nearest'); dy = np.minimum(dys, dy)      # never sink into the floor
        FJ = scfg['FJ']; keys = scfg.get('anchor', ['Lkn', 'Rkn', 'Lan', 'Ran', 'Lwr', 'Rwr', 'Lhip', 'Rhip', 'Ltoe', 'Rtoe'])
        num = np.zeros(n); den = np.zeros(n)
        for k in keys:
            jy = A(k)[:, 1]; w = np.clip((jy - (FJ - 0.35 * Tj)) / (0.25 * Tj), 0, 1) ** 2 + 1e-4
            num += w * (A(k)[:, 0] - P[k][:, 0]); den += w
        dx = num / den
        dx = R3.rate_limit(gaussian_filter1d(dx, scfg.get('anchor_sigma', 0.35) * fps, mode='nearest'), scfg.get('anchor_speed', 0.02) * Tpx)
        dx = dx + (scfg.get('center_x', 960.0) - np.median(dx + (P['hm'][:, 0] + P['sm'][:, 0]) / 2))
        off = np.stack([dx, dy], 1)
        for k in P:
            if not k.startswith('_'): P[k] = P[k] + off
        far = 'L' if near == 'R' else 'R'
        if scfg.get('stand_feet'):
            # (Oct 12, opt-in) standing upright: in profile both legs sit on one line and read as ONE leg (Sun A v1 Mountain
            # bug). When the torso is upright and both thighs + shins point down, both legs get the same (averaged) straight
            # angles, both feet flat on the floor line, and the far leg is staggered a little so two planted feet show.
            def vert(k):
                return np.abs(wrap(th[k] - math.pi / 2))
            up = np.clip((math.radians(25) - np.abs(wrap(th['t'] + math.pi / 2))) / math.radians(10), 0, 1)
            lg = np.ones(n)
            for s in 'LR':
                for k in (s + 'th', s + 'sh'): lg = lg * np.clip((math.radians(35) - vert(k)) / math.radians(12), 0, 1)
            ws = gaussian_filter1d(up * lg, 0.3 * fps, mode='nearest'); info['stand_w'] = ws
            sf = scfg['stand_feet'] if isinstance(scfg['stand_feet'], dict) else {}
            hipP = P['Lhip']; stg = sf.get('stagger', 0.10) * Tpx
            for s, off in ((near, 0.0), (far, stg * F)):
                # straight vertical leg from the hip, ankle on the floor line, foot flat pointing forward
                kn_t = hipP + np.array([off * 0.5, L['th']]); an_t = kn_t + np.array([off * 0.5, L['sh']])
                an_t[:, 1] = np.minimum(an_t[:, 1], floor_y - sf.get('foot_gap', 14) * g)
                kn_t = hipP + (an_t - hipP) * (L['th'] / (L['th'] + L['sh']))
                toe_t = an_t + np.array([F * L['ft'] * 0.97, L['ft'] * 0.22])
                toe_t[:, 1] = np.minimum(toe_t[:, 1], floor_y - 2 * g)
                for k_, t_ in ((s + 'kn', kn_t), (s + 'an', an_t), (s + 'toe', toe_t)):
                    P[k_] = P[k_] * (1 - ws[:, None]) + t_ * ws[:, None]
            # re-ground (straight legs may be a hair longer/shorter than the tracked ones)
            lowa = np.maximum(P['Lan'][:, 1], P['Ran'][:, 1]) + sf.get('foot_gap', 14) * g
            dyf = (floor_y - lowa) * ws
            for k in P:
                if not k.startswith('_'): P[k] = P[k] + np.stack([np.zeros(n), dyf], 1)
        if att.get('chair'):
            # (Oct 12, opt-in) hands resting on the top of a chair back (Down Dog - Chair). The chair is a fixed world point:
            # where Hani's hands land in the hold (shoulder + Julie's median arm direction x Hani's reach). Hands blend onto it
            # whenever Julie's wrists are near her chair top; if the chair is out of reach the whole body slides toward it
            # (smoothed, only while attached) instead of stretching the arms.
            mid_w = (A('Lwr') + A('Rwr')) / 2
            flat_t = np.abs(wrap(th['t'] - (0.0 if F > 0 else math.pi))) < math.radians(35)
            sel = flat_t if flat_t.sum() > 10 else np.ones(n, bool)
            jc = np.median(mid_w[sel], 0)
            r0, r1 = att.get('cr0', 0.30), att.get('cr1', 0.60)
            Wc = np.clip((r1 * Tj - np.linalg.norm(mid_w - jc, axis=1)) / ((r1 - r0) * Tj), 0, 1)
            Wc = gaussian_filter1d(Wc, 0.3 * fps, mode='nearest')
            shm = (P['Lsh'] + P['Rsh']) / 2
            jsh = sh; adir = mid_w - jsh; adir = adir / (np.linalg.norm(adir, axis=1)[:, None] + 1e-9)
            Tc = np.median((shm + adir * reach * att.get('chair_reach', 0.93))[sel], 0)
            # chair height: Julie's chair top relative to her standing hip height, applied to Hani's hip height
            FJ_ = scfg['FJ']; jhip = np.median(hip[~sel][:, 1]) if (~sel).sum() > 10 else np.median(hip[:, 1])
            ratio = (FJ_ - jc[1]) / max(FJ_ - jhip, 1.0)
            Tc[1] = floor_y - ratio * (L['th'] + L['sh']) * att.get('chair_h', 1.0)
            # slide toward the chair when out of reach
            dist = np.linalg.norm(Tc[None] - shm, axis=1); short = np.maximum(dist - reach * 0.97, 0)
            ux = np.sign(Tc[0] - shm[:, 0]); shift = gaussian_filter1d(short * ux * Wc, 0.4 * fps, mode='nearest')
            for k in P:
                if not k.startswith('_'): P[k] = P[k] + np.stack([shift, np.zeros(n)], 1)
            hd_dir = np.array([F * math.cos(math.radians(att.get('hand_down', 35))), math.sin(math.radians(att.get('hand_down', 35)))])
            for s in 'LR':
                tg = Tc + np.array([0.0, -att.get('grip_up', 0.05) * Tpx])
                for i in range(n):
                    if Wc[i] < 1e-3: continue
                    a1, a2 = self._ik(P[s + 'sh'][i], tg, L['ua'], L['fa'], -F)
                    el = P[s + 'sh'][i] + np.array([math.cos(a1), math.sin(a1)]) * L['ua']
                    wr = el + np.array([math.cos(a2), math.sin(a2)]) * L['fa']; tip = wr + hd_dir * L['hd']
                    w = Wc[i]
                    P[s + 'el'][i] = P[s + 'el'][i] * (1 - w) + el * w
                    P[s + 'wr'][i] = P[s + 'wr'][i] * (1 - w) + wr * w
                    P[s + 'tip'][i] = P[s + 'tip'][i] * (1 - w) + tip * w
            info['chairw'] = Wc; info['chair_shift'] = shift
            self.chair_spec = dict(top=Tc.copy(), F=F, floor=floor_y, T=Tpx)
            print(f"  chair attach: top at ({Tc[0]:.0f},{Tc[1]:.0f}), max slide {np.abs(shift).max():.0f}px, attached {np.mean(Wc > 0.5) * 100:.0f}% of frames")
        dep = np.array([-F * scfg.get('depth_x', 0.025), -scfg.get('depth_y', 0.025)]) * Tpx
        for k in list(P):
            if k.startswith(far): P[k] = P[k] + dep
        info['dy'] = dy; info['dx'] = dx; info['beta'] = np.degrees(bmag)
        look = np.array([1.0 if ph in scfg.get('look_cam_phases', ()) else 0.0 for ph in phases])
        look = gaussian_filter1d(look, 0.3 * fps, mode='nearest')
        elb = {s: np.degrees(wrap(th[s + 'fa'] - th[s + 'ua']) * -F) for s in 'LR'}
        kneeS = {s: np.degrees(wrap(th[s + 'sh'] - th[s + 'th']) * F) for s in 'LR'}
        spd = max(np.degrees(np.abs(np.diff(th[k]))).max() for k in th)
        print(f"  side plan: F {F:+d} near {near}  knee flex L {kneeS['L'].min():.0f}..{kneeS['L'].max():.0f} R {kneeS['R'].min():.0f}..{kneeS['R'].max():.0f} deg, "
              f"elbow flex L {elb['L'].min():.0f}..{elb['L'].max():.0f} R {elb['R'].min():.0f}..{elb['R'].max():.0f} deg, arch max {np.degrees(bmag).max():.0f} deg, "
              f"max segment speed {spd:.1f} deg/frame (25 fps)")
        for s in 'LR': P['_sole' + s] = SOLE[s]
        return dict(P=P, th=th, F=F, near=near, far=far, look=look, info=info, g=g, stand=False, side=True, L=L)

    @staticmethod
    def _ik(S, T, l1, l2, sgn):
        """2-bone IK in screen coords; sgn = required sign of the bend (wrap(a2-a1)*sgn >= 0)."""
        d = T - S; Ld = float(np.linalg.norm(d)); Ld = min(max(Ld, abs(l1 - l2) + 1e-3, 0.35 * (l1 + l2)), l1 + l2 - 1e-3)
        base = math.atan2(d[1], d[0]); ca = (l1 * l1 + Ld * Ld - l2 * l2) / (2 * l1 * Ld); al = math.acos(max(-1, min(1, ca)))
        for s_ in (1, -1):
            a1 = base + s_ * al; e = S + np.array([math.cos(a1), math.sin(a1)]) * l1
            w = S + d / (np.linalg.norm(d) + 1e-9) * Ld
            a2 = math.atan2(w[1] - e[1], w[0] - e[0])
            if wrap(a2 - a1) * sgn >= -1e-6: return a1, a2
        return a1, a2

    # ------------------------------------------------------------------ per-frame skeleton
    def skeleton_side(self, PL, i, Tpx, breath, tilt):
        P = PL['P']; S = {k: P[k][i].copy() for k in P}
        S['g'] = PL['g']; S['F'] = PL['F']; S['near'] = PL['near']; S['far'] = PL['far']
        ax = S['sm'] - S['hm']; S['ax'] = ax / (np.linalg.norm(ax) + 1e-9)
        S['beta'] = float(P['_beta'][i]); S['th0'] = float(P['_th0'][i])
        # gentle breath: chest rises a hair along the torso axis; small idle head tilt
        S['sm'] = S['sm'] + S['ax'] * 0.012 * Tpx * breath
        hv = S['crown'] - S['neck']; a = math.atan2(hv[1], hv[0]) + tilt * 0.6
        S['crown'] = S['neck'] + np.array([math.cos(a), math.sin(a)]) * np.linalg.norm(hv)
        S['look'] = float(PL['look'][i]); S['side'] = True; S['stand'] = False
        S['yaw'] = 0.0; S['yaw_sign'] = PL['F']
        for s in 'LR': S[s + 'hid'] = 0.0; S[s + 'wk'] = 0.0
        return S

    def draw_side(self, canvas, S, Tpx, st):
        P, g = self.P, S['g']; sp = g; F = S['F']; near, far = S['near'], S['far']
        def leg(s, pre=''):
            put(canvas, P[pre + s + 'th'], S[s + 'hip'], S[s + 'kn'], sp)
            put(canvas, P[pre + s + 'sh'], S[s + 'kn'], S[s + 'an'], sp)
            d = S[s + 'toe'] - S[s + 'an']; nrm = np.array([-d[1], d[0]])
            ft = 'footS' if np.dot(nrm, S['_sole' + s]) > 0 else 'footSm'
            put(canvas, P[pre + ft], S[s + 'an'], S[s + 'toe'], sp, sa=g)
        ART = self.art == 'side3d'
        def arm(s, pre=''):
            u = S[s + 'el'] - S[s + 'sh']; u = u / (np.linalg.norm(u) + 1e-9)
            put(canvas, P[pre + s + 'delt'], S[s + 'sh'] + u * 2 * g, S[s + 'sh'] + u * 4 * g, sp, sa=g)
            put(canvas, P[pre + s + 'ua'], S[s + 'sh'], S[s + 'el'], sp)
            put(canvas, P[pre + s + 'fa'], S[s + 'el'], S[s + 'wr'], sp)
            if ART:   # thumb/palm side toward the facing direction's front of the forearm
                d = S[s + 'tip'] - S[s + 'wr']; nrm = np.array([-d[1], d[0]]); fwd = S['_hfwd']
                put(canvas, P[pre + ('handS' if np.dot(nrm, fwd) > 0 else 'handSm')], S[s + 'wr'], S[s + 'tip'], sp, sa=g)
            else:
                put(canvas, P[pre + s + 'hand'], S[s + 'wr'], S[s + 'tip'], sp, sa=g)
        ax = S['ax']; S['_hfwd'] = np.array([-ax[1] * F, ax[0] * F])     # belly / palm side
        arm(far, 'D'); leg(far, 'D')
        if ART:
            put_bent(canvas, self.side_torso[1 if F > 0 else -1], S['hm'], S['th0'], S['beta'], float(np.linalg.norm(S['sm'] - S['hm'])), sp * self.scfg.get('art_torso_w', 0.90))
        else:
            tk = int(round(np.clip(F * self.scfg.get('torso_turn_side', 1.0), -1, 1) * 5))
            put_bent(canvas, self.torso_var[tk], S['hm'], S['th0'], S['beta'], float(np.linalg.norm(S['sm'] - S['hm'])), sp * self.scfg.get('torso_w', 0.72))
        leg(near)
        # head: 3/4 view turned to the facing direction; front head blended in when looking at the camera
        lk = S.get('look', 0.0)
        hq = P['head34R' if F > 0 else 'head34L']
        neck, crown = S['neck'], S['crown']
        if ART:
            hk = self.scfg.get('art_head_k', 1.12) * g * 0.97 / self.head_scale
            hp_ = P['headSR' if F > 0 else 'headSL']
            if lk < 0.5:
                put(canvas, hp_, neck, crown, hk, 1.0, sa=hk)
                if lk > 0.01: put(canvas, P['head'], neck, crown, sp, lk * 2, sa=g)
            else:
                put(canvas, P['head'], neck, crown, sp, 1.0, sa=g)
                if lk < 0.99: put(canvas, hp_, neck, crown, hk, (1 - lk) * 2, sa=hk)
            arm(near); return
        if lk < 0.5:
            put(canvas, hq, neck + (crown - neck) * -0.02, crown, g * 0.97, 1.0, sa=g * 0.97)
            if lk > 0.01: put(canvas, P['head'], neck, crown, sp, lk * 2 if lk < 0.5 else 1.0, sa=g)
        else:
            put(canvas, P['head'], neck, crown, sp, 1.0, sa=g)
            if lk < 0.99: put(canvas, hq, neck + (crown - neck) * -0.02, crown, g * 0.97, (1 - lk) * 2, sa=g * 0.97)
        arm(near)

    def cairo_under(self, c, S, Tpx, gt, floor_y=902.0):
        """floor shadow under the whole body + tail (behind the body), drawn on the background."""
        pts = np.array([S[k] for k in S if isinstance(S[k], np.ndarray) and S[k].shape == (2,) and k not in ('ax',)])
        x0, x1 = float(pts[:, 0].min()), float(pts[:, 0].max())
        if getattr(self, 'chair_spec', None): self.draw_chair_side(c, self.chair_spec)
        R.floor_shadow(c, (x0 + x1) / 2, floor_y + 2, max(0.45 * Tpx, (x1 - x0) / 2 + 0.15 * Tpx), 0.07 * Tpx, 0.26)
        self.draw_tail_side(c, S, Tpx, gt, floor_y)

    @staticmethod
    def draw_chair_side(c, ch):
        """Wooden chair seen from the side (same wood colours/gradients as rig.draw_chair). The backrest top is where
        Hani's hands rest; the seat points away from Hani (F = Hani's facing direction)."""
        PAL = R.PAL; T = ch['T']; F = ch['F']; fl = ch['floor']; tx, ty = ch['top']
        lw = 0.085 * T; seat_h = fl - (fl - ty) * 0.50; depth = 0.85 * T; sth = 0.10 * T
        bx = tx - F * 0.02 * T                       # back post (slight backward rake to the floor)
        R.floor_shadow(c, bx + F * depth / 2, fl - 2, depth * 0.85, 0.07 * T, 0.30)
        # back leg / post
        c.move_to(bx - lw / 2, ty); c.line_to(bx + lw / 2, ty); c.line_to(bx + lw / 2 - F * 0.06 * T, fl); c.line_to(bx - lw / 2 - F * 0.06 * T, fl); c.close_path()
        c.set_source(R.wood_grad(bx - lw, 0, bx + lw, 0)); c.fill()
        # front leg
        fx = bx + F * depth
        c.move_to(fx - lw / 2, seat_h); c.line_to(fx + lw / 2, seat_h); c.line_to(fx + lw / 2 + F * 0.03 * T, fl); c.line_to(fx - lw / 2 + F * 0.03 * T, fl); c.close_path()
        c.set_source(R.wood_grad(fx - lw, 0, fx + lw, 0)); c.fill()
        for xx in (bx - F * 0.06 * T, fx + F * 0.03 * T):
            R._c(c, PAL.WOOD_DARK, 0.35); c.rectangle(xx - lw / 2, fl - 6, lw, 6); c.fill()
        # stretcher between the legs
        R._c(c, PAL.WOOD_DARK, 0.85); c.set_line_width(0.035 * T); c.move_to(bx, fl - 0.18 * T); c.line_to(fx, fl - 0.18 * T); c.stroke()
        # seat (side edge with a light top)
        x0, x1 = min(bx, fx) - lw * 0.7, max(bx, fx) + lw * 0.7
        c.set_source(R.wood_grad(0, seat_h - sth / 2, 0, seat_h + sth / 2, PAL.WOOD_LIGHT, PAL.WOOD, PAL.WOOD_DARK)); R.rrect(c, x0, seat_h - sth / 2, x1 - x0, sth, 0.03 * T); c.fill()
        R._c(c, PAL.WOOD_LIGHT, 0.85); c.set_line_width(3); c.move_to(x0 + 6, seat_h - sth / 2 + 2); c.line_to(x1 - 6, seat_h - sth / 2 + 2); c.stroke()
        # backrest panel seen edge-on (thick) + rounded top rail
        bh = 0.42 * T
        c.set_source(R.wood_grad(bx - lw, ty, bx + lw, ty + bh)); R.rrect(c, bx - lw * 1.1, ty - 0.02 * T, lw * 2.2, bh, 0.05 * T); c.fill()
        R._c(c, PAL.WOOD_DARK, 0.5); c.set_line_width(2.0); R.rrect(c, bx - lw * 1.1, ty - 0.02 * T, lw * 2.2, bh, 0.05 * T); c.stroke()
        R._c(c, PAL.WOOD_LIGHT, 0.8); c.set_line_width(3); c.move_to(bx - lw * 0.6, ty - 0.005 * T); c.line_to(bx + lw * 0.6, ty - 0.005 * T); c.stroke()

    def draw_tail_side(self, c, S, T, t, floor_y):
        """Fur tail from the back of the pelvis, curving up and away from the facing direction, gentle sway.
        Same stroke style/colours as rig.draw_tail. Kept above the floor line."""
        F = S['F']; ax = S['ax']; fwd = np.array([-ax[1] * F, ax[0] * F])     # belly side
        base = S['hm'] - fwd * 0.20 * T + ax * 0.04 * T
        up = np.array([0.0, -1.0]); back = np.array([-F, 0.0])
        sw = 0.06 * math.sin(t * 1.3) + 0.03 * math.sin(t * 2.1 + 1)
        p0 = base; p1 = base + back * 0.62 * T + up * 0.08 * T
        p2 = base + back * (0.80 + sw) * T - up * 0.42 * T; p3 = base + back * (0.62 + sw * 1.4) * T - up * 0.28 * T
        pts = []
        for i in range(41):
            u = i / 40; a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; cc = 3 * (1 - u) * u * u; d = u ** 3
            pts.append(tuple(a * p0 + b * p1 + cc * p2 + d * p3))
        ex, ey = pts[-1]; px, py = pts[-2]; ang = math.atan2(ey - py, ex - px); r = 0.07 * T
        for i in range(1, 16):
            a2 = ang - F * i * 0.28; r2 = r * (1 - i / 22)
            ex, ey = ex + math.cos(a2) * r2 * 0.45, ey + math.sin(a2) * r2 * 0.45; pts.append((ex, ey))
        pts = [(x, min(y, floor_y - 0.05 * T)) for x, y in pts]
        n = len(pts); fur = (152 / 255, 70 / 255, 40 / 255)
        def stroke(width_fn, col, off=(0, 0)):
            c.set_line_cap(cairo.LINE_CAP_ROUND)
            for i in range(n - 1):
                c.set_source_rgba(*col); c.set_line_width(width_fn(i / (n - 1)))
                c.move_to(pts[i][0] + off[0], pts[i][1] + off[1]); c.line_to(pts[i + 1][0] + off[0], pts[i + 1][1] + off[1]); c.stroke()
        w0 = 0.085 * T
        stroke(lambda u: w0 * (1 - 0.55 * u) + 3, (0.42, 0.18, 0.09, 1))
        stroke(lambda u: w0 * (1 - 0.55 * u), fur + (1,))
        stroke(lambda u: w0 * 0.28 * (1 - 0.6 * u), (0.80, 0.45, 0.30, 0.55), (F * 0.012 * T, -0.012 * T))
