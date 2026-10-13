"""Hani SEL tool explainer (captions only, no VO). Reuses the Triangle v2 brand layer (bold/bold_base/celebrate),
the cut-out puppet (puppet/rig.py Puppet + draw_chair/draw_tail/floor_shadow) and studio_floor.png.
Captions = each step's `cue` then its `sub` from v101/mainwt/hani-rise.html, word for word.
Usage: venv/bin/python sel/make_sel.py <tool_id> [<tool_id> ...]"""
import sys, os, re, json, math, subprocess
sys.path[:0] = ['/workspace/hani/pipeline', '/workspace/hani/puppet', '/workspace/hani/brand']
import numpy as np, cairo
from PIL import Image
import bold as BD, celebrate as CEL, rig as PR
from bold_base import fireflies, draw_caps, ease
W, H, FPS = 1920, 1080, 25; XF = 0.6; IDLE = 4.0; ROOT = '/workspace/hani'
HTML = open('/workspace/v101/mainwt/hani-rise.html', encoding='utf-8').read()

def jsstr(s): return json.loads('"' + s + '"')
def load_tool(tid):
    m = re.search(r'\{\s*id:"%s".*?name:"((?:[^"\\]|\\.)*)".*?tag:"((?:[^"\\]|\\.)*)".*?lines:\[(.*?)\]\s*,\s*close:' % re.escape(tid), HTML, re.S)
    name, tag, body = jsstr(m.group(1)), jsstr(m.group(2)), m.group(3)
    steps = [(jsstr(c), jsstr(s)) for c, s in re.findall(r'cue:"((?:[^"\\]|\\.)*)",sub:"((?:[^"\\]|\\.)*)"', body)]
    return name, tag, steps

def hold(txt):   # reading time: 3-5 s by word count
    return float(np.clip(1.6 + 0.42 * len(txt.split()), 3.0, 5.0))

BGI = Image.open(ROOT + '/brand/studio_floor.png').convert('RGB')
_bg = np.asarray(BGI.convert('RGBA'))[:, :, [2, 1, 0, 3]].copy()
BGS = cairo.ImageSurface.create_for_data(memoryview(_bg), cairo.FORMAT_ARGB32, W, H)
PUP = PR.Puppet(); T = 250.0; g = T / PR.SRC_T
SEAT = 868 - 0.76 * T
CH = dict(x=960.0, floor=900.0, seat_y=SEAT, back_top=SEAT - 0.08 * T - 1.0 * T + 0.20 * T)

def skel(t):
    """Calm seated Hani: hands resting on knees; slow breath (4 s in / 4 s out), soft bob, gentle head sway."""
    br = 0.5 - 0.5 * math.cos(2 * math.pi * t / 8.0)
    bob = 3.0 * math.sin(2 * math.pi * t / 8.0 - 1.2)
    hm = np.array([960.0, SEAT - 0.08 * T + bob * 0.3]); ax = np.array([math.sin(0.015 * math.sin(t * 0.5)), -1.0]); ax /= np.linalg.norm(ax)
    sm = hm + ax * T * (1.0 + 0.025 * br) + [0, bob * 0.5]
    perp = np.array([-ax[1], ax[0]]); perp = -perp if perp[0] < 0 else perp
    wmul = 1.0 + 0.015 * br
    S = dict(hm=hm, sm=sm, ax=ax, perp=perp, g=g, wmul=wmul)
    for s, sg in (('L', 1), ('R', -1)):
        S[s + 'sh'] = sm + perp * sg * 51 * g * wmul - ax * 4 * g
        S[s + 'hip'] = hm + perp * sg * 37 * g
        kn = np.array([S[s + 'hip'][0] + sg * 0.22 * T, SEAT + 0.04 * T]); S[s + 'kn'] = kn
        S[s + 'an'] = np.array([kn[0] + sg * 0.05 * T, 868.0])
        wr_t = kn + [sg * -0.02 * T, -0.10 * T]
        el, wr = PR.ik(S[s + 'sh'], wr_t, PUP.len['ua'] * g, PUP.len['fa'] * g, S[s + 'sh'] + perp * sg * 0.4 * T + [0, 0.3 * T])
        td = np.array([sg * -0.25, 1.0]); td /= np.linalg.norm(td)
        S[s + 'el'], S[s + 'wr'], S[s + 'tip'], S[s + 'hid'] = el, wr, wr + td * 58 * g, 0.0
    neck = sm + ax * 6 * g; ha = 0.05 * math.sin(t * 0.55) + 0.02 * math.sin(t * 1.1)
    S['neck'] = neck; S['crown'] = neck + np.array([math.sin(ha), -math.cos(ha)]) * 128 * g
    S['yaw'] = 0.0; S['yaw_sign'] = 1
    return S, br

