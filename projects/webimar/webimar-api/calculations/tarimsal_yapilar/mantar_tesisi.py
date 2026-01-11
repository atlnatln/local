"""
Bu modül, mantar üretim tesisi yapılaşma kurallarını içerir.
"""
import math
import logging

logger = logging.getLogger(__name__)

# Mantar üretim tesisi için sabitler - PHASE 2 DİNAMİK EMSAL SİSTEMİ
DEFAULT_EMSAL_ORANI = 0.20  # %20 varsayılan (dinamik sistem için)
MANTAR_MIN_ARAZI_BUYUKLUGU = 800  # Minimum 800 m² arazi gereksinimi

# Referans değerler (100 kg/gün kapasite için)
MANTAR_REF_KAPASITE_KG_GUN = 100
MANTAR_REF_ARAZI_ALANI_M2 = 7500
MANTAR_REF_YAPI_ALANI_M2 = 1500

# Oda sayısı gereksinimleri
MANTAR_MIN_KULUCKA_ODA_SAYISI = 1
MANTAR_MIN_URETIM_ODA_SAYISI = 2

# Kuluçka ve üretim odaları alanı
MANTAR_KULUCKA_REFERANS_ALAN_M2 = 200  # 100 kg/gün için kuluçka odası alanı (m²)
MANTAR_URETIM_REFERANS_ALAN_M2 = 400   # 100 kg/gün için üretim odası alanı (m²)

# Kapasite kural değişikliği sınırı ve katsayılar
MANTAR_KUCUK_TESIS_KAPASITE_SINIRI_KG_GUN = 25
MANTAR_KURAL_B_ASIL_TESIS_ALANI_CARPANI = 2.0
MANTAR_KURAL_B_KULUCKA_URETIM_ODA_TOPLAM_ALANI_SINIRI_M2 = 250

# Müştemilat tanımları ve büyüme faktörleri - değerleri revize edildi
MANTAR_MUSTEMILAT_TANIMLARI = [
    {"isim": "WC ve duş", "oncelik": 1, "buyume_faktoru": 0.6, "min_alan": 10, "ref_alan": 30, "min_kapasite": 10, "buyume_tipi": "logaritmik"},
    {"isim": "Mantar temizleme ve paketleme odası", "oncelik": 2, "buyume_faktoru": 1.0, "min_alan": 15, "ref_alan": 80, "min_kapasite": 10, "buyume_tipi": "koksel"},
    {"isim": "Soğuk hava deposu", "oncelik": 3, "buyume_faktoru": 0.8, "min_alan": 8, "ref_alan": 50, "min_kapasite": 10, "buyume_tipi": "koksel"},
    {"isim": "İşçi odası", "oncelik": 4, "buyume_faktoru": 0.6, "min_alan": 5, "ref_alan": 40, "min_kapasite": 10, "buyume_tipi": "logaritmik"},
    {"isim": "Malzeme deposu", "oncelik": 5, "buyume_faktoru": 1.0, "min_alan": 12, "ref_alan": 60, "min_kapasite": 10, "buyume_tipi": "koksel"},
    {"isim": "Makine ve kazan dairesi", "oncelik": 6, "buyume_faktoru": 0.8, "min_alan": 10, "ref_alan": 60, "min_kapasite": 10, "buyume_tipi": "logaritmik"},
    {"isim": "İdari büro", "oncelik": 7, "buyume_faktoru": 0.6, "min_alan": 5, "ref_alan": 40, "min_kapasite": 10, "buyume_tipi": "logaritmik"},
    {"isim": "Kompost hazırlama platformu", "oncelik": 8, "buyume_faktoru": 1.2, "min_alan": 30, "ref_alan": 120, "min_kapasite": 20, "buyume_tipi": "koksel"},
    {"isim": "Toprak sterilizasyon odası", "oncelik": 9, "buyume_faktoru": 0.8, "min_alan": 15, "ref_alan": 40, "min_kapasite": 25, "buyume_tipi": "koksel"},
    {"isim": "Pastörizasyon odası", "oncelik": 10, "buyume_faktoru": 0.8, "min_alan": 25, "ref_alan": 60, "min_kapasite": 50, "buyume_tipi": "koksel"},
    {"isim": "Misel ekim odası", "oncelik": 11, "buyume_faktoru": 1.0, "min_alan": 35, "ref_alan": 50, "min_kapasite": 100, "buyume_tipi": "koksel"},
    {"isim": "Ar-Ge laboratuvarı", "oncelik": 12, "buyume_faktoru": 0.6, "min_alan": 50, "ref_alan": 100, "min_kapasite": 500, "buyume_tipi": "koksel"}
]


