# Güvenlik İhlali Müdahale Planı (Incident Response Playbook)

**Son Güncelleme:** 28 Şubat 2026  
**Sahip:** DevOps / Backend Ekibi  
**Gözden Geçirme Sıklığı:** 6 ayda bir

---

## 1. Amaç

Bu belge, Anka Platform'da güvenlik ihlali (security incident) tespit edildiğinde izlenecek adım adım müdahale prosedürlerini tanımlar.

## 2. Olay Seviye Tanımları

| Seviye | Tanım | Örnek | SLA |
|--------|-------|-------|-----|
| **SEV-1 (Kritik)** | Aktif veri sızıntısı veya sistem kompromize | DB erişimi elde edilmiş, JWT secret sızmış | 15 dk müdahale |
| **SEV-2 (Yüksek)** | Potansiyel veri erişimi, exploit girişimi | Brute-force başarılı, API key kötüye kullanım | 1 saat müdahale |
| **SEV-3 (Orta)** | Zafiyet keşfi, başarısız saldırı girişimi | Vulnerability scan tespiti, failed login flood | 4 saat müdahale |
| **SEV-4 (Düşük)** | Konfigürasyon hatası, policy ihlali | Açık port, expired certificate | 24 saat müdahale |

## 3. İlk Tespit ve Bildirim

### 3.1 Tespit Kaynakları
- Nginx access/error log'ları
- Django/Sentry hata raporları
- Prometheus/alertmanager bildirimleri
- ops-bot/sec-agent otomatik tarama
- Kullanıcı bildirimi
- Üçüncü parti güvenlik tarayıcıları

### 3.2 İlk Adımlar (İlk 15 dakika)

```
1. [ ] Olayı doğrula (false positive mi?)
2. [ ] Olayın seviyesini belirle (SEV-1/2/3/4)
3. [ ] Olay log kaydı oluştur (tarih, saat, kaynak, açıklama)
4. [ ] İlgili kişileri bilgilendir
5. [ ] Slack/iletişim kanalında #incident-{tarih} thread'i aç
```

## 4. Müdahale Prosedürleri

### 4.1 SEV-1: Aktif Veri Sızıntısı

```bash
# ADIM 1: Sistemi izole et
cd /home/akn/vps/projects/anka
docker compose -f docker-compose.prod.yml stop nginx frontend
# Backend'i durdurmak yerine sadece dış trafiği kesin

# ADIM 2: Mevcut oturumları sonlandır
docker exec anka_backend_prod python manage.py shell -c "
from django.contrib.sessions.models import Session
Session.objects.all().delete()
print('Tüm oturumlar sonlandırıldı')
"

# ADIM 3: JWT secret'ı rotate et (tüm mevcut token'ları geçersiz kılar)
# .env.production'da SECRET_KEY değiştir
# docker compose -f docker-compose.prod.yml restart backend celery_worker celery_beat

# ADIM 4: Veritabanı erişim loglarını kontrol et
docker logs anka_postgres_prod --since="1h" | grep -i "error\|failed\|denied"

# ADIM 5: Redis'i flush et (cache temizliği)
docker exec anka_redis_prod redis-cli FLUSHALL
```

### 4.2 SEV-2: API Key Kötüye Kullanımı

```bash
# ADIM 1: Etkilenen API key'i belirle
grep -r "GOOGLE_PLACES_API_KEY\|GOOGLE_MAPS_API_KEY" .env.production

# ADIM 2: GCP Console'dan key'i kısıtla / revoke et
# https://console.cloud.google.com/apis/credentials

# ADIM 3: Yeni key oluştur ve .env.production'ı güncelle
# vim .env.production

# ADIM 4: Servisleri yeniden başlat
docker compose -f docker-compose.prod.yml restart backend celery_worker frontend

# ADIM 5: Kullanım loglarını denetle
# GCP Console > APIs & Services > Metrics
```

### 4.3 SEV-2: Brute-Force / Credential Stuffing

```bash
# ADIM 1: Nginx rate limiting kontrolü
docker exec anka_nginx_prod cat /var/log/nginx/error.log | grep "limiting" | tail -20

# ADIM 2: Saldırgan IP'yi belirle
docker logs anka_nginx_prod --since="1h" | awk '{print $1}' | sort | uniq -c | sort -rn | head -20

# ADIM 3: IP'yi UFW ile engelle (VPS seviyesi)
sudo ufw deny from <SALDIRGAN_IP> to any

# ADIM 4: Nginx deny listesine ekle
# infrastructure/nginx/conf.d/ altına deny kuralı ekle
# nginx -s reload
```

### 4.4 SEV-3: Zafiyet Keşfi (Vulnerability)

```
1. [ ] Zafiyetin kapsamını değerlendir (hangi servisler etkileniyor?)
2. [ ] CVE numarasını ve CVSS skorunu kontrol et
3. [ ] Geçici mitigation (WAF kuralı, rate limit, endpoint disable)
4. [ ] Kalıcı fix planlama (patch, upgrade)
5. [ ] Fix deploy ve doğrulama
6. [ ] Güvenlik denetim belgesine kayıt
```

## 5. İleti̇şi̇m Şablonu

```
🔴 GÜVENLİK OLAYI — SEV-{X}
━━━━━━━━━━━━━━━━━━━━━━━━━━
Tarih/Saat: {YYYY-MM-DD HH:MM UTC+3}
Tespit Eden: {kaynak}
Etkilenen Sistem: {servis adı}
Açıklama: {kısa açıklama}
Mevcut Durum: {Araştırılıyor / İzole Edildi / Çözüldü}
Sorumlu: {isim}
Sonraki Güncelleme: {zaman}
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 6. Olay Sonrası (Post-Mortem)

Her SEV-1 ve SEV-2 olayından sonra 48 saat içinde post-mortem belgesi hazırlanır:

```markdown
# Post-Mortem: {Olay Başlığı}

## Özet
- Olay tarihi:
- Tespit süresi:
- Çözüm süresi:
- Etkilenen kullanıcı sayısı:

## Kronoloji
| Zaman | Olay |
|-------|------|
| HH:MM | ... |

## Kök Neden Analizi
{5 Neden Analizi (5 Whys)}

## Alınan Dersler
1. ...

## Aksiyon Maddeleri
| Aksiyon | Sorumlu | Hedef Tarih | Durum |
|---------|---------|-------------|-------|
| ... | ... | ... | ... |
```

## 7. Periyodik Tatbikat

- **Sıklık:** 6 ayda bir
- **Kapsam:** SEV-1 senaryosu simülasyonu
- **Katılımcılar:** Tüm teknik ekip
- **Çıktı:** Tatbikat raporu ve plan güncellemesi

## 8. İlgili Belgeler

- [Secret Rotation Runbook](secret-rotation-runbook.md)
- [Hardening Checklist](hardening-checklist.md)
- [KVKK Data Compliance](kvkk-data-compliance.md)
