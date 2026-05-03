---
type: decision
name: adr-001-monorepo-hybrid-structure
title: Monorepo + Ayrı Repo Karışık Yapısı
description: Büyük projeler ayrı repo, küçük/ilişkili projeler ve altyapı tek monorepo altında tutulur.
created: "2026-05-02"
updated: "2026-05-02"
decision_date: "2026-05-02"
tags: [decision, adr, infrastructure, git]
status: Active
supersedes:
superseded_by:
deciders:
related:
  - infrastructure
  - git-workflow
  - ops-bot
  - webimar
---

# adr-001-monorepo-hybrid-structure: Monorepo + Ayrı Repo Karışık Yapısı

Büyük projeler ayrı repo, küçük/ilişkili projeler ve altyapı tek monorepo altında tutulur.

## Context

`/home/akn/local` altında 7 proje ve ortak altyapı (infrastructure) bulunuyor. Projelerin boyutu, bağımsızlık düzeyi ve GitHub entegrasyonu ihtiyaçları farklılık gösteriyor. Hepsini tek repo altında tutmak, bağımsız CI/CD ve izole release yönetimi gerektiren büyük projeleri yavaşlatıyor. Aksine, hepsini ayrı repo yapmak VPS yönetimini ve ortak altyapı konfigürasyonunu karmaşıklaştırıyor.

## Decision

**Karar:** `ops-bot` ve `webimar` ayrı GitHub repo'larında; geri kalan projeler (`anka`, `mathlock-play`, `telegram-kimi`, `sayi-yolculugu`) ve ortak altyapı (`infrastructure`) tek monorepo (`/home/akn/local/.git`) altında tutulur.

Detaylar:
- Ayrı repo'lar: `ops-bot/` ve `projects/webimar/` kendi `.git` köklerine sahip.
- Monorepo: `projects/anka/`, `projects/mathlock-play/`, `projects/telegram-kimi/`, `projects/sayi-yolculugu/`, `infrastructure/`, `scripts/`, `wiki/` ana `.git` altında takip edilir.
- Her deploy öncesi: ayrı repo'lar için kendi commit'leri, ardından monorepo'ya commit atılır.

## Consequences

### ✅ Olumlu

- Büyük projeler bağımsız CI/CD pipeline'ına sahip olabilir.
- GitHub entegrasyonu (Actions, Issues, PR) ayrı repo'larda izole çalışır.
- Versiyonlama ve release yönetimi bağımsız hale gelir.
- Monorepo içindeki küçük projeler ortak script'ler, altyapı konfigürasyonu ve wiki ile kolay paylaşım yapar.

### ⚠️ Riskler / Maliyetler

- Deployment komutları farklılık gösterir (`deploy.sh` içeriği repo'ya göre değişir).
- Her değişiklik için potansiyel olarak iki kat commit gerekir (subrepo + monorepo).
- VPS dizin yapısı karmaşıktır; `/home/akn/vps/` altında hem Docker hem systemd servisleri vardır.

### 🔄 Tarafsız / Notlar

- `deploy.sh` script'leri her proje için farklılıkları soyutlar.
- `AGENTS.md` ve wiki, monorepo + subrepo yapısını açıkça belgeler.
- Checkpoint sistemi (`.checkpoints/*.sha`) her repo tipine uygun çalışır.

## Alternatives Considered

### Alternatif 1: Hepsi Tek Monorepo

- **Açıklama:** Tüm projeler tek `.git` altında tutulur.
- **Neden reddedildi:** `ops-bot` ve `webimar` GitHub Actions, izole issue/PR takibi ve bağımsız release döngüsü gerektirir. Tek monorepo'da bu izolasyon zorlaşır, GitHub entegrasyonu karmaşık hale gelir.

### Alternatif 2: Hepsi Ayrı Repo

- **Açıklama:** Her proje kendi GitHub repo'suna sahip olur.
- **Neden reddedildi:** VPS üzerinde 7 ayrı repo'yu yönetmek, ortak altyapıyı (nginx, SSL, monitoring) tekrarlamak ve senkronize etmek gereksiz yere karmaşık olur. Küçük projeler (anka, mathlock-play vb.) için bağımsız repo faydası düşüktür.

## Status

**Mevcut Durum:** `Active`

> Son durum güncellemesi: 2026-05-02
