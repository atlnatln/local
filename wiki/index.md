---
title: "Wiki Index"
created: 2026-05-01
updated: 2026-05-10
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
| [[AGENTS]] | index | Wiki bakım kılavuzu — büyüme kuralları, lint, arşivleme |
| [[agents-md]] | concept | AGENTS.md kalıbı — agent instruction dosyası deseni |
| [[wiki-growth-protocol]] | concept | Wiki kontrollü büyüme — limit yönetimi, sub-page, arşivleme, log zincirleme |
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
| [[deployment]] | concept | Deploy pipeline, rollback, VPS senkronizasyonu |
| [[security-ai-reporting]] | concept | AI güvenlik raporlama ve incident response deseni |

## Analysis

Derinlemesine teknik analiz ve uyum raporları.

Tüm analizler: [[analysis-index|Analizler Kataloğu]]

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[meb-2024-curriculum-technical-alignment]] | analysis | MEB 2024 ↔ MathLock Play uyum — zorluk skalası, farklılaştırma, raporlama |
| [[meb-2024-curriculum-render]] | analysis | MEB render uyumu — emoji/örüntü, çok modlu input, parse pipeline |
| [[meb-2024-curriculum-ontoloji]] | analysis | MEB veri ontolojisi — tip isimlendirme, URI şema, yapılandırılmış ID |

## Concepts

Çapraz proje süreçleri, desenler ve konseptler.

Tüm konseptler: [[concepts-index|Konseptler Kataloğu]]

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[acp-protocol]] | concept | ACP protokolü, SDK karşılaştırması, kimi-cli entegrasyonu |
| [[agents-md]] | concept | AGENTS.md kalıbı — agent instruction dosyası deseni |
| [[deployment]] | concept | Deploy pipeline, rollback, VPS senkronizasyonu |
| [[git-workflow]] | concept | GitHub Sync + Cross-Machine Development akışı |
| [[kimi-code-cli]] | concept | Kimi CLI — kurulum, konfigürasyon, çalışma modları, data locations |
| [[kimi-code-cli-skills]] | concept | Kimi CLI skills sistemi — discovery, creation, flow |
| [[kimi-code-cli-agents]] | concept | Kimi CLI agent ve sub-agent sistemi |
| [[log-management]] | concept | nginx log rotasyonu ve merkezi log yönetimi |
| [[monitoring]] | concept | VPS servis izleme, Prometheus, Grafana, health check, alert |
| [[nginx-routing]] | concept | Domain-based routing, rate limiting, SSL termination |
| [[proactive-wiki]] | concept | Proaktif wiki güncelleme akışı — auto-sync, .pending, ingest |
| [[security-ai-reporting]] | concept | AI güvenlik raporlama ve incident response deseni |
| [[ssl-automation]] | concept | Let's Encrypt sertifika yönetimi ve otomatik yenileme |

## Decisions

Aktif ve arşivlenmiş mimari karar kayıtları (ADR).

Tüm kararlar: [[decisions-index|Mimari Kararlar Kataloğu]]

| Sayfa | Tip | Açıklama |
|-------|-----|----------|
| [[adr-001-monorepo-hybrid-structure]] | decision | Monorepo + ayrı repo hibrit yapısı |
| [[adr-002-sec-agent-daily-report-agent-router]] | decision | sec-agent günlük rapor ve agent router |
| [[adr-003-robotopia-extraction]] | decision | Robotopia'nın MathLock Play'den ayrılması |
| [[adr-004-memory-game-integration]] | decision | Hafıza oyunu entegrasyon stratejisi |
| [[adr-005-ops-bot-acp-sdk-migration]] | decision | ops-bot ACP client'ı resmi SDK'ya geçiş |
| [[adr-006-github-sync-cross-machine-dev]] | decision | GitHub Sync + Cross-Machine Development |
| [[adr-007-mathlock-meb-curriculum-compliance-implantation]] | decision | MathLock MEB müfredat uyum implantasyonu |

## Projects

Tüm projeler: [[projects-index|Projeler Kataloğu]]

