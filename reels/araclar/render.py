"""Overlay + SFX generator for the mic-test reel.
Usage: python3 render.py <workdir> [frames-to-preview,comma-separated]
Writes <workdir>/ov/%04d.png (RGBA overlays), <workdir>/sfx.wav, and runs a face-overlap check.
"""
import sys, json, math, wave, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
WORK = sys.argv[1]
S = os.path.dirname(os.path.abspath(__file__))
FONT_B = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FONT_XB = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"

# ---- timeline (output seconds) -------------------------------------------
A_SRC, B_SRC = (2.5, 4.366667), (5.433333, 7.066667)
CUT = A_SRC[1] - A_SRC[0]                      # 1.8667
DUR = CUT + (B_SRC[1] - B_SRC[0])               # 3.5
N = round(DUR * FPS)
def src_time(t):
    return A_SRC[0] + t if t < CUT else B_SRC[0] + (t - CUT)

LINES = [  # (line start, line end, [(word, onset)])
    (0.0, CUT, [("SES", 0.12), ("1", 0.62), ("2", 0.93), ("3", 1.28)]),
    (CUT, DUR, [("SESİM", 1.99), ("GELİYOR", 2.46), ("MU?", 2.76)]),
]
POLL_T = 2.86

# ---- safe zones ------------------------------------------------------------
SAFE_TOP, SAFE_BOTTOM, SAFE_RIGHT = 230, 1500, 940   # Instagram UI: header / caption+buttons
SUB_Y = 1428                                          # chest line centre

faces = json.load(open(os.path.join(S, "faces.json")))   # source-time face boxes (YuNet, 30fps)
def face_box(t):
    i = min(len(faces) - 1, round(src_time(t) * FPS))
    _, x, y, w, h, _ = faces[i]
    # expand to whole head (hair above brows, ears at sides)
    return (x - 0.12 * w, y - 0.20 * h, x + 1.12 * w, y + 1.04 * h)

# ---- audio analysis for VU bars --------------------------------------------
def read_wav(p):
    w = wave.open(p); sr = w.getframerate()
    return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768, sr
voice, VSR = read_wav(os.path.join(WORK, "cut_voice.wav"))
NB = 21
def bands(t):
    i = int(t * VSR); seg = voice[max(0, i - 1024):i + 1024]
    if len(seg) < 2048: seg = np.pad(seg, (0, 2048 - len(seg)))
    sp = np.abs(np.fft.rfft(seg * np.hanning(2048)))
    f = np.fft.rfftfreq(2048, 1 / VSR)
    edges = np.geomspace(120, 6000, NB + 1)
    v = np.array([sp[(f >= edges[k]) & (f < edges[k + 1])].mean() for k in range(NB)])
    v = np.clip((20 * np.log10(v + 1e-6) + 22 + 1.6 * np.arange(NB)) / 42, 0, 1)
    return v

# ---- helpers -----------------------------------------------------------------
def ease_back(x):  # overshoot pop
    x = min(max(x, 0), 1); c = 1.9
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ease_out(x):
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

