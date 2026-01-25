import json

def normalize_name(name):
    if not name:
        return ''
    # Büyük harfe çevir
    name = name.upper()
    # Boşlukları kaldır
    name = ''.join(name.split())
    # Türkçe karakterleri normalize
    name = name.replace('İ', 'I').replace('Ö', 'O').replace('Ü', 'U').replace('Ç', 'C').replace('Ş', 'S').replace('Ğ', 'G')
    return name

# GeoJSON'u oku
with open('/home/akn/vps/projects/webimar/webimar-nextjs/public/turkey-districts.geojson', 'r', encoding='utf-8') as f:
    geo = json.load(f)

geo_set = set()
for feature in geo['features']:
    il = feature['properties']['ADM1_TR']
    ilce = feature['properties']['ADM2_TR']
    geo_set.add((normalize_name(il), normalize_name(ilce)))

# Havza JSON'u oku
with open('/home/akn/vps/projects/webimar/webimar-nextjs/public/havza_urun_desen.json', 'r', encoding='utf-8') as f:
    havza = json.load(f)

havza_set = set()
for il, ilceler in havza.items():
    for ilce in ilceler:
        havza_set.add((normalize_name(il), normalize_name(ilce)))

# GeoJSON'da var ama havza'da yok
missing_in_havza = geo_set - havza_set

# Havza'da var ama geo'da yok
extra_in_havza = havza_set - geo_set

print("GeoJSON'da var ama havza'da yok (normalize edilmiş):")
for il, ilce in sorted(missing_in_havza):
    print(f"{il} - {ilce}")

print(f"\nToplam: {len(missing_in_havza)}")

print("\nHavza'da var ama geo'da yok (normalize edilmiş):")
for il, ilce in sorted(extra_in_havza):
    print(f"{il} - {ilce}")

print(f"\nToplam: {len(extra_in_havza)}")