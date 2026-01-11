"""
Genel minimum arazi büyüklüğü ve ortak yapılaşma kuralları.
"""

def genel_minimum_arazi_kurali(yapi_tipi_detay, arazi_buyuklugu_m2):
    """
    Genel minimum arazi büyüklüğü kuralı (1 m² altı için izin verilmez).
    Args:
        yapi_tipi_detay (str): Yapı tipi adı
        arazi_buyuklugu_m2 (float): Parsel büyüklüğü (m²)
    Returns:
        dict: Sonuç ve açıklama
    """
    min_arazi = 1
    sonuc = {
        "izin_durumu": None,
        "ana_mesaj": None,
        "durum": None,
        "mesaj": None
    }
    if arazi_buyuklugu_m2 is None or arazi_buyuklugu_m2 < min_arazi:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = f"Parsel büyüklüğü ({arazi_buyuklugu_m2} m²), {yapi_tipi_detay.lower()} için minimum gereksinim olan {min_arazi} m²'nin altındadır."
        sonuc["durum"] = sonuc["izin_durumu"]
        sonuc["mesaj"] = sonuc["ana_mesaj"]
        return sonuc
    else:
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["ana_mesaj"] = f"{yapi_tipi_detay} için arazi büyüklüğü ({arazi_buyuklugu_m2} m²) yeterli olduğundan izin verilebilir."
        sonuc["durum"] = sonuc["izin_durumu"]
        sonuc["mesaj"] = sonuc["ana_mesaj"]
        return sonuc
