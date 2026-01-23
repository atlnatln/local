import json
import re

def parse_havza_urun_desen():
    with open('/home/akn/Genel/webimar/havza ürün deseni.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Başlıkları atla
    lines = content.split('\n')
    data = {}
    current_city = None
    water_restriction_notes = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Başlıkları atla
        if 'BİTKİSEL ÜRETİM PLANLANMASI' in line or 'HAVZA ÜRÜN DESENİ LİSTESİ' in line:
            i += 1
            continue

        # Şehir adı (büyük harf)
        if line.isupper() and len(line) > 2 and not any(char.isdigit() for char in line):
            current_city = line
            data[current_city] = {}
            i += 1
            continue

        # İlçe adı (Şehir/İlçe)
        if '/' in line and current_city:
            district_full = line
            # Sadece ilçe adını al
            district = district_full.split('/', 1)[1] if '/' in district_full else district_full
            i += 1
            if i < len(lines):
                products_line = lines[i].strip()
                if products_line and not products_line.startswith('*'):
                    # Ürünleri parse et ve standardize et
                    products = [p.strip() for p in products_line.split(',')]
                    # Parantezleri kaldır ve standardize et
                    standardized_products = []
                    for p in products:
                        # (Yağlık) gibi parantezleri kaldır
                        p = re.sub(r'\s*\([^)]*\)', '', p).strip()
                        standardized_products.append(p)
                    data[current_city][district] = standardized_products
                i += 1
            continue

        # Su kısıtı notları
        if '*' in line or 'Su kısıtı' in line:
            water_restriction_notes.append(line)
            i += 1
            continue

        i += 1

    return data, water_restriction_notes

# Parse et
data, notes = parse_havza_urun_desen()

# JSON olarak kaydet
with open('/home/akn/Genel/webimar/havza_urun_desen.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("JSON dosyası oluşturuldu: havza_urun_desen.json")