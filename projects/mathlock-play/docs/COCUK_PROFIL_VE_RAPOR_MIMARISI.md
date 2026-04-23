# MathLock — Çoklu Çocuk Profili, Eğitim Dönemi & Ebeveyn Rapor Mimarisi

Oluşturulma: 18 Nisan 2026
Son güncelleme: 18 Nisan 2026

## İmplementasyon Durumu

| Bileşen | Durum | Notlar |
|---------|-------|--------|
| Müfredat JSON dosyaları (`agents/curriculum/`) | ✅ Tamamlandı | 5 dönem tanımlandı |
| Dönem bazlı agent dosyaları (`agents/questions-*.agents.md`) | ✅ Tamamlandı | 4 yeni + mevcut sinif_2 |
| Backend model değişiklikleri + migration | ✅ Tamamlandı | `0004_childprofile_education_period_and_more.py` |
| Backend API endpoint'leri (children/, detail/, report/) | ✅ Tamamlandı | `urls.py` + `views.py` |
| `ai-generate.sh` `--period` desteği | ✅ Tamamlandı | Dönem bazlı agent swap + prompt |
| `validate-questions.py` dönem desteği | ✅ Tamamlandı | `--period` flag, değişken soru sayısı, yeni tipler |
| Android `ChildProfilesActivity` | ✅ Tamamlandı | CRUD + aktif profil seçimi |
| Android `PreferenceManager` güncelleme | ✅ Tamamlandı | `activeChildId`, `activeEducationPeriod` |
| SettingsActivity "Çocuk Profilleri" kartı | ✅ Tamamlandı | Kart + navigasyon |
| PostgreSQL kalıcı DB (named volume) | ✅ Tamamlandı | `docker-compose.yml` + `.env.example` |
| AI rapor üretimi (report.json) | ✅ Tamamlandı | Agent §14 + ai-generate.sh sync |
| QuestionManager profil entegrasyonu | ✅ Tamamlandı | `child_id` parametresi API isteklerinde |
| StatsTracker profil + süre takibi | ✅ Tamamlandı | `childId`, `educationPeriod`, session timer |
| İstatistik dashboard (grafik/tablo) | ✅ Tamamlandı | StatsDashboardActivity + MPAndroidChart |

## 1. Genel Bakış

Bu doküman şu özelliklerin MathLock'a eklenmesini planlar:

1. **Eğitim dönemi seçimi** — Ebeveyn her çocuk için eğitim dönemi belirler
2. **Çoklu çocuk profili** — Tek cihazda birden fazla çocuk
3. **Dönem bazlı AI ajanları** — Her dönem için ayrı AGENTS.md ve müfredat bilgisi
4. **Kalıcı veritabanı** — Deploy'larda silinmeyen PostgreSQL + volume
5. **Ebeveyn performans raporu** — AI tarafından üretilen çocuk gelişim raporu
6. **İstatistik dashboard** — Grafik/tablo ile günlük/haftalık takip

---

## 2. Eğitim Dönemleri

### 2.1 Dönem Tanımları

| Dönem Kodu | Etiket | Yaş Aralığı | Matematik Kapsamı |
|------------|--------|-------------|-------------------|
| `okul_oncesi` | Okul Öncesi | 5-6 | Sayma (1-20), basit toplama, şekil tanıma, büyük-küçük |
| `sinif_1` | 1. Sınıf | 6-7 | Toplama-çıkarma (0-100), onluk-birlik, sıralama, örüntü |
| `sinif_2` | 2. Sınıf | 7-8 | Toplama-çıkarma (3 basamak), çarpma giriş, bölme giriş, problem çözme |
| `sinif_3` | 3. Sınıf | 8-9 | Çarpma-bölme (tek basamak), kesir giriş, geometri temeli, zaman-para |
| `sinif_4` | 4. Sınıf | 9-10 | Çok basamaklı işlemler, kesirler, ondalık, alan-çevre, veri yorumlama |

### 2.2 Müfredat Bilgisi Toplama Stratejisi

Her dönem için MEB müfredatından konu listesi ve kazanımlar gerekli.

