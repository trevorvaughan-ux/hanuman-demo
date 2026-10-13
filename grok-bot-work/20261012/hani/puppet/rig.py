"""Cut-out Hani puppet built from the real Triangle v2 Hani frames (read-only source).
Parts are cut from tri/stand.png (front T-stand) and tri/pose.png (3/4 head), graded with the Triangle v2 grade,
then warped bone-to-bone onto a Hani-proportioned skeleton driven by MediaPipe keypoints."""
import math, os, sys
import numpy as np, cv2, cairo
sys.path.insert(0, '/workspace/hani/brand'); import palette as PAL
D = '/workspace/hani/puppet/'
SRC_T = 200.0                                       # Hani torso length in the source frame (px)

def smooth(e0, e1, x):
    t = min(1.0, max(0.0, (x - e0) / (e1 - e0))); return t * t * (3 - 2 * t)

class Part:
    def __init__(self, tex, a, b, hw=0, e0=0.0, e1=0.0, cap0=False, cap1=False, poly=None, pad=6):
        a = np.array(a, float); b = np.array(b, float); H, W = tex.shape[:2]
        if poly is not None:
            poly = np.array(poly, np.int32); x0, y0 = poly.min(0) - pad; x1, y1 = poly.max(0) + pad
        else:
            pts = np.array([a, b]); x0, y0 = (pts.min(0) - hw * 1.6 - pad).astype(int); x1, y1 = (pts.max(0) + hw * 1.6 + pad).astype(int)
        x0, y0 = max(0, int(x0)), max(0, int(y0)); x1, y1 = min(W, int(x1)), min(H, int(y1))
        crop = tex[y0:y1, x0:x1].astype(np.float32)
        m = np.zeros(crop.shape[:2], np.float32)
        if poly is not None:
            cv2.fillPoly(m, [poly - [x0, y0]], 1.0)
        else:
            yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
            L = np.linalg.norm(b - a); u = (b - a) / L
            px, py = xx - a[0], yy - a[1]
            t = px * u[0] + py * u[1]; dp = np.abs(px * u[1] - py * u[0])
            inside = (t >= -e0 * L) & (t <= (1 + e1) * L) & (dp <= hw)
            if cap0: inside |= (px ** 2 + py ** 2) <= hw * hw
            if cap1: inside |= ((xx - b[0]) ** 2 + (yy - b[1]) ** 2) <= hw * hw
            m = inside.astype(np.float32)
        m = cv2.GaussianBlur(m, (5, 5), 1.0)
        al = np.clip((crop[..., 3] / 255 * m - 0.3) / 0.7, 0, 1)
        al = cv2.GaussianBlur(al, (3, 3), 0.6)
        self.img = np.dstack([crop[..., :3] * al[..., None], al]).astype(np.float32)   # premultiplied
        self.a = a - [x0, y0]; self.b = b - [x0, y0]
    def mirrored(self):
        p = Part.__new__(Part); w = self.img.shape[1]
        p.img = self.img[:, ::-1].copy(); p.a = np.array([w - 1 - self.a[0], self.a[1]]); p.b = np.array([w - 1 - self.b[0], self.b[1]])
        return p

