"""
Tarımsal Amaçlı Depo hesaplama modülü
MD dosyası gereksinimlerine göre tam yeniden yazılmış
Bağ evi modülü mantığıyla dinamik emsal ve minimum arazi sistemi
"""

# Bağ evi modülünden zeytin kontrol fonksiyonları
try:
    from .bag_evi import _universal_zeytin_agac_kontrolleri
except ImportError as e:
    print(f"⚠️ Uyarı: Bağ evi modülü import hatası: {e}")
    def _universal_zeytin_agac_kontrolleri(arazi_bilgileri, config):
        """Fallback fonksiyon - zeytin kontrolü yapılmaz"""
        return True, "Zeytin kontrolü devre dışı (import hatası)"

# Minimum arazi büyüklüğü kuralları (MD dosyası)
DEPO_MIN_ARAZI_DIKILI = 5000   # Dikili, Mutlak ve Özel Ürün Arazisi
DEPO_MIN_ARAZI_MARJINAL = 20000  # Marjinal Tarım Arazisi (Tarla)
DEPO_MIN_ARAZI_ORTU_ALTI = 3000  # Örtüaltı/Sera

# Emsal oranları (MD dosyası)
DEPO_EMSAL_DIKILI = 0.05   # %5 - Dikili, Mutlak ve Özel Ürün Arazisi
DEPO_EMSAL_MARJINAL = 0.20  # %20 - Marjinal Tarım Arazisi (Tarla)

# Arazi tipi konfigürasyonları - Bağ Evi modülü mantığıyla
DEPO_ARAZI_TIPI_KONFIGURASYONLARI = {
    "Dikili vasıflı": {
        "min_alan": DEPO_MIN_ARAZI_DIKILI,
        "emsal_orani": DEPO_EMSAL_DIKILI,
        "alan_anahtar": "dikili_alani",
        "kriter_mesaji": "Dikili alan kontrolü",
        "zeytin_agac_kontrolu": False
    },
    "Tarla": {
        "min_alan": DEPO_MIN_ARAZI_MARJINAL,
        "emsal_orani": DEPO_EMSAL_MARJINAL,
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Marjinal tarım arazisi (Tarla) kontrolü",
        "zeytin_agac_kontrolu": False
    },
    "Örtüaltı tarım": {
        "min_alan": DEPO_MIN_ARAZI_ORTU_ALTI,
        "emsal_orani": DEPO_EMSAL_DIKILI,  # Dikili ile aynı %5
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Örtüaltı tarım alanı kontrolü",
        "zeytin_agac_kontrolu": False
    },
    "Sera": {
        "min_alan": DEPO_MIN_ARAZI_ORTU_ALTI,
        "emsal_orani": DEPO_EMSAL_DIKILI,  # Dikili ile aynı %5
        "alan_anahtar": "buyukluk_m2",
        "kriter_mesaji": "Sera alanı kontrolü",
        "zeytin_agac_kontrolu": False
    },
    "Zeytin ağaçlı + tarla": {
        "min_alan": DEPO_MIN_ARAZI_MARJINAL,
        "emsal_orani": DEPO_EMSAL_MARJINAL,
        "alan_anahtar": "tarla_alani",
        "kriter_mesaji": "Zeytin ağaçlı tarla kontrolü",
        "zeytin_agac_kontrolu": True,
        "max_zeytin_yogunlugu": 10,
        "agac_alan_anahtari": "zeytin_alani"
    }
}


def calculate_tarimsal_amacli_depo(alan, emsal_orani=None):
    """
    ESKİ UYUMLULUK FONKSİYONU - Geriye uyumluluk için korundu
    Yeni sistemde tarimsal_depo_degerlendir kullanılmalı
    
    Args:
        alan (float): Arazi alanı (m²)
        emsal_orani (float): Emsal oranı (opsiyonel)
        
    Returns:
        dict: Hesaplama sonuçları
    """
    print("⚠️  UYARI: Eski calculate_tarimsal_amacli_depo fonksiyonu kullanılıyor")
    print("🔄 Yeni tarimsal_depo_degerlendir fonksiyonuna yönlendiriliyor")
    
    # Eski sistemi yeni sisteme dönüştür
    arazi_bilgileri = {
        "buyukluk_m2": alan,
        "ana_vasif": "Tarla" if emsal_orani == 0.20 else "Dikili vasıflı"
    }
    
    yapi_bilgileri = {"depo_alani": alan * (emsal_orani or 0.20)}
    
    # Yeni sistem fonksiyonunu çağır
    return tarimsal_depo_degerlendir(arazi_bilgileri, yapi_bilgileri)


