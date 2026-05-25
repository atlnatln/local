# Güvenlik Sertleştirme Dokümantasyonu
**Tarih:** 25 Mayıs 2026  
**Neden:** 12-25 Mayıs arası ops-bot günlük loglarında token abuse, SSH patlaması ve bot kilitlenmesi tespit edildi.

---

## 1. Değişiklik Özeti

| Repo | Dosya Sayısı | Risk | Geri Alınabilirlik |
|------|-------------|------|-------------------|
| `ops-bot` | 5 | Orta | Yüksek (config + küçük kod) |
| `projects/webimar` | 7 | Düşük | Çok yüksek (çoğunlukla araç/admin) |

> **Fazla mühendislik yok.** Tüm değişiklikler geri alınabilir veya config üzerinden ayarlanabilir.

---

## 2. ops-bot / sec-agent (5 dosya)

### 2.1 `sec-agent/config/thresholds.yaml`

| Parametre | Eski | Yeni | Geri Alma |
|-----------|------|------|-----------|
| `block_duration` | 60 dk | **180 dk** (3 saat) | `60` yap |
| `persistent_attacker_score` | 2000 | **1000** | `2000` yap |
| `persistent_attacker_duration` | 1440 dk (1 gün) | **7200 dk** (5 gün) | `1440` yap |
| `max_blocks_per_hour` | 50 | **120** | `50` yap |

**Neden:** Günlük raporda "BLOCK: X | Aktif blok: 0" çelişkisi vardı. 60 dk block + 10 dk auto-unblock saldırganların aynı gün içinde geri dönmesine izin veriyordu.

**Geri alma tek satır:** Config dosyasını eski değerlerle değiştir, restart et.

### 2.2 `sec-agent/config/agent.yaml`

| Parametre | Eski | Yeni | Geri Alma |
|-----------|------|------|-----------|
| `auto_unblock.enabled` | true | **true** (kaldı) | — |
| `auto_unblock.lookback_minutes` | 10 | **60** | `10` yap |
| `auto_unblock.min_clean_events` | 3 | **5** | `3` yap |

**Neden:** 10 dk içinde 3 temiz event çok kolaydı; saldırgan kısa süre sessiz kalıp kaçıyordu. Tamamen kapatmak dinamik IP'li masum kullanıcıları etkilerdi.

### 2.3 `sec-agent/actions/block.py`

**Ekleme:** `block_count > 1` olan IP'ler auto-unblock dışında tutuluyor.

**Neden:** Daha önce bloklanıp geri dönen IP masum değildir.

**Geri alma:** Satır 241-252'yi sil.

### 2.4 `bot/acp_sdk_executor.py`

**Ekleme:**
- `_ensure_connection` içinde `list_sessions()` health probe (zombi proses tespiti)
- `asyncio.sleep(1.0)` → `2.0` (trailing chunk bekleme)
- Accumulator boşsa `prompt_resp` içinden fallback metin çıkarımı

**Neden:** 25 Mayıs 09:15'te "Bot boş yanıt üretti" hatası. ACP alt-prosesi kilitleniyordu.

**Geri alma:** Değişiklikleri revert et.

### 2.5 `bot/acp_sdk_client.py`

**Düzeltme:** `hasattr(update, "tool_call")` → `type(update).__name__` içinde `"ToolCall"` kontrolü.

**Neden:** Eski kontrol hiçbir zaman `True` dönmüyordu; tool call sayacı çalışmıyordu.

**Geri alma:** Bug fix olduğu için geri alınmamalı.

---

## 3. webimar API Backend (7 dosya)

### 3.1 `accounts/throttles.py` + `accounts/views/analytics_views.py` + `settings.py`

**Yeni:** `AnalyticsEventThrottle` — IP+session bazlı **30/dk** limit.

**Neden:** `/api/accounts/analytics/events/` endpoint'i `AllowAny` idi ve hiç koruması yoktu. 24-25 Mayıs'ta 4 IP toplam 1500+ istek gönderdi.

