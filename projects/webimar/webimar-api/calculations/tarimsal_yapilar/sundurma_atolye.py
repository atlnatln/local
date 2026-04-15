"""
Sundurma ve Çiftlik Atölyesi Hesaplama Modülü

Yeni yönetmelik (2025) - Kriter 8

Sundurma: kenarları açık/yarı açık, max 50 m²
Çiftlik atölyesi: max 50 m²

Arazi Büyüklüğü Şartları:
- Mutlak / Marjinal / Özel ürün: > 2 hektar (20.000 m²)
- Dikili tarım: > 1 hektar (10.000 m²)
- Örtü altı (sera): > 0,3 hektar (3.000 m²)
"""
import logging

logger = logging.getLogger(__name__)

MAX_ALAN_M2 = 50  # Her biri için max 50 m²

# Minimum arazi büyüklükleri (m²)
MIN_ARAZI_BUYUKLUKLERI = {
    "mutlak": 20000,    # 2 hektar
    "marjinal": 20000,  # 2 hektar
    "ozel_urun": 20000, # 2 hektar
    "dikili": 10000,    # 1 hektar
    "ortu_alti": 3000,  # 0,3 hektar
}

# Arazi vasfi kısaltmalarını tam adlara eşleme
ARAZI_VASFI_MAP = {
    "MT": "mutlak",
    "OT": "ozel_urun",
    "TA": "marjinal",
    "DT": "dikili",
    "OA": "ortu_alti",
}


def _kontrol_arazi_buyuklugu(arazi_m2, arazi_vasfi):
    """Arazi büyüklüğünün minimum şartı karşılayıp karşılamadığını kontrol eder."""
    vasif_key = ARAZI_VASFI_MAP.get(arazi_vasfi.upper(), "marjinal") if arazi_vasfi else "marjinal"
    min_alan = MIN_ARAZI_BUYUKLUKLERI.get(vasif_key, 20000)
    return arazi_m2 >= min_alan, min_alan, vasif_key


def sundurma_degerlendir(data, emsal_orani=None):
    """Sundurma hesaplama"""
    return _ortak_hesapla(data, "SUNDURMA", emsal_orani)


def ciftlik_atolyesi_degerlendir(data, emsal_orani=None):
    """Çiftlik atölyesi hesaplama"""
    return _ortak_hesapla(data, "ÇİFTLİK ATÖLYESİ", emsal_orani)


def _ortak_hesapla(data, yapi_adi, emsal_orani=None):
    """Sundurma ve çiftlik atölyesi için ortak hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        arazi_vasfi = data.get('arazi_vasfi', 'TA')
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        arazi_yeterli, min_alan, vasif_key = _kontrol_arazi_buyuklugu(arazi_m2, arazi_vasfi)
        
        mesaj = f"<b>{yapi_adi} DEĞERLENDİRMESİ</b><br><br>"
        mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
        mesaj += f"Arazi Sınıfı: {arazi_vasfi or 'Belirtilmemiş'}<br>"
        mesaj += f"Minimum Arazi Şartı: {min_alan:,} m²<br><br>"
        
        if arazi_yeterli:
            mesaj += (
                f"<b>SONUÇ: {yapi_adi} YAPILABİLİR</b><br>"
                f"Maksimum {yapi_adi.lower()} alanı: <b>{MAX_ALAN_M2} m²</b>"
            )
        else:
            mesaj += (
                f"<b>SONUÇ: {yapi_adi} YAPILAMAZ</b><br>"
                f"Arazi büyüklüğü ({arazi_m2:,.0f} m²), "
                f"{vasif_key} arazi için minimum {min_alan:,} m² şartını karşılamamaktadır."
            )
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if arazi_yeterli else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "max_alan_m2": MAX_ALAN_M2 if arazi_yeterli else 0,
        }
    except Exception as e:
        logger.error(f"{yapi_adi} hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}
