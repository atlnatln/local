# Runbook: Maps Sorgu Mantığı (3 Aşamalı Pipeline)

## 1) Amaç
- Şehir + sektör sorgusundan maliyeti kontrollü şekilde firma listesi üretmek.
- Yüksek maliyetli alanları sadece doğrulanmış kayıtlarda çağırmak.
- Süreci operasyonel olarak izlenebilir ve sınırlandırılabilir tutmak.

## 2) Kaynak Kod Referansları
- Orkestrasyon: `services/backend/apps/batches/services.py`
- Places istemcisi: `services/backend/apps/providers/google_places.py`
- Geo sınır/bounding box: `services/backend/apps/providers/grid_search.py`
- Demo komutu: `services/backend/apps/batches/management/commands/run_planner_demo.py`

## 3) Akış Özeti
1. **Stage 1 - COLLECTING_IDS**
   - `places:searchText` çağrısı yapılır.
   - Field mask: `places.id,places.name,nextPageToken`.
   - Amaç: düşük maliyetle aday ID havuzu.
2. **Stage 2 - FILTERING**
   - `Place Details Pro` çağrısı (`id,displayName,formattedAddress,types,businessStatus`).
   - `businessStatus=OPERATIONAL` ve tip/isim eşleşmesi kontrolü.
3. **Stage 3 - ENRICHING_CONTACTS**
   - `Place Details Enterprise` çağrısı (`websiteUri,nationalPhoneNumber`).
   - Sadece Stage 2’yi geçen kayıtlar zenginleştirilir.

## 3.1) Konum Belirleme (Frontend → Backend)

Frontend'de kullanıcıya iki konum seçim modu sunulur:

1. **Şehir / İlçe modu**: Kullanıcı şehir adı ve opsiyonel ilçe yazar. Backend, `city` ve `filters.district` alanlarından GeoJSON sınırlarını çözer.
2. **Harita ile Seç modu**: Kullanıcı Google Maps üzerinde dörtgen çizer. Frontend, `filters.location_bounds` olarak `{ low: { latitude, longitude }, high: { latitude, longitude } }` gönderir. Backend bu bounds'u doğrudan Stage 1 arama bölgesi olarak kullanır.

Her iki mod da sonuçta `Rectangle(low, high)` formatına dönüşür ve Stage 1 adaptif bölme (quadtree) algoritmasına beslenir.

## 4) Stage 1 Detayı: Adaptif Bölme (Quadtree)
- Başlangıç bölgesi: `get_adaptive_search_regions(city, district)` veya doğrudan `location_bounds` (harita modu).
- Bölge tipi: `Rectangle(low, high)`.
- Kural:
  - Sonuç sayısı `SPLIT_THRESHOLD=60` altındaysa bölme yok.
  - Üstündeyse bölge 4’e bölünür (`split()`), rekürsif devam eder.
  - `MAX_DEPTH=4` ile rekürsiyon sınırlandırılır.
- Sonuçlar `place_id` bazında tekilleştirilir (`seen_ids`).

## 5) Grid/GeoJSON Bağımlılığı
- Geo sınır dosyası: `docs/turkey-districts.geojson`.
- Dosya bulunamazsa `Grid Search will not work` uyarısı loglanır ve Stage 1 boş dönebilir.
- Container/prod ortamında bu dosyanın erişilebilir olduğundan emin olunmalıdır.

## 6) Hata Yönetimi ve Retry
`GooglePlacesClient._make_request` davranışı:
- `429`: exponential backoff ile retry.
- `5xx`: retry.
- `404`: business-level miss kabul edilir, `None` döner.
- `400/403`: konfigürasyon/quota kabul edilir, fail-fast.

## 7) Maliyet Güvenlikleri (Kodda Aktif)
### Batch pipeline limitleri (env)
- `ANKA_BATCH_MAX_RECORDS` (varsayılan: `50`)
- `ANKA_STAGE1_MAX_API_CALLS` (varsayılan: `20`)
- `ANKA_STAGE2_MAX_API_CALLS` (varsayılan: `80`)
- `ANKA_STAGE3_MAX_API_CALLS` (varsayılan: `80`)

Davranış:
- Stage 1 API çağrı tavanına ulaşırsa ID toplama erken durur.
- Stage 2 API çağrı tavanına ulaşırsa batch `PARTIAL` olur.
- Stage 3 API çağrı tavanına ulaşırsa kalan kayıtlar enrich edilmeden atlanır.

### Circuit breaker
- Stage 2’de hata oranı %50 üstüne çıkarsa batch korunmalı şekilde durdurulur (`PARTIAL`).

## 8) Çıktı ve Durum Alanları
`Batch` üzerinde izlenen temel metrikler:
- `ids_collected`
- `ids_verified`
- `contacts_enriched`
- `error_records`
- `status`: `COLLECTING_IDS` -> `FILTERING` -> `ENRICHING_CONTACTS` -> `READY` (veya `PARTIAL`/`FAILED`)

## 9) Operasyonel Kontrol Komutları
```bash
# Demo pipeline (şehir/sektör)
cd services/backend
python manage.py run_planner_demo --city "Muğla" --sector "Şehir plancısı" --limit 10 --output artifacts/demo/mugla_planci_10.csv

# Sonuç CSV kontrol
wc -l artifacts/demo/mugla_planci_10.csv
```

## 10) Bilinen Pratik Notlar
- Places API tarafında proje/credential karışıklığını önlemek için API key restriction + proje doğrulaması birlikte yapılmalıdır.
- Prod’da host-native çalıştırmada DB host çözümleme sorunları yaşanırsa pipeline container içinde çalıştırılmalıdır.
- Bu runbook, sorgu mantığı ve maliyet güvenliklerini kapsar; website enrichment detayları için `gemini-search-grounding-enrichment.md` dosyasına bakın.
