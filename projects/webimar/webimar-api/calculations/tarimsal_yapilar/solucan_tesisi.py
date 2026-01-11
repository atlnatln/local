"""
Solucan Gübresi Üretim Tesisi için Emsal ve Kapasite Hesaplama Modülü

Bu modül, solucan ve solucan gübresi üretim tesisi için arazi büyüklüğüne göre:
- Zorunlu müştemilat alanını (detaylı dağılımı ile)
- Üretim hattı için kullanılabilir alanı
- Tesisin kısıtlarını ve kapasitesini
otomatik olarak hesaplar ve anlamlı bir çıktı üretir.
"""
import math

# Temel Kurallar ve Sabitler
EMSAL_ORANI = 0.20
ORTA_URETIM_HATTI_ALANI = 300  # m² (ör: 15 ton/gün kapasiteli hat için)
REFERANS_KAPASITE = 15  # ton/gün (referans kapasitesi)
MINIMUM_ARAZI_BUYUKLUGU = 550  # m² (minimum arazi büyüklüğü - senaryolardan güncellendi)

# Kapasite dönüşüm faktörü: hayvansal gübre girdi -> solucan gübresi çıktı
CIKTI_DONUSUM_FAKTORU = 0.467  # 15 ton girdi -> 7 ton çıktı

# Referans kapasitedeki (15 ton/gün) müştemilat büyüklükleri
REFERANS_MUSTEMILAT = {
    "wc_dus": {"isim": "WC ve duş", "alan": 15, "min_alan": 5, "buyume_faktoru": 0.7, "max_alan": 150},
    "temiz_alan": {"isim": "Temiz alan (giriş-çıkış)", "alan": 25, "min_alan": 6, "buyume_faktoru": 1.0},
    "kirli_alan": {"isim": "Kirli alan (giriş-çıkış)", "alan": 25, "min_alan": 6, "buyume_faktoru": 1.0},
    "kompost_alani": {"isim": "Kompost hazırlama ve karıştırma alanı", "alan": 90, "min_alan": 15, "buyume_faktoru": 1.5},
    "isil_islem": {"isim": "Isıl işlem ünitesi", "alan": 25, "min_alan": 5, "buyume_faktoru": 1.0},
    "paketleme": {"isim": "Paketleme ve etiketleme ünitesi", "alan": 30, "min_alan": 4, "buyume_faktoru": 1.5},
    "depolama": {"isim": "Bitmiş ürün depolama alanı", "alan": 40, "min_alan": 5, "buyume_faktoru": 1.5},
    "giyinme": {"isim": "Giyinme-soyunma odası", "alan": 10, "min_alan": 4, "buyume_faktoru": 0.7, "max_alan": 150},
    "yemekhane": {"isim": "Yemekhane/Dinlenme alanı", "alan": 20, "min_alan": 5, "buyume_faktoru": 0.7, "min_kapasite": 15, "max_alan": 300},
    "buro": {"isim": "Büro/Ofis", "alan": 15, "min_alan": 4, "buyume_faktoru": 0.7, "max_alan": 250}
}

# Farklı kapasite aralıkları için ölçek tanımları
KAPASITE_OLCEKLERI = [
    {"min": 1, "max": 3, "adi": "Mikro Ölçekli"},
    {"min": 3, "max": 8, "adi": "Küçük Ölçekli"},
    {"min": 8, "max": 12, "adi": "Geçiş Ölçekli"},
    {"min": 12, "max": 20, "adi": "Orta Ölçekli"},
    {"min": 20, "max": 45, "adi": "Büyük Ölçekli"},
    {"min": 45, "max": 80, "adi": "Endüstriyel Ölçekli"},
    {"min": 80, "max": 999, "adi": "Büyük Endüstriyel"}
]

