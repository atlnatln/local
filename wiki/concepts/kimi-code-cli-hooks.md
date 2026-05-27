---
title: "Kimi Code CLI — Hooks (Beta)"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, hook, beta, automation, security]
related:
  - kimi-code-cli
  - kimi-code-cli-plugins
---

# Kimi Code CLI — Hooks (Beta)

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

::: warning Beta Özellik
Hooks sistemi şu an Beta aşamasındadır. Gelecek sürümlerde implementasyon detayları ve konfigürasyon tanımları değişebilir. Production ortamlarında dikkatli kullanın.
:::

Hooks sistemi, Agent yaşam döngüsündeki kritik noktalarda özel komutlar çalıştırmanızı sağlar. Otomasyon, güvenlik kontrolü, bildirim ve daha fazlası için kullanılır.

## Hook Nedir

Belirli event'ler gerçekleştiğinde tetiklenen bir mekanizmadır. Bir shell komutu konfigüre edilir; event tetiklendiğinde komuta context bilgisi stdin üzerinden JSON olarak aktarılır. Komutun exit kodu sonraki davranışı belirler.

Kullanım senaryoları:
- **Kod formatlama**: Dosya düzenlemesi sonrası otomatik `prettier` veya `black` çalıştırma
- **Güvenlik kontrolü**: Tehlikeli shell komutlarını (örn. `rm -rf /`) engelleme
- **Hassas dosya koruma**: `.env` gibi dosyaların değiştirilmesini önleme
- **Masaüstü bildirimleri**: İnsan onayı gerektiğinde uyarı gönderme
- **Görev doğrulama**: Session bitmeden tamamlanmamış görev kontrolü

## Desteklenen Hook Event'leri

Kimi Code CLI 13 lifecycle event'i destekler:

| Event | Tetikleyici | Matcher Filter | Mevcut Context |
|-------|-------------|----------------|----------------|
| `PreToolUse` | Tool çağrısı öncesi | Tool adı | `tool_name`, `tool_input`, `tool_call_id` |
| `PostToolUse` | Başarılı tool sonrası | Tool adı | `tool_name`, `tool_input`, `tool_output` |
| `PostToolUseFailure` | Başarısız tool sonrası | Tool adı | `tool_name`, `tool_input`, `error` |
| `UserPromptSubmit` | Kullanıcı input'u işlenmeden önce | Yok | `prompt` |
| `Stop` | Agent turn sonunda | Yok | `stop_hook_active` |
| `StopFailure` | Hata ile turn sonunda | Error tipi | `error_type`, `error_message` |
| `SessionStart` | Session oluşturulduğunda/devam ettirildiğinde | Source (`startup`/`resume`) | `source` |
| `SessionEnd` | Session kapandığında | Reason | `reason` |
| `SubagentStart` | Subagent başladığında | Agent adı | `agent_name`, `prompt` |
| `SubagentStop` | Subagent bittiğinde | Agent adı | `agent_name`, `response` |
| `PreCompact` | Context compaction öncesi | Tetikleyici nedeni | `trigger`, `token_count` |
| `PostCompact` | Context compaction sonrası | Tetikleyici nedeni | `trigger`, `estimated_token_count` |
| `Notification` | Bildirim iletildiğinde | Sink adı | `sink`, `notification_type`, `title`, `body`, `severity` |

## Hook Konfigürasyonu

`~/.kimi/config.toml` dosyasında `` `[[ hooks ]]` `` array syntax ile tanımlanır:

```toml
# Dosya düzenlemesi sonrası otomatik formatlama
[[ hooks ]]
event = "PostToolUse"
matcher = "WriteFile|StrReplaceFile"
command = "jq -r '.tool_input.file_path' | xargs prettier --write"

# .env dosyalarına düzenlemeyi engelle
[[ hooks ]]
event = "PreToolUse"
matcher = "WriteFile|StrReplaceFile"
command = ".kimi/hooks/protect-env.sh"
timeout = 10

# Onay gerektiğinde masaüstü bildirimi
[[ hooks ]]
event = "Notification"
matcher = "permission_prompt"
command = "osascript -e 'display notification \"Kimi needs attention\" with title \"Kimi CLI\"'"

# Session bitmeden görev kontrolü
[[ hooks ]]
event = "Stop"
command = ".kimi/hooks/check-complete.sh"
```

### Konfigürasyon Alanları

| Alan | Zorunlu | Varsayılan | Açıklama |
|------|---------|------------|----------|
| `event` | Evet | — | Event tipi, 13 desteklenen event'ten biri |
| `command` | Evet | — | Çalıştırılacak shell komutu, stdin üzerinden JSON alır |
| `matcher` | Hayır | `""` | Regex filtresi, boş string tümüyle eşleşir |
| `timeout` | Hayır | `30` | Saniye cinsinden timeout, timeout'ta fail-open |

