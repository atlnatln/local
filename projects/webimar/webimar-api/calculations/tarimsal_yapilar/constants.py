"""
Bu modül, tüm arazi vasıfları ve yapı türleri için kullanılan sabit değerleri içerir.
"""

# Arazi tipleri tanımı (eski projeden taşınan)
ARAZI_TIPLERI = [
    {"id": 1, "ad": "Tarla + herhangi bir dikili vasıflı"},
    {"id": 2, "ad": "Dikili vasıflı"},
    {"id": 3, "ad": "Tarla + Zeytinlik"},
    {"id": 4, "ad": "Zeytin ağaçlı + tarla"},
    {"id": 5, "ad": "Zeytin ağaçlı + herhangi bir dikili vasıf"},
    {"id": 6, "ad": "… Adetli Zeytin Ağacı bulunan tarla"},
    {"id": 7, "ad": "… Adetli Zeytin Ağacı bulunan + herhangi bir dikili vasıf"},
    {"id": 8, "ad": "Zeytinlik"},
    {"id": 9, "ad": "Ham toprak, taşlık, kıraç, palamutluk, koruluk gibi diğer vasıflı"},
    {"id": 10, "ad": "Tarla"},
    {"id": 11, "ad": "Sera"},
]

# Yapı türleri tanımı
# aktif: True = kullanımda, False = yönetmelik değişikliğiyle pasife alınmış (2025 güncellemesi)
YAPI_TURLERI = [
    {"id": 1, "ad": "Solucan ve solucan gübresi", "aktif": True},
    {"id": 2, "ad": "Mantar üretim", "aktif": False},  # 2025: Yeni yönetmelikte tarımsal yapı olarak tanımlı değil
    {"id": 3, "ad": "Sera", "aktif": True},
    {"id": 4, "ad": "Arıcılık", "aktif": True},
    {"id": 5, "ad": "Hububat ve yem depolama silosu", "aktif": False},  # 2025: Silo olarak tanımlı değil (depo/kurutma ayrı)
    {"id": 6, "ad": "Tarımsal amaçlı depo", "aktif": True},
    {"id": 7, "ad": "Lisanslı depolar", "aktif": False},  # 2025: Yeni yönetmelikte tanımlı değil
    {"id": 8, "ad": "Tarımsal ürün yıkama", "aktif": True},
    {"id": 9, "ad": "Hububat, çeltik, ceviz ve ayçiçeği kurutma", "aktif": True},  # 2025: "ceviz" eklendi
    {"id": 10, "ad": "Açıkta meyve/sebze kurutma", "aktif": False},  # 2025: Yeni yönetmelikte tanımlı değil
    {"id": 11, "ad": "Zeytinyağı fabrikası", "aktif": False},  # 2025: Entegre tesis sayılır, tarımsal yapı değil
    {"id": 12, "ad": "Su depolama", "aktif": True},
    {"id": 13, "ad": "Su kuyuları", "aktif": True},
    {"id": 14, "ad": "Bağ evi", "aktif": True},
    {"id": 15, "ad": "Su depolama ve pompaj sistemi", "aktif": True},
    {"id": 16, "ad": "Soğuk hava deposu", "aktif": False},  # 2025: Yeni yönetmelikte tanımlı değil
    {"id": 17, "ad": "Süt Sığırcılığı", "aktif": True},
    {"id": 18, "ad": "Ağıl (küçükbaş)", "aktif": True},
    {"id": 19, "ad": "Kümes (yumurtacı tavuk)", "aktif": True},
    {"id": 20, "ad": "Kümes (etçi tavuk)", "aktif": True},
    {"id": 21, "ad": "Kümes (gezen tavuk)", "aktif": True},
    {"id": 22, "ad": "Kümes (hindi)", "aktif": True},
    {"id": 23, "ad": "Kaz Ördek çiftliği", "aktif": True},
    {"id": 24, "ad": "Hara (at üretimi)", "aktif": True},
    {"id": 25, "ad": "İpek böcekçiliği", "aktif": True},
    {"id": 26, "ad": "Evcil hayvan ve bilimsel araştırma hayvanı üretim", "aktif": False},  # 2025: Yeni yönetmelikte tanımlı değil
    {"id": 27, "ad": "Besi Sığırcılığı", "aktif": True},
    {"id": 28, "ad": "Zeytinyağı üretim tesisi", "aktif": False},  # 2025: Entegre tesis sayılır, tarımsal yapı değil
    # 2025 Yönetmelik: Yeni eklenen yapı türleri
    {"id": 29, "ad": "Fide üretim tesisi", "aktif": True},
    {"id": 30, "ad": "Fidan üretim tesisi", "aktif": True},
    {"id": 31, "ad": "Sahipsiz hayvan barınağı", "aktif": True},
    {"id": 32, "ad": "Sundurma", "aktif": True},
    {"id": 33, "ad": "Çiftlik atölyesi", "aktif": True},
    {"id": 34, "ad": "Su ürünleri üretim tesisi", "aktif": True},
    {"id": 35, "ad": "Deve kuşu üretim tesisi", "aktif": True},
    {"id": 36, "ad": "Gübre deposu", "aktif": True},
    {"id": 37, "ad": "Mandıra", "aktif": True},
    {"id": 38, "ad": "Un değirmeni", "aktif": True},
    {"id": 39, "ad": "Tarımsal amaçlı teleferik", "aktif": True},
    {"id": 40, "ad": "Hayvan içme suyu göleti", "aktif": True},
    {"id": 41, "ad": "İslim ünitesi", "aktif": True},
    {"id": 42, "ad": "Muz sarartma ünitesi", "aktif": True},
    {"id": 43, "ad": "Tarımsal AR-GE tesisi", "aktif": True},
]

