---
name: seg-agent
description: "Telegram güvenlik raporlarını analiz et, sec-agent sistemindeki hata ve geliştirme fırsatlarını tespit et"
---

# sec-agent Telegram Rapor Analiz Prompt'u

Bu prompt ile kullanıcı sana günlük Telegram güvenlik rapor mesajlarını yapıştıracak. Senin görevin:
1. Raporları dikkatle oku ve anomalileri tespit et
2. sec-agent sisteminin **hatalarını** bul (yanlış tespit, kaçırılan saldırgan, state tutarsızlığı vb.)
3. **Geliştirme fırsatlarını** yakala (yeni pattern'ler, eksik flag'ler, tuning gereklilikleri)
4. Gerektiğinde kod değişikliği yap ve deploy et

---

## 1. SİSTEM MİMARİSİ

### Genel Yapı
sec-agent, VPS (89.252.152.222) üzerinde çalışan timeline-based bir güvenlik tarama sistemidir. Her 5 dakikada bir systemd timer ile tetiklenir, log dosyalarını okur, IP'leri puanlar, karar verir ve gerektiğinde UFW firewall kuralı ekler.

### Çalışma Ortamı
- **VPS IP:** 89.252.152.222
- **VPS Kullanıcısı:** akn
- **SSH bağlantısı:** `ssh akn@89.252.152.222`
- **sec-agent dizini (VPS):** `/opt/sec-agent/`
- **Kaynak kodu (lokal):** `/home/akn/vps/ops-bot/sec-agent/`
- **systemd unit'leri (lokal):** `/home/akn/vps/ops-bot/systemd/`
- **Telegram rapor scripti (lokal):** `/home/akn/vps/ops-bot/scripts/critical_security_alert.py`
- **Deploy komutu:** `cd /home/akn/vps/ops-bot && bash deploy.sh --skip-github`

