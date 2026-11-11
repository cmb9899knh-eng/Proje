"""Ladinos Otel tanitim reel'i (v2) - dis ses (VO) senaryosuna gore bolumlenmis kurgu.
Kullanim:
  python3 promo.py <work> plan                 -> zaman cizelgesi (plan tablosu) yazdirir
  python3 promo.py <work> check                -> tum kareler: yuz/kafa cakismasi + Instagram arayuz bolgesi
  python3 promo.py <work> samples t1,t2,...    -> ornek kareler + iletisim sayfasi
  python3 promo.py <work> full out.mp4 [audio] -> tam video (ONAYDAN SONRA)
VO kayitlari gelince VO_DUR (sn) ve VO_WORDS (kelime zamanlari) gercek degerlerle guncellenir; bolum sureleri buna gore yeniden hesaplanir.
"""
import sys, os, json, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

WORK = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else "plan"; ARG = sys.argv[3:]
W, H, FPS = 1080, 1920, 30
BPM = 100; BEAT = 60 / BPM                       # 0,6 sn; kesimler yarim vurusa (0,3 sn) oturur
SDR = os.path.join(WORK, "sdr")
AN = json.load(open(os.path.join(WORK, "analysis.json")))

# ------------------------------------------------------------------------------------------------
# 1) SENARYO: dis ses satirlari (sira = kayit listesindeki sira). Sure: VO gelene kadar TAHMINI.
VO = [  # (id, metin, tahmini_sure_sn)
    ("V1", "Midyat'ın kendine has taş sokaklarında bugün sizlerle çok güzel bir konaklama noktası keşfedeceğiz.", 5.4),
    ("V9", "Otel'e adım attığımız ilk andan itibaren Midyat'ın tarihi dokusunu ve kendine özgü atmosferini hissedebiliyorsunuz.", 6.6),
    ("V2", "Taş mimarisi, zarif detayları ve sıcak atmosferiyle burası gerçekten çok özel bir yer.", 4.8),
    ("V3", "Odaların konforundan ortak kullanım alanlarına, her köşesinde ayrı bir güzellik saklı.", 5.4),
    ("V4", "Özellikle lobideki şömine köşesi, akşamları ayrı bir keyif.", 3.6),
    ("V5", "Terastaki manzarasıyla Midyat'ı bir de buradan izlemek bambaşka bir keyif.", 4.2),
    ("V10", "Güne güzel bir başlangıç yapmak isteyenler için kahvaltı detayını da unutmamak gerek.", 4.6),
    ("V6", "Eğer sizin de yolunuz Midyat'a düşerse, burayı listenize eklemeyi unutmayın.", 4.2),
    ("V7", "Ladinos Otel; Midyat, Akçakaya Mahallesi, Atatürk Bulvarı'nda.", 3.6),
    ("V8", "Ben bugün burayı sizlerle keşfetmekten çok keyif aldım.", 3.4),
    ("V11", "Yeni keşiflerde görüşmek üzere.", 2.6),
]
VO_REAL = os.path.join(WORK, "vo", "vo_timing.json")   # VO gelince: {"V1": {"dur":..,"words":[[t0,t1,"kelime"],..]}, ...}
VOT = json.load(open(VO_REAL)) if os.path.exists(VO_REAL) else {}

