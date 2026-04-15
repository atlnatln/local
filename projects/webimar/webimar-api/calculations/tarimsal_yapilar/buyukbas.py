"""
Büyükbaş Hayvancılık Tesisi (Süt ve Besi) Hesaplama Modülü
"""
import math  # Logaritmik hesaplama için math kütüphanesi eklendi

# Sabit Değerler (buyukbas_hayvancilik_tum_senaryolar.txt ve referans koda göre)
EMSAL_ORANI = 0.20
AHIR_YEM_DEPOSU_ALANI_HAYVAN_BASINA = 15  # m²/hayvan
GEZINTI_ALANI_SUT_SIGIRI = 7  # m²/hayvan (emsale dahil değil)

BAKICI_EVI_ESIKLERI = {
    "süt_sığırı": 25,  # baş
    "besi_sığırı": 50   # baş
}
BAKICI_EVI_BUYUKLUKLERI = {
    "550-1500": {"taban_alani": 75, "toplam_alan": 150},
    ">1500": {"taban_alani": 150, "toplam_alan": 300}
}
BEKCI_KULUBESI_ALANI = 15  # m²
IDARI_BINA_TABAN_ALANI = 75  # m²
IDARI_BINA_TOPLAM_ALAN = 150 # m²

SAGIMHANE_KATSAYI_SUT = 0.3 # Her 10 baş için ~3m², min 15m² (20 baş ve üzeri için)
SUT_DEPOLAMA_ALANI = 15 # m² (süt üretimi için, 20 baş ve üzeri için)
BESI_EKIPMAN_ALANI = 30 # m² (besi için, 30 baş ve üzeri için)

MIN_ZORUNLU_MUSTEMILAT_ALANI = 50  # m² (5 baş hayvandan az ise)
MIN_ISLEVSEL_AHIR_ALANI = 30  # m² (2 baş hayvan için)
AHIR_ALANI_ORANI = 5/7
MUSTEMILAT_ALANI_ORANI = 2/7 # veya ahır alanının %40'ı

# Yeni Gübre Çukuru ve Samanlık Hesaplamaları (m²/hayvan)
GUBRE_CUKURU_ALANLARI = {
    "süt_sığırı": 8.66 / 4,  # 8.66 m² / 4m derinlik = 2.165 m²
    "besi_sığırı": 3.939 / 4  # 3.939 m² / 4m derinlik = 0.98475 m²
}

SAMANLIK_ALANI_BUYUKBAS = 8.4  # m² per hayvan (5m yükseklik)

# Yeni ekleme - Detaylı müştemilat tanımları
MUSTEMILAT_TANIMLARI = {
    # Zorunlu Müştemilatlar (Ahır ve Yem Deposu Hariç)
    "su_deposu": {
        "isim": "Su Deposu", "grup": "zorunlu", "oncelik": 1,
        "min_alan_m2": 5, "artis_hayvan_basi_m2": 0.03, "max_alan_m2": 40,  # max_alan_m2 düşürüldü
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "koksel"
    },
    "malzeme_deposu": {
        "isim": "Malzeme Deposu", "grup": "zorunlu", "oncelik": 2,
        "min_alan_m2": 10, "artis_hayvan_basi_m2": 0.07, "max_alan_m2": 100,  # max_alan_m2 düşürüldü
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "koksel"
    },
    "gubre_deposu": { # Gübre Çukuru / Sıvat Deposu (Derinlik: 4m)
        "isim": "Gübre Deposu/Çukuru (Derinlik: 4m)", "grup": "zorunlu", "oncelik": 3,
        "min_alan_m2": 2, "max_alan_m2": 50000,
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "yeni_orantili",
        "aciklama": "Süt sığırı: 2.165 m², Besi sığırı: 0.985 m² per hayvan (4m derinlik)"
    },
    "jenerator_odasi": {
        "isim": "Jeneratör Odası", "grup": "zorunlu", "oncelik": 4,
        "min_alan_m2": 5, "artis_hayvan_basi_m2": 0.002, "max_alan_m2": 25,  # artış katsayısı dramatik şekilde düşürüldü
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "koksel"
    },
    "revir": {
        "isim": "Revir / Hasta Hayvan Bölümü", "grup": "zorunlu", "oncelik": 5,
        "min_alan_m2": 10, "artis_hayvan_basi_m2": 0.06, "max_alan_m2": 80,  # max_alan_m2 düşürüldü
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "koksel"
    },
    "samanlik": { # Kaba Yem Deposu
        "isim": "Samanlık / Kaba Yem Deposu (Yükseklik: 5m)", "grup": "zorunlu", "oncelik": 6,
        "min_alan_m2": 4, "max_alan_m2": 20000,
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "yeni_orantili",
        "aciklama": "Her büyükbaş hayvan için 8.4 m² alan hesaplanır (5m yükseklik, yıllık kaba yem ihtiyacı)"
    },
    "sagimhane_sut_unitesi": { # Sadece Süt Sığırcılığı için Zorunlu
        "isim": "Sağımhane ve Süt Soğutma/Depolama Ünitesi", "grup": "zorunlu", "oncelik": 7,
        "min_alan_m2": 15,  
        "artis_hayvan_basi_m2": 0.12, 
        "max_alan_m2": 200,  # max_alan_m2 düşürüldü
        "aktiflesme_esigi_hayvan_sayisi": 10,
        "hayvan_tipi_gecerli": ["süt_sığırı"], "buyume_tipi": "koksel"
    },
    # Opsiyonel Müştemilatlar
    "bekci_kulubesi": {
        "isim": "Bekçi Kulübesi", "grup": "opsiyonel", "oncelik": 10,
        "sabit_alan_m2": 15,
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"]
    },
    "idari_bina": {
        "isim": "İdari Bina", "grup": "opsiyonel", "oncelik": 11,
        "sabit_alan_m2": 75, # Taban alanı
        "toplam_insaat_alan_m2": 150, # İki katlı olabilir
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"]
    },
    "besi_ozel_ekipman_alani": { # Sadece Besi Sığırcılığı için Opsiyonel
        "isim": "Besi İçin Özel Ekipman ve Yem Hazırlama Alanı", "grup": "opsiyonel", "oncelik": 12,
        "min_alan_m2": 20,
        "artis_hayvan_basi_m2": 0.2, "max_alan_m2": 50,
        "aktiflesme_esigi_hayvan_sayisi": 30, # Örneğin 30 baş ve üzeri için düşünülür
        "hayvan_tipi_gecerli": ["besi_sığırı"], "buyume_tipi": "koksel"
    },
    "paketleme_tesisi": {
        "isim": "Paketleme Tesisi ve Deposu", "grup": "opsiyonel", "oncelik": 13,
        "min_alan_m2": 50, "artis_hayvan_basi_m2": 0.5, "max_alan_m2": 200,
        "hayvan_tipi_gecerli": ["süt_sığırı", "besi_sığırı"], "buyume_tipi": "koksel" # Genellikle büyük işletmeler için
    }
}

