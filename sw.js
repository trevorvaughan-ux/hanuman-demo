// Hani by HudsonSeed — service worker
// Caches the app shell so the app opens instantly and works offline after first load.
// Never caches Supabase requests (auth/data must always be live).
const CACHE_NAME = 'hani-shell-v2';
const SHELL_FILES = [
  'hanuman-menu.html',
  'whiteboard.html',
  'manifest.json',
  'icon-192.png',
  'icon-512.png',
  'icon-512-maskable.png',
  'apple-touch-icon.png',
  'hanuman-smiling.jpg',
  'hanuman-calm.jpg',
  'hanuman-kind.jpg',
  'hanuman-angry.jpg',
  'hanuman-sadgrief.jpg',
  'hanuman-pensive.jpg',
  'hanuman-surprised.jpg'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(SHELL_FILES))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((names) =>
      Promise.all(names.filter((n) => n !== CACHE_NAME).map((n) => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Never intercept Supabase (auth, data, RPC) — always go to network.
  if (url.hostname.endsWith('supabase.co')) return;

  // Only handle GET requests for same-origin shell files.
  if (event.request.method !== 'GET' || url.origin !== self.location.origin) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      const network = fetch(event.request)
        .then((response) => {
          if (response && response.ok) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => cached);
      // Cache-first for instant load, but still refresh in the background.
      return cached || network;
    })
  );
});