def put(canvas, part, A, B, sp, op=1.0, sa=None):
    """Warp part so its bone a->b lands on A->B. sa: along-bone scale (default |AB|/|ab|), sp: across-bone scale."""
    if op <= 0.01: return
    A = np.asarray(A, float); B = np.asarray(B, float)
    vs = part.b - part.a; ls = np.linalg.norm(vs); us = vs / ls
    vt = B - A; lt = np.linalg.norm(vt)
    ut = vt / lt if lt > 1e-6 else us
    if sa is None: sa = lt / ls
    Rs = np.array([[us[0], us[1]], [-us[1], us[0]]])          # source -> local (u, v)
    Rt = np.array([[ut[0], -ut[1]], [ut[1], ut[0]]])          # local -> target
    Mm = Rt @ np.diag([sa, sp]) @ Rs
    tvec = A - Mm @ part.a
    h, w = part.img.shape[:2]
    cr = np.array([[0, 0], [w, 0], [0, h], [w, h]], float) @ Mm.T + tvec
    H, W = canvas.shape[:2]
    bx0, by0 = np.floor(cr.min(0)).astype(int) - 1; bx1, by1 = np.ceil(cr.max(0)).astype(int) + 1
    bx0, by0 = max(0, bx0), max(0, by0); bx1, by1 = min(W, bx1), min(H, by1)
    if bx1 <= bx0 or by1 <= by0: return
    M2 = np.hstack([Mm, (tvec - [bx0, by0])[:, None]])
    wimg = cv2.warpAffine(part.img, M2, (bx1 - bx0, by1 - by0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    al = wimg[..., 3:4] * op
    reg = canvas[by0:by1, bx0:bx1]
    reg *= (1 - al); reg += wimg[..., :3] * op

def ik(S, Wt, l1, l2, E_hint):
    """2-bone IK: shoulder S, wrist target Wt; elbow on the same side as E_hint."""
    S = np.asarray(S, float); Wt = np.asarray(Wt, float); d = Wt - S; L = np.linalg.norm(d)
    L = min(max(L, abs(l1 - l2) + 1e-3), l1 + l2 - 1e-3)
    u = d / (np.linalg.norm(d) + 1e-9); Wt = S + u * L
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L); hgt = math.sqrt(max(0.0, l1 * l1 - a * a))
    n = np.array([-u[1], u[0]])
    if np.dot(np.asarray(E_hint) - S, n) < 0: n = -n
    return S + u * a + n * hgt, Wt

class Puppet:
    def __init__(self):
        tf = cv2.cvtColor(cv2.imread(D + 'tex_full.png', -1), cv2.COLOR_BGRA2RGBA)
        tp = cv2.cvtColor(cv2.imread(D + 'tex_pose.png', -1), cv2.COLOR_BGRA2RGBA)
        P = {}
        P['head'] = Part(tf, (987, 432), (991, 304), poly=[(950, 432), (1022, 432), (1050, 410), (1062, 385), (1062, 360), (1048, 330), (1010, 300), (972, 300), (940, 330), (924, 360), (924, 388), (938, 412)])
        h34 = Part(tp, (1128, 573), (1232, 548), poly=[(1124, 540), (1150, 505), (1200, 498), (1248, 520), (1254, 575), (1228, 625), (1200, 634), (1168, 626), (1136, 606), (1124, 585)])
        P['head34L'] = h34; P['head34R'] = h34.mirrored()
        P['torso'] = Part(tf, (986, 440), (970, 640), poly=[(950, 425), (1022, 425), (1036, 436), (1044, 452), (1040, 480), (1037, 600), (1037, 640), (1002, 664), (940, 664), (910, 640), (923, 600), (930, 480), (927, 452), (934, 436)])
        J = {'Rsh': (936, 437), 'Rel': (831, 422), 'Rwr': (743, 406), 'Rtip': (686, 399),
             'Lsh': (1039, 444), 'Lel': (1139, 422), 'Lwr': (1231, 392), 'Ltip': (1292, 385),
             'Rhip': (936, 633), 'Rkn': (857, 746), 'Ran': (775, 864), 'Rtoe': (756, 918),
             'Lhip': (1010, 641), 'Lkn': (1086, 756), 'Lan': (1172, 864), 'Ltoe': (1230, 898)}
        for s in 'LR':
            P[s + 'ua'] = Part(tf, J[s + 'sh'], J[s + 'el'], 19, -0.10, 0.06)
            dv = np.subtract(J[s + 'el'], J[s + 'sh']); c0 = np.add(J[s + 'sh'], dv * 0.30)
            P[s + 'delt'] = Part(tf, c0, c0 + dv * 0.02, 20, 0.6, 0.6, cap0=True, cap1=True)
            P[s + 'fa'] = Part(tf, J[s + 'el'], J[s + 'wr'], 18, 0.0, 0.04, cap0=True)
            P[s + 'hand'] = Part(tf, J[s + 'wr'], J[s + 'tip'], 25, 0.0, 0.15, cap0=True)
            P[s + 'th'] = Part(tf, J[s + 'hip'], J[s + 'kn'], 33, 0.0, 0.10, cap0=True)
            P[s + 'sh'] = Part(tf, J[s + 'kn'], J[s + 'an'], 27, 0.0, 0.06, cap0=True)
            P[s + 'ft'] = Part(tf, J[s + 'an'], J[s + 'toe'], 27, 0.0, 0.15, cap0=True)
        self.P = P; self.SJ = {k: np.array(v, float) for k, v in J.items()}
        self.len = {'ua': 103.0, 'fa': 94.0}

    # ---------------- skeleton from tracking ----------------
    def skeleton(self, J, Tpx, st, cal):
        """J: Julie joints in screen px. cal: dict(dy, kua, kfa, sw0, seat_y, chair) computed once per video."""
        g = Tpx / SRC_T; q = lambda k: np.array(J[k], float)
        hm = (q('Lhip') + q('Rhip')) / 2 + [0, cal['dy']]
        sm = (q('Lsh') + q('Rsh')) / 2 + [0, cal['dy']]
        hm = np.array([cal['hx'], hm[1]])                    # pelvis stays seated on the chair
        sm = sm + [cal['hx'] - ((q('Lhip')[0] + q('Rhip')[0]) / 2), 0]
        ax = sm - hm; Lt = np.linalg.norm(ax); ax_u = ax / Lt
        sm = hm + ax_u * min(Lt, 1.08 * Tpx) * (1 + 0.012 * st.get('breath', 0))
        perp = np.array([-ax_u[1], ax_u[0]])
        if perp[0] < 0: perp = -perp                          # points to image-right
        sw = np.linalg.norm(q('Lsh') - q('Rsh')); r = sw / cal['sw0']
        wmul = float(np.clip(0.35 + 0.65 * r, 0.62, 1.0))
        S = {}
        S['hm'], S['sm'], S['wmul'], S['g'], S['perp'], S['ax'] = hm, sm, wmul, g, perp, ax_u
        S['Lsh'] = sm + perp * 51 * g * wmul + ax_u * -4 * g; S['Rsh'] = sm - perp * 51 * g * wmul + ax_u * -4 * g
        S['Lhip'] = hm + perp * 37 * g; S['Rhip'] = hm - perp * 37 * g
        # seated legs (fixed, natural): short foreshortened thighs over the seat, knees at the front edge, feet flat
        for s, sg in (('L', 1), ('R', -1)):
            kn = np.array([S[s + 'hip'][0] + sg * 0.22 * Tpx, cal['seat_y'] + 0.04 * Tpx])
            an = np.array([kn[0] + sg * 0.05 * Tpx, cal['ankle_y']])
            S[s + 'kn'], S[s + 'an'] = kn, an
        # arms: Julie's limb directions, Hani's limb lengths, hands snapped to knees / chair back
        lua, lfa = self.len['ua'] * g, self.len['fa'] * g
        for s, sg in (('L', 1), ('R', -1)):
            sh = S[s + 'sh']
            el = sh + (q(s + 'el') - q(s + 'sh')) * cal['kua']
            wr = el + (q(s + 'wr') - q(s + 'el')) * cal['kfa']
            def segd(p, a_, b_):
                v = b_ - a_; t = np.clip(np.dot(p - a_, v) / (np.dot(v, v) + 1e-9), 0, 1); return np.linalg.norm(p - (a_ + v * t))
            dk = [segd(q(s + 'wr'), q('Lhip'), q('Lkn')), segd(q(s + 'wr'), q('Rhip'), q('Rkn'))]
            ki = int(np.argmin(dk)); wk = smooth(0.42 * Tpx, 0.2 * Tpx, dk[ki])
            kn_t = S['Lkn' if ki == 0 else 'Rkn'] + [0, -0.07 * Tpx]
            wr = wr * (1 - wk) + kn_t * wk
            vis = st.get('vis_' + s, 1.0); wh = smooth(0.62, 0.38, vis) * st.get('hide_ok', 1.0)
            ch = cal['chair']
            back_t = np.array([sm[0] + sg * 0.62 * Tpx, ch['back_top'] + 0.07 * Tpx])
            wr = wr * (1 - wh) + back_t * wh
            el, wr = ik(sh, wr, lua, lfa, el + (sh - hm) * 0.0 + perp * sg * 0.3 * Tpx * wh)
            tipdir = (wr - el) / (np.linalg.norm(wr - el) + 1e-9)
            if wk > 0: tipdir = tipdir * (1 - wk) + np.array([sg * -0.25, 1.0]) * wk; tipdir /= np.linalg.norm(tipdir)
            S[s + 'el'], S[s + 'wr'], S[s + 'tip'], S[s + 'hid'] = el, wr, wr + tipdir * 58 * g, wh; S[s + 'wk'] = wk
        # head
        neck = sm + ax_u * 6 * g
        em = q('ear') + [cal['hx'] - ((q('Lhip')[0] + q('Rhip')[0]) / 2), cal['dy']]
        hv = em - (q('Lsh') + q('Rsh')) / 2 - [0, 0]
        ang_t = math.atan2(ax_u[0], -ax_u[1]); ang_h = math.atan2(hv[0], -hv[1])
        rel = (ang_h - ang_t + math.pi) % (2 * math.pi) - math.pi
        rel = float(np.clip(rel * 0.6, -0.32, 0.32)) + st.get('head_tilt', 0)
        ha = ang_t + rel
        S['neck'] = neck; S['crown'] = neck + np.array([math.sin(ha), -math.cos(ha)]) * 128 * g
        ew = abs(q('lear')[0] - q('rear')[0]) / Tpx
        yaw = float(np.clip((0.27 - ew) / 0.19, 0, 1))
        noff = q('nose')[0] - (q('lear')[0] + q('rear')[0]) / 2
        S['yaw'] = yaw; S['yaw_sign'] = 1 if noff > 0 else -1
        return S

    # ---------------- drawing ----------------
    def draw(self, canvas, S, Tpx, st):
        P, g = self.P, S['g']
        sp = g
        def limb(s, seg, a, b, w=1.0, op=1.0, sa=None): put(canvas, P[s + seg], S[a], S[b], sp * w, op, sa)
        hidden = [s for s in 'LR' if S[s + 'hid'] > 0.5]
        for s in hidden:
            limb(s, 'ua', s + 'sh', s + 'el'); limb(s, 'fa', s + 'el', s + 'wr'); limb(s, 'hand', s + 'wr', s + 'tip')
        # torso (narrows with shoulder width), with a gentle breath
        put(canvas, P['torso'], S['sm'] + S['ax'] * -2 * g, S['hm'], sp * S['wmul'] * (1 + 0.01 * st.get('breath', 0)))
        for s in 'LR':
            if s not in hidden:
                u = (S[s + 'el'] - S[s + 'sh']); u = u / (np.linalg.norm(u) + 1e-9)
                put(canvas, P[s + 'delt'], S[s + 'sh'] + u * 2 * g, S[s + 'sh'] + u * 4 * g, sp, sa=g)
                limb(s, 'ua', s + 'sh', s + 'el')
        # head: front <-> 3/4 crossfade by yaw (mirrored for the other direction)
        y = S['yaw']; w34 = smooth(0.47, 0.53, y)
        hp = P['head34R'] if S['yaw_sign'] > 0 else P['head34L']
        front = lambda op: put(canvas, P['head'], S['neck'], S['crown'], sp * (1 - 0.18 * y), op, sa=g)
        side = lambda op: put(canvas, hp, S['neck'] + (S['crown'] - S['neck']) * -0.02, S['crown'], sp * (0.9 + 0.1 * y), op, sa=g * 0.97)
        # dominant view fully opaque (never see-through), the other blended on top only inside the short switch window
        if w34 < 0.5:
            front(1.0); side(w34)
        else:
            side(1.0); front(1 - w34)
        # seated legs
        for s in 'LR':
            put(canvas, P[s + 'th'], S[s + 'hip'] + [0, -0.10 * Tpx], S[s + 'kn'] + [0, 0.02 * Tpx], sp * 1.25)
        for s in 'LR':
            limb(s, 'sh', s + 'kn', s + 'an')
            ft_dir = self.SJ[s + 'toe'] - self.SJ[s + 'an']
            put(canvas, P[s + 'ft'], S[s + 'an'], S[s + 'an'] + ft_dir * g, sp)
        for s in 'LR':
            if s not in hidden:
                limb(s, 'fa', s + 'el', s + 'wr'); limb(s, 'hand', s + 'wr', s + 'tip')

# ---------------- chair, tail, shadows (cairo, drawn behind Hani) ----------------
def _c(c, h, a=1.0): r, g, b = PAL.rgbf(h); c.set_source_rgba(r, g, b, a)
def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2); c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()
def wood_grad(x0, y0, x1, y1, light=PAL.WOOD_LIGHT, mid=PAL.WOOD, dark=PAL.WOOD_DARK):
    gr = cairo.LinearGradient(x0, y0, x1, y1)
    for o, h in ((0, light), (0.55, mid), (1, dark)): gr.add_color_stop_rgb(o, *PAL.rgbf(h))
    return gr
