"""
Su Depolama Tesisi Hesaplama Modülü - Basit Versiyon

Bu modül su depolama tesisleri için sadece arazi alanı girişi ile hesaplama yapar.
Yıkama tesisi modülündeki gibi HTML tablo ve stil ile detaylı çıktı üretir.
"""


DEFAULT_SU_DEPOLAMA_EMSAL_ORANI = 0.20  # %20 varsayılan emsal oranı (artık dinamik)
SU_DEPOLAMA_MIN_ARAZI_M2 = 500  # Minimum 500 m² arazi gereksinimi

def _olustur_mesaj_su_depolama(sonuc_data: dict) -> str:
    """
    Su depolama tesisi hesaplama sonuçlarını HTML formatında tablo ve notlarla gösterir.
    """
    izin_durumu = sonuc_data.get("izin_durumu", "")
    durum_color = "#28a745" if izin_durumu == "TESİS YAPILABİLİR" else "#dc3545"
    durum_icon = "✅" if izin_durumu == "TESİS YAPILABİLİR" else "❌"
    emsal_orani = sonuc_data.get("emsal_orani", DEFAULT_SU_DEPOLAMA_EMSAL_ORANI)
    arazi_buyuklugu_m2 = sonuc_data.get("arazi_buyuklugu_m2", 0)
    su_depolama_pompaj_alani_m2 = sonuc_data.get("su_depolama_pompaj_alani_m2", 0)
    maksimum_emsal_alani_m2 = sonuc_data.get("maksimum_emsal_alani_m2", 0)
    kalan_emsal_hakki_m2 = sonuc_data.get("kalan_emsal_hakki_m2", 0)
    emsal_kullanim_orani = sonuc_data.get("emsal_kullanim_orani", 0)
    mesaj = f"""
    <style>
        .su-depolama-sonuc {{font-family: Arial, sans-serif;}}
        .su-depolama-sonuc h3 {{color: {durum_color}; margin-bottom: 15px;}}
        .su-depolama-sonuc .baslik {{font-weight: bold; margin-top: 15px; margin-bottom: 8px;}}
        .su-depolama-sonuc table {{border-collapse: collapse; width: 100%; margin-bottom: 20px;}}
        .su-depolama-sonuc th, .su-depolama-sonuc td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
        .su-depolama-sonuc th {{background-color: #f2f2f2;}}
        .su-depolama-sonuc .basarili {{color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .su-depolama-sonuc .hata {{color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .su-depolama-sonuc .notlar {{font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}}
    </style>
    <div class="su-depolama-sonuc">
        <h3>{durum_icon} SU DEPOLAMA VE POMPAJ SİSTEMİ {izin_durumu}</h3>
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
                <th>Maksimum Emsal Alanı</th>
                <td>{maksimum_emsal_alani_m2:,.0f} m²</td>
            </tr>
            <tr>
                <th>Su Depolama ve Pompaj Sistemi Alanı</th>
                <td>{su_depolama_pompaj_alani_m2:,.0f} m²</td>
            </tr>
            <tr>
                <th>Kalan Emsal Hakkı</th>
                <td>{kalan_emsal_hakki_m2:,.0f} m²</td>
            </tr>
            <tr>
                <th>Emsal Kullanım Oranı</th>
                <td>%{emsal_kullanim_orani:.1f}</td>
            </tr>
        </table>
    """
    if izin_durumu == "TESİS YAPILABİLİR":
        mesaj += f'<div class="basarili"><b>SONUÇ:</b> Su depolama ve pompaj sistemi kurulabilir. Alan: {su_depolama_pompaj_alani_m2} m²</div>'
    else:
        hata_mesaji = sonuc_data.get("hata_mesaji", "")
        mesaj += f'<div class="hata"><b>SONUÇ:</b> Su depolama ve pompaj sistemi yapılamaz. {hata_mesaji}</div>'
    mesaj += """
        <div class="notlar">
            <b>Planlama Notları:</b><br>
            - Sadece su depolama ve pompaj sistemi yapılabilir.<br>
            - Maksimum kapalı alan emsal oranına (%20) göre belirlenir.<br>
            - Hesaplama "Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmelik" esas alınarak yapılmıştır.<br>
        </div>
    </div>
    """
    return mesaj

