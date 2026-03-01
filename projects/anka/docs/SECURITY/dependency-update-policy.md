# Bağımlılık Güncelleme ve Zafiyet Tarama Politikası

**Son Güncelleme:** 28 Şubat 2026  
**Sahip:** Tüm Geliştirme Ekibi  
**Gözden Geçirme Sıklığı:** 6 ayda bir

---

## 1. Amaç

Bu belge, Anka Platform'un Python ve Node.js bağımlılıklarının güvenli tutulması için güncelleme sıklığını, zafiyet tarama prosedürlerini ve sorumlulukları tanımlar.

## 2. Bağımlılık Envanteri

### 2.1 Python (Backend)

- **Kaynak:** `services/backend/requirements.txt`
- **Pinleme:** Versiyon aralığı (`>=X,<Y`)
- **Paket sayısı:** ~30 direkt bağımlılık

### 2.2 Node.js (Frontend)

- **Kaynak:** `services/frontend/package.json`
- **Lock dosyası:** `package-lock.json`
- **Paket sayısı:** ~15 direkt bağımlılık

### 2.3 Docker Base Image'ları

| Image | Kullanım | Güncelleme |
|-------|----------|------------|
| `node:18-alpine` | Frontend build & runtime | LTS takip |
| `python:3.12-slim` | Backend runtime | Sık güncelle |
| `postgres:14-alpine` | Veritabanı | Minor update takip |
| `redis:7-alpine` | Cache & queue | Minor update takip |
| `nginx:alpine` | Reverse proxy | Sık güncelle |
| `minio/minio` | Object storage | Stable release takip |

## 3. Zafiyet Tarama

### 3.1 Araçlar

| Araç | Kapsam | Komut |
|------|--------|-------|
| `pip-audit` | Python paketleri | `pip-audit -r requirements.txt` |
| `safety` | Python paketleri (alternatif) | `safety check -r requirements.txt` |
| `npm audit` | Node.js paketleri | `npm audit --production` |
| `trivy` | Docker image'lar | `trivy image <image-name>` |
| `grype` | SBOM tabanlı tarama | `grype sbom:./sbom.json` |

### 3.2 Tarama Sıklığı

| Tarama Türü | Sıklık | Tetikleyici |
|-------------|--------|------------|
| Python zafiyet taraması | Her deploy + haftalık | CI pipeline / cron |
| Node.js zafiyet taraması | Her deploy + haftalık | CI pipeline / cron |
| Docker image taraması | Her build | CI pipeline |
| Tam SBOM oluşturma | Aylık | Manuel |

### 3.3 CI Pipeline Entegrasyonu (Önerilen)

```yaml
# GitHub Actions örneği
security-scan:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Python vulnerability scan
      run: |
        pip install pip-audit
        pip-audit -r services/backend/requirements.txt --fail-on-error
    
    - name: Node.js vulnerability scan
      run: |
        cd services/frontend
        npm audit --production --audit-level=high
    
    - name: Docker image scan
      uses: aquasecurity/trivy-action@master
      with:
        image-ref: 'anka_backend_prod'
        severity: 'HIGH,CRITICAL'
        exit-code: '1'
```

## 4. Güncelleme Politikası

### 4.1 Güncelleme Kategorileri

| Kategori | Tanım | SLA |
|----------|-------|-----|
| **Kritik Güvenlik** | CVSS ≥ 9.0, aktif exploit | 24 saat |
| **Yüksek Güvenlik** | CVSS 7.0-8.9 | 1 hafta |
| **Orta Güvenlik** | CVSS 4.0-6.9 | 2 hafta |
| **Düşük Güvenlik** | CVSS < 4.0 | Sonraki planlı güncelleme |
| **Feature / Bugfix** | Güvenlik dışı | Aylık güncelleme döngüsü |

### 4.2 Güncelleme Prosedürü

```bash
# 1. Mevcut zafiyetleri tara
cd services/backend
pip-audit -r requirements.txt

cd ../frontend
npm audit --production

# 2. Güncellemeleri uygula (Python)
# requirements.txt'i güncelle
# pip install -r requirements.txt
# pytest çalıştır

# 3. Güncellemeleri uygula (Node.js)
npm audit fix
# veya breaking change varsa:
npm audit fix --force  # DİKKATLİ kullan
npm test

# 4. Docker image'ları güncelle
docker pull node:18-alpine
docker pull python:3.12-slim
docker pull postgres:14-alpine
docker pull redis:7-alpine
docker pull nginx:alpine

# 5. Test et
docker compose build --no-cache
docker compose up -d
# Smoke test çalıştır

# 6. Deploy et
```

### 4.3 Breaking Change Yönetimi

Major versiyon güncelleme (breaking change) durumunda:

```
1. [ ] Changelog/migration guide oku
2. [ ] Feature branch'ta güncelle
3. [ ] Tüm test suite'i çalıştır
4. [ ] Manual exploratory testing
5. [ ] Staging'de test et (varsa)
6. [ ] PR review + onay
7. [ ] Production deploy
```

## 5. Önerilen İyileştirmeler

### 5.1 Hash-Pinned Requirements

Reproducible build'ler ve supply chain güvenliği için:

```bash
# pip-compile ile hash-pinned requirements oluştur
pip install pip-tools
pip-compile --generate-hashes requirements.in -o requirements.txt
```

### 5.2 Dependabot / Renovate

Otomatik güncelleme PR'ları için GitHub Dependabot veya Renovate kurulumu:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/services/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    
  - package-ecosystem: "npm"
    directory: "/services/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    
  - package-ecosystem: "docker"
    directory: "/infra/docker"
    schedule:
      interval: "monthly"
```

## 6. Sorumluluklar

| Rol | Sorumluluk |
|-----|-----------|
| Backend Dev | Python paket güncelleme ve test |
| Frontend Dev | Node.js paket güncelleme ve test |
| DevOps | Docker image güncelleme, CI pipeline bakım |
| Tüm Ekip | Kritik güvenlik güncellemelerini takip |

## 7. Güncelleme Kaydı

Her güncelleme sonrası kayıt tutun:

| Tarih | Paket | Eski Versiyon | Yeni Versiyon | Neden | Kim |
|-------|-------|--------------|---------------|-------|-----|
| — | — | — | — | — | — |
