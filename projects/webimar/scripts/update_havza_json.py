#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out

# Türkçe karakter yazım haritası
turkish_fixes = {
    'BALIKESIR': 'BALIKESİR',
    'BILECIK': 'BİLECİK',
    'BINGÖL': 'BİNGÖL',
    'BITLIS': 'BİTLİS',
    'DENIZLI': 'DENİZLİ',
    'EDIRNE': 'EDİRNE',
    'ERZINCAN': 'ERZİNCAN',
    'ESKIŞEHIR': 'ESKİŞEHİR',
    'GAZIANTEP': 'GAZİANTEP',
    'GIRESUN': 'GİRESUN',
    'GÜMÜŞHANE': 'GÜMÜŞHANE',
    'KAYSERI': 'KAYSERİ',
    'KILIS': 'KİLİS',
    'KIRŞEHIR': 'KIRŞEHİR',
    'MANISA': 'MANİSA',
    'MERSIN': 'MERSİN',
    'NIĞDE': 'NİĞDE',
    'SIIRT': 'SİİRT',
    'SINOP': 'SİNOP',
    'SIVAS': 'SİVAS',
    'TEKIRDAĞ': 'TEKİRDAĞ',
    'TUNCELI': 'TUNCELİ',
    'İZMIR': 'İZMİR',
    'OSMANIYE': 'OSMANIYE',  # İsim kontrolü için
}


TR_KEYMAP = str.maketrans({
    'İ': 'I',
    'I': 'I',
    'ı': 'I',
    'i': 'I',
    'Ö': 'O',
    'ö': 'O',
    'Ü': 'U',
    'ü': 'U',
    'Ç': 'C',
    'ç': 'C',
    'Ş': 'S',
    'ş': 'S',
    'Ğ': 'G',
    'ğ': 'G',
    'Â': 'A',
    'â': 'A',
    'Î': 'I',
    'î': 'I',
    'Û': 'U',
    'û': 'U',
})


def normalize_key(value: str) -> str:
    if not value:
        return ''
    v = value.strip().upper()
    v = re.sub(r"\s+", "", v)
    v = v.translate(TR_KEYMAP)
    v = re.sub(r"[^A-Z0-9]", "", v)
    return v

# İlçe adı düzeltmeleri (GeoJSON ve resmi adlarla uyum için)
ilce_fixes = {
    'ALTEYÜL': 'ALTIEYLÜL',
    'ALTEYUL': 'ALTIEYLÜL',
    'BOZIYÜK': 'BOZÜYÜK',
    'BOZIYUK': 'BOZÜYÜK',
    'KARAMALI': 'KARAMANLI',
    'TEFFENI': 'TEFENNİ',
    'TEFFENİ': 'TEFENNİ',
    'KOVANCLAR': 'KOVANCILAR',
    'MIHALÇIÇIK': 'MİHALIÇÇIK',
    'SEREFLIKOÇHISAR': 'ŞEREFLİKOÇHİSAR',
    'DERBEN': 'DERBENT',
}

# Türkiye'nin tüm 81 ilini başlangıç olarak oluştur
all_provinces = [
    'ADANA', 'ADIYAMAN', 'AFYONKARAHISAR', 'AĞRI', 'AKSARAY', 'AMASYA', 'ANKARA', 'ANTALYA',
    'ARDAHAN', 'ARTVIN', 'AYDIN', 'BALIKESİR', 'BARTIN', 'BATMAN', 'BAYBURT', 'BİLECİK',
    'BİNGÖL', 'BİTLİS', 'BOLU', 'BURDUR', 'BURSA', 'ÇANAKKALE', 'ÇANKIRI', 'ÇORUM',
    'DENİZLİ', 'DIYARBAKIR', 'DÜZCE', 'EDİRNE', 'ELAZIĞ', 'ERZİNCAN', 'ERZURUM', 'ESKİŞEHİR',
    'GAZİANTEP', 'GİRESUN', 'GÜMÜŞHANE', 'HAKKARI', 'HATAY', 'IĞDIR', 'ISPARTA', 'İSTANBUL',
    'İZMİR', 'KAHRAMANMARAŞ', 'KARABÜK', 'KARAMAN', 'KARS', 'KASTAMONU', 'KAYSERİ', 'KIRIKKALE',
    'KIRKLARELI', 'KIRŞEHİR', 'KİLİS', 'KOCAELI', 'KONYA', 'KÜTAHYA', 'MALATYA', 'MANİSA',
    'MARDIN', 'MERSİN', 'MUĞLA', 'MUŞ', 'NEVŞEHIR', 'NİĞDE', 'ORDU', 'OSMANIYE', 'RIZE',
    'SAKARYA', 'SAMSUN', 'SİİRT', 'SİNOP', 'SİVAS', 'ŞANLIURFA', 'ŞIRNAK', 'TEKİRDAĞ',
    'TOKAT', 'TRABZON', 'TUNCELİ', 'UŞAK', 'VAN', 'YALOVA', 'YOZGAT', 'ZONGULDAK'
]

