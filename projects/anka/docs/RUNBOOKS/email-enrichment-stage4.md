# Runbook: Email Enrichment (Stage 4)

Bu doküman, batch pipeline içindeki Stage 4 (email kazıma/zenginleştirme) akışını, gerekli ayarları ve doğrulama adımlarını açıklar.

## 1) Kapsam

- Stage 1-2-3 sonrası `BatchItem.data` içindeki website alanlarını kullanarak e-posta çıkarımı yapılır.
- Çıkan e-postalar `BatchItem.data.email` alanına yazılır.
- Batch seviyesinde sayaç `emails_enriched` güncellenir.
- Export tarafında CSV/XLSX başlıklarına `Email` kolonu dahil edilir.

## 2) İlgili Kod Alanları

- Email provider: `services/backend/apps/providers/email_enrichment.py`
- Pipeline entegrasyonu: `services/backend/apps/batches/services.py`
- Serializer alanı: `services/backend/apps/batches/serializers.py`
- Export çıktısı: `services/backend/apps/exports/tasks.py`
- Model alanı: `services/backend/apps/batches/models.py`
- Migrationlar:
  - `services/backend/apps/batches/migrations/0003_batch_emails_enriched.py`
  - `services/backend/apps/batches/migrations/0004_alter_batch_status_add_enriching_emails.py`

## 3) Konfigürasyon

### Zorunlu Feature Flag

`.env.production` veya ilgili ortam dosyasında:

```dotenv
ANKA_EMAIL_ENRICHMENT_ENABLED=true
```

### Opsiyonel Gemini desteği

`GEMINI_API_KEY` verilirse fallback/grounding akışları kullanılabilir. Bu değer yoksa Stage 4 tamamen kapanmaz; yalnızca Gemini tabanlı parçalar devre dışı kalır.

### Token kontrol ayarları (Gemini S2)

Stage 4 içinde Gemini çağrılarının token tüketimi JSONL log dosyasına yazılır ve istenirse günlük token limiti uygulanır.

`.env.production` (veya ilgili ortam) örneği:

```dotenv
ANKA_EMAIL_TOKEN_LOG_ENABLED=true
ANKA_EMAIL_TOKEN_LOG_PATH=/app/artifacts/usage/email_enrichment_tokens.jsonl
ANKA_EMAIL_DAILY_TOKEN_LIMIT=15000
ANKA_EMAIL_TOKEN_WARN_THRESHOLD=0.8
```

- `ANKA_EMAIL_TOKEN_LOG_ENABLED`: token loglamayı aç/kapat.
- `ANKA_EMAIL_TOKEN_LOG_PATH`: JSONL log dosya yolu.
- `ANKA_EMAIL_DAILY_TOKEN_LIMIT`: günlük toplam token limiti (`0` ise sınırsız).
- `ANKA_EMAIL_TOKEN_WARN_THRESHOLD`: limitin hangi oranında uyarı üretileceği (`0.8` = %80).

Not: Limit aşılırsa Stage 4, S2 (Gemini) çağrısını güvenli şekilde atlar; S1 scraping davranışı aynı kalır.

## 4) Arama Mantığı (S2 Gemini Grounding)

S1 ile email bulunamazsa aşağıdaki prompt stratejisi kullanılır:

1. İşletme adı + adres + iletişim anahtar kelimeleri ile arama niyeti kurulur.
2. Sosyal medya ve rehber/dizin kaynakları dışlanır.
3. Modelden sadece email veya `NONE` dönmesi istenir.
4. Model yanıt metninde email yoksa grounding URL'lerinden en fazla 3 kaynak scrape edilir.

Pratik prompt formu:

```text
"{işletme_adı}" {adres} iletişim mail e-posta ...
```

Bu yaklaşım, resmi iletişim sayfalarına öncelik vererek gereksiz token ve scrape maliyetini azaltır.

## 5) Deploy Sonrası Doğrulama

1. Migrationlar uygulanmış olmalı:

```bash
python manage.py migrate --noinput
```

2. Serializer alan doğrulaması:

```bash
python manage.py shell -c "from apps.batches.serializers import BatchSerializer; print('emails_enriched' in BatchSerializer.Meta.fields)"
```

3. API doğrulaması (`/api/batches/`):
- Yanıtta `emails_enriched` anahtarı görünmeli.

4. Export doğrulaması:
- Yeni üretilen CSV başlığı `Firma,Telefon,Website,Email,Adres` olmalı.

5. Token log doğrulaması:

```bash
docker compose -f docker-compose.prod.yml exec -T backend sh -lc 'tail -n 5 /app/artifacts/usage/email_enrichment_tokens.jsonl'
```

Log satırında en az şu alanlar görülmelidir: `timestamp`, `model`, `firm_name`, `prompt_tokens`, `output_tokens`, `total_tokens`, `status`.

Not: Aynı `csv_url` tekrar okunurken browser/proxy cache eski header döndürebilir. Doğrulamada `?nocache=<timestamp>` eklenmesi önerilir.

## 6) Operasyonel Sorun Giderme

### A) API'de `emails_enriched` görünmüyor

- Çalışan container kodu eski olabilir (image rebuild/recreate gerekir).
- Migration eksik olabilir (`0003` / `0004`).
- Farklı sunucuya deploy edilmiş olabilir (DNS/IP hedefi kontrol edilmeli).

### B) CSV'de `Email` kolonu görünmüyor

- Export'u üreten celery worker eski image olabilir; worker rebuild/restart gerekir.
- Eski dosya URL'si cache'den dönüyor olabilir; yeni export üretin veya `nocache` parametresi kullanın.

### C) Stage 4 çalışmıyor

- `ANKA_EMAIL_ENRICHMENT_ENABLED` false/eksik olabilir.
- Uygun website kaydı yoksa item bazında email bulunamaz; sayaç 0 kalabilir.

### D) Token tüketimi izlenemiyor

- `ANKA_EMAIL_TOKEN_LOG_ENABLED=true` mi kontrol edin.
- Log path container içinde yazılabilir olmalı (`/app/artifacts/usage/...`).
- Son satırları okuyup JSON parse hatası olup olmadığını kontrol edin.

### E) Token limiti erken doluyor

- `ANKA_EMAIL_DAILY_TOKEN_LIMIT` değeri çok düşük olabilir.
- Arama hacmini batch bazında düşürün; önce küçük örnekle test edin (2-3 kayıt).
- `ANKA_EMAIL_TOKEN_WARN_THRESHOLD` ile erken uyarıyı artırın (örn. `0.7`).

## 7) Local vs VPS Test Notu (Özet)

- Local varsayılan akış localhost endpoint'lerini kullanır.
- VPS API'ye localden test isteniyorsa bu açık bir override gerektirir (örn. `BACKEND_URL`, `BASE_URL`, SSH tunnel).
- E2E helper `tests/e2e/playwright/helpers/auth.ts` içinde `BACKEND_URL` desteği vardır; default `http://localhost:8000`.
- Prod benzeri auth akışı (Google-only) ile test-login tabanlı E2E akışı farklıdır.

## 8) Güvenli Local Test Komutu (Önerilen)

Yeni özellik sonrası hızlı ve güvenli doğrulama için:

```bash
./scripts/local-feature-test.sh
```

Bu komut:

- Varsayılan olarak yalnızca localhost endpointlerine izin verir.
- Yanlışlıkla prod domain/IP'e test trafiği gitmesini engeller.
- Stage 4 ile ilişkili backend testlerini odaklı çalıştırır.

Opsiyonel Playwright smoke:

```bash
./scripts/local-feature-test.sh --with-e2e
```
