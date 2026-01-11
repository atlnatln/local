"""
Bu modül, lisanslı depo yapılaşma kurallarını ve hesaplamalarını içerir.
"""

# Sabitleri constants.py'den buraya taşıdık - PHASE 2 DİNAMİK EMSAL
DEFAULT_EMSAL_ORANI = 0.20  # %20 varsayılan emsal oranı (dinamik sistem için)
LISANSLI_DEPO_MIN_ARAZI_M2 = 500  # Minimum arazi büyüklüğü (m²) - küçük işletmeler için uygun hale getirildi

MUSTERMILAT_LISTESI = ["Lisanslı Depo", "Araç yolu", "İdari bina", "Çiftçi dinlenme odası", "Kantar", "Laboratuvar", "Güvenlik odası", "Teremi alanı", "Kule alanı"]

def lisansli_depo_genel_bilgilendirme(
    parsel_buyuklugu_m2: float,
    emsal_orani: float = None  # PHASE 2 DİNAMİK EMSAL PARAMETRESİ
) -> dict:
    """
    Sadece parsel büyüklüğüne göre, lisanslı depo ve müştemilatları için
    genel toplam yapılaşma hakkını hesaplar ve bilgi verir.

    Args:
        parsel_buyuklugu_m2: Toplam parsel (arazi) büyüklüğü (m²).
        emsal_orani: Emsal oranı (None ise varsayılan kullanılır).

    Returns:
        Bilgilendirme mesajını ve hesaplanan değerleri içeren bir sözlük.
    """
    # PHASE 2 DİNAMİK EMSAL SİSTEMİ
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
    
    sonuclar = {
        "giris_bilgileri": {
            "parsel_buyuklugu_m2": parsel_buyuklugu_m2,
        },
        "maks_toplam_kapali_yapi_hakki_m2": 0.0,
        "mesaj": ""
    }

    # Maksimum toplam kapalı yapılaşma hakkını hesapla - DİNAMİK EMSAL
    maks_toplam_kapali_yapi_hakki = parsel_buyuklugu_m2 * kullanilacak_emsal_orani
    sonuclar["maks_toplam_kapali_yapi_hakki_m2"] = maks_toplam_kapali_yapi_hakki

    # Tek tip HTML mesaj üretimi
    mustermilat_html = "<ul>" + "".join([f"<li>{item}</li>" for item in MUSTERMILAT_LISTESI]) + "</ul>"
    detay_mesaj = (
        f"<b>Parsel Büyüklüğü:</b> {parsel_buyuklugu_m2:,.2f} m²<br>"
        f"<b>ÖNEMLİ ŞART: Lisans Belgesi Zorunluluğu</b><br>"
        f"Bu bilgilendirme, yapılması planlanan deponun yürürlükteki mevzuata uygun bir <b>LİSANS BELGESİNE</b> sahip olması veya bu belgeyi alabilecek olması koşuluna dayanmaktadır.<br>"
        f"<button style='margin:8px 0' onclick=\"if(window.openLisansliDepoModal){{openLisansliDepoModal();}}else{{window.open('https://ticaret.gov.tr/ic-ticaret/mevzuat/lisansli-depoculuk','_blank');}}\">Lisanslı Depoculuk Mevzuatını Görüntüle</button><br><hr>"
        f"<b>1) TOPLAM KAPALI YAPILAŞMA HAKKINIZ</b><br>"
        f"Maksimum kapalı yapılaşma hakkınız (%{kullanilacak_emsal_orani*100:.0f} emsal oranı): <b>{maks_toplam_kapali_yapi_hakki:,.2f} m²</b><br>"
        f"Bu oran marjinal tarım arazisi için geçerli bir değerdir. Güncel ve kesin emsal oranları Tarım ve Orman İl Müdürlüğünce yapılacak etüt sonucu belirlenecektir.<br>"
        f"<b>2) YAPILABİLECEK TESİS VE MÜŞTEMİLATLAR (Lisans Belgesi Kapsamında)</b><br>"
        f"{mustermilat_html}"
        f"<b>3) DİKKAT EDİLMESİ GEREKENLER</b><br>"
        f"Lisanslı deponun kendisi ve yukarıda listelenen müştemilatlardan kapalı alan niteliğinde olanların toplamı, <b>{maks_toplam_kapali_yapi_hakki:,.2f} m²</b>'yi aşmamalıdır.<br>"
        f"Her müştemilatın büyüklüğü, projenizin ihtiyaçlarına ve ilgili standartlara göre belirlenmelidir.<br>"
        f"Araç yolu gibi tamamen açık alanlar ve diğer müştemilatların (ör. teremi alanı, kule alanı) yerleşimi için ilgili imar planı ve yönetmeliklere uyulmalıdır. Açık alanlar genellikle emsal hesabına dahil edilmez, ancak toplam parsel kullanımını etkileyebilir.<br><hr>"
    )
    sonuclar["mesaj"] = _format_html_message(
        "TESİS YAPILABİLİR",
        detay_mesaj,
        parsel_buyuklugu_m2,
        maks_toplam_kapali_yapi_hakki,
        kullanilacak_emsal_orani
    )

    sonuclar["izin_durumu"] = "izin_verilebilir"
    
    return sonuclar


