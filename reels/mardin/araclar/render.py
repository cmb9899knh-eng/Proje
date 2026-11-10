"""Mardin tanitim reels: goruntu kurgusu + efektler + grafikler + yerlesim kontrolu.
Kullanim: python3 render.py <work> <src> preview 30,150,...   -> secilen kareleri PNG yazar
          python3 render.py <work> <src> full [cikis.mp4]       -> tum videoyu kodlar (mix.wav ile)"""
import sys, json, re, subprocess, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import timeline, FPS
WORK, SRC, MODE = sys.argv[1], sys.argv[2], sys.argv[3]
W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
tl, T = timeline(); NF = int(round(T * FPS))
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FBO = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT = 230, 1500, 940     # Instagram arayuz guvenli alanlari

def row_at(t):
    for i, r in enumerate(tl):
        if r[0] <= t < r[1]: return i, r
    return len(tl) - 1, tl[-1]
def span(sec):
    rs = [r for r in tl if r[2]["sec"] == sec]; return rs[0][0], rs[-1][1]
REV = [r for r in tl if r[2]["sec"] == "reveal"][0]
WHIP0 = REV[0] + (3.0 - REV[2]["vi"]); WHIP1 = REV[0] + (4.4 - REV[2]["vi"])

# ---------------- kelimeler: cutcheck (konusma zamani) -> cikis zamani ----------------
SMAP = json.load(open(f"{WORK}/speech_map.json"))
def s2o(s):
    for s0, s1, t0, k, a in SMAP:
        if s0 - 1e-3 <= s < s1: return t0 + (s - s0)
    return SMAP[-1][2] + (s - SMAP[-1][0])
words = []
for line in open(os.path.join(HERE, "cutcheck_sonuc.txt")):
    m = re.match(r"\s+(-?[\d.]+)-\s*([\d.]+) (\S+)\s+p=", line)
    if m:
        s0, s1 = max(0.0, float(m[1])), float(m[2])
        # kelime baslangici bir parca sinirindan onceye tasarsa parcanin basina al
        seg = [x for x in SMAP if x[0] - 1e-3 <= s1 - 0.01 < x[1]][0]; s0 = max(s0, seg[0])
        words.append([s2o(s0) + 0.02, s2o(s1 - 1e-3), m[3]])
FIX = {"JEAN": "JİN", "RESTORANLA": "RESTORAN'LA"}   # Whisper yazimi -> soylenen/tabeladaki yazim (tabela: "Coffee JIN", "leyli")
def up(s):
    u = s.replace("i", "İ").replace("ı", "I").upper(); core = u.rstrip(".,?!"); return FIX.get(core, core) + u[len(core):]
FONT_SUB = ImageFont.truetype(FB, 74)
# anlam gruplari (kelime sayilari): MERHABA ARKADASLAR. / SIZLERE MARDIN / SOKAKLARINI TANITACAGIM. / SIMDI MARDIN /
# NEYLE MESHUR? / TABII KI BU / GUZEL SOKAKLARIYLA. / E BIR DE / MARDIN'IN NEYI MESHUR? / TABII KI BU / MERDIVENLERI. / AY /
# COK YORUCU. / SOLA DOGRU DONERSENIZ / EGER BIRAZ / YURUDUKTEN SONRA / CAFE JIN / VE LEYLI RESTORAN'LA / KARSILASACAKSINIZ. /
# KARISTIR, / GULUMSE. / YOLU / GOSTERIRSEN / DAHA GUZEL BIR / GORUNTU OLUR / ASLINDA. / SOYLE GOSTEREYIM / SIZLERE. / BU KADAR.
GROUPS = [2, 2, 2, 2, 2, 3, 2, 3, 3, 3, 1, 1, 2, 3, 2, 2, 2, 3, 1, 1, 1, 1, 1, 3, 2, 1, 2, 1, 2]
def chunks():
    assert sum(GROUPS) == len(words), (sum(GROUPS), len(words), [w[2] for w in words])
    out, i = [], 0
    for g in GROUPS: out.append([(up(w[2]), w[0], w[1]) for w in words[i:i + g]]); i += g
    res = []
    for i, c in enumerate(out):
        end = out[i + 1][0][1] if i + 1 < len(out) else c[-1][2] + 0.6
        seg_end = [r[1] for r in tl if "a" in r[2] and r[0] - 1e-3 <= c[-1][1] < r[1]]
        seg_end = max([r[1] for r in tl if "a" in r[2] and r[0] - 1e-3 <= c[-1][2] - 0.01 < r[1]] + seg_end) if seg_end else 1e9
        res.append((c[0][1], min(end, c[-1][2] + 0.6, seg_end), c))
    return res
