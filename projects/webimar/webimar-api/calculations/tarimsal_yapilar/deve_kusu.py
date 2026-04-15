"""
Deve Kuşu Üretim Tesisi Hesaplama Modülü

Talimat Madde 11.9.3 (2025):

Deve kuşu üretim tesislerinde;
- Kapalı alanın en az 100 m² ve gezinti alanın en az 350 m² olması şartıyla:
  · Bakıcı evi: taban 75 m², toplam inşaat 150 m²
  · İdari bina: taban 75 m², toplam inşaat 150 m²
- Müştemilat (kapalı alan büyüdükçe orantılı artar):
  · Kulüçkahane: kapalı alan kadar
  · Civciv büyütme alanı: kapalı alan kadar
  · Yem deposu: (kapalı alan + gezinti alanı) / 2 kadar

Genel kurallar:
- Kapalı alan emsal DAHİLİNDE (belediye plan notlarına göre %5 veya %20)
- Gezinti alanı emsal DIŞINDA
- Müştemilatlar (kulüçkahane, civciv büyütme, yem deposu) emsal DIŞINDA
- Bakıcı evi ve idari bina emsal DAHİLİNDE
"""
import logging

logger = logging.getLogger(__name__)

# Sabitler - Talimat 11.9.3
MIN_KAPALI_ALAN_M2 = 100
MIN_GEZINTI_ALANI_M2 = 350

BAKICI_EVI_TABAN_M2 = 75
BAKICI_EVI_TOPLAM_M2 = 150
IDARI_BINA_TABAN_M2 = 75
IDARI_BINA_TOPLAM_M2 = 150

# Deve kuşu alan normları (sektör standardı)
KAPALI_ALAN_HAYVAN_BASINA_M2 = 5    # kapalı barınak (yetişkin deve kuşu)
GEZINTI_ALAN_HAYVAN_BASINA_M2 = 20   # gezinti alanı (yetişkin deve kuşu)

# Varsayılan emsal oranları
VARSAYILAN_EMSAL_MARJINAL = 0.20
VARSAYILAN_EMSAL_DIKILI = 0.05


