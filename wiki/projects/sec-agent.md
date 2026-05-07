---
title: "Sec-Agent"
created: "2026-05-02"
updated: "2026-05-03"
type: project
tags: [ops-bot, security, python, systemd, monitoring, nginx]
related:
  - ops-bot
  - security-ai-reporting
  - monitoring
  - infrastructure
  - adr-002-sec-agent-daily-report-agent-router
sources:
  - raw/articles/ops-bot-readme.md
  - raw/articles/ops-bot-deploy-script.md
---

# [[Sec-Agent]]

VPS üzerinde çoklu proje trafiğini izleyen, risk skoru üreten ve guardrail korumalı otomatik aksiyon alabilen güvenlik ajanı. Timer tabanlı one-shot çalışma modeliyle düşük kaynak tüketimi hedefler.

## Purpose

- nginx (multi-site) + sshd + docker loglarını toplama ve analiz
- IP bazlı risk skoru üretme ve kalıcı SQLite state tutma
- Guardrail kontrollerinden geçen otomatik block / ratelimit / alert aksiyonları
- False-positive koruma ve iyi bot whitelist yönetimi

## Architecture

Pipeline akışı:

```
collect → normalize → flag → score → decision → action → snapshot
```

| Aşama | Bileşen | Açıklama |
|-------|---------|----------|
| Collect | `collectors/` | nginx, sshd, docker log okuma |
| Normalize | `normalizers/` | Log formatını standart event'e dönüştürme |
| Flag | `engine/flagger.py` | Event'e anomaly flag'i atama |
| Score | `engine/scorer.py` | IP bazlı risk skoru hesaplama. Explicit guard: `added == 0.0` ise skor artmaz |
| Decision | `engine/decision.py` | Deterministik aksiyon kararı |
| Action | `actions/` | block, ratelimit, alert, log |
| Snapshot | `bin/run-with-snapshot.sh` | Koşu sonrası state yedekleme |

## Directory Structure

### Yerel Geliştirme
```
ops-bot/sec-agent/
├── bin/              # Çalıştırılabilirler
├── collectors/       # Log toplayıcılar
├── config/           # Kurallar, eşikler, whitelist
├── engine/           # Scoring, decision, guardrails, firewall
├── actions/          # Aksiyon modülleri
├── store/            # Runtime veri + export
├── docs/             # Operasyon dokümanları
└── tests/            # Unit testler
```

### VPS Üretim

| Yol | Amaç | Not |
|-----|------|-----|
| `/home/akn/vps/ops-bot/sec-agent/` | Deploy sonrası kaynak | `ops-bot/deploy.sh` ile güncellenir |
| `/opt/sec-agent/` | Çalışan üretim versiyonu | `move-sec-agent-to-opt.sh` ile taşınır |
| `/opt/sec-agent/store/` | Kalıcı state + events | `sec_agent.db`, `events.jsonl`, `seen_offsets.json` |

> **Önemli:** `/opt/sec-agent` dizini `move-sec-agent-to-opt.sh` ile oluşturulur. `sec-agent-link -> /opt/sec-agent` symlink'i deploy dizini ile üretimi birbirine bağlar.

## Components

### Collectors

| Toplayıcı | Kaynak | Dosya |
|-----------|--------|-------|
| nginx | `/var/lib/docker/volumes/vps_nginx_logs/_data/` | `collectors/nginx.py` |
| sshd | `/var/log/auth.log` | `collectors/sshd.py` |
| docker | Container logları (opsiyonel) | `collectors/docker.py` |

### Normalizers

- `nginx_use.py` — nginx access/error log → event
- `sshd_use.py` — auth.log → event
- `docker_use.py` — docker log → event

### Engine