def tarimsal_depo_degerlendir(arazi_bilgileri, yapi_bilgileri, manuel_kontrol_sonucu=None):
    """
    Tarımsal Amaçlı Depo değerlendirme fonksiyonu - MD dokümantasyonu uygulaması
    Bağ evi modülü mantığıyla dinamik emsal ve minimum arazi sistemi
    
    Args:
        arazi_bilgileri: Arazi detaylarını içeren sözlük
        yapi_bilgileri: Yapı detaylarını içeren sözlük (kullanılmıyor, sadece uyumluluk için)
        manuel_kontrol_sonucu: Opsiyonel manuel kontrol sonucu
        
    Returns:
        dict: Değerlendirme sonucunu içeren sözlük
    """
    # Debug log
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
        print(f"🏞️ Arazi vasfı: '{arazi_vasfi}'")
        
        # Arazi tipi konfigürasyonunu al
        if arazi_vasfi not in DEPO_ARAZI_TIPI_KONFIGURASYONLARI:
            sonuc["izin_durumu"] = "izin_verilemez"
            sonuc["ana_mesaj"] = f"Depo yapımı için arazi vasfı uygun değil. Mevcut arazi vasfınız: {arazi_vasfi}"
            return sonuc
        
        config = DEPO_ARAZI_TIPI_KONFIGURASYONLARI[arazi_vasfi]
        
        # Alan kontrolü
        alan_kontrol_sonucu = _depo_alan_kontrolleri(arazi_bilgileri, config)
        
        # Zeytinlik kontrolleri (gerekiyorsa)
        agac_kontrol_sonucu = True
        agac_detaylari = ""
        if config.get("zeytin_agac_kontrolu", False):
            # Bağ evi modülündeki zeytin kontrol mantığını kullan
            agac_kontrol_sonucu, agac_detaylari = _universal_zeytin_agac_kontrolleri(arazi_bilgileri, config)
            print(f"🫒 Zeytin ağacı kontrolü sonucu: {agac_kontrol_sonucu} - {agac_detaylari}")
        
        # Genel değerlendirme
        genel_yeterli = alan_kontrol_sonucu["yeterli"] and agac_kontrol_sonucu
        
        if genel_yeterli:
            sonuc = _depo_basarili_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari)
        else:
            sonuc = _depo_basarisiz_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari)
    
    except Exception as e:
        sonuc["ana_mesaj"] = f"Hesaplama sırasında hata oluştu: {str(e)}"
        sonuc["izin_durumu"] = "izin_verilemez"
        print(f"❌ Depo hesaplama hatası: {e}")
    
    return sonuc


def _depo_alan_kontrolleri(arazi_bilgileri, config):
    """Depo için alan kontrolü fonksiyonu"""
    sonuc = {"yeterli": False, "detaylar": {}}
    
    print(f"🔍 Depo alan kontrolü - Config: {config}")
    print(f"🔍 Arazi bilgileri: {arazi_bilgileri}")
    
    min_alan = config["min_alan"]
    alan_anahtar = config["alan_anahtar"]
    
    # Alan değerini al
    mevcut_alan = arazi_bilgileri.get(alan_anahtar, 0)
    if mevcut_alan == 0:
        # Alternatif anahtar dene
        mevcut_alan = arazi_bilgileri.get("buyukluk_m2", 0)
    
    print(f"📏 Minimum alan: {min_alan} m², Mevcut alan: {mevcut_alan} m² (anahtar: {alan_anahtar})")
    
    if mevcut_alan >= min_alan:
        sonuc["yeterli"] = True
        sonuc["detaylar"] = {
            "mevcut_alan": mevcut_alan,
            "min_alan": min_alan,
            "fazla_alan": mevcut_alan - min_alan,
            "emsal_orani": config["emsal_orani"],
            "maksimum_depo_alani": mevcut_alan * config["emsal_orani"]
        }
    else:
        sonuc["detaylar"] = {
            "mevcut_alan": mevcut_alan,
            "min_alan": min_alan,
            "eksik_alan": min_alan - mevcut_alan
        }
    
    return sonuc


