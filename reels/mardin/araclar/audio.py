"""Muzik (Hicaz makaminda ozgun, tamamen kodla sentez), ses efektleri (sentez) ve miks.
Telifli ses kullanilmaz. Cikti: <work>/music.wav, sfx.wav, mix.wav (-14 LUFS, <= -1.5 dBTP)."""
import sys, wave, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt, resample_poly
import pyloudnorm as pyln
from edl import timeline
WORK = sys.argv[1]; SR = 48000
tl, T = timeline(); N = int(T * SR)
rng = np.random.default_rng(11)
SPEECH0 = [r for r in tl if r[5]][0][0]; SPEECH1 = [r for r in tl if r[5]][-1][1]   # 8.5 .. 24.347
OUTRO = SPEECH1

def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else x
def wr(p, x):
    x = np.atleast_2d(x.T).T if x.ndim == 1 else x
    w = wave.open(p, "wb"); w.setnchannels(x.shape[1] if x.ndim > 1 else 1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

# ---------- Hicaz (Re karar) ----------
def hz(n): return 440 * 2 ** ((n - 69) / 12)
C = {"D3": 50, "A2": 45, "D2": 38, "A3": 57, "D4": 62, "Eb4": 63, "F#4": 66, "G4": 67, "A4": 69, "Bb4": 70, "C5": 72, "D5": 74, "G3": 55, "F#3": 54, "Eb3": 51}
CENT = {"Eb4": 12, "Eb3": 12, "F#4": -12, "F#3": -12}   # Hicaz rengi: 2. derece biraz tiz, 3. derece biraz pes
def f(name): return hz(C[name]) * 2 ** (CENT.get(name, 0) / 1200)

def ud(freq, dur, vel=1.0, bright=0.5):
    """Karplus-Strong ile mizrapli tel (cift tel, hafif akortsuzluk)."""
    n = int(dur * SR); out = np.zeros(n)
    for det in (1.0, 1.0035):
        L = int(SR / (freq * det)); buf = rng.uniform(-1, 1, L)
        buf = np.convolve(buf, [bright, 1 - bright], "same"); y = np.zeros(n + L); y[:L] = buf
        for k in range(1, (n + L) // L + 1):
            s, e = k * L, min((k + 1) * L, n + L)
            if s >= n + L: break
            prev = y[s - L:e - L]; prev2 = np.concatenate([[y[s - L - 1] if s - L - 1 >= 0 else 0], prev[:-1]])
            y[s:e] = 0.996 * 0.5 * (prev + prev2)
        out += y[L:L + n]
    att = np.minimum(1, np.arange(n) / 30); rel = np.minimum(1, (n - np.arange(n)) / (0.04 * SR))
    body = sosfilt(butter(2, [180, 3800], "band", fs=SR, output="sos"), out)
    return (0.6 * body + 0.4 * out) * att * rel * vel * 0.5

def ney(notes, gain=1.0):
    """Ney benzeri: yumusak sinus + harmonikler + nefes gurultusu, vibrato, notalar arasi kayma."""
    end = max(t1 for _, t0, t1 in notes); n = int(end * SR) + SR; fr = np.zeros(n); amp = np.zeros(n)
    for name, t0, t1 in notes:
        i0, i1 = int(t0 * SR), int(t1 * SR); fr[i0:i1] = f(name)
        a = np.ones(i1 - i0); at = int(min(0.12, (t1 - t0) / 3) * SR); a[:at] = np.linspace(0.2, 1, at) ** 1.5
        rl = int(min(0.10, (t1 - t0) / 3) * SR); a[-rl:] *= np.linspace(1, 0.55, rl); amp[i0:i1] = a
    # kayma (portamento) ve vibrato
    k = int(0.05 * SR); fr = np.where(fr == 0, np.nan, fr)
    idx = np.where(~np.isnan(fr), np.arange(n), 0); np.maximum.accumulate(idx, out=idx); fr = np.nan_to_num(fr[idx], nan=f("D4"))
    fr = np.convolve(fr, np.ones(k) / k, "same")
    t = np.arange(n) / SR; vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t % 1.3) / 0.6, 0, 1)
    ph = 2 * np.pi * np.cumsum(fr * vib) / SR
    tone = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.07 * np.sin(3 * ph)
    breath = sosfilt(butter(2, [900, 4500], "band", fs=SR, output="sos"), rng.standard_normal(n)) * 0.22
    amp = np.convolve(amp, np.ones(480) / 480, "same")
    return (tone + breath) * amp * 0.28 * gain

