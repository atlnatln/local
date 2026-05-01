---
title: "SSL Automation"
created: "2026-05-01"
updated: "2026-05-01"
type: concept
tags: [infrastructure, ssl, security, automation, certbot]
related:
  - infrastructure
  - nginx-routing
  - deployment
sources: []
---

# [[SSL-Automation]]

Let's Encrypt sertifikalarının otomatik edinimi, yenilenmesi ve nginx'e entegrasyonu.

## Purpose

Tüm production domain'leri (ankadata.com.tr, tarimimar.com.tr, mathlock.com.tr) için ücretsiz SSL sertifikalarını otomatik yönetmek. Manuel müdahale olmadan sürekli HTTPS sağlamak.

## Stack

| Bileşen | Görev |
|---------|-------|
| Certbot | Let's Encrypt client (ACME protokolü) |
| `renew-ssl.sh` | Ana yenileme script'i |
| `ssl-cron-setup.sh` | Cron job kurulumu |
| `ssl/` dizini | Sertifika dosyaları (container'a mount) |
| `vps_certbot_webroot` | ACME challenge webroot volume |

## Sertifika Yapısı

```
infrastructure/ssl/
├── ankadata.com.tr/
│   ├── fullchain.pem    # Sertifika + ara sertifikalar
│   └── privkey.pem      # Özel anahtar
├── tarimimar.com.tr/
│   ├── fullchain.pem
│   └── privkey.pem
├── mathlock.com.tr/
│   ├── fullchain.pem
│   └── privkey.pem
└── default/
    ├── cert.pem         # Dummy sertifika (default server)
    └── key.pem
```

## Yenileme Akışı

### 1. Certbot Modları

| Mod | Durum | Kullanım |
|-----|-------|----------|
| **webroot** | nginx çalışıyorsa | ACME challenge `/var/www/certbot` üzerinden |
| **standalone** | nginx durmuşsa | Port 80'i geçici olarak kullanır |

### 2. renew-ssl.sh Akışı

```
Root kontrolü
    ↓
Certbot kurulu mu?
    ↓
nginx container çalışıyor mu? → Mod seç (webroot / standalone)
    ↓
certbot renew --quiet --non-interactive
    ↓
Başarılı mı? → nginx reload (sertifika yeniden yükle)
    ↓
Log yaz
```

### 3. Cron Zamanlaması

```cron
# Her gece 02:30
30 2 * * * root bash /home/akn/vps/infrastructure/renew-ssl.sh >> /var/log/ssl-renew.log 2>&1
```

- Son 30 gün içinde dolacak sertifikaları yeniler
- Günlük çalışır ama sadece gerektiğinde yenileme yapar

## Komutlar

```bash
# Manuel yenileme
sudo bash /home/akn/vps/infrastructure/renew-ssl.sh

# Zorla yenileme (test için)
sudo bash /home/akn/vps/infrastructure/renew-ssl.sh --force

# Log takibi
tail -f /var/log/ssl-renew.log

# Sertifika bilgisi
sudo certbot certificates

# Sertifika testi (SSL Labs)
# https://www.ssllabs.com/ssltest/analyze.html?d=ankadata.com.tr
```

## Kurulum (Bir Kez)

```bash
sudo bash /home/akn/vps/infrastructure/ssl-cron-setup.sh
```

Bu script:
1. `renew-ssl.sh`'e çalıştırma izni verir
2. Log dosyası oluşturur
3. `/etc/cron.d/vps-ssl-renewal` dosyasını yazar

## nginx Entegrasyonu

Sertifika yenileme sonrası nginx reload gereklidir:

```bash
# Container içinden
docker exec vps_nginx_main nginx -s reload

# Veya compose ile
cd /home/akn/vps/infrastructure && docker compose exec nginx_proxy nginx -s reload
```

`renew-ssl.sh` bunu otomatik yapar (webroot modunda).

## Güvenlik Notları

- Sertifika dosyaları container'a **read-only** mount edilir (`:ro`)
- `privkey.pem` sadece root/nginx kullanıcısı tarafından okunabilir
- Standalone modda nginx geçici olarak durdurulur (~30 sn kesinti riski)
- Webroot modu **zero-downtime**'dır

## Dependencies

- [[infrastructure]] — Docker container, volume mount'ları
- [[nginx-routing]] — SSL config'i kullanan nginx server block'ları
- [[deployment]] — nginx reload deploy prosedürü

## Troubleshooting

| Sorun | Çözüm |
|-------|-------|
| "certbot bulunamadı" | Script otomatik kurar |
| nginx container down | Standalone moda geçer, sonra yeniden başlatır |
| Sertifika yenilenmedi | `--force` ile zorla, logları kontrol et |
| 444 connection dropped | Default server SSL hatası — dummy sertifika kontrolü |
