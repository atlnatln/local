---
title: "Sayı Yolculuğu"
created: "2026-05-01"
updated: "2026-05-01"
type: project
tags: [sayi-yolculugu, html5, javascript, education]
related:
  - infrastructure
sources:
  - raw/articles/sayi-yolculugu-index.html
---

# [[Sayi-Yolculugu]]

HTML5 tabanlı, tarayıcıda çalışan çocuklar için matematik eğitim oyunu. Tek dosya (`index.html`) içinde CSS, JavaScript ve oyun mantığı bir arada.

## Purpose

Çocuklara sayılar ve temel matematik kavramlarını interaktif bir oyun deneyimiyle öğretmek. Yaş grubu seçimi ile farklı zorluk seviyeleri sunar.

## Stack

| Bileşen | Teknoloji |
|---------|-----------|
| Runtime | HTML5, CSS3, Vanilla JavaScript |
| Deploy | Statik dosya (nginx üzerinden servis edilir) |
| Boyut | ~41 KB tek dosya |

## Entry Points

| Dosya | Görev |
|-------|-------|
| `projects/sayi-yolculugu/index.html` | Tüm oyun, stil ve mantık |

## Özellikler

- Yaş grubu seçimi (splash ekranı)
- Responsive tasarım (mobil uyumlu)
- Koyu tema (dark mode)
- Skor ve ilerleme takibi

## Deploy

Statik hosting olarak nginx üzerinden servis edilir. Build gerektirmez.

```bash
# Nginx config'de statik dosya servisi
location /sayi-yolculugu {
    alias /home/akn/local/projects/sayi-yolculugu/;
    try_files $uri $uri/ =404;
}
```

## Dependencies

- [[infrastructure]] — nginx ters proxy, SSL

## Recent Commits

- (monorepo içinde izleniyor)