# 2) BOLUMLER: (id, vo_satiri | None, baslik, [(klip, aralik_bas, aralik_son, agirlik, hareket)], cikis_gecisi)
#    hareket: "push" yavas ileri zoom, "pull" geri, "none"; gecis: "cut" | "whipL" | "whipR" | "zoom" | "flash" | "fade"
SECTIONS = [
    ("intro", None, None, [("IMG_3808", 0.2, 2.6, 1, "push")], "cut", 1.2),
    ("hook", "V1", "title", [("IMG_3746", 0.3, 3.7, 1, "push"), ("IMG_3749", 3.0, 5.7, 1, "none"), ("IMG_3747", 0.3, 2.6, 1, "push")], "whipL"),
    ("giris", "V9", None, [("IMG_3750", 0.6, 4.4, 1.3, "none"), ("IMG_3754", 2.1, 4.8, 1.2, "none"), ("IMG_3832", 0.1, 2.5, 1, "none"), ("IMG_3820", 0.5, 3.5, 1, "push")], "zoom"),
    ("mimari", "V2", "DETAYLAR", [("IMG_3748", 0.2, 2.8, 1, "push"), ("IMG_3765", 0.1, 2.3, 1, "none"), ("IMG_3788", 2.0, 3.8, 1, "push"), ("IMG_3817", 0.8, 4.3, 1, "push")], "whipR"),
    ("oda", "V3", "ODALAR", [("IMG_3766", 0.3, 3.6, 1, "none"), ("IMG_3767", 0.4, 3.0, 1, "none"), ("IMG_3771", 0.2, 2.8, 1, "none"), ("IMG_3786", 0.5, 3.9, 1, "push"), ("IMG_3815", 0.3, 4.8, 1, "none")], "whipR"),
    ("banyo", None, "BANYO", [("IMG_3772", 1.4, 4.6, 1, "none"), ("SPLIT:IMG_3774@0.6|IMG_3775@0.2", 0, 1.9, 1, "none"), ("IMG_3792", 4.4, 7.4, 1, "none")], "flash", 3.6),
    ("somine", "V4", "ŞÖMİNE KÖŞESİ", [("IMG_3825", 0.2, 3.2, 1, "push"), ("IMG_3834", 0.0, 3.2, 1.2, "none"), ("IMG_3830", 0.3, 2.6, 1, "none")], "zoom"),
    ("teras", "V5", "TERAS", [("IMG_3806", 0.2, 4.8, 1, "push"), ("IMG_3805", 0.2, 4.8, 1, "none"), ("IMG_3807", 2.6, 6.8, 1, "none")], "whipL"),
    ("kahvalti", "V10", "KAHVALTI & RESTORAN", [("KAHVALTI", 0.2, 5.2, 1.3, "none"), ("IMG_3798", 0.3, 4.6, 1, "none"), ("IMG_3803", 0.2, 3.2, 1, "none"), ("IMG_3804", 0.3, 4.1, 1, "none")], "whipR"),
    ("davet", "V6", None, [("IMG_3811", 0.4, 4.7, 1.3, "none"), ("IMG_3794", 0.2, 4.1, 1, "push")], "cut"),
    ("adres", "V7", "address", [("IMG_3749", 0.0, 4.8, 1, "push")], "zoom"),
    ("kapanis", "V8", None, [("IMG_3784", 0.9, 3.7, 1, "none"), ("IMG_3791", 0.2, 3.2, 1, "none")], "cut"),
    ("son", "V11", "endcard", [("IMG_3813", 0.0, 2.5, 1, "push")], "fade"),   # <- yeni cekecegin kapanis videosu buraya gelir
]
NO_PERSON = {"IMG_3808", "IMG_3746", "IMG_3749", "IMG_3832", "IMG_3820", "IMG_3748", "IMG_3765", "IMG_3788", "IMG_3817",
             "IMG_3766", "IMG_3767", "IMG_3771", "IMG_3786", "IMG_3815", "IMG_3772", "IMG_3774", "IMG_3775", "IMG_3792",
             "IMG_3825", "IMG_3830", "IMG_3806", "IMG_3805", "IMG_3807", "KAHVALTI", "IMG_3798", "IMG_3803", "IMG_3804", "IMG_3794"}
TRANS_FR = {"cut": 0, "whipL": 5, "whipR": 5, "zoom": 6, "flash": 4, "fade": 12}
VO_LEAD, VO_TAIL = 0.3, 0.35   # bolum basinda VO oncesi / sonrasi nefes payi

def snap(t, q=BEAT / 2): return max(q, math.ceil(t / q - 1e-6) * q)

def vo_dur(v): return VOT.get(v, {}).get("dur", dict((a, c) for a, b, c in VO)[v])

# ------------------------------------------------------------------------------------------------
def best_start(clip, a, b, dur):
    """[a,b] araligindan dur suren en stabil + en net pencerenin baslangici"""
    fr = AN[clip]; n = round(dur * FPS); i0, i1 = round(a * FPS), min(round(b * FPS), len(fr)) - n
    if i1 <= i0: return a, min(dur, (len(fr) - i0) / FPS)
    dx = np.array([x[0] for x in fr]); dy = np.array([x[1] for x in fr]); sh = np.array([x[3] for x in fr])
    jerk = np.r_[0, np.abs(np.diff(dx)) + np.abs(np.diff(dy))]
    best, bi = 1e18, i0
    for i in range(i0, i1 + 1, 2):
        c = jerk[i:i + n].mean() * 3 - np.log(sh[i:i + n].mean() + 1) * 2 + 0.002 * (i - i0)
        if c < best: best, bi = c, i
    return bi / FPS, dur

