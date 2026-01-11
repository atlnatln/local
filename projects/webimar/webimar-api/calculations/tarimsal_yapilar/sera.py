"""
Bu modül, sera ve ilgili yapılar için kuralları uygulayan fonksiyonları içerir.
GES bilgilendirme odaklı hesaplamalar da bu modülde bulunur.
"""
import json
import logging

# Sera için sabitler constants.py'den buraya taşındı.
SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2 = 20
SERA_IDARI_BINA_SERA_ALANINA_ORANI_MAX = 0.05  # %5
SERA_GES_ZEMINE_PROJE_ALANINA_ORANI_MAX = 0.015  # %1.5
# SERA_VARSAYILAN_ALAN_ORANI bu modülde doğrudan kullanılmıyor, ana_modul.py'de kullanılıyor.

# Logger tanımla
logger = logging.getLogger(__name__)

def _olustur_html_mesaj_sera(sonuc_data: dict, toplam_proje_alani_m2: float, planlanan_sera_alani_m2: float) -> str:
    """
    Sera projesi hesaplama sonuçlarını HTML tablo formatında okunabilir bir mesaja dönüştürür.
    """
    # CSS stilleri
    mesaj_html = """
    <style>
        .sera-sonuc {font-family: Arial, sans-serif;}
        .sera-sonuc h3 {color: #2563eb; margin-bottom: 15px;}
        .sera-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .sera-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .sera-sonuc th, .sera-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .sera-sonuc th {background-color: #f2f2f2;}
        .sera-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .sera-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .sera-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
        .sera-sonuc .bag-evi-bildirim {color: #084298; background-color: #cff4fc; padding: 15px; border-radius: 4px; margin: 15px 0; border-left: 4px solid #0a58ca;}
    </style>
    <div class="sera-sonuc">
    <h3>SERA PROJESİ DEĞERLENDİRMESİ</h3>"""
    
    # Giriş bilgileri tablosu
    mesaj_html += '<div class="baslik">PROJE BİLGİLERİ</div>'
    mesaj_html += '<table>'
    mesaj_html += f'<tr><th>Toplam Proje Alanı</th><td>{toplam_proje_alani_m2:,.0f} m²</td></tr>'
    mesaj_html += f'<tr><th>Planlanan Sera Alanı</th><td>{planlanan_sera_alani_m2:,.0f} m²</td></tr>'
    mesaj_html += '</table>'

    # İdari ve teknik bina durumu
    idari_bina_durumu_metin = sonuc_data.get('idari_bina_durumu_metin', 'Hesaplanamadı.')
    idari_bina_izin_alan = sonuc_data.get('idari_bina_izin_verilen_alan_m2', 0)
    
    mesaj_html += '<div class="baslik">İDARİ VE TEKNİK BİNA</div>'
    mesaj_html += '<table>'
    mesaj_html += f'<tr><th>Durum</th><td>{idari_bina_durumu_metin}</td></tr>'
    mesaj_html += f'<tr><th>Maksimum İzin Verilen Alan</th><td>{idari_bina_izin_alan:,.0f} m²</td></tr>'
    mesaj_html += '</table>'

    # Sonuç durumu
    if "izin_durumu" in sonuc_data:
        if sonuc_data["izin_durumu"] == "izin_verilebilir":
            mesaj_html += '<div class="basarili">'
            mesaj_html += '<b>SONUÇ: SERA YAPIMINA İZİN VERİLEBİLİR</b><br>'
            mesaj_html += f'Planlanan {planlanan_sera_alani_m2:,.0f} m² sera alanı ve {idari_bina_izin_alan:,.0f} m² idari/teknik bina için yapılaşma uygundur.'
            mesaj_html += '</div>'
        else:
            mesaj_html += '<div class="hata">'
            mesaj_html += f'<b>SONUÇ: {sonuc_data.get("mesaj", "Detaylı bilgiye ulaşılamadı.")}</b>'
            mesaj_html += '</div>'

    # Bağ Evi Hakkı Bildirim (Sera/Örtü altı alanı 3000m² ve üzerinde ise)
    if planlanan_sera_alani_m2 >= 3000:
        mesaj_html += '''
        <div class="bag-evi-bildirim">
            <h4 style="color: #084298; margin-top: 0; margin-bottom: 10px;">🏡 BAĞ EVİ HAKKI BİLDİRİMİ</h4>
            <p style="margin-bottom: 10px;"><strong>Sera/örtü altı alanınız 3.000 m² ve üzerinde olduğu için bağ evi yapma hakkınız bulunmaktadır.</strong></p>
            <p style="margin-bottom: 10px;">Bağ evi özellikleri:</p>
            <ul style="margin-bottom: 10px;">
                <li>Maksimum taban alanı: 75 m²</li>
                <li>Maksimum toplam alan: 150 m² (2 katlı yapılabilir)</li>
                <li>Örtü altı tarım ve sera alanları için minimum 3.000 m² alan gereklidir</li>
            </ul>
            <p style="margin-bottom: 0; font-size: 14px; color: #495057;">
                <em>Not: Bağ evi yapımı için ayrıca başvuru yapmanız gerekir. Bu hesaplama sadece hak kazandığınızı bildirmektedir.</em>
            </p>
        </div>
        '''

    # GES bilgilendirmesi
    ges_bilgisi_metin = sonuc_data.get('ges_bilgisi_metin', 'GES hakkında bilgi bulunmamaktadır.')
    if ges_bilgisi_metin and ges_bilgisi_metin != 'GES hakkında bilgi bulunmamaktadır.':
        mesaj_html += '<div class="notlar">'
        mesaj_html += '<b>Güneş Enerjisi Santrali (GES) Bilgilendirmesi:</b><br>'
        ges_bilgisi_html = ges_bilgisi_metin.replace("\n- ", "<br>• ").replace("\n", "<br>")
        if ges_bilgisi_metin.startswith("Güneş Enerjisi Santrali (GES) Hakkında Genel Bilgi:\n"):
            ges_bilgisi_html = ges_bilgisi_html.replace("Güneş Enerjisi Santrali (GES) Hakkında Genel Bilgi:<br>", "")
        mesaj_html += ges_bilgisi_html
        mesaj_html += '</div>'
    
    mesaj_html += '</div>'
    return mesaj_html

