# AI-DLC İş Akışları Değerlendirme ve Raporlama Çerçevesi

[AI-DLC iş akışları](https://github.com/awslabs/aidlc-workflows) deposundaki değişiklikleri doğrulamak için otomatik test ve raporlama çerçevesi.

## Genel Bakış

Bu çerçeve altı ana çalışma akışı ("ana yapı taşları") etrafında düzenlenmiştir:

1. **Altın Test Vakası** — Tüm değerlendirmeler için referans girdiler olarak kullanılan, özenle hazırlanmış temel test vakaları (AIDLC dokümanları + kod çıktısı)
2. **Yürütme Çerçevesi** — Test vakalarını değerlendirme hattından geçiren temel orkestrasyon
3. **Anlamsal Değerlendirme** — Çıktı doğruluğu, bütünlüğü ve uygunluğunun yapay zeka tabanlı değerlendirmesi (belirleyicilik dışı sonuçlar için @k olarak raporlanır)
4. **Kod Değerlendirmesi** — Üretilen kodun statik analizi (linting, güvenlik taraması, kopya tespiti)
5. **NFR Değerlendirmesi** — İşlevsel olmayan gereksinimler testi (token tüketimi, yürütme süresi, çapraz model tutarlılığı)
6. **GitHub CI/CD Entegrasyonu ve Yönetimi** — PR'lerde değerlendirmeleri tetikleyen ve raporları ekleyen otomatik hatlar

## Hızlı Başlangıç

```bash
# Bağımlılıkları yükle
uv sync

# Tüm birim testlerini çalıştır
uv run python run.py test
# Not: Windows'ta test_run_command.py içindeki 7 testin başarısız olması beklenir
# çünkü Unix kabuk komutlarını (echo, exit, sleep vb.) kullanırlar ve bunlar Windows'ta mevcut değildir.

# Sandbox docker imajını derle
./docker/sandbox/build.sh

# Tam hat: AIDLC iş akışını yürüt + değerlendir + raporla (Bedrock gerekli, varsayılanlarla)
uv run python run.py full

# Tam hat: AIDLC iş akışını yürüt + değerlendir + raporla (Bedrock gerekli)
uv run python run.py full \
    --vision test_cases/sci-calc/vision.md \
    --tech-env test_cases/sci-calc/tech-env.md \
    --golden test_cases/sci-calc/golden-aidlc-docs \
    --openapi test_cases/sci-calc/openapi.yaml

# Mevcut bir çalışmayı değerlendir (yürütmeyi atla, sadece Bedrock ile puanla)
uv run python run.py full \
    --evaluate-only runs/<run-folder>/aidlc-docs \
    --golden test_cases/sci-calc/golden-aidlc-docs \
    --openapi test_cases/sci-calc/openapi.yaml
```

## Değerlendirme Hattı

Değerlendirme hattı (`run.py full` veya `scripts/run_evaluation.py`) altı aşamayı orkestralar:

| Aşama              | Paket                    | Açıklama                                                     |
| ------------------ | ------------------------ | ------------------------------------------------------------ |
| 1. Yürütme         | `packages/execution`     | AIDLC iki-agent iş akışını çalıştırarak doküman + kod üretir |
| 2. Çalışma Sonrası | (yürütme içinde)         | Bağımlılıkları yükler ve üretilen projenin testlerini çalıştırır |
| 3. Nicel           | `packages/quantitative`  | Üretilen kodu lintler, güvenlik tarar ve kopya kontrolü yapar |
| 4. Kontrat         | `packages/contracttest`  | Üretilen uygulamayı ayağa kaldırır ve API uç noktalarını doğrular |
| 5. Nitel           | `packages/qualitative`   | Bedrock LLM ile üretilen dokümanları altın temel hatla karşılaştırır |
| 6. Rapor           | `packages/reporting`     | Birleştirilmiş Markdown + HTML raporları oluşturur           |

Her çalıştırmanın çıktısı `runs/` altında zaman damgalı bir klasöre yazılır:

```txt
runs/<timestamp>/
  ├── aidlc-docs/                    # AIDLC iş akışı dokümanları
  ├── workspace/                     # Üretilen uygulama kodu
  ├── run-meta.yaml                  # Çalıştırma kimliği + yapılandırma
  ├── run-metrics.yaml               # Token'lar, zamanlama, yapıtlar, hatalar
  ├── test-results.yaml              # Çalışma sonrası test çıktısı
  ├── quality-report.yaml            # Lint + güvenlik + kopya bulguları
  ├── contract-test-results.yaml     # API uç noktası doğrulaması
  ├── qualitative-comparison.yaml    # Anlamsal puanlama
  ├── evaluation-config.yaml         # Tam çözümlenmiş yapılandırma anlık görüntüsü
  ├── report.md                      # Birleştirilmiş Markdown raporu
  └── report.html                    # Birleştirilmiş HTML raporu
```

## Yapılandırma

### Yapılandırma dosyası (`config/default.yaml`)

Ana yapılandırma dosyası AWS ayarlarını, modelleri, swarm parametrelerini, zaman aşımlarını ve araç yollarını kontrol eder. Varsayılanları değiştirmek için bu dosyayı düzenleyin veya özel bir yapılandırmayı `--config` ile iletin:

```yaml
aws:
  profile: "default"
  region: "us-east-1"

models:
  executor:
    provider: "bedrock"
    model_id: "global.anthropic.claude-opus-4-6-v1"
  simulator:
    provider: "bedrock"
    model_id: "global.anthropic.claude-opus-4-6-v1"
  scorer:
    provider: "bedrock"
    model_id: "global.anthropic.claude-opus-4-6-v1"

aidlc:
  rules_source: "git"   # "git" veya "local"
  rules_repo: "https://github.com/awslabs/aidlc-workflows.git"
  rules_ref: "main"
  rules_local_path: null

swarm:
  max_handoffs: 200
  max_iterations: 200
  execution_timeout: 14400
  node_timeout: 3600

runs:
  output_dir: "./runs"

execution:
  enabled: true
  command_timeout: 120
  post_run_tests: true
  post_run_timeout: 300

execution:
  sandbox:
    enabled: true
    image: aidlc-sandbox:latest
    memory: 2g
    cpus: 2

tools:
  pmd_path: null   # PMD çalıştırılabilir dosyasının yolu; null ise PATH'te 'pmd' arar
```

Öncelik: `CLI bayrakları > YAML yapılandırması > yerleşik varsayılanlar`

### Model-özel yapılandırmalar

`config/` içindeki model bazlı yapılandırma dosyaları, yürütücü modelini geçersiz kılarken `default.yaml`'den diğer her şeyi miras alır:

| Dosya                         | Model                                       |
| ----------------------------- | ------------------------------------------- |
| `config/opus-4-6.yaml`        | Claude Opus 4.6                             |
| `config/opus-4-5.yaml`        | Claude Opus 4.5                             |
| `config/sonnet-4-6.yaml`      | Claude Sonnet 4.6                           |
| `config/sonnet-4-5.yaml`      | Claude Sonnet 4.5                           |
| `config/nova-premier.yaml`    | Amazon Nova Premier                         |
| `config/nova-pro.yaml`        | Amazon Nova Pro                             |
| `config/nova-lite.yaml`       | Amazon Nova Lite                            |
| `config/mistral-large-3.yaml` | Mistral Large 3 (675B)                      |
| `config/devstral-2.yaml`      | Mistral Devstral 2 (123B, kod-uzmanlaşmış)  |

### Docker Sandbox

Değerlendirme çerçevesi, güvenilmeyen kodun ana bilgisayarı etkilemesini önlemek için AI tarafından üretilen kodu yalıtılmış bir Docker konteynerinde çalıştırır. Sandbox imajı; Python 3.13 + uv, Node.js 22 + npm ve yaygın derleme araçlarını içerir ve root olmayan bir kullanıcı olarak çalışır.

#### Ön Koşullar

Docker'ın ana makinede kurulu ve çalışıyor olması gerekir.

#### Sandbox imajını derleme

```bash
# İmajı derle (bir kez kurulum veya Dockerfile değişikliklerinden sonra)
./docker/sandbox/build.sh

# Veya manuel olarak derle
docker build -t aidlc-sandbox:latest docker/sandbox/
```

Bu, varsayılan yapılandırmada referans alınan `aidlc-sandbox:latest` imajını üretir.

#### Yapılandırma

Sandbox ayarları `config/default.yaml` dosyasında `execution.sandbox` altındadır:

```yaml
execution:
  sandbox:
    enabled: true                # Üretilen kodu doğrudan ana bilgisayarda çalıştırmak için false yapın
    image: aidlc-sandbox:latest  # Docker imaj adı (önce derlenmelidir)
    memory: 2g                   # Konteyner bellek sınırı
    cpus: 2                      # Konteyner CPU sınırı
```

Sandbox etkinleştirildiğinde, çalışma sonrası testler (aşama 2) ve kontrat test sunucuları (aşama 4) konteyner içinde yürütülür. Üretilen `workspace/` dizini konteynerde `/workspace` olarak bağlanır. Docker kullanılamıyorsa veya `enabled` `false` olarak ayarlandıysa, komutlar doğrudan ana bilgisayarda çalışır.

### Araç yapılandırması

**PMD (kod kopyası tespiti):** PMD CPD, aşama 3'te kopyala-yapıştır tespiti için kullanılır. Yolu `config/default.yaml`'de yapılandırın:

```yaml
tools:
  pmd_path: /path/to/pmd    # PMD çalıştırılabilir dosyasının mutlak yolu
  # pmd_path: null           # null = otomatik olarak PATH'te ara
```

PMD bulunamazsa, kopya analizi bir notla atlanır — değerlendirmeyi başarısız yapmaz.

### Hat CLI bayrakları

```bash
uv run python run.py full \
    --vision test_cases/sci-calc/vision.md \
    --tech-env test_cases/sci-calc/tech-env.md \
    --golden test_cases/sci-calc/golden-aidlc-docs \
    --openapi test_cases/sci-calc/openapi.yaml \
    --config config/default.yaml \
    --profile my-aws-profile \
    --region us-west-2 \
    --executor-model global.anthropic.claude-opus-4-6-v1 \
    --scorer-model us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --report-format both
```

Desteklenen bayraklar:

- `--config` — YAML yapılandırma dosyasının yolu (varsayılan: `config/default.yaml`)
- `--test` — sadece birim testlerini çalıştır
- `--vision`, `--tech-env` — yürütme girdileri
- `--evaluate-only` — yürütmeyi yeniden çalıştırmadan mevcut bir `aidlc-docs` klasörünü puanla
- `--golden` — referans temel hat dokümanları dizini
- `--openapi` — kontrat test spesifikasyonu
- `--report-format` — `markdown`, `html` veya `both`
- `--baseline` — `golden.yaml`'ın yolunu geçersiz kıl (aksi takdirde `--golden`'ın yanında otomatik bulunur)
- `--output-dir` — çalıştırma çıktı klasörünü geçersiz kıl
- `--results` — niteliksel sonuçları YAML'i özel bir yola yaz
- `--profile`, `--region` — Bedrock için AWS kimlik bilgileri/bölge
- `--executor-model` — yürütme modeli geçersiz kılması
- `--scorer-model` — niteliksel puanlama modeli geçersiz kılması
- `--rules-ref` — AIDLC kuralları için git ref (dal/etiket/commit)

