"""
Su Kuyuları Hesaplama Modülü - Kapalı Su Havzası Kontrolü

Bu modül sadece kapalı su havzası kontrolü yapar ve su kuyusu yapılabilir mi kararını verir.
HTML çıktı ipek böcekçiliği modülündeki gibi tablo ve notlar ile gösterilir.
"""

def _olustur_html_mesaj_su_kuyusu(sonuc_data: dict) -> str:
    """
    Su kuyusu hesaplama sonuçlarını HTML formatında okunabilir bir mesaja dönüştürür.
    Tablo ve notlar ipek böcekçiliği modülüne benzer şekilde revize edilmiştir.
    """
    mesaj = """
    <style>
        .su-kuyusu-sonuc {font-family: Arial, sans-serif;}
        .su-kuyusu-sonuc h3 {color: #2563eb; margin-bottom: 15px;}
        .su-kuyusu-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .su-kuyusu-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .su-kuyusu-sonuc th, .su-kuyusu-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .su-kuyusu-sonuc th {background-color: #f2f2f2;}
        .su-kuyusu-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .su-kuyusu-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .su-kuyusu-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .su-kuyusu-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
    </style>
    <div class="su-kuyusu-sonuc">
    """

    mesaj += f"<h3>SU KUYUSU KONTROL DEĞERLENDİRMESİ</h3>"
    mesaj += '<div class="baslik">GENEL DURUM</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Kapalı Su Havzası Durumu</th><th>Su Kuyusu İzin Durumu</th></tr>'
    mesaj += f'<tr><td>{"İçinde" if sonuc_data.get("kapali_su_havzasi_icinde") else "Dışında"}</td><td>{sonuc_data.get("izin_durumu")}</td></tr>'
    mesaj += '</table>'

    # Sonuç durumuna göre mesaj türünü belirle
    if sonuc_data.get("izin_durumu") == "TESİS YAPILAMAZ":
        aciklama = sonuc_data.get("aciklama", "").replace("\n", "<br>")
        mesaj += f'<div class="hata"><b>SONUÇ: SU KUYUSU YAPILAMAZ</b><br>{aciklama}</div>'
    else:
        mesaj += f'<div class="basarili"><b>SONUÇ: SU KUYUSU YAPILABİLİR</b><br>{sonuc_data.get("aciklama")}</div>'

    mesaj += '<div class="notlar">'
    mesaj += '<b>Su Kuyusu Planlama Notları:</b><br>'
    mesaj += '- Bu değerlendirme yalnızca Devlet Su İşleri Genel Müdürlüğü tarafından ilan edilen kapalı su havzası kontrolüne yöneliktir.<br>'
    mesaj += '- Kapalı su havzası içinde yer alan noktalarda su kuyusu açılması mümkün değildir.<br>'
    mesaj += '- Kapalı su havzası dışında ise su kuyusu açılması mümkündür.<br>'
    mesaj += '- Sonuç tavsiye niteliğindedir. Kesin başvuru için ilgili kurumlara danışınız.'
    mesaj += '</div>'

    mesaj += '</div>'
    return mesaj

def su_kuyulari_degerlendir(data):
    """
    Su kuyuları değerlendirme fonksiyonu - Sadece kapalı su havzası kontrolüne göre karar verir.
    """
    try:
        kapali_su_havzasi_icinde = (
            bool(data.get('kapaliSuHavzasiIcinde')) or
            (str(data.get('yas_kapali_alan_durumu', '')).lower() == 'içinde')
        )

        if kapali_su_havzasi_icinde:
            sonuc = {
                'success': False,
                'izin_durumu': 'TESİS YAPILAMAZ',
                'kapali_su_havzasi_icinde': True,
                'aciklama': "Devlet Su İşleri Genel Müdürlüğü tarafından kapalı su havzası olarak ilan edilen su kısıtının bulunduğu yerlerde su kuyusu açılması mümkün değildir."
            }
            sonuc['html_mesaj'] = _olustur_html_mesaj_su_kuyusu(sonuc)
            return sonuc

        sonuc = {
            'success': True,
            'izin_durumu': 'TESİS YAPILABİLİR',
            'kapali_su_havzasi_icinde': False,
            'aciklama': "Seçtiğiniz nokta kapalı su havzası dışında olduğundan su kuyusu açılması mümkündür."
        }
        sonuc['html_mesaj'] = _olustur_html_mesaj_su_kuyusu(sonuc)
        return sonuc

    except Exception as e:
        sonuc = {
            'success': False,
            'izin_durumu': 'HATA',
            'aciklama': f'Hesaplama sırasında hata oluştu: {str(e)}'
        }
        sonuc['html_mesaj'] = _olustur_html_mesaj_su_kuyusu(sonuc)
        return sonuc
