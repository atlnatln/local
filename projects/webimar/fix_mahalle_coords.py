#!/usr/bin/env python3
"""
Mahalle koordinatlarını düzeltme scripti.
1. İlçe/il poligonu dışındaki noktaları tespit et
2. OSM KML ve shapefile verilerinden doğru koordinat bulmaya çalış
3. Bulunamazsa noktayı sil
"""
import csv
import json
import sys
import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

try:
    from shapely.geometry import Point, shape
    import geopandas as gpd
except ImportError:
    print("shapely ve geopandas gereklidir: pip install shapely geopandas")
    sys.exit(1)

csv.field_size_limit(sys.maxsize)

# === Yollar ===
WEBIMAR_CSV = Path("/home/akn/local/projects/webimar/webimar-nextjs/public/kml_places_final.csv")
OUTPUT_CSV = Path("/home/akn/local/projects/webimar/webimar-nextjs/public/kml_places_final_cleaned.csv")
REMOVED_CSV = Path("/home/akn/local/projects/webimar/webimar-nextjs/public/kml_places_removed.csv")

IL_GEOJSON = "/home/akn/local/projects/webimar/webimar-api/static/kml/turkey-provinces.geojson"
ILCE_GEOJSON = "/home/akn/local/projects/webimar/webimar-api/static/kml/turkey-districts.geojson"

OSM_KML_FILES = [
    "/home/akn/Genel/kml/export(5).kml",
    "/home/akn/Genel/kml/export(7).kml",
]
OSM_SHP_FILES = [
    "/home/akn/Genel/kml/turkey-251209-free.shp/gis_osm_places_free_1.shp",
    "/home/akn/Genel/kml/turkey-251209-free.shp/gis_osm_places_a_free_1.shp",
]

