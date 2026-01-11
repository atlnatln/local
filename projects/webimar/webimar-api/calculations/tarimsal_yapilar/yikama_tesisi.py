"""
Yıkama Tesisi yapılaşma kurallarını ve hesaplamalarını içeren modül
Sadece tarımsal ürün yıkama tesisi (yumrulu bitkiler) yapılabilir, başka bir yapı ve müştemilat izni yoktur.
"""

import logging
logger = logging.getLogger(__name__)

DEFAULT_EMSAL_ORANI = 0.20  # %20 varsayılan (dinamik sistem için)
YIKAMA_TESISI_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²)

def _olustur_html_mesaj_yikama(sonuc_data: dict) -> str:
    """
    Yıkama tesisi hesaplama sonuçlarını HTML formatında tablo ve notlarla gösterir.
    """
    izin_durumu = sonuc_data.get("izin_durumu", "")
    durum_color = "#28a745" if izin_durumu == "TESİS YAPILABİLİR" else "#dc3545"
    durum_bg = "#d4edda" if izin_durumu == "TESİS YAPILABİLİR" else "#f8d7da"
    durum_icon = "✅" if izin_durumu == "TESİS YAPILABİLİR" else "❌"
    emsal_orani = sonuc_data.get("emsal_orani", DEFAULT_EMSAL_ORANI)
    arazi_buyuklugu_m2 = sonuc_data.get("arazi_buyuklugu_m2", 0)
    maksimum_yikama_alani = sonuc_data.get("maksimum_yikama_alani_m2", 0)

    mesaj = f"""
    <style>
        .yikama-tesisi-sonuc {{font-family: Arial, sans-serif;}}
        .yikama-tesisi-sonuc h3 {{color: {durum_color}; margin-bottom: 15px;}}
        .yikama-tesisi-sonuc .baslik {{font-weight: bold; margin-top: 15px; margin-bottom: 8px;}}
        .yikama-tesisi-sonuc table {{border-collapse: collapse; width: 100%; margin-bottom: 20px;}}
        .yikama-tesisi-sonuc th, .yikama-tesisi-sonuc td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
        .yikama-tesisi-sonuc th {{background-color: #f2f2f2;}}
        .yikama-tesisi-sonuc .basarili {{color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .yikama-tesisi-sonuc .hata {{color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .yikama-tesisi-sonuc .notlar {{font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}}
    </style>
    <div class="yikama-tesisi-sonuc">
        <h3>{durum_icon} TARIMSAL ÜRÜN YIKAMA TESİSİ {izin_durumu}</h3>
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
                <th>Maksimum Yıkama Alanı</th>
                <td>{maksimum_yikama_alani:,.0f} m²</td>
            </tr>
        </table>
    """
    if izin_durumu == "TESİS YAPILABİLİR":
        mesaj += f'<div class="basarili"><b>SONUÇ:</b> Bu araziye en fazla <b>{maksimum_yikama_alani:,.0f} m²</b> tarımsal ürün (yumrulu bitkiler) yıkama tesisi yapılabilir.</div>'
    else:
        mesaj += f'<div class="hata"><b>SONUÇ:</b> Yıkama tesisi yapılamaz. {sonuc_data.get("error", "")}</div>'

    mesaj += """
        <div class="notlar">
            <b>Planlama Notları:</b><br>
            - Sadece tarımsal ürün (yumrulu bitkiler) yıkama tesisi yapılabilir.<br>
            - İdari bina, teknik bina, depo veya ek müştemilat yapılamaz.<br>
            - Maksimum yıkama alanı emsal oranına (%20) göre belirlenir.<br>
            - Hesaplama "Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmelik" esas alınarak yapılmıştır.<br>
        </div>
    </div>
    """
    return mesaj

def yikama_tesisi_degerlendir(data, emsal_orani: float = None):
    """
    API için yıkama tesisi değerlendirme fonksiyonu
    Sadece açıkta tarımsal ürün yıkama tesisi yapılabilir, idari bina vb. yapılamaz.
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
                'maksimum_yikama_alani_m2': 0,
                'emsal_orani': kullanilacak_emsal_orani
            }
            sonuc['mesaj'] = _olustur_html_mesaj_yikama(sonuc)
            return sonuc

        if arazi_buyuklugu_m2 < YIKAMA_TESISI_MIN_ARAZI_M2:
            sonuc = {
                'success': False,
                'error': f'Yıkama tesisi için minimum {YIKAMA_TESISI_MIN_ARAZI_M2} m² arazi gereklidir',
                'izin_durumu': 'TESİS YAPILAMAZ',
                'maksimum_yikama_alani_m2': 0,
                'emsal_orani': kullanilacak_emsal_orani
            }
            sonuc['mesaj'] = _olustur_html_mesaj_yikama(sonuc)
            return sonuc

        maksimum_yikama_alani = arazi_buyuklugu_m2 * kullanilacak_emsal_orani

        sonuc = {
            'success': True,
            'izin_durumu': 'TESİS YAPILABİLİR',
            'maksimum_yikama_alani_m2': maksimum_yikama_alani,
            'emsal_orani': kullanilacak_emsal_orani
        }
        sonuc['mesaj'] = _olustur_html_mesaj_yikama(sonuc)
        return sonuc

    except Exception as e:
        sonuc = {
            'success': False,
            'error': str(e),
            'izin_durumu': 'TESİS YAPILAMAZ',
            'maksimum_yikama_alani_m2': 0,
            'emsal_orani': DEFAULT_EMSAL_ORANI
        }
        sonuc['mesaj'] = _olustur_html_mesaj_yikama(sonuc)
        return sonuc