def scene(lt, caps, blast_t, name, badge):
    S = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(S)
    c.set_source_surface(BGS); c.paint()
    SK, br = skel(lt)
    PR.draw_chair(c, CH, T); PR.floor_shadow(c, 960, 902, 0.75 * T, 0.07 * T, 0.25)
    PR.draw_tail(c, SK['hm'], T, SEAT, lt * 0.7, side=1)
    PR.floor_shadow(c, SK['hm'][0], SEAT - 0.07 * T, 0.55 * T, 0.09 * T, 0.35)
    S.flush(); arr = np.frombuffer(S.get_data(), np.uint8).reshape(H, W, 4)[:, :, [2, 1, 0]].astype(np.float32)
    PUP.draw(arr, SK, T, dict(breath=br))
    im = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert('RGBA')
    fireflies(im, lt)
    if lt >= blast_t: CEL.blast(im, lt - blast_t)
    if lt < IDLE + 0.6: BD.title_overlay(im, lt, name, badge, IDLE)
    draw_caps(im, lt, caps)
    return im

def build(tid):
    name, tag, steps = load_tool(tid)
    texts = [x for cue, sub in steps for x in (cue, sub) if x.strip()]
    caps, t = [], IDLE
    for i, x in enumerate(texts):
        d = hold(x) + (1.5 if i == len(texts) - 1 else 0)   # last caption a little longer (blast)
        caps.append((t, t + d, x)); t += d
    blast_t = caps[-1][0]; scene_dur = t + 1.2; outro = 4.2
    total = scene_dur + outro - XF
    badge = tag.split('·')[0].strip() + ' · ' + tag.split('·')[1].strip()   # "SEL · Self-Awareness"
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    slug += os.environ.get('SEL_SUFFIX', ''); out = f'{ROOT}/sel/{slug}_v1.mp4'; mid = f'/tmp/sel_{slug}_mid.mkv'
    json.dump(dict(id=tid, name=name, badge=badge, duration=round(total, 2), blast_t=round(blast_t, 2),
                   captions=[dict(start=round(a, 2), end=round(b, 2), text=x) for a, b, x in caps]),
              open(f'{ROOT}/sel/{slug}_v1_timeline.json', 'w'), indent=1, ensure_ascii=False)
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                           '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '14', '-pix_fmt', 'yuv420p', mid], stdin=subprocess.PIPE)
    o0 = scene_dur - XF
    for n in range(int(round(total * FPS))):
        tt = n / FPS
        if tt < o0: fr = scene(tt, caps, blast_t, name, badge).convert('RGB')
        elif tt >= scene_dur: fr = BD.outro_card(tt - o0, name, confetti='full').convert('RGB')
        else:
            al = ease((tt - o0) / XF)
            fr = Image.blend(scene(tt, caps, blast_t, name, badge).convert('RGB'), BD.outro_card(tt - o0, name, confetti='full').convert('RGB'), al)
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', mid, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-shortest',
                    '-c:v', 'libx264', '-preset', 'slow', '-tune', 'animation', '-profile:v', 'high', '-crf', '20', '-maxrate', '4000k',
                    '-bufsize', '8000k', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', out], check=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', out, '-vf', f'fps=1/{total/16:.3f},scale=480:-1,tile=4x4', '-frames:v', '1',
                    f'{ROOT}/sel/{slug}_v1_contact.png'], check=True)
    print(out, round(total, 2), len(caps), 'captions')

if __name__ == '__main__':
    for tid in sys.argv[1:]: build(tid)
