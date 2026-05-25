# Vizyon: CalcEngine Bilimsel Hesap Makinesi API'si

## Yönetici Özeti

CalcEngine, geliştiricilerin matematik ifadelerini string olarak gönderip doğru sonuçlar almasını sağlayan bir REST API'dir. Her ekip kendi matematik ayrıştırıcısını ve trigonometri fonksiyonlarını inşa etmek ve sürdürmek yerine API'mizi çağırır. Benimseyi artırmak için ücretsiz katmanla birlikte abonelik servisi olarak satıyoruz ve hacimli kullanım için ücretli katmanlar sunuyoruz.

## MVP Kapsamında Olan Özellikler

- İfade değerlendirme: `"2 * sin(pi/4) + sqrt(16)"` gibi bir string kabul edip sayısal sonuç döndürme
- Temel aritmetik: toplama, çıkarma, çarpma, bölme, üs alma, karekök, modül, mutlak değer, taban, tavan, yuvarlama
- Trigonometri: sin, cos, tan, asin, acos, atan, atan2 (derece ve radyan modları)
- Logaritmalar: 10 tabanında log, doğal log, keyfi tabanda log, exp
- Temel istatistik: ortalama, medyan, mod, standart sapma, varyans, min, max, toplam, yüzdelik (dizileri kabul eder)
- Matematik sabitleri: pi, e, phi, sqrt(2)
- Kombinatorik: faktöriyel, permütasyonlar (nPr), kombinasyonlar (nCr)
- Hata yönetimi: sıfıra bölme, tanım alanı hataları (negatif log), taşma, bozuk ifadeler için net hata kodları
- Ücretsiz katman (aylık 10K çağrı) ve ücretli katmanlarla API anahtarı kimlik doğrulaması
- Etkileşimli sanal alan ve kod örnekleriyle API dokümantasyon portalı

## MVP'de Açıkça Hariç Olan Özellikler

- Keyfi hassasiyetli aritmetik (Aşama 2)
- Matris ve lineer cebir (Aşama 2)
- Kalkülüs -- türevler, integraller (Aşama 2)
- Finans matematiği -- itfa, NPV, IRR (Aşama 2)
- Python/JS/Java için istemci SDK'ları (Aşama 2 -- MVP için ham HTTP yeterli)
- Adım adım çözüm dökümleri (Aşama 3)
- Birim dönüşümü ve fiziksel sabitler (Aşama 3)
- Toplu işleme / asenkron web kancaları (Aşama 3)
- Sembolik hesaplama (Aşama 3)
- Şirket içi dağıtım (Aşama 3+)

## Hedef Kullanıcılar

- Ürünlerinde matematiğe ihtiyaç duyan ama inşa etmek/sürdürmek istemeyen uygulama geliştiriciler
- Öğrenci odaklı araçlar için hesap makinesi arka ucu ihtiyacı olan EdTech şirketleri
- Denetlenebilir hesaplamalara ihtiyaç duyan FinTech girişimleri (ücretli katman, Aşama 2 odaklı)

## Temel Başarı Metrikleri

- 3 ay içinde 1.000 kayıtlı geliştirici hesabı
- 6 ay içinde 50 ücretli abone
- API çalışma süresi %99,9
- Yanıt süresi p50 50ms altında
- Sıfır kritik doğruluk hatası (yanlış hesaplama sonuçları)

## Açık Sorular

- İfade değerlendirici değişken atamayı (`x = 5; 2*x + 3`) desteklemeli mi yoksa yalnızca tek ifadeler mi?
- Sonuçlar string olarak (hassasiyeti koruyarak) mı yoksa JSON sayıları olarak mı döndürülmeli?
- Örtük çarpma desteklenmeli mi (`2pi` anlamı `2 * pi`)?
