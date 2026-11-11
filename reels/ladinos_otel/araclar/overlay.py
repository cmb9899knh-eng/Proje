"""Grafik katmani (baslik, notlar, kelime kelime altyazi, kartlar) + yerlesim guvenligi kontrolu.
Kullanim:
  python3 overlay.py <work> check            -> tum kareler: yuz/kafa cakismasi + Instagram arayuz bolgesi
  python3 overlay.py <work> png <k1,k2,...>   -> secili karelerin RGBA overlay PNG'leri (<work>/ov/)
  python3 overlay.py <work> all               -> tum karelerin PNG'leri (final render icin)
<work> icinde faces.json (YuNet, kaynak kare bazli) ve build/cutcheck.log (kelime zamanlari) beklenir.
"""
import sys, os, json, re, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from edl import SEGS, FPS, timeline, TOTAL, NO_PERSON

W, H = 1080, 1920
WORK = sys.argv[1]
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FXB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FSB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
if not os.path.exists(FSB): FSB = FXB

# ---- Instagram Reels guvenli alan -------------------------------------------------
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 230, 1500, 940, 40

# ---- segment zamanlari --------------------------------------------------------------
TL = timeline()
SEG_AT = {}
for s, f0, n in TL:
    for k in range(n): SEG_AT[f0 + k] = (s, k)
START = {s[0]: f0 / FPS for s, f0, n in TL}
END = {s[0]: (f0 + n) / FPS for s, f0, n in TL}

# ---- yuz kutulari (kafa korumasi) ---------------------------------------------------
FACES = json.load(open(os.path.join(WORK, "faces.json")))
def heads(n):
    """cikti karesi n icin genisletilmis kafa kutulari (sac/sal payi dahil), zoom donusumuyle"""
    s, k = SEG_AT[n]
    clip = s[1]
    if clip == "SPLIT" or clip in NO_PERSON: return []
    fr = FACES[clip]; i = round(s[2] * FPS) + k
    cand = fr[i] if i < len(fr) else []
    if not cand:  # tespit kacmissa en yakin (+-15 kare) tespiti kullan
        for d in range(1, 16):
            for j in (i - d, i + d):
                if 0 <= j < len(fr) and fr[j]: cand = fr[j]; break
            if cand: break
    z = s[5]; out = []
    for x, y, w, h, sc in cand:
        x0, y0, x1, y1 = x - 0.30 * w, y - 0.55 * h, x + 1.30 * w, y + 1.15 * h  # sal/sac + cene payi
        out.append(tuple((v - c) * z + c2 for v, c, c2 in ((x0, 540, 540), (y0, 960, 960), (x1, 540, 540), (y1, 960, 960))))
    return out

# satir gruplamasi (kelime indeksleri)
GROUPS = [(0, 1, 2), (3, 4), (5, 6, 7, 8), (9, 10), (11, 12, 13), (14,), (15, 16), (17,)]
# ---- kelime zamanlari (dialog stemi yeniden transkripsiyonu) + enerji ile hassaslastirma ----
def words():
    log = open(os.path.join(WORK, "build", "cutcheck.log")).read().split("== 3)")[1].split("beklenen")[0]
    ws = [(float(a), float(b), t) for a, b, t in re.findall(r"^\s+([\d.]+)-\s*([\d.]+) (\S+)", log, re.M)]
    wv = wave.open(os.path.join(WORK, "build", "dialog.wav")); sr = wv.getframerate()
    x = np.frombuffer(wv.readframes(wv.getnframes()), np.int16).astype(np.float32) / 32768
    hop = sr // 100; env = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, "same")[::hop]) + 1e-9)
    firsts = {g[0] for g in GROUPS}
    out, prev = [], -9
    for k, (a, b, t) in enumerate(ws):
        on = a
        if k in firsts:  # duraksama sonrasi satir basi: enerjinin gercekten yukseldigi ana kaydir
            rng = range(int(a * 100), int(min(b, a + 0.45) * 100))
            edge = [i for i in rng if env[i] > -30 and i >= 8 and env[i - 8:i - 3].max() < -38]
            cross = [i for i in rng if env[i] > -30]
            if edge or cross: on = (edge or cross)[0] / 100 - 0.03
        on = max(on, prev + 0.18); prev = on
        out.append([round(on, 2), b, t])
    return out
WORDS = words()

DISPLAY = {"midyatta": "Midyat'ta"}  # yazim duzeltmesi (ses degil, sadece ekrandaki yazim)
def up(t):
    t = DISPLAY.get(t.lower().strip(".,?!"), t) + ("" if t[-1].isalnum() else t[-1]) if t.lower().strip(".,?!") in DISPLAY else t
    return t.replace("i", "İ").replace("ı", "I").upper()

# ---- yardimcilar -----------------------------------------------------------------------
def ease_back(x):
    x = min(max(x, 0), 1); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def text_img(txt, font, fill, stroke=0, sfill=(0, 0, 0, 255)):
    b = font.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), txt, font=font, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    return im