| Modül | Görev |
|-------|-------|
| `scorer.py` | IP bazlı risk skoru hesaplama |
| `decision.py` | Deterministik aksiyon kararı (reason code'lu) |
| `guardrails.py` | Blast radius, cooldown, whitelist koruma |
| `firewall.py` | UFW entegrasyonlu block/ratelimit uygulama |
| `sqlite_store.py` | SQLite tabanlı IP state yönetimi |
| `decay.py` | Zamanla skor düşürme (50 pt/saat) |

### Actions

| Aksiyon | Açıklama |
|---------|----------|
| `block` | UFW üzerinden IP engelleme |
| `ratelimit` | UFW üzerinden rate limit |
| `alert` | Telegram webhook bildirimi |
| `log` | Event kaydı (events.jsonl) |

### Store

- `sec_agent.db` — Ana SQLite state veritabanı (canlı karar motoru). Yapı: `key` (IP), `value_json` (JSON string), `updated_at`
- `ip_state.json` — Uyumluluk/export dosyası (root sahipliğinde, artık ana kaynak değil)
- `events.jsonl` — Event arşivi (rotation ile sınırlı)
- `seen_offsets.json` — Log offset takibi

## Configuration

Ana konfigürasyon: `config/agent.yaml`

| Bölüm | Açıklama |
|-------|----------|
| `agent` | Mod (enforce/observe), data_dir, host_ip, log_level |
| `actions.block` | dry_run, enabled |
| `decay` | points_per_hour (100.0) |
| `scoring` | high_volume_threshold (5000), high_volume (0), max_ip_score (5000) |
| `thresholds` | block_threshold (80), persistence_score_threshold (2000) |
| `guardrails` | blast_radius, cooldown, auto_unblock |
| `resources` | Pruning limitleri, max IP state, JSONL rotation |
| `explainability` | IP-level decision reasoning (varsayılan kapalı) |

Whitelist iki katman:
1. **Manuel:** `config/ignore.yaml` — operasyonel CIDR'ler
2. **Otomatik:** `config/ignore.generated.yaml` — resmi bot IP aralıkları

Dahil edilen otomatik kaynaklar: Google crawlers, OpenAI botlar, Applebot, PerplexityBot, Bingbot, DuckDuckBot.

## Kritik Prensipler

### Dinamik IP Realitesi

- Türkiye ve dünyada bireysel kullanıcılar çoğunlukla **dinamik IP** kullanır
- Tekil IP whitelist'e ekleme **geçici ve anlamsız** bir çözümdür — aynı kullanıcı yarın farklı IP'den gelebilir
- Çözümler her zaman **behavior bazlı ve sistemik** olmalıdır

### Coğrafi Konum ≠ Güven

- Ülke veya ISP bilgisi tek başına güvenilirlik göstergesi **değildir**
- `never_block_cidrs`'e sadece altyapısal IP'ler eklenir (loopback, VPS IP'si, Cloudflare edge)
- ISP CIDR bloklarını (`188.0.0.0/8`, `176.0.0.0/8` vb.) `never_block_cidrs`'e eklemek **tehlikelidir** — milyonlarca IP'yi koruma altına alır ve saldırganları da içerir

### Behavior > Volume > Coğrafya

Değerlendirme önceliği:
1. **Flag'ler** — exploit, bruteforce, malware
2. **HTTP yanıt kodları** — 404/403 oranı
3. **User agent** — gerçek tarayıcı vs bot
4. **Endpoint pattern'i** — normal API vs exploit path
5. **Volume** — event sayısı (tek başına anlamsız)
6. **Coğrafi konum** — sadece bağlam bilgisi

## Guardrails

- Özel / loopback / VPS IP'lerini asla bloklamama
- Whitelist CIDR'lerini asla bloklamama
- Yakın zamanda başarılı SSH auth alan IP'ler için daraltılmış guardrail
- Aynı `/24` içinde max 5 blok (blast radius)
- Saatlik blok / ratelimit üst limiti
- Auto-unblock: 10 dk temiz trafik sonrası otomatik kaldırma

## systemd Services

| Servis | Tip | Tetik | Açıklama |
|--------|-----|-------|----------|
| `sec-agent.timer` | timer | ~15 dk | `sec-agent-once.service` tetikler |
| `sec-agent-once.service` | oneshot | timer | Tek seferlik pipeline koşusu |
| `sec-agent-metrics.service` | oneshot | manuel | Prometheus exporter (`:9101`) |
| `sec-agent-whitelist.timer` | timer | periyodik | `ignore.generated.yaml` yenileme |
| `sec-agent-post-deploy.service` | oneshot | manuel | Deploy sonrası yeniden başlatma |

> `sec-agent.service` `/dev/null` symlink'idir (eski daemon model devre dışı).

## Resource Limits

systemd servis limitleri:

| Limit | Değer |
|-------|-------|
| MemoryHigh | 300M |
| MemoryMax | 512M |
| CPUQuota | 50% |
| TasksMax | 128 |
| TimeoutStartSec | 10 dk |

Uygulama içi limitler:
- Overlap önleyici lock dosyası (`store/sec-agent-once.lock`)
- IP state pruning (72–720 saat pencereleri)
- Bounded JSONL okuma (max 50k satır, 100 MB)
- Max 25.000 IP state entry (LRU eviction)

## Deploy

```bash
# 1. ops-bot deploy edilir (sec-agent dahil)
cd ops-bot/
./deploy.sh

# 2. VPS'te /opt/sec-agent altına taşınır
ssh akn@89.252.152.222
cd /home/akn/vps/ops-bot
sudo ./move-sec-agent-to-opt.sh
```

// file: ops-bot/move-sec-agent-to-opt.sh
`move-sec-agent-to-opt.sh` yapılanları:
1. `/opt/sec-agent` dizini oluşturur
2. `sec-agent/*` dosyalarını kopyalar
3. Sahiplik/izinleri ayarlar
4. `sec-agent-link` symlink'i oluşturur
5. `agent.yaml` içindeki `data_dir` yolunu günceller
6. systemd unit'lerini kurar (`sec-agent-once.service`, `sec-agent.timer`)
7. Eski daemon servisini devre dışı bırakır, timer modeli enable eder

## Operations

### Tek seferlik koşu
```bash
sudo systemctl start sec-agent-once.service
sudo systemctl status sec-agent-once.service --no-pager
```

### Timer durumu
```bash
sudo systemctl status sec-agent.timer --no-pager
```

### Metrics
```bash
sudo systemctl start sec-agent-metrics.service
curl http://localhost:9101/metrics
```

### Whitelist yenileme
```bash
cd /opt/sec-agent
python3 bin/update-good-bot-allowlist.py
```

### Storage durumu
```bash
du -sh /opt/sec-agent/store/
tail -10 /opt/sec-agent/store/events.jsonl
```

### Skor Reset (Manuel)

Bir IP'nin skorunu acilen sıfırlamak gerektiğinde (örn. bilinen false positive):

```bash
cd /opt/sec-agent/store

# 1. SQLite DB'den sıfırla
python3 -c "
import sqlite3, json
conn = sqlite3.connect('sec_agent.db')
cur = conn.cursor()
cur.execute('SELECT key, value_json FROM ip_state WHERE key=?', ('IP_ADRESI',))
row = cur.fetchone()
if row:
    data = json.loads(row[1])
    data['score'] = 0.0
    data['classification'] = 'benign'
    cur.execute('UPDATE ip_state SET value_json=? WHERE key=?',
                (json.dumps(data), 'IP_ADRESI'))
    conn.commit()
    print('SQLite updated')
"

# 2. ip_state.json'dan sıfırla (root sahipliğinde)
sudo python3 -c "
import json
with open('ip_state.json') as f:
    data = json.load(f)
if 'IP_ADRESI' in data:
    data['IP_ADRESI']['score'] = 0.0
    data['IP_ADRESI']['classification'] = 'benign'
    with open('ip_state.json', 'w') as f:
        json.dump(data, f)
    print('ip_state.json updated')
"
```

## Troubleshooting

### Koşu tamamlanmıyor (Timeout)
`TimeoutStartSec=10min` aşılıyorsa log hacmi çok yüksek olabilir. `config/agent.yaml` içinde `resources.max_events_jsonl_mb` kontrol edilmeli.

### Memory limit aşımı
`MemoryMax=512M` aşılırsa pruning limitleri daraltılmalı (`prune_after_hours` değerleri düşürülmeli).

### State dosyası karışıklığı

`ops-bot-critical-alert.service` `OPS_BOT_CRITICAL_STATE_PATH` tanımlı değilse, state dosyası default olarak `/home/akn/local/ops-bot/data/sec-agent-critical-state.json` altına yazılır. Bu, deploy sonrası VPS `vps/` dizini ile local `local/` dizini arasında state kaymasına yol açar. Çözüm: servis dosyasına `Environment=OPS_BOT_CRITICAL_STATE_PATH=/home/akn/vps/ops-bot/data/sec-agent-critical-state.json` eklemek.

### events.jsonl çok büyük
Rotation otomatik çalışır ama manuel temizlik gerekiyorsa:
```bash
cd /opt/sec-agent/store
ls -lh events.jsonl archive/
```

### Bloklanmaması gereken IP engellendi

> **Prensip:** Yanlış block'lar whitelist'e çözüm değildir. Root cause sistem ayarlarındadır. Block'u kaldır, config'i düzelt.

1. Aktif block'u kaldır:
   ```bash
   sudo ufw delete deny from <IP>
   sudo iptables -D INPUT -s <IP> -j DROP 2>/dev/null || true
   ```
2. `config/scoring.yaml`, `config/agent.yaml`, `config/thresholds.yaml` ayarlarını gözden geçir
3. `sudo systemctl start sec-agent-once.service` (state yenileme)

### Normal kullanıcı yüksek skorla engellendi (flag'ler false)

**Belirti:** `events.jsonl`'de IP'nin tüm flag'leri `false`, `bot_threat_score: 0.0`, ama skor 1000+ ve `classification: "attacker"`.

**Neden:** `scorer.py` içinde `high_volume` skorlaması toplam event sayısına bakar (`high_volume_threshold`). 5000+ event yapan bir IP (örn. normal webimar kullanıcısı) her event'te `high_volume` puanı alır. Decay yetersizse skor birikir.

**Çözüm:**
- `config/scoring.yaml`: `high_volume_threshold` yükselt (500 → 5000), `high_volume` puanı düşür (2 → 0.5)
- `config/agent.yaml`: `decay.points_per_hour` artır (10 → 50)
- `config/thresholds.yaml`: `persistence_score_threshold` yükselt (500 → 2000)
- Hemen: Aktif block'u kaldır (`ufw delete`, `iptables -D`)
- **Whitelist'e ekleme** — root cause config'tedir, IP bazlı workaround değil

**Örnek (2026-05-02):** 188.132.132.225 — 62,398 event, tüm flag'ler false, skor 9750+. `high_volume_threshold: 500` ve `decay: 10` nedeniyle birikim oluşmuştu. Sistem ayarları düzeltilip block kaldırıldı; whitelist'e eklenmedi.

## Dependencies

- [[ops-bot]] — Telegram bildirim entegrasyonu
- [[infrastructure]] — nginx log kaynağı, Docker volume yapısı
- [[monitoring]] — Prometheus metrik tüketimi
- [[security-ai-reporting]] — Günlük AI yorumlu güvenlik raporu
- [[adr-002-sec-agent-daily-report-agent-router]] — Günlük raporların agent router ile yorumlanması kararı
