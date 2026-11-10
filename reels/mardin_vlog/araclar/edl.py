# Kurgu listesi: (klip, kaynak_bas, kaynak_son, tur, not)   tur: "konusma" | "ara" | "split:<ikinci klip>"
EDL=[
 ("3148",3.30,5.80,"ara","Mardin manzarası (açılış)"),
 ("3160",1.00,4.50,"konusma","Evet şimdi … Cafe'nin girişindeyiz"),
 ("3160",6.02,7.80,"konusma","Bakalım nasıl bir yer çıkacak"),
 ("3166",2.00,3.60,"ara","Barista kahveyi döküyor"),
 ("3170",0.20,1.70,"ara","Kafeye yürüyüş"),
 ("3178",0.10,1.40,"ara","İki içecek"),
 ("3161",0.30,1.50,"ara","Arkadaş cam önünde"),
 ("3191",3.00,4.60,"ara","Arkadaşla selfie"),
 ("3234",0.50,2.50,"ara","Kahve yudumu"),
 ("3287",0.20,2.00,"ara","Mardin Hatırası aynası"),
 ("3288",0.20,1.90,"split:3292","Tespihler | Şallar (bölünmüş ekran)"),
 ("3289",0.50,1.90,"ara","Asılı puşiler, çarşı"),
 ("3291",0.30,2.30,"ara","Minare"),
 ("3295",0.10,4.66,"konusma","Şu an sanırım çarşıda geziyoruz / (arkadaş) Evet meydandayız arkadaşlar"),
 ("3295",5.36,6.82,"konusma","Çok güzel yerler var"),
 ("3296",0.40,1.36,"konusma","Şu anda"),
 ("3296",2.20,4.24,"konusma","meydanın ilerisindeyiz"),
 ("3297",1.10,3.90,"konusma","Mardin'in meşhur badem şekerleri"),
 ("3297",4.72,7.30,"konusma","Nereden geçerseniz ikram ediliyor"),
]
FPS=30
def timeline():
    t=0; out=[]
    for e in EDL:
        n0=round(e[1]*FPS); n1=round(e[2]*FPS); d=(n1-n0)/FPS
        out.append(dict(clip=e[0],s=n0/FPS,e=n1/FPS,kind=e[3],note=e[4],t0=t,t1=t+d)); t+=d
    return out
if __name__=="__main__":
    for x in timeline(): print(f"{x['t0']:6.2f}-{x['t1']:6.2f}  {x['clip']} {x['s']:.2f}-{x['e']:.2f} {x['kind']:12s} {x['note']}")
    print("toplam", timeline()[-1]['t1'])
