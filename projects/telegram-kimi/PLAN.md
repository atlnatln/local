# Telegram-Kimi Bridge Bot — Proje Planı

> **Tarih:** 26 Nisan 2026  
> **Durum:** Aktif geliştirme  
> **Bot:** @Kimivps_bot  
> **VPS:** 89.252.152.222  
> **Local:** Ubuntu masaüstü (akn-ub)

---

## 1. TAMAMLANAN İŞLEMLER

### 1.1 Temel Bot Kurulumu
- [x] `bot.py` — Async Telegram bot (python-telegram-bot 20.7)
- [x] `acp_client.py` — ACP JSON-RPC 2.0 stdio client
- [x] `config.py` — Ortam değişkenleri yönetimi
- [x] `.env` — Token, authorized user ID, work dir
- [x] `systemd/telegram-kimi.service` — Otomatik başlatma

### 1.2 ACP Protokol Entegrasyonu
- [x] `initialize` → `session/new` → `session/prompt` akışı
- [x] `session/update` streaming (agent_message_chunk, tool_call)
- [x] `session/request_permission` InlineKeyboard (✅ Onayla / ❌ Reddet)
- [x] ACP session persistence (birden fazla mesajda session yaşar)
- [x] `session/cancel` desteği

### 1.3 Mesaj & Dosya Yönetimi
- [x] Uzun mesaj bölme (4000 karakter limiti)
- [x] `.txt` dosya okuma (max 1MB / 30K karakter)
- [x] **Excel desteği** — `.xlsx`, `.xlsm`, `.xls` (openpyxl 3.1.5)
  - Sheet isimleri, satır/sütun sayısı, ilk 20 satır
  - VBA projesi varlık kontrolü (.xlsm)
