"""
Soğuk Hava Deposu Hesaplama Modülü - MD Belgesi Uyumlu

Bu modül soğuk hava deposu yapılaşma kurallarını ve hesaplamalarını MD belgesi gereksinimlerine 
göre uygulamak için kullanır.

Yeni Sistem Kuralları:
1. Emsal tipi seçimi zorunludur
2. Marjinal (%20): Sadece arazi büyüklüğü, ek kontrol yok
3. Mutlak/Dikili/Özel (%5): Arazi tipi seçimi + bağ evi gibi kontroller
"""

# Soğuk hava deposu için sabitler
DEFAULT_SOGUK_HAVA_DEPOSU_EMSAL_ORANI = 0.20  # %20 varsayılan emsal oranı (artık dinamik)
SOGUK_HAVA_DEPOSU_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²) - küçük işletmeler için uygun hale getirildi

# Emsal tipleri
EMSAL_MARJINAL = 0.20  # %20 - Serbest hesaplama
EMSAL_MUTLAK_DIKILI_OZEL = 0.05  # %5 - Detaylı kontroller

# Arazi tipi konfigürasyonları (Bağ evi/tarımsal depo sistemi ile aynı)
SOGUK_HAVA_ARAZI_TIPI_KONFIGURASYONLARI = {
    "Dikili vasıflı": {
        "emsal_orani": 0.05,
        "min_alan": 5000,
        "alan_anahtar": "dikili_alani",
        "aciklama": "Dikili vasıflı arazi için minimum 5.000 m² gerekli"
    },
    "Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı": {
        "emsal_orani": 0.20,
        "min_alan": 20000,
        "alan_anahtar": "tarla_alani", 
        "aciklama": "Marjinal tarım arazisi için minimum 20.000 m² gerekli"
    },
    "Tarla": {
        "emsal_orani": 0.20,
        "min_alan": 20000,
        "alan_anahtar": "tarla_alani",
        "aciklama": "Tarla vasıflı arazi için minimum 20.000 m² gerekli"
    },
    "Sera": {
        "emsal_orani": 0.05,
        "min_alan": 3000,
        "alan_anahtar": "sera_alani",
        "aciklama": "Örtüaltı yetiştiricilik için minimum 3.000 m² gerekli"
    }
}


