"""
Tarımsal Amaçlı Depo hesaplama modülü
Talimat Madde 7.1-7.4 uygulaması

ÖNEMLİ KAVRAMSAL AYRM:
- %1 = DEPO YAPMA HAKKI: İlçe genelindeki toplam arazi varlığının %1'i kadar
  alana tarımsal depo yapılabilir. Bu bir EMSAL değildir.
- EMSAL = Belediye plan notları tarafından belirlenir. Biz hesaplamıyoruz.
- Minimum arazi büyüklüğü: Parselin arazi vasfına göre ayrı kontrol.

Madde 7.2: Kiralama/sözleşmeli üretim arazileri hesaba katılmaz.
Madde 7.3: Hisseli parsellerde hisse oranı dikkate alınır.
"""

# Bağ evi modülünden zeytin kontrol fonksiyonları
try:
    from .bag_evi import _universal_zeytin_agac_kontrolleri
except ImportError as e:
    print(f"⚠️ Uyarı: Bağ evi modülü import hatası: {e}")
    def _universal_zeytin_agac_kontrolleri(arazi_bilgileri, config):
        """Fallback fonksiyon - zeytin kontrolü yapılmaz"""
        return True, "Zeytin kontrolü devre dışı (import hatası)"

# Minimum arazi büyüklüğü kuralları - Talimat Madde 7.1
DEPO_MIN_ARAZI_DIKILI = 10000   # Dikili tarım arazisi: 1 hektar
DEPO_MIN_ARAZI_MUTLAK = 20000   # Mutlak, özel ürün ve marjinal: 2 hektar
DEPO_MIN_ARAZI_MARJINAL = 20000  # Marjinal Tarım Arazisi: 2 hektar
DEPO_MIN_ARAZI_ORTU_ALTI = 3000  # Örtüaltı/Sera: 0,3 hektar

# Depo hakkı oranı - Talimat Madde 7.1
# "toplam arazi varlığının %1'i kadar alana yapılabilir"
# NOT: Bu bir emsal DEĞİLDİR. Toplam ilçe arazi varlığının %1'i = depo yapma hakkı.
DEPO_HAK_ORANI = 0.01   # %1

# Arazi tipi konfigürasyonları - Talimat Madde 7.1
DEPO_ARAZI_TIPI_KONFIGURASYONLARI = {
    "Dikili vasıflı": {
        "min_alan": DEPO_MIN_ARAZI_DIKILI,   # 1 ha
        "alan_anahtar": "dikili_alani",
        "kriter_mesaji": "Dikili alan kontrolü (min 1 ha)",
        "zeytin_agac_kontrolu": False
    },
    "Tarla": {
        "min_alan": DEPO_MIN_ARAZI_MUTLAK,   # 2 ha
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Mutlak/marjinal/özel ürün tarım arazisi kontrolü (min 2 ha)",
        "zeytin_agac_kontrolu": False
    },
    "Örtüaltı tarım": {
        "min_alan": DEPO_MIN_ARAZI_ORTU_ALTI,  # 0,3 ha
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Örtüaltı tarım alanı kontrolü (min 0,3 ha)",
        "zeytin_agac_kontrolu": False
    },
    "Sera": {
        "min_alan": DEPO_MIN_ARAZI_ORTU_ALTI,  # 0,3 ha
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Sera alanı kontrolü (min 0,3 ha)",
        "zeytin_agac_kontrolu": False
    },
    "Zeytin ağaçlı + tarla": {
        "min_alan": DEPO_MIN_ARAZI_MUTLAK,   # 2 ha
        "alan_anahtar": "tarla_alani",
        "kriter_mesaji": "Zeytin ağaçlı tarla kontrolü (min 2 ha)",
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 10,
        "agac_alan_anahtari": "zeytin_alani"
    }
}


