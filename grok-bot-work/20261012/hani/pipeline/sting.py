"""Mix extra Warrior-style sound effects into the synthesized soundtrack (does not touch build/audio.py).
usage: sting.py events.json in.wav out.wav
events keys: beam [t] (beam ignition shimmer), sting [t] (heroic brass + timpani hit), riser [[t0, t1]] (soft swell), party [t] (confetti pops + applause/cheer, opt-in celebrate)."""
import sys, json, wave, numpy as np
ev = json.load(open(sys.argv[1])); src, out = sys.argv[2], sys.argv[3]
with wave.open(src) as w: SR = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2).astype(np.float64) / 32767
N = len(x); add = np.zeros_like(x); addp = np.zeros_like(x)   # addp = party (mixed under the limiter below)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
def place(at, sig, pan=0.0, buf=None):
    buf = add if buf is None else buf
    i0 = int(at * SR); n = min(len(sig), N - i0)
    if n <= 0 or i0 < 0: return
    buf[i0:i0 + n, 0] += sig[:n] * (1 - pan); buf[i0:i0 + n, 1] += sig[:n] * (1 + pan)
def brass(m, dur, amp):
    t = np.arange(int(dur * SR)) / SR; f = hz(m)
    env = np.minimum(1, t / 0.05) * np.exp(-t / (dur * 0.45)); vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.3)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    s = sum((0.9 ** k) / k * np.sin(k * ph) for k in range(1, 9))          # bright, saw-like
    s *= 0.6 + 0.4 * np.minimum(1, t / 0.12)                               # brassy swell
    return amp * env * s
def timp(dur=1.6, amp=0.5):
    t = np.arange(int(dur * SR)) / SR; f = 70 * (1 + 0.35 * np.exp(-t * 18))
    ph = 2 * np.pi * np.cumsum(f) / SR; rng = np.random.default_rng(1)
    return amp * (np.sin(ph) * np.exp(-t * 3.2) + 0.25 * rng.standard_normal(len(t)) * np.exp(-t * 40))
for at in ev.get('sting', []):
    # F major hero chord (fits the F/Dm pad): F3 C4 F4 A4 C5, quick pickup note first
    place(at - 0.16, brass(60, 0.18, 0.05))
    for j, m in enumerate([53, 60, 65, 69, 72]): place(at, brass(m, 2.2, 0.055), pan=-0.3 + 0.15 * j)
    place(at, timp(), 0.0)
for at in ev.get('beam', []):
    t = np.arange(int(1.9 * SR)) / SR; f = hz(76) * 2 ** (t / 1.6 * 1.0)      # rising one-octave glide
    s = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * np.minimum(1, t / 0.2) * np.exp(-np.maximum(0, t - 1.5) * 6)
    s *= 0.5 + 0.5 * np.sin(2 * np.pi * 9 * t)                               # shimmer
    place(at, 0.035 * s, -0.4); place(at + 0.03, 0.035 * s, 0.4)
for t0, t1 in ev.get('riser', []):
    d = max(0.5, t1 - t0); t = np.arange(int(d * SR)) / SR; rng = np.random.default_rng(2)
    nz = rng.standard_normal(len(t)); k = 60; nz = np.convolve(nz, np.ones(k) / k, 'same')   # soft (low-passed) noise
    tone = np.sin(2 * np.pi * np.cumsum(hz(41) * 2 ** (t / d)) / SR)
    place(t0, (0.5 * nz * 3 + 0.25 * tone) * 0.07 * (t / d) ** 2)
for at in ev.get('party', []):
    # party-popper pops (left, right, centre) + a short kids'-party applause/cheer swell under the confetti bells
    rng = np.random.default_rng(7)
    def pop(amp):
        t = np.arange(int(0.25 * SR)) / SR; nz = rng.standard_normal(len(t))
        body = np.sin(2 * np.pi * np.cumsum(180 * (1 + 2.5 * np.exp(-t * 60))) / SR) * np.exp(-t * 28)
        return amp * (0.8 * nz * np.exp(-t * 90) + 0.9 * body)
    for dt, pan in ((0.0, -0.6), (0.12, 0.6), (0.27, 0.0)): place(at + dt, pop(0.14), pan, addp)
    d = 3.2; n = int(d * SR); t = np.arange(n) / SR; env = np.minimum(1, t / 0.35) * np.exp(-np.maximum(0, t - 0.9) * 1.4)
    for ch, pan in ((0, -0.5), (1, 0.5)):           # applause: hundreds of tiny filtered noise claps
        cl = np.zeros(n)
        for _ in range(int(260 * d)):
            i0 = int(rng.uniform(0, d) * SR); k = int(0.012 * SR)
            if i0 + k < n: cl[i0:i0 + k] += rng.standard_normal(k) * np.exp(-np.arange(k) / (0.0025 * SR)) * rng.uniform(.3, 1)
        cl = cl - np.convolve(cl, np.ones(8) / 8, 'same')     # brighten (crude high-pass)
        place(at + 0.15, 0.10 * cl * env, pan, addp)
    nz = rng.standard_normal(n); cheer = np.zeros(n)        # "yaaay" crowd: noise through two vowel formants, rising pitch wobble
    for f0, bw in ((850, 180), (1250, 220)):
        fr = np.fft.rfftfreq(n, 1 / SR); sp = np.fft.rfft(nz) * np.exp(-((fr - f0 * (1.0)) / bw) ** 2)
        cheer += np.fft.irfft(sp, n)
    cheer *= (1 + 0.3 * np.sin(2 * np.pi * 5.5 * t)) / (np.abs(cheer).max() + 1e-9)
    place(at + 0.2, 0.05 * cheer * env, 0.0, addp)
    def bell(at_, m, amp, dec, pan):                         # confetti bell shower (same voicing as build/audio.py)
        n_ = int(SR * dec * 2.2); tt = np.arange(n_) / SR; f = hz(m)
        env_ = np.exp(-tt / dec * 2.2) * np.minimum(1, tt / 0.004)
        s_ = (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 2)
              + 0.14 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt * 3) + 0.05 * np.sin(2 * np.pi * f * 5.4 * tt) * np.exp(-tt * 6))
        place(at_, amp * env_ * s_, pan, addp)
    r3 = np.random.default_rng(3)
    for j in range(14): bell(at + 0.3 + j * 0.07 + r3.uniform(0, .03), int(r3.choice([84, 86, 88, 91, 93, 96])), 0.06, 1.0, r3.uniform(-.7, .7))
    for j, m in enumerate([72, 76, 79, 84]): bell(at + 0.35, m, 0.08, 2.5, 0)
y = x + add
pk = np.abs(y).max(); y = y * (0.5 / pk if pk > 0.5 else 1)   # rest of the mix normalised exactly as before
gp = 1.0                                                       # party sounds are trimmed so they never change that normalisation
while np.abs(addp).max() > 0 and np.abs(y + gp * addp).max() > 0.5 and gp > 0.05: gp *= 0.92
y = y + gp * addp
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((y * 32767).astype(np.int16).tobytes())
print('fx audio: party', len(ev.get('party', [])), 'party gain', round(gp, 3), 'sting', len(ev.get('sting', [])), 'beam', len(ev.get('beam', [])), 'riser', len(ev.get('riser', [])), 'peak', round(pk, 3))
