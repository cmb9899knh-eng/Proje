"""Mardin tanitim reels - muzik (Hicaz makaminda ozgun beste, tamamen kodla sentez), ses efektleri ve miks.
Hicbir telifli kayit/ornek kullanilmaz. Cikti: <work>/music.wav, sfx.wav, mix.wav (-14 LUFS, <= -1.5 dBTP)
Kullanim: python3 audio.py <work>"""
import sys, wave, json, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt, resample_poly
from scipy.ndimage import uniform_filter1d, maximum_filter1d, minimum_filter1d
import pyloudnorm as pyln
from edl import timeline, BEAT
WORK = sys.argv[1] if len(sys.argv) > 1 else "."
SR = 48000
tl, T = timeline(); N = int(T * SR)
rng = np.random.default_rng(11)

def sec_span(name):
    rows = [r for r in tl if r[2]["sec"] == name]; return rows[0][0], rows[-1][1]
HOOK = sec_span("hook"); TALK1 = sec_span("talk1"); STREETS = sec_span("streets"); TALK2 = sec_span("talk2")
CATS = sec_span("cats"); CAFE = sec_span("cafe"); MIRROR = sec_span("mirror"); REVEAL = sec_span("reveal"); OUTRO = sec_span("outro")
_t2 = [r for r in tl if r[2]["sec"] == "talk2"]
AY_T = _t2[2][0]                       # "Ay" basladigi an -> muzik bant gibi durur
D0 = REVEAL[0]; D_SRC0 = [r for r in tl if r[2]["sec"] == "reveal"][0][2]["vi"]
WHIP0 = D0 + (3.0 - D_SRC0); WHIP1 = D0 + (4.4 - D_SRC0)   # kamera savrulmasi -> sokak acilisi
CAFE_TALK = [r for r in tl if r[2]["sec"] == "cafe" and "a" in r[2]][0][0]

def rd(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    return x.reshape(-1, w.getnchannels()).mean(1) if w.getnchannels() > 1 else x
def wr(p, x):
    ch = 1 if x.ndim == 1 else x.shape[1]
    w = wave.open(p, "wb"); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], "band", fs=SR, output="sos"), x)
def lp(x, fc, o=2): return sosfilt(butter(o, fc, fs=SR, output="sos"), x)
def hp(x, fc, o=2): return sosfilt(butter(o, fc, "high", fs=SR, output="sos"), x)

# ---------------- Hicaz (Re karar) ----------------
NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
CENT = {"Eb": 14, "F#": -14}           # Hicaz rengi: 2. derece tiz, 3. derece pes (koma yaklasimi)
def f(n):
    name, octv = (n[:-1], int(n[-1]))
    return 440 * 2 ** ((NOTE[name] + 12 * (octv + 1) - 69) / 12) * 2 ** (CENT.get(name, 0) / 1200)

def ks(freq, dur, vel=1.0, bright=0.5, decay=0.996, detune=1.0035, body=(180, 3800)):
    """Karplus-Strong ile mizrapli tel (cift tel)."""
    n = int(dur * SR); out = np.zeros(n)
    for det in (1.0, detune):
        L = max(2, int(SR / (freq * det))); buf = rng.uniform(-1, 1, L)
        buf = np.convolve(buf, [bright, 1 - bright], "same"); y = np.zeros(n + L); y[:L] = buf
        k = 1
        while k * L < n + L:
            s, e = k * L, min((k + 1) * L, n + L)
            prev = y[s - L:e - L]; prev2 = np.concatenate([[y[s - L - 1]], prev[:-1]])
            y[s:e] = decay * 0.5 * (prev + prev2); k += 1
        out += y[L:L + n]
    att = np.minimum(1, np.arange(n) / 30); rel = np.minimum(1, (n - np.arange(n)) / (0.03 * SR))
    return (0.6 * bp(out, *body) + 0.4 * out) * att * rel * vel * 0.5
