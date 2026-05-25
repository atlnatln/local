# Oluşturulan aidlc-docs/ Referansı

AI-DLC iş akışını çalıştırdığınızda, tüm dokümantasyon yapıtları çalışma alanınızın kökündeki bir `aidlc-docs/` dizini içinde oluşturulur. Oluşturulan tam dosyalar proje türünüze (greenfield veya brownfield), karmaşıklığa ve iş akışının yürüttüğü veya atladığı aşamalara bağlıdır.

Aşağıda, tüm olası aşama ve evrelerdeki her dosyayı gösteren tam olarak doldurulmuş yapı yer almaktadır. Koşullu dosyalar, ne zaman göründüklerini belirten notlarla açıklanmıştır.

```text
aidlc-docs/
├── aidlc-state.md                                          # İş akışı durum izleyici — proje bilgisi, aşama ilerlemesi, mevcut durum
├── audit.md                                                # Tam denetim izi — her kullanıcı girdisi, yapay zeka yanıtı ve onay, zaman damgalarıyla
│
├── inception/                                              # 🔵 BAŞLANGIÇ AŞAMASI — NE inşa edileceğini ve NEDEN belirler
│   ├── plans/
│   │   ├── execution-plan.md                               # İş akışı görselleştirme ve aşama yürütme kararları (her zaman oluşturulur)
│   │   ├── story-generation-plan.md                        # Hikaye geliştirme metodolojisi ve soruları (Kullanıcı Hikayeleri yürütülürse)
│   │   ├── user-stories-assessment.md                      # Kullanıcı hikayelerinin değer katıp katmadığının değerlendirmesi (Kullanıcı Hikayeleri yürütülürse)
│   │   ├── application-design-plan.md                      # Bileşen ve servis tasarım planı, sorularıyla (Uygulama Tasarımı yürütülürse)
│   │   └── unit-of-work-plan.md                            # Sistem ayrıştırma planı, sorularıyla (İş Birimi Oluşturma yürütülürse)
│   │
│   ├── reverse-engineering/                                # Yalnızca brownfield projeler için oluşturulur (mevcut kod tabanı algılandığında)
│   │   ├── business-overview.md                            # İş bağlamı, işlemler ve sözlük
│   │   ├── architecture.md                                 # Sistem mimarisi diyagramları, bileşen açıklamaları, veri akışı
│   │   ├── code-structure.md                               # Derleme sistemi, temel sınıflar/modüller, tasarım kalıpları, dosya envanteri
│   │   ├── api-documentation.md                            # REST API'ler, dahili API'ler ve veri modelleri
│   │   ├── component-inventory.md                          # Türüne göre tüm paketlerin envanteri (uygulama, altyapı, paylaşılan, test)
│   │   ├── technology-stack.md                             # Diller, çerçeveler, altyapı, derleme araçları, test araçları
│   │   ├── dependencies.md                                 # Dahili ve harici bağımlılık grafikleri ve ilişkileri
│   │   ├── code-quality-assessment.md                      # Test kapsamı, kod kalite göstergeleri, teknik borç, kalıplar
│   │   └── reverse-engineering-timestamp.md                # Analiz meta verileri ve yapıt kontrol listesi
│   │
│   ├── requirements/
│   │   ├── requirements.md                                 # Amaç analiziyle birlikte fonksiyonel ve fonksiyonel olmayan gereksinimler (her zaman oluşturulur)
│   │   └── requirement-verification-questions.md           # Kullanıcı girdisi için [Cevap]: etiketleriyle açıklayıcı sorular (her zaman oluşturulur)
│   │
│   ├── user-stories/                                       # Yalnızca Kullanıcı Hikayeleri aşaması yürütülürse oluşturulur
│   │   ├── stories.md                                      # INVEST kriterlerine uygun kullanıcı hikayeleri, kabul kriterleriyle
│   │   └── personas.md                                     # Kullanık arketipleri, özellikleri ve persona-hikaye eşleştirmeleri
│   │
│   └── application-design/                                 # Yalnızca Uygulama Tasarımı ve/veya İş Birimi Oluşturma yürütülürse oluşturulur
│       ├── application-design.md                           # Birleştirilmiş tasarım belgesi (Uygulama Tasarımı yürütülürse)
│       ├── components.md                                   # Bileşen tanımları, sorumlulukları ve arayüzleri
│       ├── component-methods.md                            # Yöntem imzaları, amaçları ve girdi/çıktı türleri
│       ├── services.md                                     # Servis tanımları, sorumlulukları ve orkestrasyon kalıpları
│       ├── component-dependency.md                         # Bileşenler arası bağımlılık matrisi ve iletişim kalıpları
│       ├── unit-of-work.md                                 # Birim tanımları ve sorumlulukları (İş Birimi Oluşturma yürütülürse)
│       ├── unit-of-work-dependency.md                      # Birimler arası bağımlılık matrisi (İş Birimi Oluşturma yürütülürse)
│       └── unit-of-work-story-map.md                       # Kullanıcı hikayelerinin birimlere eşlenmesi (İş Birimi Oluşturma yürütülürse)
│
├── construction/                                           # 🟢 YAPIM AŞAMASI — NASIL inşa edileceğini belirler
│   ├── plans/
│   │   ├── {birim-adı}-functional-design-plan.md           # İş mantığı tasarım planı, sorularıyla (birim başına, Fonksiyonel Tasarım yürütülürse)
│   │   ├── {birim-adı}-nfr-requirements-plan.md            # NFR değerlendirme planı, sorularıyla (birim başına, NFR Gereksinimleri yürütülürse)
│   │   ├── {birim-adı}-nfr-design-plan.md                  # NFR tasarım kalıpları planı, sorularıyla (birim başına, NFR Tasarımı yürütülürse)
│   │   ├── {birim-adı}-infrastructure-design-plan.md       # Altyapı eşleme planı, sorularıyla (birim başına, Altyapı Tasarımı yürütülürse)
│   │   └── {birim-adı}-code-generation-plan.md             # Ayrıntılı kod oluşturma adımları, onay kutularıyla (birim başına, her zaman oluşturulur)
│   │
│   ├── {birim-adı}/                                        # Birim başına yapıtlar — her iş birimi için bir dizin
│   │   ├── functional-design/                              # Yalnızca bu birim için Fonksiyonel Tasarım yürütülürse oluşturulur
│   │   │   ├── business-logic-model.md                     # Ayrıntılı iş mantığı ve algoritmalar
│   │   │   ├── business-rules.md                           # İş kuralları, doğrulama mantığı ve kısıtlamalar
│   │   │   ├── domain-entities.md                          # Varlıklar ve ilişkileriyle birlikte domain modelleri
│   │   │   └── frontend-components.md                      # UI bileşen hiyerarşisi, özellikler, durum, etkileşimler (birim ön uca sahipse)
│   │   │
│   │   ├── nfr-requirements/                               # Yalnızca bu birim için NFR Gereksinimleri yürütülürse oluşturulur
│   │   │   ├── nfr-requirements.md                         # Ölçeklenebilirlik, performans, kullanılabilirlik, güvenlik gereksinimleri
│   │   │   └── tech-stack-decisions.md                     # Teknoloji seçimleri ve gerekçeleri
│   │   │
│   │   ├── nfr-design/                                     # Yalnızca bu birim için NFR Tasarımı yürütülürse oluşturulur
│   │   │   ├── nfr-design-patterns.md                      # Dayanıklılık, ölçeklenebilirlik, performans ve güvenlik kalıpları
│   │   │   └── logical-components.md                       # Mantıksal altyapı bileşenleri (kuyruklar, önbellekler, vb.)
│   │   │
│   │   ├── infrastructure-design/                          # Yalnızca bu birim için Altyapı Tasarımı yürütülürse oluşturulur
│   │   │   ├── infrastructure-design.md                    # Bulut servis eşleştirmeleri ve altyapı bileşenleri
│   │   │   └── deployment-architecture.md                  # Dağıtım modeli, ağ, ölçeklendirme yapılandırması
│   │   │
│   │   └── code/                                           # Oluşturulan kodun markdown özetleri (birim başına her zaman oluşturulur)
│   │       └── *.md                                        # Kod oluşturma özetleri (gerçek kod çalışma alanı köküne gider)
│   │
│   ├── shared-infrastructure.md                            # Birimler arası paylaşılan altyapı (uygulanabilirse)
│   │
│   └── build-and-test/                                     # Tüm birimler kod oluşturmayı tamamladıktan sonra her zaman oluşturulur
│       ├── build-instructions.md                           # Ön koşullar, derleme adımları, sorun giderme
│       ├── unit-test-instructions.md                       # Birim testi yürütme komutları ve beklenen sonuçlar
│       ├── integration-test-instructions.md                # Entegrasyon test senaryoları, kurulum ve yürütme
│       ├── performance-test-instructions.md                # Yük/stres testi yapılandırma ve yürütme (performans NFR'leri varsa)
│       ├── contract-test-instructions.md                   # Servisler arası API sözleşme doğrulama (mikroservislerse)
│       ├── security-test-instructions.md                   # Güvenlik açığı tarama ve güvenlik testi (güvenlik NFR'leri varsa)
│       ├── e2e-test-instructions.md                        # Uçtan uca kullanıcı iş akışı testi (uygulanabilirse)
│       └── build-and-test-summary.md                       # Genel derleme durumu, test sonuçları ve hazır olma değerlendirmesi
│
└── operations/                                             # 🟡 OPERASYONLAR AŞAMASI — gelecekteki genişletme için yer tutucu
```

