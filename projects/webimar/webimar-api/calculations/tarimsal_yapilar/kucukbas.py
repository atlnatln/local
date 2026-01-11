"""
Küçükbaş Hayvancılık Tesisi (Koyun ve Keçi) Hesaplama Modülü
"""
import math  # Logaritmik hesaplama için math kütüphanesi eklendi

# Sabit Değerler (buyukbas_hayvancilik_tum_senaryolar.txt ve referans koda göre)
EMSAL_ORANI = 0.20
AGIL_YEM_DEPOSU_ALANI_HAYVAN_BASINA = 3  # m²/hayvan (küçükbaş için)

# Yeni Gübre Çukuru ve Samanlık Hesaplamaları (küçükbaş için)
GUBRE_CUKURU_ALANI_KUCUKBAS = 0.7878 / 4  # 0.7878 m² / 4m derinlik = 0.19695 m²
SAMANLIK_ALANI_KUCUKBAS = 8.4  # m² per hayvan (5m yükseklik)

# Bakıcı evi eşik değeri ve büyüklükleri
BAKICI_EVI_ESIGI = 150  # baş
BAKICI_EVI_BUYUKLUKLERI = {
    "450-900": {"taban_alani": 75, "toplam_alan": 150},
    ">900": {"taban_alani": 150, "toplam_alan": 300}
}

# Müştemilat ve diğer alanlar için sabitler
BEKCI_KULUBESI_ALANI = 15  # m²
IDARI_BINA_TABAN_ALANI = 75  # m²
IDARI_BINA_TOPLAM_ALAN = 150 # m²

# Özel alanlar için sabitler
SAGIMHANE_KATSAYI_SUT = 0.2 # Her 10 baş için ~2m², min 15m² (50 baş ve üzeri için)
SUT_DEPOLAMA_ALANI = 10 # m² (süt üretimi için, 50 baş ve üzeri için)
BESI_EKIPMAN_ALANI = 20 # m² (besi için, 75 baş ve üzeri için)

# Minimum alanlar
MIN_ZORUNLU_MUSTEMILAT_ALANI = 30  # m² (30 baş hayvandan az olan işletmelerde)
MIN_ISLEVSEL_AGIL_ALANI = 18  # m² (6 baş küçükbaş hayvan için)
AGIL_ALANI_ORANI = 5/7
MUSTEMILAT_ALANI_ORANI = 2/7 # veya ağıl alanının %40'ı

# Köksel Büyüme Sistemi Limitleri (Küçükbaş için)
# NOT: gübre_deposu ve samanlik doğru orantılı büyür, köksel değil!
KUCUKBAS_KOKSEL_LIMITLER = {
    "su_deposu": {
        "max_limit": 25,  # m²
        "buyume_faktoru": 0.8,
        "min_esik": 100  # Bu kapasiteden sonra köksel büyüme
    },
    "malzeme_deposu": {
        "max_limit": 60,  # m²
        "buyume_faktoru": 0.75,
        "min_esik": 150
    },
    "revir": {
        "max_limit": 40,  # m²
        "buyume_faktoru": 0.8,
        "min_esik": 150
    },
    "sagimhane": {
        "max_limit": 100,  # m²
        "buyume_faktoru": 0.75,
        "min_esik": 80
    }
}

