# ADR-0008: Email Enrichment S2 Unified Gemini Çağrısı (Mart 2026)

- **Tarih:** 2026-03-08
- **Durum:** Kabul Edildi
- **Karar Vericiler:** Proje ekibi

## Bağlam

Stage 4 email enrichment pipeline'ı, web sitesi bilinmeyen firmalar için iki ayrı Gemini çağrısı yapıyordu:

1. **S2 (`_gemini_find_official_website`)** — Sadece resmi website URL'sini bulur (çıktı: URL veya `NONE`).
2. **S3 (`_gemini_search_email`)** — Sadece email arar; bulamazsa Gemini'ye tekrar sorar.

Bu iki çağrı firma başına en kötü durumda **~1 850 token** tüketiyordu.

Aynı dönemde `GEMINI_API_KEY` `.env.production` içinde yorum satırı halindeydi; bu nedenle S2 ve S3 hiç çalışmıyor, website'i olmayan tüm firmalar için email bulunamıyordu.

## Karar

### 1. S2 + S3 → Tek Unified Çağrı

`_gemini_find_contact_unified()` adında yeni bir metot yazıldı. Tek Gemini çağrısında
`EMAIL:` ve `WEB:` satırları ile hem email hem de resmi website döndürülür.

**Prompt çıktı formatı:**

```text
EMAIL: ornek@firma.com
WEB: https://www.firma.com.tr
```

`enrich_contacts()` içindeki S2+S3 iki-çağrı zinciri bu metotla değiştirildi.

Eski metotlar `[DEPRECATED]` olarak işaretlendi ve geriye dönük uyumluluk için bırakıldı:
- `_gemini_find_official_website()` → `[DEPRECATED]`
- `_gemini_search_email()` → `[DEPRECATED]`

### 2. GEMINI_API_KEY Production'a Eklendi

`.env.production` ve compose interpolasyon `.env` dosyasına `GEMINI_API_KEY` eklendi.
Local native geliştirme için `.env.local.native` dosyasına da eklendi.

### 3. local → VPS Tunnel Mode Scriptlere Entegre Edildi

Google API key'leri VPS IP'sine (`89.252.152.222`) kısıtlı olduğundan local backend
doğrudan Google Places / Maps API'lerini çağıramaz. İki yeni geliştirme modu eklendi:

- **`./dev-local.sh --vps`** — Django başlatılmaz; SSH tunnel ile VPS backend'e bağlanılır.
  Next.js local'de çalışmaya devam eder.
- **`./dev-docker.sh --vps-backend`** — Yalnızca frontend container başlatılır; SSH tunnel
  ile `127.0.0.1:18010 → VPS:8100` kurulur.

Bkz. [secure-local-vps-access.md §5.2](./secure-local-vps-access.md).

## Alternatifler Değerlendirmesi

| Seçenek | Artı | Eksi |
|---------|------|------|
| Mevcut iki çağrıyı koru | Hata izolasyonu kolay | Firma başına ~1 850 token; iki tur bekleme |
| S2 çıktısını S3 promptuna göm (zincirleme) | Kod değişikliği minimal | Yine iki API çağrısı |
| **Unified tek çağrı (seçilen)** | ~950 token, tek tur, telefon da döner | Parse hata riski (satır formatı bozulursa) |

Unified yaklaşımın parse hatası riski, grounding_chunks fallback ile azaltılmıştır:
Gemini cevabında EMAIL/WEB parse edilemezse grounding URL'leri scrape edilmeye devam eder.

## Sonuçlar

| Kriter | Önceki | Sonraki |
|--------|--------|---------|
| Firma başına Gemini çağrısı (website yok) | 2 | 1 |
| Worst-case token (website yok) | ~1 850 | ~950 |
| Telefon enrichment | Yalnızca scraping | Unified prompt + scraping |
| GEMINI_API_KEY durumu | Yorum satırı (etkisiz) | Aktif |
| Local → VPS geliştirme | Manuel tunnel | `--vps` / `--vps-backend` flag |

## İlgili Dosyalar

- `services/backend/apps/providers/email_enrichment.py`
- `dev-local.sh`, `dev-docker.sh` (proje + root)
- `docker-compose.yml`
- `.env.local.docker`, `.env.local.native`
- `docs/RUNBOOKS/email-enrichment-stage4.md`
- `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`
- `docs/RUNBOOKS/secure-local-vps-access.md`
