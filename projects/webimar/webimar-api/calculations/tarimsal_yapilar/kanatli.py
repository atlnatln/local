#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kanatlı Hayvancılık Tesisi Emsal Hesaplama Aracı (Revize)

Bu program, verilen arazi büyüklüğüne göre kanatlı hayvan tesisi 
kapasitesini, müştemilat alanlarını ve bakıcı evi hakkını hesaplar.
Serbest dolaşan tavuk senaryoları için gezinti alanı kısıtı da hesaba katılır.
"""

import sys  # sys modülünü ekleyelim

# Kanatlı hayvancılık için sabitler - PHASE 2 DİNAMİK EMSAL SİSTEMİ
DEFAULT_EMSAL_ORANI = 0.20  # %20 varsayılan (dinamik sistem için)

# Bakıcı evi büyüklükleri (kapalı alana göre kademeli)
BAKICI_EVI_BUYUKLUKLERI = {
    "750-1500": {"taban_alani": 75, "toplam_alan": 150},
    ">1500": {"taban_alani": 150, "toplam_alan": 300}
}

# Yeni Gübre Çukuru Hesaplamaları (1000 adet için m²)
GUBRE_CUKURU_ALANLARI = {
    "etçi_tavuk": 7.3528 / 4,        # 7.3528 m² / 4m derinlik = 1.8382 m²
    "yumurtacı_tavuk": 21.2706 / 4,  # 21.2706 m² / 4m derinlik = 5.31765 m²
    "serbest_tavuk": 21.2706 / 4,    # Gezen tavuk = Yumurtacı tavuk aynı
    "hindi": 7.3528 * 2 / 4,         # 7.3528*2 / 4m derinlik = 3.6764 m²
    "kaz": 7.3528 / 4,               # 7.3528 m² / 4m derinlik = 1.8382 m²
}

class KanatlıHesaplama:
    def __init__(self, emsal_orani: float = None):
        # Dinamik emsal oranını belirle
        self.emsal_oranı = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
        
        # Hayvan yoğunlukları (adet/m²)
        self.hayvan_yoğunlukları = {
            "yumurtacı_tavuk": 6,
            "etçi_tavuk": 14,
            "hindi": 3,
            "kaz": 2,
            "serbest_tavuk": 4
        }
        
        # Gezinti alanı gerekliliği (m²/hayvan)
        self.gezinti_alanı_gerekliliği = {
            "serbest_tavuk": 2  # Serbest tavuklar için 2 m²/tavuk
        }
        
        # Gübre çukuru alanları (1000 adet için m²)
        self.gubre_cukuru_alanlari = GUBRE_CUKURU_ALANLARI
        
        # Bakıcı evi hakkı eşik değerleri
        self.bakıcı_evi_eşikleri = {
            "yumurtacı_tavuk": 7500,
            "etçi_tavuk": 10000,
            "hindi": 1000,
            "kaz": 1000,
            "serbest_tavuk": 1000
        }
        
        # Yapı büyüklükleri
        self.bakıcı_evi_büyüklükleri = BAKICI_EVI_BUYUKLUKLERI
        self.bekçi_kulübesi_alanı = 15.0
        self.idari_bina_alanı = 75.0
        
        # Minimum alan gereksinimleri
        self.min_zorunlu_müştemilat_alanı = 40.0
        self.min_işlevsel_kümes_alanı = 30.0 # Kümesin işlevsel olabilmesi için gereken minimum alan
        
        # Müştemilat detay hesaplamaları (hayvan başına m²)
        self.mustemilat_detaylari = {
            "gubre_deposu": {
                "isim": "Gübre Deposu/Çukuru (Derinlik: 4m)",
                "hayvan_basi_alan_m2": 0.05,  # Her kanatlı için 0.05 m² (0.2 m³ / 4m derinlik)
                "min_alan_m2": 2,  # Minimum 2 m²
                "max_alan_m2": 5000,  # Maksimum 5000 m² (orantılı büyüme için)
                "aciklama": "Her kanatlı hayvan için 0.05 m² alan hesaplanır"
            },
            "yem_deposu": {
                "isim": "Konsantre Yem Deposu",
                "hayvan_basi_alan_m2": 0.08,  # Her kanatlı için 0.08 m²
                "min_alan_m2": 6,  # Minimum 6 m²
                "max_alan_m2": 40,  # Maksimum 40 m²
                "aciklama": "Her kanatlı hayvan için 0.08 m² alan hesaplanır"
            },
            "su_deposu": {
                "isim": "Su Deposu",
                "hayvan_basi_alan_m2": 0.02,  # Her kanatlı için 0.02 m²
                "min_alan_m2": 3,  # Minimum 3 m²
                "max_alan_m2": 20,  # Maksimum 20 m²
                "aciklama": "Her kanatlı hayvan için 0.02 m² alan hesaplanır"
            }
        }
        
    def _hesapla_mustemilat_detaylari(self, hayvan_kapasitesi: int, hayvan_tipi: str = "yumurtacı_tavuk") -> dict:
        """
        Hayvan kapasitesine göre müştemilat detaylarını hesaplar
        """
        detaylar = {}
        toplam_alan = 0
        
        for kod, tanim in self.mustemilat_detaylari.items():
            # Gübre çukuru için yeni hesaplama sistemi
            if kod == "gubre_deposu":
                # 1000 adet için hesaplanmış alanı kullan
                if hayvan_tipi in self.gubre_cukuru_alanlari:
                    alan_per_1000 = self.gubre_cukuru_alanlari[hayvan_tipi]
                    alan = (hayvan_kapasitesi / 1000) * alan_per_1000
                    alan = max(alan, tanim["min_alan_m2"])
                else:
                    # Varsayılan hesaplama
                    alan = max(
                        tanim["min_alan_m2"], 
                        min(
                            tanim["hayvan_basi_alan_m2"] * hayvan_kapasitesi,
                            tanim["max_alan_m2"]
                        )
                    )
            else:
                # Diğer müştemilatlar için normal hesaplama
                alan = max(
                    tanim["min_alan_m2"], 
                    min(
                        tanim["hayvan_basi_alan_m2"] * hayvan_kapasitesi,
                        tanim["max_alan_m2"]
                    )
                )
            detaylar[kod] = {
                "isim": tanim["isim"],
                "alan_m2": round(alan, 2),
                "aciklama": tanim["aciklama"]
            }
            toplam_alan += alan
        
        return {
            "detaylar": detaylar,
            "toplam_alan_m2": round(toplam_alan, 2)
        }
        
    def _belirle_bakici_evi_boyutu(self, kapali_alan_m2):
        """Kapalı alan büyüklüğüne göre bakıcı evi taban ve toplam inşaat alanını belirler."""
        if kapali_alan_m2 > 1500:
            return self.bakıcı_evi_büyüklükleri[">1500"]["taban_alani"], self.bakıcı_evi_büyüklükleri[">1500"]["toplam_alan"]
        elif kapali_alan_m2 >= 750:
            return self.bakıcı_evi_büyüklükleri["750-1500"]["taban_alani"], self.bakıcı_evi_büyüklükleri["750-1500"]["toplam_alan"]
        return 0, 0

    def hesapla(self, arazi_alanı, hayvan_tipi="yumurtacı_tavuk"):
        """Ana hesaplama fonksiyonu"""
        # Emsal hesabı
        emsal = arazi_alanı * self.emsal_oranı
        
        # Eğer hayvan tipi geçerli değilse, varsayılan olarak yumurtacı tavuk kullan
        if hayvan_tipi not in self.hayvan_yoğunlukları:
            hayvan_tipi = "yumurtacı_tavuk"
        
        # Hayvan yoğunluğu ve bakıcı evi eşiği
        hayvan_yoğunluğu = self.hayvan_yoğunlukları[hayvan_tipi]
        bakıcı_evi_eşiği = self.bakıcı_evi_eşikleri[hayvan_tipi]
        
        # Emsal yeterli mi kontrol et (minimum müştemilat + minimum kümes için)
        if emsal < self.min_zorunlu_müştemilat_alanı + self.min_işlevsel_kümes_alanı:
            açıklama_metni = ""
            if emsal < self.min_zorunlu_müştemilat_alanı:
                açıklama_metni = f"Emsale göre izin verilen {emsal:.2f} m² yapılaşma alanı, zorunlu müştemilat için gerekli olan minimum {self.min_zorunlu_müştemilat_alanı:.2f} m²'den bile azdır."
            else:
                açıklama_metni = f"Zorunlu müştemilat alanı ({self.min_zorunlu_müştemilat_alanı:.2f} m²) karşılandıktan sonra kümes için yeterli ({self.min_işlevsel_kümes_alanı:.2f} m²) alan kalmamaktadır."
            return {
                "sonuç": "TESİS YAPILAMAZ",
                "açıklama": açıklama_metni,
                "arazi_alanı": arazi_alanı,
                "emsal": emsal,
                "hayvan_tipi": hayvan_tipi
            }
        
        # Serbest dolaşan tavuklar için özel hesaplama
        if hayvan_tipi == "serbest_tavuk":
            return self.hesapla_serbest_tavuk(arazi_alanı, emsal, hayvan_yoğunluğu, bakıcı_evi_eşiği)
        
        # Standart hesaplama (diğer hayvan tipleri için)
        return self.standart_hesaplama(arazi_alanı, emsal, hayvan_tipi, hayvan_yoğunluğu, bakıcı_evi_eşiği)
    
    def hesapla_serbest_tavuk(self, arazi_alanı, emsal, hayvan_yoğunluğu, bakıcı_evi_eşiği):
        """Serbest dolaşan tavuklar için özel hesaplama fonksiyonu"""
        # Emsale göre potansiyel kümes ve müştemilat
        kümes_alanı_emsal_bazli = emsal * 0.75
        müştemilat_alanı_emsal_bazli = emsal * 0.25
        if kümes_alanı_emsal_bazli <= 120:
            if müştemilat_alanı_emsal_bazli < self.min_zorunlu_müştemilat_alanı:
                müştemilat_alanı_emsal_bazli = self.min_zorunlu_müştemilat_alanı
                kümes_alanı_emsal_bazli = emsal - müştemilat_alanı_emsal_bazli
                if kümes_alanı_emsal_bazli < 0: kümes_alanı_emsal_bazli = 0
        tavuk_kapasitesi_emsal = int(kümes_alanı_emsal_bazli * hayvan_yoğunluğu)
        
        # Gezinti alanı kısıtına göre kapasite
        yapılı_alan_tahmini_max = emsal # En kötü durum senaryosu, tüm emsal kullanılırsa
        kullanılabilir_gezinti_alanı = arazi_alanı - yapılı_alan_tahmini_max
        if kullanılabilir_gezinti_alanı < 0: kullanılabilir_gezinti_alanı = 0
        tavuk_kapasitesi_gezinti = int(kullanılabilir_gezinti_alanı / self.gezinti_alanı_gerekliliği["serbest_tavuk"])
        
        # Belirleyici kapasite
        tavuk_kapasitesi_final = min(tavuk_kapasitesi_emsal, tavuk_kapasitesi_gezinti)
        
        # Belirleyici kapasiteye göre gerçek kümes ve müştemilat alanları
        kümes_alanı_final = tavuk_kapasitesi_final / hayvan_yoğunluğu
        if kümes_alanı_final <= 120:
            müştemilat_alanı_final = self.min_zorunlu_müştemilat_alanı
        else:
            müştemilat_alanı_final = kümes_alanı_final / 3 # 1/4'ü müştemilat, 3/4'ü kümes ise müştemilat = kümes/3
        
        # Toplam kümes+müştemilat alanı, emsali aşmamalı (genelde aşmaz çünkü kapasite zaten emsal veya gezinti ile sınırlı)
        if kümes_alanı_final + müştemilat_alanı_final > emsal:
            # Bu durumun olmaması gerekir, ama bir güvenlik kontrolü
            # Emsali aşarsa, kapasiteyi emsale göre yeniden ayarla (bu durumda gezinti alanı daha kısıtlayıcı olmalıydı)
            kümes_alanı_final = emsal * 0.75
            müştemilat_alanı_final = emsal * 0.25
            if kümes_alanı_final <= 120:
                if müştemilat_alanı_final < self.min_zorunlu_müştemilat_alanı:
                    müştemilat_alanı_final = self.min_zorunlu_müştemilat_alanı
                    kümes_alanı_final = emsal - müştemilat_alanı_final
            tavuk_kapasitesi_final = int(kümes_alanı_final * hayvan_yoğunluğu)

        bakıcı_evi_hakkı_calc = tavuk_kapasitesi_final >= bakıcı_evi_eşiği
        
        sonuç_yapılar = []
        bakıcı_evi_yapıldı = False
        bakıcı_evi_taban_alanı = 0
        bakıcı_evi_toplam_inşaat = 0

        # Kapalı alan bazlı bakıcı evi boyutu belirle
        kapali_alan = kümes_alanı_final + müştemilat_alanı_final
        if bakıcı_evi_hakkı_calc:
            bakıcı_evi_taban_alanı, bakıcı_evi_toplam_inşaat = self._belirle_bakici_evi_boyutu(kapali_alan)

        # Opsiyonel yapılar için kalan emsal hesabı
        emsal_kullanılan_KM = kümes_alanı_final + müştemilat_alanı_final
        kalan_emsal_opsiyonel_icin = emsal - emsal_kullanılan_KM

        if bakıcı_evi_hakkı_calc and bakıcı_evi_taban_alanı > 0 and kalan_emsal_opsiyonel_icin >= bakıcı_evi_taban_alanı:
            bakıcı_evi_yapıldı = True
            sonuç_yapılar.append({"isim": "Bakıcı evi", "alan": bakıcı_evi_taban_alanı, "toplam_insaat": bakıcı_evi_toplam_inşaat})
            kalan_emsal_opsiyonel_icin -= bakıcı_evi_taban_alanı
        
        if kalan_emsal_opsiyonel_icin >= self.bekçi_kulübesi_alanı:
            sonuç_yapılar.append({"isim": "Bekçi kulübesi", "alan": self.bekçi_kulübesi_alanı})
            kalan_emsal_opsiyonel_icin -= self.bekçi_kulübesi_alanı
            
        if kalan_emsal_opsiyonel_icin >= self.idari_bina_alanı:
            sonuç_yapılar.append({"isim": "İdari bina", "alan": self.idari_bina_alanı})
            kalan_emsal_opsiyonel_icin -= self.idari_bina_alanı
            
        kısıt_açıklaması = "emsal kısıtı"
        if tavuk_kapasitesi_final == tavuk_kapasitesi_gezinti and tavuk_kapasitesi_gezinti < tavuk_kapasitesi_emsal :
             kısıt_açıklaması = "gezinti alanı kısıtı"
        
        açıklama = f"Kapasite {kısıt_açıklaması} nedeniyle {tavuk_kapasitesi_final} tavukla sınırlandırılmıştır."
        
        sonuç_metni = ""
        if tavuk_kapasitesi_final > 0:
            if bakıcı_evi_hakkı_calc and bakıcı_evi_yapıldı:
                sonuç_metni = f"TESİS VE BAKICI EVİ YAPILABİLİR ({tavuk_kapasitesi_final:,} ADET SERBEST TAVUK KAPASİTELİ)".replace(",", ".")
            elif bakıcı_evi_hakkı_calc and not bakıcı_evi_yapıldı:
                sonuç_metni = f"TESİS YAPILABİLİR ({tavuk_kapasitesi_final:,} ADET SERBEST TAVUK KAPASİTELİ), BAKICI EVİ HAKKI KAZANILIR, ANCAK BAKICI EVİ İÇİN YETERLİ EMSAL ALANI KALMAMIŞTIR".replace(",", ".")
            else:
                sonuç_metni = f"TESİS YAPILABİLİR ({tavuk_kapasitesi_final:,} ADET SERBEST TAVUK KAPASİTELİ, BAKICI EVİ HAK DOĞMAZ)".replace(",", ".")
        else:
            sonuç_metni = "TESİS YAPILAMAZ" # Bu durum ana fonksiyonda yakalanmalıydı
            açıklama = "Belirlenen kısıtlar nedeniyle işlevsel bir tesis kurulamamaktadır."


        # Müştemilat detaylarını hesapla
        mustemilat_detaylari = self._hesapla_mustemilat_detaylari(tavuk_kapasitesi_final, "serbest_tavuk")

        return {
            "arazi_alanı": arazi_alanı, "emsal": emsal, "hayvan_tipi": "serbest_tavuk",
            "kümes_alanı": kümes_alanı_final, "müştemilat_alanı": müştemilat_alanı_final,
            "hayvan_kapasitesi": tavuk_kapasitesi_final,
            "bakıcı_evi_hakkı": bakıcı_evi_hakkı_calc,
            "yapılar": sonuç_yapılar,
            "gezinti_alanı_kapasitesi": tavuk_kapasitesi_gezinti,
            "emsal_kapasitesi": tavuk_kapasitesi_emsal,
            "belirleyici_kısıt": kısıt_açıklaması,
            "mustemilat_detaylari": mustemilat_detaylari,
            "sonuç": sonuç_metni, "açıklama": açıklama
        }
    
    def standart_hesaplama(self, arazi_alanı, emsal, hayvan_tipi, hayvan_yoğunluğu, bakıcı_evi_eşiği):
        """Standart hesaplama (serbest dolaşan tavuk dışındaki hayvanlar için)"""
        
        # Opsiyon 1: Bakıcı evi olmadan maksimum kapasite
        kümes_opt1 = emsal * 0.75
        müştemilat_opt1 = emsal * 0.25
        if kümes_opt1 <= 120:
            if müştemilat_opt1 < self.min_zorunlu_müştemilat_alanı:
                müştemilat_opt1 = self.min_zorunlu_müştemilat_alanı
                kümes_opt1 = emsal - müştemilat_opt1
                if kümes_opt1 < 0: kümes_opt1 = 0
        kapasite_opt1 = int(kümes_opt1 * hayvan_yoğunluğu)
        
        bakıcı_evi_hakkı_calc = kapasite_opt1 >= bakıcı_evi_eşiği
        
        # Kapalı alan bazlı bakıcı evi boyutu belirle
        kapali_alan_opt1 = kümes_opt1 + müştemilat_opt1
        bakıcı_evi_taban_alanı = 0
        bakıcı_evi_toplam_inşaat = 0
        if bakıcı_evi_hakkı_calc:
            bakıcı_evi_taban_alanı, bakıcı_evi_toplam_inşaat = self._belirle_bakici_evi_boyutu(kapali_alan_opt1)
        
        # Başlangıçta final değerleri Opsiyon 1'e göre ayarla
        kümes_final = kümes_opt1
        müştemilat_final = müştemilat_opt1
        kapasite_final = kapasite_opt1
        bakıcı_evi_yapıldı = False
        sonuç_yapılar = []
        
        if bakıcı_evi_hakkı_calc and bakıcı_evi_taban_alanı > 0:
            # Opsiyon 2: Bakıcı evi ile birlikte kapasite
            emsal_for_opt2 = emsal - bakıcı_evi_taban_alanı
            if emsal_for_opt2 >= (self.min_zorunlu_müştemilat_alanı + self.min_işlevsel_kümes_alanı):
                # Bakıcı evi yapılabilir, kümes ve müştemilatı kalan emsale göre yeniden hesapla
                bakıcı_evi_yapıldı = True
                
                kümes_opt2 = emsal_for_opt2 * 0.75
                müştemilat_opt2 = emsal_for_opt2 * 0.25
                if kümes_opt2 <= 120:
                    if müştemilat_opt2 < self.min_zorunlu_müştemilat_alanı:
                        müştemilat_opt2 = self.min_zorunlu_müştemilat_alanı
                        kümes_opt2 = emsal_for_opt2 - müştemilat_opt2
                        if kümes_opt2 < 0: kümes_opt2 = 0
                
                kapasite_opt2 = int(kümes_opt2 * hayvan_yoğunluğu)

                # Final değerleri Opsiyon 2'ye göre güncelle
                kümes_final = kümes_opt2
                müştemilat_final = müştemilat_opt2
                kapasite_final = kapasite_opt2
                sonuç_yapılar.append({"isim": "Bakıcı evi", "alan": bakıcı_evi_taban_alanı, "toplam_insaat": bakıcı_evi_toplam_inşaat})
            # else: Bakıcı evi hakkı var ama (emsal - bakıcı_evi_taban_alanı) yetersiz. Yapılamaz.
            # Bu durumda final değerler Opsiyon 1 olarak kalır.
            
        # Müştemilat detaylarını hesapla
        mustemilat_detaylari = self._hesapla_mustemilat_detaylari(kapasite_final, hayvan_tipi)
            
        sonuç = {
            "arazi_alanı": arazi_alanı, "emsal": emsal, "hayvan_tipi": hayvan_tipi,
            "kümes_alanı": kümes_final,
            "müştemilat_alanı": müştemilat_final,
            "hayvan_kapasitesi": kapasite_final,
            "bakıcı_evi_hakkı": bakıcı_evi_hakkı_calc, # Hak, ilk max kapasiteye göre belirlenir
            "yapılar": sonuç_yapılar,
            "mustemilat_detaylari": mustemilat_detaylari
        }
        
        # Diğer opsiyonel yapıları (bekçi, idari) kalan emsale göre ekle
        emsal_kullanılan_ana_yapılar = kümes_final + müştemilat_final
        if bakıcı_evi_yapıldı:
            emsal_kullanılan_ana_yapılar += bakıcı_evi_taban_alanı
        
        kalan_emsal_for_diger_opsiyonel = emsal - emsal_kullanılan_ana_yapılar

        if kalan_emsal_for_diger_opsiyonel >= self.bekçi_kulübesi_alanı:
            sonuç["yapılar"].append({"isim": "Bekçi kulübesi", "alan": self.bekçi_kulübesi_alanı})
            kalan_emsal_for_diger_opsiyonel -= self.bekçi_kulübesi_alanı
        
        if kalan_emsal_for_diger_opsiyonel >= self.idari_bina_alanı:
            sonuç["yapılar"].append({"isim": "İdari bina", "alan": self.idari_bina_alanı})
        
        # Sonuç metnini hazırla
        sonuç_metni = ""
        if kapasite_final > 0 :
            hayvan_tipi_str = hayvan_tipi.upper().replace('_', ' ')
            if bakıcı_evi_hakkı_calc and bakıcı_evi_yapıldı:
                sonuç_metni = f"TESİS VE BAKICI EVİ YAPILABİLİR ({kapasite_final:,} ADET {hayvan_tipi_str} KAPASİTELİ)".replace(",", ".")
            elif bakıcı_evi_hakkı_calc and not bakıcı_evi_yapıldı:
                sonuç_metni = f"TESİS YAPILABİLİR ({kapasite_final:,} ADET {hayvan_tipi_str} KAPASİTELİ), BAKICI EVİ HAKKI KAZANILIR, ANCAK BAKICI EVİ İÇİN YETERLİ EMSAL ALANI KALMAMIŞTIR".replace(",", ".")
            else: # bakıcı_evi_hakkı_calc is False
                sonuç_metni = f"TESİS YAPILABİLİR ({kapasite_final:,} ADET {hayvan_tipi_str} KAPASİTELİ, BAKICI EVİ HAK DOĞMAZ)".replace(",", ".")
        else: # Bu durum ana fonksiyonda yakalanmalıydı
            sonuç_metni = "TESİS YAPILAMAZ"
            sonuç["açıklama"] = "Kümes için yeterli alan kalmadı veya başlangıç emsali yetersiz."

        sonuç["sonuç"] = sonuç_metni
        return sonuç

# ====== Web Arabirimi Fonksiyonları (rules_config.py ile entegrasyon için) ======

def yumurtaci_tavuk_degerlendir(arazi_buyuklugu_m2: float, su_tahsis_belgesi_var_mi: bool = None, yas_kapali_alanda_mi: bool = None, kullanici_adi: str = "", tarih_saat: str = "", emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre yumurtacı tavuk kümesi kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        su_tahsis_belgesi_var_mi: Su tahsis belgesi var mı?
        yas_kapali_alanda_mi: Parsel YAS kapalı alan sınırları içinde mi?
        kullanici_adi: Kullanıcı adı (opsiyonel)
        tarih_saat: İşlem tarihi (opsiyonel)
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    if yas_kapali_alanda_mi is True and su_tahsis_belgesi_var_mi is False:
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Yeraltı Suyu Koruma Alanında kalan Arazide Su Tahsis Belgesi Zorunluluğu</b><br><br>"
                     "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
                     "Bu tür arazilerde kanatlı hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
                     "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda yumurtacı tavuk tesisi yapımına izin verilememektedir.",
            "kapasite": 0,
            "bakici_evi_hakki": False,
            "hayvan_tipi": "yumurtacı_tavuk",
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2
        }

    hesaplayici = KanatlıHesaplama(emsal_orani)
    sonuc = hesaplayici.hesapla(arazi_buyuklugu_m2, "yumurtacı_tavuk")
    
    # Dönen sonuçlar için okunabilir bir mesaj hazırla
    html_mesaj = _olustur_html_mesaj(sonuc, "YUMURTACI TAVUK TESİSİ DEĞERLENDİRME", emsal_orani)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in sonuc["sonuç"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "kapasite": sonuc.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": sonuc.get("bakıcı_evi_hakkı", False),
        "hayvan_tipi": "yumurtacı_tavuk",
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal", 0),
        "kumes_alani_m2": sonuc.get("kümes_alanı", 0),
        "mustemilat_alani_m2": sonuc.get("müştemilat_alanı", 0)
    }

def etci_tavuk_degerlendir(arazi_buyuklugu_m2: float, su_tahsis_belgesi_var_mi: bool = None, yas_kapali_alanda_mi: bool = None, kullanici_adi: str = "", tarih_saat: str = "", emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre etçi tavuk kümesi kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        su_tahsis_belgesi_var_mi: Su tahsis belgesi var mı?
        yas_kapali_alanda_mi: Parsel YAS kapalı alan sınırları içinde mi?
        kullanici_adi: Kullanıcı adı (opsiyonel)
        tarih_saat: İşlem tarihi (opsiyonel)
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    if yas_kapali_alanda_mi is True and su_tahsis_belgesi_var_mi is False:
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Yeraltı Suyu Koruma Alanında kalan Arazide Su Tahsis Belgesi Zorunluluğu</b><br><br>"
                     "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
                     "Bu tür arazilerde kanatlı hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
                     "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda etçi tavuk tesisi yapımına izin verilememektedir.",
            "kapasite": 0,
            "bakici_evi_hakki": False,
            "hayvan_tipi": "etçi_tavuk",
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        }

    hesaplayici = KanatlıHesaplama(emsal_orani)
    sonuc = hesaplayici.hesapla(arazi_buyuklugu_m2, "etçi_tavuk")
    
    # Dönen sonuçlar için okunabilir bir mesaj hazırla
    html_mesaj = _olustur_html_mesaj(sonuc, "ETÇİ TAVUK (BROİLER) TESİSİ DEĞERLENDİRME", emsal_orani)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in sonuc["sonuç"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "kapasite": sonuc.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": sonuc.get("bakıcı_evi_hakkı", False),
        "hayvan_tipi": "etçi_tavuk",
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal", 0),
        "kumes_alani_m2": sonuc.get("kümes_alanı", 0),
        "mustemilat_alani_m2": sonuc.get("müştemilat_alanı", 0),
    }

def gezen_tavuk_degerlendir(arazi_buyuklugu_m2: float, su_tahsis_belgesi_var_mi: bool = None, yas_kapali_alanda_mi: bool = None, kullanici_adi: str = "", tarih_saat: str = "", emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre serbest dolaşan (gezen) tavuk kümesi kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        su_tahsis_belgesi_var_mi: Su tahsis belgesi var mı?
        yas_kapali_alanda_mi: Parsel YAS kapalı alan sınırları içinde mi?
        kullanici_adi: Kullanıcı adı (opsiyonel)
        tarih_saat: İşlem tarihi (opsiyonel)
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    if yas_kapali_alanda_mi is True and su_tahsis_belgesi_var_mi is False:
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Yeraltı Suyu Koruma Alanında kalan Arazide Su Tahsis Belgesi Zorunluluğu</b><br><br>"
                     "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
                     "Bu tür arazilerde kanatlı hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
                     "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda serbest dolaşan tavuk tesisi yapımına izin verilememektedir.",
            "kapasite": 0,
            "bakici_evi_hakki": False,
            "hayvan_tipi": "serbest_tavuk",
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        }

    hesaplayici = KanatlıHesaplama(emsal_orani)
    sonuc = hesaplayici.hesapla(arazi_buyuklugu_m2, "serbest_tavuk")
    
    # Dönen sonuçlar için okunabilir bir mesaj hazırla
    html_mesaj = _olustur_html_mesaj(sonuc, "SERBEST DOLAŞAN (GEZEN) TAVUK TESİSİ DEĞERLENDİRME", emsal_orani)
    
    # Serbest dolaşan tavuklar için ek bilgileri de ekle
    if sonuc.get("gezinti_alanı_kapasitesi") is not None and sonuc.get("emsal_kapasitesi") is not None:
        ek_bilgiler = (
            f"<hr><b>SERBEST DOLAŞAN TAVUKLAR İÇİN EK BİLGİLER:</b><br>"
            f"Emsalin izin verdiği kapasite: {sonuc['emsal_kapasitesi']:,} adet<br>"
            f"Gezinti alanının izin verdiği kapasite: {sonuc['gezinti_alanı_kapasitesi']:,} adet<br>"
            f"Belirleyici kısıt: {sonuc.get('belirleyici_kısıt', 'belirsiz')}<br>"
            f"Gereken gezinti alanı: {(sonuc['hayvan_kapasitesi'] * 2):,.2f} m²"
        ).replace(",", ".")
        html_mesaj = html_mesaj.replace("<hr>NOT:", f"{ek_bilgiler}<hr>NOT:")
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in sonuc["sonuç"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "kapasite": sonuc.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": sonuc.get("bakıcı_evi_hakkı", False),
        "hayvan_tipi": "serbest_tavuk",
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal", 0),
        "kumes_alani_m2": sonuc.get("kümes_alanı", 0),
        "mustemilat_alani_m2": sonuc.get("müştemilat_alanı", 0),
        "gezinti_alani_kapasitesi": sonuc.get("gezinti_alanı_kapasitesi", 0),
        "emsal_kapasitesi": sonuc.get("emsal_kapasitesi", 0), 
        "belirleyici_kisit": sonuc.get("belirleyici_kısıt", ""),
    }

def hindi_degerlendir(arazi_buyuklugu_m2: float, su_tahsis_belgesi_var_mi: bool = None, yas_kapali_alanda_mi: bool = None, kullanici_adi: str = "", tarih_saat: str = "", emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre hindi kümesi kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        su_tahsis_belgesi_var_mi: Su tahsis belgesi var mı?
        yas_kapali_alanda_mi: Parsel YAS kapalı alan sınırları içinde mi?
        kullanici_adi: Kullanıcı adı (opsiyonel)
        tarih_saat: İşlem tarihi (opsiyonel)
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    if yas_kapali_alanda_mi is True and su_tahsis_belgesi_var_mi is False:
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<b>Yeraltı Suyu Koruma Alanında kalan Arazide Su Tahsis Belgesi Zorunluluğu</b><br><br>"
                     "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
                     "Bu tür arazilerde kanatlı hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
                     "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda hindi tesisi yapımına izin verilememektedir.",
            "kapasite": 0,
            "bakici_evi_hakki": False,
            "hayvan_tipi": "hindi",
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        }

    hesaplayici = KanatlıHesaplama(emsal_orani)
    sonuc = hesaplayici.hesapla(arazi_buyuklugu_m2, "hindi")
    
    # Dönen sonuçlar için okunabilir bir mesaj hazırla
    html_mesaj = _olustur_html_mesaj(sonuc, "HİNDİ TESİSİ DEĞERLENDİRME", emsal_orani)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in sonuc["sonuç"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "kapasite": sonuc.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": sonuc.get("bakıcı_evi_hakkı", False),
        "hayvan_tipi": "hindi",
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal", 0),
        "kumes_alani_m2": sonuc.get("kümes_alanı", 0),
        "mustemilat_alani_m2": sonuc.get("müştemilat_alanı", 0),
    }

def kaz_ordek_degerlendir(arazi_buyuklugu_m2: float, su_tahsis_belgesi_var_mi: bool = None, yas_kapali_alanda_mi: bool = None, kullanici_adi: str = "", tarih_saat: str = "", emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre kaz-ördek çiftliği kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        su_tahsis_belgesi_var_mi: Su tahsis belgesi var mı?
        yas_kapali_alanda_mi: Parsel YAS kapalı alan sınırları içinde mi?
        kullanici_adi: Kullanıcı adı (opsiyonel)
        tarih_saat: İşlem tarihi (opsiyonel)
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    if yas_kapali_alanda_mi is True and su_tahsis_belgesi_var_mi is False:
        yas_mesaji = ("<b>Yeraltı Suyu Koruma Alanında kalan Arazide Su Tahsis Belgesi Zorunluluğu</b><br><br>"
                     "Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) kapalı alan sınırları içerisinde yer almaktadır. "
                     "Bu tür arazilerde kanatlı hayvancılık tesisi yapımı için <b>su tahsis belgesi zorunludur.</b> "
                     "Mevcut durumda su tahsis belgeniz bulunmadığından bu alanda kaz-ördek çiftliği yapımına izin verilememektedir.")
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": yas_mesaji,
            "kapasite": 0,
            "bakici_evi_hakki": False,
            "hayvan_tipi": "kaz", # veya "ördek" veya "kaz-ördek" olarak belirtilebilir
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        }

    hesaplayici = KanatlıHesaplama(emsal_orani)
    sonuc = hesaplayici.hesapla(arazi_buyuklugu_m2, "kaz") # Varsayılan olarak kaz yoğunluğu kullanılır
    
    # Dönen sonuçlar için okunabilir bir mesaj hazırla
    html_mesaj = _olustur_html_mesaj(sonuc, "KAZ-ÖRDEK ÇİFTLİĞİ DEĞERLENDİRME", emsal_orani)
    
    return {
        "izin_durumu": "izin_verilebilir" if "TESİS YAPILAMAZ" not in sonuc["sonuç"] else "izin_verilemez",
        "mesaj": html_mesaj,
        "kapasite": sonuc.get("hayvan_kapasitesi", 0),
        "bakici_evi_hakki": sonuc.get("bakıcı_evi_hakkı", False),
        "hayvan_tipi": "kaz",
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal", 0),
        "kumes_alani_m2": sonuc.get("kümes_alanı", 0),
        "mustemilat_alani_m2": sonuc.get("müştemilat_alanı", 0),
    }

# ====== Yardımcı Fonksiyonlar ======

def _olustur_html_mesaj(sonuc: dict, baslik: str, emsal_orani: float = None) -> str:
    """
    Kanatlı tesisi çıktısını, mantar ve büyükbaş modülündeki gibi tablo ve grid yapısına dönüştürür.
    Mobil ve UX/UI uyumlu, 2 sütunlu HTML tablo şeması ile.
    """
    # Emsal oranı ayarı
    from .constants import EMSAL_ORANI_MARJINAL
    kullanilacak_emsal = emsal_orani if emsal_orani is not None else EMSAL_ORANI_MARJINAL

    # Mobil ve modern stil
    mesaj = """
    <style>
        .kanatli-sonuc {font-family: Arial, sans-serif; max-width: 100%; margin: 0 auto;}
        .kanatli-sonuc h3 {color: #2a388f; margin-bottom: 15px;}
        .kanatli-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .kanatli-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 18px;}
        .kanatli-sonuc th, .kanatli-sonuc td {border: 1px solid #ddd; padding: 8px; font-size: 1em;}
        .kanatli-sonuc th {background-color: #e9eafc;}
        .kanatli-sonuc .ana {background-color: #e3f2fd;}
        .kanatli-sonuc .mustemilat {background-color: #eaf7ea;}
        .kanatli-sonuc .opsiyonel {background-color: #fffbe6;}
        .kanatli-sonuc .ozet {background-color: #f8f9fa;}
        .kanatli-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .kanatli-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .kanatli-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .kanatli-sonuc .notlar {font-size: 0.97em; font-style: italic; margin-top: 16px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;}
        @media (max-width: 600px) {
            .kanatli-sonuc th, .kanatli-sonuc td {font-size: 0.97em;}
            .kanatli-sonuc h3 {font-size: 1.2em;}
        }
    </style>
    <div class="kanatli-sonuc">
    """
    mesaj += f"<h3>{baslik}</h3>"
    mesaj += f"<div class='baslik'>Arazi Bilgileri</div>"
    mesaj += f"<table><tr><th>Arazi</th><th>Emsal (%)</th><th>Emsal Alanı (m²)</th></tr>"
    mesaj += f"<tr><td>{sonuc.get('arazi_alanı', 0):,.2f}</td><td>{kullanilacak_emsal*100:.0f}</td><td>{sonuc.get('emsal', 0):,.2f}</td></tr></table>"

    if "TESİS YAPILAMAZ" in sonuc.get("sonuç", ""):
        mesaj += f'<div class="hata"><b>SONUÇ: TESİS YAPILAMAZ</b><br>'
        if "açıklama" in sonuc:
            mesaj += f"<b>Açıklama:</b> {sonuc['açıklama']}</div>"
    else:
        # Kullanım Dağılımı Tablosu (2 sütun)
        mesaj += f"<div class='baslik'>Yapılar ve Alanlar</div>"
        mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"

        # Zorunlu yapılar ve opsiyoneller
        mesaj += f"<tr class='ana'><td>Kümes</td><td>{sonuc.get('kümes_alanı', 0):,.2f}</td></tr>"
        mesaj += f"<tr class='mustemilat'><td>Zorunlu Müştemilat</td><td>{sonuc.get('müştemilat_alanı', 0):,.2f}</td></tr>"

        # Opsiyonel yapılar (Bakıcı evi, Bekçi kulübesi, İdari bina)
        yapilar_sirali = sorted(
            sonuc.get("yapılar", []),
            key=lambda x: (
                x['isim'] != 'Bakıcı evi',
                x['isim'] != 'Bekçi kulübesi',
                x['isim'] != 'İdari bina'
            )
        )
        for yapı in yapilar_sirali:
            row_class = "opsiyonel"
            mesaj += f"<tr class='{row_class}'><td>{yapı['isim']}</td><td>{yapı['alan']:.2f}</td></tr>"
        mesaj += "</table>"

        # Hayvan kapasitesi ve bakıcı evi durumu grid
        hayvan_tipi_str = sonuc.get('hayvan_tipi', 'Bilinmeyen').replace("_", " ")
        mesaj += f"""
        <div class='baslik'>Kapasite ve Bakıcı Evi</div>
        <table>
          <tr><th>Hayvan Kapasitesi</th><th>Bakıcı Evi Durumu</th></tr>
          <tr>
            <td>{sonuc.get('hayvan_kapasitesi', 0):,} adet {hayvan_tipi_str}</td>
            <td>
        """
        bakıcı_evi_hakkı = sonuc.get("bakıcı_evi_hakkı", False)
        bakıcı_evi_fiilen_yapıldı = any(y['isim'] == 'Bakıcı evi' for y in sonuc.get("yapılar", []))
        if bakıcı_evi_hakkı and bakıcı_evi_fiilen_yapıldı:
            mesaj += "YAPILABİLİR (Hak kazanılmış ve alan yeterli)"
        elif bakıcı_evi_hakkı and not bakıcı_evi_fiilen_yapıldı:
            mesaj += "YAPILAMAZ (Hak kazanılmış ancak mevcut emsal ile yapılamıyor/alan yetersiz)"
        else:
            from .kanatli import KanatlıHesaplama
            hesaplayıcı = KanatlıHesaplama()
            eşik = hesaplayıcı.bakıcı_evi_eşikleri.get(sonuc.get("hayvan_tipi"), "N/A")
            mesaj += f"YAPILAMAZ (Minimum {eşik:,} adet hayvan kapasitesi gerekirken {sonuc.get('hayvan_kapasitesi',0):,} adet var)"
        mesaj += "</td></tr></table>"

        # Sonuç mesajı ve açıklama
        mesaj += f'<div class="basarili"><b>SONUÇ: {sonuc.get("sonuç","")}</b></div>'
        if "açıklama" in sonuc and sonuc["açıklama"]:
            mesaj += f'<div class="notlar"><b>Açıklama:</b> {sonuc["açıklama"]}</div>'

        # Genel özet tablosu
        mesaj += "<div class='baslik'>Genel Özet</div>"
        toplam_kullanilan_emsal = (
            sonuc.get('kümes_alanı', 0)
            + sonuc.get('müştemilat_alanı', 0)
            + sum(y['alan'] for y in yapilar_sirali)
        )
        mesaj += "<table><tr><th>Alan Türü</th><th>Değer (m²)</th></tr>"
        mesaj += f"<tr class='ozet'><td>Arazi Alanı</td><td>{sonuc.get('arazi_alanı', 0):,.2f}</td></tr>"
        mesaj += f"<tr class='ozet'><td>Emsal Alanı</td><td>{sonuc.get('emsal', 0):,.2f}</td></tr>"
        mesaj += f"<tr class='ozet'><td>Kullanılan Alan</td><td>{toplam_kullanilan_emsal:,.2f}</td></tr>"
        kalan_emsal = sonuc.get('emsal', 0) - toplam_kullanilan_emsal
        mesaj += f"<tr class='ozet'><td>Kalan Emsal</td><td>{kalan_emsal:,.2f}</td></tr>"
        mesaj += "</table>"

    mesaj += "<div class='notlar'>"
    mesaj += "<b>NOT:</b> Tüm hesaplamalar emsale dahil alanlar üzerinden yapılmıştır. "
    mesaj += "Gezinti alanları, istinat duvarları gibi emsale dahil olmayan alanlar bu hesaplamalara dahil edilmemiştir."
    mesaj += "</div></div>"
    return mesaj
def yazdir_sonuc(sonuç):
    """Hesaplama sonuçlarını ekrana yazdırır"""
    print("\n" + "=" * 70)
    print(f"ARAZİ BÜYÜKLÜĞÜ: {sonuç['arazi_alanı']:,.2f} m²".replace(",", "."))
    print(f"İZİN VERİLEN EMSAL (%20): {sonuç['emsal']:,.2f} m²".replace(",", "."))
    print("-" * 70)
    
    if "sonuç" in sonuç and sonuç["sonuç"].startswith("TESİS YAPILAMAZ"):
        print("SONUÇ: TESİS YAPILAMAZ")
        if "açıklama" in sonuç:
            print(f"Açıklama: {sonuç['açıklama']}")
    else:
        print("KULLANIM DAĞILIMI:")
        
        # Opsiyonel yapılar
        for yapı in sonuç.get("yapılar", []):
            print(f"- {yapı['isim']}: {yapı['alan']:.2f} m²")
        
        # Zorunlu yapılar
        print(f"- Kümes alanı: {sonuç['kümes_alanı']:,.2f} m²".replace(",", "."))
        print(f"- Zorunlu müştemilat: {sonuç['müştemilat_alanı']:,.2f} m²".replace(",", "."))
        print("-" * 70)
        
        # Serbest dolaşan tavuklar için özel gösterge
        if sonuç['hayvan_tipi'] == "serbest_tavuk":
            print(f"HAYVAN KAPASİTESİ: {sonuç['hayvan_kapasitesi']:,} adet {sonuç['hayvan_tipi'].replace('_', ' ')}".replace(",", "."))
            print(f"EMSALİN İZİN VERDİĞİ KAPASİTE: {sonuç.get('emsal_kapasitesi', 0):,} adet".replace(",", "."))
            print(f"GEZİNTİ ALANININ İZİN VERDİĞİ KAPASİTE: {sonuç.get('gezinti_alanı_kapasitesi', 0):,} adet".replace(",", "."))
            print(f"BELİRLEYİCİ KISIT: {sonuç.get('belirleyici_kısıt', 'belirsiz')}".replace(",", "."))
            
            # Gezinti alanı gereksinimi
            gezinti_alanı_gereksinimi = sonuç['hayvan_kapasitesi'] * 2  # Her tavuk için 2 m²
            print(f"GEREKEN GEZİNTİ ALANI: {gezinti_alanı_gereksinimi:,.2f} m²".replace(",", "."))
        else:
            print(f"HAYVAN KAPASİTESİ: {sonuç['hayvan_kapasitesi']:,} adet {sonuç['hayvan_tipi'].replace('_', ' ')}".replace(",", "."))
        
        print("-" * 70)
        
        # Bakıcı evi durum bilgisi
        bakıcı_evi_var = False
        for yapı in sonuç.get("yapılar", []):
            if yapı["isim"] == "Bakıcı evi":
                bakıcı_evi_var = True
                break
                
        if sonuç["bakıcı_evi_hakkı"] and bakıcı_evi_var:
            print("BAKICI EVİ: YAPILABİLİR (Hak kazanılmış ve alan yeterli)")
        elif sonuç["bakıcı_evi_hakkı"] and not bakıcı_evi_var:
            print("BAKICI EVİ: YAPILAMAZ (Hak kazanılmış ancak alan yetersiz)")
        else:
            eşik = hesaplayıcı.bakıcı_evi_eşikleri[sonuç["hayvan_tipi"]]
            print(f"BAKICI EVİ: YAPILAMAZ (Minimum {eşik:,} adet hayvan kapasitesi gerekirken {sonuç['hayvan_kapasitesi']:,} adet var)".replace(",", "."))
        
        print("-" * 70)
        print(f"SONUÇ: {sonuç['sonuç']}")
        if "açıklama" in sonuç:
            print(f"Açıklama: {sonuç['açıklama']}")

    print("=" * 70)
    print("NOT: Tüm hesaplamalar emsale dahil alanlar üzerinden yapılmıştır.")
    print("Gezinti alanları, istinat duvarları gibi emsale dahil olmayan")
    print("alanlar bu hesaplamalara dahil edilmemiştir.")

def ana_menu():
    """Ana menüyü gösterir ve kullanıcıdan giriş ister"""
    print("=" * 70)
    print("KANATLI HAYVANCILIK TESİSİ EMSAL HESAPLAMA ARACI")
    print("=" * 70)
    print("Bu program, arazi büyüklüğünüze göre kurulabilecek kanatlı")
    print("hayvancılık tesisi kapasitesini ve yapı alanlarını hesaplar.")
    print("-" * 70)
    
    hayvan_tipleri = {
        "1": "yumurtacı_tavuk",
        "2": "etçi_tavuk",
        "3": "hindi",
        "4": "kaz",
        "5": "serbest_tavuk"
    }
    
    print("Lütfen hayvan tipini seçiniz:")
    print("1. Yumurtacı Tavuk (1 m² alanda 6 tavuk)")
    print("2. Etçi Tavuk (1 m² alanda 14 tavuk)")
    print("3. Hindi (1 m² alanda 3 hindi)")
    print("4. Kaz (1 m² alanda 2 kaz)")
    print("5. Serbest Tavuk (1 m² alanda 4 tavuk + 2 m² gezinti alanı)")
    
    hayvan_secim = input("Seçiminiz (1-5): ")
    if hayvan_secim not in hayvan_tipleri:
        print("Hata: Geçersiz seçim. Varsayılan olarak Yumurtacı Tavuk seçildi.")
        hayvan_secim = "1"
    
    hayvan_tipi = hayvan_tipleri[hayvan_secim]
    
    # Arazi büyüklüğünü al
    try:
        arazi_alani = float(input("Arazi büyüklüğünü metrekare olarak giriniz: "))
        if arazi_alani <= 0:
            print("Hata: Arazi büyüklüğü pozitif bir değer olmalıdır.")
            return
    except ValueError:
        print("Hata: Lütfen geçerli bir sayı giriniz.")
        return
    
    # Hesapla ve yazdır
    sonuç = hesaplayıcı.hesapla(arazi_alani, hayvan_tipi)
    yazdir_sonuc(sonuç)
    
    print("\nBaşka bir hesaplama yapmak istiyor musunuz? (e/h)")
    cevap = input()
    if cevap.lower() == "e":
        ana_menu()

def test_senaryolar():
    """Test senaryoları ile programın doğru çalıştığını kontrol eder"""
    print("\n" + "=" * 70)
    print("SERBEST DOLAŞAN TAVUK TESİSİ TEST SENARYOLARI")
    print("=" * 70)
    
    # Senaryo 5.1: EMSALİN ZORUNLU MÜŞTEMİLATA YETMEDİĞİ DURUM
    print("\nSenaryo 5.1: EMSALİN ZORUNLU MÜŞTEMİLATA YETMEDİĞİ DURUM")
    sonuç = hesaplayıcı.hesapla(150, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.2: KÜÇÜK BİR İŞLETME İÇİN YETERLİ EMSAL VE GEZİNTİ ALANI
    print("\nSenaryo 5.2: KÜÇÜK BİR İŞLETME İÇİN YETERLİ EMSAL VE GEZİNTİ ALANI")
    sonuç = hesaplayıcı.hesapla(400, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.3: ORTA ÖLÇEKLİ İŞLETME - GEZİNTİ ALANI KISITI
    print("\nSenaryo 5.3: ORTA ÖLÇEKLİ İŞLETME - GEZİNTİ ALANI KISITI")
    sonuç = hesaplayıcı.hesapla(1200, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.4: GEZİNTİ ALANI KISITINA GÖRE HESAPLANMIŞ ORTA ÖLÇEKLİ İŞLETME
    print("\nSenaryo 5.4: GEZİNTİ ALANI KISITINA GÖRE HESAPLANMIŞ ORTA ÖLÇEKLİ İŞLETME")
    sonuç = hesaplayıcı.hesapla(1800, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.5: BAKICI EVİ HAK EDECEK KAPASİTEYE ULAŞAN TESİS
    print("\nSenaryo 5.5: BAKICI EVİ HAK EDECEK KAPASİTEYE ULAŞAN TESİS")
    sonuç = hesaplayıcı.hesapla(3000, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.8: GEZİNTİ ALANI KISITINA GÖRE TASARLANMIŞ BÜYÜK TESİS
    print("\nSenaryo 5.8: GEZİNTİ ALANI KISITINA GÖRE TASARLANMIŞ BÜYÜK TESİS")
    sonuç = hesaplayıcı.hesapla(10000, "serbest_tavuk")
    yazdir_sonuc(sonuç)
    
    # Senaryo 5.9: ÇOK BÜYÜK ARAZİDE MAKSİMUM KAPASİTELİ TESİS
    print("\nSenaryo 5.9: ÇOK BÜYÜK ARAZİDE MAKSİMUM KAPASİTELİ TESİS")
    sonuç = hesaplayıcı.hesapla(30000, "serbest_tavuk")
    yazdir_sonuc(sonuç)

# ====== Program Ana Girişi ======

if __name__ == "__main__":
    hesaplayıcı = KanatlıHesaplama()
    
    # Test için
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_senaryolar()
    else:
        # Web modül testi
        if len(sys.argv) > 1 and sys.argv[1] == "--web-test":
            print("Kanatlı Hayvancılık Web Modülü Test Edililiyor...")
            test_arazi = 10000  # 10.000 m² test arazisi
            
            # Her bir kanatlı türü için test yapalım
            sonuc1 = yumurtaci_tavuk_degerlendir(test_arazi)
            print(f"Yumurtacı tavuk sonuç: {sonuc1['izin_durumu']}, kapasite: {sonuc1['kapasite']}")
            
            sonuc2 = etci_tavuk_degerlendir(test_arazi)
            print(f"Etçi tavuk sonuç: {sonuc2['izin_durumu']}, kapasite: {sonuc2['kapasite']}")
            
            sonuc3 = gezen_tavuk_degerlendir(test_arazi)
            print(f"Gezen tavuk sonuç: {sonuc3['izin_durumu']}, kapasite: {sonuc3['kapasite']}")
            
            sonuc4 = hindi_degerlendir(test_arazi)
            print(f"Hindi sonuç: {sonuc4['izin_durumu']}, kapasite: {sonuc4['kapasite']}")
            
            sonuc5 = kaz_ordek_degerlendir(test_arazi)
            print(f"Kaz-Ördek sonuç: {sonuc5['izin_durumu']}, kapasite: {sonuc5['kapasite']}")
        else:
            # Normal çalıştırma - ana menüyü göster
            ana_menu()
