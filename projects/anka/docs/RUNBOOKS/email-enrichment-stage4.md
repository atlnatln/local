# Runbook: Email Enrichment (Stage 4)

Bu doküman, batch pipeline içindeki Stage 4 (email kazıma/zenginleştirme) akışını, gerekli ayarları ve doğrulama adımlarını açıklar.

## 1) Kapsam

- Stage 1-2 sonrası doğrulanmış kayıtlar için (Stage 3 başarılı olmasa bile) email enrichment çalışabilir.
- `BatchItem.data` içindeki website alanı varsa doğrudan scraping ile email aranır.
- Website yoksa önce Gemini Search Grounding ile **resmi website/iletişim sayfası** bulunmaya çalışılır; bulunan website `BatchItem.data.website_uri` alanına yazılabilir ve ardından scraping ile email aranır.
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

### Token kontrol ayarları (Gemini S2 Unified)

Stage 4 içinde Gemini çağrılarının token tüketimi JSONL log dosyasına yazılır ve istenirse günlük token limiti uygulanır.
Mart 2026 itibarıyla S2+S3 birleştirildiğinden en kötü senaryoda firma başına **~950 token** kullanılır (eski: ~1 850 token).

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

Not: Limit aşılırsa Stage 4, S2-unified (Gemini) çağrısını güvenli şekilde atlar; S1 scraping davranışı aynı kalır.

## 4) Arama Mantığı (S2 Unified — Mart 2026 itibarıyla)

> **ÖNEMLİ:** Önceki iki ayrı Gemini çağrısı (S2-website + S3-email) **tek bir unified çağrıya** indirildi.  
> Metot: `_gemini_find_contact_unified()` | Eski metotlar: `_gemini_find_official_website()` `[DEPRECATED]`, `_gemini_search_email()` `[DEPRECATED]`  
> Bkz. ADR-0008.

S1 ile email bulunamazsa veya website yoksa tek Gemini çağrısı kullanılır:

```
"{işletme_adı}" {adres} resmi web sitesi, e-posta iletişim bilgileri
```

Gemini cevabı `EMAIL:` ve `WEB:` satırlarıyla ayrıştırılır. Ardından grounding_chunks URL'leri
de scrape edilir. Tek çağrıda hem resmi website hem de email+telefon döner.

### Eski (S2+S3) vs Yeni (Unified) karşılaştırma

| Kriter | Eski akış | Yeni unified akış |
|---|---|---|
| Gemini çağrı sayısı (website yoksa) | 2 (S2-website + S3-email) | 1 (`_gemini_find_contact_unified`) |
| Token tüketimi (en kötü durum) | ~1 850 | ~950 |
| Telefon desteği | Yalnızca scraping | Unified prompt + scraping |
| Kod yolu | `_gemini_find_official_website` → `_gemini_search_email` | `_gemini_find_contact_unified` |

### Unified prompt çıktı formatı

```text
EMAIL: ornek@firma.com
WEB: https://www.firma.com.tr
```

Bulunamazsa satır `NONE` değeri alır. Parçalı/çoklu email için ilk geçerli adres kullanılır.

### Scraping zinciri (grounding_chunks)

Gemini grounding_chunks içindeki URL'ler `/iletisim`, `/contact`, `/about` yollarıyla
sırayla denenir. İlk bulunan email/telefon kaydedilir.

Bu yaklaşım, önce kanıtlanabilir URL yakalayıp sonra scraping ile doğrulamaya çalıştığı için
yanlış/uydurma email riskini azaltır.

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

### F) Dizin siteleri (örn. firma rehberleri) “website” olarak geliyor

- Resmi website adayı olarak sosyal medya/dizin/ilan domainleri blacklist ile dışlanır.
- Gerekirse blacklist listesi genişletilir (örn. `firmasec.com`, `bulurum.com` vb.).

### G) Token log eksik/yanıltıcı görünüyor