def floor_shadow(c, cx, y, rx, ry, a=0.28):
    c.save(); c.translate(cx, y); c.scale(rx, ry)
    gr = cairo.RadialGradient(0, 0, 0, 0, 0, 1); gr.add_color_stop_rgba(0, 0.32, 0.18, 0.08, a); gr.add_color_stop_rgba(1, 0.32, 0.18, 0.08, 0)
    c.set_source(gr); c.arc(0, 0, 1, 0, 2 * math.pi); c.fill(); c.restore()

def draw_chair(c, ch, T):
    x, fl, sy, bt = ch['x'], ch['floor'], ch['seat_y'], ch['back_top']
    hw = 0.74 * T; dep = 0.20 * T; th = 0.11 * T; lw = 0.075 * T
    floor_shadow(c, x, fl - 2, hw * 1.35, 0.11 * T, 0.30)
    # back legs (further away: shorter, inset) + back posts
    for sg in (-1, 1):
        bx = x + sg * (hw - 0.09 * T)
        c.set_source(wood_grad(bx - lw / 2, 0, bx + lw / 2, 0, PAL.WOOD, PAL.WOOD, PAL.WOOD_DARK))
        rrect(c, bx - lw / 2 * 0.9, bt, lw * 0.9, fl - 0.05 * T - bt, lw * 0.3); c.fill()
    # back rest panel
    bh = 0.36 * T
    c.set_source(wood_grad(0, bt, 0, bt + bh)); rrect(c, x - hw + 0.03 * T, bt, 2 * hw - 0.06 * T, bh, 0.07 * T); c.fill()
    _c(c, PAL.WOOD_DARK, 0.55); c.set_line_width(2.5); rrect(c, x - hw + 0.03 * T, bt, 2 * hw - 0.06 * T, bh, 0.07 * T); c.stroke()
    _c(c, PAL.WOOD_LIGHT, 0.7); c.set_line_width(3); c.move_to(x - hw + 0.1 * T, bt + 0.05 * T); c.line_to(x + hw - 0.1 * T, bt + 0.05 * T); c.stroke()
    # little heart cut-out on the backrest (brand touch)
    c.save(); c.translate(x, bt + bh * 0.55); s = 0.05 * T
    c.move_to(0, s * 0.9); c.curve_to(-s * 2.2, -s * 0.4, -s * 0.9, -s * 1.9, 0, -s * 0.7); c.curve_to(s * 0.9, -s * 1.9, s * 2.2, -s * 0.4, 0, s * 0.9)
    _c(c, PAL.WOOD_DARK, 0.6); c.fill(); c.restore()
    # seat top (perspective trapezoid)
    c.move_to(x - hw + 0.08 * T, sy - dep); c.line_to(x + hw - 0.08 * T, sy - dep); c.line_to(x + hw, sy); c.line_to(x - hw, sy); c.close_path()
    c.set_source(wood_grad(0, sy - dep, 0, sy, PAL.WOOD_LIGHT, PAL.WOOD_LIGHT, PAL.WOOD)); c.fill()
    # front legs
    for sg in (-1, 1):
        fx = x + sg * (hw - 0.07 * T)
        c.set_source(wood_grad(fx - lw / 2, 0, fx + lw / 2, 0)); rrect(c, fx - lw / 2, sy, lw, fl - sy, lw * 0.3); c.fill()
        _c(c, PAL.WOOD_DARK, 0.35); c.rectangle(fx - lw / 2, fl - 6, lw, 6); c.fill()
    # front apron / seat edge
    c.set_source(wood_grad(0, sy, 0, sy + th, PAL.WOOD, PAL.WOOD, PAL.WOOD_DARK)); rrect(c, x - hw - 4, sy - 3, 2 * hw + 8, th, 0.04 * T); c.fill()
    _c(c, PAL.WOOD_LIGHT, 0.8); c.set_line_width(3); c.move_to(x - hw + 6, sy); c.line_to(x + hw - 6, sy); c.stroke()

