"""YuNet ile kare kare yuz tespiti; egik kamera icin kare -75..75 derece dondurulerek taranir.
Cikti: faces_<K>.json -> her kare icin [x0,y0,x1,y1,skor] listesi (1080x1920 cikis koordinatinda)."""
import sys, json, cv2, numpy as np
model, video, out = sys.argv[1], sys.argv[2], sys.argv[3]
SC = 0.5; W, H = int(1080 * SC), int(1920 * SC)
det = cv2.FaceDetectorYN.create(model, "", (W, H), 0.6, 0.3, 50)
cap = cv2.VideoCapture(video); res = []
while True:
    ok, fr = cap.read()
    if not ok: break
    sm = cv2.resize(fr, (W, H)); boxes = []
    for ang in (0, -30, 30, -60, 60, -80, 80):
        M = cv2.getRotationMatrix2D((W / 2, H / 2), ang, 1.0)
        cos, sin = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(H * sin + W * cos), int(H * cos + W * sin)
        M[0, 2] += nw / 2 - W / 2; M[1, 2] += nh / 2 - H / 2
        rot = cv2.warpAffine(sm, M, (nw, nh)); det.setInputSize((nw, nh))
        _, f = det.detect(rot)
        if f is None: continue
        Mi = cv2.invertAffineTransform(M)
        for r in f:
            x, y, w, h, s = r[0], r[1], r[2], r[3], r[14]
            pts = np.array([[x, y], [x + w, y], [x, y + h], [x + w, y + h]])
            p = (Mi[:, :2] @ pts.T).T + Mi[:, 2]
            b = [p[:, 0].min() / SC, p[:, 1].min() / SC, p[:, 0].max() / SC, p[:, 1].max() / SC, float(s)]
            if not any(abs(b[0] - c[0]) < 80 and abs(b[1] - c[1]) < 80 for c in boxes): boxes.append(b)
    res.append([[round(v, 1) for v in b] for b in boxes])
json.dump(res, open(out, "w")); n = sum(1 for r in res if r)
print(video, "kare:", len(res), "yuz bulunan kare:", n)