- Token log yalnızca "email arama" değil, tüm Gemini çağrılarını (unified dahil) kapsamalıdır.
- JSONL satırlarında `event_type` gibi bir alan ile çağrı türü ayrıştırılabilir.
- Mart 2026 itibarıyla unified çağrısında `event_type: "s2_unified"` beklenir.

### H) Log'da `S2-website` veya `S3-email` satırları hâlâ görünüyorsa

- Container eski image üzerinde çalışıyordur. `docker cp` sonrası `restart` yeterlidir:
  ```bash
  docker cp email_enrichment.py anka_backend_prod:/app/apps/providers/email_enrichment.py
  docker compose -f docker-compose.prod.yml restart backend
  ```
- Doğrulama:
  ```bash
  docker exec anka_backend_prod grep 'S2-unified\|DEPRECATED' /app/apps/providers/email_enrichment.py | head -5
  ```

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
- E2E helper `tests/e2e/playwright/helpers/auth.ts` içinde `BACKEND_URL` desteği vardır; default `http://localhost:8000` (native local). Docker kullanımında backend için tipik değer `http://localhost:8100` olur.
- Prod benzeri auth akışı (Google-only) ile test-login tabanlı E2E akışı farklıdır.

## 9) Kök Neden Analizi — "Neden email bulunamıyor?" (Mart 2026 Canlı İnceleme)

> Bu bölüm, production'daki batch'lerde `emails_enriched: 0` görülmesinin gerçek sebeplerini
> Playwright + container exec ile doğrudan izleyerek tespit etmiştir.
> Test batch: `a70fb8fa...` ("Harita Alanı - Kalıpçı", 02.03.2026, 2 kayıt, email 0)

### Tespit 1 — `GEMINI_API_KEY` Production'da Set Edilmemiş

`.env.production` satır 103:

```dotenv
# GEMINI_API_KEY=    ← YORUM SATIRI, değer yok
```

> **[ÇÖZÜLDÜ – Mart 2026]** `GEMINI_API_KEY` artık `.env.production` içinde aktif.
> Ayrıca S2+S3 çifti `_gemini_find_contact_unified()` ile tek çağrıya indirildi (bkz. ADR-0008).

**Etkisi:**
- `EmailEnrichmentClient.__init__()` → `self._api_key = None`
- Strateji 2 (Gemini grounding) tamamen atlanıyor: `_gemini_search_email()` > `if not self._api_key: return None`
- Website'i olmayan firmalar için `_gemini_find_official_website()` da çalışmıyor
- **Yalnızca Strateji 1 (web scraping) çalışıyor**

**Doğrulama komutu:**

```bash
docker exec anka_backend_prod env | grep -i "GEMINI\|ANKA_EMAIL"
# GEMINI_API_KEY satırı çıkmamalı → sorun burada
```

**Çözüm:**
`.env.production` içinde `GEMINI_API_KEY=<gerçek_anahtar>` satırını yorum dışına alıp yeniden deploy edin:
```bash
# Deploysuz anlık test:
docker exec anka_backend_prod sh -c 'export GEMINI_API_KEY=<anahtar>; python manage.py shell -c "..."'
```

---

### Tespit 2 — SSL Sertifikası Bozuk Siteler Sessizce Atlanıyor

Test sitesi `kalipciavyaban.com` her URL için şu hatayı döndürüyor:

