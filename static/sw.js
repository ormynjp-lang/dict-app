const CACHE_NAME = 'ormyn-pwa-v1';
const urlsToCache = [
  '/',
  '/dictionary',
  '/quiz',
  '/demo',
  '/blog',
  '/look',
  '/flashcards',
  '/diary',
  '/about',
  '/contact'
];

// Sayfaları önbelleğe al
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

// İnternet yoksa önbellekten sun
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .catch(() => caches.match(event.request))
  );
});