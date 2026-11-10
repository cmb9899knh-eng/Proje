"""Ses temizleme (IMG_3293, kisa saclinin sesi + 'Kimi yakaladik yolda?').
1) klibin en sessiz %20'lik bolumlerinden gurultu profili -> spektral kapilama (noisereduce, sabit gurultu)
2) 90 Hz high-pass, 3 kHz civari +2.5 dB netlik, 7 kHz ustu hafif kisma (sokak tislamasi)
3) yumusak kompresor (3:1, -26 dB esik) -> konusma seviyesi diger kliplerle ayni
Cikti: a48b/<klip>_temiz.wav ; once/sonra olcumleri yazdirilir."""
import wave, sys, numpy as np, noisereduce as nr
from scipy.signal import lfilter, butter, sosfilt
SR = 48000
def load(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def save(p, x):
    w = wave.open(p, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
def frames_db(x, h=960):
    return np.array([20 * np.log10(np.sqrt((x[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(x) - h, h)])
def stats(x):
    d = frames_db(x); return np.percentile(d, 10), np.percentile(d, 95)
def peaking(f0, gain_db, q=0.9):
    A = 10 ** (gain_db / 40); w0 = 2 * np.pi * f0 / SR; al = np.sin(w0) / (2 * q)
    b = [1 + al * A, -2 * np.cos(w0), 1 - al * A]; a = [1 + al / A, -2 * np.cos(w0), 1 - al / A]
    return np.array(b) / a[0], np.array(a) / a[0]
def comp(x, thr=-26, ratio=3.0, att=0.005, rel=0.12):
    env = np.abs(x); out = np.empty_like(x); g = 1.0; e = 0.0
    aa, ar = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    # blok bazli (hiz icin 4 ms)
    hop = 192; gains = []
    for i in range(0, len(x), hop):
        lv = 20 * np.log10(np.sqrt((x[i:i + hop] ** 2).mean()) + 1e-9)
        tg = 0 if lv < thr else (thr + (lv - thr) / ratio) - lv
        e = (aa if tg < e else ar) * e + (1 - (aa if tg < e else ar)) * tg; gains.append(e)
    gl = np.repeat(10 ** (np.array(gains) / 20), hop)[:len(x)]
    return x * gl
for clip in sys.argv[1:]:
    x = load(f"a48b/{clip}.wav")
    d = frames_db(x); thr = np.percentile(d, 20)
    noise = np.concatenate([x[i * 960:(i + 1) * 960] for i, v in enumerate(d) if v <= thr])
    y = nr.reduce_noise(y=x, sr=SR, y_noise=noise, stationary=True, prop_decrease=0.88, n_fft=2048, time_mask_smooth_ms=60, freq_mask_smooth_hz=300)
    y = sosfilt(butter(4, 90, "hp", fs=SR, output="sos"), y)
    b, a = peaking(3000, 2.5); y = lfilter(b, a, y)
    b, a = peaking(8000, -3.0, 0.7); y = lfilter(b, a, y)
    y = comp(y.astype(np.float32))
    # konusma tepe seviyesini (95. yuzdelik) kaynakla esitle
    y *= 10 ** ((stats(x)[1] - stats(y)[1]) / 20)
    save(f"a48b/{clip}_temiz.wav", y)
    n0, s0 = stats(x); n1, s1 = stats(y)
    print(f"{clip}: gurultu tabani {n0:.1f} -> {n1:.1f} dB | konusma {s0:.1f} -> {s1:.1f} dB | SNR {s0 - n0:.1f} -> {s1 - n1:.1f} dB")
