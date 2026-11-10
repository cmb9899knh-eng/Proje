"""Kesim kontrol araci (cok klipli kurgu).
1) Her konusma segmentinin kaynak kenarlarinda (segmentin ICINDEKI ilk/son 40 ms) seviye: < -45 dB olmali (kesik hece yok)
2) Konusma segmentleri birlestirilip Whisper large-v3 ile yeniden yaziya dokulur:
   ardisik kelime/ifade tekrari, dusuk guvenli kelime, beklenen metinle eslesme kontrol edilir.
Kullanim: python3 cutcheck2.py <a48_dir> <out_wav>
"""
import sys, wave, re, numpy as np
sys.path.insert(0,".")
from edl import timeline, clip_audio, aud_src
A=sys.argv[1]; OUT=sys.argv[2]; SR=48000
EXPECTED=("mardin bir efsane bugün antik kentteyiz vol iki diyelim dün mardin sokaklarını gece gördük gezdik "
 "şimdi bir sürü kafe var derken zincir kafelerin çoğu açıldı burada "
 "aynı zamanda yemek yeme yerleri de var fotoğraf çekme yerleri de var şimdi gülbahar bunları bir görsün hangisinde oturmak istiyorsa orada oturalım "
 "evet şimdi nevada kafenin girişindeyiz bakalım nasıl bir yer çıkacak "
 "evet şimdi de espresso labdeyiz gülbahara kafeleri gösteriyorum şimdi biz çıktık kafeden kahvelerimiz elimizde aynalar bizi karşılıyor "
 "evet şu anda meydana doğru ilerliyoruz şu an sanırım çarşıda geziyoruz evet meydandayız arkadaşlar çok güzel yerler var "
 "mardinin meşhur badem şekerleri nereden geçerseniz ikram ediliyor bu yolda yürüyün aç olun doyuyorsunuz yol bitmeden "
 "aynı zamanda mardinde süryani şarabı meşhur işte size bahsettiğim yerler buralar mezopotamya dicle "
 "şimdi gülbaharı mardinde en çok fotoğraf çekmek için ziyaret edilen yere getirdim çok güzel").split()
def load(n):
    w=wave.open(clip_audio(n)); return np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
db=lambda s:20*np.log10(np.sqrt((s**2).mean())+1e-9)
ok=True; parts=[]; joins=[]; t=0
print("== 1) Konusma segmenti kenarlari (kaynakta, segment icindeki 40 ms)")
for x in timeline():
    if x["kind"]!="konusma": continue
    ac,as_=aud_src(x); a=load(ac); i0=round(as_*SR); i1=i0+round((x["e"]-x["s"])*SR); w=int(.04*SR)
    l=db(a[i0:i0+w]); r=db(a[i1-w:i1]); bad=l>-45 or r>-45; ok&=not bad
    print(f"  {ac} {as_:.3f}-{as_+x['e']-x['s']:.3f}  bas {l:6.1f} dB | son {r:6.1f} dB -> {'SORUN' if bad else 'temiz'}   ({x['note']})")
    seg=a[i0:i1].copy(); f=int(.01*SR); seg[:f]*=np.linspace(0,1,f); seg[-f:]*=np.linspace(1,0,f)
    parts.append(seg); parts.append(np.zeros(int(.25*SR),np.float32))
v=np.concatenate(parts); wo=wave.open(OUT,"wb"); wo.setnchannels(1); wo.setsampwidth(2); wo.setframerate(SR)
wo.writeframes((np.clip(v,-1,1)*32767).astype(np.int16).tobytes()); wo.close()
print("== 2) Yeniden transkripsiyon (birlesik konusma izi)")
from faster_whisper import WhisperModel
m=WhisperModel("large-v3",device="cpu",compute_type="int8",cpu_threads=4)
v16=v[::3]
segs,_=m.transcribe(v16,language="tr",word_timestamps=True,condition_on_previous_text=False,beam_size=5)
words=[(x.start,x.end,x.word.strip(),x.probability) for s in segs for x in s.words]
for w_ in words: print(f"  {w_[0]:6.2f}-{w_[1]:6.2f} {w_[2]:16s} p={w_[3]:.2f}")
def norm(t):
    t=t.replace("İ","i").replace("I","ı").lower().replace("'","").replace("’","")
    return re.sub(r"[^\wçğıöşü]","",t)
toks=[]
for w_ in words:  # kesme isaretiyle baslayan ekleri onceki kelimeye bagla (Mardin + 'in -> mardinin)
    if w_[2].startswith(("'","’")) and toks: toks[-1]+=w_[2]
    else: toks.append(w_[2])
VAR={"cafenin":"kafenin","2":"iki","kenteyiz":"kentteyiz","labdeyiz":"labdeyiz","mevazanın":"nevadanın"}
got=[VAR.get(norm(t),norm(t)) for t in toks if norm(t)]
print("  beklenen:"," ".join(EXPECTED)); print("  bulunan :"," ".join(got))
rep=[got[i] for i in range(1,len(got)) if got[i]==got[i-1]]
# ifade tekrari (2-4 kelimelik ardisik blok)
for L in (2,3,4):
    for i in range(len(got)-2*L+1):
        if got[i:i+L]==got[i+L:i+2*L]: rep.append(" ".join(got[i:i+L]))
print("  ardisik tekrar:", rep or "yok"); ok&=not rep
# beklenenle hizalama (* = ozel isim, herhangi 1-2 kelime)
import difflib
exp=[e for e in EXPECTED if e!="*"]
g2=[g for g in got]
sm=difflib.SequenceMatcher(a=exp,b=g2)
diff=[(op,exp[i1:i2],g2[j1:j2]) for op,i1,i2,j1,j2 in sm.get_opcodes() if op!="equal"]
print("  farklar (ozel isim disinda olmamali):", diff or "yok")
nameonly=False  # v2: joker yok, metin bire bir eslesmeli
ok&=(not diff) or nameonly
low=[(w_[2],round(w_[3],2)) for w_ in words if w_[3]<0.5]; print("  dusuk guvenli kelime (<0.50):", low or "yok")
print("SONUC:", "GECTI" if ok else "KALDI")
