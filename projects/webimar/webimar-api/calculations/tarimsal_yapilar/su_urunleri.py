"""
Su Ürünleri Üretim Tesisi Hesaplama Modülü

Yeni yönetmelik (2025) - Kriter 11.2

- Emsal bazlı hesaplama
- Bakıcı evi: taban max 75 m², toplam inşaat max 150 m²
"""
import logging

logger = logging.getLogger(__name__)

EMSAL_ORANI = 0.20
BAKICI_EVI_TABAN_M2 = 75
BAKICI_EVI_TOPLAM_M2 = 150
IDARI_BINA_TABAN_M2 = 75
IDARI_BINA_TOPLAM_M2 = 150
MIN_TESIS_ALANI_M2 = 500  # Minimum tesis alanı


def su_urunleri_degerlendir(data, emsal_orani=None):
    """Su ürünleri üretim tesisi hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        # Havuz/tank alanı (%70 emsal), müştemilat (%30 emsal)
        havuz_alani = emsal_m2 * 0.70
        mustemilat_alani = emsal_m2 * 0.30
        
        bakici_evi_hakki = emsal_m2 >= MIN_TESIS_ALANI_M2
        yapilanabilir = emsal_m2 >= 100  # Minimum işlevsel alan
        
        mesaj = "<b>SU ÜRÜNLERİ ÜRETİM TESİSİ DEĞERLENDİRMESİ</b><br><br>"
        mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
        mesaj += f"Emsal Alanı: {emsal_m2:,.2f} m²<br><br>"
        
        if yapilanabilir:
            mesaj += "<b>SONUÇ: TESİS KURULABİLİR</b><br><br>"
            mesaj += f"Havuz/Tank Alanı: {havuz_alani:,.2f} m²<br>"
            mesaj += f"Müştemilat Alanı: {mustemilat_alani:,.2f} m²<br>"
            if bakici_evi_hakki:
                mesaj += f"Bakıcı Evi: taban {BAKICI_EVI_TABAN_M2} m², toplam {BAKICI_EVI_TOPLAM_M2} m²<br>"
            mesaj += f"İdari Bina: taban {IDARI_BINA_TABAN_M2} m², toplam {IDARI_BINA_TOPLAM_M2} m²<br>"
        else:
            mesaj += "<b>SONUÇ: TESİS KURULAMAZ</b> - Yetersiz emsal alanı."
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "emsal_m2": emsal_m2,
            "bakici_evi_hakki": bakici_evi_hakki,
        }
    except Exception as e:
        logger.error(f"Su ürünleri hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}
