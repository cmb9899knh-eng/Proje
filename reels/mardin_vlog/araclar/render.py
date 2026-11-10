"""Mardin vlog reels — grafik/altyazi yerlesimi + kompozit.
Kullanim:
  python3 render.py samples t1,t2,...   -> ornek kareler (PNG) + guvenli alan raporu
  python3 render.py full                -> work/video_noaudio.mp4 (tum kareler) + guvenli alan raporu
Kurallar (her karede kontrol edilir):
  * Hicbir grafik/altyazi bir yuz (bas kutusu) ile kesismez.
  * Instagram arayuzu: ust 230 px, alt y>1500, sag serit x>940 bos kalir.
"""
import sys, json, math, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import timeline, FPS

W, H = 1080, 1920
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 230, 1500, 940, 40
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FXB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FSB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
RED, YEL, WHITE, INK = (200, 30, 45, 255), (255, 214, 10, 255), (255, 255, 255, 255), (15, 15, 20, 255)

TL = timeline()
DUR = TL[-1]["t1"]; N = round(DUR * FPS)
FACES_RAW = json.load(open("faces.json"))
def _iou(a, b):
    ax1, ay1, ax2, ay2 = a[0], a[1], a[0] + a[2], a[1] + a[3]; bx1, by1, bx2, by2 = b[0], b[1], b[0] + b[2], b[1] + b[3]
    iw = max(0, min(ax2, bx2) - max(ax1, bx1)); ih = max(0, min(ay2, by2) - max(ay1, by1)); i = iw * ih
    return i / (a[2] * a[3] + b[2] * b[3] - i + 1e-9)
def _stable(L):
    """Zamansal tutarlilik: +-3 karelik komsulukta en az 2 karede eslesen yuz tutulur (tek karelik yanlis algilamalar atilir)."""
    out = []
    for i, fs in enumerate(L):
        keep = []
        strong = [g for g in fs if g[4] >= 0.9]
        for f in fs:
            # el/mikrofon uzerindeki yanlis algilama: dusuk puanli ve guclu bir yuzun hemen altinda
            if f[4] < 0.85 and any(f[1] + f[3] / 2 > g[1] + g[3] and f[0] < g[0] + g[2] and g[0] < f[0] + f[2] for g in strong):
                continue
            hits = sum(1 for j in range(max(0, i - 3), min(len(L), i + 4)) if j != i and any(_iou(f, g) > 0.3 for g in L[j]))
            if hits >= 2: keep.append(f)
        out.append(keep)
    return out
FACES = {k: _stable(v) for k, v in FACES_RAW.items()}
WORDS = json.load(open("words.json"))

def seg_at(t):
    n = round(t * FPS)
    for x in TL:
        if round(x["t0"] * FPS) <= n < round(x["t1"] * FPS): return x
    return TL[-1]

def src_frame(x, t):
    return round(x["s"] * FPS) + round(t * FPS) - round(x["t0"] * FPS)

def head_boxes(t):
    """Basi tamamen kapsayan kutular (yuz + basortusu/sac payi + cene)."""
    x = seg_at(t)
    if x["kind"].startswith("split"): return []          # bolunmus ekranda yalnizca kucuk yanlis pozitifler var
    L = FACES[x["clip"]]; i = min(len(L) - 1, src_frame(x, t))
    out = []
    for fx, fy, fw, fh, sc in L[i]:
        if fh < 40 or sc < 0.7: continue                  # cok kucuk/uzak yuzler: yine de koruyalim mi? (asagida)
        out.append((fx - 0.35 * fw, fy - 0.55 * fh, fx + 1.35 * fw, fy + 1.25 * fh))
    for fx, fy, fw, fh, sc in L[i]:                       # uzak yayalar: kucuk ama korunur
        if fh < 40 and sc >= 0.8: out.append((fx - 0.5 * fw, fy - 0.8 * fh, fx + 1.5 * fw, fy + 1.4 * fh))
    return out

def inter(a, b, pad=18):
    return not (a[2] + pad <= b[0] or b[2] + pad <= a[0] or a[3] + pad <= b[1] or b[3] + pad <= a[1])