## Toplu Değerlendirme

Değerlendirme hattını birden fazla Bedrock modeli üzerinde sırayla çalıştırın, ardından çapraz model karşılaştırma raporu oluşturun.

### Mevcut modelleri listele

```bash
uv run python run.py batch --list
```

### Toplu değerlendirmeyi çalıştır

```bash
# Tüm yapılandırılmış modelleri çalıştır
uv run python run.py batch --models all

# Belirli modelleri çalıştır (isimler config/ içindeki yapılandırma dosyası kök adlarıyla eşleşir)
uv run python run.py batch --models nova-pro,sonnet-4-5

# AWS ayarlarını geçersiz kıl
uv run python run.py batch --models all \
    --profile my-aws-profile \
    --region us-east-1
```

Her model çalıştırması `runs/<model-name>/` altında tam değerlendirme yapıtlarıyla saklanır. Bir `batch-summary.yaml`, her model için zamanlama ve geçme/başarısız durumuyla çalıştırmalar dizinine yazılır.

### Çapraz model karşılaştırması oluştur

Toplu değerlendirme tamamlandıktan sonra karşılaştırma matrisi oluşturun:

```bash
# runs/ altındaki tüm model çalıştırmalarını karşılaştır
uv run python run.py compare

# Belirli modelleri altın temel hatla karşılaştır
uv run python run.py compare \
    --models nova-pro,sonnet-4-5 \
    --baseline test_cases/sci-calc/golden.yaml
```

