---
name: api
description: Describe when to use this prompt
---
Plan: Anka local Google erişimi
Kısa teşhis: Anka’da bugün itibarıyla local geliştirme için otomatik bir “local → VPS egress köprüsü” yok. Google Places çağrıları backend’den Google’a doğrudan çıkıyor; bu nedenle key yalnız VPS IP’sine kısıtlıysa local backend veya local Docker backend büyük olasılıkla çalışmaz. Buna karşılık repoda zaten SSH tunnel tabanlı bir yaklaşım tanımlı; ancak bu yaklaşım local backend’i VPS IP’sinden internete çıkarmıyor, local makineden VPS üzerindeki çalışan servisleri tüketmeye yarıyor. Seçtiğiniz hedefe göre en düşük riskli yön, local frontend + VPS backend modelini dev-local.sh ve dev-docker.sh içine görünür ve kontrollü biçimde entegre etmek.

Mevcut durum teşhisi

Native local akış, .env.local.native dosyasını .env olarak bağlayıp Django’yu doğrudan localde çalıştırıyor; burada Google egress’i VPS üzerinden yönlendiren bir adım yok. Kanıt: dev-local.sh:57-65, dev-local.sh:103.
Docker local akış, .env.local.docker ile compose başlatıyor; burada da tunnel veya proxy entegrasyonu yok. Kanıt: dev-docker.sh:35, dev-docker.sh:57, dev-docker.sh:88-96.
GooglePlacesClient, X-Goog-Api-Key ile Google Places’a doğrudan HTTP çağrısı yapıyor; yani backend’in dış ağ çıkışı kritik. Kanıt: google_places.py:10-21, base.py:16, base.py:29-30.
Frontend tarafında /api/* sadece backend’e rewrite ediliyor; Google’a özel bir proxy yok. Kanıt: next.config.ts:7, next.config.ts:24-25.
Harita alanı seçimi browser-side Google Maps JS ile çalışıyor ve NEXT_PUBLIC_GOOGLE_MAPS_API_KEY bekliyor. Native env’de bu var; Docker local hattında compose içine taşınmamış görünüyor. Kanıt: .env.local.native:21-29, .env.local.docker:21-39, docker-compose.yml:173-184, MapAreaSelector.tsx:75, MapAreaSelector.tsx:195.
Google Login da browser-side çalışıyor; bunun local çalışması GCP tarafında localhost origin/redirect izinlerine bağlı. Kanıt: projects/anka/services/frontend/app/(auth)/login/page.tsx/login/page.tsx#L51-L60), projects/anka/services/frontend/app/(auth)/login/page.tsx/login/page.tsx#L82).
Repo dokümantasyonu zaten “Google key’leri IP kısıtlıdır” diyor ve önerilen model olarak SSH tunnel ile VPS backend kullanımını tarif ediyor. Kanıt: secure-local-vps-access.md:11, secure-local-vps-access.md:75-80, secure-vps-tunnel.sh:1-48.
Steps

Hedef akışı “local frontend + VPS backend” olarak standartlaştır: dev-local.sh ve dev-docker.sh için ayrı bir tunnel-aware mod tasarla. Ana odak dosyalar: dev-local.sh, dev-docker.sh, secure-vps-tunnel.sh.
Native local akışta Djangoyı local başlatmak yerine opsiyonel olarak atlayan, frontend’i local ayağa kaldıran ve NEXT_PUBLIC_API_URL, NEXT_PUBLIC_API_BASE_URL, gerekirse NEXT_INTERNAL_BACKEND_URL değerlerini tunnel portuna yönlendiren bir plan hazırla. İlgili yapı: dev-local.sh:103, next.config.ts:7-25.
Docker akışında frontend container’ını localde tutup backend’i VPS tunnel üzerinden tüketme seçeneğini tasarla; burada compose env haritasına NEXT_PUBLIC_GOOGLE_MAPS_API_KEY eksikliği de dahil edilerek local Docker’ın browser-side Maps kullanımını bozmayacak bir düzen öner. İlgili yapı: docker-compose.yml:79-80, docker-compose.yml:173-184.
Google Places için local backend çalıştırma yerine “VPS backend’i tüket” kararını dokümante et; çünkü GooglePlacesClient doğrudan Google’a çıktığı için SSH local port-forward bunu tek başına çözmez. İlgili sembol: GooglePlacesClient içinde google_places.py:10-21.
Browser-side Google yüzeylerini ayrı değerlendir: Maps için NEXT_PUBLIC_GOOGLE_MAPS_API_KEY dev Docker hattına açıkça taşınmalı; Login için localhost izinleri dokümana kontrol maddesi olarak eklenmeli. İlgili dosyalar: MapAreaSelector.tsx:75, projects/anka/services/frontend/app/(auth)/login/page.tsx/login/page.tsx#L51-L60).
Runbook’u tek kaynak haline getir: seçilen geliştirme akışını secure-local-vps-access.md içine dev-local.sh ve dev-docker.sh senaryolarıyla güncelleyecek bir uygulama planı çıkar.
Test ve E2E akışında BACKEND_URL varsayılanlarının VPS tunnel senaryosuyla uyumlu hale getirilmesini planla; aksi halde testler local backend’e gitmeye devam eder. İlgili dosya: auth.ts:3-11.
Verification

Native senaryo doğrulaması: dev-local.sh ile local frontend açıldığında /api/health/ çağrısının tunnel portundan VPS backend’e gitmesi.
Docker senaryo doğrulaması: dev-docker.sh ile local frontend container açıldığında aynı health kontrolünün VPS backend’e gitmesi.
Places doğrulaması: batch/pipeline akışında 403 veya IP restriction hatası alınmaması.
Maps doğrulaması: harita bileşeninin key eksikliği hatası vermemesi; referans bileşen MapAreaSelector.tsx:75.
Login doğrulaması: Google giriş script’inin localde yüklenmesi ve redirect/origin uyumsuzluğu oluşturmaması; referans projects/anka/services/frontend/app/(auth)/login/page.tsx/login/page.tsx#L51-L60).
Decisions

Seçilen yön: SSH tunnel temelli yaklaşım.
Seçilen geliştirme modeli: local frontend + VPS backend.
Kaçınılacak yön: local backend’i Google’a VPS IP’si üzerinden çıkarmaya çalışan yeni egress/proxy mimarisi.
Öncelik: mevcut ayarları bozmadan dev-local.sh ve dev-docker.sh için tunnel-aware çalışma modu tanımlamak.