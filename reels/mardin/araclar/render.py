"""Mardin reels: goruntu kurgusu + grafikler + yerlesim kontrolu.
Kullanim: python3 render.py <work> <src> preview 30,150,...   -> secilen kareleri PNG olarak yazar
          python3 render.py <work> <src> full                  -> tum videoyu kodlar (mix.wav ile)"""
import sys, json, re, math, subprocess, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import timeline
WORK, SRC, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
tl, T = timeline(); NF = int(round(T * FPS))
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FXB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FBO = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FSB = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
# Instagram arayuz guvenli alanlari
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT = 230, 1500, 940

# ---------------- zaman ----------------
SEG = {"A": 0, "B": 1, "F1": 2, "C1": 3, "C2": 4, "D": 5, "E": 6, "F2": 7}
def seg_at(t):
    for i, r in enumerate(tl):
        if r[0] <= t < r[1] or (i == len(tl) - 1 and t >= r[0]): return i, r
SPEECH0 = tl[3][0]; OUTRO = tl[5][1]; D_START = tl[5][0]; D_SRC0 = tl[5][3]
WHIP0 = D_START + (3.0 - D_SRC0); WHIP1 = D_START + (4.4 - D_SRC0)

# ---------------- kelimeler (cutcheck ciktisindan; konusma zamani -> cikis zamani) ----------------
words = []
for line in open(os.path.join(HERE, "cutcheck_sonuc.txt")):
    m = re.match(r"\s+([\d.]+)-\s*([\d.]+) (\S+)\s+p=", line)
    if m: words.append([float(m[1]) + SPEECH0, float(m[2]) + SPEECH0, m[3]])
words[0][0] = SPEECH0 + 0.03   # "Evet" gercek baslangici (enerji olcumu)
# Whisper "Yolu"yu kesimden once baslatiyor; gercek ses baslangici D kaynak 2.16 sn (enerji olcumu)
for w in words:
    if w[2].lower().startswith("yolu"): w[0] = D_START + (2.16 - D_SRC0)
# speech bolumundeki kesimler konusma zamaninda sabit -> cikis zamaninda da sabit (hiz degismedi)
def up(s): return s.replace("i", "İ").replace("ı", "I").upper()
FONT_SUB = ImageFont.truetype(FB, 74)
GROUPS = [[0, 1], [2, 3], [4], [5, 6], [7], [8, 9], [10, 11], [12, 13], [14], [15], [16], [17, 18, 19], [20, 21], [22], [23, 24], [25]]
def chunks():
    assert sum(len(g) for g in GROUPS) == len(words), (len(words), [w[2] for w in words])
    res = []
    for i, g in enumerate(GROUPS):
        c = [(up(words[j][2]), words[j][0], words[j][1]) for j in g]
        start = c[0][1]; end = words[GROUPS[i + 1][0]][0] if i + 1 < len(GROUPS) else c[-1][2] + 0.6
        res.append((start, min(end, c[-1][2] + 0.7), c))
    return res
CHUNKS = chunks()

# ---------------- yuzler ----------------
FACES = {k: json.load(open(f"{WORK}/faces_{k}.json")) for k in "CD"}
def heads(t):
    """O andaki bas kutulari (yuz kutusu sac/ortu payiyla genisletilmis), cikis koordinatinda."""
    i, r = seg_at(t); k = r[2]
    if k not in "CD": return []
    src = r[3] + (t - r[0]); out = []
    if k == "D" and src > 3.25: return []      # savrulma sonrasi kisi yok (sokak)
    if k == "D": out.append((0, 1120, 340, 1920))  # yarim kadraj yuzun (dedektor kenarda kaciriyor) - elle

    for dn in (-3, -2, -1, 0, 1, 2, 3):        # +-3 kare birlesim (titreme payi)
        n = min(max(0, int(round(src * FPS)) + dn), len(FACES[k]) - 1)
        for b in FACES[k][n]:
            x0, y0, x1, y1, s = b; w, h = x1 - x0, y1 - y0
            if s < 0.7 or w < 90 or w > 420 or h / w > 1.9: continue  # >420 px: bulanik karede yanlis tespit
            out.append((x0 - 0.30 * w, y0 - 0.60 * h, x1 + 0.30 * w, y1 + 0.28 * h))
    return out

# ---------------- renk ve hareket ----------------
GRADE = {  # kazanc, gamma, doygunluk
    "A": (1.05, 0.95, 1.00), "B": (1.55, 0.80, 1.00), "C": (1.0, 1.0, 0.95), "D": (1.08, 0.95, 0.95),
    "E": (0.97, 1.03, 0.88), "F": (0.98, 1.02, 0.90)}
