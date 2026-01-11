# İki Proje Local Geliştirme (Tek Dizinden Yönetim)

Bu repo, localde iki ayrı proje dizinini tek bir “kontrol merkezi” dizinden Docker Compose ile yönetmek içindir.

## Projeler

- **webimar**: `projects/webimar/`
- **anka**: `projects/anka/`

Bu repo, projelerin compose dosyalarını **otomatik keşfeder**: `projects/*` altındaki dizinlerde `docker-compose.yml` (veya `compose.yml`) varsa proje olarak kabul edilir.

## Hızlı Başlangıç

1. Docker’ın çalıştığından emin olun.
2. Aşağıdaki komutlarla iki projeyi aynı anda başlatın:

```bash
cd /home/akn/vps
bash scripts/up.sh
```

Mevcut projeleri listeleme:

```bash
bash scripts/projects.sh
```

Durdurma:

```bash
bash scripts/down.sh
```

Durum:

```bash
bash scripts/status.sh
```

Log izleme (varsayılan: her ikisi):

```bash
bash scripts/logs.sh
# veya sadece biri
bash scripts/logs.sh webimar
bash scripts/logs.sh anka
```

## Varsayımlar / Uyumlama

Bu scriptler aşağıdaki varsayımla çalışır:

- webimar dizininde `docker-compose.yml` (veya `compose.yml`) vardır.
- anka dizininde `docker-compose.yml` (veya `compose.yml`) vardır.

Eğer compose dosyası isimleri farklıysa, [scripts/config.sh](scripts/config.sh) içindeki `COMPOSE_CANDIDATES` listesini güncelleyin.

## Takip

Yapılanlar ve yapılacaklar için [docs/TAKIP.md](docs/TAKIP.md) dosyasını kullanın.

Localde iki compose projesini yan yana çalıştırma notları: [docs/LOCAL_COMPOSE_NOTLARI.md](docs/LOCAL_COMPOSE_NOTLARI.md)