def _olustur_html_mesaj_solucan(sonuc_data: dict, arazi_buyuklugu_m2: float, emsal_orani: float = None) -> str:
    """
    Solucan tesisi hesaplama sonuçlarını HTML formatında okunabilir bir mesaja dönüştürür.
    """
    # Dinamik emsal oranını kullan veya varsayılan değeri al
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    # CSS stillerini dahil et
    mesaj_html = """
    <style>
        .solucan-sonuc {font-family: Arial, sans-serif; max-width: 100%; margin: 0 auto;}
        .solucan-sonuc h3 {color: #558B2F; margin-bottom: 15px; font-size: 1.4em;}
        .solucan-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px; color: #33691E;}
        .solucan-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.2);}
        .solucan-sonuc th, .solucan-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .solucan-sonuc th {background-color: #f1f8e9; color: #33691E;}
        .solucan-sonuc .uretim {background-color: #dcedc8;}
        .solucan-sonuc .mustemilat {background-color: #f1f8e9;}
        .solucan-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .solucan-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .solucan-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .solucan-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
        .solucan-sonuc .olcek {font-size: 1.1em; color: #33691E; font-weight: bold; margin: 5px 0;}
        .solucan-sonuc .ozet-alan {background-color: #f9f9f9; padding: 10px; border-radius: 4px; margin-bottom: 10px;}
    </style>
    <div class="solucan-sonuc">
    """
    
    mesaj_html += f"<h3>SOLUCAN GÜBRESİ ÜRETİM TESİSİ DEĞERLENDİRMESİ</h3>"
    
    # Arazi ve emsal bilgisi
    mesaj_html += f"<p><b>Arazi Büyüklüğü:</b> {arazi_buyuklugu_m2:,.2f} m²<br>".replace(",", ".")
    
    if sonuc_data.get("izin_durumu") == "izin_verilemez":
        mesaj_html += f'<div class="hata"><b>SONUÇ: TESİS YAPILAMAZ</b><br>{sonuc_data.get("mesaj_metin", "")}</div>'
    else:
        emsal_hakki = sonuc_data.get('emsal_hakki', 0)
        max_yapilasma_alani_m2 = sonuc_data.get('max_yapilasma_alani_m2', 0)
        
        mesaj_html += f"<b>İzin Verilen Toplam Emsal (%{kullanilacak_emsal_orani*100:.0f}):</b> {emsal_hakki:,.2f} m²<br>".replace(",", ".")
        
        # Ölçek bilgisi ekle
        kapasite = sonuc_data.get('gunluk_kapasite_ton', 0)
        olcek_adi = "Belirsiz"
        for olcek in KAPASITE_OLCEKLERI:
            if olcek["min"] <= kapasite <= olcek["max"]:
                olcek_adi = olcek["adi"]
                break
                
        if kapasite > 0:
            mesaj_html += f'<div class="olcek">Tesis Ölçeği: {olcek_adi} ({kapasite:.1f} ton/gün)</div>'
        
        # Günlük kapasite bilgisi
        cikti_kapasite = kapasite * CIKTI_DONUSUM_FAKTORU
        if kapasite > 0:
            mesaj_html += f'<div class="ozet-alan">'
            mesaj_html += f'<b>Kapasite Özeti:</b><br>'
            mesaj_html += f'- Günlük Gübre Girdi: {kapasite:.1f} ton/gün<br>'
            mesaj_html += f'- Günlük Solucan Gübresi Çıktı: {cikti_kapasite:.1f} ton/gün<br>'
            mesaj_html += f'- Referans Kapasite Oranı: %{(kapasite/REFERANS_KAPASITE)*100:.0f}<br>'
            mesaj_html += f'</div>'
        
        # Sonuç başlığı
        if sonuc_data.get("uretim_hatti_alani", 0) < 10:
            mesaj_html += f'<div class="uyari"><b>SONUÇ: TESİS YAPILABİLİR (ÜRETİM ALANI YETERSİZ)</b><br>{sonuc_data.get("mesaj_metin", "")}</div>'
        else:
            mesaj_html += f'<div class="basarili"><b>SONUÇ: TESİS YAPILABİLİR</b><br>{sonuc_data.get("mesaj_metin", "")}</div>'
        
        # Alan kullanım tablosu
        mesaj_html += '<div class="baslik">TESİS ALANLARI</div>'
        mesaj_html += '<table>'
        mesaj_html += '<tr><th>Alan Türü</th><th>Büyüklük (m²)</th></tr>'
        
        mustemilat_toplam_alani = sonuc_data.get('mustemilat_toplam_alani', 0)
        uretim_hatti_alani = sonuc_data.get('uretim_hatti_alani', 0)
        
        # Üretim alanı
        mesaj_html += '<tr class="uretim">'
        mesaj_html += f'<td>Asıl Üretim Alanı</td>'
        mesaj_html += f'<td>{uretim_hatti_alani:.2f}</td>'
        mesaj_html += '</tr>'
        
        # Müştemilat detayları
        for ad, alan in sonuc_data.get("mustemilat_detaylari", []):
            mesaj_html += '<tr class="mustemilat">'
            mesaj_html += f'<td>{ad}</td>'
            mesaj_html += f'<td>{alan:.2f}</td>'
            mesaj_html += '</tr>'
        
        # Toplam müştemilat alanı
        mesaj_html += '<tr style="font-weight: bold;">'
        mesaj_html += f'<td>Toplam Müştemilat Alanı</td>'
        mesaj_html += f'<td>{mustemilat_toplam_alani:.2f}</td>'
        mesaj_html += '</tr>'
        
        # Toplam yapı alanı
        toplam_yapi_alani = mustemilat_toplam_alani + uretim_hatti_alani
        mesaj_html += '<tr style="font-weight: bold; background-color: #e8f5e9;">'
        mesaj_html += f'<td>TOPLAM YAPI ALANI</td>'
        mesaj_html += f'<td>{toplam_yapi_alani:.2f}</td>'
        mesaj_html += '</tr>'
        
        mesaj_html += '</table>'
        
        # Kalan emsal
        kalan_emsal = emsal_hakki - toplam_yapi_alani
        mesaj_html += f'<p><b>Kalan Emsal:</b> {kalan_emsal:.2f} m²</p>'
        
        # Emsal kullanım oranı
        emsal_kullanim_orani = (toplam_yapi_alani / emsal_hakki) * 100 if emsal_hakki > 0 else 0
        mesaj_html += f'<p><b>Emsal Kullanım Oranı:</b> %{emsal_kullanim_orani:.1f}</p>'

    # Notlar bölümü
    mesaj_html += '<div class="notlar">'
    mesaj_html += '<b>Solucan Gübresi Üretim Tesisi Planlama Notları:</b><br>'
    mesaj_html += '- Solucan gübresi üretim tesislerinde referans kapasite: 15 ton/gün hayvansal gübre girdi → 7 ton/gün solucan gübresi çıktı<br>'
    mesaj_html += '- Kapasite artışına göre müştemilat alanları oransal olarak büyür (büyüme faktörleri: WC, büro ve sosyal alanlar için 0.7, temel üretim alanları için 1.0, depolama ve paketleme için 1.5)<br>'
    mesaj_html += '- Emsal oranı %20\'dir (arazi alanının %20\'si kadar yapılaşma izni)<br>'
    mesaj_html += '- Tesiste bakıcı evi hesaplamalara dahil edilmemiştir<br>'
    mesaj_html += '- Bu değerlendirme tavsiye niteliğindedir ve resmi başvurularda ilgili kurumların görüşleri esastır.'
    mesaj_html += '</div>'
    
    mesaj_html += '</div>'
    return mesaj_html