ZOOM = {0: (1.00, 1.10, (540, 760)), 1: (1.09, 1.00, (540, 900)), 2: (1.00, 1.06, (540, 1000)),
        6: (1.00, 1.08, (540, 1100)), 7: (1.06, 1.00, (540, 1000))}
LUT = {}
def grade(img, k):
    g, gm, sat = GRADE[k]
    if k not in LUT:
        x = np.arange(256) / 255.0; y = np.clip(g * x, 0, 1) ** gm
        y = y + 0.04 * np.sin(np.pi * y) * (y - 0.5) * 2 * 0  # (S egrisi kapali)
        LUT[k] = np.clip(y * 255, 0, 255).astype(np.uint8)
    img = cv2.LUT(img, LUT[k])
    if sat != 1.0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= sat
        img = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    return img
VIG = None
def vignette(img):
    global VIG
    if VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2)
        VIG = (1 - 0.22 * np.clip(r - 0.35, 0, 1) ** 1.5)[..., None].astype(np.float32)
    return (img.astype(np.float32) * VIG).astype(np.uint8)
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
CAPS = {}
def base_frame(t):
    i, r = seg_at(t); t0, t1, k, a, b, _ = r; src = a + (t - t0)
    key = k
    if key not in CAPS: CAPS[key] = [cv2.VideoCapture(f"{SRC}/sdr_{k}.mp4"), -1]
    cap, last = CAPS[key]; n = int(round(src * FPS))
    if n != last + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = cap.read(); CAPS[key][1] = n
    if not ok: cap.set(cv2.CAP_PROP_POS_FRAMES, n - 1); ok, fr = cap.read()
    fr = grade(fr, k)
    if i in ZOOM:
        s0, s1, (cx, cy) = ZOOM[i]; s = s0 + (s1 - s0) * smooth((t - t0) / (t1 - t0))
        M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]]); fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC)
    return vignette(fr)

# ---------------- grafik yardimcilari ----------------
YEL = (255, 196, 84, 255); WHITE = (255, 255, 255, 255); INK = (24, 18, 12, 255)
def ease_back(x, c=1.7):
    x = min(max(x, 0), 1); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def text_img(txt, font, fill, stroke=0, sf=(0, 0, 0, 255), track=0):
    if track:
        asc, desc = font.getmetrics(); pad = stroke + 4
        w = int(sum(font.getlength(ch) for ch in txt) + track * (len(txt) - 1) + 2 * pad); h = asc + desc + 2 * pad
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = pad
        for ch in txt:
            d.text((x, pad + asc), ch, font=font, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=sf); x += font.getlength(ch) + track
        return im.crop(im.getbbox())
    b = font.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sf)
    return im
def shadow(im, r=12, a=0.5, dy=6):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    sh.alpha_composite(blk, (2 * r, 2 * r + dy)); sh = sh.filter(ImageFilter.GaussianBlur(r)); sh.alpha_composite(im, (2 * r, 2 * r))
    return sh