class MantarTesisiHesaplayici:
    """Mantar üretim tesisi alan ve müştemilat hesaplamaları yapan sınıf"""
    
    def __init__(self, emsal_orani: float = None):
        # PHASE 2 DİNAMİK EMSAL SİSTEMİ
        kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
        self.yapilasma_orani = kullanilacak_emsal_orani  # DİNAMİK EMSAL
        self.min_arazi_buyuklugu = MANTAR_MIN_ARAZI_BUYUKLUGU
        self.ref_kapasite = MANTAR_REF_KAPASITE_KG_GUN
        self.ref_arazi = MANTAR_REF_ARAZI_ALANI_M2
        self.ref_yapi_alani = MANTAR_REF_YAPI_ALANI_M2
        
        self.min_kulucka_oda_sayisi = MANTAR_MIN_KULUCKA_ODA_SAYISI
        self.min_uretim_oda_sayisi = MANTAR_MIN_URETIM_ODA_SAYISI
        
        self.kulucka_ref_alan = MANTAR_KULUCKA_REFERANS_ALAN_M2
        self.uretim_ref_alan = MANTAR_URETIM_REFERANS_ALAN_M2
        
        self.kucuk_tesis_siniri = MANTAR_KUCUK_TESIS_KAPASITE_SINIRI_KG_GUN
        self.kural_b_carpani = MANTAR_KURAL_B_ASIL_TESIS_ALANI_CARPANI
        self.kural_b_alan_siniri = MANTAR_KURAL_B_KULUCKA_URETIM_ODA_TOPLAM_ALANI_SINIRI_M2
        
        self.mustemilat_tanimlari = MANTAR_MUSTEMILAT_TANIMLARI

    def hesapla_kulucka_uretim_alani(self, kapasite):
        """
        Kapasiteye göre kuluçka ve üretim odaları alanını hesaplar
        
        Args:
            kapasite (float): Mantar üretim kapasitesi (kg/gün)
            
        Returns:
            dict: Kuluçka ve üretim odaları ile ilgili bilgiler
        """
        # Kapasite 0 veya None ise minimum değer kullan
        if not kapasite:
            kapasite = 25
        
        oran = kapasite / self.ref_kapasite
        
        # Oda sayıları hesaplama
        if kapasite < 250:
            kulucka_oda_sayisi = self.min_kulucka_oda_sayisi
            uretim_oda_sayisi = self.min_uretim_oda_sayisi
        else:
            # Büyük tesisler için oda sayısı artar
            kulucka_oda_sayisi = max(self.min_kulucka_oda_sayisi, int(oran / 2) + 1)
            uretim_oda_sayisi = max(self.min_uretim_oda_sayisi, int(oran) + 1)
        
        # Alan hesaplama - minimum değerleri garanti et
        kulucka_alani = max(20, self.kulucka_ref_alan * oran)
        uretim_alani = max(40, self.uretim_ref_alan * oran)
        
        # Birim alan hesaplama
        kulucka_birim_alan = kulucka_alani / kulucka_oda_sayisi if kulucka_oda_sayisi > 0 else 0
        uretim_birim_alan = uretim_alani / uretim_oda_sayisi if uretim_oda_sayisi > 0 else 0
        
        toplam_alan = kulucka_alani + uretim_alani
        
        return {
            "kulucka_oda_sayisi": kulucka_oda_sayisi,
            "uretim_oda_sayisi": uretim_oda_sayisi,
            "kulucka_alani": kulucka_alani,
            "uretim_alani": uretim_alani,
            "kulucka_birim_alan": kulucka_birim_alan,
            "uretim_birim_alan": uretim_birim_alan,
            "toplam_alan": toplam_alan
        }

    def hesapla_mustemilat_alanlari(self, kapasite, asil_uretim_alani_referansi: float):
        """
        Kapasiteye ve asıl üretim alanına göre müştemilat alanlarını hesaplar.
        Toplam müştemilat alanını, asıl üretim alanının yaklaşık %50'si olacak şekilde ayarlar.
        Özel müştemilat birimleri için kök bazlı büyüme modeli uygular.
        
        Args:
            kapasite (float): Mantar üretim kapasitesi (kg/gün)
            asil_uretim_alani_referansi (float): Hesaplanan asıl üretim alanı (m²)
            
        Returns:
            dict: Müştemilat bilgileri içeren sözlük
        """
        if not kapasite or kapasite <= 0:
            return {"mustemilat_listesi": [], "toplam_alan": 0}

        oran = kapasite / self.ref_kapasite
        initial_mustemilat_details = []
        toplam_alan_ilk_hesap = 0
        
        # Özel kök bazlı büyüme limitlerini ve parametrelerini tanımla
        koksel_limitler = {
            "WC ve duş": {"baslangic": 10, "max_limit": 30, "buyume_faktoru": 0.3},
            "İdari büro": {"baslangic": 5, "max_limit": 40, "buyume_faktoru": 0.5},
            "İşçi odası": {"baslangic": 5, "max_limit": 60, "buyume_faktoru": 0.5},
            "Ar-Ge laboratuvarı": {"baslangic": 50, "max_limit": 100, "buyume_faktoru": 0.6}
        }

        for mustemilat in self.mustemilat_tanimlari:
            if kapasite >= mustemilat["min_kapasite"]:
                buyume_faktoru = mustemilat["buyume_faktoru"]
                buyume_tipi = mustemilat.get("buyume_tipi", "dogrusal")
                
                # Kök bazlı büyüme fonksiyonu - belirli müştemilatlar için
                if mustemilat["isim"] in koksel_limitler:
                    config = koksel_limitler[mustemilat["isim"]]
                    baslangic = config["baslangic"]
                    max_limit = config["max_limit"]
                    buyume_faktoru = config["buyume_faktoru"]
                    
                    # Kök bazlı büyüme formülü:
                    # baslangic + (max_limit - baslangic) * min(1.0, sqrt(oran * buyume_faktoru))
                    if kapasite <= self.ref_kapasite:
                        # Referans kapasiteye kadar daha hızlı artan bir eğri
                        artis_faktoru = math.sqrt(oran * buyume_faktoru)
                    else:
                        # Referans kapasiteden sonra daha yavaş büyüyen bir eğri
                        artis_faktoru = math.sqrt(1 + math.log(oran, 2) * buyume_faktoru) - 1
                    
                    artis_faktoru = min(1.0, artis_faktoru)  # En fazla 1.0 olabilir
                    hesaplanan_alan = baslangic + (max_limit - baslangic) * artis_faktoru
                    alan = max(baslangic, min(max_limit, hesaplanan_alan))
                
                # Normal büyüme formülleri diğer müştemilatlar için
                elif buyume_tipi == "logaritmik":
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * math.log(oran + 1, 2) * buyume_faktoru)
                elif buyume_tipi == "koksel":
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * (oran ** 0.5) * buyume_faktoru)
                else:
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * oran * buyume_faktoru)
                
                alan = max(mustemilat["min_alan"], hesaplanan_alan)
                
                initial_mustemilat_details.append({
                    "isim": mustemilat["isim"],
                    "original_alan": alan,
                    "min_alan": mustemilat["min_alan"],
                    "oncelik": mustemilat["oncelik"]
                })
                toplam_alan_ilk_hesap += alan

        if toplam_alan_ilk_hesap == 0:
            return {"mustemilat_listesi": [], "toplam_alan": 0}

        # Hedef toplam müştemilat alanını belirle (üretim alanının %50'si)
        hedef_toplam_mustemilat = asil_uretim_alani_referansi * 0.5
        final_mustemilat_list = []
        final_toplam_alan = 0

        # Ölçeklendirme ve son liste oluşturma - değiştirilmedi
        if toplam_alan_ilk_hesap > hedef_toplam_mustemilat and hedef_toplam_mustemilat > 0:
            scaling_factor = hedef_toplam_mustemilat / toplam_alan_ilk_hesap
            initial_mustemilat_details.sort(key=lambda x: x["oncelik"])
            for item_detail in initial_mustemilat_details:
                scaled_alan = item_detail["original_alan"] * scaling_factor
                final_alan_for_item = max(item_detail["min_alan"], scaled_alan)
                final_mustemilat_list.append({
                    "isim": item_detail["isim"],
                    "alan": round(final_alan_for_item, 2),
                    "oncelik": item_detail["oncelik"]
                })
                final_toplam_alan += final_alan_for_item
        else:
            initial_mustemilat_details.sort(key=lambda x: x["oncelik"])
            for item_detail in initial_mustemilat_details:
                final_mustemilat_list.append({
                    "isim": item_detail["isim"],
                    "alan": round(item_detail["original_alan"], 2),
                    "oncelik": item_detail["oncelik"]
                })
                final_toplam_alan += item_detail["original_alan"]

        return {
            "mustemilat_listesi": final_mustemilat_list,
            "toplam_alan": round(final_toplam_alan, 2)
        }

    def hesapla_toplam_yapi_alani(self, kapasite):
        """
        Kapasiteye göre toplam yapı alanını hesaplar
        
        Args:
            kapasite (float): Mantar üretim kapasitesi (kg/gün)
            
        Returns:
            dict: Toplam yapı alanı ve detayları
        """
        odalar = self.hesapla_kulucka_uretim_alani(kapasite)
        kulucka_uretim_alani = odalar["toplam_alan"]
        mustemilat = self.hesapla_mustemilat_alanlari(kapasite, kulucka_uretim_alani)
        if kapasite <= self.kucuk_tesis_siniri and kulucka_uretim_alani < self.kural_b_alan_siniri:
            asil_tesis_alani = kulucka_uretim_alani * self.kural_b_carpani
            uygulanan_kural = "Kural B (düşük kapasite)"
        else:
            asil_tesis_alani = kulucka_uretim_alani
            uygulanan_kural = "Kural A (standart kapasite)"
        toplam_yapi_alani = asil_tesis_alani + mustemilat["toplam_alan"]
        return {
            "asil_tesis_alani": asil_tesis_alani,
            "kulucka_uretim_alani": kulucka_uretim_alani,
            "mustemilat_alani": mustemilat["toplam_alan"],
            "toplam_yapi_alani": toplam_yapi_alani,
            "odalar": odalar,
            "mustemilat": mustemilat,
            "uygulanan_kural": uygulanan_kural
        }

    def hesapla_optimal_kapasite(self, arazi_alani):
        """
        Belirtilen arazi alanı için optimal kapasite hesaplar
        
        Args:
            arazi_alani (float): Arazi büyüklüğü (m²)
            
        Returns:
            float: Optimal kapasite (kg/gün)
        """
        # Arazi çok küçükse direkt 0 döndür
        if arazi_alani < self.min_arazi_buyuklugu:
            return 0
            
        emsal_alani = arazi_alani * self.yapilasma_orani
        
        # İkili arama (binary search) ile optimal kapasite bulunur
        # Daha geniş bir arama aralığı ve daha hassas adımlar kullan
        alt_sinir = 1.0
        ust_sinir = 2000.0  # Üst sınırı artırdık
        optimal_kapasite = 0
        hedef_kullanim_orani = 0.99  # %99 emsal kullanım hedefi
        en_iyi_kullanim_orani = 0
        
        # Binary search ile yaklaşık değer bul
        while alt_sinir <= ust_sinir:
            orta = (alt_sinir + ust_sinir) / 2
            toplam_alan = self.hesapla_toplam_yapi_alani(orta)["toplam_yapi_alani"]
            kullanim_orani = toplam_alan / emsal_alani
            
            if kullanim_orani <= hedef_kullanim_orani:
                # Bu kapasite kabul edilebilir, daha yükseğini dene
                if kullanim_orani > en_iyi_kullanim_orani:
                    optimal_kapasite = orta
                    en_iyi_kullanim_orani = kullanim_orani
                alt_sinir = orta + 0.1  # Daha küçük adımlarla ara
            else:
                # Bu kapasite çok yüksek, daha düşüğünü dene
                ust_sinir = orta - 0.1
    
        # İnce ayar: optimal kapasiteyi küçük adımlarla artırarak maksimuma yaklaştır
        test_kapasite = optimal_kapasite
        while True:
            test_kapasite += 0.5
            test_alan = self.hesapla_toplam_yapi_alani(test_kapasite)["toplam_yapi_alani"]
            if test_alan > emsal_alani:
                break
            optimal_kapasite = test_kapasite
        
        return max(25, math.floor(optimal_kapasite / 5) * 5)

    def hesapla_optimal_kapasite_emsale_gore(self, emsal_hakki):
        """
        Emsal hakkına göre optimal kapasiteyi hesaplar.
        Müştemilat + üretim odaları toplamı emsal hakkını aşmayacak en büyük kapasiteyi bulur.
        """
        if emsal_hakki <= 0:
            return 0
        alt = 1.0
        ust = 2000.0
        optimal = 0
        for _ in range(100):
            mid = (alt + ust) / 2
            toplam_alan = self.hesapla_toplam_yapi_alani(mid)["toplam_yapi_alani"]
            if toplam_alan <= emsal_hakki:
                optimal = mid
                alt = mid
            else:
                ust = mid
        return max(25, math.floor(optimal / 5) * 5)

    def analiz_et(self, arazi_alani, kapasite=None):
        """
        Belirtilen arazi alanı ve kapasiteye göre mantar tesisi analizi yapar
        
        Args:
            arazi_alani (float): Arazi büyüklüğü (m²)
            kapasite (float, optional): Mantar üretim kapasitesi (kg/gün). Belirtilmezse optimal kapasite hesaplanır.
            
        Returns:
            dict: Analiz sonuçlarını içeren sözlük
        """
        # Minimum arazi kontrolü
        if arazi_alani < self.min_arazi_buyuklugu:
            # Detaylı açıklama oluştur - minimum gereksinimler
            min_kulucka_alani = 20  # en küçük boyuttaki kuluçka odası
            min_uretim_alani = 40   # en küçük boyuttaki üretim odaları (2 oda)
            min_mustemilat = 65     # en temel müştemilat için gereken alan
            
            aciklama = f"Mantar üretim tesisi için en az {self.min_arazi_buyuklugu} m² arazi gereklidir. Mevcut arazi: {arazi_alani:.2f} m²"
            aciklama += f"\n\nNeden Minimum {self.min_arazi_buyuklugu} m² Gerekli?"
            aciklama += f"\n- Mantar üretim tesisleri en az 1 kuluçka odası ({min_kulucka_alani} m²) ve 2 üretim odası ({min_uretim_alani} m²) içermelidir."
            aciklama += f"\n- Temel müştemilat alanları (WC, paketleme, soğuk hava deposu vb.) için en az {min_mustemilat} m² gereklidir."
            aciklama += f"\n- Yasal emsal oranı %{self.yapilasma_orani*100:.0f} olduğundan, bu yapılar için minimum {(min_kulucka_alani + min_uretim_alani + min_mustemilat) / self.yapilasma_orani:.0f} m² arazi gereklidir."
            
            if arazi_alani < 500:
                aciklama += f"\n\n{arazi_alani:.0f} m² büyüklüğündeki bir arazide, açık alanda sınırlı miktarda mantar yetiştiriciliği düşünülebilir, ancak kapalı ve kontrollü bir üretim tesisi kurulması mümkün değildir."
            
            return {
                "izin_durumu": "izin_verilemez",
                "sonuc_mesaji": "TESİS YAPILAMAZ",
                "aciklama": aciklama,
                "arazi_alani_m2": arazi_alani,
                "emsal_m2": arazi_alani * self.yapilasma_orani,
                "kapasite_kg_gun": 0,
                "toplam_yapi_alani_m2": 0,
                "hesaplama_kurali": "Yetersiz arazi"
            }
        
        # Emsal alanı hesaplama
        emsal_alani = arazi_alani * self.yapilasma_orani
        
        # Eğer kapasite belirtilmemişse optimal kapasiteyi emsal hakkına göre hesapla
        if kapasite is None:
            kapasite = self.hesapla_optimal_kapasite_emsale_gore(emsal_alani)
            if kapasite <= 0:
                return {
                    "izin_durumu": "izin_verilemez",
                    "sonuc_mesaji": "TESİS YAPILAMAZ",
                    "aciklama": f"Bu arazi için uygun kapasite bulunamadı.",
                    "arazi_alani_m2": arazi_alani,
                    "emsal_m2": emsal_alani,
                    "kapasite_kg_gun": 0,
                    "toplam_yapi_alani_m2": 0,
                    "hesaplama_kurali": "Uygun kapasite bulunamadı"
                }
        # Yapı alanı hesapla
        yapi_alani_hesap = self.hesapla_toplam_yapi_alani(kapasite)
        toplam_yapi_alani = yapi_alani_hesap["toplam_yapi_alani"]
        
        # Arazi ve emsal yeterli mi?
        arazi_yeterli = arazi_alani >= self.min_arazi_buyuklugu
        emsal_yeterli = emsal_alani >= toplam_yapi_alani
        
        # Kalan emsal
        kalan_emsal = max(0, emsal_alani - toplam_yapi_alani)
        
        # Hesaplama kuralı belirleme
        hesaplama_kurali = yapi_alani_hesap["uygulanan_kural"]
        
        # Sonuç
        if arazi_yeterli and emsal_yeterli:
            izin_durumu = "izin_verilebilir"
            sonuc_mesaji = "TESİS YAPILABİLİR"
            aciklama = f"{kapasite:.0f} kg/gün kapasiteli bir mantar üretim tesisi kurulabilir."
            
            if kalan_emsal > 0:
                aciklama += f" Emsal alanının {kalan_emsal:.2f} m²'si kullanılmadan kalmıştır."
        else:
            izin_durumu = "izin_verilemez"
            sonuc_mesaji = "TESİS YAPILAMAZ"
            
            if not arazi_yeterli:
                aciklama = f"Arazi büyüklüğü ({arazi_alani:.2f} m²), mantar üretim tesisi için gereken minimum büyüklüğün ({self.min_arazi_buyuklugu} m²) altındadır."
            else:
                aciklama = f"{kapasite:.0f} kg/gün kapasiteli bir mantar üretim tesisi için gereken {toplam_yapi_alani:.2f} m² yapı alanı, " \
                          f"arazinin emsal dahilinde yapılabilir alanı olan {emsal_alani:.2f} m²'den fazladır."
                
                # Alternatif kapasite önerisi - recursive çağrı yapmadan
                # ÖNEMLİ DEĞİŞİKLİK: Burada kapasite_senaryosu yerine doğrudan optimal kapasiteyi alıyoruz
                alt_kapasite = 0
                # Emsal alanının altında bir kapasite var mı kontrol edelim
                for test_kapasite in range(1, int(kapasite), 5):
                    test_alan = self.hesapla_toplam_yapi_alani(test_kapasite)["toplam_yapi_alani"]
                    if test_alan <= emsal_alani:
                        alt_kapasite = test_kapasite
                    else:
                        break
                
                if alt_kapasite > 0:
                    aciklama += f" Bu arazi için önerilen maksimum kapasite {alt_kapasite:.0f} kg/gün'dür."
                else:
                    gerekli_arazi = toplam_yapi_alani / self.yapilasma_orani
                    aciklama += f" Bu kapasite için en az {gerekli_arazi:.0f} m² arazi gereklidir."
        
        # İki farklı hesaplama yöntemi sonuçlarını hazırla
        kural_a_uygun = emsal_yeterli if kapasite >= 25 else None
        kural_b_uygun = None
        
        # Eğer Kural A uygun değilse veya kapasite 25'in altındaysa, Kural B'yi de kontrol et
        if kapasite < 25 or not kural_a_uygun:
            # Kural B için hesaplama yapalım (düşük kapasite kuralı)
            kural_b_kapasite = min(25, kapasite)
            kural_b_toplam_alan = self.hesapla_toplam_yapi_alani(kural_b_kapasite)["toplam_yapi_alani"]
            kural_b_uygun = emsal_alani >= kural_b_toplam_alan
        # Detaylı analiz sonucunu hazırla
        sonuc = {
            "izin_durumu": izin_durumu,
            "sonuc_mesaji": sonuc_mesaji,
            "aciklama": aciklama,
            "arazi_alani_m2": arazi_alani,
            "emsal_m2": emsal_alani,
            "kapasite_kg_gun": kapasite,
            "toplam_yapi_alani_m2": toplam_yapi_alani,
            "asil_tesis_alani_m2": yapi_alani_hesap["asil_tesis_alani"],
            "kulucka_uretim_alani_m2": yapi_alani_hesap["kulucka_uretim_alani"],
            "mustemilat_alani_m2": yapi_alani_hesap["mustemilat_alani"],
            "kalan_emsal_m2": kalan_emsal,
            "odalar": yapi_alani_hesap["odalar"],
            "mustemilat": yapi_alani_hesap["mustemilat"],
            "hesaplama_kurali": hesaplama_kurali,
            
            # İki farklı hesaplama yöntemi sonuçları
            "hesaplama_yontemleri": {
                "kural_a": {
                    "aciklama": "Oranlama yöntemi (25 kg/gün ve üzeri için)",
                    "kapasite": kapasite,
                    "toplam_yapi_alani": toplam_yapi_alani if kapasite >= 25 else None,
                    "uygun": kural_a_uygun
                },
                "kural_b": {
                    "aciklama": "Düşük kapasite yöntemi (25 kg/gün altı için)",
                    "kapasite": kural_b_kapasite if kapasite < 25 else None,
                    "toplam_yapi_alani": kural_b_toplam_alan if kapasite < 25 else None,
                    "uygun": kural_b_uygun
                }
            }
        }
        
        return sonuc

    def hesapla_kapasite_senaryo(self, arazi_alani):
        """
        Belirtilen arazi alanı için kapasite senaryolarını hesaplar
        
        Args:
            arazi_alani (float): Arazi büyüklüğü (m²)
            
        Returns:
            dict: Kapasite senaryoları
        """
        # Minimum arazi kontrolü
        if arazi_alani < self.min_arazi_buyuklugu:
            return {
                "uygun": False,
                "min_arazi": self.min_arazi_buyuklugu,
                "mevcut_arazi": arazi_alani,
                "mesaj": f"Mantar üretim tesisi için en az {self.min_arazi_buyuklugu} m² arazi gereklidir."
            }
            
        emsal_alani = arazi_alani * self.yapilasma_orani
        
        # 25 kg/gün üzeri için hesaplama (Kural A)
        kural_a_kapasite = self.hesapla_optimal_kapasite(arazi_alani)
        kural_a_yapi_alani = self.hesapla_toplam_yapi_alani(kural_a_kapasite)["toplam_yapi_alani"]
        kural_a_uygun = emsal_alani >= kural_a_yapi_alani
        
        # 25 kg/gün ve altı için hesaplama (Kural B)
        # Alt sınır olarak 1 kg/gün, üst sınır olarak 25 kg/gün test edelim
        kural_b_kapasite = 0
        kural_b_yapi_alani = 0
        
        for test_kapasite in range(1, 26):
            yapi_alani = self.hesapla_toplam_yapi_alani(test_kapasite)["toplam_yapi_alani"]
            if yapi_alani <= emsal_alani:
                kural_b_kapasite = test_kapasite
                kural_b_yapi_alani = yapi_alani
            else:
                break
        
        kural_b_uygun = kural_b_kapasite > 0
        
        # En uygun kapasite seçimi
        if kural_a_uygun and kural_a_kapasite >= kural_b_kapasite:
            en_iyi_kapasite = kural_a_kapasite
            en_iyi_kural = "A"
            kullanim_orani = kural_a_yapi_alani / emsal_alani * 100 if emsal_alani > 0 else 0
        elif kural_b_uygun:
            en_iyi_kapasite = kural_b_kapasite
            en_iyi_kural = "B"
            kullanim_orani = kural_b_yapi_alani / emsal_alani * 100 if emsal_alani > 0 else 0
        else:
            en_iyi_kapasite = 0
            en_iyi_kural = "Hiçbiri"
            kullanim_orani = 0
            
        return {
            "uygun": en_iyi_kapasite > 0,
            "kural_a": {
                "kapasite": kural_a_kapasite,
                "yapi_alani": kural_a_yapi_alani,
                "uygun": kural_a_uygun,
                "mesaj": f"Oranlama yöntemine göre (Kural A) en fazla {kural_a_kapasite:.0f} kg/gün"
            },
            "kural_b": {
                "kapasite": kural_b_kapasite,
                "yapi_alani": kural_b_yapi_alani,
                "uygun": kural_b_uygun,
                "mesaj": f"Düşük kapasite yöntemine göre (Kural B) en fazla {kural_b_kapasite:.0f} kg/gün"
            },
            "en_iyi": {
                "kapasite": en_iyi_kapasite,
                "kural": en_iyi_kural,
                "kullanim_orani": kullanim_orani,
                "mesaj": f"Bu arazi için önerilen kapasite {en_iyi_kapasite:.0f} kg/gün (Kural {en_iyi_kural})"
            }
        }

