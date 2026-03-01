# Anka Platform — Güvenlik Dokümantasyonu

Bu klasör, aktif güvenlik politika ve operasyon prosedürlerini içerir.

## Aktif Belgeler

| Belge | Amaç |
|-------|------|
| [api-security-policy.md](api-security-policy.md) | API güvenlik kuralları |
| [hardening-checklist.md](hardening-checklist.md) | Deploy öncesi/sonrası hardening kontrolü |
| [incident-response-playbook.md](incident-response-playbook.md) | Olay müdahale akışı |
| [secret-rotation-runbook.md](secret-rotation-runbook.md) | Secret rotasyon prosedürü |
| [kvkk-data-compliance.md](kvkk-data-compliance.md) | KVKK/GDPR veri uyumluluğu |
| [dependency-update-policy.md](dependency-update-policy.md) | Bağımlılık güncelleme/zafiyet yönetimi |

## Önerilen Okuma Sırası

1. Bu README
2. `api-security-policy.md`
3. `hardening-checklist.md`
4. `incident-response-playbook.md`
5. `kvkk-data-compliance.md`

## Güncelleme Kuralı

- Güvenlik değişikliği varsa ilgili policy/runbook aynı PR’da güncellenir.
- Yeni endpoint/serviste `api-security-policy.md` gözden geçirilir.
- Secret rotasyonda `secret-rotation-runbook.md` tarih/kapsam notu eklenir.
