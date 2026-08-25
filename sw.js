/* Service worker for the לונדון 2026 trip page.
   Goal: full offline use on spotty signal, installable to home screen. */

const VERSION = 'london-trip-v1';
const PRECACHE = VERSION + '-precache';
const RUNTIME = VERSION + '-runtime';

// Same-origin assets we want available offline. Relative paths so it works
// both locally and under the GitHub Pages subpath (/italy-trip/).
const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png',
  './icon-maskable-512.png',
  './apple-touch-icon.png',
  './preview.jpg',
  './docs/restaurant-confirmation.jpeg',
];

// Install: pre-cache the core assets. Each is fetched individually so one
// missing file (e.g. a doc that isn't there yet) doesn't fail the whole install.
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(PRECACHE).then((cache) =>
      Promise.all(
        PRECACHE_URLS.map((url) =>
          cache.add(new Request(url, { cache: 'reload' })).catch(() => null)
        )
      )
    ).then(() => self.skipWaiting())
  );
});

// Activate: drop caches from older versions.
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((k) => k !== PRECACHE && k !== RUNTIME)
          .map((k) => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Only handle GET; let everything else (POST/PUT to the notes API) pass through.
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Never touch the notes API (jsonbin) — it must always be live and never cached.
  if (url.hostname.endsWith('jsonbin.io')) return;

  // Never touch the exchange-rate API — always hit the network so the call is
  // fresh and visible in the Network tab on every refresh.
  if (url.hostname.endsWith('er-api.com')) return;

  // Navigations (the HTML page): network-first so edits show up, fall back to
  // the cached page when offline.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(PRECACHE).then((c) => c.put('./index.html', copy));
          return res;
        })
        .catch(() =>
          caches.match(req).then((r) => r || caches.match('./index.html'))
        )
    );
    return;
  }

  // Same-origin static assets: cache-first (fast + offline).
  if (url.origin === self.location.origin) {
    event.respondWith(
      caches.match(req).then(
        (cached) =>
          cached ||
          fetch(req).then((res) => {
            const copy = res.clone();
            caches.open(RUNTIME).then((c) => c.put(req, copy));
            return res;
          })
      )
    );
    return;
  }

  // Cross-origin (Google Fonts CSS + font files): stale-while-revalidate,
  // best-effort. Opaque responses are fine to store here.
  event.respondWith(
    caches.match(req).then((cached) => {
      const network = fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(RUNTIME).then((c) => c.put(req, copy));
          return res;
        })
        .catch(() => cached);
      return cached || network;
    })
  );
});
