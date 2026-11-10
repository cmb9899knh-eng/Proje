# Mardin vlog – Reels kurgu planı (ONAY BEKLİYOR)

Kaynak: 16 klip (IMG_3148 … IMG_3297), toplam 89,6 sn ham, dikey HDR/HLG → SDR ton eşleme, 1080×1920, 30 fps
Çıkış süresi: **38,27 sn**. Hız değişikliği yok, konuşma hızlandırılmadı.

## 1. Kesim kararları

| Klip | Ham | Karar | Neden |
|---|---|---|---|
| 3148 | 6,5 sn | 3,30–5,80 tutuldu | Şehir manzarası (açılış). 0–3 sn arabalı/sallantılı. Ses yok, sadece rüzgâr |
| 3160 | 9,3 sn | 1,00–4,50 + 6,03–7,80 | "Evet şimdi … Cafe'nin girişindeyiz" + "Bakalım nasıl bir yer çıkacak". Baştaki 1 sn yürüyüş, aradaki **1,5 sn boşluk** ve sondaki 1,5 sn atıldı. "Cafe'nin — girişindeyiz" arasındaki 0,4 sn duraklama bir düzeltme değil (ayrı dinletildi), doğal kaldı |
| 3166 | 6,8 sn | 2,00–3,60 | Kahvenin dökülmesi |
| 3170 | 5,3 sn | 0,20–1,70 | Kafeye yürüyüş |
| 3178 | 2,4 sn | 0,10–1,40 | İki içecek |
| 3161 | 2,5 sn | 0,30–1,50 | Arkadaş cam önünde |
| 3191 | 5,6 sn | 3,00–4,60 | Arkadaşla selfie |
| 3234 | 5,4 sn | 0,50–2,50 | Kahve yudumu |
| 3287 | 6,5 sn | 0,20–2,00 | "Mardin Hatırası" aynası |
| 3288 + 3292 | 2,4 + 2,5 sn | 0,20–1,90 (ikisi yan yana) | **Bölünmüş ekran**: tespihler / şallar |
| 3289 | 3,5 sn | 0,50–1,90 | Asılı puşiler, çarşı |
| 3291 | 5,0 sn | 0,30–2,30 | Minare. Sondaki **yarım cümle "Ben sanırım…" atıldı** |
| 3295 | 6,9 sn | 0,10–4,67 + 5,37–6,83 | "Şu an sanırım çarşıda geziyoruz." → (arkadaşın) "Evet, meydandayız arkadaşlar." → "Çok güzel yerler var." Aradaki **0,7 sn boşluk** atıldı. *Not:* "meydandayız" cümlesini kamera ona dönükken arkadaşın söylüyor (ağzı oynuyor), yani bu bir tekrar değil, karşılıklı konuşma. İkisi de kaldı |
| 3296 | 6,6 sn | 0,40–1,37 + 2,20–4,23 | "Şu anda … meydanın ilerisindeyiz". Cümle ortasındaki **0,85 sn boşluk** atıldı. Sondaki "Bu şekilde" atıldı: klip son hecede bitiyor (kesik hece riski) ve dolgu ifadesi |
| 3297 | 7,4 sn | 1,10–3,90 + 4,73–7,30 | "Mardin'in meşhur badem şekerleri." + "Nereden geçerseniz ikram ediliyor." Aradaki 0,8 sn boşluk atıldı |

Sessiz kliplerde Whisper'ın uydurduğu "Altyazı M.K." ve "İzlediğiniz için teşekkür ederim" gibi metinler gerçek konuşma değil (seviye −45…−65 dB, ortam sesi). Bu yüzden hiçbiri altyazıya girmedi.

