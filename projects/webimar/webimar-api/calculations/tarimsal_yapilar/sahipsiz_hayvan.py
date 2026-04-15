"""
Sahipsiz Hayvan Barınağı Hesaplama Modülü

Yeni yönetmelik (2025) - Kriter 5

Kısıtlar:
- SADECE marjinal tarım arazisinde yapılabilir
- Büyük ova koruma alanı dışında olmalı
- Kazı/dolgu yapılamaz, beton dökülemez
- Sökülüp takılabilir yapı olmalı
- Alan: Doğa Koruma ve Milli Parklar GnMd tarafından uygun görülen miktarda
"""
import logging

logger = logging.getLogger(__name__)

EMSAL_ORANI = 0.20
IZIN_VERILEN_ARAZI_SINIFI = "TA"  # Sadece marjinal tarım arazisi


def sahipsiz_hayvan_barinagi_degerlendir(data, emsal_orani=None):
    """Sahipsiz hayvan barınağı hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        arazi_sinifi = data.get('arazi_vasfi', '').upper()
        buyuk_ova_alaninda = data.get('buyuk_ova_alaninda_mi', False)
        
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        engeller = []
        if arazi_sinifi and arazi_sinifi != IZIN_VERILEN_ARAZI_SINIFI:
            engeller.append(f"Arazi sınıfı '{arazi_sinifi}' - Sahipsiz hayvan barınağı SADECE marjinal tarım arazisinde (TA) yapılabilir.")
        
        if buyuk_ova_alaninda:
            engeller.append("Arazi büyük ova koruma alanı içinde - Bu alanda sahipsiz hayvan barınağı yapılamaz.")
        
        yapilanabilir = len(engeller) == 0
        
        mesaj = "<b>SAHİPSİZ HAYVAN BARINAĞI DEĞERLENDİRMESİ</b><br><br>"
        mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
        mesaj += f"Arazi Sınıfı: {arazi_sinifi or 'Belirtilmemiş'}<br>"
        mesaj += f"Emsal Alanı: {emsal_m2:,.2f} m²<br><br>"
        
        if yapilanabilir:
            mesaj += (
                "<b>SONUÇ: BARINAK YAPILABİLİR</b><br><br>"
                "<b>Önemli Koşullar:</b><br>"
                "- Kazı/dolgu yapılamaz, beton dökülemez<br>"
                "- Sökülüp takılabilir yapı olmalıdır<br>"
                "- Alan miktarı Doğa Koruma ve Milli Parklar Genel Müdürlüğü tarafından belirlenir<br>"
                f"- Emsal dahilinde kullanılabilir alan: {emsal_m2:,.2f} m²"
            )
        else:
            mesaj += "<b>SONUÇ: BARINAK YAPILAMAZ</b><br>"
            for engel in engeller:
                mesaj += f"- {engel}<br>"
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "emsal_m2": emsal_m2,
            "engeller": engeller,
        }
    except Exception as e:
        logger.error(f"Sahipsiz hayvan barınağı hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}
