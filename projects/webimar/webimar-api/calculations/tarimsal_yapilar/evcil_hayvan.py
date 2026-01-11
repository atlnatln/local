"""
Evcil Hayvan ve Bilimsel Araştırma Hayvanı Üretim Tesisi Hesaplama Modülü
"""
import math

# Emsal ve Alan Sabit Değerleri
EMSAL_ORANI = 0.20  # %20

# Zorunlu müştemilat sınırlamaları
IDARI_BINA_TABAN_ALANI = 150  # m²
IDARI_BINA_INSAAT_ALANI = 300  # m² (2 katlı)
BAKICI_EVI_TABAN_ALANI = 75  # m²
BAKICI_EVI_INSAAT_ALANI = 75  # m² (tek katlı)

# Bakıcı evi hakkı için gereken hayvan sayısı
BAKICI_EVI_ESIGI = {
    "kedi": 50,
    "kopek": 30,
    "kus": 300,
    "kemirgen": 500,
    "karma": 100  # Karma tesisler için
}

# Köksel büyüme limitler sistemi - büyük tesislerde alan hesaplamalarının mantıklı sınırlarda kalması için
EVCIL_HAYVAN_KOKSEL_LIMITLER = {
    "yem_deposu": {
        "max_limit": 50,  # m²
        "buyume_faktoru": 0.8,
        "min_esik": 100  # hayvan sayısı
    },
    "atik_malzeme_deposu": {
        "max_limit": 40,  # m²
        "buyume_faktoru": 0.7,
        "min_esik": 100
    },
    "acik_gezinti_alani": {
        "max_limit": 500,  # m²
        "buyume_faktoru": 0.6,
        "min_esik": 50  # köpek sayısı
    },
    "veteriner_odasi": {
        "max_limit": 25,  # m²
        "buyume_faktoru": 0.5,
        "min_esik": 200
    },
    "ameliyathane": {
        "max_limit": 20,  # m²
        "buyume_faktoru": 0.4,
        "min_esik": 300
    },
    "revir": {
        "max_limit": 30,  # m²
        "buyume_faktoru": 0.6,
        "min_esik": 150
    },
    "karantina_odasi": {
        "max_limit": 25,  # m²
        "buyume_faktoru": 0.5,
        "min_esik": 200
    },
    "dezenfeksiyon_odasi": {
        "max_limit": 12,  # m²
        "buyume_faktoru": 0.3,
        "min_esik": 500
    },
    "personel_dinlenme_odasi": {
        "max_limit": 20,  # m²
        "buyume_faktoru": 0.4,
        "min_esik": 300
    },
    "toplanti_odasi": {
        "max_limit": 25,  # m²
        "buyume_faktoru": 0.4,
        "min_esik": 300
    },
    "wc_dus": {
        "max_limit": 15,  # m²
        "buyume_faktoru": 0.3,
        "min_esik": 500
    },
    "ofis": {
        "max_limit": 25,  # m²
        "buyume_faktoru": 0.4,
        "min_esik": 300
    }
}

# Hayvan türleri ve alan ihtiyaçları
HAYVAN_TURLERI = {
    "kedi": {"ad": "Kedi", "kapali_alan": 1.5, "acik_alan": 2.0, "genc_kapali_alan": 0.8},
    "kopek_kucuk": {"ad": "Küçük Irk Köpek", "kapali_alan": 3.0, "acik_alan": 6.0, "genc_kapali_alan": 1.5},
    "kopek_orta": {"ad": "Orta Irk Köpek", "kapali_alan": 4.0, "acik_alan": 8.0, "genc_kapali_alan": 2.0},
    "kopek_buyuk": {"ad": "Büyük Irk Köpek", "kapali_alan": 5.0, "acik_alan": 10.0, "genc_kapali_alan": 2.5},
    "kus": {"ad": "Kuş", "kapali_alan": 0.2, "acik_alan": 0, "genc_kapali_alan": 0.1},
    "kemirgen": {"ad": "Kemirgen", "kapali_alan": 0.15, "acik_alan": 0, "genc_kapali_alan": 0.07},
    "fare": {"ad": "Fare", "kapali_alan": 0.05, "acik_alan": 0, "genc_kapali_alan": 0.02},
    "sican": {"ad": "Sıçan", "kapali_alan": 0.1, "acik_alan": 0, "genc_kapali_alan": 0.05},
    "kobay": {"ad": "Kobay", "kapali_alan": 0.2, "acik_alan": 0, "genc_kapali_alan": 0.1},
    "tavsan": {"ad": "Tavşan", "kapali_alan": 0.4, "acik_alan": 0, "genc_kapali_alan": 0.2},
    "surungen": {"ad": "Sürüngen", "kapali_alan": 0.5, "acik_alan": 0, "genc_kapali_alan": 0.25},
    "amfibi": {"ad": "Amfibi", "kapali_alan": 0.2, "acik_alan": 0, "genc_kapali_alan": 0.1},
    "balik": {"ad": "Balık", "kapali_alan": 0.01, "acik_alan": 0, "genc_kapali_alan": 0.005}
}

# Müştemilat tanımları ve zorunluluk durumları
MUSTEMILAT_TANIMLARI = {
    # İdari Bina ve İçindeki Birimler (Zorunlu)
    "idari_bina": {
        "isim": "İdari Bina", "grup": "zorunlu", "oncelik": 1,
        "min_alan_m2": 150, "max_alan_m2": 150, "toplam_insaat_alani_m2": 300,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Veteriner odası, personel dinlenme odası, toplantı odası, ofis vb. alanları içerir"
    },
    "veteriner_odasi": {
        "isim": "Veteriner Odası", "grup": "zorunlu", "oncelik": 2,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.05, "max_alan_m2": 25,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Hayvanların sağlık kontrolü ve tedavi işlemleri için",
        "idari_bina_icinde": True
    },
    "ameliyathane": {
        "isim": "Ameliyathane", "grup": "zorunlu", "oncelik": 3,
        "min_alan_m2": 12, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 20,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Cerrahi müdahale gerektiren durumlar için",
        "idari_bina_icinde": True
    },
    "revir": {
        "isim": "Revir", "grup": "zorunlu", "oncelik": 4,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.08, "max_alan_m2": 30,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Hasta hayvanların tedavi ve gözlemi için",
        "idari_bina_icinde": True
    },
    "karantina_odasi": {
        "isim": "Karantina Odası", "grup": "zorunlu", "oncelik": 5,
        "min_alan_m2": 10, "artis_hayvan_basi_m2": 0.06, "max_alan_m2": 25,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Yeni gelen veya hastalık şüphesi olan hayvanların izolasyonu için",
        "idari_bina_icinde": True
    },
    "dezenfeksiyon_odasi": {
        "isim": "Dezenfeksiyon Odası", "grup": "zorunlu", "oncelik": 6,
        "min_alan_m2": 8, "artis_hayvan_basi_m2": 0.01, "max_alan_m2": 12,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Hijyen kontrolü ve dezenfeksiyon işlemleri için",
        "idari_bina_icinde": True
    },
    "personel_dinlenme_odasi": {
        "isim": "Personel Dinlenme Odası", "grup": "zorunlu", "oncelik": 7,
        "min_alan_m2": 12, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 20,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Personel için dinlenme ve sosyal alan",
        "idari_bina_icinde": True
    },
    "toplanti_odasi": {
        "isim": "Toplantı Odası", "grup": "zorunlu", "oncelik": 8,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 25,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Eğitim ve toplantılar için alan",
        "idari_bina_icinde": True
    },
    "wc_dus": {
        "isim": "WC ve Duş", "grup": "zorunlu", "oncelik": 9,
        "min_alan_m2": 10, "artis_hayvan_basi_m2": 0.01, "max_alan_m2": 15,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Personel hijyen alanları",
        "idari_bina_icinde": True
    },
    "ofis": {
        "isim": "Ofis", "grup": "zorunlu", "oncelik": 10,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.02, "max_alan_m2": 25,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "İdari işler için ofis alanı",
        "idari_bina_icinde": True
    },
    
    # Diğer Zorunlu Müştemilatlar (İdari Bina Dışında)
    "yem_deposu": {
        "isim": "Yem Deposu", "grup": "zorunlu", "oncelik": 20,
        "min_alan_m2": 20, "artis_hayvan_basi_m2": 0.05, "max_alan_m2": 50,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Hayvan yemleri için depolama alanı"
    },
    "atik_malzeme_deposu": {
        "isim": "Atık ve Malzeme Deposu", "grup": "zorunlu", "oncelik": 21,
        "min_alan_m2": 15, "artis_hayvan_basi_m2": 0.04, "max_alan_m2": 40,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Atık ve malzemelerin depolanması için"
    },
    
    # Gezinti Alanları (Sadece Köpek için Zorunlu)
    "acik_gezinti_alani": {
        "isim": "Açık Gezinti Alanı", "grup": "zorunlu", "oncelik": 31,
        "min_alan_m2": 50, "artis_hayvan_basi_m2": 3.0, "max_alan_m2": 500,
        "hayvan_tipi_gecerli": ["kopek_kucuk", "kopek_orta", "kopek_buyuk"],
        "aciklama": "Köpeklerin dış mekanda hareket edebilecekleri alan",
        "emsal_disi": True  # Açık alan emsale dahil edilmez
    },
    
    # Bakıcı Evi (Koşullu)
    "bakici_evi": {
        "isim": "Bakıcı Evi", "grup": "bakici", "oncelik": 40,
        "sabit_alan_m2": 75, "toplam_insaat_alan_m2": 75,
        "hayvan_tipi_gecerli": ["hepsi"],
        "aciklama": "Bakıcı personel için konaklama alanı"
    }
}

