# uygulama-gelistir-play

Google Play Console'da yeni uygulama kayıt sürecini otomatikleştiren Tampermonkey betikleri ve yardımcı araçlar.

## Amaç

Copilot yardımı ile uygulama meta verilerini tanımlayıp Google Play Console'a **hızlıca** kaydetmek; geliştirme → test sürecini kısaltmak.

## Yapı

```
uygulama-gelistir-play/
├── apps/                          # Uygulama config dosyaları (JSON)
│   └── ornek-uygulama.json
├── tampermonkey/
│   └── play-console-autofill.user.js  # Ana Tampermonkey betiği
├── config-editor/
│   └── index.html                 # Yerel config editörü (tarayıcıda aç)
└── docs/
    └── KULLANIM.md
```

## Kurulum

### 1. Tampermonkey Betiği Yükle

1. Tarayıcıda Tampermonkey eklentisi kurulu olsun.  
2. Tampermonkey Dashboard → **Create a new script** → tüm içeriği temizle.  
3. `tampermonkey/play-console-autofill.user.js` dosyasının içeriğini yapıştır → Kaydet.  
4. Alternatif: Tampermonkey → **Import from file** → dosyayı seç.

### 2. Config Editörü

```bash
# Tarayıcıda aç
xdg-open /home/akn/vps/uygulama-gelistir-play/config-editor/index.html
```

Veya VS Code'dan Live Server ile servis et.

## Kullanım Akışı

### Yöntem A: Kayan Panel (Tampermonkey)

1. [https://play.google.com/console/…/create-new-app](https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app) sayfasına git.  
2. Sağda otomatik açılan **"🚀 Play Console – Hızlı Kayıt"** panelini kullan.  
3. Alanları doldur → **⚡ Formu Doldur** veya **⚡ Doldur & Oluştur**.

### Yöntem B: URL Parametresi (CI / Copilot ile)

Config editöründen veya aşağıdaki formatla URL oluştur:

```
https://play.google.com/console/u/0/developers/9071363965517112224/create-new-app
  ?ugpAutoFill=1
  &ugpName=Mathlock%20Play
  &ugpLang=tr-TR
  &ugpType=app
  &ugpPricing=free
  &ugpPolicy=1
  &ugpExport=1
  &ugpSubmit=0   ← 1 yapınca otomatik "Oluştur" butonuna da basar
```

### Yöntem C: JSON Config Dosyası

`apps/` klasöründe her uygulama için bir JSON dosyası tut:

```json
{
  "appName": "Mathlock Play",
  "defaultLanguage": "tr-TR",
  "type": "app",
  "pricing": "free",
  "declarations": {
    "developerPoliciesAccepted": true,
    "exportLawsAccepted": true
  }
}
```

Config editörüne yükle → **URL Oluştur** → tarayıcıda aç → form otomatik dolar.

## Copilot ile Hızlı Kullanım

Yeni uygulama eklerken Copilot'a şunu söyle:

> "apps/ klasöründe `benim-uygulamam.json` oluştur: ad 'Süper Uygulama', dil tr-TR, tür app, ücretsiz"

Copilot JSON'u oluşturur, config editörüne yüklersin, URL'yi kopyalarsın, tarayıcıda form otomatik dolar.

## Notlar

- `ugpSubmit=1` parametresi formu otomatik gönderir — dikkatli kullan.  
- Tampermonkey panelindeki config'ler `GM_storage`'da saklanır (tarayıcıya özel).  
- Config editöründeki kayıtlar `localStorage`'da saklanır.  
- Dil dropdown'u `tr-TR` seçmek için Angular menüsünün açılmasını bekler; yavaş bağlantılarda `sleep` süresini betikte artır.
