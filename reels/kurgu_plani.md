# Mikrofon Testi – Reels kurgu planı (onay bekliyor)

Kaynak: `IMG_2676.mov` (7,4 sn, 1080×1920, HDR/HLG → SDR ton eşleme, 30 fps çıkış)
Çıkış süresi: **3,50 sn**

## Kesim
| Kaynak | Karar | Neden |
|---|---|---|
| 0,00–2,50 | ✂️ atıldı | 0,5–1,4 sn mikrofon tutma/hışırtı sesi (konuşma değil) + 1,3 sn boşluk |
| 2,50–4,37 | ✅ tutuldu | "Ses 1 2 3" |
| 4,37–5,43 | ✂️ atıldı | 1,1 sn boşluk (kesimde ~0,26 sn doğal duraksama kaldı) |
| 5,43–7,07 | ✅ tutuldu | "Sesim geliyor mu?" + 0,35 sn nefes payı (anket kartı için) |
| 7,07–7,44 | ✂️ atıldı | sessiz kuyruk |

Hız değişikliği yok. Ses kesimlerinde 10 ms fade (tık sesi olmasın).

## Kesim kontrolü (cutcheck.py) — GEÇTİ
- Kesim noktası 1,867 sn: önce −82 dB / sonra −82 dB → kesik hece yok
- Baş −70 dB, son −85 dB → temiz
- Yeniden transkripsiyon (Whisper large-v3): `ses bir iki üç sesim geliyor mu` = beklenen metin, ardışık tekrar yok, düşük güvenli kelime yok

## Saniye saniye
| Çıkış (sn) | Görüntü | Başın üstü | Göğüs hizası (altyazı) | Ses efekti |
|---|---|---|---|---|
| 0,00 | "Ses…" başlıyor | 🎙 **MİKROFON TESTİ** başlığı pop ile girer | – | yumuşak pop |
| 0,12 | | + gerçek sesinden üretilen ses çubukları (spektrum) | **SES** | |
| 0,62 | | çubuklar sesle oynar | SES **1** | tık |
| 0,93 | | | SES 1 **2** | tık |
| 1,28 | | | SES 1 2 **3** | tık |
| 1,70–1,87 | jump cut | çubuklar söner | | whoosh (kesime) |
| 1,99 | "Sesim geliyor mu?" | başlık kalır | **SESİM** | |
| 2,46 | | | SESİM **GELİYOR** | |
| 2,76 | | | SESİM GELİYOR **MU?** | |
| 2,86–3,50 | | ✅ GELİYOR / ❌ GELMİYOR anket kartı | (satır kalır) | ding |

Aktif kelime sarı, önceki kelimeler beyaz; kelimeler ortalanır.

## Yerleşim güvenliği (render.py içinde her kare kontrol edildi)
- Yüz: YuNet yüz dedektörü, kare kare; kafa kutusu saç payıyla genişletildi → **105/105 karede grafik-yüz çakışması 0**
- Instagram arayüzü: üst 230 px, alt 420 px (y>1500), sağ buton şeridi (x>940) boş → **ihlal 0**
- Grafik alanı: y 237–472 (kafa üstü en yüksek 454… çakışmasız) ve y ~1385–1472 (çene en alt 1315)
- Kart / ekran görüntüsü / bölünmüş ekran: bu içerikte gerek yok, kullanılmadı.

## Ses
- Tüm efektler numpy ile sentezlendi (pop, tık, whoosh, ding) – telifli ses yok
- 80 Hz high-pass, miks → kazanç + true-peak limitör → hedef **−14 LUFS**, tepe ≤ −1,5 dBTP (test: −14,4 LUFS @ +14,3 dB; final ±0,1 LU'ya ayarlanacak)

## Haklar / doğrulama
- Dış görsel, logo, kişi görseli, meme, arşiv video: **yok**
- Font: Inter (SIL Open Font License 1.1)
- Ekrandaki rakamlar (1-2-3) sayma; olgusal veri değil → doğrulanacak istatistik yok
