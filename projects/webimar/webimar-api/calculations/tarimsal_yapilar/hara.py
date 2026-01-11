"""
At Yetiştiriciliği Tesisi (Hara) Hesaplama Modülü

Bu modül, verilen arazi büyüklüğüne göre at yetiştiriciliği tesisi (hara) kapasitesini,
ahır, padok, manej ve müştemilat alanlarını hesaplar.
Hayvan sağlığı, gelişimi ve refahı gözetilerek minimum 40 boks kuralını uygular.
"""
import math

# Sabit Değerler
EMSAL_ORANI = 0.20  # %20
HARA_MIN_ARAZI_M2 = 1000  # Minimum arazi büyüklüğü (m²) - küçük harasthaneler için uygun hale getirildi (2000'den 1000'e düşürüldü)

# Alan ihtiyaçları (m²/hayvan)
KISRAK_BOKS_ALANI = 16      # Kısrak için 4m x 4m = 16 m²
AYGIR_BOKS_ALANI = 25       # Aygır için 5m x 5m = 25 m²
YAVRULAMA_BOLMESI_ALANI = 25  # Yavrulama bölmesi için 5m x 5m = 25 m²
PADOK_ALANI = 32            # Padok alanı, boksun en az 2 katı
MANEJ_ALANI = 18            # Manej alanı: 3m x 6m = 18 m²

# Minimum değerler - küçük işletmeler için uyarlandı
MIN_BOKS_SAYISI = 10         # Minimum 10 boks şartı (40'tan 10'a düşürüldü)
MALZEME_DEPOSU_ALANI = 30    # Sabit 30 m²

# Diğer yapılar
IDARI_BINA_ALANI = 100       # 100 m²
VETERINER_KLINIGI_ALANI = 40 # 40 m²
KAPALI_MANEJ_ALANI = 800     # 800 m² (isteğe bağlı)

# Köksel Büyüme Sistemi Limitleri (At Yetiştiriciliği için)
HARA_KOKSEL_LIMITLER = {
    "yem_deposu": {
        "max_limit": 250,  # m²
        "buyume_faktoru": 0.75,
        "min_esik": 20  # Bu boks sayısından sonra köksel büyüme
    },
    "gubre_cukuru": {
        "max_limit": 150,  # m²
        "buyume_faktoru": 0.7,
        "min_esik": 15
    },
    "bakici_evi": {
        "max_limit": 150,  # m²
        "buyume_faktoru": 0.8,
        "min_esik": 25
    },
    "malzeme_deposu": {
        "max_limit": 100,  # m²
        "buyume_faktoru": 0.7,
        "min_esik": 20
    },
    "veteriner_klinigi": {
        "max_limit": 100,  # m²
        "buyume_faktoru": 0.8,
        "min_esik": 30
    },
    "kapalı_manej": {
        "max_limit": 2000,  # m²
        "buyume_faktoru": 0.7,
        "min_esik": 50
    }
}

# Müştemilat tanımları ve büyüme faktörleri (modern sistem)
HARA_MUSTEMILAT_TANIMLARI = [
    {"isim": "Bakıcı Evi", "min_alan": 40, "ref_alan": 65, "buyume_faktoru": 0.4, "buyume_tipi": "logaritmik", "max_alan": 150},
    {"isim": "Yem Deposu", "min_alan": 50, "ref_alan": 75, "buyume_faktoru": 0.6, "buyume_tipi": "koksel", "max_alan": 250},
    {"isim": "Gübre Çukuru", "min_alan": 30, "ref_alan": 45, "buyume_faktoru": 0.5, "buyume_tipi": "koksel", "max_alan": 150},
    {"isim": "Malzeme Deposu", "min_alan": 30, "ref_alan": 30, "buyume_faktoru": 0.4, "buyume_tipi": "logaritmik", "max_alan": 100},
    {"isim": "İdari Bina", "min_alan": 80, "ref_alan": 100, "buyume_faktoru": 0.5, "buyume_tipi": "logaritmik", "max_alan": 250},
    {"isim": "Veteriner Kliniği", "min_alan": 40, "ref_alan": 40, "buyume_faktoru": 0.3, "buyume_tipi": "logaritmik", "max_alan": 100},
    {"isim": "Kapalı Manej", "min_alan": 600, "ref_alan": 800, "buyume_faktoru": 0.7, "buyume_tipi": "koksel", "max_alan": 2000}
]


