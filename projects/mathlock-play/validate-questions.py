#!/usr/bin/env python3
"""
MathLock — questions.json ve topics.json doğrulama scripti.
kimi-cli'nin ürettiği soruların geçerliliğini kontrol eder.

Kullanım:
    python3 validate-questions.py                # her iki dosyayı kontrol et
    python3 validate-questions.py --questions     # sadece questions.json
    python3 validate-questions.py --topics        # sadece topics.json

Çıkış kodları: 0 = başarılı, 1 = hata var
"""

import json
import sys
import os
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
TOPICS_FILE = DATA_DIR / "topics.json"

# Dönem bazlı geçerli tipler ve soru sayıları
# NOT: Türkçe karakterli tip isimleri kullanılır (ç, ı, ö, ş, ğ, ü)
PERIOD_CONFIG = {
    "okul_oncesi": {
        "types": {"sayma", "toplama", "çıkarma", "karşılaştırma", "örüntü"},
        "count": 30,
    },
    "sinif_1": {
        "types": {"toplama", "çıkarma", "sıralama", "eksik_sayı"},
        "count": 40,
    },
    "sinif_2": {
        "types": {"toplama", "çıkarma", "çarpma", "bölme", "sıralama", "eksik_sayı"},
        "count": 50,
    },
    "sinif_3": {
        "types": {"toplama", "çıkarma", "çarpma", "bölme", "sıralama", "eksik_sayı", "kesir", "problem"},
        "count": 50,
    },
    "sinif_4": {
        "types": {"toplama", "çıkarma", "çarpma", "bölme", "sıralama", "eksik_sayı", "kesir", "problem"},
        "count": 50,
    },
}

EXPECTED_DISTRIBUTION = {
    "okul_oncesi": {"sayma": 0.27, "toplama": 0.27, "çıkarma": 0.13, "karşılaştırma": 0.20, "örüntü": 0.13},
    "sinif_1": {"toplama": 0.45, "çıkarma": 0.35, "sıralama": 0.13, "eksik_sayı": 0.07},
    "sinif_2": {"toplama": 0.44, "çıkarma": 0.32, "çarpma": 0.10, "bölme": 0.08, "sıralama": 0.04, "eksik_sayı": 0.02},
    "sinif_3": {"toplama": 0.24, "çıkarma": 0.20, "çarpma": 0.20, "bölme": 0.14, "sıralama": 0.06, "eksik_sayı": 0.04, "kesir": 0.06, "problem": 0.06},
    "sinif_4": {"toplama": 0.16, "çıkarma": 0.16, "çarpma": 0.18, "bölme": 0.18, "sıralama": 0.06, "eksik_sayı": 0.04, "kesir": 0.12, "problem": 0.10},
}

VALID_INTERACTION_MODES = {"text-input", "tap-to-count", "pattern-select", "tap-to-choose"}
CODE_RE = re.compile(r"^\d{4}G\d-B\d-\d{4}$")

ID_RANGES = {
    "okul_oncesi": 1000,
    "sinif_1": 2000,
    "sinif_2": 3000,
    "sinif_3": 4000,
    "sinif_4": 5000,
}
ALL_VALID_TYPES = set().union(*(c["types"] for c in PERIOD_CONFIG.values()))
REQUIRED_Q_FIELDS = {"id", "text", "answer", "type", "difficulty", "hint"}
REQUIRED_TOPIC_FIELDS = {"title", "explanation", "example", "tips"}

# Aktif dönem (komut satırından veya questions.json'dan belirlenir)
ACTIVE_PERIOD = None

errors = []
warnings = []


def err(msg):
    errors.append(f"  ❌ {msg}")


def warn(msg):
    warnings.append(f"  ⚠️  {msg}")


def _extract_numbers(text: str) -> list:
    """Metinden tüm tam sayıları çıkarır."""
    return [int(m.group()) for m in re.finditer(r"\d+", text)]


