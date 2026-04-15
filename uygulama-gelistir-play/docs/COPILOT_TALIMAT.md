# Play Console – Copilot Orkestrasyon Talimatları

## Mimari

```
Copilot (orkestra şefi)
  │
  ├─ 1. play-console.json oku
  ├─ 2. URL parametrelerini oluştur
  ├─ 3. Playwright ile URL'ye navigate et
  │
  └─▶ Tampermonkey Betiği (form doldurucu)
        │  ugpAutoFill=1 parametresini algılar
        │  Formu Material Design seçicilerle doldurur
        │  ugpSubmit=1 ise otomatik gönderir
        └─▶ Yeni uygulama oluşturulur

Copilot (son adım)
  └─ Yeni App ID'yi play-console.json'a yazar
```

**Copilot form'a asla dokunmaz.** Sadece doğru parametrelerle URL oluşturur ve navigate eder.
Form doldurma ve gönderme tamamen Tampermonkey betiğinin sorumluluğundadır.

---

## Tetikleme Komutu

Kullanıcı şunu söylediğinde bu talimatları uygula:

- `"[proje-adı] uygulamasını play console'da oluştur"`
- `"[proje-adı] için play console kaydı oluştur"`
- `"uygulama-gelistir-play ile [proje-adı] oluştur"`

---

## Copilot'un Adımları

### Adım 1 — Config Oku

```
/home/akn/vps/projects/<proje-adı>/play-console.json
```

Gerekli alanlar:

| Alan | Örnek |
|---|---|
| `appName` | `"MathLock Play"` |
| `defaultLanguage` | `"tr-TR"` |
| `type` | `"app"` veya `"game"` |
| `pricing` | `"free"` veya `"paid"` |
| `declarations.developerPoliciesAccepted` | `true` |
| `declarations.exportLawsAccepted` | `true` |

Config yoksa kullanıcıdan bu alanları iste, sonra dosyayı oluştur.

### Adım 2 — Tetikleme URL'sini Oluştur

```
https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app
  ?ugpAutoFill=1
  &ugpName=<appName — URL encode>
  &ugpLang=<defaultLanguage>
  &ugpType=<type>
  &ugpPricing=<pricing>
  &ugpPolicy=<developerPoliciesAccepted ? 1 : 0>
  &ugpExport=<exportLawsAccepted ? 1 : 0>
  &ugpSubmit=1
```

Örnek (MathLock Play, Türkçe, ücretsiz uygulama):
```
https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app?ugpAutoFill=1&ugpName=MathLock%20Play&ugpLang=tr-TR&ugpType=app&ugpPricing=free&ugpPolicy=1&ugpExport=1&ugpSubmit=1
```

### Adım 3 — Playwright ile Navigate Et

Playwright-MCP'nin `navigate` aracını kullan:
```
URL: <Adım 2'de oluşturulan URL>
```

Bundan sonra **hiçbir şey yapma.** Tampermonkey betiği devralır.

### Adım 4 — Sonucu Bekle ve Doğrula

~5-8 saniye bekle. Sayfa URL'si değişmeli:

**Beklenen**: `https://play.google.com/console/.../app/<YENİ_APP_ID>/app-dashboard`

Sayfa başlığı: `Kontrol paneli | <appName>`

Eğer hâlâ `create-new-app` URL'sindeyse Tampermonkey betiğinin yüklenip yüklenmediğini kontrol et.

### Adım 5 — App ID'yi Kaydet

Yeni URL'den `app/<APP_ID>/` kısmını parse et.
`play-console.json` dosyasına ekle:

```json
{
  "meta": {
    "appId": "<APP_ID>",
    "playConsoleUrl": "https://play.google.com/console/u/0/developers/9071363965517112224/app/<APP_ID>/app-dashboard",
    "createdAt": "<tarih>"
  }
}
```

---

## Tampermonkey Kurulumu (Ön Koşul)

Betik **bir kez** yüklenmeli, sonra her zaman aktif kalır:

1. Tampermonkey Dashboard → **Yeni betik oluştur**
2. `/home/akn/vps/uygulama-gelistir-play/tampermonkey/play-console-autofill.user.js` içeriğini yapıştır → Kaydet
3. `@match https://play.google.com/console/u/*/create-new-app*` sayfalarda otomatik devreye girer

---

## Tamamlanan Uygulamalar

| Proje | App ID | Oluşturulma |
|---|---|---|
| mathlock-play | 4973430330190022574 | 2026-03-28 |