def _olustur_html_mesaj_mantar(sonuc, emsal_orani: float = None):
    """
    Mantar tesisi hesaplama sonuçlarını HTML formatında sunar
    
    Args:
        sonuc: Hesaplama sonuçlarını içeren sözlük
        emsal_orani: Dinamik emsal oranı (varsayılan: DEFAULT_EMSAL_ORANI)
        
    Returns:
        str: HTML formatında sonuç mesajı
    """
    # Dinamik emsal oranını belirle
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
    
    # CSS stillerini dahil et
    mesaj = """
    <style>
        .mantar-sonuc {font-family: Arial, sans-serif;}
        .mantar-sonuc h3 {color: #3c763d; margin-bottom: 15px;}
        .mantar-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .mantar-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 20px;}
        .mantar-sonuc th, .mantar-sonuc td {border: 1px solid #ddd; padding: 8px; text-align: left;}
        .mantar-sonuc th {background-color: #f2f2f2;}
        .mantar-sonuc .uretim {background-color: #e8f4f8;}
        .mantar-sonuc .mustemilat {background-color: #eaf7ea;}
        .mantar-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .mantar-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .mantar-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}
        .mantar-sonuc .notlar {font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}
    </style>
    <div class="mantar-sonuc">
    """
    
    mesaj += f"<h3>MANTAR ÜRETİM TESİSİ DEĞERLENDİRMESİ</h3>"
    mesaj += f"<p><b>Arazi Büyüklüğü:</b> {sonuc.get('arazi_alani_m2', 0):,.2f} m²<br>"
    mesaj += f"<b>İzin Verilen Toplam Emsal Alanı (%{kullanilacak_emsal_orani*100:.0f}):</b> {sonuc.get('emsal_m2', 0):,.2f} m²</p>"
    
    # Sonuç durumuna göre mesaj türünü belirle
    if sonuc.get("izin_durumu") == "izin_verilemez":
        aciklama = sonuc.get("aciklama", "").replace("\n", "<br>")
        mesaj += f'<div class="hata"><b>SONUÇ: {sonuc.get("sonuc_mesaji")}</b><br>{aciklama}</div>'
    else:
        kalan_emsal = sonuc.get('kalan_emsal_m2', 0)
        mevcut_kapasite = sonuc.get('kapasite_kg_gun', 0)
        min_kalan_emsal = min(10, sonuc.get('emsal_m2', 0) * 0.01)
        # Sadece temel kapasiteyi göster, ek kapasite ve toplam potansiyel kapasite mesajlarını kaldır
        aciklama = f"{mevcut_kapasite:.0f} kg/gün kapasiteli bir mantar üretim tesisi kurulabilir."
        if kalan_emsal > 0:
            aciklama += f" Tüm emsal alanı neredeyse tamamen kullanılmıştır"
        mesaj += f'<div class="basarili"><b>SONUÇ: {sonuc.get("sonuc_mesaji")}</b><br>{aciklama}</div>'
    
    # Ana üretim alanları bilgileri
    mesaj += '<div class="baslik">ÜRETİM YAPILARI</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Yapı</th><th>Sayı</th><th>Alan (m²)</th></tr>'
    
    odalar = sonuc.get("odalar", {})
    
    # Kuluçka odaları
    kulucka_oda_sayisi = odalar.get("kulucka_oda_sayisi", 0)
    kulucka_alani = odalar.get("kulucka_alani", 0)
    
    mesaj += '<tr class="uretim">'
    if kulucka_oda_sayisi == 1:
        mesaj += f'<td>Kuluçka Odası</td><td>1</td><td>{kulucka_alani:.2f}</td>'
    else:
        mesaj += f'<td>Kuluçka Odaları</td><td>{kulucka_oda_sayisi}</td><td>{kulucka_alani:.2f}</td>'
    mesaj += '</tr>'
    
    # Üretim odaları
    uretim_oda_sayisi = odalar.get("uretim_oda_sayisi", 0)
    uretim_alani = odalar.get("uretim_alani", 0)
    
    mesaj += '<tr class="uretim">'
    if uretim_oda_sayisi == 2:
        mesaj += f'<td>Üretim Odaları</td><td>2</td><td>{uretim_alani:.2f}</td>'
    else:
        mesaj += f'<td>Üretim Odaları</td><td>{uretim_oda_sayisi}</td><td>{uretim_alani:.2f}</td>'
    mesaj += '</tr>'
    
    # Toplam asıl tesis alanı
    mesaj += '<tr style="font-weight: bold;">'
    mesaj += f'<td>ANA ÜRETİM ALANI</td><td colspan="2">{sonuc.get("asil_tesis_alani_m2", 0):.2f} m²</td>'
    mesaj += '</tr>'
    mesaj += '</table>'
    
    # Müştemilat alanları tablosu 
    mesaj += '<div class="baslik">MÜŞTEMİLAT ALANLARI</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Müştemilat</th><th>Alan (m²)</th></tr>'
    
    mustemilat_listesi = sonuc.get("mustemilat", {}).get("mustemilat_listesi", [])
    
    for mustemilat in mustemilat_listesi:
        mesaj += '<tr class="mustemilat">'
        mesaj += f'<td>{mustemilat["isim"]}</td><td>{mustemilat["alan"]:.2f}</td>'
        mesaj += '</tr>'
    
    # Toplam müştemilat alanı
    mesaj += '<tr style="font-weight: bold;">'
    mesaj += f'<td>TOPLAM MÜŞTEMİLAT ALANI</td><td>{sonuc.get("mustemilat_alani_m2", 0):.2f} m²</td>'
    mesaj += '</tr>'
    mesaj += '</table>'
    
    # Genel özet
    mesaj += '<div class="baslik">GENEL ÖZET</div>'
    mesaj += '<table>'
    mesaj += '<tr><th>Alan Türü</th><th>Değer (m²)</th></tr>'
    
    arazi_alani = sonuc.get('arazi_alani_m2', 0)
    emsal_alani = sonuc.get('emsal_m2', 0)
    toplam_yapi_alani = sonuc.get('toplam_yapi_alani_m2', 0)
    kalan_emsal = sonuc.get('kalan_emsal_m2', 0)
    
    mesaj += f'<tr><td>Toplam Arazi Alanı</td><td>{arazi_alani:.2f}</td></tr>'
    mesaj += f'<tr><td>Emsal Alanı</td><td>{emsal_alani:.2f}</td></tr>'
    mesaj += f'<tr><td>Kullanılan Yapı Alanı</td><td>{toplam_yapi_alani:.2f}</td></tr>'
    mesaj += f'<tr><td>Kalan Emsal</td><td>{kalan_emsal:.2f}</td></tr>'
    mesaj += '</table>'
    
    # Kapasite büyütme tavsiyesi bölümü kaldırıldı
    # Notlar bölümü
    mesaj += '<div class="notlar">'
    mesaj += '<b>Mantar Üretim Tesisi Planlama Notları:</b><br>'
    mesaj += '- Mantar üretim tesislerinde en az 1 adet kuluçka odası ve 2 adet üretim odası bulunması zorunludur.<br>'
    mesaj += '- 25 kg/gün kapasitenin altındaki tesisler için özel hesaplama kuralı uygulanır: Kuluçka ve üretim odası alanı 250 m²\'nin altında ise bu alanın iki katı asıl tesis alanı olarak hesaplanır.<br>'
    mesaj += '- 25 kg/gün ve üzerindeki tesisler için oranlama yöntemi uygulanır: 100 kg/gün referans alınarak orantısal hesaplama yapılır.<br>'
    mesaj += '- Emsal oranı %{:.0f}\'dir (arazi alanının %{:.0f}\'si kadar yapılaşma izni).<br>'.format(emsal_orani*100 if emsal_orani else DEFAULT_EMSAL_ORANI*100, emsal_orani*100 if emsal_orani else DEFAULT_EMSAL_ORANI*100)
    mesaj += '- Tesisin kapasitesi arttıkça müştemilat alanları ve çeşitliliği de artmalıdır.<br>'
    mesaj += '- Mikro ve küçük ölçekli tesislerde kompost ve misel dışarıdan tedarik edilebilir.<br>'
    mesaj += '- Bu değerlendirme tavsiye niteliğinde olup, kesin başvuru için ilgili kurumlara danışınız.'
    mesaj += '</div>'
    
    mesaj += '</div>'
    return mesaj


