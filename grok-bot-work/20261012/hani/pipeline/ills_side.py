"""Extra fun-fact illustrations (locked palette, same flat style as bold.ill_warrior). Registered into bold.ILL under
NEW keys only ('camel', 'sun', 'bow'); existing keys/illustrations are untouched."""
import math
from PIL import Image, ImageDraw
from bold_base import ease

TEAL = (19, 107, 107); TEAL2 = (47, 107, 110); GOLD = (217, 154, 78); CREAM = (253, 248, 240)
CORAL = (240, 120, 100); MINT = (120, 190, 170); YEL = (250, 200, 90); GLOW = (255, 205, 120); CORE = (255, 236, 190)

def _canvas(): return Image.new('RGBA', (2000, 900), (0, 0, 0, 0))
def _fin(c, k):
    c.putalpha(c.getchannel('A').point(lambda v: int(v * k)))
    return c.resize((1000, 450), Image.LANCZOS)
def _sun(d, cx, cy, r, lt, rays=12):
    for j in range(rays):
        a = lt * 0.3 + j * 2 * math.pi / rays; r0, r1 = r + 22, r + 95 + (20 if j % 2 else 0); w = 0.08
        d.polygon([(cx + r0 * math.cos(a - w), cy + r0 * math.sin(a - w)), (cx + r1 * math.cos(a), cy + r1 * math.sin(a)),
                   (cx + r0 * math.cos(a + w), cy + r0 * math.sin(a + w))], fill=(250, 200, 90, 200 if j % 2 else 140))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GLOW + (255,)); d.ellipse([cx - r * .78, cy - r * .78, cx + r * .78, cy + r * .78], fill=CORE + (255,))

def ill_camel(prog, lt):
    """desert dunes + sun + a teal camel whose hump fills with a gold 'energy' glow (fat store)."""
    c = _canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    _sun(d, 1560, 250, 120, lt)
    d.ellipse([-300, 600, 1100, 1100], fill=YEL + (255,)); d.ellipse([800, 640, 2300, 1150], fill=GOLD + (255,))
    bob = 6 * math.sin(lt * 3.0); x0, y0 = 760, 470 + bob
    leg = lambda x, ph: d.line([(x, y0 + 60), (x + 18 * math.sin(lt * 3 + ph), y0 + 250)], fill=TEAL, width=36)
    for x, ph in ((x0 - 120, 0), (x0 - 70, 2), (x0 + 150, 1), (x0 + 200, 3)): leg(x, ph)
    d.ellipse([x0 - 190, y0 - 70, x0 + 260, y0 + 110], fill=TEAL + (255,))                   # body
    hump = ease(min(1.0, prog * 1.4))
    d.ellipse([x0 - 90, y0 - 200, x0 + 160, y0 - 10], fill=TEAL + (255,))                     # hump
    d.ellipse([x0 - 40, y0 - 160 + 40 * (1 - hump), x0 + 110, y0 - 40], fill=GOLD + (255,))   # gold fat store
    d.line([(x0 + 230, y0 - 10), (x0 + 330, y0 - 190)], fill=TEAL, width=64)                  # neck
    d.ellipse([x0 + 290, y0 - 250, x0 + 430, y0 - 160], fill=TEAL + (255,))                   # head
    d.ellipse([x0 + 380, y0 - 228, x0 + 398, y0 - 210], fill=CREAM + (255,))                  # eye
    d.line([(x0 - 185, y0 - 10), (x0 - 245, y0 + 90)], fill=TEAL, width=16)                   # tail
    for j in range(5):                                                                        # sparkle dots round the hump
        a = lt * 1.5 + j * 1.256; r = 150
        d.ellipse([x0 + 35 + r * math.cos(a) - 9, y0 - 110 + r * 0.6 * math.sin(a) - 9, x0 + 35 + r * math.cos(a) + 9, y0 - 110 + r * 0.6 * math.sin(a) + 9],
                  fill=CORAL + (int(200 * hump),))
    return _fin(c, k)

def ill_sun(prog, lt):
    """big smiling sun + a beam of light zooming to a small Earth (light travel)."""
    c = _canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    _sun(d, 420, 430, 210, lt, 16)
    d.arc([330, 430, 510, 540], 20, 160, fill=TEAL, width=14)
    d.ellipse([350, 380, 378, 408], fill=TEAL + (255,)); d.ellipse([462, 380, 490, 408], fill=TEAL + (255,))
    ex, ey = 1640, 430
    d.ellipse([ex - 120, ey - 120, ex + 120, ey + 120], fill=(110, 185, 225, 255))
    d.ellipse([ex - 80, ey - 70, ex + 10, ey + 20], fill=MINT + (255,)); d.ellipse([ex + 10, ey + 10, ex + 90, ey + 80], fill=MINT + (255,))
    q = (lt * 0.45) % 1.0
    for j in range(3):
        u = (q + j / 3) % 1.0; x = 680 + u * 800
        d.line([(x - 120, ey), (x, ey)], fill=(255, 236, 190, int(255 * math.sin(math.pi * u))), width=22)
        d.ellipse([x - 16, ey - 16, x + 16, ey + 16], fill=(255, 245, 220, int(255 * math.sin(math.pi * u))))
    return _fin(c, k)

def ill_bow(prog, lt):
    """an archer's bow (gold) with a teal string pulled back and a coral-tipped arrow; it gently draws and relaxes."""
    c = _canvas(); d = ImageDraw.Draw(c); k = ease(prog)
    cx, cy = 1000, 450; pull = 60 + 70 * (0.5 + 0.5 * math.sin(lt * 1.6))
    pts = [(cx - 260 + 210 * math.sin(math.pi * u), cy - 330 + 660 * u) for u in [i / 40 for i in range(41)]]
    d.line(pts, fill=GOLD, width=40, joint='curve')
    top, bot = pts[0], pts[-1]; nock = (cx - 260 - pull, cy)
    d.line([top, nock, bot], fill=TEAL, width=10)
    d.line([nock, (cx + 420, cy)], fill=TEAL2, width=16)
    d.polygon([(cx + 470, cy), (cx + 400, cy - 34), (cx + 400, cy + 34)], fill=CORAL + (255,))
    d.polygon([nock, (nock[0] - 50, cy - 40), (nock[0] + 20, cy)], fill=MINT + (255,)); d.polygon([nock, (nock[0] - 50, cy + 40), (nock[0] + 20, cy)], fill=MINT + (255,))
    return _fin(c, k)

ILL = {'camel': ill_camel, 'sun': ill_sun, 'bow': ill_bow}
