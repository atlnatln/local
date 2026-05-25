# MCP Entegrasyon Rehberi

Bu proje, kimi-cli ile kullanılabilecek MCP (Model Context Protocol) sunucuları
için öneriler içerir.

## Önerilen MCP Sunucuları

### Context7

[Context7](https://context7.com/), aidlc-rules dokümanlarını ve proje
kaynaklarını yapılandırılmış şekilde sorgulamak için kullanılır.

Kurulum:

```bash
kimi mcp add --transport http context7 https://mcp.context7.com/mcp
```

API anahtarı gerekirse:

```bash
export CONTEXT7_API_KEY="ctx7sk-xxx"
```

veya `~/.kimi/mcp.json` üzerinden headers inject edilebilir.

Kullanım senaryoları:

- aidlc-rules/ içindeki belirli bir kuralın detaylarını sorgulama
- Proje yapısını ve workflow kurallarını hızlıca özetleme
- Yeni katkıda bulunanlar için rehber bilgisi alma

### GitHub MCP

PR, issue ve repo yönetimi için GitHub MCP sunucusu.

Kurulum:

```bash
kimi mcp add --transport http --auth oauth github https://mcp.github.com/mcp
kimi mcp auth github
```

Kullanım senaryoları:

- PR oluşturma ve reviewer atama
- Issue listeleme ve etiketleme
- CI durumunu kontrol etme

## MCP Config Şablonu

Opsiyonel: `~/.kimi/mcp.json` şablonu (doğrudan bu projeye commitlenmez):

```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp",
      "transport": "http",
      "headers": {
        "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"
      }
    },
    "github": {
      "url": "https://mcp.github.com/mcp",
      "transport": "http",
      "auth": {
        "type": "oauth"
      }
    }
  }
}
```

## Yararlı Komutlar

| Komut                        | Açıklama                                   |
| ---------------------------- | ------------------------------------------ |
| `kimi mcp list`              | Kayıtlı MCP sunucularını listele           |
| `kimi mcp info <name>`       | Belirli MCP sunucusu detaylarını göster    |
| `kimi mcp remove <name>`     | MCP sunucusunu kaldır                      |
| `kimi mcp reset-auth <name>` | OAuth token'ını sıfırla                    |

## Güvenlik Notları

- MCP sunucuları harici hizmetlere bağlanır; hassas bilgileri (credentials,
  internal API keys) MCP context'ine dahil etme.
- `.kimi/mcp.json` dosyasını asla Git'e commitleme; zaten `.gitignore`
  tarafından dışlanmıştır.
- OAuth kimlik doğrulaması kullanarak API key yönetimini basitleştir.
