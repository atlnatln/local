# Vizyon: İade ve Geri Ödeme Modülü — OrderFlow Platformu

> **Brownfield projesi.** Bu belge, mevcut bir sisteme yapılan bir değişikliği açıklar.
> Mevcut Durum bölümü gereklidir. AIDLC'ye gereksinimler ve tasarım üretmeden önce
> neyin zaten mevcut olduğunu anlaması için ihtiyaç duyduğu bağlamı sağlar.

---

## Mevcut Durum

OrderFlow, TypeScript ile Node.js üzerinde inşa edilmiş mevcut bir e-ticaret sipariş yönetim platformudur. Sipariş oluşturma, ödeme tahsilatı, yerine getirme yönlendirme ve kargo bildirimlerini yönetir. Şu anda herhangi bir iade veya geri ödeme yeteneği yoktur.
İade etmek isteyen müşteriler desteğe e-posta yoluyla ulaşır ve geri ödemeler finans ekibi tarafından ödeme sağlayıcısı panosunda manuel olarak işlenir.

Mevcut platformun üç arka uç servisi (order-service, payment-service, notification-service) ve bir React ön ucu vardır. Tüm servisler AWS ECS Fargate üzerinde dağıtılmıştır. Birincil veri deposu PostgreSQL'dir.

---

## Ne Ekliyoruz

Müşterilerin mevcut mağaza üzerinden kendi kendine iade talebi oluşturmasına olanak tanıyan ve operasyon personelinin platformdan ayrılmadan geri ödemeleri incelemesine, onaylamasına ve işlemesine olanak tanıyan bir iade ve geri ödeme modülü.

---

## Bu Yineleme İçin Kapsamda Olan Özellikler

- Müşteriye yönelik iade talep formu: sipariş seç, ürünleri seç, iade nedeni seç
- Müşteriler için iade talep durumu takibi (gönderildi, onaylandı, reddedildi, geri ödendi)
- Operasyon panosu: açık iade taleplerini görüntüle, notla onayla veya reddet
- Mevcut payment-service entegrasyonu üzerinden otomatik geri ödeme işleme
- Her durum değişikliğinde notification-service aracılığıyla müşterilere e-posta bildirimleri
- İade neden kodları: hasarlı, yanlış ürün, fikir değişikliği, diğer

## Bu Yineleme İçin Açıkça Kapsam Dışı Olan Özellikler

- İade kargo etiketi oluşturma (şimdilik manuel süreç, Aşama 2)
- Satır öğesi düzeyinde kısmi geri ödemeler (MVP'de yalnızca tam sipariş geri ödemeleri)
- Stoklama veya envanter yönetimi entegrasyonu (Aşama 2)
- Dolandırıcılık tespiti veya iade kötüye kullanım önleme (Aşama 3)
- Kendi kendine değişim (tek akışta iade + yeniden sipariş, Aşama 2)
- İade analitiği veya raporlama panosu (Aşama 2)

---

## Değişmemesi Gerekenler

- Sipariş oluşturma, ödeme tahsilatı ve yerine getirme akışları -- bunları değiştirmeyin
- Mevcut siparişler, ödemeler ve müşteriler için PostgreSQL şeması -- yalnızca ekleme değişiklikleri
- Notification-service API sözleşmesi -- olduğu gibi tüketin, değiştirmeyin
- Mevcut React ön uç bileşen kütüphanesi ve tasarım sistemi

---

## Açık Sorular

- İade taleplerinin bir onay adımı olmalı mı, yoksa uygun iadeler politika kurallarına dayalı olarak otomatik olarak onaylanmalı mı (örn. 30 gün içinde, ürün son satış olarak işaretlenmemiş)?
- Operasyon panosunda iade talebi kime ait -- müşteri destek ekibi, depo ekibi, yoksa farklı görünümlerle her ikisi mi?
- Geri ödemeler onay üzerine hemen verilmeli mi, yoksa gün sonunda toplu olarak işlenmeli mi?
- Sistemin uygulaması gereken bir iade penceresi politikası var mı (örn. teslimattan itibaren 30 gün), yoksa şimdilik vaka bazında mı?
