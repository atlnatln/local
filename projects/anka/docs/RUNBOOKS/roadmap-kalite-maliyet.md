# Roadmap — Kalite & Maliyet (Maps + Website + Email)

Bu doküman, tarayıcı testlerinde ve canlı gözlemlerde çıkan geliştirme fırsatlarını maliyet odaklı bir sıraya dizer.

1) UI: Email kolonu görünürlüğü (P0)
- Batch detay tablosunda `Email` kolonu göster.
- “CSV İndir (Tarayıcı)” çıktısında `Email` kolonu olduğundan emin ol.

2) Token görünürlüğü: Tüm Gemini çağrıları loglansın (P0)
- Email araması dışında, “resmi website bulma” Gemini çağrısı da token JSONL log’a yazsın.
- Günlük token limiti (`ANKA_EMAIL_DAILY_TOKEN_LIMIT`) prod’da sıfır (sınırsız) kalmasın.

3) Domain blacklist (P0)
- Sosyal medya / dizin / ilan / harita / kısa-link domainleri resmi website adayı olarak reddet.
- Scraping aşamasında da aynı domainler atlanmalı.

4) Website yoksa: Önce resmi website bul (P1)
- Maps/Places `websiteUri` boşsa, Gemini ile resmi site bul → siteyi kaydet → scrape ile email dene.
- Website bulunursa `BatchItem.data.website_uri` alanına yaz.

5) Kalite skoru (P1)
- Email için `source` ve `evidence_url` tut.
- Website domain ↔ email domain uyumu ile güven skoru üret (HIGH/MED/LOW).

6) Rate-limit ve maliyet korumaları (P1)
- Stage 4 Gemini çağrı tavanı (`ANKA_STAGE4_MAX_API_CALLS`) + per-batch limit.
- Domain başına scrape limit + timeout + max byte zaten var; domain bazlı backoff eklenebilir.

7) UX: Kazara batch oluşturmayı engelle (P1)
- Combobox `Enter` davranışı batch submit etmesin (sadece seçim).
- Submit sadece “Batch Oluştur” butonuyla olsun.

8) Event-driven durum güncelleme (P2)
- Polling yerine SSE/WebSocket ile batch status güncelle.

---

Sıradaki adım (hemen): 1–3’ü prod deploy ile kalıcılaştırmak ve UI email kolonunu canlıda doğrulamak.