def sera_projesi_bilgilendirme(
    toplam_proje_alani_m2: float,
    planlanan_sera_alani_m2: float,
) -> dict:
    """
    Sera projesi için idari bina kurallarını hesaplar ve GES hakkında genel bilgi verir.
    Bu fonksiyon artık doğrudan HTML mesajı üretmeyecek, ham verileri döndürecek.
    """
    sonuclar = {
        "idari_bina_izin_verilen_alan_m2": 0.0,
        "idari_bina_durumu_metin": "", # Düz metin olarak durum
        "ges_bilgisi_metin": ""      # Düz metin olarak GES bilgisi
    }

    maks_idari_bina_hesaplanan_alan_m2 = planlanan_sera_alani_m2 * SERA_IDARI_BINA_SERA_ALANINA_ORANI_MAX
    
    if maks_idari_bina_hesaplanan_alan_m2 < SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2:
        sonuclar["idari_bina_izin_verilen_alan_m2"] = SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2
        sonuclar["idari_bina_durumu_metin"] = (
            f"Planladığınız {planlanan_sera_alani_m2:,.2f} m² sera alanı için hesaplanan %{SERA_IDARI_BINA_SERA_ALANINA_ORANI_MAX*100:.0f}'lik oran ({maks_idari_bina_hesaplanan_alan_m2:,.2f} m²), "
            f"minimum {SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2:,.0f} m² şartının altında kaldığından, "
            f"yapabileceğiniz idari ve teknik bina alanı en fazla {SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2:,.2f} m² olacaktır."
        ).replace(",",".")
    else:
        sonuclar["idari_bina_izin_verilen_alan_m2"] = maks_idari_bina_hesaplanan_alan_m2
        sonuclar["idari_bina_durumu_metin"] = (
            f"Planladığınız {planlanan_sera_alani_m2:,.2f} m² sera alanı için, "
            f"bu alanın en fazla %{SERA_IDARI_BINA_SERA_ALANINA_ORANI_MAX*100:.0f}'i kadar (yani {maks_idari_bina_hesaplanan_alan_m2:,.2f} m²) "
            f"ve en az {SERA_MIN_IDARI_TEKNIK_BINA_ALANI_M2:,.0f} m² olmak şartıyla idari ve teknik bina yapabilirsiniz. "
            f"Bu durumda maksimum {maks_idari_bina_hesaplanan_alan_m2:,.2f} m² yapabilirsiniz."
        ).replace(",",".")

    logger.info(f"Sera idari bina hesaplaması: Sera alanı={planlanan_sera_alani_m2} m², " 
               f"maks idari bina={sonuclar['idari_bina_izin_verilen_alan_m2']} m²")

    sonuclar["ges_bilgisi_metin"] = (
        "Güneş Enerjisi Santrali (GES) Hakkında Genel Bilgi:\n"
        "- Sera üzerine GES kurulması: Bitkisel üretim tekniği açısından uygun olmaması ve serada yapılan bitkisel üretime olumsuz etkisi nedeniyle genellikle uygun görülmemektedir.\n"
        "- Zemine GES Kurulumu: Eğer arazinizin sınıfı 'marjinal tarım arazisi (TA)' ise, talep edilmesi durumunda proje alanınızın en fazla "
        f"%{SERA_GES_ZEMINE_PROJE_ALANINA_ORANI_MAX*100:.1f}'ine zemine GES kurulmasına izin verilebilir. Bu durum, arazinizin resmi sınıflandırmasına bağlıdır."
    )
    
    # Özet mesaj artık _olustur_html_mesaj_sera tarafından oluşturulacak.
    # Bu fonksiyon sadece ham verileri döndürecek.
    return sonuclar

