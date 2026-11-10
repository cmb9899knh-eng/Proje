import json,wave,numpy as np
from edl import timeline
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
out=[]
for x in timeline():
    if x["kind"]!="konusma": continue
    w=wave.open(f"wav/{x['clip']}.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    seg=a[round(x["s"]*16000):round(x["e"]*16000)]
    z=np.zeros(8000,np.float32)
    r=m.transcribe(np.concatenate([z,seg,z]),language="tr",word_timestamps=True,condition_on_previous_text=False,beam_size=5)[0]
    toks=[]
    for s in r:
        for ww in s.words:
            t=ww.word.strip()
            if t.startswith("'") and toks: toks[-1][2]+=t; toks[-1][1]=ww.end; continue
            toks.append([ww.start,ww.end,t])
    # enerji: bolumun ilk kelimesinin gercek baslangicini bul, Whisper kaymasini tum kelimelere uygula
    h=160; env=np.array([20*np.log10(np.sqrt((seg[i:i+h]**2).mean())+1e-9) for i in range(0,len(seg)-h,h)])
    first=next((i*0.01 for i in range(len(env)) if env[i]>-38),0.0)
    delta=first-(toks[0][0]-0.5)
    prev=-1
    for st,en,t in toks:
        on=max(st-0.5+delta,prev+0.12,0); prev=on
        out.append(dict(t=round(x["t0"]+on,3),end=round(x["t0"]+max(en-0.5+delta,on+0.1),3),w=t,clip=x["clip"]))
json.dump(out,open("words.json","w"),ensure_ascii=False,indent=0)
for o in out: print(f"{o['t']:6.2f}-{o['end']:6.2f} {o['w']}")
