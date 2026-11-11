"""Ladinos Otel reel - kurgu karar listesi (EDL). Kaynak zamanlar SDR proxy (30 fps) saniyesi."""
FPS = 30
# (id, klip, giris, cikis, tur, zoom, ortam_kazanci_dB)
#  tur: "dialog" = mikrofondaki konusma tam seviye, "broll" = ortam sesi kisik, muzik ustte
SEGS = [
    ("s01", "IMG_3746", 0.40, 2.60, "broll", 1.00, -16),   # gece cephe / tabela
    ("s02", "IMG_3750", 1.40, 4.70, "broll", 1.00, -16),   # merdiven, iceri giris (arkadan)
    ("s03", "IMG_3754", 2.20, 4.70, "broll", 1.00, -16),   # cam kapidan kameraya yuruyus
    ("s04", "IMG_3755", 1.60, 4.80, "dialog", 1.00, 0),    # "Merhaba, kolay gelsin." ... "Hos bulduk."
    ("s05", "IMG_3756", 2.10, 2.37, "dialog", 1.00, 0),    # "Ben"
    ("s06", "IMG_3756", 2.60, 3.10, "dialog", 1.07, 0),    # "bir"  (0,30 sn duraksama atildi)
    ("s07", "IMG_3756", 3.70, 7.63, "dialog", 1.15, 0),    # "iki gun Midyat'ta kalacagim. Nasil bir oda oneriyorsunuz?" (0,65 sn duraksama atildi)
    ("s08", "IMG_3759", 0.50, 3.60, "broll", 1.00, -9),    # gorevli anlatiyor (uzak, anlasilmaz ses -> altyazi yok)
    ("s09", "IMG_3762", 0.00, 1.85, "broll", 1.00, -16),   # koridor ("tamam kisa kes bitti" oncesi kesildi)
    ("s10", "IMG_3763", 1.30, 3.30, "dialog", 1.00, 0),    # "Sans odasi" (dogrulanacak)
    ("s11", "IMG_3764", 0.60, 2.92, "dialog", 1.00, 0),    # kapi aciliyor "Tesekkurler."
    ("s12", "IMG_3765", 0.30, 2.30, "broll", 1.00, -16),   # oymali paravan
    ("s13", "IMG_3766", 0.30, 3.00, "broll", 1.00, -16),   # oda genel
    ("s14", "IMG_3767", 0.40, 2.90, "broll", 1.00, -16),   # yatak basi
    ("s15", "IMG_3771", 0.20, 2.00, "broll", 1.00, -16),   # avize
    ("s16", "IMG_3770", 0.30, 3.10, "broll", 1.00, -16),   # perde -> gece manzarasi
    ("s17", "IMG_3772", 1.50, 4.50, "broll", 1.00, -16),   # banyo kapisi aciliyor
    ("s18", "SPLIT",    0.00, 2.00, "broll", 1.00, -16),   # bolunmus ekran: dus (3774) / fon (3775)
    ("s19", "IMG_3787", 0.20, 3.20, "broll", 1.00, -16),   # diger oda
    ("s20", "IMG_3788", 2.10, 3.80, "broll", 1.00, -16),   # rolyef duvar
    ("s21", "IMG_3784", 2.15, 3.70, "broll", 1.00, -16),   # ayna selfie -> kapanis
]
SPLIT = (("IMG_3774", 0.60), ("IMG_3775", 0.20))   # (klip, giris) ust / alt
# Bu kliplerde insan yok; yuz dedektorunun buldugu kutular (rolyef, avize) yanlis pozitif -> yok sayilir
NO_PERSON = {"IMG_3746", "IMG_3765", "IMG_3766", "IMG_3767", "IMG_3771", "IMG_3770", "IMG_3772",
             "IMG_3774", "IMG_3775", "IMG_3787", "IMG_3788", "IMG_3762"}

def frames(seg):  # cikti kare sayisi
    return round((seg[3] - seg[2]) * FPS)

def timeline():
    """[(seg, out_start_frame, n_frames)]"""
    out, f = [], 0
    for s in SEGS:
        n = frames(s); out.append((s, f, n)); f += n
    return out

TOTAL = sum(frames(s) for s in SEGS)
