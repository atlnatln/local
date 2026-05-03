---
type: decision
name: adr-002-sec-agent-daily-report-agent-router
title: Sec-Agent Günlük Raporlarının Ops-Bot Agent Router ile Yorumlanması
description: sec-agent tarafından üretilen günlük güvenlik raporları, basit subprocess kimi-cli çağrısı yerine ops-bot agent router üzerinden uzman ajanlara yönlendirilerek yorumlanır.
created: "2026-05-02"
updated: "2026-05-02"
decision_date: "2026-05-02"
tags: [decision, adr, ops-bot, sec-agent, security, ai, telegram-bot]
status: Active
supersedes:
superseded_by:
deciders:
related:
  - sec-agent
  - ops-bot
  - security-ai-reporting
  - monitoring
---

# adr-002-sec-agent-daily-report-agent-router: Sec-Agent Günlük Raporlarının Ops-Bot Agent Router ile Yorumlanması

sec-agent tarafından üretilen günlük güvenlik raporları, basit subprocess `kimi-cli` çağrısı yerine ops-bot agent router (`routing.py`) üzerinden uzman ajanlara yönlendirilerek yorumlanır.

## Context

Mevcut durumda sec-agent günlük rapor yorumlaması iki bileşenle yapılıyor:

1. `critical_security_alert.py` — `events.jsonl` + `ip_state.json`'den özet mesaj üretir
2. `ai_security_analyzer.py` — Anomaly listesini `kimi-cli`'yi subprocess olarak çağırarak yorumlar

Bu yaklaşımın sınırlamaları:
- Tek seferlik, yapılandırılmamış prompt; uzmanlık alanları ayrılmamış
- Raporun farklı boyutları (trend analizi, tehdit değerlendirme, öneri) tek bir çıktıda birleşiyor
- `kimi-cli` subprocess çağrısı hata yönetimi ve retry mekanizması açısından kırılgan
- Kullanıcı etkileşimi yok; yorum statik, bağlamsız

Öte yandan ops-bot'ta `routing.py` içinde 10+ uzman ajan (`ops-database-agent`, `ops-monitor-agent`, `ops-security-*` vb.) tanımlı ve heuristic seçim + conversation memory + user preferences altyapısı çalışıyor. Bu altyapı sec-agent raporlarını daha derinlemesine ve yapılandırılmış şekilde yorumlamak için kullanılabilir.

## Decision

**Karar:** sec-agent günlük raporları, `ai_security_analyzer.py` yerine ops-bot agent router üzerinden yeni tanımlanacak güvenlik uzman ajanlarına yönlendirilecek.

Detaylar:
- **Veri kaynağı:** `sec-agent/store/events.jsonl` + `sec_agent.db` özet export'u (günlük)
- **Tetikleyici:** Mevcut `ops-bot-critical-alert.timer` (08:00) korunur; `DAILY_DIGEST_MODE=true` ile çalışır
- **Router entegrasyonu:** `routing.py`'ye yeni agent(ler) eklenecek:
  - `security-summary-agent` — Rapor özetini çıkarır (event hacmi, skor dağılımı, aksiyonlar)
  - `security-threat-analyst-agent` — Kritik/high tehditleri analiz eder (IP davranışı, attack vektörü)
  - `security-recommendation-agent` — Yapılandırma ve aksiyon önerileri üretir
- **Yürütme modeli:** kimi-cli agent router üzerinden çağrılır; ops-bot conversation memory context kullanılabilir. **kimi-cli host düzeyinde çalışır** — container veya izole ortamda değil, VPS'in ana işletim sistemi üzerinde `~/.local/bin/kimi` olarak kurulu olmalıdır
- **Çıktı:** Telegram üzerinden çoklu mesaj (özet → analiz → öneri) veya tek birleşik mesaj
- **Kullanıcı etkileşimi:** Kullanıcı rapor sonrası "Bu IP nedir?" veya "Öneriyi uygula" gibi follow-up sorular sorabilir

