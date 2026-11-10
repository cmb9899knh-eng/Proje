import cv2,json,glob,os
det=cv2.FaceDetectorYN.create("models/yunet.onnx","",(540,960),0.6,0.3,50)
out={}
for p in sorted(glob.glob("sdr/*.mp4")):
  n=os.path.basename(p)[:-4]; cap=cv2.VideoCapture(p); L=[]
  while True:
    ok,f=cap.read()
    if not ok: break
    s=cv2.resize(f,(540,960)); _,fa=det.detect(s)
    L.append([[float(v*2) for v in r[:4]]+[float(r[-1])] for r in fa] if fa is not None else [])
  out[n]=L; print(n,len(L),"frames, with face:",sum(1 for x in L if x), "max faces", max(len(x) for x in L))
json.dump(out,open("faces.json","w"))
