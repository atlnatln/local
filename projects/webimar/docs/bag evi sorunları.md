# Bağ Evi Sorunları

## Problem Tanımı ve Kapsam

**Sorun:** Bağ evi akışında AlanKontrol modal'ında girilen ağaç verileri (tür ve adet) Hesaplama formunda/sonuçta 0 adet olarak gözüküyor. Aslında modal'da girilen değerler backend eklendiğinde veya sonuçta gösterilirken görünmeli.

**Kapsam:** Frontend → CalculationForm hazırlama → API gönderimi → Backend mesaj/sonuç üretimi → ResultDisplay. Hedef, modal'daki eklenenAgaclar verisinin doğru şekilde normalize edilip taşınması ve backend ile uyumlu biçimde gösterilmesi.

## 🔎 Çözümleme — İlgili Modüller ve Hata Sebebi

### AlanKontrol (`webimar-react/src/components/AlanKontrol.tsx`)
- `onSuccess` ile `result.eklenenAgaclar` gönderiliyor.

### CalculationForm (`webimar-react/src/components/CalculationForm.tsx`)
- `handleDikiliKontrolSuccess` ile `dikiliKontrolSonucu.set` ediliyor
- Submit sırasında `manuel_kontrol_sonucu = dikiliKontrolSonucu` gönderiliyor.

### Hazırlama (`webimar-react/src/utils/bagEviCalculator.ts` → `prepareFormDataForBackend`)
- `prepareFormDataForBackend`, `manuel_kontrol_sonucu` içeriğini olduğu gibi kopyalıyor 
- Ancak "eklenenAgaclar" içerisindeki key isimlerini backend'le uyumlu hale getirmiyor.

### Backend (`webimar-api/.../bag_evi.py`)
- `_universal_basarili_mesaj_olustur` ve diğer mesaj generator'lar eklenenAgaclar içindeki öğelerden `agac.get('secilenAgacTuru')` / `agac.get('agacTuru')` / `agac.get('agacSayisi')` bekliyor.

### Gerçek Sebep
Frontend'deki eklenenAgaclar objelerinde alan isimleri (ör. `sayi`, `turid`, `turAdi`) ile backend'in beklediği isimler (`agacSayisi`, `secilenAgacTuru` / `agacTuru`) farklı → backend "agacSayisi" bulamadığı için 0 veya boş yazıyor.

## 📐 Düzenlilik — Çözüm Adımları (Basitten Karmaşığa)

1. **Frontend:** `prepareFormDataForBackend` içinde `manuel_kontrol_sonucu.eklenenAgaclar` normalize edilecek (`sayi` → `agacSayisi`, `turid` → `secilenAgacTuru/agacTuru`, `turAdi` → `agacTuru`).

2. **Frontend:** Normalize edilmiş liste hem `finalFormData.manuel_kontrol_sonucu.eklenenAgaclar` hem de backward-uyumluluk için `finalFormData.eklenenAgaclar` olarak eklenmeli.

3. **Backend (hızlı tolerantlık iyileştirmesi):** `bag_evi.py` mesaj üretiminde eklenenAgaclar öğelerini okurken hem 'agacSayisi' hem 'sayi' gibi alternatif anahtarları kullanacak şekilde esneklik eklensin (defansif).

4. **Test:** Birim testi — `BagEviCalculator.prepareFormDataForBackend` için normalize davranışı.

5. **QA:** Manuel akış testi (alan kontrol → ekle ağaç → aktar → Hesapla → sonuç mesajında doğru ağaç adetlerini doğrula).

## ✅ Eksiksizlik — Kod + Test + Manuel Doğrulama

### Kod Değişiklikleri

1. **Frontend:** `prepareFormDataForBackend` içine normalize adımı eklenecek.
2. **Backend:** Mesaj elde eden yerlerde agac alan isimleri için fallback kontrolü eklenmeli (opsiyonel ama tavsiye edilir).