def drone(dur, gain=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for fq, g in ((f("D2"), 1), (f("A2"), 0.6), (f("D3"), 0.45)):
        for h in range(1, 9): y += g / h * np.sin(2 * np.pi * fq * h * t * (1 + 0.0007 * h) + h)
    y = sosfilt(butter(2, 1400, fs=SR, output="sos"), y) * (1 + 0.15 * np.sin(2 * np.pi * 0.21 * t))
    return y / np.abs(y).max() * 0.16 * gain

def dum(vel=1.0):
    n = int(0.55 * SR); t = np.arange(n) / SR
    fq = 62 + 70 * np.exp(-t / 0.03); y = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.20)
    y += sosfilt(butter(2, 900, fs=SR, output="sos"), rng.standard_normal(n)) * np.exp(-t / 0.012) * 0.5
    return y * vel * 0.9
def tek(vel=1.0, ka=False):
    n = int(0.22 * SR); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [2200, 7500] if not ka else [1200, 4500], "band", fs=SR, output="sos"), rng.standard_normal(n))
    ring = np.sin(2 * np.pi * (640 if not ka else 480) * t) * 0.6
    return (nz * np.exp(-t / 0.018) + ring * np.exp(-t / 0.05)) * vel * (0.55 if not ka else 0.35)

def reverb(x, sec=1.8, wet=0.25):
    n = int(sec * SR); t = np.arange(n) / SR
    out = []
    for s in (1, 2):
        ir = np.random.default_rng(s).standard_normal(n) * np.exp(-t / (sec / 6.9)); ir[:int(0.012 * SR)] = 0
        ir = sosfilt(butter(1, 5000, fs=SR, output="sos"), ir); ir /= np.sqrt((ir ** 2).sum())
        out.append(fftconvolve(x, ir)[:len(x)])
    return np.stack([x + wet * out[0], x + wet * out[1]], 1)

def place(buf, sig, at, pan=0.0):
    i = int(at * SR)
    if i >= len(buf): return
    s = sig[:len(buf) - i]
    if buf.ndim == 1: buf[i:i + len(s)] += s
    else:
        buf[i:i + len(s), 0] += s * np.sqrt(0.5 * (1 - pan)) * 1.414; buf[i:i + len(s), 1] += s * np.sqrt(0.5 * (1 + pan)) * 1.414

def music():
    dry = np.zeros((N + SR, 2)); perc = np.zeros((N + SR, 2)); BEAT = 0.5
    # I: 0-4 ney taksim + drone + kudum vurusu
    place(dry, drone(T + 0.5), 0.0)
    place(dry, ney([("A4", .15, 1.15), ("Bb4", 1.15, 1.45), ("A4", 1.45, 1.75), ("G4", 1.75, 2.05), ("F#4", 2.05, 2.6), ("Eb4", 2.6, 2.95), ("D4", 2.95, 3.95)]), 0.0, -0.1)
    for at in (0.0, 2.0): place(perc, dum(0.9), at)
    place(perc, dum(0.6), 3.5); place(perc, dum(0.8), 3.75)
    # Maksum ritmi (8'lik): DUM tek . tek DUM . tek .
    def maqsum(t0, bars, vel=1.0, fills=True):
        for b in range(bars):
            s = t0 + b * 4 * BEAT
            for (o, kind) in ((0, "D"), (0.5, "T"), (1.5, "T"), (2.0, "D"), (3.0, "T")):
                if kind == "D": place(perc, dum(vel), s + o * BEAT)
                else: place(perc, tek(vel * 0.8), s + o * BEAT, 0.25)
            if fills:
                for o in (1.0, 2.5, 3.5, 3.75): place(perc, tek(vel * 0.45, ka=True), s + o * BEAT, -0.25)
    # II: 4.0-8.5 tam ritim + ud riff
    maqsum(4.0, 2); place(perc, dum(1.0), 8.0); place(perc, tek(0.7), 8.25)
    riff = ["D4", "Eb4", "F#4", "G4", "A4", "G4", "F#4", "Eb4", "D4", None, "D4", "Eb4", "F#4", None, "Eb4", "D4"]
    for r in range(2):
        for i, nm in enumerate(riff):
            if nm: place(dry, ud(f(nm), 0.6, 0.9 if i % 4 == 0 else 0.7), 4.0 + r * 2.0 + i * 0.25, 0.2)
    for i in range(4): place(dry, ud(f("A3"), 0.3, 0.6), 8.0 + i * 0.125, 0.2)   # tremolo, konusmaya gecis
    # III: 8.5-OUTRO konusma alti: hafif tek + seyrek ud
    t = 8.5
    while t < OUTRO - 0.6:
        place(perc, tek(0.35), t + 0.5 * BEAT, 0.3); place(perc, dum(0.45), t)
        place(dry, ud(f("D3"), 1.6, 0.45, 0.35), t, 0.15); t += 4 * BEAT
    # IV: OUTRO - son: ud ezgisi + ney + tam ritim
    mel = ["A4", "Bb4", "A4", "G4", "F#4", "G4", "A4", None, "G4", "F#4", "Eb4", "F#4", "D4", None, None, None,
           "A4", "Bb4", "C5", "Bb4", "A4", "G4", "F#4", "G4", "F#4", "Eb4", "D4", None]
    for i, nm in enumerate(mel):
        if nm: place(dry, ud(f(nm), 0.7, 0.85 if i % 2 == 0 else 0.7), OUTRO + i * 0.2, 0.2)
    place(dry, ney([("D5", .0, 1.6), ("C5", 1.6, 2.0), ("Bb4", 2.0, 2.4), ("A4", 2.4, 3.6)], 0.6), OUTRO + 0.4, -0.2)
    maqsum(OUTRO, 2)
    END = OUTRO + 4 * 4 * BEAT * 0 + 2 * 4 * BEAT + 1.5  # son vurus
    END = min(END, T - 0.75)
    place(perc, dum(1.1), END)
    for i, nm in enumerate(("D3", "A3", "D4", "F#4", "A4")): place(dry, ud(f(nm), 2.0, 0.8), END + i * 0.018, 0.2)
    place(dry, ney([("D4", 0, T - END)], 0.6), END, -0.2)
    mix = reverb(dry[:, 0] + dry[:, 1], 2.2, 0.35) * 0.5 + reverb(perc[:, 0] + perc[:, 1], 1.0, 0.15) * 0.5
    mix[:, 0] += 0.5 * (dry[:, 0] - dry[:, 1]); mix[:, 1] += 0.5 * (dry[:, 1] - dry[:, 0])
    return mix[:N]

