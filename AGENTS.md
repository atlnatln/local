# AGENTS.md — /home/akn/local

> AI agent'lar için proje context'i ve instruction'ları.

---

## 🖥️ SEN NEREDESİN? (Her Açılışta ZORUNLU)

Bu `AGENTS.md` dosyası **HEM local HEM VPS'te aynıdır**. Aşağıdaki komutu **çalıştır** ve çıktıya göre doğru bölümü oku.

```bash
if test -d "/home/akn/vps"; then
    echo "VPS"
elif test "$HOSTNAME" = "akn-ub" -o -d "/home/akn/local/projects"; then
    echo "LOCAL"
else
    echo "BILINMIYOR"
fi
```

**👉 YUKARIDAKİ KOMUTU ÇALIŞTIR. ÇIKTISINI BURAYA YAZ: ____________**

| Çıktı | Ne Demek? | Ne Yapmalısın? |
|-------|-----------|----------------|
| **VPS** | Canlı sunucudasın | Production servislerini yönet, deploy etme, log izle |
| **LOCAL** | Geliştirme makinesindesin | Kod yaz, test et, wiki güncelle, GitHub'a push et |
| **BILINMIYOR** | Ortam belirsiz | `is_vps()` komutunu çalıştır, manuel tespit et |

---

## Ortam Ayrımı (Kritik)

