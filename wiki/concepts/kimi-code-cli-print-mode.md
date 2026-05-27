---
title: "Kimi Code CLI — Print Mode"
created: "2026-05-26"
updated: "2026-05-26"
type: concept
tags: [kimi-cli, tool, automation, ci-cd]
related:
  - kimi-code-cli
---

# Kimi Code CLI — Print Mode

> [[kimi-code-cli|Ana Kimi CLI sayfasına dön]]

Non-interactive çalışma modu. Script ve otomasyon senaryoları için tasarlanmıştır.

## Temel Kullanım

```bash
# Komut satırından (-p veya -c)
kimi --print -p "List all Python files in the current directory"

# Stdin'den
echo "Explain what this code does" | kimi --print
```

Özellikler:
- **Non-interactive**: İşlem bitince otomatik çıkar
- **Auto-approval**: Implicit `--afk` modu — tüm tool çağrıları otomatik onaylanır, `AskUserQuestion` ve plan modu geçişleri de otomatik handle edilir
- **Text output**: AI yanıtları stdout'a yazılır

## Sadece Final Mesaj

`--final-message-only` ile sadece son asistan mesajını çıktıla, ara tool çağrı süreçlerini atla:

```bash
kimi --print -p "Give me a Git commit message" --final-message-only
```

`--quiet` = `--print --output-format text --final-message-only` kısayoludur:

```bash
kimi --quiet -p "Give me a Git commit message"
```

## JSON Format

Programatik işleme için JSON giriş/çıkış desteği.

**JSON çıkış:**
```bash
kimi --print -p "Hello" --output-format=stream-json
```

Çıktı JSONL formatındadır (satır başına bir JSON):
```jsonl
{"role":"assistant","content":"Hello! How can I help you?"}
```

**JSON giriş:**
```bash
echo '{"role":"user","content":"Hello"}' | kimi --print --input-format=stream-json --output-format=stream-json
```

Bu modda Kimi Code CLI stdin'den sürekli okur, her mesajı işleyip yanıt verir. stdin kapanana kadar devam eder.

## Mesaj Formatı

Giriş ve çıkış birleşik mesaj formatı kullanır.

**Kullanıcı mesajı:**
```json
{"role": "user", "content": "Your question"}
```

**Asistan mesajı (tool call ile):**
```json
{
  "role": "assistant",
  "content": "Let me execute this command.",
  "tool_calls": [
    {
      "type": "function",
      "id": "tc_1",
      "function": {
        "name": "Shell",
        "arguments": "{\"command\":\"ls\"}"
      }
    }
  ]
}
```

**Tool mesajı:**
```json
{"role": "tool", "tool_call_id": "tc_1", "content": "Tool execution result"}
```

## Exit Kodları

Print mode script ve CI sistemlerinin retry kararı vermesini sağlar:

| Kod | Anlamı | Açıklama |
|-----|--------|----------|
| `0` | Başarılı | Görev normal tamamlandı |
| `1` | Başarısız (tekrar denenmez) | Config hatası, auth failure, quota exhaustion gibi kalıcı hatalar |
| `75` | Başarısız (tekrar denenebilir) | 429 rate limit, 5xx server error, connection timeout gibi geçici hatalar |

Retry örneği:
```bash
kimi --print -p "Run task"
code=$?
if [ $code -eq 75 ]; then
  echo "Transient error, retrying..."
  sleep 10
  kimi --print -p "Run task"
elif [ $code -ne 0 ]; then
  echo "Unrecoverable error, exit code: $code"
  exit $code
fi
```

## Kullanım Senaryoları

**CI/CD entegrasyonu:**
```bash
kimi --print -p "Check if there are any obvious security issues in src/, output JSON report"
```

**Batch işleme:**
```bash
for file in src/*.py; do
  kimi --print -p "Add type annotations to $file"
done
```

**Diğer araçlarla entegrasyon:**
```bash
my-tool | kimi --print --input-format=stream-json --output-format=stream-json | process-output
```
