#!/usr/bin/env python3
"""make_pose.py --src <video> --name '<Pose Name>' [--chair] [--config cfg.json] [--out out.mp4]
Real footage -> MediaPipe keypoints -> 2D Hani puppet -> bold Hani layer (Triangle v2 style) -> mp4.
The human footage is used only as motion reference and is never drawn."""
import argparse, json, math, os, random, subprocess, sys, time
import numpy as np, cairo
from PIL import Image
from scipy.signal import savgol_filter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import motion as M
import hani_rig as HR
import bold as BD
from bold_base import draw_caps, breath_layer, stars_layer, fireflies, paste, SPARK, with_alpha, ease, clamp
import bold_base as BB

ROOT = '/workspace/hani'; W, H, FPS = 1920, 1080, 25; XF = 0.6
JN = {'Lsh': 11, 'Rsh': 12, 'Lel': 13, 'Rel': 14, 'Lwr': 15, 'Rwr': 16, 'Lhip': 23, 'Rhip': 24, 'Lkn': 25, 'Rkn': 26,
      'Lan': 27, 'Ran': 28, 'Ltoe': 31, 'Rtoe': 32}

def slugify(s): return ''.join(ch if ch.isalnum() else '_' for ch in s).strip('_')

def load_cfg(a):
    cfg = {}
    path = a.config or os.path.join(ROOT, 'poses/configs', slugify(a.name) + ('_Chair' if a.chair else '') + '.json')
    if os.path.exists(path): cfg = json.load(open(path)); print('config:', path)
    else: print('no config found at', path, '- using generic defaults')
    cfg.setdefault('name', a.name); cfg.setdefault('signal', 'hinge'); cfg.setdefault('sides', 1)
    cfg.setdefault('badge', 'Desk Yoga' if a.chair else None)
    cfg.setdefault('chair', {'mode': 'seat'} if a.chair else None)
    cfg.setdefault('captions', {'setup': ['Stand tall and get ready'], 'enter': [f'Move into {a.name}'],
                                'hold_intro': 'Hold it right there!', 'exit': ['Slowly come back']})
    cfg.setdefault('glow', {'type': 'triangle', 'joints': ['wr', 'hip', 'an']})
    cfg.setdefault('fact', {'lines': ['Yoga helps your body and brain', 'feel calm and strong!'], 'ill': 'bridge'})
    cfg.setdefault('torso_px', 195)
    return cfg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', required=True); ap.add_argument('--name', required=True)
    ap.add_argument('--chair', action='store_true'); ap.add_argument('--config'); ap.add_argument('--out')
    ap.add_argument('--preview', help='comma list of output seconds to render as PNG only')
    ap.add_argument('--max_mb', type=float, default=7.5)
    ap.add_argument('--rig', default='vector', choices=['vector', 'puppet', 'puppet3'], help='puppet = cut-out Hani from the Triangle frames')
    ap.add_argument('--dump', help='write per-frame skeleton diagnostics npz and exit')
    ap.add_argument('--bg', help='background PNG (default: classroom / brand studio)')
    ap.add_argument('--motion_start', type=float, default=None, help='ignore source motion before this second')
    ap.add_argument('--fx', help="override cfg['fx']: none | beam | wild")
    ap.add_argument('--idle', type=float, default=0.0, help='open on Hani held still for N s with the title overlaid (replaces the intro card)')
    ap.add_argument('--lang', help="opt-in on-screen language, e.g. es (default: config 'lang' or en)")
    a = ap.parse_args(); t_start = time.time()
    cfg = load_cfg(a)
    if a.lang: cfg['lang'] = a.lang
    if cfg.get('lang', 'en') != 'en':   # opt-in: translated on-screen text (poses/i18n/<lang>.json)
        import i18n; i18n.activate(cfg['lang'])
        import atexit; atexit.register(lambda: print('i18n MISSING:', sorted(i18n.MISSING)))
    if a.fx: cfg['fx'] = None if a.fx == 'none' else a.fx
    if cfg.get('fx') and cfg.get('fact_heading_' + cfg['fx']): cfg['fact_heading'] = cfg['fact_heading_' + cfg['fx']]
    slug = slugify(a.name) + ('_Chair' if a.chair else '')
    work = os.path.join(ROOT, 'work', slug); os.makedirs(work, exist_ok=True)
    out = a.out or os.path.join(ROOT, 'poses', f'Hani_{slug}_v1.mp4')

    # 1) keypoints (cached)
    kp = os.path.join(work, 'kp.npz')
    if not os.path.exists(kp):
        import keypoints; keypoints.extract(a.src, kp)
    d = np.load(kp); fps = float(d['fps']); Kraw = d['K']; n_src = len(Kraw)
    SIDE = cfg.get('mode') == 'side'                     # opt-in side-view / floor mode (puppet/rig_side.py)
    if SIDE and cfg.get('side', {}).get('fix_swaps', True): Kraw = M.fix_lr_swaps(Kraw)
    K = M.clean(Kraw, fps)
    # 2) trim title card: first scene cut in the first 20 s, then first frame with a detection
    cuts = [t for t in M.scene_cuts(a.src) if 1.0 < t < 20.0]
    first = int(math.ceil((cuts[0] + 0.3) * fps)) if cuts else 0
    det = np.where(~np.isnan(Kraw[:, 0, 0]))[0]; first = max(first, int(det[det >= first][0]) if len(det[det >= first]) else first)
    if a.motion_start is not None: first = max(first, int(round(a.motion_start * fps)))
    print(f'motion starts at {first/fps:.2f}s')
    # 3) phases
    sig = M.signal(K, cfg['signal'])
    phases = M.detect_phases(sig, fps, first, cfg['sides'])
    for i, p in enumerate(phases):
        print(f"side {i}: enter {p['enter_start']/fps:.1f}s hold {p['hold_start']/fps:.1f}-{p['hold_end']/fps:.1f}s exit {p['exit_end']/fps:.1f}s")
    if cfg.get('enter_from') == 'arms_up':
        au = M.signal(K, 'arms_up')
        for p in phases:
            j = p['hold_start']; lim = max(first, j - int(12 * fps))
            ups = [k for k in range(lim, j) if au[k] > 0.5]
            if ups:
                k = ups[-1]
                while k > lim and au[k - 1] > 0.5: k -= 1
                p['enter_start'] = min(p['enter_start'], k)
                nz = [q for q in range(k, j) if p['norm'][q] > 0.15]   # where the twist itself begins
                if nz: p['enter_split'] = nz[0]
                print(f"  arms-up reach {k/fps:.1f}-{ups[-1]/fps:.1f}s before hold at {j/fps:.1f}s")
    sides = []
    prev_end = first
    if cfg.get('timeline'):
        # explicit hand-picked source segments per phase: [[src0, src1, speed], ...]; hold = [src0, src1] (ping-pong to 27 s)
        def pw(segs):
            segs = [(a_, b_, sp_) for a_, b_, sp_ in segs]; outd = [(b_ - a_) / sp_ for a_, b_, sp_ in segs]
            def f(t, segs=segs, outd=outd):
                acc = 0.0
                for (a_, b_, sp_), d_ in zip(segs, outd):
                    if t < acc + d_: return a_ + (t - acc) * sp_
                    acc += d_
                return segs[-1][1]
            return sum(outd), f
        phases = []
        for side in cfg['timeline']:
            pcs = []
            for name in ('setup', 'enter', 'enter_b'):
                if name in side: d_, f_ = pw(side[name]); pcs.append((name, d_, f_))
            ha, hb = side['hold']; hdur = max(hb - ha, 0.5)
            def pp(t, a_=ha, d_=hdur):
                k = int(t // d_); u = t - k * d_
                return a_ + (u if k % 2 == 0 else d_ - u)
            pcs.append(('hold', 27.0, pp))
            d_, f_ = pw(side['exit']); pcs.append(('exit', d_, f_))
            sides.append(pcs)
            phases.append(dict(enter_start=int(side['enter'][0][0] * fps), hold_start=int(ha * fps), hold_end=int(hb * fps),
                               exit_end=int(side['exit'][-1][1] * fps), norm=np.zeros(n_src)))
            print(f"timeline side: setup {side['setup'][0][0]}s enter {side['enter'][0][0]}s hold {ha}-{hb}s exit to {side['exit'][-1][1]}s")
    for i, p in enumerate(phases if not cfg.get('timeline') else []):
        last = i == len(phases) - 1
        pieces = M.build_map(p, fps, max(first, prev_end), n_src, cfg.get('setup_len', 7.0), cfg.get('max_enter', 8.0),
                             tail=cfg.get('tail_last', 1.5) if last else 1.5, min_rise=cfg.get('min_rise', 0.0), min_enter=cfg.get('min_enter', 4.0),
                             min_exit=cfg.get('min_exit_last', 4.0) if last else 4.0)
        prev_end = int(p['exit_end'] + 0.5 * fps)
        sides.append(pieces)

    # 4) per-scene output keypoints + captions
    caps_cfg = cfg['captions']
    def side_scene(si, pieces):
        if si == 0 and a.idle > 0:
            st0 = pieces[0][2](0.0)
            pieces = [('idle', a.idle, lambda t, v=st0: v)] + pieces
        dur = sum(pc[1] for pc in pieces); nf = int(round(dur * FPS))
        src_t = np.zeros(nf); phase = []; t0s = {}; acc = 0
        for name, pd, fn in pieces: t0s[name] = (acc, pd); acc += pd
        for n in range(nf):
            t = n / FPS
            for name, pd, fn in pieces:
                s0, _ = t0s[name]
                if t < s0 + pd or name == 'exit':
                    src_t[n] = fn(min(t - s0, pd)); phase.append((name, t - s0)); break
        fidx = np.clip(src_t * fps, 0, n_src - 1)
        i0 = np.floor(fidx).astype(int); i1 = np.minimum(i0 + 1, n_src - 1); w = (fidx - i0)[:, None, None]
        KO = K[i0] * (1 - w) + K[i1] * w
        win = int(FPS * 0.5) | 1
        if nf > win:
            for j in range(33):
                for c in range(3): KO[:, j, c] = savgol_filter(KO[:, j, c], win, 2)
        # gentle holds: settle toward the mean hold pose (keeps a little life), ramped in/out over 1.2 s
        hk = cfg.get('hold_settle', 0.0)
        if hk > 0:
            h0_, hd_ = t0s['hold']; a0, a1 = int(h0_ * FPS), int((h0_ + hd_) * FPS)
            mean = KO[a0:a1].mean(0)
            ramp = np.zeros(nf); r = int(1.2 * FPS)
            for n in range(max(0, a0 - r), min(nf, a1 + r)):
                ramp[n] = hk * min(1, (n - (a0 - r)) / r, ((a1 + r) - n) / r)
            KO = KO * (1 - ramp[:, None, None]) + mean[None] * ramp[:, None, None]
        # silky, zero-phase easing of all joints (no jitter or snapping)
        sg = cfg.get('smooth_sigma', 0.0)
        if sg > 0:
            from scipy.ndimage import gaussian_filter1d
            KO[..., :3] = gaussian_filter1d(KO[..., :3], sg * FPS, axis=0, mode='nearest')
        # captions (scene-local seconds)
        caps = []
        if cfg.get('caption_plan'):
            cp = cfg['caption_plan'][min(si, len(cfg['caption_plan']) - 1)]
            if 'idle' in t0s: caps.append((0.0, t0s['idle'][1], caps_cfg.get('idle', "Let's do " + cfg['name'] + ' together!')))
            for ph_name, lst in cp.items():
                if ph_name not in t0s: continue
                p0, pd_ = t0s[ph_name]
                for c0, c1, txt in lst:
                    c1 = pd_ if c1 is None else c1
                    caps.append((p0 + c0, p0 + min(c1, pd_ if ph_name != 'exit' else 1e9), txt))
            caps = [c for c in caps if c[1] - c[0] > 0.3]; caps.sort()
            return dict(nf=nf, dur=nf / FPS, K=KO, phase=phase, t0s=t0s, caps=caps, side=si)
        def spread(lst, s, e, min_len=1.6):
            lst = [x for x in lst if x]
            if not lst or e - s < 0.5: return
            k = max(1, min(len(lst), int((e - s) // min_len)))
            step = (e - s) / k
            for j in range(k): caps.append((s + j * step, s + (j + 1) * step, lst[j]))
        if 'idle' in t0s: caps.append((0.0, t0s['idle'][1], caps_cfg.get('idle', "Let's do " + cfg['name'] + ' together!')))
        st = caps_cfg.get('setup2' if si == 1 and 'setup2' in caps_cfg else 'setup', [])
        s0, sd = t0s['setup']; spread(st, s0, s0 + sd)
        s0, sd = t0s['enter']; ent = caps_cfg.get('enter', [])
        stretch = caps_cfg.get('stretch')
        if stretch and len(ent) >= 2:
            e1 = t0s['hold'][0]; n0, n1 = int(s0 * FPS), min(nf - 1, int(e1 * FPS))
            hgt = ((KO[n0:n1, 11, 1] + KO[n0:n1, 12, 1]) - (KO[n0:n1, 15, 1] + KO[n0:n1, 16, 1])) / 2
            pk = int(np.argmax(hgt >= 0.92 * hgt.max())); dn_ = [k for k in range(int(np.argmax(hgt)), len(hgt)) if hgt[k] < 0.75 * hgt.max()]
            tp = s0 + pk / FPS; td = s0 + (dn_[0] / FPS if dn_ else (e1 - s0) * 0.6)
            tp = max(tp, s0 + 2.0); td = min(max(td, tp), e1 - 2.0)
            tp = max(tp, td - 5.0); td = max(td, e1 - 5.0) if td - tp >= 2.0 else td
            if td - tp > 5.0: tp = td - 5.0
            if td - tp >= 2.0:
                caps.extend([(s0, tp, ent[0]), (tp, td, stretch), (td, e1, ent[1])])
            else:
                m_ = float(np.clip((tp + td) / 2, s0 + 2.0, e1 - 2.0)); caps.extend([(s0, m_, ent[0]), (m_, e1, ent[1])])
        elif 'enter_b' in t0s and len(ent) >= 2:
            b0, bd = t0s['enter_b']
            stretch = caps_cfg.get('stretch')
            if stretch and sd >= 3.9:
                n0, n1 = int(s0 * FPS), min(nf - 1, int((s0 + sd) * FPS))
                hgt = ((KO[n0:n1, 11, 1] + KO[n0:n1, 12, 1]) - (KO[n0:n1, 15, 1] + KO[n0:n1, 16, 1])) / 2
                r = (int(np.argmax(hgt >= 0.92 * hgt.max())) / FPS) if len(hgt) else sd / 2
                r = float(np.clip(max(r, sd - 5.0), 2.0, min(5.0, sd - 2.0)))
                caps.append((s0, s0 + r, ent[0])); caps.append((s0 + r, s0 + sd, stretch))
            else: spread(ent[:1], s0, s0 + sd, 1.2)
            spread(ent[1:], b0, b0 + bd, 1.2)
        else: spread(ent, s0, s0 + sd, 1.2)
        h0, hd = t0s['hold']
        caps.append((h0, h0 + 3, caps_cfg.get('hold_intro', 'Hold it!')))
        for k in range(3):
            caps += [(h0 + 3 + 8 * k, h0 + 7 + 8 * k, 'Breathe in...'), (h0 + 7 + 8 * k, h0 + 11 + 8 * k, 'Breathe out...')]
        x0, xd = t0s['exit']; exl = caps_cfg.get('exit2' if si == 1 and 'exit2' in caps_cfg else 'exit', [])
        done = False
        if cfg.get('enter_from') == 'arms_up' and len(exl) == 3:
            au = M.signal(K, 'arms_up'); nn = range(int(x0 * FPS), nf)
            up = [n for n in nn if au[min(n_src - 1, int(src_t[n] * fps))] > 0.5]
            if up:
                u0 = up[0] / FPS; u1 = u0
                for n in up:
                    if n / FPS - u1 > 0.2: break
                    u1 = n / FPS
                u0 = u0 - 0.3
                if u0 >= x0 + 2.2:
                    u1 = max(u0 + 2.2, u1)
                    caps.extend([(x0, u0, exl[0]), (u0, u1, exl[1]), (u1, max(u1 + 2.0, x0 + xd), exl[2])])
                else:   # arms rise right away: one combined caption so words match the picture
                    u1 = max(x0 + 2.4, u1)
                    caps.extend([(x0, u1, caps_cfg.get('exit_merge', 'Unwind and reach up tall')), (u1, max(u1 + 2.0, x0 + xd), exl[2])])
                done = True
        if not done: spread(exl, x0, x0 + xd, 1.4)
        caps = [c for c in caps if c[1] - c[0] > 0.3]
        caps.sort()
        return dict(nf=nf, dur=nf / FPS, K=KO, phase=phase, t0s=t0s, caps=caps, side=si)
    scenes = [side_scene(i, pc) for i, pc in enumerate(sides)]
    CELE = cfg.get('celebrate') or {}
    if CELE.get('blast_caption'):   # opt-in: big confetti blast when this caption appears (last scene that has it)
        for sc_ in scenes:
            hits = [c0 for (c0, c1, txt) in sc_['caps'] if txt.startswith(CELE['blast_caption'])]
            if hits: sc_['blast_t'] = hits[-1]
        for sc_ in scenes[:-1]:
            if 'blast_t' in sc_ and 'blast_t' in scenes[-1]: del sc_['blast_t']
        print('celebrate: blast at scene-local', [round(sc_.get('blast_t', -1), 2) for sc_ in scenes])
    for i, sc_ in enumerate(scenes):
        p = phases[i]; sc_['twist_sign'] = 1 if np.mean(sig[p['hold_start']:p['hold_end'] + 1]) >= 0 else -1

    # 5) screen transform (shared by all scenes)
    allK = np.concatenate([s['K'] for s in scenes])
    sh, hp = M.mid(allK, 11, 12), M.mid(allK, 23, 24)
    Tsrc = float(np.median(np.linalg.norm(sh - hp, axis=1)))
    Tpx = cfg['torso_px']; sc = Tpx / Tsrc
    floor_src = float(np.percentile(allK[:, [27, 28, 31, 32], 1], 92))
    body = allK[:, [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28, 31, 32], :2]
    xlo, xhi = np.percentile(body[..., 0], 1), np.percentile(body[..., 0], 99)
    ylo = np.percentile(body[..., 1], 1)
    # fit: horizontal extent incl. tail/head margin within 1150 px, head top below y=150
    span = (xhi - xlo) * sc * cfg.get('fit_span_k', 1.0) + 2.0 * Tpx   # fit_span_k: opt-in (Oct 12 batch 2), absent = 1.0
    FIT = not cfg.get('fit_off', False)   # fit_off: opt-in (Oct 12 batch 2) - keep torso_px, skip the auto-fit
    if FIT and span > 1250: sc *= 1250 / span; Tpx = Tsrc * sc
    sh_top = np.percentile(allK[:, [11, 12], 1], 1); wr_top = np.percentile(allK[:, [15, 16], 1], 1)
    top = (sh_top - floor_src) * sc + 900 - 1.5 * Tpx           # head sits above the shoulders
    if FIT and top < 110: f = (900 - 110) / (900 - top); sc *= f; Tpx = Tsrc * sc
    wt = (wr_top - floor_src) * sc + 900 - 0.15 * Tpx            # raised hands may go higher, but stay on screen
    if FIT and wt < 30: f = (900 - 30) / (900 - wt); sc *= f; Tpx = Tsrc * sc
    xc = (xlo + xhi) / 2
    def tf(p): return ((p[0] - xc) * sc + 960, (p[1] - floor_src) * sc + 900)
    # character box for firefly avoidance
    BB.AVOID[:] = [960 + (xlo - xc) * sc - 1.2 * Tpx, 150, 960 + (xhi - xc) * sc + 1.2 * Tpx, 940]

    # chair spec
    chair = None
    if cfg.get('chair'):
        mode = cfg['chair'].get('mode', 'seat'); s0 = scenes[0]
        h0, hd = s0['t0s']['hold']; hs = slice(int(h0 * FPS), int((h0 + hd) * FPS))
        KH = s0['K'][hs]
        if mode == 'hands':
            wr = np.median(M.mid(KH, 15, 16), axis=0); hpm = np.median(M.mid(KH, 23, 24), axis=0)
            wx, wy = tf(wr); dirn = 1 if wr[0] < hpm[0] else -1   # +1: hips right of hands -> seat extends left
            chair = dict(view='side', x=wx - dirn * 6, floor=900, back_top=wy + 0.09 * Tpx,
                         seat_y=900 - (900 - wy) * 0.56, dir=-dirn)
        else:
            hpm = np.median(M.mid(allK, 23, 24), axis=0); shm = np.median(M.mid(allK, 11, 12), axis=0)
            swid = np.median(np.abs(allK[:, 11, 0] - allK[:, 12, 0])) * sc
            hx, hy = tf(hpm); sx, sy = tf(shm)
            if swid > 0.45 * Tpx or cfg['chair'].get('view') == 'front':
                chair = dict(view='front', x=hx, floor=900, seat_y=hy + 0.2 * Tpx, back_top=sy + 0.15 * Tpx, width=1.7 * Tpx)
            else:
                nose = np.median(allK[:, 0, 0]); fdir = 1 if nose > hpm[0] else -1
                chair = dict(view='side', x=hx - fdir * 0.45 * Tpx, floor=900, seat_y=hy + 0.2 * Tpx,
                             back_top=sy + 0.1 * Tpx, dir=fdir)
    # per-scene derived state: facing, near side
    for s in scenes:
        Ks = s['K']; T_s = np.linalg.norm(M.mid(Ks, 11, 12) - M.mid(Ks, 23, 24), axis=1) + 1e-6
        ear = (Ks[:, 7, 0] + Ks[:, 8, 0]) / 2
        f = np.clip((Ks[:, 0, 0] - ear) / (0.18 * T_s), -1, 1)
        win = int(FPS * 1.2) | 1
        s['facing'] = savgol_filter(f, win, 1) if len(f) > win else f
        zl = Ks[:, [11, 23, 25], 2].mean(1); zr = Ks[:, [12, 24, 26], 2].mean(1)
        dz = savgol_filter(zl - zr, int(FPS * 2) | 1, 1) if len(zl) > 51 else zl - zr
        near = []; cur = 'L' if dz[0] < 0 else 'R'
        for v in dz:
            if cur == 'L' and v > 0.15 * Tsrc: cur = 'R'
            elif cur == 'R' and v < -0.15 * Tsrc: cur = 'L'
            near.append(cur)
        s['near'] = near
        tw = M.signal(Ks, cfg['signal']) if cfg['signal'] in ('twist', 'side_lean') else np.zeros(len(Ks))
        lim = np.percentile(np.abs(tw), 97) + 1e-6
        tw = np.clip(tw / lim, -1, 1); w2 = int(FPS * 1.0) | 1
        s['twist'] = savgol_filter(tw, w2, 1) if len(tw) > w2 else tw
        from scipy.ndimage import gaussian_filter1d as _gf
        s['visL'] = _gf(np.nan_to_num(Ks[:, 15, 3], nan=1.0), 0.35 * FPS, mode='nearest'); s['visR'] = _gf(np.nan_to_num(Ks[:, 16, 3], nan=1.0), 0.35 * FPS, mode='nearest')

    # 6) segment timeline
    segs = ([] if a.idle > 0 else [('intro', 3.6, None)]) + [('scene', scenes[0]['dur'], scenes[0])]
    if len(scenes) > 1: segs += [('fact', 4.8, None), ('scene', scenes[1]['dur'], scenes[1])]
    else: segs += [('fact', 4.8, None)]
    segs += [('outro', 4.2, None)]
    starts = []; t = 0
    for sg in segs: starts.append(t); t += sg[1] - XF
    TOTAL = t + XF; NF = int(round(TOTAL * FPS))

    bg_png = a.bg or os.path.join(ROOT, 'work', 'classroom_bg.png')
    if a.rig.startswith('puppet') and not a.bg: bg_png = os.path.join(ROOT, 'brand', 'studio_chair.png' if chair else 'studio_floor.png')
    if not os.path.exists(bg_png): HR.classroom(bg_png)
    if a.rig.startswith('puppet'):
        sys.path.insert(0, os.path.join(ROOT, 'puppet')); import rig as PR
        T_ = Tpx
        if a.rig == 'puppet3':
            import rig3 as PR3; PUP = PR3.Puppet3()
            if SIDE: import rig_side as PRS; PUP = PRS.PuppetSide(cfg.get('side'))
            if SIDE and cfg.get('side', {}).get('front'): import rig_front as PRF; PUP = PRF.PuppetFront(cfg.get('side'))   # opt-in front view (Oct 12 b2)
        else: PUP = PR.Puppet()
        allS = [tf(p) for p in M.mid(allK, 23, 24)]; jh = np.median(np.array(allS), axis=0)
        jsm = np.median(np.array([tf(p) for p in M.mid(allK, 11, 12)]), axis=0)
        def blen(i, j): return float(np.median(np.linalg.norm(allK[:, i, :2] - allK[:, j, :2], axis=1))) * sc
        seat_y = 868 - 0.76 * T_
        CAL = dict(ankle_y=868.0, seat_y=seat_y, hx=960.0, dy=(seat_y - 0.08 * T_) - jh[1],
                   kua=PUP.len['ua'] * (T_ / PR.SRC_T) / ((blen(11, 13) + blen(12, 14)) / 2),
                   kfa=PUP.len['fa'] * (T_ / PR.SRC_T) / ((blen(13, 15) + blen(14, 16)) / 2),
                   sw0=float(np.percentile(np.abs(allK[:, 11, 0] - allK[:, 12, 0]), 90)) * sc)
        CAL['chair'] = dict(x=960.0, floor=900.0, seat_y=seat_y, back_top=(jsm[1] + CAL['dy']) + 0.20 * T_)
        chair = None   # the puppet path draws its own wood chair
        STAND = cfg.get('mode') == 'stand'
        CAL['yaw_max'] = cfg.get('yaw_max', 1.0); CAL['torso_turn'] = cfg.get('torso_turn', 1.0)
        if cfg.get('rest_phases') is not None: CAL['rest_phases'] = tuple(cfg['rest_phases'])
        if cfg.get('squat_from_hip'): CAL['squat_k'] = float(cfg['squat_from_hip'])   # opt-in (Oct 12 b2) front-filmed squats
        if STAND:
            CAL['chair'] = None; CAL['mode'] = 'stand'
            lh = sum(float(np.linalg.norm(PUP.SJ[s_ + a_] - PUP.SJ[s_ + b_])) for s_ in 'LR' for a_, b_ in (('hip', 'kn'), ('kn', 'an'))) / 2
            lj = (blen(23, 25) + blen(25, 27) + blen(24, 26) + blen(26, 28)) / 2
            CAL['kL'] = lh * (T_ / PR.SRC_T) / lj
        if a.rig == 'puppet3':
            for s_ in scenes:
                if SIDE:   # side-view plan: Julie's segment directions, Hani's lengths, joint limits, grounding
                    XJ = dict(JN, Lheel=29, Rheel=30, Lidx=19, Ridx=20)
                    Js = []
                    for Ks in s_['K']:
                        J = {k: tf(Ks[v]) for k, v in XJ.items()}; J['ear'] = tf((Ks[7] + Ks[8]) / 2); J['nose'] = tf(Ks[0]); Js.append(J)
                    scf = dict(cfg.get('side', {})); Kq = s_['K']
                    if 'F' not in scf: scf['F'] = 1 if np.median(Kq[:, 0, 0] - (Kq[:, 7, 0] + Kq[:, 8, 0]) / 2) > 0 else -1
                    if isinstance(scf.get('F'), list): scf['F'] = scf['F'][min(s_['side'], len(scf['F']) - 1)]
                    if 'near' not in scf: scf['near'] = 'L' if np.median(Kq[:, [11, 23], 2]) < np.median(Kq[:, [12, 24], 2]) else 'R'
                    scf['FJ'] = 900.0
                    s_['plan'] = PUP.plan_side(Js, [p_[0] for p_ in s_['phase']], Tpx, CAL, FPS, scf)
                    continue
                Js = []
                for Ks in s_['K']:
                    J = {k: tf(Ks[v]) for k, v in JN.items()}; J['ear'] = tf((Ks[7] + Ks[8]) / 2)
                    J['nose'] = tf(Ks[0]); J['lear'] = tf(Ks[7]); J['rear'] = tf(Ks[8]); Js.append(J)
                h0s, hds = s_['t0s']['hold']; hs_ = slice(int(h0s * FPS), int((h0s + hds) * FPS))
                KH = s_['K'][hs_]; noff = np.median(KH[:, 0, 0] - (KH[:, 7, 0] + KH[:, 8, 0]) / 2)
                hdir = -1 if noff < 0 else 1
                cal_s = dict(CAL)
                if STAND:
                    JH = Js[hs_] if hds > 0 else Js
                    cal_s['X0'] = float(np.median([(J['Lan'][0] + J['Ran'][0]) / 2 for J in JH]))
                    cal_s['FJ'] = float(np.median([max(J['Lan'][1], J['Ran'][1]) for J in JH]))
                    if cfg.get('head_dir') == 'front_knee':     # gaze over the front (bent-knee) hand
                        kb = M.knee_bends(KH); hdir = 1 if np.median(kb[:, 0] - kb[:, 1]) > 0 else -1
                    s_['cal'] = cal_s
                s_['plan'] = PUP.plan(Js, {'L': s_['K'][:, 15, 3], 'R': s_['K'][:, 16, 3]}, [p_[0] for p_ in s_['phase']],
                                      (h0s, h0s + hds), Tpx, cal_s, FPS, hdir)
                print(f"scene {s_['side']}: head turns {'image-left' if hdir < 0 else 'image-right'} in the hold")
        print('puppet cal', {k: (round(v, 2) if isinstance(v, float) else v) for k, v in CAL.items()})
    STAND = cfg.get('mode') == 'stand'
    import fx as FX
    BGS = cairo.ImageSurface.create_from_png(bg_png)
    rng = random.Random(9); blinks = []; tt = 1.0
    while tt < 400: blinks.append(tt); tt += rng.uniform(2.4, 4.4)
    def blink_at(t):
        for b in blinks:
            if b <= t < b + 0.2: return 1 - abs((t - b) / 0.1 - 1)
        return 0.0

    glow = cfg['glow']
    def glow_points(J, Tpx):
        if glow['type'] == 'triangle':
            pts = []
            for jn in glow['joints']:
                pts.append(((J['L' + jn][0] + J['R' + jn][0]) / 2, (J['L' + jn][1] + J['R' + jn][1]) / 2))
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
            k = glow.get('scale', 1.35)   # halo around the body so it isn't hidden behind the limbs
            pts = [(cx + (p[0] - cx) * k, min(905, cy + (p[1] - cy) * k)) for p in pts]
            return pts, True
        shm = ((J['Lsh'][0] + J['Rsh'][0]) / 2, (J['Lsh'][1] + J['Rsh'][1]) / 2)
        hpm = ((J['Lhip'][0] + J['Rhip'][0]) / 2, (J['Lhip'][1] + J['Rhip'][1]) / 2)
        cx, cy = (shm[0] + hpm[0]) / 2, (shm[1] + hpm[1]) / 2
        return HR.spiral_pts(cx, cy, 0.25 * Tpx, 1.25 * Tpx, glow.get('turns', 1.75), glow.get('rot', 0.0) + glow.get('_spin', 0.0), 0.6), False

    def scene_frame(s, lt, gt):
        n = min(s['nf'] - 1, int(round(lt * FPS)))
        ph, pl = s['phase'][n]
        Ks = s['K'][n]
        J = {k: tf(Ks[v]) for k, v in JN.items()}; J['ear'] = tf((Ks[7] + Ks[8]) / 2)
        J['nose'] = tf(Ks[0]); J['lear'] = tf(Ks[7]); J['rear'] = tf(Ks[8])
        S = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(S)
        c.set_source_surface(BGS); c.paint()
        if chair: HR.draw_chair(c, chair)
        if a.rig.startswith('puppet'):
            pst = dict(breath=0.0, vis_L=float(s['visL'][n]), vis_R=float(s['visR'][n]), head_tilt=0.03 * math.sin(gt * 1.1))
            h0_, _ = s['t0s']['hold']; hl_ = lt - h0_
            if 3 <= hl_ < 27: p_ = (hl_ - 3) % 8; pst['breath'] = ease(p_ / 4) if p_ < 4 else 1 - ease((p_ - 4) / 4)
            SK = PUP.skeleton3(s['plan'], n, Tpx, pst['breath'], pst['head_tilt']) if a.rig == 'puppet3' and not SIDE else (PUP.skeleton_side(s['plan'], n, Tpx, pst['breath'], pst['head_tilt']) if SIDE else PUP.skeleton(J, Tpx, pst, CAL))
            if SIDE:
                PUP.cairo_under(c, SK, Tpx, gt, cfg['side'].get('floor_y', 902.0) if cfg.get('side') else 902.0)
            elif STAND:
                FX.ground(c, s, n, SK, Tpx, lt, gt, cfg)
                PR.floor_shadow(c, SK['hm'][0], 904, 0.95 * Tpx, 0.07 * Tpx, 0.22)
                for sd in 'LR': PR.floor_shadow(c, SK[sd + 'an'][0] + (12 if sd == 'L' else -6) * Tpx / 200, 904, 0.30 * Tpx, 0.05 * Tpx, 0.40)
                FX.behind(c, s, n, SK, Tpx, lt, gt, cfg)
                PR.draw_tail(c, SK['hm'], Tpx, SK['hm'][1] + 0.06 * Tpx, gt, side=-SK['yaw_sign'] if cfg.get('tail_away') else 1)
            else:
                PR.draw_chair(c, CAL['chair'], Tpx)
                PR.floor_shadow(c, 960, 902, 0.75 * Tpx, 0.07 * Tpx, 0.25)
                PR.draw_tail(c, SK['hm'], Tpx, CAL['seat_y'], gt, side=1)
                PR.floor_shadow(c, SK['hm'][0], CAL['seat_y'] - 0.07 * Tpx, 0.55 * Tpx, 0.09 * Tpx, 0.35)
        h0, hd = s['t0s']['hold']; hl = lt - h0                      # hold-local time
        breath = 0.0
        if 3 <= hl < 27:
            p = (hl - 3) % 8; breath = ease(p / 4) if p < 4 else 1 - ease((p - 4) / 4)
        # glow behind Hani
        tip = None; gpts = None
        if 0 <= hl < 27.7 and glow['type'] != 'none':
            glow['_spin'] = lt * 0.35 * s.get('twist_sign', 1)
            gpts, closed = glow_points(J if not a.rig.startswith('puppet') else {k: tuple(SK[k]) for k in ('Lsh', 'Rsh', 'Lhip', 'Rhip')}, Tpx)
            prog = ease(hl / 1.6)
            alpha = 1.0 if hl < 1.6 else (max(0.55 + 0.35 * breath, 1 - (hl - 1.6) / 1.2 * 0.45) if hl < 27 else 0.55 * (1 - (hl - 27) / 0.7))
            tip = HR.glow_path(c, gpts, prog, closed, alpha=alpha, base_w=max(8, Tpx * 0.06))
        if not a.rig.startswith('puppet'):
            HR.draw_hani(c, J, Tpx, dict(near=s['near'][n], facing=float(s['facing'][n]), blink=blink_at(gt),
                                     breath=breath, tail_t=gt, twist=float(s['twist'][n]) * cfg.get('twist_draw', 0.0), head_tilt=0.05 * math.sin(gt * 1.3)))
        arr = np.frombuffer(S.get_data(), np.uint8).reshape(H, W, 4)[:, :, [2, 1, 0]]
        if a.rig.startswith('puppet'):
            cv_ = arr.astype(np.float32); (PUP.draw_side if SIDE else PUP.draw3 if a.rig == 'puppet3' else PUP.draw)(cv_, SK, Tpx, pst); arr = np.clip(cv_, 0, 255).astype(np.uint8)
        im = Image.fromarray(np.ascontiguousarray(arr)).convert('RGBA')
        if a.rig == 'puppet3' and STAND: FX.front(im, s, n, SK, Tpx, lt, gt, cfg)
        fireflies(im, gt)
        if 'blast_t' in s and lt >= s['blast_t']:
            import celebrate as CEL; CEL.blast(im, lt - s['blast_t'])   # over Hani, under the caption pill
        if tip is not None and hl < 1.6:
            sp = SPARK[24]; paste(im, sp, (tip[0] - sp.width / 2, tip[1] - sp.height / 2))
        elif gpts is not None and 1.6 <= hl < 2.8:
            q = (hl - 1.6) / 1.2; r2 = random.Random(3)
            anchors = gpts if len(gpts) <= 4 else gpts[::max(1, len(gpts) // 5)]
            for (vx, vy) in anchors:
                for j in range(6):
                    ang = r2.uniform(0, 6.28); dist = 20 + 110 * ease(q) * r2.uniform(.5, 1); sp = SPARK[r2.choice([10, 16])]
                    paste(im, sp, (vx + dist * math.cos(ang) - sp.width / 2, vy + dist * math.sin(ang) - sp.height / 2), 1 - q)
        # breath circle + stars use the Triangle v2 clock (hold starts at 8 there)
        if -3 < hl < 33:
            bl, bv = breath_layer(hl + 8)
            if bl: paste(im, bl, (50, 40), bv)
            sl, sv = stars_layer(hl + 8)
            if sl: paste(im, sl, (W - 40 - sl.width, 40), sv)
        if s['side'] == 0 and a.idle > 0 and lt < a.idle + 0.6:
            BD.title_overlay(im, lt, cfg['name'], cfg.get('badge'), a.idle)
        draw_caps(im, lt, s['caps'])
        return im

    def render_seg(i, lt, gt):
        kind, dur, s = segs[i]
        if kind == 'intro': return BD.intro_card(lt, cfg['name'], cfg.get('badge'))
        if kind == 'fact': return BD.fact_card(lt, cfg['fact']['lines'], cfg['fact'].get('ill', 'bridge'), heading=cfg.get('fact_heading', 'Fun fact!'))
        if kind == 'outro': return BD.outro_card(lt, cfg['name'], clear_text=(a.rig.startswith('puppet')), confetti=CELE.get('card', 'classic'))
        return scene_frame(s, lt, gt)
    def frame_at(tt):
        act = [(i, tt - starts[i]) for i in range(len(segs)) if starts[i] <= tt < starts[i] + segs[i][1]]
        if len(act) == 1: return render_seg(act[0][0], act[0][1], tt).convert('RGB')
        al = ease((tt - starts[act[1][0]]) / XF)
        return Image.blend(render_seg(act[0][0], act[0][1], tt).convert('RGB'), render_seg(act[1][0], act[1][1], tt).convert('RGB'), al)

    # timeline report
    tl = []
    for i, (kind, dur, s) in enumerate(segs):
        tl.append(dict(seg=kind, start=round(starts[i], 2), dur=round(dur, 2)))
        if s:
            for (c0, c1, txt) in s['caps']: tl.append(dict(caption=txt, start=round(starts[i] + c0, 2), end=round(starts[i] + c1, 2)))
    json.dump(dict(total=TOTAL, timeline=tl, phases=[{k: round(int(v) / fps, 2) for k, v in p.items() if k != 'norm'} for p in phases], src_fps=fps,
                   first_frame=first), open(os.path.join(work, 'timeline.json'), 'w'), indent=1)

    if a.dump:
        rows = []
        for si, s in enumerate(scenes):
            for n in range(s['nf']):
                Ks = s['K'][n]; lt = n / FPS
                J = {k: tf(Ks[v]) for k, v in JN.items()}; J['ear'] = tf((Ks[7] + Ks[8]) / 2)
                J['nose'] = tf(Ks[0]); J['lear'] = tf(Ks[7]); J['rear'] = tf(Ks[8])
                pst = dict(breath=0.0, vis_L=float(s['visL'][n]), vis_R=float(s['visR'][n]), head_tilt=0.0)
                SK = (PUP.skeleton_side(s['plan'], n, Tpx, 0.0, 0.0) if SIDE else PUP.skeleton3(s['plan'], n, Tpx, 0.0, 0.0)) if a.rig == 'puppet3' else PUP.skeleton(J, Tpx, pst, CAL)
                if 'wk' not in SK.get('_', {}): SK.setdefault('Lwk', 0.0); SK.setdefault('Rwk', 0.0)
                ang = lambda p, q: math.atan2(q[1] - p[1], q[0] - p[0])
                r = [si, lt]
                for sd in 'LR':
                    r += [ang(J[sd + 'sh'], J[sd + 'el']), ang(J[sd + 'el'], J[sd + 'wr']),      # v1 (vector rig uses J directly)
                          ang(SK[sd + 'sh'], SK[sd + 'el']), ang(SK[sd + 'el'], SK[sd + 'wr']), ang(SK[sd + 'wr'], SK[sd + 'tip']),
                          SK[sd + 'wk'], SK[sd + 'hid'], pst['vis_' + sd]]
                r += [SK['yaw'], SK['yaw_sign'], float(Ks[15, 3]), float(Ks[16, 3])]
                rows.append(r)
        import pickle; pickle.dump([{k: v for k, v in s_['plan'].items() if k != 'B'} for s_ in scenes] if a.rig == 'puppet3' else None, open(a.dump + '.plan.pkl', 'wb'))
        np.save(a.dump, np.array(rows)); print('dump', a.dump, len(rows)); return
    if a.preview:
        for tt in [float(x) for x in a.preview.split(',')]:
            frame_at(tt).save(os.path.join(work, f'prev_{tt:06.2f}.png'))
        print('preview done', time.time() - t_start); return

    # 7) audio events -> wav
    ev = {'total': TOTAL, 'chimes': [], 'inhale': [], 'sparkle': [], 'confetti': [], 'boops': [], 'breath_windows': []}
    for i, (kind, dur, s) in enumerate(segs):
        ev['chimes'].append(starts[i] + (0.2 if i == 0 else XF * 0.5))
        if kind == 'scene':
            h0 = s['t0s']['hold'][0]
            for k in range(3): ev['inhale'].append(starts[i] + h0 + 3 + 8 * k)
            ev['breath_windows'].append(starts[i] + h0 + 3)
            ev['sparkle'].append(starts[i] + h0 + 1.6)
            for (c0, c1, txt) in s['caps']:
                if not txt.startswith('Breathe'): ev['chimes'].append(starts[i] + c0)
        if kind == 'outro': ev['confetti'].append(starts[i] + 0.3)
        if kind == 'intro':
            for j, ch in enumerate(cfg['name']):
                if ch != ' ': ev['boops'].append(starts[i] + 0.15 + j * 0.06 + 0.12)
        if kind == 'scene' and s['side'] == 0 and a.idle > 0:
            for j, ch in enumerate(cfg['name']):
                if ch != ' ': ev['boops'].append(starts[i] + 0.25 + j * 0.06 + 0.12)
        if kind == 'fact': ev['sparkle'].append(starts[i] + 1.8)
    wtag = os.path.splitext(os.path.basename(out))[0]
    evp = os.path.join(work, wtag + '_events.json'); wav = os.path.join(work, wtag + '_audio.wav')
    json.dump(ev, open(evp, 'w'))
    subprocess.run([sys.executable, os.path.join(ROOT, 'build/audio.py'), evp, wav, 'v2'], check=True)
    party = [starts[i] + s['blast_t'] for i, (kind, dur, s) in enumerate(segs) if kind == 'scene' and 'blast_t' in s and CELE.get('sound', True)]
    if cfg.get('fx') or party:
        fxe = {'beam': [], 'sting': [], 'riser': [], 'party': party}
        for i, (kind, dur, s) in enumerate(segs):
            if kind != 'scene' or not cfg.get('fx'): continue
            h0 = starts[i] + s['t0s']['hold'][0]; fxe['beam'].append(h0)
            if cfg['fx'] == 'wild':
                fxe['sting'].append(h0); e0 = starts[i] + s['t0s']['enter'][0]; fxe['riser'].append([max(e0, h0 - 6.0), h0])
        fxp = os.path.join(work, wtag + '_fx_events.json'); json.dump(fxe, open(fxp, 'w'))
        subprocess.run([sys.executable, os.path.join(ROOT, 'pipeline/sting.py'), fxp, wav, wav], check=True)

    # 8) render frames -> intermediate -> final (size-capped 2-pass)
    mid_mkv = os.path.join(work, wtag + '_mid.mkv')
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', mid_mkv], stdin=subprocess.PIPE)
    t_r = time.time()
    for n in range(NF):
        ff.stdin.write(frame_at(n / FPS).tobytes())
        if n % 250 == 0: print(f'frame {n}/{NF}  {time.time()-t_r:.0f}s', flush=True)
    ff.stdin.close(); ff.wait()
    vb = int(min(1800, a.max_mb * 8e3 / TOTAL - 100))
    pl = os.path.join(work, wtag + '_pass')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mid_mkv, '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-b:v', f'{vb}k',
                    '-pass', '1', '-passlogfile', pl, '-an', '-f', 'null', '/dev/null'], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mid_mkv, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow',
                    '-tune', 'animation', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-b:v', f'{vb}k', '-maxrate', f'{vb*3}k', '-bufsize', f'{vb*6}k',
                    '-pass', '2', '-passlogfile', pl, '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', '-shortest', out], check=True)
    print(f'DONE {out}  {os.path.getsize(out)/1e6:.2f} MB  {TOTAL:.1f}s  total runtime {time.time()-t_start:.0f}s (render {time.time()-t_r:.0f}s)')

if __name__ == '__main__':
    main()
