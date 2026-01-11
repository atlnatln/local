"""
Su kısıtı olan bölgelerde büyükbaş hayvancılık işletmesi yapımı yasağı kontrolü.

Bu modül, belirli il ve ilçelerde büyükbaş hayvancılık işletmesi tesisi için 
yapılacak tesis müracaatlarının ret edilmesi gereken bölgeleri kontrol eder.
"""

# Su kısıtı olan il ve ilçelerin listesi
WATER_RESTRICTED_AREAS = [
    {"province": "AKSARAY", "district": "AKSARAY"},        # Merkez = il adı
    {"province": "AKSARAY", "district": "ESKİL"},
    {"province": "AKSARAY", "district": "GÜLAĞAÇ"},
    {"province": "AKSARAY", "district": "GÜZELYURT"},
    {"province": "AKSARAY", "district": "SULTANHANI"},
    {"province": "ANKARA", "district": "BALA"},
    {"province": "ANKARA", "district": "GÖLBAŞI"},
    {"province": "ANKARA", "district": "HAYMANA"},
    {"province": "ANKARA", "district": "ŞEREFLİKOÇHİSAR"},
    {"province": "ESKİŞEHİR", "district": "ALPU"},
    {"province": "ESKİŞEHİR", "district": "BEYLİKOVA"},
    {"province": "ESKİŞEHİR", "district": "ÇİFTELER"},
    {"province": "ESKİŞEHİR", "district": "MAHMUDİYE"},
    {"province": "ESKİŞEHİR", "district": "MİHALIÇÇIK"},
    {"province": "ESKİŞEHİR", "district": "SİVRİHİSAR"},
    {"province": "HATAY", "district": "KUMLU"},
    {"province": "HATAY", "district": "REYHANLI"},
    {"province": "KARAMAN", "district": "AYRANCI"},
    {"province": "KARAMAN", "district": "KARAMAN"},        # Merkez = il adı
    {"province": "KARAMAN", "district": "KAZIMKARABEKİR"},
    {"province": "KIRŞEHİR", "district": "BOZTEPE"},
    {"province": "KIRŞEHİR", "district": "MUCUR"},
    {"province": "KONYA", "district": "AKÖREN"},
    {"province": "KONYA", "district": "AKŞEHİR"},
    {"province": "KONYA", "district": "ALTINEKİN"},
    {"province": "KONYA", "district": "CİHANBEYLİ"},
    {"province": "KONYA", "district": "ÇUMRA"},
    {"province": "KONYA", "district": "DERBENT"},
    {"province": "KONYA", "district": "DOĞANHİSAR"},
    {"province": "KONYA", "district": "EMİRGAZİ"},
    {"province": "KONYA", "district": "EREĞLİ"},
    {"province": "KONYA", "district": "GÜNEYSINIR"},
    {"province": "KONYA", "district": "HALKAPINAR"},
    {"province": "KONYA", "district": "KADINHANI"},
    {"province": "KONYA", "district": "KARAPINAR"},
    {"province": "KONYA", "district": "KARATAY"},
    {"province": "KONYA", "district": "KULU"},
    {"province": "KONYA", "district": "MERAM"},
    {"province": "KONYA", "district": "SARAYÖNÜ"},
    {"province": "KONYA", "district": "SELÇUKLU"},
    {"province": "KONYA", "district": "TUZLUKÇU"},
    {"province": "MARDİN", "district": "ARTUKLU"},
    {"province": "MARDİN", "district": "DERİK"},
    {"province": "MARDİN", "district": "KIZILTEPE"},
    {"province": "NEVŞEHİR", "district": "ACIGÖL"},
    {"province": "NEVŞEHİR", "district": "DERİNKUYU"},
    {"province": "NEVŞEHİR", "district": "GÜLŞEHİR"},
    {"province": "NİĞDE", "district": "ALTUNHİSAR"},
    {"province": "NİĞDE", "district": "BOR"},
    {"province": "NİĞDE", "district": "ÇİFTLİK"},
    {"province": "NİĞDE", "district": "NİĞDE"},           # Merkez = il adı
    {"province": "ŞANLIURFA", "district": "VİRANŞEHİR"},
]

def is_water_restricted_area(province: str, district: str) -> bool:
    """
    Verilen il ve ilçenin su kısıtı olan bölgede olup olmadığını kontrol eder.
    
    Args:
        province: İl adı (büyük harflerle)
        district: İlçe adı (büyük harflerle)
    
    Returns:
        bool: Su kısıtı bölgesindeyse True, değilse False
    """
    if not province or not district:
        return False
    
    # Büyük harfe çevir
    province = province.upper().strip()
    district = district.upper().strip()
    
    # Listede ara
    for area in WATER_RESTRICTED_AREAS:
        if area["province"] == province and area["district"] == district:
            return True
    
    return False

def get_water_restriction_message() -> str:
    """
    Su kısıtı uyarı mesajını döndürür.
    """
    return ("📍 Haritada işaretlediğiniz nokta su kısıtı olan yerler arasında olup "
            "büyükbaş hayvancılık işletmesi tesisi için yeni yapılacak tesis "
            "müracaatları ret edilmektedir.")

def is_livestock_calculation_type(calculation_type: str) -> bool:
    """
    Hesaplama türünün büyükbaş hayvancılık olup olmadığını kontrol eder.
    
    Args:
        calculation_type: Hesaplama türü
    
    Returns:
        bool: Büyükbaş hayvancılık hesaplamasıysa True
    """
    livestock_types = [
        'sut-sigirciligi',
        'besi-sigirciligi',
        'buyukbas',
        'sut_sigirciligi',
        'besi_sigirciligi'
    ]
    
    return calculation_type.lower().replace('_', '-') in livestock_types