# Geriye dönük uyumlu fonksiyonlar - ana_modul.py için gerekli
def toplam_mustemilat_alani():
    """
    Geriye dönük uyumlu fonksiyon - parametresiz versiyon
    Müştemilat listesindeki alanların toplamını döndürür.
    """
    # Sabit bir referans değeri kullanarak sabitleri döndür
    kapasite = REFERANS_KAPASITE  # Referans kapasiteyi kullan
    # Referans kapasite için asıl üretim alanını hesapla
    ref_asil_uretim_alani = hesapla_asil_uretim_alani(kapasite)
    mustemilat = hesapla_mustemilat_alanlari(kapasite, ref_asil_uretim_alani)
    return mustemilat["toplam_alan"]

def hesapla_solucan_tesisi(arazi_buyuklugu_m2: float, minimum_arazi_buyuklugu: float = None, emsal_orani: float = None):
    """
    Geriye dönük uyumlu fonksiyon - bu fonksiyon ana_modul.py tarafından import edilmekte
    
    Args:
        arazi_buyuklugu_m2 (float): Arazinin metrekare cinsinden büyüklüğü
        minimum_arazi_buyuklugu (float): Minimum arazi büyüklüğü (kurala göre)
        emsal_orani (float): Dinamik emsal oranı (varsayılan: EMSAL_ORANI)
        
    Returns:
        dict: Solucan tesisi hesaplama sonuçlarını içeren sözlük
    """
    return hesapla_solucan_tesisi_v2(arazi_buyuklugu_m2, minimum_arazi_buyuklugu, emsal_orani)

