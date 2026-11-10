"""Ses miksi: diyalog + ortam + kodla uretilmis SFX ve fon muzigi (telifsiz, tamamen numpy sentezi).
Cikti: work/mix_pre.wav (48 kHz stereo, normalize edilmemis), work/sfx_only.wav, work/music_only.wav
"""
import wave, sys, numpy as np
from edl import timeline
SR = 48000
TL = timeline(); DUR = TL[-1]["t1"]; NS = int(round(DUR * SR))
MUSIC = "--no-music" not in sys.argv
rng = np.random.default_rng(7)

def load(n):
    w = wave.open(f"a48/{n}.wav"); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def db(x): return 10 ** (x / 20)

# ---------------------------------------------------------------- diyalog + ortam
dlg = np.zeros(NS, np.float32); amb = np.zeros(NS, np.float32); speech_mask = np.zeros(NS, np.float32)
for x in TL:
    a = load(x["clip"]); i0 = round(x["s"] * SR); i1 = round(x["e"] * SR); o = round(x["t0"] * SR)
    seg = a[i0:i1].copy(); n = min(len(seg), NS - o); seg = seg[:n]
    f = int((0.012 if x["kind"] == "konusma" else 0.04) * SR)
    seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    if x["kind"] == "konusma":
        dlg[o:o + n] += seg; speech_mask[o:o + n] = 1
    elif x["kind"].startswith("split"):
        b = load(x["kind"].split(":")[1])[i0:i1][:n].copy(); b[:f] *= np.linspace(0, 1, f); b[-f:] *= np.linspace(1, 0, f)
        amb[o:o + n] += 0.5 * (seg + b) * db(-12)
    else:
        amb[o:o + n] += seg * db(-12)
# 80 Hz high-pass (1. derece, iki kez)
def hp(x, fc=80):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); px = py = 0.0
    for _ in range(2):
        y = np.empty_like(x); px = py = 0.0
        # vektorlestirilmis tek kutuplu HP: y[n] = a*(y[n-1] + x[n] - x[n-1])
        from scipy.signal import lfilter
        y = lfilter([a, -a], [1, -a], x).astype(np.float32); x = y
    return y
dlg = hp(dlg); amb = hp(amb, 100)

# ---------------------------------------------------------------- SFX sentezi
def env_ad(n, a, d):
    e = np.ones(n, np.float32); na = int(a * SR); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def pop(dur=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 350
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.03)).astype(np.float32)
def whoosh(dur=0.45, up=True):
    n = int(dur * SR); noise = rng.standard_normal(n).astype(np.float32)
    from scipy.signal import lfilter
    out = np.zeros(n, np.float32); hop = 480
    for k in range(0, n, hop):       # zamanla kayan bant-gecirgen (kaba ama etkili)
        p = k / n; fc = (400 + 3200 * p) if up else (3600 - 3200 * p)
        r = 0.97; th = 2 * np.pi * fc / SR
        b, a = [1 - r], [1, -2 * r * np.cos(th), r * r]
        out[k:k + hop] = lfilter(b, a, noise[max(0, k - 2000):k + hop])[-len(out[k:k + hop]):]
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    out = out * e; return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)
def shimmer(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k, f in enumerate([1318.5, 1568, 1975.5, 2637]):   # E6 G6 B6 E7 arpej
        st = int(k * 0.07 * SR); m = n - st
        y[st:] += np.sin(2 * np.pi * f * t[:m]) * env_ad(m, 0.004, 0.25) * 0.5
    return y / np.abs(y).max()
def tick():
    n = int(0.04 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * env_ad(n, 0.001, 0.006)).astype(np.float32)

sfx = np.zeros(NS, np.float32)
def put(sig, t, g):
    o = int(t * SR); n = min(len(sig), NS - o); sfx[o:o + n] += sig[:n] * db(g)
put(shimmer(), 0.12, -20)
for t in (2.62, 17.05, 29.95, 33.10): put(pop(), t, -19)       # rozet girisleri
split = next(x for x in TL if x["kind"].startswith("split"))
put(whoosh(0.4, True), split["t0"] - 0.2, -22); put(whoosh(0.4, False), split["t1"] - 0.2, -24)
put(tick(), split["t0"] + 0.27, -22); put(tick(), split["t0"] + 0.33, -22)
put(whoosh(0.5, True), 2.50 - 0.25, -25)                        # acilistan kafeye gecis

# ---------------------------------------------------------------- fon muzigi (sentez, 92 BPM, yumusak lo-fi)
mus = np.zeros(NS, np.float32)
if MUSIC:
    bpm = 92; beat = 60 / bpm; bar = 4 * beat
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 52, 55, 59], [55, 59, 62, 65]]   # Am7 Fmaj7 Cmaj7 G7
    mf = lambda m: 440 * 2 ** ((m - 69) / 12)
    t_all = np.arange(NS) / SR
    for bi in range(int(DUR / bar) + 2):
        ch = chords[bi % 4]; t0 = bi * bar
        for m in ch:   # elektrik piyano benzeri: sinus + hafif 2. harmonik, yavas sonum
            o = int(t0 * SR); n = min(int(bar * SR), NS - o)
            if n <= 0: continue
            t = np.arange(n) / SR; f = mf(m)
            v = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t + 0.3)) * env_ad(n, 0.01, 1.2) * 0.12
            mus[o:o + n] += v.astype(np.float32)
        # bas
        o = int(t0 * SR); n = min(int(bar * SR), NS - o)
        if n > 0:
            t = np.arange(n) / SR; mus[o:o + n] += (np.sin(2 * np.pi * mf(ch[0] - 12) * t) * env_ad(n, 0.01, 0.9) * 0.18).astype(np.float32)
        for k in range(4):   # yumusak kick (1,3) + hat (her vurus arasi)
            tb = t0 + k * beat; o = int(tb * SR)
            if k in (0, 2) and o < NS:
                n = min(int(0.25 * SR), NS - o); t = np.arange(n) / SR
                mus[o:o + n] += (np.sin(2 * np.pi * np.cumsum(60 + 90 * np.exp(-t * 30)) / SR) * env_ad(n, 0.002, 0.08) * 0.35).astype(np.float32)
            oh = int((tb + beat / 2) * SR)
            if oh < NS:
                n = min(int(0.05 * SR), NS - oh)
                hh = rng.standard_normal(n).astype(np.float32); hh = np.diff(np.concatenate([[0], hh])) * env_ad(n, 0.001, 0.012) * 0.05
                mus[oh:oh + n] += hh
    fade = int(1.2 * SR); mus[-fade:] *= np.linspace(1, 0, fade); mus[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
    # konusma altinda duck (yumusak, 150 ms)
    from scipy.ndimage import uniform_filter1d
    duck = 1 - 0.7 * np.clip(uniform_filter1d(speech_mask, int(0.3 * SR)), 0, 1)
    mus *= duck * db(-14)

mix = dlg + amb + sfx + mus
st = np.stack([mix, mix], 1)
def wr(p, x):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    w = wave.open(p, "wb"); w.setnchannels(x.shape[1] if x.ndim > 1 else 1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
wr("work/mix_pre.wav", st / max(1.0, np.abs(st).max() / 0.98))
wr("work/sfx_only.wav", sfx); wr("work/music_only.wav", mus)
print("sure", DUR, "tepe", np.abs(mix).max())
