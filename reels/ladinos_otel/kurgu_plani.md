# Ladinos Otel (Midyat) – Reels kurgu planı · ONAY BEKLİYOR

**Çıkış:** 1080×1920 dikey · 30 fps · **48,27 sn** · HDR (HLG/Dolby Vision) → SDR BT.709 ton eşleme
**Kaynak:** 32 klip (IMG_3746–3788) · kullanılan 20 klip, 21 segment
**Hız değişikliği yok** (konuşma da görüntü de 1×). Sadece boşluklar ve kamera arkası konuşmalar kesildi.

---

## 1. Ham çekimden neler atıldı

| Klip | Ne var | Karar |
|---|---|---|
| 3748 | "5 saniye falan alıyorum zaten. Bunları ara araya ekliyorum." | ✂️ kamera arkası konuşma, atıldı |
| 3756 0,0–2,1 sn | "Sen bana odaları anlatıyor musun?" | ✂️ hazırlık cümlesi, atıldı (**bkz. Soru 3**) |
| 3756 2,37–2,60 / 3,10–3,70 | "Ben … bir … iki gün" arasındaki 0,23 sn + 0,60 sn duraksama | ✂️ kısaltıldı, ~0,1 sn doğal nefes payı kaldı |
| 3756 7,63 sn sonrası, 3759 | Görevlinin cevabı | Mikrofona çok uzak (~−40 dB). Whisper bunu konuşma olarak bile algılamıyor. **Altyazı yok, söz uydurulmadı**; ses kısık ortam olarak kaldı. |
| 3762 1,9 sn sonrası | "tamam kısa kes bitti" | ✂️ kamera arkası, atıldı |
| 3763 0,0–0,7 sn | "Evet," (klip başında yarım başlıyor) | ✂️ kesik hece riski, atıldı |
| 3751, 3758 | Sonda "Tamam." | ✂️ (3751, 3758 kullanılmadı) |
| 3784 0,7–2,1 sn | Anlaşılmayan kısa ses | ✂️ |
| 3747, 3749, 3751, 3768, 3769, 3773, 3776, 3785, 3786 | Tekrar niteliğinde B-roll | kullanılmadı (süre için) |
| 3758 | "Bizi değerlendirin" standı (QR + platform logoları) | kullanılmadı (logo kuralı, **bkz. Soru 2**) |
| `1f70a829-IMG_3759` | `419d6a52-IMG_3759`'un kırpılmış kopyası (ses profili birebir aynı) | yinelenen dosya, kullanılmadı |

Klip sonlarında kalan "Altyazı M.K." / "İzlediğiniz için teşekkür ederim" metinleri gerçek konuşma değil. Whisper sessizlikte bu metinleri uyduruyor (bilinen halüsinasyon).

## 2. Kesim kontrolü (`araclar/cutcheck2.py`) — **GEÇTİ**

1. **Kaynak VAD sınır testi:** 21 segmentin hiçbir giriş/çıkış noktası konuşmayı bölmüyor. 4 sınır VAD'ın birleşik bölgesinde ama o noktada seviye −51…−67 dB (sessiz).
2. **Diyalog kesim noktaları:** 8 noktanın hepsi ±40 ms içinde −45 dB'in altında. İlk çalıştırmada 2 kesik bulundu ("bulduk"un sonu ve "bir"in sönümü 10–30 ms kırpılıyordu); bunlar düzeltildi.
3. **Yeniden transkripsiyon (Whisper large-v3):**
   `merhaba kolay gelsin hoş bulduk ben bir iki gün midyatta kalacağım nasıl bir oda öneriyorsunuz şans odası teşekkürler`
   Beklenen metinle **birebir eşleşiyor**, ardışık tekrar yok.
4. **B-roll ortam sesi dahil tam stem:** Fazladan konuşma parçası **yok**.

Tam çıktı: `onizleme/kesim_kontrolu.log`

## 3. Saniye saniye