def build():
    """-> shots: [dict(clip, src0, n, f0, sec, move, trans_out)], sections: [(id, vo, f0, n, vo_start)]"""
    shots, secs, t = [], [], 0.0
    for sec in SECTIONS:
        sid, v, title, lst, tr = sec[:5]
        if v: L = snap(VO_LEAD + vo_dur(v) + VO_TAIL)
        else: L = sec[5]
        f0 = round(t * FPS); N = round(L * FPS)
        secs.append(dict(id=sid, vo=v, title=title, f0=f0, n=N, vo_t=(t + VO_LEAD) if v else None))
        # sure dagitimi: yarim vurus (9 kare) birimleriyle, agirlikla orantili, her cekim en az 1 birim
        q = 9; units = N // q; wsum = sum(x[3] for x in lst)
        while units < len(lst) and len(lst) > 1: lst = lst[:-1]; wsum = sum(x[3] for x in lst)  # bolum cok kisaysa cekim azalt
        alloc = [max(1, int(units * x[3] / wsum)) for x in lst]
        k = 0
        while sum(alloc) < units: alloc[k % len(alloc)] += 1; k += 1
        while sum(alloc) > units: j = int(np.argmax(alloc)); alloc[j] -= 1
        alloc = [a_ * q for a_ in alloc]; alloc[-1] += N - sum(alloc)
        acc = 0
        for k, (clip, a, b, w, move) in enumerate(lst):
            n = alloc[k]
            if clip.startswith("SPLIT"): s0 = 0.0
            else:
                s0, _ = best_start(clip, a, b, n / FPS)
                n_av = len(AN[clip]) - round(s0 * FPS)
                if n > n_av: s0 = max(0.0, (len(AN[clip]) - n) / FPS)
            shots.append(dict(clip=clip, src0=s0, n=n, f0=f0 + acc, sec=sid, move=move,
                              trans=(tr if k == len(lst) - 1 else "cut")))
            acc += n
        t += L
    return shots, secs, round(t * FPS)
SHOTS, SECS, TOTAL = build()
AT = {}
for i, s in enumerate(SHOTS):
    for k in range(s["n"]): AT[s["f0"] + k] = (i, k)

# ------------------------------------------------------------------------------------------------
# GORUNTU
class Reader:
    def __init__(self): self.c = {}
    def get(self, clip, idx):
        cap, pos = self.c.get(clip, (None, -9))
        if cap is None: cap = cv2.VideoCapture(os.path.join(SDR, clip + ".mov"))
        nfr = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); idx = max(0, min(idx, nfr - 1))
        if idx != pos + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, im = cap.read()
        if not ok:
            cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, idx - 1)); ok, im = cap.read()
        self.c[clip] = (cap, idx); return im
R = Reader()

# renk: hafif sicak, yumusak S-egrisi, kontrollu doygunluk (tum kliplerde ayni "look")
_x = np.arange(256) / 255
_curve = np.clip(_x + 0.06 * np.sin(2 * np.pi * (_x - 0.5)) * -1 * (1 - np.abs(2 * _x - 1)) * 0, 0, 1)
_s = 1 / (1 + np.exp(-(_x - 0.5) * 5.2)); _s = (_s - _s.min()) / (_s.max() - _s.min())
_base = 0.72 * _x + 0.28 * _s
LUT = [np.clip(_base * g + o, 0, 1) for g, o in ((0.97, 0.0), (1.0, 0.004), (1.03, 0.01))]   # B, G, R
LUT = np.stack([(l * 255).astype(np.uint8) for l in LUT], 1).reshape(256, 1, 3)
def grade(im):
    im = cv2.LUT(im, LUT)
    hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= 1.08
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)

