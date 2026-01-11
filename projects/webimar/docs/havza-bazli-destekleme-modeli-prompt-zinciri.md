# Havza Bazlı Destekleme Modeli Prompt Zinciri

## Genel Amaç
Yeni bir Next.js sayfası yaratacağız. Bu sayfa, havza bazlı destekleme modeli hesaplaması için kullanılacak. Sayfa mobil uyumlu olacak ve aşağıdaki bileşenleri içerecek:
- Ürün seçimi (2026 destek fiyatları listesinden, birden fazla ürün + dekar girişi)
- Ürün destek bölgeleri haritası (eğlenceli, interaktif, renk navigasyonu ile)
- Genç çiftçi checkbox (41 yaş altı)
- Kadın çiftçi checkbox
- Birinci derece tarımsal örgüt üyeliği checkbox ve "hangileri" butonu ile liste gösterimi
- Üretimi geliştirme desteği seçenekleri (A, B, C, D)
- İl/ilçe seçimi (harita üzerinden veya input ile, en son adım)

## Prompt 1: Sayfa Yapısı ve Temel Bileşenler
```
Yeni bir Next.js sayfası yarat: `/havza-bazli-destekleme-modeli`

Sayfa yapısı:
- Styled-components kullan
- Ana container: flex column, max-width 1200px, margin auto
- Başlık: "Havza Bazlı Destekleme Modeli"
- Form bölümü: padding 20px, border, border-radius

İlk olarak sadece temel yapıyı yarat, diğer bileşenleri sonraki prompt'larda ekleyeceğiz.
```

## Prompt 2: Ürün Seçimi Bileşeni
```
Ürün seçimi bileşeni ekle.

Veri kaynağı: `/2026-uretim-yili-bitkisel-uretim-destek-fiyatlari-listeden.md`

Bileşen:
- Ürün ekleme sistemi: + butonu ile birden fazla ürün satırı ekleyebilme
- Her ürün satırı için:
  - Dropdown: Ürün seçimi (kategorilere göre grupla)
  - Input: Dekar miktarı (sayı, zorunlu)
  - Silme butonu (x) - birden fazla satır varsa
- Ürünler:
  - Birinci grup yem bitkileri: fiğ, burçak, mürdümük, hayvan pancarı, yem şalgamı, yem bezelyesi, yem baklası, üçgül, italyan çimi, yulaf, çavdar, tritikale ve silajları
  - İkinci grup yem bitkileri: yonca, korunga, yapay çayır mera, silajlık mısır, silajlık soya, sorgum otu, sudan otu, sorgum-sudan melezi
  - Diğer ürünler: Aspir, Mercimek, Nohut, Patates, Soğan, Arpa, Buğday, Mısır, Ayçiçeği, Fındık, Kolza, Fasulye, Soya, Çay, Çeltik, Pamuk

Seçilen ürünleri state'te array olarak tut: [{ urun: string, dekar: number }, ...]
```

## Prompt 3: Ürün Destek Bölgeleri Haritası
```
Ürün destek bölgeleri haritası bileşeni ekle (eğlenceli, interaktif özellik).

Bileşen özellikleri:
- Harita: Türkiye ilçe haritası, her ürün için farklı renk kodlaması
- Renk navigasyonu: Seçilen ürünler için renk açıklaması (legend)
- Dinamik boyama: Kullanıcı ürün seçtikçe harita gerçek zamanlı güncellenir
- İlçe hover/click: İlçe üzerine gelince desteklenen ürünler gösterilir
- Eğlenceli tasarım: Animasyonlar, geçiş efektleri ile kullanıcıyı cezbeden yapı
- Veri kaynağı: İl/ilçe bazlı ürün destek bilgileri (hangi ilçelerde hangi ürünler desteklenir)

Örnek: Kullanıcı "arpa" seçerse, arpa desteklenen ilçeler mavi renkte boyanır, "buğday" seçerse yeşil, vs.
Harita mevcut arıcılık-planlama haritasından esinlenerek yaratılır ama ürün destek bölgelerine odaklanır.
```

## Prompt 4: Yaş ve Cinsiyet Checkbox'ları
```
Yaş ve cinsiyet seçimi ekle:

- Genç çiftçi checkbox: "41 yaş altı genç çiftçi miyim?" (true/false)
- Kadın çiftçi checkbox: "Kadın çiftçi miyim?" (true/false)

Bu değerleri state'te boolean olarak tut.
```

## Prompt 4: Örgüt Üyeliği Bileşeni
```
Birinci derece tarımsal örgüt üyeliği bileşeni ekle.

Veri kaynağı: `/2025_birinci_derece_tarimsal_orgut_listesi(1)`

Bileşen:
- Checkbox: "Birinci derece tarımsal örgüt üyesi miyim?"
- Checkbox yanında "hangileri" butonu: Tıklayınca tüm örgüt listesini modal/popup'ta göster
- Liste formatı: "İl - İlçe - Örgüt Adı" (alfabetik sıralı)
- İl/ilçe seçildikten sonra ilgili örgütleri filtrele (şimdilik tüm liste gösterilir)

Seçilen örgütü state'te tut.
```

