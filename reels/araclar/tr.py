import sys, wave, numpy as np
from faster_whisper import WhisperModel
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
m=WhisperModel(sys.argv[2] if len(sys.argv)>2 else "medium",device="cpu",compute_type="int8")
segs,_=m.transcribe(a,language="tr",word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
for s in segs:
  print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}")
  for x in s.words: print(f"   {x.start:.2f}-{x.end:.2f} {x.word} ({x.probability:.2f})")
