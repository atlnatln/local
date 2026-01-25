#!/usr/bin/env python3
import json

# GeoJSON dosyasından ESKİŞEHİR ilçelerini çıkar
with open('/home/akn/vps/projects/webimar/webimar-nextjs/public/turkey-districts.geojson', 'r') as f:
    geojson_data = json.load(f)

eskisehir_districts_geojson = set()
for feature in geojson_data['features']:
    if feature['properties']['ADM1_TR'] == 'ESKİŞEHİR':
        eskisehir_districts_geojson.add(feature['properties']['ADM2_TR'])

print("GeoJSON'da ESKİŞEHİR ilçeleri:")
for district in sorted(eskisehir_districts_geojson):
    print(f"  {district}")
print(f"Toplam: {len(eskisehir_districts_geojson)} ilçe")

# Havza verisindeki ESKİŞEHİR ilçeleri
with open('/home/akn/vps/projects/webimar/webimar-nextjs/public/havza_urun_desen.json', 'r') as f:
    havza_data = json.load(f)

eskisehir_districts_havza = set(havza_data['ESKİŞEHİR'].keys())

print("\nHavza verisinde ESKİŞEHİR ilçeleri:")
for district in sorted(eskisehir_districts_havza):
    print(f"  {district}")
print(f"Toplam: {len(eskisehir_districts_havza)} ilçe")

# Eksik olan ilçeler
missing_in_havza = eskisehir_districts_geojson - eskisehir_districts_havza
missing_in_geojson = eskisehir_districts_havza - eskisehir_districts_geojson

if missing_in_havza:
    print(f"\nGeoJSON'da var ama havza verisinde yok ({len(missing_in_havza)} adet):")
    for district in sorted(missing_in_havza):
        print(f"  {district}")

if missing_in_geojson:
    print(f"\nHavza verisinde var ama GeoJSON'da yok ({len(missing_in_geojson)} adet):")
    for district in sorted(missing_in_geojson):
        print(f"  {district}")