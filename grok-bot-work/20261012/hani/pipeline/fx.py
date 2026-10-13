"""Pose-specific bold effects for standing poses (puppet3 'stand' mode). Locked palette only.
cfg['fx'] = None | 'beam' | 'wild'
  beam: fingertip-to-fingertip energy beam (halo behind the arms, bright core beyond the fingertips, glowing orbs at
        the fingertips, comet that ignites the beam from the back hand to the front hand at the start of the hold).
  wild: beam + 'power-up' aura that grows as Hani sinks into the lunge, rotating sunburst behind him that swells on
        every breath, 'strong as a mountain' ground ripples from the planted feet, rising energy sparks, hero flash."""
import math, random, sys
import numpy as np, cairo
from PIL import Image
from scipy.ndimage import gaussian_filter1d
sys.path.insert(0, '/workspace/hani/brand'); import palette as PAL
from bold_base import SPARK, paste, glowdot, ease, clamp

FPS = 25
GOLD = PAL.rgbf(PAL.GOLD); GLOW = PAL.rgbf(PAL.GLOW); CORE = PAL.rgbf(PAL.GLOW_CORE); TEAL = PAL.rgbf(PAL.TEAL)
ORB = {r: glowdot(r) for r in (7, 9, 11, 13)}

def _breath(hl):
    if 3 <= hl < 27:
        p = (hl - 3) % 8; return ease(p / 4) if p < 4 else 1 - ease((p - 4) / 4)
    return 0.0

def _prep(s, cfg, Tpx):
    """per-scene cached curves: lunge depth (power), arms-out amount, front side."""
    if '_fx' in s: return s['_fx']
    PL = s['plan']; n = s['nf']
    hy = np.array([b['hm'][1] for b in PL['B']])
    h0, hd = s['t0s']['hold']; a0, a1 = int(h0 * FPS), int((h0 + hd) * FPS)
    e0 = int(s['t0s']['enter'][0] * FPS)                 # power-up only from the start of the enter (not the setup jump)
    y_up = float(np.median(hy[max(0, e0 - 5):e0 + 5])); y_dn = np.median(hy[a0:a1])
    power = np.clip((hy - y_up) / (y_dn - y_up + 1e-6), 0, 1) if y_dn - y_up > 0.04 * Tpx else np.zeros(n)
    power[:e0] = 0.0
    power = gaussian_filter1d(power, 0.2 * FPS, mode='nearest')
    g = Tpx / 200.0; L = (103 + 94) * g; out = np.ones(n)
    for sd in 'LR':
        w = PL['arms'][sd]['wr']
        out = np.minimum(out, np.clip((w[:, 0] / L - 0.62) / 0.25, 0, 1) * np.clip(1 - np.abs(w[:, 1]) / (0.5 * L), 0, 1))
    out = gaussian_filter1d(out, 0.25 * FPS, mode='nearest')
    front = 'L' if PL['head_dir'] > 0 else 'R'
    s['_fx'] = dict(power=power, arms=out, front=front, back='R' if front == 'L' else 'L')
    return s['_fx']

def _hl(s, lt): return lt - s['t0s']['hold'][0]

def _beam_alpha(F, n, hl):
    if hl < -0.2 or hl > 27.8: return 0.0, 0.0
    prog = ease(hl / 1.6) if hl < 1.6 else 1.0
    a = 1.0 if hl < 2.0 else 0.62 + 0.38 * _breath(hl)
    if hl > 27: a *= clamp(1 - (hl - 27) / 0.8)
    return a * F['arms'][n], prog

def _beam_pts(SK, F, Tpx):
    b, f = F['back'], F['front']
    chain = [SK[b + 'tip'], SK[b + 'wr'], SK[b + 'el'], SK[b + 'sh'], SK[f + 'sh'], SK[f + 'el'], SK[f + 'wr'], SK[f + 'tip']]
    return [tuple(map(float, p)) for p in chain]

