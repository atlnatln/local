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
| **Servisler** | mathlock-backend (systemd), mathlock-celery (systemd) | ops-bot (systemd), sec-agent (systemd), telegram-kimi (systemd), webimar (Docker), anka (Docker), mathlock-play (systemd + Docker) |
| **Nginx** | Yok (VPS nginx container'a yönlendirir) | `vps_nginx_main` container'ı (80/443) |

**Kural:** Burada yazılan kod, build edilen image'lar ve hazırlanan paketler `deploy.sh` ile VPS'e gönderilir. Canlı ortamdaki dosyaları doğrudan düzenleme.

---

## Proje Yapısı (Monorepo)

```
/home/akn/local/
├── infrastructure/          # nginx, SSL, monitoring (Docker)
├── ops-bot/                 # Telegram bot (Python, systemd, ayrı repo)
├── projects/
│   ├── webimar/             # Django + Next.js + React (ayrı repo)
│   ├── anka/                # B2B veri servisi
│   ├── mathlock-play/       # Android + Django
│   └── telegram-kimi/       # Telegram Kimi bot
├── scripts/                 # Yardımcı script'ler
├── docs/                    # Operasyonel notlar
├── wiki/                    # LLM Wiki
└── ARCHITECTURE.md          # Detaylı mimari
```

**Git yapısı:**
- `ops-bot/` ve `projects/webimar/` **ayrı git repo'larıdır** (GitHub'a bağlı)
- Geri kalan her şey ana `/home/akn/local/.git` monorepo'su içindedir

