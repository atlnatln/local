"""
Bağ Evi hesaplama modülü - Mesaj formatlaması
Bu modül zengin HTML mesajları oluşturur
"""

import html
from typing import Dict, List, Any, Optional, Union


def render_success_message(arazi_vasfi: str, alan_detay: Dict[str, Any], 
                          agac_detaylari: Optional[str] = None,
                          manuel_kontrol_sonucu: Optional[Union[str, Dict[str, Any]]] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
    """Başarılı durum için zengin HTML mesajı oluşturur"""
    
    hesaplama_tipi = "DETAYLI İNCELEME SONUCU" if manuel_kontrol_sonucu else "VARSAYIMSAL HESAPLAMA SONUCU"
    
    mesaj = f"""<b>{hesaplama_tipi} - {html.escape(arazi_vasfi.upper())}</b><br><br>"""
    
    # Manuel kontrol detayları (eğer varsa)
    if manuel_kontrol_sonucu:
        mesaj += "<b>🔍 Manuel Kontrol Detayları:</b><br>"
        mesaj += render_manuel_kontrol_detay(manuel_kontrol_sonucu)
        mesaj += "<br>"
    
    # Arazi bilgileri
    mesaj += "<b>📋 Arazi Bilgileri:</b><br>"
    for alan_tip, detay in alan_detay.items():
        if isinstance(detay, dict):
            deger = detay.get('deger', 0)
            minimum = detay.get('minimum', 0)
            yeterli = detay.get('yeterli', False)
            icon = "✅" if yeterli else "❌"
            mesaj += f"• {alan_tip}: {deger:,.1f} m² (min {minimum:,} m²) {icon}<br>"
        else:
            mesaj += f"• {alan_tip}: {detay}<br>"
    
    mesaj += "<br>"
    
    # Ağaç detayları
    if agac_detaylari and agac_detaylari.strip():
        mesaj += f"<b>🌳 Ağaç Detayları:</b><br>{agac_detaylari}<br><br>"
    
    # İzin bilgileri
    mesaj += "<b>✅ Değerlendirme:</b><br>"
    if 'dikili' in arazi_vasfi.lower():
        mesaj += "Dikili alan kontrolü başarıyla sağlanmıştır.<br><br>"
    else:
        mesaj += f"{arazi_vasfi.title()} arazi alan kontrolü başarıyla sağlanmıştır.<br><br>"
    
    mesaj += render_izin_verilebilir_footer()
    
    # Öneriler ve uyarılar
    mesaj += render_oneriler(manuel_kontrol_sonucu, arazi_vasfi)
    
    return mesaj


def render_failure_message(arazi_vasfi: str, alan_detay: Dict[str, Any], 
                          agac_detaylari: Optional[str] = None,
                          manuel_kontrol_sonucu: Optional[Union[str, Dict[str, Any]]] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
    """Başarısız durum için zengin HTML mesajı oluşturur"""
    
    hesaplama_tipi = "DETAYLI İNCELEME SONUCU" if manuel_kontrol_sonucu else "VARSAYIMSAL HESAPLAMA SONUCU"
    
    # Arazi vasfı güvenli hale getir
    arazi_vasfi_safe = str(arazi_vasfi) if arazi_vasfi is not None else "Bilinmeyen"
    
    # Başlık için durum belirle - başarısızlık mesajında gerçek durumu yansıt
    if 'dikili' in arazi_vasfi_safe.lower():
        baslik_durumu = "DIKILI VASIF ŞARTLARI KARŞILANMIYOR"
    else:
        baslik_durumu = f"{arazi_vasfi_safe.upper()} ŞARTLARI KARŞILANMIYOR"
    
    mesaj = f"""<b>{hesaplama_tipi} - {html.escape(baslik_durumu)}</b><br><br>"""
    
    # Arazi bilgileri
    mesaj += "<b>📋 Arazi Bilgileri:</b><br>"
    for alan_tip, detay in alan_detay.items():
        if isinstance(detay, dict):
            deger = detay.get('deger', 0)
            minimum = detay.get('minimum', 0)
            yeterli = detay.get('yeterli', False)
            icon = "✅" if yeterli else "❌"
            mesaj += f"• {alan_tip}: {deger:,.1f} m² (min {minimum:,} m²) {icon}<br>"
        else:
            mesaj += f"• {alan_tip}: {detay}<br>"
    
    mesaj += "<br>"
    
    # Değerlendirme sonucu
    mesaj += "<b>❌ Değerlendirme:</b><br>"
    if 'dikili' in arazi_vasfi_safe.lower():
        mesaj += "Dikili alan kontrolü sağlanamamaktadır:<br><br>"
    else:
        mesaj += f"{arazi_vasfi_safe.title()} arazi alan kontrolü sağlanamamaktadır:<br><br>"
    
    # Manuel kontrol detayları
    if manuel_kontrol_sonucu:
        mesaj += "<b>🔍 Manuel Kontrol Bilgisi:</b><br>"
        if isinstance(manuel_kontrol_sonucu, str):
            mesaj += f"• Sonuç: {manuel_kontrol_sonucu}<br><br>"
        else:
            mesaj += render_manuel_kontrol_detay(manuel_kontrol_sonucu)
            mesaj += "<br>"
    
    # Ağaç detayları
    if agac_detaylari and agac_detaylari.strip():
        mesaj += f"<b>🌳 Ağaç Detayları:</b><br>{agac_detaylari}<br><br>"
    
def render_failure_message(arazi_vasfi: str, alan_detay: Dict[str, Any], 
                          agac_detaylari: Optional[str] = None,
                          manuel_kontrol_sonucu: Optional[Union[str, Dict[str, Any]]] = None,
                          config: Optional[Dict[str, Any]] = None) -> str:
    """Başarısız durum için zengin HTML mesajı oluşturur"""
    
    hesaplama_tipi = "DETAYLI İNCELEME SONUCU" if manuel_kontrol_sonucu else "VARSAYIMSAL HESAPLAMA SONUCU"
    
    # Arazi vasfı güvenli hale getir
    arazi_vasfi_safe = str(arazi_vasfi) if arazi_vasfi is not None else "Bilinmeyen"
    
    # Başlık için durum belirle - başarısızlık mesajında gerçek durumu yansıt
    if 'dikili' in arazi_vasfi_safe.lower():
        baslik_durumu = "DIKILI VASIF ŞARTLARI KARŞILANMIYOR"
    else:
        baslik_durumu = f"{arazi_vasfi_safe.upper()} ŞARTLARI KARŞILANMIYOR"
    
    mesaj = f"""<b>{hesaplama_tipi} - {html.escape(baslik_durumu)}</b><br><br>"""
    
    # Arazi bilgileri
    mesaj += "<b>📋 Arazi Bilgileri:</b><br>"
    for alan_tip, detay in alan_detay.items():
        if isinstance(detay, dict):
            deger = detay.get('deger', 0)
            minimum = detay.get('minimum', 0)
            yeterli = detay.get('yeterli', False)
            icon = "✅" if yeterli else "❌"
            mesaj += f"• {alan_tip}: {deger:,.1f} m² (min {minimum:,} m²) {icon}<br>"
        else:
            mesaj += f"• {alan_tip}: {detay}<br>"
    
    mesaj += "<br>"
    
    # Değerlendirme sonucu
    mesaj += "<b>❌ Değerlendirme:</b><br>"
    if 'dikili' in arazi_vasfi_safe.lower():
        mesaj += "Dikili vasıflı arazi kriterleri karşılanmamaktadır.<br><br>"
    else:
        mesaj += f"{arazi_vasfi_safe.title()} arazi alan kontrolü sağlanamamaktadır:<br><br>"
    
    # Manuel kontrol detayları
    if manuel_kontrol_sonucu:
        mesaj += "<b>🔍 Detaylı İnceleme Bilgisi:</b><br>"
        mesaj += render_manuel_kontrol_detay(manuel_kontrol_sonucu)
        mesaj += "<br>"
    
    # Ağaç detayları
    if agac_detaylari and agac_detaylari.strip():
        mesaj += f"<b>🌳 Ağaç Detayları:</b><br>{agac_detaylari}<br><br>"
    
    # Kullanıcı dostu açıklama
    mesaj += "<b>💡 Neden Bağ Evi Yapılamıyor?</b><br>"
    
    # Alan yetersizliği kontrolü
    alan_yetersiz = False
    for alan_tip, detay in alan_detay.items():
        if isinstance(detay, dict) and not detay.get('yeterli', False):
            alan_yetersiz = True
            break
    
    if alan_yetersiz:
        if 'dikili' in arazi_vasfi_safe.lower():
            mesaj += "Dikili alanınız minimum gereken büyüklüğün altındadır.<br><br>"
        else:
            mesaj += "Arazinizin büyüklüğü minimum gereken alanın altındadır.<br><br>"
    elif agac_detaylari and agac_detaylari.strip():
        mesaj += "Arazi büyüklüğünüz yeterli ancak ağaç yoğunluğunuz bağ evi kriterlerini karşılayamıyor.<br><br>"
    else:
        mesaj += "Arazi vasfınız veya büyüklüğünüz bağ evi kriterlerini karşılamıyor.<br><br>"
    
    return mesaj


def _get_agac_adi_from_id(agac_id: str) -> str:
    """Ağaç ID'sinden ağaç adını döndürür"""
    agac_mapping = {
        '1': 'Kestane',
        '2': 'Harnup',
        '3': 'İncir (Kurutmalık)',
        '4': 'İncir (Taze)',
        '5': 'Armut',
        '6': 'Elma',
        '7': 'Trabzon Hurması',
        '8': 'Kiraz',
        '9': 'Ayva',
        '10': 'Nar',
        '11': 'Erik',
        '12': 'Kayısı',
        '13': 'Zerdali',
        '14': 'Muşmula',
        '15': 'Yenidünya',
        '16': 'Şeftali',
        '17': 'Vişne',
        '18': 'Ceviz',
        '19': 'Dut',
        '20': 'Üvez',
        '21': 'Ünnap',
        '22': 'Kızılcık',
        '23': 'Limon',
        '24': 'Portakal',
        '25': 'Turunç',
        '26': 'Altıntop',
        '27': 'Mandarin',
        '28': 'Avokado',
        '29': 'Fındık (Düz)',
        '30': 'Fındık (Eğimli)',
        '31': 'Gül',
        '32': 'Çay',
        '33': 'Kivi',
        '34': 'Böğürtlen',
        '35': 'Ahududu',
        '36': 'Likapa',
        '37': 'Muz (Örtü altı)',
        '38': 'Muz (Açıkta)',
        '39': 'Kuşburnu',
        '40': 'Mürver',
        '41': 'Frenk Üzümü',
        '42': 'Bektaşi Üzümü',
        '43': 'Aronya',
    }
    return agac_mapping.get(str(agac_id).lower(), str(agac_id).title())


def render_manuel_kontrol_detay(manuel_kontrol_sonucu: Dict[str, Any]) -> str:
    """
    Manuel kontrol sonucundan HTML detay kısmı oluşturur

    Args:
        manuel_kontrol_sonucu: Frontend'den gelen manuel kontrol verisi

    Returns:
        str: Sanitize edilmiş HTML string
    """
    parts = []

    # String olarak gelen manuel kontrol sonuçlarını atla
    if not isinstance(manuel_kontrol_sonucu, dict):
        return ""

    # Eklenen ağaç bilgilerini göster
    eklenen_agaclar = manuel_kontrol_sonucu.get('eklenenAgaclar', [])
    if eklenen_agaclar:
        parts.append("<b>• Eklenen Ağaçlar:</b><br>")
        for agac in eklenen_agaclar:
            agac_tur_id = agac.get('secilenAgacTuru', agac.get('agacTuru', 'Bilinmiyor'))
            agac_adi = _get_agac_adi_from_id(agac_tur_id)
            agac_sayisi = int(agac.get('agacSayisi') or agac.get('sayi') or 0)
            parts.append(f"  - {html.escape(agac_adi)}: {agac_sayisi} adet<br>")
        parts.append("<br>")

    # Yeterlilik bilgileri
    normalized = _normalize_manual_yeterlilik(manuel_kontrol_sonucu)
    if normalized:
        oran = normalized.get('oran', 0.0)
        minimum = normalized.get('minimum', 100.0)
        eksik_adet = normalized.get('eksik_adet')
        yeterli = normalized.get('yeterli', False)
        ok_icon = "✅" if yeterli else "❌"

        parts.append(f"<b>• Ağaç Yeterlilik Oranı:</b> %{oran:.1f} (min: %{minimum}) {ok_icon}")
        if eksik_adet is not None and eksik_adet > 0:
            parts.append(f" - {eksik_adet} ağaç eksik")
        parts.append("<br>")

    # Haritadan alınan alan bilgileri
    dikili_alan = manuel_kontrol_sonucu.get('dikiliAlan', 0)
    tarla_alani = manuel_kontrol_sonucu.get('tarlaAlani', 0)
    zeytinlik_alani = manuel_kontrol_sonucu.get('zeytinlikAlani', 0)

    if dikili_alan > 0:
        parts.append(f"<b>• Haritadan Ölçülen Dikili Alan:</b> {dikili_alan:,} m²<br>")
    if tarla_alani > 0:
        parts.append(f"<b>• Haritadan Ölçülen Tarla Alanı:</b> {tarla_alani:,} m²<br>")
    if zeytinlik_alani > 0:
        parts.append(f"<b>• Haritadan Ölçülen Zeytinlik Alanı:</b> {zeytinlik_alani:,} m²<br>")

    return "".join(parts).replace(",", ".")


def render_izin_verilebilir_footer(max_taban_alani: int = 30, max_toplam_alan: int = 60) -> str:
    """Başarılı sonuç için footer HTML"""
    return f"""
    <b>🏠 Bağ Evi İzni VERİLEBİLİR:</b><br>
    • Maksimum taban alanı: {max_taban_alani} m²<br>
    • Maksimum toplam inşaat alanı: {max_toplam_alan} m²<br>
    """


def render_oneriler(manuel_kontrol_sonucu: Optional[Dict[str, Any]], arazi_vasfi: str) -> str:
    """Öneriler ve uyarılar kısmını render eder"""
    if manuel_kontrol_sonucu:
        return ""  # Manuel kontrol varsa öneride gerek yok

    if arazi_vasfi == "Dikili vasıflı":
        return """<br><b>💡 ÖNERİ:</b><br>
        Dikili vasıflı arazide ağaç yoğunluğunun uygun olduğundan emin olmak için dikili alan kontrolü yapmanız önerilir.<br>"""
    else:
        return """<br><b>⚠️ UYARI:</b><br>
        Bu hesaplama girdiğiniz bilgilerin doğru olduğu varsayımıyla yapılmıştır. Manuel kontrol yapmanız önerilir."""


def _alan_tipi_to_display_name(alan_tipi: str) -> str:
    """Alan tipi adını kullanıcı dostu isme çevirir"""
    display_names = {
        "dikili_alani": "Dikili Alan",
        "tarla_alani": "Tarla Alanı",
        "zeytinlik_alani": "Zeytinlik Alanı",
        "buyukluk_m2": "Toplam Alan",
        "toplam_alan": "Toplam Alan"
    }
    return display_names.get(alan_tipi, alan_tipi.replace('_', ' ').title())


def _normalize_manual_yeterlilik(manuel_kontrol_sonucu: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Manuel kontrol sonucundan yeterlilik bilgisini normalize eder
    Bu fonksiyon bag_evi.py'den kopyalandı, gelecekte ortak yere taşınabilir
    """
    if not manuel_kontrol_sonucu:
        return None

    # Olası konumlar
    possible = None
    if isinstance(manuel_kontrol_sonucu, dict):
        mk = manuel_kontrol_sonucu.get('dikiliAlanKontrolSonucu') or manuel_kontrol_sonucu.get('dikiliAlanKontrol') or manuel_kontrol_sonucu
        if isinstance(mk, dict):
            possible = mk.get('yeterlilik') or manuel_kontrol_sonucu.get('yeterlilik') or mk
        else:
            possible = manuel_kontrol_sonucu.get('yeterlilik') or manuel_kontrol_sonucu

    if not possible or not isinstance(possible, dict):
        return None

    # Normalize keys
    yeterli = possible.get('yeterli')
    if yeterli is None:
        yeterli = possible.get('sufficient') or possible.get('is_sufficient') or False

    # Oran
    oran = None
    for k in ('oran', 'yeterlilik_orani', 'yogunlukOrani', 'agacYogTlugu', 'oran_deger'):
        if possible.get(k) is not None:
            try:
                oran = float(possible.get(k))
                break
            except Exception:
                pass
    if oran is None:
        oran = 0.0

    # Minimum
    minimum = None
    for k in ('minimumOran', 'minimum_yeterlilik', 'minimum_yet'):
        if possible.get(k) is not None:
            try:
                minimum = float(possible.get(k))
                break
            except Exception:
                pass
    if minimum is None:
        minimum = 100.0

    return {
        'yeterli': bool(yeterli),
        'oran': float(oran),
        'minimum': float(minimum),
        'eksik_adet': None  # Bu kısım sonraki PR'da implement edilir
    }


# Legacy wrapper functions for backwards compatibility
def generate_success_html(data: Dict[str, Any]) -> str:
    """Wrapper for legacy tests expecting generate_success_html"""
    title = "✅ İzin Verilebilir" if data.get('success', False) else "✅ Durum"
    arazi_vasfi = data.get('arazi_vasfi') or data.get('izin_durumu', '')
    alan_detay = data.get('alan_detaylari') or data.get('alan_detay') or {}
    agac_html = data.get('agac_detaylari_html') or ''
    manual = data.get('manual_html') or None
    return render_message(title, str(arazi_vasfi), alan_detay, agac_detaylari_html=agac_html, manuel_info_html=manual)


def generate_error_html(data: Dict[str, Any]) -> str:
    """Wrapper for legacy tests expecting generate_error_html"""
    title = "❌ İzin Verilemez"
    arazi_vasfi = data.get('arazi_vasfi') or data.get('izin_durumu', '')
    alan_detay = data.get('alan_detaylari') or {}
    return render_message(title, str(arazi_vasfi), alan_detay, agac_detaylari_html=None, manuel_info_html=None)


def generate_warning_html(data: Dict[str, Any]) -> str:
    """Wrapper for legacy tests expecting generate_warning_html"""
    title = "⚠️ Uyarı"
    arazi_vasfi = data.get('arazi_vasfi') or ''
    alan_detay = data.get('alan_detaylari') or {}
    return render_message(title, str(arazi_vasfi), alan_detay, agac_detaylari_html=None, manuel_info_html=None)


# Eski sistem uyumluluğu için
def render_message(title: str, arazi_vasfi: str, alan_detay: Dict[str, Any],
                  agac_detaylari_html: Optional[str] = None,
                  manuel_info_html: Optional[str] = None) -> str:
    """Eski sistem uyumluluğu için basit mesaj renderer"""
    
    mesaj = f"<b>{html.escape(title)}</b><br><br>"
    
    if alan_detay:
        mesaj += "<b>📋 Arazi Bilgileri:</b><br>"
        for alan_tip, detay in alan_detay.items():
            if isinstance(detay, dict):
                deger = detay.get('deger', 0)
                minimum = detay.get('minimum', 0)
                yeterli = detay.get('yeterli', False)
                icon = "✅" if yeterli else "❌"
                mesaj += f"• {alan_tip}: {deger:,.1f} m² (min {minimum:,} m²) {icon}<br>"
            else:
                mesaj += f"• {alan_tip}: {detay}<br>"
    
    if agac_detaylari_html:
        mesaj += f"<br>{agac_detaylari_html}<br>"
    
    if manuel_info_html:
        mesaj += f"<br>{manuel_info_html}"
    
    return mesaj


def generate_success_html(data: Dict[str, Any]) -> str:
    """Test uyumluluğu için - başarı mesajı üretir"""
    title = "İzin Verilebilir (Varsayımsal)"
    return f"<b>{html.escape(title)}</b><br><br><b>📋 Arazi Bilgileri:</b><br>Hesaplama tamamlandı."


def generate_error_html(data: Dict[str, Any]) -> str:
    """Test uyumluluğu için - hata mesajı üretir"""
    title = "İzin Verilemez"
    return f"<b>{html.escape(title)}</b><br><br><b>📋 Arazi Bilgileri:</b><br>Hesaplama başarısız."


def generate_warning_html(data: Dict[str, Any]) -> str:
    """Test uyumluluğu için - uyarı mesajı üretir"""
    title = "Uyarı"
    return f"<b>{html.escape(title)}</b><br><br><b>📋 Arazi Bilgileri:</b><br>Dikkat edilmesi gereken durumlar var."


def render_dikili_validasyon_hatasi(dikili_validasyon: Dict[str, Any]) -> str:
    """Dikili validasyon hatası için kullanıcı dostu mesaj oluşturur"""
    if not dikili_validasyon:
        return ""
    
    mesaj = "<b>🌳 Dikili Arazi Değerlendirmesi:</b><br>"
    
    # Ana mesajı kullanıcı dostu hale getir
    if dikili_validasyon.get('mesaj'):
        orijinal_mesaj = dikili_validasyon['mesaj']
        
        # Teknik mesajları kullanıcı dostu mesajlara çevir
        if "karşılanmıyor" in orijinal_mesaj and "Gereken:" in orijinal_mesaj:
            # "❌ Ceviz (normal) dikili arazi kriterleri karşılanmıyor. Gereken: 100 adet, Mevcut: 50 adet, Eksik: 50 adet"
            # gibi mesajları parçala
            try:
                agac_adi = "Bilinmeyen Ağaç"
                if "Ceviz" in orijinal_mesaj:
                    agac_adi = "Ceviz"
                elif "Badem" in orijinal_mesaj:
                    agac_adi = "Badem"
                elif "Antep" in orijinal_mesaj:
                    agac_adi = "Antep Fıstığı"
                elif "İncir" in orijinal_mesaj:
                    agac_adi = "İncir"
                elif "Nar" in orijinal_mesaj:
                    agac_adi = "Nar"
                elif "Üzüm" in orijinal_mesaj:
                    agac_adi = "Üzüm"
                elif "Zeytin" in orijinal_mesaj:
                    agac_adi = "Zeytin"
                
                mesaj += f"• <b>{agac_adi} ağaçlarınız</b> dikili arazi kriterlerini karşılamıyor<br>"
                
                # Sayısal bilgileri çıkar
                import re
                sayilar = re.findall(r'\d+', orijinal_mesaj)
                if len(sayilar) >= 3:
                    gereken = sayilar[0]
                    mevcut = sayilar[1] 
                    eksik = sayilar[2]
                    mesaj += f"• <b>Gereken:</b> {gereken} adet, <b>Mevcut:</b> {mevcut} adet, <b>Eksik:</b> {eksik} adet<br>"
                    
            except:
                mesaj += f"• {html.escape(orijinal_mesaj)}<br>"
        else:
            mesaj += f"• {html.escape(orijinal_mesaj)}<br>"
    
    # Ağaç türü bilgisi
    if dikili_validasyon.get('agac_turu_adi'):
        mesaj += f"• <b>Ağaç Türü:</b> {html.escape(dikili_validasyon['agac_turu_adi'])}<br>"
    
    # Alan bilgisi
    if dikili_validasyon.get('alan_dekar'):
        mesaj += f"• <b>Dikili Alan:</b> {dikili_validasyon['alan_dekar']:.2f} dekar<br>"
    
    # Minimum gereksinim bilgisi
    if dikili_validasyon.get('minimum_gereksinim'):
        mesaj += f"• <b>Minimum Gereksinim:</b> {dikili_validasyon['minimum_gereksinim']} adet/dekar<br>"
    
    # Mevcut sayı bilgisi
    if dikili_validasyon.get('mevcut_sayisi'):
        mesaj += f"• <b>Mevcut Ağaç Sayısı:</b> {dikili_validasyon['mevcut_sayisi']} adet<br>"
    
    # Detay bilgiler
    detay = dikili_validasyon.get('detay', {})
    if detay:
        if detay.get('gerekli_sayi_toplam'):
            mesaj += f"• <b>Toplam Gerekli Sayı:</b> {detay['gerekli_sayi_toplam']} adet<br>"
    
    # Kullanıcı dostu öneriler ekle
    mesaj += "<br><b>💡 Çözüm Önerileri:</b><br>"
    mesaj += "• Daha fazla ağaç dikerek sayıyı artırın<br>"
    mesaj += "• Farklı bir ağaç türü değerlendirin<br>"
    mesaj += "• İl/ilçe tarım müdürlüğü ile görüşün<br>"
    mesaj += "• Profesyonel fidancılık danışmanlığı alın<br>"
    
    return mesaj + "<br>"


def render_dikili_validasyon_uyarisi(dikili_validasyon: Dict[str, Any]) -> str:
    """Dikili validasyon uyarısı için mesaj oluşturur"""
    if not dikili_validasyon:
        return ""
    
    mesaj = "<b>⚠️ Dikili Arazi Uyarısı:</b><br>"
    
    if dikili_validasyon.get('uyari'):
        mesaj += f"• {html.escape(dikili_validasyon['uyari'])}<br>"
    
    if dikili_validasyon.get('detay'):
        mesaj += f"• {html.escape(dikili_validasyon['detay'])}<br>"
    
    return mesaj + "<br>"