def hesapla_mantar_tesisi_detaylari(arazi_buyuklugu_m2, kapasite_kg_gun=None, emsal_orani: float = None):
    """
    Mantar üretim tesisi detaylarını hesaplar
    
    Args:
        arazi_buyuklugu_m2 (float): Arazi büyüklüğü (m²)
        kapasite_kg_gun (float, optional): Mantar üretim kapasitesi (kg/gün). None ise optimal kapasite hesaplanır.
        
    Returns:
        dict: Hesaplama sonuçları
    """
    # PHASE 2 DİNAMİK EMSAL SİSTEMİ  
    hesaplayici = MantarTesisiHesaplayici(emsal_orani)
    sonuc = hesaplayici.analiz_et(arazi_buyuklugu_m2, kapasite_kg_gun)
    
    # HTML mesajını oluştur
    sonuc["mesaj"] = _olustur_html_mesaj_mantar(sonuc, emsal_orani)
    
    return sonuc


# ... [dosyanın başı ve diğer fonksiyonlar aynı kalacak] ...

def mantar_tesisi_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None) -> dict:
    """
    Arazi odaklı mantar tesisi değerlendirmesi yapar
    PATCH: Response tutarlılığı için sadece root seviyede izin_durumu olacak.
    """
    # Arazi büyüklüğü kontrolü
    try:
        arazi_buyuklugu_m2 = float(arazi_bilgileri.get("buyukluk_m2", 0))
        if arazi_buyuklugu_m2 <= 0:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.</div>",
                "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.</div>",
                "kapasite": 0
            }
    except (ValueError, TypeError):
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.</div>",
            "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.</div>",
            "kapasite": 0
        }
    
    # PHASE 2 DİNAMİK EMSAL SİSTEMİ
    hesaplayici = MantarTesisiHesaplayici(emsal_orani)
    if arazi_buyuklugu_m2 < hesaplayici.min_arazi_buyuklugu:
        # Daha detaylı açıklama
        min_kulucka_alani = 20  # en küçük boyuttaki kuluçka odası
        min_uretim_alani = 40   # en küçük boyuttaki üretim odaları (2 oda)
        min_mustemilat = 65     # en temel müştemilat için gereken alan
        
        html_mesaj = f"""
        <div class='alert alert-warning'>
            <h4>Mantar Üretim Tesisi Kurulamaz</h4>
            <p><b>Mevcut Arazi:</b> {arazi_buyuklugu_m2:.0f} m² &nbsp;&nbsp; <b>Gerekli Minimum Arazi:</b> {hesaplayici.min_arazi_buyuklugu} m²</p>
            
            <div style="margin-top:10px;"><b>Neden {hesaplayici.min_arazi_buyuklugu} m² Minimum Gereklidir?</b></div>
            <ul>
                <li>Mantar üretim tesislerinde yasal olarak minimum 3 oda (1 kuluçka + 2 üretim odası) zorunludur.</li>
                <li>En küçük ölçekli tesis için bile odalar ve müştemilat için toplam yaklaşık 125 m² kapalı alan gerekir.</li>
                <li>Emsal oranı %{hesaplayici.yapilasma_orani*100:.0f} olduğundan, bu kapalı alan için en az {hesaplayici.min_arazi_buyuklugu} m² arazi gereklidir.</li>
            </ul>
            
            <div style="margin-top:10px;"><b>Minimum Tesis İçin Gereken Yapı Alanları:</b></div>
            <ul>
                <li>Kuluçka odası: {min_kulucka_alani} m²</li>
                <li>Üretim odaları (2 adet): {min_uretim_alani} m²</li>
                <li>Temel müştemilat (WC, paketleme vb.): {min_mustemilat} m²</li>
                <li>Toplam: {min_kulucka_alani + min_uretim_alani + min_mustemilat} m² yapı alanı</li>
            </ul>
            
            <div style="margin-top:10px;"><b>Öneri:</b></div>
            <p>{arazi_buyuklugu_m2:.0f} m² büyüklüğündeki bir arazide kapalı ve kontrollü mantar üretim tesisi kurmak yasal olarak mümkün değildir. Bu büyüklükteki arazilerde açık tarım alanı, küçük sera veya hobi bahçesi düşünülebilir.</p>
        </div>
        """
        
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": html_mesaj,
            "ana_mesaj": html_mesaj,
            "kapasite": 0,
            "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
            "min_arazi_gereksinimi_m2": hesaplayici.min_arazi_buyuklugu,
            "yetersizlik_orani": hesaplayici.min_arazi_buyuklugu / arazi_buyuklugu_m2
        }
    
    # Kapasite değeri varsa al
    try:
        kapasite_kg_gun = float(yapi_bilgileri.get("kapasite_kg_gun", 0))
        if kapasite_kg_gun <= 0:
            kapasite_kg_gun = None  # Hesaplayıcı optimal değeri hesaplayacak
    except (ValueError, TypeError):
        kapasite_kg_gun = None  # Hesaplayıcı optimal değeri hesaplayacak
    
    # Detaylı analiz
    if kapasite_kg_gun is not None:
        sonuc = hesaplayici.analiz_et(arazi_buyuklugu_m2, kapasite_kg_gun)
    else:
        kapasite_senaryosu = hesaplayici.hesapla_kapasite_senaryo(arazi_buyuklugu_m2)
        if kapasite_senaryosu["uygun"]:
            sonuc = hesaplayici.analiz_et(arazi_buyuklugu_m2, kapasite_senaryosu["en_iyi"]["kapasite"])
        else:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": f"<div class='alert alert-warning'><b>Uygun Kapasite Bulunamadı</b><br>{kapasite_senaryosu['mesaj']}</div>",
                "ana_mesaj": f"<div class='alert alert-warning'><b>Uygun Kapasite Bulunamadı</b><br>{kapasite_senaryosu['mesaj']}</div>",
                "kapasite": 0,
                "arazi_buyuklugu_m2": arazi_buyuklugu_m2
            }
    
    # HTML mesajını oluştur
    html_mesaj = _olustur_html_mesaj_mantar(sonuc, emsal_orani)
    
    # Sadece root seviyede izin_durumu ve ana mesajlar olacak!
    final_response = {
        "izin_durumu": sonuc.get("izin_durumu", "belirsiz"),
        "mesaj": html_mesaj,
        "ana_mesaj": html_mesaj,
        "kapasite": sonuc.get("kapasite_kg_gun", 0),
        "uygulanan_kural": sonuc.get("hesaplama_kurali", ""),
        "arazi_buyuklugu_m2": arazi_buyuklugu_m2,
        "emsal_m2": sonuc.get("emsal_m2", 0),
        "asil_tesis_alani_m2": sonuc.get("asil_tesis_alani_m2", 0),
        "toplam_yapi_alani_m2": sonuc.get("toplam_yapi_alani_m2", 0),
        "kalan_emsal_m2": sonuc.get("kalan_emsal_m2", 0),
        # Alt detaylarda izin_durumu alanı olmayacak!
        "iki_yontem_karsilastirmasi": sonuc.get("hesaplama_yontemleri", {}),
        "hesaplama_kurali_aciklama": (
            "Kural B (25 kg/gün altı için): Kuluçka ve üretim odası alanı 250 m²'nin altında ise bu alanın iki katı asıl tesis alanı olarak hesaplanır." 
            if sonuc.get("kapasite_kg_gun", 0) < 25 
            else "Kural A (25 kg/gün ve üzeri için): 100 kg/gün kapasite referans alınarak oranlama yapılır."
        )
    }
    return final_response

