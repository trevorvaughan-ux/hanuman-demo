"""2D Hani puppet + classroom + chair, drawn with cairo (anti-aliased)."""
import math, random, cairo, numpy as np

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
BODY = hexc('1f8a8a'); BODY_FAR = hexc('197676'); DARK = hexc('136b6b'); CREAM = hexc('FDF8F0')
GOLD = hexc('D99A4E'); IRIS = hexc('3fa34d'); CHARC = hexc('3A3A3A'); WHITE = (1, 1, 1, 1)
W, H = 1920, 1080

def rgba(ctx, c): ctx.set_source_rgba(*c)

# ---------------------------------------------------------------- background
def classroom(path, floor_y=900, seed=3):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(s)
    g = cairo.LinearGradient(0, 0, 0, floor_y); g.add_color_stop_rgb(0, 0.99, 0.95, 0.88); g.add_color_stop_rgb(1, 0.97, 0.89, 0.78)
    c.set_source(g); c.rectangle(0, 0, W, floor_y); c.fill()
    # subtle wallpaper dots
    r = random.Random(seed)
    for i in range(140):
        x, y = r.uniform(0, W), r.uniform(0, floor_y - 60)
        c.set_source_rgba(0.85, 0.6, 0.3, 0.06); c.arc(x, y, r.uniform(3, 7), 0, 6.3); c.fill()
    # window (left)
    wx, wy, ww, wh = 90, 140, 420, 470
    c.set_source_rgba(1, 1, 1, 1); rr(c, wx - 14, wy - 14, ww + 28, wh + 28, 18); c.fill()
    sky = cairo.LinearGradient(0, wy, 0, wy + wh); sky.add_color_stop_rgb(0, 0.62, 0.84, 0.95); sky.add_color_stop_rgb(1, 0.86, 0.94, 0.97)
    c.set_source(sky); rr(c, wx, wy, ww, wh, 10); c.fill()
    c.set_source_rgba(1, 0.86, 0.45, 1); c.arc(wx + 300, wy + 110, 46, 0, 6.3); c.fill()
    for cx, cy, k in ((wx + 110, wy + 150, 1), (wx + 250, wy + 260, 0.8)):
        c.set_source_rgba(1, 1, 1, 0.95)
        for dx, dy, rad in ((0, 0, 34), (34, -12, 40), (72, 0, 32), (36, 12, 34)):
            c.arc(cx + dx * k, cy + dy * k, rad * k, 0, 6.3); c.fill()
    c.set_source_rgba(0.55, 0.78, 0.45, 1); c.move_to(wx, wy + wh); c.curve_to(wx + 120, wy + 330, wx + 260, wy + 380, wx + ww, wy + 320)
    c.line_to(wx + ww, wy + wh); c.close_path(); c.fill()
    c.set_source_rgba(1, 1, 1, 1); c.set_line_width(14); c.move_to(wx + ww / 2, wy); c.line_to(wx + ww / 2, wy + wh)
    c.move_to(wx, wy + wh / 2); c.line_to(wx + ww, wy + wh / 2); c.stroke()
    # light beams
    for i, (x0, w0) in enumerate(((wx + 40, 120), (wx + 230, 140))):
        c.move_to(x0, wy + 10); c.line_to(x0 + w0, wy + 10); c.line_to(x0 + w0 + 520, floor_y + 160); c.line_to(x0 + 380, floor_y + 160); c.close_path()
        c.set_source_rgba(1, 0.97, 0.82, 0.16); c.fill()
    # whiteboard
    bx, by, bw, bh = 640, 120, 700, 330
    c.set_source_rgba(0.55, 0.58, 0.6, 1); rr(c, bx - 14, by - 14, bw + 28, bh + 28, 14); c.fill()
    c.set_source_rgba(0.99, 0.99, 0.98, 1); rr(c, bx, by, bw, bh, 8); c.fill()
    c.set_source_rgba(0.55, 0.58, 0.6, 1); c.rectangle(bx + 40, by + bh + 14, bw - 80, 12); c.fill()
    for i, col in enumerate((DARK, GOLD, (0.9, 0.4, 0.35, 1))):
        rgba(c, col); rr(c, bx + 80 + i * 60, by + bh + 2, 44, 12, 5); c.fill()
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    rgba(c, hexc('2F6B6E', 0.85)); c.set_line_width(6)
    # doodles: sun, triangle, heart, waves
    c.arc(bx + 110, by + 100, 38, 0, 6.3); c.stroke()
    for k in range(8):
        a = k * math.pi / 4; c.move_to(bx + 110 + 52 * math.cos(a), by + 100 + 52 * math.sin(a)); c.line_to(bx + 110 + 68 * math.cos(a), by + 100 + 68 * math.sin(a))
    c.stroke()
    rgba(c, hexc('D99A4E', 0.95)); c.move_to(bx + 560, by + 70); c.line_to(bx + 630, by + 190); c.line_to(bx + 490, by + 190); c.close_path(); c.stroke()
    c.set_source_rgba(0.9, 0.42, 0.38, 0.9); heart(c, bx + 580, by + 260, 26); c.fill()
    rgba(c, hexc('2F6B6E', 0.8)); c.set_line_width(5)
    for k in range(2):
        y = by + 240 + k * 34; c.move_to(bx + 60, y)
        for j in range(6): c.rel_curve_to(15, -16, 30, -16, 45, 0) if j % 2 == 0 else c.rel_curve_to(15, 16, 30, 16, 45, 0)
        c.stroke()
    c.select_font_face('DejaVu Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); c.set_font_size(54)
    rgba(c, hexc('136b6b', 0.9)); c.move_to(bx + 220, by + 125); c.show_text('Hani Yoga')
    # bunting
    for i in range(12):
        x = 560 + i * 72; y = 40 + 18 * math.sin(i / 11 * math.pi)
        col = [GOLD, BODY, (0.92, 0.5, 0.42, 1), (0.98, 0.82, 0.45, 1)][i % 4]
        rgba(c, col); c.move_to(x, y); c.line_to(x + 60, y + 4); c.line_to(x + 30, y + 52); c.close_path(); c.fill()
    c.set_source_rgba(0.6, 0.5, 0.4, 0.8); c.set_line_width(3); c.move_to(540, 36); c.curve_to(900, 70, 1100, 70, 1440, 36); c.stroke()
    # bookshelf right
    sx, sy = 1560, 470
    c.set_source_rgba(0.72, 0.5, 0.32, 1); rr(c, sx, sy, 300, floor_y - sy, 10); c.fill()
    c.set_source_rgba(0.62, 0.42, 0.26, 1)
    for k in range(3): c.rectangle(sx + 12, sy + 20 + k * 140, 276, 112); c.fill()
    for k in range(3):
        x = sx + 20
        while x < sx + 270:
            bw2 = r.uniform(18, 34); bh2 = r.uniform(70, 104)
            col = r.choice([GOLD, BODY, DARK, (0.92, 0.5, 0.42, 1), (0.98, 0.82, 0.45, 1), (0.55, 0.7, 0.85, 1)])
            rgba(c, col); rr(c, x, sy + 20 + k * 140 + 112 - bh2, bw2, bh2, 4); c.fill(); x += bw2 + 4
    # floor
    fg = cairo.LinearGradient(0, floor_y, 0, H); fg.add_color_stop_rgb(0, 0.88, 0.69, 0.47); fg.add_color_stop_rgb(1, 0.8, 0.58, 0.37)
    c.set_source(fg); c.rectangle(0, floor_y - 120, W, H); c.fill()
    c.set_source_rgba(1, 1, 1, 0.9); c.rectangle(0, floor_y - 132, W, 14); c.fill()
    c.set_source_rgba(0.6, 0.4, 0.22, 0.25); c.set_line_width(2)
    for k in range(7):
        y = floor_y - 110 + k * (k + 6) * 5; c.move_to(0, y); c.line_to(W, y); c.stroke()
    # rug
    c.save(); c.translate(W / 2, floor_y + 20); c.scale(1, 0.16)
    c.set_source_rgba(0.85, 0.45, 0.35, 0.30); c.arc(0, 0, 640, 0, 6.3); c.fill()
    c.set_source_rgba(0.99, 0.9, 0.7, 0.45); c.arc(0, 0, 560, 0, 6.3); c.fill(); c.restore()
    # plants
    plant(c, 70, floor_y - 120, 1.15); plant(c, 1490, floor_y - 120, 0.9)
    s.write_to_png(path)
    return path

def rr(c, x, y, w, h, r):
    c.new_sub_path(); c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); c.close_path()

