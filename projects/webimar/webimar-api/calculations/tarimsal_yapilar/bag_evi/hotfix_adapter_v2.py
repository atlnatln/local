"""
Bağ Evi API uyumluluk katmanı - HOTFIX V2 with modular core
Bu dosya mevcut bag_evi.py dosyasındaki config duplicate ve field mapping sorunlarını çözer
Modular core.py kullanır - temiz ve test edilebilir
"""

import logging
from typing import Dict, Any, List, Optional, Union
from . import core

logger = logging.getLogger(__name__)

def calculate_bag_evi_fixed(
    arazi_bilgileri: Dict[str, Any], 
    yapi_bilgileri: Dict[str, Any], 
    bag_evi_var_mi: bool = False, 
    manuel_kontrol_sonucu: Optional[str] = None
) -> Dict[str, Any]:
    """
    Bağ evi hesaplaması - Hotfix version V2 with modular core
    Config duplicate ve alan mapping sorunlarını düzeltir
    """
    
    # Modular core kullan - UPDATED to use universal function
    result = core.bag_evi_universal_degerlendir(
        arazi_bilgileri, 
        yapi_bilgileri, 
        bag_evi_var_mi, 
        manuel_kontrol_sonucu
    )
    
    # HOTFIX: Tarla alan mapping bug fix - YOK ARTIK! Core düzeldi
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', '')
    if arazi_vasfi == 'Tarla':
        tarla_alani = arazi_bilgileri.get('tarla_alani', 0)
        buyukluk_m2 = arazi_bilgileri.get('buyukluk_m2', 0)
        
        # Bug fix artık gerekli değil - clean core doğru field mapping kullanıyor
        # Field mapping bug: alan_m2 = 0 okuyor ama tarla_alani veya buyukluk_m2 doğru
        if (tarla_alani >= 20000 or buyukluk_m2 >= 20000) and result['izin_durumu'] == 'izin_verilemez':
            logger.warning("🔧 HOTFIX: Legacy bug still occurred, fixing...")
            result['izin_durumu'] = 'izin_verilebilir_varsayimsal'
            result['hotfix_applied'] = True
        elif buyukluk_m2 >= 20000 and result['izin_durumu'].startswith('izin_verilebilir'):
            logger.info("✅ CLEAN CORE: No hotfix needed - working correctly!")
            result['clean_core_working'] = True
    
    return result

# Backward compatibility - eski API
def bag_evi_degerlendir_fixed(arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi=False, manuel_kontrol_sonucu=None):
    """Backward compatible API wrapper"""
    return calculate_bag_evi_fixed(arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi, manuel_kontrol_sonucu)

# Alias for backward compatibility
bag_evi_degerlendir = bag_evi_degerlendir_fixed

# Main API function - expected by __init__.py
def bag_evi_hesapla(calculation_type, arazi_vasfi, alan_m2, 
                   agac_turler=None, agac_adedler=None, il=None, ilce=None,
                   mevcut_yapinin_alani=0, **kwargs):
    """
    Ana API uyumluluk fonksiyonu - legacy parametreler için
    
    Args:
        calculation_type: Hesaplama türü (3:Bağ Evi)
        arazi_vasfi: Arazi vasfı ID
        alan_m2: Arazi alanı (m²)
        agac_turler: Ağaç türleri listesi
        agac_adedler: Ağaç adetleri listesi
        il: İl adı
        ilce: İlçe adı
        mevcut_yapinin_alani: Mevcut yapı alanı (m²)
        **kwargs: Diğer parametreler
        
    Returns:
        dict: Hesaplama sonuçları
    """
    logger.debug("Bağ evi hesaplama başlatılıyor", extra={
        'calculation_type': calculation_type,
        'arazi_vasfi': arazi_vasfi,
        'alan_m2': alan_m2,
        'agac_count': len(agac_turler) if agac_turler else 0
    })
    
    # Backwards-compatible adapter: legacy positional args -> new core dict contract
    arazi_bilgileri = {
        'ana_vasif': arazi_vasfi if isinstance(arazi_vasfi, str) else kwargs.get('arazi_tipi', 'Dikili vasıflı'),
        'buyukluk_m2': float(alan_m2 or 0),
        'dikili_alani': float(kwargs.get('dikili_alani', 0)),
        'tarla_alani': float(kwargs.get('tarla_alani', 0)),
        'zeytinlik_alani': float(kwargs.get('zeytinlik_alani', 0)),
        'zeytin_agac_adedi': int(kwargs.get('zeytin_agac_adedi') or 0),
        'tapu_zeytin_agac_adedi': int(kwargs.get('tapu_zeytin_agac_adedi') or 0),
        'mevcut_zeytin_agac_adedi': int(kwargs.get('mevcut_zeytin_agac_adedi') or 0),
        'il': il,
        'ilce': ilce
    }

    yapi_bilgileri = {
        'agac_turler': agac_turler or [],
        'agac_adedler': agac_adedler or [],
        'mevcut_yapinin_alani': mevcut_yapinin_alani or 0
    }

    result = core.bag_evi_universal_degerlendir(
        arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi=kwargs.get('bag_evi_var_mi', False),
        manuel_kontrol_sonucu=kwargs.get('manuel_kontrol_sonucu')
    )
    
    logger.info("Bağ evi hesaplama tamamlandı", extra={
        'success': result.get('success', False),
        'toplam_alan': result.get('toplam_alan'),
        'warning_count': len(result.get('uyari_mesajlari', []))
    })
    
    return result
