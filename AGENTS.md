# AGENTS.md — /home/akn/local

> AI agent'lar için proje context'i ve **hayati kuralları**.
> Detaylı komutlar için `references/QUICKREF.md`, wiki iş akışları için `references/WORKFLOW.md`.

---

## 🖥️ SEN NEREDESİN? (Her Açılışta ZORUNLU)

```bash
is_vps() { [[ -d "/home/akn/vps" ]]; }
if is_vps; then
    echo "VPS"
elif [[ "$HOSTNAME" = "akn-ub" ]] || [[ -d "/home/akn/local/projects" ]]; then
    echo "LOCAL"
else
    echo "BILINMIYOR"
fi
```

**👉 YUKARIDAKİ KOMUTU ÇALIŞTIR. ÇIKTISINI BURAYA YAZ: ____________**

| Çıktı | Ne Demek? | Ne Yapmalısın? |
|-------|-----------|----------------|
| **VPS** | Canlı sunucu (`/home/akn/vps` var) | Production servisleri yönet, deploy etme, log izle |
| **LOCAL** | Geliştirme makinesi (`akn-ub`) | Kod yaz, test et, wiki güncelle, GitHub'a push et |
| **BILINMIYOR** | Ortam belirsiz | `is_vps()` komutunu çalıştır, manuel tespit et |

**Ortam Ayrımı:**

| | **LOCAL** | **VPS** |
|---|---|---|
| Çalışma Dizini | `/home/akn/local` | `/home/akn/vps` (deploy alanı) |
| SSH | `ssh akn@89.252.152.222` | — |
| Amaç | Kod yazma, test, build, wiki | Production çalıştırma, monitoring |
| Servisler | `mathlock-backend`, `mathlock-celery` | `ops-bot`, `sec-agent`, `telegram-kimi`, `webimar` (Docker), `mathlock-play` |

> **Kural (HER İKİ ORTAM):** Kod burada yazılır/build edilir, `deploy.sh` ile VPS'e gönderilir. Canlı ortam dosyalarını doğrudan düzenleme.

---

## 🔴 KATI KURAL: Commit/Push ÖNCESİ Wiki TOPLANMALIDIR 🔴

**İhlali kritiktir. HEM local HEM VPS'te geçerlidir.**

Aşağıdakilerden **herhangi biri** değiştiğinde wiki ingest zorunludur:
- `AGENTS.md`, `README.md`, `SCHEMA.md`
- `wiki/` dizinindeki herhangi bir dosya
- Herhangi bir projenin `deploy.sh`, `README.md`, `AGENTS.md`
- `infrastructure/` altındaki yapılandırma dosyaları
- `scripts/wiki-*` dosyaları

**Checklist:** `git diff` → wiki ingest → lint → `git add -A` → `git commit -m "type(scope): ..."` → `git push origin main`

**Otomatik Koruma:** pre-commit/pre-push hook'lar kuruludur. Atlama (ACİL): `git commit --no-verify`

---

## Session Başlangıç Temizliği

Her session başında:
1. `rm -f ~/.wiki-skip-session` → Önceki session'dan kalan skip flag'ini temizle
2. GitHub sync kontrolü → sonra wiki kontrolü

### Git Sync Kontrolü (KESİN Sıra: Git → Pull → Wiki)

```bash
# Fetch
 cd /home/akn/local          && timeout 5 git fetch origin
 cd /home/akn/local/ops-bot  && timeout 5 git fetch origin
 cd /home/akn/local/projects/webimar && timeout 5 git fetch origin
# Behind/ahead kontrolü
 git rev-list --left-right --count origin/main...HEAD
```

| Durum | Eylem |
|-------|-------|
| `Behind > 0` | **Wiki kontrolünü ATLA.** "GitHub'da N commit var. Önce `git pull` yapalım mı?" |
| `Ahead > 0` | Bilgi ver. Wiki kontrolüne devam et (ama "önce push et" öner). |
| Sync | Wiki kontrolüne geç. |

> **Neden behind'da wiki atlanır?** Eski commit'lere göre wiki güncellenirse diğer makinedeki geliştirmelerin wiki yansıması kaybolur veya geri taşınır.

**Otomatik sync:** `cd /home/akn/local && bash scripts/auto-sync.sh` (sadece fast-forward pull yapar, conflict varsa durur)

