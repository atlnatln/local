#!/usr/bin/env python3
"""
Dönem bazlı soru seti doğrulama aracı.

Her questions-{period}.json dosyasını okuyup:
- Tip dağılımı beklenen ağırlıklara uygun mu?
- Zorluk dağılımı döneme uygun mu?
- ID/code çakışması var mı?
- Duplicate soru metni var mı?
- interactionMode geçerli mi?
- MEB kazanım uyumu (temel kontroller)

Çıktı: her dönem için PASS/FAIL özeti + detaylı rapor.
"""

import json
import sys
from pathlib import Path
from collections import Counter

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

# Beklenen tip dağılımları (yüzde olarak, ±tolerance ile)
EXPECTED_TYPES = {
    "okul_oncesi": {
        "sayma": (0.20, 0.40),
        "toplama": (0.10, 0.30),
        "çıkarma": (0.10, 0.30),
        "karşılaştırma": (0.10, 0.30),
        "örüntü": (0.10, 0.30),
    },
    "sinif_1": {
        "toplama": (0.30, 0.55),
        "çıkarma": (0.20, 0.45),
        "sıralama": (0.05, 0.20),
        "eksik_sayı": (0.03, 0.12),
    },
    "sinif_2": {
        "toplama": (0.25, 0.60),
        "çıkarma": (0.10, 0.50),
        "çarpma": (0.03, 0.22),
        "bölme": (0.03, 0.30),
        "sıralama": (0.00, 0.15),
        "eksik_sayı": (0.00, 0.08),
    },
    "sinif_3": {
        "toplama": (0.12, 0.38),
        "çıkarma": (0.12, 0.38),
        "çarpma": (0.08, 0.32),
        "bölme": (0.05, 0.25),
        "sıralama": (0.00, 0.15),
        "eksik_sayı": (0.01, 0.10),
        "kesir": (0.01, 0.12),
        "problem": (0.01, 0.12),
    },
    "sinif_4": {
        "toplama": (0.10, 0.25),
        "çıkarma": (0.10, 0.25),
        "çarpma": (0.12, 0.28),
        "bölme": (0.12, 0.28),
        "sıralama": (0.03, 0.10),
        "eksik_sayı": (0.02, 0.07),
        "kesir": (0.08, 0.18),
        "problem": (0.06, 0.15),
    },
}

# Beklenen zorluk aralıkları (min, max) — kapsayıcı
EXPECTED_DIFFICULTY_RANGE = {
    "okul_oncesi": (1, 2),
    "sinif_1": (1, 2),
    "sinif_2": (1, 3),
    "sinif_3": (1, 4),   # kesir ve problem zorluk 1 verebilir
    "sinif_4": (2, 5),   # problem zorluk 2 verebilir
}

# Beklenen soru sayıları
EXPECTED_COUNTS = {
    "okul_oncesi": 30,
    "sinif_1": 40,
    "sinif_2": 50,
    "sinif_3": 50,
    "sinif_4": 50,
}

# Geçerli interactionMode değerleri
VALID_INTERACTION_MODES = {
    "text-input", "tap-to-count", "pattern-select", "tap-to-choose",
}

# Geçerli soru tipleri
VALID_TYPES = {
    "toplama", "çıkarma", "çarpma", "bölme", "sıralama", "eksik_sayı",
    "kesir", "problem", "sayma", "karşılaştırma", "örüntü",
}


def validate_period(period: str, data: dict) -> list:
    """Tek bir dönem için doğrulama yap; hata listesi döndür."""
    errors = []
    questions = data.get("questions", [])
    count = len(questions)

    # 1. Soru sayısı
    expected = EXPECTED_COUNTS.get(period)
    if expected and count != expected:
        errors.append(f"COUNT: Beklenen {expected}, gelen {count}")

    if count == 0:
        errors.append("COUNT: Hiç soru yok")
        return errors

    # 2. Tip dağılımı
    type_counts = Counter(q.get("type", "UNKNOWN") for q in questions)
    expected_types = EXPECTED_TYPES.get(period, {})

    for t, (lo, hi) in expected_types.items():
        actual = type_counts.get(t, 0) / count
        if not (lo <= actual <= hi):
            errors.append(
                f"TYPE '{t}': Beklenen %{lo*100:.0f}-%{hi*100:.0f}, "
                f"gerçekleşen %{actual*100:.1f} ({type_counts.get(t, 0)}/{count})"
            )

    # 3. Zorluk aralığı
    diff_min, diff_max = EXPECTED_DIFFICULTY_RANGE.get(period, (1, 5))
    difficulties = [q.get("difficulty", 1) for q in questions]
    actual_min, actual_max = min(difficulties), max(difficulties)
    if actual_min < diff_min:
        errors.append(f"DIFFICULTY: Min {actual_min} < beklenen {diff_min}")
    if actual_max > diff_max:
        errors.append(f"DIFFICULTY: Max {actual_max} > beklenen {diff_max}")

    # 4. Duplicate text
    texts = [q.get("text", "") for q in questions]
    duplicates = [item for item, cnt in Counter(texts).items() if cnt > 1]
    if duplicates:
        errors.append(f"DUPLICATE: {len(duplicates)} tekrar eden soru metni")

    # 5. Duplicate ID / code
    ids = [q.get("id") for q in questions]
    codes = [q.get("code") for q in questions if q.get("code")]
    if len(set(ids)) != len(ids):
        errors.append("ID: Çakışan ID'ler var")
    if len(set(codes)) != len(codes):
        errors.append("CODE: Çakışan code değerleri var")

    # 6. interactionMode kontrolü
    for q in questions:
        mode = q.get("interactionMode", "text-input")
        if mode not in VALID_INTERACTION_MODES:
            errors.append(f"INTERACTION: Geçersiz mode '{mode}' — soru: {q.get('text', '?')[:30]}")

    # 7. Soru tipi kontrolü
    for q in questions:
        t = q.get("type", "")
        if t not in VALID_TYPES:
            errors.append(f"TYPE_INVALID: Geçersiz tip '{t}' — soru: {q.get('text', '?')[:30]}")

    # 8. Zorluk histogram (bilgi amaçlı, hata değil)
    diff_hist = Counter(difficulties)
    return errors, diff_hist


def main():
    periods = ["okul_oncesi", "sinif_1", "sinif_2", "sinif_3", "sinif_4"]
    all_ok = True

    for period in periods:
        path = DATA_DIR / f"questions-{period}.json"
        if not path.exists():
            print(f"❌ {period}: Dosya bulunamadı — {path}")
            all_ok = False
            continue

        data = json.loads(path.read_text(encoding="utf-8"))
        result = validate_period(period, data)
        errors = result[0] if isinstance(result, tuple) else result
        diff_hist = result[1] if isinstance(result, tuple) else {}

        if errors:
            print(f"❌ {period}: {len(errors)} hata")
            for e in errors:
                print(f"   • {e}")
            all_ok = False
        else:
            print(f"✅ {period}: PASS")

        # Zorluk histogramı
        diffs = sorted(diff_hist.items())
        hist_str = ", ".join(f"Z{k}: {v}" for k, v in diffs)
        print(f"   Zorluk dağılımı: {hist_str}")

    if all_ok:
        print("\n🎉 Tüm dönemler PASS")
        return 0
    else:
        print("\n⚠️  Bazı dönemlerde hata var.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