def scale_about(im, z, cx=540, cy=960):
    if abs(z - 1) < 1e-4: return im
    M = np.float32([[z, 0, cx - z * cx], [0, z, cy - z * cy]])
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def move_zoom(s, k):
    p = k / max(1, s["n"] - 1)
    return {"push": 1.0 + 0.06 * p, "pull": 1.06 - 0.06 * p}.get(s["move"], 1.0)

def raw(s, k):
    if s["clip"].startswith("SPLIT"):
        (c1, a1), (c2, a2) = [(x.split("@")[0], float(x.split("@")[1])) for x in s["clip"][6:].split("|")]
        out = np.zeros((H, W, 3), np.uint8)
        for (c, a), y in (((c1, a1), 0), ((c2, a2), 963)):
            out[y:y + 957] = R.get(c, round(a * FPS) + k)[481:481 + 957]
        out[957:963] = (230, 243, 250); return out
    return scale_about(R.get(s["clip"], round(s["src0"] * FPS) + k), move_zoom(s, k))

def motion_blur(im, dx, dy):
    L = int(max(abs(dx), abs(dy)))
    if L < 3: return im
    k = np.zeros((L, L), np.float32); cv2.line(k, (0, L // 2), (L - 1, L // 2), 1, 1)
    ang = math.degrees(math.atan2(dy, dx)); M = cv2.getRotationMatrix2D((L / 2 - .5, L / 2 - .5), ang, 1)
    k = cv2.warpAffine(k, M, (L, L)); k /= k.sum() + 1e-9
    return cv2.filter2D(im, -1, k)

def shift(im, dx):
    M = np.float32([[1, 0, dx], [0, 1, 0]]); return cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_REFLECT)

def shift0(im, dx):
    M = np.float32([[1, 0, dx], [0, 1, 0]]); return cv2.warpAffine(im, M, (W, H), borderMode=cv2.BORDER_CONSTANT)

def whip_info(n):
    """n bir whip gecis penceresindeyse (A indeksi, ilerleme 0..1) dondurur"""
    i, k = AT[n]; s = SHOTS[i]
    if s["trans"] in ("whipL", "whipR") and k >= s["n"] - TRANS_FR[s["trans"]] and i + 1 < len(SHOTS):
        m = TRANS_FR[s["trans"]]; return i, (k - (s["n"] - m) + 0.5) / (2 * m)
    if i > 0 and SHOTS[i - 1]["trans"] in ("whipL", "whipR") and k < TRANS_FR[SHOTS[i - 1]["trans"]]:
        m = TRANS_FR[SHOTS[i - 1]["trans"]]; return i - 1, (m + k + 0.5) / (2 * m)
    return None

def frame_bg(n):
    i, k = AT[n]; s = SHOTS[i]
    wi = whip_info(n)
    if wi:
        ia, p = wi; A, B = SHOTS[ia], SHOTS[ia + 1]
        ka = min(k if ia == i else A["n"] - 1, A["n"] - 1); kb = k if ia + 1 == i else 0
        fa, fb = raw(A, ka), raw(B, kb)
        e = p * p * (3 - 2 * p); d = -1 if A["trans"] == "whipL" else 1
        im = cv2.add(shift0(fa, d * e * W), shift0(fb, d * (e - 1) * W))
        im = motion_blur(im, 110 * math.sin(math.pi * p) + 1, 0)
    else:
        im = raw(s, k)
        def zoom_fx(img, phase):
            z = 1 + 0.35 * phase ** 2; acc = scale_about(img, z).astype(np.float32)
            if phase > 0.2:
                for e_ in (0.04, 0.08): acc += scale_about(img, z + e_ * phase).astype(np.float32)
                acc /= 3
            return acc.astype(np.uint8)
        if s["trans"] not in ("cut",) and k >= s["n"] - TRANS_FR[s["trans"]] and i + 1 < len(SHOTS):
            m = TRANS_FR[s["trans"]]; ph = (k - (s["n"] - m) + 1) / m
            if s["trans"] == "flash": im = cv2.addWeighted(im, 1 - ph * .85, np.full_like(im, (215, 235, 255)), ph * .85, 0)
            elif s["trans"] == "fade": im = (im * (1 - ph)).astype(np.uint8)
            elif s["trans"] == "zoom": im = zoom_fx(im, ph)
        if i > 0 and SHOTS[i - 1]["trans"] in ("flash", "zoom") and k < TRANS_FR[SHOTS[i - 1]["trans"]]:
            t = SHOTS[i - 1]["trans"]; m = TRANS_FR[t]; ph = 1 - k / m
            if t == "flash": im = cv2.addWeighted(im, 1 - ph * .85, np.full_like(im, (215, 235, 255)), ph * .85, 0)
            else: im = zoom_fx(im, ph)
    if n < 9: im = (im * (n / 9)).astype(np.uint8)                     # siyahtan acilis
    if n >= TOTAL - 18: im = (im * ((TOTAL - 1 - n) / 18)).astype(np.uint8)  # sona dogru karar
    return grade(im)

# ------------------------------------------------------------------------------------------------
# KAFA KUTULARI (grafik guvenligi)
def heads(n):
    i, k = AT[n]; s = SHOTS[i]; c = s["clip"]
    if c.startswith("SPLIT") or c in NO_PERSON: return []
    fr = AN[c]; j = round(s["src0"] * FPS) + k; cand = fr[min(j, len(fr) - 1)][5]
    if not cand:
        for d in range(1, 16):
            for jj in (j - d, j + d):
                if 0 <= jj < len(fr) and fr[jj][5]: cand = fr[jj][5]; break
            if cand: break
    z = move_zoom(s, k); out = []
    for x, y, w, h, sc in cand:
        x0, y0, x1, y1 = x - 0.30 * w, y - 0.55 * h, x + 1.30 * w, y + 1.15 * h
        out.append(((x0 - 540) * z + 540, (y0 - 960) * z + 960, (x1 - 540) * z + 540, (y1 - 960) * z + 960))
    return out

# ------------------------------------------------------------------------------------------------
# GRAFIKLER
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FXB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
FSB = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
FM = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT, SAFE_LEFT = 230, 1500, 940, 40
GOLD = (232, 190, 92, 255); CREAM = (250, 243, 230, 255); INK = (28, 24, 20, 255); WHITE = (255, 255, 255, 255)
TEAL = (14, 84, 96, 255)
def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x):
    x = min(max(x, 0), 1); c = 1.5; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def timg(t, f, fill, stroke=0, sf=(0, 0, 0, 255), track=0):
    if track:  # harf aralikli: tum harfler ortak taban cizgisinde (anchor 'ls')
        asc, desc = f.getmetrics(); xs, x = [], 0
        for ch in t: xs.append(x); x += f.getlength(ch) + track
        im = Image.new("RGBA", (int(x) + 8 + 2 * stroke, asc + desc + 8 + 2 * stroke), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        for ch, x0 in zip(t, xs): d.text((x0 + 4 + stroke, asc + 4 + stroke), ch, font=f, fill=fill, anchor="ls", stroke_width=stroke, stroke_fill=sf)
        bb = im.getbbox(); return im.crop((bb[0] - 2, bb[1] - 2, bb[2] + 2, bb[3] + 2)) if bb else im
    b = f.getbbox(t, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), t, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf); return im
