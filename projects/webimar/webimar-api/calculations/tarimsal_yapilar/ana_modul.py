"""
Bu modül, çeşitli arazi vasıfları için geçerli olan genel yapılaşma kurallarının
ana işlevlerini içerir.
"""

from .constants import (
    GENEL_YAPI_TURLERI_LISTESI, 
    SERA_VARSAYILAN_ALAN_ORANI,
    ARAZI_TIPLERI,
    YAPI_TURLERI,
    ARAZI_TIPI_ID_TO_AD,
    YAPI_TURU_ID_TO_AD
)
# solucan_tesisi'nden gerekli fonksiyonları import et (EMSAL_ORANI artık dinamik olduğu için kaldırıldı)
from .solucan_tesisi import hesapla_solucan_tesisi, toplam_mustemilat_alani, ORTA_URETIM_HATTI_ALANI, MINIMUM_ARAZI_BUYUKLUGU
from .mantar_tesisi import mantar_tesisi_degerlendir, mantar_degerlendir
from .sera import hesapla_sera_yapilasma_kurallari
from .tarimsal_silo import silo_projesi_degerlendir, hesapla_silo_yapilasma_kurallari
from .ipek_bocekciligi import hesapla_ipek_bocekciligi_kurallari
from .hara import hara_tesisi_degerlendir
from .kanatli import (
    yumurtaci_tavuk_degerlendir,
    etci_tavuk_degerlendir,
    gezen_tavuk_degerlendir,
    hindi_degerlendir,
    kaz_ordek_degerlendir
)
from .buyukbas import (
    sut_sigiri_degerlendir,
    besi_sigiri_degerlendir
)
from .kucukbas import kucukbas_degerlendir
from .evcil_hayvan import evcil_hayvan_tesisi_degerlendir
from .aricilik import aricilik_degerlendir, aricilik_frontend_degerlendir
from .soguk_hava_deposu import calculate_soguk_hava_deposu
from .su_depolama import su_depolama_degerlendir
from .tarimsal_amacli_depo import calculate_tarimsal_amacli_depo
from .zeytinyagi_uretim_tesisi import zeytinyagi_uretim_tesisi_degerlendir
from .lisansli_depo import lisansli_depo_degerlendir_api  # PHASE 2 DİNAMİK EMSAL EKLENDİ

# Model/ORM bağımlılığı yok, sadece Python fonksiyonları ve sabitlerle çalışıyor.