def heart(c, x, y, s):
    c.move_to(x, y + s); c.curve_to(x - 2 * s, y - 0.2 * s, x - 0.8 * s, y - 1.6 * s, x, y - 0.5 * s)
    c.curve_to(x + 0.8 * s, y - 1.6 * s, x + 2 * s, y - 0.2 * s, x, y + s)

def plant(c, x, y, k):
    c.set_source_rgba(0.85, 0.55, 0.35, 1); c.move_to(x, y); c.line_to(x + 120 * k, y); c.line_to(x + 105 * k, y + 110 * k); c.line_to(x + 15 * k, y + 110 * k); c.close_path(); c.fill()
    for a, l in ((-1.2, 200), (-0.7, 230), (-0.2, 250), (0.3, 220), (0.8, 190), (-1.6, 150), (1.2, 160)):
        cx, cy = x + 60 * k, y
        ex, ey = cx + math.sin(a) * l * k, cy - math.cos(a) * l * k
        c.set_source_rgba(0.3 + 0.1 * math.sin(a * 3), 0.62, 0.38, 1)
        nx, ny = -(ey - cy) * 0.25, (ex - cx) * 0.25
        c.move_to(cx, cy); c.curve_to(cx + nx, cy + ny, ex + nx * 0.5, ey + ny * 0.5, ex, ey)
        c.curve_to(ex - nx * 0.5, ey - ny * 0.5, cx - nx, cy - ny, cx, cy); c.fill()

