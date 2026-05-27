---
title: "Kimi Code CLI — MCP"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, mcp, extension, integration]
related:
  - kimi-code-cli
  - kimi-code-cli-plugins
---

# Kimi Code CLI — MCP (Model Context Protocol)

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

[Model Context Protocol (MCP)](https://modelcontextprotocol.io/) AI modellerinin harici araç ve veri kaynaklarıyla güvenli etkileşim kurmasını sağlayan açık bir protokoldür.

## MCP Nedir

MCP sunucuları AI için "tool" sağlar. Örneğin:
- Bir veritabanı MCP sunucusu SQL sorgusu çalıştırma tool'u sunar
- Bir browser MCP sunucusu otomasyon görevleri için browser kontrolü sağlar
- Üçüncü parti servisler (GitHub, Linear, Notion) ile entegrasyon

Kimi Code CLI'nin built-in tool'larının (dosya okuma/yazma, shell komutları, web fetch) üzerine MCP ile daha fazla yetenek eklenebilir.

## MCP Sunucu Yönetimi

`kimi mcp` komutu ile MCP sunucularını yönetin.

### Sunucu Ekleme

**HTTP sunucu:**
```bash
# Temel kullanım
kimi mcp add --transport http context7 https://mcp.context7.com/mcp

# Header ile
kimi mcp add --transport http context7 https://mcp.context7.com/mcp \
  --header "CONTEXT7_API_KEY: your-key"

# OAuth ile
kimi mcp add --transport http --auth oauth linear https://mcp.linear.app/mcp
```

**stdio sunucu (yerel process):**
```bash
kimi mcp add --transport stdio chrome-devtools -- npx chrome-devtools-mcp@latest
```

### Sunucu Listeleme

```bash
kimi mcp list
```

Kimi Code CLI çalışırken `/mcp` komutu ile bağlı sunucuları ve yüklenen tool'ları görüntüleyebilirsiniz.

### Sunucu Kaldırma

```bash
kimi mcp remove context7
```

### OAuth Yetkilendirme

OAuth kullanan sunucular için önce yetkilendirme tamamlanmalıdır:

```bash
kimi mcp auth linear
```

Bu komut tarayıcıyı açarak OAuth flow'u tamamlar. Başarılı yetkilendirme sonrası token gelecekteki kullanımlar için kaydedilir.

MCP OAuth token'ları `~/.kimi/mcp-oauth/` dizininde saklanır. Eski versiyondan (FastMCP 2.x) yükseltme yaptıysanız token cache otomatik taşınmaz; `kimi mcp auth <name>` ile yeniden yetkilendirme yapmanız gerekir.

### Sunucu Testi

```bash
kimi mcp test context7
```

## MCP Konfigürasyon Dosyası

MCP sunucu konfigürasyonu `~/.kimi/mcp.json` dosyasında saklanır. Diğer MCP client'larla uyumlu formattadır:

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "your-key"
      }
    },
    "chrome-devtools": {
      "command": "npx",
      "args": ["chrome-devtools-mcp@latest"],
      "env": {
        "SOME_VAR": "value"
      }
    }
  }
}
```

### Geçici Konfigürasyon Yükleme

```bash
# Farklı bir konfigürasyon dosyasından yükle
kimi --mcp-config-file /path/to/mcp.json

# Doğrudan JSON geç
kimi --mcp-config '{"mcpServers": {"test": {"url": "https://..."}}}'
```

## Yükleme Durumu

MCP sunucuları shell UI başladıktan sonra asenkron olarak initialize edilir, bu sayede arayüz hemen kullanılabilir hale gelir. Shell status bar'ında canlı bağlantı ilerlemesi gösterilir, tüm sunucular bağlandığında otomatik olarak hazır durumuna geçer. Web arayüzü de her sunucunun bağlantı durumunu gerçek zamanlı olarak yansıtır.

Birden fazla MCP sunucusu konfigüre edilmişse yükleme biraz zaman alabilir. Status bar'daki ilerleme göstergesi bağlantı kurulurken bilgi verir.

## Güvenlik

MCP tool'ları harici sistemlere erişebilir ve işlem yapabilir. Güvenlik risklerine dikkat edin.

### Onay Mekanizması

Kimi Code CLI hassas operasyonlar (dosya değişikliği, komut çalıştırma) için kullanıcı onayı ister. MCP tool çağrıları da aynı onay mekanizmasına tabidir; tüm MCP tool çağrıları onay isteği gönderir.

### Prompt Injection Riskleri

MCP tool'larının döndürdüğü içerikte kötü niyetli talimatlar olabilir. Kimi Code CLI tool dönüş içeriğini işaretleyerek AI'ın tool çıktısı ile kullanıcı talimatlarını ayırt etmesine yardımcı olur, ancak yine de:

- Sadece güvenilir kaynaklardan MCP sunucusu kullanın
- AI'nın önerdiği operasyonların makul olup olmadığını kontrol edin
- Yüksek riskli operasyonlar için manuel onay alın

::: warning Not
YOLO veya AFK modunda MCP tool çağrıları da otomatik onaylanır. Bu modları sadece MCP sunucularına tamamen güvendiğinizde kullanın.
:::

## MCP vs Plugin

| Özellik | MCP | Plugin |
|---------|-----|--------|
| Süreç | Sürekli çalışan servis | Çağrıldığında çalışan script |
| İletişim | Cross-process (HTTP/stdio) | Subprocess (stdin/stdout) |
| Kullanım | Karmaşık tool orkestrasyonu, browser/database kontrolü | Basit script wrapper, proje özel araç |
| Konfigürasyon | `~/.kimi/mcp.json` | `~/.kimi/plugins/` |

## Kaynaklar

- Kimi Code CLI Docs — MCP: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/mcp.html
- Model Context Protocol: https://modelcontextprotocol.io/
