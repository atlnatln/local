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
| Servisler | `mathlock-backend`, `mathlock-celery` | `ops-bot`, `sec-agent`, `telegram-kimi`, `webimar` (Docker) |

> **Kural (HER İKİ ORTAM):** Kod burada yazılır/build edilir, `deploy.sh` ile VPS'e gönderilir. Canlı ortam dosyalarını doğrudan düzenleme.  
> **Not:** VPS'te hem `/home/akn/local/` (git clone, geliştirme) hem `/home/akn/vps/` (deploy alanı) vardır.  
> **Garanti:** AGENTS.md'deki `/home/akn/local/` yolları her iki makinede de çalışır.

---

## 🔴 KATI KURAL: Commit/Push ÖNCESİ Wiki TOPLANMALIDIR 🔴

**İhlali kritiktir. HEM local HEM VPS'te geçerlidir.**

> **Neden:** Wiki = projenin **yaşayan belleği**. Kod değişir ama wiki güncel kalmazsa sonraki agent'lar eski/yanlış bilgiyle çalışır. Bilgi kaybı, tutarsızlık, tekrarlanan hatalar.

Aşağıdakilerden **herhangi biri** değiştiğinde wiki ingest zorunludur:
- `AGENTS.md`, `README.md`, `SCHEMA.md`
- `wiki/` dizinindeki herhangi bir dosya
- Herhangi bir projenin `deploy.sh`, `README.md`, `AGENTS.md`
- `infrastructure/` altındaki yapılandırma dosyaları
- `scripts/wiki-*` dosyaları

**Checklist:** `git diff` → wiki ingest → lint → `git add -A` → `git commit -m "type(scope): ..."` → `git push origin main`

**Otomatik Koruma:** pre-commit/pre-push hook'lar kuruludur.
- **pre-commit:** Dokümantasyon değişikliğinde commit'i engeller, talimat gösterir
- **pre-push:** Wiki dosyaları commit edilmemişse push'u engeller
- Atlama (ACİL): `git commit --no-verify`

---

## Session Başlangıç Temizliği

Her session başında:
1. `rm -f ~/.wiki-skip-session` → Önceki session'dan kalan skip flag'ini temizle
2. GitHub sync kontrolü → sonra wiki kontrolü

### Git Sync Kontrolü (KESİN Sıra: Git → Pull → Wiki)

> **Context:** Kullanıcı tek kişidir ve ya local'de ya da VPS'te geliştirir. **GitHub = source of truth.** Her session'da önce GitHub'a bak, sonra wiki'ye.

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

