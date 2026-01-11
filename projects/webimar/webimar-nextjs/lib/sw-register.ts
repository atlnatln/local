// Service Worker Unregistration
// React SPA ile çakışmayı önlemek için tüm SW'leri temizle
if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // Tüm mevcut SW'leri unregister et
    navigator.serviceWorker.getRegistrations().then((registrations) => {
      registrations.forEach((registration) => {
        registration.unregister();
        console.log('🧹 Next.js SW unregistered:', registration.scope);
      });
    });

    // Cache'leri temizle
    if ('caches' in window) {
      caches.keys().then((cacheNames) => {
        cacheNames.forEach((cacheName) => {
          caches.delete(cacheName);
          console.log('🧹 Next.js cache cleared:', cacheName);
        });
      });
    }
  });
}
