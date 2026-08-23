/* Service Worker fuer Paddy's Mealplan (GitHub Pages, Unterpfad /mealplan/).
 *
 * Zweck: die App offline lauffaehig machen und als installierbare PWA/Capacitor-Basis dienen.
 * Strategie bewusst konservativ, damit nie eine veraltete App klebenbleibt:
 *   - Navigationen (die HTML-Seite selbst): NETWORK-FIRST. Online immer die frische index.html,
 *     nur wenn offline aus dem Cache. So wirkt ein Deploy sofort, ohne Cache-Invalidierungs-Zauber.
 *   - Eigene statische Assets (Icons, Manifest, ZXing, das Firebase-SDK aus vendor/):
 *     CACHE-FIRST. Seit D4 liegt das SDK im Repo, es faellt also unter diesen Zweig.
 *   - Fremde Hosts (Firestore/Identity-Toolkit-API, Open Food Facts): NICHT anfassen -
 *     einfach durchreichen. Auth/Live-Daten duerfen nie aus dem Cache kommen.
 *
 * Alle Pfade relativ, weil die App unter .../mealplan/ liegt, nicht auf dem Domain-Root.
 * Die Versionsnummer bei jedem inhaltlichen SW-Wechsel erhoehen -> activate raeumt Altes weg.
 */
const VERSION = "pm-v6";
const SHELL_CACHE = "shell-" + VERSION;

// Kern-Assets, die die App-Huelle offline tragen. index.html liegt zusaetzlich im Cache,
// damit eine Navigation offline etwas zum Ausliefern hat.
//
// Was hier NICHT mehr steht, und warum:
//
// * Die 32 Meal-Fotos (~724 KB) und vendor/zxing.min.js (~332 KB) wurden frueher bei der
//   Installation mitgeladen - gut 1 MB, bevor der Nutzer irgendetwas davon brauchte. ZXing
//   ist dabei doppelt teuer: Auf Android/Chrome kommt der Barcode-Scanner ueber das native
//   BarcodeDetector-API, die Datei wird dort also nie angefasst (siehe index.html, loadZXing).
//   Beide gehen jetzt ueber den normalen Cache-First-Pfad im fetch-Handler und liegen nach
//   dem ersten Gebrauch genauso dauerhaft im Cache - nur eben erst dann.
// * Wer die App online oeffnet, hat seine Fotos also nach dem ersten Blick auf die Meals
//   offline verfuegbar. Ein Nutzer, der ausschliesslich offline startet, bevor er je ein
//   Foto gesehen hat, bekommt die Kachel-Rueckfaelle - das war die Abwaegung.
//
// ACHTUNG: Alles hier und alle nachgeladenen Assets werden Cache-First ausgeliefert. Wird ein
// Foto oder das Logo ausgetauscht, muss VERSION hoch - sonst sieht ein wiederkehrender Nutzer
// weiter die alte Datei.
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./img/logo.png",
  "./icon-192.png",
  "./icon-512.png",
  "./icon-maskable-512.png",
  "./apple-touch-icon.png"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(SHELL_CACHE)
      // Einzeln adden und Fehler schlucken: faellt ein Asset (noch) aus, soll die
      // Installation nicht komplett scheitern.
      .then((cache) => Promise.allSettled(SHELL_ASSETS.map((u) => cache.add(u))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== SHELL_CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;

  const url = new URL(req.url);
  // Fremde Hosts komplett durchreichen (Firebase, Firestore, gstatic, Open Food Facts, CDNs).
  if (url.origin !== self.location.origin) return;

  // Navigationen: erst Netz, dann Cache (frische App online, Huelle offline).
  if (req.mode === "navigate" || (req.destination === "document")) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(SHELL_CACHE).then((c) => c.put("./index.html", copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req).then((m) => m || caches.match("./index.html")))
    );
    return;
  }

  // Eigene statische Assets: erst Cache, sonst Netz (und ins Cache nachlegen).
  event.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(SHELL_CACHE).then((c) => c.put(req, copy)).catch(() => {});
      return res;
    }).catch(() => hit))
  );
});