**Kaynak araştırması (Playwright-MCP ile):**
- MEB öğretim programları: `mufredat.meb.gov.tr`
- EBA kaynakları: `eba.gov.tr`
- Güvenilir eğitim siteleri

**Araştırma çıktısı:** Her dönem için `agents/curriculum/` altında yapılandırılmış JSON:

```
agents/
├── curriculum/
│   ├── okul_oncesi.json
│   ├── sinif_1.json
│   ├── sinif_2.json
│   ├── sinif_3.json
│   └── sinif_4.json
├── questions.agents.md          # Mevcut (sinif_2 hardcoded)
├── questions-okul-oncesi.agents.md
├── questions-sinif-1.agents.md
├── questions-sinif-3.agents.md
├── questions-sinif-4.agents.md
└── levels.agents.md
```

Her `curriculum/*.json` formatı:
```json
{
  "donem": "sinif_1",
  "yasSiniri": [6, 7],
  "konular": [
    {
      "alan": "Sayılar ve İşlemler",
      "kazanimlar": [
        "0-100 arası sayıları okur ve yazar",
        "Onluk ve birlik kavramını açıklar",
        "Toplama işlemi yapar (elde'li / elde'siz)"
      ],
      "soruTipleri": ["toplama", "cikarma", "siralama", "eksik_sayi"],
      "sayiAraligi": [0, 100],
      "zorlukSinirlari": {
        "1": "tek basamak + tek basamak, sonuç ≤ 10",
        "2": "tek basamak + tek basamak, sonuç ≤ 20",
        "3": "iki basamak + tek basamak",
        "4": "iki basamak + iki basamak, elde'siz",
        "5": "iki basamak + iki basamak, elde'li"
      }
    }
  ]
}
```

---

## 3. Çoklu Çocuk Profili

### 3.1 Mevcut Durum

- `ChildProfile` modeli zaten `device` FK + `name` ile `unique_together` → çoklu profil DB'de destekleniyor
- Register endpoint'i otomatik "Çocuk" adıyla tek profil oluşturuyor
- Android tarafında profil seçimi yok

### 3.2 Hedef Akış

```
Ebeveyn → Ayarlar → Çocuk Profilleri
  ├── [+] Yeni Çocuk Ekle
  │     ├── Ad: ________
  │     └── Eğitim Dönemi: [Okul Öncesi ▾] [1. Sınıf ▾] [2. Sınıf ▾] [3. Sınıf ▾] [4. Sınıf ▾]
  │
  ├── 👧 Elif  — 2. Sınıf — 📊 %78 başarı
  │     ├── [Dönem Değiştir]
  │     ├── [Performans Raporu]
  │     └── [Aktif Profil Yap ✓]
  │
  └── 👦 Ahmet — Okul Öncesi — 📊 %65 başarı
        ├── [Dönem Değiştir]
        ├── [Performans Raporu]
        └── [Aktif Profil Yap]
```

### 3.3 Backend Model Değişiklikleri

```python
# ChildProfile — mevcut modele eklenen alanlar
class ChildProfile(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100, default="Çocuk")
    
    # YENİ: Eğitim dönemi
    education_period = models.CharField(
        max_length=20,
        choices=[
            ('okul_oncesi', 'Okul Öncesi'),
            ('sinif_1', '1. Sınıf'),
            ('sinif_2', '2. Sınıf'),
            ('sinif_3', '3. Sınıf'),
            ('sinif_4', '4. Sınıf'),
        ],
        default='sinif_2',
    )
    
    # YENİ: Aktif profil mi (cihaz başına 1 aktif)
    is_active = models.BooleanField(default=True)
    
    # Mevcut alanlar (değişmez)
    total_correct = models.IntegerField(default=0)
    total_shown = models.IntegerField(default=0)
    current_difficulty = models.IntegerField(default=1)
    stats_json = models.JSONField(default=dict, blank=True)
    
    # YENİ: Günlük/haftalık istatistikler
    daily_stats = models.JSONField(default=dict, blank=True,
        help_text="Son 30 günlük günlük çözüm sayıları")
    weekly_report_json = models.JSONField(default=dict, blank=True,
        help_text="AI tarafından üretilen haftalık rapor")
    total_time_seconds = models.IntegerField(default=0,
        help_text="Toplam uygulama kullanım süresi (saniye)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('device', 'name')
```

