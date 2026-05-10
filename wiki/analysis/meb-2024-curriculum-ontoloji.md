---
title: "MEB 2024 Müfredatı — Veri Modeli Ontolojisi ve ID Standardizasyonu"
created: "2026-05-08"
updated: "2026-05-10"
type: concept
tags: [mathlock-play, meb, curriculum, database, concept]
related:
  - meb-2024-curriculum-technical-alignment
  - meb-2024-curriculum-render
  - mathlock-play-backend
---

# MEB 2024 Müfredatı — Veri Modeli Ontolojisi ve ID Standardizasyonu

> [[meb-2024-curriculum-technical-alignment|Ana analiz sayfasına dön]]

## 3. Veri Modeli Ontolojisi: Tip Standardizasyonu ve ID Çakışması

### 3.1 Tip İsimlendirme Çatışması Analizi

| Bileşen | İsimlendirme Konvansiyonu | Örnek: Çarpma | Örnek: Bölme |
|---|---|---|---|
| Backend (Django Model) | CharField/choices, Türkçe karakterli | çarpma | bölme |
| generate_age_questions.py | Python değişkeni, Türkçe karakterli | çarpma | bölme |
| agents.md | Markdown dokümantasyon, Türkçe karaktersiz | carpma | bolme |

**Tablo 8:** Tip İsimlendirme Çatışması Matrisi

#### 3.1.1 Çatışma Noktaları ve Risk Analizi

Çatışmanın en kritik noktası, Backend-Agents eşleşmemesidir. Backend modelinde `Question.type` alanı CharField/choices olarak tanımlanmış ve Türkçe karakterli değerler (`çarpma`, `bölme`) içermektedir. Ancak agents.md, Türkçe karaktersiz versiyonlarını (`carpma`, `bolme`) kullanmaktadır.

**Senaryo 1:** agents.md otomatik işlenirse, çıkarılan tip değerleri backend'e kaydedilemez veya yanlış eşleşmelere yol açar.

**Senaryo 2:** Geliştiriciler agents.md'yi referans alarak kod yazdıklarında, Türkçe karaktersiz isimlendirmeyi kullanma eğilimi gösterir; bu da backend ile tutarsızlık yaratır.

**Pipeline Geçişlerinde Veri Kirliliği Riski**

`generate_age_questions.py`'nin ürettiği sorular, backend'e kaydedilirken tip dönüşümü gerekebilir. Eğer bu dönüşüm tutarlı yapılmazsa, aynı işlem türü farklı kayıtlarda farklı isimlerle yer alabilir.

Bu durum, istatistiksel analizleri, raporlamayı ve filtrelemeyi güçleştirmektedir. Görünüşte küçük bir teknik ayrıntı, sistematik veri kirliliği riski taşımaktadır.

### 3.2 MEB Müfredat Hiyerarşisine Uygun Ontoloji Tasarımı

#### 3.2.1 MAT Kodlama Sistemi Referansı

MEB 2024 müfredatı, kazanımları `MAT.{Sınıf}.{Tema}.{Kazanım}` formatında kodlamaktadır. Bu kodlama sistemi, içerik çerçevesinin yapısal bütünlüğünü yansıtmakta ve her kazanımın benzersiz tanımlanmasını sağlamaktadır.

Bu kodlama sisteminin teknik ontolojiye uyarlanması, müfredatla doğrudan eşleşen bir URI şeması oluşturulmasını mümkün kılmaktadır. Böyle bir şema, tip isimlendirme çatışmasını kökten çözmekte, aynı zamanda müfredatın pedagogik yapısını teknik sisteme taşımaktadır.

#### 3.2.2 URI Şema Önerisi: MAT.{Sınıf}.{Tema}.{Kazanım}.{İşlem}

| URI Örneği | Açıklama | Karşılık Gelen Tip Değeri |
|---|---|---|
| MAT.1.2.1.toplama | 1. sınıf, İşlemler teması, 1. kazanım, toplama | toplama |
| MAT.1.2.2.cikarma | 1. sınıf, İşlemler teması, 2. kazanım, çıkarma | cikarma |
| MAT.2.1.2.carpma | 2. sınıf, Sayılar teması, 2. kazanım, çarpma | carpma |
| MAT.2.1.3.bolme | 2. sınıf, Sayılar teması, 3. kazanım, bölme | bolme |
| MAT.3.2.1.kesir_uniter | 3. sınıf, Kesirler teması, 1. kazanım, üniter kesir | kesir_uniter |

**Tablo 9:** URI Şema Örnekleri ve Tip Eşleştirmesi

#### 3.2.3 Tekilleştirme ve Eşleştirme Katmanı

**Canonical Type Registry**

Tüm tip değerlerinin tek yetkili kaynağı. URI formatındaki tip tanımlarını içerir; sistemdeki tüm bileşenler bu tanımlara başvurur. Veritabanında konfigürasyon tablosu veya kodda enum/sabitler sınıfı olarak implement edilir.

