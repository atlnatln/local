# Production Deploy Rehberi (Infrastructure + Projeler)

Bu repo iki ayrı katmanı deploy eder:

- `infrastructure/`: ortak nginx reverse proxy, SSL sertifikaları ve ops bileşenleri
- `projects/*`: proje bazlı deployment (Webimar, Anka)

Not: Projelerin production kuralları proje dizinlerindeki `README.md`/`deploy.sh` ile belirlenir. Bu dosya, “kökten” yaklaşımı özetler.

## Gereksinimler

- Linux VPS
- Docker + docker compose (plugin)
- Domain DNS (A kayıtları) hazırlanmış
- `infrastructure/nginx/conf.d/` altında domain routing ayarları

## 1) Infrastructure Kurulumu

```bash
cd /home/akn/vps/infrastructure
sudo ./setup.sh --ssl
```

Sağlık kontrolü:

```bash
curl -f http://localhost:8080/nginx-health
```

## 2) Webimar Deploy

Webimar deploy akışı proje dizininden yürütülür:

```bash
cd /home/akn/vps/projects/webimar
./deploy.sh
```

## 3) Anka Deploy

Anka deploy akışı proje dizininden yürütülür:

```bash
cd /home/akn/vps/projects/anka
./deploy.sh
```

## Operasyonel Komutlar

- Infrastructure: `cd /home/akn/vps/infrastructure && docker compose ps`
- Proje logları:
  - `cd /home/akn/vps/projects/webimar && docker compose logs -f`
  - `cd /home/akn/vps/projects/anka && docker compose logs -f`

## Sorun Giderme

- Nginx config testi: `docker exec vps_nginx_main nginx -t`
- Çalışan portlar: `ss -ltnp | grep -E ':(80|443|8080|3000|3001|3100|8001|8100)\b'`