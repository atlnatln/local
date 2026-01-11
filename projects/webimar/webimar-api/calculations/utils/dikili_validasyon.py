# -*- coding: utf-8 -*-
"""
Dikili Arazi Validasyon Modülü
Ağaç türleri ve minimum sayı gereksinimlerini kontrol eder
"""

import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Dikili arazi ağaç sayıları tablosu - dekara düşen minimum adet
DIKILI_AGAC_SAYILARI = {
    1: {"ad": "Kestane", "normal": 20, "bodur": None, "yari_bodur": None},
    2: {"ad": "Harnup", "normal": 21, "bodur": None, "yari_bodur": None},
    3: {"ad": "İncir (Kurutmalık)", "normal": 16, "bodur": None, "yari_bodur": None},
    4: {"ad": "İncir (Taze)", "normal": 18, "bodur": None, "yari_bodur": None},
    5: {"ad": "Armut", "normal": 20, "bodur": 220, "yari_bodur": 70},
    6: {"ad": "Elma", "normal": 20, "bodur": 220, "yari_bodur": 80},
    7: {"ad": "Trabzon Hurması", "normal": 40, "bodur": None, "yari_bodur": None},
    8: {"ad": "Kiraz", "normal": 25, "bodur": 50, "yari_bodur": 33},
    9: {"ad": "Ayva", "normal": 24, "bodur": 100, "yari_bodur": None},
    10: {"ad": "Nar", "normal": 40, "bodur": None, "yari_bodur": None},
    11: {"ad": "Erik", "normal": 18, "bodur": 100, "yari_bodur": 34},
    12: {"ad": "Kayısı", "normal": 16, "bodur": 50, "yari_bodur": 30},
    13: {"ad": "Zerdali", "normal": 20, "bodur": 50, "yari_bodur": 30},
    14: {"ad": "Muşmula", "normal": 25, "bodur": None, "yari_bodur": None},
    15: {"ad": "Yenidünya", "normal": 21, "bodur": None, "yari_bodur": None},
    16: {"ad": "Şeftali", "normal": 40, "bodur": 100, "yari_bodur": 67},
    17: {"ad": "Vişne", "normal": 18, "bodur": 60, "yari_bodur": 40},
    18: {"ad": "Ceviz", "normal": 10, "bodur": None, "yari_bodur": None},
    19: {"ad": "Dut", "normal": 20, "bodur": None, "yari_bodur": None},
    20: {"ad": "Üvez", "normal": 40, "bodur": None, "yari_bodur": None},
    21: {"ad": "Ünnap", "normal": 40, "bodur": None, "yari_bodur": None},
    22: {"ad": "Kızılcık", "normal": 40, "bodur": None, "yari_bodur": None},
    23: {"ad": "Limon", "normal": 21, "bodur": None, "yari_bodur": None},
    24: {"ad": "Portakal", "normal": 27, "bodur": None, "yari_bodur": None},
    25: {"ad": "Turunç", "normal": 27, "bodur": None, "yari_bodur": None},
    26: {"ad": "Altıntop", "normal": 21, "bodur": None, "yari_bodur": None},
    27: {"ad": "Mandarin", "normal": 27, "bodur": None, "yari_bodur": None},
    28: {"ad": "Avokado", "normal": 21, "bodur": None, "yari_bodur": None},
    29: {"ad": "Fındık (Düz)", "normal": 30, "bodur": None, "yari_bodur": None},
    30: {"ad": "Fındık (Eğimli)", "normal": 50, "bodur": None, "yari_bodur": None},
    31: {"ad": "Gül", "normal": 300, "bodur": None, "yari_bodur": 750},
    32: {"ad": "Çay", "normal": 1800, "bodur": None, "yari_bodur": None},
    33: {"ad": "Kivi", "normal": 60, "bodur": None, "yari_bodur": None},
    34: {"ad": "Böğürtlen", "normal": 220, "bodur": None, "yari_bodur": None},
    35: {"ad": "Ahududu", "normal": 600, "bodur": None, "yari_bodur": None},
    36: {"ad": "Likapa", "normal": 260, "bodur": None, "yari_bodur": None},
    37: {"ad": "Muz (Örtü altı)", "normal": 170, "bodur": None, "yari_bodur": None},
    38: {"ad": "Muz (Açıkta)", "normal": 200, "bodur": None, "yari_bodur": None},
    39: {"ad": "Kuşburnu", "normal": 111, "bodur": None, "yari_bodur": None},
    40: {"ad": "Mürver", "normal": 85, "bodur": None, "yari_bodur": None},
    41: {"ad": "Frenk Üzümü", "normal": 220, "bodur": None, "yari_bodur": None},
    42: {"ad": "Bektaşi Üzümü", "normal": 220, "bodur": None, "yari_bodur": None},
    43: {"ad": "Aronya", "normal": 170, "bodur": None, "yari_bodur": None},
}

