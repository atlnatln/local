#!/usr/bin/env python3
"""
kml_places_final.csv'de olmayan mahalle verilerini ptt_address_data_with_coords_merged.json'dan çeker
ve CSV dosyasına ekler.
"""

import json
import csv
from pathlib import Path
from typing import Set, Tuple, List, Dict

def normalize_mahalle_name(name: str) -> str:
    """Mahalle adını normalize et (trailing MAH vs)"""
    return name.replace(" MAH", "").replace("MAH", "").strip()

def load_csv_data() -> Tuple[Set[Tuple[str, str, str]], Dict]:
    """CSV dosyasından mevcut verileri yükle"""
    csv_file = Path("/home/akn/Genel/webimar/kml_places_final.csv")
    existing = set()
    csv_dict = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            il = row['il'].strip()
            ilce = row['ilce'].strip()
            mahalle = row['mahalle'].strip()
            
            key = (il, ilce, mahalle)
            existing.add(key)
            csv_dict[key] = row
    
    return existing, csv_dict

def load_json_data() -> List[Dict]:
    """JSON dosyasından verileri yükle"""
    json_file = Path("/home/akn/Genel/webimar/ptt_address_data_with_coords_merged.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_missing_locations() -> List[Dict]:
    """JSON'da olan ama CSV'de olmayan koordinatlı mahalleleri bul"""
    csv_existing, _ = load_csv_data()
    json_data = load_json_data()
    
    missing = []
    found_count = 0
    skipped_no_coords = 0
    skipped_existing = 0
    
    for il_item in json_data:
        il = il_item['il_adi'].strip()
        
        for ilce_item in il_item['ilceler']:
            ilce = ilce_item['ilce_adi'].strip()
            
            for mahalle_item in ilce_item['mahalleler']:
                mahalle_raw = mahalle_item['mahalle_adi'].strip()
                mahalle = normalize_mahalle_name(mahalle_raw)
                
                lat = mahalle_item.get('lat')
                lon = mahalle_item.get('lon')
                
                # Koordinatları kontrol et
                if lat is None or lon is None:
                    skipped_no_coords += 1
                    continue
                
                # CSV'de olup olmadığını kontrol et
                csv_key = (il, ilce, mahalle)
                if csv_key in csv_existing:
                    skipped_existing += 1
                    continue
                
                # Yeni mahalle
                missing.append({
                    'il': il,
                    'ilce': ilce,
                    'mahalle': mahalle,
                    'lat': lat,
                    'lon': lon
                })
                found_count += 1
    
    print(f"📊 İstatistikler:")
    print(f"  ✅ Yeni mahalleler (CSV'de yok, JSON'da var, koordinatlı): {found_count}")
    print(f"  ⏭️  CSV'de zaten mevcut: {skipped_existing}")
    print(f"  ❌ Koordinatsız mahalleler: {skipped_no_coords}")
    
    return sorted(missing, key=lambda x: (x['il'], x['ilce'], x['mahalle']))

def merge_csv_with_missing():
    """Eksik mahalle verilerini CSV'ye ekle"""
    csv_file = Path("/home/akn/Genel/webimar/kml_places_final.csv")
    
    # Mevcut verileri oku
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        existing_rows = list(reader)
    
    # Eksik verileri bul
    missing_locations = find_missing_locations()
    
    if not missing_locations:
        print("\n✅ Tüm mahalleler CSV dosyasında mevcut. Ekleme yapılacak veri yok.")
        return
    
    # Eksik verileri CSV satırlarına dönüştür
    new_rows = []
    for loc in missing_locations:
        new_rows.append({
            'il': loc['il'],
            'ilce': loc['ilce'],
            'mahalle': loc['mahalle'],
            'lat': loc['lat'],
            'lon': loc['lon']
        })
    
    # Tüm verileri birleştir ve sırala
    all_rows = existing_rows + new_rows
    all_rows.sort(key=lambda x: (x['il'], x['ilce'], x['mahalle']))
    
    # CSV dosyasına yaz
    with open(csv_file, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['il', 'ilce', 'mahalle', 'lat', 'lon']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n✅ CSV dosyası güncellendi!")
    print(f"   Yeni satır sayısı: {len(new_rows)}")
    print(f"   Toplam satır sayısı: {len(all_rows)}")
    print(f"   Dosya: {csv_file}")
    
    # Eklenen ilk 10 mahalleyi göster
    print(f"\n📍 Eklenen ilk 10 mahalle:")
    for i, row in enumerate(new_rows[:10], 1):
        print(f"   {i}. {row['il']}/{row['ilce']}/{row['mahalle']} ({row['lat']}, {row['lon']})")

if __name__ == '__main__':
    merge_csv_with_missing()
