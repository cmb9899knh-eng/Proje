s = open("render.py").read()
def R(a, b):
    global s
    assert a in s, a[:70]; s = s.replace(a, b)

# ---- 1) gecis / zoom altyapisi + head_boxes donusumu
R('''def head_boxes(t):
    """Basi tamamen kapsayan kutular (yuz + basortusu/sac payi + cene)."""
    x = seg_at(t)
    if x["kind"].startswith("split"): return []          # bolunmus ekranda yalnizca kucuk yanlis pozitifler var
    L = FACES[x["clip"]]; i = min(len(L) - 1, src_frame(x, t))
    out = []''', '''# ---------------------------------------------------------------- gecisler, zoom
TIDX = {id(x): i for i, x in enumerate(TL)}
def nb(x, d):
    i = TIDX[id(x)] + d; return TL[i] if 0 <= i < len(TL) else None
PUNCHZ = {}
for i, x in enumerate(TL):     # punch: ayni klipte jump-cut'i gizlemek icin %7 zoom, sirayla ac/kapa
    p = TL[i - 1] if i else None
    PUNCHZ[id(x)] = (1.07 if PUNCHZ.get(id(p), 1.0) == 1.0 else 1.0) if (x.get("tr") == "punch" and p and p["clip"] == x["clip"]) else 1.0
DISS, WHIP, FLASH = 0.5, 0.14, 0.18
def zoom_of(x, t):
    kb = x.get("kb") or 1.0; d = max(1e-3, x["t1"] - x["t0"])
    p = min(max((t - x["t0"] + (DISS / 2 if x.get("tr") == "dissolve" else 0)) / (d + DISS), 0), 1)
    return PUNCHZ[id(x)] * (1 + (kb - 1) * p)
def layers(t):
    """Bu anda gorunen katmanlar: [(segment, alfa, yatay_kayma_px, blur_px)]"""
    x = seg_at(t); out = [[x, 1.0, 0.0, 0]]
    nx, pv = nb(x, 1), nb(x, -1)
    if nx and nx.get("tr") == "dissolve" and t > x["t1"] - DISS / 2:
        m = (t - (x["t1"] - DISS / 2)) / DISS; out = [[x, 1.0, 0, 0], [nx, m, 0, 0]]
    if x.get("tr") == "dissolve" and pv and t < x["t0"] + DISS / 2:
        m = (t - (x["t0"] - DISS / 2)) / DISS; out = [[pv, 1.0, 0, 0], [x, m, 0, 0]]
    if nx and nx.get("tr") == "whip" and t > x["t1"] - WHIP:
        p = (t - (x["t1"] - WHIP)) / WHIP; out = [[x, 1.0, -W * 0.6 * p ** 2, int(10 + 120 * p)]]
    if x.get("tr") == "whip" and t < x["t0"] + WHIP:
        p = (t - x["t0"]) / WHIP; out = [[x, 1.0, W * 0.6 * (1 - p) ** 2, int(10 + 120 * (1 - p))]]
    return out
def xbox(b, x, t, dx=0):
    z = zoom_of(x, t); cx, cy = W / 2, H / 2
    return (cx + (b[0] - cx) * z + dx, cy + (b[1] - cy) * z, cx + (b[2] - cx) * z + dx, cy + (b[3] - cy) * z)

def head_boxes(t):
    out = []
    for x, a, dx, bl in layers(t):
        if a <= 0.05: continue
        out += [xbox(b, x, t, dx) for b in raw_head_boxes(x, t)]
    return out

def raw_head_boxes(x, t):
    """Basi tamamen kapsayan kutular (yuz + basortusu/sac payi + cene), kaynak koordinatinda."""
    if x["kind"].startswith("split") or x["kind"] == "foto": return []
    L = FACES[x["clip"]]; i = max(0, min(len(L) - 1, src_frame(x, t)))
    out = []''')

# ---- 2) basliklar: olay listesi zaman cizelgesinden
R('''def big_title():
    f1 = ImageFont.truetype(FB, 170); f2 = ImageFont.truetype(FXB, 54)
    a = text_img("MARDİN", f1, WHITE, 0); b = text_img("gezi günlüğü", f2, WHITE)''', '''def big_title(sub="VOL 2"):
    f1 = ImageFont.truetype(FB, 170); f2 = ImageFont.truetype(FXB, 54)
    a = text_img("MARDİN", f1, WHITE, 0); b = text_img(sub, f2, WHITE)''')
a = s.index("EVENTS = ["); b = s.index("def seg_by_clip")
s = s[:a] + '''ICON = {"ANTİK KENT": "arch", "KAFE DURAĞI": "cup", "ÇARŞI": "bag", "MEYDAN": "pin", "BADEM ŞEKERİ": "candy",
        "MEZOPOTAMYA": "mount", "FOTOĞRAF MOLASI": "camera"}
def _first(clip): return next(x for x in TL if x["clip"] == clip)
EVENTS = [("title", _first("3294_ffe9")["t0"] + 0.15, _first("3148")["t1"] - 0.1, "VOL 2")]
for i, x in enumerate(TL):
    if x.get("sec"):
        EVENTS.append(("badge", x["t0"] + 0.2, x["t0"] + 3.2, (x["sec"], ICON[x["sec"]])))
EVENTS.append(("title", TL[-1]["t0"] + 0.4, DUR - 0.05, "bir efsane"))
''' + s[b:]
R('''            w, h, pad = inner(big_title() if kind == "title" else badge(*c, scale=sc))''', '''            w, h, pad = inner(big_title(c) if kind == "title" else badge(*c, scale=sc))''')
R('''        im, pad = big_title() if kind == "title" else badge(*c, scale=sc)''', '''        im, pad = big_title(c) if kind == "title" else badge(*c, scale=sc)''')

# ---- 3) yeni ikonlar
R('''    elif kind == "candy":''', '''    elif kind == "arch":
        d.rectangle((S*.10, S*.30, S*.90, S*.95), fill=col); d.rectangle((S*.05, S*.18, S*.95, S*.30), fill=col)
        d.ellipse((S*.32, S*.45, S*.68, S*.80), fill=(0, 0, 0, 0)); d.rectangle((S*.32, S*.62, S*.68, S*.95), fill=(0, 0, 0, 0))
    elif kind == "mount":
        d.polygon([(S*.0, S*.92), (S*.38, S*.25), (S*.62, S*.62), (S*.74, S*.45), (S*1.0, S*.92)], fill=col)
        d.ellipse((S*.70, S*.06, S*.92, S*.28), fill=col)
    elif kind == "camera":
        d.rounded_rectangle((S*.05, S*.28, S*.95, S*.88), radius=int(S*.1), fill=col); d.rectangle((S*.32, S*.16, S*.62, S*.30), fill=col)
        d.ellipse((S*.32, S*.38, S*.68, S*.78), fill=(0, 0, 0, 0)); d.ellipse((S*.40, S*.46, S*.60, S*.70), fill=col)
    elif kind == "candy":''')

# ---- 4) kare uretimi
a = s.index("def base_frame(t):"); b = s.index("LABEL_F = ImageFont")
s = s[:a] + open("patch_v2_frames.py").read() + s[b:]
open("render.py", "w").write(s)
print("ok")