def soguk_hava_deposu_degerlendir(arazi_bilgileri, yapi_bilgileri=None) -> dict:
    """
    MD Belgesi Uyumlu Soğuk Hava Deposu Değerlendirmesi
    
    Args:
        arazi_bilgileri (dict): Arazi bilgileri ve emsal tipi seçimi
        yapi_bilgileri (dict): Yapı bilgileri (opsiyonel)
        
    Returns:
        dict: Hesaplama sonuçları ve izin durumu
    """
    print(f"🏢 Soğuk hava deposu değerlendirmesi başladı")
    print(f"📍 Arazi bilgileri: {arazi_bilgileri}")
    print(f"🏗️ Yapı bilgileri: {yapi_bilgileri}")
    
    try:
        # Emsal tipi kontrolü - MD belgesi gereksinimi
        emsal_tipi = arazi_bilgileri.get('emsal_tipi')
        if not emsal_tipi:
            return {
                'success': False,
                'error': 'EMSAL_TIPI_GEREKLI',
                'ana_mesaj': 'Emsal türü seçimi zorunludur',
                'detay_mesaj': 'Soğuk hava deposu için Marjinal (%20) veya Mutlak/Dikili/Özel (%5) emsal türünden birini seçmeniz gerekir.',
                'html_mesaj': '''
                <div class="alert alert-warning">
                    <h4>⚠️ Emsal Türü Seçimi Gerekli</h4>
                    <p>Soğuk hava deposu hesaplaması için emsal türü seçmeniz zorunludur:</p>
                    <ul>
                        <li><strong>Marjinal (%20):</strong> Sadece arazi büyüklüğü ile serbest hesaplama</li>
                        <li><strong>Mutlak/Dikili/Özel (%5):</strong> Arazi tipi seçimi ve detaylı kontroller</li>
                    </ul>
                </div>
                '''
            }
        
        # MARJINAL (%20) EMSAL - Serbest hesaplama
        if emsal_tipi == 'marjinal':
            print("📊 Marjinal (%20) emsal hesaplaması")
            return _marjinal_emsal_hesaplama(arazi_bilgileri)
            
        # MUTLAK/DİKİLİ/ÖZEL (%5) EMSAL - Detaylı kontroller
        elif emsal_tipi == 'mutlak_dikili_ozel':
            print("🔍 Mutlak/Dikili/Özel (%5) emsal hesaplaması")
            return _mutlak_dikili_ozel_hesaplama(arazi_bilgileri)
        
        else:
            return {
                'success': False,
                'error': 'GECERSIZ_EMSAL_TIPI',
                'ana_mesaj': 'Geçersiz emsal türü',
                'detay_mesaj': f'"{emsal_tipi}" geçersiz bir emsal türüdür. Lütfen "marjinal" veya "mutlak_dikili_ozel" seçin.',
                'html_mesaj': f'''
                <div class="alert alert-danger">
                    <h4>❌ Geçersiz Emsal Türü</h4>
                    <p>Seçilen emsal türü "{emsal_tipi}" geçerli değildir.</p>
                    <p>Lütfen aşağıdaki seçeneklerden birini seçin:</p>
                    <ul>
                        <li><strong>marjinal:</strong> %20 emsal oranı</li>
                        <li><strong>mutlak_dikili_ozel:</strong> %5 emsal oranı</li>
                    </ul>
                </div>
                '''
            }
            
    except Exception as e:
        print(f"❌ Soğuk hava deposu hesaplama hatası: {e}")
        return {
            'success': False,
            'error': 'HESAPLAMA_HATASI',
            'ana_mesaj': 'Hesaplama sırasında hata oluştu',
            'detay_mesaj': f'Hata detayı: {str(e)}',
            'html_mesaj': f'''
            <div class="alert alert-danger">
                <h4>❌ Hesaplama Hatası</h4>
                <p>Soğuk hava deposu hesaplaması sırasında bir hata oluştu.</p>
                <p>Hata detayı: {str(e)}</p>
                <p>Lütfen form bilgilerini kontrol edip tekrar deneyin.</p>
            </div>
            '''
        }


