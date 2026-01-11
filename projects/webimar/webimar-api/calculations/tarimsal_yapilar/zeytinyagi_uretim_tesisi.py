"""
Zeytinyağı Üretim Tesisi Hesaplama Modülü

Bu modül zeytinyağı üretim tesisi yapılaşma kurallarını ve hesaplamalarını içerir.
Basitleştirilmiş hesaplama modeli kullanır.
"""

# Zeytinyağı üretim tesisi için sabitler
ZEYTINYAGI_URETIM_TESISI_EMSAL_ORANI = 0.10  # %10 emsal oranı
ZEYTINYAGI_URETIM_TESISI_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²) - küçük işletmeler için uygun hale getirildi


def zeytinyagi_uretim_tesisi_hesapla(arazi_alani_m2: float) -> dict:
    """Zeytinyağı üretim tesisi için basitleştirilmiş hesaplama yapar"""
    
    # Minimum arazi kontrolü
    if arazi_alani_m2 < ZEYTINYAGI_URETIM_TESISI_MIN_ARAZI_M2:
        return {
            'success': False,
            'error': f'Zeytinyağı üretim tesisi için minimum {ZEYTINYAGI_URETIM_TESISI_MIN_ARAZI_M2} m² arazi gereklidir',
            'minimum_arazi_m2': ZEYTINYAGI_URETIM_TESISI_MIN_ARAZI_M2,
            'mevcut_arazi_m2': arazi_alani_m2
        }
    
    # Emsal hesaplama
    maksimum_emsal_alani = arazi_alani_m2 * ZEYTINYAGI_URETIM_TESISI_EMSAL_ORANI
    
    # Basit alan dağılımı
    uretim_alani_m2 = maksimum_emsal_alani * 0.70  # %70 üretim alanı
    idari_alan_m2 = maksimum_emsal_alani * 0.20    # %20 idari alan
    yardimci_alan_m2 = maksimum_emsal_alani * 0.10 # %10 yardımcı alan
    
    toplam_insaat_alani = uretim_alani_m2 + idari_alan_m2 + yardimci_alan_m2
    
    # Başarılı sonuç
    return {
    'success': True,
    'izin_durumu': 'TESİS YAPILABİLİR',
    'arazi_alani_m2': arazi_alani_m2,
    'emsal_orani': ZEYTINYAGI_URETIM_TESISI_EMSAL_ORANI,
    'maksimum_emsal_alani_m2': round(maksimum_emsal_alani, 2),
    'idari_alan_m2': round(idari_alan_m2, 2),
        'yardimci_alan_m2': round(yardimci_alan_m2, 2),
        'toplam_insaat_alani_m2': round(toplam_insaat_alani, 2),
        'kalan_emsal_hakki_m2': round(maksimum_emsal_alani - toplam_insaat_alani, 2),
        'emsal_kullanim_orani': round((toplam_insaat_alani / maksimum_emsal_alani) * 100, 1)
    }


def zeytinyagi_uretim_tesisi_degerlendir(data):
    """API endpoint için zeytinyağı üretim tesisi değerlendirme fonksiyonu"""
    try:
        # Alan bilgisini al - hem 'alan' hem de 'arazi_buyuklugu_m2' destekle
        alan = data.get('alan') or data.get('arazi_buyuklugu_m2') or data.get('alan_m2', 0)
        
        if not alan or alan <= 0:
            return {
                'success': False,
                'error': 'Geçerli bir arazi alanı giriniz'
            }
        
        # Hesaplama yap
        sonuc = zeytinyagi_uretim_tesisi_hesapla(float(alan))
        return sonuc
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Hesaplama hatası: {str(e)}'
        }
