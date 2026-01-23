"""
Havza Bazlı Destekleme Modeli Hesaplama API View
2026 üretim yılı bitkisel üretim destekleme sistemi
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, List, Any
import logging
import re

logger = logging.getLogger(__name__)

# Temel destek katsayıları (2026 fiyat listesine göre)
TEMEL_DESTEK = 310  # TL/da

URUN_KATEGORILERI = {
    # 1. Kategori - Katsayı: 1 (310 TL/da)
    'Aspir': 1,
    'Mercimek': 1,
    'Nohut': 1,
    'Patates': 1,
    'Soğan (kuru)': 1,
    # Birinci grup yem bitkileri
    'Fiğ': 1,
    'Burçak': 1,
    'Mürdümük': 1,
    'Hayvan Pancarı': 1,
    'Yem Şalgamı': 1,
    'Yem Bezelyesi': 1,
    'Yem Baklası': 1,
    'Üçgül': 1,
    'İtalyan Çimi': 1,
    'Yulaf (yem)': 1,
    'Çavdar (yem)': 1,
    'Tritikale (yem)': 1,
    'Diğer Ürünler': 1,
    
    # 2. Kategori - Katsayı: 1.3 (403 TL/da)
    'Arpa': 1.3,
    'Buğday': 1.3,
    'Mısır (dane)': 1.3,
    # İkinci grup yem bitkileri
    'Yonca': 1.3,
    'Korunga': 1.3,
    'Yapay Çayır Mera': 1.3,
    'Silajlık Mısır': 1.3,
    'Silajlık Soya': 1.3,
    'Sorgum Otu': 1.3,
    'Sudan Otu': 1.3,
    'Sorgum-Sudan Otu Melezi': 1.3,
    
    # 3. Kategori - Katsayı: 1.5 (465 TL/da)
    'Ayçiçeği (yağlık)': 1.5,
    'Fındık': 1.5,
    'Kolza (kanola)': 1.5,
    'Fasulye (kuru)': 1.5,
    'Soya': 1.5,
    'Çay': 1.5,
    
    # 4. Kategori - Katsayı: 2.25 (697.5 TL/da)
    'Çeltik': 2.25,
    'Pamuk (kütlü)': 2.25,
    
    # Nadas - Katsayı: 0.3
    'Nadas': 0.3,
}

# Sertifikalı tohum kullanım desteği katsayıları (normalize_name çıktısı ile uyumlu)
# Kaynak: 2026 Üretim Yılı Bitkisel Üretim Destekleme Birim Fiyatları (A - Sertifikalı tohum kullanım desteği)
SERTIFIKALI_TOHUM_KATSAYILARI = {
    # 0.56
    'arpa': 0.56,
    'bugday': 0.56,
    'cavdar': 0.56,
    'celtik': 0.56,
    'fasulye': 0.56,
    'tritikale': 0.56,
    'yulaf': 0.56,
    # 0.2
    'aspir': 0.2,
    'kolza': 0.2,
    'susam': 0.2,
    # 0.6
    'korunga': 0.6,
    'soya': 0.6,
    'yer fistigi': 0.6,
    'yonca': 0.6,
    # 0.4
    'fig': 0.4,
    'mercimek': 0.4,
    'nohut': 0.4,
    'yem bezelyesi': 0.4,
    # 2.2
    'patates': 2.2,
}

# Yerli sertifikalı tohum kullanım desteği katsayıları (normalize_name çıktısı ile uyumlu)
# Kaynak: 2026 Üretim Yılı Bitkisel Üretim Destekleme Birim Fiyatları (Yerli Sertifikalı tohum kullanım desteği)
YERLI_SERTIFIKALI_TOHUM_KATSAYILARI = {
    'aycicegi': 0.6,
    'misir': 0.6,
    'soya': 0.6,
    # STKD'ye ilave olarak ödenir
    'patates': 3.2,
}

# Organik tarım desteği katsayıları
ORGANIK_TARIM_KATSAYILARI = {
    'birinci_grup_bireysel': 1.2,
    'birinci_grup_grup': 0.6,
    'ikinci_grup_bireysel': 0.6,
    'ikinci_grup_grup': 0.3,
    'ucuncu_grup_bireysel': 0.4,
    'ucuncu_grup_grup': 0.2,
}


def normalize_urun_grubu_key(urun_grubu: str | None) -> str | None:
    if not urun_grubu:
        return None

    mapping = {
        'birinci_kategori': 'birinci_grup',
        'ikinci_kategori': 'ikinci_grup',
        'ucuncu_kategori': 'ucuncu_grup',
        'birinci_grup': 'birinci_grup',
        'ikinci_grup': 'ikinci_grup',
        'ucuncu_grup': 'ucuncu_grup',
        '1': 'birinci_grup',
        '2': 'ikinci_grup',
        '3': 'ucuncu_grup',
    }

    return mapping.get(str(urun_grubu), urun_grubu)

# İyi tarım uygulamaları desteği katsayıları
IYI_TARIM_KATSAYILARI = {
    # 2026 Üretim Yılı Bitkisel Üretim Destekleme Birim Fiyatları (C - İyi Tarım Uygulamaları Desteği)
    'birinci_grup_bireysel_ortualti': 1.7,
    'birinci_grup_grup_ortualti': 0.85,
    'birinci_grup_bireysel_acikta': 0.7,
    'birinci_grup_grup_acikta': 0.35,
    'ikinci_grup_bireysel': 0.6,
    'ikinci_grup_grup': 0.3,
    'ucuncu_grup_bireysel': 0.4,
    'ucuncu_grup_grup': 0.2,
}

# Süt havzası illeri
SUT_HAVZASI_ILLERI = [
    'Amasya', 'Bingöl', 'Bitlis', 'Çorum', 'Elazığ', 'Erzincan', 
    'Erzurum', 'Muş', 'Tokat', 'Tunceli'
]

# Su kısıtı olan ilçeler
SU_KISITI_ILCELERI = [
    {'il': 'Aksaray', 'ilce': 'Merkez'},
    {'il': 'Aksaray', 'ilce': 'Eskil'},
    {'il': 'Aksaray', 'ilce': 'Gülağaç'},
    {'il': 'Aksaray', 'ilce': 'Güzelyurt'},
    {'il': 'Aksaray', 'ilce': 'Sultanhanı'},
    {'il': 'Ankara', 'ilce': 'Bala'},
    {'il': 'Ankara', 'ilce': 'Gölbaşı'},
    {'il': 'Ankara', 'ilce': 'Haymana'},
    {'il': 'Ankara', 'ilce': 'Şereflikoçhisar'},
    {'il': 'Eskişehir', 'ilce': 'Alpu'},
    {'il': 'Eskişehir', 'ilce': 'Beylikova'},
    {'il': 'Eskişehir', 'ilce': 'Çifteler'},
    {'il': 'Eskişehir', 'ilce': 'Mahmudiye'},
    {'il': 'Eskişehir', 'ilce': 'Mihalıççık'},
    {'il': 'Eskişehir', 'ilce': 'Sivrihisar'},
    {'il': 'Hatay', 'ilce': 'Kumlu'},
    {'il': 'Hatay', 'ilce': 'Reyhanlı'},
    {'il': 'Karaman', 'ilce': 'Ayrancı'},
    {'il': 'Karaman', 'ilce': 'Merkez'},
    {'il': 'Karaman', 'ilce': 'Kazımkarabekir'},
    {'il': 'Kırşehir', 'ilce': 'Boztepe'},
    {'il': 'Kırşehir', 'ilce': 'Mucur'},
    {'il': 'Konya', 'ilce': 'Akörey'},
    {'il': 'Konya', 'ilce': 'Akşehir'},
    {'il': 'Konya', 'ilce': 'Altınekin'},
    {'il': 'Konya', 'ilce': 'Cihanbeyli'},
    {'il': 'Konya', 'ilce': 'Çumra'},
    {'il': 'Konya', 'ilce': 'Derbent'},
    {'il': 'Konya', 'ilce': 'Doğanhisar'},
    {'il': 'Konya', 'ilce': 'Emirgazi'},
    {'il': 'Konya', 'ilce': 'Ereğli'},
    {'il': 'Konya', 'ilce': 'Güneysınır'},
    {'il': 'Konya', 'ilce': 'Halkapınar'},
    {'il': 'Konya', 'ilce': 'Kadınhanı'},
    {'il': 'Konya', 'ilce': 'Karapınar'},
    {'il': 'Konya', 'ilce': 'Karatay'},
    {'il': 'Konya', 'ilce': 'Kulu'},
    {'il': 'Konya', 'ilce': 'Meram'},
    {'il': 'Konya', 'ilce': 'Sarayönü'},
    {'il': 'Konya', 'ilce': 'Selçuklu'},
    {'il': 'Konya', 'ilce': 'Tuzlukçu'},
    {'il': 'Mardin', 'ilce': 'Artuklu'},
    {'il': 'Mardin', 'ilce': 'Derik'},
    {'il': 'Mardin', 'ilce': 'Kızıltepe'},
    {'il': 'Nevşehir', 'ilce': 'Acıgöl'},
    {'il': 'Nevşehir', 'ilce': 'Derinkuyu'},
    {'il': 'Nevşehir', 'ilce': 'Gülşehir'},
    {'il': 'Niğde', 'ilce': 'Altunhisar'},
    {'il': 'Niğde', 'ilce': 'Bor'},
    {'il': 'Niğde', 'ilce': 'Çiftlik'},
    {'il': 'Niğde', 'ilce': 'Merkez'},
    {'il': 'Şanlıurfa', 'ilce': 'Viranşehir'},
]

# Su kısıtı desteği katsayıları (normalize edilmiş anahtarlar)
SU_KISITI_KATSAYILARI = {
    'aspir': 0.8,
    'fig': 0.8,
    'mercimek': 0.8,
    'nohut': 0.8,
    'yem bezelyesi': 0.8,
    'arpa': 1.4,
    'bugday': 1.4,
    'aycicegi': 1.2,
}

def normalize_name(name: str) -> str:
    """İsim normalizasyonu (Türkçe karakterler ve büyük/küçük harf)"""
    if not name:
        return ""
    
    replacements = {
        'İ': 'i', 'ı': 'i', 'Ş': 's', 'ş': 's', 'Ğ': 'g', 'ğ': 'g',
        'Ü': 'u', 'ü': 'u', 'Ö': 'o', 'ö': 'o', 'Ç': 'c', 'ç': 'c'
    }
    
    result = name
    for tr_char, en_char in replacements.items():
        result = result.replace(tr_char, en_char)
    
    return result.strip().lower()


def normalize_urun_name(name: str) -> str:
    """Ürün adı normalizasyonu.

    UI'da gelen ürün adları ile havza_urun_desen.json'daki ürün adları aynı olmayabiliyor
    (örn: "Ayçiçeği (yağlık)" vs "Ayçiçeği"). Bu fonksiyon ürün adlarını daha agresif
    normalize ederek eşleştirmeyi sağlamlaştırır.
    """
    base = normalize_name(name)
    if not base:
        return ""

    # Parantez içi açıklamaları kaldır: "(yağlık)", "(dane)", "(kuru)", "(yem)"...
    base = re.sub(r"\s*\([^)]*\)\s*", " ", base)

    # Farklı tire karakterlerini tek tipe yaklaştır (ihtiyaten)
    base = base.replace("–", "-").replace("—", "-")

    # Çoklu boşlukları tek boşluğa indir
    base = re.sub(r"\s+", " ", base).strip()

    # UI varyantlarını kanonik forma eşle
    canonical_map = {
        # UI: "Sorgum-Sudan Otu Melezi" -> listelerde genelde "sorgum-sudan melezi"
        "sorgum-sudan otu melezi": "sorgum-sudan melezi",
        # Bazı veri setlerinde "kolza (kanola)" yerine sadece "kolza" geçebilir
        "kolza kanola": "kolza",
    }

    return canonical_map.get(base, base)


def resolve_havza_urun_desen_path() -> str | None:
    """Havza ürün deseni JSON dosyasının yolunu bulur.

    Docker imajı ve yerel geliştirme senaryoları için birden fazla olası konumu dener.
    """
    import os
    from django.conf import settings

    # 1) Explicit override
    env_path = os.environ.get('HAVZA_URUN_DESEN_PATH')
    if env_path and os.path.isfile(env_path):
        return env_path

    # 2) Common in-container locations
    candidates = [
        '/app/havza_urun_desen.json',
        os.path.join(settings.BASE_DIR, 'havza_urun_desen.json'),
        os.path.join(settings.BASE_DIR, 'static', 'havza_urun_desen.json'),
        os.path.join(settings.BASE_DIR, 'static', 'data', 'havza_urun_desen.json'),
        os.path.join(settings.BASE_DIR, 'data', 'havza_urun_desen.json'),
        # Host repo layout (yerel geliştirme): Next.js public altından oku
        os.path.join(settings.BASE_DIR, '../webimar-nextjs/public/havza_urun_desen.json'),
    ]

    for candidate in candidates:
        if candidate and os.path.isfile(candidate):
            return candidate

    return None


def find_matching_key_by_normalized(mapping: dict, target: str) -> str | None:
    """Sözlük anahtarını normalize_name ile eşleştirerek bulur."""
    target_norm = normalize_name(target)
    for key in mapping.keys():
        if normalize_name(str(key)) == target_norm:
            return key
    return None


def find_matching_ilce_key(il_data: dict, il_name: str, target_ilce: str) -> str | None:
    """İlçe anahtarını bulur, gerekirse il adı = ilçe adı durumunda MERKEZ ile eşleştirir."""
    # Önce doğrudan eşleştirmeyi dene
    if target_ilce in il_data:
        return target_ilce
    
    # Normalize edilmiş eşleştirmeyi dene
    normalized_match = find_matching_key_by_normalized(il_data, target_ilce)
    if normalized_match:
        return normalized_match
    
    # İl adı = İlçe adı durumu: MERKEZ ile eşleştirmeyi dene
    # Örn: "YOZGAT" ili için "YOZGAT" ilçesi -> "MERKEZ" ile eşleştir
    if (normalize_name(il_name) == normalize_name(target_ilce) and 
        'MERKEZ' in il_data):
        return 'MERKEZ'
    
    return None

def su_kisiti_kontrolu(il: str, ilce: str) -> bool:
    """Su kısıtı olan bölge kontrolü"""
    il_norm = normalize_name(il)
    ilce_norm = normalize_name(ilce)
    
    for kisit in SU_KISITI_ILCELERI:
        if (normalize_name(kisit['il']) == il_norm and 
            normalize_name(kisit['ilce']) == ilce_norm):
            return True
    return False

def sut_havzasi_kontrolu(il: str) -> bool:
    """Süt havzası il kontrolü"""
    il_norm = normalize_name(il)
    return any(normalize_name(havza_il) == il_norm for havza_il in SUT_HAVZASI_ILLERI)

def yem_bitkisi_mi(urun: str) -> bool:
    """Ürünün yem bitkisi olup olmadığını kontrol eder (normalize edilmiş)"""
    yem_bitkileri_norm = [
        'fig', 'burcak', 'murdumuk', 'hayvan pancari', 'yem salgami',
        'yem bezelyesi', 'yem baklasi', 'ucgul', 'italyan cimi', 'yulaf',
        'cavdar', 'tritikale', 'fig silaji', 'yulaf silaji',
        'yonca', 'korunga', 'yapay cayir mera', 'silajlik misir',
        'silajlik soya', 'sorgum otu', 'sudan otu', 'sorgum-sudan melezi'
    ]
    return normalize_urun_name(urun) in yem_bitkileri_norm

def planli_uretim_destegi_var_mi(urun: str) -> bool:
    """2026 listesine göre planlı üretim desteği verilen ürünler (normalize edilmiş)"""
    planli_desteklenen_norm = [
        # 1. Kategori
        'aspir', 'mercimek', 'nohut', 'patates', 'sogan',
        'fig', 'burcak', 'murdumuk', 'hayvan pancari', 'yem salgami',
        'yem bezelyesi', 'yem baklasi', 'ucgul', 'italyan cimi', 'yulaf',
        'cavdar', 'tritikale',
        # 2. Kategori  
        'arpa', 'bugday', 'misir',
        'yonca', 'korunga', 'yapay cayir mera', 'silajlik misir',
        'silajlik soya', 'sorgum otu', 'sudan otu', 'sorgum-sudan melezi',
        # 3. Kategori
        'aycicegi', 'kolza', 'fasulye', 'soya',
        # 4. Kategori
        'pamuk'
        # NOT: Fındık, Çay, Çeltik planlı üretim listesinde yok!
    ]
    return normalize_urun_name(urun) in planli_desteklenen_norm

def urun_grubu_belirle(urun: str) -> str:
    """Ürünün hangi gruba ait olduğunu belirler (organik/iyi tarım için) - normalize edilmiş"""
    urun_norm = normalize_urun_name(urun)
    
    birinci_grup_norm = [
        'aspir', 'mercimek', 'nohut', 'patates', 'sogan',
        'fig', 'burcak', 'murdumuk', 'hayvan pancari', 'yem salgami',
        'yem bezelyesi', 'yem baklasi', 'ucgul', 'italyan cimi', 'yulaf',
        'cavdar', 'tritikale', 'fig silaji', 'yulaf silaji'
    ]
    
    ikinci_grup_norm = [
        'arpa', 'bugday', 'misir',
        'yonca', 'korunga', 'yapay cayir mera', 'silajlik misir',
        'silajlik soya', 'sorgum otu', 'sudan otu', 'sorgum-sudan melezi'
    ]
    
    ucuncu_grup_norm = [
        'aycicegi', 'findik', 'kolza', 'fasulye', 'soya', 'cay',
        'celtik', 'pamuk'
    ]
    
    if urun_norm in birinci_grup_norm:
        return 'birinci_grup'
    elif urun_norm in ikinci_grup_norm:
        return 'ikinci_grup'
    elif urun_norm in ucuncu_grup_norm:
        return 'ucuncu_grup'
    else:
        return 'birinci_grup'  # Varsayılan

@api_view(['POST'])
def havza_bazli_destekleme_modeli(request):
    """
    Havza bazlı destekleme modeli hesaplama endpoint'i
    """
    try:
        data = request.data

        debug_enabled = (
            str(getattr(request, 'query_params', {}).get('debug', '')).lower() == 'true'
            or bool(data.get('debug', False))
        )

        def debug_log(message: str) -> None:
            if debug_enabled:
                logger.info(message)
        
        # Veri doğrulaması
        il = data.get('il', '').strip()
        ilce = data.get('ilce', '').strip()
        urunler = data.get('urunler', [])
        genc_ciftci = data.get('gencCiftci', False)
        kadin_ciftci = data.get('kadinCiftci', False)
        kobuks_kayitli = data.get('kobuksKayitli', False)
        orgut_uyesi = data.get('orgutUyesi', False)
        uretimi_gelistirme = data.get('uretimiGelistirme', {})
        
        if not il or not ilce:
            return Response({
                'uygun': False,
                'mesaj': 'İl ve ilçe bilgileri zorunludur.',
                'detaylar': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not urunler or not any(u.get('urun') and u.get('dekar', 0) > 0 for u in urunler):
            return Response({
                'uygun': False,
                'mesaj': 'En az bir ürün ve dekar miktarı girilmelidir.',
                'detaylar': {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Havza verilerini yükle
        try:
            import json
            import os
            from django.conf import settings

            havza_file_path = resolve_havza_urun_desen_path()
            if not havza_file_path:
                raise FileNotFoundError('havza_urun_desen.json bulunamadı')

            with open(havza_file_path, 'r', encoding='utf-8') as f:
                havza_data = json.load(f)
        except Exception as e:
            debug_log(f"DEBUG: Havza verisi yüklenemedi: {e}")
            havza_data = {}
        
        # Su kısıtı kontrolü
        su_kisiti_bolgesi = su_kisiti_kontrolu(il, ilce)
        sut_havzasi_bolgesi = sut_havzasi_kontrolu(il)

        havza_il_key: str | None = None
        havza_ilce_key: str | None = None
        havza_urun_listesi: list[str] | None = None
        desteklenen_urunler_norm: set[str] | None = None

        if havza_data:
            havza_il_key = il if il in havza_data else find_matching_key_by_normalized(havza_data, il)
            if havza_il_key:
                havza_ilce_key = find_matching_ilce_key(havza_data[havza_il_key], il, ilce)
            if havza_il_key and havza_ilce_key:
                desteklenen_urunler = havza_data[havza_il_key][havza_ilce_key]
                if isinstance(desteklenen_urunler, list):
                    havza_urun_listesi = list(desteklenen_urunler)
                    desteklenen_urunler_norm = {normalize_urun_name(u) for u in havza_urun_listesi}
        
        # Hesaplama değişkenleri
        toplam_temel_destek = 0
        toplam_planli_uretim = 0
        toplam_genclik_ilavesi = 0
        toplam_sut_havzasi = 0
        toplam_su_kisiti = 0
        toplam_sertifikali_tohum = 0
        toplam_yerli_sertifikali_tohum = 0
        toplam_organik_tarim = 0
        toplam_iyi_tarim = 0
        toplam_gubre = 0
        
        mesajlar = []
        desteklenmeyen_urunler: list[str] = []

        debug_urun_kayitlari: list[dict] = []
        
        # Ürün bazlı hesaplamalar
        urun_bazli_destek_tipi_var = any(
            (u.get('destekTipi') in ['organik', 'iyiTarim']) for u in urunler if isinstance(u, dict)
        )
        urun_bazli_gubre_var = any(
            bool(u.get('katiOrganikGubre')) for u in urunler if isinstance(u, dict)
        )

        for urun_info in urunler:
            urun = urun_info.get('urun', '').strip()
            dekar = float(urun_info.get('dekar', 0))
            
            if not urun or dekar <= 0:
                continue
            
            # Ürün adını normalize et (Türkçe karakterler için)
            urun_norm = normalize_urun_name(urun)

            sulama_tipi = str(urun_info.get('sulamaTipi') or 'kuru')
            sulama_tipi = 'sulu' if sulama_tipi == 'sulu' else 'kuru'

            havzada_urun_deseni_var = True
            havza_eslesme_tipi: str | None = None

            if havza_urun_listesi is not None and desteklenen_urunler_norm is not None:
                if yem_bitkisi_mi(urun):
                    havzada_urun_deseni_var = any(
                        normalize_name(u) == normalize_name('Yem Bitkileri') for u in havza_urun_listesi
                    )
                    havza_eslesme_tipi = 'yem_bitkileri_etiketi' if havzada_urun_deseni_var else 'eslesme_yok'
                else:
                    havzada_urun_deseni_var = normalize_urun_name(urun) in desteklenen_urunler_norm
                    havza_eslesme_tipi = 'dogrudan_urun_adi' if havzada_urun_deseni_var else 'eslesme_yok'
            else:
                havza_eslesme_tipi = 'il_ilce_bulunamadi' if havza_data else 'havza_verisi_yok'

            if havza_urun_listesi is not None and not havzada_urun_deseni_var:
                if urun not in desteklenmeyen_urunler:
                    desteklenmeyen_urunler.append(urun)
                continue
            
            # Su kısıtı yasağı kontrolü
            if su_kisiti_bolgesi and urun_norm in ['misir', 'patates']:
                mesajlar.append(f"⚠️ {urun} su kısıtı bölgelerinde desteklenmiyor.")
                continue
            
            # Ürün kategorisi ve katsayısı (normalize edilmiş isimle)
            katsayi = URUN_KATEGORILERI.get(urun, 1)  # Önce orijinal isimle dene
            if katsayi == 1 and urun != 'Diğer Ürünler':  # Eğer bulunamadıysa normalize edilmişle dene
                # Normalize edilmiş anahtarları oluştur
                normalized_keys = {normalize_urun_name(k): v for k, v in URUN_KATEGORILERI.items()}
                katsayi = normalized_keys.get(urun_norm, 1)
            
            # Temel destek (katsayı ile çarpılır)
            temel = TEMEL_DESTEK * katsayi * dekar
            toplam_temel_destek += temel
            
            # Planlı üretim desteği (sadece listede olanlar ve havzada desteklenenler için)
            planli_var = planli_uretim_destegi_var_mi(urun_norm)
            havzada_desteklenen = False
            if planli_var and havza_urun_listesi is not None:
                havzada_desteklenen = havzada_urun_deseni_var
            elif not havza_data:
                havza_eslesme_tipi = 'havza_verisi_yok'
            elif not planli_var:
                havza_eslesme_tipi = 'planli_listede_yok'
            
            debug_log(f"DEBUG: {urun} -> planli_var: {planli_var}, havzada_desteklenen: {havzada_desteklenen}")

            if debug_enabled:
                debug_urun_kayitlari.append(
                    {
                        'urun_girdi': urun,
                        'urun_norm': urun_norm,
                        'dekar': dekar,
                        'planli_listede': bool(planli_var),
                        'havza_il_key': havza_il_key,
                        'havza_ilce_key': havza_ilce_key,
                        'havzada_desteklenen': bool(havzada_desteklenen),
                        'havza_eslesme_tipi': havza_eslesme_tipi,
                        'havza_desteklenen_urunler': havza_urun_listesi,
                    }
                )
            
            if planli_var and havzada_desteklenen:
                planli = TEMEL_DESTEK * katsayi * dekar
                toplam_planli_uretim += planli
            
            # Genç/Kadın çiftçi ilavesi (kapalı ortam bitkisel üretim için 3 katsayısı ile)
            # KOBÜKS kayıtlı genç/kadın çiftçilere örtü altı üretim için temel desteğin 3 katı ilave destek
            if (genc_ciftci or kadin_ciftci) and kobuks_kayitli:
                # Ürün seçiminde örtü altı üretim
                if urun_info.get('uretimTipi') == 'ortualti':
                    genclik_ilave = TEMEL_DESTEK * 3 * dekar  
                    toplam_genclik_ilavesi += genclik_ilave
                    debug_log(f"[DEBUG] Ürün örtü altı: {urun} {dekar}da → {genclik_ilave}₺")
            
            # Süt havzası ilavesi (yem bitkileri için - planli uretim varsa ve havzada destekleniyorsa)
            if sut_havzasi_bolgesi and yem_bitkisi_mi(urun) and planli_var and havzada_desteklenen:
                sut_ilave = (TEMEL_DESTEK * katsayi * dekar) * 0.5  # Planlı üretim desteğinin %50'si
                toplam_sut_havzasi += sut_ilave
            
            # Su kısıtı desteği
            if su_kisiti_bolgesi and sulama_tipi == 'sulu' and urun_norm in SU_KISITI_KATSAYILARI:
                su_katsayi = SU_KISITI_KATSAYILARI[urun_norm]
                su_ilave = TEMEL_DESTEK * su_katsayi * dekar
                toplam_su_kisiti += su_ilave
            
            # Sertifikalı tohum desteği (ürün bazlı; geriye dönük global alanı da destekler)
            sertifikali_tohum_secili = bool(urun_info.get('sertifikaliTohum')) or bool(
                uretimi_gelistirme.get('sertifikaliTohum', False)
            )
            yerli_sertifikali_tohum_secili = bool(urun_info.get('yerliSertifikaliTohum')) or bool(
                uretimi_gelistirme.get('yerliSertifikaliTohum', False)
            )

            if sertifikali_tohum_secili and urun_norm in SERTIFIKALI_TOHUM_KATSAYILARI:
                sert_katsayi = SERTIFIKALI_TOHUM_KATSAYILARI[urun_norm]
                sert_destek = TEMEL_DESTEK * sert_katsayi * dekar
                toplam_sertifikali_tohum += sert_destek

            if yerli_sertifikali_tohum_secili and urun_norm in YERLI_SERTIFIKALI_TOHUM_KATSAYILARI:
                yerli_katsayi = YERLI_SERTIFIKALI_TOHUM_KATSAYILARI[urun_norm]
                yerli_destek = TEMEL_DESTEK * yerli_katsayi * dekar
                toplam_yerli_sertifikali_tohum += yerli_destek
            
            # Organik tarım desteği (ürün bazlı)
            if urun_info.get('destekTipi') == 'organik':
                organik_data = urun_info.get('organikTarim', {}) or {}
                urun_grubu = normalize_urun_grubu_key(organik_data.get('urunGrubu'))
                sertifika_turu = organik_data.get('sertifikaTuru', 'bireysel')

                if urun_grubu:
                    organik_key = f"{urun_grubu}_{sertifika_turu}"
                    if organik_key in ORGANIK_TARIM_KATSAYILARI:
                        org_katsayi = ORGANIK_TARIM_KATSAYILARI[organik_key]
                        org_destek = TEMEL_DESTEK * org_katsayi * dekar
                        toplam_organik_tarim += org_destek

                        # 1. derece örgüt üyesi ilavesi
                        if orgut_uyesi:
                            org_ilave = org_destek * 0.25
                            toplam_organik_tarim += org_ilave

            # İyi tarım uygulamaları desteği (ürün bazlı)
            if urun_info.get('destekTipi') == 'iyiTarim':
                iyi_tarim_data = urun_info.get('iyiTarim', {}) or {}
                urun_grubu = iyi_tarim_data.get('urunGrubu')
                sertifika_turu = iyi_tarim_data.get('sertifikaTuru', 'bireysel')
                # 1. kategori için üretim tipi önemli: ürün satırındaki uretimTipi esas alınır
                uretim_tipi = urun_info.get('uretimTipi') or iyi_tarim_data.get('uretimTipi')

                if urun_grubu:
                    if urun_grubu == 'birinci_kategori' and uretim_tipi:
                        iyi_key = f"birinci_grup_{sertifika_turu}_{uretim_tipi}"
                    else:
                        kategori_map = {
                            'birinci_kategori': 'birinci_grup',
                            'ikinci_kategori': 'ikinci_grup',
                            'ucuncu_kategori': 'ucuncu_grup',
                        }
                        grup_adi = kategori_map.get(urun_grubu, urun_grubu)
                        iyi_key = f"{grup_adi}_{sertifika_turu}"

                    if iyi_key in IYI_TARIM_KATSAYILARI:
                        iyi_katsayi = IYI_TARIM_KATSAYILARI[iyi_key]
                        iyi_destek = TEMEL_DESTEK * iyi_katsayi * dekar
                        toplam_iyi_tarim += iyi_destek

            # Katı organik / organomineral gübre desteği (ürün bazlı)
            if urun_info.get('katiOrganikGubre'):
                toplam_gubre += 99.2 * dekar

        # Geriye dönük uyumluluk: ürün bazlı seçim yapılmadıysa eski global alanları kullan
        if not urun_bazli_destek_tipi_var:
            # Organik tarım desteği (global)
            if uretimi_gelistirme.get('organikTarim', {}).get('secili', False):
                urun_grubu = normalize_urun_grubu_key(
                    uretimi_gelistirme.get('organikTarim', {}).get('urunGrubu')
                )
                sertifika_turu = uretimi_gelistirme.get('organikTarim', {}).get('sertifikaTuru', 'bireysel')

                if urun_grubu:
                    organik_key = f"{urun_grubu}_{sertifika_turu}"
                    if organik_key in ORGANIK_TARIM_KATSAYILARI:
                        org_katsayi = ORGANIK_TARIM_KATSAYILARI[organik_key]
                        toplam_dekar = sum(
                            float(u.get('dekar', 0))
                            for u in urunler
                            if u.get('urun') and float(u.get('dekar', 0)) > 0
                        )
                        org_destek = TEMEL_DESTEK * org_katsayi * toplam_dekar
                        toplam_organik_tarim += org_destek
                        if orgut_uyesi:
                            toplam_organik_tarim += org_destek * 0.25

            # İyi tarım uygulamaları desteği (global)
            if uretimi_gelistirme.get('iyiTarim', {}).get('secili', False):
                urun_grubu = uretimi_gelistirme.get('iyiTarim', {}).get('urunGrubu')
                sertifika_turu = uretimi_gelistirme.get('iyiTarim', {}).get('sertifikaTuru', 'bireysel')
                uretim_tipi = uretimi_gelistirme.get('iyiTarim', {}).get('uretimTipi')

                if urun_grubu:
                    if urun_grubu == 'birinci_kategori' and uretim_tipi:
                        iyi_key = f"birinci_grup_{sertifika_turu}_{uretim_tipi}"
                    else:
                        kategori_map = {
                            'birinci_kategori': 'birinci_grup',
                            'ikinci_kategori': 'ikinci_grup',
                            'ucuncu_kategori': 'ucuncu_grup',
                        }
                        grup_adi = kategori_map.get(urun_grubu, urun_grubu)
                        iyi_key = f"{grup_adi}_{sertifika_turu}"

                    if iyi_key in IYI_TARIM_KATSAYILARI:
                        iyi_katsayi = IYI_TARIM_KATSAYILARI[iyi_key]
                        toplam_dekar = sum(
                            float(u.get('dekar', 0))
                            for u in urunler
                            if u.get('urun') and float(u.get('dekar', 0)) > 0
                        )
                        toplam_iyi_tarim += TEMEL_DESTEK * iyi_katsayi * toplam_dekar
        
        # Gübre desteği (geriye dönük global alan - ürün bazlı yoksa)
        if not urun_bazli_gubre_var and uretimi_gelistirme.get('katiOrganikGubre', False):
            toplam_dekar = sum(float(u.get('dekar', 0)) for u in urunler if u.get('urun') and float(u.get('dekar', 0)) > 0)
            toplam_gubre = 99.2 * toplam_dekar
        
        # Toplam hesaplama
        toplam_destek = (
            toplam_temel_destek + 
            toplam_planli_uretim + 
            toplam_genclik_ilavesi + 
            toplam_sut_havzasi + 
            toplam_su_kisiti + 
            toplam_sertifikali_tohum + 
            toplam_yerli_sertifikali_tohum +
            toplam_organik_tarim + 
            toplam_iyi_tarim + 
            toplam_gubre
        )
        
        # Başarı mesajı
        mesaj_parts = ["✅ Hesaplama başarıyla tamamlandı."]
        
        if su_kisiti_bolgesi and toplam_su_kisiti > 0:
            mesajlar.append("🌊 Su kısıtı bölgesi desteği uygulandı.")

        if desteklenmeyen_urunler:
            desteklenmeyen_unique = list(dict.fromkeys(desteklenmeyen_urunler))
            if len(desteklenmeyen_unique) == 1:
                mesajlar.append(
                    "Seçtiğiniz ürün, seçilen havzanın ürün deseni içerisinde bulunmadığından destekleme ödemesi yapılmamaktadır: "
                    f"{desteklenmeyen_unique[0]}."
                )
            else:
                mesajlar.append(
                    "Seçtiğiniz ürünler, seçilen havzanın ürün deseni içerisinde bulunmadığından destekleme ödemesi yapılmamaktadır: "
                    f"{', '.join(desteklenmeyen_unique)}."
                )
        
        if sut_havzasi_bolgesi:
            mesajlar.append("🥛 Süt havzası bölgesi ilavesi uygulandı.")
        
        if genc_ciftci:
            mesajlar.append("👨‍🌾 Genç çiftçi ilavesi uygulandı.")
        
        if kadin_ciftci:
            mesajlar.append("👩‍🌾 Kadın çiftçi ilavesi uygulandı.")
        
        mesaj_parts.extend(mesajlar)
        
        return Response({
            'uygun': True,
            'mesaj': ' '.join(mesaj_parts),
            'detaylar': {
                'temel_destek': round(toplam_temel_destek, 2),
                'planli_uretim': round(toplam_planli_uretim, 2),
                'genclik_ilavesi': round(toplam_genclik_ilavesi, 2),
                'sut_havzasi_ilavesi': round(toplam_sut_havzasi, 2),
                'su_kisiti': round(toplam_su_kisiti, 2),
                'sertifikali_tohum': round(toplam_sertifikali_tohum, 2),
                'yerli_sertifikali_tohum': round(toplam_yerli_sertifikali_tohum, 2),
                'organik_tarim': round(toplam_organik_tarim, 2),
                'iyi_tarim': round(toplam_iyi_tarim, 2),
                'gubre': round(toplam_gubre, 2),
                'toplam': round(toplam_destek, 2),
                **({'debug': {'urunler': debug_urun_kayitlari}} if debug_enabled else {})
            }
        })
        
    except Exception as e:
        logger.error(f"Havza bazlı destekleme hesaplama hatası: {str(e)}")
        return Response({
            'uygun': False,
            'mesaj': f'Hesaplama sırasında hata oluştu: {str(e)}',
            'detaylar': {}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)