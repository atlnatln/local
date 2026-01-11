# JavaScript Dosyaları Organizasyonu

Bu klasördeki JavaScript dosyaları mantıklı bir sıralama ve isimlendirme sistemine göre organize edilmiştir.

## Dosya Sıralaması ve İşlevleri

### Temel Yapı
- **01-config.js** - Sabitler ve konfigürasyon ayarları
- **02-utils.js** - Yardımcı fonksiyonlar (Utils modülü)
- **03-main.js** - Ana uygulama başlatma dosyası

### Modüller
- **04-map.js** - Harita modülü (MapModule)
- **05-polygon.js** - Polygon işlemleri modülü
- **06-content.js** - İçerik modülü
- **14-results.js** - Sonuçlar görüntüleme modülü

### Form Modülleri (Sıralama Önemli!)
- **07-form-core.js** - Form temel işlevleri (FormCore)
- **08-form-validation.js** - Form doğrulama işlemleri
- **09-form-visibility.js** - Form görünürlük kontrolü
- **10-form-special-fields.js** - Sera, Silo ve özel form alanları
- **11-form-submission.js** - Form gönderim ve veri hazırlama
- **12-form-module-legacy.js** - Eski form modülü (geriye dönük uyumluluk)
- **13-form-module.js** - Ana form modülü (tüm form modüllerini birleştirir)

### Özel Modüller
- **15-dikili-arazi.js** - Dikili arazi kontrol sistemi
- **16-imar-form.js** - İmar formu özellikleri

## Yükleme Sırası

HTML template dosyasında dosyalar şu sırayla yüklenir:

1. Konfigürasyon ve yardımcı dosyalar (01-02)
2. Temel modüller (04-06, 14)
3. Form modülleri (07-11)
4. Özel modüller (15)
5. Ana form modülü (13) - `defer` ile
6. Ana uygulama (03) - `defer` ile, en son

## Not

- Form modülleri arasındaki bağımlılık sırası kritiktir
- Ana dosyalar `defer` attributesi ile yüklenir
- Bu organizasyon kodu daha kolay maintain edilebilir hale getirir
- Dosya isimleri başındaki numaralar yükleme sırasını belirtir

## Tarihçe

- **2025-05-24**: JavaScript dosyaları yeniden organize edildi
- Eski dosya isimleri yeni kategorik isimlendirme sistemine dönüştürüldü
- Gereksiz boş dosyalar (`display-result.js`, `dynamic-sera-fields.js`) silindi
