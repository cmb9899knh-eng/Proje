"""Kodla bestelenmis, telifsiz 'Mardin havasi' (Hicaz makami). Tum sesler numpy ile sentezlenir.
ud ~ Karplus-Strong telli, ney ~ vibratolu nefesli sinus, darbuka ~ dum/tek/ka, dem ~ Re-La.
Cikti: work/music_only.wav (48 kHz mono, normalize edilmemis)."""
import numpy as np, wave
from scipy.signal import lfilter
from edl import timeline
SR = 48000; TL = timeline(); DUR = TL[-1]["t1"]; NS = int(DUR * SR) + SR
rng = np.random.default_rng(11)
BPM = 98; B = 60 / BPM; E = B / 2            # sekizlik
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# Hicaz (Re): D Eb F# G A Bb C D  -> MIDI 62 63 66 67 69 70 72 74
HIC = [62, 63, 66, 67, 69, 70, 72, 74, 75, 78, 79, 81]

def ud(f, dur, amp=0.35, bright=0.5):
    n = int(dur * SR); N = max(2, int(SR / f)); buf = rng.uniform(-1, 1, N) * amp
    buf = lfilter([bright, 1 - bright], [1], buf)          # parlaklik
    out = np.zeros(n, np.float32); idx = 0
    for i in range(n):
        out[i] = buf[idx]; nxt = (idx + 1) % N
        buf[idx] = 0.4985 * (buf[idx] + buf[nxt]); idx = nxt
    return out
_cache = {}
def ud_c(f, dur, amp):
    k = (round(f, 2), round(dur, 3), amp)
    if k not in _cache: _cache[k] = ud(f, dur, amp)
    return _cache[k]
def ney(f, dur, amp=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip(t / 0.4, 0, 1)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    br = lfilter([0.02], [1, -0.98], rng.standard_normal(n)) * 0.6
    env = np.clip(t / 0.18, 0, 1) * np.clip((dur - t) / 0.25, 0, 1)
    return ((tone + br) * env * amp).astype(np.float32)
def dum(a=0.9):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 70 + 80 * np.exp(-t * 25); s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    return (a * (s + 0.15 * rng.standard_normal(n) * np.exp(-t * 60))).astype(np.float32)
def tek(a=0.5, dec=45):
    n = int(0.12 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n)
    th = 2 * np.pi * 3800 / SR; r = 0.9
    y = lfilter([1 - r], [1, -2 * r * np.cos(th), r * r], x) * 4
    return (a * (y * np.exp(-t * dec) + 0.4 * np.sin(2 * np.pi * 620 * t) * np.exp(-t * 40))).astype(np.float32)
def drone(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = 0.5 * np.sin(2 * np.pi * hz(38) * t) + 0.35 * np.sin(2 * np.pi * hz(45) * t) + 0.12 * np.sin(2 * np.pi * hz(50) * t + 1)
    return (s * 0.10 * (0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t))).astype(np.float32)

mus = np.zeros(NS, np.float32); drums = np.zeros(NS, np.float32)
def put(buf, sig, t, g=1.0):
    o = int(t * SR)
    if o >= NS: return
    n = min(len(sig), NS - o); buf[o:o + n] += sig[:n] * g

def sec_t(name): return next(x["t0"] for x in TL if x.get("sec") == name)
T_RHY = sec_t("ANTİK KENT") - 0.02          # ritim girer (whip ile)
T_COF0 = next(x["t0"] for x in TL if x["clip"] == "3165_a5bb"); T_COF1 = next(x["t1"] for x in TL if x["clip"] == "3234")
T_FIN = sec_t("MEZOPOTAMYA") - 0.02        # finale: ritim cekilir, ney + ud

# --- dem: tum parca
put(mus, drone(DUR + 1), 0, 1.0)
# --- ney: acilis ve final melodileri (Hicaz seyir: A-Bb-A-G-F#-Eb-D)
def ney_phrase(t0, notes):
    t = t0
    for m, d in notes: put(mus, ney(hz(m), d * B), t); t += d * B
ney_phrase(0.05, [(69, 1.5), (70, 0.5), (69, 1), (67, 0.5), (66, 0.5), (63, 1), (62, 2.0)])
ney_phrase(T_FIN + 0.1, [(74, 1), (75, 0.5), (74, 0.5), (72, 1), (70, 1), (69, 2), (67, 0.5), (66, 0.5), (63, 1), (62, 3)])
ney_phrase(T_FIN + 0.1 + 11.5 * B, [(69, 1), (70, 0.5), (69, 0.5), (66, 1), (63, 1), (62, 4)])
# --- ritim bolumu: darbuka (duyek benzeri 8/8) + ud ostinato
PAT = ["D", ".", "t", "D", "T", ".", "t", "k"]
riff = [62, 63, 66, 67, 69, 67, 66, 63, 62, 63, 66, 63, 62, 60, 62, 0]     # 2 olcu, 0 = es
t = T_RHY; k = 0
while t < T_FIN:
    hot = T_COF0 - 0.3 <= t <= T_COF1          # kahve montaji: daha dolu
    p = PAT[k % 8]
    if p == "D": put(drums, dum(), t)
    elif p == "T": put(drums, tek(0.55), t)
    elif p == "t": put(drums, tek(0.32), t)
    elif p == "k": put(drums, tek(0.22, 70), t)
    if hot and p == ".": put(drums, tek(0.18, 80), t)
    m = riff[k % 16]
    if m: put(mus, ud_c(hz(m), 0.9, 0.30 if not hot else 0.36), t, 0.9)
    if k % 16 == 0: put(mus, ud_c(hz(50), 1.6, 0.35), t, 0.7)     # bas teli
    t += E; k += 1
# finalde ud: seyrek akorlar
t = T_FIN; k = 0
while t < DUR - 1:
    if k % 4 == 0: put(mus, ud_c(hz([62, 58, 60, 62][(k // 4) % 4] - 12), 2.4, 0.32), t, 0.8)
    if k % 2 == 1: put(mus, ud_c(hz([69, 67, 66, 63][(k // 2) % 4]), 1.2, 0.22), t, 0.7)
    t += B; k += 1
mix = mus + 0.9 * drums
# giris/cikis
fi = int(0.4 * SR); mix[:fi] *= np.linspace(0, 1, fi)
end = int((DUR - 1.4) * SR); fo = int(1.4 * SR); mix[end:end + fo] *= np.linspace(1, 0, fo); mix[end + fo:] = 0
mix = mix[:int(DUR * SR)]
mix /= np.abs(mix).max() + 1e-9
w = wave.open("work/music_only.wav", "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 0.9 * 32767).astype(np.int16).tobytes()); w.close()
print("muzik:", round(DUR, 2), "sn; ritim", round(T_RHY, 2), "-", round(T_FIN, 2), "; kahve", round(T_COF0, 2), "-", round(T_COF1, 2))
