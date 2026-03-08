# Secure Local → VPS Access (Anka)

Bu runbook, dinamik IP kullanan local makineden VPS (`89.252.152.222`) üzerine **çok güvenli** şekilde erişim ve operasyon akışını standartlaştırır.

## 1) Zorunlu güvenlik tabanı

- SSH erişimi yalnızca anahtar ile yapılır (parola kapalı).
- Root login kapalı, sadece `akn` kullanıcısı.
- UFW açık: `22/tcp`, `80/tcp`, `443/tcp` dışında port açılmaz.
- `fail2ban` aktif.
- Google API key’ler IP kısıtlıdır (`89.252.152.222`) ve API bazında kısıtlıdır.

## 2) VPS tarafında SSH hardening

`/etc/ssh/sshd_config` içinde:

```conf
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
AllowUsers akn
X11Forwarding no
AllowTcpForwarding yes
ClientAliveInterval 300
ClientAliveCountMax 2
```

Uygula:

```bash
sudo sshd -t && sudo systemctl reload ssh
```

## 3) UFW ve fail2ban

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

sudo apt-get update
sudo apt-get install -y fail2ban
sudo systemctl enable --now fail2ban
```

## 4) Local makinede güvenli SSH profil

`~/.ssh/config`:

```sshconfig
Host anka-vps
  HostName 89.252.152.222
  User akn
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes
  StrictHostKeyChecking yes
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ForwardAgent no
```

Bağlantı testi:

```bash
ssh anka-vps
```

## 5) API’leri localde güvenli kullanma (önerilen)

Google key’i localden doğrudan çağırma. Localde sadece SSH tunnel ile VPS’e bağlan.

Örnek backend tüneli:

```bash
ssh -N -L 18010:127.0.0.1:8100 anka-vps
```

Sonra localde API çağrısı:

```bash
curl http://127.0.0.1:18010/api/health/
```

Bu sayede Google API çağrısı VPS üzerinden çıkar ve key kısıtları bozulmaz.

## 5.1) Playwright testlerinde local → VPS yönlendirme

Repo içinde E2E helper (`tests/e2e/playwright/helpers/auth.ts`) varsayılan olarak:

- `BACKEND_URL=http://localhost:8000`

değerini kullanır. Yani default durumda test-login çağrısı lokale gider.

Not: `8000` native local (`./dev-local.sh`) içindir; Docker profilde backend `8100` portundadır (`./dev-docker.sh`).

VPS backend'e yönlendirmek için iki güvenli seçenek vardır:

### Seçenek A — SSH tunnel (önerilen)

Önce tunnel aç:

```bash
./scripts/secure-vps-tunnel.sh backend
```

Sonra testi VPS backend'e yönlendir:

```bash
BACKEND_URL=http://127.0.0.1:18010 BASE_URL=http://localhost:3100 npx playwright test
```

### Seçenek B — Doğrudan VPS domain/IP (daha kırılgan)

```bash
BACKEND_URL=https://ankadata.com.tr BASE_URL=https://ankadata.com.tr npx playwright test
```

Notlar:

- Prod ortamında `test-login` endpoint'i genellikle kapalıdır (`ANKA_ALLOW_TEST_LOGIN=False`).
- Bu yüzden prod'da test-login tabanlı senaryolar yerine gerçek Google login akışı kullanılmalıdır.
- Local testte domain/IP üzerinden çalışmak CORS/cookie/same-site farkları nedeniyle local senaryodan farklı davranabilir.

## 5.2) Tunnel-aware geliştirme modları

Google API key'leri VPS IP'sine kısıtlı olduğundan local backend direkt Google'a çıkamaz.
Aşağıdaki modlar "local frontend + VPS backend" mimarisini doğrudan scriptlere entegre eder.

### dev-local.sh --vps (native frontend + VPS backend)

```bash
./dev-local.sh --vps
```

- Django **başlatılmaz**; bunun yerine SSH tunnel ile VPS backend'e bağlanılır.
- Tunnel portu: `127.0.0.1:18010` (BACKEND_LOCAL_PORT ile override edilebilir)
- Next.js `npm run dev` olarak local'de çalışır.
- Frontend env varsları otomatik ayarlanır:
  - `NEXT_PUBLIC_API_URL=http://127.0.0.1:18010`
  - `NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:18010/api`
  - `NEXT_INTERNAL_BACKEND_URL=http://127.0.0.1:18010`

Önkoşul: `~/.ssh/config` içinde `anka-vps` profili tanımlanmış olmalı (bkz. Bölüm 4).

### dev-docker.sh --vps-backend (Docker frontend + VPS backend)

```bash
./dev-docker.sh --vps-backend
```

