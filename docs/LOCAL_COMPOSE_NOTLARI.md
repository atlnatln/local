# Local Docker Compose Notları (İki Proje)

Bu repo’nun yaklaşımı: her proje kendi dizinindeki Compose ile çalışır, bu repo sadece tek noktadan yönetir.

## Neden böyle?

- Proje içi compose’lar zaten oturmuş olur.
- Canlıda çalışan `webimar` için risk düşük.
- Çakışma yönetimi daha kolay: her proje kendi compose “project name”’i ile ayağa kalkar.

## Çakışma kontrol listesi

- Host’a publish edilen portlar eşsiz olmalı (ör: webimar `3000/8000`, anka `3100/8100`).
- Container name’ler compose içinde hard-coded ise çakışabilir.
  - Mümkünse `container_name:` kullanmayın veya projeye özgü prefix verin.

## İpucu: compose project name zorlamak

Bazı makinelerde proje adı çakışması yaşarsanız, manuel çalıştırırken `-p` kullanabilirsiniz:

```bash
cd /home/akn/Genel/webimar
docker compose -p webimar up -d

cd /home/akn/anka
docker compose -p anka up -d
```

Scriptler şu an dizin bazlı çalıştığı için genelde buna gerek kalmaz.
