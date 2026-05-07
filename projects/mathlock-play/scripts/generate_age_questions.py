#!/usr/bin/env python3
"""
MathLock Play — Yaş gruplarına özgü 50'şer (veya az) soru üretici.

Çıktı: projects/mathlock-play/data/questions-<donem>.json
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

random.seed(42)  # Tekrar üretilebilirlik


def generate_addition(max_a: int, max_b: int) -> dict:
    a = random.randint(1, max_a)
    b = random.randint(1, max_b)
    return {
        "text": f"{a} + {b} = ?",
        "answer": a + b,
        "type": "toplama",
        "difficulty": 1 if max_a <= 10 else (2 if max_a <= 50 else 3),
    }


def generate_subtraction(min_a: int, max_a: int) -> dict:
    a = random.randint(min_a, max_a)
    b = random.randint(1, a - 1)
    return {
        "text": f"{a} - {b} = ?",
        "answer": a - b,
        "type": "çıkarma",
        "difficulty": 1 if max_a <= 10 else (2 if max_a <= 50 else 3),
    }


def generate_multiplication(max_a: int, max_b: int) -> dict:
    a = random.randint(2, max_a)
    b = random.randint(1, max_b)
    return {
        "text": f"{a} × {b} = ?",
        "answer": a * b,
        "type": "çarpma",
        "difficulty": 1 if max_a <= 3 else (2 if max_a <= 5 else 3),
    }


def generate_division(max_divisor: int, max_result: int) -> dict:
    b = random.randint(2, max_divisor)
    result = random.randint(1, max_result)
    a = b * result
    return {
        "text": f"{a} ÷ {b} = ?",
        "answer": result,
        "type": "bölme",
        "difficulty": 1 if max_divisor <= 2 else (2 if max_divisor <= 5 else 3),
    }


def generate_square(max_n: int) -> dict:
    a = random.randint(1, max_n)
    return {
        "text": f"{a}² = ?  ({a} × {a})",
        "answer": a * a,
        "type": "kare",
        "difficulty": 2 if max_n <= 10 else 3,
    }


# ─── Yaş gruplarına göre üretim stratejileri ────────────────────────────────

def generate_preschool(count: int = 30) -> list:
    """Okul öncesi: sadece toplama/çıkarma, 1-5 arası sayılar."""
    questions = []
    for _ in range(count):
        if random.random() < 0.5:
            q = generate_addition(5, 5)
        else:
            q = generate_subtraction(2, 5)
        questions.append(q)
    return questions


def generate_grade1(count: int = 40) -> list:
    """1. sınıf: toplama/çıkarma 1-10, %20 ihtimalle basit çarpma (1-3 tablosu)."""
    questions = []
    for _ in range(count):
        r = random.random()
        if r < 0.40:
            q = generate_addition(10, 10)
        elif r < 0.80:
            q = generate_subtraction(2, 10)
        else:
            q = generate_multiplication(3, 3)
        questions.append(q)
    return questions


def generate_grade2(count: int = 50) -> list:
    """2. sınıf: mevcut varsayılan seviye."""
    questions = []
    for _ in range(count):
        r = random.random()
        if r < 0.20:
            q = generate_addition(50, 50)
        elif r < 0.40:
            q = generate_subtraction(10, 99)
        elif r < 0.60:
            q = generate_multiplication(10, 10)
        elif r < 0.80:
            q = generate_division(10, 10)
        else:
            q = generate_square(12)
        questions.append(q)
    return questions


def generate_grade3(count: int = 50) -> list:
    """3. sınıf: biraz daha zor."""
    questions = []
    for _ in range(count):
        r = random.random()
        if r < 0.20:
            q = generate_addition(100, 100)
        elif r < 0.40:
            q = generate_subtraction(10, 200)
        elif r < 0.60:
            q = generate_multiplication(12, 12)
        elif r < 0.80:
            q = generate_division(12, 12)
        else:
            q = generate_square(15)
        questions.append(q)
    return questions


def generate_grade4(count: int = 50) -> list:
    """4. sınıf: en zor seviye."""
    questions = []
    for _ in range(count):
        r = random.random()
        if r < 0.20:
            q = generate_addition(500, 500)
        elif r < 0.40:
            q = generate_subtraction(50, 500)
        elif r < 0.60:
            q = generate_multiplication(15, 15)
        elif r < 0.80:
            q = generate_division(15, 15)
        else:
            q = generate_square(20)
        questions.append(q)
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
    "kare": [
        "Aynı sayıyı iki kere çarp",
        "Karesi demek kendisiyle çarpmak",
    ],
}


def add_hints(questions: list) -> list:
    """Her soruya yaş uygun hint ekle."""
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


def package(questions: list, period: str, version: int = 1) -> dict:
    avg_diff = round(sum(q.get("difficulty", 1) for q in questions) / len(questions), 1)
    overall = "beginner" if avg_diff < 1.5 else ("developing" if avg_diff < 2.5 else "intermediate")
    id_base = ID_RANGES.get(period, 0)

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
                "text": q["text"],
                "answer": q["answer"],
                "type": q["type"],
                "difficulty": q["difficulty"],
                "hint": q["hint"],
            }
            for i, q in enumerate(questions)
        ],
    }


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
        questions = add_hints(questions)
        data = package(questions, period)

        out_path = data_dir / f"questions-{period}.json"
        out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        types = {}
        for q in questions:
            types[q["type"]] = types.get(q["type"], 0) + 1
        print(f"✅ {period}: {count} soru → {out_path.name}")
        print(f"   Tipler: {types}")

    print(f"\n📁 Tüm dosyalar: {data_dir}/")


if __name__ == "__main__":
    main()
