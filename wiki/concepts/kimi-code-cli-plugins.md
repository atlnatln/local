---
title: "Kimi Code CLI — Plugins (Beta)"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, plugin, beta, extension]
related:
  - kimi-code-cli
  - kimi-code-cli-skills
---

# Kimi Code CLI — Plugins (Beta)

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

::: warning Beta Özellik
Plugin sistemi şu an Beta aşamasındadır. Gelecek sürümlerde yapı ve konfigürasyon tanımları değişebilir. Production ortamlarında dikkatli kullanın.
:::

Plugin sistemi, AI'a özel çalıştırılabilir araçlar eklemenizi sağlar. Skill'lerden farklı olarak AI doğrudan tool çağrısı yaparak sonuç alır.

**Skill vs Plugin:**

| | Skill | Plugin |
|---|---|--------|
| Amaç | Bilgi tabanlı rehber | Çalıştırılabilir araç |
| Format | `SKILL.md` | `plugin.json` + script'ler |
| Etkileşim | AI okur ve uygular | AI doğrudan çağırır |

## Plugin Yönetimi

```bash
# Yerel dizinden kur
kimi plugin install /path/to/my-plugin

# ZIP dosyasından kur
kimi plugin install my-plugin.zip
kimi plugin install https://example.com/my-plugin.zip

# Git reposundan kur
kimi plugin install https://github.com/user/repo.git
kimi plugin install https://github.com/user/repo.git/plugins/my-plugin
kimi plugin install https://github.com/user/repo/tree/develop/plugins/my-plugin

# Listele
kimi plugin list

# Detay gör
kimi plugin info my-plugin

# Kaldır
kimi plugin remove my-plugin
```

Git reposunda kök dizinde `plugin.json` yoksa Kimi Code CLI kök ve bir alt düzey dizinleri tarar, mevcut plugin'leri listeler ve seçim yapmanızı sağlar.

## Plugin Oluşturma

3 adımda plugin oluşturulur:

1. Dizin oluştur
2. `plugin.json` yaz
3. Tool script'lerini implemente et

### Dizin Yapısı

```
my-plugin/
├── plugin.json       # Plugin konfigürasyonu (zorunlu)
├── config.json       # Plugin config (opsiyonel, credential injection için)
└── scripts/          # Tool script'leri
    ├── greet.py
    └── calc.ts
```

### `plugin.json` Formatı

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "description": "My custom plugin for project X",
  "config_file": "config.json",
  "inject": {
    "api_key": "api_key",
    "endpoint": "base_url"
  },
  "tools": [
    {
      "name": "greet",
      "description": "Generate a greeting message",
      "command": ["python3", "scripts/greet.py"],
      "parameters": {
        "type": "object",
        "properties": {
          "name": {
            "type": "string",
            "description": "Name to greet"
          }
        },
        "required": ["name"]
      }
    }
  ]
}
```

**Alanlar:**

| Alan | Açıklama | Zorunlu |
|------|----------|---------|
| `name` | Plugin adı; küçük harf, rakam, tire | Evet |
| `version` | Semantik versiyon | Evet |
| `description` | Açıklama | Hayır |
| `config_file` | Credential injection için config dosyası | Hayır |
| `inject` | Credential injection mapping | Hayır |
| `tools` | Tool listesi | Hayır |

**Tool alanları:**

| Alan | Açıklama | Zorunlu |
|------|----------|---------|
| `name` | Tool adı | Evet |
| `description` | Tool açıklaması | Evet |
| `command` | Çalıştırılacak komut (string array) | Evet |
| `parameters` | JSON Schema formatında parametre tanımı | Hayır |

## Credential Injection

Plugin LLM API'lerini çağırıyorsa `inject` konfigürasyonu ile Kimi Code CLI'nin credential'larını otomatik alabilir.

```json
{
  "config_file": "config.json",
  "inject": {
    "llm.api_key": "api_key",
    "llm.endpoint": "base_url"
  }
}
```

**Desteklenen injection değişkenleri:**

| Değişken | Açıklama |
|----------|----------|
| `api_key` | LLM provider API key (OAuth token veya static key) |
| `base_url` | LLM API base URL |

Kurulum sırasında Kimi Code CLI mevcut API key ve base URL'yi belirtilen config dosyasına yazar. OAuth kullanılıyorsa geçerli token otomatik elde edilir ve enjekte edilir. Sonrasında Kimi Code CLI restart edildiğinde credential'lar otomatik yenilenir. Plugin'i yeniden kurmaya genellikle gerek yoktur; sadece plugin'in kendi yapısı (`config_file` veya `inject` mapping) değişirse yeniden kurulmalıdır.

::: tip
`inject` key'leri (örn. `llm.api_key`) aynı zamanda plugin tool subprocess'lerine environment variable olarak aktarılır. Nokta içerdikleri için POSIX shell'de `$llm.api_key` geçersizdir; dictionary erişimi kullanın:

- **Node.js**: `process.env["llm.api_key"]`
- **Python**: `os.environ["llm.api_key"]`

Shell-friendly isimler isterseniz `LLM_API_KEY`, `LLM_ENDPOINT` gibi key'ler kullanın.
:::

## Tool Script Spesifikasyonu

Tool script'leri parametreleri stdin'den JSON olarak alır, sonucu stdout'a yazar.

**Giriş formatı:**
```json
{"name": "World"}
```

**Çıkış formatı:**
Script stdout'a yazdığı içerik Agent'a string olarak döner. Yapılandırılmış çıktı için JSON önerilir:
```json
{"content": "Hello, World!"}
```

**Python örneği:**
```python
#!/usr/bin/env python3
import json
import sys

