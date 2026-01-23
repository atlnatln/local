# KML Dosyaları

Bu dizin, Webimar hesaplama sayfasında kullanılan KML dosyalarını içerir.

## ⚡ Performans Optimizasyonu

**GeoJSON Formatı:** Hızlı yükleme için KML dosyaları GeoJSON formatına çevrilmiştir:
- Konum: `webimar-api/static/kml/` (backend için) ve `webimar-nextjs/public/kml/` (frontend için)
- `turkey-ova-boundaries.geojson` - Büyük Ova Sınırları (961,972 nokta, 23 MB)
- `yas-kapali-alanlar.geojson` - YAS Kapalı Alanlar (503,536 nokta, 18 MB)
- `turkey-provinces.geojson` - Türkiye il sınırları (backend polygon kontrolü için)
- `turkey-districts.geojson` - Türkiye ilçe sınırları (backend polygon kontrolü için)

**Avantajları:**
- JSON parse hızı XML'den **5-10x daha hızlı**
- Tarayıcı native JSON desteği
- **Tüm koordinatlar korunmuştur** (veri kaybı yok)
- Leaflet ile doğrudan kullanılabilir

Backend API, otomatik olarak GeoJSON dosyalarını öncelikli kullanır, bulunamazsa KML dosyalarına geçer.

## Aktif Dosyalar (Kaynak)

### `Türkiye Ova Sınırları.kml` (35 MB)
- **Amaç:** Büyük Ova Koruma Alanları sınırlarını tanımlar
- **Kullanım:** Arazi seçiminde büyük ova kontrolü için kullanılır
- **Son Güncelleme:** 11 Aralık 2025
- **Kaynak:** DSI güncel verisi

### `yas_kapali.kml` (40 MB)
- **Amaç:** YAS (Yerüstü Su İşletme Hakkı) tahsisine kapalı sahaları tanımlar
- **Kullanım:** Sulama tahsisi kontrolü için kullanılır
- **Son Güncelleme:** 11 Aralık 2025
- **Kaynak:** DSI güncel verisi

## Bölgesel Dosyalar (İzmir özel)

### `Büyük Ovalar İzmir.kml` (562 KB)
- İzmir bölgesi büyük ova sınırları

### `izmir.kml` (1.4 MB)
- İzmir il sınırları

### `izmir_kapali_alan.kml` (13 MB)
- İzmir bölgesi kapalı alanlar

## Teknik Notlar

1. **Dosya Formatı:** Tüm dosyalar standart KML (Keyhole Markup Language) formatındadır
2. **Encoding:** UTF-8
3. **Namespace:** http://www.opengis.net/kml/2.2
4. **Yükleme:** Dosyalar `maps/kml_helper.py` modülü tarafından otomatik yüklenir
5. **Cache:** İlk yükleme sonrası veriler bellekte tutulur (singleton pattern)

## Kullanım

KML dosyaları backend tarafından otomatik olarak yüklenir:

```python
from maps.kml_helper import load_kml_data, get_kml_polygons, get_yas_kapali_polygons

# Verileri yükle (ilk çağrıda)
load_kml_data()

# Büyük ova polygonlarını al
polygons, names = get_kml_polygons()

# YAS kapalı alan polygonlarını al
yas_polygons, yas_names = get_yas_kapali_polygons()
```

## Dosya Yolu Öncelikleri

Sistem aşağıdaki sırayla dosyaları arar:

1. `webimar-api/static/kml/` (tercih edilen konum)
2. Proje kök dizini (geriye uyumluluk için)

## Güncelleme

KML dosyalarını güncellerken:

1. Yeni dosyayı bu dizine kaydedin
2. Dosya adını koruduğunuzdan emin olun
3. API servisini yeniden başlatın (otomatik yükleme için)
4. Test edin: `/api/maps/check-polygon/` endpoint'ini kullanın
