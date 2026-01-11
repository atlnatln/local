# Sitemap QA Report — 2026-01-04

**Summary**
- Source: `https://tarimimar.com.tr/sitemap.xml`
- Total URLs found: 126
- OK (200): 101
- Not Found (404): 25

**Top issues**
- A group of `404` entries are under `/cevre-duzeni-planlari/il/<city>/` (25 URLs). These pages return 404 but are present in sitemap.

**404 URL list**

https://tarimimar.com.tr/cevre-duzeni-planlari/il/diyarbakir
https://tarimimar.com.tr/cevre-duzeni-planlari/il/denizli
https://tarimimar.com.tr/cevre-duzeni-planlari/il/balikesir
https://tarimimar.com.tr/cevre-duzeni-planlari/il/sinop
https://tarimimar.com.tr/cevre-duzeni-planlari/il/edirne
https://tarimimar.com.tr/cevre-duzeni-planlari/il/kirklareli
https://tarimimar.com.tr/cevre-duzeni-planlari/il/tekirdag
https://tarimimar.com.tr/cevre-duzeni-planlari/il/erzincan
https://tarimimar.com.tr/cevre-duzeni-planlari/il/izmir
https://tarimimar.com.tr/cevre-duzeni-planlari/il/manisa
https://tarimimar.com.tr/cevre-duzeni-planlari/il/kirsehir
https://tarimimar.com.tr/cevre-duzeni-planlari/il/nevsehir
https://tarimimar.com.tr/cevre-duzeni-planlari/il/nigde
https://tarimimar.com.tr/cevre-duzeni-planlari/il/tunceli
https://tarimimar.com.tr/cevre-duzeni-planlari/il/bingol
https://tarimimar.com.tr/cevre-duzeni-planlari/il/mardin
https://tarimimar.com.tr/cevre-duzeni-planlari/il/siirt
https://tarimimar.com.tr/cevre-duzeni-planlari/il/hakkari
https://tarimimar.com.tr/cevre-duzeni-planlari/il/mersin
https://tarimimar.com.tr/cevre-duzeni-planlari/il/bitlis
https://tarimimar.com.tr/cevre-duzeni-planlari/il/giresun
https://tarimimar.com.tr/cevre-duzeni-planlari/il/rize
https://tarimimar.com.tr/cevre-duzeni-planlari/il/artvin
https://tarimimar.com.tr/cevre-duzeni-planlari/il/sivas
https://tarimimar.com.tr/cevre-duzeni-planlari/il/kayseri

**Recommendations**
1. If pages should exist: implement those routes/pages or restore content, then ensure they return `200`.
2. If pages are obsolete: remove them from the sitemap generation, or set up 301 redirects to the appropriate pages.
3. For intentionally removed content, prefer returning `410` and removing from sitemap to speed Google reindexing.
4. Add a CI check that validates sitemap URLs (follow redirects, require 200/301/302) on deploy and fail builds if >X broken links.

**Next steps (I can do)**
- [ ] Update sitemap generation to exclude non-existing pages OR add redirects (need your decision which).
- [ ] Prepare a small patch (if you prefer redirects or removal) and a PR.
- [ ] Optionally submit an updated sitemap to Google Search Console.

---
Report generated automatically by a site scan on `tarimimar.com.tr`.
