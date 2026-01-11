"""
Bağ Evi Hesaplama Modülü
=======================

Modüler bağ evi hesaplama sistemi. 

Modüller:
- config.py: Sabitler ve konfigürasyon
- core.py: Ana hesaplama mantığı  
- messages.py: HTML mesaj üretimi
- hotfix_adapter_v2.py: Legacy uyumluluk katmanı

Kullanım:
    from calculations.tarimsal_yapilar.bag_evi import bag_evi_degerlendir
    
    # veya
    from calculations.tarimsal_yapilar.bag_evi.core import bag_evi_universal_degerlendir
"""

# Ana API fonksiyonlarını dışarı aktar
from .hotfix_adapter_v2 import bag_evi_degerlendir
from .core import bag_evi_universal_degerlendir, _universal_zeytin_agac_kontrolleri
from .config import (
    BAG_EVI_MIN_ARAZI_BUYUKLUGU_DIKILI,
    BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK,
    BAG_EVI_MAX_TABAN_ALANI,
    BAG_EVI_MAX_TOPLAM_ALAN,
    ARAZI_TIPI_KONFIGURASYONLARI,
    BAG_EVI_KURALLARI  # backward compatibility
)

__all__ = [
    'bag_evi_degerlendir',
    'bag_evi_universal_degerlendir', 
    '_universal_zeytin_agac_kontrolleri',  # Shared utility function
    'BAG_EVI_MIN_ARAZI_BUYUKLUGU_DIKILI',
    'BAG_EVI_MIN_ARAZI_BUYUKLUGU_MUTLAK',
    'BAG_EVI_MAX_TABAN_ALANI',
    'BAG_EVI_MAX_TOPLAM_ALAN',
    'ARAZI_TIPI_KONFIGURASYONLARI',
    'BAG_EVI_KURALLARI'  # backward compatibility
]