# ---------- SFX ----------
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def whoosh(d=0.5, seed=3, hi=True):
    n = int(d * SR); x = np.random.default_rng(seed).standard_normal(n); p = np.linspace(0, 1, n)
    y = np.zeros(n); blk = 1024
    for s in range(0, n, blk):   # suzgec merkezi kayar (yukari)
        fc = 300 + (4200 if hi else 1800) * (p[s] ** 1.6)
        sos = butter(2, [fc * 0.6, min(fc * 1.6, 20000)], "band", fs=SR, output="sos"); y[s:s + blk] = sosfilt(sos, x[s:s + blk])
    e = np.sin(np.pi * p) ** 2 * (0.4 + p); return y / (np.abs(y).max() + 1e-9) * e
def boom(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; fq = 38 + 60 * np.exp(-t / 0.08)
    y = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.5)
    return y + sosfilt(butter(2, 400, fs=SR, output="sos"), np.random.default_rng(5).standard_normal(n)) * np.exp(-t / 0.05) * 0.3
def swell(d=0.6):
    n = int(d * SR); p = np.linspace(0, 1, n); x = np.random.default_rng(9).standard_normal(n)
    y = sosfilt(butter(2, [400, 6000], "band", fs=SR, output="sos"), x); return y / np.abs(y).max() * p ** 3
def pop(f0=900, f1=320, d=0.08):
    n = int(d * SR); t = np.arange(n) / SR; fq = f0 * (f1 / f0) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(fq) / SR) * env_exp(n, 0.02) * np.minimum(1, np.arange(n) / 48)
def chime(fs=(1318.5, 1975.5, 2637.0), d=1.4):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for i, fq in enumerate(fs):
        s = int(i * 0.06 * SR); y[s:] += np.sin(2 * np.pi * fq * t[:n - s]) * np.exp(-t[:n - s] / 0.45) / (1 + i * 0.5)
    return y * np.minimum(1, np.arange(n) / 96)

SFX_LIST = []  # (zaman, ad) - plana yazmak icin
def sfx():
    out = np.zeros(N + 2 * SR)
    def add(sig, at, db, name):
        SFX_LIST.append((round(at, 2), name)); i = max(0, int(at * SR)); s = sig[:len(out) - i]; out[i:i + len(s)] += s * 10 ** (db / 20)
    add(boom(), 0.0, -10, "derin vurus (acilis)")
    add(swell(0.45), 0.0, -24, "nefes yukselis -> baslik")
    add(pop(700, 260, .09), 0.45, -18, "baslik pop")
    add(pop(1100, 500, .06), 1.90, -21, "bilgi karti pop")
    w = whoosh(0.5, 3); add(w, 4.0 - 0.3, -15, "whoosh (minare -> merdiven)")
    w = whoosh(0.45, 4); add(w, 6.5 - 0.27, -17, "whoosh (merdiven -> konak)")
    w = whoosh(0.4, 5, hi=False); add(w, 8.5 - 0.25, -19, "yumusak whoosh (konusmaya gecis)")
    for at, nm in PILLS: add(pop(), at, -20, f"not pop ({nm})")
    w = whoosh(1.1, 6); add(w, WHIP0, -14, "savrulma whoosh (kamera donusu)")
    add(chime(), WHIP1 + 0.15, -27, "sokak acilisi parilti")
    w = whoosh(0.5, 7); add(w, OUTRO - 0.3, -16, "whoosh (muzik geri gelir)")
    w = whoosh(0.4, 8, hi=False); add(w, tl[-1][0] - 0.25, -19, "yumusak whoosh (son plan)")
    add(chime((987.8, 1318.5, 1975.5)), END_T, -22, "kapanis parilti")
    return out[:N]

