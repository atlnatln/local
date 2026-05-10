---
title: "MEB 2024 Müfredatı — Matematiksel Temsil ve Android Render Uyumu"
created: "2026-05-08"
updated: "2026-05-10"
type: concept
tags: [mathlock-play, meb, curriculum, android]
related:
  - meb-2024-curriculum-technical-alignment
  - meb-2024-curriculum-ontoloji
  - mathlock-play-android
---

# MEB 2024 Müfredatı — Matematiksel Temsil ve Android Render Uyumu

> [[meb-2024-curriculum-technical-alignment|Ana analiz sayfasına dön]]

## 2. Matematiksel Temsil Becerisi ↔ Android Render Uyumu

### 2.1 MEB Alan Becerileri ve Temsil Çeşitliliği

**MAB3: Matematiksel Temsil**

Öğrencinin matematiksel düşünceleri çeşitli temsil biçimleriyle ifade etme ve bu temsiller arasında geçiş yapma becerisi. 1. sınıf ve okul öncesi düzeyinde somut nesneler, resimler, semboller ve sözel ifadeler arasında geçişin temelini oluşturur.

- Somut → Resimsel → Sembolik (CPA yaklaşımı)

**MAB5: Matematiksel Araç ve Teknoloji ile Çalışma**

Dijital araçları matematiksel keşif ve problem çözme süreçlerinde etkin olarak kullanma becerisi. Android bağlamında dokunmatik ekran etkileşimleri, sesli geri bildirimler ve görsel animasyonlar aracılığıyla temsillerin zenginleştirilmesini gerektirir.

- Dokunmatik etkileşimler, sesli geri bildirimler

**Temsil Gereksinimleri:**

- Emoji tabanlı sayma (🍎🍎🍎)
- Örüntü tamamlama (1, 2, 1, 2, ?)
- Sıralama görselleri
- Etkileşimli elemanlar
- Sürükle-bırak etkileşimi

| Temsil Düzeyi | Somut Nesne | Resim/Emoji | Sembol | Yaş Uygunluğu |
|---|---|---|---|---|
| Somut | Fiziksel elma, blok | — | — | Okul Öncesi (5–6) |
| Yarı-Somut | — | 🍎🍎🍎 emoji | — | Okul Öncesi–1. Sınıf (5–7) |
| Resimsel | — | Çizim, fotoğraf | — | 1. Sınıf (6–7) |
| Sembolik | — | — | 3, +, −, = | 1. Sınıf–2. Sınıf (6–8) |

**Tablo 5:** Temsil Düzeyleri ve Yaş Uygunluğu

### 2.2 Mevcut Android Parse Mantığı Sorunları

#### 2.2.1 "= ?" Format Bağımlılığı

MathChallengeActivity'nin mevcut parse mantığı, matematiksel soruları işlemek için tek bir formata bağımlıdır: `= ?` yapısı. Bu format, metin tabanlı, sembolik temsillere özgüdür.

Tek tip cevap input yapısı (sayısal klavye) sorunu derinleştirir. "Kaç tane elma var: 🍎🍎🍎" sorusu için öğrenci elmaları dokunarak sayabilmeli; "1, 2, 1, 2, ?" örüntü sorusu için seçenekler arasından seçim yapmalıdır.

Bu durum, MAB5 becerisinin "teknolojiyi matematiksel araç olarak kullanma" hedefinin gerçekleşmesini engellemektedir. Öğrenci, teknolojiyi pasif bir içerik tüketici olarak kullanmakta, aktif bir keşif aracı olarak deneyimleyememektedir.

#### 2.2.2 agents.md Formatlarının Render Engeli

"Kaç tane elma var: 🍎🍎🍎" — Mevcut `= ?` parse mantığı, emoji karakterlerini işlemek için tasarlanmamıştır. Emoji'lerin Unicode olarak algılanması metin düzeninde bozulmalara yol açabilmekte; boyutlandırma ve hizalama için özel işlemler gerekmektedir.

"1, 2, 1, 2, ?" — Sayı dizisinin yapısal özelliği (tekrarlayan 1-2 örüntüsü) kritik öneme sahiptir. Mevcut parse mantığı bu yapısal bilgiyi ayıklayamamakta, soruyu basit bir metin dizisi olarak işlemektedir.

Bu iki formatın render engeli, pedagojik bir fırsatın kaçırılmasıdır. Sayma ve örüntü becerileri, okul öncesi ve 1. sınıf düzeyinde matematiksel gelişimin temel yapı taşlarıdır.