def su_depolama_degerlendir(data, emsal_orani=None):
    """
    Su depolama tesisi değerlendirme fonksiyonu (yıkama tesisi modülüne benzer sade ve HTML'li)
    """
    SU_DEPOLAMA_EMSAL_ORANI = emsal_orani if emsal_orani is not None else DEFAULT_SU_DEPOLAMA_EMSAL_ORANI
    try:
        # Standart parametre ismi: alan_m2 (fallback olarak diğerleri)
        arazi_alan = float(data.get('alan_m2', 0)) or float(data.get('arazi_buyuklugu_m2', 0)) or float(data.get('alan', 0))
        if arazi_alan < SU_DEPOLAMA_MIN_ARAZI_M2:
            sonuc = {
                'success': False,
                'izin_durumu': 'TESİS YAPILAMAZ',
                'su_depolama_pompaj_alani_m2': 0,
                'maksimum_emsal_alani_m2': arazi_alan * SU_DEPOLAMA_EMSAL_ORANI,
                'kalan_emsal_hakki_m2': 0,
                'emsal_kullanim_orani': 0,
                'hata_mesaji': f'Su depolama ve pompaj sistemi için minimum arazi büyüklüğü {SU_DEPOLAMA_MIN_ARAZI_M2} m² olmalıdır.',
                'emsal_orani': SU_DEPOLAMA_EMSAL_ORANI,
                'arazi_buyuklugu_m2': arazi_alan  # EKLENDI: Arazi büyüklüğü açık şekilde eklendi
            }
            sonuc['mesaj'] = _olustur_mesaj_su_depolama(sonuc)
            return sonuc
        maksimum_emsal_alani = arazi_alan * SU_DEPOLAMA_EMSAL_ORANI
        su_depolama_pompaj_alani = maksimum_emsal_alani
        kalan_emsal_hakki = maksimum_emsal_alani - su_depolama_pompaj_alani
        sonuc = {
            'success': True,
            'izin_durumu': 'TESİS YAPILABİLİR',
            'su_depolama_pompaj_alani_m2': su_depolama_pompaj_alani,
            'maksimum_emsal_alani_m2': maksimum_emsal_alani,
            'kalan_emsal_hakki_m2': kalan_emsal_hakki,
            'emsal_kullanim_orani': 100.0,
            'mesaj': f'Su depolama ve pompaj sistemi kurulabilir. Alan: {su_depolama_pompaj_alani:.0f} m²',
            'emsal_orani': SU_DEPOLAMA_EMSAL_ORANI,
            'arazi_buyuklugu_m2': arazi_alan  # EKLENDI: Arazi büyüklüğü açık şekilde eklendi
        }
        sonuc['mesaj'] = _olustur_mesaj_su_depolama(sonuc)
        return sonuc
    except Exception as e:
        sonuc = {
            'success': False,
            'izin_durumu': 'HATA',
            'hata_mesaji': f'Hesaplama sırasında hata oluştu: {str(e)}',
            'su_depolama_pompaj_alani_m2': 0,
            'maksimum_emsal_alani_m2': 0,
            'kalan_emsal_hakki_m2': 0,
            'emsal_kullanim_orani': 0,
            'emsal_orani': SU_DEPOLAMA_EMSAL_ORANI,
            'arazi_buyuklugu_m2': 0  # EKLENDI: Hata durumunda da arazi büyüklüğü gösterimi
        }
        sonuc['mesaj'] = _olustur_mesaj_su_depolama(sonuc)
        return sonuc