def deve_kusu_degerlendir(data, emsal_orani=None):
    """
    Deve kuşu üretim tesisi hesaplama — Talimat 11.9.3

    Mantık:
    1. Arazi büyüklüğü × emsal oranı = emsal alanı (kapalı yapı bütçesi)
    2. Kapalı alan ≥ 100 m² ve gezinti ≥ 350 m² → tesis kurulabilir
    3. Kapalı alan büyüdükçe müştemilat orantılı artar:
       - Kulüçkahane = kapalı alan kadar
       - Civciv büyütme = kapalı alan kadar
       - Yem deposu = (kapalı alan + gezinti) / 2
    4. Bakıcı evi (75/150) + İdari bina (75/150) → emsal dahilinde

    Args:
        data: Request verisi (arazi_buyuklugu_m2, emsal_orani)
        emsal_orani: Opsiyonel emsal override
    """
    try:
        arazi_m2 = float(data.get('arazi_buyuklugu_m2', 0) or data.get('alan_m2', 0))
        kullanilacak_emsal = float(emsal_orani or data.get('emsal_orani', 0) or VARSAYILAN_EMSAL_MARJINAL)

        if arazi_m2 <= 0:
            return {"success": False, "error": "Geçerli bir arazi büyüklüğü giriniz."}

        emsal_m2 = arazi_m2 * kullanilacak_emsal

        # ===== KAPALANAN ALAN HESABI =====
        # Emsal dahilinde: kapalı barınak + bakıcı evi + idari bina
        # Önce bakıcı evi ve idari bina payını ayıralım, kalan = kapalı barınak
        bakici_evi_pay = BAKICI_EVI_TABAN_M2   # 75 m²
        idari_bina_pay = IDARI_BINA_TABAN_M2   # 75 m²

        # Kapalı barınak için kullanılabilir emsal
        kapali_barinaktan_once = bakici_evi_pay + idari_bina_pay  # 150 m²
        kapali_barinak_m2 = max(0, emsal_m2 - kapali_barinaktan_once)

        # Gezinti alanı (emsal dışı, arazi büyüklüğüne göre)
        # Kapasite hesabı için kapalı alan ve gezinti alanı dengeli olmalı
        gezinti_alani_m2 = kapali_barinak_m2 * (GEZINTI_ALAN_HAYVAN_BASINA_M2 / KAPALI_ALAN_HAYVAN_BASINA_M2)
        # En az MIN_GEZINTI_ALANI_M2, en fazla arazidd kalan alan
        kalan_arazi = arazi_m2 - emsal_m2
        gezinti_alani_m2 = min(gezinti_alani_m2, max(0, kalan_arazi))
        gezinti_alani_m2 = max(gezinti_alani_m2, 0)

        # ===== MİNİMUM KONTROL =====
        kapali_yeterli = kapali_barinak_m2 >= MIN_KAPALI_ALAN_M2
        gezinti_yeterli = gezinti_alani_m2 >= MIN_GEZINTI_ALANI_M2

        if not kapali_yeterli or not gezinti_yeterli:
            return _basarisiz_sonuc(arazi_m2, emsal_m2, kullanilacak_emsal,
                                    kapali_barinak_m2, gezinti_alani_m2,
                                    kapali_yeterli, gezinti_yeterli)

        # ===== KAPASİTE HESABI =====
        kapasite_kapali = int(kapali_barinak_m2 / KAPALI_ALAN_HAYVAN_BASINA_M2)
        kapasite_gezinti = int(gezinti_alani_m2 / GEZINTI_ALAN_HAYVAN_BASINA_M2)
        kapasite = min(kapasite_kapali, kapasite_gezinti)

        # ===== MÜŞTEMİLAT HESABI (Talimat 11.9.3) =====
        # Emsal DIŞI — kapalı alan büyüdükçe bunlar da büyür
        kuluckahane_m2 = round(kapali_barinak_m2, 1)          # kapalı alan kadar
        civciv_buyutme_m2 = round(kapali_barinak_m2, 1)       # kapalı alan kadar
        yem_deposu_m2 = round((kapali_barinak_m2 + gezinti_alani_m2) / 2, 1)  # (kapalı + gezinti) / 2

        # ===== BAKICI EVİ & İDARİ BİNA (emsal dahili) =====
        # Kapalı alan ≥ 100 ve gezinti ≥ 350 ise hak kazanılır
        bakici_evi_hakki = True  # minimum sağlandı (yukarıda kontrol ettik)
        idari_bina_hakki = True

        # Emsal bütçesi kontrolü
        toplam_emsal_kullanimi = kapali_barinak_m2
        bakici_evi_yapilabilir = False
        idari_bina_yapilabilir = False

        if toplam_emsal_kullanimi + bakici_evi_pay <= emsal_m2:
            bakici_evi_yapilabilir = True
            toplam_emsal_kullanimi += bakici_evi_pay

        if toplam_emsal_kullanimi + idari_bina_pay <= emsal_m2:
            idari_bina_yapilabilir = True
            toplam_emsal_kullanimi += idari_bina_pay

        # ===== YAPILAR LİSTESİ =====
        yapilar = []
        yapilar.append({
            "isim": "Kapalı Barınak (Kümes)",
            "alan_m2": round(kapali_barinak_m2, 1),
            "emsal_dahil": True,
            "aciklama": f"Deve kuşu barınağı — {kapasite} hayvan kapasiteli"
        })
        yapilar.append({
            "isim": "Gezinti Alanı",
            "alan_m2": round(gezinti_alani_m2, 1),
            "emsal_dahil": False,
            "aciklama": "Açık gezinti alanı (emsal dışı)"
        })
        yapilar.append({
            "isim": "Kulüçkahane",
            "alan_m2": kuluckahane_m2,
            "emsal_dahil": False,
            "aciklama": "Kapalı alan kadar — Talimat 11.9.3 müştemilatı"
        })
        yapilar.append({
            "isim": "Civciv Büyütme Alanı",
            "alan_m2": civciv_buyutme_m2,
            "emsal_dahil": False,
            "aciklama": "Kapalı alan kadar — Talimat 11.9.3 müştemilatı"
        })
        yapilar.append({
            "isim": "Yem Deposu",
            "alan_m2": yem_deposu_m2,
            "emsal_dahil": False,
            "aciklama": "(Kapalı alan + Gezinti alanı) / 2 — Talimat 11.9.3 müştemilatı"
        })
        if bakici_evi_yapilabilir:
            yapilar.append({
                "isim": "Bakıcı Evi",
                "alan_m2": BAKICI_EVI_TABAN_M2,
                "toplam_insaat_m2": BAKICI_EVI_TOPLAM_M2,
                "emsal_dahil": True,
                "aciklama": f"Taban {BAKICI_EVI_TABAN_M2} m², toplam inşaat {BAKICI_EVI_TOPLAM_M2} m²"
            })
        if idari_bina_yapilabilir:
            yapilar.append({
                "isim": "İdari Bina",
                "alan_m2": IDARI_BINA_TABAN_M2,
                "toplam_insaat_m2": IDARI_BINA_TOPLAM_M2,
                "emsal_dahil": True,
                "aciklama": f"Taban {IDARI_BINA_TABAN_M2} m², toplam inşaat {IDARI_BINA_TOPLAM_M2} m²"
            })

        # ===== HTML MESAJ =====
        mesaj = _basarili_html_olustur(
            arazi_m2, emsal_m2, kullanilacak_emsal, kapasite,
            kapali_barinak_m2, gezinti_alani_m2,
            kuluckahane_m2, civciv_buyutme_m2, yem_deposu_m2,
            bakici_evi_yapilabilir, idari_bina_yapilabilir,
            yapilar
        )

        return {
            "success": True,
            "izin_durumu": "izin_verilebilir",
            "mesaj": mesaj,
            "arazi_buyuklugu_m2": arazi_m2,
            "emsal_m2": round(emsal_m2, 1),
            "kapasite": kapasite,
            "kapali_alan_m2": round(kapali_barinak_m2, 1),
            "gezinti_alani_m2": round(gezinti_alani_m2, 1),
            "kuluckahane_m2": kuluckahane_m2,
            "civciv_buyutme_m2": civciv_buyutme_m2,
            "yem_deposu_m2": yem_deposu_m2,
            "bakici_evi_hakki": bakici_evi_yapilabilir,
            "idari_bina_hakki": idari_bina_yapilabilir,
            "yapilar": yapilar,
            "maksimum_insaat_alani_m2": round(toplam_emsal_kullanimi, 1),
        }
    except Exception as e:
        logger.error(f"Deve kuşu hesaplama hatası: {e}")
        return {"success": False, "error": str(e)}