# ---------------------------------------------------------------- chair
def draw_chair(c, ch, part='all'):
    """ch: dict(view='side'|'front', x=backrest x (side) / centre x (front), floor, seat_y, back_top, dir (+1 seat extends right))"""
    leg = hexc('4a4f55'); seat = hexc('E39A4A'); seat_dk = hexc('C77F35')
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    if ch['view'] == 'side':
        x, fl, sy, bt, d = ch['x'], ch['floor'], ch['seat_y'], ch['back_top'], ch['dir']
        depth = (fl - bt) * 0.5
        rgba(c, leg); c.set_line_width(13)
        c.move_to(x, fl); c.line_to(x, bt + 20); c.stroke()                     # back leg+post
        c.move_to(x + d * depth, fl); c.line_to(x + d * depth, sy); c.stroke()  # front leg
        c.set_line_width(9); c.move_to(x, fl - 70); c.line_to(x + d * depth, fl - 70); c.stroke()
        rgba(c, seat_dk); rr(c, min(x, x + d * depth) - 14, sy - 8, depth + 28, 30, 13); c.fill()
        rgba(c, seat); rr(c, min(x, x + d * depth) - 14, sy - 14, depth + 28, 26, 13); c.fill()
        bh = (sy - bt) * 0.42
        rgba(c, seat_dk); rr(c, x - 16 + (6 if d > 0 else -6), bt - 2, 32, bh + 6, 14); c.fill()
        rgba(c, seat); rr(c, x - 16, bt - 6, 32, bh, 14); c.fill()
    else:
        x, fl, sy, bt, wdt = ch['x'], ch['floor'], ch['seat_y'], ch['back_top'], ch['width']
        if part in ('all', 'back'):
            rgba(c, leg); c.set_line_width(12)
            for dx in (-wdt * 0.42, wdt * 0.42): c.move_to(x + dx, sy); c.line_to(x + dx, bt + 20); c.stroke()
            rgba(c, seat_dk); rr(c, x - wdt * 0.5, bt, wdt, (sy - bt) * 0.42, 18); c.fill()
            rgba(c, seat); rr(c, x - wdt * 0.5, bt - 6, wdt, (sy - bt) * 0.40, 18); c.fill()
        if part in ('all', 'seat'):
            rgba(c, leg); c.set_line_width(12)
            for dx in (-wdt * 0.45, wdt * 0.45, -wdt * 0.32, wdt * 0.32):
                c.move_to(x + dx, sy); c.line_to(x + dx * 1.04, fl - (10 if abs(dx) < wdt * 0.4 else 0)); c.stroke()
            rgba(c, seat_dk); rr(c, x - wdt * 0.55, sy - 2, wdt * 1.1, 34, 14); c.fill()
            rgba(c, seat); rr(c, x - wdt * 0.55, sy - 12, wdt * 1.1, 28, 14); c.fill()