| Proje | Tip | Açıklama | Son Güncelleme |
|-------|-----|----------|----------------|
| [[ops-bot]] | project | Telegram operations bot — Python, systemd, sec-agent, test suite (67+ test) | 2026-05-07 |
| [[sec-agent]] | project | Güvenlik ajanı — nginx/sshd izleme, UFW enforcement | 2026-05-07 |
| [[webimar]] | project | Tarım İmar — Django + Next.js + React | 2026-05-05 |
| [[mathlock-play]] | project | Android math game + Django backend (Robotopia'sız) — **ayrı repo** | 2026-05-10 |
| [[mathlock-play-ai]] | project | MathLock AI soru pipeline'ı | 2026-05-07 |
| [[mathlock-play-android]] | project | MathLock Android detayları | 2026-05-10 |
| [[mathlock-play-android-releases]] | project | MathLock Android release notları ve bug fix'ler | 2026-05-10 |
| [[mathlock-play-backend]] | project | MathLock backend detayları | 2026-05-10 |
| [[robotopia-android]] | project | Blockly kodlama oyunu — bağımsız Android | 2026-05-03 |
| [[telegram-kimi]] | project | Telegram Kimi Bridge — Python, systemd, ACP | 2026-05-03 |
| [[sayi-yolculugu]] | project | HTML5 matematik eğitim oyunu + MathLock entegrasyonu | 2026-05-03 |
| [[local]] | project | Ana monorepo — agent instruction'ları, references, wiki kuralları | 2026-05-10 |

## Recently Updated

- [[sayi-yolculugu]] — Standalone HTML5 oyunu güncellendi: ~41 KB → ~48 KB, mobil optimizasyon (viewport, theme-color, touch highlight, overscroll-behavior), splash features, goal bar (2026-05-11)
- [[mathlock-play]] — Experimental-web dizini eklendi: React + Vite + Tailwind deneme oyun frontend'i; repo durumu güncellendi (2026-05-11)
- [[local]] — AGENTS.md refactor: 499→167 satır, references/QUICKREF.md yeni, WORKFLOW.md'ye wiki filtreleme ve iddia kuralları eklendi (2026-05-10)
- [[mathlock-play-android]] — 7 kritik bug fix (StatsTracker idempotency, AccountManager 403 re-register, CreditApiClient 503 parsing, 409 retry loop, raw device token, LockStateManager thread-safety, SecurePrefs hard fail), UI/UX iyileştirmeleri, yeni testler (AccountManagerTest, StatsTrackerTest, LockStateManagerTest), v1.0.77 (2026-05-09)
- [[mathlock-play-backend]] — credits/auth güncellemeleri, raw+signed token dual auth, 503/409 handling, VPS deploy, yeni testler (2026-05-09)
- [[mathlock-play]] — v1.0.77 release, recent commits güncellendi (2026-05-09)
- [[mathlock-play-ai]] — MEB uyum düzeltmeleri: curriculum JSON non-üniter kesir fix, generate script çıkarma=0 fix, zorluk 5 toplama 100'e genişletildi, Android TYPE_LABELS standardizasyonu tamamlandı (2026-05-07)
- [[proactive-wiki]] — Auto-sync davranışı eklendi: `docs(wiki):` sonsuz döngü koruması, `.pending` cross-machine sync, `git commit --amend` yerine ayrı commit stratejisi (2026-05-07)
- [[ops-bot]] — `.gitignore` güncellendi: `.venv/`, `venv/`, `data/sec-agent-*.json` eklendi (2026-05-06)
- [[webimar]] — `.gitignore` güncellendi, `deploy.sh`'ta VPS domain check `-k` flag'i eklendi (2026-05-06)
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

- [[log]] — Tüm işlemlerin kronolojik kaydı (aktif)
- [[log-2026-H1]] — 2026 H1 arşivi (893 giriş, 2025-05-01 — 2026-05-10)
- [[log-lint-archive]] — Lint sonuçları arşivi

## Archived Pages

- [[anka|Anka]] (archived 2026-05-06) — B2B veri servisi, pasife alındı