# overlay ile paylasilan zamanlar
from edl import EDL
D_START = [r for r in tl if r[2] == "D"][0][0]; D_SRC0 = [r for r in tl if r[2] == "D"][0][3]
WHIP0 = D_START + (3.0 - D_SRC0); WHIP1 = D_START + (4.4 - D_SRC0)
PILLS = [(SPEECH0 + 0.58, "meydanin ust sokagi"), (SPEECH0 + 5.56, "carsinin ortasina"), (WHIP1 + 0.1, "carsiya dogru")]
END_T = tl[-1][0] + 0.6

def limiter(x, ceil_db=-1.5):
    """4x asiri ornekli, ileri bakisli tepe sinirlayici (true-peak)."""
    up = resample_poly(x, 4, 1, axis=0); pk = np.abs(up).max(1).reshape(-1, 4).max(1) if False else None
    up_abs = np.abs(up).max(1); env = np.maximum.reduceat(up_abs, np.arange(0, len(up_abs), 4))[:len(x)]
    c = 10 ** (ceil_db / 20); g = np.minimum(1, c / (env + 1e-9))
    la = int(0.005 * SR); g = np.minimum.accumulate(np.concatenate([g, np.ones(la)])[::-1])[::-1] if False else g
    # ileri bakis: 5 ms penceredeki en kucuk kazanc, sonra yumusatma
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    g = minimum_filter1d(g, size=2 * la + 1); g = uniform_filter1d(g, size=la)
    g = np.minimum(g, minimum_filter1d(np.minimum(1, c / (env + 1e-9)), size=3))
    return x * g[:, None]

if __name__ == "__main__":
    mus = music(); wr(f"{WORK}/music.wav", mus * 0.5)
    fx = sfx(); wr(f"{WORK}/sfx.wav", fx)
    voice = rd(f"{WORK}/voice_full.wav")[:N]; voice = np.pad(voice, (0, N - len(voice)))
    voice = sosfilt(butter(2, 80, "high", fs=SR, output="sos"), voice)
    # hafif kompresor (konusma)
    from scipy.ndimage import uniform_filter1d, maximum_filter1d
    rms = np.sqrt(uniform_filter1d(voice ** 2, int(0.03 * SR)) + 1e-10); lv = 20 * np.log10(rms)
    gr = np.where(lv > -24, (-24 - lv) * (1 - 1 / 2.5), 0); voice = voice * 10 ** (uniform_filter1d(gr, int(0.02 * SR)) / 20) * 2.2
    # muzik: bolum seviyesi + konusmaya gore ducking
    t = np.arange(N) / SR; sec = np.ones(N)
    sec[(t >= SPEECH0) & (t < OUTRO)] = 10 ** (-9 / 20)
    ramp = lambda a, b: np.clip((t - a) / (b - a), 0, 1)
    sec = np.where(t < SPEECH0, 1, sec) * 1.0
    sec = sec + (1 - 10 ** (-9 / 20)) * (ramp(OUTRO - 0.3, OUTRO) * (t >= SPEECH0) * (t < OUTRO))  # cikista yumusak donus
    sec = np.where((t >= SPEECH0 - 0.3) & (t < SPEECH0), 1 - (1 - 10 ** (-9 / 20)) * ramp(SPEECH0 - 0.3, SPEECH0), sec)
    act = maximum_filter1d((rms > 10 ** (-38 / 20)).astype(float), int(0.25 * SR)); act = uniform_filter1d(act, int(0.12 * SR))
    duck = 10 ** (-7 * act / 20)
    mus = mus * (sec * duck)[:, None]
    fade = np.clip((T - t) / 0.45, 0, 1); 
    mix = mus * 0.55 + (voice[:, None] + fx[:, None] * 0.9)
    mix *= fade[:, None]
    meter = pyln.Meter(SR)
    for _ in range(3):
        L = meter.integrated_loudness(mix); mix = mix * 10 ** ((-14 - L) / 20); mix = limiter(mix, -1.5)
    L = meter.integrated_loudness(mix)
    wr(f"{WORK}/mix.wav", mix)
    vL = meter.integrated_loudness(np.stack([voice, voice], 1)[int(SPEECH0 * SR):int(OUTRO * SR)])
    print(f"mix: {L:.2f} LUFS; sfx olaylari:"); [print("  ", a, n) for a, n in sorted(SFX_LIST)]