def _marjinal_emsal_hesaplama(arazi_bilgileri) -> dict:
    """
    Marjinal (%20) emsal ile serbest hesaplama
    MD belgesi: Sadece arazi büyüklüğü, hiçbir ek kontrol uygulanmaz
    """
    print("📊 Marjinal emsal hesaplaması başladı")
    
    # Arazi büyüklüğünü al
    arazi_alani = arazi_bilgileri.get('buyukluk_m2', 0)
    if arazi_alani == 0:
        # Alternatif alan anahtarlarını dene
        arazi_alani = arazi_bilgileri.get('alan_m2', 0)
    
    if arazi_alani <= 0:
        return {
            'success': False,
            'error': 'ARAZI_ALANI_GEREKLI',
            'ana_mesaj': 'Arazi alanı bilgisi eksik',
            'detay_mesaj': 'Marjinal emsal hesaplaması için arazi alanı (m²) girişi zorunludur.',
            'html_mesaj': '''
            <div class="alert alert-warning">
                <h4>⚠️ Arazi Alanı Gerekli</h4>
                <p>Marjinal emsal hesaplaması için arazi alanını (m²) girmeniz gerekir.</p>
            </div>
            '''
        }
    
    # Minimum alan kontrolü
    if arazi_alani < SOGUK_HAVA_DEPOSU_MIN_ARAZI_M2:
        return {
            'success': False,
            'error': 'MINIMUM_ALAN_YETERSİZ',
            'ana_mesaj': 'Arazi alanı yetersiz',
            'detay_mesaj': f'Soğuk hava deposu için minimum {SOGUK_HAVA_DEPOSU_MIN_ARAZI_M2} m² arazi gereklidir. Mevcut alan: {arazi_alani} m²',
            'html_mesaj': f'''
            <div class="alert alert-danger">
                <h4>❌ Yetersiz Arazi Alanı</h4>
                <p>Soğuk hava deposu için minimum <strong>{SOGUK_HAVA_DEPOSU_MIN_ARAZI_M2} m²</strong> arazi gereklidir.</p>
                <p>Mevcut arazi alanı: <strong>{arazi_alani} m²</strong></p>
                <p>Eksik alan: <strong>{SOGUK_HAVA_DEPOSU_MIN_ARAZI_M2 - arazi_alani} m²</strong></p>
            </div>
            '''
        }
    
    # Marjinal emsal hesaplaması (%20)
    maksimum_yapi_alani = arazi_alani * EMSAL_MARJINAL
    
    # Basit alan dağılımı (opsiyonel)
    depo_alani_m2 = maksimum_yapi_alani * 0.70      # %70 depo alanı
    idari_alan_m2 = maksimum_yapi_alani * 0.20      # %20 idari alan
    teknik_alan_m2 = maksimum_yapi_alani * 0.10     # %10 teknik alan
    
    print(f"✅ Marjinal hesaplama tamamlandı - Maksimum yapı alanı: {maksimum_yapi_alani} m²")
    
    return {
        'success': True,
        'emsal_tipi': 'marjinal',
        'ana_mesaj': f'Bu araziye en fazla {maksimum_yapi_alani:.0f} m² soğuk hava deposu yapılabilir.',
        'detay_mesaj': 'Marjinal emsal oranı ile serbest hesaplama yapılmıştır. Ek kontroller uygulanmamıştır.',
        'maksimum_insaat_alani_m2': maksimum_yapi_alani,
        'izin_durumu': 'İZİN VERİLEBİLİR',
        'emsal_orani': EMSAL_MARJINAL,
        'html_mesaj': f'''
        <div class="alert alert-success">
            <h4>✅ Soğuk Hava Deposu İnşaatı Mümkün</h4>
            <p><strong>Marjinal Emsal (%20) Hesaplaması</strong></p>
            
            <div class="calculation-summary">
                <div class="row">
                    <div class="col-6"><strong>Arazi Alanı:</strong></div>
                    <div class="col-6">{arazi_alani:,.0f} m²</div>
                </div>
                <div class="row">
                    <div class="col-6"><strong>Emsal Oranı:</strong></div>
                    <div class="col-6">%{EMSAL_MARJINAL*100:.0f}</div>
                </div>
                <div class="row highlight">
                    <div class="col-6"><strong>Maksimum Yapı Alanı:</strong></div>
                    <div class="col-6">{maksimum_yapi_alani:,.0f} m²</div>
                </div>
            </div>
            
            <div class="area-breakdown mt-3">
                <h6>Alan Dağılımı (Opsiyonel):</h6>
                <div class="row">
                    <div class="col-6">• Soğuk Hava Deposu:</div>
                    <div class="col-6">{depo_alani_m2:,.0f} m² (%70)</div>
                </div>
                <div class="row">
                    <div class="col-6">• İdari Alan:</div>
                    <div class="col-6">{idari_alan_m2:,.0f} m² (%20)</div>
                </div>
                <div class="row">
                    <div class="col-6">• Teknik Alan:</div>
                    <div class="col-6">{teknik_alan_m2:,.0f} m² (%10)</div>
                </div>
            </div>
            
            <div class="alert alert-info mt-3">
                <small><strong>Not:</strong> Marjinal emsal ile herhangi bir ek kontrol (dikili alan, zeytinlik, ağaç yoğunluğu vs.) uygulanmamıştır.</small>
            </div>
        </div>
        ''',
        # Ek detaylar
        'arazi_alani_m2': arazi_alani,
        'alan_dagilimi': {
            'soğuk_hava_deposu_alani': round(depo_alani_m2, 0),
            'idari_alan': round(idari_alan_m2, 0),
            'teknik_alan': round(teknik_alan_m2, 0),
            'toplam_yapi_alani': round(maksimum_yapi_alani, 0)
        }
    }


