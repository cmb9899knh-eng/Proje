# renk: ortak sicak/kontrastli ton + hafif vinyet (tum kliplere ayni)
_x = np.arange(256) / 255.0
_curve = np.clip(_x - 0.05 * np.sin(2 * np.pi * (_x - 0.5)), 0, 1)          # yumusak S-egri
_curve = np.clip((_curve - 0.5) * 1.06 + 0.5, 0, 1)
LUT8 = (np.stack([np.clip(_curve * 1.035 + 0.006, 0, 1), _curve, np.clip(_curve * 0.95, 0, 1)], 1) * 255).astype(np.uint8)
_yy, _xx = np.mgrid[0:H, 0:W]; _r = np.sqrt(((_xx - W / 2) / (W * 0.75)) ** 2 + ((_yy - H / 2) / (H * 0.72)) ** 2)
VIG = (1 - 0.22 * np.clip(_r - 0.35, 0, 1) ** 1.6)[..., None].astype(np.float32)
def grade(rgb):
    out = np.empty_like(rgb)
    for c in range(3): out[..., c] = LUT8[rgb[..., c], c]
    hsv = cv2.cvtColor(out, cv2.COLOR_RGB2HSV); hsv[..., 1] = np.clip(hsv[..., 1].astype(np.int16) * 112 // 100, 0, 255).astype(np.uint8)
    out = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    return (out.astype(np.float32) * VIG).astype(np.uint8)

def read_np(clip, n):
    return np.array(read_src(clip, max(0, n)).convert("RGB"))

def zoom_np(img, z):
    if abs(z - 1) < 1e-3: return img
    h, w = img.shape[:2]; x0, y0 = (w - w / z) / 2, (h - h / z) / 2
    M = np.float32([[z, 0, -x0 * z], [0, z, -y0 * z]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

PHOTOS = sorted(__import__("glob").glob("fotolar/*.*"))   # kullanicinin fotograflari gelince buraya
def photo_cards():
    if PHOTOS: return [Image.open(p).convert("RGB") for p in PHOTOS[:4]], False
    ph = []   # yer tutucu: cekimden kareler
    for c, tt in (("3308_6bd7", 0.6), ("3309_8598", 3.0), ("3150_ddcd", 5.0)):
        ph.append(Image.fromarray(read_np(c, round(tt * FPS))))
    return ph, True
_PH = None
def photo_frame(x, t):
    global _PH
    if _PH is None: _PH = photo_cards()
    cards, placeholder = _PH
    pv = nb(x, -1); bg = read_np(pv["clip"], round(pv["e"] * FPS) - 1)
    bg = cv2.GaussianBlur(bg, (0, 0), 28); bg = (bg * 0.75).astype(np.uint8)
    fr = Image.fromarray(bg).convert("RGBA"); lt = t - x["t0"]; d = x["t1"] - x["t0"]; n = len(cards); step = d / n
    rots = [-7, 5, -3, 6]; offs = [(-40, -60), (50, 10), (-20, 70), (30, -20)]
    for k, c in enumerate(cards):
        st = k * step
        if lt < st: break
        p = ease_back((lt - st) / 0.35)
        im = c.copy(); im.thumbnail((720, 940)); iw, ih = im.size
        pad = 28; card = Image.new("RGBA", (iw + 2 * pad, ih + pad + 120), (250, 248, 242, 255))
        kb = 1 + 0.05 * min(1, (lt - st) / d)
        big = im.resize((int(iw * kb), int(ih * kb)), Image.LANCZOS); ox, oy = (big.width - iw) // 2, (big.height - ih) // 2
        card.paste(big.crop((ox, oy, ox + iw, oy + ih)), (pad, pad))
        if placeholder:
            f = ImageFont.truetype(FXB, 34); ImageDraw.Draw(card).text((pad, ih + pad + 36), "ÖRNEK · senin fotoğrafın gelecek", font=f, fill=(120, 120, 120, 255))
        card = card.rotate(rots[k % 4] * (0.6 + 0.4 * min(1, p)), resample=Image.BICUBIC, expand=True)
        s_ = max(0.05, 0.55 + 0.45 * p); card = card.resize((max(1, int(card.width * s_)), max(1, int(card.height * s_))), Image.LANCZOS)
        sh, r = with_shadow(card, r=18, a=0.5, dy=10)
        cx, cy = W / 2 + offs[k % 4][0], H * 0.47 + offs[k % 4][1]
        fr.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
    return np.array(fr.convert("RGB"))

def seg_np(x, t):
    if x["kind"] == "foto": return photo_frame(x, t)
    n = src_frame(x, t)
    if x["kind"].startswith("split"):
        other = x["kind"].split(":")[1]
        a = read_np(x["clip"], n)[:, 270:810]; b = read_np(other, n)[:, 270:810]
        p = ease_out((t - x["t0"]) / 0.3); fr = np.full((H, W, 3), 255, np.uint8)
        oa = int(-H * (1 - p)); ob = int(H * (1 - p))
        fr[max(0, oa):H + min(0, oa), 0:540] = a[max(0, -oa):H - max(0, oa)]
        fr[max(0, ob):H + min(0, ob), 540:1080] = b[max(0, -ob):H - max(0, ob)]
        fr[:, 537:543] = 255; return fr
    return zoom_np(read_np(x["clip"], n), zoom_of(x, t))

def leak(t):
    """Bolum gecislerinde (whip) sicak isik sizmasi: 0.7 sn, ekran karisimi."""
    for x in TL:
        if x.get("tr") == "whip" and 0 <= t - x["t0"] + 0.1 < 0.7:
            p = (t - x["t0"] + 0.1) / 0.7; a = np.sin(np.pi * p) * 0.55
            cx = W * (1.1 - 1.2 * p); g = np.exp(-(((_xx - cx) / 420.0) ** 2 + ((_yy - H * 0.3) / 900.0) ** 2))
            return (g[..., None] * np.array([255, 150, 60], np.float32) * a)
    return None

def base_frame(t):
    acc = None
    for x, a, dx, bl in layers(t):
        img = seg_np(x, t)
        if dx or bl:
            M = np.float32([[1, 0, dx], [0, 1, 0]]); img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
            if bl > 1: img = cv2.blur(img, (bl, 1))
        acc = img.astype(np.float32) if acc is None else acc * (1 - a) + img.astype(np.float32) * a
    for x in TL:   # flas gecisi
        if x.get("tr") == "flash" and 0 <= t - x["t0"] < FLASH:
            f = 1 - (t - x["t0"]) / FLASH; acc = acc * (1 - 0.8 * f) + 255 * 0.8 * f
    lk = leak(t)
    if lk is not None: acc = 255 - (255 - acc) * (1 - lk / 255)
    fr = grade(np.clip(acc, 0, 255).astype(np.uint8))
    if t > DUR - 0.6: fr = (fr * max(0, (DUR - t) / 0.6)).astype(np.uint8)   # sona karartma
    return Image.fromarray(fr).convert("RGBA")