def sera_degerlendir(data):
    """
    Sera hesaplama fonksiyonu - API endpoint için
    
    Args:
        data: Form verilerini içeren dict
        
    Returns:
        dict: Hesaplama sonuçları
    """
    try:
        # Form verilerini parse et - doğru field adlarını kullan
        arazi_alani = float(data.get('arazi_buyuklugu_m2', 0))
        sera_alani = float(data.get('sera_alani_m2', arazi_alani * 0.8))  # Varsayılan %80
        
        # Arazi bilgileri
        arazi_bilgileri = {
            "buyukluk_m2": arazi_alani,
            "ana_vasif": data.get('arazi_vasfi', 'TA'),
        }
        
        # Sera bilgileri
        sera_bilgileri = {
            "sera_alani_m2": sera_alani,
        }
        
        # Ana hesaplama
        sonuc = hesapla_sera_yapilasma_kurallari(arazi_bilgileri, sera_bilgileri)
        
        # API response formatına dönüştür
        response = {
            "success": True,
            "mesaj": sonuc["mesaj"],
            "bag_evi_hakki": sonuc.get("bag_evi_hakki", False),
            "sera_alani_m2": sera_alani,
            "arazi_alani_m2": arazi_alani
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Sera hesaplama hatası: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Sera hesaplama sırasında hata oluştu"
        }

