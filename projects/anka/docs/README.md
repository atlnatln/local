# Anka Docs — Minimal Çekirdek

Bu klasör yalnızca projeyi hızla anlamak ve güvenli işletmek için gereken kanonik doküman setini içerir.

## Hızlı Başlangıç (Önerilen sıra)

1. `ADR/0001-architecture-api-frontend-split.md`
2. `ADR/0006-three-stage-verification-pipeline.md`
3. `API/openapi.yaml`
4. `RUNBOOKS/README.md`
5. `SECURITY/README.md`

## Aktif Doküman Alanları

- `ADR/` — Mimari karar kayıtları
- `API/openapi.yaml` — API sözleşmesi (kanonik)
- `RUNBOOKS/` — Güncel operasyon runbook’ları
- `SECURITY/` — Aktif güvenlik politika ve prosedürleri
- `google-maps-bilgiler.md` — Harita sağlayıcı notları
- `turkey-districts.geojson` — Grid/ilçe sınır veri kaynağı

## Öncelik Kuralı

Doküman-kod çelişkisinde sıralama:
1. Çalışan kod ve scriptler
2. `API/openapi.yaml`
3. ADR
4. Runbook / Security

## Güncelleme Politikası

- API değişiminde: `API/openapi.yaml`
- Mimari karar değişiminde: yeni ADR
- Operasyon değişiminde: ilgili runbook
- Güvenlik değişiminde: ilgili security policy/runbook
