"""Kurguya gore ses stemlerini uretir: voice.wav (dialog tam, b-roll ortam kisik), dialog_mask.npy
Kullanim: python3 audio_stem.py <sdr_klasoru> <cikis_klasoru>"""
import sys, os, subprocess, wave, numpy as np
from edl import SEGS, SPLIT, FPS, timeline, TOTAL
SR = 48000
SDR, OUT = sys.argv[1], sys.argv[2]
_cache = {}
def load(clip):
    if clip not in _cache:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SDR, clip + ".mov"), "-vn", "-ac", "1",
                              "-ar", str(SR), "-f", "s16le", "-"], capture_output=True, check=True).stdout
        _cache[clip] = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return _cache[clip]

def write(path, x):
    w = wave.open(path, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

spf = SR // FPS
voice = np.zeros(TOTAL * spf, np.float32); dmask = np.zeros(TOTAL * spf, np.float32)
cuts = []
for s, f0, n in timeline():
    sid, clip, a, b, kind, zoom, gain = s
    if clip == "SPLIT": clip, a = SPLIT[0]
    src = load(clip); i0 = round(a * FPS) * spf; L = n * spf
    seg = src[i0:i0 + L].copy()
    if len(seg) < L: seg = np.pad(seg, (0, L - len(seg)))
    fd = int((0.010 if kind == "dialog" else 0.060) * SR)
    ramp = np.linspace(0, 1, fd); seg[:fd] *= ramp; seg[-fd:] *= ramp[::-1]
    seg *= 10 ** (gain / 20)
    voice[f0 * spf:f0 * spf + L] = seg
    if kind == "dialog": dmask[f0 * spf:f0 * spf + L] = 1
    if f0: cuts.append(f0 / FPS)
write(os.path.join(OUT, "voice.wav"), voice)
# dialog-only stem (kesim kontrolu ve yeniden transkripsiyon icin)
write(os.path.join(OUT, "dialog.wav"), voice * dmask)
np.save(os.path.join(OUT, "dialog_mask.npy"), dmask)
open(os.path.join(OUT, "cuts.txt"), "w").write(",".join(f"{c:.4f}" for c in cuts))
print("sure", TOTAL / FPS, "kesim", len(cuts))
