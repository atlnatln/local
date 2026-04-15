"""
Basit Tarımsal Yapılar Hesaplama Modülü

Yeni yönetmelik (2025) ile eklenen, temel emsal hesaplama gerektiren yapılar:
- Mandıra (süt sağım/soğutma) - ID 37
- Un değirmeni (geleneksel yöntem) - ID 38
- Tarımsal amaçlı teleferik - ID 39
- Hayvan içme suyu göleti - ID 40
- İslim ünitesi - ID 41
- Muz sarartma ünitesi - ID 42
- Tarımsal AR-GE tesisi - ID 43
"""
import logging

logger = logging.getLogger(__name__)

EMSAL_ORANI = 0.20

# Yapı tipi sabitleri
YAPI_TIPLERI = {
    "mandira": {
        "ad": "Mandıra (Süt Sağım ve Soğutma Tesisi)",
        "aciklama": "Büyükbaş/küçükbaş işletme içi veya dışında sadece süt sağım ve soğutma amacıyla kullanılır.",
        "max_alan_m2": None,  # Emsal bazlı
        "emsal_oran": 0.30,   # Küçük tesis, emsal payı %30
    },
    "un_degirmeni": {
        "ad": "Un Değirmeni",
        "aciklama": "Sanayi niteliği taşımayan, geleneksel yöntemlerle un üretimi yapılan tesis.",
        "max_alan_m2": 200,
        "emsal_oran": None,
    },
    "teleferik": {
        "ad": "Tarımsal Amaçlı Teleferik",
        "aciklama": "Tarımsal ürünlerin taşınması amacıyla kurulan teleferik sistemi. Tarımsal amaçlı yapı olarak kabul edilir.",
        "max_alan_m2": None,
        "emsal_oran": 0.10,   # İstasyon/platform alanı
    },
    "golet": {
        "ad": "Hayvan İçme Suyu Göleti",
        "aciklama": "Hayvancılık işletmelerinin su ihtiyacını karşılamak amacıyla yapılan gölet.",
        "max_alan_m2": None,
        "emsal_oran": None,  # Gölet emsal dışı
    },
    "islim": {
        "ad": "İslim Ünitesi",
        "aciklama": "Tarımsal ürünlerin buharla işlenmesi amacıyla kullanılan ünite.",
        "max_alan_m2": 100,
        "emsal_oran": None,
    },
    "muz_sarartma": {
        "ad": "Muz Sarartma Ünitesi",
        "aciklama": "Muz üretim bölgelerinde hasat sonrası sarartma işlemi yapılan ünite.",
        "max_alan_m2": 200,
        "emsal_oran": None,
    },
    "tarimsal_arge": {
        "ad": "Tarımsal AR-GE Tesisi",
        "aciklama": "Tarımsal araştırma ve geliştirme faaliyetleri için kurulan tesis.",
        "max_alan_m2": None,
        "emsal_oran": 0.20,
    },
}


def basit_yapi_degerlendir(data, yapi_tipi, emsal_orani=None):
    """
    Basit tarımsal yapılar için genel hesaplama fonksiyonu.
    
    Args:
        data: Form verileri
        yapi_tipi: YAPI_TIPLERI sözlüğündeki anahtar
        emsal_orani: Opsiyonel emsal oranı override
    """
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        if yapi_tipi not in YAPI_TIPLERI:
            return {"success": False, "error": f"Bilinmeyen yapı tipi: {yapi_tipi}"}
        
        yapi = YAPI_TIPLERI[yapi_tipi]
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        # Gölet özel durum (emsal dışı)
        if yapi_tipi == "golet":
            return _golet_hesapla(data, arazi_m2, emsal_m2, yapi)
        
        # Alan hesaplama
        if yapi["max_alan_m2"]:
            izin_verilen_alan = min(yapi["max_alan_m2"], emsal_m2)
        elif yapi["emsal_oran"]:
            izin_verilen_alan = emsal_m2 * yapi["emsal_oran"]
        else:
            izin_verilen_alan = emsal_m2
        
        yapilanabilir = izin_verilen_alan >= 20  # Minimum işlevsel alan
        
        mesaj = f"<b>{yapi['ad'].upper()} DEĞERLENDİRMESİ</b><br><br>"
        mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
        mesaj += f"Emsal Alanı: {emsal_m2:,.2f} m²<br>"
        mesaj += f"<em>{yapi['aciklama']}</em><br><br>"
        
        if yapilanabilir:
            mesaj += f"<b>SONUÇ: TESİS KURULABİLİR</b><br>"
            mesaj += f"İzin verilen maksimum alan: {izin_verilen_alan:,.2f} m²"
            if yapi["max_alan_m2"]:
                mesaj += f" (yasal limit: {yapi['max_alan_m2']} m²)"
        else:
            mesaj += "<b>SONUÇ: TESİS KURULAMAZ</b> - Yetersiz alan."
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "emsal_m2": emsal_m2,
            "izin_verilen_alan_m2": round(izin_verilen_alan, 2) if yapilanabilir else 0,
        }
    except Exception as e:
        logger.error(f"{yapi_tipi} hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}


def _golet_hesapla(data, arazi_m2, emsal_m2, yapi):
    """Hayvan içme suyu göleti özel hesaplama (emsal dışı yapı)"""
    hayvan_sayisi = int(data.get('hayvan_sayisi', 0))
    
    # Basit gölet boyutu tahmini (hayvan başına ~50 litre/gün, 90 günlük depolama)
    if hayvan_sayisi > 0:
        su_ihtiyaci_m3 = hayvan_sayisi * 0.05 * 90  # m³
        golet_alani = su_ihtiyaci_m3 / 2  # Ortalama 2m derinlik
    else:
        golet_alani = arazi_m2 * 0.10  # Arazi alanının %10'u
    
    mesaj = f"<b>{yapi['ad'].upper()} DEĞERLENDİRMESİ</b><br><br>"
    mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
    mesaj += f"<em>{yapi['aciklama']}</em><br><br>"
    
    if hayvan_sayisi > 0:
        mesaj += f"Hayvan Sayısı: {hayvan_sayisi:,}<br>"
        mesaj += f"Tahmini Su İhtiyacı (90 gün): {hayvan_sayisi * 0.05 * 90:,.0f} m³<br>"
    
    mesaj += f"Tahmini Gölet Alanı: {golet_alani:,.0f} m²<br><br>"
    mesaj += "<b>SONUÇ: GÖLET YAPILABİLİR</b><br>"
    mesaj += "<em>Not: Gölet alanı emsal dışında değerlendirilir. Kesin boyutlandırma için hidrolojik etüt gereklidir.</em>"
    
    return {
        "success": True,
        "izin_durumu": "izin_verilebilir",
        "mesaj": mesaj,
        "arazi_buyuklugu_m2": arazi_m2,
        "golet_alani_m2": round(golet_alani, 2),
    }


# Kısayol fonksiyonlar (view'larden kolayca çağrılabilmesi için)
def mandira_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "mandira", emsal_orani)

def un_degirmeni_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "un_degirmeni", emsal_orani)

def teleferik_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "teleferik", emsal_orani)

def golet_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "golet", emsal_orani)

def islim_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "islim", emsal_orani)

def muz_sarartma_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "muz_sarartma", emsal_orani)

def tarimsal_arge_degerlendir(data, emsal_orani=None):
    return basit_yapi_degerlendir(data, "tarimsal_arge", emsal_orani)