CHUNKS = chunks()

# ---------------- yuzler ----------------
FACES = {}
def faces_of(k):
    if k not in FACES:
        p = f"{WORK}/faces_{k}.json"; FACES[k] = json.load(open(p)) if os.path.exists(p) else []
    return FACES[k]
NOFACE = {"A", "E", "F", "3062", "2957", "2975", "2986", "2974", "3088", "3086", "3078"}   # insan olmayan planlar (tespitler yanlis pozitif)
def heads(t):
    i, (t0, t1, e) = row_at(t); k = e["v"]; src = e["vi"] + (t - t0)
    if k in NOFACE: return []
    if k == "D" and src > 3.25: return []                           # savrulmadan sonra sokak, kisi yok
    out = []
    if k == "D": out.append((0, 1120, 340, 1920))                    # kadraja yarim giren yuz (elle)
    F = faces_of(k)
    if not F: return out
    n0 = int(round(src * FPS)); near = [b[2] - b[0] for m in range(max(0, n0 - 15), min(len(F), n0 + 16)) for b in F[m] if b[4] >= 0.7]
    medw = float(np.median(near)) if near else 1e9
    for dn in (-3, -2, -1, 0, 1, 2, 3):
        n = min(max(0, n0 + dn), len(F) - 1)
        best = max([b[4] for b in F[n]], default=0)
        for b in F[n]:
            x0, y0, x1, y1, s = b; w, h = x1 - x0, y1 - y0
            if s < 0.7 or w < 40 or w > 420 or h / w > 1.9 or w > 2.0 * medw: continue
            if best >= 0.85 and s < 0.85: continue   # karede net yuz varken dusuk skorlu ek tespit (ceket vb.) yanlis   # tek karelik dev tespit = yanlis
            out.append(transform_box((x0 - 0.30 * w, y0 - 0.60 * h, x1 + 0.30 * w, y1 + 0.28 * h), t))
    return out

# ---------------- renk, hareket, efekt ----------------
GRADE = {"B": (1.55, 0.80, 1.00), "A": (1.05, 0.95, 1.0), "E": (0.97, 1.03, 0.88), "F": (0.98, 1.02, 0.90),
         "2949": (0.98, 1.02, 0.90), "2954": (0.98, 1.02, 0.90), "2954b": (0.98, 1.02, 0.90), "3086": (0.98, 1.02, 0.90), "3088": (0.98, 1.02, 0.92)}
LUT = {}
def grade(img, k):
    g, gm, sat = GRADE.get(k, (1.0, 1.0, 0.97))
    if k not in LUT:
        x = np.arange(256) / 255.0; y = np.clip(g * x, 0, 1) ** gm
        y = y + 0.035 * np.sin(2 * np.pi * y) * -1 * (y < 1)            # hafif S egrisi (kontrast)
        LUT[k] = np.clip(y * 255, 0, 255).astype(np.uint8)
    img = cv2.LUT(img, LUT[k])
    if sat != 1.0:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= sat
        img = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    return img
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.22 * np.clip(np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.75)) ** 2) - 0.35, 0, 1) ** 1.5)[..., None].astype(np.float32)
GRAIN = [np.random.default_rng(i).normal(0, 3.2, (H // 2, W // 2, 1)).astype(np.float32) for i in range(6)]
def smooth(x): x = min(max(x, 0), 1); return x * x * (3 - 2 * x)
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x, c=1.7): x = min(max(x, 0), 1); return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def face_center(k, src):
    F = faces_of(k); n = min(int(round(src * FPS)), len(F) - 1) if F else -1
    if n >= 0:
        bs = [b for b in F[n] if b[4] > 0.7 and 40 < b[2] - b[0] < 420]
        if bs: b = max(bs, key=lambda b: b[2] - b[0]); return ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    return (540, 900)
def motion(t):
    """Klibin o anki olcek ve merkezi (yavas yaklasma/uzaklasma + vurus punch + yuz zoom)."""
    i, (t0, t1, e) = row_at(t); fx = e.get("fx", []); p = (t - t0) / (t1 - t0); s = 1.0; c = (540, 960)
    if "zc" in e: c = e["zc"]
    if "a" not in e:                                                 # konusmasiz planlar hep hafif hareketli
        s = 1.0 + 0.07 * smooth(p) if (i % 2 == 0 or "zoomin" in fx) else 1.07 - 0.07 * smooth(p)
    if "punch" in fx: s *= 1 + 0.09 * (1 - ease_out((t - t0) / 0.3))
    if "facezoom" in fx:
        c = face_center(e["v"], e["vi"] + 0.1); s *= 1 + 0.28 * ease_out((t - t0) / 0.22)
    if e["sec"] == "reveal" and t >= WHIP1: s *= 1 + 0.10 * (1 - ease_out((t - WHIP1) / 0.5))
    return s, c
def transform_box(b, t):
    s, (cx, cy) = motion(t)
    return (s * (b[0] - cx) + cx, s * (b[1] - cy) + cy, s * (b[2] - cx) + cx, s * (b[3] - cy) + cy)

CAPS = {}
def read_frame(k, src):
    if k not in CAPS: CAPS[k] = [cv2.VideoCapture(f"{SRC}/sdr_{k}.mp4"), -10]
    cap, last = CAPS[k]; n = int(round(src * FPS))
    if n != last + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, fr = cap.read()
    if not ok:
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, n - 2)); ok, fr = cap.read()
    CAPS[k][1] = n; return fr
