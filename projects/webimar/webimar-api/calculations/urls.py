from django.urls import path
from . import views

# Hayvancılık modülü importları (UX-optimize edilmiş)
from calculations.views.hayvancilik import (
    calculate_hara, calculate_ipek_bocekciligi, calculate_evcil_hayvan,
    calculate_sut_sigirciligi, calculate_besi_sigirciligi, calculate_agil_kucukbas,
    calculate_kumes_yumurtaci, calculate_kumes_etci, calculate_kumes_gezen,
    calculate_kumes_hindi, calculate_kaz_ordek
)

# Tesisler modülü importları (UX-optimize edilecek)
from calculations.views.tesisler import (
    calculate_solucan_tesisi, calculate_mantar_tesisi, calculate_sera, calculate_aricilik,
    calculate_hububat_silo, calculate_tarimsal_amacli_depo, calculate_lisansli_depo,
    calculate_yikama_tesisi, calculate_kurutma_tesisi, calculate_meyve_sebze_kurutma,
    calculate_zeytinyagi_fabrikasi, calculate_su_depolama, calculate_su_kuyulari,
    calculate_bag_evi, calculate_zeytinyagi_uretim_tesisi, calculate_soguk_hava_deposu
)

# Ayrılmış Bağ Evi Modülü (yeni modular endpoint)
from calculations.tarimsal_yapilar.bag_evi.views import calculate_bag_evi_view

# Havza Bazlı Destekleme Modeli
from calculations.havza_bazli_destekleme_modeli import havza_bazli_destekleme_modeli

# Common modülü importları
from calculations.views.common import (
    health_check, get_arazi_tipleri, get_yapi_turleri, get_structure_categories, 
    get_seo_meta, get_yonetmelikler, get_kml_files, calculation_history, 
    save_calculation, calculation_detail, track_public_calculation_event,
    public_homepage_calculation_insights
)

urlpatterns = [
    # Health check
    path('health/', health_check, name='calculations_health'),
    
    # Havza Bazlı Destekleme Modeli
    path('havza-bazli-destekleme-modeli/', havza_bazli_destekleme_modeli, name='havza_bazli_destekleme_modeli'),
    path('public-track/', track_public_calculation_event, name='track_public_calculation_event'),
    path('homepage-insights/', public_homepage_calculation_insights, name='public_homepage_calculation_insights'),
    
    # Constants endpoints
    path('arazi-tipleri/', get_arazi_tipleri, name='get_arazi_tipleri'),
    path('yapi-turleri/', get_yapi_turleri, name='get_yapi_turleri'),
    path('structure-categories/', get_structure_categories, name='get_structure_categories'),
    path('seo-meta/', get_seo_meta, name='get_seo_meta'),
    
    # Constants.py YAPI_TURU_ID_MAPPING'e göre 27 yapı türü endpoints
    
    # ID: 1-4 - Özel Üretim Tesisleri
    path('solucan-tesisi/', calculate_solucan_tesisi, name='calculate_solucan_tesisi'),  # ID: 1
    path('mantar-tesisi/', calculate_mantar_tesisi, name='calculate_mantar_tesisi'),    # ID: 2
    path('sera/', calculate_sera, name='calculate_sera'),                              # ID: 3
    path('aricilik/', calculate_aricilik, name='calculate_aricilik'),                  # ID: 4
    
    # ID: 5-16 - Depolama ve İşleme Tesisleri
    path('hububat-silo/', calculate_hububat_silo, name='calculate_hububat_silo'),      # ID: 5
    path('tarimsal-depo/', calculate_tarimsal_amacli_depo, name='calculate_tarimsal_amacli_depo'), # ID: 6
    path('lisansli-depo/', calculate_lisansli_depo, name='calculate_lisansli_depo'),   # ID: 7
    path('yikama-tesisi/', calculate_yikama_tesisi, name='calculate_yikama_tesisi'),   # ID: 8
    path('kurutma-tesisi/', calculate_kurutma_tesisi, name='calculate_kurutma_tesisi'), # ID: 9
    path('meyve-sebze-kurutma/', calculate_meyve_sebze_kurutma, name='calculate_meyve_sebze_kurutma'), # ID: 10
    path('zeytinyagi-fabrikasi/', calculate_zeytinyagi_fabrikasi, name='calculate_zeytinyagi_fabrikasi'), # ID: 11
    path('su-depolama/', calculate_su_depolama, name='calculate_su_depolama'),         # ID: 12
    path('su-kuyulari/', calculate_su_kuyulari, name='calculate_su_kuyulari'),         # ID: 13
    path('bag-evi/', calculate_bag_evi, name='calculate_bag_evi'),                     # ID: 14 (legacy - wrapper)
    path('bag-evi-v2/', calculate_bag_evi_view, name='calculate_bag_evi_view'),       # ID: 14 (new modular)
    path('zeytinyagi-uretim-tesisi/', calculate_zeytinyagi_uretim_tesisi, name='calculate_zeytinyagi_uretim_tesisi'), # ID: 15
    path('soguk-hava-deposu/', calculate_soguk_hava_deposu, name='calculate_soguk_hava_deposu'), # ID: 16
    
    # ID: 17-27 - Hayvancılık Tesisleri (UX-optimize edilmiş modüler endpoints)
    path('sut-sigirciligi/', calculate_sut_sigirciligi, name='calculate_sut_sigirciligi'), # ID: 17
    path('agil-kucukbas/', calculate_agil_kucukbas, name='calculate_agil_kucukbas'),     # ID: 18
    # Kanatlı tesisler
    path('kumes-yumurtaci/', calculate_kumes_yumurtaci, name='calculate_kumes_yumurtaci'),  # ID: 19
    path('kumes-etci/', calculate_kumes_etci, name='calculate_kumes_etci'),                 # ID: 20
    path('kumes-gezen/', calculate_kumes_gezen, name='calculate_kumes_gezen'),             # ID: 21
    path('kumes-hindi/', calculate_kumes_hindi, name='calculate_kumes_hindi'),             # ID: 22
    path('kaz-ordek/', calculate_kaz_ordek, name='calculate_kaz_ordek'),                   # ID: 23
    path('hara/', calculate_hara, name='calculate_hara'),                                       # ID: 24 (UX-optimize)
    path('ipek-bocekciligi/', calculate_ipek_bocekciligi, name='calculate_ipek_bocekciligi'),   # ID: 25 (UX-optimize)
    path('evcil-hayvan/', calculate_evcil_hayvan, name='calculate_evcil_hayvan'),               # ID: 26 (UX-optimize)
    path('besi-sigirciligi/', calculate_besi_sigirciligi, name='calculate_besi_sigirciligi'), # ID: 27
    
    # Static dosya servisleri
    path('static/yonetmelikler/', get_yonetmelikler, name='get_yonetmelikler'),
    path('static/kml-files/', get_kml_files, name='get_kml_files'),
    
    # Kullanıcı hesaplama geçmişi
    path('history/', calculation_history, name='calculation_history'),
    path('save/', save_calculation, name='save_calculation'),
    path('detail/<int:calculation_id>/', calculation_detail, name='calculation_detail'),
]