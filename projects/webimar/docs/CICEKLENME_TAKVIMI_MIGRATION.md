# Bitki Çiçeklenme Takvimi - Migrasyon Tamamlandı

## 📦 Taşınan Dosyalar

### Django API (`webimar-api/flowering_calendar/`)
- `__init__.py` - App başlatıcı
- `apps.py` - Django app konfigürasyonu
- `views.py` - Tüm API endpoint'leri (7 adet)
- `urls.py` - URL routing
- `data/flowering_data.json` - 1.6MB çiçeklenme veritabanı

### Next.js Frontend (`webimar-nextjs/pages/`)
- `ciceklenme-takvimi.tsx` - Harita tabanlı interaktif sayfa

### Yardımcı Scriptler (`scripts/`)
- `generate_turkey_geojson.py` - Türkiye ilçe sınırları GeoJSON oluşturucu

## 🔗 API Endpoint'leri

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/api/flowering/plants/` | GET | Tüm bitki listesi |
| `/api/flowering/provinces/` | GET | Tüm il listesi |
| `/api/flowering/flowering-districts/` | GET | Tarih aralığına göre çiçeklenen ilçeler |
| `/api/flowering/plant-districts/` | GET | Belirli bitkinin yetiştiği ilçeler |
| `/api/flowering/district-plants/` | GET | Bir ilçedeki tüm bitkiler |
| `/api/flowering/district-diversity/` | GET | İlçelerdeki bitki çeşitliliği (heat map) |
| `/api/flowering/province-districts/` | GET | Bir ildeki tüm ilçeler |

## 🚀 Kullanım

### Backend Başlatma
```bash
cd webimar-api
python3 manage.py runserver 8000
```

### Frontend Başlatma
```bash
cd webimar-nextjs
npm run dev
```

### Sayfa Erişimi
- Development: http://localhost:3000/ciceklenme-takvimi
- Production: https://tarimimar.com.tr/ciceklenme-takvimi/

## ⚠️ Eksikler

1. **GeoJSON Dosyası**: `/public/turkey-districts.geojson` dosyası henüz oluşturulmadı.
   
   Oluşturmak için:
   ```bash
   pip install geopandas
   python3 scripts/generate_turkey_geojson.py
   ```

2. **Ana Sayfa Linki**: Kullanıcı isteği üzerine ana sayfaya link eklenmedi.

## 📝 Konfigürasyon

### Django settings.py
```python
INSTALLED_APPS = [
    ...
    'flowering_calendar',
]
```

### Django urls.py
```python
urlpatterns = [
    ...
    path('api/flowering/', include('flowering_calendar.urls')),
]
```

## 📊 Veri Yapısı

`flowering_data.json` formatı:
```json
{
  "İL_ADI": {
    "İLÇE_ADI": [
      {
        "plant": "Bitki Adı",
        "start": [ay, gün],
        "end": [ay, gün]
      }
    ]
  }
}
```

---
*Migrasyon Tarihi: 25 Kasım 2024*