```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

`_fetch_html()` içinde bu hata `except Exception` bloğu tarafından yakalanıp `logger.debug()` ile sessizce `None` döndürülüyor.
Tüm `_CONTACT_PATHS` (`/iletisim`, `/contact`, `/`, ...) denemesi başarısız oluyor.

**Ama email aslında var!**  
`verify=False` ile `GET /` yapıldığında:

```
[200] https://www.kalipciavyaban.com/  → ['kalipciavyaban@gmail.com']
```

Email ana sayfada açıkça bulunuyor; SSL engeli olmasa Strategy 1 başarıyla çalışırdı.

**Türkiye'deki durum:** KOBİ web sitelerinin önemli bir kısmı let's encrypt zinciri
eksik / self-signed / eski sertifika kullanıyor. Bu kombinasyon yaygın bir "sessiz kayıp"
yaratıyor.

**Doğrulama komutu (container içinde):**

```bash
docker exec anka_backend_prod python3 -c "
import requests, urllib3; urllib3.disable_warnings()
r = requests.get('https://www.kalipciavyaban.com/', verify=False, timeout=8)
import re
emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}', r.text)
print(emails)
"
# Çıktı: ['kalipciavyaban@gmail.com', ...]
```

**Çözüm seçenekleri:**

| Seçenek | Yaklaşım | Güvenlik |
|---------|----------|----------|
| **A (önerilen)** | `_fetch_html()` içinde SSL hatası alınca `verify=False` ile yeniden dene + `logger.warning()` yaz | Düşük risk; sadece fallback |
| B | Session oluştururken `verify=False` varsayılan yap | Tüm bağlantılar etkilenir; tavsiye edilmez |
| C | Başarısız SSL sitelerini Gemini'ye yönlendir (S2) | Tespit 1 çözüldüğünde geçerli |

**Seçenek A için kod değişikliği (`email_enrichment.py → _fetch_html`):**

```python
def _fetch_html(self, url: str) -> Optional[str]:
    if _is_excluded_domain(url):
        return None
    try:
        # ... mevcut kod ...
        resp = self._session.get(url, timeout=_SCRAPE_TIMEOUT, stream=True, allow_redirects=True)
    except requests.exceptions.SSLError:
        # SSL sertifikası bozuk siteler için verify=False ile bir kez daha dene
        logger.warning("[EmailEnrich] SSL hatası, verify=False ile yeniden deneniyor: %s", url)
        try:
            resp = self._session.get(url, timeout=_SCRAPE_TIMEOUT, stream=True,
                                     allow_redirects=True, verify=False)
        except Exception as exc:
            logger.debug("[EmailEnrich] SSL fallback da başarısız [%s]: %s", url, exc)
            return None
    except Exception as exc:
        logger.debug("[EmailEnrich] Fetch hatası [%s]: %s", url, exc)
        return None
    # ... devam: anti-bot check, raise_for_status, stream read ...
```

---

### Özet Tablo

| Sorun | Etki | Çözüm |
|-------|------|-------|
| `GEMINI_API_KEY` yorum satırı | S2-unified tamamen devre dışı; website'i olmayan tüm firmalar için 0 email | `.env.production`'da key aktif et |
| SSL sertifikası bozuk siteler | S1 tüm sayfalar için sessizce hata verir; email sitenin ana sayfasında olmasına rağmen bulunamaz | `_fetch_html` SSL fallback ekle |
| `_CONTACT_PATHS` sırasında `/` en sonda | Şans eseri site 403/rate-limit verince `/`'a hiç gelinmez | Zaten ikincil; SSL çözümü öncelik |
| S2-website + S3-email çift çağrısı (eski) | Firma başına ~1 850 token | Çözüldü — `_gemini_find_contact_unified` tek çağrısı (~950 token) |

---

### Bulgu Nasıl Elde Edildi (Tekrarlanabilir Adımlar)

```bash
# 1) Container env kontrol
docker exec anka_backend_prod env | grep GEMINI

# 2) Belirli bir sitenin scrape testini container içinden çalıştır
docker exec anka_backend_prod python3 -c "
import requests, re
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}', re.I)
r = requests.get('https://<WEBSITE>/', timeout=8)  # SSL hatası görünür
print(r.status_code, EMAIL_RE.findall(r.text))
"

# 3) SSL bypass ile tekrar dene
docker exec anka_backend_prod python3 -c "
import requests, re, urllib3; urllib3.disable_warnings()
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}', re.I)
r = requests.get('https://<WEBSITE>/', timeout=8, verify=False)
print(r.status_code, EMAIL_RE.findall(r.text))
"

# 4) Token log (Gemini aktifse)
tail -f /app/logs/usage/email_enrichment_tokens.jsonl | python3 -c "
import sys, json
for l in sys.stdin:
    if l.strip(): print(json.dumps(json.loads(l), ensure_ascii=False, indent=2))
"
```

---

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
