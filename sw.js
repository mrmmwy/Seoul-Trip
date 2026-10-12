// 離線快取：第一次打開時存下頁面，之後沒網路也能用
const CACHE = 'seoul-trip-v40';
const FONTS = 'seoul-trip-fonts'; // 字型另外存，App 改版時不用重新下載
const CORE = ['./', './index.html', './manifest.webmanifest', './icon-180.png', './icon-192.png', './icon-512.png', './icon-maskable-512.png'];
const WAIT = 3000; // 網路太慢時，最多等這麼久就先顯示快取的版本
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE.map(u => new Request(u, { cache: 'reload' })))).then(() => self.skipWaiting()));
});
// 舊版快取裡的字型先搬到字型快取，再刪掉舊版快取
const keepFonts = k => caches.open(k).then(c => c.keys().then(reqs => Promise.all(reqs.filter(r => /fonts\.(googleapis|gstatic)\.com/.test(r.url))
  .map(r => c.match(r).then(res => res && caches.open(FONTS).then(f => f.put(r, res)))))));
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE && k !== FONTS)
    .map(k => keepFonts(k).catch(() => {}).then(() => caches.delete(k))))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  const isFont = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (url.origin !== location.origin && !isFont) return;
  // 頁面：有網路一律向伺服器確認最新版（不用瀏覽器暫存）；沒網路或等超過 WAIT 就先用快取，新版在背景存好，下次打開就是新版
  if (req.mode === 'navigate') {
    const net = fetch(req.url, { cache: 'no-cache' });
    e.waitUntil(net.then(res => {
      if (!res.ok) return;
      const copy = res.clone(); // 要在頁面讀取內容之前複製
      return caches.open(CACHE).then(c => c.put('./index.html', copy));
    }).catch(() => {}));
    e.respondWith(new Promise(resolve => {
      let done = false;
      const finish = res => { if (!done && res) { done = true; resolve(res); } };
      const cached = () => caches.match('./index.html');
      const timer = setTimeout(() => cached().then(finish), WAIT);
      net.then(res => { clearTimeout(timer); finish(res); })
        .catch(() => { clearTimeout(timer); cached().then(hit => finish(hit || Response.error())); });
    }));
    return;
  }
  // 字型與圖示：先用快取
  const store = isFont ? FONTS : CACHE;
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res.ok || res.type === 'opaque') { const copy = res.clone(); caches.open(store).then(c => c.put(req, copy)); }
    return res;
  })));
});
