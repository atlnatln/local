# AI-DLC Simülasyon Rehberi — CalcEngine (sci-calc)

Bu rehber, AI-DLC sürecinin gerçek bir test case (CalcEngine) üzerinde nasıl çalıştırılacağını adım adım açıklar.

---

## Hazırlık Durumu

✅ `vision.md` proje köküne kopyalandı  
✅ `tech-env.md` proje köküne kopyalandı  
✅ `.kimi/` yapılandırması tamam  
✅ `aidlc-rules/` mevcut  
✅ Hook'lar `~/.kimi/config.toml`'a eklendi  

---

## Simülasyon Adımları

### 🔵 Adım 1: Bootstrap (İlk Oturum)

**Terminal komutu:**

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi
```

**Gireceğin prompt:**

```text
Yeni proje başlat: CalcEngine. AI-DLC workflow'u başlat.
Vizyon belgesi: ./vision.md
Teknik ortam belgesi: ./tech-env.md
```

**Beklenen davranış:**
1. Kimi `aidlc-rules/` altındaki kuralları okur
2. `aidlc-docs/` dizinini oluşturur
3. `aidlc-state.md` ve `audit.md`'yi başlatır
4. Workspace taraması yapar → greenfield tespit eder
5. Gereksinimler analizine başlar
6. `requirement-verification-questions.md` oluşturur
7. Soruları sormak için durur

**Senin yapman gereken:**
- `aidlc-docs/inception/requirements/requirement-verification-questions.md` dosyasını aç
- Soruları cevapla (çoktan seçmeli, `[Cevap]:` etiketlerini doldur)
- "Soruları cevapladım, dosyayı yeniden oku ve devam et" de

**Context dolunca:** Session'ı kapat (Ctrl+D veya `exit` yaz). Değişiklikleri commit et.

---

### 🟢 Adım 2: Master Orchestrator

**Terminal komutu:**

```bash
cd /home/akn/local/projects/aidlc-workflows
kimi --agent-file .kimi/agents/master-orchestrator.yaml
```

**Master otomatik olarak yapacakları:**
1. `aidlc-state.md`'yi okur → "requirements-analysis tamamlandı, user-stories bekleniyor"
2. `inception-coder` sub-agent'ını çağırır
3. Inception-coder kullanıcı hikayelerini oluşturur
4. Master state'i günceller → `aidlc-state.md`'ye yazar
5. Context dolarsa session sonlanır

**Senin yapman gereken:**
- Her session sonunda `git status` ile değişiklikleri kontrol et
- Yeni session'da tekrar master'ı çalıştır
- Bu döngü tüm aşamalar bitene kadar devam eder

---

### 🟡 Adım 3: Döngü (Inception → Construction)

Master orchestrator'u tekrar tekrar çalıştırarak şu aşamalardan geçilecek:

```
1. user-stories          → inception-coder
2. workflow-planning     → inception-coder
3. application-design    → inception-coder
4. units-generation      → inception-coder
5. functional-design     → construction-coder
6. code-generation       → construction-coder
7. build-and-test        → construction-coder
```

Her aşama sonunda:
- Context sıfırla (session kapat)
- `git add -A && git commit -m "aidlc: <aşama adı>"`
- Master'ı tekrar çalıştır

---

## Beklenen Çıktılar

### Inception Sonrası

```text
aidlc-docs/
├── aidlc-state.md
├── audit.md
├── inception/
│   ├── plans/
│   │   ├── execution-plan.md
│   │   ├── story-generation-plan.md
│   │   └── user-stories-assessment.md
│   ├── requirements/
│   │   ├── requirements.md
│   │   └── requirement-verification-questions.md
│   ├── user-stories/
│   │   ├── personas.md
│   │   └── stories.md
│   └── application-design/
│       ├── application-design.md
│       ├── components.md
│       ├── component-methods.md
│       ├── services.md
│       └── component-dependency.md
```

### Construction Sonrası

```text
aidlc-docs/
├── construction/
│   ├── plans/
│   │   └── code-generation-plan.md
│   └── calcengine-api/
│       ├── functional-design/
│       │   ├── business-rules.md
│       │   └── domain-entities.md
│       ├── nfr-requirements/
│       │   └── nfr-requirements.md
│       └── code/
│           └── (markdown özetler)
src/
└── calcengine-api/
    ├── api/
    ├── engine/
    └── tests/
```

---

## Önemli Komutlar

```bash
# Durum kontrolü
cat aidlc-docs/aidlc-state.md

# Aktif hook'ları gör (kimi içinde)
/hooks

# Mevcut todo listesini kontrol et (kimi içinde)
/todo

# Context sıfırla (session kapatıp yeniden aç)
Ctrl+D  # çık
kimi --agent-file .kimi/agents/master-orchestrator.yaml  # tekrar gir
```

---

## Simülasyonu Başlat

Hazır mısın? Aşağıdaki komutu terminale yapıştır ve başla:

```bash
cd /home/akn/local/projects/aidlc-workflows && kimi
```

Sonra prompt olarak şunu gir:

```text
Yeni proje başlat: CalcEngine. AI-DLC workflow'u başlat. Vizyon: ./vision.md Teknik ortam: ./tech-env.md
```

---

> **Not:** Bu simülasyon gerçek zamanlı kimi CLI çalıştırması gerektirir. Her session 10-30 dakika sürebilir. Toplam süre projenin karmaşıklığına bağlı olarak 1-3 saat arası değişebilir.
