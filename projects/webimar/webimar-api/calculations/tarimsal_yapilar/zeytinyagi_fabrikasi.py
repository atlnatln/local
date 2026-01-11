"""
Zeytinyağı Fabrikası Hesaplama Modülü

Bu modül zeytinyağı fabrikası yapılaşma kurallarını ve hesaplamalarını içerir.
Zeytincilik Yönetmeliği'ne göre özel kurallar uygulanır.
"""

# Zeytinyağı fabrikası için sabitler
ZEYTINYAGI_FABRIKASI_EMSAL_ORANI = 0.10  # %10 emsal oranı
ZEYTINYAGI_FABRIKASI_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²) - küçük işletmeler için uygun hale getirildi

def _format_html_message(baslik, ana_mesaj, arazi_buyuklugu_m2, uretim_alani_m2, maksimum_emsal_alani):
    """HTML formatında mesaj oluştur"""
    return f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin-bottom: 20px;">
            <h3 style="margin: 0; color: #007bff;">{baslik}</h3>
        </div>
        
        <div style="background: #ffffff; padding: 20px; border: 1px solid #dee2e6; border-radius: 5px;">
            <p style="margin-bottom: 15px; font-size: 16px;">{ana_mesaj}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 20px;">
                <tr style="background: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Arazi Büyüklüğü:</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{arazi_buyuklugu_m2:.0f} m²</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Fabrika Üretim Alanı:</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{uretim_alani_m2:.0f} m²</td>
                </tr>
                <tr style="background: #f8f9fa;">
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Maksimum Emsal Alanı:</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{maksimum_emsal_alani:.0f} m²</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #dee2e6; font-weight: bold;">Emsal Kullanım Oranı:</td>
                    <td style="padding: 10px; border: 1px solid #dee2e6;">{int(ZEYTINYAGI_FABRIKASI_EMSAL_ORANI*100)}%</td>
                </tr>
            </table>
        </div>
    </div>
    """

def zeytinyagi_fabrikasi_degerlendir(data):
    """
    Zeytinyağı fabrikası değerlendirme fonksiyonu
    """
    try:
        # Giriş verilerini al - arazi_alani_m2, arazi_buyuklugu_m2, alan_m2 parametrelerini kabul et
        arazi_buyuklugu_m2 = float(
            data.get('arazi_alani_m2') or
            data.get('arazi_buyuklugu_m2') or 
            data.get('alan_m2', 0)
        )
        
        # Minimum arazi kontrolü
        if arazi_buyuklugu_m2 < ZEYTINYAGI_FABRIKASI_MIN_ARAZI_M2:
            return {
                'success': False,
                'izin_durumu': 'TESİS YAPILAMAZ',
                'mesaj': _format_html_message(
                    'TESİS YAPILAMAZ', 
                    f'Zeytinyağı fabrikası için minimum arazi büyüklüğü {ZEYTINYAGI_FABRIKASI_MIN_ARAZI_M2} m²\'dir.', 
                    arazi_buyuklugu_m2, 0, 0
                )
            }
        
        # Emsal hesaplaması
        maksimum_emsal_alani = arazi_buyuklugu_m2 * ZEYTINYAGI_FABRIKASI_EMSAL_ORANI
        
        # Basit fabrika üretim alanı hesabı (emsal alanının %70'i)
        fabrika_uretim_alani = maksimum_emsal_alani * 0.70
        
        # Kalan emsal hakkı (%30)
        kalan_emsal_hakki = maksimum_emsal_alani * 0.30
        
        # Başarılı sonuç
        api_result = {
            'success': True,
            'fabrika_uretim_alani_m2': round(fabrika_uretim_alani, 1),
            'maksimum_emsal_alani_m2': round(maksimum_emsal_alani, 1),
            'kalan_emsal_hakki_m2': round(kalan_emsal_hakki, 1),
            'emsal_kullanim_orani': round((fabrika_uretim_alani / maksimum_emsal_alani) * 100, 1),
            'izin_durumu': 'TESİS YAPILABİLİR',
            'mesaj': _format_html_message(
                'TESİS YAPILABİLİR',
                f'Zeytinyağı fabrikası kurulabilir. Fabrika üretim alanı: {fabrika_uretim_alani:.0f} m². Kalan emsal hakkı: {kalan_emsal_hakki:.0f} m² (ek yapılar için kullanılabilir).',
                arazi_buyuklugu_m2, fabrika_uretim_alani, maksimum_emsal_alani
            )
        }
        
        return api_result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'izin_durumu': 'HATA',
            'mesaj': f'Hesaplama sırasında hata oluştu: {str(e)}'
        }
