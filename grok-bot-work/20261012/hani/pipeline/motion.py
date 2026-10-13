"""Keypoint cleanup, phase detection and output time-mapping."""
import json, subprocess, numpy as np
from scipy.signal import savgol_filter, medfilt

L_SH, R_SH, L_EL, R_EL, L_WR, R_WR, L_HIP, R_HIP, L_KN, R_KN, L_AN, R_AN = 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28

def scene_cuts(src, thr=0.35):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', src, '-vf', f"scale=320:-1,select='gt(scene,{thr})',showinfo",
                          '-an', '-f', 'null', '-'], capture_output=True, text=True).stderr
    ts = []
    for line in out.splitlines():
        if 'pts_time:' in line:
            ts.append(float(line.split('pts_time:')[1].split()[0]))
    return ts

def clean(K, fps):
    K = K.copy(); T = len(K)
    ok = ~np.isnan(K[:, 0, 0])
    idx = np.arange(T)
    for j in range(33):
        for c in range(4):
            v = K[:, j, c]
            if ok.sum() > 2: K[:, j, c] = np.interp(idx, idx[ok], v[ok])
    # outlier kill + smoothing (stronger on legs)
    for j in range(33):
        for c in range(3):
            v = medfilt(K[:, j, c], 5)
            w = int(fps * (1.0 if j >= 23 else 0.6)) | 1
            K[:, j, c] = savgol_filter(v, max(5, w), 2) if T > w else v
    # depth is noisy: smooth z hard
    for j in range(33):
        w = int(fps * 2) | 1
        if T > w: K[:, j, 2] = savgol_filter(K[:, j, 2], w, 1)
    return K

def mid(K, a, b): return (K[:, a, :2] + K[:, b, :2]) / 2

def signal(K, kind):
    sh, hp = mid(K, L_SH, R_SH), mid(K, L_HIP, R_HIP)
    T = np.linalg.norm(sh - hp, axis=1) + 1e-6
    if kind == 'hinge':      # torso angle from vertical, degrees (0 upright, 90 flat)
        v = sh - hp; return np.degrees(np.arctan2(np.abs(v[:, 0]), -v[:, 1]))
    if kind == 'side_lean':  # signed lateral lean
        v = sh - hp; return np.degrees(np.arctan2(v[:, 0], -v[:, 1]))
    if kind == 'twist':      # signed shoulder rotation relative to hips (depth difference, normalised)
        dzs = K[:, L_SH, 2] - K[:, R_SH, 2]; dzh = K[:, L_HIP, 2] - K[:, R_HIP, 2]
        sw = np.abs(K[:, L_SH, 0] - K[:, R_SH, 0]); hw = np.abs(K[:, L_HIP, 0] - K[:, R_HIP, 0]) + 1e-6
        rot = np.degrees(np.arctan2(dzs - dzh, sw + 1e-6))
        return rot
    if kind == 'arms_up':
        wr = mid(K, L_WR, R_WR); return (sh[:, 1] - wr[:, 1]) / T
    if kind == 'warrior':    # signed front-knee bend: + = (MediaPipe) left knee bent more (image-right when facing camera)
        kb = knee_bends(K); return kb[:, 0] - kb[:, 1]
    if kind == 'squat':
        an = mid(K, L_AN, R_AN); return -(hp[:, 1] - an[:, 1]) / T * -1
    raise ValueError(kind)

def knee_bends(K):
    """2D knee bend in degrees (0 = straight) for [left, right]."""
    out = []
    for h, k, a in ((L_HIP, L_KN, L_AN), (R_HIP, R_KN, R_AN)):
        v1 = K[:, k, :2] - K[:, h, :2]; v2 = K[:, a, :2] - K[:, k, :2]
        c = np.sum(v1 * v2, 1) / (np.linalg.norm(v1, axis=1) * np.linalg.norm(v2, axis=1) + 1e-9)
        out.append(np.degrees(np.arccos(np.clip(c, -1, 1))))
    return np.stack(out, 1)

def _runs(mask):
    runs = []; s = None
    for i, m in enumerate(mask):
        if m and s is None: s = i
        if not m and s is not None: runs.append((s, i - 1)); s = None
    if s is not None: runs.append((s, len(mask) - 1))
    return runs

