"""v3 puppet motion: same cut-out Hani art as v2 (rig.py), new motion layer.
- Whole-sequence arm planning: outlier rejection + hysteresis + eased state blends + zero-phase smoothing of
  wrist targets in torso-local space, then IK with hard anatomical limits and a fixed elbow-bend side.
- Head: front -> 3/4 -> profile 'over the shoulder' view, driven by a scripted yaw that is guaranteed during holds.
- Torso: belly/chest slides toward the turn + far-side shading (pseudo 3D rotation)."""
import math, sys
import numpy as np, cv2
from scipy.ndimage import gaussian_filter1d, median_filter
sys.path.insert(0, '/workspace/hani/puppet')
import rig as R
from rig import Part, put, smooth, SRC_T

def rate_limit(x, vmax):
    """zero-phase angular speed limit: forward and backward clamped passes, averaged."""
    f = x.copy(); b = x.copy()
    for i in range(1, len(x)): f[i] = f[i - 1] + np.clip(x[i] - f[i - 1], -vmax, vmax)
    for i in range(len(x) - 2, -1, -1): b[i] = b[i + 1] + np.clip(x[i] - b[i + 1], -vmax, vmax)
    return (f + b) / 2

def ease(x): x = min(1.0, max(0.0, x)); return 0.5 - 0.5 * math.cos(math.pi * x)

