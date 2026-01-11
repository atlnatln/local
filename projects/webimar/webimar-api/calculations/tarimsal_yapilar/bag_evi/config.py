# -*- coding: utf-8 -*-
"""
Bağ Evi konfigürasyonu - Sabitler ve arazi tipi tanımları
Extracted from bag_evi.py for better maintainability
"""

# Ana sabitler - Unit test beklentileri için
MINIMUM_ARAZI_ALANI = 20000  # 2 hektar minimum alan (m²)
MAKSIMUM_YAPI_ORANI = 0.005  # %0.5 maksimum yapı oranı

# Arazi vasfı eşleştirme
ARAZI_VASFI_MAPPING = {
    1: 'tarla',
    2: 'ortu_alti', 
    3: 'sera',
    4: 'bag',
    5: 'dikili',
    6: 'ham_toprak'
}

# Desteklenen ağaç türleri
AGAC_TURLERI = [
    'uzum', 'incir', 'nar', 'badem', 'ceviz', 'kayisi', 
    'seftali', 'kiraz', 'visne', 'elma', 'armut', 'erik',
    'zeytin', 'antepfistigi', 'findik'
]

# Bağ evi sabit değerleri (legacy - backward compatibility)
BAG_EVI_MIN_ARAZI_BUYUKLUGU_DIKILI = 5000  # 0.5 hektar - Dikili alan minimum
BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK = 20000  # 2 hektar - Tarla alanı minimum  
BAG_EVI_MIN_ARAZI_BUYUKLUGU_ORTU_ALTI = 3000  # 0.3 hektar - Örtüaltı minimum
BAG_EVI_MAX_TABAN_ALANI = 75  # metrekare
BAG_EVI_MAX_TOPLAM_ALAN = 150  # metrekare

# Hesaplama parametreleri
MINIMUM_AGAC_SAYISI = 100  # Minimum ağaç adedi
MAKSIMUM_TABAN_ALANI = BAG_EVI_MAX_TABAN_ALANI

# Bağ evi kuralları sözlüğü (backward compatibility)
BAG_EVI_KURALLARI = {
    "dikili_min_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_DIKILI,
    "tarla_min_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK,
    "ortu_alti_min_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_ORTU_ALTI,
    "max_taban_alani": BAG_EVI_MAX_TABAN_ALANI,
    "max_toplam_alan": BAG_EVI_MAX_TOPLAM_ALAN
}