**Legacy Mapping Table**

Mevcut isimlendirme konvansiyonlarının (Türkçe karakterli, karaktersiz, kısaltmalar) URI formatındaki canonical değerlere dönüştürülmesini sağlar. Sistem geçişi ve harici entegrasyonda kritik rol oynar.

**Validation Middleware**

Veri akışının her aşamasında tip değerlerinin canonical forma uygunluğunu kontrol eder. Geçersiz veya tanımlanmamış tip değerlerinin sisteme nüfuz etmesini engeller, hataları erken tespit ederek veri kirliliğini önler.

| Legacy Değer | Kaynak Bileşen | Canonical URI |
|---|---|---|
| çarpma | Backend, generate_age_questions.py | MAT.2.1.2.carpma |
| carpma | agents.md | MAT.2.1.2.carpma |
| carp | Eski kod, kısaltma | MAT.2.1.2.carpma |
| multiplication | İngilizce dokümantasyon | MAT.2.1.2.carpma |

**Tablo 10:** Legacy Mapping Table Örneği

### 3.3 `question_id` Çakışma Riski ve Çözümü

| ID Uzayı | Aralık | Kaynak | Kullanım Amacı |
|---|---|---|---|
| Batch 0 (Legacy) | 1000+ | Manuel oluşturulmuş sorular | Kalıtım içerik, referans sorular |
| Batch 1+ (AI Pipeline) | 1–50 | Yapay zeka ile üretilmiş sorular | Dinamik içerik üretimi, kişiselleştirme |

**Tablo 11:** Mevcut ID Uzayları ve Özellikleri

#### 3.3.1 Çakışma Riski Analizi

ID aralıklarının birbirine yakın veya örtüşebilir olması temel sorundur. Batch 0'ın 1000+ offset'i kısa vadede çakışmayı önlemekle birlikte, uzun vadede skalama sorunları yaratmaktadır.

"Soru #1005'te zorlandı" ifadesi, bu sorunun Batch 0'ın 1005 numaralı sorusu mu yoksa gelecekteki bir batch'in sorusu mu olduğunu belirsiz kılmaktadır. Bu belirsizlik, hata ayıklamayı, istatistiksel analizi ve öğrenci takibini güçleştirmektedir.

#### 3.3.2 MEB "Okul Temelli Planlama" Modelinden Esinlenme

MEB 2024 programındaki "Okul Temelli Planlama" yaklaşımı, dönemsel içerik çerçevesi modeli üzerinden yapılandırılmaktadır: zamana bağlı versiyonlama, hiyerarşik yapı (yıl → dönem → hafta → konu), ve izlenebilirlik.

Bu özellikler, soru ID'lerinin de benzer bir yapıda organize edilmesi gerektiğini düşündürmektedir.

#### 3.3.3 Kalıcı Çözüm: Yapılandırılmış ID Formatı

Format: `{Yıl}G{Sınıf}-B{Batch}-{SıraNo}`

| ID Örneği | Yapısal Analiz |
|---|---|
| 2024G1-B0-1001 | 2024 eğitim yılı, 1. sınıf, Batch 0 (legacy), sıra 1001 |
| 2024G2-B1-0042 | 2024 eğitim yılı, 2. sınıf, Batch 1 (AI), sıra 42 |
| 2025G3-B2-0150 | 2025 eğitim yılı, 3. sınıf, Batch 2 (AI), sıra 150 |

**Tablo 12:** Yapılandırılmış ID Format Örnekleri

Bu formatın temel avantajları:

- **Benzersizlik:** Yıl, sınıf, batch ve sıra numarası kombinasyonuyla her ID benzersizdir
- **İzlenebilirlik:** ID'den sorunun hangi yıl, sınıf ve kaynak için üretildiği anlaşılır
- **Sıralanabilirlik:** Kronolojik ve hiyerarşik sıralama doğal olarak desteklenir
- **Genişletilebilirlik:** Yeni batch'ler ve sınıf düzeyleri mevcut yapıya zarar vermeden eklenebilir

#### 3.3.4 Geçiş ve Uyumluluk Stratejisi

**Çift ID Dönemi**

Yeni sistem devreye alınırken eski ID'ler geçici olarak korunur. Her kayıtta hem eski hem yeni ID yer alır. Süre: 3-6 ay.

**Migration Script**

Mevcut veritabanı kayıtlarının yeni formata otomatik dönüştürülmesi. Eski ID'den yeni ID üretimi, ilişkisel verilerin güncellenmesi ve dönüşüm raporu.

**API Versiyonlama**

Mobil uygulama ve diğer istemciler yeni ID formatını destekleyecek şekilde güncellenir. API'nin belirli versiyonunda her iki format da kabul edilir.