# Minimum Gereken Arazi Büyüklüğü (m²)
MIN_ARAZI_BUYUKLUGU = 500

class EvcilHayvanTesisiHesaplayici:
    """Evcil hayvan ve bilimsel araştırma hayvanı tesisi hesaplamaları için ana sınıf"""
    def __init__(self, emsal_orani: float = None):
        self.emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
        self.idari_bina_taban = IDARI_BINA_TABAN_ALANI
        self.idari_bina_insaat = IDARI_BINA_INSAAT_ALANI
        self.bakici_evi_taban = BAKICI_EVI_TABAN_ALANI
        self.bakici_evi_insaat = BAKICI_EVI_INSAAT_ALANI
        self.hayvan_turleri = HAYVAN_TURLERI
        self.bakici_evi_esigi = BAKICI_EVI_ESIGI
        self.mustemilat_tanimlari = MUSTEMILAT_TANIMLARI

    def _hesapla_mustemilat_alani(self, must_tanimi: dict, hayvan_kapasitesi: int) -> float:
        """
        Belirli bir müştemilat için hayvan kapasitesine göre alan hesaplar.
        Büyük tesisler için köksel büyüme sistemi kullanarak mantıklı alan hesaplar.
        
        Args:
            must_tanimi: Müştemilat tanımı sözlüğü
            hayvan_kapasitesi: Planlanan toplam hayvan kapasitesi
            
        Returns:
            float: Hesaplanan müştemilat alanı (m²)
        """
        # Müştemilat kodu
        kod = next((k for k, v in self.mustemilat_tanimlari.items() if v == must_tanimi), None)

        # Sabit alan varsa doğrudan onu döndür
        if "sabit_alan_m2" in must_tanimi:
            return must_tanimi["sabit_alan_m2"]
        
        # Minimum alan ile başla
        alan = must_tanimi.get("min_alan_m2", 0)
        artis_hayvan_basi = must_tanimi.get("artis_hayvan_basi_m2", 0)
        
        # Köksel büyüme sistemi kontrolü
        if kod and kod in EVCIL_HAYVAN_KOKSEL_LIMITLER:
            koksel_limit = EVCIL_HAYVAN_KOKSEL_LIMITLER[kod]
            max_limit = koksel_limit["max_limit"]
            buyume_faktoru = koksel_limit["buyume_faktoru"]
            min_esik = koksel_limit["min_esik"]
            
            if hayvan_kapasitesi > min_esik:
                # Köksel büyüme formülü: 
                # alan = min_alan + (sqrt(hayvan_kapasitesi - min_esik) * buyume_faktoru * artis_hayvan_basi * esik_katsayisi)
                esik_katsayisi = min_esik * 0.3  # Eşik değerinin %30'u kadar doğrusal artış
                koksel_buyume = math.sqrt(hayvan_kapasitesi - min_esik) * buyume_faktoru * artis_hayvan_basi * esik_katsayisi
                alan += koksel_buyume
                
                # Maksimum limit kontrolü
                alan = min(alan, max_limit)
            else:
                # Eşik değerin altında doğrusal artış
                alan += artis_hayvan_basi * hayvan_kapasitesi
        else:
            # Köksel limit tanımlı değilse eski logaritmik sistem
            olcekleme_faktoru = 1.0
            if hayvan_kapasitesi > 1000:
                olcekleme_faktoru = 0.3 + (0.2 * (math.log10(1000) / math.log10(hayvan_kapasitesi)))
            elif hayvan_kapasitesi > 500:
                olcekleme_faktoru = 0.5 + (0.3 * (math.log10(500) / math.log10(hayvan_kapasitesi)))
            elif hayvan_kapasitesi > 100:
                olcekleme_faktoru = 0.7 + (0.2 * (math.log10(100) / math.log10(hayvan_kapasitesi)))
            
            # İdari bina içindeki alanlar için özel ölçekleme
            if must_tanimi.get("idari_bina_icinde", False):
                olcekleme_faktoru *= 0.8
            
            alan += artis_hayvan_basi * hayvan_kapasitesi * olcekleme_faktoru
        
        # Genel maksimum alan kontrolü (müştemilat tanımından)
        if "max_alan_m2" in must_tanimi:
            alan = min(alan, must_tanimi["max_alan_m2"])
        
        return round(alan, 2)

    def hesapla_mustemilat_alanlari(self, hayvan_kapasitesi: int, hayvan_turleri_listesi=None) -> dict:
        """
        Hayvan kapasitesine göre tüm müştemilat alanlarını hesaplar
        
        Args:
            hayvan_kapasitesi: Planlanan toplam hayvan kapasitesi
            hayvan_turleri_listesi: Hayvan türlerine göre filtrelemek için liste
            
        Returns:
            dict: Hesaplanan müştemilat alanları
        """
        mustemilat_alanlari = {}
        idari_bina_ici_toplam_alan = 0
        
        # Eğer hayvan türleri listesi belirtilmemişse, tüm türler için hesapla
        if not hayvan_turleri_listesi:
            hayvan_tipleri = ["hepsi"]
        else:
            hayvan_tipleri = hayvan_turleri_listesi + ["hepsi"]
        
        # Önce idari bina içindeki alanları hesapla
        for kod, tanim in self.mustemilat_tanimlari.items():
            if tanim.get("idari_bina_icinde", False) and tanim["grup"] == "zorunlu":
                if any(tip in tanim["hayvan_tipi_gecerli"] for tip in hayvan_tipleri):
                    alan = self._hesapla_mustemilat_alani(tanim, hayvan_kapasitesi)
                    mustemilat_alanlari[kod] = {
                        "isim": tanim["isim"],
                        "alan_m2": alan,
                        "aciklama": tanim.get("aciklama", ""),
                        "grup": tanim["grup"],
                        "idari_bina_icinde": True
                    }
                    idari_bina_ici_toplam_alan += alan
        
        # İdari bina kapasitesini kontrol et ve ayarla
        idari_bina_max = self.mustemilat_tanimlari["idari_bina"]["min_alan_m2"]
        if idari_bina_ici_toplam_alan > idari_bina_max:
            # İdari bina içindeki alanları oranla küçült
            oran = idari_bina_max / idari_bina_ici_toplam_alan
            for kod, detay in mustemilat_alanlari.items():
                if detay.get("idari_bina_icinde", False):
                    detay["alan_m2"] *= oran
                    detay["alan_m2"] = round(detay["alan_m2"], 2)
            idari_bina_ici_toplam_alan = idari_bina_max
        
        # İdari binayı ekle
        mustemilat_alanlari["idari_bina"] = {
            "isim": self.mustemilat_tanimlari["idari_bina"]["isim"],
            "alan_m2": self.mustemilat_tanimlari["idari_bina"]["min_alan_m2"],
            "toplam_insaat_alani_m2": self.mustemilat_tanimlari["idari_bina"]["toplam_insaat_alani_m2"],
            "aciklama": self.mustemilat_tanimlari["idari_bina"]["aciklama"],
            "grup": self.mustemilat_tanimlari["idari_bina"]["grup"],
            "icerik": [detay for kod, detay in mustemilat_alanlari.items() if detay.get("idari_bina_icinde", False)]
        }
        
        # İdari bina dışındaki zorunlu müştemilatları hesapla
        for kod, tanim in self.mustemilat_tanimlari.items():
            if not tanim.get("idari_bina_icinde", False) and tanim["grup"] == "zorunlu" and kod != "idari_bina":
                if any(tip in tanim["hayvan_tipi_gecerli"] for tip in hayvan_tipleri):
                    alan = self._hesapla_mustemilat_alani(tanim, hayvan_kapasitesi)
                    mustemilat_alanlari[kod] = {
                        "isim": tanim["isim"],
                        "alan_m2": alan,
                        "aciklama": tanim.get("aciklama", ""),
                        "grup": tanim["grup"],
                        "emsal_disi": tanim.get("emsal_disi", False)
                    }
        
        return mustemilat_alanlari

    def hesapla_minimum_arazi_buyuklugu(self, hayvan_kapasitesi: int, hayvan_turleri_listesi=None) -> float:
        """
        Belirli bir hayvan kapasitesi için gereken minimum arazi büyüklüğünü hesaplar
        
        Args:
            hayvan_kapasitesi: Planlanan hayvan kapasitesi
            hayvan_turleri_listesi: Hayvan türü kodları listesi (None ise varsayılan mix)
            
        Returns:
            float: Minimum arazi büyüklüğü (m²)
        """
        if hayvan_kapasitesi <= 0:
            return MIN_ARAZI_BUYUKLUGU
            
        # Varsayılan hayvan türü kombinasyonu (basit mix)
        if not hayvan_turleri_listesi:
            hayvan_turleri_listesi = ['kedi', 'kopek_kucuk', 'kus']
            
        # Hayvan türlerinin ortalama alan gereksinimlerini hesapla
        ortalama_kapali_alan = 0
        ortalama_acik_alan = 0
        
        for tur_kodu in hayvan_turleri_listesi:
            if tur_kodu in self.hayvan_turleri:
                tur = self.hayvan_turleri[tur_kodu]
                # %80 yetişkin, %20 genç varsayımı
                ortalama_kapali_alan += ((tur["kapali_alan"] * 0.8) + (tur["genc_kapali_alan"] * 0.2)) / len(hayvan_turleri_listesi)
                if tur["acik_alan"] > 0:
                    ortalama_acik_alan += ((tur["acik_alan"] * 0.8) + ((tur["acik_alan"] * 0.5) * 0.2)) / len(hayvan_turleri_listesi)
        
        # Müştemilat alanlarını hesapla
        toplam_mustemilat_alani = 0
        for _, must_tanimi in self.mustemilat_tanimlari.items():
            if must_tanimi["grup"] == "zorunlu":
                toplam_mustemilat_alani += self._hesapla_mustemilat_alani(must_tanimi, hayvan_kapasitesi)
        
        # Bakıcı evi için alan ayır (eşik kontrolü burada yapılmıyor, genel hesaplama için)
        toplam_mustemilat_alani += self.bakici_evi_taban
        
        # Hayvanlar için kapalı alan hesapla
        toplam_kapali_alan_hayvanlar = ortalama_kapali_alan * hayvan_kapasitesi
        
        # Toplam kapalı alan (hayvan + müştemilat)
        toplam_kapali_alan = toplam_kapali_alan_hayvanlar + toplam_mustemilat_alani
        
        # Açık alan hesabı
        toplam_acik_alan = ortalama_acik_alan * hayvan_kapasitesi
        
        # Gerekli arazi büyüklüğü: Emsal formülü + açık alan gereksinimleri
        gerekli_arazi_buyuklugu = max(
            toplam_kapali_alan / self.emsal_orani,  # Emsal formülü
            toplam_kapali_alan + toplam_acik_alan,  # Kapalı + Açık alan
            MIN_ARAZI_BUYUKLUGU  # Mutlak minimum
        )
        
        return round(gerekli_arazi_buyuklugu, 2)

    def hesapla_alan_gereksinimi(self, hayvanlar, ek_alanlar=None):
        """
        Hayvanların tür ve sayısına göre alan gereksinimini hesaplar
        
        Args:
            hayvanlar: Dict, key=hayvan türü, value=Dict{yetiskin: sayı, genc: sayı}
            ek_alanlar: Dict, asıl üretim yapısına eklenecek alanlar (m²)
            
        Returns:
            Dict, hesaplanan alan gereksinimleri
        """
        if ek_alanlar is None:
            ek_alanlar = {}
        
        # Asıl üretim yapısı hesaplamaları
        asil_uretim_alani = 0
        acik_alan = 0
        hayvan_sayilari = {}
        toplam_hayvan = 0
        
        for tur_kodu, sayilar in hayvanlar.items():
            if tur_kodu in self.hayvan_turleri:
                tur = self.hayvan_turleri[tur_kodu]
                yetiskin = sayilar.get("yetiskin", 0)
                genc = sayilar.get("genc", 0)
                
                kapali_alan = yetiskin * tur["kapali_alan"] + genc * tur["genc_kapali_alan"]
                asil_uretim_alani += kapali_alan
                
                # Açık alan sadece gerekli türler için hesaplanır
                acik_alan_turun = 0
                if tur["acik_alan"] > 0:
                    acik_alan_turun = yetiskin * tur["acik_alan"] + genc * (tur["acik_alan"] * 0.5)
                acik_alan += acik_alan_turun
                
                hayvan_sayilari[tur["ad"]] = {
                    "yetiskin": yetiskin, 
                    "genc": genc, 
                    "kapali_alan": kapali_alan,
                    "acik_alan": acik_alan_turun
                }
                
                toplam_hayvan += yetiskin + genc
        
        # Ek alanları ekle
        for alan_adi, alan_m2 in ek_alanlar.items():
            asil_uretim_alani += alan_m2
        
        # Bakıcı evi ihtiyacı belirle
        # Karma tesis için en düşük eşik değeri kontrol et
        bakici_evi_hakki = False
        karma_tesis = len(hayvanlar) > 1
        
        if karma_tesis and toplam_hayvan >= self.bakici_evi_esigi["karma"]:
            bakici_evi_hakki = True
        else:
            # Tek tür için kontrol
            for tur_kodu, sayilar in hayvanlar.items():
                if tur_kodu in self.hayvan_turleri:
                    ana_kategori = tur_kodu.split('_')[0]  # örn: kopek_orta -> kopek
                    if ana_kategori in self.bakici_evi_esigi:
                        esik_degeri = self.bakici_evi_esigi[ana_kategori]
                        yetiskin = sayilar.get("yetiskin", 0)
                        genc = sayilar.get("genc", 0)
                        if yetiskin + genc >= esik_degeri:
                            bakici_evi_hakki = True
                            break
        
        # Zorunlu müştemilat alanları
        zorunlu_mustemilat = {
            "idari_bina": self.idari_bina_taban,
            "yem_deposu": max(25, asil_uretim_alani * 0.1),  # En az 25 m² veya asıl üretim alanının %10'u
            "atik_malzeme_deposu": max(25, asil_uretim_alani * 0.08)  # En az 25 m² veya asıl üretim alanının %8'i
        }
        
        # Bakıcı evi ekle
        if bakici_evi_hakki:
            zorunlu_mustemilat["bakici_evi"] = self.bakici_evi_taban
        
        # Toplam alanlar
        toplam_zorunlu_mustemilat = sum(zorunlu_mustemilat.values())
        toplam_kapali_alan = asil_uretim_alani + toplam_zorunlu_mustemilat
        
        return {
            "asil_uretim_alani": asil_uretim_alani,
            "zorunlu_mustemilat": zorunlu_mustemilat,
            "toplam_zorunlu_mustemilat": toplam_zorunlu_mustemilat,
            "toplam_kapali_alan": toplam_kapali_alan,
            "acik_alan": acik_alan,
            "hayvan_sayilari": hayvan_sayilari,
            "toplam_hayvan": toplam_hayvan,
            "bakici_evi_hakki": bakici_evi_hakki
        }
    
    def arazi_degerlendirme(self, arazi_alani, gereksinim):
        """
        Arazi alanının gereksinimleri karşılayıp karşılamadığını değerlendirir
        
        Args:
            arazi_alani: Arazi büyüklüğü (m²)
            gereksinim: hesapla_alan_gereksinimi fonksiyonundan dönen Dict
            
        Returns:
            Dict, değerlendirme sonuçları
        """
        emsal = arazi_alani * self.emsal_orani
        toplam_kapali_alan = gereksinim["toplam_kapali_alan"]
        acik_alan = gereksinim["acik_alan"]
        
        # Emsal yeterli mi?
        emsal_yeterli = emsal >= toplam_kapali_alan
        
        # Açık alan kontrolü (Açık alanın arazi alanının %50'sinden az olması ideal)
        acik_alan_orani = acik_alan / arazi_alani if arazi_alani > 0 else 1
        acik_alan_uygun = acik_alan_orani <= 0.5
        
        # Kalan emsal hesaplaması
        kalan_emsal = max(0, emsal - toplam_kapali_alan)
        
        sonuc = {
            "arazi_alani": arazi_alani,
            "emsal": emsal,
            "toplam_kapali_alan": toplam_kapali_alan,
            "acik_alan": acik_alan,
            "acik_alan_orani": acik_alan_orani,
            "emsal_yeterli": emsal_yeterli,
            "acik_alan_uygun": acik_alan_uygun,
            "kalan_emsal": kalan_emsal,
            "bakici_evi_hakki": gereksinim.get("bakici_evi_hakki", False),
            "bakici_evi_yapildi": gereksinim.get("bakici_evi_hakki", False) and emsal_yeterli
        }
        
        # Sonuç değerlendirmesi
        if emsal_yeterli and acik_alan_uygun:
            sonuc["sonuc"] = "TESİS YAPILABİLİR"
            sonuc["aciklama"] = f"{gereksinim['toplam_hayvan']} kapasiteli tesis kurulabilir. " \
                               f"Emsal alanının {kalan_emsal:.2f} m²'si kullanılmadan kalmıştır."
        elif not emsal_yeterli:
            sonuc["sonuc"] = "TESİS YAPILAMAZ"
            sonuc["aciklama"] = f"Emsale göre izin verilen {emsal:.2f} m² yapılaşma alanı, " \
                               f"gerekli olan {toplam_kapali_alan:.2f} m²'den azdır."
        elif not acik_alan_uygun:
            sonuc["sonuc"] = "TESİS PLANLAMASI UYGUNSUZ"
            sonuc["aciklama"] = f"Açık alan ihtiyacı ({acik_alan:.2f} m²) arazi alanının %{acik_alan_orani*100:.1f}'ini " \
                               f"kaplamaktadır. Bu oran %50'den az olmalıdır."
        
        return sonuc
        
    def hesapla(self, arazi_alani_m2, tesis_turu, hayvanlar, ek_alanlar=None, ekstra_acik_alanlar=None):
        """
        Ana hesaplama fonksiyonu
        
        Args:
            arazi_alani_m2: Arazi büyüklüğü (m²)
            tesis_turu: Tesis türü (string)
            hayvanlar: Dict, key=hayvan türü, value=Dict{yetiskin: sayı, genc: sayı}
            ek_alanlar: Dict, asıl üretim yapısına eklenecek alanlar (m²)
            ekstra_acik_alanlar: Dict, standart hesaplamalara ek açık alanlar (m²)
            
        Returns:
            Dict, hesaplama sonuçları
        """
        if ek_alanlar is None:
            ek_alanlar = {}
        if ekstra_acik_alanlar is None:
            ekstra_acik_alanlar = {}
            
        # Alan gereksinimlerini hesapla
        gereksinim = self.hesapla_alan_gereksinimi(hayvanlar, ek_alanlar)
        
        # Ekstra açık alanları ekle
        toplam_ekstra_acik_alan = sum(ekstra_acik_alanlar.values())
        gereksinim["acik_alan"] += toplam_ekstra_acik_alan
        
        # Arazi değerlendirmesi
        sonuc = self.arazi_degerlendirme(arazi_alani_m2, gereksinim)
        
        # Tüm hayvan türleri ve sayılarını özetle
        hayvan_ozeti = []
        for tur_kodu, sayilar in hayvanlar.items():
            if tur_kodu in self.hayvan_turleri:
                tur = self.hayvan_turleri[tur_kodu]
                yetiskin = sayilar.get("yetiskin", 0)
                genc = sayilar.get("genc", 0)
                toplam = yetiskin + genc
                
                if toplam > 0:
                    hayvan_ozeti.append({
                        "tur": tur["ad"], 
                        "yetiskin": yetiskin, 
                        "genc": genc,
                        "toplam": toplam
                    })
        
        # Yapılar listesini oluştur
        yapilar = []
        
        # Asıl üretim yapısı ekle
        yapilar.append({
            "isim": "Asıl Üretim Yapısı", 
            "taban_alani": gereksinim["asil_uretim_alani"],
            "toplam_alan": gereksinim["asil_uretim_alani"],
            "tip": "asil_uretim"
        })
        
        # Zorunlu müştemilatları ekle
        for mustemilat_ad, alan in gereksinim["zorunlu_mustemilat"].items():
            if mustemilat_ad == "idari_bina":
                yapilar.append({
                    "isim": "İdari Bina", 
                    "taban_alani": alan,
                    "toplam_alan": self.idari_bina_insaat,
                    "tip": "zorunlu_mustemilat"
                })
            elif mustemilat_ad == "bakici_evi":
                yapilar.append({
                    "isim": "Bakıcı Evi", 
                    "taban_alani": alan,
                    "toplam_alan": self.bakici_evi_insaat,
                    "tip": "bakici_evi" 
                })
            else:
                yapilar.append({
                    "isim": mustemilat_ad.replace("_", " ").title(), 
                    "taban_alani": alan,
                    "toplam_alan": alan,
                    "tip": "zorunlu_mustemilat"
                })
        
        # Sonuç sözlüğü
        hesaplama_sonucu = {
            "arazi_alani_m2": arazi_alani_m2,
            "emsal_m2": sonuc["emsal"],
            "tesis_turu": tesis_turu,
            "hayvan_kapasitesi": gereksinim["toplam_hayvan"],
            "hayvan_ozeti": hayvan_ozeti,
            "asil_uretim_alani_m2": gereksinim["asil_uretim_alani"],
            "toplam_zorunlu_mustemilat_m2": gereksinim["toplam_zorunlu_mustemilat"],
            "toplam_kapali_alan_m2": gereksinim["toplam_kapali_alan"],
            "acik_alan_m2": gereksinim["acik_alan"],
            "bakici_evi_hakki": sonuc["bakici_evi_hakki"],
            "bakici_evi_yapildi": sonuc["bakici_evi_yapildi"],
            "kalan_emsal_m2": sonuc["kalan_emsal"],
            "sonuc_mesaji": sonuc["sonuc"],
            "aciklama": sonuc["aciklama"],
            "yapilar": yapilar
        }
        
        return hesaplama_sonucu

    def hesapla_kapasite_araziye_gore(self, arazi_alani_m2, tesis_turu="Evcil Hayvan Tesisi"):
        """
        Araziden hareketle kapasite hesaplaması yapar.
        - Minimum arazi kontrolü
        - Tesisin temel gereklilikleri için alan kontrolü
        - Kapasite ve müştemilat alanlarının hesaplanması
        """
        # Temel sonuç yapısı
        sonuc = {
            "arazi_alani_m2": arazi_alani_m2,
            "emsal_m2": round(arazi_alani_m2 * self.emsal_orani, 2),
            "sonuc_durumu": "",
            "aciklama": ""
        }
        
        # 1) Mutlak minimum arazi kontrolü (500 m²)
        if arazi_alani_m2 < MIN_ARAZI_BUYUKLUGU:
            sonuc.update({
                "tahmini_kapasite": 0,
                "ortalama_kapali_alan_m2": 0,
                "zorunlu_mustemilat_alanlari_m2": {"İdari Bina": self.idari_bina_taban},
                "emsal_kullanilan_toplam_m2": self.idari_bina_taban,
                "sonuc_durumu": "TESİS YAPILAMAZ",
                "aciklama": f"Arazi büyüklüğü ({arazi_alani_m2:.2f} m²), minimum gerekli arazi büyüklüğünün ({MIN_ARAZI_BUYUKLUGU} m²) altındadır."
            })
            return sonuc
        
        # 2) Emsal hesaplama ve minimum tesis ihtiyacı kontrolü
        emsal_alani = arazi_alani_m2 * self.emsal_orani
        min_gerekli_alan = self.idari_bina_taban + 50  # İdari bina + en az 50 m² üretim alanı
        
        if emsal_alani < min_gerekli_alan:
            sonuc.update({
                "tahmini_kapasite": 0,
                "ortalama_kapali_alan_m2": 0,
                "zorunlu_mustemilat_alanlari_m2": {"İdari Bina": self.idari_bina_taban},
                "emsal_kullanilan_toplam_m2": self.idari_bina_taban,
                "sonuc_durumu": "TESİS YAPILAMAZ",
                "aciklama": f"İzin verilen toplam yapılaşma alanı ({emsal_alani:.2f} m²), " 
                           f"minimum tesis ihtiyacı ({min_gerekli_alan:.2f} m²) için yetersiz."
            })
            return sonuc
        
        # 3) Temel zorunlu müştemilat alanlarının hesaplanması (idari bina sabit)
        temel_mustemilat_alani = self.idari_bina_taban
        
        # 4) Tahmini kapasite hesaplama: (emsal - temel müştemilat) / (hayvan başı alan + ek müştemilat katsayısı)
        hayvan_basi_ortalama_alan = 4  # 3 m² temel alan + 1 m² ek müştemilat payı
        hesaplanan_kapasite = int((emsal_alani - temel_mustemilat_alani) / hayvan_basi_ortalama_alan)
        
        # 5) Minimum kapasite kontrolü - küçük işletmeler için uygun hale getirildi
        if hesaplanan_kapasite < 5:  # Minimum 5 hayvan (50'den 5'e düşürüldü)
            # Yeterli alan yoksa
            if emsal_alani < self.idari_bina_taban + 20:  # 5 hayvan için min 20 m² ek alan (200'den 20'ye düşürüldü)
                sonuc.update({
                    "tahmini_kapasite": 0,
                    "ortalama_kapali_alan_m2": 0,
                    "zorunlu_mustemilat_alanlari_m2": {"İdari Bina": self.idari_bina_taban},
                    "emsal_kullanilan_toplam_m2": self.idari_bina_taban,
                    "sonuc_durumu": "TESİS YAPILAMAZ",
                    "aciklama": "Arazi büyüklüğü, minimum 5 hayvan kapasiteli bir tesis için yetersizdir."  # 50'den 5'e değiştirildi
                })
                return sonuc
            else:
                # Alan yeterli ancak minimum standart olarak 5 kapasiteye çıkarıyoruz (50'den 5'e değiştirildi)
                kapasite = 5
        else:
            kapasite = hesaplanan_kapasite
        
        # 6) Asıl hayvan barınma/üretim alanı (ortalama 3 m²/hayvan)
        ortalama_kapali_alan = kapasite * 3
        
        # 7) Zorunlu müştemilatları hesapla
        mustemilat_alanlari = {}
        
        # İdari bina ve içindeki alanlar (kompakt bir şekilde)
        idari_bina_ici_toplam = 0
        for kod, tanim in self.mustemilat_tanimlari.items():
            if tanim.get("idari_bina_icinde", False) and tanim["grup"] == "zorunlu":
                # Logaritmik ölçekleme faktörü ile alan hesapla
                base = tanim.get("min_alan_m2", 0)
                faktor = math.log10(kapasite + 10) / math.log10(10)
                alan = round(base + base * 0.2 * math.log10(kapasite/10 + 1), 2)
                alan = min(alan, tanim.get("max_alan_m2", float('inf')))  # Üst sınır kontrolü
                
                mustemilat_alanlari[tanim["isim"]] = alan
                idari_bina_ici_toplam += alan
    
        # Toplam idari bina iç alan kontrolü
        if idari_bina_ici_toplam > self.idari_bina_taban:
            oran = self.idari_bina_taban / idari_bina_ici_toplam
            for isim in list(mustemilat_alanlari.keys()):
                mustemilat_alanlari[isim] = round(mustemilat_alanlari[isim] * oran, 2)
    
        # İdari bina dışındaki zorunlu müştemilatlar
        for kod, tanim in self.mustemilat_tanimlari.items():
            if not tanim.get("idari_bina_icinde", False) and tanim["grup"] == "zorunlu" and kod != "idari_bina":
                if kod == "acik_gezinti_alani" and not any(tip in ["kopek_kucuk", "kopek_orta", "kopek_buyuk"] for tip in ["karma"]):
                    # Sadece köpek türleri için gezinti alanı hesapla
                    continue
                    
                base = tanim.get("min_alan_m2", 0)
                faktor = math.log10(kapasite + 10) / math.log10(10)
                alan = round(base + base * 0.2 * math.log10(kapasite/10 + 1), 2)
                alan = min(alan, tanim.get("max_alan_m2", float('inf')))
                
                mustemilat_alanlari[tanim["isim"]] = alan
    
        # İdari bina alanını ekle
        mustemilat_alanlari["İdari Bina"] = self.idari_bina_taban
    
        # 8) Toplam emsale dahil alan hesapla
        toplam_alan = ortalama_kapali_alan + sum(mustemilat_alanlari.values())
        
        # Emsale dahil olmayan açık gezinti alanını ayrı hesapla
        acik_gezinti_alani = 0
        if "Açık Gezinti Alanı" in mustemilat_alanlari:
            acik_gezinti_alani = mustemilat_alanlari["Açık Gezinti Alanı"]
            toplam_alan -= acik_gezinti_alani  # Emsalden düşür
        
        # 9) Emsal kontrolü
        if toplam_alan > emsal_alani:
            # Emsal aşıldı, kapasite azaltılmalı ve tekrar hesaplanmalı
            azaltma_orani = emsal_alani / toplam_alan
            yeni_kapasite = int(kapasite * azaltma_orani)
            
            if yeni_kapasite < 5:  # Minimum kapasite kontrolü - 50'den 5'e düşürüldü
                sonuc.update({
                    "tahmini_kapasite": 0,
                    "ortalama_kapali_alan_m2": 0,
                    "zorunlu_mustemilat_alanlari_m2": {"İdari Bina": self.idari_bina_taban},
                    "emsal_kullanilan_toplam_m2": self.idari_bina_taban,
                    "sonuc_durumu": "TESİS YAPILAMAZ",
                    "aciklama": f"Arazi büyüklüğü, minimum 5 hayvan kapasiteli bir tesis için yetersizdir. Emsal alanı karşılanamamaktadır."  # 50'den 5'e değiştirildi
                })
                return sonuc
            
            # Yeni kapasiteyle tekrar hesapla (rekürsif çağrı yerine basit hesaplama)
            kapasite = yeni_kapasite
            ortalama_kapali_alan = kapasite * 3
            
            # Müştemilat alanlarını yeniden hesapla
            for isim in mustemilat_alanlari.keys():
                if isim != "İdari Bina":  # İdari bina sabit kalır
                    mustemilat_alanlari[isim] = round(mustemilat_alanlari[isim] * azaltma_orani, 2)
            
            # Toplam alanı güncelle
            toplam_alan = ortalama_kapali_alan + sum(v for k, v in mustemilat_alanlari.items() if k != "Açık Gezinti Alanı")
        # 10) Bakıcı evi hakkı kontrolü (50+ kedi, 30+ köpek, 100+ karma tesis)
        bakici_evi_hakki = (kapasite >= 30)  # Basitleştirilmiş kontrol
        
        sonuc.update({
            "tahmini_kapasite": kapasite,
            "ortalama_kapali_alan_m2": round(ortalama_kapali_alan, 2),
            "zorunlu_mustemilat_alanlari_m2": mustemilat_alanlari,
            "emsal_kullanilan_toplam_m2": round(toplam_alan, 2),
            "acik_gezinti_alani_m2": acik_gezinti_alani,
            "bakici_evi_hakki": bakici_evi_hakki,
            "sonuc_durumu": "TESİS YAPILABİLİR",
            "aciklama": f"Arazi büyüklüğü, yaklaşık {kapasite} hayvan kapasiteli bir tesis için uygundur."
        })
        
        return sonuc


