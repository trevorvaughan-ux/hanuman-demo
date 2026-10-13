"""Front-view floor / seated mode (Oct 12 2026, batch 2). Opt-in: config "mode": "side" + "side": {"front": true, ...}.
Re-uses the side-mode whole-scene planner (Julie's 2D segment DIRECTIONS, Hani's LENGTHS, smoothing, rate limits,
grounding, anchors) but for poses filmed from the FRONT, and draws the FRONT cut-out art (T-stand limbs, front torso,
front head) like the seated/standing modes. Differences vs side mode:
- hips/shoulders spread sideways (front width), no side-view knee/elbow sign limits, no far-side darkening/depth offset.
- torso FORESHORTENING: a forward fold toward the camera shortens Julie's 2D torso; Hani's torso keeps pointing up and its
  drawn length = Julie's vertical torso extent / her upright torso length (min 'f_min'). With 'invert': true (standing
  wide-legged fold) the length may go negative: the torso swings down between the legs and the head turns upside down.
- 'head_up': true keeps the head upright on top of the (shortened) torso (seated folds: face stays visible).
- 'mirror_front_legs' / 'mirror_front_arms': exact left/right mirror symmetry (Butterfly).
Nothing here runs unless a config sets side.front."""
import math, sys
import numpy as np
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '/workspace/hani/puppet')
import rig as R
import rig_side as RS
from rig import put

wrap = RS.wrap

class PuppetFront(RS.PuppetSide):
    def __init__(self, scfg=None):
        scfg = dict(scfg or {}); scfg.setdefault('defringe', False)
        super().__init__(scfg)
        SJ = self.SJ
        hw = abs(SJ['Lhip'][0] - SJ['Rhip'][0]) / 2 * scfg.get('hip_w', 1.0)
        sw = abs(SJ['Lsh'][0] - SJ['Rsh'][0]) / 2 * scfg.get('sh_w', 1.0)
        self._fw = {'Lhip': hw, 'Rhip': -hw, 'Lsh': sw, 'Rsh': -sw}

    def _front_pre(self, th, hip, sh, ear, n, fps, scfg):
        sig = lambda x, s_: gaussian_filter1d(x, max(0.5, s_ * fps), mode='nearest')
        tv = sh - hip; Tup = float(np.percentile(np.linalg.norm(tv, axis=1), 90))
        f = -tv[:, 1] / Tup
        if scfg.get('invert'): f = np.clip(f, -1.0, 1.0)
        else: f = np.clip(f, scfg.get('f_min', 0.35), 1.0)
        f = sig(f, scfg.get('f_sigma', 0.3))
        lean = np.clip(np.arctan2(tv[:, 0], -tv[:, 1]), -0.30, 0.30) * np.clip(f, 0, 1)
        th['t'] = -math.pi / 2 + sig(lean, 0.3)
        if scfg.get('head_up', True) and not scfg.get('invert'):
            th['h'] = th['t'].copy()
        elif scfg.get('invert'):
            u = np.clip((0.35 - f) / 0.7, 0, 1); u = u * u * (3 - 2 * u)
            th['h'] = th['t'] + math.pi * u
        def mirror(keys):
            for k in keys:
                a, b = th['R' + k], math.pi - th['L' + k]
                m = a + wrap(b - a) / 2
                th['R' + k] = np.unwrap(m); th['L' + k] = np.unwrap(math.pi - m)
        if scfg.get('mirror_front_legs'): mirror(('th', 'sh', 'ft'))
        if scfg.get('mirror_front_arms'): mirror(('ua', 'fa', 'hd'))
        print(f"  front plan: torso length factor {f.min():.2f}..{f.max():.2f} (Julie upright torso {Tup:.0f}px)")
        return f

    def draw_side(self, canvas, S, Tpx, st):
        P, g = self.P, S['g']; sp = g
        for s in 'LR':
            put(canvas, P[s + 'th'], S[s + 'hip'], S[s + 'kn'], sp)
            put(canvas, P[s + 'sh'], S[s + 'kn'], S[s + 'an'], sp)
            # foot: source T-stand foot direction, turned with the shin
            sv = S[s + 'an'] - S[s + 'kn']; a_sh = math.atan2(sv[1], sv[0])
            so = self.SJ[s + 'an'] - self.SJ[s + 'kn']; fo = self.SJ[s + 'toe'] - self.SJ[s + 'an']
            rot = a_sh - math.atan2(so[1], so[0]) if self.scfg.get('feet_follow_shin', True) else 0.0
            cr, sr = math.cos(rot), math.sin(rot); fd = np.array([cr * fo[0] - sr * fo[1], sr * fo[0] + cr * fo[1]])
            put(canvas, P[s + 'ft'], S[s + 'an'], S[s + 'an'] + fd * g, sp)
        hm, sm = S['hm'], S['sm']
        top = sm + (sm - hm) / (np.linalg.norm(sm - hm) + 1e-9) * 2 * g if np.linalg.norm(sm - hm) > 4 * g else sm
        put(canvas, self.torso_var[0], top, hm, sp)
        def arms():
            for s in 'LR':
                u = S[s + 'el'] - S[s + 'sh']; u = u / (np.linalg.norm(u) + 1e-9)
                put(canvas, P[s + 'delt'], S[s + 'sh'] + u * 2 * g, S[s + 'sh'] + u * 4 * g, sp, sa=g)
                put(canvas, P[s + 'ua'], S[s + 'sh'], S[s + 'el'], sp)
                put(canvas, P[s + 'fa'], S[s + 'el'], S[s + 'wr'], sp)
                put(canvas, P[s + 'hand'], S[s + 'wr'], S[s + 'tip'], sp, sa=g)
        if self.scfg.get('arms_over_head'):
            put(canvas, P['head'], S['neck'], S['crown'], sp, 1.0, sa=g); arms()
        else:
            arms(); put(canvas, P['head'], S['neck'], S['crown'], sp, 1.0, sa=g)

    def cairo_under(self, c, S, Tpx, gt, floor_y=902.0):
        pts = np.array([S[k] for k in S if isinstance(S[k], np.ndarray) and S[k].shape == (2,) and k not in ('ax',)])
        x0, x1 = float(pts[:, 0].min()), float(pts[:, 0].max())
        R.floor_shadow(c, (x0 + x1) / 2, floor_y + 2, max(0.45 * Tpx, (x1 - x0) / 2 + 0.15 * Tpx), 0.07 * Tpx, 0.26)
        if self.scfg.get('tail', True):
            R.draw_tail(c, S['hm'], Tpx, min(S['hm'][1] + 0.06 * Tpx, floor_y - 0.3 * Tpx), gt, side=1)