### Pipeline Akışı (her 5 dakikada)
1. Config yükleme (agent.yaml, sources.yaml, scoring.yaml, thresholds.yaml, known-bots.yaml)
2. SQLiteStateStore (ip_state) başlatma
3. Lock alma (`store/sec-agent-once.lock`)
4. Süresi dolmuş blok/ratelimit temizleme + yetim UFW kural reconcile
5. IP state pruning (zamana dayalı + LRU eviction)
6. Pasif decay sweep (tüm IP'lere decay uygula)
7. events.jsonl rotasyonu (100MB eşik)
8. Event toplama (nginx, sshd, docker loglarından)
9. Her event için: normalize → flag hesapla → skora → karar ver → uygula
10. State flush (SQLite'a yaz) + JSON export + offset kaydet
11. Auto-unblock false positive kontrolü
12. Metrics snapshot

### Çalıştırma Modeli
- **systemd timer:** `sec-agent.timer` → her 5dk `sec-agent-once.service` başlatır
- **Type=oneshot:** Her çalışma bağımsız, öncekini beklemez (lock ile koruma)
- **User=root:** Docker volume log'ları ve UFW için root gerekli
- **TimeoutStartSec=30min:** Büyük batch'ler için (81k event → ~15dk işlem süresi)
- **SIGTERM handler:** systemd timeout'ta SIGTERM gönderir → handler SystemExit raise eder → finally bloğu state flush + offset kaydetme yapar

---

## 2. PUANLAMA (SCORING)

### Puan Kuralları (scoring.yaml)
| Flag | Puan | Açıklama |
|------|------|----------|
| suspicious_user_agent | 10 | curl, wget, sqlmap, scanner, bot |
| repeated_404 | 5 | 404 yanıtları |
| exploit | 25 | exploit_path veya exploit_payload |
| forbidden_path | 60 | .env, .git, wp-admin, .php vb. |
| malware_payload | 90 | device.rsp, systembc, arm7, wget/curl http |
| bruteforce | 15 | SSH auth failure |
| high_volume | 2 | 500+ event eşiğinden sonra HER event başına |

### Score Cap
- **max_ip_score:** 10000 (astronomik birikim önleme)

### Decay
- **Oran:** 10 puan/saat (lineer)
- **Uygulama:** Her event işlenmeden önce elapsed süreye göre decay uygulanır

### Özel Davranışlar
- **known_good_bot:** Score her zaman 0, classification=benign (Googlebot, Bingbot vb.)
- **benign_bot:** Statik score (birikim yok), P0 guardrail ile BLOCK yapılamaz
- **high_volume:** event_count >= 500 olunca tetiklenir, volumetrik saldırı tespiti

---

## 3. FLAG TİPLERİ

| Flag | Tetikleyici |
|------|-------------|
| exploit_path | SUSPICIOUS_PATHS listesindeki yollara erişim (/wp-admin, /etc/passwd vb.) |
| exploit_payload | SQL injection pattern'leri (union+select, drop+table vb.) |
| forbidden_path | FORBIDDEN_REGEX ile eşleşen yollar |
| malware_payload | Malware göstergeleri (device.rsp, systembc, arm7) |
| bruteforce | SSH auth failure |
| automation | Şüpheli User-Agent (curl, wget, python-requests, sqlmap) |
| known_good_bot | ignore.yaml allowlist'teki IP (CIDR), UA tek başına yetmez |
| benign_bot | BotDetector analizi sonucu |
| bot_threat_score | Bot tehdit skoru (0-100 ölçeği) |

### FORBIDDEN_REGEX
```
\.env|\.git|web\.config|config\.php|settings\.py|\.htaccess|\.passwd|/admin\b|
/administrator|/wp-admin|/wp-login|/phpmyadmin|/cpanel|/plesk|/node_modules|/vendor|
/app/config|\.sql$|\.bak$|\.backup$|\.tar\.gz$|dump\.rdb|xmlrpc\.php|upl\.php|
password\.php|systembc|cgi-bin|device\.rsp|login\.rsp|setup\.php|install\.php|test\.php|
debug\.php|/shell|/cmd=|\.php
```

---

## 4. KARAR MOTORU (Decision Engine)

### Eşikler
| Aksiyon | Score Eşiği | Min Event | Not |
|---------|-------------|-----------|-----|
| BLOCK | ≥ 80 | ≥ 3 | malware_payload varsa min event yok |
| RATELIMIT | ≥ 50 | ≥ 2 | |
| ALERT | ≥ 30 | — | |
| LOG | < 30 | — | |

### Persistent Attacker (Kalıcı Saldırgan)
- **Kriter:** score ≥ 3000 AND events ≥ 100 (sadece weak signals ile)
- **Weak signals:** automation, repeated_404, high_volume (yani forbidden_path, exploit, malware, bruteforce OLMADAN)
- **Aksiyon:** BLOCK + classification=attacker

### Blok Süre Merdiveni (Escalation Ladder)
| Blok # | Süre | Normal | Persistent Attacker |
|--------|------|--------|---------------------|
| 1. | 60dk (1 saat) | ✓ | 1440dk (24 saat) |
| 2. | 180dk (3 saat) | ✓ | 4320dk (3 gün) |
| 3. | 360dk (6 saat) | ✓ | — |
| 4+ | 1440dk (24 saat) | ✓ | 10080dk (7 gün) |
| 5+ | — | — | 4320dk (3 gün) |
| 10+ | — | — | 10080dk (7 gün) |

### Guardrail'ler
- **Self-protection:** Kendi IP'si (89.252.152.222) ve özel ağlar (127.0.0.0/8, 10.0.0.0/8 vb.) ASLA bloklanmaz
- **Blast radius:** Aynı /24 subnet'te max 5 blok
- **Rate limit:** Saatte max 50 blok, 100 ratelimit
- **Escalation cooldown:** Bloktan sonra 30dk bekleme (yeniden blok için)
- **P0 guardrail:** known_good_bot veya benign_bot ASLA bloklanmaz (SEO koruması)
- **Trusted SSH:** Başarılı SSH → 240dk SSH bypass, 60dk cross-protocol alert-only

---

## 5. STATE YAPISI

### SQLite DB
- **Dosya:** `/opt/sec-agent/store/sec_agent.db` (WAL mode)
- **Tablo:** `ip_state (key TEXT PK, value_json TEXT, updated_at TEXT)`
- **JSON export:** `/opt/sec-agent/store/ip_state.json` (her cycle sonunda)

### IP State Alanları
```python
ip_state[ip] = {
    "score": 123.45,              # Mevcut tehdit puanı
    "events": 42,                 # Toplam event sayısı
    "last_seen": "ISO timestamp", # Son görülme
    "classification": "attacker", # benign/suspicious/attacker

    # Blok (aktifse)
    "blocked": True,
    "blocked_at": "ISO timestamp",
    "blocked_until": "ISO timestamp",
    "block_reason": "...",
    "block_count": 2,             # Toplam blok sayısı (escalation için)
    "firewall_applied": True,

    # Ratelimit (aktifse)
    "ratelimited": True,
    "ratelimited_at": "ISO timestamp",
    "ratelimited_until": "ISO timestamp",

    # Trust (SSH başarılı auth)
    "trusted_ssh_auth": True,
    "trusted_ssh_last_auth": "ISO timestamp",

    # Auto-unblock
    "auto_unblocked": True,
    "auto_unblock_reason": "...",
    "auto_unblock_at": "ISO timestamp"
}
```

### Offset Takibi
```python
seen_offsets = {
    "nginx": {"line_offset": 1234, "size": 567890, "inode": 524288},
    "sshd": {"line_offset": 5678, ...}
}
```
- **Dosya:** `/opt/sec-agent/store/seen_offsets.json`
- Dosya truncate veya inode değişikliğinde reset

---

## 6. LOG DOSYALARI VE KAYNAKLARI

### Girdi (Log Kaynakları)
| Kaynak | VPS Yolu | İçerik |
|--------|----------|--------|
| nginx (webimar) | `/var/lib/docker/volumes/vps_nginx_logs/_data/webimar_access.log` | HTTP trafiği (~273MB) |
| nginx (anka) | `/var/lib/docker/volumes/vps_nginx_logs/_data/anka_access.log` | HTTP trafiği (~4MB) |
| sshd | `/var/log/auth.log` | SSH giriş denemeleri |

### Çıktı (sec-agent logları) — tümü `/opt/sec-agent/` altında
| Dosya | İçerik |
|-------|--------|
| `logs/agent.log` | Pipeline çalışma logu (INFO/WARNING/ERROR) |
| `logs/decision.log` | Her IP kararı (action, score, class, reason) |
| `store/events.jsonl` | İşlenen eventler (flags, score, decision dahil) |
| `store/ip_state.json` | SQLite'ın JSON export'u |
| `store/sec_agent.db` | Ana SQLite veritabanı |
| `store/seen_offsets.json` | Offset durumu |

---

## 7. TELEGRAM RAPOR FORMATI

### Rapor oluşturma
- **Script:** `scripts/critical_security_alert.py`
- **Timer:** `ops-bot-critical-alert.timer` → her gün 08:00 İstanbul saati
- **Pencere:** Son 24 saat (CRITICAL_WINDOW_MINUTES=1440)
- **Mode:** DAILY_DIGEST_MODE=true

### Rapordaki Alanlar
| Alan | Kaynak | Açıklama |
|------|--------|----------|
| **Tehdit Seviyesi** | Event/blok sayısı | 🔴YÜKSEK (≥100 kritik event veya ≥30 blok), 🟡ORTA (≥30 event veya ≥10 blok), 🟢DÜŞÜK |
| **Toplam event** | decision.log son 24s | Tüm işlenen eventler |
| **Benzersiz IP** | decision.log | Farklı IP sayısı |
| **Kritik event** | decision.log score≥90 | Yüksek skoru eventler |
| **BLOCK** | decision.log action=block | Penceredeki blok kararları |
| **RATELIMIT** | decision.log action=ratelimit | Penceredeki ratelimit kararları |
| **Aktif blok** | ip_state.json blocked=true | ŞU AN aktif bloklama sayısı |
| **Kalıcı Saldırganlar** | ip_state.json | score≥1000 AND events≥50 VEYA (blocked AND events≥20) |
| **En Aktif IP'ler** | decision.log | En çok event üreten IP'ler |
| **Tekrar Eden Saldırganlar** | Son 72 saat decision.log | 2+ farklı zaman penceresinde görülen IP'ler |
| **Kaynak Dağılımı** | decision.log | HTTP / SSH / Other dağılımı |

### Dikkat Edilecek Anomaliler
- **Aktif blok=0 ama BLOCK sayısı yüksek:** State flush problemi (SIGTERM, timeout)
- **"Kalıcı Saldırganlar: yok" ama binlerce event:** State persistence sorunu
- **Bir IP toplam trafiğin %90+'ını oluşturuyor:** Volumetrik saldırı veya stuck client
- **block_count hep 1:** Escalation çalışmıyor (state kaybı)
- **Aynı IP her gün raporda:** Blok süresi yeterli değil, escalation gerekli
- **IP skoru 0 ama binlerce event'i var:** Decay çok hızlı veya state sıfırlanmış
- **PHP/webshell path'leri (cabs.php, xwx1.php) yakalanmadı:** FORBIDDEN_REGEX eksik
- **Persistent attacker ALERT'leri bloklanmamış ama `guardrail: escalation_cooldown` yazıyor:** `decide()`'da `already_blocked` kontrolü `weak_signals_only` path'inde atlanıyor (düzeltildi 2026-04-28)
- **decision.log'da `BLOCK` yok ama state'te `block_count > 0`:** Eski log rotate edilmiş olabilir. `zgrep` ile `.gz` arşivlerini de kontrol et

---

## 8. VPS İNCELEME KOMUTLARI

Rapordaki bir anomaliyi araştırmak için kullanacağın komutlar:

### Temel Durum Kontrolü
```bash
# sec-agent servisi çalışıyor mu?
ssh akn@89.252.152.222 "systemctl status sec-agent-once.service --no-pager | head -12"

# Timer aktif mi?
ssh akn@89.252.152.222 "systemctl status sec-agent.timer --no-pager | head -8"

# Son çalışma ne zaman oldu?
ssh akn@89.252.152.222 "journalctl -u sec-agent-once.service --no-pager -n 5"

# Timeout/SIGTERM oluştu mu?
ssh akn@89.252.152.222 "journalctl -u sec-agent-once.service --no-pager | grep -i 'timed out\|SIGTERM\|killed\|timeout'"
```

### IP Araştırma
```bash
# Belirli bir IP'nin state'ini kontrol et
ssh akn@89.252.152.222 "python3 -c \"
import json
with open('/opt/sec-agent/store/ip_state.json') as f:
    data = json.load(f)
ip = '95.70.138.188'
print(json.dumps(data.get(ip, 'NOT FOUND'), indent=2))
\""

# Belirli IP'nin decision.log'daki kararları
ssh akn@89.252.152.222 "grep '95.70.138.188' /opt/sec-agent/logs/decision.log | tail -5"

# Belirli IP'nin kaç kez bloklandığını bul
# NOT: decision.log formati 'BLOCK <ip>' seklinde (action=block icermez)
ssh akn@89.252.152.222 "grep 'BLOCK 95.70.138.188' /opt/sec-agent/logs/decision.log | wc -l"

# Belirli IP'nin nginx erişim logundaki istekleri
ssh akn@89.252.152.222 "grep '95.70.138.188' /var/lib/docker/volumes/vps_nginx_logs/_data/webimar_access.log | tail -10"
```

### Genel İstatistikler
```bash
# Aktif blokları göster
ssh akn@89.252.152.222 "python3 -c \"
import json
with open('/opt/sec-agent/store/ip_state.json') as f:
    data = json.load(f)
blocked = {k: v for k, v in data.items() if v.get('blocked')}
for ip, state in blocked.items():
    print(f'{ip}: score={state.get(\"score\",0)}, events={state.get(\"events\",0)}, until={state.get(\"blocked_until\",\"?\")}, count={state.get(\"block_count\",0)}')
\""

# UFW kurallarını göster
ssh akn@89.252.152.222 "sudo ufw status | grep DENY | head -20"

# decision.log boyutu ve satır sayısı
ssh akn@89.252.152.222 "wc -l /opt/sec-agent/logs/decision.log; ls -lh /opt/sec-agent/logs/decision.log"

# Logrotate durumu
ssh akn@89.252.152.222 "sudo logrotate -d /etc/logrotate.d/sec-agent 2>&1 | head -5"

# events.jsonl boyutu
ssh akn@89.252.152.222 "ls -lh /opt/sec-agent/store/events.jsonl"

# SQLite db boyutu
ssh akn@89.252.152.222 "ls -lh /opt/sec-agent/store/sec_agent.db"
```

---

## 9. DEPLOY SÜRECİ

### Kod Değişikliği → Deploy
1. Lokal dosyaları düzenle (`/home/akn/vps/ops-bot/sec-agent/` veya `scripts/` veya `systemd/`)
2. Testleri çalıştır: `cd /home/akn/vps/ops-bot/sec-agent && pytest tests/ -v`
3. Commit: `cd /home/akn/vps && git add -A && git commit -m "sec-agent: açıklama"`
4. Deploy: `cd /home/akn/vps/ops-bot && bash deploy.sh --skip-github`
5. Doğrulama: VPS'te servis durumu ve log kontrolü

### Deploy Script Detayları
- SSH multiplexing kullanır (UFW rate-limit tetiklemesini önler)
- Package mode: tar.gz oluşturur, SCP ile VPS'e gönderir, setup.sh çalıştırır
- setup.sh VPS'te: venv kurar, systemd unit'leri kopyalar, sec-agent kodunu `/opt/sec-agent/`'a günceller, timer'ları aktifler, tek seferlik test çalıştırması yapar
- **DİKKAT:** Deploy sırasında `sec-agent-once.service` başlatılır, büyük backlog varsa uzun sürebilir

### Dosya Sahiplik Kuralları
- Kod (actions, collectors, engine, bin, vb.): **root:root** (güvenlik)
- Config: **akn:akn**
- Data (store, logs, runtime): **akn:akn**

---

## 10. BİLİNEN SORUNLAR VE GEÇMİŞ DÜZELTMELERİ

### Düzeltilmiş Hatalar (Tarihçe)
1. **Cloudflare IP sorunu:** X-Forwarded-For header'ından gerçek IP çıkarma (CF proxy IP'leri bloklanıyordu)
2. **Progressive escalation:** Blok süresi merdiveni eklendi (60→180→360→1440dk)
3. **Volumetrik skor:** high_volume=+2/event (500 eşik) eklendi
4. **PHP webshell tespiti:** `.php` FORBIDDEN_REGEX'e eklendi
5. **SIGTERM timeout döngüsü:** 10dk→30dk timeout, SIGTERM handler eklendi (SystemExit → finally çalışır)
6. **Persistent attacker report:** `_count_persistent_attackers` relaxed (classification zorunluluğu kaldırıldı)
7. **Fail2Ban coexistence:** REJECT vs DENY ayrımı düzeltildi (is_blocked sadece DENY sayar)
8. **Yetim UFW kuralları:** `_reconcile_orphan_firewall_rules` eklendi
9. **events.jsonl rotasyon:** 200MB→100MB eşik, 100k→50k satır
10. **Bot P0 guardrail:** known_good_bot/benign_bot ASLA bloklanmaz

### Bilinen Kısıtlamalar
- decision.log logrotate: `size 50M, copytruncate, daily, rotate 7` — yoğun dönemlerde 154MB'ye çıkabilir (daily rotate arasında)
- Büyük batch (~80k event): ~15dk işlem süresi, 30dk timeout'a yaklaşabilir
- Türk Telekom IP'leri (95.70.x.x, 78.189.x.x): Gerçek kullanıcı bot benzeri davranış yapabiliyor (/api/accounts/me/ tekrarlayan istekler)

### Yeni Düzeltilen Hatalar (2026-04-28)
11. **`already_blocked` kontrol sırası:** `decide()`'da `already_blocked` ve `min_events_for_block` kontrolleri `weak_signals_only` path'inden SONRA geliyordu. Bu, zaten bloklu IP'lerin `persistent_attacker` detection'a takılıp gereksiz ALERT loglarına (ve decision.log şişmesine) yol açıyordu. Ayrıca `min_events_for_block` indentation hatası nedeniyle unreachable code olarak kalmıştı. **Fix:** Her iki kontrol `weak_signals_only` path'inden ÖNCEYE taşındı.

---

## 11. ANALİZ YAKLAŞIMI

Telegram rapor(lar)ı yapıştırıldığında şu adımları izle:

### Adım 1: Rapor Okuma
- Her raporun tarihini, tehdit seviyesini ve özet rakamlarını not al
- Günler arası trendleri karşılaştır (event sayısı artıyor mu?)

### Adım 2: Anomali Tespiti
- Normal dışı yüksek/düşük değerler (event spike, 0 aktif blok ama yüksek BLOCK)
- Tek IP'nin dominasyonu (toplam trafiğin %50+'sı)
- Kalıcı saldırgan olması gereken ama "yok" çıkan IP'ler
- Tekrar eden saldırganların blok süresi escalation durumu

