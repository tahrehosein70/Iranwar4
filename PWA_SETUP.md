# تبدیل بازی به PWA (Progressive Web App)

## مزایای PWA
- نصب مستقیم روی گوشی مانند اپلیکیشن
- کار آفلاین
- اشتراک‌گذاری آسان با لینک
- بدون نیاز به Google Play

## فایل‌های اضافی مورد نیاز

### 1. manifest.json
```json
{
  "name": "جنگ منطقه‌ای ایران",
  "short_name": "جنگ ایران",
  "description": "بازی استراتژیک چندنفره",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#667eea",
  "theme_color": "#764ba2",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/static/icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/static/icon-512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ]
}
```

### 2. Service Worker (sw.js)
```javascript
const CACHE_NAME = 'iran-war-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/simple_game.js',
  '/static/icon-192.png',
  '/static/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});
```

## نحوه استفاده

### 1. اشتراک‌گذاری لینک در واتساپ:
```
سلام! بازی جنگ منطقه‌ای ایران رو امتحان کن:
https://yourproject.replit.app

روی گوشی باز کن و "Add to Home Screen" رو بزن تا مثل اپ نصب بشه!
```

### 2. نصب مستقیم:
- لینک را در مرورگر گوشی باز کنید
- منوی مرورگر > "Add to Home Screen"
- آیکون بازی روی صفحه اصلی ظاهر می‌شود