# Anahtar Teslim Takip

Tarih: 10 Ocak 2026

## Amaç

- Canlıda çalışan **webimar**’a dokunmadan, localde iki projeyi paralel geliştirmek.
- İki (ve ileride 3+) projeyi tek dizinden (bu repo) yönetmek: `up/down/status/logs`.
- Sonraki adım: anka’yı canlıya taşırken “infrastructure + main reverse proxy” modeline geçmek.

## Yapılanlar (✅)

- ✅ Tek dizinden yönetim repo’su oluşturuldu: [README.md](../README.md)
- ✅ Çoklu proje için otomatik keşifli script seti eklendi: [scripts/](../scripts)
- ✅ Takip dokümanı oluşturuldu: [docs/TAKIP.md](TAKIP.md)
- ✅ Projeler workspace içine kopyalandı: `projects/webimar/`, `projects/anka/`
- ✅ İki proje aynı anda ayağa kaldırıldı (port çakışmaları giderildi)
- ✅ Anka local portları ayrıldı: backend `8100`, frontend `3100`, nginx `8081/8443`

## Yapılacaklar (🔜)

- [ ] Projeleri bu repo altına kopyala:
  - `projects/webimar/`
  - `projects/anka/`
- [ ] Her proje kökünde compose dosyası doğrula (`docker-compose.yml` veya `compose.yml`; gerekirse [scripts/config.sh](../scripts/config.sh) güncellenecek)
- [ ] Port çakışması kontrolü (host’a publish edilen portlar varsa: 3000/8000 vs 3100/8100)
- [ ] Local .env yönetimi netleştir (her projede ayrı `.env` mi, yoksa compose içinde override mı?)
- [ ] Anka frontend için Next.js config uyarısı (swcMinify) gerekirse güncelle
- [ ] Anka canlıya geçmeden önce production compose stratejisi seç:
  - Seçenek A: Her proje kendi `docker-compose.prod.yml` ile (önerilen)
  - Seçenek B: Tek büyük compose (genelde yönetimi zor)
- [ ] VPS tarafında `main-nginx` + ayrı network’ler ile routing (amaç.md referans)

## Notlar

- `webimar` canlıda aktif: `/home/akn/Genel/webimar` (dikkatli değişiklik)
- `anka` henüz canlı değil: `/home/akn/anka`
- Bu repo “yol gösterici + operasyon” içindir; projelerin içine müdahale etmez.
