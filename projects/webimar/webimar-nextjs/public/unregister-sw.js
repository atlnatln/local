// Service Worker Temizleme Script'i
// Eski SW cache'lerini temizler ve tüm SW'leri unregister eder

(function() {
  'use strict';

  if ('serviceWorker' in navigator) {
    // Tüm kayıtlı SW'leri temizle
    navigator.serviceWorker.getRegistrations().then(function(registrations) {
      for (let registration of registrations) {
        registration.unregister();
        console.log('🧹 Service Worker unregistered:', registration.scope);
      }
    });

    // Cache'leri temizle
    if ('caches' in window) {
      caches.keys().then(function(names) {
        for (let name of names) {
          caches.delete(name);
          console.log('🧹 Cache cleared:', name);
        }
      });
    }
  }
})();