| Çıkış (sn) | Kaynak | Görüntü | Başın üstü / üst bant | Göğüs hizası (altyazı) | Ses |
|---|---|---|---|---|---|
| 0,00–2,20 | 3746 0,40–2,60 | Gece, ışıklı otel cephesi | 0,10: **MİDYAT'TA / OTEL TURU** (sarı kart) · 0,40: 📍 *Ladinos Otel · Midyat* etiketi | – | müzik girişi, pop, tık |
| 2,20–5,50 | 3750 1,40–4,70 | Merdivenden çıkıp içeri girişin (arkadan) | başlık 3,90'da söner | – | müzik |
| 5,50–8,00 | 3754 2,20–4,70 | Cam kapıdan kameraya yürüyüş | (boş, yüz serbest) | – | müzik + ritim |
| 8,00–11,20 | 3755 1,60–4,80 | Resepsiyona yürüyüş | 8,10: *Resepsiyon* etiketi | 8,28 MERHABA, · 8,57 KOLAY · 8,77 GELSİN. · 10,31 HOŞ · 10,49 BULDUK. | müzik 11 dB kısılır, tık |
| 11,20–11,97 | 3756 2,10–3,10 | Resepsiyon tezgâhı (jump cut 1,00→1,07× zoom) | – | 11,26 BEN · 11,59 BİR | |
| 11,97–15,90 | 3756 3,70–7,63 | aynı, 1,15× punch-in (duraksama kesimini gizler) | – | 12,13 İKİ · 12,41 GÜN → 12,59 MİDYAT'TA · 12,97 KALACAĞIM. → 14,11 NASIL · 14,29 BİR · 14,47 ODA → 14,82 ÖNERİYORSUNUZ? | |
| 15,90–19,00 | 3759 0,50–3,60 | Görevli el hareketleriyle anlatıyor | 16,05: *Oda önerisini dinliyoruz* | (yok, ses anlaşılmıyor) | ortam −9 dB, müzik |
| 19,00–20,87 | 3762 0,00–1,87 | Koridor | – | – | müzik |
| 20,87–22,87 | 3763 1,30–3,30 | Kapıyı gösteriyorsun (tabela: "101 Şans Odası") | – | 21,40 ŞANS · 21,61 ODASI. | |
| 22,87–25,20 | 3764 0,60–2,93 | Görevli kapıyı açıyor | – | 23,78 TEŞEKKÜRLER. | |
| 25,20–27,20 | 3765 0,30–2,30 | Oymalı paravan, odaya giriş | – | – | müzik |
| 27,20–29,90 | 3766 0,30–3,00 | Oda geneli | 27,25: **ODA** bölüm başlığı | – | whoosh + pop |
| 29,90–32,40 | 3767 0,40–2,90 | Yatak başı, havlu düzeni | – | – | |
| 32,40–34,20 | 3771 0,20–2,00 | Dümen avize | – | – | |
| 34,20–37,00 | 3770 0,30–3,10 | Perde açılıyor → gece sokak | 35,20: *Pencereden gece manzarası* | – | tık |
| 37,00–40,00 | 3772 1,50–4,50 | Banyo kapısı açılıyor | 37,05: **BANYO** bölüm başlığı | – | whoosh + pop |
| 40,00–42,00 | **Bölünmüş ekran**: üst 3774 0,60–2,60 / alt 3775 0,20–2,20 | Yağmur duşu / fön makinesi | üst: *Yağmur duşu* · alt: *Saç kurutma makinesi* | – | swish, 2 tık |
| 42,00–45,00 | 3787 0,20–3,20 | Diğer oda (kanepe, TV, kapı, yataklar) | – | – | |
| 45,00–46,70 | 3788 2,10–3,80 | Kabartmalı duvar | – | 45,20: **Midyat'a gidecek birine gönder** (CTA etiketi) | ding |
| 46,70–48,27 | 3784 2,13–3,70 | Ayna selfien (kapanış) | – | CTA çenenin altında kalır | müzik 1,2 sn fade-out |

Altyazılar kelime kelime çıkar; aktif kelime sarı, önceki kelimeler beyaz, siyah konturlu. "midyatta" ekranda **MİDYAT'TA** olarak yazılır (yalnızca yazım düzeltmesi).

