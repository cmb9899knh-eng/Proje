"""Tanitim muzigi + gecis efektleri (tamami numpy sentezi; sample/loop/telifli ses YOK) + miks + -14 LUFS.
Kullanim: python3 promo_audio.py <work> [vo.wav]
  vo.wav verilirse dis ses eklenir ve muzik konusma altinda kisilir (ducking).
Cikti: <work>/build2/promo_mix.wav"""
import sys, os, wave, math, numpy as np, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly
from scipy.ndimage import minimum_filter1d, uniform_filter1d
WORK = sys.argv[1]; VOP = sys.argv[2] if len(sys.argv) > 2 else None
sys.argv = [sys.argv[0], WORK, "x"]
import promo
SR = 48000; DUR = promo.TOTAL / promo.FPS; N = int(DUR * SR)
BPM = promo.BPM; BEAT = 60 / BPM; BAR = 4 * BEAT
rng = np.random.default_rng(5)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def ex(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def mtof(m): return 440 * 2 ** ((m - 69) / 12)
OUT = {k: np.zeros((N + 4 * SR, 2)) for k in ("pad", "oud", "bass", "perc", "fx")}
def add(bus, sig, t, pan=0.0, g=1.0):
    i = int(t * SR)
    if i < 0: sig = sig[-i:]; i = 0
    L = min(len(sig), len(OUT[bus]) - i)
    if L <= 0: return
    OUT[bus][i:i + L, 0] += sig[:L] * g * math.sqrt(0.5 * (1 - pan)); OUT[bus][i:i + L, 1] += sig[:L] * g * math.sqrt(0.5 * (1 + pan))

# ---- enstrumanlar ------------------------------------------------------------------------
def oud(f, d=1.4, bright=0.5):  # Karplus-Strong tel (ud benzeri), hafif govde rezonansi
    P = max(2, int(round(SR / f))); n = int(d * SR)
    y = np.zeros(n + P); y[:P] = lp(rng.uniform(-1, 1, P), 2500 + 3000 * bright)
    dec = 0.992 if f < 300 else 0.986  # kisa, 'tirnakli' tel sonumu
    for s in range(P, n + P, P):
        prev = y[s - P:s]; y[s:s + P] = (dec * 0.5 * (prev + np.r_[prev[-1], prev[:-1]]))[:len(y[s:s + P])]
    y = y[P:n + P]; y = y + 0.35 * bp(y, 180, 420)
    return y * np.minimum(1, np.arange(n) / 30) / (np.abs(y).max() + 1e-9)
def pad(freqs, d):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0, 0.005):
            ph = rng.uniform(0, 6.28); y += np.sin(2 * np.pi * f * (1 + det) * t + ph) + 0.3 * np.sin(4 * np.pi * f * (1 + det) * t + ph)
    a = np.minimum(1, t / 0.9) * np.minimum(1, (d - t) / 0.7)
    return lp(y * a, 1600) / (3 * len(freqs))
def bass(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.tanh(1.6 * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)))
    return lp(y, 900) * np.minimum(1, t / 0.01) * np.minimum(1, (d - t) / 0.06) * (0.55 + 0.45 * ex(n, 0.6))
def doum():  # darbuka "dum" benzeri
    n = int(0.45 * SR); t = np.arange(n) / SR; f = 75 + 95 * np.exp(-t / 0.035)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * ex(n, 0.13) + 0.15 * lp(rng.standard_normal(n), 400) * ex(n, 0.02)
def tek(acc=1.0):  # darbuka "tek" benzeri
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (0.6 * bp(rng.standard_normal(n), 1800, 6500) * ex(n, 0.012) + 0.5 * np.sin(2 * np.pi * 690 * t) * ex(n, 0.03)) * acc
def shaker():
    n = int(0.08 * SR); return hp(rng.standard_normal(n), 7000) * ex(n, 0.016) * np.minimum(1, np.arange(n) / 150)
def kick():
    n = int(0.4 * SR); t = np.arange(n) / SR; f = 45 + 80 * np.exp(-t / 0.028)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * ex(n, 0.11)

# ---- duzenleme (bolumlere gore enerji) ----------------------------------------------------
SEC = {s["id"]: (s["f0"] / promo.FPS, (s["f0"] + s["n"]) / promo.FPS) for s in promo.SECS}
def energy(t):
    for sid, (a, b) in SEC.items():
        if a <= t < b:
            return {"intro": 0, "hook": 1, "giris": 2, "karsilama": 1, "mimari": 2, "oda": 2, "banyo": 1.5, "somine": 1, "teras": 3,
                    "kahvalti": 3, "davet": 2, "adres": 1, "kapanis": 1, "son": 0}[sid]
    return 0
CH = [[50, 53, 57, 62], [55, 58, 62, 67], [46, 50, 53, 58], [45, 49, 52, 57]]   # Dm Gm Bb A (Re armonik minor / hicaz rengi)
BS = [38, 43, 34, 33]
# ud motifi (8'lik nota, Re armonik minor: Re Mi Fa Sol La Sib Do#), olcu basina
MOT = [[74, 73, 74, 76, 77, 76, 74, 73], [74, 79, 77, 76, 74, None, 70, 69],
       [70, 69, 70, 72, 74, 72, 70, 69], [69, 70, 73, 76, 74, 73, 70, 69]]