def validate_dikili_arazi(
    alan_dekar: float,
    agac_turu_id: int,
    agac_sayisi: int,
    agac_cesidi: str = "normal"
) -> Tuple[bool, str, Dict]:
    """
    Dikili arazi kriterlerini kontrol eder
    
    Args:
        alan_dekar: Arazi alanı (dekar)
        agac_turu_id: Ağaç türü ID'si (1-43)
        agac_sayisi: Toplam ağaç sayısı
        agac_cesidi: "normal", "bodur", "yari_bodur"
    
    Returns:
        Tuple[bool, str, Dict]: (is_valid, message, details)
    """
    
    # Ağaç türü kontrolü
    if agac_turu_id not in DIKILI_AGAC_SAYILARI:
        return False, f"Geçersiz ağaç türü ID: {agac_turu_id}", {}
    
    agac_info = DIKILI_AGAC_SAYILARI[agac_turu_id]
    agac_adi = agac_info["ad"]
    
    # Çeşit kontrolü
    if agac_cesidi not in ["normal", "bodur", "yari_bodur"]:
        agac_cesidi = "normal"
    
    min_adet_per_dekar = agac_info.get(agac_cesidi)
    
    # Bu çeşit bu ağaç türü için mevcut mu?
    if min_adet_per_dekar is None:
        # Fallback to normal
        min_adet_per_dekar = agac_info["normal"]
        agac_cesidi = "normal"
    
    # Gereken minimum ağaç sayısı
    gereken_min_sayisi = min_adet_per_dekar * alan_dekar
    
    # Dekara düşen mevcut ağaç sayısı
    mevcut_dekar_basina = agac_sayisi / alan_dekar if alan_dekar > 0 else 0
    
    is_valid = agac_sayisi >= gereken_min_sayisi
    
    details = {
        "agac_adi": agac_adi,
        "agac_cesidi": agac_cesidi,
        "alan_dekar": alan_dekar,
        "mevcut_agac_sayisi": agac_sayisi,
        "min_adet_per_dekar": min_adet_per_dekar,
        "gereken_min_sayisi": gereken_min_sayisi,
        "mevcut_dekar_basina": round(mevcut_dekar_basina, 1),
        "eksik_agac_sayisi": max(0, gereken_min_sayisi - agac_sayisi)
    }
    
    if is_valid:
        message = f"✅ {agac_adi} ({agac_cesidi}) dikili arazi kriterleri karşılanıyor"
    else:
        # Kullanıcı dostu hata mesajı
        eksik_sayi = details['eksik_agac_sayisi']
        mevcut_dekar = details['mevcut_dekar_basina']
        min_dekar = details['min_adet_per_dekar']
        
        if eksik_sayi <= 10:
            message = (f"🌱 {agac_adi} ({agac_cesidi}) ağaçlarınız neredeyse yeterli! "
                      f"Sadece {eksik_sayi} adet daha dikmeniz gerekiyor.")
        elif eksik_sayi <= 50:
            message = (f"🌳 {agac_adi} ({agac_cesidi}) ağaç sayınız biraz düşük. "
                      f"{eksik_sayi} adet daha ağaç dikerek kriterleri sağlayabilirsiniz.")
        else:
            message = (f"🌲 {agac_adi} ({agac_cesidi}) için daha fazla ağaca ihtiyacınız var. "
                      f"Mevcut {mevcut_dekar:.1f} adet/dekar, gereken {min_dekar} adet/dekar. "
                      f"Toplam {eksik_sayi} adet ağaç ekmelisiniz.")
    
    logger.info(f"Dikili validasyon - {agac_adi}: {is_valid} - {message}")
    
    return is_valid, message, details