### Adım 3: VPS İnceleme
- Anomali tespit ettiysen yukarıdaki komutlarla VPS'ten doğrula
- ip_state, decision.log, agent.log, journalctl kontrol et

### Adım 4: Kök Neden Analizi
- Sorun kodda mı (flag eksik, threshold yanlış, logic hatası)?
- Sorun state'te mi (SIGTERM, corrupt data, stale state)?
- Sorun config'de mi (eşikler çok yüksek/düşük)?

### Adım 5: Düzeltme Önerisi / Uygulama
- Basit tuning: scoring.yaml veya thresholds.yaml değişikliği
- Flag ekleme: engine/flags.py FORBIDDEN_REGEX veya yeni pattern
- Logic düzeltme: engine/decision.py, engine/scorer.py
- Report düzeltme: scripts/critical_security_alert.py
- Testler: sec-agent/tests/ altında ilgili test dosyası

### Adım 6: Takip Listesi Güncelleme (Hafıza)
Her analiz sonunda bu prompt dosyasının en altındaki **AÇIK KONULAR** bölümünü güncelle:
- Çözülen konuları `Durum: kapatıldı` olarak işaretle, not ekle
- Yeni tespit edilen açık konuları ekle
- `Beklemede` olan konuların durumunu yeni rapora göre değerlendir
- Bir sonraki analizde önce bu listeyi oku, takip edilmesi gereken IP'leri ve konuları kontrol et