### 2.3 Kapsamlı Refactoring Planı

#### 2.3.1 Soru Tipi Sınıflandırma Sistemi

MEB müfredatının temsil çeşitliliğini desteklemek için, polimorfik bir mimari tasarlanmalıdır. Temel bir `MathQuestion` soyut sınıfından türeyen özel soru tipleri, kendi render mantığını, etkileşim modunu ve cevap doğrulama mekanizmasını kendisi tanımlamalıdır.

| Soru Tipi | Temsil Modu | Etkileşim Tipi | Örnek | Hedef Yaş |
|---|---|---|---|---|
| TextQuestion | Sembolik metin | Sayısal klavye | "5 + 3 = ?" | 7+ |
| VisualCountQuestion | Emoji/görsel nesne | Dokunmatik sayma/seçim | "🍎🍎🍎 kaç tane?" | 5–7 |
| PatternQuestion | Yapısal dizi | Seçenek seçimi/sürükle-bırak | "1, 2, 1, 2, ?" | 6–8 |
| SortingQuestion | Sıralanabilir nesneler | Sürükle-bırak sıralama | "Küçükten büyüğe sıralayın" | 6–9 |
| MeasurementQuestion | Cetvel, terazi simülasyonu | Sürükle-bırak ölçme | "Kaç cm?" | 7–9 |

**Tablo 6:** Soru Tipi Sınıflandırma Sistemi

#### 2.3.2 Render Katmanı Mimarisi

**EmojiSpannableBuilder**

Unicode emoji karakterlerinin metin içinde düzgün görüntülenmesini, cihaz ekranına göre ölçeklendirmeyi ve tutarlı boşluklar eklemeyi sağlar. EmojiCompat kütüphanesi entegrasyonu ve TouchDelegate ile dokunmatik etkileşim alanları genişletilir.

**PatternView**

Sayı dizisini yatay olarak sıralanmış görsel öğeler olarak render eder. Eksik öğenin yerini boş kutu veya soru işareti ile belirtir. Renk kodlaması (1=mavi, 2=yeşil) ile tekrarlayan yapı görselleştirilir.

**DraggableItemView**

ItemTouchHelper ile entegre sürükle-bırak etkileşimini yönetir. Sürükleme sırasında öğe yarı saydam hale gelir, hedef pozisyon vurgulanır. Doğru sıralamada görsel geri bildirim verilir.

#### 2.3.3 Cevap Input Dönüşüm Mekanizmaları

| Input Bileşeni | Kullanım Alanı | Etkileşim Modu | Özel Özellikler |
|---|---|---|---|
| NumericKeypad | TextQuestion | Sayısal tuş takımı | Büyük tuşlar, sesli geri bildirim, hata önleme |
| PatternContinuationInput | PatternQuestion | Seçenek düğmeleri | 2-4 seçenek, animasyonlu yerleştirme, anında doğrulama |
| DragDropAnswer | SortingQuestion, VisualCountQuestion | Sürükle-bırak | Dokunmatik hassasiyet, hedef vurgulama, düzeltme imkanı |
| VoiceInput | Okul öncesi tüm soru tipleri | Sesli cevap | SpeechRecognizer API, çocuk sesi optimizasyonu, güven eşiği |

**Tablo 7:** Çok Modlu Cevap Input Sistemi

#### 2.3.4 Parse Mantığı Genişletimi

Mevcut regex tabanlı parse mantığının genişletilmesi, hem yeni soru formatlarını destekleyecek hem de mevcut `= ?` formatını koruyacak şekilde tasarlanmalıdır. Çok aşamalı bir parse pipeline'ı:

1. **Format Tespiti:** Emoji içeren → VisualCountQuestion, virgüllü sayı dizisi → PatternQuestion, `=` işareti → TextQuestion
2. **İçerik Ayrıştırma:** Format tipine göre ilgili parser: emoji sayısı/türü, örüntü dizisi/eksik eleman, operandlar/operatör
3. **JSON Serileştirme:** Standart JSON formatına dönüştürme; tüm soru tipleri için ortak yapı + özel alanlar

Geriye uyumluluk: Mevcut `= ?` formatlı sorular otomatik olarak TextQuestion tipine dönüştürülmeli, veritabanı kayıtları için migration script çalıştırılmalıdır. Çift sistem döneminde her iki format da paralel çalışabilmelidir.