def detect_phases(sig, fps, start, sides=1, hi=0.7, lo=0.3):
    """returns list of dicts per side: enter_start, hold_start, hold_end, exit_end (frame idx)"""
    s = savgol_filter(sig, int(fps) | 1, 2)
    res = []
    signs = [1] if sides == 1 else [1, -1]
    for sg in signs:
        v = s * sg
        seg = v[start:]
        p5, p95 = np.percentile(seg, 3), np.percentile(seg, 97)
        if sides == 2: p5 = 0.0   # signed signal: neutral is zero
        n = np.clip((v - p5) / (p95 - p5 + 1e-6), 0, 1)
        n[:start] = 0
        runs = [r for r in _runs(n > hi) if r[1] - r[0] > fps * 1.5]
        if not runs: runs = _runs(n > 0.5) or [(start, len(n) - 1)]
        hs, he = max(runs, key=lambda r: r[1] - r[0])
        es = hs
        while es > start and n[es] > lo: es -= 1
        xe = he
        while xe < len(n) - 1 and n[xe] > lo: xe += 1
        res.append(dict(enter_start=es, hold_start=hs, hold_end=he, exit_end=xe, norm=n))
    res.sort(key=lambda d: d['hold_start'])
    return res

def build_map(ph, fps, first, n_src, setup_len=7.0, max_enter=8.0, hold_len=27.0, tail=1.5, min_enter=4.0, min_exit=4.0, min_rise=0.0):
    """output-time -> source-time pieces for one side; returns list of (dur, f(t_local)->src_frame, phase_name)"""
    es, hs, he, xe = ph['enter_start'], ph['hold_start'], ph['hold_end'], ph['exit_end']
    t_es, t_hs, t_he, t_xe = es / fps, hs / fps, he / fps, xe / fps
    t0 = max(first / fps, t_es - setup_len)
    P = []
    P.append(('setup', t_es - t0, lambda t, a=t0: a + t))
    if 'enter_split' in ph and ph['enter_start'] < ph['enter_split'] < ph['hold_start']:
        t_sp = ph['enter_split'] / fps
        ea = t_sp - t_es; spa = max(1.0, ea / max_enter)
        if ea < min_rise: spa = max(0.2, ea / min_rise)
        P.append(('enter', ea / spa, lambda t, a=t_es, sp=spa: a + t * sp))
        eb = t_hs - t_sp; spb = max(0.3, eb / 2.6) if eb < 2.6 else 1.0   # slow quick twists so kids can follow
        P.append(('enter_b', eb / spb, lambda t, a=t_sp, sp=spb: a + t * sp))
    else:
        ed = t_hs - t_es; sp = max(1.0, ed / max_enter)
        if ed < min_enter: sp = max(0.4, ed / min_enter)   # gentle slow-motion for quick transitions
        P.append(('enter', ed / sp, lambda t, a=t_es, sp=sp: a + t * sp))
    hd = t_he - t_hs
    if hd >= hold_len:
        P.append(('hold', hold_len, lambda t, a=t_hs: a + t))
    else:
        def pp(t, a=t_hs, d=max(hd, 0.5)):
            k = int(t // d); u = t - k * d
            return a + (u if k % 2 == 0 else d - u)
        P.append(('hold', hold_len, pp))
    xd = min(t_xe + tail, (n_src - 1) / fps) - t_he
    xs = max(0.5, xd / min_exit) if xd < min_exit else 1.0
    P.append(('exit', xd / xs, lambda t, a=t_he, xs=xs: a + t * xs))
    return P

def fix_lr_swaps(K, ratio=0.6):
    """Side-view helper (only used by "mode": "side"): MediaPipe sometimes swaps left/right labels when the body is
    seen from the side. Per frame, swap a limb group back if that is clearly (ratio) closer to the previous frame."""
    K = K.copy(); groups = [((23, 25, 27, 29, 31), (24, 26, 28, 30, 32)), ((13, 15, 17, 19, 21), (14, 16, 18, 20, 22))]
    nsw = 0
    for gl, gr in groups:
        gl, gr = list(gl), list(gr)
        for t in range(1, len(K)):
            if np.isnan(K[t, 0, 0]) or np.isnan(K[t - 1, 0, 0]): continue
            keep = np.linalg.norm(K[t, gl, :2] - K[t - 1, gl, :2], axis=1).sum() + np.linalg.norm(K[t, gr, :2] - K[t - 1, gr, :2], axis=1).sum()
            swap = np.linalg.norm(K[t, gr, :2] - K[t - 1, gl, :2], axis=1).sum() + np.linalg.norm(K[t, gl, :2] - K[t - 1, gr, :2], axis=1).sum()
            if swap < ratio * keep:
                a = K[t, gl].copy(); K[t, gl] = K[t, gr]; K[t, gr] = a; nsw += 1
    print(f'  side mode: fixed {nsw} left/right label swaps')
    return K
