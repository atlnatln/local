# Webimar Analytics System

## 📊 Genel Bakış

Webimar platformu için kapsamlı analytics ve tracking sistemi. **Tüm ziyaretçiler** (giriş yapmış ve anonim) için:
- Sayfa görüntüleme tracking
- Kullanıcı etkileşimi tracking (buton tıklama, form submit vb.)
- Hesaplama geçmişi (authenticated users için)
- Platform/browser/OS analytics

## 🏗️ Mimari

### Backend (Django)

#### Modeller (`calculations/models.py`)

1. **PageView** - Sayfa görüntüleme kayıtları
   - Session tracking
   - IP, user agent, device fingerprint
   - Platform, browser, OS tespiti
   - Performans metrikleri (load time, time on page)
   - Coğrafi bilgiler (country, city)

2. **UserInteraction** - Kullanıcı etkileşimleri
   - Click, form_submit, search, filter, scroll vb.
   - Element bilgileri (id, class, text)
   - Page context
   - Metadata (JSON)

3. **CalculationHistory** - Hesaplama geçmişi (sadece authenticated users)
   - Calculation type
   - Parameters & results
   - Map coordinates
   - Success/error tracking

4. **CalculationLog** - Tüm hesaplama logları (security & analytics)
   - Automatic logging via middleware
   - IP tracking
   - Limit tracking
   - Error logging

#### API Endpoints (`calculations/views/analytics.py`)

```
POST /api/calculations/analytics/page-view/
POST /api/calculations/analytics/interaction/
POST /api/calculations/analytics/time-on-page/
```

**Request Examples:**

```javascript
// Page view
{
  "session_id": "session_abc123",
  "path": "/sera",
  "page_title": "Sera Hesaplama",
  "referrer": "https://google.com",
  "platform": "desktop",
  "browser": "Chrome",
  "os": "Windows",
  "load_time": 1250
}

// Interaction
{
  "session_id": "session_abc123",
  "interaction_type": "click",
  "element_id": "calculate-button",
  "element_text": "Hesapla",
  "page_path": "/sera",
  "metadata": {"calculation_type": "sera"}
}
```

### Frontend (React & Next.js)

#### Analytics Library (`utils/analytics.js`)

**Features:**
- Automatic session management
- Platform/browser/OS detection
- Page view tracking
- Interaction tracking helpers
- Unload/visibility tracking
- Beacon API support

**Usage:**

```javascript
import { getAnalytics } from '@/utils/analytics';

const analytics = getAnalytics();

// Track page view (automatic with hook)
analytics.trackPageView('/sera', 'Sera Hesaplama');

// Track button click
analytics.trackButtonClick('calculate-btn', 'Hesapla');

// Track form submit
analytics.trackFormSubmit('sera-form', { alan: 5000 });

// Track search
analytics.trackSearch('zeytinyağı');

// Track filter
analytics.trackFilter('arazi_tipi', 'baglik');
```

#### React Hook (`hooks/useAnalytics.js`)

```javascript
import { usePageTracking, useAnalytics } from '@/hooks/useAnalytics';

function App() {
  // Automatic page tracking on route change
  usePageTracking();
  
  return <Router>{/* ... */}</Router>;
}

function MyComponent() {
  const analytics = useAnalytics();
  
  const handleClick = () => {
    analytics.trackButtonClick('my-button', 'Click me');
  };
  
  return <button onClick={handleClick}>Click me</button>;
}
```

#### Next.js Hook (App Router)

```javascript
'use client';
import { usePageTracking } from '@/hooks/useAnalytics';

export default function RootLayout({ children }) {
  usePageTracking(); // Automatic tracking
  return <html>{children}</html>;
}
```

## 🚀 Kurulum

### Backend

1. **Migration çalıştır:**
```bash
docker exec webimar-api python manage.py migrate
```

2. **Admin panelde görüntüleme (opsiyonel):**
```python
# calculations/admin.py
from .models import PageView, UserInteraction

admin.site.register(PageView)
admin.site.register(UserInteraction)
```

### Frontend (React)

1. **Analytics import:**
```javascript
import { getAnalytics } from './utils/analytics';
```

2. **App.tsx'de initialize:**
```javascript
import { usePageTracking } from './hooks/useAnalytics';

function App() {
  usePageTracking(); // Router değişikliklerini otomatik track eder
  // ...
}
```