def paste(c, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01: return
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def pin_icon(sz, col):
    im = Image.new("RGBA", (sz, int(sz * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = sz / 2
    d.ellipse((0, 0, sz - 1, sz - 1), fill=col); d.polygon([(r * 0.28, r * 1.45), (sz - r * 0.28, r * 1.45), (r, sz * 1.28)], fill=col)
    d.ellipse((r * 0.55, r * 0.55, sz - r * 0.55, sz - r * 0.55), fill=(255, 255, 255, 255)); return im
def arrow_icon(sz, col):
    im = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.line((sz * 0.1, sz / 2, sz * 0.8, sz / 2), fill=col, width=int(sz * 0.18))
    d.polygon([(sz * 0.55, sz * 0.18), (sz * 0.98, sz / 2), (sz * 0.55, sz * 0.82)], fill=col); return im
def pill(label, icon=None):
    f = ImageFont.truetype(FB, 46); t = text_img(label, f, INK)
    ic = pin_icon(34, (214, 64, 44, 255)) if icon == "pin" else (arrow_icon(40, (214, 64, 44, 255)) if icon == "arrow" else None)
    pad = 30; iw = (ic.width + 14) if ic else 0; h = 84; w = t.width + 2 * pad + iw
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(255, 248, 236, 255))
    if ic: im.alpha_composite(ic, (pad - 4, (h - ic.height) // 2 + 1))
    im.alpha_composite(t, (pad + iw, (h - t.height) // 2 - 2)); return shadow(im, 10, 0.35)

# statik ogeler
TITLE = shadow(text_img("MARDİN", ImageFont.truetype(FB, 170), WHITE, track=10), 16, 0.55, 8)
TAG = shadow(text_img("GECE YÜRÜYÜŞÜ", ImageFont.truetype(FBO, 44), YEL, track=10), 10, 0.6, 4)
def make_card():
    w, h = 470, 196; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=(20, 16, 12, 205))
    d.rounded_rectangle((26, 30, 32, h - 30), radius=3, fill=YEL)
    im.alpha_composite(text_img("ULU CAMİİ MİNARESİ", ImageFont.truetype(FB, 36), WHITE), (52, 30))
    im.alpha_composite(text_img("Kaidesindeki kitabe:", ImageFont.truetype(FSB, 30), (235, 225, 210, 255)), (52, 84))
    im.alpha_composite(text_img("1176", ImageFont.truetype(FB, 50), YEL), (52, 124))
    return shadow(im, 14, 0.45)
CARD = make_card()
PILLS = [(SPEECH0 + 0.58, SPEECH0 + 5.40, pill("MEYDANIN ÜST SOKAĞI", "pin")),
         (SPEECH0 + 5.56, D_START + 0.10, pill("ÇARŞININ ORTASINA", "arrow")),
         (WHIP1 + 0.10, OUTRO - 0.05, pill("ÇARŞIYA DOĞRU", "pin"))]
END0 = tl[-1][0] + 0.6
ENDT = shadow(text_img("MARDİN", ImageFont.truetype(FB, 120), WHITE, track=8), 14, 0.55, 6)
def make_cta():
    f = ImageFont.truetype(FBO, 40); t = text_img("Kaydet, gezerken lazım olur", f, WHITE)
    h = 78; w = t.width + 100; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(20, 16, 12, 190))
    bx, by = 34, 20  # yer imi ikonu
    d.polygon([(bx, by), (bx + 26, by), (bx + 26, by + 38), (bx + 13, by + 28), (bx, by + 38)], fill=YEL)
    im.alpha_composite(t, (76, (h - t.height) // 2 - 2)); return shadow(im, 10, 0.4)
CTA = make_cta()
SUBCACHE = {}
def sub_word(w, active):
    k = (w, active)
    if k not in SUBCACHE: SUBCACHE[k] = text_img(w, FONT_SUB, YEL if active else WHITE, stroke=9, sf=(0, 0, 0, 255))
    return SUBCACHE[k]

def overlaps(box, hs, pad=8):
    x0, y0, x1, y1 = box
    return any(not (x1 + pad < h[0] or x0 - pad > h[2] or y1 + pad < h[1] or y0 - pad > h[3]) for h in hs)
SUB_POS = {}
def sub_position(ci, start, end, total_w, hgt):
    """Altyazi icin gogus hizasinda yer: bu parcanin suresince hicbir basla cakismayan en yakin konum."""
    if ci in SUB_POS: return SUB_POS[ci]
    hs = []
    for tt in np.arange(start, end, 1 / FPS): hs += heads(tt)
    cands = [(505, 1380)] + [(x, 1380) for x in (560, 600, 640, 450)] + [(505, y) for y in (1420, 1340, 1300)] + \
            [(x, y) for y in (1420, 1340) for x in (600, 650, 700)]
    for sc in (1.0, 0.85, 0.75, 0.65):
        tw, hg = total_w * sc, hgt * sc
        for cx, cy in cands + [(x, y) for y in (1400, 1300, 1220) for x in (640, 660, 680, 690, 700)]:
            x0 = cx - tw / 2; box = (x0, cy - hg / 2, x0 + tw, cy + hg / 2)
            if x0 >= 50 and x0 + tw <= SAFE_RIGHT - 10 and box[3] <= SAFE_BOTTOM - 10 and not overlaps(box, hs):
                SUB_POS[ci] = (cx, cy, sc); return SUB_POS[ci]
    SUB_POS[ci] = (505, 1380, 1.0); print("UYARI: altyazi icin bos yer yok", ci); return SUB_POS[ci]

def overlay(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # 1) acilis basligi (minare)
    if t < tl[0][1] + 0.05:
        a = ease_out((t - 0.35) / 0.5) * (1 - ease_out((t - 3.65) / 0.3))
        paste(c, TITLE, 505, 1010 - 30 * ease_out((t - 0.35) / 0.6), 1.0, a)
        paste(c, TAG, 505, 1135, 1.0, ease_out((t - 0.7) / 0.4) * (1 - ease_out((t - 3.65) / 0.3)))
        if t >= 1.9:  # bilgi karti
            p = ease_back((t - 1.9) / 0.3); al = 1 - ease_out((t - 3.7) / 0.25)
            paste(c, CARD, 290 - 40 * (1 - ease_out((t - 1.9) / 0.3)), 1340, 0.85 + 0.15 * p, al)
    # 2) bas ustu notlar
    for (s, e, im) in PILLS:
        if s <= t < e:
            hs = heads(t); cy = 340
            if hs: cy = min(340, max(SAFE_TOP + 60, min(h[1] for h in hs) - 70))
            paste(c, im, 505, cy, 0.6 + 0.4 * ease_back((t - s) / 0.25), 1 - ease_out((t - e + 0.2) / 0.2))
    # 3) kelime kelime altyazi
    for ci, (s, e, ws) in enumerate(CHUNKS):
        if not (s <= t < e): continue
        full = [sub_word(w, False) for (w, a, b) in ws]; sp = 24
        tw = sum(i.width for i in full) + sp * (len(full) - 1); hg = max(i.height for i in full)
        cx, cy, ss = sub_position(ci, s, e, tw, hg); x = cx - tw * ss / 2
        shown = [(w, a, b) for (w, a, b) in ws if t >= a - 0.03]
        for j, (w, a, b) in enumerate(shown):
            act = a - 0.03 <= t < (ws[j + 1][1] - 0.03 if j + 1 < len(ws) else b + 0.15)
            im = sub_word(w, act); sc = 0.7 + 0.3 * ease_back((t - a + 0.03) / 0.14)
            paste(c, im, x + full[j].width * ss / 2, cy, sc * ss, min(1, (e - t) / 0.12))
            x += (full[j].width + sp) * ss
    # 4) kapanis
    if t >= END0:
        a = ease_out((t - END0) / 0.5)
        paste(c, ENDT, 505, 520 - 24 * (1 - a), 1.0, a)
        paste(c, TAG, 505, 625, 1.0, ease_out((t - END0 - 0.25) / 0.4))
        paste(c, CTA, 505, 1330, 0.8 + 0.2 * ease_back((t - END0 - 0.9) / 0.3), ease_out((t - END0 - 0.9) / 0.25))
    return c

def check(t, c):
    a = np.array(c.getchannel("A")); ys, xs = np.nonzero(a > 10)
    if not len(ys): return 0, 0
    face = sum(int((a[max(0, int(h[1])):max(0, int(h[3])), max(0, int(h[0])):max(0, int(h[2]))] > 10).sum()) for h in heads(t))
    ui = int((a[:SAFE_TOP] > 10).sum() + (a[SAFE_BOTTOM:] > 10).sum() + (a[SAFE_TOP:SAFE_BOTTOM, SAFE_RIGHT:] > 10).sum())
    return face, ui

def fade_black(t):  # son 0.45 sn karartma
    return min(1, max(0, (T - t) / 0.45))

def compose(n):
    t = n / FPS; fr = base_frame(t); ov = overlay(t)
    im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA"); im.alpha_composite(ov)
    out = np.array(im.convert("RGB")); k = fade_black(t)
    if k < 1: out = (out * k).astype(np.uint8)
    return out, ov

if __name__ == "__main__":
    if MODE == "preview":
        os.makedirs(f"{WORK}/prev", exist_ok=True)
        for n in [int(x) for x in sys.argv[4].split(",")]:
            out, ov = compose(n); Image.fromarray(out).save(f"{WORK}/prev/{n:04d}.png"); print(n, n / FPS, "yuz/UI ihlal:", check(n / FPS, ov))
    else:
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                "-i", "-", "-i", f"{WORK}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709",
                                "-color_trc", "bt709", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart",
                                sys.argv[4] if len(sys.argv) > 4 else f"{WORK}/mardin_reels.mp4"], stdin=subprocess.PIPE)
        bad_face = bad_ui = 0
        for n in range(NF):
            out, ov = compose(n); f_, u_ = check(n / FPS, ov); bad_face += f_ > 0; bad_ui += u_ > 0
            enc.stdin.write(out.tobytes())
        enc.stdin.close(); enc.wait()
        print(f"kare={NF} yuz-cakisma kare={bad_face} arayuz-ihlal kare={bad_ui}")