nb = int(math.ceil(DUR / BAR)) + 1
for b in range(nb):
    t0 = b * BAR; e = energy(t0 + 0.01); ch = CH[b % 4]
    add("pad", pad([mtof(m) for m in ch], BAR + 0.6), t0, 0, 1.0)
    if e >= 1: add("bass", bass(mtof(BS[b % 4]), BAR * 0.96), t0, 0, 0.55)
    for k in range(8):
        tt = t0 + k * BEAT / 2; e = energy(tt + 0.01); m = MOT[b % 4][k]
        if m is not None and (e >= 1 or k % 2 == 0):
            add("oud", oud(mtof(m - (12 if e == 0 else 0)), 1.3, 0.35 + 0.15 * e), tt, -0.25 + 0.12 * (k % 3), 0.5 if e else 0.4)
        if e >= 2:   # maksum benzeri: D T . T D . T .
            if k in (0, 4): add("perc", doum(), tt, 0, 0.9)
            if k in (1, 3, 6): add("perc", tek(0.9 if k != 3 else 0.6), tt, 0.25, 0.55)
            add("perc", shaker(), tt + BEAT / 4, 0.35, 0.12)
        elif e >= 1 and k in (0, 4): add("perc", doum(), tt, 0, 0.55)
        if e >= 3 and k in (0, 4): add("perc", kick(), tt, 0, 0.5)

# ---- gecis efektleri (goruntudeki gecislere senkron) ---------------------------------------
def whoosh(d=0.5):
    n = int(d * SR); x = rng.standard_normal(n); p = np.linspace(0, 1, n)
    y = lp(x, 700) * (1 - p) + bp(x, 1200, 6500) * p
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * p) ** 2
def riser(d=0.6):
    n = int(d * SR); t = np.arange(n) / SR; p = t / d
    y = bp(rng.standard_normal(n), 800, 7000) * p ** 2 + 0.3 * np.sin(2 * np.pi * np.cumsum(300 + 1500 * p ** 2) / SR) * p ** 2
    return y / (np.abs(y).max() + 1e-9)
def impact():
    n = int(0.9 * SR); t = np.arange(n) / SR; f = 40 + 60 * np.exp(-t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * ex(n, 0.25) + 0.25 * lp(rng.standard_normal(n), 1200) * ex(n, 0.06)
def shimmer(d=1.0):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f in (1760, 2217, 2637, 3520): y += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * ex(n, 0.35) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t))
    return y / 4 * np.minimum(1, t / 0.05)
for i, s in enumerate(promo.SHOTS[:-1]):
    tb = (s["f0"] + s["n"]) / promo.FPS
    if s["trans"] in ("whipL", "whipR"): w = whoosh(); add("fx", w, tb - len(w) / SR / 2, -0.5 if s["trans"] == "whipL" else 0.5, 0.35)
    elif s["trans"] == "zoom": r = riser(); add("fx", r, tb - len(r) / SR, 0, 0.22); add("fx", impact(), tb, 0, 0.45)
    elif s["trans"] == "flash": add("fx", shimmer(), tb - 0.1, 0, 0.25)
add("fx", impact(), SEC["hook"][0] + 0.15, 0, 0.5)            # baslik karti
add("fx", shimmer(1.6), SEC["son"][0] + 0.2, 0, 0.22)          # kapanis karti

# ---- miks --------------------------------------------------------------------------------
bus = {k: v[:N] for k, v in OUT.items()}
music = 0.6 * bus["pad"] + 0.42 * bus["oud"] + 0.55 * bus["bass"] + 0.85 * bus["perc"]
music = hp(music.T, 35).T
fl = int(2.0 * SR); fade = np.ones(N); fade[-fl:] = np.linspace(1, 0, fl) ** 1.6; music *= fade[:, None]
meter = pyln.Meter(SR)
music *= 10 ** ((-16 - meter.integrated_loudness(music)) / 20)
fx = bus["fx"]; fx *= 10 ** ((-22 - meter.integrated_loudness(fx + 1e-9 * rng.standard_normal(fx.shape))) / 20)
mix = music + fx
if VOP:
    w = wave.open(VOP); v = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
    if w.getnchannels() == 2: v = v.reshape(-1, 2).mean(1)
    if w.getframerate() != SR: v = resample_poly(v, SR, w.getframerate())
    v = np.pad(v, (0, max(0, N - len(v))))[:N]
    v *= 10 ** ((-15 - meter.integrated_loudness(v[np.abs(v) > 1e-4])) / 20)
    env = uniform_filter1d((np.abs(v) > 0.01).astype(float), int(0.3 * SR))
    duck = 10 ** (-9 * np.clip(env * 2, 0, 1) / 20)
    mix = music * duck[:, None] + fx + v[:, None]
def tp(x): return np.abs(resample_poly(x, 4, 1, axis=0)).max()
for _ in range(4):
    mix *= 10 ** ((-14 - meter.integrated_loudness(mix)) / 20)
    g = np.minimum(1, 10 ** (-1.5 / 20) / np.maximum(np.abs(mix).max(1), 1e-9))
    g = uniform_filter1d(minimum_filter1d(g, int(0.005 * SR)), int(0.003 * SR)); mix *= g[:, None] * 0.995
os.makedirs(os.path.join(WORK, "build2"), exist_ok=True)
outp = os.path.join(WORK, "build2", "promo_mix.wav")
wv = wave.open(outp, "wb"); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
print(f"{outp}: {meter.integrated_loudness(mix):.2f} LUFS, true-peak {20*math.log10(tp(mix)):.2f} dBTP, {DUR:.2f} sn, VO={'var' if VOP else 'YOK (yer tutucu)'}")
