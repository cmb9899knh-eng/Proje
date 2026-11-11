"""Dis ses izini kurguya yerlestirir (vo_track.wav) ve kesim kontrolu yapar:
 1) her cumle tek basina yeniden transkripsiyon: beklenen metin, ilk/son kelime guveni (kesik hece belirtisi)
 2) tam izde transkripsiyon: tum metin, ardisik tekrar
Kullanim: python3 vo_check.py <work>"""
import sys, os, re, json, wave, numpy as np
from faster_whisper import WhisperModel
WORK = sys.argv[1]; sys.argv = [sys.argv[0], WORK, "x"]
import promo
SR = 48000; segs = np.load(os.path.join(WORK, "vo", "vo_segs.npz")); VT = json.load(open(os.path.join(WORK, "vo", "vo_timing.json")))
N = int(promo.TOTAL / promo.FPS * SR); track = np.zeros(N, np.float32); place = []
for s in promo.SECS:
    if not s["vo"]: continue
    x = segs[s["vo"]]; i = int(s["vo_t"] * SR); track[i:i + len(x)] += x[:N - i]; place.append((s["vo"], s["vo_t"], s["vo_t"] + len(x) / SR, (s["f0"] + s["n"]) / promo.FPS))
# gercek diyalog bolumu: klip sesleri (ilk kurgudaki dogrulanmis kesimler), VO ile ayni algilanan seviyeye esitlenir
import subprocess, pyloudnorm as pyln
meter = pyln.Meter(SR); vo_l = meter.integrated_loudness(np.concatenate([segs[k] for k in segs.files]).astype(np.float64))
dl = []
for sh in promo.SHOTS:
    if not sh.get("dlg"): continue
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(WORK, "sdr", sh["clip"] + ".mov"), "-vn", "-ac", "1", "-ar", str(SR),
                          "-af", "highpass=f=80", "-f", "s16le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    i0 = round(sh["src0"] * promo.FPS) * (SR // promo.FPS); L = sh["n"] * (SR // promo.FPS); seg = x[i0:i0 + L].copy()
    f = int((0.010 if sh["gain"] == 0 else 0.06) * SR); r = np.linspace(0, 1, f); seg[:f] *= r; seg[-f:] *= r[::-1]
    dl.append((sh, seg))
sp = np.concatenate([sg for sh, sg in dl if sh["gain"] == 0]).astype(np.float64)
dg = 10 ** ((vo_l - meter.integrated_loudness(sp)) / 20)
for sh, seg in dl:
    i = sh["f0"] * (SR // promo.FPS); track[i:i + len(seg)] += seg * dg * 10 ** (sh["gain"] / 20)
print(f"diyalog kazanci {20*np.log10(dg):+.1f} dB (VO ile esitleme)")
w = wave.open(os.path.join(WORK, "vo", "vo_track.wav"), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(track, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
norm = lambda t: ["".join(re.sub(r"[^\wçğıöşü]", "", y.replace("İ", "i").replace("I", "ı").lower()) for y in t)]  # harf dizisi (kesme isareti/bolunme farki yok)
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
def tr(x):
    z = np.zeros(8000, np.float32); x16 = np.concatenate([z, x[::3].astype(np.float32), z])
    sg, _ = m.transcribe(x16, language="tr", word_timestamps=True, condition_on_previous_text=False, beam_size=5,
                         initial_prompt="Ladinos Otel, Midyat, Akçakaya Mahallesi, Atatürk Bulvarı.")
    return [(w.word.strip(), w.probability) for s in sg for w in s.words]
ok = True
print("== 1) Cumle bazinda (ilk/son kelime guveni < 0,6 ise kesik hece suphesi)")
ALIAS = {}
for v, a, b, secend in place:
    exp = norm(dict((p, q) for p, q, r in promo.VO)[v].split()); ws = tr(segs[v])
    got = [g.replace("ladinoz", "ladinos").replace("ladinus", "ladinos") for g in norm([x[0] for x in ws])]
    edge = (round(float(ws[0][1]), 2), round(float(ws[-1][1]), 2)) if ws else (0, 0)
    good = got == exp; ok &= good
    print(f"  {v:4s} {a:6.2f}-{b:6.2f} (bolum sonu {secend:6.2f})  ilk/son p={edge}  {'TAM' if got == exp else 'FARKLI: ' + ' '.join(got)}  -> {'temiz' if good else 'SORUN'}")
    ok &= b <= secend
print("== 2) Tam iz")
ws = tr(track); got = [g.replace("ladinoz", "ladinos").replace("ladinus", "ladinos") for g in norm([x[0] for x in ws])]
DLG = "Merhaba, kolay gelsin. Hoş bulduk. Ben bir iki gün Midyat'ta kalacağım. Nasıl bir oda öneriyorsunuz? Şans odası. Teşekkürler."
order = sorted([(a, dict((p, q) for p, q, r in promo.VO)[v]) for v, a, *_ in place] + [(next(x["f0"] for x in promo.SECS if x.get("dlg")) / promo.FPS, DLG)])
exp = norm(" ".join(t for _, t in order).split())
wl = [re.sub(r"[^\wçğıöşü]", "", x[0].lower()) for x in ws]; rep = [wl[i] for i in range(1, len(wl)) if wl[i] and wl[i] == wl[i - 1]]
print("  ardisik tekrar:", rep or "yok"); print("  metin:", "TAM" if got == exp else "FARKLI")
if got != exp:
    import difflib; print("  fark:", [d for d in difflib.ndiff(exp, got) if d[0] in "+-"])
ok &= not rep and got == exp
print("SONUC:", "GECTI" if ok else "KALDI")
