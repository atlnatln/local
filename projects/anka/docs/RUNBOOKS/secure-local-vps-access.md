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
