# Hızlı Referans — Sık Kullanılan Komutlar

> Detaylı wiki iş akışları için `references/WORKFLOW.md`, kod kuralları için `references/CONVENTIONS.md`.

---

## Git (Tüm Ortamlar)

```bash
git status --short              # Değişiklik özeti
git add -A && git commit -m "type(scope): ..."
git push origin main
git pull origin main
(command -v git >/dev/null 2>&1 && timeout 5 git fetch origin) || true
```

---

## Deploy

| Proje | Komut |
|-------|-------|
| **Ops-Bot** | `cd /home/akn/local/ops-bot && ./deploy.sh` (package) veya `./deploy.sh --mode git` |
| **Webimar** | `cd /home/akn/local/projects/webimar && ./deploy.sh --skip-github` (~10 dk) |
| **MathLock Backend** | `cd /home/akn/local/projects/mathlock-play/backend && pip install -r requirements.txt && sudo systemctl restart mathlock-backend mathlock-celery` |
| **MathLock Android** | `cd /home/akn/local/projects/mathlock-play && ./gradlew bundleRelease` (AAB) / `assembleDebug` (APK) |
| **Infrastructure** | `cd /home/akn/local/infrastructure && sudo ./setup.sh --ssl` |

---

## VPS Erişim (Local'den)

```bash
ssh akn@89.252.152.222
ssh akn@89.252.152.222 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
ssh akn@89.252.152.222 "systemctl status ops-bot telegram-kimi"
ssh akn@89.252.152.222 "docker exec vps_nginx_main nginx -t"
ssh akn@89.252.152.222 "journalctl -u ops-bot -n 50 --no-pager"
```

**VPS'teki kritik dizinler:**
- `/home/akn/vps/ops-bot/` — Ops-Bot (systemd)
- `/home/akn/vps/projects/webimar/` — Webimar (Docker)
- `/home/akn/vps/projects/mathlock-play/` — MathLock (systemd + Docker)
- `/home/akn/vps/infrastructure/` — nginx, SSL

---

## Test

| Proje | Komut |
|-------|-------|
| **Webimar API** | `cd projects/webimar/webimar-api && pytest` |
| **Webimar Frontend** | `cd projects/webimar/webimar-nextjs && npm run lint && npm run build` |
| **MathLock Backend** | `cd projects/mathlock-play/backend && pytest` |

### Deploy Öncesi Checklist
- [ ] Kod derleniyor / testler geçiyor
- [ ] `.env.example` güncel
- [ ] Nginx test: `docker exec vps_nginx_main nginx -t`
- [ ] Wiki ingest yapıldı (eğer proje docs'u değiştiyse)

---

## Wiki

```bash
# Lint
 cd ~/.kimi/skills/local-wiki && python3 scripts/wiki_lint.py /home/akn/local/wiki

# Auto-sync (tüm repo'lar için fetch + fast-forward pull)
 cd /home/akn/local && bash scripts/auto-sync.sh
```

---

## Git Auth (VPS)

- **SSH tercih edilir:** `git remote set-url origin git@github.com:atlnatln/local.git`
- **SSH key yoksa:** `git config credential.helper store` (bir kez token girilir, hatırlanır)
