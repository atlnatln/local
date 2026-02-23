# Sistem Akışı (Kuş Bakışı) — Kullanıcı Sorgusundan Teslime

Aşağıdaki adımlar, bir kullanıcının panelde sorgu oluşturmasından sonuçların UI/CSV/XLSX olarak teslim edilmesine kadar olan uçtan uca akışı özetler.

1) Kullanıcı şehir + sektör/işletme türü (ve gerekirse adet/opsiyonlar) bilgilerini yazar ve batch oluşturur.

2) Frontend, backend’e `POST /api/batches/` isteği atar.

3) Backend, aynı sorgunun tekrar çalışmaması için sorgudan deterministik `query_hash` üretir.
   - Aynı `query_hash` zaten varsa mevcut batch dönebilir.

4) Batch işleme (pipeline) başlar ve batch durumu (status) aşama aşama güncellenir.

5) Stage 1 — Aday ID toplama (COLLECTING_IDS)
   - Google Places “Text Search” ile geniş bir aday havuzu için Place ID’ler toplanır.

6) Stage 2 — Doğrulama/eleme (FILTERING)
   - Aday ID’ler Google Places “Details (Pro)” ile kontrol edilir.
   - Adres/işletme durumu gibi kurallara uymayan veya 404 dönenler elenir.

7) Stage 3 — İletişim zenginleştirme (ENRICHING_CONTACTS)
   - Stage 2’yi geçenler için Google Places “Details (Enterprise)” çağrılır.
   - Telefon (`nationalPhoneNumber`) ve web sitesi (`websiteUri`) gibi alanlar eklenir.

8) Stage 4 — Email zenginleştirme (ENRICHING_EMAILS) (opsiyonel)
   - Amaç: `BatchItem.data.email` alanını doldurmak.
   - 8.1) Web sitesi varsa: önce web sitesi üzerinde iletişim sayfaları kazınır (scrape) ve email aranır.
        - Bulunamazsa ve `GEMINI_API_KEY` varsa: Gemini Search Grounding ile (mümkünse aynı domain’i hedefleyerek) tekrar aranır, ardından bulunan sayfalar kazınır.
   - 8.2) Web sitesi yoksa: Gemini Search Grounding ile resmi site/iletişim sayfası bulunmaya çalışılır, sonra bulunan sayfalar kazınır ve email çıkarılır.
   - Not: `ANKA_EMAIL_ENRICHMENT_ENABLED` kapalıysa Stage 4 atlanır. `GEMINI_API_KEY` yoksa “Gemini ile arama” kısmı atlanır.

9) Pipeline biter: batch `READY` (veya korumalı şekilde `PARTIAL` / hata ile `FAILED`) olur.

10) Faturalama/kredi kesintisi yapılır.
   - Temel kural: kullanıcıya teslim edilen (zenginleştirilmiş) kayıt sayısı üzerinden hesap yapılır.

11) Çıktılar hazırlanır.
   - CSV/XLSX export job’ları üretilir ve `csv_url` / `xlsx_url` olarak sunulur.

12) Kullanıcı batch detay sayfasında sonuçları görür.
   - Frontend, `GET /api/batches/{id}/` ile batch durumunu ve item’ları düzenli aralıkla poll eder.
   - Tablo olarak listeler ve kullanıcı CSV/XLSX indirebilir.

---

İlgili dokümanlar:
- `docs/RUNBOOKS/maps-query-logic-pipeline.md`
- `docs/RUNBOOKS/email-enrichment-stage4.md`
- `docs/RUNBOOKS/gemini-search-grounding-enrichment.md`