class Puppet3(R.Puppet):
    def __init__(self):
        super().__init__()
        hp = cv2.cvtColor(cv2.imread(R.D + 'tex_headprof.png', -1), cv2.COLOR_BGRA2RGBA)
        ax, ay, S = [float(v) for v in open(R.D + 'headprof_anchor.txt').read().split()]
        h, w = hp.shape[:2]
        pl = Part(hp, (ax, ay), (ax, ay - 128 * S), poly=[(0, 0), (w - 1, 0), (w - 1, h - 1), (0, h - 1)], pad=0)
        self.prof_scale = S
        self.P['headprofL'] = pl; self.P['headprofR'] = pl.mirrored()
        # torso rotation variants (t<0: chest turns to image-left)
        self.torso_var = {}
        base = self.P['torso']
        for k in range(-5, 6):
            self.torso_var[k] = self._twist_torso(base, k / 5)
        self.limits = dict(bend_max=math.radians(150), cross_max=0.38, over_head=0.15, knee_max=math.radians(115))

    def _twist_torso(self, part, t):
        if t == 0: return part
        img = part.img; h, w = img.shape[:2]
        a, b = part.a, part.b
        mapx = np.zeros((h, w), np.float32); mapy = np.repeat(np.arange(h, dtype=np.float32)[:, None], w, 1)
        us = np.linspace(-1.6, 1.6, 1500); k = 0.42 * t
        f = us + k * np.clip(1 - us ** 2, 0, None); f = np.maximum.accumulate(f)
        hw = 56.0
        for y in range(h):
            tt = np.clip((y - a[1]) / (b[1] - a[1] + 1e-6), -0.3, 1.3); xc = a[0] + (b[0] - a[0]) * tt
            ud = (np.arange(w) - xc) / hw
            mapx[y] = xc + hw * np.interp(ud, f, us, left=-9, right=9)
        out = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        # far-side shading
        xs = np.arange(w)[None, :]; xc0 = (a[0] + b[0]) / 2
        far = np.clip(((xs - xc0) / hw) * (-np.sign(t)), 0, 1.4)
        shade = 1 - 0.22 * abs(t) * np.clip(far, 0, 1) ** 1.5
        out[..., :3] *= shade[..., None]
        p = Part.__new__(Part); p.img = out.astype(np.float32); p.a = a.copy(); p.b = b.copy(); return p

    # ------------------------------------------------------------------ torso / legs (per frame, no arms)
    def base(self, J, Tpx, cal, breath=0.0, hm=None, ax_u=None):
        g = Tpx / SRC_T; q = lambda k: np.array(J[k], float)
        stand = cal.get('mode') == 'stand'
        if stand:      # pelvis comes from the whole-scene leg plan; torso axis from Julie (smoothed by the caller)
            hm = np.asarray(hm, float)
            Lt = float(np.linalg.norm((q('Lsh') + q('Rsh')) / 2 - (q('Lhip') + q('Rhip')) / 2))
            Lt = float(np.clip(Lt, 0.9 * Tpx, 1.08 * Tpx))
        else:
            jhx = (q('Lhip')[0] + q('Rhip')[0]) / 2
            hm = (q('Lhip') + q('Rhip')) / 2 + [0, cal['dy']]; hm = np.array([cal['hx'], hm[1]])
            sm = (q('Lsh') + q('Rsh')) / 2 + [cal['hx'] - jhx, cal['dy']]
            ax = sm - hm; Lt = np.linalg.norm(ax); ax_u = ax / Lt
        # hard limit: torso lean within +-25 deg of vertical
        ang = math.atan2(ax_u[0], -ax_u[1]); ang = float(np.clip(ang, -0.44, 0.44)); ax_u = np.array([math.sin(ang), -math.cos(ang)])
        sm = hm + ax_u * min(Lt, 1.08 * Tpx) * (1 + 0.012 * breath)
        perp = np.array([-ax_u[1], ax_u[0]]);  perp = -perp if perp[0] < 0 else perp
        sw = np.linalg.norm(q('Lsh') - q('Rsh')); r = sw / cal['sw0']
        S = dict(hm=hm, sm=sm, g=g, perp=perp, ax=ax_u, wtrack=float(np.clip(0.35 + 0.65 * r, 0.62, 1.0)))
        S['Lhip'] = hm + perp * 37 * g; S['Rhip'] = hm - perp * 37 * g
        if stand: return S
        for s, sg in (('L', 1), ('R', -1)):
            kn = np.array([S[s + 'hip'][0] + sg * 0.22 * Tpx, cal['seat_y'] + 0.04 * Tpx])
            S[s + 'kn'], S[s + 'an'] = kn, np.array([kn[0] + sg * 0.05 * Tpx, cal['ankle_y']])
        return S

    def shoulders(self, S, wmul):
        g = S['g']
        for s, sg in (('L', 1), ('R', -1)):
            S[s + 'sh'] = S['sm'] + S['perp'] * sg * 51 * g * wmul - S['ax'] * 4 * g

    # ------------------------------------------------------------------ standing legs (whole scene)
    def plan_stand(self, Js, Tpx, cal, fps):
        """Standing / lunging legs. Julie's lower body is scaled by kL (Hani leg length / Julie leg length) about the
        scene anchor X0. Feet are PLANTED: stance intervals (foot still and on the floor) get one fixed x on the floor
        line; swings between them are eased, with a lift that is exactly zero at contact. Pelvis = Julie's hip height
        above her floor, scaled, smoothed + rate limited, then clamped so both legs reach (never over-stretched) and the
        knee never bends past the limit. Knee = 2-bone IK, always on the OUTER side (never inward/backward)."""
        n = len(Js); g = Tpx / SRC_T; kL = cal['kL']; X0 = cal['X0']; FJ = cal['FJ']; fy = cal['ankle_y']
        q = lambda J, k: np.array(J[k], float)
        sig = lambda x, s_: gaussian_filter1d(x, max(0.5, s_ * fps), axis=0, mode='nearest')
        hipJ = np.array([(q(J, 'Lhip') + q(J, 'Rhip')) / 2 for J in Js])
        shJ = np.array([(q(J, 'Lsh') + q(J, 'Rsh')) / 2 for J in Js])
        # torso axis: Julie, lean clamped to +-25 deg, smoothed
        ang = np.arctan2(shJ[:, 0] - hipJ[:, 0], -(shJ[:, 1] - hipJ[:, 1]))
        ang = rate_limit(sig(np.clip(ang, -0.44, 0.44), 0.3), math.radians(2.5))
        ax = np.stack([np.sin(ang), -np.cos(ang)], 1)
        perp = np.stack([-ax[:, 1], ax[:, 0]], 1); perp[perp[:, 0] < 0] *= -1
        hipoff = {'L': perp * 37 * g, 'R': -perp * 37 * g}
        l1 = {s: float(np.linalg.norm(self.SJ[s + 'kn'] - self.SJ[s + 'hip'])) * g for s in 'LR'}
        l2 = {s: float(np.linalg.norm(self.SJ[s + 'an'] - self.SJ[s + 'kn'])) * g for s in 'LR'}
        l1 = {s: (l1['L'] + l1['R']) / 2 for s in 'LR'}; l2 = {s: (l2['L'] + l2['R']) / 2 for s in 'LR'}   # symmetric legs
        bmax = self.limits['knee_max']
        an = {}; info = {}
        hwJ = float(np.median([abs(q(J, 'Lhip')[0] - q(J, 'Rhip')[0]) / 2 for J in Js]))
        hxw = cal['hx'] + (hipJ[:, 0] - X0) * kL
        for s, sg_ in (('L', 1), ('R', -1)):
            aj = np.array([q(J, s + 'an') for J in Js])
            # foot under the hip maps to foot under Hani's hip (Hani's hips are relatively wider than Julie's)
            xa = hxw + sg_ * (37 * g + (sg_ * (aj[:, 0] - hipJ[:, 0]) - hwJ) * kL)
            xa = hxw + sg_ * np.maximum(20 * g, sg_ * (xa - hxw))                              # feet never overlap
            lift = np.maximum(0.0, (FJ - aj[:, 1]) * kL - 0.05 * Tpx)
            xs_ = sig(xa, 0.08); v = np.abs(np.gradient(xs_))
            ls_ = sig(lift, 0.08)
            stance = (v < 0.010 * Tpx) & (ls_ < 0.07 * Tpx)
            # stance runs (>= 0.3 s); shorter runs count as swing
            runs = []; st0 = None
            for i in range(n + 1):
                on = i < n and stance[i]
                if on and st0 is None: st0 = i
                if not on and st0 is not None:
                    if i - st0 >= 0.3 * fps: runs.append((st0, i - 1))
                    st0 = None
            if not runs: runs = [(0, n - 1)]
            X = np.zeros(n); Y = np.full(n, fy)
            for (r0, r1) in runs: X[r0:r1 + 1] = np.median(xa[r0:r1 + 1])
            X[:runs[0][0]] = X[runs[0][0]]; X[runs[-1][1] + 1:] = X[runs[-1][1]]
            for (a0, a1), (b0, b1) in zip(runs[:-1], runs[1:]):
                xa0, xb0 = X[a1], X[b0]; L_ = b0 - a1
                for i in range(a1 + 1, b0):
                    u = (i - a1) / L_; X[i] = xa0 + (xb0 - xa0) * ease(u)
                    Y[i] = fy - ls_[i] * math.sin(math.pi * u)
            an[s] = np.stack([X, Y], 1); info[s] = dict(runs=runs)
        # pelvis
        # pelvis x: same relative place between the planted feet as Julie's hips between her feet (keeps both legs'
        # bends consistent with hers); falls back to the mapped hip when her feet are close together
        aJL = np.array([q(J, 'Lan')[0] for J in Js]); aJR = np.array([q(J, 'Ran')[0] for J in Js])
        spJ = aJL - aJR; r_ = np.clip((hipJ[:, 0] - aJR) / np.where(np.abs(spJ) > 1e-3, spJ, 1e-3), 0.05, 0.95)
        wsp = np.clip((np.abs(spJ) / (cal.get('Tsrc_px', Tpx)) - 0.5) / 0.4, 0, 1)
        r_ = sig(r_, 0.25); wsp = sig(wsp, 0.25)
        hx = (an['R'][:, 0] + r_ * (an['L'][:, 0] - an['R'][:, 0])) * wsp + hxw * (1 - wsp)
        # pelvis height: the height at which Hani's legs (own lengths) have Julie's knee bends (straight stays straight)
        kb = {}
        for s in 'LR':
            h_ = np.array([q(J, s + 'hip') for J in Js]); k_ = np.array([q(J, s + 'kn') for J in Js]); a_ = np.array([q(J, s + 'an') for J in Js])
            v1 = k_ - h_; v2 = a_ - k_
            c_ = np.sum(v1 * v2, 1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-9)
            b_ = np.arccos(np.clip(c_, -1, 1)); b_ = np.maximum(0, b_ - math.radians(8))     # tracking noise dead-zone
            kb[s] = np.minimum(sig(b_, 0.2), bmax)
        hyl = []
        for s in 'LR':
            D = np.sqrt(l1[s] ** 2 + l2[s] ** 2 + 2 * l1[s] * l2[s] * np.cos(kb[s]))
            dx = an[s][:, 0] - (hx + hipoff[s][:, 0]); dx = np.clip(dx, -0.97 * D, 0.97 * D)
            hyl.append(an[s][:, 1] - np.sqrt(D * D - dx * dx) - hipoff[s][:, 1])
        hy = np.minimum(hyl[0], hyl[1]) * 0.5 + np.maximum(hyl[0], hyl[1]) * 0.5
        if cal.get('squat_k'):
            # (Oct 12 b2, opt-in) front-filmed squats (Chair Pose): Julie's knees bend TOWARD the camera, so her 2D knee angle
            # stays ~0. Use her hip DROP (vs her standing hip height, in leg lengths) instead; Hani's pelvis drops by
            # squat_k x that x his leg length and the IK shows the bend with the knees out to the sides (front view).
            ljs = float(np.median([np.linalg.norm(q(J, s + 'kn') - q(J, s + 'hip')) + np.linalg.norm(q(J, s + 'an') - q(J, s + 'kn')) for J in Js for s in 'LR']))
            hh = FJ - hipJ[:, 1]; drop = np.clip((np.percentile(hh, 95) - hh) / ljs, 0, 0.6)
            drop = sig(np.maximum(0, drop - 0.02), 0.3) * cal['squat_k'] * (l1['L'] + l2['L'])
            hy = np.maximum(hy, np.percentile(hy, 5) + drop)
            print(f"  squat_from_hip: max Julie hip drop {np.max(drop) / cal['squat_k'] / (l1['L'] + l2['L']):.2f} leg, Hani pelvis drop max {np.max(drop):.0f}px")
        hx = rate_limit(sig(hx, 0.25), 0.03 * Tpx); hy = rate_limit(sig(hy, 0.25), 0.025 * Tpx)
        Lmin = {s: math.sqrt(l1[s] ** 2 + l2[s] ** 2 - 2 * l1[s] * l2[s] * math.cos(math.pi - bmax)) for s in 'LR'}
        def bounds(hx, hy):
            lo = np.full(n, -1e9); hi = np.full(n, 1e9)
            for s in 'LR':
                hpx = hx + hipoff[s][:, 0]; oy = hipoff[s][:, 1]
                dx = an[s][:, 0] - hpx; R = 0.997 * (l1[s] + l2[s])
                dx = np.clip(dx, -0.97 * R, 0.97 * R)
                lo = np.maximum(lo, an[s][:, 1] - np.sqrt(R * R - dx * dx) - oy)          # not over-stretched
                hi = np.minimum(hi, an[s][:, 1] - np.sqrt(np.maximum(0, Lmin[s] ** 2 - dx * dx)) - oy)   # knee <= limit
            return lo, hi
        for _ in range(3):
            lo, hi = bounds(hx, hy)
            corr = np.clip(hy, lo, hi) - hy
            hy = hy + sig(corr, 0.15) * 1.0
        lo, hi = bounds(hx, hy); hy = np.clip(hy, lo, hi)
        hm = np.stack([hx, hy], 1)
        # unreachable feet (rare): pull the ankle in along the leg (logged)
        legs = {}; pulled = 0
        for s, sg in (('L', 1), ('R', -1)):
            hp_ = hm + hipoff[s]; kn = np.zeros((n, 2)); A = an[s].copy(); bend = np.zeros(n)
            for i in range(n):
                d = A[i] - hp_[i]; L = float(np.linalg.norm(d)); R = l1[s] + l2[s]
                if L > 0.999 * R: A[i] = hp_[i] + d / L * 0.999 * R; L = 0.999 * R; pulled += 1
                L = max(L, abs(l1[s] - l2[s]) + 1e-3); u = d / (np.linalg.norm(d) + 1e-9)
                a_ = (l1[s] ** 2 - l2[s] ** 2 + L * L) / (2 * L); h_ = math.sqrt(max(0.0, l1[s] ** 2 - a_ * a_))
                nrm = np.array([-u[1], u[0]])
                if nrm[0] * sg < 0: nrm = -nrm                     # knee on the OUTER side, always
                kn[i] = hp_[i] + u * a_ + nrm * h_
                v1 = kn[i] - hp_[i]; v2 = A[i] - kn[i]
                bend[i] = math.degrees(math.acos(np.clip(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9), -1, 1)))
            legs[s] = dict(hip=hp_, kn=kn, an=A, bend=bend, runs=info[s]['runs'])
        print(f'  stand legs: kL {kL:.3f}, knee bend max L {legs["L"]["bend"].max():.0f} R {legs["R"]["bend"].max():.0f} deg, '
              f'feet pulled in {pulled} frames, stance runs L {len(info["L"]["runs"])} R {len(info["R"]["runs"])}')
        return hm, ax, legs

    # ------------------------------------------------------------------ whole-scene plan
    def plan(self, Js, vis, phases, hold, Tpx, cal, fps, head_dir):
        """Js: list of Julie joint dicts per frame; vis: {'L': arr, 'R': arr}; phases: list of phase names;
        hold: (h0, h1) seconds; head_dir: -1 = look image-left, +1 = image-right (for this side)."""
        n = len(Js); g = Tpx / SRC_T; t = np.arange(n) / fps
        stand = cal.get('mode') == 'stand'; self._stand = stand
        if stand:
            hmS, axS, legs = self.plan_stand(Js, Tpx, cal, fps)
            B = [self.base(J, Tpx, cal, hm=hmS[i], ax_u=axS[i]) for i, J in enumerate(Js)]
            for i, b in enumerate(B):
                for s_ in 'LR':
                    b[s_ + 'hip'] = legs[s_]['hip'][i]; b[s_ + 'kn'] = legs[s_]['kn'][i]; b[s_ + 'an'] = legs[s_]['an'][i]
        else:
            legs = None
            B = [self.base(J, Tpx, cal) for J in Js]
        q = lambda J, k: np.array(J[k], float)
        h0, h1 = hold
        # --- scripted head yaw (guaranteed over-the-shoulder for the whole hold) + torso twist amount
        yaw = np.array([ease((tt - (h0 - 0.8)) / 0.8) * (1 - ease((tt - h1) / 0.8)) for tt in t]) * cal.get('yaw_max', 1.0)
        tturn = cal.get('torso_turn', 1.0)
        # setup / idle: sit tall, calm (ignore Julie's resettling)
        rest_w = np.array([1.0 if ph in cal.get('rest_phases', ('idle', 'setup')) else 0.0 for ph in phases])
        rest_w = gaussian_filter1d(rest_w, 0.35 * fps, mode='nearest')
        # torso width: tracked (smoothed) but at least the scripted turn during the hold
        wt = gaussian_filter1d(np.array([b['wtrack'] for b in B]), 0.4 * fps, mode='nearest')
        wmul = np.minimum(wt * (1 - rest_w) + rest_w, 1 - 0.30 * yaw * tturn)
        for i, b in enumerate(B): self.shoulders(b, wmul[i]); b['wmul'] = wmul[i]
        out = {}
        lua, lfa = self.len['ua'] * g, self.len['fa'] * g
        for s, sg in (('L', 1), ('R', -1)):
            # torso-local frame: x = outward lateral (sg*perp), y = up (ax)
            raw = np.zeros((n, 2)); restp = np.zeros((n, 2)); kneet = np.zeros((n, 2)); backt = np.zeros((n, 2)); kw = np.zeros(n)
            for i, (J, b) in enumerate(zip(Js, B)):
                o = sg * b['perp']; u = b['ax']; sh = b[s + 'sh']
                loc = lambda p: np.array([np.dot(p - sh, o), np.dot(p - sh, u)])
                w = (q(J, s + 'el') - q(J, s + 'sh')) * cal['kua'] + (q(J, s + 'wr') - q(J, s + 'el')) * cal['kfa']
                raw[i] = [np.dot(w, o), np.dot(w, u)]
                if stand:   # relaxed arms hanging by the sides
                    restp[i] = np.array([0.16 * Tpx, -0.96 * (lua + lfa)]); kneet[i] = raw[i]; kw[i] = 0.0
                    backt[i] = loc(b['hm'] + o * 0.34 * Tpx + u * 0.10 * Tpx)
                    continue
                restp[i] = loc(b[s + 'kn'] + [-sg * 0.03 * Tpx, -0.08 * Tpx])       # own knee
                # continuous (not snapping) attraction to whichever knee Julie's hand is near, by soft weights
                def segd(p, a_, b_):
                    v = b_ - a_; tt = np.clip(np.dot(p - a_, v) / (np.dot(v, v) + 1e-9), 0, 1); return np.linalg.norm(p - (a_ + v * tt))
                wr_j = q(J, s + 'wr')
                dL = segd(wr_j, q(J, 'Lhip'), q(J, 'Lkn')); dR = segd(wr_j, q(J, 'Rhip'), q(J, 'Rkn'))
                wL = smooth(0.5 * Tpx, 0.22 * Tpx, dL); wR = smooth(0.5 * Tpx, 0.22 * Tpx, dR)
                tot = wL + wR
                if tot > 1e-6:
                    kp = (b['Lkn'] * wL + b['Rkn'] * wR) / tot + [0, -0.08 * Tpx]
                    kneet[i] = loc(kp); kw[i] = min(1.0, max(wL, wR))
                else: kneet[i] = raw[i]
                ch = cal['chair']
                backt[i] = loc(np.array([b['sm'][0] + sg * 0.56 * Tpx, ch['back_top'] + 0.01 * Tpx]))
            # 1) outlier rejection on raw tracking, then smoothing
            raw = median_filter(raw, size=(int(0.4 * fps) | 1, 1), mode='nearest')
            # 2) hidden-arm state with hysteresis (enter < 0.4, leave > 0.6) and a 1 s minimum dwell
            v = gaussian_filter1d(np.nan_to_num(vis[s], nan=1.0), 0.3 * fps, mode='nearest')
            st_ = np.zeros(n); cur = 0; last = -10 ** 9
            for i in range(n):
                if cur == 0 and v[i] < 0.4 and i - last > fps: cur, last = 1, i
                elif cur == 1 and v[i] > 0.6 and i - last > fps: cur, last = 0, i
                st_[i] = cur
            st_ *= (1 - (rest_w > 0.5))
            hid = gaussian_filter1d(st_, 0.17 * fps, mode='nearest')          # ~0.5 s eased transition
            kw = gaussian_filter1d(kw, 0.3 * fps, mode='nearest') * (1 - hid)
            tgt = raw * (1 - kw)[:, None] + kneet * kw[:, None]
            tgt = tgt * (1 - hid)[:, None] + backt * hid[:, None]
            tgt = tgt * (1 - rest_w)[:, None] + restp * rest_w[:, None]
            # head keep-out disc (torso-local per frame): hands/forearms never pass across the face;
            # a wrist inside the disc is moved to the disc edge on its OWN side at the same height
            hc = np.zeros((n, 2))
            for i, b in enumerate(B):
                c = b['sm'] + b['ax'] * 70 * g + b['perp'] * head_dir * 0.07 * Tpx * yaw[i]
                o = sg * b['perp']; sh = b[s + 'sh']; hc[i] = [np.dot(c - sh, o), np.dot(c - sh, b['ax'])]
            rk = 125 * g
            def keepout(T):
                T = T.copy()
                for i in range(n):
                    dx, dy = T[i] - hc[i]
                    if dx * dx + dy * dy < rk * rk:
                        T[i, 0] = hc[i, 0] + math.sqrt(max(0.0, rk * rk - dy * dy))
                return T
            if stand:   # hanging arms: Julie's hands in front of her thighs look short (foreshortened); let Hani's hang long
                Lf = lua + lfa; nrm_ = np.linalg.norm(tgt, axis=1) + 1e-9
                down = np.clip((-tgt[:, 1] / nrm_ - 0.64) / 0.3, 0, 1)
                Lw = np.maximum(nrm_, (0.93 * Lf) * down + nrm_ * (1 - down))
                tgt = tgt / nrm_[:, None] * Lw[:, None]
            tgt = keepout(tgt)
            # 3) zero-phase smoothing of the final wrist targets (stronger than v1)
            tgt = keepout(gaussian_filter1d(tgt, 0.30 * fps, axis=0, mode='nearest'))
            # 4) IK with hard anatomical limits, fixed elbow side
            el_l = np.zeros((n, 2)); wr_l = np.zeros((n, 2)); side = None
            for i in range(n):
                el_l[i], wr_l[i], side = self.ik_limited(tgt[i], lua, lfa, side)
            # 5) light smoothing of the solved joint angles (unwrapped) and re-solve forward kinematics
            a1 = np.arctan2(el_l[:, 1], el_l[:, 0]); a2 = np.arctan2(wr_l[:, 1] - el_l[:, 1], wr_l[:, 0] - el_l[:, 0])
            bend = (a2 - a1 + np.pi) % (2 * np.pi) - np.pi                  # wrapped per frame (never off by 360)
            a1 = rate_limit(gaussian_filter1d(np.unwrap(a1), 0.16 * fps, mode='nearest'), math.radians(6.5))
            bend = rate_limit(gaussian_filter1d(bend, 0.16 * fps, mode='nearest'), math.radians(6.5))
            a1 = gaussian_filter1d(a1, 0.06 * fps, mode='nearest'); bend = gaussian_filter1d(bend, 0.06 * fps, mode='nearest')
            bend = np.clip(bend, -self.limits['bend_max'], self.limits['bend_max'])
            a2 = a1 + bend
            # 6) hard keep-out: forearm + hand never cross the head. Straighten the elbow first, then swing the
            #    upper arm outward, until wrist, forearm middle and fingertips clear the head disc.
            rh = 70 * g; hl = 58 * g
            def collides(a1_, a2_, c):
                e = np.array([math.cos(a1_), math.sin(a1_)]) * lua; w = e + np.array([math.cos(a2_), math.sin(a2_)]) * lfa
                tip = w + np.array([math.cos(a2_), math.sin(a2_)]) * hl
                pts = [w, (e + w) / 2, tip, (w + tip) / 2]
                return any(np.linalg.norm(p_ - c) < rh for p_ in pts)
            def fix_all(a1, bend):
                for i in range(n):
                    a1i, bi = a1[i], bend[i]; k = 0
                    while collides(a1i, a1i + bi, hc[i]) and k < 40:
                        if abs(bi) > math.radians(4): bi *= 0.85
                        else:
                            w1 = (a1i + math.pi) % (2 * math.pi) - math.pi
                            a1i += -math.radians(3) if w1 > 0 else math.radians(3)
                        k += 1
                    a1[i], bend[i] = a1i, bi
                return a1, bend
            for _pass in range(3):
                a1, bend = fix_all(a1.copy(), bend.copy())
                a1 = rate_limit(gaussian_filter1d(a1, 0.10 * fps, mode='nearest'), math.radians(6.5))
                bend = rate_limit(gaussian_filter1d(bend, 0.10 * fps, mode='nearest'), math.radians(6.5))
            a1, bend = fix_all(a1.copy(), bend.copy())
            a1 = gaussian_filter1d(a1, 0.04 * fps, mode='nearest'); bend = gaussian_filter1d(bend, 0.04 * fps, mode='nearest')
            a2 = a1 + bend
            el_l = np.stack([np.cos(a1), np.sin(a1)], 1) * lua
            wr_l = el_l + np.stack([np.cos(a2), np.sin(a2)], 1) * lfa
            out_coll = sum(collides(a1[i], a2[i], hc[i]) for i in range(n)); print(f'  arm {s}: frames still touching head after keep-out: {out_coll}')
            out[s] = dict(el=el_l, wr=wr_l, hid=hid, a1=a1, a2=a2)
            out[s]['tgt'] = tgt; out[s]['raw'] = raw; out[s]['kw'] = kw; out[s]['rest'] = rest_w
        return dict(B=B, arms=out, yaw=yaw, head_dir=head_dir, wmul=wmul, rest=rest_w, legs=legs, stand=stand, tturn=tturn)


    def ik_limited(self, tl, l1, l2, prev):
        """Torso-local 2-bone IK (x = outward from the body, y = up; mirrored per arm).
        Natural elbow: always on the OUTER side of the shoulder->wrist line (slightly preferring below), chosen with
        hysteresis so it can never flip between frames. Elbow bend limited to 0..150 deg. Shoulder range limited."""
        tl = np.asarray(tl, float); L = np.linalg.norm(tl)
        bmax = self.limits['bend_max']
        Lmin = math.sqrt(l1 * l1 + l2 * l2 - 2 * l1 * l2 * math.cos(math.pi - bmax))
        if L < 1e-6: tl = np.array([0.0, -1.0]); L = 1.0
        d = tl / np.linalg.norm(tl); L = min(max(L, Lmin), l1 + l2 - 1e-3)
        ca = (l1 * l1 + L * L - l2 * l2) / (2 * l1 * L); al = math.acos(max(-1, min(1, ca)))
        base = math.atan2(d[1], d[0])
        def cand(sgn):
            a1 = base + sgn * al; e = np.array([math.cos(a1), math.sin(a1)]) * l1
            return a1, e, float(np.dot(e, [1.0, -1.0]))
        c1, c2 = cand(1), cand(-1)
        if prev is None: side = 1 if c1[2] >= c2[2] else -1
        else:
            side = prev
            other = c2 if prev == 1 else c1; mine = c1 if prev == 1 else c2
            cint = (l1 * l1 + l2 * l2 - L * L) / (2 * l1 * l2); bend_mag = math.pi - math.acos(max(-1, min(1, cint)))
            # hysteresis + only switch the elbow side while the arm is nearly straight (switch is then invisible)
            if other[2] - mine[2] > 0.18 * l1 and bend_mag < math.radians(35): side = -prev
        # never an inward elbow on a lowered arm (that reads as arms crossed / broken): take the outer solution
        ch_ = c1 if side == 1 else c2; ot_ = c2 if side == 1 else c1
        if getattr(self, '_stand', False) and ch_[1][0] < -0.05 * l1 and ch_[1][1] < 0 and ot_[1][0] > ch_[1][0]: side = -side   # stand mode only (seated v3 unchanged)
        a1, e, _ = c1 if side == 1 else c2
        a2 = math.atan2(d[1] * L - e[1], d[0] * L - e[0])
        # shoulder range: upper arm may not cross far in front of the chest, and never across the head
        ux, uy = math.cos(a1), math.sin(a1)
        lim = -self.limits['cross_max'] if uy < 0.3 else self.limits['over_head']
        if ux < lim:
            uy2 = math.copysign(math.sqrt(max(0.0, 1 - lim * lim)), uy if abs(uy) > 1e-3 else -1)
            a1 = math.atan2(uy2, lim); e = np.array([math.cos(a1), math.sin(a1)]) * l1
            a2 = math.atan2(d[1] * L - e[1], d[0] * L - e[0])
        bend = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        bend = float(np.clip(bend, -bmax, bmax)); a2 = a1 + bend
        w = e + np.array([math.cos(a2), math.sin(a2)]) * l2
        return e, w, side

    # ------------------------------------------------------------------ per-frame skeleton from the plan
    def skeleton3(self, PL, i, Tpx, breath, tilt):
        b = dict(PL['B'][i]); g = b['g']
        S = b; o = {}
        for s, sg in (('L', 1), ('R', -1)):
            A = PL['arms'][s]; ou = sg * b['perp']; up = b['ax']; sh = b[s + 'sh']
            toW = lambda v: sh + ou * v[0] + up * v[1]
            el, wr = toW(A['el'][i]), toW(A['wr'][i])
            fd = (wr - el) / (np.linalg.norm(wr - el) + 1e-9)
            S[s + 'el'], S[s + 'wr'], S[s + 'tip'], S[s + 'hid'] = el, wr, wr + fd * 58 * g, float(A['hid'][i])
        y = float(PL['yaw'][i]); hd = PL['head_dir']
        S['yaw'], S['yaw_sign'] = y, hd
        # head: rotates/tilts toward the turn shoulder and slides a little that way
        ha = math.atan2(b['ax'][0], -b['ax'][1]) + tilt + hd * 0.10 * y
        neck = b['sm'] + b['ax'] * 6 * g + b['perp'] * hd * 0.07 * Tpx * y
        S['neck'] = neck; S['crown'] = neck + np.array([math.sin(ha), -math.cos(ha)]) * 128 * g
        S['twist'] = hd * y * PL.get('tturn', 1.0); S['stand'] = PL.get('stand', False)
        S['wmul'] = float(PL['wmul'][i]) * (1 + 0.01 * breath)
        return S

    def draw3(self, canvas, S, Tpx, st):
        P, g = self.P, S['g']; sp = g
        def limb(s, seg, a, b, w=1.0, op=1.0, sa=None): put(canvas, P[s + seg], S[a], S[b], sp * w, op, sa)
        hidden = [s for s in 'LR' if S[s + 'hid'] > 0.5]
        for s in hidden:
            limb(s, 'ua', s + 'sh', s + 'el'); limb(s, 'fa', s + 'el', s + 'wr'); limb(s, 'hand', s + 'wr', s + 'tip')
        if S.get('stand'):
            for s in 'LR':
                ft_dir = self.SJ[s + 'toe'] - self.SJ[s + 'an']
                put(canvas, P[s + 'ft'], S[s + 'an'], S[s + 'an'] + ft_dir * g, sp)
            for s in 'LR':
                put(canvas, P[s + 'th'], S[s + 'hip'], S[s + 'kn'], sp)
                limb(s, 'sh', s + 'kn', s + 'an')
        tk = int(round(np.clip(S['twist'], -1, 1) * 5))
        put(canvas, self.torso_var[tk], S['sm'] + S['ax'] * -2 * g, S['hm'], sp * S['wmul'])
        for s in 'LR':
            if s not in hidden:
                u = (S[s + 'el'] - S[s + 'sh']); u = u / (np.linalg.norm(u) + 1e-9)
                put(canvas, P[s + 'delt'], S[s + 'sh'] + u * 2 * g, S[s + 'sh'] + u * 4 * g, sp, sa=g)
                limb(s, 'ua', s + 'sh', s + 'el')
        # head: front -> 3/4 -> profile. Short crossfades; dominant view always fully opaque.
        y = S['yaw']; L = S['yaw_sign'] < 0
        views = [('front', P['head'], 1.0), ('q', P['head34L' if L else 'head34R'], 0.97), ('prof', P['headprofL' if L else 'headprofR'], 0.97 / self.prof_scale)]
        wq = smooth(0.22, 0.30, y); wp = smooth(0.62, 0.70, y)
        wts = [1 - wq, wq * (1 - wp), wp]
        order = np.argsort(wts)[::-1]
        for j, k in enumerate(order):
            name, part, sc = views[k]; op = 1.0 if j == 0 else wts[k]
            if op < 0.01: continue
            if name == 'front': put(canvas, part, S['neck'], S['crown'], sp * (1 - 0.18 * min(y, 0.3)), op, sa=g)
            else: put(canvas, part, S['neck'] + (S['crown'] - S['neck']) * -0.02, S['crown'], g * sc, op, sa=g * sc)
        for s in ('LR' if not S.get('stand') else ''):
            put(canvas, P[s + 'th'], S[s + 'hip'] + [0, -0.10 * Tpx], S[s + 'kn'] + [0, 0.02 * Tpx], sp * 1.25)
        for s in ('LR' if not S.get('stand') else ''):
            limb(s, 'sh', s + 'kn', s + 'an')
            ft_dir = self.SJ[s + 'toe'] - self.SJ[s + 'an']
            put(canvas, P[s + 'ft'], S[s + 'an'], S[s + 'an'] + ft_dir * g, sp)
        for s in 'LR':
            if s not in hidden:
                limb(s, 'fa', s + 'el', s + 'wr'); limb(s, 'hand', s + 'wr', s + 'tip')
