# Frontend-Backend İzin Durumu Mapping Sorunu Çözüm Roadmap

## Amaç
Backend'den gelen response'da `"izin_durumu"` field'ının sadece root seviyede bulunduğu ve alt path'lerde duplicate/yanlış değerler olmadığından emin olundu. Ancak frontend'de (özellikle `CalculationForm.tsx` ve `ResultDisplay.tsx`), eski fallback mantığı nedeniyle mapping hatası oluşuyor. Bu roadmap, VS Code üzerinde Copilot ile birlikte optimize frontend mapping ve gösterim için adım adım yol haritasıdır.

---

## 1. **Dosya ve Kod Noktalarının Tespiti**

### İlgili Dosyalar:
- `webimar-react/src/components/CalculationForm.tsx`
- `webimar-react/src/components/ResultDisplay.tsx`
- (Opsiyonel) `webimar-react/src/services/api.ts` (API servis mantığı)
- (Opsiyonel) `webimar-react/src/types.ts` (Response type tanımları)

---

## 2. **Sorunun Kökü**

- Response'da `"izin_durumu"` sadece root'ta var; alt path'lerde yok.
- Frontend mapping (özellikle CalculationForm.tsx'de) fallback ile alt path'lerden arama yapıyor, eski/yanlış değeri özet kartına yansıtıyor.
- Doğru mapping için sadece root path üzerinden `"izin_durumu"` kullanılmalı.

---

## 3. **Çözüm Adımları**

### 3.1 CalculationForm.tsx'de Mapping Mantığını Sadeleştir

**Bul:**
```typescript
izin_durumu: (apiResult as any).data?.detaylar?.izin_durumu 
           || (apiResult as any).detaylar?.izin_durumu 
           || (apiResult as any).data?.izin_durumu 
           || (apiResult as any).results?.izin_durumu 
           || (apiResult as any).izin_durumu 
           || 'izin_verilemez'
```

**Değiştir:**
```typescript
izin_durumu: (apiResult as any).izin_durumu || 'izin_verilemez'
```

> Artık sadece root seviyedeki alanı kullan. Alt path fallback mantığı kaldırılmalı.

---

### 3.2 ResultDisplay.tsx'de Gösterim Mantığını Sadeleştir

**Bul:**
```typescript
const izinDurumu = data.detaylar?.izin_durumu || data.izin_durumu;
```
**Değiştir:**
```typescript
const izinDurumu = data.izin_durumu;
```
> Alt path aramasını bırak, sadece root kullan.

---

### 3.3 Test ve Validasyon

- Farklı büyüklükte alanlar ile (ör. 3000, 5000, 30000 m²) test et.
- Ekranda "izin_durumu" doğru şekilde gösteriliyor mu?
- Tablo ve HTML çıktı backend'den doğru geliyorsa, frontend'de tutarlı şekilde render ediliyor mu?

---

## 4. **Ek İyileştirmeler**

- Mapping mantığının sadeleştirildiği noktaları yorum satırı ile açıkla.  
  Örn: `// izin_durumu artık sadece root seviyede backend'den geliyor, fallback kaldırıldı`
- Eğer ileride backend tekrar alt path'lerde izin_durumu gönderirse, bu mantık kolayca tekrar genişletilebilir şekilde tutulmalı (örn. helper fonksiyon ile).

---

## 5. **Dokümantasyon ve Commit Mesajı Önerisi**

- `docs/CHANGES.md` veya uygun bir değişiklik dokümanında şu notu ekle:
  - _"Frontend mapping mantığı sadeleştirildi. Artık izin_durumu sadece root seviyeden alınmaktadır. Alt path fallback kaldırıldı."_

- Commit mesajı örneği:
  ```
  fix: izin_durumu frontend mapping fallback kaldırıldı, sadece root kullanılıyor (#frontend-backend-mapping)
  ```

---

## 6. **Kod Review Checklist**

- [ ] Mapping mantığı sadece root path üzerinden mi?
- [ ] Alt path fallback tamamen kaldırıldı mı?
- [ ] Testlerde izin_durumu ve özet kartı tutarlı mı?
- [ ] Backend ile tam uyumlu mu?
- [ ] Kullanıcıya yanlış bilgi (eski/yanlış izin durumu) gösterilmiyor mu?

---

## 7. **Gelecekteki Genişletme ve Bakım**

- Backend'de izin_durumu field'ı alt path'lerde tekrar eklenirse, frontend'de helper fonksiyon ile kontrol edilebilir.
- Mapping mantığı sade ve tek noktadan yönetilmeli (örn. `getIzinDurumuFromResponse(response)` fonksiyonu).

---

## 8. **Özet**

Bu roadmap ile, VS Code üzerinde Copilot desteğiyle, ilgili dosyalarda mapping düzeltmesi yaparak frontend-backend veri tutarlılığını sağlayabilir ve kullanıcıya hatasız veri sunabilirsin.

---


### **Dosya Bazlı Değişiklik Özet**

| Dosya                                        | Ana Değişiklik                     |
|----------------------------------------------|------------------------------------|
| `src/components/CalculationForm.tsx`         | Mapping sadeleştirilecek           |
| `src/components/ResultDisplay.tsx`           | Gösterim root izin_durumu ile      |
| `src/services/api.ts` (opsiyonel)            | Response type kontrolü             |

---

**Bu adımlar, VS Code Copilot ile birlikte hızlıca uygulanabilir ve kodun hatasız şekilde çalışmasını sağlar.**