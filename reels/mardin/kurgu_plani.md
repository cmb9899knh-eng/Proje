# Mardin Gece Yürüyüşü – Tanıtım Reels kurgu planı v2 (ONAY BEKLİYOR)

Çıkış: 1080×1920, 30 fps, **47,5 sn**, HDR (HLG) → SDR ton eşleme, ses **−14,0 LUFS / −1,5 dBTP**
Malzeme: 35 yükleme → **32 farklı çekim** (iki IMG_3060 ve IMG_2945'in iki kaydı birebir aynı dosya). Kurguda 26 çekim kullanıldı.
Müzik 120 BPM; tüm kurgu kesimleri vuruşa (0,5 sn) oturuyor.

## 1. Konuşma kesimleri (hız değişikliği YOK)
| Kaynak | Tutulan | Atılan ve nedeni |
|---|---|---|
| IMG_2949 | 0,30–5,05 "Şimdi Mardin neyle meşhur? Tabii ki bu güzel sokaklarıyla." | 0–0,30: kayıt "Evet" kelimesinin ortasından başlıyor (kesik). 5,38–8,5: "Bu sokakların dili olsa da…" yarım cümle |
| IMG_2954 | 0,30–1,955 "E bir de Mardin'in neyi meşhur?" | 1,98–2,55: anlaşılmayan bir kelime (Whisper "Tinda?" p=0,41); altyazıya yanlış şey yazmamak için atıldı |
| IMG_2954 | 3,25–6,00 "Tabii ki bu merdivenleri." (görüntü: IMG_2907 merdivenler) | – |
| IMG_2954 | 6,82–7,45 "Ay…" + 7,94–8,66 "çok yorucu." | 7,45–7,94 boşluk (0,5 sn) kısaltıldı; 8,74 sonrası nefes ve gürültü |
| IMG_2973 | 0,20–2,76 "Karıştır, gülümse." | – |
| IMG_2945 (2. kayıt) | 2,105–9,00 "Yolu gösterirsen daha güzel bir görüntü olur aslında. Şöyle göstereyim sizlere." | 0–2,1: ilk kelime kesik ("…laklar ve kafeler…"); nefes (2,105–2,152) ve arka plandaki mırıltı (5,90–6,36) −30 dB'ye indirildi |
| Kullanılmayan konuşmalar | – | IMG_2945 1. kayıt ("Evet şimdi meydanın üst sokağından…"): "Evet şimdi" 2949 ile tekrar edeceği ve video uzayacağı için. 2972 "Çok açmışsın" iki kez tekrarlanıyor. 2968 ve 2971 düşük güvenle anlaşılıyor; bu çekimler müzik altında, altyazısız kullanıldı. 2906 (minare) sesinde arka planda telefon konuşması var; kapatıldı |

Bütün konuşma parçaları aynı seviyeye eşitlendi (−24 dB). Uzaktan gelen "Karıştır, gülümse" de duyulur.

## 2. Kesim kontrolü (`araclar/cutcheck.py`): GEÇTİ
- 6 kesim noktası (kesimin iki yanında 10 ms): −43,7 ile −86 dB arası → kesik hece yok. Baş −59,2 dB, son −62,0 dB.
- Whisper large-v3 ile yeniden transkripsiyon, beklenen metinle **TAM** eşleşme. Ardışık tekrar yok, düşük güvenli kelime yok.
- "Mardin neyle meşhur? Tabii ki bu…" / "Mardin'in neyi meşhur? Tabii ki bu…" bilinçli paralel şaka (soru-cevap esprisi). Araçta izinli ifade olarak tanımlandı; başka tekrar yok.
- İlk çalıştırmada "Şimdi" düşük güvenliydi (p=0,23). Başına 0,5 sn sessizlik eklenince p=0,86 → kelime sağlam; düşük güven, sesin dosyanın tam başında başlamasından kaynaklanıyordu. Ayrıntı: `araclar/cutcheck_sonuc.txt`

## 3. Saniye saniye
| Çıkış (sn) | Görüntü (kaynak) | Grafik | Altyazı (göğüs hizası) | Müzik | Efekt (ses/görüntü) |
|---|---|---|---|---|---|
| 0,0–1,5 | **KANCA:** MARDİN TÜRKİYE tabelası (3062), tabelaya yaklaşma | "GECE YÜRÜYÜŞÜ" | – | Büyük vuruş: darbuka düm, bas, ud akoru, ney düşüşü; darbuka rulosu | Beyaz flaş · derin vuruş |
| 1,5–6,25 | 2949: kameraya yürüyüşün | – | ŞİMDİ MARDİN · NEYLE MEŞHUR? · TABİİ Kİ BU · GÜZEL SOKAKLARIYLA. | Hafif ritim, bas, ud (ducking) | – |
| 6,25–12,25 | **SOKAKLAR montajı** (vuruşa kesim): fenerli sokak (F), Eski Şeyler sokağı (3082), sarı dar sokak (E), konak cephesi (F), minare (A) | 10,87 📍 ULU CAMİİ | – | **Ana tema:** bağlama benzeri tel + ney + darbuka (maksum) + el çırpma + zil + yaylı dolgu | Her kesimde zoom-punch ve whip (hareket bulanıklığı) geçişi + whoosh |
| 12,25–13,9 | 2954: koşarak gelişin | – | E BİR DE · MARDİN'İN NEYİ MEŞHUR? | Ritim alçak | – |
| 13,9–16,65 | **Merdivenler** (2907), ses 2954'ten devam | – | TABİİ Kİ BU · MERDİVENLERİ. | Ritim alçak | Zoom-punch |
| 16,65–18,0 | 2954: nefes nefese sen | – | AY · ÇOK YORUCU. | **Müzik bant gibi yavaşlayıp durur** (şaka), sessizlik | Bant durması sesi · yüzüne komik zoom |
| 18,0–21,0 | **Kediler:** beyaz-gri kedi ve sen (2954b), siyah kedi (3086), tekir (3078) | SOKAKLARIN GERÇEK SAHİPLERİ | – | Oyuncaklı pizzicato (kanun benzeri) + parmak şıklatma | Işık sızması · kodla üretilmiş "miyav" · zoom-punch |
| 21,0–23,5 | **Gizli kapı** gibi açılan kitaplık (2960) | GİZLİ KAPI?! (sallanarak) | – | Kafe teması başlar: kanun arpejleri, bendir | Işık sızması · sihirli parıltı |
| 23,5–29,5 | Kitap kafe: kitap duvarı (2957), çevirmeli telefon (2975), kemerli raflar (2986), çiçek (2974), kitap seçen sen (3038), okuyan sen (2980) | 📚 KİTAP KAFE | – | Sakin kafe teması, ney | Vuruşa zoom-punch |
| 29,5–32,06 | Çay karıştıran arkadaşın (2973) | – | KARIŞTIR, · GÜLÜMSE. | Alçak | – |
| 32,06–33,0 | Menüyle gülümsemen (2968) | – | – | | Zoom-punch |
| 33,0–34,5 | Kafe aynasında selfie (3060) | – | – | **Gerilim yükselir:** darbuka rulosu, kreşendo, ney tırmanışı | Whip · deklanşör sesi |
| 34,5–36,0 | **Aynalı Sokak** tabelası ve sen (3082) | 📍 AYNALI SOKAK | – | Yükseliş sürer | Whip |
| 36,0–38,3 | 2945: arkadaşın konuşuyor → kamera savrulur | – | YOLU · GÖSTERİRSEN · DAHA GÜZEL BİR | Kalp atışı gibi düm + yaylı gerilim + rulo | Yükselen gerilim + savrulma whoosh |
| 38,3–42,9 | **Sokak açılır** (2945) | 📍 ÇARŞIYA DOĞRU | GÖRÜNTÜ OLUR · ASLINDA. · ŞÖYLE GÖSTEREYİM · SİZLERE. | **Ana tema patlar** (konuşma altında alçak) | Beyaz flaş + açılış vuruşu + zoom |
| 42,9–44,5 | Nazar boncuklu ağaç (3088) | – | – | Ana tema (tam) | Işık sızması · zoom-punch |
| 44,5–46,0 | Aynada el sallaman (2987) | **GÖRÜŞÜRÜZ** | – | Ana tema | Whip · parıltı |
| 46,0–47,5 | Minare (2906) | **MARDİN · GECE YÜRÜYÜŞÜ** + 🔖 "Kaydet, gezerken lazım olur" | – | **Final vuruşu** + bağlama akoru + ney uzun nota | Flaş · son 0,4 sn karartma |

Her karede: hafif S-eğrisi kontrast, vinyet, çok hafif film greni. Konuşmasız planlarda yavaş yaklaşma ya da uzaklaşma var.

## 4. Yerleşim güvenliği (her karede otomatik kontrol)
- Yüz tespiti (YuNet): 22 çekim, eğik kamera için −80…+80° döndürülerek tarandı. Baş kutusu örtü/saç payıyla genişletildi ve ±3 kare birleştirildi. Tek karelik dev yanlış tespitler ayıklandı.
- Altyazı ve notlar, gösterildikleri sürenin tamamında hiçbir başa çarpmayan en yakın konuma yerleşiyor, gerekirse küçülüyor.
  - Uzaktan yürüdüğün 2949'da yüzün çok küçük; göğüs hizası yüze çok yakın düştüğü için altyazı başının biraz üstünde.
  - "ÇOK YORUCU." da aynı nedenle başının üstünde.
- Duvardaki portre tabloları da yüz sayıldı; üstlerine yazı gelmiyor.
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500) ve sağ buton şeridi (x>940) boş.
- 18 örnek karede yüz çakışması **0**, arayüz ihlali **0**. Tam çıkışta 1425 karenin hepsi kontrol edilip rapor edilecek.
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
  - MARDİN tabelası, Aynalı Sokak ve Eski Şeyler tabelaları çekimin içinde kendiliğinden görünüyor.
- Telifli müzik ya da ses: **yok**.
- Font: Inter / Inter Display (SIL Open Font License 1.1). İkonlar (konum, kitap, yer imi) kodla çizildi.
- **Ekranda rakam yok.** Önceki plandaki "1176" kartı, minare artık 1,5 sn'lik montaj planı olduğu için kaldırıldı.
- "ULU CAMİİ" etiketi: çekim GPS'i (37,3135 K, 40,7345 D; Mardin eski şehir) ve minarenin biçimi Mardin Ulu Camii minaresiyle uyumlu.
- "AYNALI SOKAK" etiketi sadece tabelanın göründüğü IMG_3082'de. Kafe aynası (3060) GPS'e göre ~500 m uzakta olduğu için etiketlenmedi.
