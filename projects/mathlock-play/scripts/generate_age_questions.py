#!/usr/bin/env python3
"""
MathLock Play — Yaş gruplarına özgü soru üretici.

MEB müfredatına uygun, her eğitim dönemi için yalnızca o dönemde
öngörülen soru tiplerini üretir.

Çıktı: projects/mathlock-play/data/questions-<donem>.json
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

random.seed(42)  # Tekrar üretilebilirlik


# ─── Dönem bazlı işlem ağırlıkları (MEB müfredatına uygun) ───────────────────

OPERATION_WEIGHTS = {
    "okul_oncesi": {
        "sayma": 0.27,
        "toplama": 0.27,
        "çıkarma": 0.13,
        "karşılaştırma": 0.20,
        "örüntü": 0.13,
    },
    "sinif_1": {
        "toplama": 0.45,
        "çıkarma": 0.35,
        "sıralama": 0.13,
        "eksik_sayı": 0.07,
    },
    "sinif_2": {
        "toplama": 0.44,
        "çıkarma": 0.32,
        "çarpma": 0.10,
        "bölme": 0.08,
        "sıralama": 0.04,
        "eksik_sayı": 0.02,
    },
    "sinif_3": {
        "toplama": 0.24,
        "çıkarma": 0.20,
        "çarpma": 0.20,
        "bölme": 0.14,
        "sıralama": 0.06,
        "eksik_sayı": 0.04,
        "kesir": 0.06,
        "problem": 0.06,
    },
    "sinif_4": {
        "toplama": 0.16,
        "çıkarma": 0.16,
        "çarpma": 0.18,
        "bölme": 0.18,
        "sıralama": 0.06,
        "eksik_sayı": 0.04,
        "kesir": 0.12,
        "problem": 0.10,
    },
}


# ─── Zorluk hesaplama (1–5 skalası) ─────────────────────────────────────────

def _calc_difficulty_addition(max_a: int) -> int:
    if max_a <= 10: return 1
    if max_a <= 50: return 2
    if max_a <= 200: return 3
    if max_a <= 500: return 4
    return 5


def _calc_difficulty_multiplication(max_a: int) -> int:
    if max_a <= 3: return 1
    if max_a <= 5: return 2
    if max_a <= 10: return 3
    if max_a <= 20: return 4
    return 5


def _calc_difficulty_division(max_divisor: int) -> int:
    if max_divisor <= 2: return 1
    if max_divisor <= 5: return 2
    if max_divisor <= 9: return 3
    if max_divisor <= 20: return 4
    return 5


def _calc_difficulty_sorting(count: int, max_val: int) -> int:
    if count <= 2 and max_val <= 20: return 1
    if count <= 3 and max_val <= 100: return 2
    if count <= 4 and max_val <= 500: return 3
    if count <= 5 and max_val <= 5000: return 4
    return 5


def _calc_difficulty_fraction(denominator: int, unit_fraction: bool = True) -> int:
    base = 1
    if denominator > 3: base = 2
    if denominator > 5: base = 3
    if denominator > 8: base = 4
    if denominator > 10: base = 5
    # Non-üniter kesirler (pay > 1) ek bilişsel adım içerir
    if not unit_fraction:
        base = min(5, base + 1)
    return base


def _calc_difficulty_missing_number(max_a: int, max_result: int) -> int:
    if max_a <= 5 and max_result <= 10: return 1
    if max_a <= 15 and max_result <= 50: return 2
    if max_a <= 30 and max_result <= 100: return 3
    if max_a <= 50 and max_result <= 500: return 4
    return 5


# ─── Temel üreticiler ───────────────────────────────────────────────────────

def generate_addition(max_a: int, max_b: int, result_max: int = None, *, min_a: int = 1, min_b: int = 1) -> dict:
    if result_max is not None and min_a + min_b > result_max:
        raise ValueError(f"min_a({min_a}) + min_b({min_b}) = {min_a + min_b} > result_max({result_max})")
    a = random.randint(min_a, max_a)
    b = random.randint(min_b, max_b)
    if result_max and a + b > result_max:
        return generate_addition(max_a, max_b, result_max, min_a=min_a, min_b=min_b)
    return {
        "text": f"{a} + {b} = ?",
        "answer": a + b,
        "type": "toplama",
        "difficulty": _calc_difficulty_addition(max_a),
    }


def generate_subtraction(min_a: int, max_a: int, no_borrow: bool = False) -> dict:
    a = random.randint(min_a, max_a)
    if no_borrow and a >= 10:
        max_b = a % 10
        if max_b >= 1:
            b = random.randint(1, max_b)
        else:
            b = random.randint(1, a - 1)
    else:
        b = random.randint(1, a - 1)
    return {
        "text": f"{a} - {b} = ?",
        "answer": a - b,
        "type": "çıkarma",
        "difficulty": _calc_difficulty_addition(max_a),
    }


def generate_multiplication(max_a: int, max_b: int, result_max: int = None, *, min_a: int = 2, min_b: int = 1) -> dict:
    if result_max is not None and min_a * min_b > result_max:
        raise ValueError(f"min_a({min_a}) × min_b({min_b}) = {min_a * min_b} > result_max({result_max})")
    a = random.randint(min_a, max_a)
    b = random.randint(min_b, max_b)
    if result_max and a * b > result_max:
        return generate_multiplication(max_a, max_b, result_max, min_a=min_a, min_b=min_b)
    return {
        "text": f"{a} × {b} = ?",
        "answer": a * b,
        "type": "çarpma",
        "difficulty": _calc_difficulty_multiplication(max_a),
    }


def generate_division(max_divisor: int, max_result: int, *, min_divisor: int = 2, min_result: int = 1) -> dict:
    b = random.randint(min_divisor, max_divisor)
    result = random.randint(min_result, max_result)
    a = b * result
    return {
        "text": f"{a} ÷ {b} = ?",
        "answer": result,
        "type": "bölme",
        "difficulty": _calc_difficulty_division(max_divisor),
    }


def generate_counting(max_items: int = 5) -> dict:
    items = ["🍎", "⭐", "🐱", "🚗", "🌸", "🍌", "🦋"]
    labels = ["elma", "yıldız", "kedi", "araba", "çiçek", "muz", "kelebek"]
    idx = random.randint(0, len(items) - 1)
    item, label = items[idx], labels[idx]
    count = random.randint(1, max_items)
    emojis = item * count
    return {
        "text": f"Kaç tane {label} var: {emojis} = ?",
        "answer": count,
        "type": "sayma",
        "difficulty": 1 if count <= 5 else 2,
    }


def generate_pattern() -> dict:
    templates = [
        ("1, 2, 1, 2, ?", 1),
        ("1, 2, 2, 1, 2, 2, ?", 1),
        ("1, 2, 3, 1, 2, 3, ?", 1),
        ("2, 4, 6, ?", 8),
        ("1, 3, 5, ?", 7),
        ("2, 3, 2, 3, ?", 2),
        ("5, 4, 3, ?", 2),
    ]
    text, answer = random.choice(templates)
    return {
        "text": f"{text} = ?",
        "answer": answer,
        "type": "örüntü",
        "difficulty": 1,
    }


def generate_comparison(max_val: int = 10, mode: str = "biggest") -> dict:
    a = random.randint(1, max_val)
    b = random.randint(1, max_val)
    while b == a:
        b = random.randint(1, max_val)

    if mode == "biggest":
        text = f"Hangisi büyük: {a}, {b} = ?"
        answer = max(a, b)
    else:
        text = f"Hangisi küçük: {a}, {b} = ?"
        answer = min(a, b)
    return {
        "text": text,
        "answer": answer,
        "type": "karşılaştırma",
        "difficulty": 1 if max_val <= 10 else 2,
    }


def generate_sorting(max_val: int, count: int = 2, mode: str = "biggest") -> dict:
    numbers = []
    while len(numbers) < count:
        n = random.randint(1, max_val)
        if n not in numbers:
            numbers.append(n)
    nums_str = ", ".join(str(n) for n in numbers)
    if mode == "biggest":
        text = f"En büyüğü hangisi: {nums_str} = ?"
        answer = max(numbers)
    else:
        text = f"En küçüğü hangisi: {nums_str} = ?"
        answer = min(numbers)
    return {
        "text": text,
        "answer": answer,
        "type": "sıralama",
        "difficulty": _calc_difficulty_sorting(count, max_val),
    }


def generate_missing_number(max_a: int, max_result: int) -> dict:
    fmt = random.choice(["add", "sub"])
    if fmt == "add":
        a = random.randint(1, max_a)
        b = random.randint(a + 1, max_result)
        return {
            "text": f"? + {a} = {b}",
            "answer": b - a,
            "type": "eksik_sayı",
            "difficulty": _calc_difficulty_missing_number(max_a, max_result),
        }
    else:
        a = random.randint(2, max_result)
        b = random.randint(1, a - 1)
        return {
            "text": f"? - {a} = {b}",
            "answer": a + b,
            "type": "eksik_sayı",
            "difficulty": _calc_difficulty_missing_number(max_a, max_result),
        }


def generate_fraction(unit_fraction: bool = True, *, max_denominator: int = 10) -> dict:
    denominators = [2, 3, 4, 5, 6, 8, 10]
    valid_dens = [d for d in denominators if d <= max_denominator]
    if not valid_dens:
        raise ValueError(f"No valid denominator <= {max_denominator}")
    if unit_fraction:
        den = random.choice(valid_dens[:5] if len(valid_dens) >= 5 else valid_dens)
    else:
        valid_non_unit = [d for d in valid_dens if d >= 3]
        if not valid_non_unit:
            raise ValueError("No valid denominator >= 3 for non-unit fraction")
        den = random.choice(valid_non_unit)
    num = 1 if unit_fraction else random.randint(2, den - 1)
    multiplier = random.randint(2, 20)
    a = den * multiplier
    answer = num * multiplier

    if num == 1:
        fraction_names = {
            2: "yarısı", 3: "üçte biri", 4: "çeyreği",
            5: "beşte biri", 6: "altıda biri", 8: "sekizde biri", 10: "onda biri",
        }
        name = fraction_names.get(den, f"{den}'de biri")
    else:
        name = f"{num}/{den}'i"

    return {
        "text": f"{a}'nin {name} kaçtır = ?",
        "answer": answer,
        "type": "kesir",
        "difficulty": _calc_difficulty_fraction(den, unit_fraction),
    }


def generate_problem(difficulty: int = 1) -> dict:
    templates_l1 = [
        ("Ali'nin {a} TL'si var. {b} TL harcadı. Kaç TL kaldı = ?", lambda a, b: a - b),
        ("Ayşe'nin {a} bilyesi var. {b} tane daha aldı. Kaç bilyesi oldu = ?", lambda a, b: a + b),
        ("Sınıfta {a} öğrenci var. {b} tanesi erkek. Kaç tanesi kız = ?", lambda a, b: a - b),
    ]
    templates_l2 = [
        ("{a} kutudan her birinde {b} kalem var. Toplam kaç kalem var = ?", lambda a, b: a * b),
        ("{a} elma {b} çocuğa eşit paylaştırıldı. Her çocuğa kaç elma düştü = ?", lambda a, b: a // b),
    ]
    templates_l3 = [
        ("Ali'nin {a} TL'si var. {b} TL harcadı, {c} TL daha aldı. Kaç TL'si var = ?", lambda a, b, c: a - b + c),
        ("{a} paket aldı, her biri {b} TL. {c} TL verdi. Para üstü kaç = ?", lambda a, b, c: c - a * b),
    ]

    if difficulty == 1:
        tmpl, op = random.choice(templates_l1)
        a = random.randint(10, 50)
        b = random.randint(5, a - 1)
        text = tmpl.format(a=a, b=b)
        answer = op(a, b)
    elif difficulty == 2:
        tmpl, op = random.choice(templates_l2)
        a = random.randint(3, 12)
        b = random.randint(2, 10)
        if "elma" in tmpl:
            a = a * b
        text = tmpl.format(a=a, b=b)
        answer = op(a, b)
    else:
        tmpl, op = random.choice(templates_l3)
        if "Para üstü" in tmpl:
            a = random.randint(2, 10)
            b = random.randint(5, 20)
            c = a * b + random.randint(5, 50)  # verilen para > toplam tutar
        else:
            a = random.randint(20, 80)
            b = random.randint(5, a // 2)
            c = random.randint(10, 50)
        text = tmpl.format(a=a, b=b, c=c)
        answer = op(a, b, c)
        if answer < 0:
            # Fallback: basit toplama problemi
            text = f"Ayşe'nin {a} bilyesi var. {b} tane daha aldı. Kaç bilyesi oldu = ?"
            answer = a + b

    return {
        "text": text,
        "answer": answer,
        "type": "problem",
        "difficulty": difficulty,
    }


# ─── Dönem bazlı üretim stratejileri ────────────────────────────────────────

def generate_preschool(count: int = 30) -> list:
    """Okul öncesi: sayma, toplama, çıkarma, karşılaştırma, örüntü."""
    gen_map = {
        "sayma": lambda: generate_counting(random.choice([5, 10])),
        "toplama": lambda: generate_addition(5, 5, result_max=10),
        "çıkarma": lambda: generate_subtraction(2, 5),
        "karşılaştırma": lambda: generate_comparison(random.choice([5, 10]), "biggest"),
        "örüntü": lambda: generate_pattern(),
    }
    cfg = OPERATION_WEIGHTS["okul_oncesi"]
    names = list(cfg.keys())
    weights = [cfg[n] for n in names]
    generators = [gen_map[n] for n in names]
    chosen = random.choices(generators, weights=weights, k=count)
    questions = [g() for g in chosen]
    return questions


def generate_grade1(count: int = 40) -> list:
    """1. sınıf: toplama, çıkarma, sıralama, eksik_sayı.
    Çarpma YOK (MEB 1. sınıf müfredatında çarpma yoktur).
    Çıkarmada onluktan bozma YASAK.
    """
    gen_map = {
        "toplama": lambda: generate_addition(10, 10, result_max=20),
        "çıkarma": lambda: generate_subtraction(2, 10, no_borrow=True),
        "sıralama": lambda: generate_sorting(20, count=2, mode="biggest"),
        "eksik_sayı": lambda: generate_missing_number(5, 10),
    }
    cfg = OPERATION_WEIGHTS["sinif_1"]
    names = list(cfg.keys())
    weights = [cfg[n] for n in names]
    generators = [gen_map[n] for n in names]
    chosen = random.choices(generators, weights=weights, k=count)
    questions = [g() for g in chosen]
    return questions


def generate_grade2(count: int = 50) -> list:
    """2. sınıf: toplama, çıkarma, çarpma, bölme, sıralama, eksik_sayı.
    Kare YOK (MEB 2. sınıf müfredatında kare sayılar yoktur).
    Çarpma tablosu 9×9 sınırı (MEB MAT.2.1.4).
    """
    gen_map = {
        "toplama": lambda: generate_addition(50, 50, min_a=1, min_b=1),
        "çıkarma": lambda: generate_subtraction(10, 99),
        "çarpma": lambda: generate_multiplication(9, 9, result_max=81, min_a=2, min_b=2),
        "bölme": lambda: generate_division(9, 9, min_divisor=2, min_result=1),
        "sıralama": lambda: generate_sorting(100, count=3, mode="smallest"),
        "eksik_sayı": lambda: generate_missing_number(15, 50),
    }
    cfg = OPERATION_WEIGHTS["sinif_2"]
    names = list(cfg.keys())
    weights = [cfg[n] for n in names]
    generators = [gen_map[n] for n in names]
    chosen = random.choices(generators, weights=weights, k=count)
    questions = [g() for g in chosen]
    return questions


def generate_grade3(count: int = 50) -> list:
    """3. sınıf: 4 işlem + sıralama + eksik_sayı + kesir + problem.
    Kare YOK — MEB 3. sınıf kazanımlarında kare sayılar yoktur.
    Kesir SADECE üniter (pay = 1).
    """
    gen_map = {
        "toplama": lambda: generate_addition(200, 100),
        "çıkarma": lambda: generate_subtraction(10, 200),
        "çarpma": lambda: generate_multiplication(20, 9, result_max=900, min_a=2, min_b=2),
        "bölme": lambda: generate_division(9, 20),
        "sıralama": lambda: generate_sorting(500, count=4, mode="smallest"),
        "eksik_sayı": lambda: generate_missing_number(30, 100),
        "kesir": lambda: generate_fraction(unit_fraction=True),
        "problem": lambda: generate_problem(difficulty=random.randint(1, 3)),
    }
    cfg = OPERATION_WEIGHTS["sinif_3"]
    names = list(cfg.keys())
    weights = [cfg[n] for n in names]
    generators = [gen_map[n] for n in names]
    chosen = random.choices(generators, weights=weights, k=count)
    questions = [g() for g in chosen]
    return questions


def generate_grade4(count: int = 50) -> list:
    """4. sınıf: 4 işlem + sıralama + eksik_sayı + kesir + problem.
    Kare YOK — MEB 4. sınıf kazanımlarında kare sayılar yoktur.
    Kesir non-üniter (pay > 1).
    """
    gen_map = {
        "toplama": lambda: generate_addition(500, 500),
        "çıkarma": lambda: generate_subtraction(50, 500),
        "çarpma": lambda: generate_multiplication(100, 50, result_max=10000),
        "bölme": lambda: generate_division(50, 100),
        "sıralama": lambda: generate_sorting(10000, count=5, mode="biggest"),
        "eksik_sayı": lambda: generate_missing_number(100, 1000),
        "kesir": lambda: generate_fraction(unit_fraction=False),
        "problem": lambda: generate_problem(difficulty=random.randint(2, 5)),
    }
    cfg = OPERATION_WEIGHTS["sinif_4"]
    names = list(cfg.keys())
    weights = [cfg[n] for n in names]
    generators = [gen_map[n] for n in names]
    chosen = random.choices(generators, weights=weights, k=count)
    questions = [g() for g in chosen]
    return questions


# ─── Hint ekleme ─────────────────────────────────────────────────────────────

HINTS = {
    "toplama": [
        "Büyük sayıdan başla, küçük sayıyı parmakla say",
        "Önce onlukları topla, sonra birlikleri ekle",
        "Sayıları kafanda sırala, topla",
    ],
    "çıkarma": [
        "Büyük sayıdan geriye doğru say",
        "Onluklardan onlukları, birliklerden birlikleri çıkar",
        "Sayı doğrusunda geriye git",
    ],
    "çarpma": [
        "Toplama ile düşün: 3 × 2 = 3 + 3",
        "Çarpım tablosunu hatırla",
        "10 ile çarpınca sona 0 eklenir",
    ],
    "bölme": [
        "Eşit parçalara bölersen her tarafa kaç düşer?",
        "Hangi sayı ile çarpınca bu sonucu bulursun?",
        "Çarpma tablosunu tersten düşün",
    ],
    "sayma": [
        "Parmaklarınla tek tek say",
        "Bir bir göster ve say",
        "Yavaş yavaş, hiç atlamadan say",
    ],
    "karşılaştırma": [
        "Hangi sayı daha çok?",
        "Parmaklarınla karşılaştır",
        "Büyük olan sayıyı bul",
    ],
    "örüntü": [
        "Tekrar eden parçayı bul",
        "Sıra neyle devam ediyor?",
        "İlk iki sayıya bak, tekrar ediyor mu?",
    ],
    "sıralama": [
        "Sayıları kafanda sırala, en küçüğünü bul",
        "Hangi sayı daha çok?",
        "En büyük sayıyı seç",
    ],
    "eksik_sayı": [
        "Sonuçtan bilinen sayıyı çıkar",
        "Bilinmeyen yerde ne olmalı?",
        "Ters işlem yap",
    ],
    "kesir": [
        "Sayıyı paydaya böl, sonucu pay ile çarp",
        "Bütünü parçalara böl, kaç parça alındı?",
        "Önce paydaya böl, sonra pay kadar çarp",
    ],
    "problem": [
        "Problemi adım adım çöz, ilk işlemi yap",
        "Ne verilmiş, ne isteniyor bul",
        "Sayıları işleme yerleştir",
    ],
}


def add_hints(questions: list) -> list:
    """Her soruya türüne uygun hint ekle."""
    for q in questions:
        t = q["type"]
        q["hint"] = random.choice(HINTS.get(t, ["Dikkatlice düşün"]))
    return questions


# ─── JSON paketleme ──────────────────────────────────────────────────────────

# Her yaş grubu için farklı id aralığı (DB unique constraint çakışmasını önler)
ID_RANGES = {
    "okul_oncesi": 1000,
    "sinif_1": 2000,
    "sinif_2": 3000,
    "sinif_3": 4000,
    "sinif_4": 5000,
}

INTERACTION_MODES = {
    "sayma": "tap-to-count",
    "örüntü": "pattern-select",
    "karşılaştırma": "tap-to-choose",
    "sıralama": "tap-to-choose",
}


def structured_id(year: int, grade: int, batch: int, seq: int) -> str:
    return f"{year}G{grade}-B{batch}-{seq:04d}"


def package(questions: list, period: str, version: int = 1, use_offset: bool = True, year: int = 2025, batch: int = 1) -> dict:
    avg_diff = round(sum(q.get("difficulty", 1) for q in questions) / len(questions), 1)
    if avg_diff < 1.5:
        overall = "beginner"
    elif avg_diff < 2.5:
        overall = "developing"
    elif avg_diff < 3.5:
        overall = "intermediate"
    else:
        overall = "advanced"
    id_base = ID_RANGES.get(period, 0) if use_offset else 0
    grade_num = int(period.replace("sinif_", "").replace("okul_oncesi", "0"))

    return {
        "version": version,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "generatedBy": "mathlock-generator",
        "educationPeriod": period,
        "difficultyProfile": {
            "overall": overall,
            "avgDifficulty": avg_diff,
            "adjustmentReason": f"Yaş uygun ilk set — {period}",
        },
        "questions": [
            {
                "id": id_base + i + 1,
                "code": structured_id(year, grade_num, batch, id_base + i + 1),
                "text": q["text"],
                "answer": q["answer"],
                "type": q["type"],
                "difficulty": q["difficulty"],
                "hint": q["hint"],
                "interactionMode": INTERACTION_MODES.get(q["type"], "text-input"),
            }
            for i, q in enumerate(questions)
        ],
    }


# ─── Yardımcılar ─────────────────────────────────────────────────────────────

def _deduplicate(questions: list, count: int) -> list:
    """Tekrar eden soru metinlerini kaldır, eksik kalanları yeniden üret."""
    seen = set()
    unique = []
    for q in questions:
        if q["text"] not in seen:
            seen.add(q["text"])
            unique.append(q)
    return unique[:count]


# ─── Ana akış ────────────────────────────────────────────────────────────────

def main():
    project_dir = Path(__file__).resolve().parents[1]
    data_dir = project_dir / "data"
    data_dir.mkdir(exist_ok=True)

    configs = [
        ("okul_oncesi", generate_preschool, 30),
        ("sinif_1", generate_grade1, 40),
        ("sinif_2", generate_grade2, 50),
        ("sinif_3", generate_grade3, 50),
        ("sinif_4", generate_grade4, 50),
    ]

    for period, generator, count in configs:
        questions = generator(count)
        questions = _deduplicate(questions, count)
        # Eksik kaldıysa yeniden üret (nadiren)
        attempts = 0
        while len(questions) < count and attempts < 100:
            extra = generator(count - len(questions))
            for q in extra:
                if q["text"] not in {x["text"] for x in questions}:
                    questions.append(q)
                if len(questions) >= count:
                    break
            attempts += 1
        questions = add_hints(questions)
        data = package(questions, period, use_offset=True)

        out_path = data_dir / f"questions-{period}.json"
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        types = {}
        for q in questions:
            types[q["type"]] = types.get(q["type"], 0) + 1
        print(f"✅ {period}: {len(questions)} soru → {out_path.name}")
        print(f"   Tipler: {types}")

    # Varsayılan active questions.json (sinif_2, ID offset yok — validate-questions.py uyumu)
    default_period, default_gen, default_count = configs[2]  # sinif_2
    default_questions = default_gen(default_count)
    default_questions = _deduplicate(default_questions, default_count)
    while len(default_questions) < default_count:
        extra = default_gen(default_count - len(default_questions))
        for q in extra:
            if q["text"] not in {x["text"] for x in default_questions}:
                default_questions.append(q)
            if len(default_questions) >= default_count:
                break
    default_questions = add_hints(default_questions)
    default_data = package(default_questions, default_period, use_offset=False)
    (data_dir / "questions.json").write_text(
        json.dumps(default_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"✅ default: {len(default_questions)} soru → questions.json (sinif_2, ID 1-{len(default_questions)})")

    print(f"\n📁 Tüm dosyalar: {data_dir}/")


if __name__ == "__main__":
    main()
