// Service Worker for Tarım İmar
const CACHE_NAME = 'tarim-imar-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
  '/favicon.svg'
];

// Install event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
  // Force the waiting service worker to become the active service worker
  self.skipWaiting();
});

// Activate event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // Take control of all pages immediately
  self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  // Handle font requests with cache-first strategy
  if (event.request.url.includes('fonts.googleapis.com') ||
      event.request.url.includes('fonts.gstatic.com')) {
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          if (response) {
            return response;
          }
          return fetch(event.request)
            .then((response) => {
              // Cache the response
              const responseClone = response.clone();
              caches.open('fonts-cache-v1')
                .then((cache) => {
                  cache.put(event.request, responseClone);
                });
              return response;
            });
        })
    );
    return;
  }

  // Handle image requests with cache-first strategy
  if (event.request.url.match(/\.(png|jpg|jpeg|svg|gif|webp)$/)) {
    event.respondWith(
      caches.match(event.request)
        .then((response) => {
          if (response) {
            return response;
          }
          return fetch(event.request)
            .then((response) => {
              if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
              }
              const responseClone = response.clone();
              caches.open('images-cache-v1')
                .then((cache) => {
                  cache.put(event.request, responseClone);
                });
              return response;
            });
        })
    );
    return;
  }

  // Default network-first strategy for other requests
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Don't cache non-successful responses
        if (!response || response.status !== 200 || response.type !== 'basic') {
          return response;
        }

        // Cache successful responses
        const responseClone = response.clone();
        caches.open(CACHE_NAME)
          .then((cache) => {
            cache.put(event.request, responseClone);
          });

        return response;
      })
      .catch(() => {
        // Return cached version if network fails
        return caches.match(event.request);
      })
  );
});
