/* VectorCraft community PWA service worker.
   Installs an offline shell and caches successfully loaded WASM/JS/fonts.
   Keeps requests scoped to the deployed GitHub Pages project. */
const CACHE = "vectorcraft-pwa-2026-10-v1";
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png"];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter(name => name.startsWith("vectorcraft-pwa-") && name !== CACHE)
      .map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const request = event.request;
  const url = new URL(request.url);
  const scopePath = new URL(self.registration.scope).pathname;
  if (request.method !== "GET" || url.origin !== self.location.origin
      || !url.pathname.startsWith(scopePath)) return;

  if (request.mode === "navigate") {
    event.respondWith((async () => {
      const cache = await caches.open(CACHE);
      try {
        const response = await fetch(request);
        if (response.ok) await cache.put("./index.html", response.clone());
        return response;
      } catch (error) {
        return await cache.match("./index.html") || Response.error();
      }
    })());
    return;
  }

  event.respondWith((async () => {
    const cache = await caches.open(CACHE);
    const saved = await cache.match(request);
    if (saved) return saved;
    const response = await fetch(request);
    if (response.ok && (response.type === "basic" || response.type === "cors")) {
      try { await cache.put(request, response.clone()); }
      catch (error) { console.warn("VectorCraft PWA: cache unavailable", error); }
    }
    return response;
  })());
});
