# Genel fonksiyonları common.py'den import et
from .common import (
    health_check, 
    get_yonetmelikler, 
    get_kml_files, 
    get_arazi_tipleri, 
    get_yapi_turleri,
    calculation_history,
    save_calculation,
    calculation_detail,
    delete_calculation
)

# Hayvancılık endpointlerini dışa aktar
from .hayvancilik import (
    calculate_hara,
    calculate_evcil_hayvan, 
    calculate_ipek_bocekciligi,
    calculate_kumes_yumurtaci,
    calculate_kumes_etci,
    calculate_kumes_gezen,
    calculate_kumes_hindi,
    calculate_kaz_ordek
)
# Hayvancılık endpointleri
from .hayvancilik import *
# Tesisler, depolama, sera, arıcılık endpointleri
from .tesisler import *