## Prompt 6: Üretimi Geliştirme Desteği Seçenekleri
```
Üretimi geliştirme desteği seçenekleri bileşeni ekle.

Veri kaynağı: `/2026-uretim-yili-bitkisel-uretim-destek-fiyatlari-listeden.md` (Üretimi Geliştirme Desteği bölümü)

Bileşen:
- A - Sertifikalı tohum kullanım desteği: Checkbox ile seçilebilir
- B - Organik Tarım Desteği: Checkbox ile seçilebilir (Bireysel/Grup seçimi ile)
- C - İyi Tarım Uygulamaları Desteği: Checkbox ile seçilebilir, seçildiğinde alt menü açılır (Üretim tipi: Örtüaltı/Kapalı ortam, Açıkta; Sertifikasyon türü: Bireysel/Grup)
- D - Katı Organik/Organomineral Gübre Desteği: Checkbox ile seçilebilir

Seçilen seçenekleri state'te object olarak tut: { sertifikaliTohum: boolean, organikTarim: { secili: boolean, tur: 'bireysel'|'grup' }, iyiTarim: { secili: boolean, uretimTipi: string, sertifikaTuru: string }, guBre: boolean }
```

## Prompt 7: İl/İlçe Seçimi Bileşeni
```
Havza-bazli-destekleme-modeli sayfasına il/ilçe seçimi bileşeni ekle (en son adım).

Bileşen özellikleri:
- Harita gösterimi: Arıcılık-planlama sayfasındaki gibi ilçeleri gösteren harita (opsiyonel, kullanıcı isterse kullanabilir)
- Input alanları: İl ve İlçe için ayrı text input'lar (alternatif seçim yöntemi)
- Harita tıklamasıyla veya input girişiyle seçim yapılabilmeli
- Seçilen il/ilçe state'te tutulmalı

Harita bileşenini mevcut arıcılık-planlama sayfasından kopyala/adapte et.
```

## Prompt 8: Form Validasyonu ve API Entegrasyonu
```
Form validasyonu ekle:
- İl/ilçe seçimi zorunlu (harita üzerinden veya input ile)
- En az bir ürün-dekar kombinasyonu zorunlu (dekar > 0)
- Diğer alanlar opsiyonel

API endpoint'i hazırla: `/api/havza-bazli-destekleme-modeli`
- POST request
- Body: { il, ilce, urunler: [{ urun: string, dekar: number }, ...], gencCiftci: boolean, kadinCiftci: boolean, orgut: string, uretimGelisme: { sertifikaliTohum: boolean, organikTarim: { secili: boolean, tur: string }, iyiTarim: { secili: boolean, uretimTipi: string, sertifikaTuru: string }, guBre: boolean } }

Hesaplama mantığını backend'de implement et (Django API):
- Temel destek: 310 TL/da (sabit)
- Diğer destekler: Temel destek * destek katsayısı
- Destek katsayıları 2026 listesine göre belirlenir
- Genç/Kadın çiftçi ilaveleri: 3 katsayısı ile çarpılır
- Süt havzaları ilave desteği: Amasya, Bingöl, Bitlis, Çorum, Elâzığ, Erzincan, Erzurum, Muş, Tokat, Tunceli illerinde yem bitkisi üretenlere planlı üretim desteğinin %50'si kadar ilave
- Su kısıtı desteği: `/su kısıtı olan ilçeler.txt` dosyasındaki 52 ilçe/havzada sulu tarım yapanlara ilave (Aspir, Fiğ, Mercimek, Nohut, Yem bezelyesi: 0.8×310=248 TL/da; Arpa, Buğday: 1.4×310=434 TL/da; Ayçiçeği: 1.2×310=372 TL/da)
- Su kısıtı kısıtlaması: Su kısıtı bölgelerinde mısır (dane) ve patates için temel, planlı üretim ve üretimi geliştirme desteği verilmez
- Üretimi geliştirme destekleri: Seçilen A, B, C, D seçeneklerine göre ilave destekler hesaplanır- Organik tarım ilave desteği: 1. derece tarımsal örgüt üyesi organik tarım yapan çiftçilere ürün grubuna göre bireysel/grup destek katsayısının %25'i kadar ilave- İlave destekler (su kısıtı, organik tarım vb.) hesaplanır
- Toplam destek = (temel + diğer destekler + ilaveler) * dekar
```