Detaylı proje bilgileri, stack'ler ve entry point'ler için bkz. `wiki/system-overview.md` ve `wiki/projects/`.

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
- [ ] Wiki ingest yapıldı (eğer proje docs'u değiştiyse): `wiki ingest <proje>`

---

## Session Başlangıç Temizliği

Her session başında ÖNCE şunu yap:
- `rm -f ~/.wiki-skip-session 2>/dev/null` → Önceki session'dan kalan skip flag'ini temizle
- Sonra "Proaktif Wiki Kontrolü" adımlarına devam et

Neden: Kullanıcı "bu session'da tekrar sorma" dedi, kapattı, ertesi gün açtı. Eğer bu dosya kalırsa wiki bir daha asla sormaz. Her yeni session'da otomatik silinmeli.

## Proaktif Wiki Kontrolü (Auto-Prompt)

Kullanıcıya ilk yanıt vermeden ÖNCE aşağıdaki adımları takip et:

### Skip Koşulları (Proaktif Kontrolü Atlama)
Aşağıdaki durumlarda proaktif kontrolü ATLA:
- Kullanıcı direkt `wiki ...` komutu söylediyse (örn. `wiki durum`). Zaten wiki ile ilgileniyor, tekrar sorma.
- Kullanıcı `/flow:wiki-topla` yazdıysa. Zaten flow çalışıyor, tekrar sorma.
- `~/.wiki-skip-session` dosyası varsa (kullanıcı "bu session'da tekrar sorma" dedi).

**NOT:** Kullanıcı `wiki topla`, `wiki ingest`, `wiki güncelle` gibi komutlar söylerse, proaktif kontrolü atla ve doğrudan **Wiki Ingest Flow (Tool-Based)** bölümündeki adımları takip et.

### Kontrol Adımları
1. `cat /home/akn/local/wiki/.pending 2>/dev/null || echo "EMPTY"` çalıştır
2. Eğer çıktı `EMPTY` değilse:
   - Satır sayısını say → kaç commit bekliyor
   - Repo isimlerini parse et → kaç proje etkilenmiş
   - `AskUserQuestion` ile kullanıcıya sor:
     - **Soru:** "Wiki güncellemesi bekliyor: {X} proje, {Y} commit. Otomatik toplayayım mı?"
     - **Seçenekler:**
       1. "Evet, otomatik topla" (Recommended)
       2. "Sadece bir projeyi güncelle (manual)" → proje adı iste, sonra `local-wiki` skill'ini kullan
       3. "Durumu göster" → `wiki durum` çalıştır, sonra tekrar bu soruyu sor
       4. "Şimdi değil (bir sonraki seansta tekrar sor)" → sessizce devam et, marker'ı koru
       5. "Bu session'da tekrar sorma" → `touch ~/.wiki-skip-session`, sessizce devam et
3. **Seçenek 1 seçilirse (CRITICAL):**
   - Hemen **Wiki Ingest Flow (Tool-Based)** bölümündeki adımları takip et
   - Kullanıcıya ara sorular sorma, tüm işlemi tek seferde bitir
4. Seçenek 2 veya 3 seçilirse:
   - `local-wiki` skill'ini lazy-load et (SKILL.md oku)
   - Orientation Ritual'ı takip et: CONVENTIONS.md → SCHEMA.md → index.md → log.md
   - WORKFLOW.md'ye göre ingest çalıştır
   - **Başarılı ingest sonrası** marker dosyasını temizle: `> /home/akn/local/wiki/.pending`
5. Seçenek 4 ("Şimdi değil") seçilirse:
   - Marker'ı silme (bir sonraki seansta tekrar sorulacak)
   - Kullanıcının orijinal sorusuna/söylediğine geç
6. Seçenek 5 ("Bu session'da tekrar sorma") seçilirse:
   - `touch ~/.wiki-skip-session`
   - Marker'ı silme (bir sonraki session'da tekrar sorulacak, ama bu session'da atlanacak)
   - Kullanıcının orijinal sorusuna/söylediğine geç

---

## Wiki Ingest Flow (Tool-Based)

Bu bölüm, wiki ingest işleminin **tam otomatik** çalışması için gerekli adımları tanımlar. Kullanıcı "Evet, otomatik topla" dediğinde veya `wiki topla`/`wiki ingest`/`wiki güncelle` komutları geldiğinde, LLM bu adımları ara sormadan tek seferde tamamlar.

### Adım 1: Checkpoint'leri Oku
```bash
cat /home/akn/local/wiki/.checkpoints/local.sha
cat /home/akn/local/wiki/.checkpoints/ops-bot.sha
cat /home/akn/local/wiki/.checkpoints/webimar.sha
```

### Adım 2: Git Diff Kontrolü
Her proje için checkpoint SHA ile HEAD arasındaki farkı kontrol et:
```bash
cd /home/akn/local && git diff --name-status $(cat wiki/.checkpoints/local.sha)..HEAD
cd /home/akn/local/ops-bot && git diff --name-status $(cat /home/akn/local/wiki/.checkpoints/ops-bot.sha)..HEAD
cd /home/akn/local/projects/webimar && git diff --name-status $(cat /home/akn/local/wiki/.checkpoints/webimar.sha)..HEAD
```

### Adım 3: Karar (LLM Kendi Yapar, Kullanıcıya Sorma)
- **Eğer TÜM diff'ler boşsa:**
  1. `.pending` marker dosyasını temizle: `> /home/akn/local/wiki/.pending`
  2. Wiki lint çalıştır
  3. Log'a "no changes" girişi ekle
  4. Kullanıcıya özet rapor ver, bitir
- **Eğer en az bir diff doluysa:** Adım 4'e devam et

### Adım 4: Değişen Dosyaları Analiz Et
Diff çıktısındaki her satırı parse et:
- `A	<path>` → Yeni dosya eklendi
- `M	<path>` → Dosya değiştirildi
- `D	<path>` → Dosya silindi
- `R	<old>	<new>` → Dosya yeniden adlandırıldı

### Adım 5: Wiki Sayfalarını Güncelle
Her değişen dosya için ilgili wiki sayfasını bul (wiki/projects/<repo>.md):
- Yeni dosya → Sayfa bölümüne ekle
- Değişiklik → Sayfadaki ilgili bölümü güncelle
- Silme → Sayfaya `[STALE]` işareti koy veya arşivle
- Yeniden adlandırma → Eski yolu güncelle, yeni ekle

### Adım 6: Çapraz Referansları Yenile
- `wiki/index.md`'deki proje listesini kontrol et
- Yeni projeler varsa ekle
- `wiki/log.md`'ye yeni giriş ekle

### Adım 7: Lint Kontrolü
```bash
cd ~/.kimi/skills/local-wiki && python3 scripts/wiki_lint.py /home/akn/local/wiki
```
- Eğer 10/10 passing ise → Adım 8'e devam
- Eğer hata varsa → Hataları düzelt, tekrar lint çalıştır

### Adım 8: Checkpoint'leri Güncelle
Her proje için mevcut HEAD SHA'sını checkpoint dosyasına yaz:
```bash
cd /home/akn/local && git rev-parse HEAD > wiki/.checkpoints/local.sha
cd /home/akn/local/ops-bot && git rev-parse HEAD > /home/akn/local/wiki/.checkpoints/ops-bot.sha
cd /home/akn/local/projects/webimar && git rev-parse HEAD > /home/akn/local/wiki/.checkpoints/webimar.sha
```

### Adım 9: Son Temizlik
1. `.pending` marker dosyasını temizle: `> /home/akn/local/wiki/.pending`
2. Kullanıcıya özet rapor ver:
   - Kaç proje güncellendi
   - Kaç sayfa değiştirildi/eklendi/silindi
   - Lint sonucu
   - Yeni checkpoint SHA'ları

---

## Wiki Kullanımı (local-wiki)

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen bilgi tabanı. Detaylı komut rehberi ve organizasyon kuralları: bkz. `wiki/README.md`.

**Wiki komutları:**
- `wiki topla` veya `wiki ingest` veya `wiki güncelle` — **Tool-based flow'u başlat** (yukarıdaki 9 adımı otomatik çalıştır)
- `wiki durum` veya `wiki status` — Wiki durum özetini göster
- `/flow:wiki-topla` — Yapılandırılmış prompt flow (manuel kullanım için)

**Ne zaman wiki ingest yapılır:**
- Yeni modül eklendiğinde / refactor sonrası
- Deploy script değiştiğinde
- README veya dokümantasyon güncellendiğinde
- Haftalık bakım rutini
- Kullanıcı `wiki topla`, `wiki ingest` istediğinde

**Obsidian:** `wiki/` dizinini vault olarak açabilirsin. `[[wikilink]]` desteği ve Graph View çalışır.

---

## GitHub Sync ve Cross-Machine Development

Bu proje `github.com/atlnatln/local.git` reposu üzerinden yönetilir. GitHub = source of truth. Local ve VPS birbirine `git push` / `git pull` üzerinden senkronize olur.

### Dizin Yapısı (İki Makine)

| Makine | Dizin | Amaç |
|---|---|---|
| **Local** | `/home/akn/local/` | Geliştirme + git repo |
| **VPS** | `/home/akn/local/` | Git clone (geliştirme alanı) |
| **VPS** | `/home/akn/vps/` | Deploy alanı (tar.gz çıkarma, production) |

- Her iki makinede de `/home/akn/local/` aynı yapıya sahip git repodur.
- VPS'teki `/home/akn/vps/` deploy script'lerinin hedefi olarak kalır (GitHub'dan bağımsız).
- AGENTS.md'lerdeki `/home/akn/local/` yolları her iki makinede de çalışır.

### Session Başı Git Kontrolü

Her session başında wiki kontrolüne paralel:

```
1. rm -f ~/.wiki-skip-session
2. timeout 5 git fetch origin 2>/dev/null || true
   → Behind ise: "GitHub'da yeni değişiklik var (N commit). Pull yapalım mı?"
   → Ahead ise: "Local'de push bekleyen değişiklik var."
   → Sync veya offline: sessizce devam et
3. Wiki kontrolü (.pending)
```

**Not:** Otomatik pull YAPMA. Conflict riski var. Kullanıcı onay verirse `git pull` çalıştır.

### Push Komutu Protokolü (Zorunlu Wiki Ingest)

Kullanıcı "push yap" dediğinde:

```
1. git status --short → değişiklik özetini göster
2. ZORUNLU: Wiki kontrolü
   a. git status --short | grep -E "wiki/|\\.checkpoints" → wiki değişikliği var mı?
   b. Eğer wiki değişikliği varsa:
      - "Wiki değişiklikleri toplanmamış. Önce wiki ingest çalıştırılıyor."
      - wiki ingest çalıştır (veya wiki topla)
      - git add wiki/ && git commit -m "docs(wiki): ingest <proje>"
   c. Eğer wiki değişikliği yoksa: devam et
3. Commit mesajı iste (type(scope): description formatında öner)
4. git add -A && git commit -m "..." && git push origin main
5. Eğer ops-bot/ veya webimar/ dirty ise: "Nested repo'ları da unutma!" uyarısı
```

**Kural:** Wiki dosyalarında (`wiki/`, `.checkpoints/`) değişiklik varsa, wiki ingest yapılmadan ve commit edilmeden **push yapılmaz**.

### Nested Repo Hatırlatması

- `ops-bot/` ve `projects/webimar/` root repo'da `.gitignore`'dadır.
- Bunlar ayrı GitHub repo'larıdır (`github.com/atlnatln/ops-bot`, `github.com/atlnatln/webimar`).
- Root repo push'u bunları içermez. Kendi dizinlerinde ayrı commit + push yapılmalı.

### Wiki Cross-Machine Sync

- Wiki hem local'de hem VPS'de aktif.
- Push öncesi wiki ingest iste (opsiyonel ama önerilir).
- `.checkpoints/*.sha` GitHub'da kalmalı (ortak referans).
- `.pending` her makinede ayrı oluşur (`wiki/.pending` gitignore'dadır).

### Git Auth (VPS)

- **SSH tercih edilir:** `git remote set-url origin git@github.com:atlnatln/local.git`
- **SSH key yoksa:** `git config credential.helper store` (bir kez token girilir, hatırlanır)

---

## Güvenlik Notları

- **sudo şifresi:** Kullanıcıya sor (sadece yerel makinede, VPS'te sudoers yapılandırması var)
- **SSH key:** `~/.ssh/id_ed25519` (VPS erişimi için)
- **API Key'ler:** `.env` dosyalarında, asla commit'lenmez
- **SSL:** Let's Encrypt, otomatik yenileme (`renew-ssl.sh`)
- **sec-agent:** `ops-bot/sec-agent/` — sürekli güvenlik izleme, 3 dk'da bir sweep

---

## Sık Kullanılan Komutlar

```bash
# Git
 git status --short              # Değişiklik özeti
git add -A && git commit -m "type(scope): ..."  # Commit
git push origin main            # Push
git pull origin main            # Pull
timeout 5 git fetch origin      # GitHub'daki son değişiklikleri kontrol et

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

> **Son güncelleme:** 2026-05-05  
> **Wiki durumu:** 7 proje ingest edildi, 10/10 lint passing  
> **VPS durumu:** ops-bot ✅, sec-agent ✅, telegram-kimi ✅, webimar ✅, anka ✅, mathlock-play ✅
> **GitHub:** `github.com/atlnatln/local.git`

> **GitHub push:** 2026-05-05 tarihinde test edildi ✅
