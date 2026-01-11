# Google Search Console - Teknik İmplementasyon Rehberi

## 🚀 Hızlı Başlangıç (1. Gün İçinde Yapılacak)

### Adım 1: Core Web Vitals INP Sorunu - React Component Profiling

**Sorunlu Sayfa:** `https://tarimimar.com.tr/sigir-ahiri-kapasite-hesaplama/`

```bash
# 1. Projeyi native ortamda başlat
cd /home/akn/Genel/webimar
./dev-local.sh

# 2. Chrome DevTools'ü aç
# URL: http://localhost:3001/sigir-ahiri-kapasite-hesaplama/
# Performance tab → Record → Formda hesaplama yap

# 3. React Profiler'ı kullan
# Components tab → Profiler → İşaretli render'ları gör
# Hangi component 200ms+ sürüyor?
```

**Teşhis Adımları:**
```javascript
// webimar-react/src/components/CalculationForm.tsx içine ekle (debug amaçlı)
console.time('calculateResult');
const result = calculateSigirAhiri(inputs);
console.timeEnd('calculateResult');

// Output örneği:
// calculateResult: 150ms ← Sorun burada!
```

### Adım 2: Yönlendirmeli Sayfaları Tanımla

**Search Console'da:**
1. [Index Coverage Raporu](https://search.google.com/search-console/index?resource_id=sc-domain%3Atarimimar.com.tr) aç
2. Filtre: "Dizine Eklenmedi" → "Yönlendirmeli Sayfa" (45 adet)
3. Tabloyu CSV'ye export et

```bash
# Terminal'de export edilen CSV'yi analiz et
cat redirects.csv | cut -d',' -f2 | sort | uniq > unique_redirects.txt

# Her yönlendirmenin nereden geldiğini bul
while IFS= read -r url; do
  echo "=== $url ==="
  curl -I "$url" 2>/dev/null | head -1
done < unique_redirects.txt
```

### Adım 3: nginx.conf'da Yönlendirmelerini Düzelt

**Dosya:** [docker/nginx/nginx.conf](docker/nginx/nginx.conf)

```nginx
# ❌ AYLAR ÖNCEKI KOD (Silinmiş sayfalar hala yönlendiriliyor)
location ~ ^/hesaplama/(.*) {
  rewrite ^/hesaplama/(.*)$ /$1 permanent;  # İkinci yönlendirme!
}

# ✅ DOĞRU KOD (Direktmen canonical URL'ye yönlendir)
location ~ ^/hesaplama/(.*) {
  rewrite ^/hesaplama/(.*)$ /api/calculations/$1 permanent;
}
```

**Kontrol:**
```bash
curl -I https://tarimimar.com.tr/hesaplama/sera/
# HTTP/1.1 301 Moved Permanently
# Location: /api/calculations/sera/  ✅ İyi

curl -I https://tarimimar.com.tr/api/calculations/sera/
# HTTP/1.1 200 OK  ✅ Final destination bulundu
```

---

## 🔧 Haftanın Teknik Yapılacaklar

### Pazartesi: INP Optimizasyonuna Başla

**Görev 1: React Bundle Analiz**
```bash
cd webimar-react

# Bundle boyutunu görmek
npm run build
npm install --save-dev webpack-bundle-analyzer
# webpack.config.js'e ekle: new BundleAnalyzerPlugin()

# Sonuç:
# - Hangi package'lar büyük?
# - Lazy-load edilebilir mi?
```

**Görev 2: Ağır Hesaplamaları Web Worker'a Taşı**
```typescript
// webimar-react/src/workers/calculationWorker.ts (YENİ DOSYA)
self.onmessage = (event: MessageEvent) => {
  const { inputs, structureType } = event.data;
  
  // Burada ağır hesaplama yap (main thread bloklanmaz)
  const result = calculateStructure(inputs, structureType);
  
  self.postMessage(result);
};

// webimar-react/src/hooks/useCalculationWorker.ts (YENİ DOSYA)
import { useRef, useCallback } from 'react';

export function useCalculationWorker() {
  const workerRef = useRef<Worker | null>(null);

  const calculate = useCallback((inputs: any, structureType: string) => {
    if (!workerRef.current) {
      workerRef.current = new Worker(
        new URL('../workers/calculationWorker.ts', import.meta.url),
        { type: 'module' }
      );
    }

    return new Promise((resolve) => {
      workerRef.current!.onmessage = (e) => resolve(e.data);
      workerRef.current!.postMessage({ inputs, structureType });
    });
  }, []);

  return { calculate };
}
```

**Görev 3: Form Input'lara Debounce Ekle**
```typescript
// webimar-react/src/hooks/useDebouncedState.ts (YENİ DOSYA)
import { useState, useCallback } from 'react';

export function useDebouncedState<T>(initialValue: T, delay: number = 300) {
  const [value, setValue] = useState<T>(initialValue);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const setDebouncedValue = useCallback((newValue: T) => {
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => {
      setValue(newValue);
    }, delay);
  }, [delay]);

  return [value, setDebouncedValue] as const;
}

// Kullanım:
const [inputs, setInputs] = useDebouncedState({ alan_m2: '' }, 500);
const handleInputChange = (e) => {
  setInputs({ ...inputs, [e.target.name]: e.target.value });
  // Her input değişikliğinde re-render değil, 500ms sonra
};
```

### Salı: Index Coverage Sorunlarını Çöz

**Görev 1: 26 × 404 URL'i Tespit Et**
```bash
# Search Console'dan export et: index-not-covered.csv

# Django'da 404 log'larını kontrol et
docker logs webimar-api --tail 1000 | grep "404" | head -20

# Problematik API endpoint'leri bul
python webimar-api/manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> for pattern in resolver.url_patterns:
...     if 'sigir' in str(pattern):
...         print(pattern)
```

**Görev 2: Dead URL'leri Tekrar Yönlendir veya Sil**
```python
# webimar-api/utils/redirect_manager.py (YENİ DOSYA)
from django.views.decorators.http import require_http_methods
from django.http import HttpResponsePermanentRedirect

REDIRECT_MAP = {
    '/hesaplama/sigir-ahiri/': '/sigir-ahiri-kapasite-hesaplama/',
    '/documents/old-file/': '/documents/tarim-arazileri-kullanimi-genelgesi/',
    # Diğer 404'ler...
}

@require_http_methods(["GET"])
def redirect_legacy_url(request, old_path):
    if old_path in REDIRECT_MAP:
        return HttpResponsePermanentRedirect(REDIRECT_MAP[old_path])
    return HttpResponse(status=410)  # Gone (silinmiş)

# urls.py'ye ekle
urlpatterns = [
    ...
    path('old/<path:old_path>', redirect_legacy_url, name='legacy_redirect'),
]
```

**Görev 3: Sitemap.xml'i Güncelle**
```python
# webimar-api/management/commands/generate_sitemap.py (GÜNCELLE)
from django.core.management.base import BaseCommand
from django.urls import reverse
import xml.etree.ElementTree as ET

class Command(BaseCommand):
    def handle(self, *args, **options):
        urls = []
        
        # Yalnızca live sayfaları ekle
        for page in Page.objects.filter(status='live', is_deleted=False):
            urls.append({
                'loc': f'https://tarimimar.com.tr{page.get_absolute_url()}',
                'lastmod': page.updated_at.isoformat(),
                'changefreq': 'monthly',
                'priority': '0.8' if page.is_featured else '0.5'
            })

        # XML oluştur
        urlset = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')
        for url in urls:
            url_elem = ET.SubElement(urlset, 'url')
            ET.SubElement(url_elem, 'loc').text = url['loc']
            ET.SubElement(url_elem, 'lastmod').text = url['lastmod']
            ET.SubElement(url_elem, 'changefreq').text = url['changefreq']
            ET.SubElement(url_elem, 'priority').text = url['priority']

        tree = ET.ElementTree(urlset)
        tree.write('/app/static/sitemap.xml', encoding='utf-8', xml_declaration=True)

# Günlük çalışacak şekilde schedule et (Celery)
# webimar-api/celery.py
from celery.schedules import crontab

app.conf.beat_schedule = {
    'generate-sitemap': {
        'task': 'tarimsal_yapilar.tasks.generate_sitemap',
        'schedule': crontab(hour=0, minute=0),  # Her gün saat 00:00
    },
}
```

### Çarşamba: Veritabanı Optimizasyonu

**Görev 1: Redis Cache'i Kur**
```python
# webimar-api/settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
        }
    }
}

# Cache time-out'ları
CACHE_TIMEOUT_CALCULATION = 86400  # 24 saat
CACHE_TIMEOUT_CONFIG = 604800  # 7 gün
```

**Görev 2: ORM Query'lerini Optimize Et**
```python
# webimar-api/tarimsal_yapilar/views.py

# ❌ AYLAR ÖNCESI (N+1 problem)
@api_view(['POST'])
def calculate_structure(request):
    structures = Structure.objects.all()
    for struct in structures:
        regulations = struct.regulations.all()  # ← N queries!

# ✅ DÜZELTME
from django.db.models import Prefetch

@api_view(['POST'])
def calculate_structure(request):
    structures = Structure.objects.prefetch_related(
        Prefetch('regulations')
    ).select_related('category').all()  # ← 1 query!
    
    # Ek olarak cache kullan
    cache_key = f'structures_{request.data.get("type")}'
    if cache_key in cache:
        return Response(cache.get(cache_key))
    
    # ... hesaplama ...
    cache.set(cache_key, result, CACHE_TIMEOUT_CALCULATION)
    return Response(result)
```

**Görev 3: Slow Query Logging**
```python
# webimar-api/settings.py
import logging

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'slow_queries.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Sonra loglara bak
docker exec webimar-api tail -f /app/slow_queries.log | grep "took"
```

---

## 🧪 Test Planı

### Performance Test (Lighthouse CI)

```bash
# webimar-react/.github/workflows/lighthouse.yml (YENİ)
name: Lighthouse CI

on: [pull_request, push]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci && npm run build
      - uses: treosh/lighthouse-ci-action@v9
        with:
          configPath: './lighthouserc.json'
          uploadArtifacts: true

# lighthouserc.json (YENİ)
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["http://localhost:3001/sigir-ahiri-kapasite-hesaplama/"]
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "metrics:interaction-to-next-paint": ["error", {"maxNumericValue": 200}]
      }
    }
  }
}
```

### Unit Test - INP Optimizasyonu

```typescript
// webimar-react/src/hooks/useCalculationWorker.test.ts (YENİ)
import { renderHook, act } from '@testing-library/react';
import { useCalculationWorker } from './useCalculationWorker';

describe('useCalculationWorker', () => {
  it('should not block main thread during calculation', async () => {
    const { result } = renderHook(() => useCalculationWorker());
    
    const startTime = performance.now();
    const promise = result.current.calculate(
      { alan_m2: 5000, arazi_tipi: 'tarla' },
      'sigir-ahiri'
    );
    const afterPostTime = performance.now();
    
    // Main thread'in block olmadığını kontrol et
    expect(afterPostTime - startTime).toBeLessThan(10); // ← <10ms
    
    const calcResult = await promise;
    expect(calcResult.uygun).toBeDefined();
  });
});
```

---

## 📊 Deployment Adımları

### Lokalde Test Et

```bash
# 1. Development docker ortamında test et
./dev-docker.sh

# 2. Tarayıcıda sorunlu sayfayı aç
# http://localhost:3001/sigir-ahiri-kapasite-hesaplama/

# 3. Performance measurement
# Chrome DevTools → Performance → Record
# Herhangi bir form input'u değiştir
# Rendering'in ne kadar sürdüğünü kontrol et (Target: <200ms)

# 4. Network speed'i sınırla (3G simulate)
# Chrome DevTools → Network → "Throttling" → "Slow 3G"
```

### Production'a Deploy Et

```bash
# 1. Commitleri yapıştır
git add -A
git commit -m "fix: INP optimization for mobile calculators

- Implement Web Worker for heavy calculations
- Add debouncing to form inputs
- Optimize React renders with useMemo
- Remove unnecessary state updates

Fixes: INP > 200ms on /sigir-ahiri-kapasite-hesaplama/
Metrics: INP 203ms → 150ms (target: <200ms)"

# 2. Push et
git push origin main

# 3. VPS'de pull et
ssh user@vps "cd /var/www/webimar && git pull"

# 4. Docker rebuild et
docker compose -f docker-compose.prod.yml up -d --build webimar-react

# 5. Monitoring'i kontrol et
docker logs webimar-react --tail 50 | grep -i "error"
```

---

## 🔍 Monitoring ve Uyarılar

### Google Search Console API ile Günlük Rapor

```python
# webimar-api/management/commands/daily_seo_check.py (YENİ)
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Google Search Console API bağlantısı
        credentials = Credentials.from_service_account_file('gsc-credentials.json')
        service = build('searchconsole', 'v1', credentials=credentials)
        
        # Core Web Vitals verilerini çek
        request = {
            'startDate': '2026-01-01',
            'endDate': '2026-01-04',
            'dimensions': ['DATE', 'DEVICE'],
            'metrics': ['CLICKS', 'IMPRESSIONS', 'CTR', 'POSITION']
        }
        
        response = service.searchanalytics().query(
            siteUrl='sc-domain:tarimimar.com.tr',
            body=request
        ).execute()
        
        # INP değerleri kontrol et
        mobile_ctr = sum([r['clicks'] for r in response['rows'] if 'MOBILE' in r['dimensions']])
        
        # Slack'e bildir
        if mobile_ctr < ALERT_THRESHOLD:
            send_slack_alert(f"⚠️ Mobile CTR dropped to {mobile_ctr}")
        
        self.stdout.write('✓ Daily SEO check completed')

# Crontab'a ekle
# 0 9 * * * python /app/manage.py daily_seo_check
```

### Slack Webhook

```python
# webimar-api/utils/slack_notifier.py (YENİ)
import requests

def send_slack_alert(message: str, severity: str = 'warning'):
    color = {
        'error': '#FF0000',
        'warning': '#FFA500',
        'success': '#00FF00'
    }.get(severity, '#0099FF')
    
    payload = {
        'attachments': [{
            'color': color,
            'title': 'SEO Alert - tarimimar.com.tr',
            'text': message,
            'footer': 'Google Search Console',
            'ts': int(time.time())
        }]
    }
    
    requests.post(os.getenv('SLACK_WEBHOOK_URL'), json=payload)
```

---

## 📋 Yönetici Kontrol Listesi

- [ ] **Week 1**
  - [ ] INP profiling başlandı
  - [ ] 45 yönlendirme analiz edildi
  - [ ] 26 × 404 URL düzeltildi
  
- [ ] **Week 2**
  - [ ] Web Worker implementasyonu tamamlandı
  - [ ] Canonical tag'ler eklendi (33 sayfa)
  - [ ] Redis cache deploy edildi
  
- [ ] **Week 3**
  - [ ] Lighthouse CI setup edildi
  - [ ] Query optimizasyonu yapıldı
  - [ ] INP < 200ms oldu ✓
  
- [ ] **Week 4+**
  - [ ] Sitemap otomasyonu çalışıyor
  - [ ] Günlük SEO monitoring aktif
  - [ ] Yanıt süresi 629ms → <200ms ✓

---

*Son Güncelleme: 4 Ocak 2026*
