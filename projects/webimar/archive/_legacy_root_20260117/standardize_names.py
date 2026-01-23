#!/usr/bin/env python3
import json
import re

def standardize_name(name):
    """İsimleri GeoJSON formatına uygun şekilde standardize eder"""
    # Yıldız işaretlerini kaldır
    name = name.replace('*', '')
    # Büyük harfe çevir
    name = name.upper()
    # Fazla boşlukları temizle
    name = ' '.join(name.split())
    return name

def create_name_mapping(geojson_districts, havza_districts):
    """Havza isimlerini GeoJSON isimlerine eşleştir - gelişmiş algoritma"""
    mapping = {}

    # 1. Önce doğrudan eşleşenleri bul
    for geo_name in geojson_districts:
        for havza_name in havza_districts:
            if standardize_name(havza_name) == geo_name:
                mapping[havza_name] = geo_name
                break

    # 2. Benzerlik tabanlı eşleştirme (Levenshtein distance ile)
    def levenshtein_distance(s1, s2):
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    # Eşleşmemiş havza ilçeleri için GeoJSON'da en benzerini bul
    used_geo_names = set(mapping.values())
    available_geo_names = geojson_districts - used_geo_names

    for havza_name in havza_districts:
        if havza_name in mapping:
            continue

        standardized_havza = standardize_name(havza_name)
        best_match = None
        best_distance = float('inf')

        for geo_name in available_geo_names:
            distance = levenshtein_distance(standardized_havza, geo_name)
            if distance < best_distance and distance <= 2:  # Max 2 karakter farkı
                best_distance = distance
                best_match = geo_name

        if best_match:
            mapping[havza_name] = best_match
            used_geo_names.add(best_match)

    # 3. Manuel eşleştirme için kalan durumlar
    manual_mappings = {
        # İlçeler
        '19 Mayıs': '19 MAYIS',
        'Acıgöl*': 'ACIGÖL',
        'Akören*': 'AKÖREN',
        'Alpu*': 'ALPU',
        'Altunhisar*': 'ALTUNHİSAR',
        'Altınekin*': 'ALTINEKİN',
        'Ayrancı*': 'AYRANCI',
        'Bala*': 'BALA',
        'Beylikova*': 'BEYLİKOVA',
        'Boztepe*': 'BOZTEPE',
        'Cihanbeyli*': 'CİHANBEYLİ',
        'Derbent*': 'DERBENT',
        'Derik*': 'DERİK',
        'Derinkuyu*': 'DERİNKUYU',
        'Doğanhisar*': 'DOĞANHİSAR',
        'Ereğli*': 'EREĞLİ',
        'Eskil*': 'ESKİL',
        'Gölbaşı*': 'GÖLBAŞI',
        'Gülağaç*': 'GÜLAĞAÇ',
        'Gülşehir*': 'GÜLŞEHİR',
        'Güneysınır*': 'GÜNEYSINIR',
        'Güzelyurt*': 'GÜZELYURT',
        'Halkapınar*': 'HALKAPINAR',
        'Haymana*': 'HAYMANA',
        'Kadınhanı*': 'KADINHANI',
        'Karapınar*': 'KARAPINAR',
        'Karatay*': 'KARATAY',
        'Kazımkarabekir*': 'KAZIMKARABEKİR',
        'Kızıltepe*': 'KIZILTEPE',
        'Kumlu*': 'KUMLU',
        'Kulu*': 'KULU',
        'Mahmudiye*': 'MAHMUDİYE',
        'Meram*': 'MERAM',
        'Mihalıççık*': 'MİHALIÇÇIK',
        'Mucur*': 'MUCUR',
        'Reyhanlı*': 'REYHANLI',
        'Sarayönü*': 'SARAYÖNÜ',
        'Selçuklu*': 'SELÇUKLU',
        'Sereflikoçhisar*': 'ŞEREFLİKOÇHİSAR',
        'Sivrihisar*': 'SİVRİHİSAR',
        'Sultanhanı*': 'SULTANHANI',
        'Tuzlukçu*': 'TUZLUKÇU',
        'Viranşehir*': 'VİRANŞEHİR',
        'Çifteler*': 'ÇİFTELER',
        'Çiftlik*': 'ÇİFTLİK',
        'Çumra*': 'ÇUMRA',
        # İl düzeltmeleri
        'İkizce': 'İKİZCE',
        'İkizdere': 'İKİZDERE',
        'İlkadım': 'İLKADIM',
        'İmamoğlu': 'İMAMOĞLU',
        'İmranlı': 'İMRANLI',
        'İncesu': 'İNCESU',
        'İncirliova': 'İNCİRLİOVA',
        'İnebolu': 'İNEBOLU',
        'İnegöl': 'İNEGÖL',
        'İnhisar': 'İNHİSAR',
        'İnönü': 'İNÖNÜ',
        'İpekyolu': 'İPEKYOLU',
        'İpsala': 'İPSALA',
        'İscehisar': 'İSCEHİSAR',
        'İskenderun': 'İSKENDERUN',
        'İskilip': 'İSKİLİP',
        'İslahiye': 'İSLAHİYE',
        'İspir': 'İSPİR',
        'İvrindi': 'İVRİNDİ',
        'İyidere': 'İYİDERE',
        'İzmit': 'İZMİT',
        'İznik': 'İZNİK',
        # Ek manual eşleştirmeler
        'Beyşehir': 'BEYŞEHİR',
        'Dikili': 'DİKİLİ',
        'Düziçi': 'DÜZİÇİ',
        'Milas': 'MİLAS',
        'Polateli': 'POLATELİ',
        'Kumluca': 'KUMLUCA',
        'Fethiye': 'FETHİYE',
        'Bodrum': 'BODRUM',
        'Marmaris': 'MARMARİS',
        'Datça': 'DATÇA',
        'Köyceğiz': 'KÖYCEĞİZ',
        'Ula': 'ULA',
        'Ortaca': 'ORTACA',
        'Dalaman': 'DALAMAN',
        'Kavaklıdere': 'KAVAKLIDERE',
        'Çine': 'ÇİNE',
        'Yatağan': 'YATAĞAN',
        'Tavas': 'TAVAS',
        'Ula': 'ULA',
        'Karpuzlu': 'KARPUZLU',
        'Köyceğiz': 'KÖYCEĞİZ',
        'Dalyan': 'DALAMAN',  # Yaklaşık eşleştirme
        'Marmaris': 'MARMARİS',
        'İçmeler': 'MARMARİS',  # Yaklaşık eşleştirme
        'Turunç': 'MARMARİS',  # Yaklaşık eşleştirme
    }

    for havza_name, geo_name in manual_mappings.items():
        if havza_name in havza_districts and geo_name in geojson_districts:
            mapping[havza_name] = geo_name

    return mapping

