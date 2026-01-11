# KML-Çiçeklenme Verisi İlçe Eşleştirme Raporu

**Oluşturulma Tarihi:** 26 Kasım 2025

## Özet
- **Toplam çiçeklenme ilçesi:** 901
- **Eşleşen ilçe:** 871
- **Eşleşmeyen ilçe:** 30
- **Eşleşme oranı:** %96.7

## Eşleşmeyen İlçeler (30 adet)

| # | İl | İlçe (Çiçeklenme Verisi) | Normalize | Benzer GeoJSON İsimleri |
|---|-----|--------------------------|-----------|-------------------------|
| 1 | AFYON | EVCÜLER | EVCULER | - |
| 2 | BURSA | ZEMBIL OTU | ZEMBILOTU | - |
| 3 | DIYARBAKIR | CUNGUZ | CUNGUZ | ÇÜNGÜŞ |
| 4 | ELÂZIĞ | KARAKOCAĞAN | KARAKOCAGAN | KAZIMKARABEKİR, KOÇARLI, KARACABEY |
| 5 | ERZINCAN | KEKIK TÜRLERI | KEKIKTURLERI | - |
| 6 | ERZINCAN | KEVEN | KEVEN | - |
| 7 | ERZINCAN | YABANI YONCA | YABANIYONCA | BOYABAT, ABANA |
| 8 | ERZINCAN | ÇIĞDEM, HARDAL | CIGDEM,HARDAL | ARDAHAN, ARDANUÇ |
| 9 | ESKIŞEHIR | MIHALIÇIK | MIHALICIK | MİHALGAZİ, MİHALIÇÇIK, HALİLİYE |
| 10 | ISPARTA | Y.BADEMLI | Y.BADEMLI | - |
| 11 | ISPARTA | Ş.KARAAĞAÇ | S.KARAAGAC | KARACABEY, KARAMANLI, KARAMÜRSEL |
| 12 | KIRKLARELI | B.ESKI | B.ESKI | ESKİL, ESKİPAZAR |
| 13 | KIRKLARELI | L.BURGAZ | L.BURGAZ | - |
| 14 | KIRKLARELI | P. HISAR | P.HISAR | HİSARCIK |
| 15 | KIRKLARELI | P.KÖY | P.KOY | - |
| 16 | KONYA | AHRILI | AHRILI | - |
| 17 | SAKARYA | KOCAILI | KOCAILI | KOÇARLI, KARAKOÇAN, KOCAKÖY |
| 18 | TEKIRDAĞ | TEKIRDAĞ | TEKIRDAG | - |
| 19 | TUNCELI | MARGIRT | MARGIRT | - |
| 20 | TUNCELI | NAZMIYE | NAZMIYE | - |
| 21 | VAN | TUŞPA | TUSPA | - |
| 22 | YALOVA | HÜNNAP | HUNNAP | - |
| 23 | YALOVA | IHLAMUR | IHLAMUR | - |
| 24 | YALOVA | KEKIK | KEKIK | - |
| 25 | YALOVA | KESTANE | KESTANE | KESTEL |
| 26 | YALOVA | NARENCIYE | NARENCIYE | - |
| 27 | YALOVA | YONCA, FIĞ | YONCA,FIG | - |
| 28 | ÇORUM | BOĞAZLAKE | BOGAZLAKE | BOĞAZKALE, BOĞAZLIYAN |
| 29 | ÇORUM | MERKEZ-İLÇE | -ILCE | - |
| 30 | ŞANLIURFA | BIROCIK | BIROCIK | - |


## Notlar

### Eşleşme Mantığı
1. Türkçe karakterler ASCII'ye dönüştürülür (İ→I, Ş→S, Ğ→G, Ü→U, Ö→O, Ç→C)
2. Boşluklar ve parantezler kaldırılır
3. Sondaki "MERKEZ" kelimesi kaldırılır
4. Tam eşleşme veya içerme kontrolü yapılır

### Tipik Sorunlar
- **Bitki isimleri ilçe olarak girilmiş:** KESTANE, KEKIK, NARENCIYE, YONCA vb.
- **Birleşik ilçe isimleri:** "BAYRAMIÇ,ÇAN YENICE", "EŞME/ ULUBEY" vb.
- **Kısaltmalar:** "L.BURGAZ", "P. HISAR", "B.ESKI" vb.
- **Farklı yazımlar:** AKÇAKOÇA vs AKÇAKOCA, BIGADIÇ vs BİGADİÇ vb.

### Çözüm Önerileri
1. Bitki isimlerini ilçe listesinden çıkar (veri temizliği)
2. Manuel eşleştirme tablosu oluştur
3. GeoJSON'da eksik ilçeleri ekle
