"""
Gübre Deposu Hesaplama Modülü

Yeni yönetmelik (2025) - Kriter 11.10

Nitrat Yönetmeliği ve 2025/17 Tebliği kapsamında gübre depolama tesisi.
EK-13 hesaplama cetveline göre alan hesabı yapılır.

Temel formül: Gübre hacmi = hayvan sayısı × günlük gübre üretimi × depolama süresi (gün)
Gübre deposu alanı = gübre hacmi / depo derinliği
"""
import logging

logger = logging.getLogger(__name__)

EMSAL_ORANI = 0.20

# Hayvan başına günlük gübre üretimi (m³/gün) - EK-13 referansları
GUNLUK_GUBRE_URETIMI = {
    "sut_sigiri": 0.045,      # ~45 litre/gün
    "besi_sigiri": 0.035,     # ~35 litre/gün
    "kucukbas": 0.005,        # ~5 litre/gün
    "at": 0.025,              # ~25 litre/gün
    "tavuk_yumurta": 0.00015, # ~0.15 litre/gün
    "tavuk_etci": 0.00012,    # ~0.12 litre/gün
    "hindi": 0.0003,          # ~0.3 litre/gün
}

# Gübre depolama süresi (gün) - Nitrat Yönetmeliği
DEPOLAMA_SURESI_GUN = 120  # 4 ay (minimum)
DEPO_DERINLIGI_M = 4  # metre


def gubre_deposu_degerlendir(data, emsal_orani=None):
    """Gübre deposu hesaplama"""
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0))
        hayvan_tipi = data.get('hayvan_tipi', 'sut_sigiri')
        hayvan_sayisi = int(data.get('hayvan_sayisi', 0))
        depolama_suresi = int(data.get('depolama_suresi_gun', DEPOLAMA_SURESI_GUN))
        
        kullanilacak_emsal = emsal_orani if emsal_orani else EMSAL_ORANI
        emsal_m2 = arazi_m2 * kullanilacak_emsal
        
        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}
        
        if hayvan_sayisi <= 0:
            return {"success": False, "error": "Hayvan sayısını giriniz."}
        
        gunluk_uretim = GUNLUK_GUBRE_URETIMI.get(hayvan_tipi, 0.035)
        
        # Toplam gübre hacmi (m³)
        toplam_hacim = hayvan_sayisi * gunluk_uretim * depolama_suresi
        
        # Gübre deposu taban alanı (m²)
        depo_alani = toplam_hacim / DEPO_DERINLIGI_M
        
        # %20 güvenlik payı
        depo_alani_guvenlikli = depo_alani * 1.20
        
        yapilanabilir = depo_alani_guvenlikli <= emsal_m2
        
        hayvan_tipi_ad = {
            "sut_sigiri": "Süt Sığırı",
            "besi_sigiri": "Besi Sığırı",
            "kucukbas": "Küçükbaş",
            "at": "At",
            "tavuk_yumurta": "Yumurtacı Tavuk",
            "tavuk_etci": "Etçi Tavuk",
            "hindi": "Hindi",
        }.get(hayvan_tipi, hayvan_tipi)
        
        mesaj = "<b>GÜBRE DEPOSU DEĞERLENDİRMESİ (EK-13)</b><br><br>"
        mesaj += f"Arazi Büyüklüğü: {arazi_m2:,.0f} m²<br>"
        mesaj += f"Hayvan Tipi: {hayvan_tipi_ad}<br>"
        mesaj += f"Hayvan Sayısı: {hayvan_sayisi:,}<br>"
        mesaj += f"Depolama Süresi: {depolama_suresi} gün<br>"
        mesaj += f"Günlük Gübre Üretimi: {gunluk_uretim * 1000:.1f} litre/hayvan<br><br>"
        mesaj += f"Toplam Gübre Hacmi: {toplam_hacim:,.2f} m³<br>"
        mesaj += f"Depo Derinliği: {DEPO_DERINLIGI_M} m<br>"
        mesaj += f"Gerekli Depo Alanı: {depo_alani:,.2f} m² (+%20 güvenlik: {depo_alani_guvenlikli:,.2f} m²)<br>"
        mesaj += f"Emsal Alanı: {emsal_m2:,.2f} m²<br><br>"
        
        if yapilanabilir:
            mesaj += f"<b>SONUÇ: GÜBRE DEPOSU YAPILABİLİR</b><br>"
            mesaj += f"Gerekli alan: {depo_alani_guvenlikli:,.2f} m²"
        else:
            mesaj += f"<b>SONUÇ: GÜBRE DEPOSU YAPILAMAZ</b><br>"
            mesaj += f"Gerekli alan ({depo_alani_guvenlikli:,.2f} m²) emsal alanını ({emsal_m2:,.2f} m²) aşmaktadır."
        
        return {
            "success": True,
            "izin_durumu": "izin_verilebilir" if yapilanabilir else "izin_verilemez",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "emsal_m2": emsal_m2,
            "depo_alani_m2": round(depo_alani_guvenlikli, 2),
            "toplam_hacim_m3": round(toplam_hacim, 2),
        }
    except Exception as e:
        logger.error(f"Gübre deposu hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}