**Geri alma:**
- `views/analytics_views.py` → `@throttle_classes([AnalyticsEventThrottle])` satırını sil
- `settings.py` → `'analytics_event': '30/min'` satırını sil
- `throttles.py` → `AnalyticsEventThrottle` class'ını sil

### 3.2 `accounts/middleware_token_abuse.py`

**Yeni:** IP bazlı anomaly tespiti. Saatte 300+ istek atan IP'yi `IP_ABUSE` logu olarak kaydeder.

**Neden:** Önceki middleware sadece authenticated user'ları izliyordu. Anonim flood'u yakalayamıyordu.

**Not:** Pasif dedektör. **Bloklamaz**, sadece loglar. Sistemi etkilemez.

**Geri alma:** `_check_ip_anomaly` metodunu ve çağrısını sil.

### 3.3 `accounts/management/commands/token_abuse_report.py` (YENİ)

**Ne yapar:** Son N gün içindeki şüpheli IP'leri, çoklu IP kullanıcılarını ve yüksek 200 OK oranlı kullanıcıları raporlar. Opsiyonel olarak token'ları revoke eder.

**Risk:** Sıfır. Sadece okuma + opsiyonel revoke.

**Geri alma:** Dosyayı sil.

### 3.4 `accounts/admin.py`

**Yeni:**
- `TrackedApiCallAdmin` — API çağrılarını admin panelden filtreleme ve CSV export
- `SecurityEventAdmin` — "🔍 Seçili olayları incele" action'ı

**Risk:** Sıfır. Salt okuma admin araçları.

**Geri alma:** `TrackedApiCallAdmin` kaydını ve `investigate_selected` metodunu sil.

### 3.5 `accounts/admin_token_blacklist.py`

**Yeni:** "🔒 Kullanıcının TÜM token'larını revoke et" admin action'ı.

**Risk:** Düşük. Sadece admin panelinde kullanılır.

**Geri alma:** `blacklist_all_user_tokens` metodunu sil.

---

## 4. Hızlı Geri Alma Rehberi

### Tümünü geri almak istiyorsan:

```bash
# ops-bot
cd /home/akn/local/ops-bot
git checkout -- sec-agent/config/thresholds.yaml sec-agent/config/agent.yaml \
  sec-agent/actions/block.py bot/acp_sdk_executor.py bot/acp_sdk_client.py

# webimar
cd /home/akn/local/projects/webimar
git checkout -- webimar-api/accounts/throttles.py \
  webimar-api/accounts/views/analytics_views.py \
  webimar-api/webimar_api/settings.py \
  webimar-api/accounts/middleware_token_abuse.py \
  webimar-api/accounts/admin.py \
  webimar-api/accounts/admin_token_blacklist.py
rm webimar-api/accounts/management/commands/token_abuse_report.py
```

### Sadece throttle'ı geri almak istiyorsan:

```bash
# webimar
cd /home/akn/local/projects/webimar
git checkout -- webimar-api/accounts/throttles.py \
  webimar-api/accounts/views/analytics_views.py \
  webimar-api/webimar_api/settings.py
```

---

## 5. Deploy Komutları

```bash
# ops-bot
cd /home/akn/local/ops-bot
git add -A
git commit -m "fix(sec-agent): tighten block rules, smarter auto-unblock
fix(bot): ACP empty-response race and tool-call tracking"
git push origin main
./deploy.sh

# webimar
cd /home/akn/local/projects/webimar
git add -A
git commit -m "feat(security): analytics throttle, IP anomaly detection, admin tools"
git push origin main
# VPS'te: docker compose -f docker-compose.prod.yml up --build -d
```

---

## 6. Çalıştırma Komutları (Deploy Sonrası)

```bash
# VPS'te, webimar container'ı içinde:
python manage.py token_abuse_report --days=7 --min-requests=300

# Şüpheli token'ları otomatik revoke et + CSV kaydet
python manage.py token_abuse_report --days=7 --auto-revoke --output=/tmp/abuse_report.csv
```
