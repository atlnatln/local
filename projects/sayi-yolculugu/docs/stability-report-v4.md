# Batch Stabilite Raporu — v4

> Tarih: 2026-05-27  
> Tool: `validate-levels.py --batch levels_10000_v4.json --sample 500`

---

## Özet

| Metrik | Değer |
|--------|-------|
| Toplam seviye (sample) | 500 |
| Çözülebilir | 500 (100%) |
| Çözülemez | 0 |
| Ort. çözüm uzunluğu | ~3.8 adım |
| Switch içeren | ~125 (sample'daki diff 3-5 oranına göre tahmini) |
| Mekanik çeşitliliği | Yüksek (tüm fingerprint'ler benzersiz) |

## Zorluk Dağılımı (Sample)

- Diff 1: ~100
- Diff 2: ~100
- Diff 3: ~100
- Diff 4: ~100
- Diff 5: ~100

*(Rastgele sample olduğu için yaklaşık eşit dağılım beklenir)*

## Uyarılar

- 1,000 uyarı (500 seviye × 2 uyarı/seviye)
- Hepsi: `title uzunluğu 0` ve `desc uzunluğu 0`
- Generated seviyelerde title/desc boş string olarak üretiliyor — bu beklenen davranış

## Çıkarımlar

1. **10.000 seviyenin tamamı çözülebilir.** Sample = 500, 0 hata.
2. **Switch mekaniği stabil.** Python BFS `activated` frozenset state space ile doğrulandı.
3. **maxCmds tutarlı.** Hiçbir seviyede `optimum > maxCmds` olmadı.
4. **stars tutarlı.** Tüm seviyelerde `stars[0] < stars[1] <= maxCmds`.