def lisansli_depo_degerlendir(arazi_buyuklugu_m2: float, emsal_orani: float = None) -> dict:
    """
    Arazi büyüklüğüne göre lisanslı depo kurulup kurulamayacağını değerlendirir.
    
    Args:
        arazi_buyuklugu_m2: Arazinin büyüklüğü (m²)
        emsal_orani: Emsal oranı (None ise varsayılan kullanılır)
        
    Returns:
        dict: Değerlendirme sonuçlarını içeren sözlük
    """
    sonuclar = lisansli_depo_genel_bilgilendirme(
        arazi_buyuklugu_m2, 
        emsal_orani  # PHASE 2 DİNAMİK EMSAL PARAMETRESİ
    )
    
    if arazi_buyuklugu_m2 < LISANSLI_DEPO_MIN_ARAZI_M2:
        sonuclar["izin_durumu"] = "TESİS YAPILAMAZ"
        sonuclar["mesaj"] = _format_html_message(
            "TESİS YAPILAMAZ",
            f"Girdiğiniz {arazi_buyuklugu_m2:.2f} m² arazi büyüklüğü, lisanslı depo tesisi için önerilen minimum büyüklük olan {LISANSLI_DEPO_MIN_ARAZI_M2} m²'nin altındadır. Lisanslı depo için daha büyük bir arazi önerilmektedir.",
            arazi_buyuklugu_m2, 0, emsal_orani
        )
    
    return sonuclar

def lisansli_depo_degerlendir_api(data, emsal_orani: float = None):
    """
    API için lisanslı depo değerlendirme fonksiyonu - PHASE 2 DİNAMİK EMSAL
    
    Args:
        data: {
            'alan_m2': float  # Sadece arazi büyüklüğü gerekli
        }
        emsal_orani: Dinamik emsal oranı (None ise varsayılan kullanılır)
    
    Returns:
        dict: Değerlendirme sonucu
    """
    try:
        # PHASE 2 DİNAMİK EMSAL SİSTEMİ
        kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
        
        # Parametreleri al - arazi_alani_m2, alan_m2, arazi_buyuklugu_m2 destekle
        arazi_buyuklugu_m2 = float(
            data.get('arazi_alani_m2') or 
            data.get('arazi_buyuklugu_m2') or 
            data.get('alan_m2', 0)
        )
        
        # Girdi kontrolü
        if arazi_buyuklugu_m2 <= 0:
            return {
                'success': False,
                'error': 'Arazi büyüklüğü pozitif olmalıdır',
                'izin_durumu': 'TESİS YAPILAMAZ',
                'mesaj': _format_html_message('TESİS YAPILAMAZ', 'Geçersiz arazi büyüklüğü', arazi_buyuklugu_m2, 0, kullanilacak_emsal_orani)
            }
        
        # Minimum arazi kontrolü
        if arazi_buyuklugu_m2 < LISANSLI_DEPO_MIN_ARAZI_M2:
            return {
                'success': False,
                'error': f'Lisanslı depo için minimum {LISANSLI_DEPO_MIN_ARAZI_M2} m² arazi gereklidir',
                'izin_durumu': 'TESİS YAPILAMAZ',
                'mesaj': _format_html_message(
                    'TESİS YAPILAMAZ', 
                    f'Minimum arazi büyüklüğü: {LISANSLI_DEPO_MIN_ARAZI_M2} m²', 
                    arazi_buyuklugu_m2, 0, kullanilacak_emsal_orani
                )
            }
        
        # Emsal hesaplaması - DİNAMİK EMSAL
        maksimum_emsal_alani = arazi_buyuklugu_m2 * kullanilacak_emsal_orani
        
        # Başarılı durumda
        api_result = {
            'success': True,
            'maksimum_emsal_alani_m2': maksimum_emsal_alani,
            'emsal_orani': kullanilacak_emsal_orani,  # DİNAMİK EMSAL
            'kalan_emsal_hakki_m2': maksimum_emsal_alani,  # Tamamı kullanılabilir
            'izin_durumu': 'TESİS YAPILABİLİR',
            'mesaj': _format_html_message(
                'TESİS YAPILABİLİR',
                f'Lisanslı depo tesisi kurulabilir. Toplam kullanılabilir alan: {maksimum_emsal_alani:.0f} m² (depo, araç yolu, idari bina, laboratuvar vb. için)',
                arazi_buyuklugu_m2, maksimum_emsal_alani, kullanilacak_emsal_orani
            )
        }
        
        return api_result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'izin_durumu': 'TESİS YAPILAMAZ',
            'mesaj': _format_html_message('TESİS YAPILAMAZ', f'Hesaplama hatası: {str(e)}', 0, 0)
        }


