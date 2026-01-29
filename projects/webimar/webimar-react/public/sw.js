// Performance-optimized Service Worker for Webimar
const CACHE_NAME = 'webimar-performance-v1';
const STATIC_ASSETS = [
  '/leaflet.css',
  '/manifest.json',
  '/favicon.ico',
];

// Install event - Cache critical resources
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Activate event - Clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Claim all clients immediately
  self.clients.claim();
});

// Fetch event - Serve from cache with network fallback
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;
  
  // Skip non-HTTP(S) requests
  if (!event.request.url.match(/^https?:/)) return;
  
  event.respondWith(
    caches.match(event.request).then((response) => {
      // Return cached version or fetch from network
      return response || fetch(event.request).then((fetchResponse) => {
        // Cache successful responses for static assets
        if (fetchResponse.ok && STATIC_ASSETS.some(asset => event.request.url.includes(asset))) {
          const responseClone = fetchResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return fetchResponse;
      });
    }).catch(() => {
      // Fallback for offline scenarios
      if (event.request.destination === 'document') {
        return new Response('Offline page would go here', {
          headers: { 'Content-Type': 'text/html' }
        });
      }
    })
  );
});