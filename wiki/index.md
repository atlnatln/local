---
title: "Wiki Index"
created: 2026-05-01
updated: 2026-05-01
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

## Decisions

Mimari karar kayıtları (ADR).

| Karar | Açıklama |
|-------|----------|
| [[adr-001-vps-rename-local]] | VPS dizin yapısı: `wiki` → `local` yeniden adlandırması |
| [[adr-002-mathlock-systemd]] | MathLock oyun sunucusu systemd servis yapılandırması |

## Projects

| Proje | Tip | Açıklama | Son Güncelleme |
|-------|-----|----------|----------------|
| [[ops-bot]] | project | Telegram operations bot — Python, systemd, sec-agent | 2026-05-01 |
| [[webimar]] | project | Tarım İmar — Django + Next.js + React | 2026-05-01 |
| [[anka]] | project | B2B veri servisi — Django + Next.js | 2026-05-01 |
| [[mathlock-play]] | project | Android math game + Django backend | 2026-05-01 |
| [[telegram-kimi]] | project | Telegram Kimi Bridge — Python, systemd, ACP | 2026-05-01 |
| [[sayi-yolculugu]] | project | HTML5 matematik eğitim oyunu | 2026-05-01 |

## Recently Updated

- [[proactive-wiki]] — Konsept sayfası oluşturuldu (2026-05-01)
- [[README]] — Organizasyon kuralları eklendi (2026-05-01)
- [[nginx-routing]] — Yeni konsept sayfası (2026-05-01)
- [[ssl-automation]] — Yeni konsept sayfası (2026-05-01)
- [[log-management]] — Yeni konsept sayfası (2026-05-01)

## Log

- [[log]] — Tüm işlemlerin kronolojik kaydı

## Archived Pages

(Henüz arşivlenmiş sayfa yok.)
