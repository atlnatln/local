"""
KML dosyalarını işlemek için yardımcı fonksiyonlar.
Bu modül, KML dosyalarını okuyup polygon verilerini çıkarır.
"""
import os
import json
import zipfile
import threading
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Dict, Any

from django.conf import settings
from shapely.geometry import Point, Polygon, MultiPolygon, shape

def parse_kml_coordinates(coordinates_text):
    """
    KML koordinat metnini ayrıştırır ve Shapely Polygon formatına dönüştürür.
    """
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
    
    if len(coordinates) >= 3:  # Polygon için minimum 3 nokta gerekli
        return Polygon(coordinates)
    return None


def _extract_extended_data(placemark: ET.Element, ns: Dict[str, str]) -> Dict[str, str]:
    """Placemark içindeki ExtendedData/SchemaData alanlarını okur."""
    data: Dict[str, str] = {}

    for data_elem in placemark.findall('.//kml:Data', ns):
        key = data_elem.get('name')
        value_elem = data_elem.find('kml:value', ns)
        value = value_elem.text.strip() if value_elem is not None and value_elem.text else None
        if key and value:
            data[key] = value

    for simple_elem in placemark.findall('.//kml:SimpleData', ns):
        key = simple_elem.get('name')
        value = simple_elem.text.strip() if simple_elem is not None and simple_elem.text else None
        if key and value:
            data.setdefault(key, value)

    return data


def _resolve_placemark_name(placemark: ET.Element, ns: Dict[str, str]) -> str:
    """Placemark adı için name tag veya ExtendedData fallback uygular."""
    name_elem = placemark.find('.//kml:name', ns)
    name = name_elem.text.strip() if name_elem is not None and name_elem.text else None
    if name:
        return name

    data = _extract_extended_data(placemark, ns)
    for key in ('Ad', 'Adı', 'Adi', 'ad', 'adi', 'NAME', 'Name', 'name'):
        value = data.get(key)
        if value:
            return value

    return "Unnamed"

def _read_kml_content(file_path: str) -> Optional[str]:
    """Supports plain KML and KMZ (zip) containers and returns KML xml text."""
    if not os.path.exists(file_path):
        print(f"KML dosyası bulunamadı: {file_path}")
        return None

    if file_path.lower().endswith('.kmz'):
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # KMZ genellikle doc.kml içerir, yoksa ilk .kml dosyasını al
                kml_name = 'doc.kml'
                if kml_name not in zf.namelist():
                    kml_candidates = [n for n in zf.namelist() if n.lower().endswith('.kml')]
                    if not kml_candidates:
                        print(f"KMZ içinde KML bulunamadı: {file_path}")
                        return None
                    kml_name = kml_candidates[0]
                with zf.open(kml_name) as f:
                    return f.read().decode('utf-8', errors='ignore')
        except Exception as exc:
            print(f"KMZ okunamadı: {file_path}: {exc}")
            return None

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        # xsi namespace tanımını ekle (eğer yoksa)
        if 'xmlns:xsi=' not in content and 'xsi:schemaLocation' in content:
            content = content.replace(
                '<kml xmlns=',
                '<kml xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns=',
                1
            )
        return content
    except Exception as exc:
        print(f"KML okunamadı: {file_path}: {exc}")
        return None


def load_kml_file(file_path):
    """
    Tek bir KML/KMZ dosyasını yükler ve polygon listesi döndürür.
    """
    polygons: List[Polygon] = []
    names: List[str] = []

    content = _read_kml_content(file_path)
    if not content:
        return polygons, names

    try:
        root = ET.fromstring(content)

        # KML namespace
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}

        # Tüm Placemark'ları bul
        for placemark in root.findall('.//kml:Placemark', ns):
            name = _resolve_placemark_name(placemark, ns)

            # Tüm Polygon koordinatlarını bul (MultiGeometry desteği)
            for coordinates_elem in placemark.findall('.//kml:coordinates', ns):
                if coordinates_elem is not None and coordinates_elem.text:
                    polygon = parse_kml_coordinates(coordinates_elem.text)
                    if polygon:
                        polygons.append(polygon)
                        names.append(name)

    except ET.ParseError as e:
        print(f"KML dosyası ayrıştırma hatası {file_path}: {e}")
    except Exception as e:
        print(f"KML dosyası yükleme hatası {file_path}: {e}")

    print(f"Yüklenen dosya: {file_path}, Polygon sayısı: {len(polygons)}")
    return polygons, names


