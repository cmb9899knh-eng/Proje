# Kesim kontrol araci: (1) kesim noktasinin hemen iki yaninda (10 ms) seviye -> kesik hece yok mu
# (2) yeniden transkripsiyon: beklenen metinle tam eslesme, ardisik tekrar yok, dusuk guvenli kelime raporu
# Kullanim: python3 cutcheck.py voice_speech.wav "5.210,8.452" "beklenen metin" [izinli,ikileme]
import sys, wave, re, numpy as np
from faster_whisper import WhisperModel
path=sys.argv[1]; cuts=[float(x) for x in sys.argv[2].split(",") if x]; expected=sys.argv[3]
allow=set(sys.argv[4].split(",")) if len(sys.argv)>4 and sys.argv[4] else set()
allow_ng=set(sys.argv[5].split(",")) if len(sys.argv)>5 and sys.argv[5] else set()
# tabelayla dogrulanmis ozel isimler ve Whisper yazim varyantlari: "cafejin:cafe jean|cafe jin"
proper=set(); alias={}
for item in (sys.argv[6].lower().split(",") if len(sys.argv)>6 else []):
    name,_,vs=item.partition(":"); proper.add(name)
    for v in [x for x in vs.split("|") if x]: alias[v]=name; proper.update(v.split())  # bilincli paralel ifadeler (or. "tabii ki bu")
w=wave.open(path); sr=w.getframerate(); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def db(s): return 20*np.log10(np.sqrt((s**2).mean())+1e-9)
ok=True; win=int(.010*sr)
print("== 1) Kesim noktalari (kesimin hemen iki yaninda 10 ms; kesik hece yoksa < -40 dB)")
for c in cuts:
    i=int(round(c*sr)); l=db(a[i-win:i]); r=db(a[i:i+win]); bad=l>-40 or r>-40; ok&=not bad
    print(f"  {c:.3f}s  once {l:6.1f} dB | sonra {r:6.1f} dB  -> {'SORUN' if bad else 'temiz'}")
print("== 1b) Bas/son kenar")
for n,s in (("bas",a[:win]),("son",a[-win:])):
    l=db(s); bad=l>-40; ok&=not bad; print(f"  {n}: {l:6.1f} dB -> {'SORUN' if bad else 'temiz'}")
print("== 2) Yeniden transkripsiyon (large-v3)")
m=WhisperModel("large-v3",device="cpu",compute_type="int8")
LEAD=0.5  # transkripsiyonda basa 0.5 sn sessizlik (videoda konusmadan once baska ses var; Whisper'a baglam)
ap=np.concatenate([np.zeros(int(LEAD*sr),np.float32),a])
a16=np.interp(np.arange(0,len(ap),sr/16000),np.arange(len(ap)),ap).astype(np.float32)
segs,_=m.transcribe(a16,language="tr",word_timestamps=True,condition_on_previous_text=False,beam_size=5)
words=[]
for s_ in segs:
    for x in s_.words:
        wd=x.word.strip()
        if words and wd[:1] in "'’":   # ek (Mardin'in) onceki kelimeye bitisik
            p0=words[-1]; words[-1]=(p0[0],x.end-LEAD,p0[2]+wd,min(p0[3],x.probability))
        else: words.append((x.start-LEAD,x.end-LEAD,wd,x.probability))
for x in words: print(f"  {x[0]:5.2f}-{x[1]:5.2f} {x[2]:14s} p={x[3]:.2f}")
norm=lambda t:[re.sub(r"[^\wçğıöşü]","",x.replace("İ","i").replace("I","ı").lower()) for x in t]
got=[x for x in norm([w[2] for w in words]) if x]; exp=[x for x in norm(expected.split()) if x]
g=" "+" ".join(got)+" "
for v,name in alias.items(): g=g.replace(" "+v+" "," "+name+" ")
got=g.split()
print("  beklenen:"," ".join(exp)); print("  bulunan :"," ".join(got))
rep=[got[i] for i in range(1,len(got)) if got[i]==got[i-1] and got[i] not in allow]
print("  ardisik tekrar:",rep or "yok"); ok&=not rep
# ayni cumlenin iki kez gecmesi (3+ kelimelik n-gram tekrari)
ng=[" ".join(got[i:i+3]) for i in range(len(got)-2)]; dup=sorted({g for g in ng if ng.count(g)>1 and g not in allow_ng})
if allow_ng: print("  izinli paralel ifade:",sorted(allow_ng))
print("  tekrar eden ifade (3 kelime):",dup or "yok"); ok&=not dup
low=[w[2] for w in words if w[3]<0.5 and re.sub(r"[^\wçğıöşü]","",w[2].lower()) not in proper]
print("  dusuk guvenli kelime (<0.5):",low or "yok", ("| ozel isim istisnasi: "+",".join(sorted(proper))) if proper else ""); ok&=not low
match=got==exp; ok&=match; print("  metin eslesmesi:","TAM" if match else "FARKLI")
print("SONUC:","GECTI" if ok else "KALDI")
