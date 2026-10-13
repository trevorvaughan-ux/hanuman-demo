"""Opt-in confetti celebration (config field "celebrate"; nothing here runs unless a config asks for it).
blast(im, bt)       big confetti blast over the live scene, bt = seconds since the trigger caption appeared:
                    3 cannons from the top edge + 2 volleys from each side cannon + a steady rain from above.
card_back(lt)       dense full-card confetti rain + corner cannons for the end card (drawn BEHIND the text).
card_front(lt)      a lighter foreground layer (caller masks it off the text block).
Colours: brand/palette.py CONFETTI only. Drawn with cairo (antialiased), composited with numpy."""
import math, random, sys
import numpy as np, cairo
sys.path.insert(0, '/workspace/hani/brand'); import palette as P
W, H = 1920, 1080
COLS = [P.rgbf(h) for h in P.CONFETTI]

def _piece(rng, kind_w=(0.80, 0.06, 0.14), size=(14, 28)):
    k = rng.random(); kind = 'rect' if k < kind_w[0] else ('ribbon' if k < kind_w[0] + kind_w[1] else 'dot')
    return dict(kind=kind, col=rng.choice(COLS), sz=rng.uniform(*size), rot=rng.uniform(0, 6.28), rs=rng.uniform(-8, 8),
                flip=rng.uniform(2.0, 5.0), fph=rng.uniform(0, 6.28), sway=rng.uniform(15, 55), sw=rng.uniform(1.2, 2.6),
                sph=rng.uniform(0, 6.28), vfall=rng.uniform(170, 320))

def _make(seed, dense=1.0, size=(14, 28)):
    rng = random.Random(seed); ps = []
    # top cannons: spray downward/outward from the top edge
    for cx in (0.18 * W, 0.5 * W, 0.82 * W):
        for _ in range(int(110 * dense)):
            p = _piece(rng, size=size); ang = math.radians(rng.uniform(15, 165)); sp = rng.uniform(500, 1500)
            p.update(x0=cx + rng.uniform(-40, 40), y0=-30, vx=sp * math.cos(ang), vy=sp * math.sin(ang) * 0.8 + 150,
                     drag=rng.uniform(1.6, 2.4), t0=rng.uniform(0, 0.18)); ps.append(p)
    # side cannons (two volleys each side): up and inward, then flutter down over the frame
    for side in (0, 1):
        for vol in (0.0, 0.45):
            for _ in range(int(130 * dense)):
                p = _piece(rng, size=size); ang = math.radians(rng.uniform(20, 72)); sp = rng.uniform(1300, 2700)
                p.update(x0=(-20 if side == 0 else W + 20), y0=rng.uniform(560, 860),
                         vx=sp * math.cos(ang) * (1 if side == 0 else -1), vy=-sp * math.sin(ang),
                         drag=rng.uniform(1.4, 2.0), t0=vol + rng.uniform(0, 0.2)); ps.append(p)
    # steady rain from above (staggered so the frame stays full for several seconds)
    for _ in range(int(380 * dense)):
        p = _piece(rng, size=size)
        p.update(x0=rng.uniform(-60, W + 60), y0=-40, vx=rng.uniform(-60, 60), vy=rng.uniform(0, 200),
                 drag=1.5, t0=rng.uniform(0.15, 5.0)); ps.append(p)
    return ps

def _draw(ps, t, ctx, alpha=1.0):
    for p in ps:
        tt = t - p['t0']
        if tt <= 0: continue
        e = 1 - math.exp(-p['drag'] * tt)
        x = p['x0'] + p['vx'] * e / p['drag'] + p['sway'] * math.sin(p['sw'] * tt + p['sph']) * e
        y = p['y0'] + p['vfall'] * tt + (p['vy'] - p['vfall']) * e / p['drag']
        if y > H + 50 or y < -400 or x < -80 or x > W + 80: continue
        s = p['sz']; fl = math.cos(p['flip'] * tt + p['fph']); ang = p['rot'] + p['rs'] * tt
        r, g, b = p['col']; shade = 0.72 + 0.28 * abs(fl)          # darker when seen edge-on / back side
        if fl < 0: shade *= 0.88
        ctx.save(); ctx.translate(x, y); ctx.rotate(ang)
        ctx.set_source_rgba(r * shade, g * shade, b * shade, alpha)
        if p['kind'] == 'rect':
            w2 = s * 0.55 * max(0.12, abs(fl)); h2 = s * 0.32
            ctx.rectangle(-w2, -h2, 2 * w2, 2 * h2); ctx.fill()
        elif p['kind'] == 'dot':
            ctx.scale(1, max(0.2, abs(fl))); ctx.arc(0, 0, s * 0.38, 0, 2 * math.pi); ctx.fill()
        else:   # curly ribbon streamer
            L = s * 1.9; ctx.set_line_width(max(3.0, s * 0.26)); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
            ph = p['flip'] * tt
            for i in range(9):
                u = i / 8; px = -L / 2 + L * u; py = s * 0.35 * math.sin(u * 2 * math.pi + ph)
                (ctx.move_to if i == 0 else ctx.line_to)(px, py)
            ctx.stroke()
        ctx.restore()

def _layer(ps, t, alpha=1.0):
    S = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(S); c.set_antialias(cairo.ANTIALIAS_GOOD)
    _draw(ps, t, c, alpha); S.flush()
    a = np.frombuffer(S.get_data(), np.uint8).reshape(H, W, 4)
    return a   # BGRA premultiplied

def comp(im, a):
    """alpha-composite a premultiplied BGRA layer onto PIL RGBA image im (in place)."""
    from PIL import Image
    base = np.asarray(im.convert('RGBA')).astype(np.float32)
    al = a[..., 3:4].astype(np.float32) / 255
    base[..., :3] = a[..., [2, 1, 0]].astype(np.float32) + base[..., :3] * (1 - al)
    base[..., 3:4] = np.maximum(base[..., 3:4], a[..., 3:4])
    im.paste(Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGBA'))

# density tuned for the 7.5 MB cap (~415 kbps): fewer, bigger pieces compress far better than a dense fine sprinkle
# (a 1,230-piece version took ~1.5 Mbps in the blast and starved the rest of the video by 11 %; render with --max_mb 7.75)
BLAST = _make(77, 0.38, (24, 42))
def blast(im, bt):
    if bt < 0: return
    comp(im, _layer(BLAST, bt))

CARD = _make(91, 0.5, (20, 34))
CARD_PRE = 1.6   # card rain already in flight when the card fades in (continues the scene blast)
def card_back(lt): return _layer(CARD, lt + CARD_PRE)
CARD_F = _make(93, 0.2, (22, 36))
def card_front(lt): return _layer(CARD_F, lt + 0.4)