def base_frame(t):
    i, (t0, t1, e) = row_at(t); k = e["v"]; fr = grade(read_frame(k, e["vi"] + (t - t0)), k)
    s, (cx, cy) = motion(t)
    if abs(s - 1) > 1e-3:
        M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]]); fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    # whip gecisi: kesimin +-0.1 sn cevresinde yatay hareket bulaniklik + kayma
    for j, (a0, a1, ee) in enumerate(tl):
        if "whip" in ee.get("fx", []) and abs(t - a0) < 0.1 and a0 > 0:
            k_ = 1 - abs(t - a0) / 0.1; L = int(10 + 110 * k_)
            ker = np.zeros((1, L), np.float32); ker[0, :] = 1 / L; fr = cv2.filter2D(fr, -1, ker)
            sh = int(90 * k_ * (1 if t < a0 else -1)); fr = np.roll(fr, sh, axis=1)
    out = fr.astype(np.float32) * VIG
    out += cv2.resize(GRAIN[int(t * FPS) % 6], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    # flas: kanca basi ve sokak acilisi
    for (ft, dur) in ((0.0, 0.25), (WHIP1, 0.3), (END0, 0.25)):
        if 0 <= t - ft < dur: out += 255 * 0.85 * (1 - (t - ft) / dur) ** 2
    # isik sizmasi: bolum gecislerinde sicak gradyan
    for sec in ("cats", "cafe", "outro"):
        st = span(sec)[0]; d = t - st + 0.15
        if 0 <= d < 0.7:
            a = np.sin(np.pi * d / 0.7) * 0.55; cxl = -200 + 1500 * d / 0.7
            g = np.exp(-(((xx - cxl) / 420.0) ** 2 + ((yy - 500) / 900.0) ** 2))[..., None]
            out += a * g * np.array([40, 140, 255], np.float32)            # BGR: sicak turuncu
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------- grafikler ----------------
YEL = (255, 196, 84, 255); WHITE = (255, 255, 255, 255); INK = (24, 18, 12, 255); RED = (214, 64, 44, 255)
def text_img(txt, font, fill, stroke=0, sf=(0, 0, 0, 255), track=0):
    asc, desc = font.getmetrics(); pad = stroke + 4
    w = int(sum(font.getlength(ch) for ch in txt) + track * (len(txt) - 1) + 2 * pad) if track else int(font.getlength(txt) + 2 * pad)
    im = Image.new("RGBA", (w, asc + desc + 2 * pad), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if track:
        x = pad
        for ch in txt: d.text((x, pad + asc), ch, font=font, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=sf); x += font.getlength(ch) + track
    else: d.text((pad, pad + asc), txt, font=font, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=sf)
    return im.crop(im.getbbox())
def shadow(im, r=12, a=0.5, dy=6):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    sh.alpha_composite(blk, (2 * r, 2 * r + dy)); sh = sh.filter(ImageFilter.GaussianBlur(r)); sh.alpha_composite(im, (2 * r, 2 * r)); return sh
def paste(c, im, cx, cy, s=1.0, alpha=1.0, rot=0.0):
    if s <= 0.01 or alpha <= 0.01: return
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def icon(kind, sz):
    im = Image.new("RGBA", (sz, int(sz * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); r = sz / 2
    if kind == "pin":
        d.ellipse((0, 0, sz - 1, sz - 1), fill=RED); d.polygon([(r * 0.28, r * 1.45), (sz - r * 0.28, r * 1.45), (r, sz * 1.28)], fill=RED)
        d.ellipse((r * 0.55, r * 0.55, sz - r * 0.55, sz - r * 0.55), fill=WHITE)
    elif kind == "book":
        d.rounded_rectangle((2, 6, r - 1, sz), radius=3, fill=RED); d.rounded_rectangle((r + 1, 6, sz - 2, sz), radius=3, fill=RED)
        d.line((r, 4, r, sz + 2), fill=WHITE, width=3)
    return im.crop(im.getbbox())
def pill(label, ic=None, maxw=820):
    f = ImageFont.truetype(FB, 46); t = text_img(label, f, INK); i_ = icon(ic, 34) if ic else None
    pad = 30; iw = (i_.width + 14) if i_ else 0; h = 84; w = t.width + 2 * pad + iw
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(255, 248, 236, 255))
    if i_: im.alpha_composite(i_, (pad - 4, (h - i_.height) // 2))
    im.alpha_composite(t, (pad + iw, (h - t.height) // 2)); im = shadow(im, 10, 0.35)
    if im.width > maxw: im = im.resize((maxw, int(im.height * maxw / im.width)), Image.LANCZOS)
    return im
PILLS = []   # (baslangic, bitis, gorsel, etiket)
last = None
for (t0, t1, e) in tl:
    p = e.get("pill")
    if p and p == last: PILLS[-1][1] = t1
    elif p:
        st = WHIP1 + 0.1 if e["sec"] == "reveal" else t0 + 0.12
        PILLS.append([st, t1, pill(*p), p[0]])
    last = p
TAG = shadow(text_img("GECE YÜRÜYÜŞÜ", ImageFont.truetype(FBO, 46), YEL, track=10), 10, 0.6, 4)
OUT_ROWS = [r for r in tl if r[2]["sec"] == "outro"]; BYE0 = OUT_ROWS[-2][0] + 0.55; END0 = OUT_ROWS[-1][0]
ENDT1 = shadow(text_img("GÖRÜŞÜRÜZ", ImageFont.truetype(FB, 96), WHITE, track=6), 14, 0.55, 6)
ENDT2 = shadow(text_img("MARDİN", ImageFont.truetype(FB, 150), YEL, track=8), 16, 0.55, 8)
def make_cta():
    f = ImageFont.truetype(FBO, 40); t = text_img("Kaydet, gezerken lazım olur", f, WHITE)
    h = 78; w = t.width + 100; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=(20, 16, 12, 190)); bx, by = 34, 20
    d.polygon([(bx, by), (bx + 26, by), (bx + 26, by + 38), (bx + 13, by + 28), (bx, by + 38)], fill=YEL)
    im.alpha_composite(t, (76, (h - t.height) // 2)); return shadow(im, 10, 0.4)
CTA = make_cta()
SUBC = {}
def sub_word(w, active):
    if (w, active) not in SUBC: SUBC[(w, active)] = text_img(w, FONT_SUB, YEL if active else WHITE, stroke=9)
    return SUBC[(w, active)]
def overlaps(box, hs, pad=8):
    x0, y0, x1, y1 = box
    return any(not (x1 + pad < h[0] or x0 - pad > h[2] or y1 + pad < h[1] or y0 - pad > h[3]) for h in hs)
def free_spot(key, start, end, tw, hg, cands, scales=(1.0, 0.85, 0.75, 0.65)):
    if key in SPOT: return SPOT[key]
    hs = []
    for tt in np.arange(start, end, 1 / FPS): hs += heads(tt)
    for sc in scales:
        for cx, cy in cands:
            x0 = cx - tw * sc / 2; box = (x0, cy - hg * sc / 2, x0 + tw * sc, cy + hg * sc / 2)
            if x0 >= 40 and box[2] <= SAFE_RIGHT - 10 and box[1] >= SAFE_TOP + 10 and box[3] <= SAFE_BOTTOM - 10 and not overlaps(box, hs):
                SPOT[key] = (cx, cy, sc); return SPOT[key]
    print("UYARI: bos yer yok", key); SPOT[key] = (cands[0][0], cands[0][1], scales[-1]); return SPOT[key]
SPOT = {}
SUB_CANDS = [(505, 1380), (505, 820), (505, 760), (560, 1380), (620, 1380), (450, 1380), (505, 1420), (505, 1300), (640, 1300), (660, 1220), (505, 1220), (505, 1140),
             (330, 1430), (700, 1430), (330, 1300), (720, 1300), (505, 900), (505, 800)]
TOP_CANDS = [(505, 340), (505, 300), (505, 380), (505, 420), (505, 460), (505, 520), (505, 620)]

def overlay(t):
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    h0 = span("hook")
    if t < h0[1]:   # kanca: tabelanin ustunde kucuk etiket
        a = ease_out((t - 0.25) / 0.35) * (1 - ease_out((t - h0[1] + 0.25) / 0.2))
        paste(c, TAG, 505, 340 + 20 * (1 - a), 1.0, a)
    for (s, e, im, lab) in PILLS:
        if s <= t < e:
            cx, cy, sc = free_spot(("pill", s), s, e, im.width, im.height, TOP_CANDS, (1.0, 0.85))
            wob = 3 * np.sin((t - s) * 9) * np.exp(-(t - s) * 3) if "?!" in lab else 0
            paste(c, im, cx, cy, sc * (0.6 + 0.4 * ease_back((t - s) / 0.25)), 1 - ease_out((t - e + 0.15) / 0.15), wob)
    for ci, (s, e, ws) in enumerate(CHUNKS):
        if not (s <= t < e): continue
        full = [sub_word(w, False) for (w, a, b) in ws]; sp = 24
        tw = sum(i.width for i in full) + sp * (len(full) - 1); hg = max(i.height for i in full)
        cx, cy, ss = free_spot(("sub", ci), s, e, tw, hg, SUB_CANDS); x = cx - tw * ss / 2
        for j, (w, a, b) in enumerate(ws):
            if t < a - 0.03: break
            act = a - 0.03 <= t < (ws[j + 1][1] - 0.03 if j + 1 < len(ws) else b + 0.15)
            sc = 0.7 + 0.3 * ease_back((t - a + 0.03) / 0.14)
            paste(c, sub_word(w, act), x + full[j].width * ss / 2, cy, sc * ss, min(1, (e - t) / 0.12))
            x += (full[j].width + sp) * ss
    if t >= END0:   # minare: "GORUSURUZ" + "MARDIN" + kaydet
        a1 = ease_back((t - END0 - 0.05) / 0.3); b = ease_back((t - END0 - 0.2) / 0.35)
        paste(c, ENDT1, 505, 860, 0.6 + 0.4 * a1, min(1, max(0, a1)))
        paste(c, ENDT2, 505, 1000, 0.6 + 0.4 * b, min(1, max(0, b)))
        paste(c, TAG, 505, 1120, 1.0, ease_out((t - END0 - 0.45) / 0.3))
        paste(c, CTA, 505, 1330, 0.8 + 0.2 * ease_back((t - END0 - 0.6) / 0.3), ease_out((t - END0 - 0.6) / 0.25))
    return c

def check(t, c):
    a = np.array(c.getchannel("A")); m = a > 10
    if not m.any(): return 0, 0
    face = sum(int(m[max(0, int(h[1])):max(0, int(h[3])), max(0, int(h[0])):max(0, int(h[2]))].sum()) for h in heads(t))
    ui = int(m[:SAFE_TOP].sum() + m[SAFE_BOTTOM:].sum() + m[SAFE_TOP:SAFE_BOTTOM, SAFE_RIGHT:].sum())
    return face, ui
def compose(n):
    t = n / FPS; fr = base_frame(t); ov = overlay(t)
    im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert("RGBA"); im.alpha_composite(ov)
    out = np.array(im.convert("RGB")); k = min(1, max(0, (T - t) / 0.4))
    if k < 1: out = (out * k).astype(np.uint8)
    return out, ov

if __name__ == "__main__":
    if MODE == "preview":
        os.makedirs(f"{WORK}/prev", exist_ok=True)
        for n in [int(x) for x in sys.argv[4].split(",")]:
            out, ov = compose(n); Image.fromarray(out).save(f"{WORK}/prev/{n:04d}.png"); print(n, f"{n / FPS:.2f}", "yuz/UI ihlal:", check(n / FPS, ov))
    else:
        dst = sys.argv[4] if len(sys.argv) > 4 else f"{WORK}/mardin_reels.mp4"
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                "-i", "-", "-i", f"{WORK}/mix.wav", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "slow",
                                "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high", "-colorspace", "bt709", "-color_primaries", "bt709",
                                "-color_trc", "bt709", "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", dst],
                               stdin=subprocess.PIPE)
        bf = bu = 0
        for n in range(NF):
            out, ov = compose(n); f_, u_ = check(n / FPS, ov); bf += f_ > 0; bu += u_ > 0
            enc.stdin.write(out.tobytes())
        enc.stdin.close(); enc.wait()
        print(f"kare={NF} yuz-cakisma kare={bf} arayuz-ihlal kare={bu}")