# Büyükbaş müştemilatlar için köksel büyüme limitlerini ve parametrelerini tanımla (Mantar tesisine benzer)
# Bu değerler kullanıcının istediği maksimum sınırları yansıtır
# NOT: gubre_deposu ve samanlik doğru orantılı büyür, köksel değil!
BUYUKBAS_KOKSEL_LIMITLER = {
    "su_deposu": {"baslangic": 5, "max_limit": 40, "buyume_faktoru": 0.3},               # Max: 40 m²
    "malzeme_deposu": {"baslangic": 10, "max_limit": 100, "buyume_faktoru": 0.5},      # Max: 100 m²
    "jenerator_odasi": {"baslangic": 5, "max_limit": 25, "buyume_faktoru": 0.2},       # Max: 25 m²
    "revir": {"baslangic": 10, "max_limit": 80, "buyume_faktoru": 0.4},                # Max: 80 m²
    "sagimhane_sut_unitesi": {"baslangic": 15, "max_limit": 200, "buyume_faktoru": 0.5}, # Max: 200 m²
    "besi_ozel_ekipman_alani": {"baslangic": 20, "max_limit": 50, "buyume_faktoru": 0.4},
    "paketleme_tesisi": {"baslangic": 50, "max_limit": 200, "buyume_faktoru": 0.6}
}

