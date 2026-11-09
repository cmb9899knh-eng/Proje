"""Konusma parcalarini kesip birlestirir (hiz degisikligi yok, kesimlerde 8 ms fade).
Cikti: <work>/voice_speech.wav (yalniz konusma bolumu) ve <work>/voice_full.wav (tam zaman cizelgesinde)."""
import sys, wave, numpy as np, subprocess, os
from edl import timeline, MUTE
WORK, SRC = sys.argv[1], sys.argv[2]; SR = 48000
def load(k):
    p = f"{WORK}/{k}48.wav"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg","-v","error","-y","-i",f"{SRC}/{k}.mov","-map","0:a:0","-ac","1","-ar","48000",p],check=True)
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def save(p, x):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
tl, T = timeline(); full = np.zeros(int(T * SR) + SR); speech = []; cuts = []; acc = 0
fade = int(0.008 * SR); ramp = np.linspace(0, 1, fade)
for (t0, t1, k, a, b, v) in tl:
    if not v: continue
    seg = load(k)[int(round(a * SR)):int(round(b * SR))].copy()
    g = np.ones(len(seg)); r5 = int(0.005 * SR)
    for (m0, m1) in MUTE.get(k, []):
        i0, i1 = int((m0 - a) * SR), int((m1 - a) * SR)
        if i1 <= 0 or i0 >= len(seg): continue
        env = np.full(i1 - i0 + 2 * r5, 10 ** (-30 / 20)); env[:r5] = np.linspace(1, env[r5], r5); env[-r5:] = np.linspace(env[r5], 1, r5)
        j0 = i0 - r5; lo = max(0, j0); hi = min(len(seg), j0 + len(env)); g[lo:hi] = np.minimum(g[lo:hi], env[lo - j0:hi - j0])
    seg *= g
    seg[:fade] *= ramp; seg[-fade:] *= ramp[::-1]
    i = int(round(t0 * SR)); full[i:i + len(seg)] += seg
    if speech: cuts.append(acc)
    speech.append(seg); acc += len(seg) / SR
save(f"{WORK}/voice_speech.wav", np.concatenate(speech)); save(f"{WORK}/voice_full.wav", full[:int(T * SR)])
print("konusma bolumu:", round(acc, 3), "sn; kesimler:", ",".join(f"{c:.3f}" for c in cuts))