def olustur_html_mesaj_evcil_hayvan_genel(sonuc, hesaplayici=None):
    emsal_yuzde = (hesaplayici.emsal_orani if hesaplayici else EMSAL_ORANI) * 100
    toplam_alan = sonuc.get('emsal_m2', sonuc.get('emsal', 0))
    # Kedi ve köpek başı alanlar
    kedi_basi_alan = HAYVAN_TURLERI['kedi']['kapali_alan']
    kopek_kucuk_basi_alan = HAYVAN_TURLERI['kopek_kucuk']['kapali_alan']
    kopek_orta_basi_alan = HAYVAN_TURLERI['kopek_orta']['kapali_alan']
    kopek_buyuk_basi_alan = HAYVAN_TURLERI['kopek_buyuk']['kapali_alan']
    # Sadece kedi kapasitesi
    kedi_kapasite = int(toplam_alan // kedi_basi_alan)
    # Sadece köpek kapasitesi (küçük/orta/büyük dağılımı ile)
    kopek_kapasite = int(toplam_alan // 3)  # Ortalama köpek alanı 3 m² (örnek)
    # Dağılım: %50 küçük, %30 orta, %20 büyük
    kopek_kucuk = int(kopek_kapasite * 0.5)
    kopek_orta = int(kopek_kapasite * 0.3)
    kopek_buyuk = kopek_kapasite - kopek_kucuk - kopek_orta

    mesaj = f"""
    <style>
        .evcil-sonuc {{font-family: Arial, sans-serif; max-width: 100%; margin: 0 auto;}}
        .evcil-sonuc h3 {{color: #1565c0; margin-bottom: 15px;}}
        .evcil-sonuc .baslik {{font-weight: bold; margin-top: 15px; margin-bottom: 8px;}}
        .evcil-sonuc table {{border-collapse: collapse; width: 100%; margin-bottom: 18px;}}
        .evcil-sonuc th, .evcil-sonuc td {{border: 1px solid #ddd; padding: 8px; font-size: 1em;}}
        .evcil-sonuc th {{background-color: #e3f2fd;}}
        .evcil-sonuc .asil {{background-color: #e8f5e9;}}
        .evcil-sonuc .mustemilat {{background-color: #fffde7;}}
        .evcil-sonuc .bakici {{background-color: #f0f4c3;}}
        .evcil-sonuc .ozet {{background-color: #f8f9fa;}}
        .evcil-sonuc .uyari {{color: #856404; background-color: #fff3cd; padding: 8px; border-radius: 4px; margin: 10px 0;}}
        .evcil-sonuc .basarili {{color: #155724; background-color: #d4edda; padding: 8px; border-radius: 4px; margin: 10px 0;}}
        .evcil-sonuc .hata {{color: #721c24; background-color: #f8d7da; padding: 8px; border-radius: 4px; margin: 10px 0;}}
        .evcil-sonuc .notlar {{font-size: 0.97em; font-style: italic; margin-top: 16px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;}}
        @media (max-width: 600px) {{
            .evcil-sonuc th, .evcil-sonuc td {{font-size: 0.97em;}}
            .evcil-sonuc h3 {{font-size: 1.2em;}}
        }}
    </style>
    <div class="evcil-sonuc">
    """
    mesaj += f"<h3>EVCİL HAYVAN TESİSİ DEĞERLENDİRME</h3>"
    mesaj += f"<div class='baslik'>Arazi Bilgileri</div>"
    mesaj += f"<table><tr><th>Arazi</th><th>Emsal (%)</th><th>Emsal Alanı (m²)</th></tr>"
    mesaj += f"<tr><td>{sonuc.get('arazi_alani_m2', sonuc.get('arazi_alani', 0)):,.2f}</td><td>{emsal_yuzde:.0f}</td><td>{toplam_alan:,.2f}</td></tr></table>"
    # Sonuç mesajı
    # 'aciklama' alanında kapasite cümlesi varsa onu filtrele
    aciklama = sonuc.get('aciklama','')
    if aciklama:
        # Kapasite cümlesini kaldır
        aciklama = aciklama.replace('Arazi büyüklüğü, yaklaşık', '').split('kapasiteli bir tesis için uygundur.')[1] if 'kapasiteli bir tesis için uygundur.' in aciklama else aciklama
    mesaj += f"<div class='basarili'><b>SONUÇ: {sonuc.get('sonuc_mesaji') or sonuc.get('sonuc_durumu', '')}</b><br>{aciklama}</div>"
    mesaj += f"<div class='baslik'>Kedi Kapasitesi</div>"
    mesaj += f"<table><tr><th>Tür</th><th>Kapasite (adet)</th><th>Hayvan başı alan (m²)</th></tr>"
    mesaj += f"<tr><td>{HAYVAN_TURLERI['kedi']['ad']}</td><td>{kedi_kapasite}</td><td>{kedi_basi_alan}</td></tr>"
    mesaj += f"</table>"
    mesaj += f"<div class='baslik'>Köpek Kapasitesi</div>"
    mesaj += f"<table><tr><th>Tür</th><th>Kapasite (adet)</th><th>Hayvan başı alan (m²)</th></tr>"
    mesaj += f"<tr><td>{HAYVAN_TURLERI['kopek_kucuk']['ad']}</td><td>{kopek_kucuk}</td><td>{kopek_kucuk_basi_alan}</td></tr>"
    mesaj += f"<tr><td>{HAYVAN_TURLERI['kopek_orta']['ad']}</td><td>{kopek_orta}</td><td>{kopek_orta_basi_alan}</td></tr>"
    mesaj += f"<tr><td>{HAYVAN_TURLERI['kopek_buyuk']['ad']}</td><td>{kopek_buyuk}</td><td>{kopek_buyuk_basi_alan}</td></tr>"
    mesaj += f"<tr style='font-weight:bold'><td>Toplam</td><td>{kopek_kapasite}</td><td>-</td></tr>"
    mesaj += f"</table>"
    # Asıl üretim yapısı tablosu
    asil_uretim = sonuc.get('asil_uretim_alani_m2', sonuc.get('ortalama_kapali_alan_m2', 0))
    mesaj += f"<div class='baslik'>Asıl Üretim Yapısı</div>"
    mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"
    mesaj += f"<tr class='asil'><td>Asıl Üretim Yapısı</td><td>{asil_uretim:,.2f}</td></tr>"
    mesaj += "</table>"

    # Zorunlu müştemilatlar tablosu
    mesaj += f"<div class='baslik'>Zorunlu Müştemilatlar</div>"
    mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"
    # Detaylı modda
    if "yapilar" in sonuc:
        for yapi in sonuc.get("yapilar", []):
            if yapi.get("tip") == "zorunlu_mustemilat":
                mesaj += f"<tr class='mustemilat'><td>{yapi.get('isim','')}</td><td>{yapi.get('taban_alani',0):,.2f}</td></tr>"
    # Kapasiteye göre modda
    elif "zorunlu_mustemilat_alanlari_m2" in sonuc:
        for isim, alan in sonuc.get("zorunlu_mustemilat_alanlari_m2", {}).items():
            mesaj += f"<tr class='mustemilat'><td>{isim}</td><td>{alan:,.2f}</td></tr>"
    mesaj += "</table>"

    # Bakıcı evi tablosu (varsa)
    bakici_evi_var = False
    if "yapilar" in sonuc:
        bakici_evi_var = any(y.get("tip") == "bakici_evi" for y in sonuc.get("yapilar", []))
    elif "bakici_evi_hakki" in sonuc:
        bakici_evi_var = sonuc.get("bakici_evi_hakki", False)
    if bakici_evi_var:
        mesaj += f"<div class='baslik'>Bakıcı Evi</div>"
        mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"
        if "yapilar" in sonuc:
            for yapi in sonuc.get("yapilar", []):
                if yapi.get("tip") == "bakici_evi":
                    mesaj += f"<tr class='bakici'><td>{yapi.get('isim','')}</td><td>{yapi.get('taban_alani',0):,.2f}</td></tr>"
        else:
            mesaj += f"<tr class='bakici'><td>Bakıcı Evi</td><td>{BAKICI_EVI_TABAN_ALANI:,.2f}</td></tr>"
        mesaj += "</table>"

    # Açık alan tablosu
    acik_alan = sonuc.get('acik_alan_m2', sonuc.get('acik_alan', 0))
    mesaj += f"<div class='baslik'>Açık Alanlar</div>"
    mesaj += "<table><tr><th>Alan</th><th>Değer (m²)</th></tr>"
    mesaj += f"<tr><td>Açık Alan İhtiyacı</td><td>{acik_alan:,.2f}</td></tr>"
    mesaj += "</table>"

    # Genel özet tablosu (en altta)
    toplam_kullanilan_emsal = sonuc.get('toplam_kapali_alan_m2', sonuc.get('emsal_kullanilan_toplam_m2', 0))
    mesaj += "<div class='baslik'>Genel Özet</div>"
    mesaj += "<table><tr><th>Alan Türü</th><th>Değer (m²)</th></tr>"
    mesaj += f"<tr class='ozet'><td>Arazi Alanı</td><td>{sonuc.get('arazi_alani_m2', sonuc.get('arazi_alani', 0)):,.2f}</td></tr>"
    mesaj += f"<tr class='ozet'><td>Emsal Alanı</td><td>{sonuc.get('emsal_m2', sonuc.get('emsal', 0)):,.2f}</td></tr>"
    mesaj += f"<tr class='ozet'><td>Kullanılan Alan</td><td>{toplam_kullanilan_emsal:,.2f}</td></tr>"
    kalan_emsal = sonuc.get('kalan_emsal_m2', sonuc.get('kalan_emsal', 0))
    mesaj += f"<tr class='ozet'><td>Kalan Emsal</td><td>{kalan_emsal:,.2f}</td></tr>"
    mesaj += "</table>"

    # Notlar bölümü
    mesaj += "<div class='notlar'>"
    mesaj += "<b>NOT:</b> Tüm hesaplamalar ilgili yönetmeliklere göre yapılmıştır.<br>"
    mesaj += "- Bakıcı evi hakkı için yeterli hayvan kapasitesi gereklidir.<br>"
    mesaj += "- Açık alanlar emsale dahil değildir.<br>"
    mesaj += "- Bu değerlendirme ön bilgilendirme amaçlıdır ve resmi bir belge niteliği taşımaz."
    mesaj += "</div></div>"
    return mesaj

def _olustur_html_mesaj_evcil_hayvan_kapasiteye_gore(sonuc, hesaplayici=None):
    """Ayrıntılı tesis değerlendirme sonucunu HTML tablosu olarak oluşturur"""
    # Arazi ve sonuç durumu bilgileri
    arazi_alani = sonuc.get('arazi_alani_m2', 0)
    emsal_alani = sonuc.get('emsal_m2', 0)
    emsal_yuzde = (hesaplayici.emsal_orani if hesaplayici else EMSAL_ORANI) * 100
    sonuc_durumu = sonuc.get('sonuc_durumu', '')
    aciklama = sonuc.get('aciklama', '')
    
    mesaj = f"""
    <div class="result-container">
        <h3>EVCİL HAYVAN TESİSİ DEĞERLENDİRMESİ</h3>
        <p><b>Arazi Büyüklüğü:</b> {arazi_alani:,.2f} m²</p>
        <p><b>İzin Verilen Toplam Yapılaşma Alanı (%{emsal_yuzde:.0f}):</b> {emsal_alani:,.2f} m²</p>
    """
    
    # Eğer tesis yapılamazsa hata mesajı göster
    if sonuc_durumu == "TESİS YAPILAMAZ":
        mesaj += f"""
        <div class="alert alert-danger">
            <h4>SONUÇ: {sonuc_durumu}</h4>
            <p><b>Açıklama:</b> {aciklama}</p>
        </div>
        """
    else:
        # Tesis yapılabiliyorsa kapasite ve alan bilgilerini tabloda göster
        kapasite = sonuc.get('tahmini_kapasite', 0)
        kapali_alan = sonuc.get('ortalama_kapali_alan_m2', 0)
        mustemilat_alanlari = sonuc.get('zorunlu_mustemilat_alanlari_m2', {})
        toplam_emsal = sonuc.get('emsal_kullanilan_toplam_m2', 0)
        bakici_evi_hakki = sonuc.get('bakici_evi_hakki', False)
        
        mesaj += f"""
        <div class="alert alert-success">
            <h4>SONUÇ: {sonuc_durumu}</h4>
            <p><b>Kapasite:</b> Yaklaşık {kapasite} hayvan barındırabilir</p>
            <p><b>Açıklama:</b> {aciklama}</p>
        </div>
        
        <h4>TESİS DETAYLARI</h4>
        <table class="table table-bordered">
            <thead>
                <tr>
                    <th>Alan Tipi</th>
                    <th>Büyüklük (m²)</th>
                    <th>Notlar</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Asıl Üretim Alanı</td>
                    <td>{kapali_alan:,.2f}</td>
                    <td>Hayvan barınma/üretim alanı</td>
                </tr>
        """
        
        # Müştemilat alanlarını göster
        idari_bina = False
        for isim, alan in mustemilat_alanlari.items():
            ek_not = ""
            stil = ""
            
            # Özel durum notları
            if isim == "İdari Bina":
                idari_bina = True
                ek_not = "Veteriner odası, ofis, duş/WC vb. birimleri içerir"
                stil = "style='background-color:#f8f9fa'"
                
            # Emsale dahil olmayan alanlar için not
            emsal_disi = isim == "Açık Gezinti Alanı"
            if emsal_disi:
                ek_not = "Emsale dahil değil"
                stil = "style='background-color:#e8f4f8'"
            
            mesaj += f"""
                <tr {stil}>
                    <td>{isim}</td>
                    <td>{alan:,.2f}</td>
                    <td>{ek_not}</td>
                </tr>
            """
        
        # Bakıcı evi bilgisi
        if bakici_evi_hakki:
            mesaj += f"""
                <tr style='background-color:#f0f4c3'>
                    <td>Bakıcı Evi (Opsiyonel)</td>
                    <td>{BAKICI_EVI_TABAN_ALANI:,.2f}</td>
                    <td>Bakıcı evi hakkı kazanılmıştır</td>
                </tr>
            """
            
        # Toplam alan bilgisi
        mesaj += f"""
                <tr style='font-weight:bold'>
                    <td>TOPLAM YAPILACAK ALAN</td>
                    <td>{toplam_emsal:,.2f}</td>
                    <td>Emsale dahil toplam alan ({emsal_alani:,.2f} m² sınırı içinde)</td>
                </tr>
            </tbody>
        </table>
        """
        
        # Uyarı ve notlar
        mesaj += """
        <div class="notes">
            <h4>UYARI VE NOTLAR</h4>
            <ul>
                <li>Bu değerlendirme ön bilgilendirme amaçlıdır ve resmi bir belge niteliği taşımaz.</li>
                <li>Tüm hesaplamalar 'Ev ve Süs Hayvanlarının Üretim ve Satış, Barınma ve Eğitim Yerleri Hakkında Yönetmelik' ile 'Deneysel ve Diğer Bilimsel Amaçlar İçin Kullanılan Hayvanların Refah ve Korunmasına Dair Yönetmelik' hükümlerine göre yapılmıştır.</li>
                <li>Tesis kurulumu öncesinde resmi başvuru yaparak detaylı bilgi alınması önerilir.</li>
            </ul>
        </div>
        """
    mesaj += "</div>"
    return mesaj

def evcil_hayvan_tesisi_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None) -> dict:
    """
    Arazi odaklı evcil hayvan tesisi değerlendirmesi yapar.
    Kullanıcı dostu bir HTML çıktısı üretir.
    """
    # Arazi büyüklüğü kontrolü
    try:
        arazi_buyuklugu = float(arazi_bilgileri.get("buyukluk_m2", 0))
        if arazi_buyuklugu <= 0:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Girilen arazi büyüklüğü sıfır veya negatif olamaz.</div>",
                "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Girilen arazi büyüklüğü sıfır veya negatif olamaz.</div>",
                "kapasite": 0,
                "bakici_evi_hakki": False
            }
    except (ValueError, TypeError):
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Lütfen sayısal bir değer giriniz.</div>",
            "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Lütfen sayısal bir değer giriniz.</div>",
            "kapasite": 0,
            "bakici_evi_hakki": False
        }
    
    # YAS ve su tahsis belgesi kontrolü
    su_tahsis_belgesi_var_mi = str(arazi_bilgileri.get("su_tahsis_belgesi","false")).lower() == "true"
    yas_kapali_alanda_mi = arazi_bilgileri.get("yas_kapali_alan_durumu") == "içinde"
    
    # YAS alanında olup su tahsis belgesi yoksa
    if yas_kapali_alanda_mi and not su_tahsis_belgesi_var_mi:
        yas_uyari_mesaji = """
        <div class='alert alert-warning'>
            <h4>Yeraltı Suyu Koruma Alanında Su Tahsis Belgesi Gerekli</h4>
            <p>Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) içerisinde yer almaktadır. 
            Bu bölgede tesis kurulumu için <b>su tahsis belgesi zorunludur</b>.</p>
            <p>Su tahsis belgesi olmadan tesise izin verilmemektedir.</p>
        </div>
        """
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": yas_uyari_mesaji,
            "ana_mesaj": yas_uyari_mesaji,
            "kapasite": 0,
            "bakici_evi_hakki": False
        }

    # Kapasiteye göre hesaplama yap
    hesaplayici = EvcilHayvanTesisiHesaplayici(emsal_orani)
    kapasite_sonucu = hesaplayici.hesapla_kapasite_araziye_gore(arazi_buyuklugu)
    html = olustur_html_mesaj_evcil_hayvan_genel(kapasite_sonucu, hesaplayici)
    
    # Sonuç için gerekli bilgileri çıkar
    kapasite = kapasite_sonucu.get("tahmini_kapasite", 0)
    bakici_evi_hakki = kapasite_sonucu.get("bakici_evi_hakki", False)
    izin_durumu = "izin_verilebilir" if kapasite_sonucu.get("sonuc_durumu") == "TESİS YAPILABİLİR" else "izin_verilemez"
    
    # Sonucu döndür
    return {
        "izin_durumu": izin_durumu,
        "mesaj": html,
        "ana_mesaj": html,
        "kapasite": kapasite,
        "bakici_evi_hakki": bakici_evi_hakki,
    }

# Minimum arazi ihtiyacı için önbellek
_min_arazi_ihtiyaci_onbellek = {}

def hesapla_minimum_arazi_buyuklugu_onbellekli(hesaplayici, kapasite, hayvan_turleri_listesi):
    """Minimum arazi ihtiyacını hesaplar ve sonucu önbelleğe alır"""
    anahtar = (kapasite, tuple(hayvan_turleri_listesi) if hayvan_turleri_listesi else None)
    if anahtar not in _min_arazi_ihtiyaci_onbellek:
        _min_arazi_ihtiyaci_onbellek[anahtar] = hesaplayici.hesapla_minimum_arazi_buyuklugu(kapasite, hayvan_turleri_listesi)
    return _min_arazi_ihtiyaci_onbellek[anahtar]

# Diğer optimizasyonlar...