province_by_norm = {normalize_key(p): p for p in all_provinces}
ilce_fixes_by_norm = {normalize_key(k): v for k, v in ilce_fixes.items()}

# Markdown dosyasını oku
with open("/home/akn/local/projects/webimar/webimar-nextjs/data/2026 havza ürün deseni.md", "r", encoding="utf-8") as f:
    markdown_content = f.read()

# Yeni JSON oluştur (tüm şehirlerle başla)
json_data = {prov: {} for prov in all_provinces}

# Satırları teker teker işle
lines = markdown_content.split('\n')

for line in lines:
    # Tablo satırlarını kontrol et (| ile başlaması gerekir)
    if not line.startswith('|'):
        continue
    
    # Ayırıcı satırlarını atla (-----)
    if '-----' in line or 'HAVZA ADI' in line or 'PLANLAMAYA' in line:
        continue
    
    # Pipe karakterlerini kullanarak alanları ayırt et
    parts = [p.strip() for p in line.split('|')]
    
    # | şehir/ilçe | ürünler | formatında 3 parça olmalı
    if len(parts) < 3:
        continue
    
    havza_adi = parts[1].strip()
    urun_deseni = parts[2].strip()
    
    # Boş alanları atla
    if not havza_adi or not urun_deseni:
        continue
    
    # Havza ve ilçe adını ayırt et (/ ile ayrılmalı)
    if "/" not in havza_adi:
        continue
    
    # Şehir ve ilçe adını ayırt et
    havza_parts = havza_adi.split("/")
    if len(havza_parts) != 2:
        continue
    
    sehir_raw = havza_parts[0].strip()
    ilce_raw = havza_parts[1].strip()
    if ilce_raw.endswith('*'):
        ilce_raw = ilce_raw[:-1].strip()

    sehir_norm = normalize_key(sehir_raw)
    ilce_norm = normalize_key(ilce_raw)

    sehir = province_by_norm.get(sehir_norm, sehir_raw.upper())
    ilce = ilce_fixes_by_norm.get(ilce_norm, ilce_raw.upper())

    # Üstte normalize lookup yapıldı; legacy düzeltmelerle de uyum için ihtiyaten bırakıyoruz
    ilce = ilce_fixes.get(ilce, ilce)
    sehir = turkish_fixes.get(sehir, sehir)
    
    # Parantez içindeki açıklamaları kaldır
    # Örneğin: "Mısır (Dane)" -> "Mısır"
    urunler_text = re.sub(r'\s*\([^)]+\)', '', urun_deseni)
    
    # Ürünleri virgülü ayırt et ve liste yap
    urunler = [u.strip() for u in urunler_text.split(",") if u.strip()]
    urunler = dedupe_preserve_order(urunler)
    
    # Ürün listesi boşsa atla
    if not urunler:
        continue
    
    # Şehir JSON'da yoksa ekle
    if sehir not in json_data:
        json_data[sehir] = {}
    
    # İlçeyi ekle (overwrite)
    json_data[sehir][ilce] = urunler

# JSON dosyasını yaz (Türkiye'nin 81 ilini takip ederek)
final_data = {}
for prov in all_provinces:
    if prov in json_data:
        final_data[prov] = json_data[prov]

with open("/home/akn/local/projects/webimar/webimar-nextjs/public/havza_urun_desen.json", "w", encoding="utf-8") as f:
    json.dump(final_data, f, ensure_ascii=False, indent=2)

print("JSON dosyası güncellendi!")
print(f"Toplam şehir sayısı: {len(final_data)}")