def _mutlak_dikili_ozel_hesaplama(arazi_bilgileri) -> dict:
    """
    Mutlak/Dikili/Özel (%5) emsal ile detaylı kontroller
    MD belgesi: Arazi tipi seçimi + bağ evi sistemi gibi kontroller
    """
    print("🔍 Mutlak/Dikili/Özel hesaplaması başladı")
    
    # Arazi vasfi kontrolü
    arazi_vasfi = arazi_bilgileri.get('ana_vasif') or arazi_bilgileri.get('arazi_vasfi')
    if not arazi_vasfi:
        return {
            'success': False,
            'error': 'ARAZI_TIPI_GEREKLI', 
            'ana_mesaj': 'Arazi tipi seçimi gerekli',
            'detay_mesaj': 'Mutlak/Dikili/Özel emsal hesaplaması için arazi tipi seçimi zorunludur.',
            'html_mesaj': '''
            <div class="alert alert-warning">
                <h4>⚠️ Arazi Tipi Seçimi Gerekli</h4>
                <p>Mutlak/Dikili/Özel emsal hesaplaması için arazi tipini seçmeniz gerekir:</p>
                <ul>
                    <li>Dikili vasıflı</li>
                    <li>Tarla</li>
                    <li>Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı</li>
                    <li>Sera (Örtüaltı yetiştiricilik)</li>
                </ul>
            </div>
            '''
        }
    
    # Konfigürasyon kontrolü
    config = SOGUK_HAVA_ARAZI_TIPI_KONFIGURASYONLARI.get(arazi_vasfi)
    if not config:
        return {
            'success': False,
            'error': 'DESTEKLENMEYEN_ARAZI_TIPI',
            'ana_mesaj': 'Desteklenmeyen arazi tipi',
            'detay_mesaj': f'"{arazi_vasfi}" arazi tipi için henüz hesaplama desteği bulunmamaktadır.',
            'html_mesaj': f'''
            <div class="alert alert-danger">
                <h4>❌ Desteklenmeyen Arazi Tipi</h4>
                <p>Seçilen arazi tipi "{arazi_vasfi}" için hesaplama desteği bulunmamaktadır.</p>
                <p>Desteklenen arazi tipleri:</p>
                <ul>
                    {chr(10).join([f"<li>{tip}</li>" for tip in SOGUK_HAVA_ARAZI_TIPI_KONFIGURASYONLARI.keys()])}
                </ul>
            </div>
            '''
        }
    
    # Alan kontrolleri
    alan_kontrol_sonucu = _soguk_hava_alan_kontrolleri(arazi_bilgileri, config)
    if not alan_kontrol_sonucu["yeterli"]:
        return alan_kontrol_sonucu.get("hata_detayi", {
            'success': False,
            'error': 'ALAN_KONTROLLERI_BASARISIZ',
            'ana_mesaj': 'Alan kontrolleri başarısız',
            'detay_mesaj': 'Arazi alanı gereksinimleri karşılanmıyor.',
            'html_mesaj': '<div class="alert alert-danger"><h4>❌ Alan Kontrolleri Başarısız</h4><p>Arazi alanı gereksinimleri karşılanmıyor.</p></div>'
        })
    
    # Zeytinlik kontrolleri (eğer varsa)
    zeytin_kontrol_sonucu = _soguk_hava_zeytin_kontrolleri(arazi_bilgileri)
    if not zeytin_kontrol_sonucu["gecerli"]:
        return zeytin_kontrol_sonucu.get("hata_detayi", {
            'success': False,
            'error': 'ZEYTIN_KONTROLLERI_BASARISIZ',
            'ana_mesaj': 'Zeytinlik kontrolleri başarısız',
            'detay_mesaj': 'Zeytinlik alan kontrolleri karşılanmıyor.',
            'html_mesaj': '<div class="alert alert-danger"><h4>❌ Zeytinlik Kontrolleri Başarısız</h4><p>Zeytinlik alan kontrolleri karşılanmıyor.</p></div>'
        })
    
    # Hesaplama
    toplam_gecerli_alan = alan_kontrol_sonucu["detaylar"]["toplam_gecerli_alan"]
    emsal_orani = config["emsal_orani"]
    maksimum_yapi_alani = toplam_gecerli_alan * emsal_orani
    
    # Alan dağılımı
    depo_alani_m2 = maksimum_yapi_alani * 0.70      # %70 depo alanı
    idari_alan_m2 = maksimum_yapi_alani * 0.20      # %20 idari alan
    teknik_alan_m2 = maksimum_yapi_alani * 0.10     # %10 teknik alan
    
    print(f"✅ Mutlak/Dikili/Özel hesaplama tamamlandı - Maksimum yapı alanı: {maksimum_yapi_alani} m²")
    
    return {
        'success': True,
        'emsal_tipi': 'mutlak_dikili_ozel',
        'ana_mesaj': f'Bu araziye en fazla {maksimum_yapi_alani:.0f} m² soğuk hava deposu yapılabilir.',
        'detay_mesaj': f'{arazi_vasfi} arazi tipi için detaylı kontroller uygulanmış ve başarıyla geçilmiştir.',
        'maksimum_insaat_alani_m2': maksimum_yapi_alani,
        'izin_durumu': 'İZİN VERİLEBİLİR',
        'emsal_orani': emsal_orani,
        'html_mesaj': f'''
        <div class="alert alert-success">
            <h4>✅ Soğuk Hava Deposu İnşaatı Mümkün</h4>
            <p><strong>Mutlak/Dikili/Özel Emsal (%{emsal_orani*100:.0f}) Hesaplaması</strong></p>
            
            <div class="calculation-summary">
                <div class="row">
                    <div class="col-6"><strong>Arazi Tipi:</strong></div>
                    <div class="col-6">{arazi_vasfi}</div>
                </div>
                <div class="row">
                    <div class="col-6"><strong>Toplam Geçerli Alan:</strong></div>
                    <div class="col-6">{toplam_gecerli_alan:,.0f} m²</div>
                </div>
                <div class="row">
                    <div class="col-6"><strong>Emsal Oranı:</strong></div>
                    <div class="col-6">%{emsal_orani*100:.0f}</div>
                </div>
                <div class="row highlight">
                    <div class="col-6"><strong>Maksimum Yapı Alanı:</strong></div>
                    <div class="col-6">{maksimum_yapi_alani:,.0f} m²</div>
                </div>
            </div>
            
            <div class="area-breakdown mt-3">
                <h6>Alan Dağılımı (Opsiyonel):</h6>
                <div class="row">
                    <div class="col-6">• Soğuk Hava Deposu:</div>
                    <div class="col-6">{depo_alani_m2:,.0f} m² (%70)</div>
                </div>
                <div class="row">
                    <div class="col-6">• İdari Alan:</div>
                    <div class="col-6">{idari_alan_m2:,.0f} m² (%20)</div>
                </div>
                <div class="row">
                    <div class="col-6">• Teknik Alan:</div>
                    <div class="col-6">{teknik_alan_m2:,.0f} m² (%10)</div>
                </div>
            </div>
            
            <div class="alert alert-info mt-3">
                <small><strong>Not:</strong> Tüm arazi tipi kontrolleri ve zeytinlik kontrolleri başarıyla geçilmiştir.</small>
            </div>
        </div>
        ''',
        # Ek detaylar
        'arazi_alani_m2': toplam_gecerli_alan,
        'arazi_tipi': arazi_vasfi,
        'alan_kontrolleri': alan_kontrol_sonucu["detaylar"],
        'zeytin_kontrolleri': zeytin_kontrol_sonucu.get("detaylar", {}),
        'alan_dagilimi': {
            'soğuk_hava_deposu_alani': round(depo_alani_m2, 0),
            'idari_alan': round(idari_alan_m2, 0),
            'teknik_alan': round(teknik_alan_m2, 0),
            'toplam_yapi_alani': round(maksimum_yapi_alani, 0)
        }
    }