class BuyukbasHesaplama:
    def __init__(self, emsal_orani: float = None):
        self.emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
        self.ahir_yem_deposu_alani_hayvan_basina = AHIR_YEM_DEPOSU_ALANI_HAYVAN_BASINA
        self.gezinti_alani_sut_sigiri = GEZINTI_ALANI_SUT_SIGIRI
        self.bakici_evi_esikleri = BAKICI_EVI_ESIKLERI
        self.bakici_evi_buyuklukleri = BAKICI_EVI_BUYUKLUKLERI
        self.bekci_kulubesi_alani = BEKCI_KULUBESI_ALANI
        self.idari_bina_taban_alani = IDARI_BINA_TABAN_ALANI
        self.idari_bina_toplam_alan = IDARI_BINA_TOPLAM_ALAN
        self.sagimhane_katsayi_sut = SAGIMHANE_KATSAYI_SUT
        self.sut_depolama_alani = SUT_DEPOLAMA_ALANI
        self.besi_ekipman_alani = BESI_EKIPMAN_ALANI
        self.min_zorunlu_mustemilat_alani = MIN_ZORUNLU_MUSTEMILAT_ALANI
        self.min_islevsel_ahir_alani = MIN_ISLEVSEL_AHIR_ALANI
        self.ahir_alani_orani = AHIR_ALANI_ORANI
        self.mustemilat_alani_orani = MUSTEMILAT_ALANI_ORANI
        # Yeni eklenen özellik
        self.mustemilat_tanimlari = MUSTEMILAT_TANIMLARI
        # Mantar tesisindeki gibi köksel büyüme limitlerini ekle
        self.koksel_limitler = BUYUKBAS_KOKSEL_LIMITLER
        self.gubre_cukuru_alanlari = GUBRE_CUKURU_ALANLARI
        self.samanlik_alani = SAMANLIK_ALANI_BUYUKBAS

    def _hesapla_mustemilat_alani(self, must_tanimi: dict, hayvan_kapasitesi: int, hayvan_tipi: str = "süt_sığırı") -> float:
        """
        Belirli bir müştemilat için hayvan kapasitesine göre alan hesaplar.
        Mantar tesisindeki gibi köksel büyüme kontrolü ve maksimum limitler uygular.
        """
        if must_tanimi.get("aktiflesme_esigi_hayvan_sayisi", 0) > hayvan_kapasitesi:
            return 0.0

        # kod değişkenini fonksiyon başında tanımla
        kod = next((k for k, v in self.mustemilat_tanimlari.items() if v == must_tanimi), None)

        # Sabit alan varsa direkt döndür
        if "sabit_alan_m2" in must_tanimi:
            return must_tanimi["sabit_alan_m2"]
        
        # Mantar tesisindeki gibi köksel büyüme kontrolü uygula
        buyume_tipi = must_tanimi.get("buyume_tipi", "dogrusal")
        
        # Eğer bu müştemilat için özel köksel limit tanımlıysa onu kullan (buyume_tipi kontrolü kaldırıldı)
        if kod in self.koksel_limitler:
            config = self.koksel_limitler[kod]
            baslangic = config["baslangic"]
            max_limit = config["max_limit"] 
            buyume_faktoru = config["buyume_faktoru"]
            
            # Referans kapasiteyi dinamik belirle (100 hayvan referans olarak alınsın)
            ref_kapasite = 100
            oran = hayvan_kapasitesi / ref_kapasite
            
            # Kök bazlı büyüme formülü:
            # baslangic + (max_limit - baslangic) * min(1.0, sqrt(oran * buyume_faktoru))
            if hayvan_kapasitesi <= ref_kapasite:
                # Referans kapasiteye kadar daha hızlı artan bir eğri
                artis_faktoru = (oran * buyume_faktoru) ** 0.5
            else:
                # Referans kapasiteden sonra daha yavaş büyüyen bir eğri
                import math
                artis_faktoru = (1 + math.log(oran, 2) * buyume_faktoru) ** 0.5 - 1
            
            artis_faktoru = min(1.0, artis_faktoru)  # En fazla 1.0 olabilir
            hesaplanan_alan = baslangic + (max_limit - baslangic) * artis_faktoru
            alan = max(baslangic, min(max_limit, hesaplanan_alan))
            return alan
        
        # Standart hesaplama (eski kodun korunmuş hali)
        alan = must_tanimi.get("min_alan_m2", 0)
        
        # Büyük tesisler için özel ölçekleme uygulanacak müştemilatlar
        ozel_olcekleme_gerektiren_mustemilatlar = ["jenerator_odasi", "revir", "su_deposu"]
        
        # Jeneratör odası için çok daha sıkı bir ölçekleme stratejisi
        if kod == "jenerator_odasi":
            if hayvan_kapasitesi < 50:
                val = 10
            else:
                val = 10 + 30 * math.log10(hayvan_kapasitesi / 50)
            val = round(val, 2)
            return min(val, must_tanimi.get("max_alan_m2", 100))
        
        # Diğer kritik müştemilatlar için özel bir ölçekleme fonksiyonu
        elif kod in ozel_olcekleme_gerektiren_mustemilatlar:
            if hayvan_kapasitesi > 20000:  # Çok büyük tesisler için sabit değerler
                # 20,000+ baş için kritik altyapı müştemilat boyutları çok fazla büyümemeli
                if kod == "su_deposu":
                    return min(40, must_tanimi.get("max_alan_m2", 40))  # Sabit 40m² veya max değer
                elif kod == "revir":
                    return min(80, must_tanimi.get("max_alan_m2", 80))  # Sabit 80m² veya max değer
            elif hayvan_kapasitesi > 1000:
                # 1000-20,000 arası hayvan için çok daha agresif ölçekleme
                if hayvan_kapasitesi > 5000:  # Çok büyük tesisler
                    olcekleme_faktoru = 0.005 + (0.01 * (math.log10(1000) / math.log10(hayvan_kapasitesi)))
                else:  # Orta büyüklükteki tesisler
                    olcekleme_faktoru = 0.05 + (0.1 * (math.log10(1000) / math.log10(hayvan_kapasitesi)))
                
                artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * hayvan_kapasitesi * olcekleme_faktoru
                alan += artis
                return min(alan, must_tanimi.get("max_alan_m2", float('inf')))

        # YENİ ORANTILI: Gübre deposu ve samanlık için hayvan tipine göre alan hesaplama
        if kod in ["gubre_deposu", "samanlik"] and must_tanimi.get("buyume_tipi") == "yeni_orantili":
            if kod == "gubre_deposu":
                # Hayvan tipine göre gübre çukuru alanı
                if hayvan_tipi == "süt_sığırı":
                    alan_per_hayvan = self.gubre_cukuru_alanlari["süt_sığırı"]
                elif hayvan_tipi == "besi_sığırı":
                    alan_per_hayvan = self.gubre_cukuru_alanlari["besi_sığırı"]
                else:
                    alan_per_hayvan = self.gubre_cukuru_alanlari["süt_sığırı"]  # varsayılan
                
                alan = hayvan_kapasitesi * alan_per_hayvan
                return max(alan, must_tanimi.get("min_alan_m2", 0))
                
            elif kod == "samanlik":
                # Samanlık için sabit alan per hayvan
                alan = hayvan_kapasitesi * self.samanlik_alani
                return max(alan, must_tanimi.get("min_alan_m2", 0))
        
        # Gübre deposu ve samanlık TAM ORANTILI (lineer) büyüme - özel ölçekleme YOK!
        if kod in ["gubre_deposu", "samanlik"]:
            olcekleme_faktoru = 1.0  # Tam orantılı
        # Sağımhane için özel ölçekleme - daha da agresif sınırlandırma
        elif kod == "sagimhane_sut_unitesi":
            if hayvan_kapasitesi > 20000:  # Çok büyük tesisler için daha agresif ölçekleme
                olcekleme_faktoru = 0.005 + (0.005 * (math.log10(5000) / math.log10(hayvan_kapasitesi)))
            elif hayvan_kapasitesi > 5000:
                olcekleme_faktoru = 0.02 + (0.03 * (math.log10(5000) / math.log10(hayvan_kapasitesi)))
            elif hayvan_kapasitesi > 500:
                olcekleme_faktoru = 0.1 + (0.1 * (math.log10(500) / math.log10(hayvan_kapasitesi)))
            else:
                olcekleme_faktoru = 1.0
        # Diğer müştemilatlar için normal logaritmik ölçekleme
        else:
            olcekleme_faktoru = 1.0
            if hayvan_kapasitesi > 500:
                # Orta büyüklükteki tesisler (500-5000 arası)
                if hayvan_kapasitesi <= 5000:  
                    olcekleme_faktoru = 0.3 + (0.5 * (math.log10(500) / math.log10(hayvan_kapasitesi)))
                # Büyük tesisler (5000-15000 arası)
                elif hayvan_kapasitesi <= 15000:  
                    olcekleme_faktoru = 0.15 + (0.15 * (math.log10(5000) / math.log10(hayvan_kapasitesi)))
                # Çok büyük tesisler (15000-30000 arası)
                elif hayvan_kapasitesi <= 30000:  
                    olcekleme_faktoru = 0.05 + (0.1 * (math.log10(15000) / math.log10(hayvan_kapasitesi)))
                # Devasa tesisler (30000+)
                else:
                    olcekleme_faktoru = 0.03 + (0.02 * (math.log10(30000) / math.log10(hayvan_kapasitesi)))

        artis = must_tanimi.get("artis_hayvan_basi_m2", 0) * hayvan_kapasitesi * olcekleme_faktoru
        alan += artis
        
        # KESİN MAKSİMUM LİMİT KONTROLÜ - Bu çok önemli!
        if "max_alan_m2" in must_tanimi:
            alan = min(alan, must_tanimi["max_alan_m2"])

        return alan

    def hesapla(self, arazi_alani_m2: float, hayvan_tipi: str, buyuk_ova_alaninda_mi: bool = False):
        """Büyükbaş hayvancılık tesisi için alan ve kapasite hesaplaması yapar"""
        emsal = arazi_alani_m2 * self.emsal_orani
        bakici_evi_esigi = self.bakici_evi_esikleri[hayvan_tipi]

        # Emsal alanı, minimum zorunlu müştemilat alanından bile azsa, hiçbir şekilde yapılamaz
        if emsal < self.min_zorunlu_mustemilat_alani:
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": f"Emsale göre izin verilen {emsal:.2f} m² yapılaşma alanı, zorunlu müştemilat için gerekli olan minimum {self.min_zorunlu_mustemilat_alani:.2f} m²'den bile azdır.",
                "arazi_alani_m2": arazi_alani_m2, 
                "emsal_m2": emsal, 
                "hayvan_tipi": hayvan_tipi, 
                "hayvan_kapasitesi": 0,
                "bakici_evi_hakki": False, 
                "yapilar": []
            }
        
        # Emsal yeterli ama ahır için alan kalmıyorsa yine yapılamaz
        if emsal < self.min_zorunlu_mustemilat_alani + self.min_islevsel_ahir_alani:
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": f"Zorunlu müştemilat alanı ({self.min_zorunlu_mustemilat_alani:.2f} m²) karşılandıktan sonra ahır için yeterli ({self.min_islevsel_ahir_alani:.2f} m²) alan kalmamaktadır.",
                "arazi_alani_m2": arazi_alani_m2, 
                "emsal_m2": emsal, 
                "hayvan_tipi": hayvan_tipi, 
                "hayvan_kapasitesi": 0,
                "bakici_evi_hakki": False, 
                "yapilar": []
            }

        # ---------- Yeniden Yapılandırılmış Hesaplama Mantığı ----------
        final_hayvan_kapasitesi = 0
        ahir_alani_final = 0
        zorunlu_mustemilat_detaylari_final = []
        # Kalan emsal, ahır, zorunlu müştemilatlar VE bakıcı evi (yapılırsa) sonrası
        kalan_emsal_opsiyonel_icin = 0 
        
        # Bakıcı evi detayları (iterasyonla belirlenecek)
        bakici_evi_yapildi_final = False
        bakici_evi_taban_alani_final = 0
        bakici_evi_toplam_insaat_alani_final = 0
        
        # Maksimum olası hayvan sayısından başlayarak en uygun kapasiteyi bulma (iteratif yaklaşım)
        tahmini_max_hayvan_emsalden = int((emsal * self.ahir_alani_orani) / self.ahir_yem_deposu_alani_hayvan_basina)
        
        for h_kapasite_deneme in range(tahmini_max_hayvan_emsalden, -1, -1):
            if h_kapasite_deneme == 0 and emsal < self.min_zorunlu_mustemilat_alani:
                 return {
                     "sonuc_mesaji": "TESİS YAPILAMAZ", 
                     "aciklama": f"Emsal ({emsal:.2f} m²), minimum zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) için bile yetersiz.",
                     "arazi_alani_m2": arazi_alani_m2, 
                     "emsal_m2": emsal, 
                     "hayvan_tipi": hayvan_tipi,
                     "hayvan_kapasitesi": 0,
                     "bakici_evi_hakki": False,
                     "yapilar": []
                 }

            gerekli_ahir_alani_deneme = h_kapasite_deneme * self.ahir_yem_deposu_alani_hayvan_basina
            
            if h_kapasite_deneme > 0 and gerekli_ahir_alani_deneme < self.min_islevsel_ahir_alani:
                continue

            anlik_zorunlu_mustemilat_detaylari = []
            toplam_hesaplanan_zorunlu_must_alani = 0
            for key, tanim in self.mustemilat_tanimlari.items():
                if tanim["grup"] == "zorunlu" and hayvan_tipi in tanim["hayvan_tipi_gecerli"]:
                    alan = self._hesapla_mustemilat_alani(tanim, h_kapasite_deneme, hayvan_tipi)
                    if alan > 0:
                        anlik_zorunlu_mustemilat_detaylari.append({"isim": tanim["isim"], "alan_m2": alan, "kod": key})
                        toplam_hesaplanan_zorunlu_must_alani += alan
            
            min_toplam_zorunlu_must_kurali = 0
            if h_kapasite_deneme > 0:
                min_toplam_zorunlu_must_kurali = max(gerekli_ahir_alani_deneme * 0.40, self.min_zorunlu_mustemilat_alani if h_kapasite_deneme < 5 else 0)
            elif emsal >= self.min_zorunlu_mustemilat_alani:
                min_toplam_zorunlu_must_kurali = self.min_zorunlu_mustemilat_alani

            farki_kapatmak_icin_ek_alan = 0
            if toplam_hesaplanan_zorunlu_must_alani < min_toplam_zorunlu_must_kurali:
                farki_kapatmak_icin_ek_alan = min_toplam_zorunlu_must_kurali - toplam_hesaplanan_zorunlu_must_alani

            fiili_toplam_zorunlu_must_alani = toplam_hesaplanan_zorunlu_must_alani + farki_kapatmak_icin_ek_alan

            if farki_kapatmak_icin_ek_alan > 0 and toplam_hesaplanan_zorunlu_must_alani > 0:
                # ESKI YÖNTEMİ KALDIRDIK: Köksel büyüme limitlerini korumak için 
                # müştemilat alanlarını artırmak yerine ek alanı ayrı bir kalem olarak ekliyoruz
                anlik_zorunlu_mustemilat_detaylari.append({
                    "isim": "Ek Zorunlu Müştemilat Alanı (Yasal Minimum İçin)", 
                    "alan_m2": farki_kapatmak_icin_ek_alan, 
                    "kod": "diger_zorunlu"
                })
            elif farki_kapatmak_icin_ek_alan > 0:
                anlik_zorunlu_mustemilat_detaylari.append({"isim": "Asgari Zorunlu Müştemilat Alanı", "alan_m2": farki_kapatmak_icin_ek_alan, "kod": "diger_zorunlu"})

            # Bakıcı evi için potansiyel alanı hesapla (eğer hak kazanılıyorsa ve yapılabiliyorsa)
            deneme_bakici_evi_hakki = h_kapasite_deneme >= bakici_evi_esigi
            potansiyel_bakici_evi_taban_alani_iter = 0
            potansiyel_bakici_evi_toplam_insaat_iter = 0
            
            if deneme_bakici_evi_hakki:
                toplam_ana_yapi_alani_deneme = gerekli_ahir_alani_deneme + fiili_toplam_zorunlu_must_alani
                if toplam_ana_yapi_alani_deneme > 1500:
                    potansiyel_bakici_evi_taban_alani_iter = self.bakici_evi_buyuklukleri[">1500"]["taban_alani"]
                    potansiyel_bakici_evi_toplam_insaat_iter = self.bakici_evi_buyuklukleri[">1500"]["toplam_alan"]
                elif toplam_ana_yapi_alani_deneme >= 550:
                    potansiyel_bakici_evi_taban_alani_iter = self.bakici_evi_buyuklukleri["550-1500"]["taban_alani"]
                    potansiyel_bakici_evi_toplam_insaat_iter = self.bakici_evi_buyuklukleri["550-1500"]["toplam_alan"]

            toplam_gerekli_emsal_deneme = gerekli_ahir_alani_deneme + fiili_toplam_zorunlu_must_alani + potansiyel_bakici_evi_taban_alani_iter

            if toplam_gerekli_emsal_deneme <= emsal:
                final_hayvan_kapasitesi = h_kapasite_deneme
                ahir_alani_final = gerekli_ahir_alani_deneme
                zorunlu_mustemilat_detaylari_final = sorted(anlik_zorunlu_mustemilat_detaylari, 
                                                          key=lambda x: self.mustemilat_tanimlari.get(x["kod"], {"oncelik": 99}).get("oncelik", 99))
                
                bakici_evi_yapildi_final = (potansiyel_bakici_evi_taban_alani_iter > 0)
                bakici_evi_taban_alani_final = potansiyel_bakici_evi_taban_alani_iter
                bakici_evi_toplam_insaat_alani_final = potansiyel_bakici_evi_toplam_insaat_iter
                
                kalan_emsal_opsiyonel_icin = emsal - toplam_gerekli_emsal_deneme
                break 
        
        if final_hayvan_kapasitesi == 0 and ahir_alani_final == 0: # Ve bakıcı evi de yapılamadıysa
            # Bu durum, ya başlangıçta emsal yetersizdir ya da min. işlevsel ahır + min. müştemilat sığmıyordur.
            # Başlangıç kontrolleri bu durumu yakalamalı.
            aciklama = f"Emsal ({emsal:.2f} m²), "
            if emsal < self.min_zorunlu_mustemilat_alani:
                 aciklama += f"minimum zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) için bile yetersiz."
            elif emsal < self.min_zorunlu_mustemilat_alani + self.min_islevsel_ahir_alani:
                 aciklama += f"zorunlu müştemilat ({self.min_zorunlu_mustemilat_alani:.2f} m²) ve minimum işlevsel ahır ({self.min_islevsel_ahir_alani:.2f} m²) için yetersiz."
            else:
                 aciklama += "belirlenen kapasitede ahır, zorunlu müştemilatlar ve potansiyel bakıcı evi için yeterli alan bulunamadı."
            return {
                "sonuc_mesaji": "TESİS YAPILAMAZ", 
                "aciklama": aciklama, 
                "arazi_alani_m2": arazi_alani_m2, 
                "emsal_m2": emsal, 
                "hayvan_tipi": hayvan_tipi,
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
        
        # Raporlama için bakıcı evi hakkı durumu
        bakici_evi_hakki_kazanildi_raporlama = final_hayvan_kapasitesi >= bakici_evi_esigi

        sonuc_mesaji_str = ""
        hayvan_tipi_metni = "SÜT SIĞIRI" if hayvan_tipi == "süt_sığırı" else "BESİ SIĞIRI"
        if final_hayvan_kapasitesi > 0:
            if bakici_evi_hakki_kazanildi_raporlama and bakici_evi_yapildi_final:
                sonuc_mesaji_str = f"TESİS VE BAKICI EVİ YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {hayvan_tipi_metni} KAPASİTELİ)"
            elif bakici_evi_hakki_kazanildi_raporlama and not bakici_evi_yapildi_final:
                sonuc_mesaji_str = f"TESİS YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {hayvan_tipi_metni} KAPASİTELİ), BAKICI EVİ HAKKI KAZANILIR ANCAK YAPILAMAZ (Yetersiz emsal veya yapı alanı kriteri sağlanmıyor)"
            else: # bakıcı evi hakkı kazanılmadı
                sonuc_mesaji_str = f"TESİS YAPILABİLİR ({final_hayvan_kapasitesi} BAŞ {hayvan_tipi_metni} KAPASİTELİ, BAKICI EVİ HAK DOĞMAZ)"
        else:
            sonuc_mesaji_str = "TESİS YAPILAMAZ"
            # Açıklama zaten ilk kontrollerde veya iterasyon sonrası 'if final_hayvan_kapasitesi == 0' bloğunda set edilmiş olmalı.

        hesaplama_sonucu = {
            "arazi_alani_m2": arazi_alani_m2,
            "emsal_m2": emsal,
            "hayvan_tipi": hayvan_tipi,
            "ahir_alani_m2": ahir_alani_final,
            "mustemilat_alani_m2": sum(yapi["taban_alani"] for yapi in yapilar_listesi if yapi["tip"] == "zorunlu_mustemilat"),
            "hayvan_kapasitesi": final_hayvan_kapasitesi,
            "bakici_evi_hakki": bakici_evi_hakki_kazanildi_raporlama, # Raporlama için genel hak durumu
            "bakici_evi_yapildi": bakici_evi_yapildi_final, # Fiili yapılma durumu
            "bakici_evi_taban_alani_m2": bakici_evi_taban_alani_final if bakici_evi_yapildi_final else 0,
            "bakici_evi_toplam_insaat_alani_m2": bakici_evi_toplam_insaat_alani_final if bakici_evi_yapildi_final else 0,
            "yapilar": yapilar_listesi,
            "sonuc_mesaji": sonuc_mesaji_str,
            "aciklama": "Detaylı değerlendirme yapılmıştır.", # Bu, _olustur_html_mesaj_buyukbas içinde daha spesifik bir açıklama ile desteklenebilir.
            "kalan_emsal_m2": kalan_emsal_opsiyonel_icin 
        }
        
        # Süt sığırları için gezinti alanı hesaplaması ve kontrolü
        if hayvan_tipi == "süt_sığırı" and final_hayvan_kapasitesi > 0:
            gezinti_alani_gerekli = final_hayvan_kapasitesi * self.gezinti_alani_sut_sigiri
            hesaplama_sonucu["gezinti_alani_m2_gerekli"] = gezinti_alani_gerekli
            
            if arazi_alani_m2 < (emsal + hesaplama_sonucu["gezinti_alani_m2_gerekli"]):
                 hesaplama_sonucu["uyari_gezinti_alani"] = f"Dikkat: {final_hayvan_kapasitesi} baş süt sığırı için gereken {hesaplama_sonucu['gezinti_alani_m2_gerekli']:.2f} m² gezinti alanını karşılamak için toplam arazi büyüklüğü yetersiz olabilir."

        return hesaplama_sonucu


def _olustur_html_mesaj_buyukbas(sonuc: dict, baslik_ek: str, emsal_orani: float = None, arazi_alani_m2: float = None) -> str:
    """HTML formatında minimum sütunlu, mantar tesisiyle uyumlu renkli ve çerçeveli detaylı sonuç raporu oluşturur"""
    kullanilacak_emsal = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    mesaj = """
    <style>
        .buyukbas-sonuc {font-family: Arial, sans-serif;}
        .buyukbas-sonuc h3 {color: #3c763d; margin-bottom: 15px;}
        .buyukbas-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .buyukbas-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .buyukbas-sonuc th, .buyukbas-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .buyukbas-sonuc th {background-color: #f2f2f2;}
        .buyukbas-sonuc .ahir {background-color: #e8f4f8;}
        .buyukbas-sonuc .mustemilat {background-color: #eaf7ea;}
        .buyukbas-sonuc .opsiyonel {background-color: #fffbe6;}
        .buyukbas-sonuc .bakici {background-color: #fef6e4;}
        .buyukbas-sonuc .ozet {background-color: #f8f9fa;}
        .buyukbas-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .buyukbas-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .buyukbas-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .buyukbas-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
    </style>
    <div class="buyukbas-sonuc">
    """
    mesaj += f"<h3>BÜYÜKBAŞ {baslik_ek.upper()} TESİSİ DEĞERLENDİRME</h3>"
    mesaj += f"<p><b>Arazi Büyüklüğü:</b> {arazi_alani_m2 or sonuc.get('arazi_alani_m2', 0):,.2f} m²<br>"
    emsal_alani = (arazi_alani_m2 or 0) * (emsal_orani or 0.20)
    mesaj += f"<b>İzin Verilen Toplam Emsal Alanı (%{kullanilacak_emsal*100:.0f}):</b> {emsal_alani or sonuc.get('emsal_m2', 0):,.2f} m²</p>"

    if "TESİS YAPILAMAZ" in sonuc.get("sonuc_mesaji", ""):
        mesaj += f'<div class="hata"><b>SONUÇ: TESİS YAPILAMAZ</b><br>{sonuc.get("aciklama", "Belirtilmemiş")}</div>'
    else:
        # Ahır ve Yem Deposu Tablosu
        mesaj += '<div class="baslik">AHIR VE YEM DEPOSU</div>'
        mesaj += '<table>'
        mesaj += '<tr><th>Yapı</th><th>Alan (m²)</th></tr>'
        mesaj += f'<tr class="ahir"><td>Ahır ve Yem Deposu</td><td>{sonuc.get("ahir_alani_m2", 0):,.2f}</td></tr>'
        mesaj += '</table>'

        # Zorunlu müştemilatlar tablosu
        zorunlu_mustemilatlar = [
            y for y in sonuc.get("yapilar", [])
            if y.get("tip") == "zorunlu_mustemilat"
        ]
        if zorunlu_mustemilatlar:
            mesaj += '<div class="baslik">ZORUNLU MÜŞTEMİLATLAR</div>'
            mesaj += '<table>'
            mesaj += '<tr><th>Müştemilat</th><th>Alan (m²)</th></tr>'
            for yapi in zorunlu_mustemilatlar:
                mesaj += f'<tr class="mustemilat"><td>{yapi["isim"]}</td><td>{yapi["taban_alani"]:.2f}</td></tr>'
            mesaj += '</table>'

        # Opsiyonel müştemilatlar tablosu
        opsiyonel_mustemilatlar = [
            y for y in sonuc.get("yapilar", [])
            if y.get("tip") == "opsiyonel_mustemilat"
        ]
        if opsiyonel_mustemilatlar:
            mesaj += '<div class="baslik">OPSİYONEL MÜŞTEMİLATLAR</div>'
            mesaj += '<table>'
            mesaj += '<tr><th>Müştemilat</th><th>Alan (m²)</th></tr>'
            for yapi in opsiyonel_mustemilatlar:
                mesaj += f'<tr class="opsiyonel"><td>{yapi["isim"]}</td><td>{yapi["taban_alani"]:.2f}</td></tr>'
            mesaj += '</table>'

        # Bakıcı evi tablosu (3 sütun)
        bakici_evi_yapildi = [
            y for y in sonuc.get("yapilar", [])
            if y.get("tip") == "bakici_evi"
        ]
        mesaj += '<div class="baslik">BAKICI EVİ</div>'
        mesaj += '<table>'
        mesaj += '<tr><th>Hak Durumu</th><th>Taban Alanı (m²)</th><th>Toplam Alan (m²)</th></tr>'
        if bakici_evi_yapildi:
            for yapi in bakici_evi_yapildi:
                mesaj += (
                    f'<tr class="bakici"><td>Yapılabilir</td>'
                    f'<td>{yapi["taban_alani"]:.2f}</td>'
                    f'<td>{yapi["toplam_alan"]:.2f}</td></tr>'
                )
        else:
            mesaj += (
                f'<tr class="bakici"><td>Yapılamaz</td>'
                f'<td>0.00</td>'
                f'<td>0.00</td></tr>'
            )
        mesaj += '</table>'

        # Hayvan kapasitesi
        mesaj += f'<div class="baslik">HAYVAN KAPASİTESİ</div>'
        mesaj += f'<div><b>Hayvan Kapasitesi:</b> {sonuc.get("hayvan_kapasitesi", 0)} Baş {sonuc.get("hayvan_tipi","").replace("_"," ").upper()}</div>'

        # Gezinti alanı (süt sığırı ise)
        if sonuc.get('hayvan_tipi') == 'süt_sığırı':
            mesaj += f'<div class="baslik">AÇIK GEZİNTİ ALANI</div>'
            mesaj += f'<div><b>Gerekli Açık Gezinti Alanı (Emsal Dışı):</b> {sonuc.get("gezinti_alani_m2_gerekli", 0):,.2f} m²</div>'
            if "uyari_gezinti_alani" in sonuc:
                mesaj += f'<div class="uyari"><i>{sonuc["uyari_gezinti_alani"]}</i></div>'

        # Genel özet tablosu
        mesaj += '<div class="baslik">GENEL ÖZET</div>'
        mesaj += '<table>'
        mesaj += '<tr><th>Alan Türü</th><th>Değer (m²)</th></tr>'
        mesaj += f'<tr class="ozet"><td>Arazi Alanı</td><td>{sonuc.get("arazi_alani_m2", 0):,.2f}</td></tr>'
        mesaj += f'<tr class="ozet"><td>Emsal Alanı</td><td>{sonuc.get("emsal_m2", 0):,.2f}</td></tr>'
        toplam_kullanilan_emsal = (
            sonuc.get('ahir_alani_m2', 0)
            + sum(y['taban_alani'] for y in zorunlu_mustemilatlar)
            + sum(y['taban_alani'] for y in opsiyonel_mustemilatlar)
            + sum(y['taban_alani'] for y in bakici_evi_yapildi)
        )
        mesaj += f'<tr class="ozet"><td>Kullanılan Alan</td><td>{toplam_kullanilan_emsal:,.2f}</td></tr>'
        mesaj += f'<tr class="ozet"><td>Kalan Emsal</td><td>{sonuc.get("kalan_emsal_m2", 0):,.2f}</td></tr>'
        mesaj += '</table>'

        # Sonuç mesajı
        mesaj += f'<div class="basarili"><b>SONUÇ: {sonuc.get("sonuc_mesaji","")}</b></div>'
        
        if sonuc.get("aciklama") and "Detaylı değerlendirme" not in sonuc.get("aciklama"):
             mesaj += f'<div class="notlar"><b>Açıklama:</b> {sonuc.get("aciklama")}</div>'

    # Not bölümü
    mesaj += '<div class="notlar">'
    mesaj += "<b>NOT:</b> Tüm hesaplamalar güncel mevzuat ve yönetmeliklere göre yapılmıştır. "
    mesaj += "Süt sığırları için belirtilen açık gezinti alanı emsale dahil değildir, ancak parsel içerisinde karşılanmalıdır. "
    mesaj += "Bu değerlendirme ön bilgilendirme amaçlıdır ve resmi bir belge niteliği taşımaz."
    mesaj += '</div></div>'
    return mesaj
def sut_sigiri_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None, buyuk_ova_alaninda_mi: bool = False) -> dict:
    """Süt sığırcılığı tesisi için değerlendirme yapar"""
    # Arazi büyüklüğü kontrolü ve negatif değer koruması
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

    su_tahsis_belgesi_var_mi = str(arazi_bilgileri.get("su_tahsis_belgesi","false")).lower() == "true"
    yas_kapali_alanda_mi = arazi_bilgileri.get("yas_kapali_alan_durumu") == "içinde"

    if yas_kapali_alanda_mi and not su_tahsis_belgesi_var_mi:
        # GEÇICI ÇÖZÜM: Su tahsis belgesi uyarısını göster ama hesaplamaya devam et
        yas_uyari_mesaji = (
            "<div style='background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 15px 0;'>"
            "<h4 style='color: #856404; margin-top: 0;'>⚠️ Su Tahsis Belgesi Gerekli</h4>"
            "<p style='margin-bottom: 10px;'><strong>Uyarı:</strong> Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır.</p>"
            "<p style='margin-bottom: 10px;'>Bu tür arazilerde büyükbaş hayvancılık tesisi yapımı için <strong>su tahsis belgesi zorunludur.</strong></p>"
            "<p style='margin-bottom: 10px; color: #721c24;'><strong>Çözüm:</strong> Yukarıdaki formdaki 'Su tahsis belgem mevcut' seçeneğini işaretleyerek hesaplama yapabilirsiniz.</p>"
            "<p style='margin-bottom: 0; font-size: 14px; color: #6c757d;'><em>Not: Su tahsis belgesi olmadan bu alanda tesis kurulamaz. Lütfen önce ilgili kurumlardan belgenizi temin ediniz.</em></p>"
            "</div>"
        )
        # Uyarıyı sakla ama hesaplamaya devam et (frontend problemi çözülünceye kadar geçici)
        yas_uyari_mesaji_temp = yas_uyari_mesaji
    else:
        yas_uyari_mesaji_temp = ""

    hesaplayici = BuyukbasHesaplama(emsal_orani)
    hesap_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2, "süt_sığırı", buyuk_ova_alaninda_mi)
    
    html_mesaj = _olustur_html_mesaj_buyukbas(hesap_sonucu, "SÜT SIĞIRCILIĞI", emsal_orani, arazi_buyuklugu_m2)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in hesap_sonucu["sonuc_mesaji"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "ana_mesaj": html_mesaj,  # decision_logic.py'de kullanım için eklendi
        "kapasite": hesap_sonucu.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": hesap_sonucu.get("bakici_evi_hakki", False),
        # Frontend için arazi bilgilerini ekle
        "arazi_alani_m2": arazi_buyuklugu_m2,
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "buyukluk_m2": arazi_buyuklugu_m2,
        "toplam_emsal_m2": hesap_sonucu.get("toplam_emsal_m2", arazi_buyuklugu_m2 * (emsal_orani or 0.20)),
        "kalan_emsal_m2": hesap_sonucu.get("kalan_emsal_m2", 0),
    }

