#!/usr/bin/env python3
"""
CSV dosyalarını flowering_data.json formatına dönüştürür.

CSV Format:
İl,İlçe,Bitki,Çiçeklenme Başlangıç,Çiçeklenme Bitiş
Adana,Aladağ,Kekik,10 Temmuz,20 Ağustos

JSON Format:
{
  "ADANA": {
    "ALADAĞ": [
      {"plant": "Kekik", "start": [7, 10], "end": [8, 20]}
    ]
  }
}
"""

import csv
import json
import os
from pathlib import Path
import re

# Türkçe ay isimleri -> ay numarası (yazım hatalarını da içerir)
MONTH_MAP = {
    'ocak': 1, 'şubat': 2, 'mart': 3, 'nisan': 4,
    'mayıs': 5, 'mayis': 5, 'mayız': 5,
    'haziran': 6, 'haizran': 6, 'haziraan': 6, 'hazitan': 6, 'hazi̇ran': 6,
    'temmuz': 7, 'tem': 7,
    'ağustos': 8, 'agustos': 8, 'ağustus': 8, 'ağostos': 8, 'ağistos': 8, 'ağustas': 8,
    'eylül': 9, 
    'ekim': 10, 
    'kasım': 11, 
    'aralık': 12
}

def parse_date(date_str: str) -> tuple:
    """
    '10 Temmuz' -> (7, 10)  # (ay, gün)
    """
    if not date_str or date_str.strip() == '':
        return None
    
    date_str = date_str.strip().lower()
    
    # Boşluksuz format düzeltmesi: "01mayıs" -> "01 mayıs"
    date_str = re.sub(r'(\d+)([a-züğışöç])', r'\1 \2', date_str)
    
    # "15ağustos" gibi formatlar için
    date_str = re.sub(r'(\d+)([a-züğışöç])', r'\1 \2', date_str)
    
    # "10 temmuz" formatı
    match = re.match(r'(\d+)\s+(\w+)', date_str)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        month = MONTH_MAP.get(month_name)
        if month:
            return (month, day)
    
    # "temmuz 10" formatı (alternatif)
    match = re.match(r'(\w+)\s+(\d+)', date_str)
    if match:
        month_name = match.group(1)
        day = int(match.group(2))
        month = MONTH_MAP.get(month_name)
        if month:
            return (month, day)
    
    # Sadece ay ismi varsa (gün olmadan) - 1 veya 15 varsay
    for month_name, month_num in MONTH_MAP.items():
        if month_name in date_str and not any(c.isdigit() for c in date_str):
            # Ay başı için 1, sonu için 28 varsay
            return (month_num, 15)  # Ortasını varsay
    
    print(f"  ⚠️  Tarih parse edilemedi: '{date_str}'")
    return None


def convert_csvs_to_json(csv_dir: str, output_file: str):
    """
    Tüm CSV dosyalarını tek bir JSON dosyasına dönüştürür.
    """
    result = {}
    stats = {
        'total_files': 0,
        'total_records': 0,
        'parse_errors': 0,
        'provinces': set(),
        'districts': set()
    }
    
    csv_path = Path(csv_dir)
    csv_files = sorted(csv_path.glob('*.csv'))
    
    print(f"📂 {len(csv_files)} CSV dosyası bulundu\n")
    
    for csv_file in csv_files:
        stats['total_files'] += 1
        print(f"📄 İşleniyor: {csv_file.name}")
        
        file_records = 0
        file_errors = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    province = row.get('İl', '').strip().upper()
                    district = row.get('İlçe', '').strip().upper()
                    plant = row.get('Bitki', '').strip()
                    start_str = row.get('Çiçeklenme Başlangıç', '')
                    end_str = row.get('Çiçeklenme Bitiş', '')
                    
                    if not all([province, district, plant, start_str, end_str]):
                        continue
                    
                    start_date = parse_date(start_str)
                    end_date = parse_date(end_str)
                    
                    if not start_date or not end_date:
                        file_errors += 1
                        stats['parse_errors'] += 1
                        continue
                    
                    # Veriyi yapıya ekle
                    if province not in result:
                        result[province] = {}
                        stats['provinces'].add(province)
                    
                    if district not in result[province]:
                        result[province][district] = []
                        stats['districts'].add(f"{province}/{district}")
                    
                    result[province][district].append({
                        'plant': plant,
                        'start': list(start_date),
                        'end': list(end_date)
                    })
                    
                    file_records += 1
                    stats['total_records'] += 1
                    
                except Exception as e:
                    print(f"  ❌ Satır hatası: {e}")
                    file_errors += 1
                    stats['parse_errors'] += 1
        
        print(f"   ✅ {file_records} kayıt, {file_errors} hata\n")
    
    # İlleri ve ilçeleri alfabetik sırala
    sorted_result = {}
    for province in sorted(result.keys()):
        sorted_result[province] = {}
        for district in sorted(result[province].keys()):
            # Bitkileri de sırala
            sorted_result[province][district] = sorted(
                result[province][district],
                key=lambda x: x['plant']
            )
    
    # JSON'a yaz
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_result, f, ensure_ascii=False, indent=2)
    
    print("=" * 50)
    print(f"✅ Dönüşüm tamamlandı!")
    print(f"   📊 {stats['total_files']} dosya işlendi")
    print(f"   📊 {len(stats['provinces'])} il")
    print(f"   📊 {len(stats['districts'])} ilçe")
    print(f"   📊 {stats['total_records']} toplam kayıt")
    print(f"   ⚠️  {stats['parse_errors']} parse hatası")
    print(f"   💾 Çıktı: {output_file}")
    
    return sorted_result


def verify_data(json_file: str, check_district: str = "BORÇKA"):
    """
    JSON dosyasındaki veriyi kontrol et
    """
    print(f"\n🔍 Doğrulama: {check_district} ilçesi kontrol ediliyor...")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for province, districts in data.items():
        if check_district in districts:
            print(f"\n📍 {check_district}, {province}:")
            for plant in districts[check_district]:
                print(f"   🌱 {plant['plant']}")
                print(f"      Çiçeklenme: {plant['start'][1]}/{plant['start'][0]} → {plant['end'][1]}/{plant['end'][0]}")
            return
    
    print(f"   ❌ {check_district} bulunamadı")


if __name__ == '__main__':
    script_dir = Path(__file__).parent
    csv_dir = script_dir / 'source_csvs'
    output_file = script_dir / 'flowering_data.json'
    
    print("🌸 Çiçeklenme Takvimi CSV → JSON Dönüştürücü")
    print("=" * 50)
    
    convert_csvs_to_json(str(csv_dir), str(output_file))
    
    # Borçka'yı kontrol et (kullanıcının belirttiği sorunlu ilçe)
    verify_data(str(output_file), "BORÇKA")
    
    # Köşk'ü de kontrol et
    verify_data(str(output_file), "KÖŞK")