### 3.4 Yeni API Endpoint'leri

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `children/` | GET | Cihazın tüm çocuk profillerini listele |
| `children/` | POST | Yeni çocuk profili oluştur (`name`, `education_period`) |
| `children/<id>/` | PATCH | Profil güncelle (ad, dönem, aktif durumu) |
| `children/<id>/activate/` | POST | Bu profili aktif yap (diğerleri pasif) |
| `children/<id>/report/` | GET | AI performans raporunu getir |
| `children/<id>/stats-history/` | GET | Günlük/haftalık istatistik geçmişi |

### 3.5 Android Tarafı Değişiklikleri

1. **`ChildProfileActivity.kt`** (yeni) — Profil listesi, ekleme, dönem seçimi
2. **`SettingsActivity.kt`** — "Çocuk Profilleri" kartı eklenir
3. **`PreferenceManager.kt`** — `activeChildId` ve `activeEducationPeriod` eklenir
4. **`QuestionManager.kt`** — Aktif çocuğun dönemine göre soru çekme
5. **`StatsTracker.kt`** — Aktif çocuğun ID'siyle stats gönderme + süre takibi
6. **`AccountActivity.kt`** — Çocuk profil yönetimi bölümü eklenir

---

## 4. Dönem Bazlı AI Ajanları

### 4.1 Agent Seçim Mekanizması

`ai-generate.sh` çocuğun `education_period` değerine göre doğru AGENTS.md'yi seçer:

```bash
# ai-generate.sh değişikliği
EDUCATION_PERIOD="${1:-sinif_2}"  # Backend'den parametre olarak gelir

AGENTS_FILE="agents/questions-${EDUCATION_PERIOD}.agents.md"
if [ ! -f "$AGENTS_FILE" ]; then
    AGENTS_FILE="agents/questions.agents.md"  # fallback
fi

agents_swap_in "$AGENTS_FILE"
```

### 4.2 Dönem Başına Agent Farklılıkları

| Dönem | Soru Tipleri | Sayı Aralığı | Özel Kurallar |
|-------|-------------|-------------|---------------|
| Okul Öncesi | toplama, cikarma, sayma, karsilastirma | 0-20 | Görsel ipucu zorunlu, max 30 soru (dikkat süresi kısa) |
| 1. Sınıf | toplama, cikarma, siralama, eksik_sayi | 0-100 | Elde'siz işlemler ağırlıklı |
| 2. Sınıf | toplama, cikarma, carpma, bolme, siralama, eksik_sayi | 0-999 | Mevcut sistem (değişmez) |
| 3. Sınıf | carpma, bolme, kesir_giris, zaman, para | 0-9999 | Çarpma tablosu vurgusu, günlük hayat problemleri |
| 4. Sınıf | cok_basamakli, kesir, ondalik, geometri | 0-99999 | Çok adımlı problemler, alan-çevre hesabı |

### 4.3 Validatör Güncellemesi

`validate-questions.py` dönem parametresi almalı:
- Sayı aralığı kontrolü döneme göre değişir
- Soru tipi seti döneme göre kontrol edilir
- Cevap negatif olamaz kuralı tüm dönemlerde geçerli

---

## 5. Kalıcı Veritabanı (Deploy-Safe)

