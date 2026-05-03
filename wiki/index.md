---
title: "Wiki Index"
created: 2026-05-01
updated: 2026-05-03
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

## Active Decisions

Aktif mimari karar kayıtları (ADR).

| Karar | Durum | Tarih | Açıklama |
|-------|-------|-------|----------|
| [[adr-001-monorepo-hybrid-structure]] | Active | 2026-05-02 | Monorepo + ayrı repo karışık yapısı kararı |
| [[adr-002-sec-agent-daily-report-agent-router]] | Active | 2026-05-02 | sec-agent raporlarının ops-bot agent router ile yorumlanması |

## Archived Decisions

Geçersiz kılınmış veya değişmiş kararlar.

| Karar | Durum | Tarih | Açıklama |
|-------|-------|-------|----------|

*(Henüz arşivlenmiş karar yok.)*

## Projects

| Proje | Tip | Açıklama | Son Güncelleme |
|-------|-----|----------|----------------|
| [[ops-bot]] | project | Telegram operations bot — Python, systemd, sec-agent | 2026-05-03 |
| [[sec-agent]] | project | Güvenlik ajanı — nginx/sshd izleme, UFW enforcement | 2026-05-02 |
| [[webimar]] | project | Tarım İmar — Django + Next.js + React | 2026-05-01 |
| [[anka]] | project | B2B veri servisi — Django + Next.js | 2026-05-01 |
| [[mathlock-play]] | project | Android math game + Django backend | 2026-05-01 |
| [[telegram-kimi]] | project | Telegram Kimi Bridge — Python, systemd, ACP | 2026-05-01 |
| [[sayi-yolculugu]] | project | HTML5 matematik eğitim oyunu | 2026-05-01 |

## Recently Updated

- [[ops-bot]] — Tek beyin mimarisi, güvenlik filtreleri, tool limit, memory trim (2026-05-03)
- [[ops-bot]] — V2 routing, timeout fixes, keywords_tr, embedding router aktifleştirildi (2026-05-03)
- [[adr-002-sec-agent-daily-report-agent-router]] — Yeni ADR oluşturuldu (2026-05-02)
- [[sec-agent]] — Yeni proje sayfası oluşturuldu (2026-05-02)
- [[ops-bot]] — VPS Dizin Yapısı ve Troubleshooting eklendi (2026-05-02)
- [[adr-001-monorepo-hybrid-structure]] — İlk ADR oluşturuldu (2026-05-02)

## Log

- [[log]] — Tüm işlemlerin kronolojik kaydı

## Archived Pages

(Henüz arşivlenmiş sayfa yok.)
