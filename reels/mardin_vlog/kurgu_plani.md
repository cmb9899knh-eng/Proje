# Mardin Vol 2 – Reels kurgu planı v2 (ONAY BEKLİYOR)

Kaynak: 48 klip (ilk 16 + 32 yeni). Aynı IMG numaralı dosyalar tek uzun kaydın ~10 sn'lik ardışık parçaları.
Hepsi dikey HDR/HLG → SDR ton eşleme, 1080×1920, 30 fps. **Çıkış: 2:10,3 (130,3 sn)**. Reels sınırı 3 dk.
Konuşma hızlandırılmadı. Sadece boşluklar, tekrarlar, yarım ve kesik cümleler atıldı.

## 1. Tekrar / temizlik kararları

| Nerede | Ne vardı | Karar |
|---|---|---|
| 3150 ↔ 3151 (giriş iki kez çekilmiş) | "Bugün rotamızda Mardin Antik Kenti var / Bir sürü kafe… / Aynı zamanda yemek yeme yerleri…" iki kez | Son çekim **3151**: "Bugün Antik Kent'teyiz. Vol 2 diyelim. Dün Mardin sokaklarını gece gördük, gezdik." 3151'in "yemek yeme yerleri **bulunmuyor/bulunmaktadır**" cümlesi klip sonunda kesik olduğu için bu cümlenin tek temiz hâli 3150'den alındı: "Aynı zamanda yemek yeme yerleri de var, fotoğraf çekme yerleri de var." |
| 3151 "Şimdi de sırada antik kent var." | "var" ile sonraki "Mardin" arasında sessizlik yok (−32 dB) | Atıldı (temiz kesilemiyor, "Antik Kent'teyiz" ile aynı bilgi) |
| 3150 "…yeni yeni aslında **eee** popüler olmaya başladı. Çünkü önceden… yoktu." | "eee" ile "popüler" arasında boşluk yok | Atıldı (temiz kesim mümkün değil) |
| 3152 "Şimdi acaba Gülbahar'ı nereye götürsem?" | Parça başında "Şimdi" kesik (−23 dB'de başlıyor) | Atıldı |
| 3152 "Mesela Firuze, mesela Espresso, mesela **(belirsiz)**, mesela Nevada gibi" | Üçüncü kafe adı anlaşılmıyor ve sonraki kelimeye yapışık | Liste atıldı (yanlış isim yazmamak için). Nevada ve Espresso Lab kendi kliplerinde geçiyor |
| 3152 "Mardin'de olmayan birçok kafe açıldı." | Önceki cümlenin tekrarı, klip sonunda kesik | Atıldı |
| 3159 "Bakalım Tinda/Tilda'nın bahsettiği… Benlik dedi ama bakalım" | İsim ve anlam belirsiz | Atıldı. 3159 sessiz ara görüntü (kemerden giriş) |
| 3162 "Nevada'nın merdivenlerinden aşağı inip … değerlendireceğim. Ona göre oturup…" | "değerlendireceğim" sonraki yarım cümleye yapışık | Konuşma atıldı. 3162 sessiz ara görüntü (merdivenden iniş) |
| 3286 "**Evet** şimdi biz çıktık…" / "**Güzel** aynalar…" | İlk kelimeler kayıt başında kesik | "Şimdi biz çıktık kafeden. Kahvelerimiz elimizde." / "Aynalar bizi karşılıyor." |
| 3286 "Neresine geziyoruz? Meydana doğru gidiyoruz. Evet şu anda meydana doğru ilerliyoruz." | Aynı cümle iki kez | Son temiz hâli: "Evet, şu anda meydana doğru ilerliyoruz." |
| 3294 "Şu anda size meydanı gösteriyorum. Kale de…" | Baş kesik, ikinci cümle anlaşılmıyor | Sessiz manzara olarak kullanıldı (kale + şehir) |
| 3296 "Şu anda meydanın ilerisindeyiz. Bu şekilde." | "Bu şekilde" klip sonunda kesik. "Meydan" bilgisi zaten var | Sessiz ara görüntü + MEYDAN rozeti |
| 3298 "Mardin'de sadece… evet tam diyordum aç gezen doyuyor" ↔ 3299 "İşte ne diyecektim? Bu yolda yürüyün, aç olun, doyuyorsunuz yol bitmeden." | Aynı fikir iki kez | Son temiz hâli (3299): "Bu yolda yürüyün, aç olun, doyuyorsunuz yol bitmeden." |
| 3301 "Gümüş, şarap, kuruyemiş… meşhur olanlar Mardin'de" ↔ 3302 "Aynı zamanda Mardin'de Süryani şarabı meşhur, Süryani çöreği meşhur. Bir de… hediyelik / şallar… Gümüş, bakır çok talep ediliyor." | Aynı fikir iki kez | Son çekim 3302: "Aynı zamanda Mardin'de Süryani şarabı meşhur." "…çöreği meşhur. Bir de…" geçişinde sessizlik yok. "Şallar" parça başında, "ediliyor" parça sonunda kesik. Süryani çöreği tabelası ve gümüş vitrini görüntüyle gösteriliyor |
| 3309 "…getirdim. Mezopotamya'nın eşsizliğinde." | Son kelime klip sonunda kesik | "…ziyaret edilen yere getirdim." ile bitiyor |
| 3291 "Ben sanırım…" | Yarım cümle | Atıldı |
| Uzun boşluklar | 3151 (0,7 + 0,6 sn), 3150 (1 sn), 3160 (1,5 sn), 3163 (0,4 sn), 3286 (1,4 + 0,45 sn), 3295 (0,7 sn), 3297 (0,8 sn), 3299 (0,3 sn), 3308 (0,45 sn) | Kırpıldı |

Sessiz kliplerdeki "Altyazı M.K." ve "İzlediğiniz için teşekkür ederim" Whisper uydurması. Hiçbiri altyazıya girmedi.

## 2. Kesim kontrolü (`araclar/cutcheck2.py`, rapor: `araclar/kesim_kontrol_raporu.txt`): **GEÇTİ**
- 38 konuşma kenarının hepsi −45 dB altında → kesik hece yok. İlk denemede 4 kesik kenar ve 3 eksik kelime yakalandı. Hepsi düzeltildi, gerekirse cümle atıldı (yukarıdaki tablo)
- Birleşik konuşma izi Whisper large-v3 ile yeniden yazıya döküldü. Beklenen metinle **bire bir** eşleşiyor. Ardışık kelime ya da ifade tekrarı **yok**
- Düşük güvenli kelimeler: "Cafe" (bilinen kafe adı, Nevada Cafe) ve "Şimdi" (0,50 sınırda, metin doğru)

## 3. Görsel dil
- **Renk:** Tüm kliplere aynı sıcak/kontrastlı ton eğrisi, +%12 doygunluk, hafif vinyet. Farklı ışıktaki çekimler tek bir video gibi görünür
- **Geçişler:** Bölüm başlarında **whip-pan** (yatay hareket bulanıklığı) + sıcak **ışık sızması**. Manzaralar arasında **çapraz geçiş**. Kahve montajında **flaş**. Aynı çekimdeki atlamalarda **%7 punch-in** (jump-cut'ı gizler). Sonda karartma
- **Manzara ön planda:** Açılış minare + Mezopotamya ovası (üstünde "Mardin bir efsane" dış sesi) → kale/şehir → panorama. Final: Mezopotamya terası → **fotoğraf molası** → ova/kubbeler → yol. Manzaralarda yavaş Ken Burns yakınlaşması
- **Fotoğrafların (eklendi):** Minare ve ova önündeki 3 teras fotoğrafı (1, 2, 4), 3309'daki "…en çok fotoğraf çekmek için ziyaret edilen yere getirdim" cümlesinden hemen sonra polaroid kart olarak düşüyor. Her biri deklanşör sesi + flaşla giriyor: hafif dönük, gölgeli, içinde yavaş zoom, arkada bulanık manzara. Kafede bardakla çekilen yakın plan (3) teras anına uymadığı için **kahve montajında** latte art'tan sonra 1,3 sn tam ekran flaşla giriyor. Fotoğraflardaki yüzler de algılanıyor, rozet ve yazı onlara binmiyor
- **Başlık/rozet:** Açılışta MARDİN · VOL 2. Bölüm rozetleri ANTİK KENT, KAFE DURAĞI, ÇARŞI, MEYDAN, BADEM ŞEKERİ, MEZOPOTAMYA, FOTOĞRAF MOLASI. Kapanış MARDİN · bir efsane (kendi cümlen)
- **Altyazı:** Göğüs hizasında, kelime kelime. Aktif kelime sarı ve pop ile girer. Metin doğrulanmış cümlelerden, zamanlama enerji adacıklarına hizalı
- Ara görüntüler (kahve montajı vb.) bilerek grafiksiz

## 4. Saniye saniye

| Çıkış (sn) | Kaynak | İçerik | Giriş geçişi | Başın üstü / grafik | Göğüs hizası (altyazı) | Ses |
|---|---|---|---|---|---|---|
| 0.00–2.93 | 3309_790d 1.80–4.73 | Mardin bir efsane. | kesme, Ken Burns ×1.07 | — | MARDİN BİR EFSANE | dış ses (3308_699e) |
| 2.93–5.33 | 3294_ffe9 2.30–4.70 | Kale ve şehir manzarası | çapraz geçiş, Ken Burns ×1.08 | **MARDİN · VOL 2** başlık (3.1–7.2) | — | ortam kapalı · parıltı |
| 5.33–7.33 | 3148 3.30–5.30 | Mardin panoraması | çapraz geçiş, Ken Burns ×1.06 | — | — | ortam -14 dB |
| 7.33–10.77 | 3151_6953 0.73–4.17 | Bugün Antik Kent'teyiz. Vol 2 diyelim. | **whip-pan** + ışık sızması | **ANTİK KENT** rozeti (7.5–10.5) | BUGÜN ANTİK KENT'TEYİZ VOL 2 DİYELİM | konuşma · whoosh, pop |
| 10.77–13.27 | 3151_6953 4.57–7.07 | Dün Mardin sokaklarını gece gördük, | kesme | — | DÜN MARDİN SOKAKLARINI GECE GÖRDÜK | konuşma |
| 13.27–14.87 | 3151_6953 7.50–9.10 | gezdik. | kesme | — | GEZDİK | konuşma |
| 14.87–17.30 | 3159_adfb 0.27–2.70 | Kemerden giriş | kesme | — | — | ortam kapalı |
| 17.30–21.93 | 3152_f5e4 2.97–7.60 | Şimdi bir sürü kafe var derken zincir kafelerin çoğu açıldı burada. | kesme | — | ŞİMDİ BİR SÜRÜ KAFE VAR DERKEN ZİNCİR KAFELERİN ÇOĞU AÇILDI BURADA | konuşma |
| 21.93–25.20 | 3150_ddcd 2.53–5.80 | Aynı zamanda yemek yeme yerleri de var, | kesme | — | AYNI ZAMANDA YEMEK YEME YERLERİ DE VAR | konuşma |
| 25.20–26.70 | 3150_ddcd 6.47–7.97 | fotoğraf çekme yerleri de var. | kesme + %7 punch-in | — | FOTOĞRAF ÇEKME YERLERİ DE VAR | konuşma |
| 26.70–31.87 | 3152_f22a 0.60–5.77 | Şimdi Gülbahar bunları bir görsün. Hangisinde oturmak istiyorsa orada oturalım. | kesme | — | ŞİMDİ GÜLBAHAR BUNLARI BİR GÖRSÜN HANGİSİNDE OTURMAK İSTİYORSA ORADA OTURALIM | konuşma |
| 31.87–33.87 | 3159_ca2e 4.00–6.00 | Kafelerin önünden yürüyüş | kesme | — | — | ortam -14 dB |
| 33.87–37.37 | 3160 1.00–4.50 | Evet şimdi Nevada Cafe'nin girişindeyiz. | **whip-pan** + ışık sızması | **KAFE DURAĞI** rozeti (34.1–37.1) | EVET ŞİMDİ NEVADA CAFE'NİN GİRİŞİNDEYİZ | konuşma · whoosh, pop |
| 37.37–39.13 | 3160 6.03–7.80 | Bakalım nasıl bir yer çıkacak. | kesme | — | BAKALIM NASIL BİR YER ÇIKACAK | konuşma |
| 39.13–40.33 | 3161 0.30–1.50 | Camdan manzara | kesme | — | — | ortam -14 dB |
| 40.33–42.53 | 3162_6a6b 5.40–7.60 | Merdivenlerden iniş | kesme | — | — | ortam kapalı |
| 42.53–45.40 | 3163_edd4 0.77–3.63 | Evet, şimdi de Espresso Lab'deyiz. | kesme | — | EVET ŞİMDİ DE ESPRESSO LAB'DEYİZ | konuşma |
| 45.40–47.93 | 3163_edd4 4.00–6.53 | Gülbahar'a kafeleri gösteriyorum. | kesme | — | GÜLBAHAR'A KAFELERİ GÖSTERİYORUM | konuşma |
| 47.93–49.13 | 3165_a5bb 1.00–2.20 | Portafiltre | flaş | — | — | ortam -12 dB · tık |
| 49.13–50.43 | 3167_385d 0.00–1.30 | Espresso akıyor | kesme | — | — | ortam -12 dB |
| 50.43–52.23 | 3168_21df 0.60–2.40 | Latte art | kesme | — | — | ortam -12 dB |
| 52.23–53.53 | foto3_kafe.jpg | Kafe fotoğrafı (tam ekran) | flaş | tam ekran fotoğraf, yavaş zoom | — | müzik · tık |
| 53.53–54.73 | 3166 2.20–3.40 | Buzlu kahve | kesme | — | — | ortam -12 dB |
| 54.73–55.83 | 3178 0.10–1.20 | İki içecek | kesme | — | — | ortam -12 dB |
| 55.83–57.03 | 3170 0.20–1.40 | Kafede yürüyüş | kesme | — | — | ortam -12 dB |
| 57.03–58.43 | 3191 3.00–4.40 | Selfie | kesme | — | — | ortam kapalı |
| 58.43–60.03 | 3234 0.60–2.20 | Kahve yudumu | kesme | — | — | ortam -12 dB |
| 60.03–61.67 | 3286_7f55 0.43–2.07 | Şimdi biz | **whip-pan** + ışık sızması | **ÇARŞI** rozeti (61.0–64.0) | ŞİMDİ BİZ | konuşma · whoosh, pop |
| 61.67–64.40 | 3286_7f55 3.03–5.77 | çıktık kafeden. Kahvelerimiz elimizde. | kesme | — | ÇIKTIK KAFEDEN KAHVELERİMİZ ELİMİZDE | konuşma |
| 64.40–66.93 | 3286_2b7d 0.40–2.93 | Aynalar bizi karşılıyor. | kesme | — | AYNALAR BİZİ KARŞILIYOR | konuşma |
| 66.93–68.53 | 3287 0.20–1.80 | Mardin Hatırası aynası | kesme | — | — | ortam -14 dB |
| 68.53–70.67 | 3286_ddcc 5.00–7.13 | Evet, şu anda meydana doğru | kesme | — | EVET ŞU ANDA MEYDANA DOĞRU | konuşma |
| 70.67–71.87 | 3286_ddcc 7.40–8.60 | ilerliyoruz. | kesme + %7 punch-in | — | İLERLİYORUZ | konuşma |
| 71.87–73.57 | 3288 0.20–1.90 | Tespih | Şal (bölünmüş ekran) | kesme | bölünmüş ekran, TESPİH / ŞAL etiketleri | — | ortam -14 dB · whoosh + tık |
| 73.57–74.87 | 3289 0.50–1.80 | Puşiler | kesme | — | — | ortam -14 dB |
| 74.87–76.87 | 3291 0.30–2.30 | Minare | çapraz geçiş, Ken Burns ×1.06 | — | — | ortam -14 dB |
| 76.87–81.43 | 3295 0.10–4.67 | Şu an sanırım çarşıda geziyoruz. Evet, meydandayız arkadaşlar. | **whip-pan** + ışık sızması | — | ŞU AN SANIRIM ÇARŞIDA GEZİYORUZ EVET MEYDANDAYIZ ARKADAŞLAR | konuşma · whoosh |
| 81.43–82.90 | 3295 5.37–6.83 | Çok güzel yerler var. | kesme | — | ÇOK GÜZEL YERLER VAR | konuşma |
| 82.90–84.50 | 3296 4.27–5.87 | Meydan sokağı | kesme, Ken Burns ×1.05 | **MEYDAN** rozeti (83.1–84.4) | — | ortam -14 dB · pop |
| 84.50–87.30 | 3297 1.10–3.90 | Mardin'in meşhur badem şekerleri. | kesme | **BADEM ŞEKERİ** rozeti (84.7–87.7) | MARDİN'İN MEŞHUR BADEM ŞEKERLERİ | konuşma · pop |
| 87.30–89.87 | 3297 4.73–7.30 | Nereden geçerseniz ikram ediliyor. | kesme | — | NEREDEN GEÇERSENİZ İKRAM EDİLİYOR | konuşma |
| 89.87–92.37 | 3298_c3fc 5.40–7.90 | Tadımlık ikramlar | kesme | — | — | ortam kapalı |
| 92.37–94.70 | 3299_9f0d 2.17–4.50 | Bu yolda yürüyün, | kesme | — | BU YOLDA YÜRÜYÜN | konuşma |
| 94.70–98.33 | 3299_9f0d 4.80–8.43 | aç olun, doyuyorsunuz yol bitmeden. | kesme + %7 punch-in | — | AÇ OLUN DOYUYORSUNUZ YOL BİTMEDEN | konuşma |
| 98.33–102.97 | 3302_177a 0.07–4.70 | Aynı zamanda Mardin'de Süryani şarabı meşhur. | kesme | — | AYNI ZAMANDA MARDİN'DE SÜRYANİ ŞARABI MEŞHUR | konuşma |
| 102.97–104.67 | 3301_1f5b 6.30–8.00 | Hakiki Süryani Çöreği tabelası | kesme | — | — | ortam kapalı |
| 104.67–106.47 | 3301_852a 6.50–8.30 | Gümüş vitrini | kesme | — | — | ortam kapalı |
| 106.47–110.30 | 3308_6bd7 0.20–4.03 | İşte size bahsettiğim yerler, buralar. | **whip-pan** + ışık sızması | **MEZOPOTAMYA** rozeti (106.7–109.7) | İŞTE SİZE BAHSETTİĞİM YERLER BURALAR | konuşma · whoosh, pop |
| 110.30–112.73 | 3308_6bd7 4.50–6.93 | Mezopotamya, Dicle. | kesme, Ken Burns ×1.04 | — | MEZOPOTAMYA DİCLE | konuşma |
| 112.73–118.87 | 3309_8598 0.33–6.47 | Şimdi Gülbahar'ı Mardin'de en çok fotoğraf çekmek için ziyaret edilen yere getirdim. | kesme | — | ŞİMDİ GÜLBAHAR'I MARDİN'DE EN ÇOK FOTOĞRAF ÇEKMEK İÇİN ZİYARET EDİLEN YERE GETİRDİM | konuşma |
| 118.87–123.07 | foto1_teras.jpg, foto2_teras.jpg, foto4_teras.jpg | Teras fotoğrafları (deklanşör + polaroid) | flaş | **FOTOĞRAF MOLASI** rozeti (119.1–122.1); 3 polaroid fotoğraf, deklanşör + flaş | — | müzik · tık, pop, deklanşör ×3 |
| 123.07–125.53 | 3309_790d 4.73–7.20 | Ova → kubbeler | çapraz geçiş, Ken Burns ×1.06 | — | — | ortam -14 dB |
| 125.53–127.10 | 3308_699e 0.47–2.03 | Çok güzel. | çapraz geçiş, Ken Burns ×1.05 | — | ÇOK GÜZEL | konuşma |
| 127.10–130.30 | 3359_9eae 1.00–4.20 | Yol (kapanış) | çapraz geçiş | **MARDİN · BIR EFSANE** başlık (127.5–130.2) | — | ortam -16 dB · parıltı |

## 5. Yerleşim güvenliği (`araclar/render.py`, her karede)
- Yüz: YuNet, 48 klipte kare kare. Kutular başörtüsü/saç ve çene payıyla genişletildi. **Zoom/punch-in/whip kaymasına göre dönüştürülerek** kontrol ediliyor. Tek karelik ya da elin üstündeki yanlış algılamalar elendi. Uzak yayalar korunuyor
- Rozetler **yalnızca başın gerçekten üstüne** konuyor. Yer yoksa aynı çekim içinde yer olan ana kaydırılıyor, o da yoksa yüzün yanına. Rozet yalnızca kendi çekiminde görünüyor (yanlış etiketleme yok)
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500), sağ buton şeridi (x>940) boş. Pop animasyonu taşması dâhil
- Grafik–grafik çakışması kontrol ediliyor
- **41 örnek karede: yüz ihlali 0, arayüz ihlali 0, çakışma 0.** Tam render'da 3909 karenin hepsi kontrol edilecek

## 6. Ses
- Konuşma: kaynak seviyesi, 80 Hz high-pass, kesimlerde 12 ms fade
- Ara görüntü ortam sesi: −12…−16 dB. İçinde başka konuşma olan ara görüntülerde kapalı
- SFX (hepsi numpy sentezi, telifsiz): whoosh (whip), pop (rozet), parıltı (başlık), tık (flaş/bölünmüş ekran), deklanşör (fotoğraflar)
- **Müzik (karar bekliyor, aşağıda soru 1):** Kodla bestelenmiş "Mardin havası". Hicaz makamı. Açılış ve finalde ney + dem, Antik Kent'ten itibaren darbuka + ud ostinatosu, kahve montajında daha dolu ritim. Konuşma altında ~−11 dB kısılıyor. Dinle: `onizleme/muzik_ornegi_30sn.m4a`
- Seviye: müzikli miks **−14,1 LUFS / −2,3 dBTP**, müziksiz miks **−14,1 LUFS / −2,3 dBTP**

## 7. Haklar / doğrulama
- Eklenen dış görsel, logo, kişi görseli, meme, arşiv video: **yok**. Görünen tabela ve logolar senin çekiminde zaten var
- Font: Inter / Inter Display (SIL Open Font License 1.1). İkonlar kodla çizildi
- Müzik ve efektler: kodla üretildi, telifsiz
- Ekranda gösterilen rakam: **yok** ("VOL 2" senin kendi ifaden, istatistik değil)
- Araçlar: Whisper large-v3 (MIT), YuNet (OpenCV Zoo, MIT), ffmpeg

## 8. Onay için sorular
1. **Müzik:** Mardin'e özgü şarkıların kayıtları telifli (anonim türkülerin kayıtları da). Seçenekler:
   (a) Kodla bestelediğim Hicaz parçası videoda olsun (örneği dinle)
   (b) Videoyu müziksiz ver, Instagram'da yüklerken lisanslı müzik kütüphanesinden bir Mardin şarkısı seç (en "has" sonuç bu olur, telif sorunu yok)
   (c) İkisi birden: müzikli ve müziksiz iki dosya
3. **Bölünmüş ekrandaki dükkân telefon numarası** (sağ üst tabela): bulanıklaştırayım mı?
4. **Minare:** etiket koymadım. "Ulu Camii" yazmamı istersen teyit et
5. Videoda Gülbahar, diğer arkadaşın ve badem şekeri satıcısı yüzleriyle görünüyor. Paylaşım izinlerini senin teyit etmen gerekiyor
6. Süre 2:10. Daha kısa (~60–90 sn) bir sürüm istersen hangi bölümlerin kalacağını söyle ya da ben öneri getireyim
