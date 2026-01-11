"""
İpek Böcekçiliği Tesisi için yapılaşma kurallarını hesaplar.
v3 - Alan dağılımı ve minimum üretim alanı, MD senaryosuna göre güncellendi.
Kerevetler 3 katlı yapılabiliyor kuralı eklendi. 
Ek olarak: toplam yaprak ihtiyacı ve tahmini yaş koza üretimi çıktılarına eklendi.
HTML çıktı mantar tesisi şablonuna uygun şekilde revize edildi.
"""
import logging

# Logger tanımla
logger = logging.getLogger(__name__)

# Sabitler
IPEK_BOCEKCILIGI_MIN_ARAZI_M2 = 500
DEFAULT_EMSAL_ORANI = 0.05  # Sadece %5 emsal uygulanacak
MIN_URETIM_ALANI_M2 = 50    # Minimum üretim alanı gerekliliği
BAKICI_EVI_M2 = 75
IDARI_BINA_M2 = 75
KAT_SAYISI_KEREVET = 3      # Kerevetler 3 katlı yapılabiliyor

YAPRAK_KG_PER_KUTU = 600    # Bir kutu için gereken dut yaprağı (kg)
KOZA_KG_PER_KUTU = 37       # Bir kutudan elde edilen yaş koza ortalaması (kg)