def _format_html_message(izin_durumu, mesaj, arazi_buyuklugu_m2, maksimum_emsal=0, emsal_orani=None):
    """HTML formatında mesaj oluştur - kullanıcı dostu versiyon"""
    kullanilacak_emsal_orani = emsal_orani if emsal_orani is not None else DEFAULT_EMSAL_ORANI
    durum_color = "#28a745" if izin_durumu == "TESİS YAPILABİLİR" else "#dc3545"
    durum_icon = "✅" if izin_durumu == "TESİS YAPILABİLİR" else "❌"
    mustermilat_html = "<ul>" + "".join([f"<li>{item}</li>" for item in MUSTERMILAT_LISTESI]) + "</ul>"
    return f"""
    <style>
        .lisansli-depo-sonuc {{font-family: Arial, sans-serif;}}
        .lisansli-depo-sonuc h3 {{color: {durum_color}; margin-bottom: 15px;}}
        .lisansli-depo-sonuc .baslik {{font-weight: bold; margin-top: 15px; margin-bottom: 8px;}}
        .lisansli-depo-sonuc table {{border-collapse: collapse; width: 100%; margin-bottom: 20px;}}
        .lisansli-depo-sonuc th, .lisansli-depo-sonuc td {{border: 1px solid #ddd; padding: 8px; text-align: left;}}
        .lisansli-depo-sonuc th {{background-color: #f2f2f2;}}
        .lisansli-depo-sonuc .uyari {{color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .lisansli-depo-sonuc .basarili {{color: #155724; background-color: #d4edda; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .lisansli-depo-sonuc .hata {{color: #721c24; background-color: #f8d7da; padding: 10px; border-radius: 4px; margin: 10px 0;}}
        .lisansli-depo-sonuc .notlar {{font-size: 0.9em; font-style: italic; margin-top: 20px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;}}
    </style>
    <div class="lisansli-depo-sonuc">
        <h3>{durum_icon} LİSANSLI DEPO TESİSİ {izin_durumu}</h3>
        <div class="baslik">GENEL DURUM</div>
        <table>
            <tr>
                <th>Arazi Büyüklüğü</th>
                <td>{arazi_buyuklugu_m2:,.0f} m²</td>
            </tr>
            <tr>
                <th>Maksimum İzin Verilen Alan</th>
                <td>{maksimum_emsal:,.0f} m²</td>
            </tr>
            <tr>
                <th>Emsal Oranı</th>
                <td>%{kullanilacak_emsal_orani*100:.0f}</td>
            </tr>
            <tr>
                <th>Minimum Arazi Gereksinimi</th>
                <td>{LISANSLI_DEPO_MIN_ARAZI_M2:,.0f} m²</td>
            </tr>
            <tr>
                <th>İzin Durumu</th>
                <td>{izin_durumu}</td>
            </tr>
        </table>
        <div class="baslik">YAPILABİLECEK TESİS VE MÜŞTEMİLATLAR</div>
        {mustermilat_html}
        <div class="notlar">
            <b>Planlama Notları:</b><br>
            - Lisanslı depo ve müştemilatların toplam kapalı alanı maksimum izin verilen alanı aşmamalıdır.<br>
            - Her müştemilatın büyüklüğü, projenizin ihtiyaçlarına ve ilgili standartlara göre belirlenmelidir.<br>
            - Araç yolu gibi tamamen açık alanlar ve diğer müştemilatların (ör. teremi alanı, kule alanı) yerleşimi için ilgili imar planı ve yönetmeliklere uyulmalıdır.<br>
            - Bu değerlendirme tavsiye niteliğindedir. Kesin başvuru için ilgili kurumlara danışınız.<br>
        </div>
    </div>
    """

# --- Kodun Kullanım Örneği ---
if __name__ == "__main__":
    # Test ile arazi büyüklüğü ve dinamik emsal
    parsel_alani_1 = 10000.0  # Örnek bir parsel büyüklüğü
    bilgilendirme_sonucu_1 = lisansli_depo_genel_bilgilendirme(parsel_alani_1)
    
    print(f"--- PARSEL BÜYÜKLÜĞÜ: {parsel_alani_1} m² İÇİN GENEL BİLGİLENDİRME ---")
    print(bilgilendirme_sonucu_1["html_mesaj"])
    print("-" * 70)

    parsel_alani_2 = 3500.0
    bilgilendirme_sonucu_2 = lisansli_depo_genel_bilgilendirme(parsel_alani_2)
    print(f"--- PARSEL BÜYÜKLÜĞÜ: {parsel_alani_2} m² İÇİN GENEL BİLGİLENDİRME ---")
    print(bilgilendirme_sonucu_2["html_mesaj"])
    print("-" * 70)