def ud(n, dur, vel=1.0): return ks(f(n), dur, vel, 0.55, 0.996, 1.004, (150, 3500))
def saz(n, dur, vel=1.0): return ks(f(n), dur, vel, 0.25, 0.993, 1.006, (300, 6500)) * 0.9
def kanun(n, dur, vel=1.0): return ks(f(n), dur, vel, 0.2, 0.9965, 1.002, (500, 8000)) * 0.75

def ney(notes, gain=1.0):
    """[(nota, t0, t1)] -> ney benzeri ses (yumusak sinus + harmonik + nefes, vibrato, kayma)."""
    end = max(t1 for _, t0, t1 in notes); n = int(end * SR) + SR // 2; fr = np.full(n, np.nan); amp = np.zeros(n)
    for name, t0, t1 in notes:
        i0, i1 = int(t0 * SR), int(t1 * SR); fr[i0:i1] = f(name)
        a = np.ones(i1 - i0); at = int(min(0.10, (t1 - t0) / 3) * SR); a[:at] = np.linspace(0.15, 1, at) ** 1.5
        rl = int(min(0.10, (t1 - t0) / 3) * SR); a[-rl:] *= np.linspace(1, 0.5, rl); amp[i0:i1] = a
    idx = np.where(~np.isnan(fr), np.arange(n), 0); np.maximum.accumulate(idx, out=idx)
    fr = np.nan_to_num(fr[idx], nan=f(notes[0][0])); fr = uniform_filter1d(fr, int(0.04 * SR))
    t = np.arange(n) / SR; vib = 1 + 0.006 * np.sin(2 * np.pi * 5.3 * t)
    ph = 2 * np.pi * np.cumsum(fr * vib) / SR
    tone = np.sin(ph) + 0.20 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)
    breath = bp(rng.standard_normal(n), 900, 4500) * 0.25
    amp = uniform_filter1d(amp, 480)
    return (tone + breath) * amp * 0.26 * gain

def pad(root_notes, dur, gain=1.0):
    """Yay benzeri dolgu: dedune testere dalgalar, alcak geciren, yavas giris."""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for nm in root_notes:
        for dt in (-0.12, 0.0, 0.12):
            fq = f(nm) * 2 ** (dt / 12); y += 2 * ((t * fq + rng.random()) % 1) - 1
    y = lp(y, 1600, 2); env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 0.5)
    return y / (np.abs(y).max() + 1e-9) * env * 0.12 * gain

def bass(n, dur, vel=1.0):
    k = int(dur * SR); t = np.arange(k) / SR; fq = f(n)
    y = np.sin(2 * np.pi * fq * t) + 0.3 * np.sin(4 * np.pi * fq * t) + 0.15 * np.sign(np.sin(2 * np.pi * fq * t))
    env = np.exp(-t / 0.35) * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.02)
    return lp(y, 900) * env * 0.45 * vel

def dum(vel=1.0):
    n = int(0.55 * SR); t = np.arange(n) / SR; fq = 64 + 70 * np.exp(-t / 0.03)
    y = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.22)
    y += lp(rng.standard_normal(n), 900) * np.exp(-t / 0.012) * 0.5
    return y * vel * 0.9
def tek(vel=1.0, ka=False):
    n = int(0.22 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), *((2200, 7500) if not ka else (1200, 4500)))
    ring = np.sin(2 * np.pi * (640 if not ka else 480) * t) * 0.6
    return (nz * np.exp(-t / 0.018) + ring * np.exp(-t / 0.05)) * vel * (0.55 if not ka else 0.35)
def bendir(vel=1.0):
    n = int(0.6 * SR); t = np.arange(n) / SR; fq = 52 + 30 * np.exp(-t / 0.05)
    y = np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.3) + bp(rng.standard_normal(n), 2000, 6000) * np.exp(-t / 0.08) * 0.15
    return y * vel * 0.8
