"""
Meyve Sebze Kurutma Alanı yapılaşma kurallarını ve hesaplamalarını içeren modül
Sadece açıkta meyve/sebze kurutma alanı yapılabilir, başka bir yapı ve müştemilat izni yoktur.
"""

import logging
logger = logging.getLogger(__name__)

DEFAULT_EMSAL_ORANI = 0.20  # %20 varsayılan (dinamik sistem için)
MEYVE_SEBZE_KURUTMA_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²)
# Sadece açık kurutma alanı yapılabilir, bina yok!

def _olustur_html_mesaj_meyve_sebze_kurutma(sonuc_data: dict) -> str:
    """
    Meyve/sebze kurutma alanı hesaplama sonucunu HTML formatında tablo ve notlarla gösterir.
    """
    izin_durumu = sonuc_data.get("izin_durumu", "")
    durum_color = "#28a745" if izin_durumu == "TESİS YAPILABİLİR" else "#dc3545"
    durum_bg = "#d4edda" if izin_durumu == "TESİS YAPILABİLİR" else "#f8d7da"
    durum_icon = "✅" if izin_durumu == "TESİS YAPILABİLİR" else "❌"
    emsal_orani = sonuc_data.get("emsal_orani", DEFAULT_EMSAL_ORANI)
    arazi_buyuklugu_m2 = sonuc_data.get("arazi_buyuklugu_m2", 0)
    maksimum_kurutma_alani = sonuc_data.get("maksimum_kurutma_alani_m2", 0)

    mesaj = f"""
    <style>
        .meyve-sebze-kurutma-sonuc {{font-family: Arial, sans-serif;}}
        .meyve-sebze-kurutma-sonuc h3 {{color: {durum_color}; margin-bottom: 15px;}}
        .meyve-sebze-kurutma-sonuc .baslik {{font-weight: bold; margin-top: 15px; margin-bottom: 8px;}}
        .meyve-sebze-kurutma-sonuc table {{border-collapse: collapse; width: 100%; margin-bottom: 20px;}}
        .meyve-sebze-kurutma-sonuc th, .meyve-sebze-kurutma-sonuc td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
        .meyve-sebze-kurutma-sonuc th {{background-color: #f2f2f2;}}
        .meyve-sebze-kurutma-sonuc .basarili {{color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .meyve-sebze-kurutma-sonuc .hata {{color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .meyve-sebze-kurutma-sonuc .notlar {{font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}}
    </style>
    <div class="meyve-sebze-kurutma-sonuc">
        <h3>{durum_icon} MEYVE/SEBZE KURUTMA ALANI {izin_durumu}</h3>
        <div class="baslik">GENEL DURUM</div>
        <table>
            <tr>
                <th>Arazi Büyüklüğü</th>
                <td>{arazi_buyuklugu_m2:,.0f} m²</td>
            </tr>
            <tr>
                <th>Emsal Oranı</th>
                <td>%{emsal_orani*100:.0f}</td>
            </tr>
            <tr>
                <th>Maksimum Kurutma Alanı</th>
                <td>{maksimum_kurutma_alani:,.0f} m²</td>
            </tr>
        </table>
    """
    if izin_durumu == "TESİS YAPILABİLİR":
        mesaj += f'<div class="basarili"><b>SONUÇ:</b> Bu araziye en fazla <b>{maksimum_kurutma_alani:,.0f} m²</b> açıkta meyve/sebze kurutma alanı yapılabilir.</div>'
    else:
        mesaj += f'<div class="hata"><b>SONUÇ:</b> Kurutma tesisi yapılamaz. {sonuc_data.get("error", "")}</div>'

    mesaj += """
        <div class="notlar">
            <b>Planlama Notları:</b><br>
            - Sadece açıkta meyve ve sebze kurutma alanı yapılabilir.<br>
            - İdari bina, teknik bina, depo veya ek müştemilat yapılamaz.<br>
            - Maksimum kurutma alanı emsal oranına (%20) göre belirlenir.<br>
            - Hesaplama "Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmelik" esas alınarak yapılmıştır.<br>
        </div>
    </div>
    """
    return mesaj

def meyve_sebze_kurutma_degerlendir(data, emsal_orani: float = None):
    """
    API için meyve/sebze kurutma alanı değerlendirme fonksiyonu
    Sadece açıkta kurutma alanı yapılabilir, idari bina vb. yapılamaz.
    """
    try:
        kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
        arazi_buyuklugu_m2 = float(
            data.get('arazi_alani_m2') or 
            data.get('alan_m2') or 
            data.get('arazi_buyuklugu_m2') or 0
        )
        if arazi_buyuklugu_m2 <= 0:
            sonuc = {
                'success': False,
                'error': 'Arazi büyüklüğü pozitif olmalıdır',
                'izin_durumu': 'TESİS YAPILAMAZ',
                'maksimum_kurutma_alani_m2': 0,
                'emsal_orani': kullanilacak_emsal_orani
            }
            sonuc['html_mesaj'] = _olustur_html_mesaj_meyve_sebze_kurutma(sonuc)
            return sonuc

        if arazi_buyuklugu_m2 < MEYVE_SEBZE_KURUTMA_MIN_ARAZI_M2:
            sonuc = {
                'success': False,
                'error': f'Meyve/sebze kurutma alanı için minimum {MEYVE_SEBZE_KURUTMA_MIN_ARAZI_M2} m² arazi gereklidir',
                'izin_durumu': 'TESİS YAPILAMAZ',
                'maksimum_kurutma_alani_m2': 0,
                'emsal_orani': kullanilacak_emsal_orani
            }
            sonuc['html_mesaj'] = _olustur_html_mesaj_meyve_sebze_kurutma(sonuc)
            return sonuc

        maksimum_kurutma_alani = arazi_buyuklugu_m2 * kullanilacak_emsal_orani

        sonuc = {
            'success': True,
            'izin_durumu': 'TESİS YAPILABİLİR',
            'maksimum_kurutma_alani_m2': maksimum_kurutma_alani,
            'emsal_orani': kullanilacak_emsal_orani
        }
        sonuc['html_mesaj'] = _olustur_html_mesaj_meyve_sebze_kurutma(sonuc)
        return sonuc

    except Exception as e:
        sonuc = {
            'success': False,
            'error': str(e),
            'izin_durumu': 'TESİS YAPILAMAZ',
            'maksimum_kurutma_alani_m2': 0,
            'emsal_orani': DEFAULT_EMSAL_ORANI
        }
        sonuc['html_mesaj'] = _olustur_html_mesaj_meyve_sebze_kurutma(sonuc)
        return sonuc
