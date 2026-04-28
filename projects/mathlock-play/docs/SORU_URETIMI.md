# MathLock Soru Üretim Mimarisi

> **Son güncelleme:** 26 Nisan 2026 — Celery + Redis, `--locale` desteği

---

## Özet

MathLock'ta soru üretimi **tek kaynaktan** yapılır: **AGENTS.md + kimi-cli**.
Hiçbir aşamada OpenAI/Gemini API key veya ayrı algoritmik üretici kullanılmaz.

Arka plan üretimi `threading.Thread` yerine **Celery task kuyruğu** üzerinden çalışır.

---

## Tek Motor: AGENTS.md + kimi-cli

### Matematik Soru Üretimi (`ai-generate.sh`)

```
use_credit API → stats.json yaz → ai-generate.sh → kimi-cli → questions.json → QuestionSet DB
```

- **Kurallar:** `AGENTS.md` (Vygotsky ZPD, 6 soru tipi, 5 zorluk seviyesi, psikolojik sıralama)
- **Kimlik doğrulama:** OAuth (kimi-cli `kimi login` ile cihaz yetkilendirmesi)
- **Model:** `kimi-code/kimi-for-coding` (Kimi-k2.6, 256K context window)
- **Girdi:** `data/stats.json` (çocuğun performans verileri)
- **Çıktı:** 30-50 soru + konu açıklamaları (JSON, eğitim dönemine göre)
- **Doğrulama:** `validate-questions.py` ile format/içerik kontrolü
- **Tetikleme:** `POST /api/mathlock/credits/use/` → `_generate_via_kimi()` → `generate_question_set.delay()`
- **i18n:** `--locale tr|en` parametresi ile dil bazlı soru üretimi

### Sayı Yolculuğu Seviye Üretimi (`ai-generate-levels.sh`)

```
levels/progress/ API → level-stats.json yaz → ai-generate-levels.sh → kimi-cli → levels.json → LevelSet DB
```

- **Kurallar:** `AGENTS.md` (Sayı Yolculuğu bölümü) — grid boyutu, komutlar, duvar/operasyon, BFS çözülebilirlik
- **Girdi:** `data/level-stats.json` (seviye tamamlanma/yıldız/derleme verisi)
- **Çıktı:** 12 seviye (`levels.json` formatında)
- **Doğrulama:** `validate-levels.py` ile BFS çözülebilirlik kontrolü
- **Tetikleme:** `POST /api/mathlock/levels/progress/` (tüm 12 seviye bitince auto-renew) → `generate_level_set.delay()`
- **i18n:** `--locale tr|en` parametresi ile çok dilli seviye üretimi

---

## Akış (Matematik)

1. Android uygulaması `POST /credits/use/` çağırır
2. Backend krediyi düşer, `child.stats_json`'ı `data/stats.json`'a yazar
3. `generate_question_set.delay(child_pk, cb_pk, is_free, stats, education_period, locale)` çağrılır
4. Celery worker (`mathlock_celery` container) task'i işler
5. kimi-cli `AGENTS.md` kurallarını okur + stats'a göre kişiselleştirilmiş 50 soru üretir
6. `validate-questions.py` ile doğrulama yapılır
7. Backend `data/questions.json`'ı okur → `QuestionSet`'e kaydeder
8. Hata durumunda kredi iade edilir (task `max_retries=3`, `finally`'de kilit serbest bırakılır)

### Akış (Sayı Yolculuğu)

1. Android uygulaması her seviye çözüldüğünde `POST /levels/progress/` çağırır
2. 12. seviye bitince backend `all_completed` kontrolü yapar
3. Kredi varsa `_auto_renew_levels()` → `generate_level_set.delay()` çağrılır
4. Celery worker yeni 12 seviye üretir → `LevelSet` olarak DB'ye kaydeder
5. Hata durumunda kredi iade edilir, kilit `finally`'de serbest bırakılır

---

## Arka Plan Üretim Mimarisi (Celery + Redis)

```python
# credits/tasks.py
from celery import shared_task

@shared_task(bind=True, max_retries=3)
def generate_question_set(self, child_pk, cb_pk, is_free, stats, education_period, locale='tr'):
    try:
        child = ChildProfile.objects.get(pk=child_pk)
        questions = _generate_via_kimi(stats, education_period, locale)
        # ...create QuestionSet...
    except Exception as exc:
        if cb_pk and not is_free: _refund_credit(cb_pk, is_free)
        raise self.retry(exc=exc, countdown=60)
    finally:
        _release_renewal_lock(child_pk, 'questions')
```

**Docker Compose servisleri:**
```yaml
mathlock_redis:
  image: redis:7-alpine

mathlock_celery:
  build: ./backend
  command: celery -A mathlock_backend worker -l info
  environment:
    CELERY_BROKER_URL: redis://mathlock_redis:6379/0
    CELERY_RESULT_BACKEND: redis://mathlock_redis:6379/0
```

---

## ⛔ Kaldırılan Bileşenler

- `question_generator.py` → **Silindi** (Haziran 2025) — Algoritmik üretici, AGENTS.md ile ikilik yaratıyordu
- `ai_proxy.py` → **Silindi** — OpenAI/Gemini proxy'si
- `ai_query_view` endpoint → **Silindi**
- `settings.py`'deki `AI_PROVIDER`, `OPENAI_API_KEY`, `GEMINI_API_KEY` → **Silindi**
- `threading.Thread` arka plan üretimi → **Kaldırıldı** — Celery + Redis ile değiştirildi

Bu karar bilinçlidir: kimi-cli OAuth ile çalışır, ek API anahtarı maliyeti yoktur. Celery task queue ile sunucu crash veya timeout durumlarında bile üretim güvenilir şekilde retry edilir.
