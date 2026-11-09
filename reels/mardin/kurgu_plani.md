# Mardin Gece Yürüyüşü – Reels kurgu planı (ONAY BEKLİYOR)

Çıkış: 1080×1920, 30 fps, **30,5 sn**, HDR (HLG) → SDR ton eşleme, ses −14 LUFS / ≤ −1,5 dBTP

Kaynak harfleri: A = IMG_2906 (minare) · B = IMG_2907 (merdiven) · C = IMG_2945 (1. kayıt, konuşma) ·
D = IMG_2945 (2. kayıt, konuşma + sokak) · E = IMG_2946 (sokak) · F = IMG_2948 (sokak)

## 1. Kesim kararları
| Kaynak | Karar | Neden |
|---|---|---|
| A 0–1,5 / 5,5–16 | ✂️ | Minarenin en sabit 4 sn'si alındı |
| A sesi | 🔇 | Arka planda telefon konuşması var ("Selam, ona da selamlar… Dinliyorum aşkım"): kapatıldı, yerine müzik |
| B 2,6–5,1 | ✅ | Merdivenden inen kişi; görüntü karanlıktı, aydınlatıldı |
| C 0–0,93 | ✂️ | Kamera dönüşü ve sessizlik |
| C 0,93–6,14 | ✅ | "Evet şimdi meydanın üst sokağından yürümeye devam ediyoruz. Nereye gidiyoruz?" |
| C 6,14–6,38 | ✂️ | 0,7 sn'lik boşluğun 0,24 sn'si kısaltıldı (doğal nefes payı kaldı) |
| C 6,38–9,622 | ✅ | "Birazcık çarşının ortasına doğru gideceğiz." ("z" sesi 9,61'de bitiyor, kesim 9,622'de) |
| C 9,63–10,04 | ✂️ | Bir sonraki kelimenin başı (yarım) |
| D 0–2,105 | ✂️ | "…laklar ve kafeler bizi bekliyor olacak": **ilk kelime kayıt başında kesik** (kesik hece kuralı gereği atıldı) |
| D 2,105–9,50 | ✅ | "Yolu gösterirsen daha güzel bir görüntü olur aslında. Şöyle göstereyim sizlere." + kamera dönüşüyle sokağın açılışı |
| D 2,105–2,152 ve 5,90–6,36 | 🔉 −30 dB | Konuşma değil: nefes/hışırtı ve arkadan çok kısık bir mırıltı ("evet"e benziyor). Görüntü akışı bozulmasın diye kesilmedi, sesi kısıldı |
| E 1–4, F 4,7–6,7 ve 0–3,2 | ✅ | Işıklı taş sokaklar (manzara) |

Hız değişikliği **yok**. Ses kesimlerinde 8 ms yumuşak geçiş (tık sesi olmasın).

## 2. Kesim kontrolü (`araclar/cutcheck.py`): GEÇTİ
- Kesim 5,210 sn: önce −63,9 dB / sonra −68,1 dB → temiz
- Kesim 8,452 sn: önce −42,8 dB / sonra −86,0 dB → temiz
- Baş −62,8 dB, son −63,8 dB → temiz
- Whisper large-v3 ile yeniden transkripsiyon, beklenen metinle **TAM** eşleşme
- Ardışık tekrar yok, tekrar eden ifade yok, düşük güvenli kelime yok
- İlk denemede kontrol **KALDI**: Whisper kesim ardında "Çok" (p=0,08) ve D içinde "Evet" (p=0,32) duydu. Nedenler nefes ve arka plan mırıltısıydı; sesleri kısıldı, kontrol yeniden çalıştırıldı ve geçti. Ayrıntı: `araclar/cutcheck_sonuc.txt`

