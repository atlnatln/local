# AGENTS.md — /home/akn/local

> AI agent'lar için proje context'i ve instruction'ları.

---

## Ortam Ayrımı (Kritik)

| | **Geliştirme (Burada)** | **Canlı (Uzak Sunucu)** |
|---|---|---|
| **Makine** | Yerel geliştirme istasyonu | VPS (Ubuntu) |
| **Dizin** | `/home/akn/local` | `/home/akn/vps` |
| **SSH** | — | `ssh akn@89.252.152.222` |
| **Amaç** | Kod yazma, test, build, wiki yönetimi | Production çalıştırma |
| **Servisler** | mathlock-backend (systemd), mathlock-celery (systemd) | ops-bot (systemd), telegram-kimi (systemd), webimar (Docker), anka (Docker) |
| **Nginx** | Yok (VPS nginx container'a yönlendirir) | `vps_nginx_main` container'ı (80/443) |

**Kural:** Burada yazılan kod, build edilen image'lar ve hazırlanan paketler `deploy.sh` ile VPS'e gönderilir. Canlı ortamdaki dosyaları doğrudan düzenleme.

---

## Proje Yapısı (Monorepo)

```
/home/akn/local/
├── infrastructure/          # Ortak nginx, SSL, monitoring (Docker)
│   ├── nginx/conf.d/        # Domain routing config'leri
│   ├── docker-compose.yml   # nginx + prometheus
│   ├── setup.sh             # Infrastructure kurulum
│   └── ssl/                 # Let's Encrypt sertifikaları
│
├── ops-bot/                 # Telegram operations bot (Python, systemd)
│   ├── agent.py             # Ana bot uygulaması
│   ├── routing.py           # Agent seçim mantığı
│   ├── deploy.sh            # VPS deploy script'i
│   ├── sec-agent/           # Güvenlik motoru
│   └── systemd/             # Unit/timer dosyaları
│
├── projects/
│   ├── webimar/             # Tarım İmar — Django + Next.js + React
│   │   ├── webimar-api/     # Django backend
│   │   ├── webimar-nextjs/  # Next.js frontend
│   │   ├── webimar-react/   # React SPA (hesaplamalar)
│   │   └── deploy.sh        # Docker image build + VPS upload
│   │
│   ├── anka/                # B2B veri servisi — Django + Next.js
│   │   ├── services/backend/
│   │   ├── services/frontend/
│   │   └── deploy.sh
│   │
│   ├── mathlock-play/       # Android math game + Django backend
│   │   ├── app/             # Android (Kotlin)
│   │   ├── backend/         # Django (systemd on VPS)
│   │   ├── website/         # Privacy/Support HTML
│   │   └── deploy.sh        # Build + data sync
│   │
│   └── telegram-kimi/       # Telegram Kimi bot
│
├── scripts/                 # Yardımcı shell script'leri
├── docs/                    # Operasyonel notlar
├── wiki/                    # LLM Wiki (kimi-cli tarafından yönetilir)
└── ARCHITECTURE.md          # Detaylı mimari doküman
```

**Git yapısı:**
- `ops-bot/` ve `projects/webimar/` **ayrı git repo'larıdır** (GitHub'a bağlı)
- Geri kalan her şey ana `/home/akn/local/.git` monorepo'su içindedir

---

## Deploy Komutları

### 1. Ops-Bot
```bash
cd /home/akn/local/ops-bot
./deploy.sh              # package modu (default): tar.gz → VPS
./deploy.sh --mode git   # git modu: VPS'te git pull + restart
```

### 2. Webimar
```bash
cd /home/akn/local/projects/webimar
./deploy.sh --skip-github   # Docker build + VPS upload (~10 dk)
```

### 3. Anka
```bash
cd /home/akn/local/projects/anka
./deploy.sh
```

### 4. MathLock Play
```bash
# Backend (host-based systemd on VPS)
cd /home/akn/local/projects/mathlock-play/backend
pip install -r requirements.txt
sudo systemctl restart mathlock-backend mathlock-celery

# Android build
./gradlew bundleRelease    # Play Store AAB
./gradlew assembleDebug    # Debug APK
```

### 5. Infrastructure (nginx, SSL)
```bash
cd /home/akn/local/infrastructure
sudo ./setup.sh --ssl
```

---

## VPS (Canlı) Erişim

```bash
# SSH
ssh akn@89.252.152.222

# Hızlı komutlar (yerelden VPS'ye)
ssh akn@89.252.152.222 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
ssh akn@89.252.152.222 "systemctl status ops-bot telegram-kimi"
ssh akn@89.252.152.222 "docker exec vps_nginx_main nginx -t"
```

