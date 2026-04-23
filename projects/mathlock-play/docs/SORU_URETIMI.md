# MathLock Soru Üretim Mimarisi

## Özet

MathLock'ta soru üretimi **tek kaynaktan** yapılır: **AGENTS.md + kimi-cli**.
Hiçbir aşamada OpenAI/Gemini API key veya ayrı algoritmik üretici kullanılmaz.

## Tek Motor: AGENTS.md + kimi-cli

Tüm soru üretimi `ai-generate.sh` üzerinden **kimi-cli** ile yapılır:

```
use_credit API → stats.json yaz → ai-generate.sh → kimi-cli → questions.json → QuestionSet DB
```

- **Kurallar:** `AGENTS.md` (Vygotsky ZPD, 6 soru tipi, 5 zorluk seviyesi, psikolojik sıralama)
- **Kimlik doğrulama:** OAuth (kimi-cli `kimi login` ile cihaz yetkilendirmesi)
- **Model:** `kimi-code/kimi-for-coding` (Kimi-k2.6, 256K context window)
- **Girdi:** `data/stats.json` (çocuğun performans verileri)
- **Çıktı:** 50 soru + konu açıklamaları (JSON)
- **Doğrulama:** `validate-questions.py` ile format/içerik kontrolü
- **Tetikleme:** `POST /api/mathlock/credits/use/` → `_generate_via_kimi()` → `ai-generate.sh --vps-mode --skip-sync`

### Akış

1. Android uygulaması `POST /credits/use/` çağırır
2. Backend krediyi düşer, `child.stats_json`'ı `data/stats.json`'a yazar
3. `ai-generate.sh --vps-mode --skip-sync` subprocess olarak çalıştırılır
4. kimi-cli `AGENTS.md` kurallarını okur + stats'a göre kişiselleştirilmiş 50 soru üretir
5. `validate-questions.py` ile doğrulama yapılır
6. Backend `data/questions.json`'ı okur → `QuestionSet`'e kaydeder
7. Hata durumunda kredi iade edilir (503 döner, `credits_refunded: true`)

## ⛔ Kaldırılan Bileşenler

- `question_generator.py` → **Silindi** (Haziran 2025) — Algoritmik üretici, AGENTS.md ile ikilik yaratıyordu
- `ai_proxy.py` → **Silindi** — OpenAI/Gemini proxy'si
- `ai_query_view` endpoint → **Silindi**
- `settings.py`'deki `AI_PROVIDER`, `OPENAI_API_KEY`, `GEMINI_API_KEY` → **Silindi**

Bu karar bilinçlidir: kimi-cli OAuth ile çalışır, ek API anahtarı maliyeti yoktur.
