import sys,glob,wave,numpy as np,os
from faster_whisper import WhisperModel
m=WhisperModel(sys.argv[1],device="cpu",compute_type="int8",cpu_threads=4)
for p in sorted(glob.glob(sys.argv[2]+"/*.wav")):
  w=wave.open(p); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
  segs,_=m.transcribe(a,language="tr",word_timestamps=True,vad_filter=False,condition_on_previous_text=False)
  print("=====",os.path.basename(p),f"{len(a)/16000:.2f}s",flush=True)
  for s in segs:
    print(f"[{s.start:.2f}-{s.end:.2f}] {s.text}  (nospeech={s.no_speech_prob:.2f})")
    for x in s.words: print(f"   {x.start:.2f}-{x.end:.2f} {x.word} ({x.probability:.2f})")
  print(flush=True)