# Pasif yapı ID'leri (hızlı erişim için)
PASIF_YAPI_IDLERI = {yapi["id"] for yapi in YAPI_TURLERI if not yapi["aktif"]}

# Aktif yapı türleri listesi (API ve frontend için)
AKTIF_YAPI_TURLERI = [yapi for yapi in YAPI_TURLERI if yapi["aktif"]]

# Arazi tipi ID'lerinden adlarına mapping
ARAZI_TIPI_ID_TO_AD = {arazi["id"]: arazi["ad"] for arazi in ARAZI_TIPLERI}

# Arazi tipi adlarından ID'lere mapping
ARAZI_TIPI_AD_TO_ID = {arazi["ad"]: arazi["id"] for arazi in ARAZI_TIPLERI}

# Yapı türü ID'lerinden adlarına mapping
YAPI_TURU_ID_TO_AD = {yapi["id"]: yapi["ad"] for yapi in YAPI_TURLERI}

# Yapı türü adlarından ID'lere mapping
YAPI_TURU_AD_TO_ID = {yapi["ad"]: yapi["id"] for yapi in YAPI_TURLERI}

# Sera için sabitler
SERA_VARSAYILAN_ALAN_ORANI = 0.8

# Emsal oranları
EMSAL_ORANI_MARJINAL = 0.20  # Marjinal tarım arazileri için %20
EMSAL_ORANI_MUTLAK_DIKILI = 0.05  # Mutlak tarım arazisi, dikili tarım arazisi ve özel ürün arazileri için %5

# Genel yapı türleri listesi - YAPI_TURLERI'nden dinamik olarak oluşturulan
GENEL_YAPI_TURLERI_LISTESI = [yapi["ad"] for yapi in YAPI_TURLERI]

# Aktif yapı türleri listesi (sadece aktif olanlar)
AKTIF_YAPI_TURLERI_LISTESI = [yapi["ad"] for yapi in YAPI_TURLERI if yapi["aktif"]]

# Özel arazi tipi filtreleme kuralları
YAPI_ARAZI_FILTRELEME = {
    "Zeytinyağı fabrikası": {
        "allowed_arazi_types": [8],  # Sadece Zeytinlik (id: 8)
        "reason": "Zeytinyağı fabrikası sadece zeytinlik vasıflı arazilerde kurulabilir"
    },
    "Zeytinyağı üretim tesisi": {
        "allowed_arazi_types": [8],  # Sadece Zeytinlik (id: 8)
        "reason": "Zeytinyağı üretim tesisi sadece zeytinlik vasıflı arazilerde kurulabilir"
    }
}

# Zeytinyağı fabrikası ve üretim tesisi hariç diğer yapılar için zeytinlik yasağı
ZEYTINLIK_YASAGI_OLAN_YAPILAR = [
    yapi["ad"] for yapi in YAPI_TURLERI 
    if yapi["ad"] not in ["Zeytinyağı fabrikası", "Zeytinyağı üretim tesisi"]
]
