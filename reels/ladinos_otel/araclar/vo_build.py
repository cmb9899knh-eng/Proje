"""Dis ses kayitlarini cumlelere boler, temizler, zamanlar (vo_timing.json) ve VO izini (vo.wav) kurar.
Kullanim: python3 vo_build.py <work>   (girdi: <work>/vo2/IMG_*.wav, <work>/vo2/words.json)"""
import sys, os, json, wave, subprocess, numpy as np
from faster_whisper.vad import get_speech_timestamps, VadOptions
WORK = sys.argv[1]; D = os.path.join(WORK, "vo2"); SR = 48000
WJ = json.load(open(os.path.join(D, "words.json")))
# cumle -> (kayit, aralik_bas, aralik_son)   (aralik: whisper kelime araligina gore kaba pencere)
MAP = {"V1": ("IMG_3964", 0, 99), "V9": ("IMG_3972", 0, 99), "V2": ("IMG_3965", 0, 99), "V3": ("IMG_3966", 0, 99),
       "V4": ("IMG_3967", 0, 99), "V5": ("IMG_3968", 0, 99), "V10": ("IMG_3973", 0, 5.85), "V6": ("IMG_3969", 0, 99),
       "V7": ("IMG_3971", 0, 5.35), "V8": ("IMG_3971", 5.35, 99), "V11": ("IMG_3973", 5.85, 99)}
FIX = {"Ladinoz": "Ladinos"}   # yalniz ekrandaki yazim
def load(name):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(D, name + ".wav"), "-af",
                          "highpass=f=80,afftdn=nf=-42:nr=10,lowpass=f=14000", "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
out, segs = {}, {}
for v, (rec, a, b) in MAP.items():
    x = load(rec); x16 = x[::3]
    ts = [(t["start"] / 16000, t["end"] / 16000) for t in get_speech_timestamps(x16, VadOptions(threshold=0.45, min_silence_duration_ms=250, speech_pad_ms=0))]
    ts = [(s, e) for s, e in ts if e > a + 0.05 and s < b - 0.05]
    s0 = max(a, ts[0][0]); e0 = min(b, ts[-1][1]) if b < 99 else ts[-1][1]
    # enerji tabanli genisletme: VAD yumusak hece baslangiclarini gec yakalayabiliyor
    fl = np.percentile([20 * np.log10(np.sqrt((x[i:i + 480] ** 2).mean()) + 1e-9) for i in range(0, len(x) - 480, 480)], 10)
    L10 = lambda t: 20 * np.log10(np.sqrt((x[int(t * SR):int(t * SR) + 480] ** 2).mean()) + 1e-9)
    t = s0
    while t > max(a, 0.01) and max(L10(t - 0.01), L10(t - 0.02), L10(t - 0.03)) > fl + 7: t -= 0.01
    s0 = t; t = e0
    while t < min(b, len(x) / SR) - 0.04 and max(L10(t), L10(t + 0.01), L10(t + 0.02)) > fl + 7: t += 0.01
    e0 = t
    st, en = max(0, s0 - 0.10, a), min(len(x) / SR, e0 + 0.15, b)
    seg = x[int(st * SR):int(en * SR)].copy(); f = int(0.012 * SR); r = np.linspace(0, 1, f); seg[:f] *= r; seg[-f:] *= r[::-1]
    words = [[round(max(w0 - st, 0.08), 2), round(w1 - st, 2), FIX.get(w, w)] for w0, w1, w, p in WJ[rec + ".wav"] if w1 > st + 0.02 and w0 < en - 0.05]
    # kayitta 'Midyat'+''ın' gibi bolunmus kelimeleri birlestir
    m = []
    for w in words:
        if m and w[2].startswith("'"): m[-1][1] = w[1]; m[-1][2] += w[2]
        else: m.append(w)
    words = m
    # kesik hece kontrolu: kesilen kisimdaki (sinirin 150 ms disi) en yuksek 10 ms seviye
    lv = lambda u, v: max([20 * np.log10(np.sqrt((x[int(t * SR):int(t * SR) + 480] ** 2).mean()) + 1e-9) for t in np.arange(max(0, u), min(v, len(x) / SR - 0.01), 0.01)] or [-120])
    floor = np.percentile([20 * np.log10(np.sqrt((x[i:i + 480] ** 2).mean()) + 1e-9) for i in range(0, len(x) - 480, 480)], 10)
    out_chk = (round(float(lv(st - 0.15, st)), 1), round(float(lv(en, en + 0.15)), 1), round(float(floor), 1))
    segs[v] = seg; out[v] = {"dur": round(len(seg) / SR, 3), "words": words, "src": f"{rec} {st:.2f}-{en:.2f}", "edge_db": out_chk}
    print(f"{v:4s} {rec} {st:5.2f}-{en:5.2f} ({len(seg)/SR:.2f} sn) kenar-disi {out_chk[0]}/{out_chk[1]} dB (taban {out_chk[2]})  " + " ".join(w[2] for w in words))
os.makedirs(os.path.join(WORK, "vo"), exist_ok=True)
json.dump(out, open(os.path.join(WORK, "vo", "vo_timing.json"), "w"), ensure_ascii=False, indent=1)
np.savez(os.path.join(WORK, "vo", "vo_segs.npz"), **segs)