class HaraTesisiHesaplayici:
    """At yetiştiriciliği tesisi (hara) hesaplama sınıfı"""
    def __init__(self, emsal_orani: float = None):
        # Dinamik emsal oranı kullan
        self.emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
        
        # Alan ihtiyaçları (m²/hayvan)
        self.kisrak_boks_alani = KISRAK_BOKS_ALANI
        self.aygir_boks_alani = AYGIR_BOKS_ALANI
        self.yavrulama_bolmesi_alani = YAVRULAMA_BOLMESI_ALANI
        self.padok_alani = PADOK_ALANI
        self.manej_alani = MANEJ_ALANI
        
        # Minimum değerler
        self.min_boks_sayisi = MIN_BOKS_SAYISI
        self.malzeme_deposu = MALZEME_DEPOSU_ALANI
        
        # Müştemilat tanımları
        self.mustemilat_tanimlari = HARA_MUSTEMILAT_TANIMLARI
        self.koksel_limitler = HARA_KOKSEL_LIMITLER
        
        # Referans kapasite değeri
        self.ref_boks_sayisi = 10  # 10 boks referans alınır (küçük işletmeler için)

    def hesapla_optimal_boks_sayisi(self, arazi_alani):
        """
        Belirtilen arazi alanı için optimal boks sayısını hesaplar
        
        Args:
            arazi_alani (float): Arazi büyüklüğü (m²)
            
        Returns:
            int: Optimal boks sayısı
        """
        # Arazi çok küçükse direkt minimum boks sayısını döndür
        if arazi_alani < HARA_MIN_ARAZI_M2:
            return self.min_boks_sayisi
            
        emsal_alani = arazi_alani * self.emsal_orani
        
        # Gerçekçi maksimum sınırlar uygula - çok büyük arazilerde mantıksız büyüklükte tesisler önermeyi engelle
        MAX_BOKS_SAYISI = 1000  # Gerçekçi üst sınır - profesyonel büyük ölçekli tesisler için
        
        # Çok büyük arazilerde (100+ hektar) boks sayısı sınırlaması
        if arazi_alani > 1000000:  # 100 hektar
            ust_sinir = MAX_BOKS_SAYISI
        else:
            ust_sinir = 1000  # Normal araziler için üst sınır
        
        # İkili arama (binary search) ile optimal boks sayısını bulalım
        alt_sinir = self.min_boks_sayisi
        optimal_boks = self.min_boks_sayisi
        hedef_kullanim_orani = 0.99  # %99 emsal kullanım hedefi
        en_iyi_kullanim_orani = 0
        
        while alt_sinir <= ust_sinir:
            orta = (alt_sinir + ust_sinir) // 2
            
            # Bu boks sayısı için yapı alanını hesapla
            test_sonuc = self.hesapla_test(arazi_alani, orta)
            kullanilan_emsal = test_sonuc["toplam_kapali_alan_m2"]
            kullanim_orani = kullanilan_emsal / emsal_alani if emsal_alani > 0 else 0
            
            if kullanim_orani <= hedef_kullanim_orani:
                # Bu boks sayısı kabul edilebilir, daha yükseğini dene
                if kullanim_orani > en_iyi_kullanim_orani:
                    optimal_boks = orta
                    en_iyi_kullanim_orani = kullanim_orani
                alt_sinir = orta + 1
            else:
                # Bu boks sayısı çok yüksek, daha düşüğünü dene
                ust_sinir = orta - 1
        
        # İnce ayar: birer birer artırarak maksimuma yaklaştır
        test_boks = optimal_boks
        while test_boks < MAX_BOKS_SAYISI:  # Maksimum limiti aşmadığını kontrol et
            test_boks += 1
            test_sonuc = self.hesapla_test(arazi_alani, test_boks)
            test_alan = test_sonuc["toplam_kapali_alan_m2"]
            
            if test_alan > emsal_alani:
                break  # Emsal alanını aştık, son uygun değeri kullan
            
            optimal_boks = test_boks  # Hala uygun, kapasiteyi güncelle
            
        return min(optimal_boks, MAX_BOKS_SAYISI)  # Maksimum sınırı aşmamalı

    def hesapla_mustemilat_alani(self, boks_sayisi, ahir_alani):
        """
        Boks sayısı ve ahır alanına göre müştemilat alanlarını hesaplar
        Köksel büyüme sistemi uygulayarak maximum limitler korunur
        
        Args:
            boks_sayisi: Planlanan boks sayısı
            ahir_alani: Hesaplanan ahır alanı (m²)
            
        Returns:
            dict: Hesaplanan müştemilat alanlarını içeren sözlük
        """
        mustemilat_alanlar = []
        toplam_alan = 0
        
        # Büyüme oranı (referans boks sayısına göre)
        oran = boks_sayisi / self.ref_boks_sayisi if boks_sayisi > 0 else 1
        
        # Her müştemilat için köksel büyüme sistemi uygula
        for mustemilat in self.mustemilat_tanimlari:
            buyume_faktoru = mustemilat["buyume_faktoru"]
            buyume_tipi = mustemilat.get("buyume_tipi", "dogrusal")
            
            # Müştemilat adından köksel limit anahtarını oluştur
            anahtar = mustemilat["isim"].lower().replace(" ", "_").replace("ı", "i").replace("ğ", "g").replace("ç", "c").replace("ş", "s").replace("ü", "u").replace("ö", "o")
            
            # Köksel büyüme sistemi kontrolü
            if anahtar in self.koksel_limitler:
                koksel_config = self.koksel_limitler[anahtar]
                max_limit = koksel_config["max_limit"]
                koksel_buyume_faktoru = koksel_config["buyume_faktoru"]
                min_esik = koksel_config["min_esik"]
                
                if boks_sayisi <= min_esik:
                    # Minimum eşiğin altında lineer büyüme
                    if buyume_tipi == "logaritmik":
                        hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * math.log(oran + 1, 2) * buyume_faktoru)
                    elif buyume_tipi == "koksel":
                        hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * (oran ** 0.5) * buyume_faktoru)
                    else:
                        hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * oran * buyume_faktoru)
                else:
                    # Minimum eşiğin üstünde köksel büyüme
                    # Önce eşik kapasiteye kadar lineer büyüme
                    esik_orani = min_esik / self.ref_boks_sayisi
                    if buyume_tipi == "logaritmik":
                        esik_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * math.log(esik_orani + 1, 2) * buyume_faktoru)
                    elif buyume_tipi == "koksel":
                        esik_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * (esik_orani ** 0.5) * buyume_faktoru)
                    else:
                        esik_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * esik_orani * buyume_faktoru)
                    
                    # Eşik üstü için köksel büyüme
                    fazla_oran = (boks_sayisi - min_esik) / self.ref_boks_sayisi
                    if buyume_tipi == "logaritmik":
                        koksel_artis = (mustemilat["ref_alan"] * math.log(fazla_oran + 1, 2) * buyume_faktoru) * (fazla_oran ** koksel_buyume_faktoru)
                    elif buyume_tipi == "koksel":
                        koksel_artis = (mustemilat["ref_alan"] * (fazla_oran ** 0.5) * buyume_faktoru) * (fazla_oran ** koksel_buyume_faktoru)
                    else:
                        koksel_artis = (mustemilat["ref_alan"] * fazla_oran * buyume_faktoru) * (fazla_oran ** koksel_buyume_faktoru)
                    
                    hesaplanan_alan = esik_alan + koksel_artis
                
                # Maximum limit kontrolü
                hesaplanan_alan = min(hesaplanan_alan, max_limit)
                
            else:
                # Köksel büyüme sistemi olmayan müştemilatlar için eski sistem
                if buyume_tipi == "logaritmik":
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * math.log(oran + 1, 2) * buyume_faktoru)
                elif buyume_tipi == "koksel":
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * (oran ** 0.5) * buyume_faktoru)
                else:
                    hesaplanan_alan = mustemilat["min_alan"] + (mustemilat["ref_alan"] * oran * buyume_faktoru)
                
                # Maksimum alanı kontrol et (eğer tanımlanmışsa)
                if "max_alan" in mustemilat:
                    hesaplanan_alan = min(hesaplanan_alan, mustemilat["max_alan"])
            
            # Minimum sınırı kontrol et
            hesaplanan_alan = max(mustemilat["min_alan"], hesaplanan_alan)
            
            alan = round(hesaplanan_alan, 2)
            
            mustemilat_alanlar.append({
                "isim": mustemilat["isim"],
                "alan": alan,
                "tip": "mustemilat" if mustemilat["isim"] not in ["İdari Bina", "Veteriner Kliniği", "Kapalı Manej"] else "opsiyonel"
            })
            
            # İlk 4 müştemilat zorunlu, diğerleri opsiyonel, opsiyonelleri toplam alana dahil etmiyoruz
            if mustemilat["isim"] in ["Bakıcı Evi", "Yem Deposu", "Gübre Çukuru", "Malzeme Deposu"]:
                toplam_alan += alan
        
        return {
            "mustemilat_listesi": mustemilat_alanlar,
            "toplam_zorunlu_alan": toplam_alan
        }

    def hesapla(self, arazi_alani, boks_sayisi=None):
        """
        Ana hesaplama fonksiyonu
        
        Args:
            arazi_alani: Arazi büyüklüğü (m²)
            boks_sayisi: Planlanan boks sayısı (None ise optimal değer hesaplanır)
            
        Returns:
            dict: Hesaplama sonuçlarını içeren sözlük
        """
        # Emsal hesabı
        emsal = arazi_alani * self.emsal_orani
        
        # Çok büyük araziler için alternatif kullanım önerileri
        cok_buyuk_arazi = arazi_alani > 1000000  # 100 hektar üzeri
        
        # Eğer belirtilen boks sayısı yoksa optimal değeri hesapla
        if boks_sayisi is None:
            boks_sayisi = self.hesapla_optimal_boks_sayisi(arazi_alani)
        # Minimum değerden küçükse, minimum değeri kullan
        elif boks_sayisi < self.min_boks_sayisi:
            boks_sayisi = self.min_boks_sayisi
    
        # Standart bokslar için minimum alan hesabı
        # Boks tiplerine göre dağılım
        kisrak_boks_orani = 0.85  # %85 kısrak boksları
        aygir_boks_orani = 0.05   # %5 aygır boksları
        yavrulama_boks_orani = 0.10  # %10 yavrulama bölmeleri
        
        kisrak_boks_sayisi = math.floor(boks_sayisi * kisrak_boks_orani)
        aygir_boks_sayisi = math.floor(boks_sayisi * aygir_boks_orani)
        yavrulama_boks_sayisi = boks_sayisi - kisrak_boks_sayisi - aygir_boks_sayisi
        
        # Alanlara göre hesaplama
        kisrak_bokslari_alani = kisrak_boks_sayisi * self.kisrak_boks_alani
        aygir_bokslari_alani = aygir_boks_sayisi * self.aygir_boks_alani
        yavrulama_bolmeleri_alani = yavrulama_boks_sayisi * self.yavrulama_bolmesi_alani
        
        min_ahir_alani = kisrak_bokslari_alani + aygir_bokslari_alani + yavrulama_bolmeleri_alani
        
        # Modern müştemilat hesaplama
        mustemilat_hesap = self.hesapla_mustemilat_alani(boks_sayisi, min_ahir_alani)
        zorunlu_mustemilat_alani = mustemilat_hesap["toplam_zorunlu_alan"]
        mustemilat_alanlar = mustemilat_hesap["mustemilat_listesi"]  # Burada tanımlama eksikliği var
    
        # Toplam minimum kapalı alan (ahır + zorunlu müştemilat)
        min_toplam_kapali_alan = min_ahir_alani + zorunlu_mustemilat_alani
        
        # Açık alan ihtiyaçları
        min_padok_alani = boks_sayisi * self.padok_alani
        min_manej_alani = boks_sayisi * self.manej_alani
        min_acik_alan = min_padok_alani + min_manej_alani
        
        # Emsal yeterli mi kontrol et
        if emsal < min_toplam_kapali_alan:
            return {
                "sonuc_durumu": "TESİS YAPILAMAZ",
                "aciklama": f"Emsale göre izin verilen {emsal:.2f} m² yapılaşma alanı, minimum kapasite için gerekli olan {min_toplam_kapali_alan:.2f} m²'den azdır.",
                "arazi_alani": arazi_alani,
                "emsal": emsal,
                "min_boks_sayisi": self.min_boks_sayisi,
                "min_ahir_alani": min_ahir_alani,
                "min_toplam_kapali_alan": min_toplam_kapali_alan,
                "boks_sayisi": boks_sayisi
            }
        
        # Açık alan sorunu var mı?
        acik_alan_sorunu = False
        acik_alan_oran = min_acik_alan / arazi_alani
        
        # Arazi büyüklüğüne göre kabul edilebilir açık alan oranı değişir
        # Kabul edilebilir oranları artırdık ve küçük arazilerde toleransı yükselttik
        if arazi_alani <= 50000:  # 5 hektar veya daha küçük
            kabul_edilebilir_oran = 0.60  # %60'a çıkarıldı - önceki: 0.50
        elif arazi_alani <= 200000:  # 5-20 hektar arası
            kabul_edilebilir_oran = 0.70  # %70'e çıkarıldı - önceki: 0.60
        elif arazi_alani <= 1000000:  # 20-100 hektar arası
            kabul_edilebilir_oran = 0.75  # %75'e çıkarıldı - önceki: 0.70
        else:  # 100 hektar üzeri
            kabul_edilebilir_oran = 0.85  # %85'e çıkarıldı - önceki: 0.80
        
        # Sınırda olan durumlar için özel kontrol (%50 ile %55 arası)
        # Bu aralıktaki değerler için uyarı göstermiyoruz
        if 0.50 <= acik_alan_oran <= 0.55:
            acik_alan_sorunu = False  # Sınırda olan durumları sorun yapmıyoruz
        else:
            # Açık alan oranı, kabul edilebilir oranın üzerindeyse sorun var
            acik_alan_sorunu = acik_alan_oran > kabul_edilebilir_oran
        
        # Çok büyük arazilerde (300+ hektar) açık alan sorunu göstermeyelim
        # Bu büyüklükteki arazilerde açık alan yüzdesi değil, toplam alan önemlidir
        if arazi_alani > 3000000:  # 300 hektar üzeri
            acik_alan_sorunu = False
        
        # Toplam yapı alanı hesaplaması
        toplam_zorunlu_alan = min_ahir_alani + zorunlu_mustemilat_alani
        
        # Kalan emsal hesaplaması
        kalan_emsal = emsal - toplam_zorunlu_alan
        
        # Yapilar listesi oluştur
        yapilar = [
            {"isim": "Ahır (Tavla)", "taban_alani": min_ahir_alani, "toplam_alan": min_ahir_alani, "tip": "ana_yapi"}
        ]
        
        # Zorunlu müştemilatları ekle
        for mustemilat in mustemilat_alanlar:
            if mustemilat["tip"] == "mustemilat":
                yapilar.append({
                    "isim": mustemilat["isim"], 
                    "taban_alani": mustemilat["alan"], 
                    "toplam_alan": mustemilat["alan"] * (2 if mustemilat["isim"] == "Bakıcı Evi" else 1),
                    "tip": "mustemilat"
                })
        
        # Opsiyonel yapılar eklenebilir mi?
        ek_yapilar = []
        kullanilan_emsal = toplam_zorunlu_alan
        
        # Opsiyonel yapıları dene
        for mustemilat in mustemilat_alanlar:
            if mustemilat["tip"] == "opsiyonel":
                alan = mustemilat["alan"]
                if kalan_emsal >= alan:
                    ek_yapilar.append({
                        "isim": mustemilat["isim"],
                        "taban_alani": alan,
                        "toplam_alan": alan * (2 if mustemilat["isim"] == "İdari Bina" else 1),
                        "tip": "opsiyonel"
                    })
                    kalan_emsal -= alan
                    kullanilan_emsal += alan
        
        # Tüm yapıları birleştir
        tum_yapilar = yapilar + ek_yapilar
        
        # Sonuç yapısını hazırla
        sonuc = {
            "arazi_alani_m2": arazi_alani,
            "emsal_m2": emsal,
            "boks_sayisi": boks_sayisi,
            "ahir_alani_m2": min_ahir_alani,
            "toplam_kapali_alan_m2": kullanilan_emsal,
            "padok_alani_m2": min_padok_alani,
            "manej_alani_m2": min_manej_alani,
            "toplam_acik_alan_m2": min_acik_alan,
            "yapilar": tum_yapilar,
            "kalan_emsal_m2": kalan_emsal,
            "acik_alan_sorunu": acik_alan_sorunu,
            "acik_alan_oran": acik_alan_oran,
            "cok_buyuk_arazi": cok_buyuk_arazi,
            "boks_detaylari": {
                "kisrak_boks_sayisi": kisrak_boks_sayisi,
                "aygir_boks_sayisi": aygir_boks_sayisi,
                "yavrulama_boks_sayisi": yavrulama_boks_sayisi,
                "kisrak_bokslari_alani_m2": kisrak_bokslari_alani,
                "aygir_bokslari_alani_m2": aygir_bokslari_alani,
                "yavrulama_bolmeleri_alani_m2": yavrulama_bolmeleri_alani
            }
        }
        
        # Açık alan sorunu varsa uyarı mesajı
        if acik_alan_sorunu:
            sonuc["sonuc_durumu"] = "TESİS PLANLAMASI UYGUNSUZ"
            
            # Arazi büyüklüğüne göre daha açıklayıcı mesajlar
            if arazi_alani > 500000:  # 50 hektar üzeri
                sonuc["aciklama"] = f"Bu arazi büyüklüğünde {boks_sayisi} boks kapasiteli hara tesisi kurulabilir, " \
                                 f"ancak dikkat edilmesi gereken husus: toplam açık alan ihtiyacı ({min_acik_alan:.2f} m²) " \
                                 f"arazinin %{acik_alan_oran*100:.1f}'ini kaplayacaktır. " \
                                 f"Boks sayısını azaltarak veya padok/manej alanlarını optimize ederek daha dengeli bir yerleşim planı oluşturulabilir."
            else:
                sonuc["aciklama"] = f"Bu arazi büyüklüğünde emsal dahilinde {boks_sayisi} boks ve zorunlu müştemilatlar için alan sağlanabilse de, " \
                                 f"toplam açık alan ihtiyacı ({min_acik_alan:.2f} m²) arazinin %{acik_alan_oran*100:.1f}'ini kaplayacaktır. " \
                                 f"Bu durum, at refahı açısından sağlıklı bir tesis işleyişi için uygun değildir."
        else:
            # Çok büyük araziler için özel açıklamalar ekleme
            if cok_buyuk_arazi:
                sonuc["sonuc_durumu"] = f"TESİS YAPILABİLİR (ÇOK BÜYÜK ARAZİ)"
                arazi_hektar = arazi_alani / 10000
                
                sonuc["aciklama"] = f"Bu {arazi_hektar:.1f} hektarlık çok büyük arazi için önerilen optimal hara kapasitesi {boks_sayisi} boksdur. " \
                                 f"Böyle büyük bir arazi için ek önerilerimiz:\n\n" \
                                 f"1) Ana hara tesisi (yaklaşık {boks_sayisi} boks kapasiteli) yanında birden fazla bağlı ünite kurabilirsiniz.\n" \
                                 f"2) Arazinin bir kısmını yarış pisti, açık etkinlik alanları gibi rekreasyon alanlarına ayırabilirsiniz.\n" \
                                 f"3) Arazinin bir bölümünü doğal otlak veya mera alanı olarak bırakabilirsiniz.\n" \
                                 f"4) Alternatif tarım alanları oluşturabilir veya doğal yaşam alanları geliştirebilirsiniz."
            else:
                # Opsiyonel yapılar eklendiyse bildir
                if ek_yapilar:
                    ek_yapi_isimleri = ", ".join([yapi["isim"] for yapi in ek_yapilar])
                    sonuc["sonuc_durumu"] = f"TESİS YAPILABİLİR ({boks_sayisi} BOKS KAPASİTELİ HARA)"
                    
                    # Kalan emsal çok az ise optimum kullanım mesajı
                    if kalan_emsal < emsal * 0.01:  # %1'den az kalan emsal
                        sonuc["aciklama"] = f"Bu arazide maksimum verimlilik ile {boks_sayisi} boks kapasiteli bir hara tesisi kurulabilir. " \
                                        f"Ek olarak {ek_yapi_isimleri} yapıları da inşa edilebilir. " \
                                        f"Emsal alanı neredeyse tamamen kullanılmıştır (kalan: {kalan_emsal:.2f} m²)."
                    else:
                        sonuc["aciklama"] = f"Bu arazide {boks_sayisi} boks kapasiteli bir hara tesisi kurulabilir. " \
                                        f"Ek olarak {ek_yapi_isimleri} yapıları da inşa edilebilir. " \
                                        f"Toplam {kalan_emsal:.2f} m² emsal alanı kullanılmadan kalmıştır."
                else:
                    sonuc["sonuc_durumu"] = f"TESİS YAPILABİLİR ({boks_sayisi} BOKS KAPASİTELİ HARA)"
                    
                    # Kalan emsal çok az ise optimum kullanım mesajı
                    if kalan_emsal < emsal * 0.01:  # %1'den az kalan emsal
                        sonuc["aciklama"] = f"Bu arazide maksimum verimlilik ile {boks_sayisi} boks kapasiteli bir hara tesisi kurulabilir. " \
                                        f"Emsal alanı neredeyse tamamen kullanılmıştır (kalan: {kalan_emsal:.2f} m²)."
                    else:
                        sonuc["aciklama"] = f"Bu arazide {boks_sayisi} boks kapasiteli bir hara tesisi kurulabilir. " \
                                        f"Toplam {kalan_emsal:.2f} m² emsal alanı ek yapılar için kullanılabilir."
        
        return sonuc

    def hesapla_test(self, arazi_alani, boks_sayisi):
        """
        Boks sayısına göre emsal alanı kullanımını test eder
        (hesapla metodunun sadece alan hesaplamalarını yapan versiyonu)
        
        Args:
            arazi_alani: Arazi büyüklüğü (m²)
            boks_sayisi: Test edilecek boks sayısı
            
        Returns:
            dict: Test sonuçları
        """
        # Emsal hesabı
        emsal = arazi_alani * self.emsal_orani
        
        # Boks tiplerini dağıt
        kisrak_boks_orani = 0.85  # %85 kısrak boksları
        aygir_boks_orani = 0.05   # %5 aygır boksları
        yavrulama_boks_orani = 0.10  # %10 yavrulama bölmeleri
        
        kisrak_boks_sayisi = math.floor(boks_sayisi * kisrak_boks_orani)
        aygir_boks_sayisi = math.floor(boks_sayisi * aygir_boks_orani)
        yavrulama_boks_sayisi = boks_sayisi - kisrak_boks_sayisi - aygir_boks_sayisi
        
        # Alanlara göre hesaplama
        kisrak_bokslari_alani = kisrak_boks_sayisi * self.kisrak_boks_alani
        aygir_bokslari_alani = aygir_boks_sayisi * self.aygir_boks_alani
        yavrulama_bolmeleri_alani = yavrulama_boks_sayisi * self.yavrulama_bolmesi_alani
        
        min_ahir_alani = kisrak_bokslari_alani + aygir_bokslari_alani + yavrulama_bolmeleri_alani
        
        # Modern müştemilat hesaplama
        mustemilat_hesap = self.hesapla_mustemilat_alani(boks_sayisi, min_ahir_alani)
        zorunlu_mustemilat_alani = mustemilat_hesap["toplam_zorunlu_alan"]
        
        # Toplam minimum kapalı alan (ahır + zorunlu müştemilat)
        toplam_zorunlu_alan = min_ahir_alani + zorunlu_mustemilat_alani
        
        # Açık alan ihtiyaçları
        min_padok_alani = boks_sayisi * self.padok_alani
        min_manej_alani = boks_sayisi * self.manej_alani
        min_acik_alan = min_padok_alani + min_manej_alani
        
        # Toplam yapı alanı hesaplaması
        kullanilan_emsal = toplam_zorunlu_alan
        
        # Opsiyonel yapılar için kalan emsal
        kalan_emsal = emsal - toplam_zorunlu_alan
        
        # Opsiyonel yapıları ekle
        mustemilat_alanlar = mustemilat_hesap["mustemilat_listesi"]
        for mustemilat in mustemilat_alanlar:
            if mustemilat["tip"] == "opsiyonel":
                alan = mustemilat["alan"]
                if kalan_emsal >= alan:
                    kalan_emsal -= alan
                    kullanilan_emsal += alan
        
        return {
            "toplam_kapali_alan_m2": kullanilan_emsal,
            "kalan_emsal_m2": kalan_emsal
        }

