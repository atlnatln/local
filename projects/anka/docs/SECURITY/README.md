# Anka Platform — Güvenlik Dokümantasyonu

**Son Güncelleme:** Mart 2026  
**Kapsam:** Anka Platform (Django API + Next.js Frontend + Docker/Nginx Altyapı)

---

## Genel Bakış

Bu dizin, Anka Platform'un güvenlik politikalarını, prosedürlerini ve denetim kayıtlarını içerir. Tüm ekip üyelerinin bu belgeleri okuması ve güncel tutması zorunludur.

## Belge Dizini

| Belge | Açıklama | Hedef Kitle |
|-------|----------|-------------|
| [security-audit-2026-02-28.md](security-audit-2026-02-28.md) | İlk kapsamlı güvenlik denetimi raporu (Şubat, Haziran, Temmuz 2026 güncellemeleri dahil) | Tüm ekip |
| [incident-response-playbook.md](incident-response-playbook.md) | Güvenlik ihlali müdahale planı | Ops / Backend |
| [secret-rotation-runbook.md](secret-rotation-runbook.md) | Gizli anahtar rotasyon prosedürleri | DevOps |
| [api-security-policy.md](api-security-policy.md) | API güvenlik politikası ve kuralları | Backend dev |
| [hardening-checklist.md](hardening-checklist.md) | Sistem sıkılaştırma kontrol listesi | DevOps / Ops |
| [kvkk-data-compliance.md](kvkk-data-compliance.md) | KVKK/GDPR veri uyumluluk rehberi | Tüm ekip |
| [dependency-update-policy.md](dependency-update-policy.md) | Bağımlılık güncelleme ve zafiyet tarama politikası | Tüm dev |

## Okuma Sırası (Yeni Ekip Üyeleri)

1. Bu README
2. `security-audit-2026-02-28.md` — Mevcut durum ve bulgular
3. `api-security-policy.md` — API geliştirme kuralları
4. `hardening-checklist.md` — Deploy öncesi kontroller
5. `kvkk-data-compliance.md` — Veri koruma zorunlulukları

## Güncelleme İlkesi

- Her güvenlik değişikliğinde ilgili belge aynı PR'da güncellenir.
- Üç ayda bir güvenlik denetimi (`security-audit-*`) tekrarlanır.
- Yeni servis/endpoint eklendiğinde `api-security-policy.md` gözden geçirilir.
- Secret rotasyon yapıldığında `secret-rotation-runbook.md`'ye tarih ve kapsam notu eklenir.

## İletişim

Güvenlik açığı bildirimi: Direkt olarak proje yöneticisine bildirilmelidir. Public issue/PR açılmamalı.