### Proaktif Wiki Kontrolü

```bash
cat /home/akn/local/wiki/.pending 2>/dev/null || echo "EMPTY"
```

`EMPTY` değilse → `AskUserQuestion`: "Wiki güncellemesi bekliyor: {X} proje, {Y} commit. Otomatik toplayayım mı?"
- **Evet** → `wiki topla` flow'u (ara sorma yok)
- **Hayır** → marker'ı koru, devam et
- **Bu session sorma** → `touch ~/.wiki-skip-session`, devam et

**Skip:** Kullanıcı zaten `wiki ...` komutu söylediyse veya `~/.wiki-skip-session` varsa atla.

---

## Wiki Ingest Flow (9 Adım)

Kullanıcı "wiki topla"/"wiki ingest"/"wiki güncelle" dediğinde ara sormadan tek seferde:

| Adım | İşlem |
|------|-------|
| 1 | Checkpoint SHA'ları oku (`.checkpoints/*.sha`) |
| 2 | Her repo için `git diff --name-status <checkpoint>..HEAD` |
| 3 | Diff boşsa → `.pending` temizle, lint, log'a "no changes", bitir |
| 4 | Diff doluysa → değişen dosyaları analiz et (A/M/D/R) |
| 5 | İlgili wiki sayfalarını güncelle (`wiki/projects/<repo>.md`) |
| 6 | Çapraz referansları yenile (`index.md`, `log.md`) |
| 7 | Lint çalıştır: `python3 scripts/wiki_lint.py /home/akn/local/wiki` |
| 8 | Checkpoint'leri güncelle (`git rev-parse HEAD > .checkpoints/<repo>.sha`) |
| 9 | `.pending` temizle, kullanıcıya özet rapor ver |

Detaylı komutlar ve kurallar: `references/WORKFLOW.md` ve `~/.kimi/skills/local-wiki/SKILL.md`

---

## Push Komutu Protokolü (Zorunlu Wiki Ingest)

Kullanıcı "push yap" dediğinde:

1. `git status --short` → değişiklik özetini göster
2. **ZORUNLU:** `git status --short | grep -E "^wiki/"` → wiki değişikliği varsa wiki ingest çalıştır → `git add wiki/ && git commit -m "docs(wiki): ingest <proje>"`
3. Commit mesajı iste (`type(scope): description`)
4. `git add -A && git commit -m "..." && git push origin main`
5. `ops-bot/` veya `webimar/` dirty ise: **"Nested repo'ları da unutma!"**

**Nested Repo Hatırlatması:** `ops-bot/` ve `projects/webimar/` root repo'da `.gitignore`'dadır. Ayrı GitHub repo'larıdır. Kendi dizinlerinde ayrı commit + push yapılmalı.

---

## Proje Yapısı (Monorepo)

```
/home/akn/local/
├── infrastructure/    # nginx, SSL, monitoring (Docker)
├── ops-bot/           # Telegram bot (Python, systemd, ayrı repo)
├── projects/
│   ├── webimar/       # Django + Next.js + React (ayrı repo)
│   ├── mathlock-play/ # Android + Django
│   └── telegram-kimi/ # Telegram Kimi bot
├── scripts/           # Yardımcı script'ler
├── wiki/              # LLM Wiki
└── ARCHITECTURE.md    # Detaylı mimari
```

Detaylı komutlar: `references/QUICKREF.md` | Wiki iş akışları: `references/WORKFLOW.md` | Kod stili: `references/CONVENTIONS.md`

---

## Güvenlik Notları

- **sudo şifresi:** Kullanıcıya sor (sadece yerel, VPS'te sudoers var)
- **SSH key:** `~/.ssh/id_ed25519`
- **API Key'ler:** `.env` dosyalarında, asla commit'lenmez
- **SSL:** Let's Encrypt, otomatik yenileme
- **sec-agent:** `ops-bot/sec-agent/` — 3 dk'da bir sweep

---

> **Son güncelleme:** 2026-05-09
> **Wiki durumu:** 7 proje ingest edildi, 8/10 lint passing
> **VPS durumu:** ops-bot ✅, sec-agent ✅, telegram-kimi ✅, webimar ✅, mathlock-play ✅
> **GitHub:** `github.com:atlnatln/local.git`
