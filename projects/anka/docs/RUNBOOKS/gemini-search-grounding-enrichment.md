# Ankadata Runbook: Gemini Search Grounding ile Website Enrichment

## 1) Amaç
- Google Maps verisinde `website` alanı boş işletmeler için yalnızca resmi web sitesi URL'si bulmak.
- Token/request tüketimini kayıt altına alıp limit aşımı öncesi uyarı vermek.

## 2) Kullanılan Bileşenler
- Script: `services/backend/enrich_websites_with_gemini.py`
- Model: Varsayılan `gemini-2.5-flash`
- Grounding aracı: `google_search`
- Girdi: Google Maps çıktı CSV'si (`results.csv`)
- Çıktı: Aynı CSV içinde `website` alanı güncellemesi + JSONL kullanım logu

## 3) Güvenli Maliyet Stratejisi
- Çıktı kısa tutulur: sadece `URL` veya `NONE`.
- `max_output_tokens=64` ile gereksiz output token engellenir.
- Sosyal medya ve dizin domainleri filtrelenir.
- Günlük request limiti script içinde stop mekanizmasıyla korunur.
- İsteğe bağlı günlük token limiti ile ikinci güvenlik katmanı eklenir.

## 4) Ortam Değişkenleri
- `.env` içinde:
  - `GEMINI_API_KEY=...`
  - `ANKA_GROUNDING_DAILY_REQUEST_LIMIT=500` (grounding request güvenlik limiti)
  - `ANKA_GEMINI_DAILY_TOKEN_LIMIT=50000` (token güvenlik limiti)

## 5) Komutlar

### Dry-run (önerilen ilk adım)
```bash
cd services/backend
./venv/bin/python enrich_websites_with_gemini.py \
  --input data/google_maps_searches/query_3_20260201_165628/results.csv \
  --limit 20 \
  --dry-run
```

### Gerçek yazma
```bash
cd services/backend
./venv/bin/python enrich_websites_with_gemini.py \
  --input data/google_maps_searches/query_3_20260201_165628/results.csv
```

### Limitli ve uyarılı çalışma
```bash
cd services/backend
./venv/bin/python enrich_websites_with_gemini.py \
  --grounding-daily-limit 500 \
  --daily-token-limit 50000 \
  --warn-threshold 0.8 \
  --usage-log artifacts/usage/gemini_grounding_usage.jsonl
```

Not:
- `--daily-request-limit` argümanı geriye dönük uyumluluk için korunur.
- Yeni isimlendirme: `--grounding-daily-limit`.

## 6) Kullanım Logu
- Varsayılan log dosyası:
  - `services/backend/artifacts/usage/gemini_grounding_usage.jsonl`
- Her satır JSON formatında şunları içerir:
  - `timestamp`, `model`, `business_name`, `status`, `website`
  - `request_index`, `prompt_tokens`, `output_tokens`, `total_tokens`
  - Hata varsa `error`

Örnek satır:
```json
{"timestamp":"2026-02-15T14:30:00+00:00","model":"gemini-2.5-flash","business_name":"Örnek Ltd","status":"success","website":"https://ornek.com","request_index":12,"prompt_tokens":158,"output_tokens":14,"total_tokens":172}
```

## 7) Limit ve Uyarı Kuralları
- `--grounding-daily-limit` (veya `--daily-request-limit`) dolarsa script güvenli şekilde durur.
- `--daily-token-limit` dolarsa script güvenli şekilde durur.
- `--warn-threshold` (varsayılan `%80`) aşılırsa terminalde uyarı basılır.

## 8) İzleme ve Faturalama
- AI Studio kullanım ekranı:
  - https://aistudio.google.com/app/usage?timeRange=last-28-days&project=gen-lang-client-0896549621
- Proje içi gerçek tüketim doğrulaması:
  - JSONL log toplamları (`total_tokens`, `request_index`)
  - Script sonu özet çıktısı

## 9) Operasyonel Notlar
- Önce `--dry-run`, sonra gerçek yazma önerilir.
- Bulunamayan kayıtlar için ayrı fallback stratejisi uygulanabilir (isim sadeleştirme, ilçe bazlı ikinci deneme).
- Bu akış yalnızca web sitesi URL'sini hedefler; site içi scraping bu runbook kapsamı dışındadır.
- `gemini-2.0-flash` yeni kullanıcılar/projeler için erişim dışı olabilir. 404 `NOT_FOUND` alınırsa `gemini-2.5-flash` ile devam edilmelidir.