def zil(vel=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    y = bp(rng.standard_normal(n), 6000, 14000) * np.exp(-t / 0.06) + 0.3 * np.sin(2 * np.pi * 7400 * t) * np.exp(-t / 0.08)
    return y * vel * 0.25
def clap(vel=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR; nz = bp(rng.standard_normal(n), 900, 3200); env = np.zeros(n)
    for o in (0, 0.009, 0.019): i = int(o * SR); env[i:] += np.exp(-np.arange(n - i) / (0.01 * SR))
    env += np.exp(-t / 0.09) * 0.5
    return nz * env * vel * 0.32
def snap_(vel=1.0):
    n = int(0.08 * SR); t = np.arange(n) / SR
    return bp(rng.standard_normal(n), 1800, 6000) * np.exp(-t / 0.008) * vel * 0.5

def reverb(x, sec=1.8, wet=0.25, seed=1):
    n = int(sec * SR); t = np.arange(n) / SR; out = []
    for s in (seed, seed + 1):
        ir = np.random.default_rng(s).standard_normal(n) * np.exp(-t / (sec / 6.9)); ir[:int(0.015 * SR)] = 0
        ir = lp(ir, 5000, 1); ir /= np.sqrt((ir ** 2).sum()); out.append(fftconvolve(x, ir)[:len(x)])
    return np.stack([x + wet * out[0], x + wet * out[1]], 1)

class Bus:
    def __init__(s): s.x = np.zeros((N + 3 * SR, 2))
    def add(s, sig, at, gain=1.0, pan=0.0):
        i = int(round(at * SR))
        if i >= len(s.x) or i + len(sig) <= 0: return
        if i < 0: sig = sig[-i:]; i = 0
        sig = sig[:len(s.x) - i] * gain
        s.x[i:i + len(sig), 0] += sig * np.sqrt(0.5 * (1 - pan)) * 1.414
        s.x[i:i + len(sig), 1] += sig * np.sqrt(0.5 * (1 + pan)) * 1.414

# ---------------- beste ----------------
B = BEAT; BAR = 4 * B
def grid(t): return np.floor(t / B + 1e-6) * B
MAIN = [  # ana tema (8'likler, None = es) - 3 olcu
    "A4", None, "Bb4", "A4", "G4", "F#4", "G4", "A4",
    "Bb4", "C5", "Bb4", "A4", "G4", "F#4", "Eb4", "D4",
    "D4", "Eb4", "F#4", "G4", "A4", "A4", "A4", "A4"]
ROOTS = ["D3", "D3", "C3", "D3", "Bb2", "A2", "D3", "D3"]   # olcu basina bas kok sesi

def maqsum(bus, t0, t1, vel=1.0, fills=True, claps=False, zils=False):
    t = t0
    while t < t1 - 1e-6:
        for (o, kind) in ((0, "D"), (0.5, "T"), (1.5, "T"), (2.0, "D"), (3.0, "T")):
            at = t + o * B
            if at >= t1: continue
            if kind == "D": bus.add(dum(vel), at)
            else: bus.add(tek(vel * 0.8), at, pan=0.25)
        if fills:
            for o in (1.0, 2.5, 3.5, 3.75):
                if t + o * B < t1: bus.add(tek(vel * 0.45, ka=True), t + o * B, pan=-0.25)
        if claps:
            for o in (1.0, 3.0):
                if t + o * B < t1: bus.add(clap(vel), t + o * B, pan=0.1)
        if zils:
            for o in (0.5, 1.5, 2.5, 3.5):
                if t + o * B < t1: bus.add(zil(vel), t + o * B, pan=-0.4)
        t += BAR
def bassline(bus, t0, t1, vel=1.0, bar0=0):
    t = t0; k = bar0
    while t < t1 - 1e-6:
        r = ROOTS[k % len(ROOTS)]; fifth = {"D3": "A2", "C3": "G2", "Bb2": "F2", "A2": "E2"}[r]
        for o, nm, d in ((0, r, 0.45), (1.5, fifth, 0.3), (2.0, r, 0.45), (3.5, r, 0.2)):
            if t + o * B < t1: bus.add(bass(nm, d, vel), t + o * B)
        t += BAR; k += 1
def theme(bus, t0, t1, inst=saz, vel=1.0, trem_last=True):
    for i, nm in enumerate(MAIN * 2):
        at = t0 + i * B / 2
        if at >= t1 - 0.05: break
        if not nm: continue
        if trem_last and i % len(MAIN) >= 20:   # son olcude tremolo
            for k in range(4): bus.add(inst(nm, 0.18, vel * (0.75 if k else 1)), at + k * B / 8, pan=0.2)
        else: bus.add(inst(nm, 0.5, vel), at, pan=0.2)
def roll(bus, t0, t1, v0=0.2, v1=1.0):
    n = int((t1 - t0) / (B / 4))
    for i in range(n): bus.add(tek(v0 + (v1 - v0) * i / max(1, n - 1), ka=(i % 2 == 1)), t0 + i * B / 4, pan=0.2 * (-1) ** i)

def compose():
    mel, perc, low, padb = Bus(), Bus(), Bus(), Bus()
    # KANCA: buyuk vurus + ney dususu + ud akoru, sonra darbuka rulosu
    perc.add(dum(1.2), HOOK[0]); low.add(bass("D2", 1.2, 1.2), HOOK[0])
    for i, nm in enumerate(("D3", "A3", "D4", "F#4", "A4")): mel.add(ud(nm, 1.4, 0.9), HOOK[0] + i * 0.015)
    mel.add(ney([("D5", 0.0, 0.35), ("C5", 0.35, 0.6), ("Bb4", 0.6, 0.85), ("A4", 0.85, 1.4)], 0.8), HOOK[0] + 0.05, -0.2)
    roll(perc, HOOK[1] - 0.5, HOOK[1], 0.15, 0.7)
    # KONUSMA 1: hafif ritim, bas, ud akorlari (ducking ile alcak)
    maqsum(perc, TALK1[0], TALK1[1], 0.55, fills=False); bassline(low, TALK1[0], TALK1[1], 0.8)
    t = TALK1[0]
    while t < TALK1[1] - 0.1: mel.add(ud("D3", 1.6, 0.5), t, 0.15); mel.add(ud("A3", 1.2, 0.35), t + 1.0, 0.15); t += BAR
    roll(perc, STREETS[0] - 0.5, STREETS[0], 0.2, 0.9)
    # SOKAKLAR: ana tema (saz + ney) + tam ritim + alkis + zil + yay dolgusu
    perc.add(dum(1.2), STREETS[0]); perc.add(bendir(1.0), STREETS[0])
    maqsum(perc, STREETS[0], STREETS[1], 1.0, claps=True, zils=True); bassline(low, STREETS[0], STREETS[1], 1.0)
    theme(mel, STREETS[0], STREETS[1], saz, 1.0)
    mel.add(ney([(n, i * B / 2, (i + 1) * B / 2) for i, n in enumerate(MAIN) if n][:24], 0.55), STREETS[0], -0.25)
    padb.add(pad(["D3", "A3"], STREETS[1] - STREETS[0], 1.0), STREETS[0])
    # KONUSMA 2: ritim + bas devam (ducking), "Ay" aninda bant durmasi (asagida), sessizlik
    maqsum(perc, TALK2[0], AY_T + 0.5, 0.6, fills=True); bassline(low, TALK2[0], AY_T + 0.5, 0.8)
    t = TALK2[0]
    while t < AY_T: mel.add(saz(["D4", "F#4", "A4", "G4"][int((t - TALK2[0]) / B) % 4], 0.4, 0.35), t + B / 2, 0.3); t += B
    # KEDILER: pizzicato motif + parmak sikirtmasi
    pz = ["D5", None, "A4", None, "F#4", "G4", "A4", None, "Bb4", "A4", "G4", "F#4", "Eb4", None, "D4", None,
          "D5", None, "C5", "Bb4", "A4", None, "D4", None]
    for i, nm in enumerate(pz):
        at = CATS[0] + i * B / 4 * 2
        if at >= CATS[1]: break
        if nm: mel.add(kanun(nm, 0.25, 0.9), at, 0.3)
    t = CATS[0]
    while t < CATS[1] - 1e-6: perc.add(snap_(1.0), t + B, -0.3); perc.add(snap_(1.0), t + 3 * B, -0.3); perc.add(dum(0.6), t); t += BAR
    low.add(bass("D2", 0.3), CATS[0]); low.add(bass("A2", 0.3), CATS[0] + 2 * B); low.add(bass("D2", 0.3), CATS[0] + 4 * B)
    # KITAP KAFE: sakin, kanun arpejleri + bendir + yay dolgusu (yarim tempo hissi)
    arp = ["D4", "F#4", "A4", "D5", "A4", "F#4", "Eb4", "F#4"]; arp2 = ["C4", "Eb4", "G4", "C5", "G4", "Eb4", "D4", "Eb4"]
    t = CAFE[0]; bar = 0
    while t < CAFE[1] - 1e-6:
        seq = arp if bar % 4 != 2 else arp2
        for i, nm in enumerate(seq):
            if t + i * B / 2 < CAFE[1]: mel.add(kanun(nm, 0.7, 0.65 if i else 0.85), t + i * B / 2, 0.3 * (-1) ** i)
        perc.add(bendir(0.8), t); perc.add(tek(0.35, ka=True), t + 1.5 * B, 0.2); perc.add(bendir(0.5), t + 2.5 * B); perc.add(tek(0.4), t + 3 * B, 0.2)
        low.add(bass("D2" if bar % 4 != 2 else "C2", 1.5, 0.7), t)
        t += BAR; bar += 1
    padb.add(pad(["D3", "A3", "F#4"], CAFE[1] - CAFE[0], 0.9), CAFE[0])
    mel.add(ney([("A4", 0, 1.0), ("Bb4", 1.0, 1.4), ("A4", 1.4, 2.6), ("G4", 2.6, 3.0), ("F#4", 3.0, 4.0)], 0.5), CAFE[0] + 3.0, -0.3)
    # AYNALAR: gerilim yukselir (darbuka rulosu + yay) -> konusma altinda kalp atisi + yukselen dolgu -> ACILIS'ta patlama
    roll(perc, MIRROR[0], MIRROR[1], 0.3, 1.25)
    for i, at in enumerate(np.arange(MIRROR[0], MIRROR[1] - 1e-6, B)): perc.add(dum(0.4 + 0.7 * i / 6), at)
    mel.add(ney([("A4", 0, 1.0), ("Bb4", 1.0, 1.5), ("C5", 1.5, 2.2), ("D5", 2.2, 3.0)], 0.7), MIRROR[0], -0.2)
    padb.add(pad(["D3", "A3", "D4"], MIRROR[1] - MIRROR[0] + 0.5, 1.2), MIRROR[0])
    t = REVEAL[0]
    while t < WHIP1 - 0.1: perc.add(dum(0.55), t); perc.add(dum(0.35), t + B * 0.6); t += BAR / 2
    padb.add(pad(["D3", "A3"], WHIP1 - REVEAL[0], 0.9), REVEAL[0])
    roll(perc, WHIP1 - 1.0, WHIP1, 0.1, 1.0)
    perc.add(dum(1.3), WHIP1); low.add(bass("D2", 1.0, 1.3), WHIP1); perc.add(bendir(1.0), WHIP1)
    g0 = grid(WHIP1) + (B if grid(WHIP1) < WHIP1 - 0.01 else 0)
    LAST = [r for r in tl if r[2]['sec'] == 'outro'][-1][0]
    maqsum(perc, g0, LAST, 1.0, claps=True, zils=True); bassline(low, g0, LAST, 1.0)
    theme(mel, g0, LAST, saz, 1.0)
    mel.add(ney([(n, i * B / 2, (i + 1) * B / 2) for i, n in enumerate(MAIN + MAIN) if n], 0.5), g0, -0.25)
    padb.add(pad(["D3", "A3"], OUTRO[1] - g0, 1.0), g0)
    # FINAL vurusu + akor + ney uzun nota
    END = [r for r in tl if r[2]['sec'] == 'outro'][-1][0]   # son plan (minare) girisi
    perc.add(dum(1.3), END); perc.add(bendir(1.2), END); low.add(bass("D2", 1.2, 1.2), END)
    for i, nm in enumerate(("D3", "A3", "D4", "F#4", "A4", "D5")): mel.add(saz(nm, 1.2, 0.85), END + i * 0.02, 0.2)
    mel.add(ney([("D5", 0, 1.0)], 0.6), END, -0.2)
    music = reverb(mel.x[:, 0] + mel.x[:, 1], 2.0, 0.35, 1) * 0.5 + reverb(perc.x[:, 0] + perc.x[:, 1], 0.9, 0.12, 3) * 0.5
    music[:, 0] += 0.45 * (mel.x[:, 0] - mel.x[:, 1]); music[:, 1] += 0.45 * (mel.x[:, 1] - mel.x[:, 0])
    music += reverb(padb.x[:, 0] + padb.x[:, 1], 2.5, 0.5, 5) * 0.5 + low.x * 0.9
    music = music[:N]
    # bant durmasi: "Ay" aninda muzik 0.45 sn icinde yavaslayip durur, sonra kediler bolumune kadar sessiz
    i0 = int(AY_T * SR); L = int(0.45 * SR); seg = music[i0:i0 + 3 * L].copy()
    rate = np.linspace(1.0, 0.0, L); pos = np.cumsum(rate); pos = np.clip(pos, 0, len(seg) - 2)
    stop = np.stack([np.interp(pos, np.arange(len(seg)), seg[:, c]) for c in (0, 1)], 1) * np.linspace(1, 0, L)[:, None] ** 0.5
    music[i0:i0 + L] = stop; music[i0 + L:int(CATS[0] * SR) - 1] = 0
    return music

# ---------------- ses efektleri (sentez) ----------------
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def whoosh(d=0.5, seed=3, hi=True):
    n = int(d * SR); x = np.random.default_rng(seed).standard_normal(n); p = np.linspace(0, 1, n); y = np.zeros(n); blk = 1024
    for s in range(0, n, blk):
        fc = 300 + (4200 if hi else 1800) * (p[s] ** 1.6)
        y[s:s + blk] = sosfilt(butter(2, [fc * 0.6, min(fc * 1.6, 20000)], "band", fs=SR, output="sos"), x[s:s + blk])
    e = np.sin(np.pi * p) ** 2 * (0.4 + p); return y / (np.abs(y).max() + 1e-9) * e
def boom(d=1.6):
    n = int(d * SR); t = np.arange(n) / SR; fq = 38 + 60 * np.exp(-t / 0.08)
    return np.sin(2 * np.pi * np.cumsum(fq) / SR) * np.exp(-t / 0.5) + lp(np.random.default_rng(5).standard_normal(n), 400) * np.exp(-t / 0.05) * 0.3
def riser(d=1.5):
    n = int(d * SR); p = np.linspace(0, 1, n); t = np.arange(n) / SR
    nz = np.zeros(n); x = np.random.default_rng(21).standard_normal(n); blk = 1024
    for s in range(0, n, blk):
        fc = 400 + 7000 * p[s] ** 2; nz[s:s + blk] = sosfilt(butter(2, [fc * 0.7, min(fc * 1.4, 20000)], "band", fs=SR, output="sos"), x[s:s + blk])
    tone = np.sin(2 * np.pi * np.cumsum(200 * 2 ** (3 * p)) / SR) * 0.3
    return (nz / np.abs(nz).max() + tone) * p ** 2.5
def pop(f0=900, f1=320, d=0.08):
    n = int(d * SR); t = np.arange(n) / SR; fq = f0 * (f1 / f0) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(fq) / SR) * env_exp(n, 0.02) * np.minimum(1, np.arange(n) / 48)
def chime(fs=(1318.5, 1975.5, 2637.0), d=1.4, step=0.06):
    n = int(d * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for i, fq in enumerate(fs):
        s = int(i * step * SR); y[s:] += np.sin(2 * np.pi * fq * t[:n - s]) * np.exp(-t[:n - s] / 0.45) / (1 + i * 0.4)
    return y * np.minimum(1, np.arange(n) / 96)
def meow(d=0.55):
    """Kodla uretilmis kedi sesi: formant gecisli testere dalga."""
    n = int(d * SR); p = np.linspace(0, 1, n)
    f0 = 520 + 260 * np.sin(np.pi * p ** 0.8) - 120 * p
    src = 2 * ((np.cumsum(f0) / SR) % 1) - 1
    f1 = 700 + 900 * np.sin(np.pi * np.clip(p * 1.3, 0, 1))      # "mi-yav" agiz acilmasi
    y = np.zeros(n); blk = 512
    for s in range(0, n, blk):
        y[s:s + blk] = sosfilt(butter(2, [f1[s] * 0.7, f1[s] * 1.5], "band", fs=SR, output="sos"), src[s:s + blk]) + \
            0.5 * sosfilt(butter(2, [2600, 3600], "band", fs=SR, output="sos"), src[s:s + blk])
    env = np.minimum(1, p / 0.08) * np.minimum(1, (1 - p) / 0.35)
    return y / (np.abs(y).max() + 1e-9) * env
def tapestop(d=0.45):
    n = int(d * SR); p = np.linspace(0, 1, n); fq = 180 * (1 - p) ** 1.5 + 20
    return np.sin(2 * np.pi * np.cumsum(fq) / SR) * (1 - p) * 0.6
def shutter():
    y = np.zeros(int(0.18 * SR))
    for at in (0.0, 0.07):
        n = int(0.05 * SR); t = np.arange(n) / SR; i = int(at * SR)
        y[i:i + n] += bp(rng.standard_normal(n), 1500, 7000) * np.exp(-t / 0.008)
    return y
def sparkle(d=1.0):
    y = np.zeros(int(d * SR)); r = np.random.default_rng(31)
    for k in range(14):
        fq = 2000 + 3000 * r.random(); at = k * d / 16; n = int(0.25 * SR); t = np.arange(n) / SR; i = int(at * SR)
        m = min(n, len(y) - i); y[i:i + m] += (np.sin(2 * np.pi * fq * t) * np.exp(-t / 0.06) * (0.4 + 0.6 * r.random()))[:m]
    return y

SFX_LIST = []
def sfx():
    out = np.zeros(N + 3 * SR)
    def add(sig, at, db, name):
        SFX_LIST.append((round(at, 2), name)); i = max(0, int(at * SR)); s = sig[:len(out) - i]; out[i:i + len(s)] += s * 10 ** (db / 20)
    add(boom(), HOOK[0], -9, "derin vurus (kanca)")
    for (t0, t1, e) in tl:
        if "whip" in e.get("fx", []) and t0 > 0.1: add(whoosh(0.42, int(t0 * 10) % 50), t0 - 0.25, -19, f"whoosh gecis ({e['v']})")
    for at, name in PILL_TIMES: add(pop(), at, -21, f"not pop ({name})")
    add(tapestop(), AY_T, -16, "bant durmasi ('Ay')")
    add(meow(), CATS[0] + 1.0 + 0.15, -24, "kedi sesi (kodla)")
    add(sparkle(1.0), CAFE[0] + 0.1, -26, "sihirli parilti (gizli kapi)")
    add(shutter(), MIRROR[0] + 0.5, -20, "deklansor (ayna selfie)")
    add(riser(WHIP1 - WHIP0 + 0.4), WHIP0 - 0.4, -18, "yukselen gerilim (savrulma oncesi)")
    add(whoosh(1.1, 6), WHIP0, -15, "savrulma whoosh")
    add(boom(1.2), WHIP1, -12, "acilis vurusu (sokak)")
    add(chime(), [r for r in tl if r[2]["sec"] == "outro"][-2][0] + 0.2, -24, "GORUSURUZ parilti"); add(boom(1.4), [r for r in tl if r[2]["sec"] == "outro"][-1][0], -12, "final vurusu (minare)")
    return out[:N]

# grafik (render.py) ile ayni zamanlar
def pill_times():
    out = []; last = None
    for (t0, t1, e) in tl:
        p = e.get("pill")
        if p and p != last:
            at = t0 + (WHIP1 - t0 + 0.1 if e["sec"] == "reveal" else 0.12)
            out.append((round(at, 3), p[0]))
        last = p
    return out
PILL_TIMES = pill_times()

def limiter(x, ceil_db=-1.5):
    """4x asiri ornekli ileri bakisli tepe sinirlayici (true-peak)."""
    up = resample_poly(x, 4, 1, axis=0); a = np.abs(up).max(1)
    env = np.maximum.reduceat(a, np.arange(0, len(a), 4))[:len(x)]
    c = 10 ** (ceil_db / 20); g0 = np.minimum(1, c / (env + 1e-9)); la = int(0.005 * SR)
    g = uniform_filter1d(minimum_filter1d(g0, size=2 * la + 1), size=la); g = np.minimum(g, minimum_filter1d(g0, size=3))
    return x * g[:, None]

if __name__ == "__main__":
    mus = compose(); wr(f"{WORK}/music.wav", np.clip(mus * 0.5, -1, 1))
    fx = sfx(); wr(f"{WORK}/sfx.wav", np.clip(fx, -1, 1))
    voice = rd(f"{WORK}/voice_full.wav")[:N]; voice = np.pad(voice, (0, N - len(voice)))
    voice = hp(voice, 80)
    rms = np.sqrt(uniform_filter1d(voice ** 2, int(0.03 * SR)) + 1e-10); lv = 20 * np.log10(rms)
    gr = np.where(lv > -24, (-24 - lv) * (1 - 1 / 2.5), 0); voice = voice * 10 ** (uniform_filter1d(gr, int(0.02 * SR)) / 20) * 2.2
    # muzik seviyesi: konusma bolumlerinde -9 dB + konusmaya gore -7 dB ducking
    t = np.arange(N) / SR; talk = np.zeros(N, bool)
    for (t0, t1, e) in tl:
        if "a" in e: talk |= (t >= t0) & (t < t1)
    sec = np.where(talk, 10 ** (-9 / 20), 1.0); sec = uniform_filter1d(sec, int(0.25 * SR))
    act = maximum_filter1d((rms > 10 ** (-38 / 20)).astype(float), int(0.25 * SR)); act = uniform_filter1d(act, int(0.12 * SR))
    mus = mus * (sec * 10 ** (-7 * act / 20))[:, None]
    fade = np.clip((T - t) / 0.5, 0, 1)
    mix = (mus * 0.55 + voice[:, None] + fx[:, None] * 0.9) * fade[:, None]
    meter = pyln.Meter(SR)
    for _ in range(3):
        L = meter.integrated_loudness(mix); mix = mix * 10 ** ((-14 - L) / 20); mix = limiter(mix, -1.5)
    wr(f"{WORK}/mix.wav", mix)
    print(f"mix: {meter.integrated_loudness(mix):.2f} LUFS")
    json.dump(sorted(SFX_LIST), open(f"{WORK}/sfx_list.json", "w"), ensure_ascii=False)
    for a, n in sorted(SFX_LIST): print(f"  {a:6.2f} {n}")
