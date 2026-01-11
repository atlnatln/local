# -*- coding: utf-8 -*-
"""
Unified Bag Evi API Adapter
Single entry point for all bag evi calculations with proper contract validation
"""

import logging
from typing import Dict, Any, List, Optional, Union
from . import core
from .performance import performance_monitor

logger = logging.getLogger(__name__)

@performance_monitor
def bag_evi_unified_calculate(
    request_data: Dict[str, Any], 
    legacy_format: bool = False
) -> Dict[str, Any]:
    """
    Unified bag evi calculation endpoint
    
    Args:
        request_data: Normalized request data
        legacy_format: If True, returns legacy format for backward compatibility
        
    Returns:
        Dict containing calculation results in requested format
    """
    logger.info("🎯 Unified bag evi calculation started")
    
    try:
        # Extract standardized parameters
        arazi_bilgileri = _extract_arazi_bilgileri(request_data)
        yapi_bilgileri = _extract_yapi_bilgileri(request_data)
        manuel_kontrol = request_data.get('manuel_kontrol_sonucu')
        
        # Validate required parameters
        _validate_required_parameters(arazi_bilgileri, yapi_bilgileri)
        
        # Execute core calculation
        core_result = core.bag_evi_universal_degerlendir(
            arazi_bilgileri, 
            yapi_bilgileri,
            bag_evi_var_mi=request_data.get('bag_evi_var_mi', False),
            manuel_kontrol_sonucu=manuel_kontrol,
            raw_data=request_data  # Raw data'yı dikili validasyon için geç
        )
        
        # Format response based on legacy requirement
        if legacy_format:
            return _format_legacy_response(core_result)
        else:
            return _format_standard_response(core_result)
            
    except Exception as e:
        logger.error(f"❌ Unified calculation failed: {e}")
        error_result = {
            'success': False,
            'error': str(e),
            'izin_durumu': 'HATA_OLUSTU'
        }
        
        if legacy_format:
            return _format_legacy_response(error_result)
        else:
            return _format_standard_response(error_result)

def _extract_arazi_bilgileri(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize arazi bilgileri from request"""
    # Handle different input formats
    if 'arazi_bilgileri' in request_data:
        return request_data['arazi_bilgileri']
    
    # Legacy format extraction
    arazi_data = {}
    
    # Area mapping
    if 'alan_m2' in request_data:
        arazi_data['buyukluk_m2'] = float(request_data['alan_m2'])
    elif 'arazi_alani' in request_data:
        arazi_data['buyukluk_m2'] = float(request_data['arazi_alani'])
    
    # Vasif mapping
    if 'arazi_vasfi' in request_data:
        if isinstance(request_data['arazi_vasfi'], str):
            arazi_data['ana_vasif'] = request_data['arazi_vasfi']
        else:
            # Numeric arazi vasfi - map to string
            vasif_map = {1: 'tarla', 2: 'ortu_alti', 3: 'sera', 4: 'bag', 5: 'dikili'}
            arazi_data['ana_vasif'] = vasif_map.get(request_data['arazi_vasfi'], 'dikili_vasifli')
    
    # Additional area fields
    for field in ['dikili_alani', 'tarla_alani', 'zeytinlik_alani']:
        if field in request_data:
            arazi_data[field] = float(request_data[field])
    
    # Location info
    for field in ['il', 'ilce']:
        if field in request_data:
            arazi_data[field] = request_data[field]
    
    return arazi_data

def _extract_yapi_bilgileri(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and normalize yapi bilgileri from request"""
    if 'yapi_bilgileri' in request_data:
        return request_data['yapi_bilgileri']
    
    yapi_data = {}
    
    # Handle different mevcut yapi alan field names
    for field_name in ['mevcut_yapi_alani', 'mevcut_yapinin_alani', 'existing_building_area']:
        if field_name in request_data:
            yapi_data['mevcut_yapi_alani'] = float(request_data[field_name])
            break
    
    return yapi_data

def _validate_required_parameters(arazi_bilgileri: Dict, yapi_bilgileri: Dict) -> None:
    """Validate that required parameters are present"""
    if not arazi_bilgileri.get('buyukluk_m2'):
        raise ValueError("Arazi alanı (buyukluk_m2) gereklidir")
    
    if not arazi_bilgileri.get('ana_vasif'):
        raise ValueError("Arazi vasfı (ana_vasif) gereklidir")
    
    # Ensure numeric values are valid
    if arazi_bilgileri['buyukluk_m2'] <= 0:
        raise ValueError("Arazi alanı 0'dan büyük olmalıdır")

def _format_legacy_response(core_result: Dict[str, Any]) -> Dict[str, Any]:
    """Format response for legacy API compatibility"""
    return {
        'html_message': core_result.get('detay_mesaji', ''),
        'calculation_details': {
            'success': core_result.get('success', False),
            'izin_durumu': core_result.get('izin_durumu', ''),
            'alan_detaylari': core_result.get('alan_detaylari', {}),
            'agac_detaylari': core_result.get('agac_detaylari', {}),
            'debug_info': core_result.get('debug_info', {})
        },
        '_performance': core_result.get('_performance', {}),
        '_unified_adapter': True
    }

def _format_standard_response(core_result: Dict[str, Any]) -> Dict[str, Any]:
    """Format response for standard API"""
    return {
        **core_result,
        '_api_version': '2.0',
        '_unified_adapter': True
    }

# Legacy compatibility functions
def bag_evi_hesapla(*args, **kwargs) -> Dict[str, Any]:
    """Legacy bag_evi_hesapla wrapper"""
    logger.warning("🔄 Using legacy bag_evi_hesapla - consider migrating to unified adapter")
    
    # Convert positional args to request_data dict
    if args:
        request_data = _convert_legacy_args_to_dict(*args, **kwargs)
    else:
        request_data = kwargs
    
    return bag_evi_unified_calculate(request_data, legacy_format=True)

def bag_evi_degerlendir(*args, **kwargs) -> Dict[str, Any]:
    """Legacy bag_evi_degerlendir wrapper"""
    logger.warning("🔄 Using legacy bag_evi_degerlendir - consider migrating to unified adapter")
    
    if args:
        request_data = args[0] if args else {}
    else:
        request_data = kwargs
    
    result = bag_evi_unified_calculate(request_data, legacy_format=False)
    
    # Legacy format expects specific fields
    return {
        'sonuc': result.get('izin_durumu', ''),
        'detaylar': result.get('alan_detaylari', {}),
        **result
    }

def _convert_legacy_args_to_dict(*args, **kwargs) -> Dict[str, Any]:
    """Convert legacy positional arguments to unified dict format"""
    request_data = {}
    
    if len(args) >= 3:
        # bag_evi_hesapla(calculation_type, arazi_vasfi, alan_m2, ...)
        request_data['calculation_type'] = args[0]
        request_data['arazi_vasfi'] = args[1]
        request_data['alan_m2'] = args[2]
        
        if len(args) >= 4:
            request_data['agac_turler'] = args[3]
        if len(args) >= 5:
            request_data['agac_adedler'] = args[4]
    
    # Merge kwargs
    request_data.update(kwargs)
    
    return request_data
