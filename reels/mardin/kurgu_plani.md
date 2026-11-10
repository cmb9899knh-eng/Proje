# Mardin Gece Yürüyüşü – Tanıtım Reels kurgu planı v3 (ONAY BEKLİYOR)

Çıkış: 1080×1920, 30 fps, **55,5 sn**, HDR (HLG) → SDR ton eşleme, ses **−14,0 LUFS / −1,5 dBTP**
Malzeme: 38 yükleme → **35 farklı çekim** (iki IMG_3060 ve IMG_2945'in iki kaydı birebir aynı dosya; IMG_2944'ün üç kaydı birbirinden farklı). Kurguda 27 çekim kullanıldı.

**v3 değişiklikleri:** IMG_2944 (arkadaşının mikrofonlu sunuculuğu) eklendi: açılış, Cafe Jin / Leyli Restoran bölümü ve "Bu kadar." kapanışı. Süre uzamasın diye ikinci konak planı (F), çiçek (2974) ve ayna el sallaması (2987) çıkarıldı. "GÖRÜŞÜRÜZ" minaredeki kapanış kartına taşındı.
Müzik 120 BPM; tüm kurgu kesimleri vuruşa (0,5 sn) oturuyor.

## 1. Konuşma kesimleri (hız değişikliği YOK)
| Kaynak | Tutulan | Atılan ve nedeni |
|---|---|---|
| IMG_2944 (1. kayıt) | 0,90–5,30 "Merhaba arkadaşlar, sizlere Mardin sokaklarını tanıtacağım." | 5,48–6,48 anlaşılmayan ifade (Whisper "Vol 1", p=0,37). 6,48–10,3 "Öncelikle meydandan merdivenleri…" kayıt bitince yarım kalıyor |
| IMG_2944 (2. kayıt) | 0,00–6,22 "Sola doğru dönerseniz eğer biraz yürüdükten sonra Cafe Jin ve Leyli Restoran'la karşılaşacaksınız." Ses kesintisiz; görüntü "Cafe Jin"de Coffee JIN tabelasına (2. kayıt 7,0 sn), "Leyli Restoran"da vitray cepheye (1. kayıt 4,4 sn) geçiyor | Kayıt "S" sesinin içinde başlıyor, bu yüzden 0,00'dan alındı (0,04'ten alınınca Whisper "Kola" duydu). 6,49–9,64 "Tabi buraya varmadan önce şöyle ışıkla…" yarım |
| IMG_2944 (3. kayıt) | 5,95–6,80 "Bu kadar." + gülümseme | 0–5,0: kayıt kelimenin ortasından başlıyor (0,02 sn'de −24 dB; "…landırmalı bir ara yoldan…", 2. kaydın devamı). Kelimeler arasında boşluk olmadığı için kesik hece bırakmadan kesilemiyor |
| IMG_2949 | 0,30–5,05 "Şimdi Mardin neyle meşhur? Tabii ki bu güzel sokaklarıyla." | 0–0,30: kayıt "Evet" kelimesinin ortasından başlıyor (kesik). 5,38–8,5: "Bu sokakların dili olsa da…" yarım cümle |
| IMG_2954 | 0,30–1,955 "E bir de Mardin'in neyi meşhur?" | 1,98–2,55: anlaşılmayan bir kelime (Whisper "Tinda?" p=0,41); altyazıya yanlış şey yazmamak için atıldı |
| IMG_2954 | 3,25–6,00 "Tabii ki bu merdivenleri." (görüntü: IMG_2907 merdivenler) | – |
| IMG_2954 | 6,82–7,45 "Ay…" + 7,94–8,66 "çok yorucu." | 7,45–7,94 boşluk (0,5 sn) kısaltıldı; 8,74 sonrası nefes ve gürültü |
| IMG_2973 | 0,20–2,76 "Karıştır, gülümse." | – |
| IMG_2945 (2. kayıt) | 2,105–9,00 "Yolu gösterirsen daha güzel bir görüntü olur aslında. Şöyle göstereyim sizlere." | 0–2,1: ilk kelime kesik ("…laklar ve kafeler…"); nefes (2,105–2,152) ve arka plandaki mırıltı (5,90–6,36) −30 dB'ye indirildi |
| Kullanılmayan konuşmalar | – | IMG_2945 1. kayıt ("Evet şimdi meydanın üst sokağından…"): "Evet şimdi" 2949 ile tekrar edeceği ve video uzayacağı için. 2972 "Çok açmışsın" iki kez tekrarlanıyor. 2968 ve 2971 düşük güvenle anlaşılıyor; bu çekimler müzik altında, altyazısız kullanıldı. 2906 (minare) sesinde arka planda telefon konuşması var; kapatıldı |

Bütün konuşma parçaları aynı seviyeye eşitlendi (−24 dB). Uzaktan gelen "Karıştır, gülümse" de duyulur.

## 2. Kesim kontrolü (`araclar/cutcheck.py`): GEÇTİ
- 9 kesim noktası (kesimin iki yanında 10 ms): −45,2 ile −88,3 dB arası → kesik hece yok. Baş −69,2 dB, son −44,2 dB.
- "Cafe Jin" özel isim: Whisper ham kayıtta da düşük güvenle duyuyor (0,48; "Cafejin" ya da "Cafe Jean" yazıyor). Tabelada "Coffee JIN" yazıyor. Araçta yazım varyantlarıyla özel isim istisnası olarak tanımlandı; altyazıda "CAFE JİN".
- Whisper large-v3 ile yeniden transkripsiyon, beklenen metinle **TAM** eşleşme. Ardışık tekrar yok, düşük güvenli kelime yok.
- "Mardin neyle meşhur? Tabii ki bu…" / "Mardin'in neyi meşhur? Tabii ki bu…" bilinçli paralel şaka (soru-cevap esprisi). Araçta izinli ifade olarak tanımlandı; başka tekrar yok.
- İlk çalıştırmada "Şimdi" düşük güvenliydi (p=0,23). Başına 0,5 sn sessizlik eklenince p=0,86 → kelime sağlam; düşük güven, sesin dosyanın tam başında başlamasından kaynaklanıyordu. Ayrıntı: `araclar/cutcheck_sonuc.txt`

## 3. Saniye saniye
| Çıkış (sn) | Görüntü (kaynak) | Grafik | Altyazı (göğüs hizası) | Müzik | Efekt (ses/görüntü) |
|---|---|---|---|---|---|
| 0,0–1,5 | **KANCA:** MARDİN TÜRKİYE tabelası (3062), tabelaya yaklaşma | "GECE YÜRÜYÜŞÜ" | – | Büyük vuruş: darbuka düm, bas, ud akoru, ney düşüşü; darbuka rulosu | Beyaz flaş · derin vuruş |
| 1,5–5,9 | Arkadaşın mikrofonla kameraya geliyor (2944) | – | MERHABA ARKADAŞLAR. · SİZLERE MARDİN · SOKAKLARINI TANITACAĞIM. | Hafif ritim, bas, ud (ducking) | – |
| 5,9–10,65 | 2949: kameraya yürüyüşün | – | ŞİMDİ MARDİN · NEYLE MEŞHUR? · TABİİ Kİ BU · GÜZEL SOKAKLARIYLA. | Hafif ritim | – |
| 10,65–15,5 | **SOKAKLAR montajı** (vuruşa kesim): fenerli sokak (F), Eski Şeyler sokağı (3082), sarı dar sokak (E), minare (A) | 14,1 📍 ULU CAMİİ | – | **Ana tema:** bağlama benzeri tel + ney + darbuka + el çırpma + zil + yaylı dolgu | Zoom-punch + whip geçişleri + whoosh |
| 15,5–17,15 | 2954: koşarak gelişin | – | E BİR DE · MARDİN'İN NEYİ MEŞHUR? | Ritim alçak | – |
| 17,15–19,9 | **Merdivenler** (2907), ses 2954'ten devam | – | TABİİ Kİ BU · MERDİVENLERİ. | Ritim alçak | Zoom-punch |
| 19,9–21,25 | 2954: nefes nefese sen | – | AY · ÇOK YORUCU. | **Müzik bant gibi yavaşlayıp durur** (şaka) | Bant durması sesi · yüzüne komik zoom |
| 21,25–24,5 | **Kediler** (2954b, 3086, 3078) | SOKAKLARIN GERÇEK SAHİPLERİ | – | Oyuncaklı pizzicato + parmak şıklatma | Işık sızması · kodla "miyav" |
| 24,5–30,7 | Arkadaşın sokakta (2944) → "Cafe Jin"de **Coffee JIN** tabelası → "Leyli Restoran"da **vitray cephe** | – | SOLA DOĞRU DÖNERSENİZ · EĞER BİRAZ · YÜRÜDÜKTEN SONRA · CAFE JİN · VE LEYLİ RESTORAN'LA · KARŞILAŞACAKSINIZ. | Hafif ritim, ud (ducking) | Zoom-punch (ses kesintisiz akar) |
| 30,7–33,0 | **Gizli kapı** gibi açılan kitaplık (2960) | GİZLİ KAPI?! | – | Kafe teması: kanun arpejleri, bendir | Işık sızması · sihirli parıltı · whip |
| 33,0–38,0 | Kitap kafe: kitap duvarı, çevirmeli telefon, kemerli raflar, kitap seçen sen, okuyan sen | 📚 KİTAP KAFE | – | Sakin kafe teması, ney | Vuruşa zoom-punch |
| 38,0–40,56 | Çay karıştıran arkadaşın (2973) | – | KARIŞTIR, · GÜLÜMSE. | Alçak | – |
| 40,56–41,5 | Menüyle gülümsemen (2968) | – | – | | Zoom-punch |
| 41,5–44,5 | Kafe aynasında selfie (3060) → **Aynalı Sokak** tabelası ve sen (3082) | 📍 AYNALI SOKAK (yalnız 3082'de) | – | **Gerilim yükselir:** darbuka rulosu, kreşendo, ney | Whip · deklanşör |
| 44,5–46,8 | 2945: arkadaşın konuşuyor → kamera savrulur | – | YOLU · GÖSTERİRSEN · DAHA GÜZEL BİR | Kalp atışı gibi düm + gerilim | Yükselen gerilim + savrulma whoosh |
| 46,8–51,4 | **Sokak açılır** (2945) | 📍 ÇARŞIYA DOĞRU | GÖRÜNTÜ OLUR · ASLINDA. · ŞÖYLE GÖSTEREYİM · SİZLERE. | **Ana tema patlar** (konuşma altında alçak) | Beyaz flaş + açılış vuruşu + zoom |
| 51,4–53,0 | Nazar boncuklu ağaç (3088) | – | – | Ana tema (tam) | Işık sızması · zoom-punch |
| 53,0–54,0 | Arkadaşın Leyli önünde: "Bu kadar." + gülümseme (2944) | – | BU KADAR. | Tema durur, ney | Whip |
| 54,0–55,5 | Minare (2906) | **GÖRÜŞÜRÜZ / MARDİN / GECE YÜRÜYÜŞÜ** + 🔖 "Kaydet, gezerken lazım olur" | – | **Final vuruşu** + bağlama akoru + ney | Flaş · parıltı · son 0,4 sn karartma |

Her karede: hafif S-eğrisi kontrast, vinyet, çok hafif film greni. Konuşmasız planlarda yavaş yaklaşma ya da uzaklaşma var.

## 4. Yerleşim güvenliği (her karede otomatik kontrol)
- Yüz tespiti (YuNet): 25 çekim, eğik kamera için −80…+80° döndürülerek tarandı. Baş kutusu örtü/saç payıyla genişletildi ve ±3 kare birleştirildi. Tek karelik dev yanlış tespitler ayıklandı.
- Altyazı ve notlar, gösterildikleri sürenin tamamında hiçbir başa çarpmayan en yakın konuma yerleşiyor, gerekirse küçülüyor.
  - Uzaktan yürüdüğün 2949'da yüzün çok küçük; göğüs hizası yüze çok yakın düştüğü için altyazı başının biraz üstünde.
  - "ÇOK YORUCU." da aynı nedenle başının üstünde.
- Duvardaki portre tabloları da yüz sayıldı; üstlerine yazı gelmiyor.
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500) ve sağ buton şeridi (x>940) boş.
- Tespit temizliği: karede net bir yüz (skor ≥0,85) varken ceket gibi yerlerde çıkan düşük skorlu tespitler atıldı.
- Altyazılar ait oldukları konuşma planının sonunda bitiyor; sonraki sahneye taşmıyor.
- 18 örnek karede yüz çakışması **0**, arayüz ihlali **0**. Tam çıkışta 1665 karenin hepsi kontrol edilip rapor edilecek.
- Bölünmüş ekran ve kart bu kurguda gerekmedi. Not balonları kullanıldı; her yeri doldurmamak için manzara planlarının çoğu yazısız.

## 5. Ses
- **Müzik** (`araclar/audio.py`): tamamen kodla sentezlenmiş özgün beste. Hicaz makamı, Re karar (2. derece tiz, 3. derece pes koma yaklaşımı), 120 BPM, maksum ritmi.
  - Enstrümanlar: bağlama, ud ve kanun benzeri teller (Karplus-Strong), ney benzeri üflemeli, darbuka (düm/tek/ka), bendir, zil, el çırpma, bas, yaylı dolgu.
  - Bölümler: kanca vuruşu → sokaklar ana teması → bant durması şakası → kedi pizzicatosu → kitap kafe teması → gerilim yükselişi → sokak açılışında tema patlaması → final.
- **Efektler** (hepsi kodla): derin vuruş, whoosh, pop, bant durması, kedi sesi, sihirli parıltı, deklanşör, yükselen gerilim.
- **Konuşmada:** müzik −9 dB, ayrıca konuşmaya bağlı −7 dB ducking. Konuşmalar 80 Hz high-pass ve hafif kompresörden geçti.
- **Ölçüm (ffmpeg ebur128):** Integrated **−14,0 LUFS**, True peak **−1,5 dBTP**.

## 6. Haklar / doğrulama
- Dış görsel, logo, gerçek kişi görseli, meme ya da arşiv video: **yok**. Görüntüdeki her şey kendi çekimlerin.
  - MARDİN tabelası ile Aynalı Sokak, Eski Şeyler, Coffee JIN ve Leyli tabelaları çekimin içinde kendiliğinden görünüyor. Mekân adları ayrı logo ya da grafik olarak eklenmedi; yalnız arkadaşının söylediği şekliyle altyazıda geçiyor.
- Telifli müzik ya da ses: **yok**.
- Font: Inter / Inter Display (SIL Open Font License 1.1). İkonlar (konum, kitap, yer imi) kodla çizildi.
- **Ekranda rakam yok.** Önceki plandaki "1176" kartı, minare artık 1,5 sn'lik montaj planı olduğu için kaldırıldı.
- "ULU CAMİİ" etiketi: çekim GPS'i (37,3135 K, 40,7345 D; Mardin eski şehir) ve minarenin biçimi Mardin Ulu Camii minaresiyle uyumlu.
- "AYNALI SOKAK" etiketi sadece tabelanın göründüğü IMG_3082'de. Kafe aynası (3060) GPS'e göre ~500 m uzakta olduğu için etiketlenmedi.
