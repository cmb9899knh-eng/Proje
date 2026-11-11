"""Muzik altligi + ses efektleri (tamami numpy ile sentez, harici/telifli ses yok) + miks + -14 LUFS.
Kullanim: python3 audio_mix.py <work>    (girdi: build/voice.wav, build/dialog_mask.npy; cikti: build/mix.wav)"""
import sys, os, wave, numpy as np, pyloudnorm as pyln
from scipy.signal import butter, sosfilt, resample_poly
sys.argv += ["x"] if len(sys.argv) < 3 else []
WORK = sys.argv[1]
sys.argv = [sys.argv[0], WORK, "x"]
from edl import TOTAL, FPS
from overlay import SFX
SR = 48000; N = int(TOTAL / FPS * SR)
rng = np.random.default_rng(11)
def rd(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64) / 32768
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def mtof(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- muzik: 96 BPM, La minor, sicak / sakin "seyahat" altligi ----------------
BPM = 96; beat = 60 / BPM; bar = 4 * beat
# akorlar (MIDI): Am9, Fmaj7, Cmaj7, G6  -> her biri 1 olcu
CHORDS = [[57, 60, 64, 67, 71], [53, 57, 60, 64, 69], [48, 55, 59, 64, 67], [55, 59, 62, 64, 67]]
BASS = [45, 41, 48, 43]
music = np.zeros((N + SR, 2))
def add(buf, sig, t, pan=0.0, g=1.0):
    i = int(t * SR); L = min(len(sig), len(buf) - i)
    if L <= 0: return
    buf[i:i + L, 0] += sig[:L] * g * np.sqrt(0.5 * (1 - pan)); buf[i:i + L, 1] += sig[:L] * g * np.sqrt(0.5 * (1 + pan))
def pad_note(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * (1 + dt) * t + p) for dt, p in ((0, 0), (0.004, 1.3), (-0.0035, 2.1)))
    y += 0.25 * sum(np.sin(2 * np.pi * 2 * f * (1 + dt) * t) for dt in (0.002, -0.002))
    a = np.minimum(1, t / 0.6) * np.minimum(1, (d - t) / 0.5)
    return lp(y * a, 1800) / 3
def pluck(f, d=1.2):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * env_exp(n, 0.15) + 0.12 * np.sin(2 * np.pi * 3 * f * t) * env_exp(n, 0.06)
    return y * env_exp(n, 0.35) * np.minimum(1, np.arange(n) / 60)
def kick():
    n = int(0.35 * SR); t = np.arange(n) / SR; f = 50 + 70 * np.exp(-t / 0.03)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.09)
def shaker():
    n = int(0.09 * SR); return hp(rng.standard_normal(n), 6000) * env_exp(n, 0.018) * np.minimum(1, np.arange(n) / 200)
def bass_note(f, d):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(2 * np.pi * 2 * f * t)
    return y * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.08) * (0.6 + 0.4 * env_exp(n, 0.5))
ARP = [0, 2, 1, 3, 4, 3, 2, 1]
nbars = int(np.ceil(TOTAL / FPS / bar)) + 1
for b in range(nbars):
    t0 = b * bar; ch = CHORDS[b % 4]
    add(music, pad_note(0, 1) if False else sum(pad_note(mtof(m), bar + 0.4) for m in ch[:4]), t0, 0, 0.09)
    add(music, bass_note(mtof(BASS[b % 4]), bar * 0.95), t0, 0, 0.28)
    if b >= 1:  # giristen sonra ritim
        for k in range(4):
            if k in (0, 2): add(music, kick(), t0 + k * beat, 0, 0.45)
            add(music, shaker(), t0 + k * beat + beat / 2, 0.3, 0.10)
    for k in range(8):  # sekizlik arpej
        m = ch[ARP[k]] + 12; add(music, pluck(mtof(m)), t0 + k * beat / 2, -0.35 + 0.1 * (k % 3), 0.07)