params = json.load(sys.stdin)
name = params.get("name", "Guest")

result = {"content": f"Hello, {name}!"}
print(json.dumps(result))
```

**TypeScript örneği:**
```typescript
#!/usr/bin/env tsx
import * as readline from "readline";

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false,
});

let input = "";
rl.on("line", (line) => { input += line; });
rl.on("close", () => {
  const params = JSON.parse(input);
  const name = params.name || "Guest";
  console.log(JSON.stringify({ content: `Hello, ${name}!` }));
});
```

## Tam Örnek

```json
{
  "name": "sample-plugin",
  "version": "1.0.0",
  "description": "Sample plugin demonstrating Skills + Tools",
  "tools": [
    {
      "name": "py_greet",
      "description": "Generate a greeting message (Python tool)",
      "command": ["python3", "scripts/greet.py"],
      "parameters": {
        "type": "object",
        "properties": {
          "name": { "type": "string", "description": "Name to greet" },
          "lang": { "type": "string", "enum": ["en", "zh", "ja"], "description": "Language" }
        },
        "required": ["name"]
      }
    },
    {
      "name": "ts_calc",
      "description": "Evaluate a math expression (TypeScript tool)",
      "command": ["npx", "tsx", "scripts/calc.ts"],
      "parameters": {
        "type": "object",
        "properties": {
          "expression": { "type": "string", "description": "Math expression to evaluate" }
        },
        "required": ["expression"]
      }
    }
  ]
}
```

## Plugin ile Skill Birleştirme (Bundling)

Bir plugin opsiyonel olarak `plugin.json` yanında tek bir `SKILL.md` dosyası içerebilir. Bu dosya varsa Kimi Code CLI startup'ta otomatik keşfeder — ek kayıt gerekmez. Çünkü `~/.kimi/plugins/` dizini aynı zamanda bir skills root olarak kabul edilir.

```
my-plugin/
├── plugin.json
├── SKILL.md          # Opsiyonel: birleştirilmiş skill
└── scripts/
```

Skill adı `SKILL.md` frontmatter'ındaki `name` alanından alınır; ayarlanmamışsa plugin dizin adı kullanılır. Skill `extra` scope'unda keşfedilir, bu yüzden aynı isimde proje-seviyesi veya kullanıcı-seviyesi skill'ler önceliklidir.

**Sınırlama:** Her plugin için sadece bir `SKILL.md` keşfedilir. `<plugin>/skills/<name>/SKILL.md` gibi nested yapılar taranmaz.

## Plugin Kurulum Konumu

Plugin'ler `~/.kimi/plugins/` dizinine kurulur. Her plugin bağımsız bir alt dizindir ve `plugin.json` ile script dosyalarını içerir.

::: info Official Plugins
Kimi Code CLI tarafından resmi olarak sağlanan plugin'ler de vardır. Mevcutta **kimi-datasource** (Beta) bulunur — finansal piyasalar, makroekonomik göstergeler ve akademik literatür verilerine doğal dil ile erişim sağlar. Detaylar: [[kimi-code-cli-official-plugins|Official Plugins →]]
:::

::: info Not
Plugin'ler ve MCP sunucuları birbirini tamamlayan extension mekanizmalarıdır:

- **MCP**: Sürekli çalışması gereken servisler, karmaşık tool orkestrasyonu, cross-process iletişim için uygundur
- **Plugin**: Basit script wrapper'ları, proje özel araçlar, hızlı prototipleme için uygundur
:::

## Kaynaklar

- Kimi Code CLI Docs — Plugins: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/plugins.html