def besi_sigiri_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None, buyuk_ova_alaninda_mi: bool = False) -> dict:
    """Besi sığırcılığı tesisi için değerlendirme yapar"""
    # Arazi büyüklüğü kontrolü ve negatif değer koruması
    try:
        arazi_buyuklugu_m2 = float(arazi_bilgileri.get("buyukluk_m2", 0))
        if arazi_buyuklugu_m2 <= 0:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": "<b>Geçersiz Arazi Büyüklüğü</b><br><br>"
                         "Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.",
                "kapasite": 0,
                "bakici_evi_hakki": False,
            }
    except (ValueError, TypeError):
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Geçersiz Arazi Büyüklüğü</b><br><br>"
                     "Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.",
            "kapasite": 0,
            "bakici_evi_hakki": False,
        }

    # Su tahsis ve YAS kontrolü
    su_tahsis_belgesi_var_mi = str(arazi_bilgileri.get("su_tahsis_belgesi","false")).lower() == "true"
    yas_kapali_alanda_mi = arazi_bilgileri.get("yas_kapali_alan_durumu") == "içinde"

    if yas_kapali_alanda_mi and not su_tahsis_belgesi_var_mi:
        # GEÇICI ÇÖZÜM: Su tahsis belgesi uyarısını göster ama hesaplamaya devam et  
        yas_uyari_mesaji = (
            "<b>Yeraltı Suyu Koruma Alanında Su Tahsis Belgesi Zorunluluğu</b><br><br>"
            "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
            "Bu tür arazilerde büyükbaş hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
            "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda büyükbaş hayvancılık tesisi yapımına izin verilememektedir."
        )
        # Uyarıyı sakla ama hesaplamaya devam et (frontend problemi çözülünceye kadar geçici)
        yas_uyari_mesaji_temp = yas_uyari_mesaji
    else:
        yas_uyari_mesaji_temp = ""

    # Hesaplamayı yap
    hesaplayici = BuyukbasHesaplama(emsal_orani)
    hesap_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2, "besi_sığırı", buyuk_ova_alaninda_mi)
    html_mesaj = _olustur_html_mesaj_buyukbas(hesap_sonucu, "BESİ SIĞIRCILIĞI", emsal_orani, arazi_buyuklugu_m2)

    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in hesap_sonucu["sonuc_mesaji"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "ana_mesaj": html_mesaj,
        "kapasite": hesap_sonucu.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": hesap_sonucu.get("bakici_evi_hakki", False),
        # Frontend için arazi bilgilerini ekle
        "arazi_alani_m2": arazi_buyuklugu_m2,
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "buyukluk_m2": arazi_buyuklugu_m2,
        "toplam_emsal_m2": hesap_sonucu.get("toplam_emsal_m2", arazi_buyuklugu_m2 * (emsal_orani or 0.20)),
        "kalan_emsal_m2": hesap_sonucu.get("kalan_emsal_m2", 0),
    }

# Evet, "TESİS YAPILAMAZ" sonucu buyukbas.py dosyasındaki hesapla fonksiyonunda aşağıdaki durumlarda üretiliyor:
# 1. Emsal alanı minimum zorunlu müştemilat alanından azsa:
#    if emsal < self.min_zorunlu_mustemilat_alani:
#        return {"sonuc_mesaji": "TESİS YAPILAMAZ", ...}
# 2. Emsal yeterli ama ahır için alan kalmıyorsa:
#    if emsal < self.min_zorunlu_mustemilat_alani + self.min_islevsel_ahir_alani:
#        return {"sonuc_mesaji": "TESİS YAPILAMAZ", ...}
# 3. İterasyon sonunda uygun kapasite bulunamazsa:
#    if final_hayvan_kapasitesi == 0 and ahir_alani_final == 0:
#        return {"sonuc_mesaji": "TESİS YAPILAMAZ", ...}
# Bu "sonuc_mesaji" değeri, üstteki fonksiyonlarda "izin_durumu" değerinin "izin_verilemez" olarak set edilmesine sebep olur.