def _ext(SK, sd, Tpx, k=0.75):
    d = np.asarray(SK[sd + 'tip']) - np.asarray(SK[sd + 'wr']); d = d / (np.linalg.norm(d) + 1e-9)
    return tuple(map(float, SK[sd + 'tip'])), tuple(map(float, np.asarray(SK[sd + 'tip']) + d * k * Tpx))

BEAM_LAYERS = ((9, .14, GOLD), (6, .22, GOLD), (3.6, .42, GOLD), (2.2, .75, GLOW), (1.2, 1.0, GLOW), (0.6, 1.0, CORE))
def _stroke_glow(c, pts, w, a, layers=BEAM_LAYERS):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for k, al, col in layers:
        c.move_to(*pts[0])
        for p in pts[1:]: c.line_to(*p)
        c.set_source_rgba(*col, al * a); c.set_line_width(w * k); c.stroke()

def _partial(pts, prog):
    lens = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]; L = prog * sum(lens); out = [pts[0]]
    for i, l in enumerate(lens):
        if L >= l: out.append(pts[i + 1]); L -= l
        else:
            f = L / max(l, 1e-6); out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f)); break
    return out

# ------------------------------------------------------------------ layers
def ground(c, s, n, SK, Tpx, lt, gt, cfg):
    if cfg.get('fx') != 'wild': return
    F = _prep(s, cfg, Tpx); hl = _hl(s, lt)
    # warm floor glow under the feet while powered up
    p = F['power'][n]
    if p > 0.02:
        for sd in 'LR':
            x = float(SK[sd + 'an'][0]); c.save(); c.translate(x, 906); c.scale(0.55 * Tpx, 0.09 * Tpx)
            gr = cairo.RadialGradient(0, 0, 0, 0, 0, 1); gr.add_color_stop_rgba(0, *GLOW, 0.45 * p); gr.add_color_stop_rgba(1, *GLOW, 0)
            c.set_source(gr); c.arc(0, 0, 1, 0, 2 * math.pi); c.fill(); c.restore()
    # 'strong as a mountain' ripples: at the hold start and every breath-out
    starts = [0.0] + [7 + 8 * k for k in range(3)]
    for t0 in starts:
        u = hl - t0
        if not (0 <= u < 2.4): continue
        for j in range(3):
            v = u - j * 0.28
            if v <= 0: continue
            r = 0.15 * Tpx + 0.95 * Tpx * ease(min(1, v / 2.0)); a = 0.55 * (1 - v / 2.1) if v < 2.1 else 0
            if a <= 0: continue
            for sd in 'LR':
                x = float(SK[sd + 'an'][0])
                c.save(); c.translate(x, 908); c.scale(r, r * 0.16)
                c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()
                c.set_source_rgba(*(GOLD if j != 1 else TEAL), min(1, a * (1.2 if j == 0 else 0.8))); c.set_line_width(7 - 1.5 * j); c.stroke()