# Arazi tipi konfigürasyonları - Duplicate temizlenmiş versiyon
ARAZI_TIPI_KONFIGURASYONLARI = {
    "dikili_vasifli": {
        "min_dikili_alan": 5000,
        "min_tarla_alan": None,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["dikili_alani"],
        "kriter_mesaji": "Dikili alan kontrolü"
    },
    "tarla": {  
        "min_dikili_alan": None,
        "min_tarla_alan": None,  
        "min_toplam_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK,  # 20000
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],  
        "kriter_mesaji": "Tarla arazi alan kontrolü (min 20.000 m²)",
        "dual_function": False,
        "universal_function": True
    },
    "sera": {
        "min_dikili_alan": None,
        "min_tarla_alan": None,
        "min_toplam_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_ORTU_ALTI,  # 3000 - Sera ve örtü altı tarım için
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],
        "kriter_mesaji": "Sera ve örtü altı tarım alanı kontrolü (min 3.000 m²)",
        "universal_function": True
    },
    "Dikili vasıflı": {
        "min_dikili_alan": 5000,
        "min_tarla_alan": None,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["dikili_alani"],
        "kriter_mesaji": "Dikili alan kontrolü"
    },
    "Tarla": {  # 🔧 CLEAN VERSION - no duplicates, fixed field mapping
        "min_dikili_alan": None,
        "min_tarla_alan": None,  # Will use min_toplam_alan instead
        "min_toplam_alan": BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK,  # 20000
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],  # Fixed: use buyukluk_m2 not alan_m2
        "kriter_mesaji": "Tarla arazi alan kontrolü (min 20.000 m²)",
        "dual_function": False,
        "universal_function": True
    },
    "Örtüaltı tarım": {
        "min_dikili_alan": None,
        "min_tarla_alan": None,
        "min_toplam_alan": 3000,
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],
        "kriter_mesaji": "Örtüaltı tarım alanı kontrolü"
    },
    "Sera": {
        "min_dikili_alan": None,
        "min_tarla_alan": None,
        "min_toplam_alan": 5000,  # Cleaned up version
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],
        "kriter_mesaji": "Sera arazi alan kontrolü (min 5.000 m²)",
        "universal_function": True
    },
    "Tarla + herhangi bir dikili vasıflı": {
        "min_dikili_alan": 5000,
        "min_tarla_alan": 20000,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["dikili_alani", "tarla_alani"],
        "kriter_mesaji": "Dikili alan veya tarla alanı kontrolü (alternatif)",
        "dual_function": True,
        "varsayimsal_fonksiyon": "bag_evi_degerlendir_varsayimsal",
        "manuel_fonksiyon": "bag_evi_degerlendir_manuel_kontrol"
    },
    "Tarla + Zeytinlik": {
        "min_dikili_alan": None,
        "min_tarla_alan": 20000,
        "min_toplam_alan": 20001,
        "min_zeytinlik_alan": 1,
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["tarla_alani", "zeytinlik_alani"],
        "kriter_mesaji": "Tarla + Zeytinlik alan kontrolü",
        "dual_function": True,
        "varsayimsal_fonksiyon": "bag_evi_degerlendir_tarla_zeytinlik_varsayimsal",
        "manuel_fonksiyon": "bag_evi_degerlendir_tarla_zeytinlik_manuel"
    },
    "Zeytin ağaçlı + tarla": {
        "min_dikili_alan": None,
        "min_tarla_alan": 20000,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 10,
        "alan_tipleri": ["tarla_alani"],
        "agac_alan_anahtari": "zeytin_alani",
        "kriter_mesaji": "Zeytin ağaçlı tarla kontrolü",
        "dual_function": True,
        "varsayimsal_fonksiyon": "bag_evi_degerlendir_zeytin_tarla_varsayimsal",
        "manuel_fonksiyon": "bag_evi_degerlendir_zeytin_tarla_manuel"
    },
    "Zeytin ağaçlı + herhangi bir dikili vasıf": {
        "min_dikili_alan": 5000,
        "min_tarla_alan": None,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 100,  # %100 ağaç yeterlilik zorunluluğu
        "alan_tipleri": ["dikili_alani"],
        "agac_alan_anahtari": "zeytin_agac_adedi",
        "kriter_mesaji": "Zeytin ağaçlı dikili vasıf ve ağaç yeterlilik kontrolü",
        "dual_function": True,
        "varsayimsal_fonksiyon": "bag_evi_degerlendir_zeytin_dikili_varsayimsal",
        "manuel_fonksiyon": "bag_evi_degerlendir_zeytin_dikili_manuel"
    },
    "… Adetli Zeytin Ağacı bulunan tarla": {
        "min_dikili_alan": None,
        "min_tarla_alan": 20000,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 10,
        "alan_tipleri": ["tarla_alani"],
        "agac_alan_anahtari": "zeytin_agac_adedi",
        "kriter_mesaji": "Zeytin ağaçlı tarla kontrolü (adet belirtilmiş)",
        "universal_function": True
    },
    "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf": {
        "min_dikili_alan": 5000,
        "min_tarla_alan": None,
        "min_toplam_alan": None,
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 100,  # %100 ağaç yeterlilik zorunluluğu
        "alan_tipleri": ["dikili_alani"],
        "agac_alan_anahtari": "zeytin_agac_adedi",
        "kriter_mesaji": "Adetli zeytin ağaçlı dikili vasıf ve ağaç yeterlilik kontrolü",
        "universal_function": True
    },
    "Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı": {
        "min_dikili_alan": None,
        "min_tarla_alan": None,
        "min_toplam_alan": 20000,  # Ham toprak için 20.000 m² minimum alan şartı
        "zeytin_agac_kontrolu": False,
        "max_zeytin_yogunlugu": None,
        "alan_tipleri": ["buyukluk_m2"],  # Toplam alan kontrolü
        "kriter_mesaji": "Ham toprak arazi alan kontrolü (min 20.000 m²)",
        "universal_function": True
    }
}