---

## 11a. AÇIK KONULAR / TAKİP LİSTESİ

Bu bölüm geçmiş analizlerden kalan açık konuları, takip edilmesi gereken IP'leri ve planlanan eylemleri içerir. **Her analiz sonunda güncellenir.**

| ID | Konu | İlk Tespit | Durum | Son Kontrol | Notlar / Eylem |
|----|------|-----------|-------|-------------|----------------|
| TK-001 | 188.132.132.225 tekrar eden saldırgan — 3 pencerede göründü, 3 kez bloklandı (block_count=3), her seferinde 1440dk blok aldı. Blok süresi dolunca tekrar geliyor. | 2026-04-24 | açık | 2026-04-28 | Persistent attacker ladder: 10+ blok → 7 gün. Şu an 3. blokta (24 saat). Eğer tekrar gelirse escalation kritik. Son görülme: 26 Nisan. Bir sonraki raporda hâlâ "Tekrar Edenler" listesinde mi kontrol et. |
| TK-002 | Stale IP'ler state'te birikiyor — 185.177.72.11/66, 188.132.132.225 gibi IP'ler artık aktif değil ama skorları ~9500. IP State sayısı 865'e çıktı. | 2026-04-28 | açık | 2026-04-28 | `prune_ip_state_bounded()` çalışıyor mu? `max_ip_state_entries` değerini kontrol et. Decay uygulanıyor ama pruning daha agresif olabilir. LRU eviction tetikleniyor mu kontrol et. |
| TK-003 | BLOCK sayısı düşük kalıyor — 28 Nisan'da 9 BLOCK (57,908 event'e karşı). | 2026-04-28 | beklemede | 2026-04-28 | `already_blocked` bug'ı düzeltildi (2026-04-28). Bir sonraki raporda BLOCK sayısı normale döndü mü? Kontrol et. Hâlâ düşükse rate limit, blast radius veya threshold ayarlaması gerekebilir. |
| TK-004 | Volumetrik saldırgan rotasyonu — Her gün farklı bir IP dominant: 188.132.132.225 (Nisan 24-26), 176.88.28.225 (Nisan 27), 78.173.48.188 (Nisan 28). Hepsi Türk Telekom altyapısından gibi görünüyor. | 2026-04-28 | açık | 2026-04-28 | Bu IP'lerin hepsi aynı botnet'e mi ait? Subnet pattern'i var mı? (188.132.x, 176.88.x, 78.173.x). Bir sonraki raporda yeni bir dominant IP var mı kontrol et. Türk Telekom IP aralıklarına özel bir guardrail gerekli mi değerlendir. |
| TK-005 | 94.54.4.207 aktif bloklu — 11,880 event, skor 9885, 24 saatlik blok (28 Nisan 06:43). | 2026-04-28 | açık | 2026-04-28 | Blok süresi 29 Nisan 06:43'te doluyor. Bir sonraki raporda bu IP hâlâ saldırıyor mu? Tekrar bloklandı mı? Takip et. |


