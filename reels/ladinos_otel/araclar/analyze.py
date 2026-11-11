"""Klip analizi: kare bazinda kamera hareketi (optik akis dx,dy,zoom), sarsinti, netlik, parlaklik + YuNet yuz kutulari.
Kullanim: python3 analyze.py <sdr_klasoru> <yunet.onnx> <cikis.json> [klip ...]"""
import sys, os, json, glob, cv2, numpy as np
sdr, model, outp = sys.argv[1:4]
clips = sys.argv[4:] or sorted(os.path.basename(p)[:-4] for p in glob.glob(os.path.join(sdr, "*.mov")))
res = json.load(open(outp)) if os.path.exists(outp) else {}
det = cv2.FaceDetectorYN.create(model, "", (540, 960), 0.6, 0.3, 50)
for c in clips:
    cap = cv2.VideoCapture(os.path.join(sdr, c + ".mov")); prev = None; fr = []
    while True:
        ok, im = cap.read()
        if not ok: break
        g = cv2.cvtColor(cv2.resize(im, (135, 240)), cv2.COLOR_BGR2GRAY)
        dx = dy = zm = 0.0
        if prev is not None:
            fl = cv2.calcOpticalFlowFarneback(prev, g, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            dx, dy = float(np.median(fl[..., 0])) * 8, float(np.median(fl[..., 1])) * 8  # 1080p piksel/kare
            ys, xs = np.mgrid[0:240, 0:135]; rx, ry = xs - 67, ys - 120
            zm = float(np.median((fl[..., 0] * rx + fl[..., 1] * ry) / (rx ** 2 + ry ** 2 + 1)))
        prev = g
        sm = cv2.resize(im, (540, 960)); _, f = det.detect(sm)
        faces = [[round(float(v) * 2, 1) for v in x[:4]] + [round(float(x[14]), 2)] for x in (f if f is not None else [])]
        sharp = float(cv2.Laplacian(cv2.cvtColor(sm, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var())
        fr.append([round(dx, 2), round(dy, 2), round(zm, 4), round(sharp, 1), round(float(g.mean()), 1), faces])
    res[c] = fr
    m = np.array([[x[0], x[1], x[3]] for x in fr])
    print(f"{c}: {len(fr)} kare  ort.dx {m[:,0].mean():6.1f} dy {m[:,1].mean():6.1f} netlik {np.median(m[:,2]):6.0f}  yuzlu kare {sum(1 for x in fr if x[5])}", flush=True)
json.dump(res, open(outp, "w"))
