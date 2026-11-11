"""Kesim kontrolu v2 (cok klipli kurgu icin)
1) Kaynak VAD: her segmentin giris/cikis noktasi kaynak klipteki bir konusma araliginin icine dusuyor mu? (kesik hece)
2) Dialog steminde kesim noktalari +-40 ms seviye (< -45 dB olmali)
3) Dialog stemi yeniden transkripsiyon: beklenen metin, ardisik tekrar, dusuk guvenli kelime
4) Tam ses steminde (b-roll ortam dahil) transkripsiyon: beklenmeyen konusma parcasi var mi
Kullanim: python3 cutcheck2.py <sdr> <build> "<beklenen metin>" """
import sys, os, re, wave, subprocess, numpy as np
from faster_whisper import WhisperModel
from faster_whisper.vad import get_speech_timestamps, VadOptions
from edl import SEGS, SPLIT, FPS, timeline
SDR, B, EXPECTED = sys.argv[1], sys.argv[2], sys.argv[3]
def rd(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr
def a16(clip):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SDR, clip + ".mov"), "-vn", "-ac", "1", "-ar", "16000",
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768
db = lambda s: 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-9)
ok = True
def _flag():
    pass
print("== 1) Kaynak VAD: segment sinirlari konusmayi bolmuyor mu (tolerans 30 ms)")
vadc, A16 = {}, {}
for s, f0, n in timeline():
    clips = [SPLIT[0], SPLIT[1]] if s[1] == "SPLIT" else [(s[1], s[2])]
    for clip, a in clips:
        if clip not in vadc:
            A16[clip] = a16(clip)
            vadc[clip] = [(t["start"] / 16000, t["end"] / 16000) for t in get_speech_timestamps(
                A16[clip], VadOptions(threshold=0.4, min_silence_duration_ms=120, speech_pad_ms=0, min_speech_duration_ms=60))]
        a0 = round(a * FPS) / FPS; b0 = a0 + n / FPS
        x16 = A16[clip]; msg = []
        for p in (a0, b0):
            inside = [(round(x, 2), round(y, 2)) for x, y in vadc[clip] if x + 0.03 < p < y - 0.03]
            if not inside: continue
            lv = db(x16[max(0, int((p - .02) * 16000)):int((p + .02) * 16000)])
            if lv > -45: ok = False; msg.append(f"SORUN @{p:.2f}s {lv:.0f} dB VAD{inside}")
            else: msg.append(f"@{p:.2f}s VAD birlesik bolgede ama sinir sessiz ({lv:.0f} dB)")
        print(f"  {s[0]} {clip} {a0:5.2f}-{b0:5.2f}  -> {'; '.join(msg) if msg else 'temiz'}")
print("== 2) Dialog steminde kesim noktalari (+-40 ms)")
d, sr = rd(os.path.join(B, "dialog.wav")); cuts = [float(x) for x in open(os.path.join(B, "cuts.txt")).read().split(",")]
for c in cuts:
    i = int(c * sr); l = db(d[max(0, i - int(.04 * sr)):i]); r = db(d[i:i + int(.04 * sr)])
    if l < -85 and r < -85: continue  # iki taraf da b-roll (dialog steminde sessiz)
    bad = l > -45 or r > -45; ok &= not bad
    print(f"  {c:6.2f}s  once {l:6.1f} dB | sonra {r:6.1f} dB -> {'SORUN' if bad else 'temiz'}")
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
def tr(x, sr):
    x16 = np.interp(np.arange(0, len(x), sr / 16000), np.arange(len(x)), x).astype(np.float32)
    segs, _ = m.transcribe(x16, language="tr", word_timestamps=True, condition_on_previous_text=False, vad_filter=True)
    return [(w.start, w.end, w.word.strip(), w.probability) for s in segs for w in s.words]
norm = lambda t: [x for x in (re.sub(r"[^\wçğıöşü]", "", y.replace("İ", "i").replace("I", "ı").lower()) for y in t) if x]
print("== 3) Dialog stemi yeniden transkripsiyon")
words = tr(d, sr)
for w in words: print(f"  {w[0]:6.2f}-{w[1]:6.2f} {w[2]:16s} p={w[3]:.2f}")
got, exp = norm([w[2] for w in words]), norm(EXPECTED.split())
print("  beklenen:", " ".join(exp)); print("  bulunan :", " ".join(got))
rep = [got[i] for i in range(1, len(got)) if got[i] == got[i - 1]]
print("  ardisik tekrar:", rep or "yok"); ok &= not rep
low = [w[2] for w in words if w[3] < 0.5]; print("  dusuk guvenli kelime:", low or "yok")
match = got == exp; ok &= match; print("  metin eslesmesi:", "TAM" if match else "FARKLI")
print("== 4) Tam ses stemi (b-roll ortam dahil)")
v, sr = rd(os.path.join(B, "voice.wav")); words = tr(v, sr); gv = norm([w[2] for w in words])
print("  bulunan:", " ".join(gv)); extra = gv != exp
print("  b-roll'da ek konusma:", "VAR -> " + str(gv) if extra else "yok"); ok &= not extra
print("SONUC:", "GECTI" if ok else "KALDI")