def draw_tail(c, hm, T, sy, t, side=1):
    """Fur tail peeking out beside the chair and curling up, swaying gently."""
    sw = 0.06 * math.sin(t * 1.3) + 0.03 * math.sin(t * 2.1 + 1)
    p0 = (hm[0] + side * 0.30 * T, sy - 0.08 * T)
    p1 = (hm[0] + side * 0.95 * T, sy - 0.02 * T)
    p2 = (hm[0] + side * (1.05 + sw) * T, sy + 0.55 * T)
    p3 = (hm[0] + side * (0.88 + sw * 1.4) * T, sy + 0.38 * T)
    pts = []
    for i in range(41):
        u = i / 40; a = (1 - u) ** 3; b = 3 * (1 - u) ** 2 * u; cc = 3 * (1 - u) * u * u; d = u ** 3
        pts.append((a * p0[0] + b * p1[0] + cc * p2[0] + d * p3[0], a * p0[1] + b * p1[1] + cc * p2[1] + d * p3[1]))
    # curl at the tip
    ex, ey = pts[-1]; px, py = pts[-2]; ang = math.atan2(ey - py, ex - px); r = 0.07 * T
    for i in range(1, 16):
        a2 = ang + side * i * 0.28; r2 = r * (1 - i / 22)
        ex, ey = ex + math.cos(a2) * r2 * 0.45, ey + math.sin(a2) * r2 * 0.45; pts.append((ex, ey))
    n = len(pts); fur = (152 / 255, 70 / 255, 40 / 255)
    def stroke(width_fn, col, off=(0, 0)):
        c.set_line_cap(cairo.LINE_CAP_ROUND)
        for i in range(n - 1):
            c.set_source_rgba(*col); c.set_line_width(width_fn(i / (n - 1)))
            c.move_to(pts[i][0] + off[0], pts[i][1] + off[1]); c.line_to(pts[i + 1][0] + off[0], pts[i + 1][1] + off[1]); c.stroke()
    w0 = 0.085 * T
    stroke(lambda u: w0 * (1 - 0.55 * u) + 3, (0.42, 0.18, 0.09, 1))
    stroke(lambda u: w0 * (1 - 0.55 * u), fur + (1,))
    stroke(lambda u: w0 * 0.28 * (1 - 0.6 * u), (0.80, 0.45, 0.30, 0.55), (-side * 0.012 * T, -0.012 * T))