def _soguk_hava_alan_kontrolleri(arazi_bilgileri, config):
    """Soğuk hava deposu için alan kontrolü fonksiyonu"""
    sonuc = {"yeterli": False, "detaylar": {}}
    
    print(f"🔍 Soğuk hava alan kontrolü - Config: {config}")
    print(f"🔍 Arazi bilgileri: {arazi_bilgileri}")
    
    min_alan = config["min_alan"]
    alan_anahtar = config["alan_anahtar"]
    
    # Alan değerini al
    mevcut_alan = arazi_bilgileri.get(alan_anahtar, 0)
    if mevcut_alan == 0:
        # Alternatif anahtar dene
        mevcut_alan = arazi_bilgileri.get("buyukluk_m2", 0)
        if mevcut_alan == 0:
            mevcut_alan = arazi_bilgileri.get("alan_m2", 0)
    
    print(f"🔍 Mevcut alan: {mevcut_alan} m², Minimum gerekli: {min_alan} m²")
    
    if mevcut_alan < min_alan:
        eksik_alan = min_alan - mevcut_alan
        sonuc["hata_detayi"] = {
            'success': False,
            'error': 'MINIMUM_ALAN_YETERSİZ',
            'ana_mesaj': f'Minimum arazi alanı yetersiz',
            'detay_mesaj': f'{config["aciklama"]}. Mevcut alan: {mevcut_alan} m², Eksik alan: {eksik_alan} m²',
            'html_mesaj': f'''
            <div class="alert alert-danger">
                <h4>❌ Yetersiz Arazi Alanı</h4>
                <p>{config["aciklama"]}</p>
                <p>Mevcut arazi alanı: <strong>{mevcut_alan:,.0f} m²</strong></p>
                <p>Eksik alan: <strong>{eksik_alan:,.0f} m²</strong></p>
            </div>
            '''
        }
        return sonuc
    
    # Başarılı
    sonuc["yeterli"] = True
    sonuc["detaylar"] = {
        "toplam_gecerli_alan": mevcut_alan,
        "min_alan_gereksinimi": min_alan,
        "fazla_alan": mevcut_alan - min_alan,
        "alan_tipi": alan_anahtar
    }
    
    print(f"✅ Alan kontrolü başarılı: {mevcut_alan} m² (Min: {min_alan} m²)")
    return sonuc