def hesapla_sera_yapilasma_kurallari(arazi_bilgileri, sera_bilgileri):
    """
    Sera yapılaşma kurallarını hesaplar ve değerlendirir.
    HTML mesajını _olustur_html_mesaj_sera kullanarak oluşturur.
    """
    arazi_buyuklugu_m2 = arazi_bilgileri.get("buyukluk_m2", 0)
    arazi_vasfi = arazi_bilgileri.get("ana_vasif", "belirlenmemiş")
    planlanan_sera_alani_m2 = sera_bilgileri.get("sera_alani_m2", 0)
    
    logger.info(f"Sera bilgileri: {json.dumps(sera_bilgileri, default=str)}")
    
    bilgilendirme_verileri = sera_projesi_bilgilendirme(
        toplam_proje_alani_m2=arazi_buyuklugu_m2,
        planlanan_sera_alani_m2=planlanan_sera_alani_m2,
    )
    
    logger.info(f"İdari bina izin verilen alan: {bilgilendirme_verileri['idari_bina_izin_verilen_alan_m2']} m²")
    logger.info(f"İdari bina durumu (metin): {bilgilendirme_verileri['idari_bina_durumu_metin']}")
    
    sonuc = {
        "izin_durumu": "izin_verilebilir",
        "mesaj": "", # Bu ana HTML mesajı olacak
        "maksimum_taban_alani": planlanan_sera_alani_m2, # Bu seranın taban alanı
        "maksimum_idari_bina_alani": bilgilendirme_verileri["idari_bina_izin_verilen_alan_m2"],
        # Ham verileri de ekleyelim, HTML mesajı oluşturulurken kullanılacak
        "idari_bina_durumu_metin": bilgilendirme_verileri["idari_bina_durumu_metin"],
        "ges_bilgisi_metin": bilgilendirme_verileri["ges_bilgisi_metin"],
        "idari_bina_izin_verilen_alan_m2": bilgilendirme_verileri["idari_bina_izin_verilen_alan_m2"], # _olustur_html_mesaj_sera için
        "uyari_mesaji_ozel_durum": "", # Gerekirse doldurulabilir
        "sonraki_adim_bilgisi": "",    # Gerekirse doldurulabilir
        # Bağ evi hakkı bilgisi
        "bag_evi_hakki": planlanan_sera_alani_m2 >= 3000,
        "sera_alani_m2": planlanan_sera_alani_m2
    }
    
    # HTML mesajını oluştur
    # ana_modul.py'den gelen genel mesajı da dikkate alabiliriz, şimdilik sadece sera özelinde oluşturalım.
    # ana_modul.py'deki mesaj, bu mesajın bir parçası olarak eklenebilir veya ayrı yönetilebilir.
    # Şimdilik, ana_modul.py'nin kendi mesajını koruduğunu varsayalım ve bu mesajı daha çok detay olarak düşünelim.
    # Ancak, idealde tek bir kapsamlı HTML mesajı olmalı.
    # Bu yüzden, ana_modul.py'nin sonuc["mesaj"]'ını buraya aktarıp birleştirebiliriz.
    # Ya da ana_modul.py bu fonksiyondan dönen mesajı direkt kullanır.
    # İkinci yaklaşım daha temiz.
    
    # `sonuc` sözlüğünü _olustur_html_mesaj_sera'ya gönderiyoruz.
    # Bu fonksiyon, `sonuc` içindeki `izin_durumu` gibi anahtar bilgilere de erişebilir.
    sonuc["mesaj"] = _olustur_html_mesaj_sera(sonuc, arazi_buyuklugu_m2, planlanan_sera_alani_m2)
    
    # ana_modul.py'nin sonraki_adim_bilgisi'ni de bu HTML mesajına dahil edebiliriz.
    # Şimdilik, ana_modul.py'nin bu alanı ayrıca yönettiğini varsayalım.
    # sonuc["sonraki_adim_bilgisi"] = "Detaylar yukarıdaki değerlendirme raporunda belirtilmiştir." 
    # Bu satır yerine, _olustur_html_mesaj_sera'nın bu bilgiyi zaten içerdiğini varsayıyoruz.

    logger.info(f"Sera kuralları sonuç (HTML mesajı dahil): {json.dumps(sonuc, default=str, ensure_ascii=False)}")
    
    return sonuc