## Prompt 9: UI/UX İyileştirmeleri
```
UI iyileştirmeleri:
- Mobil uyumlu responsive design (öncelikli)
- Harita bileşeni mobil cihazlarda dokunmatik kullanım için optimize edilsin
- Form elemanları mobil için uygun boyutlarda (büyük butonlar, kolay tıklanabilir checkbox'lar)
- Ürün destek haritası için eğlenceli animasyonlar ve geçiş efektleri
- Loading states
- Error handling
- Form reset butonu
- Sonuç gösterimi bölümü ekle (hesaplama sonrası)

Styling'i mevcut proje standartlarına göre tutarlı yap.
```

## Ek Notlar
- Tüm bileşenler TypeScript kullan
- State management için React hooks kullan (Redux yok)
- API çağrıları için Axios kullan
- Mobil uyumlu tasarım (responsive, touch-friendly)
- Ürün destek bölgeleri haritası: Eğlenceli, interaktif, renk navigasyonu ile kullanıcıyı sayfada tutan özellik
- Test dosyaları ekle
- Validation sonrası build/test çalıştır
- Hesaplama mantığı: Temel destek 310 TL/da sabit, diğer destekler katsayı ile çarpılır (gelecekte temel destek değişince otomatik güncellenir)
- Süt havzaları: Belirtilen 10 ilde yem bitkisi üretenlere %50 ilave planlı üretim desteği
- Su kısıtı: 52 ilçe/havzada sulu tarım yapanlara ürün kategorisine göre ilave destek (0.8-1.4 katsayısı)
- Su kısıtı kısıtlaması: Su kısıtı bölgelerinde mısır (dane) ve patates için hiçbir destek verilmez
- Organik tarım ilave: 1. derece örgüt üyesi organik tarım yapanlara %25 ilave destek

## Prompt 10: Üretimi Geliştirme Desteği Seçenekleri
```
Üretimi geliştirme desteği seçeneklerini ekle (ürün seçiminden sonra, il/ilçe seçiminden önce).

Bileşen:
- Ana checkbox: "Üretimi Geliştirme Desteği Alıyorum"
- Alt menüler (ana checkbox seçilince açılır):
  - Sertifikalı Tohum Kullanım Desteği checkbox
  - Organik Tarım Desteği checkbox (alt menü: Bireysel/Grup sertifikası seçimi)
  - İyi Tarım Uygulamaları Desteği checkbox (alt menü: Üretim tipi seçimi - Birinci grup için Örtüaltı/Açıkta, diğer gruplar için sadece Bireysel/Grup)
  - KATI ORGANİK / ORGANOMİNERAL GÜBRE DESTEĞİ checkbox

Her seçenek için:
- Sertifikalı Tohum: Ürün bazlı destek (2026 listesine göre)
- Organik Tarım: Ürün grubu + sertifika türü seçimi (Bireysel/Grup)
- İyi Tarım: Ürün grubu + üretim tipi (gerektiğinde) + sertifika türü (Bireysel/Grup)
- Gübre: Basit checkbox (ürün bağımsız)

Seçilen değerleri state'te object olarak tut: 
{
  uretimiGelistirme: boolean,
  sertifikaliTohum: boolean,
  organikTarim: { secili: boolean, tur: 'bireysel' | 'grup' },
  iyiTarim: { secili: boolean, uretimTipi: 'ortualti' | 'ackta' | null, sertifikaTur: 'bireysel' | 'grup' },
  katıOrganikGubre: boolean
}
```

## Prompt 11: Hesaplama Mantığı Güncellemesi
```
Hesaplama mantığını güncelle (Django API):

Temel hesaplamalar:
- Temel Destek: 310 TL/da (tüm ürünler için)
- Planlı Üretim Desteği: Kategori bazlı (temel destek * katsayı)
- Genç/Kadın Çiftçi İlavesi: 3 katsayısı ile çarpılır
- Süt Havzası İlavesi: Yem bitkileri için %50 ilave
- Su Kısıtı Desteği: Belirtilen ilçelerde ilave

Üretimi Geliştirme Destekleri:
- Sertifikalı Tohum: Ürün bazlı sabit destekler
- Organik Tarım: Ürün grubu + sertifika türüne göre
  - İlave: 1. derece örgüt üyesi ise %25 ilave
- İyi Tarım: Ürün grubu + üretim tipi + sertifika türüne göre
- Gübre: 99,2 TL/da sabit

Toplam Destek = (Temel + Planlı + İlave Destekler) * Dekar + Üretimi Geliştirme Destekleri

API Response formatı:
{
  "uygun": true,
  "mesaj": "Hesaplama başarılı",
  "detaylar": {
    "temel_destek": 310,
    "planli_uretim": 403,
    "genclik_ilavesi": 0,
    "sut_havzasi_ilavesi": 0,
    "su_kisiti": 0,
    "sertifikali_tohum": 173.6,
    "organik_tarim": 372,
    "iyi_tarim": 527,
    "gubre": 99.2,
    "toplam": 1234.56
  }
}
```</content>
<parameter name="filePath">/home/akn/Genel/webimar/aricilik-destek-hesaplama-prompt-zinciri.md