# ---------------------------------------------------------------- Hani
def capsule(c, pts, w, col, outline=DARK, ow=3.0):
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    def path():
        c.move_to(*pts[0])
        if len(pts) == 3:
            # smooth through the joint with a quadratic-ish curve
            (x0, y0), (x1, y1), (x2, y2) = pts
            c.line_to(x1, y1); c.line_to(x2, y2)
        else:
            for p in pts[1:]: c.line_to(*p)
    if outline:
        path(); rgba(c, outline); c.set_line_width(w + 2 * ow); c.stroke()
    path(); rgba(c, col); c.set_line_width(w); c.stroke()

def ellipse(c, x, y, rx, ry, ang=0.0):
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(rx, ry); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore()

def norm(v):
    n = math.hypot(*v) + 1e-9; return (v[0] / n, v[1] / n)

def draw_hani(c, J, T, st):
    """J: dict of joint name -> (x,y) screen; T: torso length px; st: state dict
       (near='L'/'R', facing in [-1,1], blink 0..1, breath 0..1, tail_t, head_tilt)"""
    near = st.get('near', 'L'); far = 'R' if near == 'L' else 'L'
    sh = ((J['Lsh'][0] + J['Rsh'][0]) / 2, (J['Lsh'][1] + J['Rsh'][1]) / 2)
    hp = ((J['Lhip'][0] + J['Rhip'][0]) / 2, (J['Lhip'][1] + J['Rhip'][1]) / 2)
    up = norm((sh[0] - hp[0], sh[1] - hp[1]))
    ang = math.atan2(up[0], -up[1])                    # torso rotation (0 = upright)
    R = 0.56 * T
    br = st.get('breath', 0.0)
    ua, fa, th, sn = 0.22 * T, 0.19 * T, 0.30 * T, 0.26 * T

    def arm(side, col, ol):
        capsule(c, [J[side + 'sh'], J[side + 'el'], J[side + 'wr']], ua, col, ol)
        hx, hy = J[side + 'wr']; ex, ey = J[side + 'el']; d = norm((hx - ex, hy - ey))
        rgba(c, ol); ellipse(c, hx + d[0] * 0.06 * T, hy + d[1] * 0.06 * T, 0.14 * T + 3, 0.12 * T + 3, math.atan2(d[1], d[0])); c.fill()
        rgba(c, CREAM); ellipse(c, hx + d[0] * 0.06 * T, hy + d[1] * 0.06 * T, 0.14 * T, 0.12 * T, math.atan2(d[1], d[0])); c.fill()
    def leg(side, col, ol):
        capsule(c, [J[side + 'hip'], J[side + 'kn'], J[side + 'an']], th, col, ol)
        ax, ay = J[side + 'an']; tx, ty = J.get(side + 'toe', (ax + 0.3 * T * st.get('facing', 1), ay))
        d = norm((tx - ax, ty - ay)); fx, fy = ax + d[0] * 0.12 * T, ay + d[1] * 0.12 * T
        rgba(c, DARK); ellipse(c, fx, fy, 0.22 * T, 0.13 * T, math.atan2(d[1], d[0])); c.fill()

    farcol = BODY_FAR
    leg(far, farcol, DARK); arm(far, farcol, DARK)
    # tail (from hips, opposite to facing, curly + sway)
    f = st.get('facing', 0.0); back = -1 if f >= 0 else 1
    t = st.get('tail_t', 0.0); sway = math.sin(t * 1.7) * 0.35
    bx, by = hp[0] + back * 0.1 * T, hp[1] + 0.05 * T
    perp = (-up[1], up[0])
    c.set_line_cap(cairo.LINE_CAP_ROUND); rgba(c, DARK); c.set_line_width(0.13 * T)
    p1 = (bx + back * 0.6 * T - up[0] * 0.2 * T, by - up[1] * 0.2 * T + 0.1 * T)
    p2 = (bx + back * (0.95 + sway * 0.3) * T + up[0] * 0.5 * T, by + up[1] * 0.5 * T)
    p3 = (bx + back * (0.75 + sway * 0.4) * T + up[0] * 0.95 * T, by + up[1] * 0.95 * T)
    c.move_to(bx, by); c.curve_to(p1[0], p1[1], p2[0], p2[1], p3[0], p3[1])
    c.rel_curve_to(back * -0.18 * T, up[1] * 0.12 * T - 0.05 * T, back * -0.3 * T, up[1] * -0.08 * T, back * -0.12 * T, up[1] * -0.2 * T)
    c.stroke()
    # torso
    cx, cy = (sh[0] + hp[0]) / 2 - up[0] * 0.05 * T, (sh[1] + hp[1]) / 2 - up[1] * 0.05 * T
    sq = 1 + 0.035 * br
    rgba(c, DARK); ellipse(c, cx, cy, 0.44 * T * sq + 3, 0.66 * T / sq ** 0.5 + 3, ang); c.fill()
    rgba(c, BODY); ellipse(c, cx, cy, 0.44 * T * sq, 0.66 * T / sq ** 0.5, ang); c.fill()
    tw = st.get('twist', 0.0)
    if tw: f = max(-1.0, min(1.0, f + tw))
    bfx = cx + perp[0] * f * 0.08 * T - up[0] * -0.06 * T; bfy = cy + perp[1] * f * 0.08 * T + up[1] * 0.06 * T
    bfx += perp[0] * tw * 0.12 * T; bfy += perp[1] * tw * 0.12 * T
    rgba(c, CREAM); ellipse(c, bfx, bfy, 0.28 * T * sq * (1 - 0.3 * abs(f)), 0.46 * T, ang); c.fill()
    # near leg before head so a folded head stays on top
    leg(near, BODY, DARK)
    arm(near, BODY, DARK)
    # head
    if 'ear' in J:
        ev = norm((J['ear'][0] - sh[0], J['ear'][1] - sh[1]))
        hd = norm((0.6 * ev[0] + 0.4 * up[0], 0.6 * ev[1] + 0.4 * up[1]))
    else: hd = up
    hc = (sh[0] + hd[0] * R * 0.72, sh[1] + hd[1] * R * 0.72)
    ha = max(-0.85, min(0.85, math.atan2(hd[0], -hd[1]) * 0.8)) + st.get('head_tilt', 0.0)
    c.save(); c.translate(*hc); c.rotate(ha)
    fx = f * 0.22 * R
    for sgn in (-1, 1):  # ears
        ex = sgn * R * 0.9 - fx * 0.6; ey = -0.12 * R
        rgba(c, DARK); c.arc(ex, ey, 0.33 * R + 3, 0, 6.3); c.fill()
        rgba(c, BODY); c.arc(ex, ey, 0.33 * R, 0, 6.3); c.fill()
        rgba(c, GOLD); c.arc(ex, ey, 0.17 * R, 0, 6.3); c.fill()
    rgba(c, DARK); c.arc(0, 0, R + 3, 0, 6.3); c.fill()
    rgba(c, BODY); c.arc(0, 0, R, 0, 6.3); c.fill()
    rgba(c, CREAM); ellipse(c, fx, 0.19 * R, 0.72 * R * (1 - 0.12 * abs(f)), 0.7 * R); c.fill()
    # crown zigzag
    c.set_line_width(0.07 * R); rgba(c, GOLD); c.set_line_join(cairo.LINE_JOIN_ROUND)
    zx = fx * 0.6; c.move_to(zx - 0.28 * R, -0.62 * R); c.line_to(zx - 0.15 * R, -0.42 * R); c.line_to(zx, -0.68 * R)
    c.line_to(zx + 0.15 * R, -0.42 * R); c.line_to(zx + 0.28 * R, -0.62 * R); c.stroke()
    # eyes
    blink = st.get('blink', 0.0)
    look = (f * 0.06 * R, 0.0)
    for sgn in (-1, 1):
        ex, ey = fx + sgn * 0.3 * R * (1 - 0.15 * abs(f)), 0.1 * R
        ry = 0.29 * R * (1 - 0.9 * blink)
        rgba(c, DARK); ellipse(c, ex, ey, 0.25 * R + 2.5, ry + 2.5); c.fill()
        rgba(c, WHITE); ellipse(c, ex, ey, 0.25 * R, ry); c.fill()
        if blink < 0.6:
            c.save(); ellipse(c, ex, ey, 0.25 * R, ry); c.clip()
            rgba(c, IRIS); c.arc(ex + look[0], ey + 0.02 * R, 0.13 * R, 0, 6.3); c.fill()
            rgba(c, CHARC); c.arc(ex + look[0], ey + 0.02 * R, 0.06 * R, 0, 6.3); c.fill()
            rgba(c, WHITE); c.arc(ex + look[0] + 0.045 * R, ey - 0.04 * R, 0.04 * R, 0, 6.3); c.fill()
            c.restore()
    # muzzle, nose, smile, cheeks
    rgba(c, CREAM); ellipse(c, fx * 1.15, 0.56 * R, 0.37 * R, 0.27 * R); c.fill()
    c.set_source_rgba(0.95, 0.6, 0.55, 0.45)
    for sgn in (-1, 1): ellipse(c, fx + sgn * 0.5 * R, 0.45 * R, 0.1 * R, 0.06 * R); c.fill()
    rgba(c, CHARC); ellipse(c, fx * 1.25, 0.42 * R, 0.075 * R, 0.05 * R); c.fill()
    c.set_line_width(0.04 * R); c.set_line_cap(cairo.LINE_CAP_ROUND)
    c.move_to(fx * 1.2 - 0.2 * R, 0.6 * R); c.curve_to(fx * 1.2 - 0.08 * R, 0.76 * R, fx * 1.2 + 0.08 * R, 0.76 * R, fx * 1.2 + 0.2 * R, 0.6 * R); c.stroke()
    c.restore()
    return hc, R

