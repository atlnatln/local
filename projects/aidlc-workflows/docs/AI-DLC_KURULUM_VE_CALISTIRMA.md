# AI-DLC Kurulum ve Çalıştırma Kılavuzu

Bu doküman, AI-DLC (Yapay Zeka Destekli Geliştirme Yaşam Döngüsü) metodolojisinin Kimi Code CLI ile nasıl kurulacağını, çalıştırılacağını ve yönetileceğini açıklar.

---

## İçindekiler

1. [Genel Bakış](#1-genel-bakış)
2. [Ön Koşullar](#2-ön-koşullar)
3. [Adım 1: Bootstrap (İlk Oturum)](#3-adım-1-bootstrap-ilk-oturum)
4. [Adım 2: Master Orchestrator](#4-adım-2-master-orchestrator)
5. [Agent Hiyerarşisi](#5-agent-hiyerarşisi)
6. [Context Yönetimi](#6-context-yönetimi)
7. [Hook Sistemi](#7-hook-sistemi)
8. [Simülasyon Örneği](#8-simülasyon-örneği)
9. [Sık Karşılaşılan Sorunlar](#9-sık-karşılaşılan-sorunlar)

---

## 1. Genel Bakış

AI-DLC, bir yapay zeka asistanını yazılım geliştirme sürecinden yapılandırılmış bir şekilde geçiren bir metodolojidir. İki ana aşamadan oluşur:

- **Inception (Başlangıç):** Ne inşa edileceği ve neden — gereksinimler, kullanıcı hikayeleri, tasarım
- **Construction (Yapım):** Nasıl inşa edileceği — kod, test, altyapı

Kimi Code CLI ile bu süreç, bir **Bootstrap** adımıyla başlar ve ardından **Master Orchestrator** tarafından yönetilir.

---

## 2. Ön Koşullar

### Gerekli Dosyalar

Proje kök dizininde aşağıdaki yapı olmalıdır:

```text
proje-koku/
├── aidlc-rules/             # AI-DLC kural dosyaları
├── .kimi/
│   ├── agent.yaml           # Ana agent yapılandırması
│   ├── agents/              # Agent tanımları
│   │   ├── master-orchestrator.yaml
│   │   ├── inception-coder.yaml
│   │   ├── construction-coder.yaml
│   │   └── operations-coder.yaml
│   ├── subagents/           # Subagent rolleri
│   ├── hooks/               # Lifecycle hook'ları
│   └── skills/              # Skill dosyaları
├── docs/                    # Proje dokümantasyonu
│   ├── WORKING-WITH-AIDLC.md
│   └── writing-inputs/      # Vizyon ve tech-env kılavuzları
└── (daha sonra oluşacak)
    └── aidlc-docs/          # AI-DLC kalıcı bellek (markdown)
```

### Hook Sistemi

`~/.kimi/config.toml` dosyasında aşağıdaki hook'lar tanımlı olmalıdır:

```toml
[[hooks]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "/home/akn/local/projects/aidlc-workflows/.kimi/hooks/domain-guard.sh"
timeout = 10

[[hooks]]
event = "PreToolUse"
matcher = "Shell"
command = "/home/akn/local/projects/aidlc-workflows/.kimi/hooks/protect-rules.sh"
timeout = 10

[[hooks]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "/home/akn/local/projects/aidlc-workflows/.kimi/hooks/markdown-lint.sh"
timeout = 30

[[hooks]]
event = "Stop"
command = "/home/akn/local/projects/aidlc-workflows/.kimi/hooks/check-todos.sh"
timeout = 10
```

### Girdi Belgeleri

Başlamadan önce hazırlanması gereken iki belge:

1. **Vizyon Belgesi** (`vision.md`) — ne inşa edilecek ve neden
2. **Teknik Ortam Belgesi** (`tech-env.md`) — hangi araçlar ve kısıtlar

Detaylar için bkz. [writing-inputs/inputs-quickstart.md](writing-inputs/inputs-quickstart.md)

---

## 3. Adım 1: Bootstrap (İlk Oturum)

Bootstrap, AI-DLC sürecini başlatan ilk adımdır. Default agent ile yapılır.

### Komut

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi
```

### Prompt

```text
Yeni proje başlat: [Proje Adı]. AI-DLC workflow'u başlat.
Vizyon belgesi: [vision.md yolu]
Teknik ortam belgesi: [tech-env.md yolu]
```

### Ne Yapar

1. `aidlc-docs/` dizin yapısını oluşturur
2. `aidlc-state.md` ve `audit.md`'yi başlatır
3. Workspace taraması yapar (greenfield/brownfield tespiti)
4. Gereksinimler analizine başlar
5. Açıklayıcı soruları `requirement-verification-questions.md`'ye yazar

### Çıktı

```text
aidlc-docs/
├── aidlc-state.md           # Workflow durum izleyici
├── audit.md                 # Denetim kayıtları
├── inception/
│   ├── plans/
│   │   └── execution-plan.md
│   └── requirements/
│       ├── requirements.md
│       └── requirement-verification-questions.md
```

### Sonraki Adım

Soruları cevapla → "Soruları cevapladım, devam et" de → agent devam eder.

Bootstrap tamamlandığında (tüm inception aşamaları bittikten veya context dolunca), session kapatılır. Sonraki oturumda Master Orchestrator devreye girer.

---

## 4. Adım 2: Master Orchestrator

Master Orchestrator, AI-DLC sürecinin koordinatörüdür. Bootstrap sonrası her yeni oturumda çalıştırılır.

### Komut

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi --agent-file .kimi/agents/master-orchestrator.yaml
```

> **Neden proje kökünde çalıştırılır:** `master-orchestrator.yaml` içindeki `system_prompt_path: .kimi/agents/master-prompt.md` göreli yoldur. Komutun çalıştırıldığı dizine göre çözümlenir.

### Ne Yapar

1. `aidlc-docs/aidlc-state.md`'yi okur → mevcut durumu tespit eder
2. Stage bağımlılık haritasına göre sıradaki stage'i belirler
3. Uygun sub-agent'ı (`Agent` tool'u ile) çağırır:
   - `inception-coder` — planlama, gereksinimler, kullanıcı hikayeleri
   - `construction-coder` — kod, test (full-stack)
   - `operations-coder` — Docker, dağıtım
4. Stage çıktılarını `aidlc-docs/` altına kaydeder
5. `aidlc-state.md`'yi **atomik** olarak günceller (tek `WriteFile` ile)
6. `audit.md`'ye ISO 8601 zaman damgalı kayıt ekler

### Stage Bağımlılık Haritası

```
workspace-detection
  → reverse-engineering (brownfield ise)
  → requirements-analysis
    → user-stories (koşullu)
    → workflow-planning
    → application-design
      → units-generation
        → functional-design → code-generation → build-and-test
```

### Context Yönetimi Kuralları

- **Yeni phase = yeni instance** — Her `Agent()` çağrısı temiz context ile başlar (`resume` kullanılmaz)
- **Context %70** → `/compact` (checkpoint sonrası)
- **Context %80** → Session sonlandır, `aidlc-state.md`'den devam et

---

## 5. Agent Hiyerarşisi

| Seviye | Agent | Ne Zaman Çalışır | Çalışma Dizini | Görevi |
|--------|-------|------------------|----------------|--------|
| 0 | **default** | Bootstrap | Proje kökü | `aidlc-docs/` oluşturur, state başlatır |
| 1 | **master-orchestrator** | Her yeni oturum | `aidlc-docs/` | Stage koordinasyonu, state yönetimi |
| 2 | **inception-coder** | Master çağırır | `aidlc-docs/inception/` | Planlama, DDD, gereksinimler, kullanıcı hikayeleri |
| 2 | **construction-coder** | Master çağırır | `src/{birim-adı}/` + `aidlc-docs/construction/` | Kod + test (full-stack) |
| 2 | **operations-coder** | Master çağırır | `infrastructure/` + `aidlc-docs/operations/` | Docker, dağıtım, izleme |

> **Kural:** Sub-agent'lar kendi alt ajanlarını çağıramaz (maksimum 2 seviye: Root → Sub).

---

## 6. Context Yönetimi

AIDLC, bağlamın (context) etkin yönetimine dayanır.

### Temel Kural

**Her doğal karar noktasında bağlamı temizle.**

AIDLC geçitler (gates) etrafında inşa edilmiştir — yapay zekanın durduğu ve sizden bir şey beklediği anlar:
- Soru dosyasını yanıtlamanızı beklediğinde
- Belgeyi onaylamanızı beklediğinde
- Planı incelemenizi beklediğinde

Bu duraklar yalnızca onay kontrol noktaları değil, aynı zamanda **taze bağlam başlatmak için doğru anlardır**.

### Nasıl Yapılır

1. **Soruları yanıtla** → "Devam et" de
2. **Yeni context başlat** — kimi session'ını kapatıp yeniden aç
3. **Master Orchestrator'u çalıştır**:
   ```bash
   cd /home/akn/local/projects/aidlc-workflows
   kimi --agent-file .kimi/agents/master-orchestrator.yaml
   ```
4. Master otomatik olarak `aidlc-state.md`'yi okur ve kaldığı yerden devam eder

### Neden Önemli

Bağlamın birden fazla geçitte birikmesine izin verirseniz, yapay zeka önceki talimatların ve yapıtların sıkıştırılmış veya kısmen kaybolmuş bir sürümünden çalışmaya başlar. Çıktı kalitesi ince ve teşhisi zor şekillerde düşer.

> **İpucu:** Bağlamı her sıfırladığınızda mevcut tüm değişiklikleri depoya işleyin ve gönderin. Saniyeler sürer ve her zaman temiz bir kurtarma noktası sağlar.

---

## 7. Hook Sistemi

Hook'lar, kimi CLI'nin yaşam döngüsü olaylarına müdahale eden shell script'leridir.

| Hook | Event | Tetikleyici | Engelleyici mi? | İşlevi |
|------|-------|-------------|-----------------|--------|
| `domain-guard.sh` | PreToolUse | WriteFile/StrReplaceFile | **Evet** (Exit 2) | Agent'ları kendi yetki alanlarına hapseder |
| `protect-rules.sh` | PreToolUse | Shell | **Evet** (Exit 2) | Kural dosyalarını silme/taşıma koruması |
| `markdown-lint.sh` | PostToolUse | WriteFile/StrReplaceFile | Hayır (Uyarı) | .md dosyalarını otomatik lint kontrolü |
| `check-todos.sh` | Stop | — | Hayır (Hatırlatma) | Arka plan görevleri ve todo kontrolü |

### Fail-Open Davranışı

Tüm hook'lar "güvenli mod" (fail-open) çalışır:
- Script bulunamazsa → işlem engellenmez
- Timeout aşılırsa → işlem engellenmez
- Script çökerse → işlem engellenmez

Bu, normal workflow'u aksatmaz.

---

## 8. Simülasyon Örneği

Bu bölüm, AI-DLC sürecinin adım adım nasıl çalıştığını gösterir. Örnek olarak bilimsel hesap makinesi API'si (sci-calc) kullanılır.

### Senaryo: CalcEngine API

**Proje:** REST API ile matematik ifadelerini değerlendiren bir servis.

#### Adım 1 — Girdi Belgelerini Hazırla

Vizyon belgesi (`vision.md`):
```markdown
## Yönetici Özeti
CalcEngine, geliştiricilerin matematik ifadelerini string olarak gönderip
sonuç almasını sağlayan bir REST API'dir.

## MVP Kapsamında
- İfade değerlendirme: "2 * sin(pi/4) + sqrt(16)"
- Temel aritmetik, trigonometri, logaritmalar
- API anahtarı kimlik doğrulaması (ücretsiz + ücretli katmanlar)

## MVP Dışında
- Matris işlemleri (Aşama 2)
- Sembolik hesaplama (Aşama 3)
```

Teknik ortam belgesi (`tech-env.md`):
```markdown
## Dil ve Paket Yöneticisi
- Python 3.12+, uv

## Web Çerçevesi
- FastAPI + Pydantic v2

## Bulut ve Dağıtım
- AWS, sunucusuz (Lambda + API Gateway)
- DynamoDB API anahtarı depolama için

## Test
- pytest (%90 kapsam)
- hypothesis (özellik tabanlı test)
```

#### Adım 2 — Bootstrap

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi
```

**Prompt:**
```text
Yeni proje: CalcEngine. AI-DLC workflow'u başlat.
Vizyon: docs/writing-inputs/example-minimal-vision-scientific-calculator-api.md
Teknik ortam: docs/writing-inputs/example-minimal-tech-env-scientific-calculator-api.md
```

**Beklenen Çıktı:**
- `aidlc-docs/` dizini oluşturulur
- `aidlc-state.md` başlatılır
- `audit.md` başlatılır
- Workspace taraması: greenfield tespit edilir
- Gereksinimler analizi başlar
- `requirement-verification-questions.md` oluşturulur

#### Adım 3 — Soruları Yanıtla

`aidlc-docs/inception/requirements/requirement-verification-questions.md` dosyasını aç, soruları cevapla.

**Prompt:**
```text
Soruları cevapladım. Lütfen dosyayı yeniden oku ve devam et.
```

#### Adım 4 — Context Sıfırla

Session'ı kapat (context temizle).

#### Adım 5 — Master Orchestrator'u Çalıştır

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi --agent-file .kimi/agents/master-orchestrator.yaml
```

**Beklenen Davranış:**
1. Master `aidlc-state.md`'yi okur
2. Durum: "requirements-analysis tamamlandı, user-stories bekleniyor"
3. `inception-coder` sub-agent'ını çağırır
4. Inception-coder kullanıcı hikayelerini oluşturur
5. Master state'i günceller
6. Context dolarsa session sonlanır

#### Adım 6 — Tekrar Context Sıfırla ve Master Çalıştır

Bu döngü, tüm inception ve construction aşamaları tamamlanana kadar devam eder:

```bash
kimi --agent-file .kimi/agents/master-orchestrator.yaml
# → application-design
# → units-generation
# → functional-design
# → code-generation
# → build-and-test
```

Her seferinde master kaldığı yerden devam eder.

---

## 9. Sık Karşılaşılan Sorunlar

### "aidlc-state.md bulunamadı" hatası

**Neden:** Master Orchestrator bootstrap yapılmadan çalıştırılmış.

**Çözüm:** Önce `kimi` ile bootstrap yapın, sonra master'ı çalıştırın.

### "Cross-domain write blocked" hatası

**Neden:** Bir sub-agent kendi yetki alanı dışına yazmaya çalışıyor.

**Çözüm:** `domain-guard.sh` hook'u devreye girmiştir. Doğru agent'ı kullandığınızdan emin olun. Kod yazması gerekiyorsa `construction-coder` çağrılmalı.

### Hook'lar çalışmıyor

**Neden:** `~/.kimi/config.toml`'da tanımlı değil veya dosya yolu yanlış.

**Çözüm:**
```bash
# Hook'ların varlığını kontrol et
ls -la /home/akn/local/projects/aidlc-workflows/.kimi/hooks/

# Kimi içinde aktif hook'ları gör
/hooks
```

### Context çok hızlı doluyor

**Neden:** Çok fazla dosya aynı session'da işleniyor.

**Çözüm:** Her doğal karar noktasında session'ı kapatıp master orchestrator ile yeni session başlatın.

---

## Referanslar

- [WORKING-WITH-AIDLC.md](WORKING-WITH-AIDLC.md) — Detaylı etkileşim kılavuzu
- [inputs-quickstart.md](writing-inputs/inputs-quickstart.md) — Girdi belgesi hazırlama
- [vision-document-guide.md](writing-inputs/vision-document-guide.md) — Vizyon belgesi yazma
- [technical-environment-guide.md](writing-inputs/technical-environment-guide.md) — Teknik ortam belgesi yazma
