"""Build studio backgrounds from the graded Triangle clean plate.
studio_floor.png : plain studio (floor/standing poses)
studio_chair.png : + 'Hani Yoga' whiteboard (chair/desk poses only). The chair itself is drawn per frame."""
import sys, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, '/workspace/hani/brand'); import palette as P
sys.path.insert(0, '/workspace/hani/pipeline'); from bold_base import font
plate = Image.open('/workspace/hani/brand/studio_plate_graded.png').convert('RGB')
plate.save('/workspace/hani/brand/studio_floor.png')
W, H = plate.size
x0, y0, x1, y1 = 700, 92, 1220, 342      # board incl. frame
lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
# soft wall shadow
sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle((x0 + 10, y0 + 16, x1 + 10, y1 + 18), 18, fill=120)
sh = sh.filter(ImageFilter.GaussianBlur(14))
fr = 16
d.rounded_rectangle((x0, y0, x1, y1), 16, fill=P.rgb(P.BOARD_FRAME) + (255,))
d.rounded_rectangle((x0, y0, x1, y1), 16, outline=P.rgb(P.WOOD) + (255,), width=3)
d.rounded_rectangle((x0 + fr, y0 + fr, x1 - fr, y1 - fr), 8, fill=P.rgb(P.CREAM) + (255,))
d.line((x0 + fr, y0 + fr + 1, x1 - fr, y0 + fr + 1), fill=P.rgb(P.CREAM_2) + (255,), width=3)
# title
tf = font('p', 70, 'Bold'); cx = (x0 + x1) // 2
d.text((cx, y0 + 108), 'Hani Yoga', font=tf, fill=P.rgb(P.TEAL_2) + (255,), anchor='mm')
# gold swoosh underline
pts = [(cx - 150 + i * 3, y0 + 160 + 7 * np.sin(i / 100 * np.pi * 1.0) - i * 0.04) for i in range(101)]
d.line(pts, fill=P.rgb(P.GOLD) + (255,), width=7, joint='curve')
# doodles: sun (gold), leaf (teal), star (orange), little hearts/dots
sx, sy = x0 + 62, y0 + 62
d.ellipse((sx - 15, sy - 15, sx + 15, sy + 15), fill=P.rgb(P.GOLD) + (255,))
for k in range(8):
    a = k * np.pi / 4; d.line((sx + 21 * np.cos(a), sy + 21 * np.sin(a), sx + 29 * np.cos(a), sy + 29 * np.sin(a)), fill=P.rgb(P.GOLD) + (255,), width=4)
def star(c, r, col):
    p = []
    for k in range(10):
        a = -np.pi / 2 + k * np.pi / 5; rr = r if k % 2 == 0 else r * 0.45; p.append((c[0] + rr * np.cos(a), c[1] + rr * np.sin(a)))
    d.polygon(p, fill=P.rgb(col) + (255,))
star((x1 - 60, y0 + 60), 22, P.DECOR_ORANGE)
# leaf
lx, ly = x0 + 58, y1 - 66
d.ellipse((lx - 11, ly - 26, lx + 11, ly + 22), fill=P.rgb(P.TEAL_2) + (255,)); d.line((lx, ly - 30, lx, ly + 40), fill=P.rgb(P.TEAL) + (255,), width=3)
# breathing dots row
sf = font('d', 28, 'Bold')
d.text((cx, y1 - 56), 'breathe  •  stretch  •  smile', font=sf, fill=P.rgb(P.CHARCOAL) + (230,), anchor='mm')
star((x1 - 56, y1 - 62), 13, P.TEAL)
# marker tray
d.rounded_rectangle((cx - 120, y1 - 6, cx + 120, y1 + 8), 5, fill=P.rgb(P.WOOD) + (255,))
for i, col in enumerate([P.TEAL, P.GOLD, P.DECOR_ORANGE]):
    d.rounded_rectangle((cx - 80 + i * 50, y1 - 14, cx - 40 + i * 50, y1 - 4), 4, fill=P.rgb(col) + (255,))
# grade the board like the plate (warmth) and let the window light fall across it
arr = np.asarray(lay).astype(np.float32)
pl = np.asarray(plate).astype(np.float32)
lum = cv2.GaussianBlur(pl.mean(2), (0, 0), 6)
base = np.median(lum[y0:y1, x0:x1])
light = np.clip(lum / base, 0.8, 1.18)[..., None]
warm = np.array([1.0, 0.975, 0.93])
rgbv = np.clip(arr[..., :3] * warm * (0.94 + 0.06) * light, 0, 255)
a = arr[..., 3:] / 255
out = pl * (1 - np.asarray(sh, np.float32)[..., None] / 255 * 0.35)
out = out * (1 - a) + rgbv * a
Image.fromarray(out.astype(np.uint8)).save('/workspace/hani/brand/studio_chair.png')
Image.fromarray(out.astype(np.uint8)).resize((960, 540)).save('/workspace/hani/brand/studio_chair_chk2.png')
Image.fromarray(out.astype(np.uint8)).crop((660,60,1260,380)).save('/workspace/hani/brand/board_zoom.png')
