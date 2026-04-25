"""
Arıcılık Tesisi Hesaplama Modülü

Bu modül, genelge.md'deki kurallara göre arıcılık tesisi hesaplamalarını yapar.
Kural: 50 arılı kovana sahip arıcılık yapılması şartıyla, bal sağım/saklama ve 
arıcılık malzeme depolaması için bir işletmeye 50 metrekare kapalı alanda 
arıhane veya arı kışlatma evi yapılabilir.
İşletmeye ilave her 50 arılı kovanlık için ilave 10 metrekare alan eklenebilir.
"""

# Sabit değerler
EMSAL_ORANI = 0.20
MINIMUM_KOVANI_SAYISI = 50  # Minimum kovan sayısı
BASE_ALAN = 50  # İlk 50 kovan için temel alan (m²)
ADDITIONAL_ALAN_PER_50_KOVAN = 10  # Her ilave 50 kovan için ek alan (m²)

def _olustur_html_mesaj_aricilik(sonuc_data: dict) -> str:
    """
    Arıcılık hesaplama sonuçlarını HTML formatında tablo ve notlarla gösterir.
    """
    mesaj = """
    <style>
        .aricilik-sonuc {font-family: Arial, sans-serif;}
        .aricilik-sonuc h3 {color: #2563eb; margin-bottom: 15px;}
        .aricilik-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .aricilik-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .aricilik-sonuc th, .aricilik-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .aricilik-sonuc th {background-color: #f2f2f2;}
        .aricilik-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .aricilik-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .aricilik-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
    </style>
    <div class="aricilik-sonuc">
    """
    mesaj += f"<h3>ARICILIK TESİSİ DEĞERLENDİRMESİ</h3>"
    mesaj += '<div class="baslik">GENEL DURUM</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Arazi Büyüklüğü</th><td>{:.0f} m²</td></tr>'.format(sonuc_data.get("arazi_buyuklugu_m2", 0))
    mesaj += '<tr><th>Emsal Oranı</th><td>%{:.0f}</td></tr>'.format(sonuc_data.get("emsal_orani", EMSAL_ORANI)*100)
    mesaj += '<tr><th>Kullanılabilir Emsal Alanı</th><td>{:.2f} m²</td></tr>'.format(sonuc_data.get("emsal_m2", 0))
    mesaj += '<tr><th>Planlanan Kovan Sayısı</th><td>{}</td></tr>'.format(sonuc_data.get("kovan_sayisi", "-"))
    mesaj += '<tr><th>Gerekli Kapalı Alan</th><td>{} m²</td></tr>'.format(sonuc_data.get("gerekli_alan_m2", "-"))
    mesaj += '</table>'

    if sonuc_data.get("yapilanabilir"):
        mesaj += f'<div class="basarili"><b>SONUÇ: TESİS YAPILABİLİR</b><br>{sonuc_data.get("aciklama")}</div>'
    else:
        mesaj += f'<div class="hata"><b>SONUÇ: TESİS YAPILAMAZ</b><br>{sonuc_data.get("aciklama")}</div>'

    mesaj += '<div class="baslik">KAPASİTE ANALİZİ</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Bu araziye maksimum konulabilecek kovan sayısı</th><td>{} adet</td></tr>'.format(sonuc_data.get("maksimum_kovan_kapasitesi", 0))
    mesaj += '</table>'

    mesaj += '<div class="notlar">'
    mesaj += '<b>Arıcılık Tesisi Planlama Notları:</b><br>'
    mesaj += '- Minimum 50 arılı kovan şartı.<br>'
    mesaj += '- İlk 50 kovan için 50 m², her ilave 50 kovan için +10 m².<br>'
    mesaj += '- Emsal oranı: %{:.0f}.<br>'.format(sonuc_data.get("emsal_orani", EMSAL_ORANI)*100)
    mesaj += '- Hesaplama, Tarım Arazilerinin Korunması, Kullanılması ve Planlanmasına Dair Yönetmelik ve genelge hükümlerine göre yapılır.<br>'
    mesaj += '</div>'

    mesaj += '</div>'
    return mesaj