# Ana fonksiyonu yeni isimle çağıralım, böylece geriye dönük uyumluluk korunur
def hesapla_solucan_tesisi_v2(arazi_buyuklugu_m2: float, minimum_arazi_buyuklugu: float = None, emsal_orani: float = None):
    """
    Solucan ve solucan gübresi üretim tesisi için yapılaşma kurallarını hesaplar.

    Args:
        arazi_buyuklugu_m2 (float): Arazinin metrekare cinsinden büyüklüğü
        minimum_arazi_buyuklugu (float): Minimum arazi büyüklüğü (kurala göre)
        emsal_orani (float): Dinamik emsal oranı (varsayılan: EMSAL_ORANI)
        
    Returns:
        dict: Solucan tesisi hesaplama sonuçlarını içeren sözlük
    """
    # Dinamik emsal oranını kullan veya varsayılan değere geri dön
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    # Sonuç şablonu
    sonuc = {
        "izin_durumu": "belirsiz",
        "mesaj": "", 
        "mesaj_metin": "", 
        "ana_mesaj_html": "", 
        "mustemilat_toplam_alani": 0,
        "mustemilat_detaylari": [],
        "emsal_hakki": 0,
        "max_yapilasma_alani_m2": 0,
        "uretim_hatti_alani": 0,
        "gunluk_kapasite_ton": 0,
        "mustemilat_yuzde": 0,
    }
    
    # Minimum arazi büyüklüğü kontrolü
    if minimum_arazi_buyuklugu is None:
        minimum_arazi_buyuklugu = MINIMUM_ARAZI_BUYUKLUGU
    
    if arazi_buyuklugu_m2 < minimum_arazi_buyuklugu:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["mesaj_metin"] = (
            f"Solucan ve solucan gübresi üretim tesisi için minimum {minimum_arazi_buyuklugu:,.0f} m² arazi gereklidir. "
            f"Arazinizi {arazi_buyuklugu_m2:,.2f} m² olduğundan yapılaşmaya izin verilememektedir."
        ).replace(",",".")
        sonuc["ana_mesaj_html"] = _olustur_html_mesaj_solucan(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
        sonuc["mesaj"] = sonuc["mesaj_metin"]
        return sonuc
    
    # Optimal kapasite hesaplayarak tam fonksiyona yönlendir
    # kapasite_ton = hesapla_optimal_kapasite(arazi_buyuklugu_m2)
    return hesapla_solucan_tesisi_helper(arazi_buyuklugu_m2, None, kullanilacak_emsal_orani)

def hesapla_solucan_tesisi_helper(arazi_buyuklugu_m2: float, kapasite_ton: float = None, emsal_orani: float = None):
    """
    Solucan ve solucan gübresi üretim tesisi için yapılaşma kurallarını hesaplar.

    Args:
        arazi_buyuklugu_m2 (float): Arazinin metrekare cinsinden büyüklüğü
        kapasite_ton (float, optional): İstenen kapasite ton/gün cinsinden. 
                                      None ise optimal değer hesaplanır.
        emsal_orani (float): Dinamik emsal oranı (varsayılan: EMSAL_ORANI)
        
    Returns:
        dict: Solucan tesisi hesaplama sonuçlarını içeren sözlük
    """
    # Dinamik emsal oranını kullan veya varsayılan değere geri dön
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    # Sonuç şablonu
    sonuc = {
        "izin_durumu": "belirsiz",
        "mesaj": "", 
        "mesaj_metin": "", 
        "ana_mesaj_html": "", 
        "mustemilat_toplam_alani": 0,
        "mustemilat_detaylari": [],
        "emsal_hakki": 0,
        "max_yapilasma_alani_m2": 0,
        "uretim_hatti_alani": 0,
        "gunluk_kapasite_ton": 0,
        "mustemilat_yuzde": 0,
    }
    
    # Minimum arazi büyüklüğü kontrolü
    if arazi_buyuklugu_m2 < MINIMUM_ARAZI_BUYUKLUGU:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["mesaj_metin"] = (
            f"Solucan ve solucan gübresi üretim tesisi için minimum {MINIMUM_ARAZI_BUYUKLUGU:,.0f} m² arazi gereklidir. "
            f"Araziniz {arazi_buyuklugu_m2:,.2f} m² olduğundan yapılaşmaya izin verilememektedir."
        ).replace(",",".")
        sonuc["ana_mesaj_html"] = _olustur_html_mesaj_solucan(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
        sonuc["mesaj"] = sonuc["mesaj_metin"]
        return sonuc
    
    # Emsal hesabı - dinamik emsal oranını kullan
    emsal_hakki = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
    sonuc["emsal_hakki"] = emsal_hakki
    sonuc["max_yapilasma_alani_m2"] = emsal_hakki
    
    # Kapasite belirtilmemişse optimal değeri hesapla (emsal hakkına göre!)
    if kapasite_ton is None:
        kapasite_ton = hesapla_optimal_kapasite_emsale_gore(emsal_hakki)
    
    sonuc["gunluk_kapasite_ton"] = kapasite_ton
    
    # Asıl üretim alanını hesapla (müştemilat hesaplamasından önce)
    if kapasite_ton > 0:
        asil_uretim_alani = hesapla_asil_uretim_alani(kapasite_ton)
    else:
        asil_uretim_alani = 0
    
    # Müştemilat alanları ve toplam alanı hesapla
    # asil_uretim_alani parametresini müştemilat hesaplamasına gönder
    mustemilat = hesapla_mustemilat_alanlari(kapasite_ton, asil_uretim_alani)
    
    sonuc["mustemilat_detaylari"] = mustemilat["mustemilat_listesi"]
    sonuc["mustemilat_toplam_alani"] = mustemilat["toplam_alan"]
    
    # Toplam alan
    toplam_alan = mustemilat["toplam_alan"] + asil_uretim_alani
    
    # Emsal alanı kontrol et
    if emsal_hakki < mustemilat["toplam_alan"]:
        # Sadece müştemilatlar için bile alan yeterli değil
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["mustemilat_yuzde"] = 100
        sonuc["uretim_hatti_alani"] = 0
        
        # Mevcut emsale sığan müştemilat oranını hesapla
        mustemilat_oran = emsal_hakki / mustemilat["toplam_alan"]
        azaltilmis_mustemilat = [(ad, alan * mustemilat_oran) for ad, alan in sonuc["mustemilat_detaylari"]]
        
        sonuc["mustemilat_detaylari"] = [(ad, round(alan, 2)) for ad, alan in azaltilmis_mustemilat]
        sonuc["mustemilat_toplam_alani"] = emsal_hakki
        sonuc["max_yapilasma_alani_m2"] = emsal_hakki  # Emsalin tamamı kullanılabilir
        
        sonuc["mesaj_metin"] = (
            f"Araziniz {arazi_buyuklugu_m2:,.2f} m² ve emsal hakkınız {emsal_hakki:,.2f} m².\n"
            f"Bu büyüklükte bir arazide, zorunlu müştemilatlar için gereken {mustemilat['toplam_alan']:,.2f} m² alanın tamamı karşılanamamaktadır. "
            f"Sadece {emsal_hakki:,.2f} m²'lik bir müştemilat alanı oluşturulabilir. "
            f"Bu durumda üretim hattı için hiç kapalı alan hakkınız kalmamaktadır."
        ).replace(",",".")
    elif toplam_alan > emsal_hakki:
        # Müştemilatlar sığıyor ama üretim alanı için yeterli yer yok
        sonuc["izin_durumu"] = "izin_verilebilir"
        
        # Üretim için kalan alanı hesapla
        kalan_alan = emsal_hakki - mustemilat["toplam_alan"]
        sonuc["uretim_hatti_alani"] = kalan_alan
        
        # Kalan alanla yapılabilecek kapasiteyi hesapla
        yapilabilecek_kapasite = (kalan_alan / ORTA_URETIM_HATTI_ALANI) * REFERANS_KAPASITE
        yapilabilecek_kapasite = round(max(0, yapilabilecek_kapasite), 1)
        
        sonuc["mesaj_metin"] = (
            f"Araziniz {arazi_buyuklugu_m2:,.2f} m² ve emsal hakkınız {emsal_hakki:,.2f} m².\n"
            f"Talep ettiğiniz {kapasite_ton:.1f} ton/gün kapasiteli tesis için toplam {toplam_alan:.2f} m² yapı alanı gerekirken, "
            f"emsal dahilinde sadece {emsal_hakki:.2f} m² inşaat yapabilirsiniz.\n\n"
            f"Müştemilatlar ({mustemilat['toplam_alan']:.2f} m²) tamamen yapılabilir, ancak asıl üretim hattı için "
            f"sadece {kalan_alan:.2f} m² alan kalır. Bu da yaklaşık {yapilabilecek_kapasite:.1f} ton/gün kapasiteye denk gelir."
        ).replace(",",".")
    else:
        # Hem müştemilat hem üretim alanı için yeterli alan var
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["uretim_hatti_alani"] = asil_uretim_alani
        
        # Kalan emsal hesapla
        kalan_emsal = emsal_hakki - toplam_alan
        
        # Eğer büyük oranda emsal kullanılıyorsa, bunu belirt
        if kalan_emsal < 10 or (kalan_emsal / emsal_hakki) < 0.05:  # 10m² veya %5'ten az kalırsa
            sonuc["mesaj_metin"] = (
                f"Araziniz {arazi_buyuklugu_m2:,.2f} m² ve emsal hakkınız {emsal_hakki:,.2f} m².\n"
                f"Bu arazide {kapasite_ton:.1f} ton/gün kapasiteli bir solucan gübresi üretim tesisi kurabilirsiniz. "
                f"Tüm müştemilatlar ({mustemilat['toplam_alan']:.2f} m²) ve asıl üretim alanı ({asil_uretim_alani:.2f} m²) için "
                f"yeterli alan mevcuttur. Emsal alanının neredeyse tamamı kullanılmıştır (kalan: {kalan_emsal:.2f} m²)."
            ).replace(",",".")
        else:
            # Hala yeterli emsal kaldıysa alternatif öneriler sun
            ek_kapasite = (kalan_emsal / ORTA_URETIM_HATTI_ALANI) * REFERANS_KAPASITE
            ek_kapasite = round(max(0, ek_kapasite), 1)
            
            sonuc["mesaj_metin"] = (
                f"Araziniz {arazi_buyuklugu_m2:,.2f} m² ve emsal hakkınız {emsal_hakki:,.2f} m².\n"
                f"Bu arazide {kapasite_ton:.1f} ton/gün kapasiteli bir solucan gübresi üretim tesisi kurabilirsiniz. "
                f"Tüm müştemilatlar ({mustemilat['toplam_alan']:.2f} m²) ve asıl üretim alanı ({asil_uretim_alani:.2f} m²) için "
                f"yeterli alan mevcuttur. Emsal alanından geriye kalan {kalan_emsal:.2f} m² ile kapasitenizi "
                f"yaklaşık {ek_kapasite:.1f} ton/gün daha artırabilirsiniz."
            ).replace(",",".")
    
    # HTML mesajı oluştur
    sonuc["ana_mesaj_html"] = _olustur_html_mesaj_solucan(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
    sonuc["mesaj"] = sonuc["mesaj_metin"]  # Geriye dönük uyumluluk için
    
    return sonuc

def hesapla_mustemilat_alanlari(kapasite_ton: float, asil_uretim_alani_referansi: float) -> dict:
    """
    Kapasiteye ve asıl üretim alanına göre müştemilat alanlarını hesaplar.
    Toplam müştemilat alanını, asıl üretim alanının yaklaşık %50'si olacak şekilde ayarlar.
    Bireysel müştemilatlar için max_alan sınırlarını uygular.
    
    Args:
        kapasite_ton: Günlük kapasite (ton cinsinden)
        asil_uretim_alani_referansi: Hesaplanan asıl üretim alanı (m²)
        
    Returns:
        dict: Müştemilat bilgileri içeren sözlük
    """
    if kapasite_ton <= 0:
        return {"mustemilat_listesi": [], "toplam_alan": 0}
        
    oran = kapasite_ton / REFERANS_KAPASITE
    
    initial_mustemilat_details = []
    current_total_mustemilat = 0
    
    # 1. Her bir müştemilat için başlangıç alanını hesapla
    for key, mustemilat_item_ref in REFERANS_MUSTEMILAT.items():
        if "min_kapasite" in mustemilat_item_ref and kapasite_ton < mustemilat_item_ref["min_kapasite"]:
            continue
            
        buyume_faktoru = mustemilat_item_ref.get("buyume_faktoru", 1.0)
        
        # Temel alan hesaplaması
        alan_hesaplandi = mustemilat_item_ref["alan"] * oran * buyume_faktoru
        
        # Kapasiteye bağlı özel çarpanlar (eğer varsa)
        if key == "kompost_alani" and kapasite_ton > 30:
            alan_hesaplandi = mustemilat_item_ref["alan"] * oran * buyume_faktoru * 1.2 
        elif key == "depolama" and kapasite_ton > 60:
            alan_hesaplandi = mustemilat_item_ref["alan"] * oran * buyume_faktoru * 1.3
            
        # Minimum alan kontrolü
        alan = max(mustemilat_item_ref.get("min_alan", 5), alan_hesaplandi)
        
        # Maksimum alan kontrolü (yeni eklendi)
        if "max_alan" in mustemilat_item_ref:
            alan = min(alan, mustemilat_item_ref["max_alan"])
        
        initial_mustemilat_details.append({
            "isim": mustemilat_item_ref["isim"], 
            "original_alan": alan, # Bu artık min ve max ile sınırlandırılmış alan
            "min_alan": mustemilat_item_ref.get("min_alan", 5),
            "max_alan": mustemilat_item_ref.get("max_alan", float('inf')) # Ölçekleme için max_alan'ı da sakla
        })
        current_total_mustemilat += alan

    if current_total_mustemilat == 0:
        return {"mustemilat_listesi": [], "toplam_alan": 0}

    # 2. Hedef toplam müştemilat alanını belirle (üretim alanının %50'si)
    target_total_mustemilat = asil_uretim_alani_referansi * 0.5

    final_mustemilat_list = []
    final_toplam_alan = 0

    # 3. Eğer mevcut toplam müştemilat hedefi aşıyorsa, ölçeklendirerek azalt
    if current_total_mustemilat > target_total_mustemilat and target_total_mustemilat > 0 :
        scaling_factor = target_total_mustemilat / current_total_mustemilat
        
        for item_detail in initial_mustemilat_details:
            scaled_alan = item_detail["original_alan"] * scaling_factor
            # Minimum alanın altına düşmemesini sağla
            # Ölçeklenmiş alan, orijinal hesaplamadaki max_alan'ı da (dolaylı olarak) korumalıdır,
            # çünkü original_alan zaten max_alan ile sınırlıydı ve scaling_factor <= 1.
            final_alan_for_item = max(item_detail["min_alan"], scaled_alan)
            # Tekrar max_alan kontrolüne gerek yok çünkü scaled_alan <= original_alan (max ile sınırlı)
            
            final_mustemilat_list.append((item_detail["isim"], round(final_alan_for_item, 2)))
            final_toplam_alan += final_alan_for_item
    else:
        # Eğer mevcut toplam hedef dahilindeyse veya hedef 0 ise, orijinal (min/max ile sınırlandırılmış) değerleri kullan
        for item_detail in initial_mustemilat_details:
            final_mustemilat_list.append((item_detail["isim"], round(item_detail["original_alan"], 2)))
            final_toplam_alan += item_detail["original_alan"]
            
    return {
        "mustemilat_listesi": final_mustemilat_list,
        "toplam_alan": round(final_toplam_alan, 2)
    }

def hesapla_asil_uretim_alani(kapasite_ton: float) -> float:
    """
    Kapasiteye göre asıl üretim alanını hesaplar
    
    Args:
        kapasite_ton: Günlük kapasite (ton cinsinden)
        
    Returns:
        float: Asıl üretim alanı (m²)
    """
    if kapasite_ton <= 0:
        return 0
        
    # Referans kapasiteye göre oran
    oran = kapasite_ton / REFERANS_KAPASITE
    alan = ORTA_URETIM_HATTI_ALANI * oran
    return max(60, alan)  # Minimum 60 m²

def hesapla_optimal_kapasite(arazi_buyuklugu_m2: float) -> float:
    """
    Belirtilen arazi alanı için optimal kapasiteyi hesaplar.
    Emsal alanını maksimuma yakın kullanmayı hedefler.
    
    Args:
        arazi_buyuklugu_m2: Arazi büyüklüğü (m²)
        
    Returns:
        float: Optimal kapasite (ton/gün)
    """
    if arazi_buyuklugu_m2 < MINIMUM_ARAZI_BUYUKLUGU:
        return 0
    
    emsal_alani = arazi_buyuklugu_m2 * EMSAL_ORANI
    
    alt_sinir = 0.1  # Minimum denenecek kapasite
    ust_sinir = 5000.0  # Pratik bir üst kapasite limiti (örneğin 5000 ton/gün)
    optimal_kapasite = 0.0

    # 1. İkili Arama (Binary Search) ile kaba bir optimal değer bulma
    # Bu döngü, alt_sinir ve ust_sinir arasındaki fark çok küçülene kadar veya belirli sayıda iterasyonla çalışır.
    for _ in range(100): # Genellikle 100 iterasyon iyi bir yakınsama sağlar
        if ust_sinir - alt_sinir < 0.01: # Yeterli hassasiyete ulaşıldıysa döngüden çık
            break
        
        orta_kapasite = (alt_sinir + ust_sinir) / 2
        if orta_kapasite == 0: # Sıfır kapasite durumunu atla
            alt_sinir = 0.01 # Çok küçük bir değerle devam et
            continue

        asil_uretim_test = hesapla_asil_uretim_alani(orta_kapasite)
        mustemilat_sonuc_test = hesapla_mustemilat_alanlari(orta_kapasite, asil_uretim_test)
        toplam_alan_test = asil_uretim_test + mustemilat_sonuc_test["toplam_alan"]
        
        if toplam_alan_test <= emsal_alani:
            # Bu kapasite emsal dahilinde, potansiyel bir optimal değer.
            # Daha yüksek bir kapasite deneyebiliriz.
            optimal_kapasite = orta_kapasite
            alt_sinir = orta_kapasite
        else:
            # Bu kapasite emsal alanını aşıyor, daha düşük bir kapasite denemeliyiz.
            ust_sinir = orta_kapasite
            
    # 2. İnce Ayar (Fine-tuning) ile emsal sınırına daha da yaklaşma
    # optimal_kapasite (binary search'ten gelen en iyi tahmin) ile başla
    current_best_kapasite = optimal_kapasite
    adim_buyuklugu = 0.01 # Çok küçük adımlarla hassasiyeti artır

    # Maksimum iterasyon sayısı, sonsuz döngüyü engellemek için
    # Bu döngü, kapasiteyi küçük adımlarla artırarak emsal sınırını aşana kadar devam eder.
    for _ in range(20000): # (0.01 adımla 200 ton/gün gibi bir aralığı tarayabilir)
        test_kapasite_sonraki = current_best_kapasite + adim_buyuklugu
        
        asil_uretim_sonraki = hesapla_asil_uretim_alani(test_kapasite_sonraki)
        mustemilat_sonuc_sonraki = hesapla_mustemilat_alanlari(test_kapasite_sonraki, asil_uretim_sonraki)
        toplam_alan_sonraki = asil_uretim_sonraki + mustemilat_sonuc_sonraki["toplam_alan"]

        if toplam_alan_sonraki <= emsal_alani:
            # Hala emsal dahilinde, bu kapasiteyi yeni en iyi olarak kabul et
            current_best_kapasite = test_kapasite_sonraki
        else:
            # Emsal aşıldı, bir önceki current_best_kapasite değeri son geçerli optimal kapasitedir.
            break 
        
        # Pratik bir üst kapasite limitini tekrar kontrol et
        if current_best_kapasite > 5000: 
            break
            
    return round(current_best_kapasite, 1)

def hesapla_optimal_kapasite_emsale_gore(emsal_hakki: float) -> float:
    """
    Emsal hakkına göre optimal kapasiteyi hesaplar.
    Müştemilat + üretim hattı toplamı emsal hakkını aşmayacak en büyük kapasiteyi bulur.
    """
    if emsal_hakki <= 0:
        return 0

    alt = 0.1
    ust = 5000
    optimal = 0
    for _ in range(100):
        mid = (alt + ust) / 2
        asil_uretim = hesapla_asil_uretim_alani(mid)
        mustemilat = hesapla_mustemilat_alanlari(mid, asil_uretim)
        toplam = asil_uretim + mustemilat["toplam_alan"]
        if toplam <= emsal_hakki:
            optimal = mid
            alt = mid
        else:
            ust = mid
    return round(optimal, 1)

def solucan_tesisi_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict = None) -> dict:
    """
    Arazi bilgilerine göre solucan tesisi değerlendirmesi yapar.
    
    Args:
        arazi_bilgileri: Arazi bilgilerini içeren sözlük
        yapi_bilgileri: Yapı bilgilerini içeren sözlük (opsiyonel)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    try:
        arazi_buyuklugu_m2 = arazi_bilgileri.get("buyukluk_m2", 0)
        
        # Minimum arazi kontrolü
        if arazi_buyuklugu_m2 < MINIMUM_ARAZI_BUYUKLUGU:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": f"Minimum {MINIMUM_ARAZI_BUYUKLUGU} m² arazi gereklidir. Mevcut arazi: {arazi_buyuklugu_m2} m²"
            }
        
        # Emsal türünü al (varsayılan: marjinal)
        emsal_turu = None
        if yapi_bilgileri:
            emsal_turu = yapi_bilgileri.get("emsal_turu")
        
        # constants.py'den emsal oranlarını içe aktarma
        from .constants import EMSAL_ORANI_MARJINAL, EMSAL_ORANI_MUTLAK_DIKILI
        
        # Emsal türüne göre oranı belirle
        emsal_orani = None
        if emsal_turu == "mutlak_dikili":
            emsal_orani = EMSAL_ORANI_MUTLAK_DIKILI  # %5
        elif emsal_turu == "marjinal":
            emsal_orani = EMSAL_ORANI_MARJINAL  # %20
            
        # Hesaplama yap
        sonuc = hesapla_solucan_tesisi(arazi_buyuklugu_m2, emsal_orani=emsal_orani)
        
        return {
            "izin_durumu": "izin_verilebilir",
            "mesaj": sonuc.get("ana_mesaj_html", sonuc.get("mesaj", "")),
            "maksimum_taban_alani": sonuc.get("max_yapilasma_alani_m2", 0),
            "maksimum_toplam_alan": sonuc.get("max_yapilasma_alani_m2", 0),
            "minimum_arazi_buyuklugu": MINIMUM_ARAZI_BUYUKLUGU,
            "kapasite": sonuc.get("gunluk_kapasite_ton", 0),
            "uretim_hatti_alani": sonuc.get("uretim_hatti_alani", 0),
            "toplam_mustemilat_alani": sonuc.get("mustemilat_toplam_alani", 0)
        }
        
    except Exception as e:
        return {
            "izin_durumu": "hata",
            "mesaj": f"Hesaplama sırasında hata oluştu: {str(e)}"
        }

def solucan_degerlendir(data):
    """
    API endpoint için solucan tesisi hesaplama fonksiyonu
    
    Args:
        data: Form verilerini içeren dict
        
    Returns:
        dict: Hesaplama sonuçları
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        # Form verilerini parse et
        arazi_alani = float(data.get('alan_m2', 0)) or float(data.get('alan', 0))
        
        # Arazi bilgileri
        arazi_bilgileri = {
            "buyukluk_m2": arazi_alani,
            "ana_vasif": data.get('arazi_vasfi', 'TA'),
        }
        
        # Yapı bilgileri
        yapi_bilgileri = {
            "emsal_turu": data.get('emsal_turu', 'marjinal')
        }
        
        # Ana hesaplama
        sonuc = solucan_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri)
        
        # API response formatına dönüştür
        if sonuc["izin_durumu"] == "izin_verilebilir":
            response = {
                "success": True,
                "mesaj": sonuc["mesaj"],
            }
        else:
            response = {
                "success": False,
                "error": sonuc["mesaj"],
                "message": "Solucan tesisi yapılaşma koşulları sağlanamıyor"
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Solucan tesisi hesaplama hatası: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": "Solucan tesisi hesaplama sırasında hata oluştu"
        }
