# MathLock Soru Üretim Mimarisi

## Özet

MathLock'ta soru üretimi **tek kaynaktan** yapılır: **AGENTS.md + Copilot CLI**.
Hiçbir aşamada OpenAI/Gemini API key veya ayrı algoritmik üretici kullanılmaz.

## Tek Motor: AGENTS.md + Copilot CLI

Tüm soru üretimi `ai-generate.sh` üzerinden **GitHub Copilot CLI** ile yapılır:

```
use_credit API → stats.json yaz → ai-generate.sh → Copilot CLI → questions.json → QuestionSet DB
```

- **Kurallar:** `AGENTS.md` (Vygotsky ZPD, 6 soru tipi, 5 zorluk seviyesi, psikolojik sıralama)
- **Kimlik doğrulama:** `GITHUB_TOKEN` (GitHub Copilot hesabı)
- **Model:** `claude-haiku-4.5` (Copilot CLI üzerinden)
- **Girdi:** `data/stats.json` (çocuğun performans verileri)
- **Çıktı:** 50 soru + konu açıklamaları (JSON)
- **Doğrulama:** `validate-questions.py` ile format/içerik kontrolü
- **Tetikleme:** `POST /api/mathlock/credits/use/` → `_generate_via_copilot()` → `ai-generate.sh --vps-mode --skip-sync`

### Akış

1. Android uygulaması `POST /credits/use/` çağırır
2. Backend krediyi düşer, `child.stats_json`'ı `data/stats.json`'a yazar
3. `ai-generate.sh --vps-mode --skip-sync` subprocess olarak çalıştırılır
4. Copilot CLI `AGENTS.md` kurallarını okur + stats'a göre kişiselleştirilmiş 50 soru üretir
5. `validate-questions.py` ile doğrulama yapılır
6. Backend `data/questions.json`'ı okur → `QuestionSet`'e kaydeder
7. Hata durumunda kredi iade edilir (503 döner, `credits_refunded: true`)

## ⛔ Kaldırılan Bileşenler

- `question_generator.py` → **Silindi** (Haziran 2025) — Algoritmik üretici, AGENTS.md ile ikilik yaratıyordu
- `ai_proxy.py` → **Silindi** — OpenAI/Gemini proxy'si
- `ai_query_view` endpoint → **Silindi**
- `settings.py`'deki `AI_PROVIDER`, `OPENAI_API_KEY`, `GEMINI_API_KEY` → **Silindi**

Bu karar bilinçlidir: Copilot CLI zaten GitHub aboneliği ile gelir, ek API maliyeti yoktur.
