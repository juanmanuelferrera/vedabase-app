const CACHE_NAME = 'vedabase-v2.3.0';

const PRECACHE_URLS = [
  './',
  './index.html',
  './manifest.json',
  './font-control.js',
  './collapse-script.js',
  './vedabase-source/bg.html',
  './vedabase-source/cc1.html',
  './vedabase-source/cc2.html',
  './vedabase-source/cc3.html',
  './vedabase-source/kb.html',
  './vedabase-source/sb1.html',
  './vedabase-source/sb2.html',
  './vedabase-source/sb3.html',
  './vedabase-source/other.html',
  './vedabase-source/lec1a.html',
  './vedabase-source/lec1b.html',
  './vedabase-source/lec1c.html',
  './vedabase-source/lec2a.html',
  './vedabase-source/lec2b.html',
  './vedabase-source/lec2c.html',
  './vedabase-source/conv1.html',
  './vedabase-source/conv2.html',
  './vedabase-source/conv3.html',
  './vedabase-source/missing_convs_pre1975.html',
  './vedabase-source/missing_convs_1975_1976.html',
  './vedabase-source/missing_convs_1977.html',
  './vedabase-source/let1.html',
  './vedabase-source/let2.html',
  './vedabase-source/let3.html',
  './vedabase-source/let4.html',
  './vedabase-source/collapse-script.js',
  './vedabase-source/font-control.js',
  './vedabase-source/css/htmlize.css',
  './vedabase-source/css/readtheorg.css',
  './vedabase-source/js/bootstrap.min.js',
  './vedabase-source/js/jquery.min.js',
  './vedabase-source/js/jquery.stickytableheaders.min.js',
  './vedabase-source/js/readtheorg.js',
  './vedabase-source/js/search.js'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const url = event.request.url;
  // Network-first for HTML files (ensures corrections are picked up)
  if (url.endsWith('.html') || url.endsWith('/')) {
    event.respondWith(
      fetch(event.request).then(response => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for static assets (JS, CSS, images)
    event.respondWith(
      caches.match(event.request).then(cached => {
        if (cached) return cached;
        return fetch(event.request).then(response => {
          if (!response || response.status !== 200 || response.type !== 'basic') return response;
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        });
      })
    );
  }
});