def paste(c, im, cx, cy, s=1.0, alpha=1.0):
    if s <= 0.01 or alpha <= 0.01: return
    if abs(s - 1) > 1e-3: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if alpha < 1:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def shadow(im, r=10, a=0.45):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    sh.alpha_composite(blk, (2 * r, 2 * r + r // 2)); sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (2 * r, 2 * r)); return sh

YEL = (255, 206, 64, 255); WHITE = (255, 255, 255, 255); INK = (24, 20, 16, 255)
TEAL = (16, 92, 104, 255); CREAM = (250, 243, 230, 255)

def pill(text, size=40, bg=WHITE, fg=INK, icon=None, padx=34, h=None):
    f = ImageFont.truetype(FXB, size); t = text_img(text, f, fg)
    ih = 0 if icon is None else size + 8
    h = h or t.height + 34; w = t.width + 2 * padx + ih
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=bg)
    if icon == "pin":  # cizimle konum ikonu (harici varlik yok)
        cx, cy, r = padx + size // 2 - 4, h // 2 - 4, size // 2 - 6
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(226, 72, 72, 255))
        d.polygon([(cx - r * 0.8, cy + r * 0.5), (cx + r * 0.8, cy + r * 0.5), (cx, cy + r * 1.9)], fill=(226, 72, 72, 255))
        d.ellipse((cx - r * 0.38, cy - r * 0.38, cx + r * 0.38, cy + r * 0.38), fill=bg)
    im.alpha_composite(t, (padx + ih, (h - t.height) // 2 - 2))
    return shadow(im, 8, 0.35)

def title(lines, size=84):
    f = ImageFont.truetype(FB, size); ts = [text_img(x, f, INK) for x in lines]
    w = max(t.width for t in ts) + 80; h = sum(t.height for t in ts) + 18 * (len(ts) - 1) + 48
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=24, fill=YEL)
    y = 24
    for t in ts: im.alpha_composite(t, ((w - t.width) // 2, y)); y += t.height + 18
    return shadow(im, 10, 0.4)

def section(text):  # bolum basligi: koyu zemin, krem yazi, alt cizgi
    f = ImageFont.truetype(FB, 92); t = text_img(text, f, CREAM)
    w, h = t.width + 96, t.height + 52
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=26, fill=TEAL)
    d.rounded_rectangle((48, h - 18, w - 48, h - 10), radius=4, fill=YEL)
    im.alpha_composite(t, (48, (h - t.height) // 2 - 8)); return shadow(im, 10, 0.4)

def cta():
    f1 = ImageFont.truetype(FB, 44); a = text_img("Midyat'a gidecek birine gönder", f1, INK)
    w, h = a.width + 84, a.height + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=YEL)
    im.alpha_composite(a, (42, (h - a.height) // 2 - 3)); return shadow(im, 10, 0.45)

TITLE = title(["MİDYAT'TA", "OTEL TURU"])
LOC = pill("Ladinos Otel · Midyat", 40, icon="pin")
NOTE_RES = pill("Resepsiyon", 38)
NOTE_ONERI = pill("Oda önerisini dinliyoruz", 38)
NOTE_MANZ = pill("Pencereden gece manzarası", 38)
SEC_ODA = section("ODA")
SEC_BANYO = section("BANYO")
LBL_DUS = pill("Yağmur duşu", 38)
LBL_FON = pill("Saç kurutma makinesi", 38)
CTA = cta()

# ---- olay listesi: (baslangic, bitis, cizim, cx, cy, giris_animasyonu) ----------------------
T = START
EVENTS = [
    (0.10, 3.90, TITLE, 490, 365, "pop"),
    (0.40, 3.90, LOC, 490, 530, "pop"),
    (T["s04"] + 0.10, END["s04"] - 0.10, NOTE_RES, 490, 320, "pop"),
    (T["s08"] + 0.15, END["s08"] - 0.10, NOTE_ONERI, 490, 320, "pop"),
    (T["s13"] + 0.05, T["s13"] + 1.80, SEC_ODA, 490, 345, "pop"),
    (T["s16"] + 1.00, END["s16"] - 0.10, NOTE_MANZ, 490, 320, "pop"),
    (T["s17"] + 0.05, T["s17"] + 1.80, SEC_BANYO, 490, 345, "pop"),
    (T["s18"] + 0.10, END["s18"], LBL_DUS, 490, 300, "pop"),
    (T["s18"] + 0.25, END["s18"], LBL_FON, 490, 1060, "pop"),
    (T["s20"] + 0.20, TOTAL / FPS, CTA, 490, 1405, "pop"),
]
# ses efekti isaretleri (audio_mix.py okur)
SFX = [("pop", 0.10), ("tick", 0.40), ("tick", T["s04"] + 0.10), ("tick", T["s08"] + 0.15),
       ("whoosh", T["s13"]), ("pop", T["s13"] + 0.05), ("tick", T["s16"] + 1.00),
       ("whoosh", T["s17"]), ("pop", T["s17"] + 0.05), ("swish", T["s18"]), ("tick", T["s18"] + 0.10),
       ("tick", T["s18"] + 0.25), ("ding", T["s20"] + 0.20)]

# ---- altyazi: konusmacinin gogus hizasi ------------------------------------------------------
SUB_FONT = ImageFont.truetype(FB, 70)
CLIP_OF = {s[0]: s[1] for s in SEGS}
def chest_y(sid):
    """ayni kaynak plana ait tum segmentlerdeki kafa kutularinin en alt noktasinin altina; arayuz sinirina kadar"""
    bottoms = []
    for s2, f0, n in TL:
        if s2[1] == CLIP_OF[sid]: bottoms += [hb[3] for k in range(n) for hb in heads(f0 + k)]
    if not bottoms: return 1380
    return int(min(max(np.percentile(bottoms, 98) + 95, 1080), 1430))
SUB_LINES = []
for g in GROUPS:
    ws = [WORDS[i] for i in g]
    nxt = WORDS[g[-1] + 1][0] if g[-1] + 1 < len(WORDS) else ws[-1][1] + 0.6
    end = min(ws[-1][1] + 0.55, nxt - 0.02)
    sid = SEG_AT[min(int(ws[0][0] * FPS), TOTAL - 1)][0][0]
    SUB_LINES.append((ws[0][0], end, ws, sid))
CHEST = {sid: chest_y(sid) for sid in {l[3] for l in SUB_LINES}}
for l in SUB_LINES:  # konusma ayni karede baska segmente tasarsa dusuk olanini kullan
    pass

def sub_word(w, active, size=70):
    f = SUB_FONT if size == 70 else ImageFont.truetype(FB, size)
    return text_img(up(w), f, YEL if active else WHITE, stroke=9)

def render(n):
    t = n / FPS
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for (a, b, im, cx, cy, anim) in EVENTS:
        if not (a <= t < b): continue
        s = ease_back((t - a) / 0.24); al = 1 - ease_out((t - (b - 0.15)) / 0.15)
        paste(c, im, cx, cy, s, al)
    # (bolunmus ekran ayrac cizgisi video kompozisyonunda cizilir - render.py)
    for (a, b, ws, sid) in SUB_LINES:
        if not (a <= t < b): continue
        shown = [w for w in ws if t >= w[0]]
        size = 70
        while True:
            full = [sub_word(w[2], False, size) for w in shown]; sp = int(size * 0.32)
            tot = sum(i.width for i in full) + sp * (len(full) - 1)
            if tot <= 860 or size <= 50: break
            size -= 4
        x = 490 - tot / 2; y = CHEST[sid]
        for i, w in enumerate(shown):
            im = sub_word(w[2], i == len(shown) - 1, size)
            paste(c, im, x + full[i].width / 2, y, 0.65 + 0.35 * ease_back((t - w[0]) / 0.14))
            x += full[i].width + sp
    return c

def check(frames):
    bad, ui, rows = [], [], []
    for n in frames:
        a = np.array(render(n).getchannel("A"))
        ys, xs = np.nonzero(a > 8)
        if not len(ys): continue
        for hb in heads(n):
            x0, y0, x1, y1 = [int(round(v)) for v in hb]
            hit = int((a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] > 8).sum())
            if hit: bad.append((n, round(n / FPS, 2), SEG_AT[n][0][0], hit, (x0, y0, x1, y1)))
        if ys.min() < SAFE_TOP or ys.max() > SAFE_BOTTOM or xs.max() > SAFE_RIGHT or xs.min() < SAFE_LEFT:
            ui.append((n, round(n / FPS, 2), int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())))
        rows.append((ys.min(), ys.max(), xs.min(), xs.max()))
    print(f"kontrol edilen kare={len(frames)}  grafikli kare={len(rows)}  yuz/kafa cakismasi={len(bad)}  arayuz ihlali={len(ui)}")
    for b in bad[:8]: print("  CAKISMA", b)
    for u in ui[:8]: print("  ARAYUZ", u)
    if rows:
        r = np.array(rows); print(f"  grafik y araligi {r[:,0].min()}-{r[:,1].max()}  x araligi {r[:,2].min()}-{r[:,3].max()}")
    return not bad and not ui

if __name__ == "__main__":
    mode = sys.argv[2]
    if mode == "check":
        print("altyazi satirlari:")
        for a, b, ws, sid in SUB_LINES: print(f"  {a:6.2f}-{b:6.2f} {sid} y={CHEST[sid]}  " + " ".join(f"{w[2]}@{w[0]:.2f}" for w in ws))
        ok = check(range(TOTAL)); print("SONUC:", "GECTI" if ok else "KALDI")
    else:
        os.makedirs(os.path.join(WORK, "ov"), exist_ok=True)
        fr = range(TOTAL) if mode == "all" else [int(x) for x in sys.argv[3].split(",")]
        for n in fr: render(n).save(os.path.join(WORK, "ov", f"{n:05d}.png"))
