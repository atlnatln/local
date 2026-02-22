# Dokümantasyon-Kod Uyum Denetimi (2026-02-21)

## 1) Kapsam
Bu denetim, proje içindeki kullanıcıya ait markdown dokümanlarının mevcut kod yapısı ile uyumunu doğrulamak için yapılmıştır.

Kapsama dahil:
- Kök dokümanlar (`README.md`, `CONTRIBUTING.md` vb.)
- `docs/` altındaki ADR ve RUNBOOKS dosyaları
- Operasyonel olarak kullanılan akış dokümanları

Kapsam dışı:
- `node_modules`, `venv`, `test_env`, `artifacts`, `backups`, `playwright-report`, `test-results` gibi türetilmiş/harici klasörler.

## 2) Yöntem
1. Kod tabanında kritik akış dosyaları incelendi:
   - `services/backend/apps/batches/services.py`
   - `services/backend/apps/providers/google_places.py`
   - `services/backend/apps/providers/grid_search.py`
   - `services/backend/enrich_websites_with_gemini.py`
2. Tüm proje markdown dosyalarında yerel link bütünlüğü otomatik tarandı.
3. Bulunan sapmalar doküman düzeltmesi ile giderildi.

## 3) Otomatik Link Bütünlüğü Sonucu
- Taranan markdown dosyası: **27**
- Kırık yerel markdown linki: **0** (düzeltme sonrası)

## 4) Düzeltilen Uyum Sapmaları
1. **README test stratejisi linki hatalıydı**
   - Eski: `docs/TESTING.md` (dosya yok)
   - Yeni: `tests/kurallar.md`

2. **Google Maps strateji dokümanında GeoJSON linki hatalıydı**
   - Eski: `docs/turkey-districts.geojson` (doküman içinden göreli yol hatalı)
   - Yeni: `turkey-districts.geojson`

3. **Google Maps strateji dokümanında model referansı güncel değildi**
   - Eski: `gemini-2.0-flash`
   - Yeni: `gemini-2.5-flash`

4. **Runbooks index dosyası eksikti**
   - Eklendi: `docs/RUNBOOKS/README.md`

5. **Maps sorgu mantığı için operasyonel runbook yoktu**
   - Eklendi: `docs/RUNBOOKS/maps-query-logic-pipeline.md`

6. **Gemini enrichment runbook güncel limit/model bilgisi içermiyordu**
   - Güncellendi: `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`

## 5) Kodla Eşleşen Güncel Durum Özeti
- Varsayılan enrichment modeli: `gemini-2.5-flash`
- Grounding günlük limit argümanı: `--grounding-daily-limit` (legacy alias korunuyor)
- Token limit desteği: aktif
- Batch tarafında stage bazlı API çağrı limitleri: env ile aktif

## 6) Sonuç
Bu denetim kapsamında proje dokümanları, mevcut çalışma akışını ve kod davranışını yansıtacak şekilde güncellendi.

- Link bütünlüğü: **Tamam**
- Runbook kapsaması (Maps + Gemini): **Tamam**
- README referans uyumu: **Tamam**
