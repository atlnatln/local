# Çoklu Web Projesi Sistemi (Webimar + Anka)

Bu doküman, monorepo içinde birden çok web projesini **bağımsız deploy** ederken ortak edge (Nginx) katmanını nasıl yöneteceğimizi açıklar.

## Hedef Mimari

- **Tek edge sahibi**: `infrastructure` içindeki `vps_nginx_main` containerı (80/443).
- **Proje bağımsızlığı**:
  - `projects/webimar/deploy.sh` yalnız Webimar stack’ini yönetir.
  - `projects/anka/deploy.sh` yalnız Anka stack’ini yönetir.
- **Ortak ağ**: `vps_infrastructure_network`.
  - Edge nginx bu ağda.
  - Projelerin nginx servisleri bu ağa bağlı.

## Trafik Akışı

- `tarimimar.com.tr` -> `vps_nginx_main` -> `webimar-nginx` (container DNS üzerinden)
- `ankadata.com.tr` -> `vps_nginx_main` -> `anka_nginx_prod` (container DNS üzerinden)

Not: `infrastructure/nginx/conf.d/*.conf` dosyalarında upstream hedefleri `localhost`/host port yerine container DNS adıyla tanımlanmalıdır.

## Deploy Bağımsızlığı Kuralları

1. Proje deploy scripti başka projenin compose dosyasını, containerını veya volume’unu değiştirmez.
2. `docker image prune -a` / `docker volume prune` gibi global temizleme komutları kullanılmaz.
3. Edge katmana müdahale yalnız ilgili domain conf dosyası ile yapılır:
   - Webimar: `infrastructure/nginx/conf.d/webimar.conf`
   - Anka: `infrastructure/nginx/conf.d/anka.conf`
4. Deploy sonrası edge reload standardı:
   - `nginx -t`
   - `nginx -s reload`

## Local Geliştirme (Sorunsuz Çalışma)

Önerilen akış Docker ile:

- Tam stack: `./dev-docker.sh`
- Sadece projeler: `bash scripts/up.sh`

Nokta atışı kural: Host’a publish edilen portlar çakışmamalı. Ayrıntı için:
- `docs/LOCAL_COMPOSE_NOTLARI.md`

## Ne Zaman Infrastructure Revizyonu Gerekir?

Aşağıdaki durumlarda `infrastructure/` güncellenir:

- Yeni domain/yeni proje ekleniyorsa
- TLS/sertifika yolu veya edge güvenlik politikası değişiyorsa
- Ortak yönlendirme kuralı (rate limit, header, cache) güncellenecekse

Aşağıdaki durumlarda **gerekmez**:

- Sadece Webimar uygulama kodu/deploy değişikliği
- Sadece Anka uygulama kodu/deploy değişikliği

## Yeni Proje Ekleme Kısa Checklist

1. `projects/<yeni-proje>/docker-compose.prod.yml` hazırla.
2. Proje nginx servisini ekle ve `vps_infrastructure_network` ağına bağla.
3. `infrastructure/nginx/conf.d/<yeni-proje>.conf` domain route ekle.
4. Sertifikayı `infrastructure/ssl/<domain>/` altında hazırla.
5. `vps_nginx_main` için `nginx -t && nginx -s reload` çalıştır.

## Operasyonel Doğrulama

- `docker ps` ile 80/443 yalnız `vps_nginx_main` üzerinde mi?
- Domain başlıkları ve sertifika CN/SAN doğru mu?
- `curl -L` ile root endpoint final 200/302 beklenen akışta mı?