Mevcut `ai_security_analyzer.py` **deprecated** (eski) olarak işaretlenir; yeni sistem devreye girdikten sonra kaldırılır.

## Consequences

### ✅ Olumlu

- Uzman ajanlar raporu farklı boyutlarıyla derinlemesine yorumlar; tek monolitik çıktı yerine yapılandırılmış analiz
- ops-bot conversation memory sayesinde kullanıcı follow-up sorularıyla devam edebilir
- `routing.py` heuristic agent seçimi ile rapor içeriğine göre en uygun uzman ajan otomatik seçilir
- Hata yönetimi, retry ve timeout ops-bot altyapısında merkezi yönetilir
- Kullanıcı tercihleri (`user_preferences.py`) ile rapor detay seviyesi kişiselleştirilebilir
- Host düzeyinde kimi-cli çalıştırma, container bağımlılığı olmadan doğrudan VPS kaynaklarına erişim sağlar (örn. `store/sec_agent.db` okuma)

### ⚠️ Riskler / Maliyetler

- ops-bot ve sec-agent arasındaki bağımlılık artar; sec-agent tek başına çalışamaz hale gelmez ama rapor yorumlaması ops-bot'a bağımlı olur
- Agent router yükü artar; günlük sabah saatinde ek kimi-cli çağrıları CPU/bellek tüketimi artırabilir
- Yeni agent tanımları `routing.py`'yi daha da büyütür; bakım karmaşıklığı artar
- `sec-agent-metrics.service` (`:9101`) ile aynı zaman diliminde çalışırsa resource contention olabilir
- Host düzeyinde kimi-cli çalıştırma, container izolasyonu sağlamaz; güvenlik açısından input sanitization kritik hale gelir
- kimi-cli host düzeyinde `/home/akn/.local/bin/kimi` olarak kurulu olmalıdır; container veya chroot ortamında çalışmaz

### 🔄 Tarafsız / Notlar

- Mevcut `security-ai-reporting` konsept sayfası bu ADR sonrası güncellenmelidir
- `ops-bot-critical-alert.timer`'ın `DAILY_DIGEST_MODE` değişkeni korunur; yeni sistem bu değişkene bağımlı kalır
- sec-agent rapor verisi JSON formatında agent router'a iletilir; prompt injection riskine karşı input sanitization gerekir

## Alternatives Considered

### Alternatif 1: Mevcut `ai_security_analyzer.py`'yi Geliştirmek

- **Açıklama:** Subprocess kimi-cli çağrısını tutar; prompt'u daha detaylı hale getirir, hata yönetimi ekler
- **Neden reddedildi:** Subprocess modeli retry, memory, kullanıcı etkileşimi ve agent seçimi gibi yetenekleri doğal olarak desteklemez. Her ek özellik için yeniden icat etmek gerekecek.

### Alternatif 2: Ayrı Bir Microservice/API Oluşturmak

- **Açıklama:** Sec-agent rapor yorumlaması için ayrı bir Python servisi (FastAPI/Flask) yazılır; kimi-cli bu servis içinden çağrılır
- **Neden reddedildi:** VPS üzerinde yeni bir servis daha fazla kaynak tüketir ve yönetim yükü getirir. ops-bot agent altyapısı zaten mevcut, yeniden yazmaya gerek yok.

### Alternatif 3: LLM Entegrasyonunu Tamamen Kaldırmak

- **Açıklama:** Günlük rapor sadece ham sayılarla (event sayısı, blok sayısı, top IP'ler) iletilir; AI yorumu yapılmaz
- **Neden reddedildi:** Kullanıcı "neden önemli?" sorusuna yanıt alamaz; düşük sinyal/gürültü oranı bozulur. Düşük gürültü politikası sadece iletişim sıklığını değil, iletişim kalitesini de hedefler.

## Status

**Mevcut Durum:** `Active`

> Son durum güncellemesi: 2026-05-02
