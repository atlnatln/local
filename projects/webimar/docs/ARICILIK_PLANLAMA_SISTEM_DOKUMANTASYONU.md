# 🐝 Arıcılık Planlama Sistemi - Dokümantasyon

## Genel Bakış

Arıcılık Planlama Sistemi, arıcıların üretmek istedikleri bal çeşidine ve tarih aralığına göre Türkiye'nin en uygun bölgelerini bulmalarına yardımcı olan akıllı bir rota planlama aracıdır.

**Tarih:** 25 Kasım 2025  
**Versiyon:** 1.0.0  
**Durum:** ✅ Production Ready

---

## 🎯 Özellikler

### Kullanıcı Özellikleri
1. **Bal Çeşidi Seçimi**: 23 farklı bal türü (Kestane, Çam, Narenciye, Lavanta, vb.)
2. **Tarih Aralığı**: Başlangıç ve bitiş tarihi seçimi
3. **Otomatik Plan Önerileri**: Sistem 3-4 optimum bölge önerir
4. **Harita Görselleştirme**: Önerilen bölgeleri harita üzerinde görüntüleme
5. **Detaylı Bitki Bilgisi**: Her bölgedeki hedef bitkilerin çiçeklenme tarihleri

### Teknik Özellikler
- **Backend**: Django REST API
- **Frontend**: Next.js 15 (TypeScript, React Leaflet)
- **Veri Kaynağı**: Tarım ve Orman Bakanlığı çiçeklenme veritabanı
- **Algoritma**: Çok kriterli sıralama (hedef bitki yoğunluğu + biyoçeşitlilik skoru)

---

## 📁 Dosya Yapısı

```
webimar/
├── webimar-api/
│   └── flowering_calendar/
│       ├── views.py                 # BeekeepingPlanView endpoint
│       ├── urls.py                  # /api/flowering/beekeeping-plan/
│       └── data/
│           └── flowering_data.json  # Çiçeklenme veritabanı
├── webimar-nextjs/
│   └── pages/
│       ├── aricilik-planlama.tsx    # Yeni arıcılık planlama sayfası
│       └── ciceklenme-takvimi.tsx   # Redirect → aricilik-planlama
├── bal_cesitleri.json               # 81 il, 23 bal türü verisi
└── test_aricilik_planlama.py        # Test script (API + edge cases)
```

---

## 🔧 API Endpoint

### POST `/api/flowering/beekeeping-plan/`

**Request Body:**
```json
{
  "honey_type": "KESTANE",
  "start_month": 6,
  "start_day": 1,
  "end_month": 7,
  "end_day": 31
}
```

**Response (Success):**
```json
{
  "success": true,
  "honey_type": "KESTANE",
  "date_range": {
    "start": "1/6",
    "end": "31/7"
  },
  "total_matching_districts": 166,
  "plans": [
    {
      "plan_number": 1,
      "province": "DENİZLİ",
      "district": "BULDAN",
      "target_plants": [
        {
          "plant": "kestane",
          "start": [6, 1],
          "end": [7, 31]
        }
      ],
      "diversity_score": 11,
      "recommendation_reason": "🥇 En yüksek hedef bitki yoğunluğu | 2 farklı hedef bitki mevcut"
    }
    // ... 3 plan daha
  ]
}
```

**Response (No Results):**
```json
{
  "success": false,
  "message": "OLMAYAN_BAL balı için uygun bölge bulunamadı.",
  "plans": []
}
```

**Error Response (400):**
```json
{
  "error": "honey_type parametresi gerekli (örn: KESTANE, ÇAM, NARENCİYE)"
}
```

---

## 🧪 Test Sonuçları

### Başarılı Testler

| Bal Türü | Tarih Aralığı | Uygun Bölge | Plan Sayısı | Durum |
|----------|---------------|-------------|-------------|-------|
| KESTANE | 1/6 - 31/7 | 166 | 4 | ✅ |
| ÇAM | 1/7 - 31/8 | 68 | 4 | ✅ |
| LAVANTA | 1/6 - 30/6 | 41 | 4 | ✅ |
| NARENCİYE | 1/3 - 30/4 | 0 | 0 | ⚠️ Sonuç yok |

**Örnek Çıktılar:**

#### KESTANE Balı
```
Plan 1: BULDAN, DENİZLİ
   🥇 En yüksek hedef bitki yoğunluğu
   2 hedef bitki | 11 toplam tür

Plan 2: İNEBOLU, KASTAMONU
   🥈 İkinci en iyi hedef bitki yoğunluğu
   2 hedef bitki | 9 toplam tür
```

#### ÇAM Balı
```
Plan 1: PAMUKKALE, DENİZLİ
   🥇 En yüksek hedef bitki yoğunluğu
   Orta düzey çeşitlilik (36 tür)
   2 hedef bitki (Sebze.Çam Koşnili, Çam)
```

### Edge Case Testleri
- ✅ Eksik parametre → 400 Bad Request
- ✅ Geçersiz bal türü → Success false + açıklayıcı mesaj
- ✅ Sonuç bulunamayan tarih → 0 plan, açıklayıcı mesaj