def behind(c, s, n, SK, Tpx, lt, gt, cfg):
    fx = cfg.get('fx')
    if not fx: return
    F = _prep(s, cfg, Tpx); hl = _hl(s, lt); br = _breath(hl)
    cx, cy = float(SK['sm'][0]), float(SK['sm'][1]) + 0.25 * Tpx
    if fx == 'wild':
        p = F['power'][n]
        hold_w = clamp((hl + 0.5) / 1.0) * clamp((28.2 - hl) / 1.0)
        inten = max(0.55 * p, hold_w)
        if inten > 0.01:
            # sunburst: soft rays, slowly rotating, swelling on every inhale
            R = (2.1 + 0.35 * br + 0.25 * p) * Tpx; rot = gt * 0.12; nr = 18
            for k in range(nr):
                a0 = rot + k * 2 * math.pi / nr; da = math.pi / nr * 0.55
                gr = cairo.RadialGradient(cx, cy, 0.3 * Tpx, cx, cy, R)
                col = GLOW if k % 2 == 0 else GOLD
                gr.add_color_stop_rgba(0, *col, 0.34 * inten); gr.add_color_stop_rgba(1, *col, 0)
                c.move_to(cx, cy); c.arc(cx, cy, R, a0 - da, a0 + da); c.close_path(); c.set_source(gr); c.fill()
            # aura around the body
            gr = cairo.RadialGradient(cx, cy - 0.2 * Tpx, 0, cx, cy - 0.2 * Tpx, (1.25 + 0.15 * br) * Tpx)
            gr.add_color_stop_rgba(0, *CORE, 0.55 * inten); gr.add_color_stop_rgba(0.55, *GLOW, 0.30 * inten); gr.add_color_stop_rgba(1, *GLOW, 0)
            c.set_source(gr); c.arc(cx, cy - 0.2 * Tpx, (1.25 + 0.15 * br) * Tpx, 0, 2 * math.pi); c.fill()
    # energy beam halo along the arms (behind the puppet) + light wash on the wall
    a, prog = _beam_alpha(F, n, hl); G = cfg.get('beam_gain', {'beam': 1.8, 'wild': 1.3}.get(fx, 1.0))
    if a > 0.01:
        sh = (np.asarray(SK['Lsh']) + np.asarray(SK['Rsh'])) / 2
        c.save(); c.translate(float(sh[0]), float(sh[1])); c.scale(2.6 * Tpx * (0.4 + 0.6 * prog), 0.55 * Tpx)
        gr = cairo.RadialGradient(0, 0, 0, 0, 0, 1); gr.add_color_stop_rgba(0, *CORE, min(1, 0.40 * a * G)); gr.add_color_stop_rgba(0.5, *GLOW, 0.22 * a * G); gr.add_color_stop_rgba(1, *GLOW, 0)
        c.set_source(gr); c.arc(0, 0, 1, 0, 2 * math.pi); c.fill(); c.restore()
        pts = _partial(_beam_pts(SK, F, Tpx), prog)
        _stroke_glow(c, pts, max(10, 0.10 * Tpx * G), min(1.0, a * G), layers=((7, .20, GOLD), (4.8, .32, GOLD), (3.2, .55, GLOW), (2.3, .8, CORE)))
    elif F['arms'][n] > 0.3 and hl < -0.2:   # charging: faint flicker along the arms before the hold
        fl = 0.18 + 0.10 * math.sin(gt * 9.0) + 0.06 * math.sin(gt * 23.0)
        _stroke_glow(c, _beam_pts(SK, F, Tpx), max(8, 0.07 * Tpx), 1.6 * fl * F['arms'][n], layers=((4.8, .25, GOLD), (3.0, .45, GLOW), (2.2, .5, CORE)))

