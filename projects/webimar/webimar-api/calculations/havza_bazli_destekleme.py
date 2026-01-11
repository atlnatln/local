from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def havza_bazli_destekleme_modeli(request):
    """
    Havza Bazlı Destekleme Modeli hesaplama endpoint'i
    """
    try:
        data = request.data
        
        # Veri doğrulama
        if not data.get('il') or not data.get('ilce'):
            return Response({
                'uygun': False,
                'mesaj': 'İl ve ilçe bilgisi zorunludur.',
                'detaylar': {}
            }, status=status.HTTP_400_BAD_REQUEST)
            
        urunler = data.get('urunler', [])
        gecerli_urunler = [u for u in urunler if u.get('urun') and u.get('dekar', 0) > 0]
        
        if not gecerli_urunler:
            return Response({
                'uygun': False,
                'mesaj': 'En az bir ürün ve dekar miktarı girmelisiniz.',
                'detaylar': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Temel veriler
        TEMEL_DESTEK = 310  # TL/da
        
        # Ürün kategorileri ve katsayıları
        URUN_KATEGORILERI = {
            # 1. Kategori - Katsayı: 1
            'Aspir': 1, 'Mercimek': 1, 'Nohut': 1, 'Patates': 1, 'Soğan': 1,
            'Fiğ': 1, 'Burçak': 1, 'Mürdümük': 1, 'Hayvan pancarı': 1, 
            'Yem şalgamı': 1, 'Yem bezelyesi': 1, 'Yem baklası': 1, 
            'Üçgül': 1, 'İtalyan çimi': 1, 'Yulaf': 1, 'Çavdar': 1, 'Tritikale': 1,
            
            # 2. Kategori - Katsayı: 1.3
            'Arpa': 1.3, 'Buğday': 1.3, 'Mısır': 1.3,
            'Yonca': 1.3, 'Korunga': 1.3, 'Yapay çayır mera': 1.3, 
            'Silajlık mısır': 1.3, 'Silajlık soya': 1.3, 'Sorgum otu': 1.3, 
            'Sudan otu': 1.3, 'Sorgum-sudan melezi': 1.3,
            
            # 3. Kategori - Katsayı: 1.5
            'Ayçiçeği': 1.5, 'Fındık': 1.5, 'Kolza': 1.5, 'Fasulye': 1.5, 'Soya': 1.5, 'Çay': 1.5,
            
            # 4. Kategori - Katsayı: 2.25
            'Çeltik': 2.25, 'Pamuk': 2.25
        }
        
        # Süt havzası illeri
        SUT_HAVZASI_ILLERI = [
            'AMASYA', 'BİNGÖL', 'BİTLİS', 'ÇORUM', 'ELAZIĞ', 
            'ERZİNCAN', 'ERZURUM', 'MUŞ', 'TOKAT', 'TUNCELİ'
        ]
        
        # Su kısıtı bölgeleri
        SU_KISITI_BOLGELERI = {
            'AKSARAY': ['Merkez', 'Eskil', 'Gülağaç', 'Güzelyurt', 'Sultanhanı'],
            'ANKARA': ['Bala', 'Gölbaşı', 'Haymana', 'Şereflikoçhisar'],
            'ESKİŞEHİR': ['Alpu', 'Beylikova', 'Çifteler', 'Mahmudiye', 'Mihalıççık', 'Sivrihisar'],
            'HATAY': ['Kumlu', 'Reyhanlı'],
            'KARAMAN': ['Ayrancı', 'Merkez', 'Kazımkarabekir'],
            'KIRŞEHİR': ['Boztepe', 'Mucur'],
            'KONYA': ['Akören', 'Akşehir', 'Altınekin', 'Cihanbeyli', 'Çumra', 'Derbent', 
                     'Doğanhisar', 'Emirgazi', 'Ereğli', 'Güneysınır', 'Halkapınar', 
                     'Kadınhanı', 'Karapınar', 'Karatay', 'Kulu', 'Meram', 'Sarayönü', 
                     'Selçuklu', 'Tuzlukçu'],
            'MARDİN': ['Artuklu', 'Derik', 'Kızıltepe'],
            'NEVŞEHİR': ['Acıgöl', 'Derinkuyu', 'Gülşehir'],
            'NİĞDE': ['Altunhisar', 'Bor', 'Çiftlik', 'Merkez'],
            'ŞANLIURFA': ['Viranşehir']
        }
        
        # Su kısıtı destek katsayıları
        SU_KISITI_KATSAYILARI = {
            'Aspir': 0.8, 'Fiğ': 0.8, 'Mercimek': 0.8, 'Nohut': 0.8, 'Yem bezelyesi': 0.8,
            'Arpa': 1.4, 'Buğday': 1.4,
            'Ayçiçeği': 1.2
        }
        
        # Sertifikalı tohum destekleri
        SERTIFIKALI_TOHUM_DESTEKLERI = {
            'Arpa': 0.56, 'Buğday': 0.56, 'Çavdar': 0.56, 'Çeltik': 0.56, 
            'Fasulye': 0.56, 'Tritikale': 0.56, 'Yulaf': 0.56,
            'Aspir': 0.2, 'Kolza': 0.2, 'Susam': 0.2,
            'Korunga': 0.6, 'Soya': 0.6, 'Yer fıstığı': 0.6, 'Yonca': 0.6,
            'Fiğ': 0.4, 'Mercimek': 0.4, 'Nohut': 0.4, 'Yem bezelyesi': 0.4,
            'Patates': 2.2,
            # Yerli sertifikalı tohum destekleri
            'Ayçiçeği': 0.6, 'Mısır': 0.6  # Soya da 0.6 ama yukarıda zaten var
        }
        
        # Organik tarım destekleri (grup bazında)
        ORGANIK_TARIM_DESTEKLERI = {
            'birinci_grup': {'bireysel': 1.2, 'grup': 0.6},
            'ikinci_grup': {'bireysel': 0.6, 'grup': 0.3},
            'ucuncu_grup': {'bireysel': 0.4, 'grup': 0.2}
        }
        
        # İyi tarım destekleri
        IYI_TARIM_DESTEKLERI = {
            'birinci_grup': {
                'ortualti_bireysel': 1.7,
                'ortualti_grup': 0.85,
                'acikta_bireysel': 0.7,
                'acikta_grup': 0.35
            },
            'ikinci_grup': {'bireysel': 0.6, 'grup': 0.3},
            'ucuncu_grup': {'bireysel': 0.4, 'grup': 0.2}
        }
        
        # Hesaplama başlangıcı
        il_adi = data.get('il', '').upper().strip()
        ilce_adi = data.get('ilce', '').strip()
        
        toplam_temel_destek = 0
        toplam_planli_uretim = 0
        toplam_su_kisiti = 0
        toplam_sertifikali_tohum = 0
        toplam_organik_tarim = 0
        toplam_iyi_tarim = 0
        toplam_gubre = 0
        
        # Ürün bazlı hesaplamalar
        for urun in gecerli_urunler:
            urun_adi = urun.get('urun', '')
            dekar = float(urun.get('dekar', 0))
            
            if dekar <= 0:
                continue
                
            # Ürün katsayısı
            katsayi = URUN_KATEGORILERI.get(urun_adi, 1)
            
            # Su kısıtı kontrolü - Mısır (dane) ve Patates için kısıtlama
            su_kisiti_bolgesinde = (il_adi in SU_KISITI_BOLGELERI and 
                                   ilce_adi in SU_KISITI_BOLGELERI.get(il_adi, []))
            
            if su_kisiti_bolgesinde and urun_adi in ['Mısır', 'Patates']:
                # Su kısıtı bölgelerinde mısır (dane) ve patates için hiçbir destek verilmez
                continue
            
            # Temel destek
            temel_destek_urun = TEMEL_DESTEK * dekar
            toplam_temel_destek += temel_destek_urun
            
            # Planlı üretim desteği
            planli_uretim_urun = TEMEL_DESTEK * katsayi * dekar
            toplam_planli_uretim += planli_uretim_urun
            
            # Su kısıtı desteği
            if su_kisiti_bolgesinde and urun_adi in SU_KISITI_KATSAYILARI:
                su_kisiti_katsayi = SU_KISITI_KATSAYILARI[urun_adi]
                su_kisiti_destek = TEMEL_DESTEK * su_kisiti_katsayi * dekar
                toplam_su_kisiti += su_kisiti_destek
            
            # Sertifikalı tohum desteği
            uretimiGelistirme = data.get('uretimiGelistirme', {})
            if uretimiGelistirme.get('sertifikaliTohum') and urun_adi in SERTIFIKALI_TOHUM_DESTEKLERI:
                sertifikali_katsayi = SERTIFIKALI_TOHUM_DESTEKLERI[urun_adi]
                sertifikali_destek = TEMEL_DESTEK * sertifikali_katsayi * dekar
                toplam_sertifikali_tohum += sertifikali_destek
                
                # Patates için yerli sertifikalı tohum ilavesi
                if urun_adi == 'Patates':
                    toplam_sertifikali_tohum += TEMEL_DESTEK * 1 * dekar
            
            # Organik tarım desteği
            if uretimiGelistirme.get('organikTarim', {}).get('secili'):
                organik_tur = uretimiGelistirme.get('organikTarim', {}).get('tur', 'bireysel')
                # Basit gruplandırma - gerçekte daha detaylı olacak
                grup = 'birinci_grup'  # Varsayılan
                if urun_adi in ['Arpa', 'Buğday', 'Mısır', 'Yonca', 'Korunga']:
                    grup = 'ikinci_grup'
                elif urun_adi in ['Ayçiçeği', 'Fındık', 'Kolza']:
                    grup = 'ucuncu_grup'
                    
                organik_katsayi = ORGANIK_TARIM_DESTEKLERI[grup][organik_tur]
                organik_destek = TEMEL_DESTEK * organik_katsayi * dekar
                toplam_organik_tarim += organik_destek
            
            # İyi tarım desteği
            if uretimiGelistirme.get('iyiTarim', {}).get('secili'):
                # Basit implementasyon
                grup = 'birinci_grup'  # Varsayılan
                iyi_tarim_katsayi = 0.7  # Açıkta bireysel varsayılan
                iyi_tarim_destek = TEMEL_DESTEK * iyi_tarim_katsayi * dekar
                toplam_iyi_tarim += iyi_tarim_destek
            
            # Gübre desteği
            if uretimiGelistirme.get('katiOrganikGubre'):
                gubre_destek = TEMEL_DESTEK * 0.32 * dekar
                toplam_gubre += gubre_destek
        
        # Süt havzası ilavesi
        toplam_sut_havzasi = 0
        if il_adi in SUT_HAVZASI_ILLERI:
            # Yem bitkisi kontrolü yapılacak
            yem_bitkileri = ['Fiğ', 'Burçak', 'Mürdümük', 'Yonca', 'Korunga', 'Yulaf', 'Çavdar']
            for urun in gecerli_urunler:
                if urun.get('urun') in yem_bitkileri:
                    dekar = float(urun.get('dekar', 0))
                    katsayi = URUN_KATEGORILERI.get(urun.get('urun', ''), 1)
                    sut_havzasi_ilave = TEMEL_DESTEK * katsayi * 0.5 * dekar  # %50 ilave
                    toplam_sut_havzasi += sut_havzasi_ilave
        
        # Genç/Kadın çiftçi ilavesi
        toplam_genclik_ilavesi = 0
        genc_ciftci = data.get('gencCiftci', False)
        kadin_ciftci = data.get('kadinCiftci', False)
        
        if genc_ciftci or kadin_ciftci:
            # Her ürün için 3 katsayısı ile temel destek ilavesi
            for urun in gecerli_urunler:
                dekar = float(urun.get('dekar', 0))
                if dekar > 0:
                    genclik_ilave = TEMEL_DESTEK * 3 * dekar
                    toplam_genclik_ilavesi += genclik_ilave
        
        # Organik tarım ilave desteği (1. derece örgüt üyesi için)
        orgut_ilavesi = 0
        if (data.get('orgutUyesi', False) and 
            uretimiGelistirme.get('organikTarim', {}).get('secili')):
            # %25 ilave
            orgut_ilavesi = toplam_organik_tarim * 0.25
            toplam_organik_tarim += orgut_ilavesi
        
        # Toplam hesaplama
        toplam_destek = (
            toplam_temel_destek + 
            toplam_planli_uretim + 
            toplam_genclik_ilavesi +
            toplam_sut_havzasi +
            toplam_su_kisiti +
            toplam_sertifikali_tohum +
            toplam_organik_tarim +
            toplam_iyi_tarim +
            toplam_gubre
        )
        
        # Sonuç hazırlama
        detaylar = {
            'temel_destek': round(toplam_temel_destek, 2),
            'planli_uretim': round(toplam_planli_uretim, 2),
            'genclik_ilavesi': round(toplam_genclik_ilavesi, 2),
            'sut_havzasi_ilavesi': round(toplam_sut_havzasi, 2),
            'su_kisiti': round(toplam_su_kisiti, 2),
            'sertifikali_tohum': round(toplam_sertifikali_tohum, 2),
            'organik_tarim': round(toplam_organik_tarim, 2),
            'iyi_tarim': round(toplam_iyi_tarim, 2),
            'gubre': round(toplam_gubre, 2),
            'toplam': round(toplam_destek, 2)
        }
        
        mesaj = f"{il_adi}/{ilce_adi} için {len(gecerli_urunler)} ürün üzerinden hesaplama tamamlandı."
        
        if genc_ciftci:
            mesaj += " Genç çiftçi ilavesi dahil edildi."
        if kadin_ciftci:
            mesaj += " Kadın çiftçi ilavesi dahil edildi."
        if data.get('orgutUyesi'):
            mesaj += " Örgüt üyesi ilavesi dahil edildi."
        
        return Response({
            'uygun': True,
            'mesaj': mesaj,
            'detaylar': detaylar
        })
        
    except Exception as e:
        return Response({
            'uygun': False,
            'mesaj': f'Hesaplama sırasında hata oluştu: {str(e)}',
            'detaylar': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)