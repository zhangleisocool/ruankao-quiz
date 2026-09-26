/* Service Worker:缓存应用外壳,离线可刷题。
   注意:每次发布新版本时把 CACHE 版本号 +1,客户端下次打开会自动换新缓存。 */
var CACHE = "ruankao-quiz-v3";
var ASSETS = [
  "./",
  "./index.html",
  "./data/bank.js",
  "./manifest.webmanifest",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-180.png",
  "./icons/icon-32.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(caches.open(CACHE).then(function (c) { return c.addAll(ASSETS); }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); }));
    }).then(function () { return self.clients.claim(); })
  );
});

/* stale-while-revalidate:优先用缓存秒开,后台拉新版更新缓存 */
self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;
  e.respondWith(
    caches.match(req, { ignoreSearch: req.mode === "navigate" }).then(function (cached) {
      var network = fetch(req).then(function (res) {
        if (res && res.ok && new URL(req.url).origin === location.origin) {
          var copy = res.clone();
          caches.open(CACHE).then(function (c) { c.put(req, copy); });
        }
        return res;
      }).catch(function () { return cached; });
      return cached || network;
    })
  );
});
