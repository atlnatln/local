# -*- coding: utf-8 -*-
"""
Response utilities for calculations
- sanitize_bag_evi_result: remove or hide debug / raw fields before returning to client
"""

from typing import Dict, Any, Iterable

# Keys considered debug / internal that shouldn't be exposed to end-users by default
DEFAULT_DEBUG_KEYS = [
    'debug_info',
    '_performance',
    'alan_detaylari',
    'agac_detaylari',
    'hotfix_applied',
    'clean_core_working',
    'uyari_mesajlari',  # optional: move to debug if you prefer (adjust as needed)
]

def sanitize_bag_evi_result(result: Dict[str, Any], expose_debug: bool = False, extra_debug_keys: Iterable[str] = ()) -> Dict[str, Any]:
    """
    Sanitize bag_evi calculation result before sending to client.

    - Eğer expose_debug False ise, DEFAULT_DEBUG_KEYS ve extra_debug_keys içindeki alanları
      result içinden alıp result['_debug'] altına taşıyarak istemciye doğrudan gösterilmesini engeller.
    - Eğer expose_debug True ise, result olduğu gibi döner.

    Not: Bu fonksiyon copy yapmaz; çağıran kod gerektiğinde deep copy alabilir.
    """
    if not isinstance(result, dict):
        return result

    if expose_debug:
        return result

    debug_keys = set(DEFAULT_DEBUG_KEYS) | set(extra_debug_keys)
    debug_bucket = {}

    for k in list(result.keys()):
        if k in debug_keys:
            debug_bucket[k] = result.pop(k)

    # Eğer zaten detay mesajı (HTML) varsa onu bırakıyoruz; ham yapılar debug altında saklanır.
    # _debug alanını da temizledik - ham veri gösterilmeyecek
    
    return result