## 12. DOSYA YAPISI

```
ops-bot/sec-agent/
├── bin/
│   ├── sec-agent-once              # Wrapper (run-with-snapshot.sh ile)
│   ├── sec-agent-once.real         # Ana pipeline kodu (Python)
│   └── sec-agent-metrics           # Prometheus metrics (port 9101)
├── config/
│   ├── agent.yaml                  # Ana konfig
│   ├── scoring.yaml                # Puan kuralları
│   ├── thresholds.yaml             # Karar eşikleri + escalation
│   ├── sources.yaml                # Log kaynakları
│   ├── known-bots.yaml             # Bot tanımlama kuralları
│   ├── ignore.yaml                 # Whitelist (CIDR'lar)
│   └── ignore.generated.yaml       # Otomatik üretilen whitelist
├── engine/
│   ├── scorer.py                   # Puanlama + decay
│   ├── flags.py                    # Flag hesaplama
│   ├── decision.py                 # Karar motoru
│   ├── decay.py                    # Pruning + LRU eviction
│   ├── guardrails.py               # Güvenlik sınırları
│   └── sqlite_store.py             # SQLite state store + DirtyDict
├── actions/
│   ├── block.py                    # UFW blok + escalation
│   └── ratelimit.py                # Ratelimit aksiyonu
├── collectors/
│   ├── nginx_collector.py          # Nginx log parser
│   ├── sshd_collector.py           # SSH auth log parser
│   └── docker_collector.py         # Docker container log parser
├── normalizers/
│   └── normalizer.py               # Raw event → standart format
├── tests/                          # pytest testleri (~250+)
├── store/                          # (VPS'te) Çalışma verisi - deploy'da kopyalanMAZ
├── logs/                           # (VPS'te) Log dosyaları - deploy'da kopyalanMAZ
└── runtime/                        # (VPS'te) PID/lock - deploy'da kopyalanMAZ

ops-bot/scripts/
├── critical_security_alert.py      # Günlük Telegram raporu
└── ...

ops-bot/systemd/
├── sec-agent-once.service          # Oneshot service (root, 30dk timeout)
├── sec-agent.timer                 # 5dk timer
├── sec-agent-whitelist.service     # Haftalık whitelist güncelleme
├── sec-agent-whitelist.timer       # Pazar 04:00 UTC
├── ops-bot-critical-alert.service  # Günlük rapor servisi
└── ops-bot-critical-alert.timer    # 08:00 İstanbul
```

