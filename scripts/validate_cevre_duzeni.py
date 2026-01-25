#!/usr/bin/env python3
"""
Çevre Düzeni Planları Metin Doğrulama Scripti
- JSON verisi (cevre-duzeni-planlari.json) ile plan metin dosyaları arasında tutarlılık kontrolü
- Kaynaklar: archive/_legacy_root_20260117/100binlik/*.txt dosyaları
"""

import os
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Dizinler
REPO_ROOT = Path(__file__).parent.parent
JSON_FILE = REPO_ROOT / "projects/webimar/webimar-nextjs/data/cevre-duzeni-planlari.json"
PLAN_FILES_DIR = REPO_ROOT / "projects/webimar/webimar-nextjs/data/100binlik"
ARCHIVE_SOURCE_DIR = REPO_ROOT / "projects/webimar/archive/_legacy_root_20260117/100binlik"

def normalize_text(text: str) -> str:
    """Başlık normalizasyonu: büyük harf, özel karakterler temizleme"""
    return text.upper().strip()

def read_text_file(path: Path) -> str:
    """Dosyayı oku, ilk 500 karakteri getir"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read(500)
    except Exception as e:
        return f"[HATA: {e}]"

def extract_title_from_file(path: Path) -> str:
    """Dosya içeriğinden başlık çıkart (ilk satır)"""
    content = read_text_file(path)
    first_line = content.split('\n')[0] if content else ""
    return first_line.strip()

def check_file_existence() -> Tuple[int, List[str]]:
    """JSON'daki tüm dosyaların fiziksel olarak var olduğunu kontrol et"""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing = []
    for plan in data['planlar']:
        file_path = PLAN_FILES_DIR / plan['dosya']
        if not file_path.exists():
            missing.append(f"  ✗ {plan['id']}: {plan['dosya']} (YOK)")
    
    return len(missing), missing

def check_title_match() -> Tuple[int, List[str]]:
    """JSON başlıklarını dosyadaki ilk satırlarla karşılaştır"""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mismatches = []
    for plan in data['planlar']:
        file_path = PLAN_FILES_DIR / plan['dosya']
        if file_path.exists():
            file_title = extract_title_from_file(file_path)
            json_title = plan['baslik']
            
            # Normalize et ve karşılaştır (basit uyum kontrolü)
            file_normalized = normalize_text(file_title)
            json_normalized = normalize_text(json_title)
            
            if not (json_normalized in file_normalized or 
                    file_normalized in json_normalized or
                    file_normalized.startswith(json_normalized[:20])):
                mismatches.append(
                    f"  ⚠ {plan['id']}:\n"
                    f"    JSON:  {json_title[:60]}\n"
                    f"    Dosya: {file_title[:60]}"
                )
    
    return len(mismatches), mismatches

def check_il_presence() -> Tuple[int, List[str]]:
    """İl adlarının dosya içeriğinde geçip geçmediğini kontrol et"""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    missing_ils = []
    for plan in data['planlar']:
        file_path = PLAN_FILES_DIR / plan['dosya']
        if file_path.exists():
            content = read_text_file(file_path).upper()
            
            for il in plan['iller']:
                if il.upper() not in content:
                    missing_ils.append(
                        f"  ⚠ {plan['id']}: '{il}' dosya başlığında bulunamadı"
                    )
    
    return len(missing_ils), missing_ils

def check_archive_consistency() -> Tuple[int, List[str]]:
    """Archive kaynağında aynı dosyaların olup olmadığını doğrula"""
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    inconsistent = []
    for plan in data['planlar']:
        archive_path = ARCHIVE_SOURCE_DIR / plan['dosya']
        plan_path = PLAN_FILES_DIR / plan['dosya']
        
        if not archive_path.exists():
            inconsistent.append(
                f"  ✗ {plan['id']}: Archive'de kaynak dosya yok: {plan['dosya']}"
            )
        elif plan_path.exists():
            # İçeriğin başlarını karşılaştır
            archive_start = read_text_file(archive_path)[:100]
            plan_start = read_text_file(plan_path)[:100]
            if archive_start != plan_start:
                inconsistent.append(
                    f"  ⚠ {plan['id']}: Archive ve plan dosya içeriği farklı"
                )
    
    return len(inconsistent), inconsistent

def main():
    print("=" * 70)
    print("ÇEVRE DÜZENİ PLANLARI - METIN DOĞRULAMA RAPORU")
    print("=" * 70)
    
    if not JSON_FILE.exists():
        print(f"HATA: {JSON_FILE} bulunamadı")
        sys.exit(1)
    
    all_issues = []
    total_issues = 0
    
    # Test 1: Dosya varlığı
    print("\n1️⃣  DOSYA VARLIK KONTROLÜ")
    print("-" * 70)
    count, issues = check_file_existence()
    total_issues += count
    if count == 0:
        print("  ✓ Tüm dosyalar mevcut")
    else:
        print(f"  ✗ {count} dosya eksik:")
        for issue in issues:
            print(issue)
    
    # Test 2: Başlık eşleşmesi
    print("\n2️⃣  BAŞLIK EŞLEŞMESİ (JSON vs Dosya)")
    print("-" * 70)
    count, issues = check_title_match()
    total_issues += count
    if count == 0:
        print("  ✓ Tüm başlıklar eşleşiyor")
    else:
        print(f"  ⚠ {count} uyumsuzluk:")
        for issue in issues[:5]:  # İlk 5'i göster
            print(issue)
        if len(issues) > 5:
            print(f"  ... ve {len(issues) - 5} daha")
    
    # Test 3: İl varlığı
    print("\n3️⃣  İL ADIN VARLIK KONTROLÜ")
    print("-" * 70)
    count, issues = check_il_presence()
    total_issues += count
    if count == 0:
        print("  ✓ Tüm il adları dosyalarda geçiyor")
    else:
        print(f"  ⚠ {count} il adı uyumsuzluğu:")
        for issue in issues[:5]:
            print(issue)
        if len(issues) > 5:
            print(f"  ... ve {len(issues) - 5} daha")
    
    # Test 4: Archive tutarlılığı
    print("\n4️⃣  ARCHIVE TUTARLILIK KONTROLÜ")
    print("-" * 70)
    count, issues = check_archive_consistency()
    total_issues += count
    if count == 0:
        print("  ✓ Archive kaynaklar ile uyumlu")
    else:
        print(f"  ⚠ {count} tutarsızlık:")
        for issue in issues[:5]:
            print(issue)
        if len(issues) > 5:
            print(f"  ... ve {len(issues) - 5} daha")
    
    # Özet
    print("\n" + "=" * 70)
    if total_issues == 0:
        print("✓ SONUÇ: TÜM KONTROLLER GEÇTİ - VERİ TUTARLIDIR")
        print("=" * 70)
        return 0
    else:
        print(f"⚠ SONUÇ: {total_issues} SORUN BULUNDU")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(main())