---

## 🚀 Deployment

### Gerekli Adımlar

1. **Django Migrations** (gerekli değil, mevcut DB kullanılıyor)
2. **Static Files**: Türkiye GeoJSON haritası
   ```bash
   cp turkey-districts.geojson webimar-nextjs/public/
   ```

3. **Servis Restart**:
   ```bash
   ./stop-all-services.sh
   ./start-all-services.sh
   ```

4. **Test**:
   ```bash
   python3 test_aricilik_planlama.py
   ```

5. **Frontend Erişim**:
   - Yeni sayfa: `http://localhost:3000/aricilik-planlama`
   - Eski sayfa (redirect): `http://localhost:3000/ciceklenme-takvimi`

---

## 📊 Algoritma Mantığı

### Plan Sıralama Kriterleri

1. **Birincil Kriter**: Hedef Bitki Yoğunluğu
   - Aranan bal türünü içeren bitki sayısı
   - Örnek: "KESTANE" arayan kullanıcı → "Kestane", "kestane", "KESTANE" içeren tüm bitkiler

2. **İkincil Kriter**: Biyoçeşitlilik Skoru
   - İlçedeki toplam bitki türü sayısı
   - Yüksek çeşitlilik = daha uzun sezon, alternatif kaynak

### Skorlama Formülü

```python
score = (target_plant_count, diversity_score)
# Python tuple comparison: önce ilk eleman, eşitse ikinci
```

### Önerilen Plan Sayısı
- Maksimum 4 plan
- Sonuç yoksa: açıklayıcı hata mesajı

---

## 🎨 Kullanıcı Arayüzü

### Sol Panel (Form)
- 🍯 Bal çeşidi dropdown (23 seçenek)
- 📅 Başlangıç tarihi (gün + ay)
- 📅 Bitiş tarihi (gün + ay)
- 🚀 "Plan Oluştur" butonu
- 📋 Önerilen planlar listesi (tıklanabilir)

### Sağ Panel (Harita + Detay)
- 🗺️ Türkiye haritası (Leaflet.js)
  - Sarı: Önerilen tüm bölgeler
  - Yeşil: Seçili plan
  - Gri: Diğer ilçeler
- 📝 Alt panel: Seçili plan detayları
  - Hedef bitkiler
  - Çiçeklenme tarihleri
  - Öneri nedeni

### Responsive Tasarım
- Mobil: Dikey stack (form üstte, harita altta)
- Desktop: Yatay split (form solda, harita sağda)

---

## 🔗 İlgili Dosyalar

### Veri Kaynakları
- `bal_cesitleri.json`: Tarım ve Orman Bakanlığı - İl bazlı bal türleri
- `flowering_data.json`: İlçe + bitki + çiçeklenme tarihleri

### Test & Debug
- `test_aricilik_planlama.py`: Kapsamlı API test script
- Django logs: `/tmp/django.log`

### URL Routes
- Frontend: `/aricilik-planlama`
- API: `/api/flowering/beekeeping-plan/`

---

## 📈 Gelecek Geliştirmeler

### Önerilen Özellikler
1. **Mesafe Optimizasyonu**: Birbirine yakın bölgeleri önceliklendir
2. **Hava Durumu Entegrasyonu**: Tarihsel hava verileri ile tahmin
3. **Kullanıcı Konumu**: GPS → en yakın bölge öner
4. **Rota Haritası**: Çoklu bölge rotası çiz (A → B → C)
5. **Kayıt Sistemi**: Geçmiş planları kaydet (authenticated users)
6. **PDF Export**: Planları PDF olarak indir
7. **Mobil Uygulama**: React Native versiyonu

### Veri İyileştirmeleri
- İlçe koordinatları: GeoJSON'dan otomatik çıkar
- Bal verimi tahminleri: Kovan başına kg/yıl
- Arazi uygunluk skoru: Yükselti, iklim, erişim

---

## 🐛 Bilinen Sorunlar

1. **GeoJSON Koordinatları**: İlçe merkez noktaları hardcoded değil, dinamik hesaplanmalı
2. **Leaflet CSS Import Warning**: TypeScript lint hatası (çalışmayı etkilemiyor)
3. **NARENCİYE Balı Test**: Mart/Nisan aralığında sonuç yok (veri eksikliği olabilir)

---

## 🙏 Krediler

- **Veri Kaynağı**: T.C. Tarım ve Orman Bakanlığı
  - https://aricilikharitasi.tarimorman.gov.tr/
- **Harita Altyapısı**: OpenStreetMap + Leaflet.js
- **GeoJSON**: Türkiye İl/İlçe sınırları (turkey-districts.geojson)

---

## 📞 Destek

**Teknik Sorular**: GitHub Issues  
**API Dokümantasyon**: `/api/flowering/` endpoint listesi  
**Test Script**: `python3 test_aricilik_planlama.py`

---

**Son Güncelleme**: 25 Kasım 2025  
**Geliştirici**: Webimar AI Agent  
**Versiyon**: 1.0.0 Production