## 2. Kesim kontrolü (`araclar/cutcheck2.py`): GEÇTİ
- 8 konuşma bölümünün 16 kenarı: −47,3 … −64,2 dB (eşik −45 dB) → **kesik hece yok**
- Birleşik konuşma izi Whisper large-v3 ile yeniden yazıya döküldü:
  `evet şimdi nevada kafenin girişindeyiz bakalım nasıl bir yer çıkacak şu an sanırım çarşıda geziyoruz evet meydandayız arkadaşlar çok güzel yerler var şu anda meydanın ilerisindeyiz mardinin meşhur badem şekerleri nereden geçerseniz ikram ediliyor`
- Ardışık kelime tekrarı yok, 2–4 kelimelik ifade tekrarı yok, güveni 0,50'nin altında kelime yok
- Beklenen metinle tek fark: kafe adı (aşağıdaki soru 1)

## 3. Saniye saniye

Altyazı: göğüs hizasında, kelime kelime. Söylenen kelime sarı ve "pop" ile girer, önceki kelimeler beyaz kalır. Satır başına en fazla 2 kelime.

| Çıkış (sn) | Görüntü | Başın üstü / grafik | Göğüs hizası (altyazı) | Ses efekti |
|---|---|---|---|---|
| 0,00–2,50 | 3148 Mardin manzarası | **MARDİN** + 📍 "gezi günlüğü" (gökyüzünde) | – | parıltı (shimmer) |
| 2,50 | ↘ 3160 kafe girişi | | | whoosh |
| 2,62–5,95 | | ☕ **KAFE DURAĞI** rozeti (başın üstü) | 2,67 EVET ŞİMDİ · 3,73 NEVADA CAFE'NİN · 4,89 GİRİŞİNDEYİZ | pop |
| 6,00–7,77 | 3160 (arkadaşla) | – | 6,24 BAKALIM NASIL · 6,88 BİR YER · 7,24 ÇIKACAK | |
| 7,77–9,37 | 3166 kahve dökülüyor | boş (ara görüntü, ortam sesi) | – | |
| 9,37–10,87 | 3170 kafeye yürüyüş | boş | – | |
| 10,87–12,17 | 3178 iki içecek | boş | – | |
| 12,17–13,37 | 3161 arkadaş cam önünde | boş | – | |
| 13,37–14,97 | 3191 selfie | boş | – | |
| 14,97–16,97 | 3234 kahve yudumu | boş | – | |
| 16,97–18,77 | 3287 "Mardin Hatırası" | 🛍 **ÇARŞI** rozeti (17,05–23,80) | – | pop |
| 18,77–20,47 | **Bölünmüş ekran** 3288 \| 3292 (yarılar üstten/alttan kayarak girer) | "TESPİH" / "ŞAL" etiketleri + ÇARŞI | – | whoosh giriş/çıkış + 2 tık |
| 20,47–21,87 | 3289 puşiler | ÇARŞI | – | |
| 21,87–23,87 | 3291 minare | ÇARŞI (biter). Minare etiketi yok (soru 2) | – | |
| 23,87–28,43 | 3295 sen → arkadaşın | – (yakın çekim, başın üstünde yer yok) | 24,16 ŞU AN · 25,18 SANIRIM ÇARŞIDA · 26,20 GEZİYORUZ · 26,82 EVET · 27,40 MEYDANDAYIZ · 28,24 ARKADAŞLAR | |
| 28,43–29,90 | 3295 sen | – | 28,55 ÇOK GÜZEL · 29,39 YERLER VAR | |
| 29,90–32,90 | 3296 meydan sokağı | 📍 **MEYDAN** rozeti (29,95–32,85) | 30,02 ŞU ANDA · 31,05 MEYDANIN · 32,17 İLERİSİNDEYİZ | pop |
| 32,90–38,27 | 3297 badem şekeri tepsisi / satıcı | 🍬 **BADEM ŞEKERİ** rozeti (satıcının başından uzakta, sol üst) | 33,19 MARDİN'İN · 34,41 MEŞHUR BADEM · 35,31 ŞEKERLERİ · 35,75 NEREDEN · 36,65 GEÇERSENİZ · 37,25 İKRAM EDİLİYOR | pop |