music = music[:N]
fade = np.ones(N); fl = int(1.2 * SR); fade[-fl:] = np.linspace(1, 0, fl) ** 1.5; fade[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
music *= fade[:, None]

# ---------------- ses efektleri (sentez) ----------------
def pop(f0=820, f1=300, d=0.08):
    n = int(d * SR); t = np.arange(n) / SR; f = f0 * (f1 / f0) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_exp(n, 0.02) * np.minimum(1, np.arange(n) / 48)
def tick(): return pop(1500, 900, 0.035) * 0.8
def whoosh(d=0.45, up=True):
    n = int(d * SR); x = rng.standard_normal(n); p = np.linspace(0, 1, n)
    lo, hi = lp(x, 900), bp(x, 1500, 7000)
    y = lo * (1 - p) + hi * p if up else lo * p + hi * (1 - p)
    return y / (np.abs(y).max() + 1e-9) * np.sin(np.pi * p) ** 2
def ding(f=1318.5, d=1.0):
    n = int(d * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * 2 * f * t) * env_exp(n, 0.12) + 0.2 * np.sin(2 * np.pi * 3.01 * f * t) * env_exp(n, 0.06)
    return y * env_exp(n, 0.3) * np.minimum(1, np.arange(n) / 96)
sfx = np.zeros((N + SR, 2))
for kind, t in SFX:
    if kind == "pop": add(sfx, pop(), t, 0, 10 ** (-15 / 20))
    elif kind == "tick": add(sfx, tick(), t, 0, 10 ** (-21 / 20))
    elif kind == "whoosh": w = whoosh(); add(sfx, w, t - len(w) / SR * 0.6, -0.2, 10 ** (-17 / 20))
    elif kind == "swish": w = whoosh(0.3, False); add(sfx, w, t - 0.15, 0.2, 10 ** (-19 / 20))
    elif kind == "ding": add(sfx, ding(), t, 0, 10 ** (-20 / 20)); add(sfx, ding(1975.5), t + 0.08, 0, 10 ** (-27 / 20))
sfx = sfx[:N]

# ---------------- miks ----------------
voice = rd(os.path.join(WORK, "build", "voice.wav"))[:N]; voice = np.pad(voice, (0, N - len(voice)))
voice = hp(voice, 80)
mask = np.load(os.path.join(WORK, "build", "dialog_mask.npy"))[:N]; mask = np.pad(mask, (0, N - len(mask)))
meter = pyln.Meter(SR)
# diyalogu ~-16 LUFS'e getir (yalniz dialog bolgelerinde olcum)
dl = meter.integrated_loudness(voice[mask > 0]); vg = 10 ** ((-16 - dl) / 20); voice *= vg
# muzik: b-roll'da -20 LUFS civari, konusma altinda 11 dB kisilir (yumusak atak/birakma)
ml = meter.integrated_loudness(music); music *= 10 ** ((-20 - ml) / 20)
duck = np.convolve(mask, np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
duck = 10 ** (-11 * np.clip(duck * 1.6, 0, 1) / 20)
music *= duck[:, None]
mix = music + sfx + voice[:, None]
# -14 LUFS hedefi + true-peak limitor (4x asiri ornekleme, -1.5 dBTP)
def true_peak(x): return np.abs(resample_poly(x, 4, 1, axis=0)).max()
for _ in range(4):
    L = meter.integrated_loudness(mix); mix *= 10 ** ((-14 - L) / 20)
    ceil = 10 ** (-1.5 / 20); a = np.abs(mix).max(1)
    g = np.minimum(1, ceil / np.maximum(a, 1e-9))
    win = int(0.004 * SR); g = -np.convolve(-np.pad(g, (win, win), constant_values=1), np.ones(2 * win + 1), "valid") if False else g
    # basit ileri-bakisli limitor: kazanc zarfini 5 ms min-filtre + 30 ms birakma ile yumusat
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    g = uniform_filter1d(minimum_filter1d(g, int(0.005 * SR)), int(0.003 * SR))
    mix *= g[:, None] * 0.995
L = meter.integrated_loudness(mix); tp = 20 * np.log10(true_peak(mix))
w = wave.open(os.path.join(WORK, "build", "mix.wav"), "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print(f"miks: entegre {L:.2f} LUFS, true-peak {tp:.2f} dBTP, diyalog kazanci {20*np.log10(vg):+.1f} dB, sure {N/SR:.2f} sn")
