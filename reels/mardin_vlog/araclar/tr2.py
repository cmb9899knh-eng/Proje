import glob,wave,numpy as np,os,json
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=3)
out={}
for p in sorted(glob.glob("wav2/*.wav")):
  w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
  segs,_=m.transcribe(a,language="tr",word_timestamps=True,vad_filter=True,vad_parameters=dict(min_silence_duration_ms=300),condition_on_previous_text=False,beam_size=5)
  n=os.path.basename(p)[:-4]; L=[]
  print("=====",n,f"{len(a)/16000:.2f}s",flush=True)
  for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}  (ns={s.no_speech_prob:.2f} lp={s.avg_logprob:.2f})",flush=True)
    L.append(dict(s=s.start,e=s.end,text=s.text,ns=s.no_speech_prob,lp=s.avg_logprob,words=[(x.start,x.end,x.word,x.probability) for x in s.words]))
  out[n]=L
json.dump(out,open("tr2.json","w"),ensure_ascii=False)
