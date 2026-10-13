import sys, json, wave, math
import numpy as np
ev = json.load(open(sys.argv[1])); OUT = sys.argv[2]; B = sys.argv[3] == 'v2'
SR = 44100; T = ev['total']; N = int(T * SR) + 1
t = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# warm pad: alternate Fmaj9 / Dm9 every 8s with smooth crossfade
chA = [41, 48, 57, 64, 67]; chB = [38, 45, 53, 60, 64]
xf = 0.5 - 0.5 * np.cos(2 * np.pi * t / 16)          # 0..1..0 every 16s
for chord, w in ((chA, 1 - xf), (chB, xf)):
    for j, m in enumerate(chord):
        f = hz(m); amp = [0.5, 0.42, 0.3, 0.2, 0.16][j]
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.05 + 0.017 * j) * t + j)
        for det, ch in ((-0.7, L), (0.7, R)):
            ph = 2 * np.pi * (f + det) * t
            sig = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
            ch += amp * w * lfo * sig
pad_gain = np.ones(N)
for st in ev['breath_windows']:      # pad swells with the breathing
    m = (t >= st) & (t < st + 24)
    p = ((t[m] - st) % 8) / 8
    pad_gain[m] = 1 + 0.35 * np.sin(np.pi * p) ** 2 * np.where(p < .5, 1, 0.6)
L *= pad_gain; R *= pad_gain
pad_peak = np.max(np.abs(L)); L = L / pad_peak * 0.16; R = R / pad_peak * 0.16

def bell(at, m, amp, dec=2.8, pan=0.0):
    i0 = int(at * SR); n = int(min(N - i0, SR * dec * 2.2))
    if n <= 0: return
    tt = np.arange(n) / SR; f = hz(m)
    env = np.exp(-tt / dec * 2.2) * np.minimum(1, tt / 0.004)
    s = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 2)
         + 0.14 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3) + 0.05 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 6))
    L[i0:i0 + n] += amp * env * s * (1 - pan) ; R[i0:i0 + n] += amp * env * s * (1 + pan)
penta = [72, 74, 76, 79, 81, 84]
for k, at in enumerate(sorted(ev['chimes'])): bell(at, penta[k % len(penta)], 0.07, 2.6, 0.3 * math.sin(k))
for k, at in enumerate(ev['inhale']): bell(at, [79, 81, 84][k % 3], 0.06, 3.5, -0.2)
for at in ev['sparkle']:
    for j, m in enumerate([84, 88, 91, 96, 100]): bell(at + j * 0.09, m, 0.045, 1.4, -0.5 + 0.25 * j)
for j, at in enumerate(ev['boops']): bell(at, [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86][j % 12], 0.06, 0.35, -0.4 + 0.07 * j)
for at in ev['confetti']:
    rng = np.random.default_rng(3)
    for j in range(14): bell(at + j * 0.07 + rng.uniform(0, .03), int(rng.choice([84, 86, 88, 91, 93, 96])), 0.035, 1.0, rng.uniform(-.7, .7))
    for j, m in enumerate([72, 76, 79, 84]): bell(at + 0.05, m, 0.05, 2.5, 0)
fade = np.minimum(1, np.minimum(t / 1.5, (T - t) / 2.0)).clip(0, 1)
L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); g = 0.35 / pk if pk > 0.35 else 1  # cap peak ~ -9 dBFS
st = (np.stack([L, R], 1) * g * 32767).astype(np.int16)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
print('audio', T, 'peak', pk)
