# Kurgu listesi v2 (tum klipler). Satir: (klip, kaynak_bas, kaynak_son, tur, not, secenekler)
#   tur: "konusma" | "ara" | "split:<ikinci klip>" | "foto"
#   secenekler: amb = ara goruntu ortam sesi (dB, None = sessiz: icinde baska konusma var)
#               tr  = bu segmente GIRIS gecisi: "cut" | "punch" (jump-cut'i gizleyen %6 zoom) | "whip" | "dissolve" | "flash"
#               kb  = Ken Burns yakinlasma (manzara)
#               sec = bolum basligi (rozet)
import os
FPS = 30
P = {}  # kisaltma
def S(c, s, e, k, note, **o): return (c, s, e, k, note, o)
EDL = [
 # ---------------- A. ACILIS (kanca) ----------------
 S("3309_790d", 1.80, 4.73, "konusma", "Mardin bir efsane.", tr="cut", kb=1.07, aud=("3308_699e", 4.72)),
 S("3294_ffe9", 2.30, 4.70, "ara", "Kale ve şehir manzarası", amb=None, tr="dissolve", kb=1.08),
 S("3148",      3.30, 5.30, "ara", "Mardin panoraması", amb=-14, tr="dissolve", kb=1.06),
 # ---------------- B. ANTIK KENT ----------------
 S("3151_6953", 0.74, 4.17, "konusma", "Bugün Antik Kent'teyiz. Vol 2 diyelim.", tr="whip", sec="ANTİK KENT"),
 S("3151_6953", 4.58, 7.08, "konusma", "Dün Mardin sokaklarını gece gördük,", tr="cut"),
 S("3151_6953", 7.49, 9.10, "konusma", "gezdik.", tr="cut"),
 S("3159_adfb", 0.28, 2.70, "ara", "Kemerden giriş", amb=None, tr="cut"),
 S("3152_f5e4", 2.97, 7.60, "konusma", "Şimdi bir sürü kafe var derken zincir kafelerin çoğu açıldı burada.", tr="cut"),
 S("3150_ddcd", 2.54, 5.79, "konusma", "Aynı zamanda yemek yeme yerleri de var,", tr="cut"),
 S("3150_ddcd", 6.45, 7.967, "konusma", "fotoğraf çekme yerleri de var.", tr="punch"),
 S("3152_f22a", 0.60, 5.77, "konusma", "Şimdi Gülbahar bunları bir görsün. Hangisinde oturmak istiyorsa orada oturalım.", tr="cut"),
 S("3159_ca2e", 4.00, 6.00, "ara", "Kafelerin önünden yürüyüş", amb=-14, tr="cut"),
 # ---------------- C. KAFELER ----------------
 S("3160", 1.00, 4.50, "konusma", "Evet şimdi Nevada Cafe'nin girişindeyiz.", tr="whip", sec="KAFE DURAĞI"),
 S("3160", 6.03, 7.80, "konusma", "Bakalım nasıl bir yer çıkacak.", tr="cut"),
 S("3161", 0.30, 1.50, "ara", "Camdan manzara", amb=-14, tr="cut"),
 S("3162_6a6b", 5.40, 7.60, "ara", "Merdivenlerden iniş", amb=None, tr="cut"),
 S("3163_edd4", 0.76, 3.62, "konusma", "Evet, şimdi de Espresso Lab'deyiz.", tr="cut"),
 S("3163_edd4", 4.00, 6.54, "konusma", "Gülbahar'a kafeleri gösteriyorum.", tr="cut"),
 S("3165_a5bb", 1.00, 2.20, "ara", "Portafiltre", amb=-12, tr="flash"),
 S("3167_385d", 0.00, 1.30, "ara", "Espresso akıyor", amb=-12, tr="cut"),
 S("3168_21df", 0.60, 2.40, "ara", "Latte art", amb=-12, tr="cut"),
 S("3166",      2.20, 3.40, "ara", "Buzlu kahve", amb=-12, tr="cut"),
 S("3178",      0.10, 1.20, "ara", "İki içecek", amb=-12, tr="cut"),
 S("3170",      0.20, 1.40, "ara", "Kafede yürüyüş", amb=-12, tr="cut"),
 S("3191",      3.00, 4.40, "ara", "Selfie", amb=None, tr="cut"),
 S("3234",      0.60, 2.20, "ara", "Kahve yudumu", amb=-12, tr="cut"),
 # ---------------- D. CARSI & MEYDAN ----------------
 S("3286_7f55", 0.44, 2.06, "konusma", "Şimdi biz", tr="whip", sec="ÇARŞI"),
 S("3286_7f55", 3.02, 5.76, "konusma", "çıktık kafeden. Kahvelerimiz elimizde.", tr="cut"),
 S("3286_2b7d", 0.40, 2.933, "konusma", "Aynalar bizi karşılıyor.", tr="cut"),
 S("3287",      0.20, 1.80, "ara", "Mardin Hatırası aynası", amb=-14, tr="cut"),
 S("3286_ddcc", 4.99, 7.13, "konusma", "Evet, şu anda meydana doğru", tr="cut"),
 S("3286_ddcc", 7.40, 8.60, "konusma", "ilerliyoruz.", tr="punch"),
 S("3288",      0.20, 1.90, "split:3292", "Tespih | Şal (bölünmüş ekran)", amb=-14, tr="cut"),
 S("3289",      0.50, 1.80, "ara", "Puşiler", amb=-14, tr="cut"),
 S("3291",      0.30, 2.30, "ara", "Minare", amb=-14, tr="dissolve", kb=1.06),
 S("3295",      0.10, 4.67, "konusma", "Şu an sanırım çarşıda geziyoruz. Evet, meydandayız arkadaşlar.", tr="whip"),
 S("3295",      5.37, 6.83, "konusma", "Çok güzel yerler var.", tr="cut"),
 S("3296",      4.25, 5.85, "ara", "Meydan sokağı", amb=-14, tr="cut", kb=1.05, sec="MEYDAN"),
 S("3297",      1.10, 3.90, "konusma", "Mardin'in meşhur badem şekerleri.", tr="cut", sec="BADEM ŞEKERİ"),
 S("3297",      4.73, 7.30, "konusma", "Nereden geçerseniz ikram ediliyor.", tr="cut"),
 S("3298_c3fc", 5.40, 7.90, "ara", "Tadımlık ikramlar", amb=None, tr="cut"),
 S("3299_9f0d", 2.17, 4.51, "konusma", "Bu yolda yürüyün,", tr="cut"),
 S("3299_9f0d", 4.81, 8.44, "konusma", "aç olun, doyuyorsunuz yol bitmeden.", tr="punch"),
 S("3302_177a", 0.07, 4.69, "konusma", "Aynı zamanda Mardin'de Süryani şarabı meşhur.", tr="cut"),
 S("3301_1f5b", 6.30, 8.00, "ara", "Hakiki Süryani Çöreği tabelası", amb=None, tr="cut"),
 S("3301_852a", 6.50, 8.30, "ara", "Gümüş vitrini", amb=None, tr="cut"),
 # ---------------- E. MEZOPOTAMYA & FINAL ----------------
 S("3308_6bd7", 0.20, 4.03, "konusma", "İşte size bahsettiğim yerler, buralar.", tr="whip", sec="MEZOPOTAMYA"),
 S("3308_6bd7", 4.49, 6.92, "konusma", "Mezopotamya, Dicle.", tr="cut", kb=1.04),
 S("3309_8598", 0.33, 6.47, "konusma", "Şimdi Gülbahar'ı Mardin'de en çok fotoğraf çekmek için ziyaret edilen yere getirdim.", tr="cut"),
 S("FOTO",      0.00, 4.00, "foto", "Senin fotoğrafların (deklanşör + polaroid)", tr="flash", sec="FOTOĞRAF MOLASI"),
 S("3309_790d", 4.73, 7.20, "ara", "Ova → kubbeler", amb=-14, tr="dissolve", kb=1.06),
 S("3308_699e", 0.45, 2.04, "konusma", "Çok güzel.", tr="dissolve", kb=1.05),
 S("3359_9eae", 1.00, 4.20, "ara", "Yol (kapanış)", amb=-16, tr="dissolve"),
]

def clip_video(c): return f"sdr/{c}.mp4"
def aud_src(x):
    """Segmentin ses kaynagi: (klip, kaynak_bas). 'aud' verilmisse goruntuden farkli klipten dis ses."""
    if x.get("aud"): return x["aud"][0], x["aud"][1]
    return x["clip"], x["s"]
def clip_audio(c): return f"a48/{c}.wav" if os.path.exists(f"a48/{c}.wav") else f"a48b/{c}.wav"

def timeline():
    t = 0; out = []
    for c, s, e, k, note, o in EDL:
        n0 = round(s * FPS); n1 = round(e * FPS); d = (n1 - n0) / FPS
        out.append(dict(clip=c, s=n0 / FPS, e=n1 / FPS, kind=k, note=note, t0=t, t1=t + d, **o)); t += d
    return out

if __name__ == "__main__":
    for x in timeline():
        print(f"{x['t0']:6.2f}-{x['t1']:6.2f}  {x['clip']:10s} {x['s']:5.2f}-{x['e']:5.2f} {x['kind']:10s} {x.get('tr',''):8s} {x.get('sec','') or '':16s} {x['note']}")
    print("toplam", round(timeline()[-1]['t1'], 2))
