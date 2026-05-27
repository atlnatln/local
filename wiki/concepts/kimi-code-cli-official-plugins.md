---
title: "Kimi Code CLI — Official Plugins"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, plugin, official, data, finance]
related:
  - kimi-code-cli
  - kimi-code-cli-plugins
---

# Kimi Code CLI — Official Plugins

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]] | [[kimi-code-cli-plugins|Plugins Detayları →]]

Kimi Code CLI tarafından resmi olarak sağlanan plugin'ler. Bu plugin'ler Kimi'nin altyapısı üzerinden çalışır ve ek konfigürasyon gerektirmez.

## kimi-datasource (Beta)

Kimi-datasource, Kimi Code CLI'nin resmi veri kaynağı plugin'idir. Finansal piyasalar, makroekonomik göstergeler, şirket kayıtları ve akademik literatür bağlantısı sağlar. A-shares, Hong Kong hisseleri, küresel piyasalar ve 50+ yıllık World Bank ekonomik verisi doğal dil ile sorgulanabilir.

**Mevcut versiyon:** `2.0.2`. Önceki kurulumunuz varsa güncellemek için kurulum komutunu yeniden çalıştırın.

### Kurulum

```bash
# Plugin'i kur
kimi plugin install https://cdn.kimi.com/kimi-code-plugins/kimi-datasource.zip

# Kurulumu doğrula
kimi plugin list
```

Plugin `~/.kimi/plugins/` dizinine kurulur.

### Kullanım

Slash command ile:
```
/skill:kimi-datasource What's the current price of Moutai?
```

Doğal dil ile:
```
Did BYD go up or down today?
```

Başarılı bir sorgu sonrası konsolda **Usage History** altında çağrıyı doğrulayabilirsiniz.

### Finansal Veri

#### Hisse ve Küresel Piyasa Fiyatları

| Özellik | Açıklama | Piyasalar |
|---------|----------|-----------|
| Gerçek zamanlı fiyatlar | Güncel fiyat, değişim %, gün içi veri | A-shares, HK, US |
| Geçmiş fiyatlar | Kapanış fiyatları ve değişim aralıkları | A-shares, HK, US, küresel |
| Teknik göstergeler | MACD, KDJ, RSI, BOLL, MA — yukarı/aşağı sinyalleri | Sadece A-shares |
| Finansal tablolar | Bilançolar, yıllık karşılaştırmalı veri | A-shares, HK, US, küresel |
| Şirket temelleri | İşletme özeti, hissedar bilgileri | A-shares, HK, US, küresel |
| Hisse tarama | Sektör, piyasa değeri, fiyat değişimi, finansal metriklere göre filtreleme | A-shares, HK, US |
| Piyasa endeksleri | CSI 300, SSE, S&P 500, Nasdaq, Nikkei vb. | A-shares, küresel |
| İzleme listesi | Pozisyon takibi, maliyet bazlı P&L hesaplama | A-shares, HK, US |

#### Makroekonomik Veri

**World Bank** Open Data API üzerinden çalışır — **189 üye ülke, 50+ yıllık** tarihsel zaman serisi. GDP, ticaret, nüfus, yoksulluk, eğitim, iklim ve onlarca diğer göstergeyi kapsar.

| Özellik | Açıklama |
|---------|----------|
| Temel makro göstergeler | GDP, CPI, ticaret hacmi, işsizlik, dış borç vb. |
| Uzun dönem veri | Ülke başına 50+ yıllık veri |
| Ülkeler arası karşılaştırma | Herhangi bir göstergeyi birden fazla ülkede karşılaştırma |
| Tematik veri setleri | Yoksulluk oranları, eğitim kayıtları, CO₂ emisyonları, enerji kaynakları, demografi |

### Akademik Veri

Fizik, matematik, bilgisayar bilimi, nicel finans, ekonomi ve daha fazlasındaki milyonlarca makaleye erişim — hem hakemli dergiler hem de preprint repository'leri.

| Özellik | Açıklama |
|---------|----------|
| Makale arama | Anahtar kelime, yazar, konu veya alan ile arama |
| Atıf arama | Herhangi bir alandaki en çok atıf alan ve etkili makaleleri bulma |
| Preprint erişimi | Resmi yayınlanmadan önceki en son araştırmalara erişim |
| Disiplinler arası | Fizik, matematik, CS, ekonomi, nicel finans, iklim bilimi vb. |

### Kullanım Örnekleri

**Geçmiş fiyat sorgusu:**
```
What was Apple's (AAPL) highest and lowest closing price in Q4 2025?
```

**Finansal tablo analizi:**
```
What are the key figures in Microsoft's 2024 annual balance sheet — total assets, liabilities, and equity?
```

**Şirket temelleri:**
```
What are NVIDIA's main business segments and who are its largest institutional shareholders?
```

**Hisse tarama:**
```
In the US semiconductor sector, find stocks with market cap above $500B and list their names and current market caps.
```

**Küresel piyasa görünümü:**
```
How are the S&P 500, Nasdaq, and Nikkei 225 performing today? Any notable sector moves?
```

**Makroekonomik karşılaştırma:**
```
Compare GDP growth rates and GDP per capita trends for China, India, and Vietnam over the past 20 years.
```

**Tematik veri araştırması:**
```
Show CO₂ emissions trends for major economies over the past decade, alongside their renewable energy share.
```

**Akademik literatür araması:**
```
Find key academic papers on financial fraud detection from the past five years, focusing on abnormal accruals and earnings manipulation models.
```

**Araştırma öncüsü:**
```
What are the most important recent papers on LLM reasoning capabilities? Summarize the main findings.
```

**Atıf analizi:**
```
What are the most influential papers on reinforcement learning from human feedback? Who are the key authors?
```

### Plugin Yönetimi

```bash
# Detayları gör
kimi plugin info kimi-datasource

# Kaldır
kimi plugin remove kimi-datasource

# Güncelle (yeniden kurarak üzerine yaz)
kimi plugin install https://cdn.kimi.com/kimi-code-plugins/kimi-datasource.zip
```

### Önemli Notlar

- Plugin sorguları **kredi bazlıdır** ve çağrı başına ücretlendirilir.
- Bu plugin **sadece okunabilir** (read-only). Ticaret, yazma veya veri gönderimi desteklenmez.
- Teknik göstergeler ve gerçek zamanlı fiyatlar sadece **aktif işlem saatlerinde** kullanılabilir. Piyasa kapalıyken kapanış verisi sorun (örn. "How did X close today?").
- AI tarafından üretilen çıktı sadece referans amaçlıdır ve **yatırım veya iş tavsiyesi teşkil etmez**.

## Kaynaklar

- Kimi Code CLI Docs — Official Plugins: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/official%20plugins.html
