---
title: "Wiki Index"
created: 2026-05-01
updated: 2026-05-07
type: index
tags: [meta, index]
related: []
---

# Wiki Index

Master content catalog for `local-wiki`. All pages are reachable via wikilink.

---

## System

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[README]] | index | Wiki kullanım kılavuzu ve organizasyon kuralları |
| [[SCHEMA]] | index | Wiki yapı tanımı, etiket taksonomisi ve frontmatter şeması |
| [[system-overview]] | concept | VPS genel mimarisi ve proje haritası |

## Infrastructure & Platform

Ortak altyapı ve platform servisleri. Diğer tüm projelere hizmet eden katman.

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[infrastructure]] | project | VPS altyapısı — nginx, SSL, Docker, shared services |
| [[monitoring]] | concept | VPS servis izleme, Prometheus, Grafana, health check, alert |
| [[nginx-routing]] | concept | Domain-based routing, rate limiting, SSL termination |
| [[ssl-automation]] | concept | Let's Encrypt sertifika yönetimi ve otomatik yenileme |
| [[log-management]] | concept | nginx log rotasyonu ve merkezi log yönetimi |

## Concepts

Çapraz proje süreçleri, desenler ve konseptler.

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[deployment]] | concept | Uygulama dağıtım süreçleri ve yapılandırması |
| [[git-workflow]] | concept | Monorepo git stratejisi, commit konvansiyonları ve kurallar |
| [[proactive-wiki]] | concept | Git commit sonrası otomatik wiki güncelleme önerisi (Auto-Prompt) |
| [[security-ai-reporting]] | concept | Günlük güvenlik raporunun AI yorumlaması ve Telegram bildirimi |
| [[kimi-code-cli]] | concept | Terminal tabanlı AI kodlama asistanı — kurulum, modlar, customisation |
| [[agents-md]] | concept | AI agent'lar için proje context dosyası — format, konum, best practices |
| [[acp-protocol]] | concept | Agent Client Protocol — client ↔ AI agent JSON-RPC stdio protokolü |

## Active Decisions

Aktif mimari karar kayıtları (ADR).

| Karar | Durum | Tarih | Açıklama |
|-------|-------|-------|----------|
| [[adr-001-monorepo-hybrid-structure]] | Active | 2026-05-02 | Monorepo + ayrı repo karışık yapısı kararı |
| [[adr-002-sec-agent-daily-report-agent-router]] | Active | 2026-05-02 | sec-agent raporlarının ops-bot agent router ile yorumlanması |
| [[adr-003-robotopia-extraction]] | Active | 2026-05-03 | Robotopia'nın MathLock Play'den bağımsız projeye ayrılması |
| [[adr-004-memory-game-integration]] | Active | 2026-05-03 | Sayı Hafızası oyununun MathLock Play'e entegrasyonu |
| [[adr-005-ops-bot-acp-sdk-migration]] | Active | 2026-05-04 | Ops-bot ACP client'ının resmi SDK'ya geçiş kararı |
| [[adr-006-github-sync-cross-machine-dev]] | Active | 2026-05-05 | GitHub Sync + Cross-Machine Development |
| [[adr-007-mathlock-meb-curriculum-compliance-implantation]] | Active | 2026-05-07 | MathLock Play MEB 2024 müfredat uyum implantasyonu |

## Archived Decisions

Geçersiz kılınmış veya değişmiş kararlar.

| Karar | Durum | Tarih | Açıklama |
|-------|-------|-------|----------|

*(Henüz arşivlenmiş karar yok.)*

## Projects

