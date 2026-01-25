#!/usr/bin/env python3
"""
KML dosyalarını optimize eder - polygon'ları basitleştirir ve GeoJSON formatına çevirir.
Büyük KML dosyalarının harita üzerinde hızlı yüklenmesi için kullanılır.
"""
import os
import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional

# Django ayarlarını yükle
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webimar_api.settings')

try:
    import django
    django.setup()
except Exception as e:
    print(f"⚠️  Django yüklenemedi: {e}")
    print("Shapely kullanılarak devam ediliyor...")

from shapely.geometry import Polygon, mapping
from shapely.ops import transform
import zipfile


def parse_kml_coordinates(coordinates_text: str) -> List[Tuple[float, float]]:
    """KML koordinat metnini parse et"""
    coordinates = []
    coord_pairs = coordinates_text.strip().split()
    
    for coord_pair in coord_pairs:
        if coord_pair.strip():
            parts = coord_pair.split(',')
            if len(parts) >= 2:
                try:
                    lon = float(parts[0])
                    lat = float(parts[1])
                    coordinates.append((lon, lat))
                except ValueError:
                    continue
    
    return coordinates


def read_kml_content(file_path: str) -> str:
    """KML veya KMZ dosyasını oku ve namespace sorunlarını düzelt"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")
    
    # KMZ dosyası mı?
    if file_path.lower().endswith('.kmz'):
        with zipfile.ZipFile(file_path, 'r') as zf:
            kml_name = 'doc.kml'
            if kml_name not in zf.namelist():
                kml_candidates = [n for n in zf.namelist() if n.lower().endswith('.kml')]
                if not kml_candidates:
                    raise ValueError(f"KMZ içinde KML bulunamadı: {file_path}")
                kml_name = kml_candidates[0]
            with zf.open(kml_name) as f:
                content = f.read().decode('utf-8', errors='ignore')
    else:
        # Normal KML
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    
    # xsi namespace tanımını ekle (eğer yoksa)
    if 'xmlns:xsi=' not in content and 'xsi:schemaLocation' in content:
        # İlk <kml> tag'ine xsi namespace'i ekle
        content = content.replace(
            '<kml xmlns=',
            '<kml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns=',
            1  # Sadece ilk eşleşmeyi değiştir
        )
    
    return content


def _extract_extended_data(placemark: ET.Element) -> Dict[str, str]:
    """KML placemark içindeki ExtendedData ve SchemaData alanlarını okur."""
    data: Dict[str, str] = {}
    ns = '{http://www.opengis.net/kml/2.2}'

    for data_elem in placemark.findall(f'.//{ns}Data'):
        key = data_elem.get('name')
        value_elem = data_elem.find(f'{ns}value')
        value = value_elem.text.strip() if value_elem is not None and value_elem.text else None
        if key and value:
            data[key] = value

    for simple_elem in placemark.findall(f'.//{ns}SimpleData'):
        key = simple_elem.get('name')
        value = simple_elem.text.strip() if simple_elem is not None and simple_elem.text else None
        if key and value:
            data.setdefault(key, value)

    return data


def _resolve_placemark_name(placemark: ET.Element) -> str:
    """Placemark adı için name tag veya ExtendedData fallback uygular."""
    ns = '{http://www.opengis.net/kml/2.2}'
    name_elem = placemark.find(f'{ns}name')
    name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
    if name:
        return name

    data = _extract_extended_data(placemark)
    for key in ('Ad', 'Adı', 'Adi', 'ad', 'adi', 'NAME', 'Name', 'name'):
        value = data.get(key)
        if value:
            return value

    return "Unnamed"


def kml_to_geojson(kml_file: str, preserve_all_points: bool = True) -> Dict[str, Any]:
    """
    KML dosyasını GeoJSON'a çevir - VERİ KAYBI OLMADAN
    
    Args:
        kml_file: KML/KMZ dosya yolu
        preserve_all_points: True ise tüm koordinatları koru (önerilen)
    """
    print(f"\n📄 İşleniyor: {kml_file}")
    print(f"   Mod: {'TÜM NOKTALARI KORU (veri kaybı yok)' if preserve_all_points else 'Basitleştirilmiş'}")
    
    content = read_kml_content(kml_file)
    
    # XML namespace'leri tanımla (xsi dahil)
    # ElementTree için tüm namespace'leri kaydet
    namespaces = {
        'kml': 'http://www.opengis.net/kml/2.2',
        'gx': 'http://www.google.com/kml/ext/2.2',
        'atom': 'http://www.w3.org/2005/Atom',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
    }
    
    # Namespace'leri register et
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    
    root = ET.fromstring(content)
    
    features = []
    total_points = 0
    
    # Tüm Placemark'ları işle
    for placemark in root.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        name = _resolve_placemark_name(placemark)
        
        # Koordinatları bul
        coordinates_elem = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates')
        if coordinates_elem is None:
            continue
        
        coords = parse_kml_coordinates(coordinates_elem.text)
        if len(coords) < 3:
            continue
        
        total_points += len(coords)
        
        # Shapely Polygon oluştur (sadece geometri validasyonu için)
        try:
            polygon = Polygon(coords)
            
            # GeoJSON feature oluştur - AYNEN TÜM NOKTALARI KULLAN
            feature = {
                'type': 'Feature',
                'properties': {
                    'name': name,
                    'point_count': len(coords)
                },
                'geometry': mapping(polygon)  # Orijinal polygon, simplify YOK
            }
            
            features.append(feature)
            
        except Exception as e:
            print(f"   ⚠️  Polygon oluşturulamadı ({name}): {e}")
            continue
    
    # İstatistikler
    print(f"   ✅ {len(features)} polygon işlendi")
    print(f"   📊 Toplam nokta sayısı: {total_points:,} (korundu)")
    
    geojson = {
        'type': 'FeatureCollection',
        'features': features,
        'metadata': {
            'source_file': os.path.basename(kml_file),
            'preserve_all_points': preserve_all_points,
            'total_points': total_points,
            'feature_count': len(features),
            'note': 'Tüm koordinatlar korunmuştur, veri kaybı yoktur'
        }
    }
    
    return geojson


def optimize_kml_files():
    """Ana KML dosyalarını GeoJSON formatına çevir - VERİ KAYBI OLMADAN"""
    
    # Dosya yolları
    script_dir = Path(__file__).parent.parent
    static_kml = script_dir / 'static' / 'kml'
    output_dir = script_dir.parent / 'webimar-nextjs' / 'public' / 'kml'
    
    # Output klasörünü oluştur
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 KML → GeoJSON Format Dönüşümü Başladı")
    print("⚡ Tarayıcıda JSON parse etmek XML'den 5-10x daha hızlıdır")
    print("✅ Tüm koordinatlar aynen korunacak, VERİ KAYBI YOK")
    print(f"   Kaynak: {static_kml}")
    print(f"   Hedef: {output_dir}")
    
    # İşlenecek dosyalar - VERİ KAYBI OLMADAN, SADECE FORMAT DEĞİŞİMİ
    files_to_process = [
        {
            'input': static_kml / 'Türkiye Ova Sınırları.kml',
            'output': output_dir / 'turkey-ova-boundaries.geojson',
            'description': 'Türkiye Büyük Ova Sınırları (Tam Hassasiyet)'
        },
        {
            'input': static_kml / 'yas_kapali.kml',
            'output': output_dir / 'yas-kapali-alanlar.geojson',
            'description': 'YAS Tahsisine Kapalı Alanlar (Tam Hassasiyet)'
        },
    ]
    
    # Her dosyayı işle
    for config in files_to_process:
        input_file = config['input']
        output_file = config['output']
        
        if not input_file.exists():
            print(f"\n⚠️  Dosya bulunamadı: {input_file}")
            continue
        
        print(f"\n{'='*60}")
        print(f"📁 {config['description']}")
        
        try:
            # KML'i GeoJSON'a çevir - TÜM NOKTALARI KORU
            geojson = kml_to_geojson(str(input_file), preserve_all_points=True)
            
            # Dosyaya kaydet (minified JSON - daha küçük dosya)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(geojson, f, ensure_ascii=False, separators=(',', ':'))
            
            # Dosya boyutlarını göster
            input_size = input_file.stat().st_size / (1024 * 1024)  # MB
            output_size = output_file.stat().st_size / (1024 * 1024)  # MB
            
            print(f"   💾 Dosya boyutu: {input_size:.2f} MB → {output_size:.2f} MB")
            print(f"   📊 Format: KML → GeoJSON (parse hızı ~10x daha hızlı)")
            print(f"   ✅ Kaydedildi: {output_file.name}")
            
        except Exception as e:
            print(f"   ❌ Hata: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("✨ Format dönüşümü tamamlandı!")
    print(f"\n📦 GeoJSON dosyaları: {output_dir}")
    print("⚡ Avantajlar:")
    print("   • JSON parse hızı XML'den 5-10x daha hızlı")
    print("   • Tarayıcı native JSON desteği")
    print("   • Tüm koordinatlar korundu (veri kaybı yok)")
    print("   • Leaflet ile doğrudan kullanılabilir")


if __name__ == '__main__':
    optimize_kml_files()