def _olustur_html_mesaj_ipek_bocekciligi(sonuc_data: dict, arazi_buyuklugu_m2: float, genel_emsal_orani: float) -> str:
    """
    İpek böcekçiliği tesisi hesaplama sonuçlarını HTML formatında okunabilir bir mesaja dönüştürür.
    v3 - Alan dağılımı, minimum üretim alanı ve kutu kapasitesi ile mantar tesisi şablonuna uygun revize edildi.
    Toplam yaprak ihtiyacı ve yaş koza üretimi eklendi.
    """
    kullanilacak_emsal_orani = genel_emsal_orani if genel_emsal_orani is not None else DEFAULT_EMSAL_ORANI

    # Hesaplama: kerevet/besleme taban alanı ve kapasite
    kerevet_besleme_taban_alani = sonuc_data.get("uretim_alani_m2", 0) * 0.5
    kutu_sayisi_tekkat = kerevet_besleme_taban_alani / 25
    kutu_sayisi_3kat = (kerevet_besleme_taban_alani * KAT_SAYISI_KEREVET) / 25

    toplam_yaprak_ihtiyaci_kg = kutu_sayisi_3kat * YAPRAK_KG_PER_KUTU
    toplam_yas_koza_kg = kutu_sayisi_3kat * KOZA_KG_PER_KUTU

    mesaj = """
    <style>
        .ipek-sonuc {font-family: Arial, sans-serif;}
        .ipek-sonuc h3 {color: #3c763d; margin-bottom: 15px;}
        .ipek-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .ipek-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .ipek-sonuc th, .ipek-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .ipek-sonuc th {background-color: #f2f2f2;}
        .ipek-sonuc .uretim {background-color: #f0f7fc;}
        .ipek-sonuc .yardimci {background-color: #f9f9e6;}
        .ipek-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .ipek-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .ipek-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .ipek-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
    </style>
    <div class="ipek-sonuc">
    """

    mesaj += "<h3>İPEK BÖCEKÇİLİĞİ TESİSİ DEĞERLENDİRMESİ</h3>"
    mesaj += f"<p><b>Arazi Büyüklüğü:</b> {arazi_buyuklugu_m2:,.2f} m²<br>"
    mesaj += f"<b>Dut Bahçesi Durumu:</b> {'Var' if sonuc_data.get('dut_bahcesi_var_mi') else 'Yok'}<br>"
    mesaj += f"<b>İzin Verilen Toplam Emsal Alanı (%{kullanilacak_emsal_orani*100:.0f}):</b> {sonuc_data.get('maksimum_yapilasma_alani_m2', 0):,.2f} m²</p>"

    # Sonuç durumuna göre mesaj türünü belirle
    if sonuc_data.get("izin_durumu") == "izin_verilemez":
        aciklama = sonuc_data.get("mesaj_metin", "").replace("\n", "<br>")
        mesaj += f'<div class="hata"><b>SONUÇ: TESİS YAPILAMAZ</b><br>{aciklama}</div>'
    else:
        mesaj += f'<div class="basarili"><b>SONUÇ: TESİS YAPILABİLİR</b><br>{sonuc_data.get("mesaj_metin")}</div>'

    # Üretim alanı dağılımı (min 50 m² olacak şekilde)
    uretim_alani = sonuc_data.get("uretim_alani_m2", 0)
    depo_alani = sonuc_data.get("depo_alani_m2", 0)
    cekim_odasi_alani = sonuc_data.get("cekim_odasi_alani_m2", 0)
    bakici_evi = sonuc_data.get("bakici_evi_m2", 0)
    idari_bina = sonuc_data.get("idari_bina_m2", 0)

    mesaj += '<div class="baslik">TESİS ALAN DAĞILIMI</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Alan Türü</th><th>Alan (m²)</th></tr>'
    mesaj += f'<tr class="uretim"><td>Üretim Alanı (min 50 m²)</td><td>{uretim_alani:.2f}</td></tr>'
    mesaj += f'<tr class="uretim"><td>Kerevet/Besleme Alanı (%50, taban)</td><td>{kerevet_besleme_taban_alani:.2f}</td></tr>'
    mesaj += f'<tr class="yardimci"><td>Depo (%25)</td><td>{depo_alani:.2f}</td></tr>'
    mesaj += f'<tr class="yardimci"><td>İpek Çekim Odası (%25)</td><td>{cekim_odasi_alani:.2f}</td></tr>'
    if bakici_evi > 0:
        mesaj += f'<tr><td>Bakıcı Evi</td><td>{bakici_evi:.2f}</td></tr>'
    if idari_bina > 0:
        mesaj += f'<tr><td>İdari Bina</td><td>{idari_bina:.2f}</td></tr>'
    mesaj += '</table>'

    # Kutu kapasitesi bilgisini ekle (tek katlı ve 3 katlı ayrı göster)
    mesaj += '<div class="baslik">KAPASİTE</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Kerevet/Besleme Taban Alanı</th><th>Kutu Kapasitesi (Tek Katlı)</th><th>Kutu Kapasitesi (3 Katlı)</th></tr>'
    mesaj += f'<tr><td>{kerevet_besleme_taban_alani:.2f} m²</td><td>{kutu_sayisi_tekkat:.2f} kutu</td><td>{kutu_sayisi_3kat:.2f} kutu</td></tr>'
    mesaj += '</table>'

    # Verimlilik & üretim bölümü ekle
    mesaj += '<div class="baslik">VERİMLİLİK & ÜRETİM</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Açıklama</th><th>Değer</th></tr>'
    mesaj += f'<tr><td>Beslenebilecek Kutu (3 Katlı)</td><td>{kutu_sayisi_3kat:.2f} kutu</td></tr>'
    mesaj += f'<tr><td>Toplam Yaprak İhtiyacı</td><td>{toplam_yaprak_ihtiyaci_kg:.0f} kg</td></tr>'
    mesaj += f'<tr><td>Tahmini Yaş Koza Üretimi</td><td>{toplam_yas_koza_kg:.1f} kg</td></tr>'
    mesaj += '</table>'

    # Genel özet
    mesaj += '<div class="baslik">GENEL ÖZET</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Alan Türü</th><th>Değer (m²)</th></tr>'
    mesaj += f'<tr><td>Toplam Arazi Alanı</td><td>{arazi_buyuklugu_m2:.2f}</td></tr>'
    mesaj += f'<tr><td>Emsal Alanı</td><td>{sonuc_data.get("maksimum_yapilasma_alani_m2", 0):.2f}</td></tr>'
    mesaj += f'<tr><td>Kullanılan Yapı Alanı</td><td>{sonuc_data.get("maksimum_taban_alani", 0):.2f}</td></tr>'
    mesaj += '</table>'

    # Notlar bölümü
    mesaj += '<div class="notlar">'
    mesaj += '<b>İpek Böcekçiliği Tesisi Planlama Notları:</b><br>'
    mesaj += '- Tesis kurulabilmesi için arazide dut bahçesi bulunması ve minimum 500 m² arazi büyüklüğü gereklidir.<br>'
    mesaj += '- Üretim alanı en az 50 m² olmalı, üretim alanı %50 kerevet/besleme (taban), %25 depo ve %25 ipek çekim odası olarak ayrılır.<br>'
    mesaj += '- Her 25 m² kerevet/besleme taban alanı için 1 kutu kapasiteli üretim yapılabilir.<br>'
    mesaj += '- Kerevetler 3 katlı yapılabiliyorsa, kutu kapasitesi (taban alanı × 3) / 25 olarak hesaplanır.<br>'
    mesaj += '- Bir kutunun beslenmesi için yaklaşık 600 kg dut yaprağı gerekir, bir kutudan ortalama 37 kg yaş koza elde edilir.<br>'
    mesaj += f'- Emsal oranı %{kullanilacak_emsal_orani*100:.0f}\'dir (arazi alanının %{kullanilacak_emsal_orani*100:.0f}\'si kadar yapılaşma izni).<br>'
    mesaj += '- Öncelik üretim alanında olup, alan yeterli ise bakıcı evi ve idari bina inşa edilebilir.<br>'
    mesaj += '- Bu değerlendirme tavsiye niteliğinde olup, kesin başvuru için ilgili kurumlara danışınız.'
    mesaj += '</div>'

    mesaj += '</div>'
    return mesaj

