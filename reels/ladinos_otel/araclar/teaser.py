"""Instagram hikaye teaser'i (~10,8 sn): otel adi gizli, "Bu aksam hesabimda" duyurusu.
Kullanim: python3 teaser.py <work> check|samples|full <cikis.mp4>"""
import sys, os, math, wave, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
WORK, MODE = sys.argv[1], sys.argv[2]; OUTP = sys.argv[3] if len(sys.argv) > 3 else None
sys.argv = [sys.argv[0], WORK, "x"]
import promo
from promo import W, H, FPS, R, grade, scale_about, timg, shadow, paste, ease_out, ease_back, FB, FXB, GOLD, WHITE, CREAM

BEAT = 0.6
# (klip, kaynak_bas, kare, hareket)  - otel adi/tabela gorunen planlar bilerek yok
SHOTS = [("IMG_3832", 0.30, 54, "push"),                                   # 0,0-1,8 kirmizi hali, giris
         ("IMG_3825", 0.40, 18, "push"), ("IMG_3830", 1.40, 18, "none"), ("IMG_3766", 1.80, 18, "none"),
         ("IMG_3771", 0.40, 18, "none"), ("IMG_3763", 1.60, 18, "none"), ("IMG_3792", 5.70, 18, "none"),
         ("IMG_3770", 2.00, 18, "none"), ("IMG_3807", 5.60, 18, "push"),   # 1,8-6,6 hizli montaj (vurus basina)
         ("IMG_3811", 0.40, 126, "push")]                                  # 6,6-10,8 kapanis + duyuru
F0 = np.cumsum([0] + [s[2] for s in SHOTS]); TOTAL = int(F0[-1])
NO_PERSON = {"IMG_3832", "IMG_3825", "IMG_3830", "IMG_3766", "IMG_3771", "IMG_3792", "IMG_3770", "IMG_3807"}
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 250, 1640, 1020, 60   # hikaye: ust profil cubugu, alt mesaj alani

def shot_at(n):
    i = int(np.searchsorted(F0, n, side="right") - 1); return i, n - F0[i]

def frame_bg(n):
    i, k = shot_at(n); c, a, m, mv = SHOTS[i]
    z = 1 + (0.08 if mv == "push" else 0.0) * k / max(1, m - 1)
    im = scale_about(R.get(c, round(a * FPS) + k), z)
    if i == 1 and k < 4: im = cv2.addWeighted(im, 1 - (1 - k / 4) * .8, np.full_like(im, 255), (1 - k / 4) * .8, 0)  # montaja flas
    if 1 <= i <= 8 and k < 2: im = scale_about(im, 1.06 - 0.03 * k)                                       # vurusta kucuk "punch"
    if i == len(SHOTS) - 1:   # kapanis: yavas kararma + vinyet (yazi okunurlugu)
        p = min(1, k / 90); yy, xx = np.mgrid[0:H, 0:W]; v = ((xx - 540) / 700) ** 2 + ((yy - 960) / 1100) ** 2
        im = (im * (1 - 0.55 * p * np.clip(v, 0, 1)[..., None]) * (1 - 0.35 * p)).astype(np.uint8)
    if n < 6: im = (im * (n / 6)).astype(np.uint8)
    if n >= TOTAL - 10: im = (im * ((TOTAL - 1 - n) / 10)).astype(np.uint8)
    return grade(im)

def heads(n):
    i, k = shot_at(n); c, a, m, mv = SHOTS[i]
    if c in NO_PERSON: return []
    fr = promo.AN[c]; j = round(a * FPS) + k; cand = fr[min(j, len(fr) - 1)][5]
    if not cand:
        for d in range(1, 16):
            for jj in (j - d, j + d):
                if 0 <= jj < len(fr) and fr[jj][5]: cand = fr[jj][5]; break
            if cand: break
    z = 1 + (0.08 if mv == "push" else 0.0) * k / max(1, m - 1); out = []
    for x, y, w, h, sc in cand:
        x0, y0, x1, y1 = x - 0.30 * w, y - 0.55 * h, x + 1.30 * w, y + 1.15 * h
        out.append(((x0 - 540) * z + 540, (y0 - 960) * z + 960, (x1 - 540) * z + 540, (y1 - 960) * z + 960))
    return out

EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
    return im.resize((int(im.width * size / im.height), size), Image.LANCZOS)
