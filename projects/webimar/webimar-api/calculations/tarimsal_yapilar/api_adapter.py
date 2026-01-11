# -*- coding: utf-8 -*-
"""
API Adapter for bag_evi module
Normalizes input from views and handles backwards compatibility
"""

from . import config, bag_evi

def bag_evi_degerlendir_adapter(request_data: dict):
    """
    API adapter: normalizes frontend payload to backend expected format
    
    Args:
        request_data: Raw request data from views
    
    Returns:
        dict: bag_evi calculation result
    """
    
    # Normalize incoming payload
    alan_m2 = float(request_data.get('alan_m2') or request_data.get('buyukluk_m2') or 0)
    arazi_vasfi = request_data.get('arazi_vasfi') or request_data.get('arazi_tipi', '')
    
    arazi_bilgileri = {
        'ana_vasif': arazi_vasfi,
        'buyukluk_m2': alan_m2,
        'dikili_alani': float(request_data.get('dikili_alani') or request_data.get('bag_alani_m2') or 0),
        'tarla_alani': float(request_data.get('tarla_alani') or 0),
        'zeytinlik_alani': float(request_data.get('zeytinlik_alani') or 0),
        'zeytin_agac_adedi': int(request_data.get('zeytin_agac_adedi') or 0),
        'tapu_zeytin_agac_adedi': int(request_data.get('tapu_zeytin_agac_adedi') or 0),
        'mevcut_zeytin_agac_adedi': int(request_data.get('mevcut_zeytin_agac_adedi') or 0),
        'buyuk_ova_icinde': bool(request_data.get('buyuk_ova_icinde', False))
    }
    
    # CRITICAL FIX: Smart field mapping based on arazi type
    if arazi_vasfi == 'Tarla':
        # For Tarla: use alan_m2 (due to config duplicate issue)
        arazi_bilgileri['alan_m2'] = alan_m2
    elif arazi_vasfi in ['Dikili vasıflı', 'Bağ vasfı']:
        # For Dikili: use dikili_alani field, fallback to total area
        if arazi_bilgileri['dikili_alani'] <= 0:
            arazi_bilgileri['dikili_alani'] = alan_m2
    
    yapi_bilgileri = {
        'taban_alani_m2': config.BAG_EVI_MAX_TABAN_ALANI,
        'toplam_alan_m2': config.BAG_EVI_MAX_TOPLAM_ALAN
    }
    
    manuel_kontrol_sonucu = request_data.get('manuel_kontrol_sonucu')
    bag_evi_var_mi = request_data.get('bag_evi_var_mi', False)
    
    # Call core
    return bag_evi.bag_evi_degerlendir(
        arazi_bilgileri, 
        yapi_bilgileri, 
        bag_evi_var_mi=bag_evi_var_mi, 
        manuel_kontrol_sonucu=manuel_kontrol_sonucu
    )