- Backend/db/redis container'ları **başlatılmaz**.
- SSH tunnel ile `127.0.0.1:18010 → VPS:8100` kurulur.
- Yalnızca `frontend` container `--no-deps` ile başlatılır.
- `extra_hosts: host.docker.internal:host-gateway` sayesinde container içi SSR
  çağrıları `http://host.docker.internal:18010` üzerinden tünele ulaşır.
- Browser-side NEXT_PUBLIC_* değişkenleri `localhost:18010`'a yönlendirilir.

Aynı zamanda build zorlamak için:

```bash
./dev-docker.sh --vps-backend --build
```

### Google Maps (browser-side) key eksikliği

`docker-compose.yml` artık `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` ortam değişkenini okur:

```yaml
NEXT_PUBLIC_GOOGLE_MAPS_API_KEY: ${NEXT_PUBLIC_GOOGLE_MAPS_API_KEY:-}
```

`.env.local.docker` dosyasına key değeri eklenmiştir. Maps bileşeni (`MapAreaSelector`)
Docker local ortamında bu sayede key hatası vermez.

### Google Login için localhost izinleri

Google Cloud Console → OAuth 2.0 Client → Authorized origins:
- `http://localhost:3000` (native local)
- `http://localhost:3100` (Docker local)
- `http://127.0.0.1:3000`

Authorized redirect URIs:
- `http://localhost:3000` ve `http://localhost:3100` eklenmezse login ekranı
  `redirect_uri_mismatch` hatası verir.

## 6) Operasyon güvenliği

- Deploy sadece anahtar doğrulamalı SSH ile yapılır (`deploy.sh` içinde sertleştirildi).
- Prod `.env` dosyasında key’ler sadece VPS’te tutulur.
- Her 90 günde SSH key rotate önerilir.
- Sunucuda düzenli: `sudo unattended-upgrades` veya haftalık patch penceresi.

## 7) Hızlı kontrol listesi

- [ ] `ssh anka-vps` parola sormadan anahtar ile bağlanıyor
- [ ] `sudo ufw status` yalnız 22/80/443 açık
- [ ] `sudo fail2ban-client status sshd` aktif
- [ ] Google API key kısıtları: `IP addresses + 1 API`
- [ ] Uygulama localde sadece tunnel üzerinden test ediliyor

### Native local (dev-local.sh --vps) doğrulaması

```bash
./dev-local.sh --vps
# Beklenen: "VPS backend tunnel hazır → http://127.0.0.1:18010"
curl http://127.0.0.1:18010/api/health/
# Beklenen: {"status": "ok"}
# Frontend başladıktan sonra:
curl http://localhost:3000/api/health   # Next.js healthcheck
```

### Docker local (dev-docker.sh --vps-backend) doğrulaması

```bash
./dev-docker.sh --vps-backend
# Frontend container başladıktan sonra:
curl http://localhost:3100             # Next.js OK
# Container içinden backend erişimi (SSR):
docker compose exec frontend curl http://host.docker.internal:18010/api/health/
```

### Places API doğrulaması

Batch pipeline sırasında 403 / IP restriction hatası alınmamalı; çağrı VPS üzerinden çıkacağı için key kısıtları geçerli IP'ye sahip.

### Maps bileşeni doğrulaması

`MapAreaSelector` bileşeninin Docker local'de `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` eksikliği hatası vermemesi gerekiyor. `.env.local.docker` içindeki key `.env`'e symlink edildiğinde compose'a geçer.

### Login doğrulaması

Google giriş ekranı `localhost:3000` veya `localhost:3100`'ü authorized origin olarak tanımalı. `redirect_uri_mismatch` hatası alınıyorsa GCP Console → OAuth client → Authorized origins listesi güncellenmeli.

## 8) Tek komutla uygulama (repo içinden)

VPS hardening + doğrulama tek adım:

```bash
./scripts/security/apply-remote-hardening.sh
```

Sadece doğrulama tekrar çalıştırmak için:

```bash
ssh anka@89.252.152.222 'bash -s' < scripts/security/vps-hardening-check.sh
```

## 9) Muğla Plancı Demo (Maps + Search AI, max 10)

Bu demo, akışı VPS üzerinden güvenli biçimde çalıştırır:

- Stage 1-2-3 (Maps/Places) batch pipeline
- Eksik website alanları için Search AI (Gemini + Google Search grounding)
- Sıkı limit: `LIMIT=10` (10’u geçmez)

Çalıştır:

```bash
chmod +x scripts/demos/run-mugla-planci-10.sh
./scripts/demos/run-mugla-planci-10.sh
```

Opsiyonel bütçe/limit override:

```bash
LIMIT=10 DAILY_REQUEST_LIMIT=10 DAILY_TOKEN_LIMIT=8000 ./scripts/demos/run-mugla-planci-10.sh
```

Çıktı CSV (VPS):

- `/home/akn/vps/projects/anka/services/backend/artifacts/demo/mugla_planci_10.csv`