def shadow(im, r=10, a=0.45):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * a)))
    sh.alpha_composite(blk, (2 * r, 2 * r + r // 2)); sh = sh.filter(ImageFilter.GaussianBlur(r)); sh.alpha_composite(im, (2 * r, 2 * r)); return sh
def paste(c, im, cx, cy, s=1.0, al=1.0, dy=0):
    if s <= .01 or al <= .01: return
    if abs(s - 1) > 1e-3: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if al < 1: im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * al)))
    c.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2 + dy)))

def section_header(text):  # ince altin cizgi + genis harf aralikli baslik + kucuk otel adi
    sz = 64
    while True:
        f = ImageFont.truetype(FB, sz); t = timg(text, f, WHITE, track=6)
        if t.width <= 760 or sz <= 40: break
        sz -= 4
    k = timg("LADİNOS OTEL · MİDYAT", ImageFont.truetype(FSB, 26), GOLD, track=4)
    w = max(t.width, k.width) + 20; h = t.height + k.height + 46
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    im.alpha_composite(k, ((w - k.width) // 2, 0))
    d.rectangle(((w - 120) // 2, k.height + 14, (w + 120) // 2, k.height + 18), fill=GOLD)
    im.alpha_composite(t, ((w - t.width) // 2, k.height + 34)); return shadow(im, 12, 0.6)
def title_card():
    f1 = ImageFont.truetype(FB, 120); f2 = ImageFont.truetype(FSB, 34)
    a = timg("LADİNOS", f1, WHITE, track=10); b = timg("O T E L", ImageFont.truetype(FXB, 46), GOLD)
    c = timg("MİDYAT · MARDİN", f2, CREAM, track=6)
    w = max(a.width, b.width, c.width) + 20; h = a.height + b.height + c.height + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 0
    im.alpha_composite(a, ((w - a.width) // 2, y)); y += a.height + 18
    im.alpha_composite(b, ((w - b.width) // 2, y)); y += b.height + 22
    d.rectangle(((w - 160) // 2, y, (w + 160) // 2, y + 4), fill=GOLD); y += 26
    im.alpha_composite(c, ((w - c.width) // 2, y)); return shadow(im, 16, 0.65)
def pin(d, cx, cy, r, col):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col)
    d.polygon([(cx - r * .82, cy + r * .5), (cx + r * .82, cy + r * .5), (cx, cy + r * 2.0)], fill=col)
    d.ellipse((cx - r * .38, cy - r * .38, cx + r * .38, cy + r * .38), fill=CREAM)
def address_card():
    l1 = timg("Ladinos Otel", ImageFont.truetype(FB, 54), INK)
    l2 = timg("Akçakaya Mahallesi", ImageFont.truetype(FSB, 40), (70, 60, 50, 255))
    l3 = timg("Atatürk Bulvarı · Midyat / Mardin", ImageFont.truetype(FSB, 40), (70, 60, 50, 255))
    w = max(l1.width, l2.width, l3.width) + 170; h = l1.height + l2.height + l3.height + 100
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=30, fill=CREAM)
    d.rounded_rectangle((0, 0, 14, h - 1), radius=7, fill=GOLD)
    pin(d, 70, 62, 22, (200, 60, 50, 255)); y = 34
    for t, gap in ((l1, 18), (l2, 10), (l3, 0)): im.alpha_composite(t, (128, y)); y += t.height + gap
    return shadow(im, 14, 0.5)
def end_card():
    a = timg("LADİNOS OTEL", ImageFont.truetype(FB, 78), WHITE, track=6)
    b = timg("Akçakaya Mah. · Atatürk Blv. · Midyat", ImageFont.truetype(FXB, 38), CREAM)
    c = timg("Kaydet · Midyat'a gidecek birine gönder", ImageFont.truetype(FXB, 34), GOLD)
    w = max(a.width, b.width, c.width) + 20; h = a.height + b.height + c.height + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); y = 0
    for t, g in ((a, 20), (b, 22), (c, 0)):
        im.alpha_composite(t, ((w - t.width) // 2, y)); y += t.height + g
        if t is a: d.rectangle(((w - 140) // 2, y - 8, (w + 140) // 2, y - 4), fill=GOLD); y += 8
    return shadow(im, 16, 0.7)
HEADERS = {s[2]: section_header(s[2]) for s in SECTIONS if s[2] and s[2] not in ("title", "address", "endcard")}
TITLE = title_card(); ADDR = address_card(); END = end_card()

# VO altyazi: kelime kelime (VO gelene kadar kelimeler satir icinde esit dagitilmis YER TUTUCU zamanlarla)
SUBF = {}
def subfont(sz):
    if sz not in SUBF: SUBF[sz] = ImageFont.truetype(FB, sz)
    return SUBF[sz]
def up(t): return t.replace("i", "İ").replace("ı", "I").upper()
def vo_words(v, t0):
    if v in VOT: return [(t0 + a, t0 + b, w) for a, b, w in VOT[v]["words"]]
    txt = dict((a, b) for a, b, c in VO)[v].split(); d = vo_dur(v)
    wl = np.array([len(x) + 2 for x in txt], float); st = np.r_[0, np.cumsum(wl)[:-1]] / wl.sum() * d
    return [(t0 + s, t0 + s + 0.3, w) for s, w in zip(st, txt)]
def chunks(words, maxw=840, sz=62):
    out, cur = [], []
    for w in words:
        test = cur + [w]; width = sum(subword(x[2], False, sz).width for x in test) + 20 * (len(test) - 1)
        if cur and (width > maxw or len(cur) >= 4): out.append(cur); cur = [w]
        else: cur = test
        if w[2][-1] in ".,;?!" and len(cur) >= 2: out.append(cur); cur = []
    if cur: out.append(cur)
    return out
_swc = {}
def subword(w, active, sz=62):
    key = (w, active, sz)
    if key not in _swc: _swc[key] = timg(up(w), subfont(sz), GOLD if active else WHITE, stroke=8)
    return _swc[key]
SUBLINES = []
for s in SECS:
    if not s["vo"]: continue
    ws = vo_words(s["vo"], s["vo_t"]); cs = chunks(ws)
    for j, c in enumerate(cs):
        end = cs[j + 1][0][0] - 0.02 if j + 1 < len(cs) else c[-1][1] + 0.45
        SUBLINES.append((c[0][0], end, c))

def sub_y(n):
    hb = heads(n)
    if not hb: return 1395
    return int(min(max(max(h[3] for h in hb) + 70, 1080), 1430))

EV = []  # (t0, t1, img, cx, cy)
for s in SECS:
    t0, t1 = s["f0"] / FPS, (s["f0"] + s["n"]) / FPS
    if s["title"] == "title": EV.append((t0 + 0.15, t1 - 0.2, TITLE, 490, 760))
    elif s["title"] == "address": EV.append((t0 + 0.25, t1 - 0.1, ADDR, 490, 1100))
    elif s["title"] == "endcard": EV.append((t0 + 0.2, TOTAL / FPS, END, 490, 520))
    elif s["title"]: EV.append((t0 + 0.12, min(t1, t0 + 2.4) - 0.1, HEADERS[s["title"]], 490, 330))

def render(n):
    t = n / FPS; c = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for a, b, im, cx, cy in EV:
        if a <= t < b:
            p = ease_out((t - a) / 0.35); al = p * (1 - ease_out((t - (b - 0.2)) / 0.2))
            paste(c, im, cx, cy, 0.94 + 0.06 * p, al, dy=(1 - p) * 26)
    for a, b, ws in SUBLINES:
        if not (a <= t < b): continue
        shown = [w for w in ws if t >= w[0]]
        if not shown: continue
        sz = 62; full = [subword(w[2], False, sz) for w in ws]; sp = 20
        tot = sum(i.width for i in full) + sp * (len(full) - 1); x = 490 - tot / 2; y = sub_y(n)
        al = 1 - ease_out((t - (b - 0.12)) / 0.12)
        for j, w in enumerate(ws):
            if t >= w[0]:
                act = j == len(shown) - 1
                paste(c, subword(w[2], act, sz), x + full[j].width / 2, y, 0.8 + 0.2 * ease_back((t - w[0]) / 0.12), al)
            x += full[j].width + sp
    return c

def compose(n):
    im = Image.fromarray(cv2.cvtColor(frame_bg(n), cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.alpha_composite(render(n)); return im.convert("RGB")

# ------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    if MODE == "plan":
        print(f"TOPLAM {TOTAL / FPS:.2f} sn, {len(SHOTS)} cekim, {len(SECS)} bolum")
        for s in SECS: print(f"[{s['id']}] {s['f0']/FPS:6.2f}-{(s['f0']+s['n'])/FPS:6.2f}  VO={s['vo']} @{s['vo_t']}")
        for s in SHOTS: print(f"   {s['f0']/FPS:6.2f}-{(s['f0']+s['n'])/FPS:6.2f} {s['clip'][:34]:34s} kaynak {s['src0']:.2f}-{s['src0']+s['n']/FPS:.2f} {s['move']:5s} -> {s['trans']}")
        for a, b, ws in SUBLINES: print(f"   SUB {a:6.2f}-{b:6.2f} " + " ".join(w[2] for w in ws))
    elif MODE == "md":
        TRN = {"cut": "kesme (vuruşta)", "whipL": "whip ←", "whipR": "whip →", "zoom": "zoom-through + riser/impact", "flash": "ışık patlaması + shimmer", "fade": "karartma"}
        HD = {s[0]: s[2] for s in SECTIONS}
        print("| Çıkış (sn) | Bölüm | Dış ses (tahmini yerleşim) | Çekim | Kaynak (sn) | Hareket | Ekrandaki grafik | Çıkış geçişi |")
        print("|---|---|---|---|---|---|---|---|")
        for s in SHOTS:
            sec = next(x for x in SECS if x["id"] == s["sec"]); first = s["f0"] == sec["f0"]
            vo = (dict((a, b) for a, b, c in VO)[sec["vo"]] if sec["vo"] else "— (müzik)") if first else "↳"
            h = HD[s["sec"]]; g = {"title": "LADİNOS OTEL açılış kartı", "address": "📍 adres kartı", "endcard": "kapanış kartı (otel adı + adres)"}.get(h, f"bölüm başlığı: {h}" if h else "—") if first else "↳"
            clip = s["clip"].replace("SPLIT:", "bölünmüş ekran ").replace("|", " / ")
            src = "—" if s["clip"].startswith("SPLIT") else f"{s['src0']:.2f}–{s['src0'] + s['n'] / FPS:.2f}"
            mv = {"push": "yavaş ileri zoom", "none": "—"}.get(s["move"], s["move"])
            print(f"| {s['f0']/FPS:.2f}–{(s['f0']+s['n'])/FPS:.2f} | {s['sec']} | {vo} | {clip} | {src} | {mv} | {g} | {TRN[s['trans']]} |")
    elif MODE == "check":
        bad, ui, ys0, ys1 = [], [], 1e9, 0
        for n in range(TOTAL):
            a = np.array(render(n).getchannel("A")); ys, xs = np.nonzero(a > 8)
            if not len(ys): continue
            ys0, ys1 = min(ys0, ys.min()), max(ys1, ys.max())
            for hb in heads(n):
                x0, y0, x1, y1 = [max(0, int(v)) for v in hb]
                hit = int((a[y0:y1, x0:x1] > 8).sum())
                if hit: bad.append((n, round(n / FPS, 2), SHOTS[AT[n][0]]["clip"], hit))
            if ys.min() < SAFE_TOP or ys.max() > SAFE_BOTTOM or xs.max() > SAFE_RIGHT or xs.min() < SAFE_LEFT:
                ui.append((n, round(n / FPS, 2), int(ys.min()), int(ys.max()), int(xs.min()), int(xs.max())))
        print(f"kare={TOTAL}  yuz/kafa cakismasi={len(bad)}  arayuz ihlali={len(ui)}  grafik y {ys0}-{ys1}")
        for b in bad[:10]: print("  CAKISMA", b)
        for u in ui[:10]: print("  ARAYUZ", u)
        print("SONUC:", "GECTI" if not bad and not ui else "KALDI")
    elif MODE == "samples":
        od = os.path.join(WORK, "samples2"); os.makedirs(od, exist_ok=True)
        f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 28); tiles = []
        for t in [float(x) for x in ARG[0].split(",")]:
            n = min(int(round(t * FPS)), TOTAL - 1); im = compose(n); im.save(os.path.join(od, f"kare_{t:05.2f}.jpg"), quality=92)
            th = im.resize((300, 533), Image.LANCZOS); d = ImageDraw.Draw(th)
            d.rectangle((0, 0, 300, 40), fill=(0, 0, 0)); d.text((8, 5), f"{t:.2f} sn · {SHOTS[AT[n][0]]['sec']}", font=f, fill="white"); tiles.append(th)
        cols = 5; rows = (len(tiles) + cols - 1) // cols
        sh = Image.new("RGB", (cols * 308 + 8, rows * 541 + 8), "white")
        for i, th in enumerate(tiles): sh.paste(th, (8 + (i % cols) * 308, 8 + (i // cols) * 541))
        sh.save(os.path.join(od, "ornek_kareler.jpg"), quality=86); print("->", od)
    elif MODE == "full":
        out = ARG[0]; aud = ARG[1] if len(ARG) > 1 else None
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        if aud: cmd += ["-i", aud, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "256k", "-shortest"]
        cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
                "-color_trc", "bt709", "-colorspace", "bt709", "-movflags", "+faststart", out]
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for n in range(TOTAL):
            p.stdin.write(np.asarray(compose(n)).tobytes())
            if n % 300 == 0: print(f"  {n}/{TOTAL}", flush=True)
        p.stdin.close(); p.wait(); print("yazildi:", out)