def validate_math(q):
    """Basit matematik doğrulaması — mümkün olan soruları kontrol et."""
    text = q["text"]
    answer = q["answer"]
    qtype = q["type"]

    if qtype == "toplama":
        m = re.match(r"^(\d+)\s*\+\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a + b != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a+b}")
                return
        # Üç sayılı toplama
        m = re.match(r"^(\d+)\s*\+\s*(\d+)\s*\+\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a + b + c != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a+b+c}")
                return

    elif qtype == "çıkarma":
        m = re.match(r"^(\d+)\s*-\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a - b != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a-b}")
                return
            if a - b < 0:
                err(f"Soru {q['id']}: Çıkarma sonucu negatif: {a}-{b}={a-b}")
                return
        # Üç sayılı çıkarma (d5)
        m = re.match(r"^(\d+)\s*-\s*(\d+)\s*-\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b, c = int(m.group(1)), int(m.group(2)), int(m.group(3))
            if a - b - c != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a-b-c}")
                return
            if a - b - c < 0:
                err(f"Soru {q['id']}: Çıkarma sonucu negatif: {a}-{b}-{c}={a-b-c}")
                return

    elif qtype == "çarpma":
        m = re.match(r"^(\d+)\s*[×xX]\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a * b != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a*b}")
                return
            if a * b > 10000:
                err(f"Soru {q['id']}: Çarpma sonucu 10000'i aşıyor: {a}×{b}={a*b}")
                return

    elif qtype == "bölme":
        m = re.match(r"^(\d+)\s*[÷/]\s*(\d+)\s*=\s*\?$", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b == 0:
                err(f"Soru {q['id']}: Sıfıra bölme!")
                return
            if a % b != 0:
                err(f"Soru {q['id']}: {text} → tam bölünmüyor ({a}/{b}={a/b:.2f})")
                return
            if a // b != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a//b}")
                return

    elif qtype == "eksik_sayı":
        # ? + a = b → answer = b - a
        m = re.match(r"^\?\s*\+\s*(\d+)\s*=\s*(\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b - a != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {b-a}")
                return
        # a + ? = b → answer = b - a
        m = re.match(r"^(\d+)\s*\+\s*\?\s*=\s*(\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b - a != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {b-a}")
                return
        # ? - a = b → answer = b + a
        m = re.match(r"^\?\s*-\s*(\d+)\s*=\s*(\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if b + a != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {b+a}")
                return
        # a × ? = b → answer = b / a  (d4)
        m = re.match(r"^(\d+)\s*[×xX]\s*\?\s*=\s*(\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a == 0:
                err(f"Soru {q['id']}: Sıfıra bölme (a × ? = b, a=0)")
                return
            if b % a != 0:
                err(f"Soru {q['id']}: {text} → tam bölünmüyor ({b}/{a})")
                return
            if b // a != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {b//a}")
                return
        # ? ÷ a = b → answer = a * b  (d5)
        m = re.match(r"^\?\s*[÷/]\s*(\d+)\s*=\s*(\d+)", text)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            if a * b != answer:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {a*b}")
                return

    elif qtype == "sıralama":
        numbers = _extract_numbers(text)
        if len(numbers) >= 2:
            if "büyük" in text or "büyüğü" in text:
                expected = max(numbers)
            elif "küçük" in text or "küçüğü" in text:
                expected = min(numbers)
            else:
                expected = None
            if expected is not None and answer != expected:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {expected}")
                return

    elif qtype == "karşılaştırma":
        numbers = _extract_numbers(text)
        if len(numbers) == 2:
            if "büyük" in text:
                expected = max(numbers)
            else:
                expected = min(numbers)
            if answer != expected:
                err(f"Soru {q['id']}: {text} → cevap {answer} olmamalı, doğru: {expected}")
                return

    elif qtype == "sayma":
        # Emoji sayma sorularında cevap sayısal olmalı
        if answer < 0:
            err(f"Soru {q['id']}: Sayma sorusu cevabı negatif olamaz: {answer}")
            return

    elif qtype == "örüntü":
        # Örüntü soruları manuel doğrulama gerektirir
        if answer < 0:
            err(f"Soru {q['id']}: Örüntü sorusu cevabı negatif olamaz: {answer}")
            return

    elif qtype == "kesir":
        # Kesir soruları metin tabanlıdır; cevap sayısal olmalı
        if answer < 0:
            err(f"Soru {q['id']}: Kesir sorusu cevabı negatif olamaz: {answer}")
            return

    elif qtype == "problem":
        # Problem soruları manuel doğrulama gerektirir
        if answer < 0:
            err(f"Soru {q['id']}: Problem sorusu cevabı negatif olamaz: {answer}")
            return


def validate_questions():
    print("📋 questions.json doğrulanıyor...")

    if not QUESTIONS_FILE.exists():
        err("questions.json bulunamadı!")
        return

    try:
        data = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"JSON parse hatası: {e}")
        return

    # Üst seviye alanlar
    for field in ["version", "generatedAt", "generatedBy", "difficultyProfile", "questions"]:
        if field not in data:
            err(f"Üst seviye alan eksik: '{field}'")

    if "questions" not in data:
        return

    questions = data["questions"]

    # Dönemi belirle
    global ACTIVE_PERIOD
    if ACTIVE_PERIOD is None:
        ACTIVE_PERIOD = data.get("educationPeriod", "sinif_2")
    period_cfg = PERIOD_CONFIG.get(ACTIVE_PERIOD, PERIOD_CONFIG["sinif_2"])
    valid_types = period_cfg["types"]
    expected_count = period_cfg["count"]
    print(f"  📚 Dönem: {ACTIVE_PERIOD} ({expected_count} soru bekleniyor)")

    # Soru sayısı kontrolü
    if len(questions) != expected_count:
        err(f"Soru sayısı {expected_count} olmalı, {len(questions)} bulundu")

    seen_ids = set()
    seen_texts = set()
    types_found = set()

    for q in questions:
        qid = q.get("id", "?")

        # Zorunlu alanlar
        missing = REQUIRED_Q_FIELDS - set(q.keys())
        if missing:
            err(f"Soru {qid}: Eksik alanlar: {missing}")
            continue

        # ID kontrolü
        if q["id"] in seen_ids:
            err(f"Soru {qid}: Tekrar eden id")
        seen_ids.add(q["id"])

        # ID kontrolü — offset'li ID'ler için normalize et
        raw_id = q["id"]
        period_offset = ID_RANGES.get(ACTIVE_PERIOD, 0)
        normalized_id = raw_id - period_offset if raw_id > period_offset else raw_id
        if normalized_id < 1 or normalized_id > expected_count:
            err(f"Soru {qid}: id 1-{expected_count} arasında olmalı (raw={raw_id})")

        # Text tekrarı
        if q["text"] in seen_texts:
            err(f"Soru {qid}: Tekrar eden soru metni: '{q['text']}'")
        seen_texts.add(q["text"])

        # Tip kontrolü
        if q["type"] not in valid_types:
            err(f"Soru {qid}: Geçersiz tip '{q['type']}'. {ACTIVE_PERIOD} için geçerliler: {valid_types}")
        types_found.add(q["type"])

        # Zorluk kontrolü
        if not (1 <= q["difficulty"] <= 5):
            err(f"Soru {qid}: Zorluk 1-5 arasında olmalı, {q['difficulty']} bulundu")

        # Cevap kontrolü
        if not isinstance(q["answer"], int):
            err(f"Soru {qid}: Cevap tam sayı olmalı, {type(q['answer']).__name__} bulundu")
        elif q["answer"] < 0:
            err(f"Soru {qid}: Cevap negatif olamaz: {q['answer']}")

        # Hint boş olmamalı
        if not q.get("hint", "").strip():
            warn(f"Soru {qid}: Hint boş")
        else:
            hint_len = len(q["hint"].strip())
            if hint_len < 10:
                warn(f"Soru {qid}: Hint çok kısa ({hint_len} karakter)")
            elif hint_len > 60:
                warn(f"Soru {qid}: Hint çok uzun ({hint_len} karakter)")

        # code formatı (varsa)
        if "code" in q:
            if not CODE_RE.match(str(q["code"])):
                err(f"Soru {qid}: Geçersiz code formatı: '{q['code']}' (beklenen: YYYYG{grade}-B{batch}-{seq:04d})")

        # interactionMode (varsa)
        if "interactionMode" in q:
            if q["interactionMode"] not in VALID_INTERACTION_MODES:
                err(f"Soru {qid}: Geçersiz interactionMode: '{q['interactionMode']}'")

        # Matematik doğrulaması
        validate_math(q)

    # Dağılım uyarıları — temel tipler dönem bazlı
    core_types = {"toplama", "çıkarma"} & valid_types
    for ct in core_types:
        if ct not in types_found:
            warn(f"{ct} sorusu yok — {ACTIVE_PERIOD} için temel tip")

    # Zorluk dağılımı
    diff_counts = {}
    for q in questions:
        d = q.get("difficulty", 0)
        diff_counts[d] = diff_counts.get(d, 0) + 1

    type_counts = {}
    for q in questions:
        t = q.get("type", "?")
        type_counts[t] = type_counts.get(t, 0) + 1

    print(f"  📊 Tip dağılımı: {dict(sorted(type_counts.items()))}")
    print(f"  📊 Zorluk dağılımı: {dict(sorted(diff_counts.items()))}")

    # Tip dağılımı tolerance kontrolü (%5)
    if ACTIVE_PERIOD in EXPECTED_DISTRIBUTION:
        expected = EXPECTED_DISTRIBUTION[ACTIVE_PERIOD]
        total = len(questions)
        tolerance = 0.05
        for t, expected_ratio in expected.items():
            actual_count = type_counts.get(t, 0)
            actual_ratio = actual_count / total
            diff = abs(actual_ratio - expected_ratio)
            if diff > tolerance:
                warn(f"Tip dağılımı sapması: {t} beklenen %{expected_ratio*100:.0f} ({int(expected_ratio*total)}), "
                     f"gerçekleşen %{actual_ratio*100:.0f} ({actual_count}) — sapma %{diff*100:.1f} > %5")

    # Ardışık aynı tip kontrolü (max 3)
    if len(questions) >= 4:
        for i in range(len(questions) - 3):
            types_window = [questions[i+j].get("type") for j in range(4)]
            if len(set(types_window)) == 1:
                warn(f"Soru {questions[i]['id']}-{questions[i+3]['id']}: Arka arkaya 4+ aynı tip ({types_window[0]})")


def validate_topics():
    print("📋 topics.json doğrulanıyor...")

    if not TOPICS_FILE.exists():
        err("topics.json bulunamadı!")
        return

    try:
        topics = json.loads(TOPICS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        err(f"JSON parse hatası: {e}")
        return

    if not isinstance(topics, dict):
        err("topics.json bir obje (dict) olmalı")
        return

    # questions.json'daki tipleri kontrol et
    if QUESTIONS_FILE.exists():
        try:
            qdata = json.loads(QUESTIONS_FILE.read_text(encoding="utf-8"))
            q_types = {q["type"] for q in qdata.get("questions", [])}
            for t in q_types:
                if t not in topics:
                    err(f"'{t}' tipi questions.json'da var ama topics.json'da konu anlatımı yok")
        except (json.JSONDecodeError, KeyError):
            pass

    for type_name, topic in topics.items():
        if type_name not in ALL_VALID_TYPES:
            warn(f"topics.json'da bilinmeyen tip: '{type_name}'")

        missing = REQUIRED_TOPIC_FIELDS - set(topic.keys())
        if missing:
            err(f"'{type_name}' konusunda eksik alanlar: {missing}")
            continue

        if not topic["title"].strip():
            err(f"'{type_name}': title boş")
        if not topic["explanation"].strip():
            err(f"'{type_name}': explanation boş")
        if not topic["example"].strip():
            err(f"'{type_name}': example boş")
        if not isinstance(topic["tips"], list) or len(topic["tips"]) == 0:
            err(f"'{type_name}': tips boş veya liste değil")

    print(f"  📊 Konu sayısı: {len(topics)} tip tanımlı")


def main():
    global ACTIVE_PERIOD, DATA_DIR, QUESTIONS_FILE, TOPICS_FILE
    check_q = True
    check_t = True

    if "--questions" in sys.argv:
        check_t = False
    if "--topics" in sys.argv:
        check_q = False

    # --period argümanı
    for i, arg in enumerate(sys.argv):
        if arg == "--period" and i + 1 < len(sys.argv):
            period = sys.argv[i + 1]
            if period not in PERIOD_CONFIG:
                print(f"❌ Geçersiz dönem: {period}")
                print(f"   Geçerli dönemler: {', '.join(PERIOD_CONFIG.keys())}")
                sys.exit(1)
            ACTIVE_PERIOD = period

    # --data-dir argümanı (çakışmasız çocuk-bazlı üretim için)
    for i, arg in enumerate(sys.argv):
        if arg == "--data-dir" and i + 1 < len(sys.argv):
            DATA_DIR = Path(sys.argv[i + 1])
            QUESTIONS_FILE = DATA_DIR / "questions.json"
            TOPICS_FILE = DATA_DIR / "topics.json"

    print("🔍 MathLock Doğrulama Başlıyor...\n")

    if check_q:
        validate_questions()
    if check_t:
        validate_topics()

    print()

    if warnings:
        print("⚠️  Uyarılar:")
        for w in warnings:
            print(w)
        print()

    if errors:
        print(f"❌ {len(errors)} hata bulundu:")
        for e in errors:
            print(e)
        print(f"\n💥 Doğrulama BAŞARISIZ — {len(errors)} hata")
        sys.exit(1)
    else:
        print("✅ Doğrulama BAŞARILI — tüm kontroller geçti!")
        sys.exit(0)


if __name__ == "__main__":
    main()
