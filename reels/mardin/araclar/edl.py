# Mardin tanitim reels - kurgu listesi (EDL)
# Kaynak adlari: A=IMG_2906 (minare), B=IMG_2907 (merdiven), D=IMG_2945 2. kayit (konusma + sokak),
# E=IMG_2946, F=IMG_2948; digerleri IMG numarasi (2954b = IMG_2954'un 2. kaydi).
# Alanlar: v/vi = goruntu kaynagi/giris; a/ai/ao = konusma sesi kaynagi/giris/cikis (yoksa ses yok, muzik);
# d = sure (konusmada ao-ai); snap = bitisi muzik vurusuna (0.5 sn) oturt; sec = bolum; pill = bas ustu not;
# fx = goruntu efektleri.
BEAT = 0.5
EDL = [
    # 1) KANCA
    dict(sec="hook",   v="3062", vi=1.10, d=1.5, fx=["flash", "zoomin"], zc=(420, 1000)),
    # 2a) arkadasin sunucu girisi: "Merhaba arkadaslar, sizlere Mardin sokaklarini tanitacagim."
    dict(sec="intro",  v="2944a", vi=0.90, a="2944a", ai=0.900, ao=5.300),
    # 2) "Simdi Mardin neyle meshur? Tabii ki bu guzel sokaklariyla."
    dict(sec="talk1",  v="2949", vi=0.30, a="2949", ai=0.30, ao=5.05),
    # 3) sokaklar montaji (muzik tam)
    dict(sec="streets", v="F",    vi=0.00, d=1.0, snap=True, fx=["punch", "whip"]),
    dict(sec="streets", v="3082", vi=4.30, d=1.5, fx=["punch", "whip"]),
    dict(sec="streets", v="E",    vi=1.00, d=1.0, fx=["punch", "whip"]),
    dict(sec="streets", v="A",    vi=2.00, d=1.5, fx=["punch", "whip", "zoomin"], pill=("ULU CAMİİ", "pin")),
    # 4) "E bir de Mardin'in neyi meshur?" / (merdiven goruntusu) "Tabii ki bu merdivenleri." / "Ay... cok yorucu."
    dict(sec="talk2",  v="2954", vi=0.30, a="2954", ai=0.300, ao=1.955),
    dict(sec="talk2",  v="B",    vi=2.60, a="2954", ai=3.250, ao=6.000, fx=["punch"]),
    dict(sec="talk2",  v="2954", vi=6.82, a="2954", ai=6.820, ao=7.450),
    dict(sec="talk2",  v="2954", vi=7.94, a="2954", ai=7.940, ao=8.660, fx=["facezoom"]),
    # 5) kediler
    dict(sec="cats",   v="2954b", vi=5.00, d=1.0, snap=True, fx=["punch"], pill=("SOKAKLARIN GERÇEK SAHİPLERİ", None)),
    dict(sec="cats",   v="3086", vi=2.60, d=1.0, fx=["punch"], pill=("SOKAKLARIN GERÇEK SAHİPLERİ", None)),
    dict(sec="cats",   v="3078", vi=0.50, d=1.0, fx=["punch"], pill=("SOKAKLARIN GERÇEK SAHİPLERİ", None)),
    # 5b) "Sola dogru donerseniz eger biraz yurudukten sonra Cafe Jin ve Leyli Restoran'la karsilasacaksiniz."
    #     ses kesintisiz; goruntu "Cafe Jin"de Coffee JIN tabelasina, "Leyli Restoran"da vitray cepheye gecer
    dict(sec="places", v="2944b", vi=0.00, a="2944b", ai=0.000, ao=2.950),   # kayit "S" sesinin icinde basliyor: 0.00dan al
    dict(sec="places", v="2944b", vi=7.00, a="2944b", ai=2.950, ao=3.950, fx=["punch"]),
    dict(sec="places", v="2944a", vi=4.40, a="2944b", ai=3.950, ao=6.220, fx=["punch"]),
    # 6) kitap kafe
    dict(sec="cafe",   v="2960", vi=1.40, d=2.5, snap=True, fx=["whip"], pill=("GİZLİ KAPI?!", None)),
    dict(sec="cafe",   v="2957", vi=0.80, d=1.0, fx=["punch"], pill=("KİTAP KAFE", "book")),
    dict(sec="cafe",   v="2975", vi=0.50, d=1.0, fx=["punch"], pill=("KİTAP KAFE", "book")),
    dict(sec="cafe",   v="2986", vi=1.00, d=1.0, fx=["punch"], pill=("KİTAP KAFE", "book")),
    dict(sec="cafe",   v="3038", vi=2.00, d=1.0, fx=["punch"]),
    dict(sec="cafe",   v="2980", vi=6.00, d=1.0, fx=["punch"]),
    dict(sec="cafe",   v="2973", vi=0.20, a="2973", ai=0.200, ao=2.760),   # "Karistir, gulumse."
    dict(sec="cafe",   v="2968", vi=0.20, d=0.9, snap=True, fx=["punch"]),
    # 7) aynalar
    dict(sec="mirror", v="3060", vi=2.60, d=1.5, fx=["whip"]),
    dict(sec="mirror", v="3082", vi=0.50, d=1.5, fx=["whip"], pill=("AYNALI SOKAK", "pin")),
    # 8) "Yolu gosterirsen daha guzel bir goruntu olur aslinda. Soyle gostereyim sizlere." + sokak acilisi
    dict(sec="reveal", v="D",    vi=2.105, a="D", ai=2.105, ao=9.000, fx=["revealflash"], pill=("ÇARŞIYA DOĞRU", "pin")),
    # 9) kapanis
    dict(sec="outro",  v="3088", vi=5.00, d=1.5, snap=True, fx=["punch"]),
    dict(sec="outro",  v="2944c", vi=5.95, a="2944c", ai=5.950, ao=6.800, d=1.0, snap=True, fx=["whip"]),   # "Bu kadar." + gulumseme
    dict(sec="outro",  v="A",    vi=6.00, d=1.5, fx=["flash2", "zoomin"]),       # minare -> "MARDIN" + kaydet
]
# konusma olmayan kisa sesleri bastir (kaynak zamani, -30 dB): nefes/hisirti ve arkadan kisik mirilti
MUTE = {"D": [(2.105, 2.152), (5.90, 6.36)]}
FPS = 30

def timeline():
    """[(t0, t1, entry)] dondurur; snap=True olan klipler bitisi vurusa denk gelecek sekilde uzar/kisalir."""
    t = 0.0; out = []
    for e in EDL:
        d = e["d"] if "d" in e else (e["ao"] - e["ai"])   # konusmali planda goruntu sesten uzun olabilir
        if e.get("snap"):
            end = round((t + d) / BEAT) * BEAT
            if end - t < 0.6 * d: end += BEAT
            d = end - t
        out.append((round(t, 4), round(t + d, 4), e)); t += d
    return out, round(t, 4)

if __name__ == "__main__":
    tl, T = timeline()
    for t0, t1, e in tl:
        print(f"{t0:6.3f}-{t1:6.3f} {e['sec']:8s} {e['v']:5s} {e['vi']:.2f}  {('ses ' + e['a'] + f' {e[chr(97)+chr(105)]:.3f}-{e[chr(97)+chr(111)]:.3f}') if 'a' in e else ''}")
    print("toplam", T)