Bu, tüm modeller arasında yan yana metrikler (birim testleri, kontrat testleri, kod kalitesi, niteliksel puanlar, token kullanımı ve zamanlama) içeren `runs/comparison/comparison-report.md` ve `runs/comparison/comparison-data.yaml` üretir.

## CLI Değerlendirmesi

AIDLC değerlendirmesini CLI tabanlı yapay zeka asistanları (Claude Code, Kiro CLI) üzerinden CLI bağdaştırıcısı (`packages/cli-harness`) kullanarak çalıştırın.

### Mevcut bağdaştırıcıları listele

```bash
uv run python run.py cli --list
```

Desteklenen bağdaştırıcılar: `claude-code`, `kiro-cli`.

### CLI değerlendirmesini çalıştır

```bash
# Claude Code üzerinden değerlendirme çalıştır
uv run python run.py cli --cli claude-code \
    --vision test_cases/sci-calc/vision.md \
    --golden test_cases/sci-calc/golden-aidlc-docs

# Belirli bir model ile Kiro CLI üzerinden çalıştır
uv run python run.py cli --cli kiro-cli \
    --vision test_cases/sci-calc/vision.md \
    --golden test_cases/sci-calc/golden-aidlc-docs \
    --model claude-sonnet-4

# Bir bağdaştırıcı için ön koşulları kontrol et
uv run python run.py cli --cli claude-code --check-only
```