## Notlar

- `{birim-adı}`, gerçek birim adıyla değiştirilir (örn. `api-service`, `frontend-app`, `data-processor`). Tek birimli projeler için `construction/` altında tipik olarak bir birim dizini vardır.
- Daha basit tek birimli projeler için model isimlendirmeyi basitleştirebilir — örneğin, `construction/plans/{birim-adı}-code-generation-plan.md` yerine `construction/plans/code-generation-plan.md`, veya bireysel bileşen dosyaları olmadan tek birleştirilmiş dosya olarak `application-design.md`.
- `build-and-test/` dizini her zaman `build-and-test-summary.md` içerir. Bireysel talimat dosyaları (`build-instructions.md`, `unit-test-instructions.md`, `integration-test-instructions.md`, vb.) proje karmaşıklığına ve test ihtiyaçlarına göre oluşturulur.
- `inception/plans/` ve `construction/plans/` altındaki planlar, kullanıcı girdisinin sağlandığı `[Cevap]:` etiketleri ve yürütme ilerlemesini izleyen `[ ]`/`[x]` onay kutuları içerir.
- Uygulama kodu asla `aidlc-docs/` içine konmaz — çalışma alanı köküne gider. Burada yalnızca markdown dokümantasyonu yaşar.
- `audit.md` dosyası yalnızca ekleme yapılabilir (append-only) ve her etkileşimi ISO 8601 zaman damgalarıyla kaydeder.
- `aidlc-state.md` dosyası, hangi aşamaların tamamlandığını, atlandığını veya devam ettiğini, uzantı yapılandırmasıyla birlikte izler.