def validate_multiple_agac_turleri(
    alan_dekar: float,
    agac_bilgileri: List[Dict]
) -> Tuple[bool, List[str], Dict]:
    """
    Birden fazla ağaç türü için dikili validasyon
    
    Args:
        alan_dekar: Toplam arazi alanı (dekar)
        agac_bilgileri: [{"agac_turu_id": int, "agac_sayisi": int, "agac_cesidi": str, "alan_orani": float}]
    
    Returns:
        Tuple[bool, List[str], Dict]: (all_valid, messages, detailed_results)
    """
    
    # Aynı ağaç türlerinin toplamını hesapla
    agac_turu_toplamlari = {}
    
    for agac in agac_bilgileri:
        agac_turu_id = agac["agac_turu_id"]
        agac_sayisi = agac["agac_sayisi"]
        agac_cesidi = agac.get("agac_cesidi", "normal")
        alan_orani = agac.get("alan_orani", 1.0)
        
        key = (agac_turu_id, agac_cesidi)
        if key in agac_turu_toplamlari:
            agac_turu_toplamlari[key]['sayi'] += agac_sayisi
            # Alan oranını da güncelle (ortalama al)
            agac_turu_toplamlari[key]['alan_orani'] = (
                agac_turu_toplamlari[key]['alan_orani'] + alan_orani
            ) / 2
        else:
            agac_turu_toplamlari[key] = {
                'sayi': agac_sayisi,
                'alan_orani': alan_orani,
                'agac_adi': agac.get("agac_adi", f"ID:{agac_turu_id}")
            }
    
    # Toplanmış ağaç türleri için validasyon yap
    results = []
    messages = []
    all_valid = True
    
    for (agac_turu_id, agac_cesidi), toplam_bilgi in agac_turu_toplamlari.items():
        agac_alan_dekar = alan_dekar * toplam_bilgi['alan_orani']
        
        is_valid, message, details = validate_dikili_arazi(
            alan_dekar=agac_alan_dekar,
            agac_turu_id=agac_turu_id,
            agac_sayisi=toplam_bilgi['sayi'],
            agac_cesidi=agac_cesidi
        )
        
        results.append({
            "agac_turu_id": agac_turu_id,
            "is_valid": is_valid,
            "message": message,
            "details": details,
            "toplam_sayi": toplam_bilgi['sayi']
        })
        
        messages.append(message)
        
        if not is_valid:
            all_valid = False
    
    summary = {
        "toplam_kontrol_edilen": len(agac_turu_toplamlari),
        "gecerli_olanlar": len([r for r in results if r["is_valid"]]),
        "gecersiz_olanlar": len([r for r in results if not r["is_valid"]]),
        "all_valid": all_valid,
        "results": results,
        "toplam_agac_sayisi": sum([r["toplam_sayi"] for r in results])
    }
    
    return all_valid, messages, summary

def get_agac_turleri_listesi() -> Dict[int, Dict]:
    """
    Mevcut ağaç türlerini döndürür
    
    Returns:
        Dict: {id: {ad, normal, bodur, yari_bodur}}
    """
    return DIKILI_AGAC_SAYILARI.copy()