| Proje | Tip | Açıklama | Son Güncelleme |
|-------|-----|----------|----------------|
| [[ops-bot]] | project | Telegram operations bot — Python, systemd, sec-agent, test suite (67+ test) | 2026-05-07 |
| [[sec-agent]] | project | Güvenlik ajanı — nginx/sshd izleme, UFW enforcement | 2026-05-07 |
| [[webimar]] | project | Tarım İmar — Django + Next.js + React | 2026-05-05 |
| [[mathlock-play]] | project | Android math game + Django backend (Robotopia'sız) | 2026-05-07 |
| [[mathlock-play-ai]] | project | MathLock AI soru pipeline'ı | 2026-05-07 |
| [[mathlock-play-android]] | project | MathLock Android detayları | 2026-05-07 |
| [[mathlock-play-backend]] | project | MathLock backend detayları | 2026-05-07 |
| [[robotopia-android]] | project | Blockly kodlama oyunu — bağımsız Android | 2026-05-03 |
| [[telegram-kimi]] | project | Telegram Kimi Bridge — Python, systemd, ACP | 2026-05-03 |
| [[sayi-yolculugu]] | project | HTML5 matematik eğitim oyunu + MathLock entegrasyonu | 2026-05-03 |

## Recently Updated

- [[mathlock-play-ai]] — MEB uyum düzeltmeleri: curriculum JSON non-üniter kesir fix, generate script çıkarma=0 fix, zorluk 5 toplama 100'e genişletildi, Android TYPE_LABELS standardizasyonu tamamlandı (2026-05-07)
- [[mathlock-play-android]] — `StatsDashboardActivity` + `PerformanceReportActivity` tip isimlendirme fix'i eklendi (2026-05-07)
- [[proactive-wiki]] — Auto-sync davranışı eklendi: `docs(wiki):` sonsuz döngü koruması, `.pending` cross-machine sync, `git commit --amend` yerine ayrı commit stratejisi (2026-05-07)
- [[ops-bot]] — `critical_security_alert.py` medium severity desteği, `token_abuse_detector.py` auth endpoint genişlemesi, `OPS_BOT_CRITICAL_STATE_PATH` tanımı (2026-05-07)
- [[sec-agent]] — State path karışıklığı troubleshooting notu eklendi (2026-05-07)
- [[ops-bot]] — `.gitignore` güncellendi: `.venv/`, `venv/`, `data/sec-agent-*.json` eklendi (2026-05-06)
- [[webimar]] — `.gitignore` güncellendi, `deploy.sh`'ta VPS domain check `-k` flag'i eklendi (2026-05-06)
- [[mathlock-play]] — `.env.example` güncellendi: DB config ayrıldı, Celery/Redis eklendi, Google Play path güncellendi (2026-05-06)
- [[git-workflow]] — GitHub Sync + Cross-Machine Development bölümü eklendi, anka referansları kaldırıldı (2026-05-06)
- [[ops-bot]] — VPS senkronizasyonu: router.py silindi, orchestrator.py + agents/ dizini eklendi, eski ACP client/executor bot/'a geri taşındı, routing master'a bırakıldı (2026-05-05)
- [[ops-bot]] — ACP SDK migration tamamlandı: bot/acp_sdk_client.py + bot/acp_sdk_executor.py eklendi, eski ACP client/executor arşivlendi, file I/O sandboxing, terminal execution, markdown sanitize, tests/sdk/ (10 unit test) (2026-05-05)
- [[ops-bot]] — ACP fix'leri: tool_call_count reset, /iptal process kill, boş yanıt guard, /durum komutu, structured logging, get_diagnostics, reader loop EOF cleanup (2026-05-04)
- [[acp-protocol]] — Yeni konsept sayfası: ACP protokolü, SDK karşılaştırması, kimi-cli entegrasyonu (2026-05-04)
- [[adr-005-ops-bot-acp-sdk-migration]] — Yeni ADR: ops-bot ACP client'ı resmi SDK'ya geçiyor (2026-05-04)
- [[sec-agent]] — AGENTS.md v2.1 revizyonu: SOURCE OF TRUTH, BENIGN CEILING, DAVRANIŞ PATTERN, sembolik kural formatı (2026-05-03)
- [[mathlock-play]] — Auth mekanizması (DeviceTokenAuthentication), backend test suite (169 test / 10 modül), Sayı Yolculuğu auth fix dökümante edildi (2026-05-03)
- [[sayi-yolculugu]] — Wiki sayfası genişletildi: MathLock entegrasyonu, backend endpoint'leri, AI pipeline, cache davranışı eklendi (2026-05-03)
- [[robotopia-android]] — Yeni proje oluşturuldu, MathLock Play'den ayrıldı (2026-05-03)
- [[mathlock-play]] — Robotopia temizlendi, ~2.9 MB asset kaldırıldı (2026-05-03)
- [[ops-bot]] — ACP protocol fix (kimi-cli 1.40), word-boundary risky matching, /iptal footer, 7 yeni test (2026-05-03)
- [[telegram-kimi]] — SSH komut refactor, context usage ACP üzerinden (kimi-cli 1.40) (2026-05-03)
- [[ops-bot]] — Test suite genişletildi (57 test), executor output temizliği, router caching (2026-05-03)
- [[ops-bot]] — Security prompt merge (explain+observe), deploy fix, 30 test suite (2026-05-03)
- [[ops-bot]] — Tek beyin mimarisi, güvenlik filtreleri, tool limit, memory trim (2026-05-03)
- [[ops-bot]] — V2 routing, timeout fixes, keywords_tr, embedding router aktifleştirildi (2026-05-03)
- [[adr-002-sec-agent-daily-report-agent-router]] — Yeni ADR oluşturuldu (2026-05-02)
- [[sec-agent]] — Yeni proje sayfası oluşturuldu (2026-05-02)

## Log

- [[log]] — Tüm işlemlerin kronolojik kaydı

## Archived Pages

- [[anka|Anka]] (archived 2026-05-06) — B2B veri servisi, pasife alındı
