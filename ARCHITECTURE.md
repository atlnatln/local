# Mimari (Özet)

Bu repo 3 katmanlı bir yapıyı yönetir:

1) `infrastructure/`: ortak reverse proxy (nginx), SSL (certbot) ve ops/monitoring bileşenleri
2) `projects/*`: her biri kendi stack’ine sahip bağımsız projeler (örn. Webimar, Anka)
3) `scripts/` ve kök `dev-*.sh`: geliştirme/operasyon orkestrasyonu

## Ağ Topolojisi

- Infrastructure tarafında ortak bir Docker ağı kullanılır: `vps_infrastructure_network`.
- Proje servisleri (gerekli olduğu ölçüde) bu ağa bağlanır; böylece infra nginx upstream’lere konteyner adıyla erişebilir.

## Yerel Docker Geliştirme Portları (Mevcut Ayar)

- Infrastructure: `80`, `443`, `8080` (health)
- Webimar:
    - Next.js: `3000`
    - React SPA: `3001`
    - API: `8001` (örn. `http://localhost:8001/api/`)
- Anka:
    - Frontend: `3100`
    - Backend: `8100`

Not: Production’da erişim genelde domain + infra nginx üzerinden yönetilir (örn. `/api` reverse-proxy). Localde ise hem doğrudan portlarla hem de infra üzerinden test edilebilir.