### Test
Jest testi örneği veriyorum (repo'da test altyapınız varsa ekleyin).

### Manuel Test Adımları

1. Haritada nokta seç.
2. Arazi vasfı = "Dikili vasıflı" (veya uygun tip).
3. AlanKontrol aç → ağaç türü ekle (örn. Ceviz, sayi: 10).
4. "Verileri hesaplama sayfasına aktar" (`devamEt/directTransfer`) butonuna bas.
5. Hesaplama formunda "Hesapla" butonuna bas.
6. Sonuçta veya uyarı mesajında eklenenAgaclar ve toplam ağaç sayısı doğru görünmeli.

## 💻 Kod Uygulaması

Aşağıda önerilen değişiklikleri ekliyorum.

### Frontend: Normalize İşlemini prepareFormDataForBackend İçine Ekleyin

### Backend: Daha Toleranslı Alım

Backend tarafında `bag_evi.py` içinde eklenenAgaclar döngüsünde `agacSayisi` ve tür id alma kısmını şu şekilde değiştirin:

> **Not:** Bu değişiklik backend tarafında birkaç yerde tekrar ediliyor; `_universal_basarisiz_mesaj_olustur` vb. bölümlerde de aynı şekilde uyum sağlayın.

### Test: Örnek Jest Testi

Öneri, repo test altyapısına ekleyin:

## Uygulama ve QA Talimatları

1. Deploy frontend değişikliğini; jest/CI varsa testi çalıştırın.
2. Gerekirse backend tolerant kodu deploy edin.
3. **Manuel akış testi:** AlanKontrol modal'ında 2 farklı ağaç ekleyin (farklı key/formatlarla) → aktar → Hesapla → ResultDisplay veya API response içinde eklenenAgaclar'ın doğru adet ve türle geldiğini doğrulayın.

### Eğer Hâlâ 0 Görünüyorsa:

- **Browser console:** CalculationForm.handleSubmit içinde `console.log('🍇 Hazırlanan veriler:', preparedData)` çıktısını kontrol edin — `manuel_kontrol_sonucu.eklenenAgaclar` normalize edilmiş mi?
- **Backend logs:** `calculate_bag_evi` `request.data['manuel_kontrol_sonucu']` içeriğini loglayın.

## Kapanış — Neden Bu Çözüm?

Sorun veri sözleşmesi (schema) uyuşmazlığı: frontend farklı alan isimleri gönderiyor, backend başka isim bekliyor. 

En temiz çözüm frontend'de gönderimi normalize etmek (Single Responsibility: `prepareFormDataForBackend` sorumluluğu). Ek olarak backend'e defansif okuma ekleyerek geriye dönük uyumluluk sağlanır. 

Bu yaklaşım Clean Code / SOLID ilkeleriyle uyumludur (Açıkça tek bir yerde map/dönüştürme yapılır, değişiklik lokalize edilir, testlenebilir).

---

## Kod Örnekleri

### `webimar-react/src/utils/bagEviCalculator.ts`
```typescript
// --- (dosyanın ilgili kısmı) ---
export const prepareFormDataForBackend = (formData: BagEviFormData): BagEviFormData => {
  const finalFormData = { ...formData };

  // (mevcut arazi_vasfi -> alan_m2 mapping'ları burada korunuyor)
  // ... mevcut mapping kodu aynen kalacak ...

  // === Yeni: manuel_kontrol_sonucu.eklenenAgaclar normalize et ===
  try {
    const mk = formData.manuel_kontrol_sonucu;
    if (mk && Array.isArray(mk.eklenenAgaclar)) {
      const normalized = mk.eklenenAgaclar.map((agac: any) => {
        // normalize keys: desteklenen alternatif anahtarları kontrol et
        const agacSayisi = Number(
          agac.agacSayisi ?? agac.sayi ?? agac.count ?? agac.agacSayisi ?? 0
        ) || 0;

        const secilenAgacTuru = String(
          agac.secilenAgacTuru ?? agac.agacTuru ?? agac.turid ?? agac.turId ?? agac.turAdi ?? ''
        );

        const agacTuru = String(
          agac.agacTuru ?? agac.turAdi ?? agac.tur ?? ''
        );

        return {
          // Backend'in beklediği alan isimleri
          secilenAgacTuru,
          agacTuru,
          agacSayisi,
          // preserve original useful fields (opsiyonel)
          tipi: agac.tipi ?? agac.type ?? 'normal',
          gerekliAgacSayisi: agac.gerekliAgacSayisi ?? agac.gerekli ?? undefined,
          // raw source for debugging (isteğe bağlı)
          __raw: agac
        };
      });

      // Assign normalized back into finalFormData
      finalFormData.manuel_kontrol_sonucu = {
        ...finalFormData.manuel_kontrol_sonucu,
        eklenenAgaclar: normalized
      };

      // Backward-compat: üst seviyeye de ekle (bazı eski kodlar burayı okuyabilir)
      (finalFormData as any).eklenenAgaclar = normalized;
    }
  } catch (e) {
    // Normalizasyon hatası sonucu akışı bozmayacak; loglanması yeterli
    console.error('prepareFormDataForBackend - eklenenAgaclar normalize hatası:', e);
  }

  return finalFormData;
};
```

### `webimar-api/calculations/tarimsal_yapilar/bag_evi.py`

```python
# örnek: _universal_basarili_mesaj_olustur içindeki eklenen ağaç döngüsü
for agac in eklenen_agaclar:
    # frontend farklı anahtarlarla gönderebilir; fallback'ler ekleyelim
    agac_tur_id = agac.get('secilenAgacTuru') or agac.get('agacTuru') or agac.get('turid') or agac.get('turAdi')
    agac_sayisi = agac.get('agacSayisi') if agac.get('agacSayisi') is not None else agac.get('sayi', 0)
    agac_adi = _get_agac_adi_from_id(agac_tur_id) if agac_tur_id else (agac.get('agacTuru') or agac.get('turAdi') or str(agac_tur_id))
    agac_sayisi = int(agac_sayisi) if agac_sayisi else 0
    mesaj += f"  - {agac_adi}: {agac_sayisi} adet<br>"
```

### `webimar-react/src/utils/__tests__/bagEviCalculator.prepareFormData.test.ts`

```typescript
import BagEviCalculator, { prepareFormDataForBackend } from '../bagEviCalculator';

describe('prepareFormDataForBackend - eklenenAgaclar normalize', () => {
  it('should normalize frontend eklenenAgaclar keys to backend expected names', () => {
    const raw = {
      arazi_vasfi: 'Dikili vasıflı',
      alan_m2: 6000,
      manuel_kontrol_sonucu: {
        eklenenAgaclar: [
          { turid: '18', turAdi: 'Ceviz', tipi: 'normal', sayi: 12 },
          { secilenAgacTuru: '19', agacTuru: 'Zeytin', agacSayisi: 30 }
        ]
      }
    };

    const final = prepareFormDataForBackend(raw as any);
    expect(final.manuel_kontrol_sonucu).toBeDefined();
    expect(Array.isArray(final.manuel_kontrol_sonucu!.eklenenAgaclar)).toBe(true);
    const normalized = final.manuel_kontrol_sonucu!.eklenenAgaclar!;
    expect(normalized[0].agacSayisi).toBe(12);
    expect(normalized[0].secilenAgacTuru).toBe('18');
    expect(normalized[1].agacSayisi).toBe(30);
    expect(normalized[1].secilenAgacTuru).toBe('19');
  });
});
```

webimar-api/calculations/tarimsal_yapilar/bag_evi.py
# örnek: _universal_basarili_mesaj_olustur içindeki eklenen ağaç döngüsü
for agac in eklenen_agaclar:
    # frontend farklı anahtarlarla gönderebilir; fallback'ler ekleyelim
    agac_tur_id = agac.get('secilenAgacTuru') or agac.get('agacTuru') or agac.get('turid') or agac.get('turAdi')
    agac_sayisi = agac.get('agacSayisi') if agac.get('agacSayisi') is not None else agac.get('sayi', 0)
    agac_adi = _get_agac_adi_from_id(agac_tur_id) if agac_tur_id else (agac.get('agacTuru') or agac.get('turAdi') or str(agac_tur_id))
    agac_sayisi = int(agac_sayisi) if agac_sayisi else 0
    mesaj += f"  - {agac_adi}: {agac_sayisi} adet<br>"

webimar-react/src/utils/__tests__/bagEviCalculator.prepareFormData.test.ts	
import BagEviCalculator, { prepareFormDataForBackend } from '../bagEviCalculator';

describe('prepareFormDataForBackend - eklenenAgaclar normalize', () => {
  it('should normalize frontend eklenenAgaclar keys to backend expected names', () => {
    const raw = {
      arazi_vasfi: 'Dikili vasıflı',
      alan_m2: 6000,
      manuel_kontrol_sonucu: {
        eklenenAgaclar: [
          { turid: '18', turAdi: 'Ceviz', tipi: 'normal', sayi: 12 },
          { secilenAgacTuru: '19', agacTuru: 'Zeytin', agacSayisi: 30 }
        ]
      }
    };

    const final = prepareFormDataForBackend(raw as any);
    expect(final.manuel_kontrol_sonucu).toBeDefined();
    expect(Array.isArray(final.manuel_kontrol_sonucu!.eklenenAgaclar)).toBe(true);
    const normalized = final.manuel_kontrol_sonucu!.eklenenAgaclar!;
    expect(normalized[0].agacSayisi).toBe(12);
    expect(normalized[0].secilenAgacTuru).toBe('18');
    expect(normalized[1].agacSayisi).toBe(30);
    expect(normalized[1].secilenAgacTuru).toBe('19');
  });
});