# ---------------------------------------------------------------- glow shapes (drawn behind Hani)
def glow_path(c, pts, prog, closed=True, color=GOLD, alpha=1.0, base_w=8):
    P = list(pts) + ([pts[0]] if closed else [])
    lens = [math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)]; tot = sum(lens) + 1e-6
    L = prog * tot; out = [P[0]]; tip = P[0]
    for i, l in enumerate(lens):
        if L >= l: out.append(P[i + 1]); L -= l; tip = P[i + 1]
        else:
            f = L / l; tip = (P[i][0] + (P[i + 1][0] - P[i][0]) * f, P[i][1] + (P[i + 1][1] - P[i][1]) * f); out.append(tip); break
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_join(cairo.LINE_JOIN_ROUND)
    for w, a, col in ((base_w * 7, 0.10, (1, 0.8, 0.45)), (base_w * 4.5, 0.16, (1, 0.8, 0.45)), (base_w * 2.6, 0.30, (1, 0.78, 0.4)),
                      (base_w * 1.2, 0.9, (1, 0.8, 0.48)), (base_w * 0.5, 1.0, (1, 0.97, 0.88))):
        c.move_to(*out[0])
        for p in out[1:]: c.line_to(*p)
        c.set_source_rgba(col[0], col[1], col[2], a * alpha); c.set_line_width(w); c.stroke()
    return tip

def spiral_pts(cx, cy, r0, r1, turns, rot, squash=1.0, n=160):
    pts = []
    for i in range(n + 1):
        u = i / n; a = rot + u * turns * 2 * math.pi; r = r0 + (r1 - r0) * u
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a) * squash))
    return pts
