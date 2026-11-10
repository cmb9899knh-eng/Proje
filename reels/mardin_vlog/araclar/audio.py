"""Ses miksi v2: diyalog + ortam + kodla uretilmis SFX + (istege bagli) kodla bestelenmis muzik.
Kullanim: python3 audio.py [--no-music]   -> work/mix_pre.wav (48 kHz stereo, normalize edilmemis)
Telifli ses yok: tum efektler ve muzik numpy ile sentezlenir."""
import wave, sys, numpy as np
from scipy.signal import lfilter
from scipy.ndimage import uniform_filter1d
from edl import timeline, clip_audio, aud_src
SR = 48000
TL = timeline(); DUR = TL[-1]["t1"]; NS = int(round(DUR * SR))
MUSIC = "--no-music" not in sys.argv
rng = np.random.default_rng(7)
def load(c):
    w = wave.open(clip_audio(c)); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def db(x): return 10 ** (x / 20)
def hp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2): x = lfilter([a, -a], [1, -a], x).astype(np.float32)
    return x

# ---------------------------------------------------------------- diyalog + ortam
dlg = np.zeros(NS, np.float32); amb = np.zeros(NS, np.float32); speech = np.zeros(NS, np.float32)
for x in TL:
    o = round(x["t0"] * SR); n = round((x["t1"] - x["t0"]) * SR); n = min(n, NS - o)
    if x["kind"] == "foto": continue
    if x["kind"] == "konusma":
        c, s0 = aud_src(x); a = load(c)[round(s0 * SR):round(s0 * SR) + n].copy()
        f = int(0.012 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        dlg[o:o + len(a)] += a; speech[o:o + len(a)] = 1
    elif x.get("amb") is not None:
        a = load(x["clip"])[round(x["s"] * SR):round(x["s"] * SR) + n].copy()
        if x["kind"].startswith("split"):
            b = load(x["kind"].split(":")[1])[round(x["s"] * SR):round(x["s"] * SR) + n]; m = min(len(a), len(b)); a = 0.5 * (a[:m] + b[:m])
        f = int(0.06 * SR); a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
        amb[o:o + len(a)] += a * db(x["amb"])
dlg = hp(dlg, 80); amb = hp(amb, 120)

# ---------------------------------------------------------------- SFX sentezi
def env_ad(n, a, d):
    e = np.ones(n, np.float32); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def pop():
    n = int(0.12 * SR); t = np.arange(n) / SR; f = 900 * np.exp(-t * 18) + 350
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.03)).astype(np.float32)
def whoosh(dur=0.45, up=True):
    n = int(dur * SR); noise = rng.standard_normal(n).astype(np.float32); out = np.zeros(n, np.float32); hop = 480
    for k in range(0, n, hop):
        p = k / n; fc = (400 + 3200 * p) if up else (3600 - 3200 * p); r = 0.97; th = 2 * np.pi * fc / SR
        seg = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], noise[max(0, k - 2000):k + hop]); out[k:k + hop] = seg[-len(out[k:k + hop]):]
    out *= np.sin(np.pi * np.linspace(0, 1, n)) ** 2; return (out / (np.abs(out).max() + 1e-9)).astype(np.float32)
def shimmer(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n, np.float32)
    for k, f in enumerate([1318.5, 1568, 1975.5, 2637]):
        st = int(k * 0.07 * SR); m = n - st; y[st:] += np.sin(2 * np.pi * f * t[:m]) * env_ad(m, 0.004, 0.25) * 0.5
    return y / np.abs(y).max()
def tick():
    n = int(0.04 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2400 * t) * env_ad(n, 0.001, 0.006)).astype(np.float32)
def shutter():
    """Fotograf makinesi deklansoru: iki mekanik tik + kisa gurultu."""
    n = int(0.16 * SR); y = np.zeros(n, np.float32)
    for st, g in ((0, 1.0), (0.075, 0.7)):
        o = int(st * SR); m = int(0.03 * SR); b = rng.standard_normal(m) * env_ad(m, 0.0005, 0.006)
        y[o:o + m] += lfilter([1, -0.6], [1], b).astype(np.float32) * g
    return y / np.abs(y).max()

sfx = np.zeros(NS, np.float32)
def put(sig, t, g):
    o = int(t * SR)
    if o < 0 or o >= NS: return
    n = min(len(sig), NS - o); sfx[o:o + n] += sig[:n] * db(g)
import render                                  # rozet zamanlari (yerlesimde kaydirilmis olabilir)
render.plan()
for kind, t0, t1, c in render.EVENTS:
    put(shimmer() if kind == "title" else pop(), t0 - 0.02, -20 if kind == "title" else -19)
for x in TL:
    tr = x.get("tr")
    if tr == "whip": put(whoosh(0.42, True), x["t0"] - 0.24, -20)
    if tr == "flash": put(tick(), x["t0"], -20)
    if x["kind"].startswith("split"):
        put(whoosh(0.4, True), x["t0"] - 0.2, -23); put(tick(), x["t0"] + 0.27, -22); put(tick(), x["t0"] + 0.33, -22)
    if x["kind"] == "foto":
        cards, _ = render.photo_cards(); step = (x["t1"] - x["t0"]) / len(cards)
        for k in range(len(cards)): put(shutter(), x["t0"] + k * step, -16)

# ---------------------------------------------------------------- muzik (kodla bestelenmis, music.py)
mus = np.zeros(NS, np.float32)
if MUSIC:
    w = wave.open("work/music_only.wav"); m = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    m = m[:NS]; mus[:len(m)] = m
    duck = 1 - 0.72 * np.clip(uniform_filter1d(speech, int(0.35 * SR)), 0, 1)     # konusma altinda ~ -11 dB
    mus *= duck * db(-13)

mix = dlg + amb + sfx + mus
st = np.stack([mix, mix], 1)
def wr(p, x):
    x = x if x.ndim > 1 else x[:, None]
    w = wave.open(p, "wb"); w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
out = "work/mix_pre.wav" if MUSIC else "work/mix_pre_nomusic.wav"
wr(out, st / max(1.0, np.abs(st).max() / 0.98))
print(out, "sure", round(DUR, 2), "tepe", round(float(np.abs(mix).max()), 3))