def line(parts, size, col):
    ims = [emoji(p[1:], int(size * 1.05)) if p.startswith("@") else timg(p, ImageFont.truetype(FB, size), col) for p in parts]
    w = sum(i.width for i in ims) + 16 * (len(ims) - 1); h = max(i.height for i in ims)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); x = 0
    for i in ims: out.alpha_composite(i, (x, (h - i.height) // 2)); x += i.width + 16
    return out
def card(lines, pad=(46, 30), bg=(20, 16, 12, 150)):
    w = max(l.width for l in lines) + 2 * pad[0]; h = sum(l.height for l in lines) + 18 * (len(lines) - 1) + 2 * pad[1]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=34, fill=bg); y = pad[1]
    for l in lines: im.alpha_composite(l, ((w - l.width) // 2, y)); y += l.height + 18
    return shadow(im, 12, 0.35)
T1 = card([line(["Midyat'ta çok özel"], 60, WHITE), line(["bir yer keşfettim…", "@🤫"], 60, WHITE)])
T2 = shadow(line(["Neresi mi?", "@👀"], 92, WHITE), 14, 0.7)
T3 = card([line(["BU AKŞAM"], 104, GOLD), line(["hesabımda!"], 70, WHITE)], bg=(20, 16, 12, 170))
EV = [(0.15, 1.75, T1, 540, 520), (7.0, 10.8, T2, 540, 400), (8.1, 10.8, T3, 540, 590)]

def render(n):
    t = n / FPS; c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for a, b, im, cx, cy in EV:
        if a <= t < b:
            p = ease_back((t - a) / 0.3); al = min(1, (t - a) / 0.15) * (1 - ease_out((t - (b - 0.15)) / 0.15))
            paste(c, im, cx, cy, 0.85 + 0.15 * p, al)
    return c

def compose(n):
    im = Image.fromarray(cv2.cvtColor(frame_bg(n), cv2.COLOR_BGR2RGB)).convert("RGBA"); im.alpha_composite(render(n)); return im.convert("RGB")

# ---- ses: gerilimli kisa altlik (numpy sentezi) ----
def audio(path):
    SR = 48000; N = int(TOTAL / FPS * SR); out = np.zeros((N + SR, 2)); rng = np.random.default_rng(3)
    from scipy.signal import butter, sosfilt, resample_poly
    import pyloudnorm as pyln
    lp = lambda x, f: sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
    bp = lambda x, a, b: sosfilt(butter(2, [a, b], "band", fs=SR, output="sos"), x)
    ex = lambda n, tau: np.exp(-np.arange(n) / (tau * SR)); mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    def add(sig, t, g=1.0, pan=0.0):
        i = max(0, int(t * SR)); L = min(len(sig), len(out) - i); out[i:i + L, 0] += sig[:L] * g * math.sqrt(.5 * (1 - pan)); out[i:i + L, 1] += sig[:L] * g * math.sqrt(.5 * (1 + pan))
    def oud(f, d=1.0):
        P = int(round(SR / f)); n = int(d * SR); y = np.zeros(n + P); y[:P] = lp(rng.uniform(-1, 1, P), 4000)
        for s in range(P, n + P, P):
            pr = y[s - P:s]; y[s:s + P] = (0.988 * 0.5 * (pr + np.r_[pr[-1], pr[:-1]]))[:len(y[s:s + P])]
        y = y[P:]; return y / (np.abs(y).max() + 1e-9)
    def pad(fs, d):
        n = int(d * SR); t = np.arange(n) / SR
        y = sum(np.sin(2 * np.pi * f * (1 + dt) * t) for f in fs for dt in (-.005, 0, .004))
        return lp(y * np.minimum(1, t / .6) * np.minimum(1, (d - t) / .8), 1400) / (3 * len(fs))
    def doum():
        n = int(.4 * SR); t = np.arange(n) / SR; f = 70 + 100 * np.exp(-t / .03); return np.sin(2 * np.pi * np.cumsum(f) / SR) * ex(n, .12)
    def tek():
        n = int(.1 * SR); t = np.arange(n) / SR; return .6 * bp(rng.standard_normal(n), 1800, 6500) * ex(n, .012) + .5 * np.sin(2 * np.pi * 690 * t) * ex(n, .03)
    D = TOTAL / FPS
    add(pad([mtof(m) for m in (50, 57, 62, 65)], D + .5), 0, .9)                          # Dm (sus)
    for k, m in enumerate([74, 73, 74, 77]): add(oud(mtof(m)), .3 + k * .3, .45)           # acilis motifi (Re armonik minor)
    for b in range(8):                                                                      # 1,8-6,6: vurus basina dum + tek
        t0 = 1.8 + b * BEAT; add(doum(), t0, .9); add(tek(), t0 + BEAT / 2, .5, .3)
        add(oud(mtof([69, 70, 73, 74, 76, 77, 73, 74][b])), t0, .4, -.2)
    n = int(1.2 * SR); p = np.linspace(0, 1, n)                                             # riser -> 6,6
    add(bp(rng.standard_normal(n), 800, 7000) * p ** 2.2 / 3, 6.6 - 1.2, .55)
    n2 = int(1.4 * SR); t2 = np.arange(n2) / SR; f2 = 38 + 70 * np.exp(-t2 / .05)            # impact (Neresi mi?)
    imp = np.sin(2 * np.pi * np.cumsum(f2) / SR) * ex(n2, .35); add(imp, 7.0, .9); add(imp, 8.1, .7)
    for f, g in ((1318.5, .22), (1760, .16), (2637, .1)):                                    # BU AKSAM: parilti
        n3 = int(2.2 * SR); t3 = np.arange(n3) / SR; add(np.sin(2 * np.pi * f * t3) * ex(n3, .6) * np.minimum(1, t3 / .02), 8.1, g)
    out = out[:N]; fl = int(.6 * SR); out[-fl:] *= np.linspace(1, 0, fl)[:, None]
    meter = pyln.Meter(SR)
    from scipy.ndimage import minimum_filter1d, uniform_filter1d
    for _ in range(5):   # -14 LUFS hedefi + ileri-bakisli limitor (-1,5 dBTP)
        out *= 10 ** ((-14 - meter.integrated_loudness(out)) / 20)
        g = np.minimum(1, 10 ** (-1.8 / 20) / np.maximum(np.abs(out).max(1), 1e-9))
        g = uniform_filter1d(minimum_filter1d(g, int(0.006 * SR)), int(0.004 * SR)); out *= g[:, None]
    w = wave.open(path, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    print(f"ses: {meter.integrated_loudness(out):.2f} LUFS, tepe {20*math.log10(np.abs(resample_poly(out,4,1,axis=0)).max()):.2f} dBTP")

if __name__ == "__main__":
    if MODE == "check":
        bad = ui = 0
        for n in range(TOTAL):
            a = np.array(render(n).getchannel("A")); ys, xs = np.nonzero(a > 8)
            if not len(ys): continue
            for hb in heads(n):
                x0, y0, x1, y1 = [max(0, int(v)) for v in hb]; bad += int((a[y0:y1, x0:x1] > 8).sum() > 0)
            ui += int(ys.min() < SAFE_TOP or ys.max() > SAFE_BOTTOM or xs.max() > SAFE_RIGHT or xs.min() < SAFE_LEFT)
        print(f"kare={TOTAL} ({TOTAL/FPS:.1f} sn)  yuz/kafa cakismasi={bad}  hikaye arayuz ihlali={ui}  ->", "GECTI" if not bad and not ui else "KALDI")
    elif MODE == "samples":
        ts = [0.9, 2.1, 2.7, 3.3, 3.9, 4.5, 5.1, 5.7, 6.3, 7.5, 9.0, 10.3]; tiles = []
        f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 26)
        for t in ts:
            th = compose(int(t * FPS)).resize((270, 480), Image.LANCZOS); d = ImageDraw.Draw(th); d.rectangle((0, 0, 110, 34), fill=(0, 0, 0)); d.text((6, 3), f"{t:.1f} sn", font=f, fill="white"); tiles.append(th)
        sh = Image.new("RGB", (6 * 276 + 6, 2 * 486 + 6), "white")
        for i, th in enumerate(tiles): sh.paste(th, (6 + (i % 6) * 276, 6 + (i // 6) * 486))
        sh.save(os.path.join(WORK, "teaser_kareler.jpg"), quality=88); print("ok")
    elif MODE == "full":
        wav = os.path.join(WORK, "teaser.wav"); audio(wav)
        p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                              "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-b:v", "6000k", "-maxrate", "8000k", "-bufsize", "12000k",
                              "-profile:v", "high", "-level", "4.1", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                              "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUTP], stdin=subprocess.PIPE)
        for n in range(TOTAL): p.stdin.write(np.asarray(compose(n)).tobytes())
        p.stdin.close(); p.wait(); print("yazildi:", OUTP)