def front(im, s, n, SK, Tpx, lt, gt, cfg):
    fx = cfg.get('fx')
    if not fx: return
    F = _prep(s, cfg, Tpx); hl = _hl(s, lt); br = _breath(hl)
    a, prog = _beam_alpha(F, n, hl); G = cfg.get('beam_gain', {'beam': 1.8, 'wild': 1.3}.get(fx, 1.0))
    if a > 0.01:
        # long beams shooting out of both hands (bright core), energy pulses flowing back hand -> front hand, orbs
        lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, im.width, im.height); c = cairo.Context(lay)
        w = max(12, 0.085 * Tpx * G)
        for sd, gate in ((F['back'], 0.0), (F['front'], 1.0)):
            p0, p1 = _ext(SK, sd, Tpx, (1.45 + 0.25 * br) * G)
            k = clamp(prog * 3) if gate == 0 else clamp((hl - 1.5) / 0.45)
            if k <= 0.02: continue
            p1 = (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
            # tapered: draw in 6 sub-segments with decreasing width/alpha
            for j in range(6):
                u0, u1 = j / 6, (j + 1) / 6
                q0 = (p0[0] + (p1[0] - p0[0]) * u0, p0[1] + (p1[1] - p0[1]) * u0); q1 = (p0[0] + (p1[0] - p0[0]) * u1, p0[1] + (p1[1] - p0[1]) * u1)
                _stroke_glow(c, [q0, q1], w * (1 - 0.6 * u0), min(1.0, a * (1 - 0.75 * u0) * (0.85 + 0.15 * G)))
            # inhale pulse: a bright bead racing out along each beam
            if hl > 3 and k > 0.9:
                u = ((hl - 3) % 8) / 4.0
                if u < 1:
                    bx, by = p0[0] + (p1[0] - p0[0]) * ease(u), p0[1] + (p1[1] - p0[1]) * ease(u)
                    c.arc(bx, by, w * 1.2, 0, 2 * math.pi); c.set_source_rgba(*CORE, 0.8 * (1 - u) * a); c.fill()
        lay.flush()
        arr = np.frombuffer(lay.get_data(), np.uint8).reshape(im.height, im.width, 4)[:, :, [2, 1, 0, 3]].copy()
        al = arr[..., 3:4].astype(np.float32); rgb = np.where(al > 0, arr[..., :3] * 255.0 / np.maximum(al, 1), 0)
        im.alpha_composite(Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), 'RGBA'))
        chain = _beam_pts(SK, F, Tpx)
        if hl >= 1.6:   # pulses riding the beam
            for j in range(3):
                u = ((hl - 1.6) * 0.55 + j / 3) % 1
                x, y = _partial(chain, u)[-1]; o = ORB[7]
                paste(im, o, (x - o.width / 2, y - o.height / 2), a * math.sin(math.pi * u) * 0.9)
        r = 11 + int(round(2 * br)) if hl > 2 else 11
        o = ORB[min(ORB, key=lambda q: abs(q - r))]
        for sd in (F['back'], F['front']):
            if sd == F['front'] and prog < 1.0: continue
            x, y = SK[sd + 'tip']
            paste(im, o, (x - o.width / 2, y - o.height / 2), a)
            tw = 0.5 + 0.5 * math.sin(gt * 5 + (0 if sd == 'L' else 2))
            sp = SPARK[24]; paste(im, sp, (x - sp.width / 2, y - sp.height / 2), a * (0.4 + 0.6 * tw))
        if hl < 1.6:   # comet igniting the beam back hand -> front hand
            x, y = _partial(chain, prog)[-1]; sp = SPARK[24]
            o = ORB[13]; paste(im, o, (x - o.width / 2, y - o.height / 2)); paste(im, sp, (x - sp.width / 2, y - sp.height / 2))
        elif hl < 2.8:  # sparkle burst + shock ring off the front hand
            q = (hl - 1.6) / 1.2; r2 = random.Random(8); x0, y0 = SK[F['front'] + 'tip']
            for j in range(14):
                ang = r2.uniform(0, 6.28); dist = 20 + 150 * ease(q) * r2.uniform(.5, 1); sp = SPARK[r2.choice([10, 16, 24])]
                paste(im, sp, (x0 + dist * math.cos(ang) - sp.width / 2, y0 + dist * math.sin(ang) - sp.height / 2), 1 - q)
    elif F['arms'][n] > 0.3 and hl < -0.2:   # charging sparks at the fingertips
        for sd in 'LR':
            x, y = SK[sd + 'tip']; tw = 0.5 + 0.5 * math.sin(gt * 7 + (0 if sd == 'L' else 1.7))
            sp = SPARK[16]; paste(im, sp, (x - sp.width / 2, y - sp.height / 2), 0.5 * tw * F['arms'][n])
    if fx == 'wild':
        p = F['power'][n]
        hold_w = clamp((hl + 0.5) / 1.0) * clamp((28.2 - hl) / 1.0)
        inten = max(0.55 * p, hold_w)
        if inten > 0.01:
            # sunburst: soft rays, slowly rotating, swelling on every inhale
            R = (2.1 + 0.35 * br + 0.25 * p) * Tpx; rot = gt * 0.12; nr = 18
            for k in range(nr):
                a0 = rot + k * 2 * math.pi / nr; da = math.pi / nr * 0.55
                gr = cairo.RadialGradient(cx, cy, 0.3 * Tpx, cx, cy, R)
                col = GLOW if k % 2 == 0 else GOLD
                gr.add_color_stop_rgba(0, *col, 0.34 * inten); gr.add_color_stop_rgba(1, *col, 0)
                c.move_to(cx, cy); c.arc(cx, cy, R, a0 - da, a0 + da); c.close_path(); c.set_source(gr); c.fill()
            # aura around the body
            gr = cairo.RadialGradient(cx, cy - 0.2 * Tpx, 0, cx, cy - 0.2 * Tpx, (1.25 + 0.15 * br) * Tpx)
            gr.add_color_stop_rgba(0, *CORE, 0.55 * inten); gr.add_color_stop_rgba(0.55, *GLOW, 0.30 * inten); gr.add_color_stop_rgba(1, *GLOW, 0)
            c.set_source(gr); c.arc(cx, cy - 0.2 * Tpx, (1.25 + 0.15 * br) * Tpx, 0, 2 * math.pi); c.fill()
    # energy beam halo along the arms (behind the puppet) + light wash on the wall
    a, prog = _beam_alpha(F, n, hl); G = cfg.get('beam_gain', {'beam': 1.8, 'wild': 1.3}.get(fx, 1.0))
    if a > 0.01:
        sh = (np.asarray(SK['Lsh']) + np.asarray(SK['Rsh'])) / 2
        c.save(); c.translate(float(sh[0]), float(sh[1])); c.scale(2.6 * Tpx * (0.4 + 0.6 * prog), 0.55 * Tpx)
        gr = cairo.RadialGradient(0, 0, 0, 0, 0, 1); gr.add_color_stop_rgba(0, *CORE, min(1, 0.40 * a * G)); gr.add_color_stop_rgba(0.5, *GLOW, 0.22 * a * G); gr.add_color_stop_rgba(1, *GLOW, 0)
        c.set_source(gr); c.arc(0, 0, 1, 0, 2 * math.pi); c.fill(); c.restore()
        pts = _partial(_beam_pts(SK, F, Tpx), prog)
        _stroke_glow(c, pts, max(10, 0.10 * Tpx * G), min(1.0, a * G), layers=((7, .20, GOLD), (4.8, .32, GOLD), (3.2, .55, GLOW), (2.3, .8, CORE)))
    elif F['arms'][n] > 0.3 and hl < -0.2:   # charging: faint flicker along the arms before the hold
        fl = 0.18 + 0.10 * math.sin(gt * 9.0) + 0.06 * math.sin(gt * 23.0)
        _stroke_glow(c, _beam_pts(SK, F, Tpx), max(8, 0.07 * Tpx), 1.6 * fl * F['arms'][n], layers=((4.8, .25, GOLD), (3.0, .45, GLOW), (2.2, .5, CORE)))