### Frontend (Next.js)

1. **Root layout'ta initialize:**
```javascript
// app/layout.tsx
'use client';
import { usePageTracking } from '@/hooks/useAnalytics';

export default function RootLayout({ children }) {
  usePageTracking();
  return <html>{children}</html>;
}
```

## 📈 Analytics Queries

### Django ORM ile sorgulamalar:

```python
from calculations.models import PageView, UserInteraction
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

# Son 24 saatte en çok görüntülenen sayfalar
PageView.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=1)
).values('path').annotate(
    views=Count('id')
).order_by('-views')[:10]

# Platform dağılımı
PageView.objects.values('platform').annotate(
    count=Count('id')
).order_by('-count')

# Kullanıcı etkileşimleri (son 7 gün)
UserInteraction.objects.filter(
    created_at__gte=timezone.now() - timedelta(days=7)
).values('interaction_type').annotate(
    count=Count('id')
).order_by('-count')

# Session başına ortalama sayfa görüntüleme
from django.db.models import Avg
PageView.objects.values('session_id').annotate(
    page_count=Count('id')
).aggregate(Avg('page_count'))

# Hesaplama geçmişi (authenticated users)
from calculations.models import CalculationHistory
CalculationHistory.objects.filter(
    user__isnull=False,
    created_at__gte=timezone.now() - timedelta(days=1)
).values('calculation_type').annotate(
    count=Count('id')
).order_by('-count')
```

## 🔍 Monitoring & Reports

### Günlük Raporlar

```python
# scripts/daily_analytics_report.py
from calculations.models import PageView, UserInteraction
from django.utils import timezone
from datetime import timedelta

def generate_daily_report():
    yesterday = timezone.now() - timedelta(days=1)
    
    # Toplam page views
    total_views = PageView.objects.filter(created_at__gte=yesterday).count()
    
    # Unique visitors (by session)
    unique_sessions = PageView.objects.filter(
        created_at__gte=yesterday
    ).values('session_id').distinct().count()
    
    # Top pages
    top_pages = PageView.objects.filter(
        created_at__gte=yesterday
    ).values('path').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top interactions
    top_interactions = UserInteraction.objects.filter(
        created_at__gte=yesterday
    ).values('interaction_type', 'page_path').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return {
        'total_views': total_views,
        'unique_sessions': unique_sessions,
        'top_pages': list(top_pages),
        'top_interactions': list(top_interactions)
    }
```

## 📝 Best Practices

1. **Privacy Compliance:**
   - Session ID kullanımı (cookie-less tracking mümkün)
   - IP anonimization option eklenebilir
   - GDPR/KVKK compliance için user consent mekanizması

2. **Performance:**
   - Analytics calls async (non-blocking)
   - Batch operations için beacon API
   - Database indexes mevcut

3. **Data Retention:**
   - Eski kayıtları periyodik temizleme:
   ```python
   # 6 aydan eski page views
   PageView.objects.filter(
       created_at__lt=timezone.now() - timedelta(days=180)
   ).delete()
   ```

4. **Error Handling:**
   - Frontend: Console error, silent fail
   - Backend: Logging, graceful degradation

## 🔧 Troubleshooting

### Analytics çalışmıyor

1. **Backend kontrol:**
```bash
docker exec webimar-api python manage.py shell
>>> from calculations.models import PageView
>>> PageView.objects.count()
```

2. **Network kontrol (Browser DevTools):**
   - Network tab'de `/api/calculations/analytics/` requests
   - Status code 201 OK?

3. **CORS issues:**
```python
# webimar-api/webimar/settings.py
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',  # React
    'http://localhost:3001',  # Next.js
]
```

### Session tracking issues

- SessionStorage kullanılıyor, incognito'da her seferinde yeni session
- Persistent tracking için localStorage kullanılabilir

## 📚 Referanslar

- Django Models: `/webimar-api/calculations/models.py`
- API Views: `/webimar-api/calculations/views/analytics.py`
- Frontend Library: `/webimar-react/src/utils/analytics.js`
- React Hook: `/webimar-react/src/hooks/useAnalytics.js`
- Next.js Hook: `/webimar-nextjs/src/hooks/useAnalytics.js`

---

**Oluşturulma Tarihi:** 2025-12-20  
**Versiyon:** 1.0.0  
**Sorumlular:** Analytics & Tracking Implementation