def calculate_tarimsal_amacli_depo(alan, emsal_orani=None):
    """
    ESKİ UYUMLULUK FONKSİYONU - Geriye uyumluluk için korundu
    Yeni sistemde tarimsal_depo_degerlendir kullanılmalı
    """
    print("⚠️  UYARI: Eski calculate_tarimsal_amacli_depo fonksiyonu kullanılıyor")
    print("🔄 Yeni tarimsal_depo_degerlendir fonksiyonuna yönlendiriliyor")
    
    arazi_bilgileri = {
        "buyukluk_m2": alan,
        "ana_vasif": "Tarla",
        "toplam_arazi_varligi": alan  # Eski API'de parsel alanı = toplam varsay
    }
    
    yapi_bilgileri = {}
    return tarimsal_depo_degerlendir(arazi_bilgileri, yapi_bilgileri)


def tarimsal_depo_degerlendir(arazi_bilgileri, yapi_bilgileri, manuel_kontrol_sonucu=None):
    """
    Tarımsal Amaçlı Depo değerlendirme fonksiyonu - Talimat Madde 7.1-7.4

    İki ayrı kontrol yapar:
    1) Parselin minimum arazi büyüklüğü şartını karşılayıp karşılamadığı
    2) İlçe genelindeki toplam arazi varlığının %1'i = depo yapma hakkı (m²)

    NOT: Fiili yapı alanı belediye plan notlarındaki emsal oranına göre belirlenir.
    Biz sadece mevzuat kapsamında "depo yapma hakkı"nı hesaplıyoruz.
    """
    print(f"🏬 tarimsal_depo_degerlendir ÇAĞRILDI")
    print(f"📋 Gelen arazi_bilgileri: {arazi_bilgileri}")
    print(f"🏗️ Gelen yapi_bilgileri: {yapi_bilgileri}")
    
    sonuc = {
        "success": True,
        "izin_durumu": "belirtilmedi",
        "ana_mesaj": "",
        "mesaj": "",
        "maksimum_insaat_alani_m2": 0
    }
    
    try:
        arazi_vasfi = arazi_bilgileri.get("ana_vasif", "")
        toplam_arazi_varligi = float(arazi_bilgileri.get("toplam_arazi_varligi", 0))
        print(f"🏞️ Arazi vasfı: '{arazi_vasfi}', Toplam arazi varlığı: {toplam_arazi_varligi} m²")
        
        # Toplam arazi varlığı kontrolü
        if toplam_arazi_varligi <= 0:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["ana_mesaj"] = "İlçe genelindeki toplam arazi varlığı bilgisi girilmedi veya geçersiz."
            return sonuc
        
        # Arazi tipi konfigürasyonunu al
        if arazi_vasfi not in DEPO_ARAZI_TIPI_KONFIGURASYONLARI:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["ana_mesaj"] = f"Depo yapımı için arazi vasfı uygun değil. Mevcut arazi vasfınız: {arazi_vasfi}"
            return sonuc
        
        config = DEPO_ARAZI_TIPI_KONFIGURASYONLARI[arazi_vasfi]
        
        # 1) Parselin minimum arazi büyüklüğü kontrolü
        alan_kontrol_sonucu = _depo_alan_kontrolleri(arazi_bilgileri, config)
        
        # 2) Depo hakkı hesabı: toplam arazi varlığının %1'i
        depo_hakki_m2 = toplam_arazi_varligi * DEPO_HAK_ORANI
        
        # Zeytinlik kontrolleri (gerekiyorsa)
        agac_kontrol_sonucu = True
        agac_detaylari = ""
        if config.get("zeytin_agac_kontrolu", False):
            agac_kontrol_sonucu, agac_detaylari = _universal_zeytin_agac_kontrolleri(arazi_bilgileri, config)
            print(f"🫒 Zeytin ağacı kontrolü sonucu: {agac_kontrol_sonucu} - {agac_detaylari}")
        
        # Genel değerlendirme
        genel_yeterli = alan_kontrol_sonucu["yeterli"] and agac_kontrol_sonucu
        
        if genel_yeterli:
            sonuc = _depo_basarili_sonuc_olustur(
                arazi_bilgileri, config, alan_kontrol_sonucu,
                toplam_arazi_varligi, depo_hakki_m2, agac_detaylari
            )
        else:
            sonuc = _depo_basarisiz_sonuc_olustur(
                arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari
            )
    
    except Exception as e:
        sonuc["ana_mesaj"] = f"Hesaplama sırasında hata oluştu: {str(e)}"
        sonuc["izin_durumu"] = "izin_verilemez"
        print(f"❌ Depo hesaplama hatası: {e}")
    
    return sonuc