def _basarisiz_sonuc(arazi_m2, emsal_m2, emsal_orani,
                     kapali_m2, gezinti_m2,
                     kapali_yeterli, gezinti_yeterli):
    """Minimum şartlar karşılanmadığında dönen sonuç"""

    sorunlar = []
    if not kapali_yeterli:
        gerekli_arazi = MIN_KAPALI_ALAN_M2 / emsal_orani + (BAKICI_EVI_TABAN_M2 + IDARI_BINA_TABAN_M2) / emsal_orani
        sorunlar.append(
            f"Kapalı barınak alanı ({kapali_m2:,.0f} m²) minimum {MIN_KAPALI_ALAN_M2} m² şartını karşılamıyor. "
            f"%{emsal_orani*100:.0f} emsal ile en az {gerekli_arazi:,.0f} m² arazi gerekir."
        )
    if not gezinti_yeterli:
        sorunlar.append(
            f"Gezinti alanı ({gezinti_m2:,.0f} m²) minimum {MIN_GEZINTI_ALANI_M2} m² şartını karşılamıyor."
        )

    html = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background-color: #f8d7da; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h4 style="color: #721c24; margin-top: 0;">🦢 Deve Kuşu Üretim Tesisi Değerlendirmesi</h4>
        <p><strong>Sonuç: TESİS KURULAMAZ</strong></p>
        <div style="margin: 15px 0;">
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Arazi:</strong> {arazi_m2:,.0f} m²</li>
                <li><strong>Emsal Oranı:</strong> %{emsal_orani*100:.0f}</li>
                <li><strong>Emsal Alanı:</strong> {emsal_m2:,.0f} m²</li>
            </ul>
        </div>
        <div style="margin: 15px 0;">
            <h5 style="color: #721c24;">❌ Yetersizlikler:</h5>
            <ul style="margin: 0; padding-left: 20px;">
                {''.join(f'<li>{s}</li>' for s in sorunlar)}
            </ul>
        </div>
        <div style="background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #ffc107;">
            <p style="margin: 0; color: #856404;"><strong>💡 İpucu:</strong>
            Deve kuşu tesisi için kapalı alan en az {MIN_KAPALI_ALAN_M2} m², gezinti alanı en az {MIN_GEZINTI_ALANI_M2} m² olmalıdır (Talimat Md. 11.9.3).</p>
        </div>
    </div>