def text_img(txt, font, fill, stroke=0, stroke_fill=(0, 0, 0, 255)):
    b = font.getbbox(txt, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 4, b[3] - b[1] + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((2 - b[0], 2 - b[1]), txt, font=font, fill=fill,
                            stroke_width=stroke, stroke_fill=stroke_fill)
    return im

def paste_scaled(canvas, im, cx, cy, s, alpha=1.0):
    if s <= 0.01 or alpha <= 0: return
    im2 = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    if alpha < 1:
        a = im2.getchannel("A").point(lambda v: int(v * alpha)); im2.putalpha(a)
    canvas.alpha_composite(im2, (int(cx - im2.width / 2), int(cy - im2.height / 2)))

def shadow(im, r=10, a=0.55):
    sh = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    m = im.getchannel("A").point(lambda v: int(v * a))
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(m)
    sh.alpha_composite(blk, (2 * r, 2 * r + r // 2))
    sh = sh.filter(ImageFilter.GaussianBlur(r))
    sh.alpha_composite(im, (2 * r, 2 * r)); return sh

# ---- static elements ----------------------------------------------------------
YEL = (255, 210, 63, 255); WHITE = (255, 255, 255, 255); INK = (17, 17, 17, 255)

def make_title():
    f = ImageFont.truetype(FONT_B, 58)
    t = text_img("MİKROFON TESTİ", f, INK)
    pad_x, pad_y, icon = 36, 20, 44
    w, h = t.width + 2 * pad_x + icon + 14, t.height + 2 * pad_y
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=WHITE)
    # simple mic glyph (drawn, no external asset)
    cx, cy = pad_x + icon // 2, h // 2
    d.rounded_rectangle((cx - 11, cy - 22, cx + 11, cy + 6), radius=11, fill=YEL, outline=INK, width=4)
    d.arc((cx - 18, cy - 12, cx + 18, cy + 16), 0, 180, fill=INK, width=4)
    d.line((cx, cy + 16, cx, cy + 24), fill=INK, width=4)
    d.line((cx - 10, cy + 24, cx + 10, cy + 24), fill=INK, width=4)
    im.alpha_composite(t, (pad_x + icon + 14, pad_y - 2))
    return shadow(im, 8, 0.35)
TITLE = make_title()

def make_poll():
    f = ImageFont.truetype(FONT_B, 38)
    def pill(label, col, mark):
        t = text_img(label, f, WHITE)
        w, h = t.width + 108, 76
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=h // 2, fill=col)
        cx, cy = 42, h // 2
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=WHITE)
        if mark == "yes":
            d.line((cx - 11, cy + 1, cx - 3, cy + 10, cx + 12, cy - 9), fill=col, width=7, joint="curve")
        else:
            d.line((cx - 9, cy - 9, cx + 9, cy + 9), fill=col, width=7)
            d.line((cx - 9, cy + 9, cx + 9, cy - 9), fill=col, width=7)
        im.alpha_composite(t, (76, (h - t.height) // 2 - 3)); return im
    return shadow(pill("GELİYOR", (36, 170, 90, 255), "yes"), 8, 0.35), \
           shadow(pill("GELMİYOR", (226, 72, 72, 255), "no"), 8, 0.35)
POLL_Y, POLL_N = make_poll()

SUB_FONT = ImageFont.truetype(FONT_B, 74)
def sub_word(w, active):
    return text_img(w, SUB_FONT, YEL if active else WHITE, stroke=8)

# ---- frame renderer -----------------------------------------------------------
TITLE_C = (540, 300)
BARS_Y = 432          # baseline; bars grow upward to ~372
POLL_C = 404
def render(n):
    t = n / FPS
    c = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    # title pop-in at start
    paste_scaled(c, TITLE, *TITLE_C, ease_back(t / 0.25))
    # VU bars during "Ses 1 2 3" (fade out into the cut)
    if t < CUT + 0.15:
        al = ease_out(t / 0.2) * (1 - ease_out((t - CUT + 0.1) / 0.25))
        v = bands(t); bw, gap = 14, 9; x0 = 540 - (NB * (bw + gap) - gap) / 2
        for k in range(NB):
            hgt = 8 + 54 * v[k]
            x = x0 + k * (bw + gap)
            col = YEL if v[k] > 0.55 else WHITE
            d.rounded_rectangle((x, BARS_Y - hgt, x + bw, BARS_Y), radius=7,
                                fill=col[:3] + (int(255 * al),))
    # yes/no poll after the question
    if t >= POLL_T:
        p = t - POLL_T
        paste_scaled(c, POLL_Y, 540 - 168, POLL_C, ease_back(p / 0.22))
        paste_scaled(c, POLL_N, 540 + 168, POLL_C, ease_back((p - 0.07) / 0.22))
    # word-by-word subtitles at chest height
    for (ls, le, words) in LINES:
        if not (ls <= t < le): continue
        shown = [(w, o) for (w, o) in words if t >= o]
        if not shown: continue
        imgs = [sub_word(w, i == len(shown) - 1) for i, (w, o) in enumerate(shown)]
        full = [sub_word(w, False) for (w, o) in shown]
        space = 26
        total = sum(i.width for i in full) + space * (len(full) - 1)
        x = 505 - total / 2
        for i, (w, o) in enumerate(shown):
            s = 0.6 + 0.4 * ease_back((t - o) / 0.16)
            paste_scaled(c, imgs[i], x + full[i].width / 2, SUB_Y, s)
            x += full[i].width + space
    return c

# ---- SFX (synthesised, no external audio) ------------------------------------
SR = 48000
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def pop(f0=880, f1=330, d=0.07):
    n = int(d * SR); t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / d); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * env_exp(n, 0.018) * np.minimum(1, np.arange(n) / 48)
def whoosh(d=0.42):
    n = int(d * SR); rng = np.random.default_rng(7); x = rng.standard_normal(n)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(n, 1 / SR)
    X *= 1 / np.sqrt(1 + (f / 2500) ** 4); y = np.fft.irfft(X, n)
    # sweeping band via short-time crossfade of low/high passed versions
    lo = np.convolve(y, np.ones(24) / 24, "same"); hi = y - lo
    p = np.linspace(0, 1, n); y = lo * (1 - p) + hi * p * 0.8
    e = np.sin(np.pi * np.clip(p, 0, 1)) ** 2 * np.exp(-1.5 * p)
    return y / np.abs(y).max() * e
def ding(f=1318.5, d=0.9):
    n = int(d * SR); t = np.arange(n) / SR
    y = (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) * env_exp(n, 0.12)
         + 0.25 * np.sin(2 * np.pi * 3.01 * f * t) * env_exp(n, 0.06))
    return y * env_exp(n, 0.28) * np.minimum(1, np.arange(n) / 96)

def build_sfx():
    out = np.zeros(int(DUR * SR) + SR)
    def add(sig, at, gain_db):
        i = int(at * SR); out[i:i + len(sig)] += sig[:len(out) - i] * 10 ** (gain_db / 20)
    add(pop(700, 260, 0.09), 0.0, -14)              # title pop
    for _, o in LINES[0][2][1:]: add(pop(), o, -20)  # count ticks 1-2-3
    w = whoosh(); add(w, CUT - len(w) / SR * 0.55, -16)  # cut transition
    add(ding(), POLL_T, -19); add(ding(1975.5), POLL_T + 0.07, -25)
    out = out[:int(DUR * SR)]
    pcm = (np.clip(out, -1, 1) * 32767).astype(np.int16)
    wf = wave.open(os.path.join(WORK, "sfx.wav"), "wb"); wf.setnchannels(1); wf.setsampwidth(2)
    wf.setframerate(SR); wf.writeframes(pcm.tobytes()); wf.close()

# ---- main ----------------------------------------------------------------------
if __name__ == "__main__":
    os.makedirs(os.path.join(WORK, "ov"), exist_ok=True)
    only = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else range(N)
    worst = []
    for n in only:
        im = render(n); im.save(os.path.join(WORK, "ov", f"{n:04d}.png"))
        a = np.array(im.getchannel("A"))
        x0, y0, x1, y1 = [int(v) for v in face_box(n / FPS)]
        hit = int((a[max(0, y0):y1, max(0, x0):x1] > 8).sum())
        ys, xs = np.nonzero(a > 8)
        worst.append((n, hit, (ys.min() if len(ys) else None), (ys.max() if len(ys) else None),
                      (xs.max() if len(xs) else None), y0, y1))
    build_sfx()
    bad = [w for w in worst if w[1] > 0]
    ui = [w for w in worst if w[2] is not None and (w[2] < SAFE_TOP or w[3] > SAFE_BOTTOM or w[4] > SAFE_RIGHT)]
    print(f"frames={len(worst)}  face-overlap frames={len(bad)}  UI-zone violations={len(ui)}")
    for w in bad[:5] + ui[:5]: print("  ", w)
    mins = [w[2] for w in worst if w[2] is not None]; maxs = [w[3] for w in worst if w[3] is not None]
    gap_top = min(w[5] - w[3] for w in worst if w[3] is not None and w[3] < 700) if any(w[3] is not None and w[3] < 700 for w in worst) else None
    print("graphics y-range:", min(mins), "-", max(maxs), " | head top min:", min(w[5] for w in worst),
          " head bottom max:", max(w[6] for w in worst))