def _depo_alan_kontrolleri(arazi_bilgileri, config):
    """Parselin minimum arazi büyüklüğü kontrolü"""
    sonuc = {"yeterli": False, "detaylar": {}}
    
    min_alan = config["min_alan"]
    alan_anahtar = config["alan_anahtar"]
    
    # Alan değerini al
    mevcut_alan = arazi_bilgileri.get(alan_anahtar, 0)
    if mevcut_alan == 0:
        mevcut_alan = arazi_bilgileri.get("buyukluk_m2", 0)
    
    mevcut_alan = float(mevcut_alan)
    print(f"📏 Minimum alan: {min_alan} m², Mevcut alan: {mevcut_alan} m² (anahtar: {alan_anahtar})")
    
    if mevcut_alan >= min_alan:
        sonuc["yeterli"] = True
        sonuc["detaylar"] = {
            "mevcut_alan": mevcut_alan,
            "min_alan": min_alan,
            "fazla_alan": mevcut_alan - min_alan
        }
    else:
        sonuc["detaylar"] = {
            "mevcut_alan": mevcut_alan,
            "min_alan": min_alan,
            "eksik_alan": min_alan - mevcut_alan
        }
    
    return sonuc


def _depo_basarili_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu,
                                  toplam_arazi_varligi, depo_hakki_m2, agac_detaylari=""):
    """Başarılı depo sonucu oluştur — min alan sağlandı, depo hakkı hesaplandı"""
    detaylar = alan_kontrol_sonucu["detaylar"]
    mevcut_alan = detaylar["mevcut_alan"]
    toplam_dekar = toplam_arazi_varligi / 1000
    depo_hakki_dekar = depo_hakki_m2 / 1000
    
    ana_mesaj = "TARIMSAL DEPO YAPILABİLİR"
    
    html_mesaj = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h4 style="color: #155724; margin-top: 0;">🏬 Tarımsal Amaçlı Depo Hesaplama Sonucu</h4>
        <p><strong>Sonuç:</strong> {ana_mesaj}</p>
        
        <div style="margin: 15px 0;">
            <h5 style="color: #155724;">📊 Parsel Bilgileri:</h5>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Parsel Alanı:</strong> {mevcut_alan:,.0f} m²</li>
                <li><strong>Arazi Vasfı:</strong> {arazi_bilgileri.get('ana_vasif', '')}</li>
                <li><strong>Minimum Alan Şartı:</strong> ✅ Sağlanıyor ({config['min_alan']:,.0f} m² gerekli)</li>
            </ul>
        </div>
        
        <div style="margin: 15px 0;">
            <h5 style="color: #155724;">🏗️ Depo Yapma Hakkı (Talimat Md. 7.1):</h5>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>İlçe İçi Toplam Arazi Varlığı:</strong> {toplam_arazi_varligi:,.0f} m² ({toplam_dekar:,.1f} dekar)</li>
                <li><strong>Depo Hakkı (%1):</strong> <span style="font-size: 1.1em; color: #155724; font-weight: bold;">{depo_hakki_m2:,.1f} m² ({depo_hakki_dekar:,.2f} dekar)</span></li>
            </ul>
        </div>
        
        {f'<div style="margin: 15px 0;"><p style="color: #856404;"><strong>🫒 Zeytin Ağacı Kontrolü:</strong> {agac_detaylari}</p></div>' if agac_detaylari else ''}
        
        <div style="background-color: #cff4fc; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #0dcaf0;">
            <p style="margin: 0; font-weight: bold; color: #055160;">ℹ️ Önemli Bilgi</p>
            <p style="margin: 5px 0 0 0; color: #055160;">
                Depo hakkı ({depo_hakki_m2:,.1f} m²), toplam arazi varlığınızın %1'i kadardır. 
                Fiili yapım alanı, belediye plan notlarındaki emsal oranına göre belirlenir.
                Kiralama/sözleşmeli üretim arazileri hesaba dahil edilmez. 
                Hisseli parsellerde hisse oranı dikkate alınır.
            </p>
        </div>
    </div>