- [x] **VBA dosya gönderme** — ````vba` blokları otomatik `.vba` dosyası

### 1.4 Context & Token Takibi
- [x] `context.jsonl` → son `_usage` satırı okuma
- [x] `config.toml` → `max_context_size` okuma
- [x] Her yanıt sonunda footer: `📊 Context: 12.3k / 262.1k (4.7%)`

### 1.5 VPS Deploy & Local/VPS Mod
- [x] Bot kodu VPS'e kopyalandı (`/home/akn/telegram-kimi`)
- [x] VPS'te venv + bağımlılıklar kuruldu
- [x] VPS'te kimi-cli kuruldu (uv tool)
- [x] VPS'te systemd service aktif
- [x] **Reverse SSH tunnel** — `autossh` (local → VPS:9876)
- [x] SSH key-based auth (VPS ↔ local)
- [x] `/start`, `/start local`, `/start vps` komutları
- [x] Local'deki bot durduruldu & disabled

### 1.6 Güvenlik
- [x] SSH server sadece localhost'tan dinliyor (`ListenAddress 127.0.0.1`)
- [x] Password auth kapalı
- [x] `setfacl` ile `~/.kimi/logs` kalıcı izinler (`akn:rwx`)
- [x] `StrictHostKeyChecking=accept-new`

---

## 2. AKTİF SORUNLAR

### 🟢 KRİTİK: Local Mod Çalışmıyor → ÇÖZÜLDÜ
**Durum:** Bot `/start` komutunda "Local bilgisayar erişilemez" hatası veriyordu.

**Neden:** `AcpClient` `subprocess.Popen` ile `ssh` çalıştırırken, `stdin=subprocess.PIPE` nedeniyle `kimi acp` EOF alıp hemen çıkıyordu. `ssh -tt` pseudo-terminal allocate etse bile, subprocess PIPE ile PTY arasında veri iletilemiyordu.

**Çözüm:** `bot.py`'de `ssh` komutu yerine `script -q -c "ssh ..." /dev/null` pseudo-terminal wrapper kullanıldı. `script` komutu gerçek bir TTY oluşturduğu için `kimi acp` düzgün çalışıyor.

**Yapılan değişiklik:**
- `bot.py`: `import shlex` eklendi
- Local mod `AcpClient` yapılandırması `cmd="script", args=["-q", "-c", ssh_cmd, "/dev/null"]` olarak değiştirildi
- `ssh_cmd` `shlex.quote` ile güvenli şekilde oluşturuluyor
- Aynı değişiklik `auto` modda local fallback için de uygulandı

---

### 🟡 ORTA: Kimi CLI İzin Sorunu (VPS)
**Durum:** `~/.kimi/logs/kimi.log` dosyası `root` sahibi oluyor.

**Neden:** `kimi` komutu ara sıra `root` olarak çalıştırılıyor.

**Geçici çözüm:** `sudo chown -R akn:akn ~/.kimi`

**Kalıcı çözüm:** `setfacl` ile `logs` dizinine `akn:rwx` verildi. Reboot sonrası da geçerli.

**Durum:** Çözüldü (izleniyor).

---

## 3. GELECEKTE YAPILACAKLAR

### 3.1 Kısa Vade (Bu hafta)
- [x] **Local mod düzeltmesi** — `script` ile pseudo-terminal wrapper uygulandı
- [ ] Bot loglarının detaylı izlenmesi (`LOG_LEVEL=DEBUG` geçici)
- [ ] `/help` komutunu güncelle (yeni komutlar)

### 3.2 Orta Vade (Bu ay)
- [ ] **Session yönetimi** — `/resume`, session listeleme
- [ ] **Daha fazla dosya formatı** — `.csv`, `.pdf`, `.json`
- [ ] **OCR desteği** — Resimlerden metin okuma (PNG/JPG)
- [ ] **Auto-compaction uyarısı** — Context %80'i geçince kullanıcıyı uyarma
- [ ] **Background task izleme** — `/tasks`, `/task status`

### 3.3 Uzun Vade (Gelecek aylar)
- [ ] **Multi-user desteği** — Birden fazla authorized user
- [ ] **Webhook mode** — Polling yerine webhook (daha hızlı)
- [ ] **Session persistence** — Bot restart sonrası session'ı kurtarma
- [ ] **MCP Server entegrasyonu** — Kendi MCP tool'larını ekleme
- [ ] **Web arayüzü** — Telegram yerine web üzerinden erişim

---

## 4. TEKNİK DETAYLAR

### 4.1 Mimari
```
[Telegram] ←→ [Bot VPS'te] ←→ [kimi acp]
                     ↓
              [Local PC] ← SSH tunnel (port 9876)
```

### 4.2 Reverse SSH Tunnel
```bash
# Local PC'de çalışıyor (systemd)
autossh -M 0 -N -R 9876:localhost:22 akn@89.252.152.222
```

### 4.3 Context Okuma Akışı
```
context.jsonl → son "_usage" satırı → token_count
config.toml → models["kimi-code/kimi-for-coding"].max_context_size
```

### 4.4 Önemli Dizinler
| Dizin | Açıklama |
|---|---|
| `/home/akn/telegram-kimi/` | Bot kodu (VPS) |
| `/home/akn/vps/projects/telegram-kimi/` | Bot kodu (Local) |
| `~/.kimi/` | Kimi CLI config, logs, sessions |
| `~/.kimi/sessions/{md5(work_dir)}/` | Session dosyaları |
| `~/.ssh/id_ed25519_kimibot` | SSH key (VPS → Local) |

---

## 5. KOMUT REFERANSI

| Komut | Açıklama |
|---|---|
| `/start` | Otomatik mod (local açıksa local, kapalıysa VPS) |
| `/start local` | Her zaman local bilgisayardaki kimi CLI |
| `/start vps` | Her zaman VPS'teki kimi CLI |
| `/stop` | Kimi'yi kapat |
| `/cancel` | Aktif işlemi iptal et |
| `/help` | Yardım mesajı |

---

## 6. NOTLAR

- Kimi CLI ACP modu **slash komutlarını desteklemiyor** (`/clear`, `/plan`, vb.)
- Doğal dilde "context'i temizle" veya "plan hazırla" denebilir
- `kimi acp` stdio üzerinden NDJSON konuşur
- `session/update` notifikasyonları: `agent_message_chunk`, `tool_call`, `usage_update`
- Permission schema: `{"outcome": {"outcome": "selected", "optionId": "approve"}}`