def genel_vasif_kural_kontrolu(arazi_bilgileri, yapi_bilgileri):
    """
    Zeytinlik dışındaki genel vasıflar için bir kural kontrol fonksiyonu örneği.

    Args:
        arazi_bilgileri (dict): Arazinin vasfı, büyüklüğü gibi bilgileri içeren sözlük.
        yapi_bilgileri (dict): Yapılmak istenen yapının türü, özellikleri gibi bilgileri içeren sözlük.

    Returns:
        dict: Kural değerlendirme sonucunu ve mesajları içeren bir sözlük.
    """
    print(f"Genel vasıf kuralı kontrolü başlatılıyor...")
    print(f"Arazi bilgileri: {arazi_bilgileri}")
    print(f"Yapı bilgileri: {yapi_bilgileri}")
    
    # Gelen verilerin geçerliliğini kontrol et
    if not isinstance(arazi_bilgileri, dict) or not isinstance(yapi_bilgileri, dict):
        return {
            "izin_durumu": "hata",
            "mesaj": "Geçersiz veri formatı: Arazi ve yapı bilgileri sözlük formatında olmalıdır.",
            "maksimum_taban_alani": None,
            "maksimum_toplam_alan": None,
            "uyari_mesaji_ozel_durum": "Veri format hatası tespit edildi. Lütfen teknik ekiple iletişime geçin.",
            "sonraki_adim_bilgisi": ""
        }
        
    # Silo için özel kontrol
    if yapi_bilgileri.get("tur_ad") and "Hububat ve yem depolama silosu" in yapi_bilgileri["tur_ad"]:
        print("Hububat ve yem depolama silosu algılandı, özel kontroller yapılıyor...")
        
        # Silo alanı kontrolü
        planlanan_silo_taban_alani_m2 = yapi_bilgileri.get("planlanan_silo_taban_alani_m2")
        print(f"Silo taban alanı (ham): {planlanan_silo_taban_alani_m2}, tipi: {type(planlanan_silo_taban_alani_m2)}")
        
        try:
            # Sayıya dönüştür
            if planlanan_silo_taban_alani_m2 is not None:
                if isinstance(planlanan_silo_taban_alani_m2, str):
                    planlanan_silo_taban_alani_m2 = float(planlanan_silo_taban_alani_m2.strip())
                else:
                    planlanan_silo_taban_alani_m2 = float(planlanan_silo_taban_alani_m2)
                
                print(f"Silo taban alanı (dönüştürülmüş): {planlanan_silo_taban_alani_m2}")
                yapi_bilgileri["planlanan_silo_taban_alani_m2"] = planlanan_silo_taban_alani_m2
            else:
                print("UYARI: Silo taban alanı tanımlanmamış!")
        except (ValueError, TypeError) as e:
            print(f"Silo alanı dönüştürme hatası: {str(e)}")
            return {
                "izin_durumu": "hata",
                "mesaj": f"Silo taban alanı geçersiz bir formatta girilmiş. Lütfen sayısal bir değer giriniz. Hata: {str(e)}",
                "maksimum_taban_alani": None,
                "maksimum_toplam_alan": None,
                "uyari_mesaji_ozel_durum": "Geçersiz silo taban alanı değeri.",
                "sonraki_adim_bilgisi": ""
            }
    sonuc = {
        "izin_durumu": "belirsiz",
        "mesaj": "Bu arazi vasfı ve yapı türü için genel bir değerlendirme yapılmaktadır.",
        "maksimum_taban_alani": None,
        "maksimum_toplam_alan": None,
        "uyari_mesaji_ozel_durum": "",
        "sonraki_adim_bilgisi": ""
    }

    arazi_vasfi = arazi_bilgileri.get("ana_vasif")
    yapi_turu_ad = yapi_bilgileri.get("tur_ad")
    arazi_buyuklugu_m2 = float(arazi_bilgileri.get("buyukluk_m2", 0)) # float olduğundan emin ol
    buyuk_ova_icinde = arazi_bilgileri.get("buyuk_ova_icinde", False)
    yas_kapali_alan_durumu_str = arazi_bilgileri.get("yas_kapali_alan_durumu", "degerlendirilmedi")
    yas_kapali_alanda_mi_bool = (yas_kapali_alan_durumu_str == "içinde")
    
    su_tahsis_belgesi_str = str(arazi_bilgileri.get("su_tahsis_belgesi", "false")).lower() # String ve küçük harf
    su_tahsis_belgesi_var_mi_bool = (su_tahsis_belgesi_str == "true")

    # Emsal türü bilgisini al (frontend'den gelen)
    emsal_turu = yapi_bilgileri.get("emsal_turu", "marjinal")  # Default marjinal
    
    # Emsal oranını belirle
    from .constants import EMSAL_ORANI_MARJINAL, EMSAL_ORANI_MUTLAK_DIKILI
    if emsal_turu == "mutlak_dikili":
        secilen_emsal_orani = EMSAL_ORANI_MUTLAK_DIKILI  # %5
        emsal_aciklama = "Mutlak tarım arazisi, dikili tarım arazisi ve özel ürün arazileri"
    else:
        secilen_emsal_orani = EMSAL_ORANI_MARJINAL  # %20
        emsal_aciklama = "Marjinal tarım arazileri"
    
    print(f"🏛️ Seçilen emsal türü: {emsal_turu}")
    print(f"📐 Kullanılacak emsal oranı: %{secilen_emsal_orani*100:.0f} ({emsal_aciklama})")

    if yapi_turu_ad not in GENEL_YAPI_TURLERI_LISTESI:
        sonuc["mesaj"] = f"{yapi_turu_ad} için bu modülde özel bir kural bulunmamaktadır. Diğer kurallar değerlendirilecek."
        return sonuc

    # Solucan ve solucan gübresi üretim tesisi için özel kurallar
    if yapi_turu_ad == "Solucan ve solucan gübresi üretim tesisi":
        solucan_sonuclari = hesapla_solucan_tesisi(arazi_buyuklugu_m2, emsal_orani=secilen_emsal_orani)
        
        if solucan_sonuclari["izin_durumu"] == "izin_verilemez":
            sonuc["izin_durumu"] = "izin_verilemez"
            # HTML mesajını kullan
            sonuc["mesaj"] = solucan_sonuclari.get("ana_mesaj_html", solucan_sonuclari.get("mesaj_metin", "Bir hata oluştu."))
            return sonuc
            
        sonuc["izin_durumu"] = "izin_verilebilir"
        # HTML mesajını kullan
        sonuc["mesaj"] = solucan_sonuclari.get("ana_mesaj_html", solucan_sonuclari.get("mesaj_metin", "Detaylar için hesaplama modülüne bakınız."))
        
        sonuc["maksimum_taban_alani"] = solucan_sonuclari["max_yapilasma_alani_m2"]
        # uyari_mesaji_ozel_durum ve sonraki_adim_bilgisi HTML mesajına dahil edilebilir veya ayrı kalabilir.
        # Şimdilik ayrı bırakalım, HTML mesajı zaten detayları içeriyor.
        # Dinamik emsal oranını kullan
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste bakıcı evi hesaplamalara dahil değildir. {emsal_aciklama} için toplam yapılaşma alanı arazinizin %{secilen_emsal_orani*100:.0f}'ini geçemez."
        
        mustemilat_toplam = solucan_sonuclari["mustemilat_toplam_alani"] 
        sonuc["sonraki_adim_bilgisi"] = (
            f"Bu hesaplamada, toplam müştemilatlar için yaklaşık {mustemilat_toplam} m² alan gerektiği varsayılmıştır. "
            f"Gerekli müştemilatlar hakkında ayrıntılı bilgi için sonuç raporuna bakınız."
        )
        
        return sonuc
        
    # Mantar üretim tesisi için özel kurallar
    elif yapi_turu_ad == "Mantar üretim tesisi":
        # Frontend'den gelen veriler ile mantar_degerlendir fonksiyonunu çağır
        mantar_data = {
            'alan_m2': arazi_buyuklugu_m2,
            'arazi_vasfi': arazi_bilgileri.get('ana_vasif', 'tarım'),
            'emsal_orani': secilen_emsal_orani,
            'emsalTuru': emsal_turu
        }
        mantar_sonuclari = mantar_degerlendir(mantar_data)
        
        # Sonuçları güncelle
        if mantar_sonuclari.get("success", False):
            sonuc["izin_durumu"] = mantar_sonuclari.get("izin_durumu", "belirsiz")
            sonuc["mesaj"] = mantar_sonuclari.get("mesaj", "Mantar tesisi için hesaplama sonucu bulunamadı.")
            sonuc["maksimum_taban_alani"] = mantar_sonuclari.get("detaylar", {}).get("toplam_yapi_alani_m2", 0)
            sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
            sonuc["sonraki_adim_bilgisi"] = f"Kapasite: {mantar_sonuclari.get('detaylar', {}).get('kapasite', 0)} kg/gün"
        else:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["mesaj"] = mantar_sonuclari.get("error", "Mantar tesisi hesaplama hatası")
        
        return sonuc
        
    # Sera için özel kurallar
    elif yapi_turu_ad == "Sera":
        # Sera alanı string gelebilir, float'a çevir
        raw = yapi_bilgileri.get("sera_alani_m2", 0)
        try:
            sera_alani_m2 = float(raw) if isinstance(raw, (str, int, float)) else 0.0
        except ValueError:
            sera_alani_m2 = 0.0

        sera_bilgileri = {
            "sera_alani_m2": sera_alani_m2,
            "idari_bina_isteniyor": yapi_bilgileri.get("idari_bina_isteniyor", False)
        }
        
        # Sera yapılaşma kurallarını hesapla
        sera_sonuclari = hesapla_sera_yapilasma_kurallari(arazi_bilgileri, sera_bilgileri)
        
        sonuc.update(sera_sonuclari)
        return sonuc

    # Hububat ve yem depolama silosu için özel kurallar
    elif yapi_turu_ad == "Hububat ve yem depolama silosu":
        # Silo bilgilerini yapi_bilgileri içinden alıyoruz
        silo_bilgileri = {}
        planlanan_silo_taban_alani_m2 = None
        for kaynak in [yapi_bilgileri, arazi_bilgileri]:
            if not kaynak:
                continue
            silo_alani = kaynak.get("planlanan_silo_taban_alani_m2")
            if silo_alani is not None:
                planlanan_silo_taban_alani_m2 = silo_alani
                break
        silo_bilgileri["planlanan_silo_taban_alani_m2"] = planlanan_silo_taban_alani_m2

        # Silo yapılaşma kurallarını hesapla
        silo_sonuclari = hesapla_silo_yapilasma_kurallari(arazi_bilgileri, silo_bilgileri)

        # Anahtarları tek tek ata (mantar ile aynı mantık)
        sonuc["izin_durumu"] = silo_sonuclari.get("izin_durumu", "belirsiz")
        sonuc["mesaj"] = silo_sonuclari.get("mesaj", "")
        sonuc["maksimum_taban_alani"] = silo_sonuclari.get("maksimum_taban_alani")
        sonuc["maksimum_idari_teknik_alan"] = silo_sonuclari.get("maksimum_idari_teknik_alan")
        sonuc["kalan_emsal_hakki"] = silo_sonuclari.get("kalan_emsal_hakki")
        sonuc["uyari_mesaji_ozel_durum"] = silo_sonuclari.get("surec_bilgisi_buyuk_ova", "")
        sonuc["sonraki_adim_bilgisi"] = silo_sonuclari.get("ana_mesaj", "")
        sonuc["uygulanan_kural"] = silo_sonuclari.get("uygulanan_kural", "")

        return sonuc

    # İpek böcekçiliği tesisi için özel kurallar
    elif yapi_turu_ad == "İpek böcekçiliği tesisi":
        # İpek böcekçiliği için dut bahçesi kontrolü
        dut_bahcesi_var_mi = yapi_bilgileri.get("dut_bahcesi_var_mi", False)
        
        # İpek böcekçiliği tesisi hesaplama fonksiyonunu çağır
        ipek_sonuclari = hesapla_ipek_bocekciligi_kurallari(
            arazi_bilgileri, 
            yapi_bilgileri, 
            genel_emsal_orani=secilen_emsal_orani  # Dinamik emsal oranını kullan
        )
        
        # Sonuçları güncelle
        sonuc["izin_durumu"] = ipek_sonuclari.get("izin_durumu", "belirsiz")
        sonuc["mesaj"] = ipek_sonuclari.get("mesaj", "İpek böcekçiliği tesisi için hesaplama sonucu bulunamadı.")
        sonuc["maksimum_taban_alani"] = ipek_sonuclari.get("maksimum_taban_alani")
        sonuc["uyari_mesaji_ozel_durum"] = ipek_sonuclari.get("uyari_mesaji_ozel_durum", "")
        sonuc["sonraki_adim_bilgisi"] = ipek_sonuclari.get("sonraki_adim_bilgisi", "")
        
        return sonuc

    # Hara (at yetiştiriciliği) tesisi için özel kurallar
    elif yapi_turu_ad == "Hara (at üretimi/yetiştiriciliği tesisi)":
        hara_sonuclari = hara_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani=secilen_emsal_orani)
        
        # Sonuçları güncelle
        sonuc["izin_durumu"] = hara_sonuclari.get("izin_durumu", "belirsiz")
        sonuc["mesaj"] = hara_sonuclari.get("ana_mesaj", hara_sonuclari.get("mesaj", "Hara tesisi için hesaplama sonucu bulunamadı."))
        sonuc["maksimum_taban_alani"] = hara_sonuclari.get("maksimum_taban_alani")
        sonuc["uyari_mesaji_ozel_durum"] = hara_sonuclari.get("uyari_mesaji_ozel_durum", "")
        sonuc["sonraki_adim_bilgisi"] = hara_sonuclari.get("sonraki_adim_bilgisi", "")
        
        return sonuc

    # Kanatlı Hayvancılık Tesisleri için özel kurallar
    elif yapi_turu_ad == "Kümes (yumurtacı tavuk)":
        kanatli_sonuc = yumurtaci_tavuk_degerlendir(
            arazi_buyuklugu_m2=arazi_buyuklugu_m2,
            su_tahsis_belgesi_var_mi=su_tahsis_belgesi_var_mi_bool,
            yas_kapali_alanda_mi=yas_kapali_alanda_mi_bool
        )
        sonuc.update(kanatli_sonuc)
        return sonuc
    
    elif yapi_turu_ad == "Kümes (etçi tavuk)":
        kanatli_sonuc = etci_tavuk_degerlendir(
            arazi_buyuklugu_m2=arazi_buyuklugu_m2,
            su_tahsis_belgesi_var_mi=su_tahsis_belgesi_var_mi_bool,
            yas_kapali_alanda_mi=yas_kapali_alanda_mi_bool
        )
        sonuc.update(kanatli_sonuc)
        return sonuc

    elif yapi_turu_ad == "Kümes (gezen tavuk)": # "Kümes (serbest gezen tavuk)" yerine bu kullanıldı
        kanatli_sonuc = gezen_tavuk_degerlendir(
            arazi_buyuklugu_m2=arazi_buyuklugu_m2,
            su_tahsis_belgesi_var_mi=su_tahsis_belgesi_var_mi_bool,
            yas_kapali_alanda_mi=yas_kapali_alanda_mi_bool
        )
        sonuc.update(kanatli_sonuc)
        return sonuc

    elif yapi_turu_ad == "Kümes (hindi)":
        kanatli_sonuc = hindi_degerlendir(
            arazi_buyuklugu_m2=arazi_buyuklugu_m2,
            su_tahsis_belgesi_var_mi=su_tahsis_belgesi_var_mi_bool,
            yas_kapali_alanda_mi=yas_kapali_alanda_mi_bool
        )
        sonuc.update(kanatli_sonuc)
        return sonuc

    elif yapi_turu_ad == "Kaz Ördek çiftliği": # "Kümes (kaz/ördek)" yerine bu kullanıldı
        kanatli_sonuc = kaz_ordek_degerlendir(
            arazi_buyuklugu_m2=arazi_buyuklugu_m2,
            su_tahsis_belgesi_var_mi=su_tahsis_belgesi_var_mi_bool,
            yas_kapali_alanda_mi=yas_kapali_alanda_mi_bool
        )
        sonuc.update(kanatli_sonuc)
        return sonuc

    # Büyükbaş Hayvancılık Tesisleri için özel kurallar
    # YAPI_TURLERI modelindeki "ad" alanıyla eşleşecek şekilde güncellendi
    elif yapi_turu_ad == "Süt Sığırcılığı Tesisi":
        buyukbas_sonuc = sut_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, secilen_emsal_orani)
        sonuc.update(buyukbas_sonuc)
        return sonuc

    # YAPI_TURLERI modelindeki "ad" alanıyla eşleşecek şekilde güncellendi
    elif yapi_turu_ad == "Besi Sığırcılığı Tesisi":
        buyukbas_sonuc = besi_sigiri_degerlendir(arazi_bilgileri, yapi_bilgileri, secilen_emsal_orani)
        sonuc.update(buyukbas_sonuc)
        return sonuc

    # Küçükbaş Hayvancılık Tesisi için özel kurallar (ID: 18)
    elif yapi_turu_ad == "Ağıl (küçükbaş hayvan barınağı)":
        kucukbas_sonuc = kucukbas_degerlendir(arazi_bilgileri, yapi_bilgileri, secilen_emsal_orani)
        sonuc.update(kucukbas_sonuc)
        return sonuc
        
    # Evcil Hayvan ve Bilimsel Araştırma Hayvanı Üretim Tesisi için özel kurallar (ID: 26)
    elif yapi_turu_ad == "Evcil hayvan ve bilimsel araştırma hayvanı üretim tesisi":
        evcil_hayvan_sonuc = evcil_hayvan_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri, secilen_emsal_orani)
        sonuc.update(evcil_hayvan_sonuc)
        return sonuc

    # Arıcılık Tesisleri için özel kurallar (ID: 4)
    elif yapi_turu_ad == "Arıcılık tesisleri":
        # Frontend'den gelen veriler ile aricilik_frontend_degerlendir fonksiyonunu çağır
        aricilik_data = {
            'alan_m2': arazi_buyuklugu_m2,
            'arazi_vasfi': arazi_bilgileri.get('ana_vasif', 'tarım'),
            'emsal_orani': secilen_emsal_orani,
            'emsalTuru': emsal_turu
        }
        aricilik_sonuc = aricilik_frontend_degerlendir(aricilik_data)
        
        # Sonuçları uygun formata çevir
        if aricilik_sonuc.get("success", False):
            sonuc["izin_durumu"] = aricilik_sonuc.get("izin_durumu", "belirsiz")
            sonuc["mesaj"] = aricilik_sonuc.get("mesaj", "Arıcılık tesisi için hesaplama sonucu bulunamadı.")
            sonuc["maksimum_taban_alani"] = aricilik_sonuc.get("detaylar", {}).get("gerekli_alan_m2", 0)
            sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
            sonuc["sonraki_adim_bilgisi"] = f"Maksimum kovan kapasitesi: {aricilik_sonuc.get('detaylar', {}).get('maksimum_kovan_kapasitesi', 'N/A')} adet"
        else:
            sonuc["izin_durumu"] = "izin_verilemez" 
            sonuc["mesaj"] = aricilik_sonuc.get("error", "Arıcılık tesisi hesaplama hatası")
        
        return sonuc

    # Soğuk Hava Deposu için özel kurallar (ID: 16)
    elif yapi_turu_ad == "Soğuk hava deposu":
        soguk_hava_sonuc = calculate_soguk_hava_deposu(arazi_buyuklugu_m2, emsal_orani=secilen_emsal_orani)
        
        # Sonuçları uygun formata çevir
        sonuc["izin_durumu"] = "izin_verilebilir" if soguk_hava_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = soguk_hava_sonuc.get("message", soguk_hava_sonuc.get("error", "Soğuk hava deposu hesaplama sonucu bulunamadı."))
        sonuc["maksimum_taban_alani"] = soguk_hava_sonuc.get("maksimum_yapilasma_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = soguk_hava_sonuc.get("uyari_mesaji", "")
        sonuc["sonraki_adim_bilgisi"] = soguk_hava_sonuc.get("detay_mesaj", "")
        
        return sonuc

    # Su Depolama için özel kurallar (ID: 12)
    elif yapi_turu_ad == "Su depolama":
        # Su depolama için arazi bilgilerini yapi_bilgileri formatına dönüştür
        su_depolama_data = {
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            **yapi_bilgileri
        }
        su_depolama_sonuc = su_depolama_degerlendir(su_depolama_data, emsal_orani=secilen_emsal_orani)
        
        # Sonuçları uygun formata çevir
        sonuc["izin_durumu"] = "izin_verilebilir" if su_depolama_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = su_depolama_sonuc.get("mesaj", su_depolama_sonuc.get("hata_mesaji", su_depolama_sonuc.get("izin_durumu", "Su depolama hesaplama sonucu bulunamadı.")))
        sonuc["maksimum_taban_alani"] = su_depolama_sonuc.get("maksimum_emsal_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
        sonuc["sonraki_adim_bilgisi"] = f"Teknik bina: {su_depolama_sonuc.get('teknik_bina_alani_m2', 0)} m², İdari alan: {su_depolama_sonuc.get('idari_alan_m2', 0)} m², Toplam: {su_depolama_sonuc.get('toplam_kapali_alan_m2', 0)} m²"
        
        return sonuc

    # Su Depolama ve Pompaj Sistemi için özel kurallar (ID: 15)
    elif yapi_turu_ad == "Su depolama ve pompaj sistemi":
        # Su depolama ve pompaj sistemi için arazi bilgilerini yapi_bilgileri formatına dönüştür
        su_depolama_data = {
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            **yapi_bilgileri
        }
        su_depolama_sonuc = su_depolama_degerlendir(su_depolama_data, emsal_orani=secilen_emsal_orani)
        
        # Sonuçları uygun formata çevir
        sonuc["izin_durumu"] = "izin_verilebilir" if su_depolama_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = su_depolama_sonuc.get("mesaj", su_depolama_sonuc.get("hata_mesaji", su_depolama_sonuc.get("izin_durumu", "Su depolama ve pompaj sistemi hesaplama sonucu bulunamadı.")))
        sonuc["maksimum_taban_alani"] = su_depolama_sonuc.get("maksimum_emsal_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
        sonuc["sonraki_adim_bilgisi"] = f"Teknik bina: {su_depolama_sonuc.get('teknik_bina_alani_m2', 0)} m², İdari alan: {su_depolama_sonuc.get('idari_alan_m2', 0)} m², Toplam: {su_depolama_sonuc.get('toplam_kapali_alan_m2', 0)} m²"
        
        return sonuc

    # Tarımsal Amaçlı Depo için özel kurallar (ID: 6) - PHASE 2 DİNAMİK EMSAL
    elif yapi_turu_ad == "Tarımsal amaçlı depo":
        tarimsal_depo_sonuc = calculate_tarimsal_amacli_depo(arazi_buyuklugu_m2, emsal_orani=secilen_emsal_orani)
        
        # Sonuçları uygun formata çevir - PHASE 2 DİNAMİK SİSTEM
        sonuc["izin_durumu"] = "izin_verilebilir" if tarimsal_depo_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = tarimsal_depo_sonuc.get("mesaj", tarimsal_depo_sonuc.get("message", "Tarımsal amaçlı depo hesaplama sonucu bulunamadı."))
        sonuc["maksimum_taban_alani"] = tarimsal_depo_sonuc.get("maksimum_insaat_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
        sonuc["sonraki_adim_bilgisi"] = f"Depo: {tarimsal_depo_sonuc.get('detaylar', {}).get('depo_alani', 150)} m², İdari: {tarimsal_depo_sonuc.get('detaylar', {}).get('idari_alan', 30)} m², Teknik: {tarimsal_depo_sonuc.get('detaylar', {}).get('teknik_alan', 20)} m²"
        
        return sonuc

    # Zeytinyağı Üretim Tesisi için özel kurallar (ID: 28)
    elif yapi_turu_ad == "Zeytinyağı üretim tesisi":
        zeytinyagi_data = {
            "alan": arazi_buyuklugu_m2,  # Fonksiyon 'alan' anahtarını bekliyor
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            **yapi_bilgileri
        }
        zeytinyagi_sonuc = zeytinyagi_uretim_tesisi_degerlendir(zeytinyagi_data)
        
        # Sonuçları uygun formata çevir
        sonuc["izin_durumu"] = "izin_verilebilir" if zeytinyagi_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = zeytinyagi_sonuc.get("izin_durumu", zeytinyagi_sonuc.get("error", "Zeytinyağı üretim tesisi hesaplama sonucu bulunamadı."))
        sonuc["maksimum_taban_alani"] = zeytinyagi_sonuc.get("maksimum_emsal_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste %10 emsal oranı kullanılır."
        sonuc["sonraki_adim_bilgisi"] = f"Üretim alanı: {zeytinyagi_sonuc.get('uretim_alani_m2', 0)} m², İdari alan: {zeytinyagi_sonuc.get('idari_alan_m2', 0)} m², Yardımcı alan: {zeytinyagi_sonuc.get('yardimci_alan_m2', 0)} m²"
        
        return sonuc

    # Tarımsal ürün yıkama tesisi için YAS ve su tahsis kontrolü
    # ÖNEMLİ NOT: Aşağıdaki 'if' blokları, eğer yukarıdaki 'elif' zincirinin bir parçası olmaları gerekiyorsa
    # 'elif' olarak değiştirilmelidir. Mevcut yapılarıyla ayrı koşullar olarak değerlendirilirler.
    # Eğer bu yapı türleri GENEL_YAPI_TURLERI_LISTESI içinde tanımlı değilse, aşağıdaki kontroller
    # gereksiz yere çalışabilir veya istenmeyen sonuçlar doğurabilir.
    if yapi_turu_ad == "Tarımsal ürün yıkama tesisi":
        # YAS kontrolü
        yas_var_mi = arazi_bilgileri.get("yas_var_mi", False)
        eger_yas_varsa = arazi_bilgileri.get("eger_yas_varsa", "")
        
        if not yas_var_mi:
            return {
                "izin_durumu": "hata",
                "mesaj": "Tarımsal ürün yıkama tesisi için YAS gereklidir. Lütfen YAS'ı kontrol edin.",
                "maksimum_taban_alani": None,
                "maksimum_toplam_alan": None,
                "uyari_mesaji_ozel_durum": "YAS kontrolü başarısız.",
                "sonraki_adim_bilgisi": ""
            }
        
        # Su tahsis belgesi kontrolü
        if not su_tahsis_belgesi_var_mi_bool:
            return {
                "izin_durumu": "hata",
                "mesaj": "Tarımsal ürün yıkama tesisi için su tahsis belgesi gereklidir.",
                "maksimum_taban_alani": None,
                "maksimum_toplam_alan": None,
                "uyari_mesaji_ozel_durum": "Su tahsis belgesi kontrolü başarısız.",
                "sonraki_adim_bilgisi": ""
            }
        
        # Eğer tüm kontroller geçildiyse
        return {
            "izin_durumu": "izin_verilebilir",
            "mesaj": "Tarımsal ürün yıkama tesisi için izin verilebilir.",
            "maksimum_taban_alani": None,
            "maksimum_toplam_alan": None,
            "uyari_mesaji_ozel_durum": "",
            "sonraki_adim_bilgisi": ""
        }

    # --- İSTİSNA: Hububat, çeltik, ayçiçeği kurutma tesisi için su tahsis belgesi gerekliliği YOK ---
    if yapi_turu_ad == "Hububat, çeltik, ayçiçeği kurutma tesisi":
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["mesaj"] = "Tarımsal üretiminiz olması durumunda tesisi yapabilirsiniz."
        return sonuc
    # --- İSTİSNA SONU ---

    # --- İSTİSNA: Açıkta meyve/sebze kurutma alanı için YAS ve su tahsis belgesi gerekliliği YOK ---
    if yapi_turu_ad == "Açıkta meyve/sebze kurutma alanı":
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["mesaj"] = "Tarımsal üretiminiz olması durumunda açıkta meyve/sebze kurutma alanı yapabilirsiniz."
        return sonuc
    # --- İSTİSNA SONU ---

    # Arıcılık tesisi için özel kurallar
    elif yapi_turu_ad == "Arıcılık tesisleri":
        aricilik_data = {
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            "kovan_sayisi": yapi_bilgileri.get("kovan_sayisi", 50)
        }
        aricilik_sonuc = aricilik_degerlendir(aricilik_data, emsal_orani=secilen_emsal_orani)
        sonuc.update(aricilik_sonuc)
        return sonuc

    # Soğuk hava deposu için özel kurallar (dinamik emsal ile)
    elif yapi_turu_ad == "Soğuk hava deposu":
        soguk_hava_sonuc = calculate_soguk_hava_deposu(arazi_buyuklugu_m2, emsal_orani=secilen_emsal_orani)
        sonuc["izin_durumu"] = "izin_verilebilir"
        sonuc["mesaj"] = "Soğuk hava deposu hesaplaması başarıyla tamamlandı."
        sonuc["maksimum_taban_alani"] = soguk_hava_sonuc.get("maksimum_taban_alani")
        sonuc["uyari_mesaji_ozel_durum"] = f"{emsal_aciklama} için hesaplanmıştır."
        return sonuc

    # Su depolama tesisi için özel kurallar  
    elif yapi_turu_ad == "Su depolama ve pompaj sistemi":
        su_depolama_data = {
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2
        }
        su_depolama_sonuc = su_depolama_degerlendir(su_depolama_data, emsal_orani=secilen_emsal_orani)
        sonuc.update(su_depolama_sonuc)
        return sonuc

    # Tarımsal amaçlı depo için özel kurallar - PHASE 2 DİNAMİK EMSAL
    elif yapi_turu_ad == "Tarımsal amaçlı depo":
        tarimsal_depo_sonuc = calculate_tarimsal_amacli_depo(arazi_buyuklugu_m2, emsal_orani=secilen_emsal_orani)
        sonuc["izin_durumu"] = "izin_verilebilir" if tarimsal_depo_sonuc.get("success", False) else "izin_verilemez"
        sonuc["mesaj"] = tarimsal_depo_sonuc.get("mesaj", "Tarımsal amaçlı depo hesaplaması tamamlandı.")
        sonuc["maksimum_taban_alani"] = tarimsal_depo_sonuc.get("maksimum_insaat_alani_m2")
        sonuc["uyari_mesaji_ozel_durum"] = f"Bu tesiste dinamik emsal sistemi kullanılır ({emsal_aciklama})."
        return sonuc

    return sonuc