## İletişim Protokolü

### Giriş (Standard Input)

Hook komutları stdin üzerinden JSON context alır:

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "hook_event_name": "PreToolUse",
  "tool_name": "Shell",
  "tool_input": {"command": "rm -rf /"}
}
```

### Çıkış (Exit Code)

| Exit Kod | Davranış | Geri Bildirim |
|----------|----------|---------------|
| `0` | İzin ver | stdout (boş değilse) context'e eklenir |
| `2` | Engelle | stderr içeriği LLM'e düzeltme olarak iletilir |
| Diğer | İzin ver | stderr sadece loglanır, LLM'e gösterilmez |

### Yapılandırılmış JSON Çıkış

Exit code 0 ile yapılandırılmış JSON çıktı verilebilir:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Please use rg instead of grep"
  }
}
```

`permissionDecision: deny` olduğunda operasyon engellenir ve `permissionDecisionReason` LLM'e geri bildirim olarak iletilir.

## Hook Script Örnekleri

### Hassas Dosyaları Koruma

```bash
#!/bin/bash
# .kimi/hooks/protect-env.sh

read JSON
echo "$JSON" | jq -r '.tool_input.file_path' | grep -qE '\.env$|\.env\.local$'

if [ $? -eq 0 ]; then
    echo "Error: Direct modification of .env files is not allowed. Use .env.example instead." >&2
    exit 2
fi

exit 0
```

### Otomatik Kod Formatlama

```bash
#!/bin/bash
# .kimi/hooks/auto-format.sh

FILE=$(python3 -c "import sys,json; print(json.load(sys.stdin).get('tool_input',{}).get('file_path',''))")

if [ "$FILE" = *.js ] || [ "$FILE" = *.ts ]; then
    prettier --write "$FILE" 2>/dev/null
elif [ "$FILE" = *.py ]; then
    black "$FILE" 2>/dev/null
fi

exit 0
```

### Tamamlanmamış Görev Kontrolü

```bash
#!/bin/bash
# .kimi/hooks/check-complete.sh

if kimi task list --active 2>/dev/null | grep -q "running"; then
    echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Background tasks are still running. Please check /task first."}}'
    exit 0
fi

exit 0
```

## Konfigüre Edilmiş Hook'ları Görüntüleme

Shell modunda `/hooks` komutu ile mevcut hook'ları görüntüleyin:

```
/hooks
```

Örnek çıktı:
```
Configured Hooks:

  PostToolUse: 1 hook(s)
  PreToolUse: 1 hook(s)
  Notification: 1 hook(s)
  Stop: 1 hook(s)
```

## Tasarım İlkeleri

### Fail-Open Politikası

Tüm hook çalıştırma hataları (timeout, crash, regex hatası) "izin ver" olarak işlenir. Agent'ın normal iş akışı engellenmez. Hata nedenlerini log'lardan kontrol edebilirsiniz.

### Paralel Çalıştırma

Aynı event için birden fazla hook paralel çalıştırılır. Aynı komutlar otomatik olarak deduplicate edilir.

### Stop Hook Anti-Loop

Stop hook'ları sadece bir kez yeniden tetiklenebilir (sonsuz döngüyü önler). Yeniden tetiklendiğinde `stop_hook_active` alanı `true` olarak ayarlanır; hook'lar erken çıkabilir.

### Context Değişkenleri

Session ID ContextVar üzerinden iletilir, her tool çağrısında explicit parametre geçmeye gerek yoktur.

## Hook vs Plugin Karşılaştırması

| Özellik | Hook | Plugin |
|---------|------|--------|
| Tetikleyici | Yaşam döngüsü event'leri | Tool çağrıları |
| Zamanlama | Belirli event'ler | AI tarafından başlatılır |
| Etkileşim | Etkileşimsiz, stdin alır | JSON parametre alır |
| Amaç | Otomasyon, güvenlik, bildirim | AI yeteneklerini genişletme |
| Dönüş | Exit kodu akışı kontrol eder | stdout sonuç olarak döner |

Hook'lar kritik noktalarda kontrol ve otomasyon için; plugin'ler AI'a yeni tool yetenekleri kazandırmak içindir. Birlikte kullanılabilir — örneğin hook'larla belirli operasyonları engelleyip plugin'lerle alternatifler sunulabilir.

## Kaynaklar

- Kimi Code CLI Docs — Hooks: https://www.kimi.com/code/docs/en/kimi-code-cli/customization/hooks.html
