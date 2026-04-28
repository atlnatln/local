# Telegram Kimi Bridge

VPS'deki [Kimi Code CLI](https://github.com/MoonshotAI/kimi-cli)'yi Telegram üzerinden kullanmanızı sağlayan bir köprü botudur.

## Özellikler

- `/start` ile Kimi'yi başlat, `/stop` ile kapat
- Doğrudan mesaj yazarak Kimi ile sohbet et
- Aynı oturumda (session) devam etme — bağlam korunur
- Uzun yanıtlar otomatik parçalanır
- `/cancel` ile uzun süren işlemi iptal et
- Sadece yetkili kullanıcılar erişebilir

## Kurulum

### 1. Gerekli bağımlılıkları kur

```bash
cd /home/akn/vps/projects/telegram-kimi
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

### 2. Çevre değişkenlerini ayarla

```bash
cp .env.example .env
nano .env
```

```env
TELEGRAM_TOKEN=your_bot_token_here
AUTHORIZED_USERS=123456789
WORK_DIR=/home/akn/vps
```

- `TELEGRAM_TOKEN`: [BotFather](https://t.me/BotFather) üzerinden alınan token
- `AUTHORIZED_USERS`: Telegram user ID'niz (virgülle ayrılmış birden fazla olabilir)
- `WORK_DIR`: Kimi'nin çalışacağı dizin

### 3. Systemd servis olarak çalıştır

```bash
sudo cp systemd/telegram-kimi.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable telegram-kimi
sudo systemctl start telegram-kimi
```

Logları izlemek için:

```bash
sudo journalctl -u telegram-kimi -f
```

### 4. Manuel çalıştırma (test için)

```bash
./venv/bin/python bot.py
```

## Kullanım

Telegram'da bota şunları yazabilirsiniz:

| Komut | Açıklama |
|-------|----------|
| `/start` | Kimi'yi başlat ve yeni oturum aç |
| `/stop` | Kimi'yi kapat |
| `/cancel` | Şu anki işlemi iptal et |
| `/help` | Yardım mesajı |
| Herhangi bir mesaj | Kimi'ye gönderilir |

## Teknik Detaylar

Bot, Kimi Code CLI'nin `kimi acp` (Agent Client Protocol) modunu kullanır. ACP, JSON-RPC 2.0 over stdio protokolüdür ve IDE'lerle entegrasyon için tasarlanmıştır. Bot, bu protokol üzerinden Kimi ile sürekli bir oturum sürdürür.

### Bilinen Sınırlamalar

- Kimi CLI ACP implementasyonu henüz TUI'deki `/help`, `/clear`, `/plan`, `/task` gibi slash komutlarını desteklemiyor. Bu komutları doğal dilde ifade edebilirsiniz (örneğin "sohbeti temizle" veya "plan moduna geç").
- Context/token kullanım bilgisi henüz ACP üzerinden görünmüyor.
- `ctrl+s` (araya prompt sokma) ve `ctrl+x` (shell mode) ACP protokolünde henüz desteklenmiyor.

## Proje Yapısı

```
telegram-kimi/
├── bot.py              # Telegram bot (async)
├── acp_client.py       # ACP JSON-RPC stdio client
├── config.py           # Yapılandırma
├── requirements.txt    # Python bağımlılıkları
├── .env.example        # Çevre değişkeni şablonu
├── README.md           # Bu dosya
└── systemd/
    └── telegram-kimi.service
```

## Lisans

Kişisel kullanım için.