def front(im, s, n, SK, Tpx, lt, gt, cfg):
    fx = cfg.get('fx')
    if not fx: return
    F = _prep(s, cfg, Tpx); hl = _hl(s, lt); br = _breath(hl)
    a, prog = _beam_alpha(F, n, hl)
    if a > 0.01:
        # bright core beyond the fingertips (beam shooting out of both hands) + orbs
        lay = cairo.ImageSurface(cairo.FORMAT_ARGB32, im.width, im.height); c = cairo.Context(lay)
        w = max(8, 0.06 * Tpx)
        for sd, gate in ((F['back'], 0.0), (F['front'], 1.0)):
            if prog < 1.0 and gate > 0: continue
            p0, p1 = _ext(SK, sd, Tpx, 0.55 + 0.25 * br)
            k = 1.0 if gate == 0 else clamp((hl - 1.6) / 0.5)
            p1 = (p0[0] + (p1[0] - p0[0]) * k, p0[1] + (p1[1] - p0[1]) * k)
            if k > 0.02: _stroke_glow(c, [p0, p1], w * 0.8, a * 0.9)
        lay.flush()
        arr = np.frombuffer(lay.get_data(), np.uint8).reshape(im.height, im.width, 4)[:, :, [2, 1, 0, 3]].copy()
        # un-premultiply for PIL
        al = arr[..., 3:4].astype(np.float32); rgb = np.where(al > 0, arr[..., :3] * 255.0 / np.maximum(al, 1), 0)
        im.alpha_composite(Image.fromarray(np.dstack([np.clip(rgb, 0, 255), al]).astype(np.uint8), 'RGBA'))
        r = 9 + int(round(4 * br)) if hl > 2 else 9
        r = min(13, max(7, r - r % 2 + 1 if r % 2 == 0 else r))
        for sd in (F['back'], F['front']):
            if sd == F['front'] and prog < 1.0: continue
            o = ORB[min(ORB, key=lambda q: abs(q - r))]; x, y = SK[sd + 'tip']
            paste(im, o, (x - o.width / 2, y - o.height / 2), a)
        if hl < 1.6:   # comet igniting the beam back hand -> front hand
            pts = _partial(_beam_pts(SK, F, Tpx), prog); x, y = pts[-1]; sp = SPARK[24]
            paste(im, sp, (x - sp.width / 2, y - sp.height / 2))
        elif hl < 2.8:  # sparkle burst off the front hand
            q = (hl - 1.6) / 1.2; r2 = random.Random(8); x0, y0 = SK[F['front'] + 'tip']
            for j in range(10):
                ang = r2.uniform(0, 6.28); dist = 20 + 120 * ease(q) * r2.uniform(.5, 1); sp = SPARK[r2.choice([10, 16])]
                paste(im, sp, (x0 + dist * math.cos(ang) - sp.width / 2, y0 + dist * math.sin(ang) - sp.height / 2), 1 - q)
    if fx == 'wild':
        p = F['power'][n]; cx, cy = float(SK['sm'][0]), float(SK['sm'][1]) + 0.3 * Tpx
        # rising energy sparks while powering up (and gently during the hold)
        amt = max(p * (1 if hl < 0 else 0.0), 0.35 * clamp((hl + 0.5)) * clamp((27.5 - hl) / 0.5))
        if amt > 0.02:
            r2 = random.Random(21)
            for j in range(26):
                ph = (gt * r2.uniform(0.25, 0.45) + r2.random()) % 1
                x = cx + r2.uniform(-1.7, 1.7) * Tpx; y = 905 - ph * (2.6 * Tpx)
                sp = SPARK[r2.choice([6, 10, 10, 16])]
                paste(im, sp, (x - sp.width / 2, y - sp.height / 2), amt * math.sin(math.pi * ph))
        # hero flash + burst exactly when the warrior pose locks in
        if 0 <= hl < 1.2:
            q = hl / 1.2
            fl = Image.new('RGBA', im.size, tuple(int(255 * v) for v in CORE) + (int(90 * (1 - q) ** 2),)); im.alpha_composite(fl)
            r2 = random.Random(31)
            for j in range(22):
                ang = r2.uniform(0, 6.28); dist = 40 + 420 * ease(q) * r2.uniform(.4, 1); sp = SPARK[r2.choice([10, 16, 24])]
                paste(im, sp, (cx + dist * math.cos(ang) - sp.width / 2, cy - 0.4 * Tpx + dist * 0.7 * math.sin(ang) - sp.height / 2), 1 - q)