Çıktı `runs/<cli-name>-<timestamp>-<uuid>/` altına yazılır. CLI bağdaştırıcısı bağdaştırıcıyı çalıştırır, ardından puanlama için (aşamalar 2–6) `scripts/run_evaluation.py --evaluate-only` çağrır.

## IDE Değerlendirmesi

AIDLC değerlendirmesini üçüncü taraf IDE yapay zeka asistanları üzerinden IDE bağdaştırıcısı (`packages/ide-harness`) kullanarak çalıştırın.

### Mevcut bağdaştırıcıları listele

```bash
uv run python run.py ide --list
```

Desteklenen bağdaştırıcılar: Cursor, Cline, Copilot, Kiro, Windsurf, Antigravity.

### IDE değerlendirmesini çalıştır

```bash
# Cursor üzerinden değerlendirme çalıştır
uv run python run.py ide --ide cursor \
    --vision test_cases/sci-calc/vision.md \
    --golden test_cases/sci-calc/golden-aidlc-docs

# Bir IDE bağdaştırıcısı için ön koşulları kontrol et
uv run python run.py ide --ide kiro --check-only
```

Çıktı `runs/ide-<adapter-name>/` altına yazılır.

## Eklenti Kancası Testi

AIDLC iş akışını farklı kurallar eklenti yapılandırmalarıyla test edin. Eklenti kancası özelliği, katılım isteğine bağlı sorular temelinde uzantıların (güvenlik, performans, gözlenebilirlik) aşamalı olarak yüklenmesine olanak tanır.