def _depo_basarili_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari=""):
    """Başarılı depo sonucu oluştur"""
    detaylar = alan_kontrol_sonucu["detaylar"]
    mevcut_alan = detaylar["mevcut_alan"]
    emsal_orani = config["emsal_orani"]
    maksimum_depo_alani = detaylar["maksimum_depo_alani"]
    
    # Ana mesaj
    ana_mesaj = f"TARIMSAL DEPO YAPILABİLİR"
    
    # HTML mesaj oluştur
    html_mesaj = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h4 style="color: #155724; margin-top: 0;">🏬 Tarımsal Amaçlı Depo Hesaplama Sonucu</h4>
        <p><strong>Sonuç:</strong> {ana_mesaj}</p>
        
        <div style="margin: 15px 0;">
            <h5 style="color: #155724;">📊 Alan ve Emsal Detayları:</h5>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Arazi Alanı:</strong> {mevcut_alan:,.0f} m²</li>
                <li><strong>Arazi Vasfı:</strong> {arazi_bilgileri.get('ana_vasif', '')}</li>
                <li><strong>Emsal Oranı:</strong> {emsal_orani*100:.0f}%</li>
                <li><strong>Maksimum Depo Alanı:</strong> {maksimum_depo_alani:,.1f} m²</li>
                <li><strong>Minimum Alan Şartı:</strong> ✅ Sağlanıyor</li>
            </ul>
        </div>
        
        {f'<div style="margin: 15px 0;"><p style="color: #856404;"><strong>🫒 Zeytin Ağacı Kontrolü:</strong> {agac_detaylari}</p></div>' if agac_detaylari else ''}
        
        <div style="background-color: #cff4fc; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #0dcaf0;">
            <p style="margin: 0; font-weight: bold; color: #055160;">ℹ️ MD Dokümantasyonu Uygulaması</p>
            <p style="margin: 5px 0 0 0; color: #055160;">Bu değerlendirme Bağ Evi modülü mantığıyla dinamik emsal sistemi kullanır.</p>
        </div>
    </div>
</div>
    """.strip()
    
    return {
        "success": True,
        "izin_durumu": "izin_verilebilir",
        "ana_mesaj": ana_mesaj,
        "mesaj": html_mesaj,
        "maksimum_insaat_alani_m2": round(maksimum_depo_alani, 1),
        "arazi_alani": mevcut_alan,
        "emsal_orani_yuzde": f"{emsal_orani*100:.0f}%",
        "maksimum_depo_alani": round(maksimum_depo_alani, 1),
        "min_alan_sarti": "✅ Sağlanıyor",
        "zeytin_kontrol": agac_detaylari if agac_detaylari else "Gerekmiyor"
    }


def _depo_basarisiz_sonuc_olustur(arazi_bilgileri, config, alan_kontrol_sonucu, agac_detaylari=""):
    """Başarısız depo sonucu oluştur"""
    detaylar = alan_kontrol_sonucu["detaylar"]
    
    # Başarısızlık nedenini belirle
    if not alan_kontrol_sonucu["yeterli"]:
        neden = f"Minimum arazi alanı ({config['min_alan']} m²) sağlanmıyor"
        eksik_alan = detaylar.get("eksik_alan", 0)
        detay_mesaji = f"Eksik alan: {eksik_alan:,.0f} m²"
    elif agac_detaylari and "uygun değil" in agac_detaylari:
        neden = "Zeytin ağacı yoğunluğu çok fazla"
        detay_mesaji = agac_detaylari
    else:
        neden = "Bilinmeyen bir sorun"
        detay_mesaji = ""
    
    ana_mesaj = f"TARIMSAL DEPO YAPILAMAZ - {neden}"
    
    # HTML mesaj oluştur
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
