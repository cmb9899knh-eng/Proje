import wave,numpy as np,sys
def L(n):
  try: w=wave.open(f"a48b/{n}.wav")
  except FileNotFoundError: w=wave.open(f"a48/{n}.wav")
  return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def db(x): return 20*np.log10(np.sqrt((x**2).mean())+1e-9)
for arg in sys.argv[1:]:
  n,t,r=arg.split(":"); t=float(t); r=float(r); a=L(n); sr=48000; h=int(.04*sr)
  best=None
  for k in np.arange(max(0,t-r),min(len(a)/sr-.04,t+r),0.01):
    v=db(a[int(k*sr):int(k*sr)+h])
    if best is None or v<best[1]: best=(k+0.02,v)
  prof=" ".join(f"{db(a[int(k*sr):int(k*sr)+480]):.0f}" for k in np.arange(max(0,t-r),min(len(a)/sr-.01,t+r),0.02))
  print(f"{n} hedef {t:.2f}±{r}: en sessiz {best[0]:.2f}s ({best[1]:.0f} dB) | {prof}")