```bash
# Mevcut eklenti yapılandırmalarını listele
uv run python run.py ext-test --list-configs

# Standart testi çalıştır (tüm uzantılar vs uzantı yok)
uv run python run.py ext-test --scenario sci-calc

# Eklenti desteği olan belirli bir kurallar dalı kullan
uv run python run.py ext-test --scenario sci-calc \
    --rules-ref feat/extension_hook_question_split
```

Bu, değerlendirmeyi iki kez çalıştırır:

1. Tüm eklenti katılımları "EVET" olarak yanıtlanmış (maksimum rehberlik)
2. Tüm eklenti katılımları "HAYIR" olarak yanıtlanmış (sadece temel hat)

Sonuçlar, farklı eklenti yapılandırmalarının etkisini gösteren bir karşılaştırma raporuyla `runs/<scenario>/extension-test/` altına kaydedilir.

Ayrıntılı dokümantasyon için [Eklenti Kancası Test Kılavuzu](./docs/extension-hook-testing.md)'na bakın.

## Trend Raporlaması

Zaman içinde değerlendirme metriklerini izleyen çapraz sürüm trend raporları oluşturun. Değerlendirme paketlerini GitHub sürümlerinden ve Actions yapıtlarından getirir, ardından HTML, Markdown ve YAML raporları oluşturur.

```bash
# Trend raporu oluştur (kimliği doğrulanmış gh CLI gerekli)
uv run python run.py trend --baseline test_cases/sci-calc/golden.yaml

# Sadece HTML, ayrıntılı çıktı ile
uv run python run.py trend --baseline test_cases/sci-calc/golden.yaml --format html -v

# Yerel değerlendirme paketlerini dahil et
uv run python run.py trend --baseline test_cases/sci-calc/golden.yaml \
    --local-bundle runs/my-run/report.zip

# Kapı modu (gerilemede sıfır dışı çıkış)
uv run python run.py trend --baseline test_cases/sci-calc/golden.yaml --gate
```

HTML yönetici özeti altı metrik kartı görüntüler:

- **Niteliksel Puan** — altın temel hata karşı anlamsal kalite (yüksek daha iyi)
- **Kontrat Testleri** — geçen/toplam olarak API geçme oranı (yüksek daha iyi)
- **Birim Testleri** — yüzde olarak gösterilen geçme oranı (yüksek daha iyi)
- **Lint Bulguları** — statik analiz sorunları (düşük daha iyi)
- **Yürütme Süresi** — oluşturma süresi (düşük daha iyi)
- **Toplam Token** — LLM token tüketimi (düşük daha iyi)

Çıktı, çıktı dizini altında (varsayılan: `runs/`) zaman damgalı bir klasöre yazılır.

Örnek bir HTML raporu [`packages/trend-reports/examples/trend-report.html`](./packages/trend-reports/examples/trend-report.html) adresinde mevcuttur.

## Yürütme Bileşenini Doğrudan Çalıştırma

Tam yürütme düzeyinde kontroller için `aidlc-runner`'ı doğrudan çalıştırabilirsiniz:

```bash
uv run aidlc-runner \
    --vision test_cases/sci-calc/vision.md \
    --tech-env test_cases/sci-calc/tech-env.md \
    --config config/default.yaml \
    --aws-profile my-aws-profile \
    --aws-region us-west-2 \
    --executor-model global.anthropic.claude-opus-4-6-v1 \
    --simulator-model us.anthropic.claude-sonnet-4-5-20250929-v1:0 \
    --output-dir ./runs
```

Yürütme-özel anahtarlar:

- `--rules-path <local-rules-dir>` — yerel kurallar kaynağını zorlar
- `--no-exec` — iş akışı içi komut yürütmeyi devre dışı bırak
- `--no-post-tests` — çalışma sonrası testleri devre dışı bırak

## Depo Yapısı