## 4. Yerleşim güvenliği (`araclar/overlay.py check`) — **GEÇTİ (1448/1448 kare)**

- **Yüz/kafa:** YuNet ile kare kare yüz tespiti yapıldı. Kutu, şal/saç için üstten %55, yanlardan %30 genişletildi; zoom'lu planlarda kutu da dönüştürüldü. **Grafik ile kafa çakışması 0.**
  - İlk denemede kapanış CTA'sı selfiedeki yüze biniyordu (9 kare). CTA tek satıra küçültülüp çene altına (y≈1405) alındı.
- **Instagram arayüzü:** Üst 230 px, alt 420 px (y>1500) ve sağ buton şeridi (x>940) boş. **İhlal 0.** Grafikler y 236–1472, x 65–914 aralığında.
  - İlk denemede tek satırlık başlık sağ şeride taşıyordu (171 kare). İki satıra bölündü, tüm öğeler x=490'a ortalandı.
- **Bölünmüş ekran:** Duş ve fön kliplerinde insan yok, kesilen baş yok. Ayırıcı çizgi videonun parçası.
- **Kart:** Açılıştaki konum etiketi. **Ekran görüntüsü:** gerek görülmedi, kullanılmadı.

## 5. Ses

- **Müzik:** 96 BPM La minör altlık (pad, bas, arpej, yumuşak kick/shaker). Tamamı numpy ile sentezlendi; sample, loop ya da telifli ses yok.
- **Efektler:** pop, tık, whoosh, swish, ding. Hepsi kodla sentezlendi.
- **Diyalog:** −16 LUFS'e çekildi, 80 Hz high-pass. Konuşma sırasında müzik 11 dB kısılıyor (250 ms yumuşak geçiş). B-roll ortam sesi −16 dB.
- **Final:** **−14,0 LUFS** entegre (ffmpeg ebur128 ile doğrulandı) · true-peak **−1,4 dBTP** · LRA 6,5 LU.

## 6. Haklar, lisanslar, doğrulama

- **Dış görsel, logo, meme, arşiv video, gerçek kişi görseli eklenmedi.** Ekrandaki her şey senin çekimin ve kodla çizilmiş grafikler (konum ikonu dahil).
- **Font:** Inter / Inter Display (Rasmus Andersson). Lisans: SIL Open Font License 1.1, ticari kullanım serbest.
- **Müzik ve efektler:** Bu projede kodla üretildi, harici kaynak yok.
- **Yüz tespiti modeli (yalnız analiz, videoda görünmez):** OpenCV Zoo YuNet. Lisans: MIT.
- **Transkripsiyon (yalnız analiz):** Whisper large-v3, MIT lisansı (faster-whisper, MIT).
- **Rakamlar:** Ekranda grafik olarak rakam yok. "bir iki gün" senin sözün, yazıyla gösteriliyor. Tabeladaki "101" grafik olarak kullanılmadı. Doğrulanması gereken bir istatistik yok.

## 7. Onayından önce cevaplaman gerekenler

1. **"Merhaba, kolay gelsin":** İlk kelime kısa ve hızlı. Bağlamla birlikte çözümlemede 16 denemenin 10'unda "Merhaba" çıktı. Tek başına bırakılınca bazen "Eyvah" çıkıyor. "Merhaba" doğru mu?
2. **Görünen kişiler ve tabela:** Resepsiyon görevlisi ve kapıyı açan görevli kadrajda (s04, s07, s08, s11). Konum etiketinde ve görüntüde otelin adı "Ladinos Otel" geçiyor. Görevlilerin görünmesine ve otel adının yazılmasına izin var mı? Ayrıca 3758'deki QR/değerlendirme standını ister misin? (Şu an çıkarıldı.)
3. **"Sen bana odaları anlatıyor musun?"** cümlesi atıldı. Kalsın mı?
4. **Müzik** kodla üretilmiş altlık. Müzik istemezsen yalnız ortam sesi ve efektlerle bırakırım.
5. **Eksik numaralar:** 3752–53, 3757, 3760–61, 3777–83 yok. Yüklenecek başka klip var mı?