---

## 13. TEST ÇALIŞTIRMA

```bash
# Tüm testleri çalıştır (~250+ test)
cd /home/akn/vps/ops-bot/sec-agent && PYTHONPATH=/home/akn/vps/ops-bot/sec-agent python3 -m pytest tests/ -v

# Belirli test dosyası
PYTHONPATH=/home/akn/vps/ops-bot/sec-agent python3 -m pytest tests/test_scorer.py -v

# Belirli test
PYTHONPATH=/home/akn/vps/ops-bot/sec-agent python3 -m pytest tests/test_engine.py -v -k "test_scoring_decision"

# Coverage
PYTHONPATH=/home/akn/vps/ops-bot/sec-agent python3 -m pytest tests/ --cov=engine --cov=actions --cov-report=term-missing
```

---

## ÖNEMLİ NOTLAR

- **Rapor verileri şişirme:** Telegram mesajındaki bilgileri olduğu gibi analiz et. Gereksiz alarm verme, ama gerçek anomalileri kaçırma.
- **Değişiklik yapmadan önce:** İlgili dosyayı oku, mevcut logic'i anla, testleri çalıştır.
- **Deploy sonrası:** VPS'te servis durumunu kontrol et, bir sonraki raporda düzeltmenin etkisini takip et.
- **Türk IP'leri:** 78.189.x.x, 95.70.x.x gibi Türk Telekom IP'leri bazen gerçek kullanıcılar olabilir (bot benzeri davranış: /api/accounts/me/ tekrar). Dikkatli ol.
- **decision.log vs ip_state:** decision.log pencere içi anlık kararları gösterir; ip_state.json ŞU ANKİ kalıcı durumu gösterir. İkisi farklı şeylerdir.
- **Her zaman testleri çalıştır:** Kod değişikliği sonrası `pytest tests/ -v` ile tüm testlerin geçtiğini doğrula.
- **/home/akn/vps/.github/prompts/seg-agent.prompt.md dosyasını geliştir:** bu okuduğun prompt dosyasını güncel tut, yeni bulgular, düzeltmeler veya önemli noktalar oldukça ekle. Bu dosya senin ve gelecekteki ekip üyelerinin sec-agent'ı anlaması için temel kaynak olacak.