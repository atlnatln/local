"""
Fide ve Fidan Üretim Tesisi Hesaplama Modülü

Yeni yönetmelik (2025) - Kriter 4

Fide üretim tesisi:
- Minimum sera alanı: 0,2 hektar (2.000 m²)
- Kapalı alan (depo/sevkiyat): max 500 m²

Fidan üretim tesisi:
- Açık alan üretim kapasitesine göre:
  - Her 1.000 adet kapasite için: soğuk hava deposu 1,5-2,5 m², yönetim 0,15 m², malzeme deposu 0,1 m²
- Doku kültürü kapasitesine göre:
  - Her 1.000 adet kapasite için: iklimlendirme 0,1 m², transfer 0,02 m², sera 7 m²
"""
import logging

logger = logging.getLogger(__name__)

# Fide üretim tesisi sabitleri
FIDE_MIN_SERA_ALANI_M2 = 2000  # 0,2 hektar
FIDE_MAX_KAPALI_ALAN_M2 = 500  # depo/sevkiyat

# Fidan üretim tesisi sabitleri (her 1000 adet kapasite için m²)
FIDAN_ACIK_ALAN = {
    "soguk_hava_deposu": {"min": 1.5, "max": 2.5, "ortalama": 2.0},
    "yonetim_idare": 0.15,
    "malzeme_deposu": 0.1,
}
FIDAN_DOKU_KULTURU = {
    "iklimlendirme": 0.1,
    "transfer_odasi": 0.02,
    "sera": 7.0,
}

EMSAL_ORANI = 0.20


def fide_uretim_degerlendir(data, emsal_orani=None):
    """Fide üretim tesisi hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        planlanan_sera_m2 = float(data.get('sera_alani_m2', 0))
        
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        if planlanan_sera_m2 <= 0:
            planlanan_sera_m2 = min(arazi_m2 * 0.8, emsal_m2)
        
        yapilanabilir = planlanan_sera_m2 >= FIDE_MIN_SERA_ALANI_M2
        kapali_alan = min(FIDE_MAX_KAPALI_ALAN_M2, emsal_m2 * 0.25)
        
        if yapilanabilir:
            mesaj = (
                f"<b>FİDE ÜRETİM TESİSİ DEĞERLENDİRMESİ</b><br><br>"
                f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
                f"Planlanan Sera Alanı: {planlanan_sera_m2:,.0f} m²<br>"
                f"Minimum Sera Alanı Şartı: {FIDE_MIN_SERA_ALANI_M2:,} m² ✓<br><br>"
                f"<b>SONUÇ: TESİS KURULABİLİR</b><br>"
                f"Kapalı alan (depo/sevkiyat): max {kapali_alan:,.0f} m² (limit: {FIDE_MAX_KAPALI_ALAN_M2} m²)"
            )
        else:
            mesaj = (
                f"<b>FİDE ÜRETİM TESİSİ DEĞERLENDİRMESİ</b><br><br>"
                f"Planlanan sera alanı ({planlanan_sera_m2:,.0f} m²), "
                f"minimum {FIDE_MIN_SERA_ALANI_M2:,} m² şartını karşılamamaktadır.<br>"
                f"<b>SONUÇ: TESİS KURULAMAZ</b>"
            )
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "sera_alani_m2": planlanan_sera_m2,
            "kapali_alan_m2": kapali_alan if yapilanabilir else 0,
        }
    except Exception as e:
        logger.error(f"Fide üretim hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}


def fidan_uretim_degerlendir(data, emsal_orani=None):
    """Fidan üretim tesisi hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        kapasite_adet = int(data.get('kapasite_adet', 0))
        uretim_tipi = data.get('uretim_tipi', 'acik_alan')  # acik_alan veya doku_kulturu
        
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        if kapasite_adet <= 0:
            # Kapasite girilmemişse emsale göre tahmin
            kapasite_adet = int(emsal_m2 * 100)  # Yaklaşık tahmin
        
        birim_1000 = kapasite_adet / 1000.0
        yapilar = []
        toplam_alan = 0
        
        if uretim_tipi == 'doku_kulturu':
            iklimlendirme = birim_1000 * FIDAN_DOKU_KULTURU["iklimlendirme"]
            transfer = birim_1000 * FIDAN_DOKU_KULTURU["transfer_odasi"]
            sera = birim_1000 * FIDAN_DOKU_KULTURU["sera"]
            yapilar = [
                {"isim": "İklimlendirme Odası", "alan_m2": round(iklimlendirme, 2)},
                {"isim": "Transfer Odası", "alan_m2": round(transfer, 2)},
                {"isim": "Sera", "alan_m2": round(sera, 2)},
            ]
            toplam_alan = iklimlendirme + transfer + sera
        else:
            soguk_depo = birim_1000 * FIDAN_ACIK_ALAN["soguk_hava_deposu"]["ortalama"]
            yonetim = birim_1000 * FIDAN_ACIK_ALAN["yonetim_idare"]
            malzeme = birim_1000 * FIDAN_ACIK_ALAN["malzeme_deposu"]
            yapilar = [
                {"isim": "Soğuk Hava Deposu", "alan_m2": round(soguk_depo, 2)},
                {"isim": "Yönetim/İdare Binası", "alan_m2": round(yonetim, 2)},
                {"isim": "Malzeme Deposu", "alan_m2": round(malzeme, 2)},
            ]
            toplam_alan = soguk_depo + yonetim + malzeme
        
        yapilanabilir = toplam_alan <= emsal_m2
        
        mesaj = (
            f"<b>FİDAN ÜRETİM TESİSİ DEĞERLENDİRMESİ</b><br><br>"
            f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
            f"Üretim Tipi: {'Doku Kültürü' if uretim_tipi == 'doku_kulturu' else 'Açık Alan'}<br>"
            f"Kapasite: {kapasite_adet:,} adet<br>"
            f"Toplam Gerekli Alan: {toplam_alan:,.2f} m²<br>"
            f"Emsal Alanı: {emsal_m2:,.2f} m²<br><br>"
        )
        
        if yapilanabilir:
            mesaj += "<b>SONUÇ: TESİS KURULABİLİR</b><br>"
            for y in yapilar:
                mesaj += f"- {y['isim']}: {y['alan_m2']} m²<br>"
        else:
            mesaj += f"<b>SONUÇ: TESİS KURULAMAZ</b> - Gerekli alan ({toplam_alan:,.2f} m²) emsal alanını ({emsal_m2:,.2f} m²) aşmaktadır."
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "kapasite_adet": kapasite_adet,
            "yapilar": yapilar,
            "toplam_alan_m2": round(toplam_alan, 2),
        }
    except Exception as e:
        logger.error(f"Fidan üretim hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}
