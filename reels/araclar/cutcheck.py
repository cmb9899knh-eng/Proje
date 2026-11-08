# Kesim kontrol araci: (1) kesim noktalarinda sessizlik/kesik hece kontrolu, (2) yeniden transkripsiyon + tekrar kontrolu
import sys, wave, re, numpy as np
from faster_whisper import WhisperModel
path=sys.argv[1]; cuts=[float(x) for x in sys.argv[2].split(",")]; expected=sys.argv[3]
w=wave.open(path); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def db(seg): return 20*np.log10(np.sqrt((seg**2).mean())+1e-9)
ok=True
print("== 1) Kesim noktalari (±40 ms pencerede seviye; kesik hece yoksa < -45 dB olmali)")
for c in cuts:
    i=int(c*sr); l=db(a[max(0,i-int(.04*sr)):i]); r=db(a[i:i+int(.04*sr)])
    bad = l>-45 or r>-45; ok&=not bad
    print(f"  {c:.3f}s  once {l:6.1f} dB | sonra {r:6.1f} dB  -> {'SORUN' if bad else 'temiz'}")
print("== 1b) Bastaki/sondaki kenarlar")
for name,seg in (("bas",a[:int(.04*sr)]),("son",a[-int(.04*sr):])):
    l=db(seg); bad=l>-45; ok&=not bad; print(f"  {name}: {l:6.1f} dB -> {'SORUN' if bad else 'temiz'}")
print("== 2) Yeniden transkripsiyon")
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
a16=a if sr==16000 else np.interp(np.arange(0,len(a),sr/16000),np.arange(len(a)),a).astype(np.float32)
segs,_=m.transcribe(a16,language="tr",word_timestamps=True,condition_on_previous_text=False)
words=[]
for s in segs:
    for x in s.words: words.append((x.start,x.end,x.word.strip(),x.probability)); print(f"  {x.start:5.2f}-{x.end:5.2f} {x.word.strip():10s} p={x.probability:.2f}")
norm=lambda t:[re.sub(r"[^\wçğıöşü]","",x.lower().replace("İ","i").replace("I","ı")) for x in t]
got=[x for x in norm([w[2] for w in words]) if x]
num={"1":"bir","2":"iki","3":"üç"}; got=[num.get(x,x) for x in got]
exp=[x for x in norm(expected.split()) if x]
print("  beklenen:",exp); print("  bulunan :",got)
rep=[got[i] for i in range(1,len(got)) if got[i]==got[i-1]]
print("  ardisik tekrar:", rep or "yok"); ok&= not rep
low=[w for w in words if w[3]<0.5]; print("  dusuk guvenli kelime:", [w[2] for w in low] or "yok")
match = got==exp; ok&=match; print("  metin eslesmesi:", "TAM" if match else "FARKLI")
print("SONUC:", "GECTI" if ok else "KALDI")