def _olustur_html_mesaj_hara(sonuc, emsal_orani: float = None):
    kullanilacak_emsal = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    mesaj = """
    <style>
        .hara-sonuc {font-family: Arial, sans-serif; max-width: 100%; margin: 0 auto;}
        .hara-sonuc h3 {color: #2e7d32; margin-bottom: 15px;}
        .hara-sonuc .baslik {font-weight: bold; margin-top: 15px; margin-bottom: 8px;}
        .hara-sonuc table {border-collapse: collapse; width: 100%; margin-bottom: 18px;}
        .hara-sonuc th, .hara-sonuc td {border: 1px solid #ddd; padding: 8px; font-size: 1em;}
        .hara-sonuc th {background-color: #e9eafc;}
        .hara-sonuc .ana {background-color: #e3f2fd;}
        .hara-sonuc .mustemilat {background-color: #eaf7ea;}
        .hara-sonuc .opsiyonel {background-color: #fffbe6;}
        .hara-sonuc .ozet {background-color: #f8f9fa;}
        .hara-sonuc .uyari {color: #856404; background-color: #fff3cd; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .hara-sonuc .basarili {color: #155724; background-color: #d4edda; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .hara-sonuc .hata {color: #721c24; background-color: #f8d7da; padding: 8px; border-radius: 4px; margin: 10px 0;}
        .hara-sonuc .notlar {font-size: 0.97em; font-style: italic; margin-top: 16px; padding: 8px; background-color: #f8f9fa; border-radius: 4px;}
        @media (max-width: 600px) {
            .hara-sonuc th, .hara-sonuc td {font-size: 0.97em;}
            .hara-sonuc h3 {font-size: 1.2em;}
        }
    </style>
    <div class="hara-sonuc">
    """
    mesaj += f"<h3>AT YETİŞTİRİCİLİĞİ TESİSİ (HARA) DEĞERLENDİRME</h3>"
    mesaj += f"<div class='baslik'>Arazi Bilgileri</div>"
    mesaj += f"<table><tr><th>Arazi</th><th>Emsal (%)</th><th>Emsal Alanı (m²)</th></tr>"
    mesaj += f"<tr><td>{sonuc.get('arazi_alani_m2', 0):,.2f}</td><td>{kullanilacak_emsal*100:.0f}</td><td>{sonuc.get('emsal_m2', 0):,.2f}</td></tr></table>"

    # Sonuç mesajı
    sonuc_durumu = sonuc.get("sonuc_durumu", "")
    if "YAPILAMAZ" in sonuc_durumu:
        mesaj += f'<div class="hata"><b>SONUÇ: {sonuc_durumu}</b><br>{sonuc.get("aciklama", "")}</div>'
    elif "UYGUNSUZ" in sonuc_durumu:
        mesaj += f'<div class="uyari"><b>SONUÇ: {sonuc_durumu}</b><br>{sonuc.get("aciklama", "")}</div>'
    elif "ÇOK BÜYÜK ARAZİ" in sonuc_durumu:
        aciklama = sonuc.get("aciklama", "").replace("\n\n", "</p><p>").replace("\n", "<br>")
        mesaj += f'<div class="uyari"><b>SONUÇ: {sonuc_durumu}</b><br><p>{aciklama}</p></div>'
    else:
        mesaj += f'<div class="basarili"><b>SONUÇ: {sonuc_durumu}</b><br>{sonuc.get("aciklama", "")}</div>'

    # Yapılar ve alanlar tablosunu ikiye böl
    ana_yapilar = [y for y in sonuc.get("yapilar", []) if y.get("tip") == "ana_yapi"]
    mustemilatlar = [y for y in sonuc.get("yapilar", []) if y.get("tip") == "mustemilat"]

    mesaj += f"<div class='baslik'>Ana Yapı</div>"
    mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"
    for yapi in ana_yapilar:
        mesaj += f"<tr class='ana'><td>{yapi.get('isim','')}</td><td>{yapi.get('taban_alani',0):,.2f}</td></tr>"
    mesaj += "</table>"

    # Detaylı hesaplama tablosu (Ana Yapı tablosunun hemen altında)
    mesaj += "<div class='baslik'>Detaylı Hesaplama</div>"
    boks_detay = sonuc.get('boks_detaylari', {})
    mesaj += "<table><tr><th>Boks Türü</th><th>Adet</th><th>Alan (m²)</th></tr>"
    mesaj += f"<tr><td>Kısrak Boksu</td><td>{boks_detay.get('kisrak_boks_sayisi',0)}</td><td>{boks_detay.get('kisrak_bokslari_alani_m2',0):,.2f}</td></tr>"
    mesaj += f"<tr><td>Aygır Boksu</td><td>{boks_detay.get('aygir_boks_sayisi',0)}</td><td>{boks_detay.get('aygir_bokslari_alani_m2',0):,.2f}</td></tr>"
    mesaj += f"<tr><td>Yavrulama Bölmesi</td><td>{boks_detay.get('yavrulama_boks_sayisi',0)}</td><td>{boks_detay.get('yavrulama_bolmeleri_alani_m2',0):,.2f}</td></tr>"
    mesaj += "</table>"

    mesaj += f"<div class='baslik'>Müştemilatlar</div>"
    mesaj += "<table><tr><th>Yapı</th><th>Alan (m²)</th></tr>"
    for yapi in mustemilatlar:
        mesaj += f"<tr class='mustemilat'><td>{yapi.get('isim','')}</td><td>{yapi.get('taban_alani',0):,.2f}</td></tr>"
    mesaj += "</table>"

    # Açık alanlar tablosu
    mesaj += "<div class='baslik'>Açık Alanlar</div>"
    mesaj += "<table><tr><th>Alan</th><th>Değer (m²)</th></tr>"
    mesaj += f"<tr class='acik-alan'><td>Padok</td><td>{sonuc.get('padok_alani_m2', 0):,.2f}</td></tr>"
    mesaj += f"<tr class='acik-alan'><td>Manej</td><td>{sonuc.get('manej_alani_m2', 0):,.2f}</td></tr>"
    mesaj += f"<tr class='acik-alan'><td>Toplam Açık Alan</td><td>{sonuc.get('toplam_acik_alan_m2', 0):,.2f}</td></tr>"
    mesaj += "</table>"

    # Açık alan oranı ve uyarı
    if sonuc.get("acik_alan_sorunu", False):
        arazi_alani = sonuc.get('arazi_alani_m2', 0)
        acik_alan_oran = sonuc.get("acik_alan_oran", 0)
        if 0.50 <= acik_alan_oran <= 0.55:
            pass
        elif arazi_alani > 500000:
            mesaj += f'<div class="uyari"><b>ÖNERİ:</b> Açık alanlar (padok ve manej) arazinin %{acik_alan_oran*100:.1f}\'ini kaplıyor. Çok büyük arazinizde ({arazi_alani/10000:.1f} hektar) bu oran kabul edilebilir olmakla birlikte, açık alan dağılımını optimize etmenizi öneririz.</div>'
        elif acik_alan_oran > 0.65:
            mesaj += f'<div class="uyari"><b>UYARI:</b> Açık alanlar (padok ve manej) arazinin oldukça büyük bir kısmını (%{acik_alan_oran*100:.1f}) kaplıyor. Açık alanların daha verimli kullanılması için padok ve manej yerleşimini optimize etmenizi öneririz.</div>'

    # Genel özet tablosu (en altta)
    mesaj += "<div class='baslik'>Genel Özet</div>"
    toplam_kullanilan_emsal = sonuc.get('toplam_kapali_alan_m2', 0)
    mesaj += "<table><tr><th>Alan Türü</th><th>Değer (m²)</th></tr>"
    mesaj += f"<tr class='ozet'><td>Arazi Alanı</td><td>{sonuc.get('arazi_alani_m2', 0):,.2f}</td></tr>"
    mesaj += f"<tr class='ozet'><td>Emsal Alanı</td><td>{sonuc.get('emsal_m2', 0):,.2f}</td></tr>"
    mesaj += f"<tr class='ozet'><td>Kullanılan Alan</td><td>{toplam_kullanilan_emsal:,.2f}</td></tr>"
    kalan_emsal = sonuc.get('kalan_emsal_m2', 0)
    mesaj += f"<tr class='ozet'><td>Kalan Emsal</td><td>{kalan_emsal:,.2f}</td></tr>"
    mesaj += "</table>"

    # Notlar bölümü
    mesaj += "<div class='notlar'>"
    mesaj += "<b>NOT:</b> Tüm hesaplamalar emsale dahil alanlar üzerinden yapılmıştır. Padok ve manej gibi açık alanlar emsale dahil değildir.<br>"
    mesaj += "- Minimum 40 boks kapasitesi şartı aranmaktadır.<br>"
    mesaj += "- Boks alanları: Kısrak için 16 m² (4x4m), Aygır için 25 m² (5x5m), Yavrulama bölmesi için 25 m² (5x5m).<br>"
    mesaj += "- Padok alanı, at başına en az boks alanının 2 katı (32m²) olmalıdır.<br>"
    mesaj += "- Manej alanı, at başına en az 18 m² (3x6m) olmalıdır.<br>"
    mesaj += "- Bakıcı evi ahır alanının %6-7'si, yem deposu %7-8'i, gübre çukuru %4-5'i olarak hesaplanmalıdır.<br>"
    mesaj += "- Tesiste bulunan hayvanların günlük en az 8 saat açık alanda hareket imkanı bulması önerilir.<br>"
    mesaj += "- Bu değerlendirme ön bilgilendirme amaçlıdır ve resmi bir belge niteliği taşımaz."
    mesaj += "</div></div>"
    return mesaj