```txt
.
├── run.py                     # Ana giriş noktası — değerlendirme modlarına yönlendirir
├── scripts/                   # Uzmanlaşmış çalıştırma betikleri
│   ├── run_evaluation.py      # Tek model değerlendirme hattı
│   ├── run_batch_evaluation.py    # Çok model toplu değerlendirme
│   ├── run_comparison_report.py   # Çapraz model karşılaştırma raporu oluşturucu
│   ├── run_cli_evaluation.py      # CLI bağdaştırıcı değerlendirme çalıştırıcısı
│   ├── run_ide_evaluation.py      # IDE bağdaştırıcı değerlendirme çalıştırıcısı
│   ├── run_extension_test.py      # Eklenti kancası testi (katılım yapılandırmaları)
│   ├── run_trend_report.py        # Çapraz sürüm trend raporu oluşturma
│   └── README.md              # Betikler dokümantasyonu
├── config/
│   ├── default.yaml           # Varsayılan yapılandırma (modeller, AWS, zaman aşımları, araçlar)
│   ├── nova-premier.yaml      # Amazon Nova Premier yürütücü geçersiz kılması
│   ├── nova-pro.yaml          # Amazon Nova Pro yürütücü geçersiz kılması
│   ├── sonnet-4-5.yaml        # Claude Sonnet 4.5 yürütücü geçersiz kılması
│   └── sonnet-4-6.yaml        # Claude Sonnet 4.6 yürütücü geçersiz kılması
├── packages/
│   ├── execution/             # AIDLC iş akışı çalıştırıcısı (iki-agent Strands orkestratörü)
│   ├── qualitative/           # Anlamsal değerlendirme — Bedrock ile niyet ve tasarım benzerliği
│   ├── quantitative/          # Kod değerlendirmesi — linting, güvenlik, kopya (PMD CPD)
│   ├── contracttest/          # OpenAPI spesifikasyonlarına karşı API kontrat testi
│   ├── nonfunctional/         # NFR değerlendirmesi — token'lar, zamanlama, tutarlılık
│   ├── reporting/             # Birleştirilmiş rapor oluşturma (Markdown + HTML)
│   ├── trend-reports/         # Çapraz sürüm trend raporlaması (HTML, Markdown, YAML)
│   ├── cli-harness/           # CLI bağdaştırıcı çerçevesi (Claude Code, Kiro CLI)
│   ├── ide-harness/           # IDE bağdaştırıcı çerçevesi (Cursor, Cline, Kiro, vb.)
│   └── shared/                # Ortak yardımcı programlar
├── test_cases/                # Altın test vakaları (vision + tech-env + golden aidlc-docs)
├── runs/                      # Çalıştırma çıktı klasörleri (değerlendirme başına bir tane)
├── docker/
│   └── sandbox/               # Yalıtılmış yürütme için Dockerfile + derleme betiği
├── docs/                      # Ek dokümantasyon
│   ├── extension-hook-testing.md  # Eklenti kancası test kılavuzu
│   ├── ide-harness-design.md      # IDE bağdaştırıcı mimarisi
│   └── file-structure.md          # Proje dosya organizasyonu referansı
├── pyproject.toml             # Çalışma alanı yapılandırması
└── uv.lock                    # Bağımlılık kilit dosyası
```

## Dokümantasyon

- [SSS](./FAQ.md) — Sık sorulan sorular ve yanıtlar
- [Katkıda Bulunma](./CONTRIBUTING.md) — Değişiklik gönderme kuralları
- [Mimari](./ARCHITECTURE.md) — Sistem tasarımı ve uygulama detayları
- [Eklenti Kancası Testi](./docs/extension-hook-testing.md) — AIDLC'yi farklı eklenti yapılandırmalarıyla test etme
- [IDE Bağdaştırıcı Tasarımı](./docs/ide-harness-design.md) — IDE bağdaştırıcı çerçevesinin mimarisi
- [Dosya Yapısı](./docs/file-structure.md) — Proje dosya organizasyonu referansı

## Katkıda Bulunma

Değişiklik gönderme kuralları için [CONTRIBUTING.md](./CONTRIBUTING.md)'ye bakın.

## Lisans

[Lisans bilgisi eklenecek]
