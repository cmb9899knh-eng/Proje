import wave,numpy as np,sys,json
d=json.load(open("tr2.json"))
def L(n):
  w=wave.open(f"a48b/{n}.wav"); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
for n in sys.argv[1:]:
  a=L(n); h=480; e=np.array([20*np.log10(np.sqrt((a[i:i+h]**2).mean())+1e-9) for i in range(0,len(a)-h,h)])
  floor=np.percentile(e,10); thr=max(-42,floor+12)
  on=e>thr; isl=[]; i=0
  while i<len(on):
    if on[i]:
      j=i
      while j<len(on) and on[j]: j+=1
      isl.append([i*0.01,j*0.01]); i=j
    else: i+=1
  m=[]
  for s,t in isl:
    if m and s-m[-1][1]<0.12: m[-1][1]=t
    else: m.append([s,t])
  m=[x for x in m if x[1]-x[0]>0.06]
  print(f"== {n} dur {len(a)/48000:.2f} taban {floor:.0f} esik {thr:.0f}")
  print("   adaciklar:", " ".join(f"{s:.2f}-{t:.2f}" for s,t in m))
  print("   kelimeler:", " ".join(f"{w[2].strip()}@{w[0]:.2f}" for s in d.get(n,[]) for w in s["words"]))