def aricilik_degerlendir(data, emsal_orani: float = None):
    """
    Arıcılık tesisi hesaplama API fonksiyonu
    
    Args:
        data: Hesaplama için gerekli veriler
            - arazi_buyuklugu_m2: Arazi büyüklüğü (m²)  
            - kovan_sayisi: Planlanan kovan sayısı (opsiyonel - girilmezse maksimum kapasite hesaplanır)
            
    Returns:
        dict: Hesaplama sonuçları
    """
    try:
        # Veri çıkarma
        arazi_buyuklugu_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        kovan_sayisi_input = data.get('kovan_sayisi')
        
        # Temel kontroller
        if arazi_buyuklugu_m2 <= 0:
            return {
                "success": False,
                "error": "Geçerli bir arazi büyüklüğü giriniz."
            }
        
        # Emsal oranını belirle
        kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
        emsal_m2 = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
        
        # Kovan sayısı belirleme
        hesaplama_modu = ""
        if kovan_sayisi_input and int(kovan_sayisi_input) > 0:
            # Kovan sayısı girilmiş - bu sayıya göre hesapla
            kovan_sayisi = int(kovan_sayisi_input)
            hesaplama_modu = "kovan_sayisi_bazli"
            
            if kovan_sayisi < MINIMUM_KOVANI_SAYISI:
                return {
                    "success": False,
                    "error": f"Arıcılık tesisi için minimum {MINIMUM_KOVANI_SAYISI} adet kovan gereklidir."
                }
        else:
            # Kovan sayısı girilmemiş - araziye göre maksimum kapasiteyi hesapla
            hesaplama_modu = "alan_bazli"
            if emsal_m2 >= BASE_ALAN:
                kalan_emsal = emsal_m2 - BASE_ALAN
                ek_kovan_grubu = int(kalan_emsal / ADDITIONAL_ALAN_PER_50_KOVAN)
                kovan_sayisi = MINIMUM_KOVANI_SAYISI + (ek_kovan_grubu * 50)
            else:
                kovan_sayisi = 0  # Minimum alan bile sağlanamıyor
        
        # Emsal hesaplama
        emsal_m2 = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
        
        # Gerekli kapalı alan hesaplama
        gerekli_alan = BASE_ALAN
        if kovan_sayisi > MINIMUM_KOVANI_SAYISI:
            ilave_kovan_sayisi = kovan_sayisi - MINIMUM_KOVANI_SAYISI
            ilave_50_li_grup_sayisi = (ilave_kovan_sayisi + 49) // 50  # Yukarı yuvarlama
            gerekli_alan += ilave_50_li_grup_sayisi * ADDITIONAL_ALAN_PER_50_KOVAN
        
        # Minimum emsal alan kontrolü
        if emsal_m2 < BASE_ALAN:
            max_kovan = 0
            aciklama = (
                f"Arazi büyüklüğü ve emsal oranı ile kullanılabilir alan ({emsal_m2:.2f} m²) "
                f"ilk 50 kovan için gerekli 50 m²'yi sağlamamaktadır.<br>"
                f"Bu araziye arıcılık tesisi kurulamaz.<br>"
                f"Bu araziye maksimum {max_kovan} kovan konulabilir."
            )
            sonuc = {
                "success": True,
                "yapilanabilir": False,
                "sonuc": "TESİS YAPILAMAZ",
                "aciklama": aciklama,
                "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
                "kovan_sayisi": "-",
                "gerekli_alan_m2": BASE_ALAN,
                "emsal_orani": kullanilacak_emsal_orani,
                "emsal_m2": emsal_m2,
                "maksimum_kovan_kapasitesi": max_kovan
            }
            sonuc["mesaj"] = _olustur_html_mesaj_aricilik(sonuc)
            return sonuc

        # Yapılabilirlik kontrolü
        if gerekli_alan > emsal_m2:
            max_kovan = MINIMUM_KOVANI_SAYISI + int((emsal_m2 - BASE_ALAN) // ADDITIONAL_ALAN_PER_50_KOVAN) * 50 if emsal_m2 >= BASE_ALAN else 0
            aciklama = (
                f"{kovan_sayisi} kovan için gereken kapalı alan ({gerekli_alan} m²) "
                f"emsal hakkı ({emsal_m2:.2f} m²) ile karşılanamıyor.<br>"
                f"Bu araziye maksimum {max_kovan} kovan konulabilir."
            )
            sonuc = {
                "success": True,
                "yapilanabilir": False,
                "sonuc": "TESİS YAPILAMAZ",
                "aciklama": aciklama,
                "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
                "kovan_sayisi": kovan_sayisi,
                "gerekli_alan_m2": gerekli_alan,
                "emsal_orani": kullanilacak_emsal_orani,
                "emsal_m2": emsal_m2,
                "maksimum_kovan_kapasitesi": max_kovan
            }
            sonuc["mesaj"] = _olustur_html_mesaj_aricilik(sonuc)
            return sonuc
        
        # Başarılı hesaplama
        kalan_alan = emsal_m2 - gerekli_alan
        # Maksimum kovan kapasitesi
        ilave_grup = int((emsal_m2 - BASE_ALAN) // ADDITIONAL_ALAN_PER_50_KOVAN) if emsal_m2 >= BASE_ALAN else 0
        maks_kovan_kapasitesi = MINIMUM_KOVANI_SAYISI + ilave_grup * 50

        # Hesaplama moduna göre açıklama
        if hesaplama_modu == "kovan_sayisi_bazli":
            aciklama = f"{kovan_sayisi} kovan için tesis kurulabilir.<br>Kalan emsal hakkı: {kalan_alan:.2f} m²"
        else:  # alan_bazli
            aciklama = f"Bu araziye maksimum {kovan_sayisi} kovan konulabilir.<br>Tüm emsal hakkı kullanılmıştır."

        sonuc = {
            "success": True,
            "yapilanabilir": True,
            "sonuc": f"TESİS YAPILABİLİR ({kovan_sayisi} ADET KOVAN KAPASİTELİ)",
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            "kovan_sayisi": kovan_sayisi,
            "gerekli_alan_m2": gerekli_alan,
            "emsal_orani": kullanilacak_emsal_orani,
            "emsal_m2": emsal_m2,
            "kalan_alan_m2": kalan_alan,
            "maksimum_kovan_kapasitesi": maks_kovan_kapasitesi,
            "aciklama": aciklama,
            "hesaplama_modu": hesaplama_modu
        }
        sonuc["mesaj"] = _olustur_html_mesaj_aricilik(sonuc)
        return sonuc
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Hesaplama hatası: {str(e)}"
        }

import logging
logger = logging.getLogger('calculations')

def aricilik_frontend_degerlendir(data: dict) -> dict:
    """
    Frontend'den gelen parametreleri backend formatına dönüştürerek arıcılık tesisi değerlendirmesi yapar
    Args:
        data: Frontend'den gelen veri (alan_m2, arazi_vasfi, vs.)
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    try:
        # Frontend parametrelerini backend formatına dönüştür
        alan_m2 = data.get('alan_m2') or data.get('arazi_buyuklugu_m2') or data.get('buyukluk_m2') or data.get('alan', 0)
        arazi_vasfi = data.get('arazi_vasfi', 'tarım')
        
        # Emsal oranı parametresini al (frontend'deki butonlardan gelen değer)
        emsal_orani = data.get('emsal_orani', None)
        emsal_turu = data.get('emsalTuru') or data.get('emsal_turu')
        if emsal_orani is None and emsal_turu:
            if emsal_turu in ['mutlak_dikili_8']:
                emsal_orani = 0.08
            elif emsal_turu in ['mutlak_dikili', 'mutlak', 'dikili']:
                emsal_orani = 0.05
            elif emsal_turu in ['marjinal', 'marjinal_tarim']:
                emsal_orani = 0.20
        
        # Kovan sayısı girilmemişse, araziye göre maksimum kapasiteyi hesapla
        kovan_sayisi = data.get('kovan_sayisi')
        if not kovan_sayisi:
            kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
            emsal_m2 = float(alan_m2) * kullanilacak_emsal_orani
            if emsal_m2 >= BASE_ALAN:
                kalan_emsal = emsal_m2 - BASE_ALAN
                ek_kovan_grubu = int(kalan_emsal / ADDITIONAL_ALAN_PER_50_KOVAN)
                kovan_sayisi = MINIMUM_KOVANI_SAYISI + (ek_kovan_grubu * 50)
            else:
                kovan_sayisi = MINIMUM_KOVANI_SAYISI
        
        backend_data = {
            'arazi_buyuklugu_m2': alan_m2,
            'kovan_sayisi': kovan_sayisi
        }
        result = aricilik_degerlendir(backend_data, emsal_orani)
        if result.get('success'):
            return {
                'success': True,
                'results': {
                    'ana_mesaj': result.get('mesaj', ''),
                    'mesaj': result.get('mesaj', ''),
                    'izin_durumu': 'izin_verilebilir' if result.get('yapilanabilir') else 'izin_verilemez',
                    'yapilanabilir': result.get('yapilanabilir', False),
                    'arazi_alani_m2': result.get('arazi_alani_m2', 0),
                    'emsal_orani': result.get('emsal_orani', 0.2)
                },
                'message': 'Hesaplama başarıyla tamamlandı'
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Arıcılık tesisi hesaplama hatası'),
                'mesaj': result.get('error', 'Arıcılık tesisi hesaplama hatası'),
                'izin_durumu': 'izin_verilemez'
            }
    except Exception as e:
        logger.error(f"Arıcılık tesisi frontend wrapper error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'mesaj': f'Arıcılık tesisi hesaplama sırasında hata oluştu: {str(e)}',
            'izin_durumu': 'izin_verilemez'
        }