def hesapla_ipek_bocekciligi_kurallari(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None):
    """
    İpek böcekçiliği tesisi için yapılaşma kurallarını hesaplar.
    Alan dağılımı ve minimum üretim alanı, MD senaryosuna göre güncellendi.
    Kerevetler 3 katlı kuralı eklendi.
    Ek olarak: toplam yaprak ihtiyacı ve tahmini yaş koza üretimi eklendi.
    """
    arazi_buyuklugu_m2 = arazi_bilgileri.get("buyukluk_m2", 0)
    dut_bahcesi_var_mi = yapi_bilgileri.get("dut_bahcesi_var_mi", False)
    buyuk_ova_icinde = arazi_bilgileri.get("buyuk_ova_icinde", False)
    kullanilacak_emsal_orani = DEFAULT_EMSAL_ORANI

    logger.info(f"[IPEK] Hesaplama başlatılıyor: arazi={arazi_buyuklugu_m2}m², dut bahçesi={dut_bahcesi_var_mi}, emsal={kullanilacak_emsal_orani}")

    sonuc = {
        "izin_durumu": "belirsiz",
        "mesaj_metin": "",
        "mesaj": "",
        "maksimum_taban_alani": 0,
        "maksimum_yapilasma_alani_m2": 0,
        "min_arazi_sarti_saglandi_mi": False,
        "dut_bahcesi_var_mi": dut_bahcesi_var_mi,
        "uyari_mesaji_ozel_durum": "",
        "sonraki_adim_bilgisi": "",
        "bakici_evi_m2": 0,
        "idari_bina_m2": 0,
        "uretim_alani_m2": 0,
        "depo_alani_m2": 0,
        "cekim_odasi_alani_m2": 0,
        "kutu_sayisi": 0,
        "beslenebilecek_kutu_sayisi": 0,
        "toplam_yaprak_ihtiyaci_kg": 0,
        "toplam_yas_koza_kg": 0
    }

    # Dut bahçesi kontrolü
    if not dut_bahcesi_var_mi:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["mesaj_metin"] = (
            "İpek böcekçiliği tesisi için arazide dut bahçesi bulunması zorunludur. Dut bahçesi kurulumu ve ağaç dikimi için Tarım ve Orman İl Müdürlüğü'nden uygun görüş/izin alınması zorunludur. "
                "Dut bahçesi olmayan arazide ipek böcekçiliği tesisi yapılamaz."
        )
        logger.warning(f"[IPEK] Dut bahçesi yok: {arazi_buyuklugu_m2}m²")
        sonuc["mesaj"] = _olustur_html_mesaj_ipek_bocekciligi(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
        return sonuc

    if arazi_buyuklugu_m2 < IPEK_BOCEKCILIGI_MIN_ARAZI_M2:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["mesaj_metin"] = (
            f"İpek böcekçiliği tesisi için minimum arazi büyüklüğü {IPEK_BOCEKCILIGI_MIN_ARAZI_M2} m² olmalıdır. "
            f"Mevcut arazi {arazi_buyuklugu_m2:.2f} m² olduğundan bu alanda tesis yapımına izin verilememektedir."
        )
        sonuc["min_arazi_sarti_saglandi_mi"] = False
        logger.warning(f"[IPEK] Arazi büyüklüğü yetersiz: {arazi_buyuklugu_m2}m²")
        sonuc["mesaj"] = _olustur_html_mesaj_ipek_bocekciligi(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
        return sonuc

    sonuc["min_arazi_sarti_saglandi_mi"] = True
    toplam_emsal_alan = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
    sonuc["maksimum_yapilasma_alani_m2"] = toplam_emsal_alan
    sonuc["maksimum_taban_alani"] = toplam_emsal_alan

    # Alan dağılımı önceliği: Üretim (min 50 m²) → Bakıcı Evi (75) → İdari Bina (75)
    kalan_emsal_alan = toplam_emsal_alan
    bakici_evi = 0
    idari_bina = 0
    uretim_alani = 0

    if kalan_emsal_alan < MIN_URETIM_ALANI_M2:
        # 50 m² altında üretim yapılamaz
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["mesaj_metin"] = (
            f"İzin verilen toplam yapılaşma alanı ({kalan_emsal_alan:.2f} m²) minimum üretim alanı ({MIN_URETIM_ALANI_M2} m²) için bile yeterli değildir. "
            "Bu büyüklükte tesise izin verilemez."
        )
    else:
        # 50 m² ve üstü üretim alanı varsa, öncelik üretim alanında
        uretim_alani = min(kalan_emsal_alan, MIN_URETIM_ALANI_M2)
        kalan_emsal_alan -= uretim_alani

        # 2. Öncelik: Bakıcı evi (75 m²)
        if kalan_emsal_alan >= BAKICI_EVI_M2:
            bakici_evi = BAKICI_EVI_M2
            kalan_emsal_alan -= BAKICI_EVI_M2

        # 3. Öncelik: İdari bina (75 m²)
        if kalan_emsal_alan >= IDARI_BINA_M2:
            idari_bina = IDARI_BINA_M2
            kalan_emsal_alan -= IDARI_BINA_M2

        # Kalan emsal alan üretime ekleniyorsa
        if kalan_emsal_alan > 0:
            uretim_alani += kalan_emsal_alan
            kalan_emsal_alan = 0

        # Dağılım: %50 kerevet/besleme, %25 depo, %25 çekim odası
        kerevet_besleme_alani = uretim_alani * 0.5
        depo_alani = uretim_alani * 0.25
        cekim_odasi_alani = uretim_alani * 0.25

        # Kapasite ve verimlilik hesapları
        kutu_sayisi_tekkat = kerevet_besleme_alani / 25
        kutu_sayisi_3kat = (kerevet_besleme_alani * KAT_SAYISI_KEREVET) / 25
        toplam_yaprak_ihtiyaci_kg = kutu_sayisi_3kat * YAPRAK_KG_PER_KUTU
        toplam_yas_koza_kg = kutu_sayisi_3kat * KOZA_KG_PER_KUTU

        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["bakici_evi_m2"] = bakici_evi
        sonuc["idari_bina_m2"] = idari_bina
        sonuc["uretim_alani_m2"] = uretim_alani
        sonuc["depo_alani_m2"] = depo_alani
        sonuc["cekim_odasi_alani_m2"] = cekim_odasi_alani
        sonuc["kutu_sayisi"] = int(kutu_sayisi_3kat)
        # Tek katlı kapasite bilgisi de döndürülüyor (gösterim için)
        sonuc["kutu_sayisi_tekkat"] = int(kutu_sayisi_tekkat)
        sonuc["beslenebilecek_kutu_sayisi"] = kutu_sayisi_3kat
        sonuc["toplam_yaprak_ihtiyaci_kg"] = toplam_yaprak_ihtiyaci_kg
        sonuc["toplam_yas_koza_kg"] = toplam_yas_koza_kg

        sonuc["mesaj_metin"] = (
            f"İpek böcekçiliği tesisi için {arazi_buyuklugu_m2:.2f} m² arazide toplam {toplam_emsal_alan:.2f} m² yapılaşma hakkınız vardır. "
            f"Öncelikli olarak minimum üretim alanı ({MIN_URETIM_ALANI_M2} m²) tahsis edilir, kalan alan varsa bakıcı evi ve idari bina için ayrılır. "
            f"Üretim alanının %50'si kerevet/besleme (taban: {kerevet_besleme_alani:.2f} m², 3 katlı kapasite: {kutu_sayisi_3kat:.2f} kutu), "
            f"%25'i depo ({depo_alani:.2f} m²), %25'i ipek çekim odası ({cekim_odasi_alani:.2f} m²) olarak önerilir. "
            f"Bu alanda yaklaşık {toplam_yaprak_ihtiyaci_kg:.0f} kg dut yaprağı ile {toplam_yas_koza_kg:.1f} kg yaş koza elde edilebilir."
        )

    # Uyarı ve sonraki adım bilgisi
    sonuc["uyari_mesaji_ozel_durum"] = "Tesis için öncelik üretim alanında olmalıdır. Alan yetiyorsa bakıcı evi ve idari bina yapılabilir."
    sonuc["sonraki_adim_bilgisi"] = "İpek böcekçiliği yapımı için Tarım ve Orman İl Müdürlüğü'nden onay almanız gerekmektedir."

    if buyuk_ova_icinde:
        sonuc["uyari_mesaji_ozel_durum"] += " Araziniz Büyük Ova Koruma Alanı içinde yer aldığı için süreç uzayabilir."

    logger.info(f"[IPEK] Sonuç: izin_durumu={sonuc['izin_durumu']} üretim={uretim_alani} kutu={sonuc['kutu_sayisi']} bakıcı={bakici_evi} idari={idari_bina}")

    # HTML mesajını oluştur ve ata
    sonuc["mesaj"] = _olustur_html_mesaj_ipek_bocekciligi(sonuc, arazi_buyuklugu_m2, kullanilacak_emsal_orani)
    return sonuc

def ipek_bocekciligi_kurali(arazi_buyuklugu_m2, dut_bahcesi_var_mi=False, buyuk_ova_icinde_mi=False, emsal_orani: float = None):
    """
    İpek böcekçiliği tesisi için yapılaşma kurallarını değerlendirir.
    Ön kontrol amaçlı, asıl hesaplama için hesapla_ipek_bocekciligi_kurallari kullanılmalı.
    """
    kullanilacak_emsal_orani = DEFAULT_EMSAL_ORANI
    sonuc = {
        "izin_durumu": "belirsiz",
        "ana_mesaj": "",
        "detay_mesaj_bakici_evi": "",
        "uyari_mesaji_ozel_durum": "",
        "surec_bilgisi_buyuk_ova": "",
        "sonraki_adim_bilgisi": ""
    }

    if not dut_bahcesi_var_mi:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = (
            "İpek böcekçiliği tesisi için arazide dut bahçesi bulunması zorunludur. Dut bahçesi kurulumu ve ağaç dikimi için Tarım ve Orman İl Müdürlüğü'nden uygun görüş/izin alınması zorunludur. "
                "Dut bahçesi olmayan arazide ipek böcekçiliği tesisi yapılamaz."
        )
        return sonuc

    if arazi_buyuklugu_m2 < IPEK_BOCEKCILIGI_MIN_ARAZI_M2:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = (
            f"İpek böcekçiliği tesisi için minimum arazi büyüklüğü {IPEK_BOCEKCILIGI_MIN_ARAZI_M2} m² olmalıdır. "
            f"Mevcut arazi {arazi_buyuklugu_m2:.2f} m² olduğundan yapılaşmaya izin verilememektedir."
        )
        return sonuc

    toplam_emsal_alan = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
    if toplam_emsal_alan < MIN_URETIM_ALANI_M2:
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = (
            f"Toplam izinli yapılaşma alanı ({toplam_emsal_alan:.2f} m²) minimum üretim alanı ({MIN_URETIM_ALANI_M2} m²) için yeterli değildir."
        )
        return sonuc

    sonuc["izin_durumu"] = "izin_verilebilir"
    sonuc["ana_mesaj"] = (
        f"İpek böcekçiliği tesisi için {arazi_buyuklugu_m2:.2f} m² arazide yapılaşmaya izin verilebilir. "
        "Öncelik üretim alanında, alan yetiyorsa bakıcı evi ve idari bina yapılabilir."
    )

    if buyuk_ova_icinde_mi:
        sonuc["surec_bilgisi_buyuk_ova"] = (
            "Araziniz Büyük Ova Koruma Alanı içerisinde yer almaktadır. "
            "Başvuru süreci uzayabilir ve ek izinler gerekebilir."
        )

    sonuc["uyari_mesaji_ozel_durum"] = (
        "Tesis için öncelik üretim alanında olmalıdır. Alan yetiyorsa bakıcı evi ve idari bina yapılabilir."
    )
    sonuc["sonraki_adim_bilgisi"] = (
        "İpek böcekçiliği yapımı için Tarım ve Orman İl Müdürlüğü'nden onay almanız gerekmektedir."
    )

    return sonuc