> `.pending` GitHub üzerinden cross-machine sync sağlar (commit'lenir); `.checkpoints/*.sha` ise gitignored local cursor'dur.  
>  
```bash
cat /home/akn/local/wiki/.pending 2>/dev/null || echo "EMPTY"
```

> **`.pending` formatı:** `TARIH|SON_INGEST_COMMIT|DOSYA_ADI|DOSYA_YOLU` — örn. `2026-05-10 12:53|5a047ee3|AGENTS.md|/home/akn/local/AGENTS.md`. Buradaki hash, dosyanın kendi hash'i değil, **son wiki ingest'in yapıldığı git commit hash'i** (kısaltılmış). `git diff --name-status 5a047ee3..HEAD -- AGENTS.md` ile değişiklik tespit edilir.
>
> `EMPTY` değilse → `AskUserQuestion`: "Wiki güncellemesi bekliyor: {X} proje, {Y} commit. Otomatik toplayayım mı?"
- **Evet** → `wiki topla` flow'u (ara sorma yok)
- **Hayır** → marker'ı koru, devam et
- **Bu session sorma** → `touch ~/.wiki-skip-session`, devam et

**Skip:** Kullanıcı zaten `wiki ...` komutu söylediyse veya `~/.wiki-skip-session` varsa atla.

---

## Wiki Kullanımı

`/home/akn/local/wiki` — Kimi CLI tarafından yönetilen bilgi tabanı. `wiki topla` / `wiki ingest` / `wiki güncelle` → tool-based flow başlatır.

### Wiki'de Bilgi Arama

Üst ajan wiki'de bilgi ararken **asistan birincil kaynaktır**:

```bash
python3 /home/akn/local/scripts/wiki-assistant.py --query "<konu>"
```

Asistan ilgili sayfaları ve bölümleri JSON olarak sunar. Daha hızlıdır ve token tasarrufu sağlar.

**Asistan çalışmazsa veya yetersiz kalırsa:** `index.md` → alt index → `Grep` arama → `ReadFile` okuma → wikilink gezintisi

> Asistan cache'i (`wiki/.assistant-index.json`) wiki sayfalarının başlık yapısını tutar. Değişmemiş sayfalar için tekrar parse edilmez.

İlk başvuru kaynağı her zaman `index.md`'dir. Acil/kronolojik bilgi için `log.md`, tag taksonomisi için `SCHEMA.md` kullanılır.

## Wiki Ingest Flow

Kullanıcı "wiki topla"/"wiki ingest"/"wiki güncelle" dediğinde **asistanlı akış** birincildir.

### Asistanlı Akış (Birincil)

| Adım | İşlem | Kim Yapar? |
|------|-------|------------|
| 1 | Checkpoint SHA'ları oku (`wiki/.checkpoints/*.sha`) | Kimi |
| 2 | Git diff çalıştır (`git diff --name-status <checkpoint>..HEAD`) | Kimi |
| **3** | **Asistanı çalıştır: `python3 /home/akn/local/scripts/wiki-assistant.py --prepare [--project X]`** | **Kimi çağırır, Asistan çalıştırır** |
| 4 | Asistan JSON çıktısını analiz et. Diff boş mu kontrol et. | Kimi |
| 5 | Asistanın `changed_files[].snippets` çıktısını oku. Sadece snippet'leri değerlendir. | Kimi |
| 6 | Asistanın `wiki_targets[].sections` çıktısını kullan. **Sadece ilgili bölümleri** oku. | Kimi |
| 7 | Çapraz referansları yenile. Asistan candidate listesi sunar. | Kimi |
| 8 | Lint çalıştır: `wiki_lint.py` | Kimi (veya Asistan çağırır) |
| 9 | Checkpoint'leri güncelle | Kimi |
| 10 | `.pending` temizle, kullanıcıya özet rapor ver | Kimi |

**Asistan ne yapar?**
- Git diff analizi (checkpoint'ten HEAD'e)
- Değişen dosyaları ilgili wiki sayfalarına eşler
- Her dosyadan snippet (yapısal özet) çıkarır
- Wiki sayfalarından ilgili bölümleri bulur
- Tüm bunları JSON "context paketi" olarak Kimi'ye sunar

**Asistan cache'i:** `wiki/.assistant-index.json` — wiki sayfalarının başlık yapısını cache'ler. Değişmemiş sayfalar için tekrar parse etmez.

### Fallback (Asistan Çalışmazsa)

Eğer `wiki-assistant.py` hata verirse veya çıktı üretmezse:
1. Hatayı kullanıcıya söyle
2. Klasik akışa dön: Checkpoint → Git diff → Dosyaları oku → Wiki güncelle → Lint → Checkpoint güncelle
3. Asistan olmadan devam et

### Token Tasarrufu Kuralları

> Aşağıdaki kurallar `wiki/concepts/wiki-growth-protocol.md` ve `references/CONVENTIONS.md`'den türetilmiştir.
> **Not:** Kurallar 2 ve 3 artık `wiki-assistant.py` tarafından otomatik uygulanır. Asistan zaten sadece ilgili bölümleri sunar ve `StrReplaceFile` öncesinde dosyayı açmaz.

| # | Kural | Neden |
|---|-------|-------|
| 1 | **Lint sonuçları `log.md`'ye yazılmaz.** Lint sadece kontrol edilir, PASS/WARN/FAIL kullanıcıya söylenir. Geçmiş lint kayıtları `wiki/log-lint-archive.md`'de arşivlenir. | `log.md`'nin gereksiz büyümesini engeller |
| 2 | **Wiki sayfasını baştan sona okuma.** Asistan `wiki_targets[].sections.matched` ile sadece ilgili bölümü sunar. Eşleşme yoksa `type: "outline"` ile başlık listesi gelir. | ~%90 context tasarrufu |
| 3 | **`StrReplaceFile` doğrudan dene.** Asistan çıktısı üzerinden değişiklik yapılır; gereksiz `ReadFile` önlenir. | %95 vakada başarılı |
| 4 | **Raw arşiv kopyası:** Kaynak dosya ingest edildiğinde `wiki/raw/articles/<filename>` yoluna kopyala (`cp` ile). | CONVENTIONS.md Section 6.1 |
| 5 | **Gereksiz `git status` tekrarlarından kaçın.** Tek kontrol yeterli. | Her komut bir tool call = token |

Detaylı komutlar ve kurallar: `references/WORKFLOW.md` ve `~/.kimi/skills/local-wiki/SKILL.md`  
Wiki bakım, büyüme kontrolü ve ortam bazlı yetki kuralları: `wiki/AGENTS.md`

---

## Push Komutu Protokolü (Zorunlu Wiki Ingest)

Kullanıcı "push yap" dediğinde:

1. `git status --short` → değişiklik özetini göster
2. **ZORUNLU:** `git status --short | grep -E "^wiki/"` → wiki değişikliği varsa wiki ingest çalıştır → `git add wiki/ && git commit -m "docs(wiki): ingest <proje>"`
3. Commit mesajı iste (`type(scope): description`)
4. `git add -A && git commit -m "..." && git push origin main`
5. `ops-bot/` veya `webimar/` dirty ise: **"Nested repo'ları da unutma!"**

**Nested Repo Hatırlatması:** `ops-bot/`, `projects/webimar/` ve `mathlock-play` (aynı dizinde ama ayrı repo) root repo'da `.gitignore`'dadır. Ayrı GitHub repo'larıdır. Kendi dizinlerinde ayrı commit + push yapılmalı.

---

## Proje Yapısı (Monorepo + Ayrı Repo'lar)

| Proje | Dizin | Repo | Deploy | AGENTS.md |
|-------|-------|------|--------|-----------|
| `ops-bot` | `ops-bot/` | Ayrı (`atlnatln/ops-bot`) | systemd | `ops-bot/AGENTS.md` |
| `webimar` | `projects/webimar/` | Ayrı (`atlnatln/webimar`) | Docker | `projects/webimar/AGENTS.md` |
| `mathlock-play` | `projects/mathlock-play/` | Ayrı (`atlnatln/mathlock-play`) | Play Store | `projects/mathlock-play/AGENTS.md` |
| `infrastructure` | `infrastructure/` | **local monorepo** | VPS Docker | `AGENTS.md` (root) |
| `wiki` | `wiki/` | **local monorepo** | — | `AGENTS.md` (root) |
| `scripts` | `scripts/` | **local monorepo** | — | `AGENTS.md` (root) |

```bash
# Tüm repo'ların durumunu tek komutla gör
bash scripts/repo-status.sh
```

> **Ayrı repo'lar:** `ops-bot` → `github.com/atlnatln/ops-bot` | `webimar` → `github.com/atlnatln/webimar` | `mathlock-play` → `github.com/atlnatln/mathlock-play`

Detaylı komutlar: `references/QUICKREF.md` | Wiki iş akışları: `references/WORKFLOW.md` | Wiki kuralları: `references/CONVENTIONS.md`

---

## Kod Stili ve Konvansiyonlar

- **Dosya adlandırma:** Shell `kebab-case.sh`, Python `snake_case.py`, Django app `snake_case`, React `PascalCase.tsx`
- **Git commit:** `type(scope): description` — örn. `feat(webimar): add endpoint`, `fix(ops-bot): timeout`, `docs(wiki): update guide`
- **Çevre değişkenleri:** `.env` asla commit'lenmez, `.env.example` güncel tutulur, hassas veriler sadece VPS `.env`'lerinde ve yerel `~/.env`'de
- `ops-bot` ve `webimar` için ayrı repo commit'leri, ardından `local` monorepo'ya commit
- **Her deploy öncesi commit**

---

## ACE Playbook Yükleme

Her oturum başında:
1. Genel playbook'u oku: `wiki/ace/playbook.md`
2. Proje playbook'unu oku (bulunduğun dizine göre):
   - `ops-bot/` içindeysem → `wiki/ace/ops-bot.md`
   - `projects/webimar/` içindeysem → `wiki/ace/webimar.md`
   - `projects/mathlock-play/` içindeysem → `wiki/ace/mathlock-play.md`
   - `projects/sayi-yolculugu/` içindeysem → `wiki/ace/sayi-yolculugu.md`
   - `projects/telegram-kimi/` içindeysem → `wiki/ace/telegram-kimi.md`
   - `projects/robotopia-android/` içindeysem → `wiki/ace/robotopia-android.md`
   - `infrastructure/` içindeysem → `wiki/ace/infrastructure.md`
   - Diğer tüm durumlar → sadece genel playbook
3. Playbook'teki dersleri uygula:
   - Confidence >= 0.70 olan dersleri **mutlaka** uygula
   - Confidence 0.50-0.69 olan dersleri **dikkatli** uygula
   - Confidence < 0.50 olan dersleri **göz ardı et** (eski olabilir)

---

## Kod Araştırması (Investigation)

Bir hatanın kökenini, bir API'nin kullanımını veya veri akışını anlamak için iki katman vardır:

### 1. Static Analiz (Kod yapısı)
**Birinci kaynak LSP'dir.** Sembol konumlandırma, cross-references ve tip bilgisi için:

```bash
scripts/wiki-assistant.py --locate --file <path> --symbol <name>
```

- **Go to definition:** Sembol nerede tanımlı
- **Find references:** Kimler çağırıyor
- **Hover / tip bilgisi:** Dokümantasyon ve tip çıkarımı
- **Workspace symbols:** Proje genelinde sembol arama

**LSP yetersiz kalırsa (reflection, generated kod, build hatası):** `Grep` ile full-text arama → `ReadFile` ile bağlam okuma

### 2. Runtime Analiz (Davranış)
LSP static analizdir, runtime'ı görmez. Crash, log veya network sorunlarında:

| Ortam | Araç | Örnek |
|-------|------|-------|
| Android | `adb logcat`, `adb shell dumpsys` | ACRA init logu, ANR trace |
| Backend | `journalctl`, `docker logs` | Django traceback, 5xx hatası |
| Network | `curl`, browser devtools | API timeout, 403/500 |
| DB | `psql`, `redis-cli`, Django shell | Query performansı, race condition |

> **Kural:** Runtime sorununda önce log/veri topla, sonra kodu oku. Tersi yapılırsa LSP "kod doğru görünüyor" dediği halde uygulama çöküyor olabilir.

---

## Kod Düzenleme Prensibi

Kod düzenleme isteklerinde (fonksiyon ekleme, değiştirme, refactor):
1. `scripts/wiki-assistant.py --locate --file <path> --symbol <name>` ile sembol konumunu bul
2. Kimi sadece ilgili satır aralığını (`range`) okur, `snippet` ile bağlam alır
3. Değişiklik `StrReplaceFile` ile uygulanır
4. İlgili wiki sayfası otomatik güncellenir (`wiki-assistant.py --prepare`)

**Desteklenen diller:** Python (Pyright) ✅ | JS/TS (TypeScript Server) ✅ | Kotlin ✅ | Java (JDTLS gerek yok — 0 kaynak dosya)

---

## Güvenlik Notları

- **sudo şifresi:** Kullanıcıya sor (sadece yerel, VPS'te sudoers var)
- **SSH key:** `~/.ssh/id_ed25519`
- **API Key'ler:** `.env` dosyalarında, asla commit'lenmez
- **SSL:** Let's Encrypt, otomatik yenileme
- **sec-agent:** `ops-bot/sec-agent/` — 3 dk'da bir sweep

---

> **Son güncelleme:** 2026-05-30
> **Wiki durumu:** 10 proje ingest edildi, 10/10 lint passing
> **VPS durumu:** ops-bot ✅, sec-agent ✅, telegram-kimi ✅, webimar ✅, mathlock-play ✅
> **GitHub:** `github.com:atlnatln/local.git`