</div>""".strip()

    return {
        "success": True,
        "izin_durumu": "izin_verilemez",
        "mesaj": html,
        "arazi_buyuklugu_m2": arazi_m2,
        "emsal_m2": round(emsal_m2, 1),
        "kapasite": 0,
        "bakici_evi_hakki": False,
        "maksimum_insaat_alani_m2": 0,
    }


def _basarili_html_olustur(arazi_m2, emsal_m2, emsal_orani, kapasite,
                           kapali_m2, gezinti_m2,
                           kuluckahane_m2, civciv_m2, yem_m2,
                           bakici_evi, idari_bina, yapilar):
    """Başarılı sonuç HTML mesajı"""

    yapilar_html = ""
    emsal_dahili_toplam = 0
    emsal_disi_toplam = 0
    for y in yapilar:
        dahil = "✅ Emsal dahili" if y.get("emsal_dahil") else "📐 Emsal dışı (müştemilat)"
        yapilar_html += f"""
        <tr>
            <td style="padding: 6px 10px; border-bottom: 1px solid #e0e0e0;">{y['isim']}</td>
            <td style="padding: 6px 10px; border-bottom: 1px solid #e0e0e0; text-align: right;">{y['alan_m2']:,.0f} m²</td>
            <td style="padding: 6px 10px; border-bottom: 1px solid #e0e0e0; font-size: 0.85em; color: #666;">{dahil}</td>
        </tr>"""
        if y.get("emsal_dahil"):
            emsal_dahili_toplam += y["alan_m2"]
        else:
            emsal_disi_toplam += y["alan_m2"]

    html = f"""
<div style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="background-color: #d4edda; padding: 15px; border-radius: 8px; margin: 15px 0;">
        <h4 style="color: #155724; margin-top: 0;">🦢 Deve Kuşu Üretim Tesisi Değerlendirmesi</h4>
        <p><strong>Sonuç: TESİS KURULABİLİR</strong></p>

        <div style="margin: 15px 0;">
            <h5 style="color: #155724;">📊 Arazi ve Emsal Bilgileri:</h5>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Arazi:</strong> {arazi_m2:,.0f} m²</li>
                <li><strong>Emsal Oranı:</strong> %{emsal_orani*100:.0f}</li>
                <li><strong>Emsal Alanı:</strong> {emsal_m2:,.0f} m²</li>
                <li><strong>Tahmini Kapasite:</strong> {kapasite} adet deve kuşu</li>
            </ul>
        </div>

        <div style="margin: 15px 0;">
            <h5 style="color: #155724;">🏗️ Yapı Hakları (Arazi Büyüdükçe Artan):</h5>
            <table style="width: 100%; border-collapse: collapse; background: #fff; border-radius: 4px;">
                <thead>
                    <tr style="background: #f0f0f0;">
                        <th style="padding: 8px 10px; text-align: left;">Yapı</th>
                        <th style="padding: 8px 10px; text-align: right;">Alan</th>
                        <th style="padding: 8px 10px; text-align: left;">Durum</th>
                    </tr>
                </thead>
                <tbody>{yapilar_html}</tbody>
            </table>
            <p style="font-size: 0.85em; color: #666; margin-top: 8px;">
                Emsal dahili toplam: {emsal_dahili_toplam:,.0f} m² / {emsal_m2:,.0f} m² | 
                Emsal dışı müştemilat: {emsal_disi_toplam:,.0f} m²
            </p>
        </div>

        <div style="background-color: #cff4fc; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #0dcaf0;">
            <p style="margin: 0; font-weight: bold; color: #055160;">ℹ️ Talimat Madde 11.9.3</p>
            <p style="margin: 5px 0 0 0; color: #055160;">
                Kapalı alan büyüdükçe kulüçkahane, civciv büyütme ve yem deposu orantılı artar.
                Bakıcı evi ve idari bina, kapalı alan ≥ 100 m² ve gezinti ≥ 350 m² şartıyla hak kazanılır.
            </p>
        </div>
    </div>
</div>""".strip()

    return html
