import cv2,json,os
from edl import EDL
det=cv2.FaceDetectorYN.create("models/yunet.onnx","",(540,960),0.6,0.3,50)
out=json.load(open("faces.json"))
need=sorted({e[0] for e in EDL if e[0]!="FOTO"} | {e[3].split(":")[1] for e in EDL if e[3].startswith("split")})
for n in need:
  if n in out: continue
  cap=cv2.VideoCapture(f"sdr/{n}.mp4"); L=[]
  while True:
    ok,f=cap.read()
    if not ok: break
    _,fa=det.detect(cv2.resize(f,(540,960)))
    L.append([[float(v*2) for v in r[:4]]+[float(r[-1])] for r in fa] if fa is not None else [])
  out[n]=L; print(n,len(L),sum(1 for x in L if x),flush=True)
json.dump(out,open("faces.json","w"))
print("FACES_DONE")