Kart / ekran görüntüsü: bu içerikte bilgi kartı gerektiren bir veri ya da anlatılan bir uygulama/site yok, o yüzden kullanılmadı. Rozetler kart görevi görüyor. Ara görüntüler (7,8–17 sn) bilerek boş bırakıldı ("her yeri doldurma").

Kelime zamanları şu an Whisper + enerji hizalamasıyla ±0,15 sn hassasiyetinde. Tam render'dan önce zorunlu hizalamayla (wav2vec2 CTC) kare doğruluğuna getirilecek.

## 4. Yerleşim güvenliği (`araclar/render.py`, her karede kontrol)
- Yüz: YuNet dedektörü, 16 klipte kare kare. Kutu başörtüsü/saç ve çene payıyla genişletildi. Tek karelik yanlış algılamalar (ör. eldeki mikrofon/bardak) zamansal tutarlılıkla elendi. Uzaktaki yayaların yüzleri de korunuyor
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500), sağ buton şeridi (x>940) boş
- Grafik–grafik çakışması da kontrol ediliyor (rozet ↔ altyazı)
- Bölünmüş ekranda baş yok (iki yarı da ürün çekimi), yani baş kesilmesi söz konusu değil
- 12 örnek karede: **yüz ihlali 0, arayüz ihlali 0, grafik çakışması 0**. Tam render'da 1148 karenin hepsi aynı kontrolden geçecek
- Başın üstünde yer kalmayan yakın çekimlerde (3295) rozet konmadı. "Yüze binmesin" kuralı önceliklidir

## 5. Ses
- Konuşma: kaynak seviyesi, 80 Hz high-pass, kesimlerde 12 ms fade (tık yok)
- Ara görüntüler: kendi doğal ortam sesi −12 dB, 40 ms geçişler
- SFX: pop, whoosh, shimmer, tık. Hepsi numpy ile sentezlendi, telifli ses yok
- Fon müziği (öneri, soru 3): kodla üretilmiş 92 BPM yumuşak lo-fi (Am7–Fmaj7–Cmaj7–G7, sinüs piyano + bas + yumuşak kick/hat). Konuşma altında otomatik kısılıyor
- Ses seviyesi: kazanç + 4× örneklemeli tepe sınırlayıcı → test miksi **−14,1 LUFS, gerçek tepe −2,3 dBTP**. Final ±0,1 LU'ya ayarlanacak

## 6. Haklar / doğrulama
- Eklenen dış görsel, logo, kişi görseli, meme, arşiv video: **yok**
- Font: Inter / Inter Display (SIL Open Font License 1.1)
- İkonlar (pin, fincan, çanta, şeker): kodla çizildi
- Ekranda gösterilen rakam: **yok**, doğrulanacak istatistik yok
- Araçlar (içerik değil): Whisper large-v3 (MIT), YuNet (OpenCV Zoo, MIT), ffmpeg

## 7. Onay için sorular
1. **Kafe adı:** Sesten "Nevada Cafe" çıkıyor ama net değil (diğer okumalar: "Levada", "Levat"). İnternette Mardin'de bu adla bir kafe doğrulayamadım. Doğru adı ve yazımı nedir?
2. **Minare (3291):** Mardin Ulu Camii minaresine benziyor. Yer etiketi koyayım mı? Kaynaklar minarenin yapım tarihinde çelişiyor (1176 kitabesi / 16. yy / 1888-89 yenileme), bu yüzden tarih yazmayacağım
3. **Fon müziği:** Kodla ürettiğim lo-fi altlık olsun mu, yoksa sadece ortam sesi + efekt mi?
4. **3292'deki dükkân telefon numarası:** Bölünmüş ekranın sağ üstünde bir dükkân tabelasındaki telefon numarası görünüyor. Bulanıklaştırayım mı?
5. Videoda arkadaşın ve badem şekeri satıcısı yüzleriyle görünüyor. Kendi çekimin olduğu için ekleme yapmadım, ama paylaşım izinlerini senin teyit etmen gerekiyor