def hara_kurali(arazi_buyuklugu_m2):
    """
    Hara (at yetiştiriciliği tesisi) için arazi büyüklüğü ve diğer koşulları kontrol eden kural
    
    Args:
        arazi_buyuklugu_m2: Arazi büyüklüğü (m²)
        
    Returns:
        dict: Kontrol sonuçlarını içeren sözlük
    """
    sonuc = {
        "izin_durumu": None,
        "ana_mesaj": None,
        "detay_mesaj_bakici_evi": "",
        "bilgi_mesaji_bakici_evi_hara": "",
        "uyari_mesaji_ozel_durum": "",
    }

    try:
        # Arazi büyüklüğünü güvenli bir şekilde float'a çevir
        try:
            arazi_buyuklugu_m2 = float(arazi_buyuklugu_m2)
        except (ValueError, TypeError):
            arazi_buyuklugu_m2 = 0

        # Minimum arazi büyüklüğü kontrolü
        if arazi_buyuklugu_m2 < HARA_MIN_ARAZI_M2:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["ana_mesaj"] = f"Hara (at üretimi/yetiştiriciliği tesisi) kurulumu için araziniz yeterli büyüklükte değildir. " \
                                f"Minimum {HARA_MIN_ARAZI_M2:,} m² arazi gereklidir. Mevcut arazi: {arazi_buyuklugu_m2:,} m²"
            sonuc["uyari_mesaji_ozel_durum"] = "Hara tesisleri için MINIMUM 4 dekarlık arazi gereklidir."
            return sonuc

        # Minimum arazi büyüklüğü yeterli, tam hesaplama için yönlendir
        kullanilacak_emsal_orani = EMSAL_ORANI
        hesaplayici = HaraTesisiHesaplayici(kullanilacak_emsal_orani)
        hesaplama_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2)
        
        html_mesaj = _olustur_html_mesaj_hara(hesaplama_sonucu, kullanilacak_emsal_orani)
        
        sonuc["izin_durumu"] = "izin_verilebilir" if "YAPILABİLİR" in hesaplama_sonucu.get("sonuc_durumu", "") else "izin_verilemez"
        sonuc["ana_mesaj"] = html_mesaj
        sonuc["detay_mesaj_bakici_evi"] = ""
        sonuc["bilgi_mesaji_bakici_evi_hara"] = "Hara tesislerinde bakıcı evi, müştemilat olarak dahil edilir."
        
        return sonuc
    except Exception as e:
        # Hata durumunda güvenli bir sonuç döndür
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = f"Hesaplama sırasında bir hata oluştu: {str(e)}"
        sonuc["uyari_mesaji_ozel_durum"] = "Lütfen sistem yöneticisiyle iletişime geçiniz."
        return sonuc


