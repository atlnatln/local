// Unregister all service workers to prevent caching issues
export function unregisterServiceWorker() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
        console.log('✅ Service Worker unregistered successfully');
      })
      .catch((error) => {
        console.error('❌ Service Worker unregistration error:', error);
      });
  }
}