## 3. Saniye saniye
| Çıkış (sn) | Görüntü | Başın üstü / üst alan | Göğüs hizası (altyazı) | Müzik | Ses efekti |
|---|---|---|---|---|---|
| 0,00–4,00 | A: aydınlatılmış minare, yavaş yaklaşma (1,00→1,10) | 0,35 **MARDİN** + "GECE YÜRÜYÜŞÜ" (minare gövdesinde, kubbe açık) | – | Ney açılışı (Hicaz), dem, kudüm vuruşu | 0,00 derin vuruş + nefes yükselişi · 0,45 başlık pop |
| 1,90–3,90 | | Sol altta bilgi kartı: **ULU CAMİİ MİNARESİ · Kaidesindeki kitabe: 1176** | – | | 1,90 kart pop |
| 4,00–6,50 | B: merdivenler, geri çekilme (1,09→1,00) | Boş (manzara temiz) | – | Darbuka (maksum) + ud riffi girer | 3,70 whoosh |
| 6,50–8,50 | F: ışıklı konak cephesi, yavaş yaklaşma | Boş | – | Ritim sürer, sonda ud tremolo | 6,23 whoosh · 8,25 yumuşak whoosh |
| 8,50–13,71 | C: selfie, yürüyüş | 9,08 📍 **MEYDANIN ÜST SOKAĞI** | EVET, ŞİMDİ · MEYDANIN ÜST · SOKAĞINDAN · YÜRÜMEYE DEVAM · EDİYORUZ. · NEREYE GİDİYORUZ? | Müzik −9 dB'ye iner, konuşma sırasında ek −7 dB ducking | 9,08 pop |
| 13,71–16,95 | C: (jump cut) | 14,06 ➜ **ÇARŞININ ORTASINA** | BİRAZCIK ÇARŞININ · ORTASINA DOĞRU · GİDECEĞİZ. | alçak | 14,06 pop |
| 16,95–19,35 | D: arkadaşın konuşuyor → kamera savrulur | ➜ ÇARŞININ ORTASINA (17,0'da kapanır) | YOLU · GÖSTERİRSEN (yüzün sol altta olduğu için altyazı sağda) · DAHA GÜZEL BİR | alçak | 17,85 savrulma whoosh |
| 19,35–24,35 | D: savrulma bitip **sokak açılır** | 19,45 📍 **ÇARŞIYA DOĞRU** | GÖRÜNTÜ OLUR · ASLINDA. · ŞÖYLE GÖSTEREYİM · SİZLERE. | alçak | 19,40 parıltı |
| 24,35–27,35 | E: dar sarı sokak, yavaş yaklaşma | Boş | – | **Müzik geri gelir**: ud ezgisi + ney + darbuka | 24,05 whoosh |
| 27,35–30,55 | F: fenerli sokak, geri çekilme | 27,95 **MARDİN · GECE YÜRÜYÜŞÜ**, 28,85 🔖 "Kaydet, gezerken lazım olur" | – | 29,8 final vuruşu + ud akoru, ney uzun nota | 27,10 whoosh · 27,95 kapanış parıltısı |
| 30,10–30,55 | Siyaha karartma | | | Söner | |

Altyazı: aktif kelime sarı, önceki kelimeler beyaz, siyah kontur, kelime kelime pop. Kart, ekran görüntüsü ya da bölünmüş ekran sadece gerektiği yerde kullanıldı: tek kart minarede. Bölünmüş ekran bu içerikte gerekmedi (konuşma zaten iki kişilik tek kadraj).

## 4. Yerleşim güvenliği (`araclar/render.py` her karede kontrol eder)
- Yüz tespiti: YuNet, eğik kamera için −80…+80° döndürerek kare kare tarandı. Baş kutusu örtü/saç payıyla genişletildi, ±3 kare birleştirildi.
- D başında kadrajın sol altına kısmen giren yüzün için elle ek güvenlik alanı tanımlandı (dedektör kenarda kaçırıyor).
- Altyazı her parça için başlarla çakışmayan en yakın konuma otomatik yerleşiyor, gerekirse küçülüyor.
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500) ve sağ buton şeridi (x>940) boş.
- Önizleme karelerinde yüz çakışması **0**, arayüz ihlali **0**. Tam çıkışta 916 karenin hepsi kontrol edilip rapor edilecek.

## 5. Ses
- **Müzik:** tamamen kodla sentezlenmiş özgün parça (`araclar/audio.py`). Hicaz makamı (Re karar, 2. derece hafif tiz, 3. derece hafif pes), 120 BPM maksum ritmi. Enstrümanlar: darbuka düm/tek/ka, Karplus-Strong ile ud benzeri çift tel, ney benzeri üflemeli (vibrato + nefes), dem. Telifli kayıt ya da örnek yok.
- **Efektler:** derin vuruş, whoosh, pop, parıltı; hepsi numpy ile üretildi.
- **Konuşma:** 80 Hz high-pass, hafif kompresör. Konuşmada müzik −9 dB ve konuşmaya bağlı ek −7 dB ducking.
- **Ölçüm (ffmpeg ebur128):** Integrated **−14,0 LUFS**, True peak **−1,5 dBTP**.

## 6. Haklar / doğrulama
- Dış görsel, logo, gerçek kişi görseli, meme ya da arşiv video: **yok**. Görüntüdeki herkes kendi çekiminden.
- Font: Inter / Inter Display (SIL Open Font License 1.1). İkonlar (konum, ok, yer imi) kodla çizildi.
- Ekrandaki tek rakam **1176**: Mardin Ulu Camii minaresinin kare kaidesindeki kitabenin verdiği yapım tarihi.
  - Mardin İl Kültür ve Turizm Müdürlüğü: kitabe tarihi 1176; bugünkü minare 1888/89'da yeniden yapılmış. Bu yüzden kartta "minare 1176'da yapıldı" değil, "kaidesindeki kitabe: 1176" yazıyor.
  - Dergipark makalesi aynı kitabeyi 572 H. (1176) olarak okuyor.
- Minarenin Ulu Camii olduğu çekimin GPS'iyle (37,3135 K, 40,7345 D; Mardin eski şehir) ve minarenin biçimiyle uyumlu.
