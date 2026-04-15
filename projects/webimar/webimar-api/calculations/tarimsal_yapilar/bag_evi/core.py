# -*- coding: utf-8 -*-
"""
Bağ Evi hesaplama modülü - Ana hesaplama mantığı
"""

from . import config
from . import messages

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from . import config
from .performance import performance_monitor, cached_calculation
from calculations.utils.dikili_validasyon import validate_dikili_arazi_by_name, get_agac_turleri_listesi

logger = logging.getLogger(__name__)
from . import messages

@performance_monitor
@cached_calculation()
def bag_evi_universal_degerlendir(
    arazi_bilgileri: Dict[str, Any], 
    yapi_bilgileri: Dict[str, Any], 
    bag_evi_var_mi: bool = False, 
    manuel_kontrol_sonucu: Optional[str] = None,
    raw_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Genişletilmiş evrensel bağ evi değerlendirmesi
    Tüm arazi tiplerini destekler ve mümkün olduğunca genel mantık kullanır
    """
    logger.info("🚀 bag_evi_universal_degerlendir called")
    logger.debug("📋 Input arazi_bilgileri: %s", arazi_bilgileri)
    logger.debug("🏗️ Input yapi_bilgileri: %s", yapi_bilgileri)
    logger.debug("🏠 bag_evi_var_mi: %s", bag_evi_var_mi)
    logger.debug("🗺️ manuel_kontrol_sonucu: %s", manuel_kontrol_sonucu)
    
    # Aynı ilçede mevcut bağ evi kontrolü
    if bag_evi_var_mi:
        return {
            'success': False,
            'izin_durumu': 'izin_verilemez',
            'alan_detaylari': {},
            'agac_detaylari': {},
            'detay_mesaji': "Tarım Arazilerinde Yapılaşma Şartları Genelgesi'ne göre, her aile için aynı ilçe sınırları içerisinde sadece bir adet bağ evi izni verilebilir.",
            'ana_mesaj': "Tarım Arazilerinde Yapılaşma Şartları Genelgesi'ne göre, her aile için aynı ilçe sınırları içerisinde sadece bir adet bağ evi izni verilebilir."
        }

    # Arazi vasfını al
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', arazi_bilgileri.get('arazi_tipi', 'dikili_vasifli'))
    print(f"🔍 DEBUG - RAW arazi_vasfi from data: '{arazi_vasfi}'")
    print(f"🔍 DEBUG - arazi_bilgileri keys: {list(arazi_bilgileri.keys())}")
    print(f"🔍 DEBUG - ana_vasif value: '{arazi_bilgileri.get('ana_vasif')}'")
    print(f"🔍 DEBUG - arazi_tipi value: '{arazi_bilgileri.get('arazi_tipi')}'")
    logger.info("🏞️ Processing arazi vasfı: '%s'", arazi_vasfi)
    
    # Arazi vasfı validasyonu
    if arazi_vasfi is None:
        arazi_vasfi = 'dikili_vasifli'  # Default fallback
    elif not isinstance(arazi_vasfi, str):
        arazi_vasfi = str(arazi_vasfi)  # Convert to string
    
    # Config'den arazi tipi konfigürasyonunu al - CASE INSENSITIVE
    arazi_config = config.ARAZI_TIPI_KONFIGURASYONLARI.get(arazi_vasfi)
    
    if not arazi_config:
        # Case-insensitive fallback
        for key, value in config.ARAZI_TIPI_KONFIGURASYONLARI.items():
            if key.lower() == arazi_vasfi.lower():
                arazi_config = value
                arazi_vasfi = key  # Use canonical name
                break
    
    if not arazi_config:
        # Final fallback - default dikili vasıflı config
        arazi_config = config.ARAZI_TIPI_KONFIGURASYONLARI.get("dikili_vasifli", {})
        arazi_vasfi = "dikili_vasifli"
    
    logger.debug("🔍 Universal alan kontrolü - Config: %s", arazi_config)
    logger.debug("🔍 Arazi bilgileri: %s", arazi_bilgileri)
    
    # Alan kontrolü
    alan_kontrol_sonucu = _universal_alan_kontrolleri(arazi_bilgileri, arazi_config)
    logger.info("🎯 Alan kontrolü sonucu: %s", alan_kontrol_sonucu)
    
    # Mevcut yapı kontrolü
    mevcut_yapi_sonucu = _universal_mevcut_yapi_kontrolleri(yapi_bilgileri, arazi_config)
    logger.info("🏗️ Mevcut yapı kontrolü sonucu: %s", mevcut_yapi_sonucu)
    
        # Dikili arazi validasyonu (ağaç türü ve sayısı kontrolü)
    dikili_validasyon_sonucu = {}
    print(f"🔍 DEBUG - Arazi vasfı: '{arazi_vasfi}', contains dikili: {'dikili' in arazi_vasfi.lower()}")
    
    if 'dikili' in arazi_vasfi.lower():
        print("🌳 DEBUG - Dikili validasyon başlatılıyor...")
        dikili_validasyon_sonucu = _dikili_arazi_validasyonu(arazi_bilgileri, raw_data)
        print(f"🌳 DEBUG - Dikili validasyon sonucu: {dikili_validasyon_sonucu}")
        logger.info("🌳 Dikili arazi validasyonu sonucu: %s", dikili_validasyon_sonucu)
    else:
        logger.info("🌳 Dikili validasyon atlandı - arazi vasfı: %s", arazi_vasfi)
    
    # Zeytin ağacı kontrolleri (opsiyonel)
    agac_kontrol_sonucu = {}
    if arazi_config.get('zeytin_agac_kontrolu', False):
        agac_kontrol_sonucu = _universal_zeytin_agac_kontrolleri(
            arazi_bilgileri, arazi_config, manuel_kontrol_sonucu
        )
    
    # Sonuç belirleme - Dikili validasyon HER ZAMAN kontrol edilir
    # İlk olarak dikili validasyon kontrolü yap
    if dikili_validasyon_sonucu and not dikili_validasyon_sonucu.get('gecerli', True):
        # Dikili validasyon başarısız - direkt ret
        sonuc = {
            'izin_durumu': 'izin_verilemez',
            'neden': 'dikili_agac_yetersiz',
            'dikili_detay': dikili_validasyon_sonucu
        }
    elif manuel_kontrol_sonucu:
        # Dikili validasyon OK + Manuel kontrol var
        # Manuel kontrol sonucu dict ise dikili validasyon sonucuna göre karar ver
        if isinstance(manuel_kontrol_sonucu, dict):
            # Alan kontrolü her zaman önce değerlendirilir — hiçbir manuel onay bunu geçersiz kılamaz
            if not alan_kontrol_sonucu['yeterli']:
                manuel_kontrol_normalized = 'IZIN_VERILEMEZ'
            # Dict formatında eklenenAgaclar varsa ve dikili validasyon başarılıysa başarılı
            elif dikili_validasyon_sonucu and dikili_validasyon_sonucu.get('gecerli', False):
                manuel_kontrol_normalized = 'IZIN_VERILEBILIR'
            elif manuel_kontrol_sonucu.get('type') == 'success':
                manuel_kontrol_normalized = 'IZIN_VERILEBILIR'
            elif manuel_kontrol_sonucu.get('type') == 'error':
                manuel_kontrol_normalized = 'IZIN_VERILEMEZ'
            else:
                # eklenenAgaclar dict'i varsa ve dikili validasyon OK ise başarılı
                if 'eklenenAgaclar' in manuel_kontrol_sonucu and dikili_validasyon_sonucu and dikili_validasyon_sonucu.get('gecerli', False):
                    manuel_kontrol_normalized = 'IZIN_VERILEBILIR'
                else:
                    manuel_kontrol_normalized = str(manuel_kontrol_sonucu).upper()
        elif isinstance(manuel_kontrol_sonucu, str):
            manuel_kontrol_normalized = manuel_kontrol_sonucu.upper().strip()
        else:
            manuel_kontrol_normalized = str(manuel_kontrol_sonucu).upper().strip()
        
        print(f"🔍 DEBUG - manuel_kontrol_normalized: '{manuel_kontrol_normalized}'")
        print(f"🔍 DEBUG - dikili_validasyon_sonucu.gecerli: {dikili_validasyon_sonucu.get('gecerli') if dikili_validasyon_sonucu else None}")
        
        if manuel_kontrol_normalized in ['IZIN_VERILEBILIR', 'İZİN_VERİLEBİLİR']:
            sonuc = {
                'izin_durumu': 'izin_verilebilir_manuel',
                'neden': 'manuel_onay'
            }
        elif manuel_kontrol_normalized in ['IZIN_VERILEMEZ', 'İZİN_VERİLEMEZ']:
            sonuc = {
                'izin_durumu': 'izin_verilemez',
                'neden': 'manuel_red'
            }
        else:
            # Geçersiz manuel kontrol sonucu
            sonuc = {
                'izin_durumu': 'izin_verilemez',
                'neden': 'gecersiz_manuel_kontrol',
                'detay': f'Geçersiz manuel kontrol sonucu: {manuel_kontrol_sonucu}'
            }
    else:
        # Normal akış - manuel kontrol yok ve dikili validasyon OK
        if alan_kontrol_sonucu['yeterli'] and mevcut_yapi_sonucu['yeterli']:
            # Zeytin ağacı kontrolü (varsa)
            if arazi_config.get('zeytin_agac_kontrolu', False) and not agac_kontrol_sonucu.get('yeterli', True):
                sonuc = {
                    'izin_durumu': 'izin_verilemez',
                    'neden': 'zeytin_agac_yetersizligi'
                }
            else:
                sonuc = {
                    'izin_durumu': 'izin_verilebilir_varsayimsal',
                    'neden': 'alan_yeterli'
                }
        elif not alan_kontrol_sonucu['yeterli']:
            sonuc = {
                'izin_durumu': 'izin_verilemez',
                'neden': 'alan_yetersiz'
            }
        else:  # not mevcut_yapi_sonucu['yeterli']
            sonuc = {
                'izin_durumu': 'izin_verilemez',
                'neden': 'mevcut_yapi_fazla'
            }
    
    # Detaylı arazi değerlendirmesi ve mesaj oluşturma
    return _universal_arazi_degerlendirmesi(
        arazi_bilgileri, yapi_bilgileri, arazi_config, 
        manuel_kontrol_sonucu, sonuc, dikili_validasyon_sonucu
    )

def _universal_arazi_degerlendirmesi(
    arazi_bilgileri: Dict[str, Any], 
    yapi_bilgileri: Dict[str, Any], 
    config: Dict[str, Any], 
    manuel_kontrol_sonucu: Optional[str], 
    sonuc: Dict[str, Any],
    dikili_validasyon_sonucu: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Universal arazi değerlendirmesi ve mesaj oluşturma"""
    
    # Alan kontrollerini yeniden yap (mesaj için)
    alan_kontrol_sonucu = _universal_alan_kontrolleri(arazi_bilgileri, config)
    
    # Mevcut yapı kontrollerini yeniden yap (mesaj için)
    mevcut_yapi_sonucu = _universal_mevcut_yapi_kontrolleri(yapi_bilgileri, config)
    
    # Ağaç kontrollerini yap (eğer gerekiyorsa)
    agac_detaylari = {}
    if config.get('zeytin_agac_kontrolu', False):
        agac_detaylari = _universal_zeytin_agac_kontrolleri(
            arazi_bilgileri, config, manuel_kontrol_sonucu
        )
    
    # Mesaj oluştur
    if sonuc['izin_durumu'].startswith('izin_verilebilir'):
        detay_mesaji = _universal_basarili_mesaj_olustur(
            arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari, 
            manuel_kontrol_sonucu, mevcut_yapi_sonucu
        )
    else:
        detay_mesaji = _universal_basarisiz_mesaj_olustur(
            arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari, 
            manuel_kontrol_sonucu, mevcut_yapi_sonucu
        )
    
    return {
        'success': sonuc['izin_durumu'] not in ['izin_verilemez', 'alan_yetersiz', 'agac_yetersiz', 'dikili_validasyon_basarisiz'],
        'izin_durumu': sonuc['izin_durumu'],
        'detay_mesaji': detay_mesaji,
        'mesaj': detay_mesaji,  # HTML tablosu için eklendi
        'ana_mesaj': detay_mesaji,  # HTML tablosu için eklendi
        'alan_detaylari': alan_kontrol_sonucu.get('detaylar', {}),
        'agac_detaylari': agac_detaylari,
        'dikili_validasyon': dikili_validasyon_sonucu if dikili_validasyon_sonucu else None
    }

def _universal_alan_kontrolleri(arazi_bilgileri: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Evrensel alan kontrolü - tüm arazi tipleri için"""
    
    alan_tipleri = config.get('alan_tipleri', ['buyukluk_m2'])
    yeterli_alanlar = {}
    genel_yeterlilik = True
    
    # Arazi vasfına göre alan mapping'i
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', '')
    
    # Arazi vasfı validation
    if arazi_vasfi is None:
        arazi_vasfi = ''  # Empty string fallback
    elif not isinstance(arazi_vasfi, str):
        arazi_vasfi = str(arazi_vasfi)  # Convert to string
    
    buyukluk = float(arazi_bilgileri.get('buyukluk_m2', 0))
    
    for alan_tipi in alan_tipleri:
        logger.debug("🔍 Alan tipi: %s", alan_tipi)
        
        # Alan değerini arazi vasfına göre belirle
        if alan_tipi == 'dikili_alani':
            # Dikili vasıflı araziler için - sadece saf dikili vasfı durumunda buyukluk kullan
            if arazi_vasfi.lower() == 'dikili vasıflı':
                alan_degeri = buyukluk
            else:
                # Mixed types için dikili_alani field'ını kullan
                alan_degeri = float(arazi_bilgileri.get('dikili_alani', 0))
        elif alan_tipi == 'tarla_alani':
            # Tarla araziler için buyukluk_m2 = tarla_alani
            if arazi_vasfi.lower() == 'tarla':
                alan_degeri = buyukluk
            else:
                # Tarla + mixed types için tarla_alani field'ını kullan
                alan_degeri = float(arazi_bilgileri.get('tarla_alani', 0))
        else:
            # Diğer durumlar için direkt alan değeri
            alan_degeri = float(arazi_bilgileri.get(alan_tipi, buyukluk if alan_tipi in ['buyukluk_m2', 'alan_m2'] else 0))
        
        logger.debug("🔍 Alan tipi: %s, Değer: %s (vasıf: %s)", alan_tipi, alan_degeri, arazi_vasfi)
        minimum_alan = None
        alan_yeterli = True
        
        # Minimum alan gereksinimlerini kontrol et
        if alan_tipi == 'dikili_alani' and config.get('min_dikili_alan'):
            minimum_alan = config['min_dikili_alan']
            alan_yeterli = alan_degeri >= minimum_alan
            logger.debug("🔍 Dikili alan kontrolü: alan=%s, minimum=%s, yeterli=%s", 
                        alan_degeri, minimum_alan, alan_yeterli)
        elif alan_tipi == 'tarla_alani' and config.get('min_tarla_alan'):
            minimum_alan = config['min_tarla_alan']
            alan_yeterli = alan_degeri >= minimum_alan
            logger.debug("🔍 Tarla alan kontrolü: alan=%s, minimum=%s, yeterli=%s", 
                        alan_degeri, minimum_alan, alan_yeterli)
        elif alan_tipi in ['buyukluk_m2', 'alan_m2'] and config.get('min_toplam_alan'):
            minimum_alan = config['min_toplam_alan']
            alan_yeterli = alan_degeri >= minimum_alan
            logger.debug("🔍 Toplam alan kontrolü: alan=%s, minimum=%s, yeterli=%s", 
                        alan_degeri, minimum_alan, alan_yeterli)
        
        # Sonuçları kaydet
        yeterli_alanlar[_alan_tipi_to_display_name(alan_tipi)] = {
            'deger': alan_degeri,
            'minimum': minimum_alan,
            'yeterli': alan_yeterli
        }
        
        if not alan_yeterli:
            genel_yeterlilik = False
    
    # Özel durumlar için ekstra kontroller
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', '')
    
    # Arazi vasfı kontrolü - None veya numeric değerler için safe check
    if not isinstance(arazi_vasfi, str):
        arazi_vasfi = str(arazi_vasfi) if arazi_vasfi is not None else ''
    
    # Dikili vasıf - sadece dikili alan kontrolü
    if 'dikili' in arazi_vasfi.lower() and 'dikili_alani' in alan_tipleri:
        dikili_yeterli = yeterli_alanlar.get('Dikili Alanı', {}).get('yeterli', False)
        logger.debug("🔍 Dikili vasıf için sadece dikili alan kontrolü: %s", dikili_yeterli)
        return {
            'yeterli': dikili_yeterli,
            'detaylar': yeterli_alanlar
        }
    
    # Tarla vasıf - sadece tarla/toplam alan kontrolü  
    if arazi_vasfi.lower() == 'tarla':
        if 'tarla_alani' in [at for at in alan_tipleri]:
            tarla_yeterli = yeterli_alanlar.get('Tarla Alanı', {}).get('yeterli', False)
            logger.debug("🔍 Tarla vasfı için sadece tarla alanı kontrolü: %s", tarla_yeterli)
            return {
                'yeterli': tarla_yeterli,
                'detaylar': yeterli_alanlar
            }
        else:
            # Toplam alan kontrolü
            toplam_yeterli = yeterli_alanlar.get('Toplam Alan', {}).get('yeterli', False)
            logger.debug("🔍 Tarla vasfı için sadece tarla alanı kontrolü: %s", {toplam_yeterli})
            return {
                'yeterli': toplam_yeterli,
                'detaylar': {'toplam_alan': yeterli_alanlar.get('Toplam Alan', {})}
            }
    
    return {
        'yeterli': genel_yeterlilik,
        'detaylar': yeterli_alanlar
    }

def _universal_mevcut_yapi_kontrolleri(yapi_bilgileri: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """Mevcut yapı kontrolü - tüm arazi tipleri için"""
    if not yapi_bilgileri:
        yapi_bilgileri = {}
    
    mevcut_yapi_alani = float(yapi_bilgileri.get('mevcut_yapi_alani', 0))
    max_taban_alani = config.get('max_taban_alani', 30)  # Default 30m² (2025 güncellemesi)
    
    yapi_yeterli = mevcut_yapi_alani <= max_taban_alani
    
    logger.debug("🏗️ Mevcut yapı kontrolü: mevcut=%s, maksimum=%s, yeterli=%s", 
                mevcut_yapi_alani, max_taban_alani, yapi_yeterli)
    
    return {
        'yeterli': yapi_yeterli,
        'detay': {
            'mevcut_alan': mevcut_yapi_alani,
            'maksimum_alan': max_taban_alani,
            'kalan_alan': max_taban_alani - mevcut_yapi_alani if yapi_yeterli else 0
        }
    }

def _universal_zeytin_agac_kontrolleri(arazi_bilgileri, config, manuel_kontrol_sonucu=None):
    """Universal zeytin ağacı kontrolü"""
    # Simplified version for now
    return {'yeterli': True, 'detay': 'Ağaç kontrolü aktif değil'}

def _universal_basarili_mesaj_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari, 
                                      manuel_kontrol_sonucu, mevcut_yapi_sonucu=None):
    """Başarılı durum için güzel formatlanmış mesaj oluştur - eski sistem formatını kullanır"""
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', 'Bilinmeyen')
    
    return messages.render_success_message(
        arazi_vasfi=arazi_vasfi,
        alan_detay=alan_kontrol_sonucu.get('detaylar', {}),
        agac_detaylari=agac_detaylari.get('detay') if agac_detaylari else None,
        manuel_kontrol_sonucu=manuel_kontrol_sonucu,
        config=config
    )

def _universal_basarisiz_mesaj_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari, 
                                        manuel_kontrol_sonucu, mevcut_yapi_sonucu=None):
    """Başarısız durum için güzel formatlanmış mesaj oluştur - eski sistem formatını kullanır"""
    arazi_vasfi = arazi_bilgileri.get('ana_vasif', 'Bilinmeyen')
    
    return messages.render_failure_message(
        arazi_vasfi=arazi_vasfi,
        alan_detay=alan_kontrol_sonucu.get('detaylar', {}),
        agac_detaylari=agac_detaylari.get('detay') if agac_detaylari else None,
        manuel_kontrol_sonucu=manuel_kontrol_sonucu,
        config=config
    )

def _dikili_arazi_validasyonu(arazi_bilgileri, root_data=None):
    """
    Dikili arazi için ağaç türü ve sayısı validasyonu - Çoklu ağaç türü desteği ile
    """
    try:
        # Arazi bilgilerinden dikili alan ve ağaç bilgilerini al
        dikili_alan = arazi_bilgileri.get('dikili_alani', 0)
        if not dikili_alan:
            dikili_alan = arazi_bilgileri.get('alan_m2', 0)
        
        # Root data'dan da kontrol et
        if not dikili_alan and root_data:
            dikili_alan = root_data.get('dikili_alani', 0)
            if not dikili_alan:
                dikili_alan = root_data.get('alan_m2', 0)
        
        # Dekar'a çevir
        dikili_alan_dekar = float(dikili_alan) / 1000.0 if dikili_alan else 0
        
        print(f"🌳 DEBUG - dikili_alan: {dikili_alan}, alan_dekar: {dikili_alan_dekar}")
        print(f"🌳 DEBUG - arazi_bilgileri keys: {list(arazi_bilgileri.keys())}")
        print(f"🌳 DEBUG - root_data keys: {list(root_data.keys()) if root_data else 'None'}")
        
        logger.info("🌳 Dikili validasyon başlatıldı - Alan: %s m² (%s dekar)", 
                   dikili_alan, dikili_alan_dekar)
        
        # Önce manuel_kontrol_sonucu.eklenenAgaclar'dan çoklu ağaç kontrolü yap
        manuel_kontrol = arazi_bilgileri.get('manuel_kontrol_sonucu', {})
        
        # Root data'dan da kontrol et
        if not manuel_kontrol and root_data:
            manuel_kontrol = root_data.get('manuel_kontrol_sonucu', {})
        
        # Eğer manuel_kontrol string ise parse et
        if isinstance(manuel_kontrol, str):
            try:
                import json
                manuel_kontrol = json.loads(manuel_kontrol)
                print(f"🌳 DEBUG - Parsed manuel_kontrol from string: {manuel_kontrol}")
            except Exception as e:
                print(f"🌳 DEBUG - Failed to parse manuel_kontrol string: {manuel_kontrol}, error: {e}")
                manuel_kontrol = {}
        
        eklenen_agaclar = manuel_kontrol.get('eklenenAgaclar', []) if isinstance(manuel_kontrol, dict) else []
        
        print(f"🌳 DEBUG - manuel_kontrol: {manuel_kontrol}")
        print(f"🌳 DEBUG - eklenen_agaclar: {eklenen_agaclar}")
        print(f"🌳 DEBUG - eklenen_agaclar count: {len(eklenen_agaclar) if eklenen_agaclar else 0}")
        print(f"🌳 DEBUG - eklenen_agaclar type: {type(eklenen_agaclar)}")
        
        # Eğer eklenenAgaclar string ise parse et
        if isinstance(eklenen_agaclar, str):
            try:
                import json
                eklenen_agaclar = json.loads(eklenen_agaclar)
                print(f"🌳 DEBUG - Parsed eklenen_agaclar from string: {eklenen_agaclar}")
            except:
                print(f"🌳 DEBUG - Failed to parse eklenen_agaclar string: {eklenen_agaclar}")
                eklenen_agaclar = []
        
        if eklenen_agaclar and len(eklenen_agaclar) > 0:
            logger.info("🌳 Çoklu ağaç validasyonu başlatılıyor - %s ağaç türü", len(eklenen_agaclar))
            
            # Frontend'den gelen veriyi backend formatına dönüştür
            agac_bilgileri_listesi = []
            agac_turu_toplamlari = {}  # Aynı türlerin toplamını tutmak için
            toplam_agac_sayisi = 0  # Toplam ağaç sayısını başlat
            
            print(f"🌳 DEBUG - Raw eklenen_agaclar: {eklenen_agaclar}")
            
            for agac in eklenen_agaclar:
                agac_adi = agac.get('turAdi', agac.get('secilenAgacTuru', agac.get('agacTuru', ''))).strip()
                agac_sayisi = int(agac.get('agacSayisi', agac.get('sayi', 0)))
                agac_tipi = agac.get('secilenAgacTipi', agac.get('tipi', 'normal'))
                
                print(f"🌳 DEBUG - Raw agac object: {agac}")
                print(f"🌳 DEBUG - agac_adi: '{agac_adi}' (from turAdi: '{agac.get('turAdi')}', secilenAgacTuru: '{agac.get('secilenAgacTuru')}', agacTuru: '{agac.get('agacTuru')}')")
                print(f"🌳 DEBUG - agac_sayisi: {agac_sayisi} (from agacSayisi: '{agac.get('agacSayisi')}', sayi: '{agac.get('sayi')}')")
                print(f"🌳 DEBUG - agac_tipi: '{agac_tipi}' (from secilenAgacTipi: '{agac.get('secilenAgacTipi')}', tipi: '{agac.get('tipi')}')")
                
                if agac_adi and agac_sayisi > 0:
                    # Ağaç türünü ID'ye çevir
                    from calculations.utils.dikili_validasyon import find_agac_by_name
                    
                    agac_match = find_agac_by_name(agac_adi)
                    if agac_match:
                        agac_id, agac_info = agac_match
                        
                        # Ağaç çeşidini belirle
                        agac_cesidi = "normal"
                        if agac_tipi == "bodur":
                            agac_cesidi = "bodur"
                        elif agac_tipi == "yaribodur":
                            agac_cesidi = "yari_bodur"
                        
                        # Aynı ağaç türünün toplamını hesapla
                        key = (agac_id, agac_cesidi)
                        if key in agac_turu_toplamlari:
                            agac_turu_toplamlari[key]['sayi'] += agac_sayisi
                            print(f"🌳 DEBUG - Added to existing: {agac_adi} ({agac_cesidi}) - new total: {agac_turu_toplamlari[key]['sayi']}")
                        else:
                            agac_turu_toplamlari[key] = {
                                'sayi': agac_sayisi,
                                'adi': agac_adi,
                                'info': agac_info
                            }
                            print(f"🌳 DEBUG - New entry: {agac_adi} ({agac_cesidi}) - count: {agac_sayisi}")
                        
                        logger.info("🌳 Ağaç eklendi/toplandı: %s (%s) - %s adet (toplam: %s)", 
                                   agac_adi, agac_cesidi, agac_sayisi, agac_turu_toplamlari[key]['sayi'])
                    else:
                        logger.warning("⚠️ Tanınmayan ağaç türü: %s", agac_adi)
            
            # Toplanmış ağaç türlerini listeye çevir
            for (agac_id, agac_cesidi), toplam_bilgi in agac_turu_toplamlari.items():
                agac_bilgileri_listesi.append({
                    "agac_turu_id": agac_id,
                    "agac_sayisi": toplam_bilgi['sayi'],
                    "agac_cesidi": agac_cesidi,
                    "alan_orani": 1.0,  # Tüm alan için
                    "agac_adi": toplam_bilgi['adi']
                })
                
                toplam_agac_sayisi += toplam_bilgi['sayi']
            
        print(f"🌳 DEBUG - Final eklenen_agaclar: {eklenen_agaclar}")
        print(f"🌳 DEBUG - eklenen_agaclar count: {len(eklenen_agaclar) if eklenen_agaclar else 0}")
        print(f"🌳 DEBUG - eklenen_agaclar type: {type(eklenen_agaclar)}")
        
        # Her bir ağacı detaylı logla
        for i, agac in enumerate(eklenen_agaclar or []):
            print(f"🌳 DEBUG - Agac {i}: {agac}")
            print(f"🌳 DEBUG - Agac {i} keys: {list(agac.keys()) if isinstance(agac, dict) else 'Not dict'}")
        
        if eklenen_agaclar and len(eklenen_agaclar) > 0:
            print(f"🌳 DEBUG - Final agac_bilgileri_listesi: {agac_bilgileri_listesi}")
            print(f"🌳 DEBUG - Final toplam_agac_sayisi: {toplam_agac_sayisi}")
            
            if agac_bilgileri_listesi:
                # Çoklu ağaç validasyonu yap
                from calculations.utils.dikili_validasyon import validate_multiple_agac_turleri
                
                all_valid, messages, summary = validate_multiple_agac_turleri(
                    dikili_alan_dekar, agac_bilgileri_listesi
                )
                
                logger.info("🌳 Çoklu ağaç validasyon sonucu: %s geçerli, %s geçersiz", 
                           summary['gecerli_olanlar'], summary['gecersiz_olanlar'])
                
                # Detaylı sonuç oluştur
                detaylar = {
                    'toplam_agac_sayisi': toplam_agac_sayisi,
                    'agac_turleri': len(agac_bilgileri_listesi),
                    'alan_dekar': dikili_alan_dekar,
                    'validasyon_sonucu': summary,
                    'agac_detaylari': agac_bilgileri_listesi
                }
                
                if all_valid:
                    mesaj = f"✅ Tüm ağaç türleri için dikili kriterler karşılanıyor. Toplam {toplam_agac_sayisi} ağaç, {len(agac_bilgileri_listesi)} farklı tür."
                else:
                    gecerli_sayisi = summary['gecerli_olanlar']
                    gecersiz_sayisi = summary['gecersiz_olanlar']
                    mesaj = f"❌ {gecersiz_sayisi} ağaç türü kriterleri karşılamıyor. {gecerli_sayisi} geçerli, {gecersiz_sayisi} geçersiz."
                
                return {
                    'gecerli': all_valid,
                    'mesaj': mesaj,
                    'detay': detaylar,
                    'minimum_gereksinim': 0,  # Çoklu validasyonda anlamlı değil
                    'mevcut_sayisi': toplam_agac_sayisi,
                    'alan_dekar': dikili_alan_dekar,
                    'coklu_agac_validasyonu': True
                }
            else:
                logger.warning("⚠️ Geçerli ağaç bilgisi bulunamadı")
        
        # Eski tekil ağaç validasyonu (fallback)
        logger.info("🌳 Tekil ağaç validasyonuna geçiliyor (fallback)")
        
        # Ağaç bilgilerini al - önce arazi_bilgileri içinden, sonra root_data'dan
        agac_bilgileri = arazi_bilgileri.get('agac_bilgileri', {})
        if not agac_bilgileri and root_data:
            agac_bilgileri = root_data.get('agac_bilgileri', {})
        
        agac_turu = agac_bilgileri.get('turu', '').lower() if agac_bilgileri else ''
        agac_sayisi = agac_bilgileri.get('sayisi', 0) if agac_bilgileri else 0
        
        print(f"🌳 DEBUG - agac_bilgileri: {agac_bilgileri}")
        print(f"🌳 DEBUG - agac_turu: '{agac_turu}'")
        print(f"🌳 DEBUG - agac_sayisi: {agac_sayisi}")
        print(f"🌳 DEBUG - Empty check: turu empty={not agac_turu}, sayisi zero={not agac_sayisi}")
        
        logger.info("🌳 Tekil dikili validasyon - Alan: %s dekar, Ağaç türü: %s, Sayı: %s", 
                   dikili_alan_dekar, agac_turu, agac_sayisi)
        
        # Eğer ağaç bilgisi yoksa, sadece uyarı ver ama geçerli say
        if not agac_turu or not agac_sayisi:
            logger.warning("⚠️ Dikili arazi için ağaç bilgisi eksik - validasyon atlanıyor")
            return {
                'gecerli': True,
                'uyari': 'Ağaç türü ve sayısı bilgisi eksik - manuel kontrol önerilir',
                'detay': 'Dikili arazi validasyonu için ağaç bilgileri gereklidir'
            }
        
        # Tekil ağaç validasyonu yap
        from calculations.utils.dikili_validasyon import validate_dikili_arazi_by_name
        validasyon_sonucu = validate_dikili_arazi_by_name(agac_turu, agac_sayisi, dikili_alan_dekar)
        
        logger.info("🌳 Tekil dikili validasyon sonucu: %s", validasyon_sonucu)
        
        return {
            'gecerli': validasyon_sonucu['gecerli'],
            'mesaj': validasyon_sonucu.get('mesaj', ''),
            'detay': validasyon_sonucu.get('detay', {}),
            'minimum_gereksinim': validasyon_sonucu.get('minimum_gereksinim', 0),
            'mevcut_sayisi': agac_sayisi,
            'alan_dekar': dikili_alan_dekar,
            'coklu_agac_validasyonu': False
        }
        
    except Exception as e:
        logger.error("❌ Dikili validasyon hatası: %s", str(e))
        return {
            'gecerli': True,  # Hata durumunda geçerli say
            'hata': f'Dikili validasyon hatası: {str(e)}',
            'uyari': 'Validasyon hatası nedeniyle manuel kontrol önerilir'
        }

def _alan_tipi_to_display_name(alan_tipi):
    """Alan tipi kodunu görüntü adına çevir"""
    mapping = {
        'dikili_alani': 'Dikili Alanı',
        'tarla_alani': 'Tarla Alanı', 
        'buyukluk_m2': 'Toplam Alan',
        'alan_m2': 'Toplam Alan',
        'zeytinlik_alani': 'Zeytinlik Alanı'
    }
    return mapping.get(alan_tipi, alan_tipi.title())

# Public API functions - backwards compatibility
def bag_evi_degerlendir(arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi=False, manuel_kontrol_sonucu=None):
    """Main public API - uses universal function"""
    return bag_evi_universal_degerlendir(
        arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi, manuel_kontrol_sonucu
    )

def bag_evi_ana_hesaplama(arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi=False, manuel_kontrol_sonucu=None):
    """Alternative API name - same functionality"""
    return bag_evi_universal_degerlendir(
        arazi_bilgileri, yapi_bilgileri, bag_evi_var_mi, manuel_kontrol_sonucu
    )