</div>
    """.strip()
    
    return {
        "success": True,
        "izin_durumu": "izin_verilebilir",
        "ana_mesaj": ana_mesaj,
        "mesaj": html_mesaj,
        "maksimum_insaat_alani_m2": round(depo_hakki_m2, 1),
        "arazi_alani": mevcut_alan,
        "toplam_arazi_varligi": toplam_arazi_varligi,
        "depo_hakki_m2": round(depo_hakki_m2, 1),
        "depo_hakki_dekar": round(depo_hakki_dekar, 2),
        "min_alan_sarti": "✅ Sağlanıyor",
        "zeytin_kontrol": agac_detaylari if agac_detaylari else "Gerekmiyor"
    }


def _depo_basarisiz_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari=""):
    """Başarısız depo sonucu oluştur"""
    detaylar = alan_kontrol_sonucu["detaylar"]
    
    if not alan_kontrol_sonucu["yeterli"]:
        neden = f"Minimum arazi alanı ({config['min_alan']:,.0f} m²) sağlanmıyor"
        eksik_alan = detaylar.get("eksik_alan", 0)
        detay_mesaji = f"Eksik alan: {eksik_alan:,.0f} m²"
    elif agac_detaylari and "uygun değil" in agac_detaylari:
        neden = "Zeytin ağacı yoğunluğu çok fazla"
        detay_mesaji = agac_detaylari
    else:
        neden = "Bilinmeyen bir sorun"
        detay_mesaji = ""
    
    ana_mesaj = f"TARIMSAL DEPO YAPILAMAZ - {neden}"
    
    html_mesaj = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h4 style="color: #721c24; margin-top: 0;">🏬 Tarımsal Amaçlı Depo Hesaplama Sonucu</h4>
        <p><strong>Sonuç:</strong> {ana_mesaj}</p>
        
        <div style="margin: 15px 0;">
            <h5 style="color: #721c24;">❌ Sorun Detayları:</h5>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Mevcut Alan:</strong> {detaylar.get('mevcut_alan', 0):,.0f} m²</li>
                <li><strong>Gerekli Minimum Alan:</strong> {config['min_alan']:,.0f} m²</li>
                <li><strong>Sorun:</strong> {detay_mesaji}</li>
            </ul>
        </div>
        
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107;">
            <p style="margin: 0; font-weight: bold; color: #856404;">💡 Çözüm Önerisi</p>
            <p style="margin: 5px 0 0 0; color: #856404;">
                {'Arazi alanını artırın veya uygun vasfta arazi bulun.' if not alan_kontrol_sonucu["yeterli"] else 'Zeytin ağacı yoğunluğunu azaltın (dekara maksimum 10 adet).'}
            </p>
        </div>
    </div>
</div>
    """.strip()
    
    return {
        "success": False,
        "izin_durumu": "izin_verilemez", 
        "ana_mesaj": ana_mesaj,
        "mesaj": html_mesaj,
        "mevcut_alan_m2": detaylar.get('mevcut_alan', 0),
        "gerekli_minimum_alan_m2": config['min_alan'],
        "sorun_detay": detay_mesaji,
        "neden": neden,
        "maksimum_insaat_alani_m2": 0
    }