# ---------------------------------------------------------------- yazi yardimcilari
def text_img(txt, font, fill, stroke=0, stroke_fill=INK):
    b = font.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 6, b[3] - b[1] + 6), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((3 - b[0], 3 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def with_shadow(im, r=12, a=0.45, dy=6):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r + dy), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: int(v * a))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(m)
    sh.paste(blk, (2 * r, 2 * r + dy), blk); sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (2 * r, 2 * r)); return sh, 2 * r

def ease_back(x):
    x = min(max(x, 0), 1); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

# ---------------------------------------------------------------- ikonlar (vektor, elle cizilmis)
def icon(kind, s, col=WHITE):
    im = Image.new("RGBA", (s * 4, s * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); S = s * 4
    if kind == "pin":
        d.ellipse((S*.18, S*.05, S*.82, S*.69), fill=col)
        d.polygon([(S*.24, S*.50), (S*.76, S*.50), (S*.5, S*.97)], fill=col)
        d.ellipse((S*.36, S*.23, S*.64, S*.51), fill=(0, 0, 0, 0))
    elif kind == "cup":
        d.rounded_rectangle((S*.10, S*.32, S*.70, S*.90), radius=int(S*.12), fill=col)
        d.ellipse((S*.58, S*.42, S*.94, S*.76), outline=col, width=int(S*.09))
        for x0 in (.24, .44):
            d.line([(S*x0, S*.24), (S*(x0+.05), S*.14), (S*x0, S*.04)], fill=col, width=int(S*.06))
    elif kind == "bag":
        d.rounded_rectangle((S*.12, S*.32, S*.88, S*.94), radius=int(S*.08), fill=col)
        d.arc((S*.30, S*.06, S*.70, S*.50), 180, 360, fill=col, width=int(S*.08))
    elif kind == "candy":
        d.ellipse((S*.20, S*.28, S*.80, S*.72), fill=col)
        d.polygon([(S*.22, S*.5), (S*.02, S*.30), (S*.02, S*.70)], fill=col)
        d.polygon([(S*.78, S*.5), (S*.98, S*.30), (S*.98, S*.70)], fill=col)
    return im.resize((s, s), Image.LANCZOS)

def badge(txt, ic, scale=1.0):
    f = ImageFont.truetype(FB, int(64 * scale)); t = text_img(txt, f, WHITE)
    s = int(66 * scale); pad = int(30 * scale); gap = int(18 * scale)
    w = pad + s + gap + t.width + pad; h = max(s, t.height) + int(36 * scale)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=RED)
    im.alpha_composite(icon(ic, s), (pad, (h - s) // 2))
    im.alpha_composite(t, (pad + s + gap, (h - t.height) // 2))
    return with_shadow(im)

def big_title():
    f1 = ImageFont.truetype(FB, 170); f2 = ImageFont.truetype(FXB, 54)
    a = text_img("MARDİN", f1, WHITE, 0); b = text_img("gezi günlüğü", f2, WHITE)
    pin = icon("pin", 96, RED)
    w = max(a.width, b.width + 110); h = a.height + 24 + max(b.height, 96)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    im.alpha_composite(a, ((w - a.width) // 2, 0))
    x0 = (w - (96 + 14 + b.width)) // 2
    im.alpha_composite(pin, (x0, a.height + 24)); im.alpha_composite(b, (x0 + 110, a.height + 24 + (96 - b.height) // 2))
    return with_shadow(im, r=16, a=0.55)

# ---------------------------------------------------------------- olay listesi
# (tur, bas, son, icerik)
EVENTS = [
    ("title", 0.15, 2.45, None),
    ("badge", 2.62, 5.95, ("KAFE DURAĞI", "cup")),
    ("badge", 17.05, 23.80, ("ÇARŞI", "bag")),
    ("badge", 29.95, 32.85, ("MEYDAN", "pin")),
    ("badge", 33.10, DUR - 0.05, ("BADEM ŞEKERİ", "candy")),
]
def seg_by_clip(clip, kind=None):
    return next(x for x in TL if x["clip"] == clip and (kind is None or x["kind"].startswith(kind)))
SPLIT = seg_by_clip("3288", "split")

# altyazi satirlari: en fazla 3 kelime / cumle sonunda kir
LINES = []
cur = []
for i, w in enumerate(WORDS):
    nxt = WORDS[i + 1] if i + 1 < len(WORDS) else None
    cur.append(w)
    brk = (len(cur) >= 2 or w["w"].endswith((".", ",", "?", "!")) or nxt is None
           or nxt["t"] - w["end"] > 0.35 or nxt["clip"] != w["clip"] or len(" ".join(c["w"] for c in cur)) > 13 or (nxt and len(" ".join(c["w"] for c in cur + [nxt])) > 15))
    if brk:
        end = min(cur[-1]["end"] + 0.25, nxt["t"] - 0.02) if nxt else cur[-1]["end"] + 0.35
        x = seg_at(cur[0]["t"]); end = min(end, x["t1"] if True else end)
        LINES.append(dict(t0=cur[0]["t"], t1=end, words=cur)); cur = []

def disp(w):
    return w.replace("İ", "İ").upper().replace("I", "I").rstrip(",.") if False else tr_upper(w.rstrip(",."))
def tr_upper(s):
    return s.replace("i", "İ").replace("ı", "I").upper()

FSUBS = {s: ImageFont.truetype(FB, int(76 * s)) for s in (1.0, 0.85, 0.7)}
def line_img(line, t, sc=1.0):
    FSUB = FSUBS[sc]
    """Kelime kelime: gorunen kelimeler beyaz, aktif kelime sari + pop."""
    ws = line["words"]; parts = []
    for k, w in enumerate(ws):
        on = w["t"] <= t
        active = on and (k == len(ws) - 1 or ws[k + 1]["t"] > t)
        parts.append((tr_upper(w["w"].rstrip(",.")), on, active, t - w["t"]))
    imgs = [text_img(p[0], FSUB, YEL if p[2] else WHITE, 9) for p in parts]
    sp = 22; total = sum(i.width for i in imgs) + sp * (len(imgs) - 1); h = max(i.height for i in imgs)
    canvas = Image.new("RGBA", (total + 40, h + 40), (0, 0, 0, 0)); x = 20
    for im, p in zip(imgs, parts):
        if p[1]:
            s = 0.6 + 0.4 * ease_back(p[3] / 0.16)
            im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
            canvas.alpha_composite(im2, (int(x + (im.width - im2.width) / 2), int(20 + (h - im2.height) / 2)))
        x += im.width + sp
    return with_shadow(canvas, r=10, a=0.5, dy=4)

# ---------------------------------------------------------------- yerlesim (zaman penceresi boyunca sabit, yuzden kacinir)
def window_boxes(t0, t1):
    fr = range(int(t0 * FPS), int(t1 * FPS) + 1)
    return [b for n in fr for b in head_boxes(n / FPS)]

def place(w, h, t0, t1, prefer, xc=None, extra=()):
    """prefer: 'above' (basin ustu, basa en yakin) | 'chest' (basin alti) | 'top'.
    Dondurur: (x, y) sol-ust veya None."""
    boxes = window_boxes(t0, t1) + list(extra)
    xc = xc if xc is not None else (SAFE_LEFT + SAFE_RIGHT) / 2
    xs = [xc - w / 2] + [SAFE_LEFT + k * 20 for k in range(0, int(SAFE_RIGHT - w - SAFE_LEFT) // 20 + 1)]
    xs = [x for x in xs if SAFE_LEFT <= x and x + w <= SAFE_RIGHT]
    ys = list(range(SAFE_TOP + 10, SAFE_BOTTOM - h - 10 + 1, 10))
    ok = [(x, y) for y in ys for x in xs if not any(inter((x, y, x + w, y + h), b) for b in boxes)]
    if not ok: return None
    hb = window_boxes(t0, t1)
    tops = [b[1] for b in hb if b[3] - b[1] > 150]; bots = [b[3] for b in hb if b[3] - b[1] > 150]
    if prefer == "above":
        ref = min(tops) if tops else 420
        key = lambda p: (p[1] + h > ref + 5, abs(ref - 30 - (p[1] + h)), abs(p[0] + w / 2 - xc))
    elif prefer == "chest":
        ref = max(bots) + 40 if bots else 1300
        key = lambda p: (p[1] < ref - 5, abs(p[1] - ref), abs(p[0] + w / 2 - xc))
    else:
        key = lambda p: (p[1], abs(p[0] + w / 2 - xc))
    return min(ok, key=key)

PLACEMENT = {}
def inner(im_pad):
    im, pad = im_pad; return im.width - 2 * pad, im.height - 2 * pad - 6, pad
def plan():
    for k, (kind, t0, t1, c) in enumerate(EVENTS):
        res = None
        for sc in ((1.0,) if kind == "title" else (1.0, 0.8)):
            w, h, pad = inner(big_title() if kind == "title" else badge(*c, scale=sc))
            pos = place(w, h, t0, t1, "top" if kind == "title" else "above")
            if pos: res = (pos, (w, h), sc); break
        PLACEMENT[("ev", k)] = res
    def ev_boxes(a0, a1):
        out = []
        for k, (kind, t0, t1, c) in enumerate(EVENTS):
            p = PLACEMENT[("ev", k)]
            if p and t0 < a1 and a0 < t1: (x, y), (w, h), _ = p; out.append((x, y, x + w, y + h))
        return out
    for k, L in enumerate(LINES):
        res = None
        for sc in (1.0, 0.85, 0.7):
            w, h, pad = inner(line_img(L, L["t1"], sc)); w = int(w * 1.06)
            pos = place(w, h, L["t0"], L["t1"], "chest", extra=ev_boxes(L["t0"], L["t1"]))
            if pos: res = [(L["t0"], L["t1"], pos, (w, h), sc)]; break
        if res is None:   # kamera hareketli: kelime kelime ayri pencerelerde yerlestir
            res = []; ws = L["words"]
            for j, wd in enumerate(ws):
                a0 = wd["t"]; a1 = ws[j + 1]["t"] if j + 1 < len(ws) else L["t1"]
                for sc in (1.0, 0.85, 0.7):
                    w, h, pad = inner(line_img(L, L["t1"], sc)); w = int(w * 1.06)
                    pos = place(w, h, a0, a1, "chest", extra=ev_boxes(a0, a1))
                    if pos: res.append((a0, a1, pos, (w, h), sc)); break
                else: res.append((a0, a1, None, (0, 0), 1.0))
        PLACEMENT[("ln", k)] = res

# ---------------------------------------------------------------- kare uretimi
caps = {}
def read_src(clip, n):
    cap = caps.get(clip)
    if cap is None: cap = caps[clip] = [cv2.VideoCapture(f"sdr/{clip}.mp4"), -1]
    if cap[1] != n - 1: cap[0].set(cv2.CAP_PROP_POS_FRAMES, n)
    ok, f = cap[0].read(); cap[1] = n
    if not ok:  # klip sonu: son kareyi tekrar et
        cap[0].set(cv2.CAP_PROP_POS_FRAMES, n - 1); ok, f = cap[0].read()
    return Image.fromarray(cv2.cvtColor(f, cv2.COLOR_BGR2RGB)).convert("RGBA")

def base_frame(t):
    x = seg_at(t); n = src_frame(x, t)
    if not x["kind"].startswith("split"): return read_src(x["clip"], n)
    other = x["kind"].split(":")[1]
    a = read_src(x["clip"], n).crop((270, 0, 810, 1920)); b = read_src(other, n).crop((270, 0, 810, 1920))
    p = ease_out((t - x["t0"]) / 0.3)                      # iki yari ustten/alttan kayarak girer
    fr = Image.new("RGBA", (W, H), (255, 255, 255, 255))
    fr.alpha_composite(a, (0, int(-H * (1 - p)))); fr.alpha_composite(b, (540, int(H * (1 - p))))
    ImageDraw.Draw(fr).rectangle((537, 0, 543, H), fill=WHITE)
    return fr

LABEL_F = ImageFont.truetype(FB, 52)
def split_labels(t, ov, rects):
    x = SPLIT
    if not (x["t0"] + 0.25 <= t < x["t1"]): return
    a = ease_back((t - x["t0"] - 0.25) / 0.25)
    for txt, cx in (("TESPİH", 270), ("ŞAL", 760)):
        im = text_img(txt, LABEL_F, WHITE)
        pill = Image.new("RGBA", (im.width + 48, im.height + 28), (0, 0, 0, 0))
        ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, pill.height - 1), radius=pill.height // 2, fill=(0, 0, 0, 170))
        pill.alpha_composite(im, (24, 14)); s = max(0.01, a)
        p2 = pill.resize((max(1, int(pill.width * s)), max(1, int(pill.height * s))), Image.LANCZOS)
        y = 300; px = int(cx - p2.width / 2); px = min(px, SAFE_RIGHT - p2.width)
        ov.alpha_composite(p2, (px, int(y + (pill.height - p2.height) / 2)))
        rects.append((px, y, px + pill.width, y + pill.height))

def overlay(t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); rects = []
    for k, (kind, t0, t1, c) in enumerate(EVENTS):
        if not (t0 <= t < t1) or PLACEMENT[("ev", k)] is None: continue
        pos, (w, h), sc = PLACEMENT[("ev", k)]
        im, pad = big_title() if kind == "title" else badge(*c, scale=sc)
        a_in = ease_back((t - t0) / 0.3); a_out = 1 - ease_out((t - (t1 - 0.2)) / 0.2) if t > t1 - 0.2 else 1
        s_ = max(0.01, a_in * a_out)
        im2 = im.resize((max(1, int(im.width * s_)), max(1, int(im.height * s_))), Image.LANCZOS)
        cx, cy = pos[0] + w / 2, pos[1] + h / 2
        ov.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))
        rects.append((cx - w / 2 * s_, cy - h / 2 * s_, cx + w / 2 * s_, cy + h / 2 * s_))
    for k, L in enumerate(LINES):
        if not (L["t0"] <= t < L["t1"]): continue
        for a0, a1, pos, (w, h), sc in PLACEMENT[("ln", k)]:
            if not (a0 <= t < a1) or pos is None: continue
            im, pad = line_img(L, t, sc)
            x0 = int(pos[0] + w / 2 - im.width / 2); y0 = pos[1] - pad
            ov.alpha_composite(im, (x0, y0))
            bb = im.getchannel("A").point(lambda v: 255 if v > 100 else 0).getbbox()   # gercek yazi pikselleri
            if bb: rects.append((x0 + bb[0], y0 + bb[1], x0 + bb[2], y0 + bb[3]))
    split_labels(t, ov, rects)
    return ov, rects

def check(t, rects):
    """Gercek cizilen piksellerin kutusu: yuz ve Instagram arayuzu ihlali."""
    bad = []
    for r in rects:
        if r[1] < SAFE_TOP or r[3] > SAFE_BOTTOM or r[2] > SAFE_RIGHT or r[0] < 0: bad.append(("arayuz", r))
        for b in head_boxes(t):
            if inter(r, b, pad=0): bad.append(("yuz", r, b))
    for i in range(len(rects)):
        for j in range(i + 1, len(rects)):
            if inter(rects[i], rects[j], pad=0): bad.append(("grafik-grafik", rects[i], rects[j]))
    return bad

if __name__ == "__main__":
    plan()
    mode = sys.argv[1]
    os.makedirs("work/frames", exist_ok=True)
    for k, L in enumerate(LINES):
        p = [(round(a0, 2), q, sc) for a0, a1, q, _, sc in PLACEMENT[("ln", k)]]
        print(f"altyazi {L['t0']:6.2f}-{L['t1']:6.2f} {' '.join(w['w'] for w in L['words']):26s} -> {p}")
    for k, e in enumerate(EVENTS): print("grafik", e[0], e[1], e[2], e[3], "->", PLACEMENT[("ev", k)])
    if mode == "samples":
        ts = [float(v) for v in sys.argv[2].split(",")]
        frames = [round(t * FPS) for t in ts]
    else:
        frames = range(N)
        import subprocess
        pipe = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                                 "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p",
                                 "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "work/video_noaudio.mp4"],
                                stdin=subprocess.PIPE)
    viol = 0; checked = 0
    for n in frames:
        t = n / FPS
        fr = base_frame(t); ov, rects = overlay(t); fr.alpha_composite(ov)
        bad = check(t, rects); checked += 1
        if bad: viol += 1; print("IHLAL", f"{t:.2f}", bad[:2])
        if mode == "samples": fr.convert("RGB").save(f"work/frames/{n:04d}.png")
        else: pipe.stdin.write(fr.convert("RGB").tobytes())
    if mode != "samples": pipe.stdin.close(); pipe.wait()
    print(f"GUVENLI ALAN: {checked} karede ihlal {viol}")