# === Normalizasyon ===
def normalize_tr(s):
    if not s:
        return ""
    s = str(s).strip().upper()
    repl = {
        'İ': 'I', 'Ş': 'S', 'Ğ': 'G', 'Ü': 'U', 'Ö': 'O', 'Ç': 'C',
        'Â': 'A', 'Û': 'U', 'Î': 'I', 'Ê': 'E',
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    s = re.sub(r'\s+MAHALLE(SI)?$', '', s)
    s = re.sub(r'\s+KOYU?$', '', s)
    s = re.sub(r'\s+MERKEZ$', '', s)
    s = s.replace(' ', '')
    return s


def find_osm_match(mahalle_norm, il_key, ilce_key, osm_by_name, ilce_polys):
    """OSM verilerinden en iyi eşleşmeyi bul."""
    candidates = osm_by_name.get(mahalle_norm, [])
    if not candidates:
        return None
    
    best = None
    best_score = 0
    
    for cand in candidates:
        score = 0
        
        # İl hint kontrolü
        if cand['il_hint'] and cand['il_hint'] == il_key:
            score += 3
        elif cand['il_hint'] and (cand['il_hint'] in il_key or il_key in cand['il_hint']):
            score += 1
        
        # İlçe hint kontrolü
        if cand['ilce_hint'] and cand['ilce_hint'] == ilce_key:
            score += 3
        elif cand['ilce_hint'] and (cand['ilce_hint'] in ilce_key or ilce_key in cand['ilce_hint']):
            score += 1
        
        # İlçe poligonu içinde mi?
        cand_point = Point(cand['lon'], cand['lat'])
        for poly in ilce_polys.get((il_key, ilce_key), []):
            if poly.contains(cand_point):
                score += 5
                break
        
        if score > best_score:
            best_score = score
            best = cand
    
    # En az bir hint veya poligon içinde olma eşleşmesi varsa kabul et
    if best and best_score >= 1:
        return best
    
    return None


# === Poligonları yükle ===
print("İl poligonları yükleniyor...")
il_polys = {}
with open(IL_GEOJSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
for feat in data['features']:
    props = feat['properties']
    il = props.get('ADM1_TR', props.get('name', '')).strip().upper()
    il_polys[normalize_tr(il)] = shape(feat['geometry'])
print(f"  {len(il_polys)} il yüklendi")

print("İlçe poligonları yükleniyor...")
ilce_polys = defaultdict(list)
with open(ILCE_GEOJSON, 'r', encoding='utf-8') as f:
    data = json.load(f)
for feat in data['features']:
    props = feat['properties']
    il = normalize_tr(props.get('ADM1_TR', ''))
    ilce = normalize_tr(props.get('ADM2_TR', ''))
    ilce_polys[(il, ilce)].append(shape(feat['geometry']))
print(f"  {len(ilce_polys)} ilçe kombinasyonu yüklendi")

# === OSM KML verilerini yükle ===
print("OSM KML verileri yükleniyor...")
osm_points = []

ns = {'kml': 'http://www.opengis.net/kml/2.2'}

for kml_file in OSM_KML_FILES:
    print(f"  {kml_file}")
    count = 0
    for event, elem in ET.iterparse(kml_file, events=('end',)):
        if elem.tag.endswith('Placemark'):
            name_elem = elem.find('kml:name', ns)
            name = name_elem.text.strip() if name_elem is not None and name_elem.text else ""
            if not name:
                elem.clear()
                continue
            
            point = elem.find('.//kml:Point/kml:coordinates', ns)
            if point is None or not point.text:
                elem.clear()
                continue
            
            coords = point.text.strip().split(',')
            if len(coords) < 2:
                elem.clear()
                continue
            
            lon, lat = float(coords[0]), float(coords[1])
            
            il_hint = ""
            ilce_hint = ""
            
            for data in elem.findall('.//kml:Data', ns):
                key = data.get('name', '')
                val_elem = data.find('kml:value', ns)
                val = val_elem.text.strip() if val_elem is not None and val_elem.text else ""
                
                if key == 'salb:adm1name':
                    il_hint = val
                elif key == 'salb:adm2name':
                    ilce_hint = val
                elif key == 'wikipedia' and val.startswith('tr:'):
                    parts = val[3:].split(',')
                    if len(parts) > 1:
                        ilce_hint = parts[1].strip()
            
            osm_points.append({
                'norm_name': normalize_tr(name),
                'lat': lat,
                'lon': lon,
                'il_hint': normalize_tr(il_hint),
                'ilce_hint': normalize_tr(ilce_hint),
            })
            count += 1
            elem.clear()
    print(f"    {count} nokta yüklendi")

print(f"  Toplam OSM KML noktası: {len(osm_points)}")

# === OSM Shapefile verilerini yükle ===
print("OSM Shapefile verileri yükleniyor...")
for shp_file in OSM_SHP_FILES:
    print(f"  {shp_file}")
    try:
        gdf = gpd.read_file(shp_file)
        shp_count = 0
        for _, row in gdf.iterrows():
            name = row.get('name', '')
            if not name or not isinstance(name, str):
                continue
            geom = row.geometry
            if geom is None:
                continue
            if geom.geom_type == 'Point':
                lat, lon = geom.y, geom.x
            else:
                centroid = geom.centroid
                lat, lon = centroid.y, centroid.x
            
            osm_points.append({
                'norm_name': normalize_tr(name),
                'lat': lat,
                'lon': lon,
                'il_hint': '',
                'ilce_hint': '',
            })
            shp_count += 1
        print(f"    {shp_count} nokta yüklendi")
    except Exception as e:
        print(f"    Hata: {e}")

print(f"  Toplam OSM noktası (KML+SHP): {len(osm_points)}")

# OSM noktalarını isme göre indeksle
print("OSM noktaları indeksleniyor...")
osm_by_name = defaultdict(list)
for p in osm_points:
    osm_by_name[p['norm_name']].append(p)

# === Webimar CSV'yi işle ===
print("Webimar CSV işleniyor...")

stats = {
    'toplam': 0,
    'dogru': 0,
    'düzeltilen_ilce_disi': 0,
    'düzeltilen_il_disi': 0,
    'silinen': 0,
}

kept_rows = []
removed_rows = []

with open(WEBIMAR_CSV, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    
    for row in reader:
        stats['toplam'] += 1
        
        il = row['il'].strip().upper()
        ilce = row['ilce'].strip().upper()
        mahalle = row['mahalle'].strip()
        
        try:
            lat = float(row['lat'])
            lon = float(row['lon'])
        except (ValueError, TypeError):
            removed_rows.append({**row, 'silme_nedeni': 'bozuk_koordinat'})
            stats['silinen'] += 1
            continue
        
        il_key = normalize_tr(il)
        ilce_key = normalize_tr(ilce)
        if ilce_key == 'MERKEZ':
            ilce_key = il_key
        
        mahalle_norm = normalize_tr(mahalle)
        point = Point(lon, lat)
        
        # İlçe poligonu içinde mi?
        ilce_ici = False
        for poly in ilce_polys.get((il_key, ilce_key), []):
            if poly.contains(point):
                ilce_ici = True
                break
        
        # İl poligonu içinde mi?
        il_ici = il_key in il_polys and il_polys[il_key].contains(point)
        
        if ilce_ici:
            stats['dogru'] += 1
            kept_rows.append(row)
        elif il_ici:
            new_coord = find_osm_match(mahalle_norm, il_key, ilce_key, osm_by_name, ilce_polys)
            if new_coord:
                row['lat'] = str(new_coord['lat'])
                row['lon'] = str(new_coord['lon'])
                stats['düzeltilen_ilce_disi'] += 1
                kept_rows.append(row)
            else:
                removed_rows.append({**row, 'silme_nedeni': 'ilce_disi_duzeltilemedi'})
                stats['silinen'] += 1
        else:
            new_coord = find_osm_match(mahalle_norm, il_key, ilce_key, osm_by_name, ilce_polys)
            if new_coord:
                row['lat'] = str(new_coord['lat'])
                row['lon'] = str(new_coord['lon'])
                stats['düzeltilen_il_disi'] += 1
                kept_rows.append(row)
            else:
                removed_rows.append({**row, 'silme_nedeni': 'il_disi_duzeltilemedi'})
                stats['silinen'] += 1
        
        if stats['toplam'] % 5000 == 0:
            print(f"  İşlendi: {stats['toplam']} | Doğru: {stats['dogru']} | Düzeltilen: {stats['düzeltilen_il_disi']+stats['düzeltilen_ilce_disi']} | Silinen: {stats['silinen']}")

# === Sonuçları kaydet ===
print()
print("=" * 60)
print("SONUÇLAR")
print("=" * 60)
print(f"Toplam işlenen:       {stats['toplam']}")
print(f"Zaten doğru:          {stats['dogru']} ({stats['dogru']/stats['toplam']*100:.1f}%)")
print(f"İl dışı düzeltilen:   {stats['düzeltilen_il_disi']}")
print(f"İlçe dışı düzeltilen: {stats['düzeltilen_ilce_disi']}")
print(f"Silinen:              {stats['silinen']} ({stats['silinen']/stats['toplam']*100:.1f}%)")
print(f"Kalan (temiz):        {len(kept_rows)} ({len(kept_rows)/stats['toplam']*100:.1f}%)")

print(f"\nTemiz CSV kaydediliyor: {OUTPUT_CSV}")
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(kept_rows)

print(f"Silinenler kaydediliyor: {REMOVED_CSV}")
with open(REMOVED_CSV, 'w', newline='', encoding='utf-8') as f:
    fn = list(fieldnames) + ['silme_nedeni']
    writer = csv.DictWriter(f, fieldnames=fn)
    writer.writeheader()
    writer.writerows(removed_rows)

print("Tamamlandı!")