def main():
    # GeoJSON'dan isimleri oku
    with open('/home/akn/Genel/webimar/webimar-nextjs/public/turkey-districts.geojson', 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    geojson_provinces = set()
    geojson_districts = set()
    for feature in geojson_data['features']:
        props = feature['properties']
        geojson_provinces.add(props['ADM1_TR'])
        geojson_districts.add(props['ADM2_TR'])

    # Havza verilerini oku
    with open('/home/akn/Genel/webimar/havza_urun_desen.json', 'r', encoding='utf-8') as f:
        havza_data = json.load(f)

    havza_provinces = set(havza_data.keys())
    havza_districts = set()
    for province, districts in havza_data.items():
        for district in districts.keys():
            havza_districts.add(district)

    # İl isimlerini düzelt
    province_mapping = {}
    for geo_prov in geojson_provinces:
        for havza_prov in havza_provinces:
            if standardize_name(havza_prov) == geo_prov:
                province_mapping[havza_prov] = geo_prov
                break

    # Özel il düzeltmeleri
    province_mapping['ESKİŞEHİR'] = 'ESKİŞEHİR'

    # İlçe mapping'ini oluştur
    district_mapping = create_name_mapping(geojson_districts, havza_districts)

    # Yeni havza verilerini oluştur
    new_havza_data = {}
    for old_province, districts in havza_data.items():
        # İl adını düzelt
        new_province = province_mapping.get(old_province, old_province)

        new_havza_data[new_province] = {}
        for old_district, products in districts.items():
            # İlçe adını düzelt
            new_district = district_mapping.get(old_district, old_district)
            new_havza_data[new_province][new_district] = products

    # Yeni dosyayı kaydet
    with open('/home/akn/Genel/webimar/havza_urun_desen_standardized.json', 'w', encoding='utf-8') as f:
        json.dump(new_havza_data, f, ensure_ascii=False, indent=2)

    print("Standardizasyon tamamlandı!")
    print(f"Orijinal dosya: {len(havza_data)} il")
    print(f"Standardize dosya: {len(new_havza_data)} il")

    # Örnek düzeltmeleri göster
    print("\nİl düzeltme örnekleri:")
    for old, new in list(province_mapping.items())[:3]:
        if old != new:
            print(f"  {old} → {new}")

    print("\nİlçe düzeltme örnekleri:")
    for old, new in list(district_mapping.items())[:5]:
        if old != new:
            print(f"  {old} → {new}")

if __name__ == "__main__":
    main()