**VPS'teki kritik dizinler:**
- `/home/akn/vps/ops-bot/` — Ops-Bot (systemd)
- `/home/akn/vps/projects/webimar/` — Webimar (Docker)
- `/home/akn/vps/projects/anka/` — Anka (Docker)
- `/home/akn/vps/projects/mathlock-play/` — MathLock (systemd + Docker)
- `/home/akn/vps/infrastructure/` — nginx, SSL

---

## Kod Stili ve Konvansiyonlar

### Dosya Adlandırma
- Shell script'ler: `kebab-case.sh`
- Python modülleri: `snake_case.py`
- Django app'leri: `snake_case`
- Next.js/React dosyaları: `PascalCase.tsx` (component), `kebab-case.ts` (utils)

### Git
- Commit mesaj formatı: `type(scope): description`
  - `feat(webimar): add new calculation endpoint`
  - `fix(ops-bot): handle timeout in agent routing`
  - `docs(wiki): update deployment guide`
- Her deploy öncesi commit
- `ops-bot` ve `webimar` için ayrı repo commit'leri, ardından `local` monorepo'ya commit

### Çevre Değişkenleri
- `.env` dosyaları asla commit'lenmez
- `.env.example` şablonu güncel tutulur
- Hassas veriler (API key, şifre) sadece VPS `.env`'lerinde ve yerel `~/.env`'de

---

## Test Prosedürleri

### Webimar
```bash
cd projects/webimar/webimar-api
pytest

cd ../webimar-nextjs
npm run lint
npm run build
```

### Anka
```bash
cd projects/anka/services/backend
pytest

cd ../frontend
npm run lint
```

### MathLock Play
```bash
cd projects/mathlock-play/backend
pytest
```

### Deploy Öncesi Checklist
- [ ] Kod derleniyor / testler geçiyor
- [ ] `.env.example` güncel
- [ ] Nginx config test geçiyor: `docker exec vps_nginx_main nginx -t`
- [ ] Wiki ingest yapıldı (eğer proje docs'u değiştiyse): `/wiki ingest <proje>`

---

## Wiki Kullanımı (local-wiki)

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen bilgi tabanı.

| Komut | Açıklama |
|-------|----------|
| `/wiki ingest` | Tüm projelerde değişiklik tara, wiki'yi güncelle |
| `/wiki ingest <proje>` | Tek proje işle (ops-bot, webimar, anka, mathlock-play, infrastructure) |
| `/wiki query "soru"` | Wiki'den cevap ara ve sentezle |
| `/wiki lint` | Sağlık kontrolü (10/10 check) |
| `/wiki status` | Checkpoint'leri ve sayfa sayısını göster |

**Ne zaman wiki ingest yapılır:**
- Yeni modül eklendiğinde / refactor sonrası
- Deploy script değiştiğinde
- README veya dokümantasyon güncellendiğinde
- Haftalık bakım rutini

**Obsidian:** `wiki/` dizinini vault olarak açabilirsin. `[[wikilink]]` desteği ve Graph View çalışır.

---

## Güvenlik Notları

- **sudo şifresi:** `jst` (sadece yerel makinede, VPS'te sudoers yapılandırması var)
- **SSH key:** `~/.ssh/id_ed25519` (VPS erişimi için)
- **API Key'ler:** `.env` dosyalarında, asla commit'lenmez
- **SSL:** Let's Encrypt, otomatik yenileme (`renew-ssl.sh`)
- **sec-agent:** `ops-bot/sec-agent/` — sürekli güvenlik izleme, 3 dk'da bir sweep

---

## Sık Kullanılan Komutlar

```bash
# Tüm servislerin durumu
systemctl status mathlock-backend mathlock-celery
ssh akn@89.252.152.222 "systemctl status ops-bot telegram-kimi"
ssh akn@89.252.152.222 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Nginx config test (VPS)
ssh akn@89.252.152.222 "docker exec vps_nginx_main nginx -t"

# Wiki lint
cd ~/.kimi/skills/local-wiki && python3 scripts/wiki_lint.py /home/akn/local/wiki

# Log takibi
ssh akn@89.252.152.222 "journalctl -u ops-bot -n 50 --no-pager"
```

---

> **Son güncelleme:** 2026-05-01  
> **Wiki durumu:** 5 proje ingest edildi, 10/10 lint passing  
> **VPS durumu:** ops-bot ✅, telegram-kimi ✅, webimar ✅, anka ✅, mathlock ✅
