# Çekirdek Yapı Denetim Raporu (2026-02-15)

## Amaç
Bu rapor, mevcut sistemin çekirdek çalışma alanını tanımlar ve **MVP+ / canlıya hazırlık uygulamalarına dokunmadan** sadeleştirme yapılması için sınırları netleştirir.

## Karar (Kritik)
- Aşağıdaki uygulamalar **kaldırılmayacak**.
- Çekirdekleştirme, kod/sistem silme değil; operasyonel sadeleştirme, çalışma profili, script odaklı kullanım ve gereksiz süreçlerin pasifleştirilmesi şeklinde yapılacak.

## Mevcut Aktif Uygulama Envanteri
`services/backend/project/settings/base.py` içindeki uygulamalar:

- `apps.accounts`
- `apps.catalog`
- `apps.records`
- `apps.batches`
- `apps.credits`
- `apps.ledger`
- `apps.payments`
- `apps.exports`
- `apps.disputes`
- `apps.providers`
- `apps.audit`
- `apps.common`

## API Entegrasyonları (Gözlenen)
`services/backend/project/urls.py` içinden:

- Auth: `api/auth/`
- Credits: `api/credits/*`
- Payments: `api/payments/*`
- Catalog: `api/catalog/*`
- Records: `api/records/*`
- Router: `batches`, `exports`, `disputes`, `ledger/entries`

Bu nedenle sistem sadece Maps + Gemini değildir; ödeme/ledger/dispute/export modülleri de aktif mimarinin parçasıdır.

## Çekirdek (Operasyonel) Akış
Şu an veri üretim çekirdeği:
1. Google Places (Text Search + Details)
2. Kayıt/aday yönetimi (`records`, `batches`, `providers`)
3. Website boş kayıtlar için Gemini Search Grounding enrichment
4. Kullanım/token loglama (`artifacts/usage/gemini_grounding_usage.jsonl`)

## Dokunulmayacak Alanlar (No-Touch)
Aşağıdaki alanlar MVP+ / canlı gereksinimleri için korunacak:

- `apps.payments`
- `apps.ledger`
- `apps.credits`
- `apps.disputes`
- `apps.exports`
- `apps.accounts`
- `apps.audit`
- ilgili migration dosyaları
- frontend iskeleti (`services/frontend`)
- altyapı dosyaları (`docker-compose*`, `infra/*`)

## Non-Destructive Çekirdekleştirme Prensibi
- Kod silme yok (özellikle domain app silme yok).
- Feature-flag ve çalışma profili ile sadeleştirme.
- Operasyonel olarak sadece Maps+Gemini hattı çalıştırılabilir; diğer domain modüller hazır bekler.
- Dokümantasyon ve runbook’lar tek merkezden güncel tutulur.

## Bir Sonraki Güvenli Adım
- “Core runtime profile” tanımlanacak:
  - hangi servislerin zorunlu olduğu,
  - hangi endpoint/grup akışlarının opsiyonel olduğu,
  - geliştirme ve canlıda aç/kapa stratejisi.
- Bu adımda da uygulama silinmeyecek, sadece çalışma profili netleştirilecek.

## Uygulanan Sadeleştirme (2026-02-15)
- `docs/` altında işlevsel dokümanlar korundu (ADR, API, RUNBOOKS, geojson).
- Geçici tarayıcı/debug dökümanları temizlendi: `.playwright-mcp/` kaldırıldı.
- Kalıcı hijyen için `.gitignore` güncellendi (`.playwright-mcp`, `playwright-report`, `test-results`, runtime log çıktıları).