| | **LOCAL'deysem** | **VPS'teysem** |
|---|---|---|
| **Makine** | Yerel geliştirme istasyonu (`akn-ub`) | VPS (Ubuntu, `vps.aknatln.com`) |
| **Çalışma Dizini** | `/home/akn/local` | `/home/akn/vps` (deploy edilmiş kod) |
| **SSH** | VPS'ye bağlanmak için: `ssh akn@89.252.152.222` | — |
| **Amaç** | Kod yazma, test, build, wiki yönetimi | Production çalıştırma, monitoring |
| **Servisler** | `mathlock-backend`, `mathlock-celery` | `ops-bot`, `sec-agent`, `telegram-kimi`, `webimar` (Docker), `mathlock-play` |
| **Nginx** | Yok (VPS nginx container'a yönlendirir) | `vps_nginx_main` container'ı (80/443) |

**Kural (HER İKİ ORTAM İÇİN):** Kod burada yazılır, build edilir, `deploy.sh` ile VPS'e gönderilir. Canlı ortamdaki dosyaları doğrudan düzenleme.

---

## 🔴 KATI KURAL: Commit/Push ÖNCESİ Wiki TOPLANMALIDIR 🔴

**Bu kural HEM local HEM VPS'te geçerlidir. İhlali kritiktir.**

### Neden?

- Wiki = projenin **yaşayan belleği**
- Kod değişir ama wiki güncel kalmazsa sonraki agent'lar eski/yanlış bilgiyle çalışır
- Bilgi kaybı, tutarsızlık, tekrarlanan hatalar

### Ne Zaman Uygulanır?

Aşağıdaki dosyalardan **herhangi biri** değiştiğinde:
- `AGENTS.md`, `README.md`, `SCHEMA.md`
- `wiki/` dizinindeki herhangi bir dosya
- Herhangi bir projenin `deploy.sh`, `README.md`, `AGENTS.md`
- `infrastructure/` altındaki yapılandırma dosyaları
- `scripts/wiki-*` dosyaları

### Checklist (SIRASIYLA)

```
□ Değişen dosyaları analiz et (git diff)
□ İlgili wiki sayfalarını güncelle (ingest)
□ wiki log.md'ye ingest girişi ekle
□ wiki lint çalıştır → 10/10 hedefi
□ git add -A
□ git commit -m "type(scope): ..."
□ git push origin main
```

### Otomatik Koruma

Git hook'lar kuruludur:
- **pre-commit:** Dokümantasyon değişikliğinde commit'i engeller, talimat gösterir
- **pre-push:** Wiki dosyaları commit edilmemişse push'u engeller

Hook'ları atlamak için (ACİL durumlar): `git commit --no-verify`

---

### Ortam Tespiti (Environment Detection)

Agent'ın ve script'lerin hangi makinede çalıştığını anlaması için basit bir kural:

```bash
# VPS tespiti: /home/akn/vps dizini sadece VPS'te vardır
is_vps() { [[ -d "/home/akn/vps" ]]; }

# Kullanım
if is_vps; then
    echo "VPS ortamı — doğrudan deploy edilecek"
else
    echo "Local geliştirme ortamı — uzak VPS'ye gönderilecek"
fi
```

**Not:** Tüm `deploy.sh` script'leri bu tespiti içerir. VPS'te (`/home/akn/local` altında) çalıştırıldığında `scp`/`ssh` olmadan doğrudan deploy eder. Local'den çalıştırıldığında eski davranışı korur (uzak bağlantı).

---

## Proje Yapısı (Monorepo)

```
/home/akn/local/
├── infrastructure/          # nginx, SSL, monitoring (Docker)
├── ops-bot/                 # Telegram bot (Python, systemd, ayrı repo)
├── projects/
│   ├── webimar/             # Django + Next.js + React (ayrı repo)
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

Deploy script'leri **ortam tespiti** yapar. Aynı komutları hem local'den hem VPS'ten çalıştırabilirsin — script'ler otomatik olarak doğru davranışı seçer.

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

### 3. MathLock Play
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

Kullanıcıya ilk yanıt vermeden ÖNCE:

1. `rm -f ~/.wiki-skip-session` → Session temizliği
2. `cat /home/akn/local/wiki/.pending 2>/dev/null || echo "EMPTY"`
3. `EMPTY` değilse → `AskUserQuestion`: "Wiki güncellemesi bekliyor: {X} proje, {Y} commit. Otomatik toplayayım mı?"
   - **Evet** → `wiki topla` flow'u başlat (kullanıcıya ara sorma)
   - **Hayır/şimdi değil** → marker'ı koru, devam et
   - **Bu session sorma** → `touch ~/.wiki-skip-session`, devam et

**Skip:** Kullanıcı zaten `wiki ...` komutu söylediyse veya `~/.wiki-skip-session` varsa atla.

---

## Wiki Ingest Flow (Tool-Based)

Kullanıcı "wiki topla" / "wiki ingest" / "wiki güncelle" dediğinde veya proaktif kontrolde "evet" seçildiğinde, aşağıdaki 9 adımı ara sormadan tek seferde tamamla:

| Adım | İşlem |
|------|-------|
| 1 | Checkpoint SHA'ları oku (`wiki/.checkpoints/*.sha`) |
| 2 | Her repo için `git diff --name-status <checkpoint>..HEAD` |
| 3 | Tüm diff boşsa → `.pending` temizle, lint çalıştır, log'a "no changes", bitir |
| 4 | Diff doluysa → değişen dosyaları analiz et (A/M/D/R) |
| 5 | İlgili wiki sayfalarını güncelle (`wiki/projects/<repo>.md`) |
| 6 | Çapraz referansları yenile (`index.md`, `log.md`) |
| 7 | Lint çalıştır: `python3 scripts/wiki_lint.py /home/akn/local/wiki` |
| 8 | Checkpoint'leri güncelle (`git rev-parse HEAD > wiki/.checkpoints/<repo>.sha`) |
| 9 | `.pending` temizle (`> /home/akn/local/wiki/.pending`), kullanıcıya özet rapor ver |

Detaylı komutlar ve kurallar: bkz. `wiki/README.md` ve `~/.kimi/skills/local-wiki/SKILL.md`.

---

## Wiki Kullanımı (local-wiki)

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen bilgi tabanı.

**Komutlar:** `wiki topla` / `wiki ingest` / `wiki güncelle` → Tool-based flow başlatır. `wiki durum` → özet gösterir.

Detaylı rehber: `wiki/README.md` ve `~/.kimi/skills/local-wiki/SKILL.md`.

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

### Session Başı Git Kontrolü (Çift Yönlü Sync)

**Kullanıcı tek kişidir ve ya local'de ya da VPS'te geliştirir.** Kimi her session açılışında **önce GitHub'a bakmalı**, sonra wiki'ye. Çünkü diğer makineden push edilmiş commit'ler olabilir.

**Sıra (KESİN):** Git Sync Kontrolü → Pull (gerekirse) → Wiki Kontrolü

#### Adım 1 — Tüm Repo'lar İçin Fetch

```bash
cd /home/akn/local          && timeout 5 git fetch origin 2>/dev/null || true
cd /home/akn/local/ops-bot  && timeout 5 git fetch origin 2>/dev/null || true
cd /home/akn/local/projects/webimar && timeout 5 git fetch origin 2>/dev/null || true
```

#### Adım 2 — Behind/Ahead Kontrolü

Her repo için:
```bash
cd /home/akn/local          && git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "0 0"
cd /home/akn/local/ops-bot  && git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "0 0"
cd /home/akn/local/projects/webimar && git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "0 0"
```

| Çıktı | Anlamı | Eylem |
|-------|--------|-------|
| `Behind > 0` | GitHub'da yeni commit var (diğer makineden push edilmiş) | **Wiki kontrolünü ATLA.** "GitHub'da N commit var. Önce `git pull` yapmalısın." |
| `Ahead > 0` | Local'de push bekleyen değişiklik var | Bilgi ver. Wiki kontrolüne devam et (ama "önce push et" öner). |
| `Behind=0, Ahead=0` | Sync | Wiki kontrolüne geç. |

#### Adım 3 — Karar (KESİN)

- **Behind > 0 olan repo varsa:** Wiki proaktif kontrolünü **TAMAMEN ATLA**. Kullanıcıya sadece şunu söyle:
  > "GitHub'da {N} yeni commit var ({repo listesi}). Diğer makineden push edilmiş olabilir. Önce `git pull` yapalım mı?"
- Pull onay verilirse: `git pull origin main` çalıştır, ardından wiki kontrolüne geç.
- Pull reddedilirse: Kullanıcının orijinal sorusuna geç. Wiki'yi sorma.

**Neden?** Eğer behind durumunda wiki toplarsan, eski commit'lere göre wiki'yi güncellersin. Bu, diğer makinede yapılan geliştirmelerin wiki'ye yansımasını engeller veya geri taşır.

#### Adım 4 — Otomatik Sync (İsteğe Bağlı)

Manuel fetch kontrolü yerine `auto-sync.sh` script'i kullanılabilir:

```bash
cd /home/akn/local
bash scripts/auto-sync.sh
```

Bu script:
- Tüm repo'lar için `fetch` yapar
- Behind varsa **otomatik fast-forward pull** yapar
- Ahead varsa "push bekliyor" bildirir
- Diverged (conflict) varsa hata rapor eder, manuel müdahale ister

**Not:** `auto-sync.sh` sadece fast-forward pull yapar. Conflict varsa durur ve kullanıcıya bildirir.

#### Adım 5 — Wiki Kontrolü (Sadece Sync Durumunda)

Tüm repo'lar `Behind=0` ise, normal "Proaktif Wiki Kontrolü" akışına devam et.

### Push Komutu Protokolü (Zorunlu Wiki Ingest)

Kullanıcı "push yap" dediğinde:

```
1. git status --short → değişiklik özetini göster
2. ZORUNLU: Wiki kontrolü
   a. git status --short | grep -E "^wiki/" → wiki değişikliği var mı?
   b. Eğer wiki değişikliği varsa:
      - "Wiki değişiklikleri toplanmamış. Önce wiki ingest çalıştırılıyor."
      - wiki ingest çalıştır (veya wiki topla)
      - git add wiki/ && git commit -m "docs(wiki): ingest <proje>"
   c. Eğer wiki değişikliği yoksa: devam et
3. Commit mesajı iste (type(scope): description formatında öner)
4. git add -A && git commit -m "..." && git push origin main
5. Eğer ops-bot/ veya webimar/ dirty ise: "Nested repo'ları da unutma!" uyarısı
```

**Kural:** Wiki dosyalarında (`wiki/`) değişiklik varsa, wiki ingest yapılmadan ve commit edilmeden **push yapılmaz**.

### Nested Repo Hatırlatması

- `ops-bot/` ve `projects/webimar/` root repo'da `.gitignore`'dadır.
- Bunlar ayrı GitHub repo'larıdır (`github.com/atlnatln/ops-bot`, `github.com/atlnatln/webimar`).
- Root repo push'u bunları içermez. Kendi dizinlerinde ayrı commit + push yapılmalı.

### Wiki Cross-Machine Sync

- Wiki hem local'de hem VPS'de aktif.
- Push öncesi wiki ingest iste (opsiyonel ama önerilir).
- `.checkpoints/*.sha` gitignored'dır (local cursor). `.pending` GitHub üzerinden cross-machine sync sağlar.
- `.pending` her makinede ayrı oluşur (`wiki/.pending` gitignore'dadır).

### Wiki İçeriği İddiası Kuralı

Wiki dosyalarında **"X yok"**, **"Y yansımamış"** gibi kesin olumsuz iddia yapmadan önce:

1. `grep -r "aranan-terim" wiki/` ile doğrudan wiki dosyalarında ara
2. Bulamazsan `git log --grep="proje-adı" -- wiki/` ile wiki ingest commit'lerini kontrol et
3. Hâlâ emin değilsen **"kontrol edeyim"** de, **"yok"** deme

> **Neden:** Wiki ingest'ler (`docs(wiki): ingest ...`) kod commit'lerinden bağımsız ayrı commit'lerle yapılır. `git log -- projects/foo` sadece kod değişikliklerini gösterir; `wiki/` altındaki ingest commit'lerini görmez.

### Wiki Toplama Filtreleme Kuralı

`.pending` dosyasındaki her commit'i toplama sırasında filtrele. Post-commit hook basit tutulur (her commit'i yazar); agent (sen) `.pending`'i okuduğunda AGENTS.md'ye göre karar verirsin.

**Wiki'ye YAZILMALILAR (Etkili Değişiklikler):**
- `projects/*/app/src/main/java/**/*.kt` — Android logic değişiklikleri
- `projects/*/backend/**/*.py` — Backend API/model değişiklikleri
- `projects/*/scripts/*.py` — Pipeline/script değişiklikleri
- `deploy.sh`, `docker-compose.yml`, `systemd/` — Altyapı değişiklikleri
- `AGENTS.md`, `README.md`, `SCHEMA.md` — Proje dokümantasyonu değişiklikleri
- `.env.example` — Çevre değişkeni şablonu değişiklikleri

**Wiki'ye YAZILMAMALILAR (Atla):**
- `*.xml` layout/values dosyaları — Sadece UI renk/padding/dimens
- `res/drawable/*`, `*.png`, `*.svg`, `*.jpg` — Saf görsel asset'ler
- `*Test.kt`, `test_*.py`, `*_test.go` — Test dosyaları
- `.gitignore`, `gradle.properties`, `local.properties` — Config dosyaları
- `wiki/` altındaki dosyalar — Zaten wiki'nin kendisi
- `*.md` dosyaları (wiki hariç) — Zaten markdown

**Karar veremediğinde:**
```bash
cd /home/akn/local && git show --stat <SHA>
```
Değişen dosyaları gör, sonra yukarıdaki listeye göre karar ver.

> **Neden:** Karar mantığı AGENTS.md'de yaşar, hook script'ine gömülü kalmaz. Böylece kurallar zamanla evrilebilir, agent her session'da güncel kılavuzu okur.

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

### Her Ortamda Çalışan Komutlar
```bash
# Git
git status --short              # Değişiklik özeti
git add -A && git commit -m "type(scope): ..."  # Commit
git push origin main            # Push
git pull origin main            # Pull
(command -v git >/dev/null 2>&1 && timeout 5 git fetch origin) || true  # GitHub'daki son değişiklikleri kontrol et

# Wiki lint
cd ~/.kimi/skills/local-wiki && python3 scripts/wiki_lint.py /home/akn/local/wiki
```

### Local Geliştirme Ortamı Komutları
```bash
# Local servisler
systemctl status mathlock-backend mathlock-celery

# VPS'ye uzaktan bakış (local'den çalıştır)
ssh akn@89.252.152.222 "systemctl status ops-bot telegram-kimi"
ssh akn@89.252.152.222 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
ssh akn@89.252.152.222 "docker exec vps_nginx_main nginx -t"
ssh akn@89.252.152.222 "journalctl -u ops-bot -n 50 --no-pager"
```

### VPS Geliştirme Ortamı Komutları
```bash
# VPS'te çalışan servisler (doğrudan çalıştır)
systemctl status ops-bot telegram-kimi
docker ps --format 'table {{.Names}}\t{{.Status}}'
docker exec vps_nginx_main nginx -t
journalctl -u ops-bot -n 50 --no-pager

# Docker container'ları
 docker compose -f docker-compose.prod.yml ps
```

---

> **Son güncelleme:** 2026-05-09  
> **Wiki durumu:** 7 proje ingest edildi, 8/10 lint passing  
> **VPS durumu:** ops-bot ✅, sec-agent ✅, telegram-kimi ✅, webimar ✅, mathlock-play ✅
> **GitHub:** `github.com/atlnatln/local.git`

> **GitHub push:** 2026-05-09 tarihinde test edildi ✅
