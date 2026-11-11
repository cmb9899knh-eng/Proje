"""Video kompozisyonu: SDR proxy'lerden kurgu + zoom + bolunmus ekran + grafik katmani.
Kullanim:
  python3 render.py <work> samples <t1,t2,...>   -> onizleme kareleri + iletisim sayfasi + guvenli alan gorseli
  python3 render.py <work> full <cikis.mp4>       -> tam video (mix.wav ile)  [onaydan sonra]
"""
import sys, os, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
WORK, MODE = sys.argv[1], sys.argv[2]
ARG = sys.argv[3] if len(sys.argv) > 3 else ""
sys.argv = [sys.argv[0], WORK, "x"]
from edl import SEGS, SPLIT, FPS, TOTAL, timeline
import overlay
W, H = 1080, 1920
SDR = os.path.join(WORK, "sdr")
CREAM = (250, 243, 230)

class Reader:  # sirali okuma icin klip basina acik VideoCapture
    def __init__(self): self.caps = {}
    def get(self, clip, idx):
        cap, pos = self.caps.get(clip, (None, -1))
        if cap is None: cap = cv2.VideoCapture(os.path.join(SDR, clip + ".mov"))
        if idx != pos + 1: cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ok, im = cap.read()
        if not ok: raise RuntimeError(f"{clip} kare {idx} okunamadi")
        self.caps[clip] = (cap, idx); return im
R = Reader()

def zoom(im, z):
    if abs(z - 1) < 1e-3: return im
    big = cv2.resize(im, None, fx=z, fy=z, interpolation=cv2.INTER_LANCZOS4)
    y0 = int(round(960 * z - 960)); x0 = int(round(540 * z - 540))
    return big[y0:y0 + H, x0:x0 + W]

def bg(n):
    s, k = overlay.SEG_AT[n]
    if s[1] == "SPLIT":
        out = np.zeros((H, W, 3), np.uint8)
        for (clip, a), y in zip(SPLIT, (0, 963)):
            im = R.get(clip, round(a * FPS) + k)
            out[y:y + 957] = im[481:481 + 957]
        out[957:963] = CREAM[::-1]
        return out
    return zoom(R.get(s[1], round(s[2] * FPS) + k), s[5])

def compose(n):
    im = Image.fromarray(cv2.cvtColor(bg(n), cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.alpha_composite(overlay.render(n)); return im.convert("RGB")

if MODE == "samples":
    od = os.path.join(WORK, "samples"); os.makedirs(od, exist_ok=True)
    ts = [float(x) for x in ARG.split(",")]
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 30)
    tiles = []
    for t in ts:
        n = min(int(round(t * FPS)), TOTAL - 1); im = compose(n)
        im.save(os.path.join(od, f"kare_{t:05.2f}.jpg"), quality=92)
        th = im.resize((360, 640), Image.LANCZOS); d = ImageDraw.Draw(th)
        d.rectangle((0, 0, 360, 44), fill=(0, 0, 0)); d.text((10, 6), f"{t:.2f} sn · {overlay.SEG_AT[n][0][0]}", font=f, fill="white")
        tiles.append(th)
    cols = 4; rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 370 + 10, rows * 650 + 10), "white")
    for i, th in enumerate(tiles): sheet.paste(th, (10 + (i % cols) * 370, 10 + (i // cols) * 650))
    sheet.save(os.path.join(od, "ornek_kareler.jpg"), quality=88)
    # guvenli alan + kafa kutusu gorsellestirme (2 kare)
    F = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 40); g2 = []
    for t in (12.8, 47.3):
        n = int(round(t * FPS)); g = compose(n).convert("RGBA"); lay = Image.new("RGBA", g.size, (0, 0, 0, 0)); gd = ImageDraw.Draw(lay)
        gd.rectangle((0, 0, W, overlay.SAFE_TOP), fill=(255, 0, 0, 90)); gd.rectangle((0, overlay.SAFE_BOTTOM, W, H), fill=(255, 0, 0, 90))
        gd.rectangle((overlay.SAFE_RIGHT, overlay.SAFE_TOP, W, overlay.SAFE_BOTTOM), fill=(255, 0, 0, 60))
        for hb in overlay.heads(n): gd.rectangle(hb, outline=(0, 255, 120, 255), width=6)
        gd.text((30, 90), "Instagram üst arayüz", font=F, fill="white"); gd.text((30, 1680), "Instagram alt arayüz / açıklama", font=F, fill="white")
        g.alpha_composite(lay); g2.append(g.convert("RGB").resize((540, 960), Image.LANCZOS))
    gs = Image.new("RGB", (1090, 960), "white"); gs.paste(g2[0], (0, 0)); gs.paste(g2[1], (550, 0))
    gs.save(os.path.join(od, "guvenli_alan.jpg"), quality=88)
    print("ornekler:", od)
elif MODE == "full":
    out = ARG
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-i", os.path.join(WORK, "build", "mix.wav"), "-map", "0:v", "-map", "1:a",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", "-profile:v", "high",
                          "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                          "-c:a", "aac", "-b:a", "256k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for n in range(TOTAL):
        p.stdin.write(np.asarray(compose(n)).tobytes())
        if n % 150 == 0: print(f"  {n}/{TOTAL}", flush=True)
    p.stdin.close(); p.wait(); print("yazildi:", out)