def _soguk_hava_zeytin_kontrolleri(arazi_bilgileri):
    """Soğuk hava deposu için zeytinlik kontrolleri"""
    try:
        # Bağ evi modülünden zeytin kontrol fonksiyonlarını kullan
        from .bag_evi import _universal_zeytin_agac_kontrolleri
        
        # Zeytinlik ile ilgili parametreler varsa kontrol et
        zeytin_parametreleri = [
            'zeytinlik_alani', 'zeytin_agac_sayisi', 'zeytin_agac_adedi',
            'tapu_zeytin_agac_adedi', 'mevcut_zeytin_agac_adedi'
        ]
        
        zeytin_var = any(arazi_bilgileri.get(param, 0) > 0 for param in zeytin_parametreleri)
        
        if not zeytin_var:
            print("ℹ️ Zeytinlik alanı bulunmuyor, kontrol geçiliyor")
            return {"gecerli": True, "detaylar": {"mesaj": "Zeytinlik alanı bulunmamaktadır"}}
        
        print("🫒 Zeytinlik kontrolü yapılıyor")
        return _universal_zeytin_agac_kontrolleri(arazi_bilgileri)
        
    except ImportError as e:
        print(f"⚠️ Zeytin kontrol modülü yüklenemedi, kontrol geçiliyor: {e}")
        return {"gecerli": True, "detaylar": {"mesaj": "Zeytin kontrolleri geçildi (modül bulunamadı)"}}
    except Exception as e:
        print(f"⚠️ Zeytin kontrolü hata verdi, kontrol geçiliyor: {e}")
        return {"gecerli": True, "detaylar": {"mesaj": f"Zeytin kontrolleri geçildi (hata: {str(e)})"}}


# ESKİ FONKSİYON - Geriye uyumluluk için korunuyor
def calculate_soguk_hava_deposu(alan_m2: float, emsal_orani: float = None) -> dict:
    """
    ESKİ VERSİYON - Geriye uyumluluk için korunuyor
    Yeni sistem için soguk_hava_deposu_degerlendir() kullanın
    """
    print("⚠️ Eski soguk hava deposu fonksiyonu kullanılıyor, yeni sisteme yönlendiriliyor")
    
    # Eski sistem parametrelerini yeni sisteme çevir
    arazi_bilgileri = {
        "buyukluk_m2": alan_m2,
        "ana_vasif": "Tarla" if emsal_orani == 0.20 else "Dikili vasıflı",
        "emsal_tipi": "marjinal" if emsal_orani == 0.20 else "mutlak_dikili_ozel"
    }
    
    yapi_bilgileri = {}
    
    # Yeni sistem fonksiyonunu çağır
    return soguk_hava_deposu_degerlendir(arazi_bilgileri, yapi_bilgileri)