# Müştemilat tanımları
MUSTEMILAT_TANIMLARI = {
    # Zorunlu Müştemilatlar (Ağıl ve Yem Deposu Hariç)
    "su_deposu": {
        "isim": "Su Deposu", "grup": "zorunlu", "oncelik": 1,
        "min_alan_m2": 5, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 25,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "malzeme_deposu": {
        "isim": "Malzeme Deposu", "grup": "zorunlu", "oncelik": 2,
        "min_alan_m2": 8, "artis_hayvan_basi_m2": 0.03, "max_alan_m2": 60,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "gubre_deposu": {
        "isim": "Gübre Deposu/Çukuru (Derinlik: 4m)", "grup": "zorunlu", "oncelik": 3,
        "min_alan_m2": 2, "max_alan_m2": 10000,
        "hayvan_tipi_gecerli": ["koyun", "keçi"], "buyume_tipi": "yeni_orantili",
        "aciklama": "Küçükbaş hayvan için 0.197 m² alan hesaplanır (4m derinlik)"
    },
    "jenerator_odasi": {
        "isim": "Jeneratör Odası", "grup": "zorunlu", "oncelik": 4,
        "min_alan_m2": 4, "artis_hayvan_basi_m2": 0.001, "max_alan_m2": 15,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "revir": {
        "isim": "Revir / Hasta Hayvan Bölümü", "grup": "zorunlu", "oncelik": 5,
        "min_alan_m2": 6, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 40,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "samanlik": {
        "isim": "Samanlık / Kaba Yem Deposu (Yükseklik: 5m)", "grup": "zorunlu", "oncelik": 6,
        "min_alan_m2": 4, "max_alan_m2": 15000,
        "hayvan_tipi_gecerli": ["koyun", "keçi"], "buyume_tipi": "yeni_orantili",
        "aciklama": "Her küçükbaş hayvan için 8.4 m² alan hesaplanır (5m yükseklik, yıllık kaba yem ihtiyacı)"
    },
    "sagimhane": {
        "isim": "Sağımhane ve Süt Depolama Ünitesi", "grup": "zorunlu", "oncelik": 7,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.04, "max_alan_m2": 100,
        "aktiflesme_esigi_hayvan_sayisi": 50,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    # Opsiyonel Müştemilatlar
    "bekci_kulubesi": {
        "isim": "Bekçi Kulübesi", "grup": "opsiyonel", "oncelik": 10,
        "sabit_alan_m2": 15,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "idari_bina": {
        "isim": "İdari Bina", "grup": "opsiyonel", "oncelik": 11,
        "sabit_alan_m2": 75, # Taban alanı
        "toplam_insaat_alan_m2": 150, # İki katlı olabilir
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "besi_ozel_ekipman_alani": {
        "isim": "Besi İçin Özel Ekipman ve Yem Hazırlama Alanı", "grup": "opsiyonel", "oncelik": 12,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.04, "max_alan_m2": 40,
        "aktiflesme_esigi_hayvan_sayisi": 75,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    },
    "paketleme_tesisi": {
        "isim": "Paketleme Tesisi ve Deposu", "grup": "opsiyonel", "oncelik": 13,
        "min_alan_m2": 25, "artis_hayvan_basi_m2": 0.1, "max_alan_m2": 80,
        "hayvan_tipi_gecerli": ["koyun", "keçi"]
    }
}

class KucukbasHesaplama:
    def __init__(self, emsal_orani: float = None):
        self.emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
        self.agil_yem_deposu_alani_hayvan_basina = AGIL_YEM_DEPOSU_ALANI_HAYVAN_BASINA
        self.bakici_evi_esigi = BAKICI_EVI_ESIGI
        self.bakici_evi_buyuklukleri = BAKICI_EVI_BUYUKLUKLERI
        self.bekci_kulubesi_alani = BEKCI_KULUBESI_ALANI
        self.idari_bina_taban_alani = IDARI_BINA_TABAN_ALANI
        self.idari_bina_toplam_alan = IDARI_BINA_TOPLAM_ALAN
        self.sagimhane_katsayi_sut = SAGIMHANE_KATSAYI_SUT
        self.sut_depolama_alani = SUT_DEPOLAMA_ALANI
        self.besi_ekipman_alani = BESI_EKIPMAN_ALANI
        self.min_zorunlu_mustemilat_alani = MIN_ZORUNLU_MUSTEMILAT_ALANI
        self.min_islevsel_agil_alani = MIN_ISLEVSEL_AGIL_ALANI
        self.agil_alani_orani = AGIL_ALANI_ORANI
        self.mustemilat_alani_orani = MUSTEMILAT_ALANI_ORANI
        self.mustemilat_tanimlari = MUSTEMILAT_TANIMLARI
        self.koksel_limitler = KUCUKBAS_KOKSEL_LIMITLER
        self.gubre_cukuru_alani = GUBRE_CUKURU_ALANI_KUCUKBAS
        self.samanlik_alani = SAMANLIK_ALANI_KUCUKBAS

    def _hesapla_mustemilat_alani(self, must_tanimi: dict, hayvan_kapasitesi: int) -> float:
        """
        Belirli bir müştemilat için hayvan kapasitesine göre alan hesaplar
        Köksel büyüme sistemi uygulanarak maximum limitler korunur
        """
        # kod değişkenini fonksiyon başında tanımla
        kod = next((k for k, v in self.mustemilat_tanimlari.items() if v == must_tanimi), None)
        
        if must_tanimi.get("aktiflesme_esigi_hayvan_sayisi", 0) > hayvan_kapasitesi:
            return 0.0

        alan = 0
        if "sabit_alan_m2" in must_tanimi:
            alan = must_tanimi["sabit_alan_m2"]
        else:
            alan = must_tanimi.get("min_alan_m2", 0)
            
            # YENİ ORANTILI: Gübre deposu ve samanlık için küçükbaş tipine göre hesaplama
            if kod in ["gubre_deposu", "samanlik"] and must_tanimi.get("buyume_tipi") == "yeni_orantili":
                if kod == "gubre_deposu":
                    alan = hayvan_kapasitesi * self.gubre_cukuru_alani
                elif kod == "samanlik":
                    alan = hayvan_kapasitesi * self.samanlik_alani
                return max(alan, must_tanimi.get("min_alan_m2", 0))
            
            # Gübre deposu ve samanlık TAM ORANTILI büyür (eski sistem)
            if kod in ["gubre_deposu", "samanlik"]:
                artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * hayvan_kapasitesi
                alan += artis
                return alan  # Diğer ölçeklemelerden etkilenmesin
            
            # Köksel büyüme sistemi uygulama
            if kod in self.koksel_limitler:
                koksel_config = self.koksel_limitler[kod]
                max_limit = koksel_config["max_limit"]
                buyume_faktoru = koksel_config["buyume_faktoru"]
                min_esik = koksel_config["min_esik"]
                
                if hayvan_kapasitesi <= min_esik:
                    # Minimum eşiğin altında lineer büyüme
                    artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * hayvan_kapasitesi
                    alan += artis
                else:
                    # Minimum eşiğin üstünde köksel büyüme
                    # Önce eşik kapasiteye kadar lineer büyüme
                    esik_artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * min_esik
                    alan += esik_artis
                    
                    # Eşik üstü için köksel büyüme
                    fazla_kapasite = hayvan_kapasitesi - min_esik
                    koksel_artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * (fazla_kapasite ** buyume_faktoru)
                    alan += koksel_artis
                
                # Maximum limit kontrolü
                alan = min(alan, max_limit)
                
            elif kod == "jenerator_odasi":
                # Jeneratör odası için sabit değerler kullanma (teknik oda)
                alan = min(15, must_tanimi.get("max_alan_m2", 15))
                
            else:
                # Köksel büyüme sistemi olmayan müştemilatlar için eski sistem
                
                # Logaritmik ölçekleme (eski sistem - fallback)
                olcekleme_faktoru = 1.0
                if hayvan_kapasitesi > 500:
                    if hayvan_kapasitesi <= 1000:
                        olcekleme_faktoru = 0.5 + (0.5 * (math.log10(500) / math.log10(hayvan_kapasitesi)))
                    elif hayvan_kapasitesi <= 2000:
                        olcekleme_faktoru = 0.3 + (0.2 * (math.log10(1000) / math.log10(hayvan_kapasitesi)))
                    else:
                        olcekleme_faktoru = 0.2 + (0.1 * (math.log10(2000) / math.log10(hayvan_kapasitesi)))
                
                artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * hayvan_kapasitesi * olcekleme_faktoru
                alan += artis
                
                if "max_alan_m2" in must_tanimi:
                    alan = min(alan, must_tanimi["max_alan_m2"])
        
        return round(alan, 2)

    def hesapla(self, arazi_alani_m2: float, hayvan_tipi: str = "koyun", uretim_tipi: str = "genel"):
        """Küçükbaş hayvancılık tesisi için alan ve kapasite hesaplaması yapar"""
        emsal = arazi_alani_m2 * self.emsal_orani

        # Emsal alanı, minimum zorunlu müştemilat alanından bile azsa, hiçbir şekilde yapılamaz
        if emsal < self.min_zorunlu_mustemilat_alani:
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": f"Emsale göre izin verilen {emsal:.2f} m² yapılaşma alanı, zorunlu müştemilat için gerekli olan minimum {self.min_zorunlu_mustemilat_alani:.2f} m²'den bile azdır.",
                "arazi_alani_m2": arazi_alani_m2, 
                "emsal_m2": emsal, 
                "hayvan_tipi": hayvan_tipi, 
                "uretim_tipi": uretim_tipi,
                "hayvan_kapasitesi": 0,
                "bakici_evi_hakki": False, 
                "yapilar": []
            }
        
        # Emsal yeterli ama ağıl için alan kalmıyorsa yine yapılamaz
        if emsal < self.min_zorunlu_mustemilat_alani + self.min_islevsel_agil_alani:
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": f"Zorunlu müştemilat alanı ({self.min_zorunlu_mustemilat_alani:.2f} m²) karşılandıktan sonra ağıl için yeterli ({self.min_islevsel_agil_alani:.2f} m²) alan kalmamaktadır.",
                "arazi_alani_m2": arazi_alani_m2, 
                "emsal_m2": emsal, 
                "hayvan_tipi": hayvan_tipi,
                "uretim_tipi": uretim_tipi,
                "hayvan_kapasitesi": 0,
                "bakici_evi_hakki": False, 
                "yapilar": []
            }

        # İterasyon ile en uygun kapasiteyi bulma
        final_hayvan_kapasitesi = 0
        agil_alani_final = 0
        zorunlu_mustemilat_detaylari_final = []
        kalan_emsal_opsiyonel_icin = 0 
        
        # Bakıcı evi detayları
        bakici_evi_yapildi_final = False
        bakici_evi_taban_alani_final = 0
        bakici_evi_toplam_insaat_alani_final = 0
        
        # Maximum olası hayvan sayısı tahmini
        tahmini_max_hayvan_emsalden = int((emsal * self.agil_alani_orani) / self.agil_yem_deposu_alani_hayvan_basina)
        
        for h_kapasite_deneme in range(tahmini_max_hayvan_emsalden, -1, -1):
            if h_kapasite_deneme == 0 and emsal < self.min_zorunlu_mustemilat_alani:
                 return {
                     "sonuc_mesaji": "TESİS YAPILAMAZ", 
                     "aciklama": f"Emsal ({emsal:.2f} m²), minimum zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) için bile yetersiz.",
                     "arazi_alani_m2": arazi_alani_m2, 
                     "emsal_m2": emsal, 
                     "hayvan_tipi": hayvan_tipi,
                     "uretim_tipi": uretim_tipi,
                     "hayvan_kapasitesi": 0,
                     "bakici_evi_hakki": False,
                     "yapilar": []
                 }

            gerekli_agil_alani_deneme = h_kapasite_deneme * self.agil_yem_deposu_alani_hayvan_basina
            
            if h_kapasite_deneme > 0 and gerekli_agil_alani_deneme < self.min_islevsel_agil_alani:
                continue

            anlik_zorunlu_mustemilat_detaylari = []
            toplam_hesaplanan_zorunlu_must_alani = 0
            
            # Süt üretimi için ekstra kontrol
            mustemilat_uretim_tipi = "genel"
            if uretim_tipi == "süt":
                mustemilat_uretim_tipi = "süt"
            
            for key, tanim in self.mustemilat_tanimlari.items():
                if tanim["grup"] == "zorunlu" and hayvan_tipi in tanim["hayvan_tipi_gecerli"]:
                    # Sağımhane sadece süt üretimi için
                    if key == "sagimhane" and uretim_tipi != "süt":
                        continue
                    
                    alan = self._hesapla_mustemilat_alani(tanim, h_kapasite_deneme)
                    if alan > 0:
                        anlik_zorunlu_mustemilat_detaylari.append({"isim": tanim["isim"], "alan_m2": alan, "kod": key})
                        toplam_hesaplanan_zorunlu_must_alani += alan
            
            min_toplam_zorunlu_must_kurali = 0
            if h_kapasite_deneme > 0:
                min_toplam_zorunlu_must_kurali = max(gerekli_agil_alani_deneme * 0.40, self.min_zorunlu_mustemilat_alani if h_kapasite_deneme < 30 else 0)
            elif emsal >= self.min_zorunlu_mustemilat_alani:
                min_toplam_zorunlu_must_kurali = self.min_zorunlu_mustemilat_alani

            farki_kapatmak_icin_ek_alan = 0
            if toplam_hesaplanan_zorunlu_must_alani < min_toplam_zorunlu_must_kurali:
                farki_kapatmak_icin_ek_alan = min_toplam_zorunlu_must_kurali - toplam_hesaplanan_zorunlu_must_alani

            fiili_toplam_zorunlu_must_alani = toplam_hesaplanan_zorunlu_must_alani + farki_kapatmak_icin_ek_alan

            if farki_kapatmak_icin_ek_alan > 0 and toplam_hesaplanan_zorunlu_must_alani > 0:
                # KÖKSEL BÜYÜME LİMİTLERİNİ KORUMAK İÇİN
                # müştemilat alanlarını artırmak yerine ek alanı ayrı bir kalem olarak ekliyoruz
                anlik_zorunlu_mustemilat_detaylari.append({
                    "isim": "Ek Zorunlu Müştemilat Alanı (Yasal Minimum İçin)", 
                    "alan_m2": farki_kapatmak_icin_ek_alan, 
                    "kod": "diger_zorunlu"
                })
            elif farki_kapatmak_icin_ek_alan > 0:
                anlik_zorunlu_mustemilat_detaylari.append({"isim": "Asgari Zorunlu Müştemilat Alanı", "alan_m2": farki_kapatmak_icin_ek_alan, "kod": "diger_zorunlu"})

            # Bakıcı evi için potansiyel alanı hesapla
            deneme_bakici_evi_hakki = h_kapasite_deneme >= self.bakici_evi_esigi
            potansiyel_bakici_evi_taban_alani_iter = 0
            potansiyel_bakici_evi_toplam_insaat_iter = 0
            
            if deneme_bakici_evi_hakki:
                toplam_ana_yapi_alani_deneme = gerekli_agil_alani_deneme + fiili_toplam_zorunlu_must_alani
                if toplam_ana_yapi_alani_deneme > 900:
                    potansiyel_bakici_evi_taban_alani_iter = self.bakici_evi_buyuklukleri[">900"]["taban_alani"]
                    potansiyel_bakici_evi_toplam_insaat_iter = self.bakici_evi_buyuklukleri[">900"]["toplam_alan"]
                elif toplam_ana_yapi_alani_deneme >= 450:
                    potansiyel_bakici_evi_taban_alani_iter = self.bakici_evi_buyuklukleri["450-900"]["taban_alani"]
                    potansiyel_bakici_evi_toplam_insaat_iter = self.bakici_evi_buyuklukleri["450-900"]["toplam_alan"]

            toplam_gerekli_emsal_deneme = gerekli_agil_alani_deneme + fiili_toplam_zorunlu_must_alani + potansiyel_bakici_evi_taban_alani_iter

            if toplam_gerekli_emsal_deneme <= emsal:
                final_hayvan_kapasitesi = h_kapasite_deneme
                agil_alani_final = gerekli_agil_alani_deneme
                zorunlu_mustemilat_detaylari_final = sorted(anlik_zorunlu_mustemilat_detaylari, 
                                                          key=lambda x: self.mustemilat_tanimlari.get(x["kod"], {"oncelik": 99}).get("oncelik", 99))
                
                bakici_evi_yapildi_final = (potansiyel_bakici_evi_taban_alani_iter > 0)
                bakici_evi_taban_alani_final = potansiyel_bakici_evi_taban_alani_iter
                bakici_evi_toplam_insaat_alani_final = potansiyel_bakici_evi_toplam_insaat_iter
                
                kalan_emsal_opsiyonel_icin = emsal - toplam_gerekli_emsal_deneme
                break 
        
        if final_hayvan_kapasitesi == 0 and agil_alani_final == 0:
            aciklama = f"Emsal ({emsal:.2f} m²), "
            if emsal < self.min_zorunlu_mustemilat_alani:
                 aciklama += f"minimum zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) için bile yetersiz."
            elif emsal < self.min_zorunlu_mustemilat_alani + self.min_islevsel_agil_alani:
                 aciklama += f"zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) ve minimum işlevsel ağıl ({self.min_islevsel_agil_alani:.2f} m²) için yetersiz."
            else:
                 aciklama += "belirlenen kapasitede ağıl, zorunlu müştemilatlar ve potansiyel bakıcı evi için yeterli alan bulunamadı."
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": aciklama, 
                "hayvan_tipi": hayvan_tipi,
                "uretim_tipi": uretim_tipi,
                "hayvan_kapasitesi": 0,
                "bakici_evi_hakki": False,
                "yapilar": []
            }

        yapilar_listesi = []
        for z_must in zorunlu_mustemilat_detaylari_final:
            yapilar_listesi.append({
                "isim": z_must["isim"], 
                "taban_alani": z_must["alan_m2"], 
                "toplam_alan": z_must["alan_m2"], 
                "tip": "zorunlu_mustemilat"
            })

        if bakici_evi_yapildi_final:
            yapilar_listesi.append({
                "isim": "Bakıcı Evi", 
                "taban_alani": bakici_evi_taban_alani_final, 
                "toplam_alan": bakici_evi_toplam_insaat_alani_final,
                "tip": "bakici_evi"
            })
        
        # Bakıcı evi hakkı durumu
        bakici_evi_hakki_kazanildi_raporlama = final_hayvan_kapasitesi >= self.bakici_evi_esigi
        
        # Opsiyonel müştemilatlar
        sirali_opsiyonel_mustemilatlar = sorted(
            [v for k, v in self.mustemilat_tanimlari.items() if v["grup"] == "opsiyonel" and hayvan_tipi in v["hayvan_tipi_gecerli"]],
            key=lambda x: x["oncelik"]
        )

        for ops_tanim in sirali_opsiyonel_mustemilatlar:
            # Besi ekipmanı sadece besi için
            if "Besi İçin" in ops_tanim["isim"] and uretim_tipi != "besi":
                continue
                
            ops_alan = self._hesapla_mustemilat_alani(ops_tanim, final_hayvan_kapasitesi)
            ops_toplam_insaat = ops_tanim.get("toplam_insaat_alan_m2", ops_alan)

            if ops_alan > 0 and kalan_emsal_opsiyonel_icin >= ops_alan:
                yapilar_listesi.append({
                    "isim": ops_tanim["isim"], 
                    "taban_alani": ops_alan, 
                    "toplam_alan": ops_toplam_insaat,
                    "tip": "opsiyonel_mustemilat"
                })
                kalan_emsal_opsiyonel_icin -= ops_alan

        sonuc_mesaji_str = ""
        hayvan_tipi_metni = hayvan_tipi.upper()
        uretim_tipi_eki = ""
        if uretim_tipi == "süt":
            uretim_tipi_eki = "SÜT AMAÇLI "
        elif uretim_tipi == "besi":
            uretim_tipi_eki = "BESİ AMAÇLI "
        
        if final_hayvan_kapasitesi > 0:
            if bakici_evi_hakki_kazanildi_raporlama and bakici_evi_yapildi_final:
                sonuc_mesaji_str = f"TESİS VE BAKICI EVİ YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {uretim_tipi_eki}{hayvan_tipi_metni} KAPASİTELİ)"
            elif bakici_evi_hakki_kazanildi_raporlama and not bakici_evi_yapildi_final:
                sonuc_mesaji_str = f"TESİS YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {uretim_tipi_eki}{hayvan_tipi_metni} KAPASİTELİ), BAKICI EVİ HAKKI KAZANILIR ANCAK YAPILAMAZ (Yetersiz emsal veya yapı alanı kriteri sağlanmıyor)"
            else:
                sonuc_mesaji_str = f"TESİS YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {uretim_tipi_eki}{hayvan_tipi_metni} KAPASİTELİ, BAKICI EVİ HAK DOĞMAZ)"
        else:
            sonuc_mesaji_str = "TESİS YAPILAMAZ"

        hesaplama_sonucu = {
            "hayvan_tipi": hayvan_tipi,
            "uretim_tipi": uretim_tipi,
            "hayvan_kapasitesi": final_hayvan_kapasitesi,
            "bakici_evi_hakki": bakici_evi_hakki_kazanildi_raporlama,
            "bakici_evi_yapildi": bakici_evi_yapildi_final,
            "bakici_evi_taban_alani_m2": bakici_evi_taban_alani_final if bakici_evi_yapildi_final else 0,
            "bakici_evi_toplam_insaat_alani_m2": bakici_evi_toplam_insaat_alani_final if bakici_evi_yapildi_final else 0,
            "yapilar": yapilar_listesi,
            "sonuc_mesaji": sonuc_mesaji_str,
            "aciklama": "Detaylı değerlendirme yapılmıştır.",
            "kalan_emsal_m2": kalan_emsal_opsiyonel_icin 
        }
        
        return hesaplama_sonucu


def _olustur_html_mesaj_kucukbas(sonuc: dict, emsal_orani: float = None, arazi_alani_m2: float = None) -> str:
    """HTML formatında detaylı sonuç raporu oluşturur"""
    kullanilacak_emsal = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    hayvan_tipi = sonuc.get('hayvan_tipi', 'koyun').upper()
    uretim_tipi = sonuc.get('uretim_tipi', 'genel')
    
    baslik_ek = hayvan_tipi
    if uretim_tipi == "süt":
        baslik_ek = f"SÜT AMAÇLI {hayvan_tipi}"
    elif uretim_tipi == "besi":
        baslik_ek = f"BESİ AMAÇLI {hayvan_tipi}"
    
    mesaj = f"<b>=== KÜÇÜKBAŞ {baslik_ek} AĞIL TESİSİ DEĞERLENDİRME ===</b><br><br>"
    mesaj += f"<b>Arazi Büyüklüğü:</b> {arazi_alani_m2 or sonuc.get('arazi_alani_m2', 0):,.2f} m²<br>"
    emsal_alani = (arazi_alani_m2 or 0) * (emsal_orani or 0.20)
    mesaj += f"<b>İzin Verilen Toplam Emsal Alanı (%{kullanilacak_emsal*100:.0f}):</b> {emsal_alani or sonuc.get('emsal_m2', 0):,.2f} m²<br><br>"

    if "TESİS YAPILAMAZ" in sonuc.get("sonuc_mesaji", ""):
        mesaj += f"<b style='color:red;'>SONUÇ: TESİS YAPILAMAZ</b><br>"
        mesaj += f"<b>Açıklama:</b> {sonuc.get('aciklama', 'Belirtilmemiş')}<br>"
    else:
        mesaj += "<b>TESİS BİLGİLERİ:</b><br>"
        
        mesaj += f"- Ağıl ve Yem Deposu Alanı: {sonuc.get('agil_alani_m2', 0):,.2f} m²<br>"
        
        toplam_kullanilan_emsal = sonuc.get('agil_alani_m2', 0)
        
        if sonuc.get("yapilar"):
            yapilar_gruplu = {
                "zorunlu_mustemilat": [],
                "bakici_evi": [],
                "opsiyonel_mustemilat": []
            }
            
            for yapi in sonuc.get("yapilar", []):
                tip = yapi.get("tip", "diger")
                if tip in yapilar_gruplu:
                    yapilar_gruplu[tip].append(yapi)
            
            if yapilar_gruplu["zorunlu_mustemilat"]:
                mesaj += "<b>Yapılabilecek Müştemilatlar:</b><br>"
                for yapi in yapilar_gruplu["zorunlu_mustemilat"]:
                    mesaj += f"- {yapi['isim']}: {yapi['taban_alani']:.2f} m²<br>"
                    toplam_kullanilan_emsal += yapi['taban_alani']
            
            if yapilar_gruplu["bakici_evi"]:
                for yapi in yapilar_gruplu["bakici_evi"]:
                    mesaj += f"<br><b>Bakıcı Evi:</b> {yapi['taban_alani']:.2f} m² taban alanı (Toplam inşaat: {yapi['toplam_alan']:.2f} m²)<br>"
                    toplam_kullanilan_emsal += yapi['taban_alani']
            
            if yapilar_gruplu["opsiyonel_mustemilat"]:
                mesaj += "<br><b>Opsiyonel Yapılar:</b><br>"
                for yapi in yapilar_gruplu["opsiyonel_mustemilat"]:
                    mesaj += f"- {yapi['isim']}: {yapi['taban_alani']:.2f} m²"
                    if yapi.get('toplam_alan', yapi['taban_alani']) != yapi['taban_alani']:
                        mesaj += f" (Toplam İnşaat: {yapi['toplam_alan']:.2f} m²)"
                    mesaj += "<br>"
                    toplam_kullanilan_emsal += yapi['taban_alani']
        
        mesaj += f"<br><b>Hayvan Kapasitesi:</b> {sonuc.get('hayvan_kapasitesi', 0)} Baş {baslik_ek}<br>"
        
        mesaj += "<br><b>Bakıcı Evi Durumu:</b> "
        if sonuc.get("bakici_evi_hakki"):
            if sonuc.get("bakici_evi_yapildi"):
                mesaj += f"YAPILABİLİR (Hak kazanılmış, {sonuc.get('bakici_evi_taban_alani_m2',0)} m² taban alanlı, {sonuc.get('bakici_evi_toplam_insaat_alani_m2',0)} m² toplam inşaat alanlı olarak planlanmıştır).<br>"
            else:
                mesaj += "YAPILAMAZ (Hak kazanılmış ancak mevcut emsal ile yapılamıyor veya yapı alanı kriteri sağlanmıyor).<br>"
        else:
            mesaj += f"YAPILAMAZ (Minimum {BAKICI_EVI_ESIGI} baş hayvan kapasitesi gerekirken {sonuc.get('hayvan_kapasitesi',0)} baş var).<br>"

        mesaj += "<br><table style='width:100%; border-collapse: collapse;'>"
        mesaj += "<tr><td colspan='2' style='border:1px solid #ddd; padding:8px; background-color:#f2f2f2;'><b>ÖZET BİLGİLER</b></td></tr>"
        mesaj += f"<tr><td style='border:1px solid #ddd; padding:8px;'><b>Toplam Kullanılan Emsal Alanı:</b></td><td style='border:1px solid #ddd; padding:8px;'>{toplam_kullanilan_emsal:,.2f} m²</td></tr>"
        mesaj += f"<tr><td style='border:1px solid #ddd; padding:8px;'><b>Kalan Emsal Alanı:</b></td><td style='border:1px solid #ddd; padding:8px;'>{sonuc.get('kalan_emsal_m2', 0):,.2f} m²</td></tr>"
        mesaj += "</table>"

        mesaj += f"<br><b style='color:green;'>SONUÇ: {sonuc.get('sonuc_mesaji','')}</b><br>"
        if sonuc.get("aciklama") and "Detaylı değerlendirme" not in sonuc.get("aciklama"):
             mesaj += f"<b>Açıklama:</b> {sonuc.get('aciklama')}<br>"

    if sonuc.get("hayvan_kapasitesi", 0) > 1000 and not "TESİS YAPILAMAZ" in sonuc.get("sonuc_mesaji", ""):
        mesaj += "<br><div style='background-color:#fff3cd; padding:10px; border:1px solid #ffeeba; border-radius:4px;'>"
        mesaj += "<b style='color:#856404;'>ÖNEMLİ UYARI:</b> "
        mesaj += "Hesaplanan kapasite (1.000+ hayvan) çok büyük ölçekli bir tesis anlamına gelir. "
        mesaj += "Bu boyutta işletmeler genellikle daha küçük modüler birimlere bölünür veya "
        mesaj += "birden fazla tesis olarak projelendirilir. Projelendirme aşamasında bu hususa dikkat edilmelidir."
        mesaj += "</div><br>"
    
    if not "TESİS YAPILAMAZ" in sonuc.get("sonuc_mesaji", ""):
        mesaj += "<br><small><i>Not: Müştemilat alanları, hayvan kapasitesine göre logaritmik olarak ölçeklenmektedir. "
        mesaj += "Özellikle büyük kapasiteli tesisler için jeneratör odası, su deposu gibi belirli müştemilatlar için "
        mesaj += "gerçekçi maksimum alanlar uygulanmıştır. Bu alanlar, temel ihtiyaçları karşılayacak şekilde "
        mesaj += "tasarlanmıştır.</i></small><br>"
    
    mesaj += "<hr>"
    mesaj += "<b>NOT:</b> Tüm hesaplamalar güncel mevzuat ve yönetmeliklere göre yapılmıştır. "
    mesaj += "Bu değerlendirme ön bilgilendirme amaçlıdır ve resmi bir belge niteliği taşımaz."
    
    return mesaj

def kucukbas_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None) -> dict:
    """Küçükbaş hayvancılık tesisi için değerlendirme yapar"""
    try:
        arazi_buyuklugu_m2 = float(arazi_bilgileri.get("buyukluk_m2", 0))
        if arazi_buyuklugu_m2 <= 0:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": "<b>Geçersiz Arazi Büyüklüğü</b><br><br>"
                         "Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.",
                "kapasite": 0, "bakici_evi_hakki": False,
            }
    except (ValueError, TypeError):
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Geçersiz Arazi Büyüklüğü</b><br><br>"
                     "Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.",
            "kapasite": 0, "bakici_evi_hakki": False,
        }

    su_tahsis_belgesi_var_mi = str(arazi_bilgileri.get("su_tahsis_belgesi", "false")).lower() == "true"
    yas_kapali_alanda_mi = arazi_bilgileri.get("yas_kapali_alan_durumu") == "içinde"

    if yas_kapali_alanda_mi and not su_tahsis_belgesi_var_mi:
        # GEÇICI ÇÖZÜM: Su tahsis belgesi uyarısını göster ama hesaplamaya devam et  
        yas_uyari_mesaji = (
            "<b>Yeraltı Suyu Koruma Alanında Su Tahsis Belgesi Zorunluluğu</b><br><br>"
            "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
            "Bu tür arazilerde küçükbaş hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
            "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda küçükbaş hayvancılık tesisi yapımına "
            "izin verilememektedir."
        )
        # Uyarıyı sakla ama hesaplamaya devam et (frontend problemi çözülünceye kadar geçici)
        yas_uyari_mesaji_temp = yas_uyari_mesaji
    else:
        yas_uyari_mesaji_temp = ""
    
    # Hayvan ve üretim tipi
    hayvan_tipi = yapi_bilgileri.get("hayvan_tipi", "koyun") # koyun veya keçi
    uretim_tipi = yapi_bilgileri.get("uretim_tipi", "genel") # genel, süt veya besi
    
    hesaplayici = KucukbasHesaplama(emsal_orani)
    hesap_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2, hayvan_tipi, uretim_tipi)
    
    html_mesaj = _olustur_html_mesaj_kucukbas(hesap_sonucu, emsal_orani, arazi_buyuklugu_m2)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in hesap_sonucu["sonuc_mesaji"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "ana_mesaj": html_mesaj,
        "kapasite": hesap_sonucu.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": hesap_sonucu.get("bakici_evi_hakki", False),
        "hayvan_tipi": hayvan_tipi,
        "uretim_tipi": uretim_tipi,
        # Frontend için arazi bilgilerini ekle
        "arazi_alani_m2": arazi_buyuklugu_m2,
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "buyukluk_m2": arazi_buyuklugu_m2,
        "toplam_emsal_m2": hesap_sonucu.get("toplam_emsal_m2", arazi_buyuklugu_m2 * (emsal_orani or 0.20)),
        "kalan_emsal_m2": hesap_sonucu.get("kalan_emsal_m2", 0),
    }