def hara_tesisi_degerlendir(arazi_bilgileri: dict, yapi_bilgileri: dict, emsal_orani: float = None) -> dict:
    """
    Arazi bilgilerine göre hara tesisi değerlendirmesi yapar
    
    Args:
        arazi_bilgileri: Arazi bilgilerini içeren sözlük
        yapi_bilgileri: Yapı bilgilerini içeren sözlük
        emsal_orani: Dinamik emsal oranı (opsiyonel)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    # Dinamik emsal oranını kullan
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else EMSAL_ORANI
    # Arazi büyüklüğü kontrolü
    try:
        # Frontend'den alan_m2, arazi_alani_m2 veya buyukluk_m2 alanından veriyi al
        arazi_buyuklugu_m2 = float(
            arazi_bilgileri.get("arazi_alani_m2") or 
            arazi_bilgileri.get("alan_m2") or 
            arazi_bilgileri.get("buyukluk_m2") or 0
        )
        if arazi_buyuklugu_m2 <= 0:
            return {
                "izin_durumu": "izin_verilemez",
                "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.</div>",
                "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü geçerli bir değer değil. Pozitif bir sayı girmelisiniz.</div>",
            }
    except (ValueError, TypeError):
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.</div>",
            "ana_mesaj": "<div class='alert alert-danger'><b>Geçersiz Arazi Büyüklüğü</b><br>Belirtilen arazi büyüklüğü sayısal bir değer değil. Geçerli bir sayı girmelisiniz.</div>",
        }
    
    # YAS ve su tahsis belgesi kontrolü - Daha güvenli hale getirildi
    try:
        su_tahsis_belgesi_var_mi = str(arazi_bilgileri.get("su_tahsis_belgesi", "false")).lower() == "true"
        yas_kapali_alanda_mi = arazi_bilgileri.get("yas_kapali_alan_durumu") == "içinde"
    except (TypeError, AttributeError):
        # Varsayılan olarak en güvenli değerleri kullan
        su_tahsis_belgesi_var_mi = False
        yas_kapali_alanda_mi = False
    
    if yas_kapali_alanda_mi and not su_tahsis_belgesi_var_mi:
        # GEÇICI ÇÖZÜM: Su tahsis belgesi uyarısını göster ama hesaplamaya devam et
        yas_uyari_mesaji = """
        <div class='alert alert-warning'>
            <h4>⚠️ Yeraltı Suyu Koruma Alanında Su Tahsis Belgesi Gerekli</h4>
            <p>Seçilen arazi YAS (Yeraltı Suları Koruma Alanı) içerisinde yer almaktadır. 
            Bu bölgede hara tesisi kurulumu için <b>su tahsis belgesi zorunludur</b>.</p>
            <p><strong>Uyarı:</strong> Su tahsis belgesi olmadan tesise izin verilmeyecektir.</p>
            <p><em>Bu hesaplama sadece bilgilendirme amaçlıdır.</em></p>
        </div>
        """
        # Uyarıyı sakla ama hesaplamaya devam et (frontend problemi çözülünceye kadar geçici)
        yas_uyari_mesaji_temp = yas_uyari_mesaji
    else:
        yas_uyari_mesaji_temp = ""
    
    # Hesaplama yap - Boks sayısı varsa onu kullan, yoksa optimal hesaplasın
    hesaplayici = HaraTesisiHesaplayici(kullanilacak_emsal_orani)
    
    # Boks sayısı değeri varsa al - Daha güvenli hale getirildi
    try:
        # yapi_bilgileri None olabilir veya "boks_sayisi" key olmayabilir, bu durumları kontrol et
        if yapi_bilgileri is None:
            boks_sayisi = None
        else:
            boks_sayisi_str = yapi_bilgileri.get("boks_sayisi", "")
            if boks_sayisi_str and isinstance(boks_sayisi_str, (str, int, float)):
                boks_sayisi = int(float(boks_sayisi_str))
                if boks_sayisi <= 0:
                    boks_sayisi = None  # Hesaplayıcı optimal değeri hesaplayacak
            else:
                boks_sayisi = None  # Hesaplayıcı optimal değeri hesaplayacak
    except (ValueError, TypeError, AttributeError):
        boks_sayisi = None  # Hesaplayıcı optimal değeri hesaplayacak
    
    try:
        hesaplama_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2, boks_sayisi)
        html_mesaj = _olustur_html_mesaj_hara(hesaplama_sonucu, kullanilacak_emsal_orani)
        
        # Sonuç
        izin_durumu = "izin_verilebilir" if "YAPILABİLİR" in hesaplama_sonucu.get("sonuc_durumu", "") else "izin_verilemez"
        
        return {
            "izin_durumu": izin_durumu,
            "mesaj": html_mesaj,
            "ana_mesaj": html_mesaj,
        }
    except Exception as e:
        # Hata durumunda kullanıcıya bilgi ver
        hata_mesaji = f"""
        <div class='alert alert-danger'>
            <h4>Hesaplama Sırasında Bir Hata Oluştu</h4>
            <p>Hara tesisi hesaplaması yapılırken beklenmeyen bir hata oluştu.</p>
            <p>Lütfen değerleri kontrol edip tekrar deneyiniz veya sistem yöneticisiyle iletişime geçiniz.</p>
            <p><small>Hata detayı: {str(e)}</small></p>
        </div>
        """
        return {
            "izin_durumu": "izin_verilemez",
            "mesaj": hata_mesaji,
            "ana_mesaj": hata_mesaji,
            "hata": str(e)
        }


def hara_kurali(arazi_buyuklugu_m2):
    """
    Hara (at yetiştiriciliği tesisi) için arazi büyüklüğü ve diğer koşulları kontrol eden kural
    
    Args:
        arazi_buyuklugu_m2: Arazi büyüklüğü (m²)
        
    Returns:
        dict: Kontrol sonuçlarını içeren sözlük
    """
    sonuc = {
        "izin_durumu": None,
        "ana_mesaj": None,
        "detay_mesaj_bakici_evi": "",
        "bilgi_mesaji_bakici_evi_hara": "",
        "uyari_mesaji_ozel_durum": "",
    }

    try:
        # Arazi büyüklüğünü güvenli bir şekilde float'a çevir
        try:
            arazi_buyuklugu_m2 = float(arazi_buyuklugu_m2)
        except (ValueError, TypeError):
            arazi_buyuklugu_m2 = 0

        # Minimum arazi büyüklüğü kontrolü
        if arazi_buyuklugu_m2 < HARA_MIN_ARAZI_M2:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["ana_mesaj"] = f"Hara (at üretimi/yetiştiriciliği tesisi) kurulumu için araziniz yeterli büyüklükte değildir. " \
                                f"Minimum {HARA_MIN_ARAZI_M2:,} m² arazi gereklidir. Mevcut arazi: {arazi_buyuklugu_m2:,} m²"
            sonuc["uyari_mesaji_ozel_durum"] = "Hara tesisleri için MINIMUM 4 dekarlık arazi gereklidir."
            return sonuc

        # Minimum arazi büyüklüğü yeterli, tam hesaplama için yönlendir
        kullanilacak_emsal_orani = EMSAL_ORANI
        hesaplayici = HaraTesisiHesaplayici(kullanilacak_emsal_orani)
        hesaplama_sonucu = hesaplayici.hesapla(arazi_buyuklugu_m2)
        
        html_mesaj = _olustur_html_mesaj_hara(hesaplama_sonucu, kullanilacak_emsal_orani)
        
        sonuc["izin_durumu"] = "izin_verilebilir" if "YAPILABİLİR" in hesaplama_sonucu.get("sonuc_durumu", "") else "izin_verilemez"
        sonuc["ana_mesaj"] = html_mesaj
        sonuc["detay_mesaj_bakici_evi"] = ""
        sonuc["bilgi_mesaji_bakici_evi_hara"] = "Hara tesislerinde bakıcı evi, müştemilat olarak dahil edilir."
        
        return sonuc
    except Exception as e:
        # Hata durumunda güvenli bir sonuç döndür
        sonuc["izin_durumu"] = "izin_verilemez"
        sonuc["ana_mesaj"] = f"Hesaplama sırasında bir hata oluştu: {str(e)}"
        sonuc["uyari_mesaji_ozel_durum"] = "Lütfen sistem yöneticisiyle iletişime geçiniz."
        return sonuc