def mantar_degerlendir(data: dict) -> dict:
    """
    Frontend'den gelen parametreleri backend formatına dönüştürerek mantar tesisi değerlendirmesi yapar
    PATCH: Response tutarlılığı için sadece root seviyede izin_durumu olacak.
    """
    try:
        alan_m2 = data.get('alan_m2') or data.get('alan', 0)
        arazi_vasfi = data.get('arazi_vasfi', 'tarım')
        emsal_orani = data.get('emsal_orani', None)
        emsal_turu = data.get('emsalTuru') or data.get('emsal_turu')
        if emsal_orani is None and emsal_turu:
            if emsal_turu in ['mutlak_dikili', 'mutlak', 'dikili']:
                emsal_orani = 0.05
            elif emsal_turu in ['marjinal', 'marjinal_tarim']:
                emsal_orani = 0.20

        arazi_bilgileri = {
            'buyukluk_m2': alan_m2
        }
        yapi_bilgileri = {
            'arazi_vasfi': arazi_vasfi
        }
        result = mantar_tesisi_degerlendir(arazi_bilgileri, yapi_bilgileri, emsal_orani)
        # PATCH: HAM VERİ TEMİZLİK - Standart format, html_mesaj ve detaylar kaldırıldı
        return {
            'success': True,
            'results': {
                'mesaj': result.get('mesaj', ''),
                'ana_mesaj': result.get('mesaj', ''),
                'kapasite': result.get('kapasite', 0),
                'arazi_buyuklugu_m2': result.get('arazi_buyuklugu_m2', 0),
                'emsal_m2': result.get('emsal_m2', 0),
                'toplam_yapi_alani_m2': result.get('toplam_yapi_alani_m2', 0),
                'kalan_emsal_m2': result.get('kalan_emsal_m2', 0),
                'izin_durumu': result.get('izin_durumu', 'izin_verilemez'),
                'uygulanan_kural': result.get('uygulanan_kural', ''),
                'hesaplama_kurali_aciklama': result.get('hesaplama_kurali_aciklama', '')
            },
            'message': 'Hesaplama başarıyla tamamlandı'
        }
    except Exception as e:
        logger.error(f"Mantar tesisi frontend wrapper error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'mesaj': f'Mantar tesisi hesaplama sırasında hata oluştu: {str(e)}'
        }
