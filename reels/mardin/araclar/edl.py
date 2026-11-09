# Kurgu listesi (kaynak harfleri: A=IMG_2906 minare, B=IMG_2907 merdiven, C=IMG_2945(1) konusma,
# D=IMG_2945(2) konusma+sokak, E=IMG_2946 sokak, F=IMG_2948 sokak)
# (kaynak, giris, cikis, ses_kullan)
EDL = [
    ("A", 1.50, 5.50, False),   # minare - kanca (arka plandaki telefon konusmasi kapatildi)
    ("B", 2.60, 5.10, False),   # merdivenler
    ("F", 4.70, 6.70, False),   # isikli konak cephesi
    ("C", 0.930, 6.140, True),  # "Evet simdi meydanin ust sokagindan ... Nereye gidiyoruz?"
    ("C", 6.380, 9.622, True),  # "Birazcik carsinin ortasina dogru gidecegiz."
    ("D", 2.105, 9.500, True),  # "Yolu gosterirsen ... Soyle gostereyim sizlere." + sokak acilisi
    ("E", 1.00, 4.00, False),   # aydinlatilmis dar sokak
    ("F", 0.00, 3.20, False),   # fenerli sokak - kapanis
]
# Konusma olmayan kisa sesleri bastir (kaynak zamani, -30 dB): nefes/hisirti ve arkadan kisik mirilti
MUTE = {"D": [(2.105, 2.152), (5.90, 6.36)]}
FPS = 30
def timeline():
    t = 0; out = []
    for s, a, b, v in EDL:
        out.append((t, t + (b - a), s, a, b, v)); t += b - a
    return out, t
if __name__ == "__main__":
    tl, T = timeline()
    for r in tl: print(f"{r[0]:6.3f}-{r[1]:6.3f}  {r[2]} {r[3]:.3f}-{r[4]:.3f} {'ses' if r[5] else '-'}")
    print("toplam", round(T, 3))