def load_geojson_polygons(file_path: str, name_keys: Tuple[str, ...]) -> Tuple[List[Polygon], List[str]]:
    """GeoJSON'daki poligonları Shapely Polygon/MultiPolygon olarak yükler."""
    polygons: List[Polygon] = []
    names: List[str] = []

    if not os.path.exists(file_path):
        print(f"GeoJSON dosyası bulunamadı: {file_path}")
        return polygons, names

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        features = data.get('features', [])
        for feature in features:
            geom = feature.get('geometry')
            props: Dict[str, Any] = feature.get('properties', {})
            if not geom:
                continue
            try:
                shp = shape(geom)
                if isinstance(shp, (Polygon, MultiPolygon)):
                    polygons.append(shp)
                    # isimleri birleştir
                    name = next((str(props[k]) for k in name_keys if k in props and props[k]), "")
                    names.append(name)
            except Exception:
                continue

        print(f"GeoJSON yüklendi: {file_path}, Polygon sayısı: {len(polygons)}")
    except Exception as exc:
        print(f"GeoJSON yükleme hatası {file_path}: {exc}")

    return polygons, names

class KMLDataManager:
    """
    KML verilerini yönetmek için thread-safe singleton sınıfı.
    Global değişken sorunlarını çözer ve thread güvenliği sağlar.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.polygons = []
            self.polygon_names = []
            self.yas_kapali_polygons = []
            self.yas_kapali_names = []
            self.province_polygons = []
            self.province_names = []
            self.district_polygons = []
            self.district_names = []
            self._kml_loaded = False
            self._data_lock = threading.RLock()
            self._initialized = True
    
    def get_data(self):
        """Thread-safe veri erişimi"""
        with self._data_lock:
            if not self._kml_loaded:
                self._load_kml_data()
            return {
                'polygons': self.polygons.copy(),
                'polygon_names': self.polygon_names.copy(),
                'yas_kapali_polygons': self.yas_kapali_polygons.copy(),
                'yas_kapali_names': self.yas_kapali_names.copy(),
                'province_polygons': self.province_polygons.copy(),
                'province_names': self.province_names.copy(),
                'district_polygons': self.district_polygons.copy(),
                'district_names': self.district_names.copy()
            }
    
    def _load_kml_data(self):
        """
        Tüm KML dosyalarını yükler ve instance değişkenlerine atar.
        Bu metod thread-safe'dir.
        """
        if self._kml_loaded:
            return
            
        # Ana klasör: repo root (BASE_DIR bir alt klasörde)
        repo_root = os.path.abspath(os.path.join(settings.BASE_DIR, os.pardir))
        api_static_kml = os.path.join(settings.BASE_DIR, 'static', 'kml')

        # Dosya yolları
        nextjs_public_kml = os.path.join(repo_root, 'webimar-nextjs', 'public', 'kml')
        
        kml_files = {
            'buyuk_ovalar': [
                # Önce GeoJSON (daha hızlı parse) - API static dizininde
                os.path.join(api_static_kml, 'turkey-ova-boundaries.geojson'),
                # Next.js public dizininde
                os.path.join(nextjs_public_kml, 'turkey-ova-boundaries.geojson'),
                # Fallback: KML dosyaları
                os.path.join(api_static_kml, 'Türkiye Ova Sınırları.kml'),
                os.path.join(repo_root, 'Türkiye Ova Sınırları.kml')
            ],
            'yas_kapali': [
                # Önce GeoJSON (daha hızlı parse) - API static dizininde
                os.path.join(api_static_kml, 'yas-kapali-alanlar.geojson'),
                # Next.js public dizininde
                os.path.join(nextjs_public_kml, 'yas-kapali-alanlar.geojson'),
                # Fallback: KML dosyaları
                os.path.join(api_static_kml, 'yas_kapali.kml'),
                os.path.join(repo_root, 'yas_kapali.kml'),
                os.path.join(repo_root, 'YAS Tahsisine Kapali Sahalar KML.kmz')
            ],
            'provinces': [
                # Önce API imajı içinde garanti olan static dizin
                os.path.join(api_static_kml, 'turkey-provinces.geojson'),
                # Next.js/React public (development repo yapısı)
                os.path.join(nextjs_public_kml, 'turkey-provinces.geojson'),
                os.path.join(repo_root, 'webimar-react', 'public', 'turkey-provinces.geojson'),
            ],
            'districts': [
                os.path.join(api_static_kml, 'turkey-districts.geojson'),
                os.path.join(nextjs_public_kml, 'turkey-districts.geojson'),
                os.path.join(repo_root, 'webimar-react', 'public', 'turkey-districts.geojson'),
            ]
        }

        # Static klasörü yoksa oluştur
        os.makedirs(api_static_kml, exist_ok=True)

        # Büyük ova (Türkiye geneli)
        for path in kml_files['buyuk_ovalar']:
            if os.path.exists(path):
                # GeoJSON mi KML mi kontrol et
                if path.endswith('.geojson'):
                    self.polygons, self.polygon_names = load_geojson_polygons(
                        path, ('name', 'Ad', 'Adı', 'Adi', 'ad', 'adi', 'NAME', 'Name')
                    )
                else:
                    self.polygons, self.polygon_names = load_kml_file(path)
                print(f"Büyük Ovalar yüklendi: {path}")
                break

        # YAS kapalı alanlar
        for path in kml_files['yas_kapali']:
            if os.path.exists(path):
                # GeoJSON mi KML mi kontrol et
                if path.endswith('.geojson'):
                    self.yas_kapali_polygons, self.yas_kapali_names = load_geojson_polygons(
                        path, ('name', 'Ad', 'Adı', 'Adi', 'ad', 'adi', 'NAME', 'Name')
                    )
                else:
                    self.yas_kapali_polygons, self.yas_kapali_names = load_kml_file(path)
                print(f"YAS Kapalı Alanlar yüklendi: {path}")
                break

        # İller
        for path in kml_files['provinces']:
            if os.path.exists(path):
                self.province_polygons, self.province_names = load_geojson_polygons(path, ('ADM1_TR', 'name', 'il'))
                break

        # İlçeler
        for path in kml_files['districts']:
            if os.path.exists(path):
                self.district_polygons, self.district_names = load_geojson_polygons(path, ('ADM2_TR', 'name', 'ilce'))
                break

        self._kml_loaded = True
        print(
            "KML veriler yüklendi - Büyük Ovalar: %s, YAS Kapalı Alanlar: %s, İller: %s, İlçeler: %s"
            % (len(self.polygons), len(self.yas_kapali_polygons), len(self.province_polygons), len(self.district_polygons))
        )

# Singleton instance'ı oluştur
_kml_manager = KMLDataManager()


def load_kml_data():
    """
    Geriye uyumluluk için eski API'yi korur.
    KML verilerini yükler.
    """
    _kml_manager.get_data()  # Bu otomatik olarak verileri yükler


def get_kml_polygons():
    """
    Thread-safe şekilde büyük ova polygonlarını döndürür.
    Returns: (polygons, names) tuple
    """
    data = _kml_manager.get_data()
    return data['polygons'], data['polygon_names']


def get_yas_kapali_polygons():
    data = _kml_manager.get_data()
    return data['yas_kapali_polygons'], data['yas_kapali_names']


def get_province_polygons():
    data = _kml_manager.get_data()
    return data['province_polygons'], data['province_names']


def get_district_polygons():
    data = _kml_manager.get_data()
    return data['district_polygons'], data['district_names']


def get_all_kml_data():
    """
    Thread-safe şekilde tüm KML verilerini döndürür.
    Returns: dict with all polygon data
    """
    return _kml_manager.get_data()


# Geriye uyumluluk için global değişken benzeri erişim
# Bu fonksiyonlar kullanılmalı, global değişkenler değil
def get_polygons():
    """Büyük ova polygonlarını döndürür"""
    polygons, _ = get_kml_polygons()
    return polygons


def get_polygon_names():
    """Büyük ova polygon isimlerini döndürür"""
    _, names = get_kml_polygons()
    return names


def get_yas_kapali_polygon_list():
    polygons, _ = get_yas_kapali_polygons()
    return polygons


def get_yas_kapali_names():
    _, names = get_yas_kapali_polygons()
    return names


def check_point_in_polygons(lat, lng, polygons, names):
    """
    Verilen koordinatın hangi polygonların içinde olduğunu kontrol eder.
    """
    point = Point(lng, lat)  # Shapely Point(lon, lat) formatını kullanır
    inside_polygons = []
    
    for i, polygon in enumerate(polygons):
        try:
            if polygon.contains(point):
                name = names[i] if i < len(names) else f"Polygon_{i}"
                inside_polygons.append(name)
        except Exception as e:
            print(f"Polygon kontrol hatası: {e}")
            continue
    
    return inside_polygons