### 5.1 Mevcut Durum
- Dev: SQLite (`db.sqlite3` — container içinde, deploy'da silinir)
- Prod: PostgreSQL ayarı `settings.py`'de var ama yapılandırılmamış

### 5.2 Hedef Mimari

```yaml
# docker-compose.yml değişikliği
services:
  mathlock-db:
    image: postgres:16-alpine
    restart: always
    environment:
      POSTGRES_DB: mathlock
      POSTGRES_USER: mathlock
      POSTGRES_PASSWORD: ${MATHLOCK_DB_PASSWORD}
    volumes:
      - mathlock_pgdata:/var/lib/postgresql/data  # Named volume → deploy'da silinmez
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mathlock"]
      interval: 10s
      timeout: 5s
      retries: 5

  mathlock-backend:
    build: ./backend
    depends_on:
      mathlock-db:
        condition: service_healthy
    environment:
      DATABASE_URL: postgres://mathlock:${MATHLOCK_DB_PASSWORD}@mathlock-db:5432/mathlock
    # ...

volumes:
  mathlock_pgdata:
    name: mathlock_pgdata  # Named volume — docker compose down ile silinmez
```

### 5.3 Yedekleme Stratejisi

```bash
# Günlük otomatik yedekleme (cron)
0 3 * * * docker exec mathlock-db pg_dump -U mathlock mathlock | gzip > /home/akn/backups/mathlock/mathlock_$(date +\%Y\%m\%d).sql.gz

# Son 30 yedeği tut
find /home/akn/backups/mathlock/ -name "*.sql.gz" -mtime +30 -delete
```

### 5.4 Migration Güvenliği

Deploy scriptinde:
```bash
# deploy.sh'a eklenecek
docker compose exec mathlock-backend python manage.py migrate --no-input
# ↑ Sadece yeni migration'lar uygulanır, veri silinmez
```

---

## 6. Ebeveyn Performans Raporu

### 6.1 AI Rapor Üretimi

Her soru seti tamamlandığında (50 soru çözüldüğünde) AI sadece yeni sorular değil, bir **performans raporu** da üretir.

```
ai-generate.sh çalışırken → kimi-cli → questions.json + report.json
```

### 6.2 Rapor Formatı

```json
{
  "childName": "Elif",
  "educationPeriod": "sinif_2",
  "reportDate": "2026-04-18",
  "reportVersion": 5,
  "summary": "Elif bu hafta toplam 150 soru çözdü. Toplama ve çıkarma konularında çok başarılı (%92). Çarpma konusunda gelişim gösteriyor (%68). Bölme konusunda ek çalışma gerekiyor (%45).",
  "strengths": [
    "Toplama işlemlerinde çok hızlı ve doğru",
    "İpucu kullanma oranı düşük — özgüveni yüksek"
  ],
  "improvementAreas": [
    "Bölme işlemlerinde zorlanıyor, konu anlatımına sık bakıyor",
    "3. zorluk seviyesinde süre artıyor"
  ],
  "recommendation": "Elif'in bölme konusunda somut örneklerle (paylaşma, eşit dağıtma) pratik yapması önerilir. Çarpma tablosundaki gelişimi olumlu, devam edilmeli.",
  "metrics": {
    "totalQuestionsSolved": 150,
    "averageAccuracy": 78.5,
    "averageTimePerQuestion": 6.2,
    "streakDays": 5,
    "totalTimeMinutes": 45,
    "byType": {
      "toplama": {"accuracy": 92, "trend": "stable", "difficulty": 3},
      "cikarma": {"accuracy": 85, "trend": "improving", "difficulty": 3},
      "carpma": {"accuracy": 68, "trend": "improving", "difficulty": 2},
      "bolme": {"accuracy": 45, "trend": "declining", "difficulty": 1}
    }
  },
  "weeklyProgress": [
    {"week": "2026-W14", "solved": 50, "accuracy": 72},
    {"week": "2026-W15", "solved": 50, "accuracy": 76},
    {"week": "2026-W16", "solved": 50, "accuracy": 78}
  ],
  "dailyActivity": [
    {"date": "2026-04-12", "solved": 8, "timeMinutes": 5},
    {"date": "2026-04-13", "solved": 12, "timeMinutes": 7},
    {"date": "2026-04-14", "solved": 0, "timeMinutes": 0},
    {"date": "2026-04-15", "solved": 15, "timeMinutes": 9}
  ]
}
```

### 6.3 AGENTS.md Rapor Bölümü Eklentisi

Her dönem agent'ına eklenecek:

```markdown
### Adım 6 - Performans Raporu Üret

stats.json ve önceki rapor verileriyle bir ebeveyn raporu oluştur.
Raporu `data/report.json` dosyasına yaz.

Rapor kuralları:
- Dil: Türkçe, sade, ebeveyne yönelik (pedagojik jargon kullanma)
- Olumlu başla, gelişim alanlarını yapıcı ifade et
- Somut öneriler ver (ne yapmalı, nasıl destek olmalı)
- Kıyaslama YAPMA (diğer çocuklarla karşılaştırma yok)
- Çocuğun adını kullan
```

---

## 7. Android — Ebeveyn Dashboard

### 7.1 Yeni Ekranlar

#### `ChildProfilesActivity.kt`
- Çocuk listesi (profil kartları)
- Her kartta: ad, dönem, başarı oranı, son aktivite
- [+] Yeni çocuk ekleme butonu
- Tıklayınca: profil detayı + dönem değiştirme

#### `PerformanceReportActivity.kt`
- AI raporunun güzel görselleştirilmesi
- Güçlü yanlar (yeşil kartlar)
- Gelişim alanları (turuncu kartlar)
- Öneri (mavi kart)
- Paylaşma butonu (raporu PDF veya resim olarak paylaşma)

#### `StatsDashboardActivity.kt`
- **Günlük çözüm grafiği** — Son 7/30 gün bar chart
- **Konu bazlı başarı** — Radar/spider chart veya horizontal bar
- **Zorluk seviyesi dağılımı** — Pie chart
- **Süre takibi** — Günlük uygulama kullanım süresi
- **Seri (streak)** — Kaç gün art arda çözdüğü

### 7.2 Grafik Kütüphanesi

Önerilen: **MPAndroidChart** (Apache 2.0, yaygın, hafif)

```kotlin
// build.gradle.kts
implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")
```

### 7.3 Süre Takibi

`StatsTracker.kt`'ye ekleme:
```kotlin
// Her MathChallengeActivity açılışında başlat
private var sessionStartTime: Long = 0

fun startSession() {
    sessionStartTime = System.currentTimeMillis()
}

fun endSession() {
    val duration = (System.currentTimeMillis() - sessionStartTime) / 1000
    // SharedPreferences'ta günlük toplam birikir
    val today = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())
    val dailyTotal = prefs.getLong("time_$today", 0) + duration
    prefs.edit().putLong("time_$today", dailyTotal).apply()
}
```

---

## 8. Uygulama Karmaşıklığını Yönetme

### 8.1 "Basit Tutma" Prensibi

Çocuk tarafı **hiçbir şekilde karmaşıklaşmaz** — profil seçimi sadece ebeveyn panelinde:

```
Çocuk açısından:
  Uygulama aç → Soru çöz → Kilit aç
  (Hangi profilin aktif olduğunu bilmesine gerek yok)

Ebeveyn açısından:
  Logo'ya 5 tap → Biyometrik → Ayarlar
  → Çocuk Profilleri → Elif'i seç / Ahmet'i seç
  → Dönem değiştir / Rapor gör
```

### 8.2 Varsayılan Davranış

- İlk kurulumda: Tek çocuk profili ("Çocuk", sinif_2) — mevcut gibi
- Ebeveyn isterse: "Çocuk Profilleri"nden yeni ekler
- Çoklu çocuk varsa: Son aktif profil otomatik seçili
- Ebeveyn hiçbir şey yapmazsa: Mevcut deneyim aynı kalır (backward compatible)

---

## 9. Uygulama Fazları / Yol Haritası

### Faz 1 — Temel Altyapı (Öncelik: YÜKSEK)
1. PostgreSQL + named volume kurulumu
2. `ChildProfile` modeline `education_period`, `is_active`, `daily_stats`, `total_time_seconds` ekleme
3. Migration oluşturma ve mevcut verileri koruma
4. Yedekleme cron'u kurma
5. Çocuk profili CRUD API endpoint'leri

### Faz 2 — Müfredat Araştırması (Öncelik: YÜKSEK)
1. Playwright-MCP ile MEB müfredatı araştırması (5 dönem)
2. `agents/curriculum/*.json` dosyaları oluşturma
3. Her dönem için `questions-<donem>.agents.md` yazma
4. `validate-questions.py`'yi dönem-aware yapma
5. `ai-generate.sh`'ı dönem parametresi alacak şekilde güncelleme

### Faz 3 — Android Profil Yönetimi (Öncelik: ORTA)
1. `ChildProfilesActivity.kt` — profil listesi + ekleme
2. Eğitim dönemi seçim UI (Spinner/Dropdown)
3. `PreferenceManager` — aktif çocuk ID takibi
4. `QuestionManager` + `StatsTracker` — profil-aware
5. `SettingsActivity` — "Çocuk Profilleri" kartı

### Faz 4 — Performans Raporu (Öncelik: ORTA)
1. AGENTS.md'lere rapor üretim adımı ekleme
2. Backend'de rapor endpoint'i
3. `PerformanceReportActivity.kt` — rapor görüntüleme
4. Rapor paylaşma (PDF/resim)

### Faz 5 — İstatistik Dashboard (Öncelik: DÜŞÜK)
1. MPAndroidChart entegrasyonu
2. `StatsDashboardActivity.kt` — grafikler
3. Süre takibi (StatsTracker session timer)
4. Günlük/haftalık seri (streak) hesaplama
5. Push notification — "Elif bugün henüz çalışmadı"

---

## 10. Veritabanı Şeması (Güncellenmiş)

```
Device (1) ──→ (N) ChildProfile ──→ (N) QuestionSet
   │                    │                     
   │                    ├── education_period
   │                    ├── is_active
   │                    ├── daily_stats (JSON: {date: {solved, correct, time_s}})
   │                    ├── weekly_report_json (AI rapor)
   │                    └── total_time_seconds
   │
   ├──→ (1) CreditBalance  ← Cihaz bazlı (paylaşılır)
   ├──→ (N) PurchaseRecord
   └──→ (N) UserQuestionProgress
```

**Önemli kararlar:**
- Kredi bakiyesi **cihaz** bazlı kalır (aile paylaşımlı)
- Soru setleri **çocuk** bazlı (zaten öyle)
- Eğitim dönemi **çocuk** bazlı
- Rapor **çocuk** bazlı
- İstatistikler **çocuk** bazlı

---

## 11. API Sözleşmeleri (Taslak)

### POST /api/mathlock/children/
```json
// Request
{"name": "Elif", "education_period": "sinif_2"}

// Response 201
{"id": 3, "name": "Elif", "education_period": "sinif_2", "is_active": true}
```

### GET /api/mathlock/children/
```json
// Response
[
  {"id": 1, "name": "Elif", "education_period": "sinif_2", "is_active": true,
   "total_correct": 150, "total_shown": 200, "accuracy": 75.0},
  {"id": 2, "name": "Ahmet", "education_period": "okul_oncesi", "is_active": false,
   "total_correct": 30, "total_shown": 50, "accuracy": 60.0}
]
```

### GET /api/mathlock/children/1/report/
```json
// Response — AI raporu (önceden üretilmiş, weekly_report_json'dan)
{
  "summary": "Elif bu hafta...",
  "strengths": [...],
  "improvementAreas": [...],
  "recommendation": "...",
  "metrics": {...},
  "weeklyProgress": [...],
  "dailyActivity": [...]
}
```

### GET /api/mathlock/children/1/stats-history/
```json
// Response — Son 30 günlük istatistikler (grafik için)
{
  "daily": [
    {"date": "2026-04-01", "solved": 12, "correct": 10, "time_seconds": 420},
    ...
  ],
  "byType": {
    "toplama": {"total": 45, "correct": 42, "trend": "stable"},
    ...
  },
  "streakDays": 5,
  "totalTimeMinutes": 180
}
```

### POST /api/mathlock/credits/use/
```json
// Request — artık child_id zorunlu
{"child_id": 1}

// Response — education_period'a göre agent seçilir
{"questions": [...], "version": 6, "report": {...}}
```

---

## 12. Güvenlik ve Gizlilik Notları

- Çocuk adları sadece cihaz + sunucu arasında kalır, üçüncü tarafa gönderilmez
- Performans verileri anonim analiz için kullanılmaz
- Privacy policy güncellenmeli: "Çocuk profili bilgileri" bölümü eklenmeli
- COPPA / KVKK uyumu: Çocuğa ait veriler ebeveyn onayıyla toplanır (ilk kurulumda disclosure)
- Veritabanı yedekleri şifreli tutulabilir (gpg)