def calculate_required_trees(
    alan_dekar: float,
    agac_turu_id: int,
    agac_cesidi: str = "normal"
) -> Tuple[int, Dict]:
    """
    Belirtilen alan için gerekli ağaç sayısını hesaplar
    
    Args:
        alan_dekar: Alan (dekar)
        agac_turu_id: Ağaç türü ID
        agac_cesidi: Ağaç çeşidi
    
    Returns:
        Tuple[int, Dict]: (required_count, details)
    """
    
    if agac_turu_id not in DIKILI_AGAC_SAYILARI:
        return 0, {"error": f"Geçersiz ağaç türü ID: {agac_turu_id}"}
    
    agac_info = DIKILI_AGAC_SAYILARI[agac_turu_id]
    min_adet_per_dekar = agac_info.get(agac_cesidi)
    
    if min_adet_per_dekar is None:
        min_adet_per_dekar = agac_info["normal"]
        agac_cesidi = "normal"
    
    required_count = int(min_adet_per_dekar * alan_dekar)
    
    details = {
        "agac_adi": agac_info["ad"],
        "agac_cesidi": agac_cesidi,
        "alan_dekar": alan_dekar,
        "min_adet_per_dekar": min_adet_per_dekar,
        "required_count": required_count
    }
    
    return required_count, details


def find_agac_by_name(agac_adi: str) -> Optional[Tuple[int, Dict]]:
    """
    Ağaç adından veya ID'sinden ID ve bilgileri bulur (case-insensitive)
    
    Args:
        agac_adi: Ağaç adı (string) veya ID (string/int)
    
    Returns:
        Optional[Tuple[int, Dict]]: (agac_id, agac_info) veya None
    """
    agac_adi_str = str(agac_adi).strip()
    
    # Önce numeric ID kontrolü yap
    try:
        agac_id = int(agac_adi_str)
        if agac_id in DIKILI_AGAC_SAYILARI:
            return agac_id, DIKILI_AGAC_SAYILARI[agac_id]
    except ValueError:
        pass
    
    # String isme göre arama
    agac_adi_lower = agac_adi_str.lower()
    
    # Tam eşleşme ara
    for agac_id, agac_info in DIKILI_AGAC_SAYILARI.items():
        if agac_info["ad"].lower() == agac_adi_lower:
            return agac_id, agac_info
    
    # Kısmi eşleşme ara (ağaç adı içinde geçiyorsa)
    for agac_id, agac_info in DIKILI_AGAC_SAYILARI.items():
        agac_tam_adi = agac_info["ad"].lower()
        if agac_adi_lower in agac_tam_adi or agac_tam_adi in agac_adi_lower:
            return agac_id, agac_info
    
    return None


def validate_dikili_arazi_by_name(
    agac_adi: str,
    agac_sayisi: int,
    alan_dekar: float,
    agac_cesidi: str = "normal"
) -> Dict[str, Any]:
    """
    Ağaç adı ile dikili validasyon (string-based)
    
    Args:
        agac_adi: Ağaç türü adı (string)
        agac_sayisi: Toplam ağaç sayısı
        alan_dekar: Arazi alanı (dekar)
        agac_cesidi: "normal", "bodur", "yari_bodur"
    
    Returns:
        Dict: Validasyon sonucu
    """
    
    # Ağaç türünü bul
    agac_match = find_agac_by_name(agac_adi)
    if not agac_match:
        return {
            'gecerli': False,
            'mesaj': f'Tanınmayan ağaç türü: {agac_adi}',
            'detay': {
                'agac_turu': agac_adi,
                'durum': 'Geçersiz ağaç türü'
            }
        }
    
    agac_id, agac_info = agac_match
    
    # ID-based validasyon yap
    is_valid, message, details = validate_dikili_arazi(
        alan_dekar=alan_dekar,
        agac_turu_id=agac_id,
        agac_sayisi=agac_sayisi,
        agac_cesidi=agac_cesidi
    )
    
    return {
        'gecerli': is_valid,
        'mesaj': message,
        'detay': details,
        'agac_turu_id': agac_id,
        'agac_turu_adi': agac_info["ad"],
        'minimum_gereksinim': details.get('min_adet_per_dekar', 0),
        'mevcut_sayisi': agac_sayisi,
        'alan_dekar': alan_dekar
    }
