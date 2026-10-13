"""Hani Yoga locked palette - single source of truth for every stage (sampled from Triangle v2)."""
def rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def rgbf(h): return tuple(v / 255 for v in rgb(h))
# UI
TEAL = '#136B6B'; TEAL_2 = '#2F6B6E'; GOLD = '#D99A4E'; CREAM = '#FDF8F0'; CREAM_2 = '#F7E6CD'; CHARCOAL = '#3A3A3A'
GLOW = '#FFCD78'; GLOW_CORE = '#FFF5DC'; SPARKLE = '#FFECBE'; FIREFLY = '#FFF6D7'
CONFETTI = ['#136B6B', '#D99A4E', '#F07864', '#78BEAA', '#FAC85A', '#2F6B6E']
# Studio (clean plate)
WALL = '#E2C494'; SUNBEAM = '#FAEBBE'; FLOOR = '#C8924C'; WINDOW = '#F2F5F2'; LEAF = '#658226'; POT = '#FCE798'
MAT_BLUE = '#CBE1DE'; MAT_YELLOW = '#FBEE91'; MAT_PINK = '#F5C1B0'; MAT_MINT = '#CBE1C2'; DECOR_ORANGE = '#E1700D'
# Hani (source)
FUR = '#B16F54'; FACE = '#D99B7B'; BELLY = '#DDA387'; COLLAR = '#E09540'
# Furniture (derived to sit in the studio palette)
WOOD = '#C98B4E'; WOOD_LIGHT = '#E3B27A'; WOOD_DARK = '#8E5A2E'; BOARD_FRAME = '#E8C99A'
GRADE = ('eq=saturation=1.22:contrast=1.05:gamma=1.02,colorbalance=rs=0.05:bs=-0.06:rm=0.05:gm=0.01:bm=-0.05:rh=0.03:bh=-0.03')
VIGNETTE = 'vignette=angle=PI/4.5'
FONT_SANS = 'DM Sans'; FONT_SERIF = 'Playfair Display'
