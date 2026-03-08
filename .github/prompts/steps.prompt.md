---
name: webimar-auth-sync
description: Webimar authentication flow senkronizasyonu – JWT, localStorage, cookies ve legacy fallbacks arasındaki tutarsızlıkları gider
agent: planning
tags: [auth, refactor, production-critical]
---
Plan: Webimar auth senkronu
DRAFT — Production öncelikli incelemeye göre auth akışı şu anda tek bir kaynaktan yönetilmiyor; React, Next.js ve Django tarafında aynı oturum için birden fazla “doğruluk kaynağı” var: JWT/localStorage, webimar_auth_state, UI amaçlı cookie ve bazı legacy/fallback yollar. En riskli noktalar: Next tarafındaki legacy “fake token” senaryosu, React tarafındaki 5 saniyelik polling ile logout senkronu, Next account çıkışında cookie temizlenmemesi ve backend’de mail/şifre login route’u kapalıyken frontend’de hâlâ /api/token/ kullanan eski kodun duruyor olması. Bu yüzden sorun “rastgele” görünebilir; aslında aynı state farklı katmanlarda farklı okunuyor.

Steps

Auth sözleşmesini tekilleştir: hangi veri gerçekten oturumu temsil ediyor netleştir.

Mevcut akışı uçtan uca referans al: GoogleLoginButton.tsx:64-67, google_auth_views.py:31-45, google_auth_views.py:312-313, GoogleCallback.tsx:63-123, Layout.tsx:98-241.
Hedef: JWT + doğrulanmış user + tek senkron sinyali. Cookie yalnızca UI fallback ise bu açıkça sınırlandırılmalı; auth kanıtı gibi davranmamalı.
Next.js tarafındaki legacy/fallback auth yollarını sadeleştir.

Özellikle Layout içindeki checkUrlAuthParams() ve fake token yazımı kaldırılacak/izole edilecek: Layout.tsx:66-77.
authCookie === '1' ile kullanıcıyı “login” sayan fallback yeniden tasarlanacak: Layout.tsx:202-212.
fetchUserFromBackend() yalnızca gerçek access token ile çalışacak; sentinel değerler kabul edilmeyecek: Layout.tsx:24-54 ve Layout.tsx:186.
Logout davranışını iki frontend arasında birebir aynı hale getir.

React logout temizliği referans alınacak: AuthContext.tsx:564-609.
Next Layout logout ile Next account logout aynı kurala çekilecek; şu an account sayfası cookie temizlemiyor ve webimar_auth_state’i “false state” yerine siliyor: Layout.tsx:268-287, account.tsx:44-50.
Sonuç: her logout aynı anahtarları silsin, aynı cookie’leri temizlesin, aynı global auth-state’i yazsın.
React↔Next senkron mekanizmasını polling’den event-driven modele indir.

Şu an React tarafı 5 saniyede bir webimar_auth_state poll ediyor: AppLayout.tsx:608-634.
React zaten local event tetikliyor: tokenStorage.ts:12-57.
Plan: mümkünse storage + tek bir custom event katmanı kullanılacak; polling yalnızca son çare olacak. Böylece logout/login gecikmeli görünmeyecek.
Token yaşam döngüsünü yeniden hizala.

Backend’de /api/token/refresh/ açık, /api/token/ kapalı: urls.py:35-38.
React içinde kapalı route’a giden eski mail/şifre akışı hâlâ duruyor: AuthContext.tsx:353, authApi.ts:44.
Plan: kullanılmayan eski login akışı ya tamamen kaldırılacak ya da feature-flag/uyarı ile izole edilecek. Next tarafı için de access token süresi dolduğunda me → refresh → retry → hard logout zinciri netleştirilecek.
Google OAuth callback zincirini tek kanonik akışa indir.

Backend callback React SPA callback’e yönlendiriyor: google_auth_views.py:45.
React callback gerçek tokenları yazıp Next’e dönüyor: GoogleCallback.tsx:63-123.
Next callback de ayrıca token işleyebiliyor: callback.tsx:12-70.
Plan: production’da tek callback hattı kalacak. İkinci callback yalnızca migration/debug amaçlı ise ayrıştırılacak. Böylece çift işleme ve farklı state yazımı bitecek.
Backend auth semantiğini frontend beklentisiyle hizala.

handle_google_user() mevcut pasif kullanıcıyı otomatik aktif ediyor: google_auth_views.py:383-444.
logout endpoint’i Django UserSession kaydını pasifleştiriyor, fakat JWT invalidation yapmıyor: main_views.py:352-379, utils.py:168-188.
Plan: “logout gerçekten neyi bitiriyor?” net tanımlanacak. Eğer refresh blacklisting beklenecekse frontend ve backend birlikte güncellenecek.
Son olarak gözlenebilirlik ve hata ayıklama netleştirilecek.

webimar_auth_state yazımı, refresh başarısızlığı, cookie fallback kullanımı ve forced logout için sınırlı ama tutarlı log noktaları belirlenecek.
Hedef: “neden çıkmış göründü / neden login göründü” sorusu tek log zincirinden okunabilsin.
Verification

Google ile login → React’te hesap açık → Next ana sayfa/header hemen senkron.
Next’ten logout → aynı origin başka React sekmesi en fazla anlık event ile çıkmalı; 5 saniye beklememeli.
React’ten logout → Next header/account sayfası cookie fallback yüzünden tekrar login görünmemeli.
Access token expire senaryosu → me çağrısı başarısız olursa refresh denenmeli; refresh de başarısızsa temiz logout olmalı.
Hard refresh, yeni sekme, geri/ileri tarayıcı navigasyonu ve /account, /login, /hesaplama/account geçişleri ayrı ayrı test edilmeli.
Production domain üzerinde cookie/domain davranışı ayrıca doğrulanmalı.