"""
Bu paket, çeşitli arazi vasıfları için geçerli olan genel yapılaşma 
kurallarını ve mantığını içerir.

Kapsanan arazi vasıflarına örnekler:
- Tarla vasıflı + herhangi bir dikili vasıflı
- Sadece Dikili vasıflı
- Zeytin ağaçlı + tarla
- Zeytin ağaçlı + herhangi bir dikili vasıf
- Adetli Zeytin Ağacı bulunan tarla
- Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf
- Mera vasıflı
- Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı

Not: Zeytin ağaçlarının bulunduğu arazilerde, zeytincilik mevzuatının 
gereklilikleri de ayrıca dikkate alınmalıdır.
"""

from .constants import (
    GENEL_YAPI_TURLERI_LISTESI,
    ARAZI_TIPLERI,
    YAPI_TURLERI,
    ARAZI_TIPI_ID_TO_AD,
    YAPI_TURU_ID_TO_AD,
    ARAZI_TIPI_AD_TO_ID,
    YAPI_TURU_AD_TO_ID
)
from .ana_modul import genel_vasif_kural_kontrolu
from .sera import hesapla_sera_yapilasma_kurallari, sera_projesi_bilgilendirme
from .tarimsal_silo import (silo_projesi_degerlendir, hesapla_silo_yapilasma_kurallari, 
                           silo_projesi_bilgilendirme, hububat_silo_degerlendir)
from .genel_kurallar import genel_minimum_arazi_kurali
from .bag_evi import bag_evi_degerlendir, BAG_EVI_KURALLARI
from .hara import hara_tesisi_degerlendir
from .ipek_bocekciligi import hesapla_ipek_bocekciligi_kurallari
from .evcil_hayvan import evcil_hayvan_tesisi_degerlendir
from .buyukbas import sut_sigiri_degerlendir, besi_sigiri_degerlendir
from .aricilik import aricilik_degerlendir
from .kanatli import (yumurtaci_tavuk_degerlendir, etci_tavuk_degerlendir,
                     gezen_tavuk_degerlendir, hindi_degerlendir, kaz_ordek_degerlendir)
from .kucukbas import kucukbas_degerlendir
from .soguk_hava_deposu import calculate_soguk_hava_deposu
from .meyve_sebze_kurutma import meyve_sebze_kurutma_degerlendir
from .lisansli_depo import lisansli_depo_degerlendir, lisansli_depo_genel_bilgilendirme
from .mantar_tesisi import mantar_tesisi_degerlendir
from .kurutma_tesisi import kurutma_tesisi_degerlendir
from .su_kuyulari import su_kuyulari_degerlendir
from .su_depolama import su_depolama_degerlendir
from .solucan_tesisi import solucan_degerlendir, solucan_tesisi_degerlendir
from .zeytinyagi_uretim_tesisi import zeytinyagi_uretim_tesisi_degerlendir
from .zeytinyagi_fabrikasi import zeytinyagi_fabrikasi_degerlendir
from .yikama_tesisi import yikama_tesisi_degerlendir
from .tarimsal_amacli_depo import calculate_tarimsal_amacli_depo

__all__ = [
    # Ana fonksiyonlar
    'genel_vasif_kural_kontrolu', 
    
    # Sabitler ve tanımlar
    'GENEL_YAPI_TURLERI_LISTESI',
    'ARAZI_TIPLERI',
    'YAPI_TURLERI', 
    'ARAZI_TIPI_ID_TO_AD',
    'YAPI_TURU_ID_TO_AD',
    'ARAZI_TIPI_AD_TO_ID',
    'YAPI_TURU_AD_TO_ID',
    
    # Sera fonksiyonları
    'hesapla_sera_yapilasma_kurallari',
    'sera_projesi_bilgilendirme',
    
    # Silo fonksiyonları
    'silo_projesi_degerlendir',
    'hesapla_silo_yapilasma_kurallari',
    'silo_projesi_bilgilendirme',
    'hububat_silo_degerlendir',
    
    # Genel kurallar
    'genel_minimum_arazi_kurali',
    
    # Bağ evi
    'bag_evi_degerlendir',
    'BAG_EVI_KURALLARI',
    
    # Diğer tesisler
    'hara_tesisi_degerlendir',
    'hesapla_ipek_bocekciligi_kurallari',
    'evcil_hayvan_tesisi_degerlendir',
    'sut_sigiri_degerlendir', 
    'besi_sigiri_degerlendir',
    'aricilik_degerlendir',
    'yumurtaci_tavuk_degerlendir',
    'etci_tavuk_degerlendir',
    'gezen_tavuk_degerlendir',
    'hindi_degerlendir',
    'kaz_ordek_degerlendir',
    'kucukbas_degerlendir',
    'calculate_soguk_hava_deposu',
    'meyve_sebze_kurutma_degerlendir',
    'lisansli_depo_degerlendir',
    'lisansli_depo_genel_bilgilendirme',
    'mantar_tesisi_degerlendir',
    'kurutma_tesisi_degerlendir',
    'su_kuyulari_degerlendir',
    'su_depolama_degerlendir',
    'solucan_degerlendir',
    'solucan_tesisi_degerlendir',
    'zeytinyagi_uretim_tesisi_degerlendir',
    'zeytinyagi_fabrikasi_degerlendir',
    'yikama_tesisi_degerlendir',
    'calculate_tarimsal_amacli_depo'
]
