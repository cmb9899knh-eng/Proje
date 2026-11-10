"""Konusma parcalarini kesip birlestirir (hiz degisikligi yok, kesimlerde 8 ms fade, MUTE araliklari -30 dB).
Cikti: <work>/voice_speech.wav (yalniz konusmalar arka arkaya), <work>/voice_full.wav (zaman cizelgesinde),
       <work>/speech_map.json (konusma zamani -> cikis zamani eslemesi)."""
import sys, wave, json, numpy as np, subprocess, os
from edl import timeline, MUTE
WORK, SRC = sys.argv[1], sys.argv[2]; SR = 48000
def load(k):
    p = f"{WORK}/{k}48.wav"
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{SRC}/{k}.mov", "-map", "0:a:0", "-ac", "1", "-ar", "48000", p], check=True)
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def save(p, x):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
tl, T = timeline(); full = np.zeros(int(T * SR) + SR); speech = []; cuts = []; acc = 0; smap = []
fade = int(0.008 * SR); ramp = np.linspace(0, 1, fade); r5 = int(0.005 * SR)
# ayni kaynaktan kesintisiz devam eden parcalar (goruntu kesilir, ses akar) tek parca olarak islenir
groups = []
for (t0, t1, e) in tl:
    if "a" not in e: continue
    if groups and groups[-1]["k"] == e["a"] and abs(groups[-1]["b"] - e["ai"]) < 1e-6 and abs(groups[-1]["t1"] - t0) < 1e-3:
        groups[-1]["b"] = e["ao"]; groups[-1]["t1"] = t1
    else: groups.append(dict(k=e["a"], a=e["ai"], b=e["ao"], t0=t0, t1=t1))
for G in groups:
    k, a, b, t0 = G["k"], G["a"], G["b"], G["t0"]
    seg = load(k)[int(round(a * SR)):int(round(b * SR))].copy(); g = np.ones(len(seg))
    for (m0, m1) in MUTE.get(k, []):
        i0, i1 = int((m0 - a) * SR), int((m1 - a) * SR)
        if i1 <= 0 or i0 >= len(seg): continue
        env = np.full(i1 - i0 + 2 * r5, 10 ** (-30 / 20)); env[:r5] = np.linspace(1, env[r5], r5); env[-r5:] = np.linspace(env[r5], 1, r5)
        j0 = i0 - r5; lo = max(0, j0); hi = min(len(seg), j0 + len(env)); g[lo:hi] = np.minimum(g[lo:hi], env[lo - j0:hi - j0])
    seg *= g
    # parca seviyesi esitleme: konusma olan kisimlarin RMS'i -24 dBFS
    blk = int(0.02 * SR); r = np.sqrt(np.array([np.mean(seg[i:i + blk] ** 2) for i in range(0, len(seg) - blk, blk)]) + 1e-12)
    act = r[r > r.max() * 10 ** (-20 / 20)]; lvl = 20 * np.log10(np.sqrt(np.mean(act ** 2)))
    seg *= 10 ** ((-24 - lvl) / 20); print(f"  {k} {a:.2f}-{b:.2f}: {lvl:.1f} dB -> -24 dB")
    seg[:fade] *= ramp; seg[-fade:] *= ramp[::-1]
    i = int(round(t0 * SR)); full[i:i + len(seg)] += seg
    if speech: cuts.append(round(acc, 3))
    smap.append([acc, acc + len(seg) / SR, t0, k, a])
    speech.append(seg); acc += len(seg) / SR
save(f"{WORK}/voice_speech.wav", np.concatenate(speech)); save(f"{WORK}/voice_full.wav", full[:int(T * SR)])
json.dump(smap, open(f"{WORK}/speech_map.json", "w"))
print("konusma toplam:", round(acc, 3), "sn; kesimler:", ",".join(f"{c:.3f}" for c in cuts))
