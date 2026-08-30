/* Service Worker fuer Paddy's Mealplan.
 *
 * Zweck: die App offline lauffaehig machen und als installierbare PWA/Capacitor-Basis dienen.
 * Strategie bewusst konservativ, damit nie eine veraltete App klebenbleibt:
 *   - Navigationen (die HTML-Seite selbst): NETWORK-FIRST. Online immer die frische index.html,
 *     nur wenn offline aus dem Cache. So wirkt ein Deploy sofort, ohne Cache-Invalidierungs-Zauber.
 *   - Eigener App-Code aus css/, data/ und lib/: EBENFALLS NETWORK-FIRST. Bis zur Aufteilung
 *     steckte dieser Code komplett in index.html und fiel damit unter den Navigations-Zweig.
 *     Laege er jetzt im Cache-First-Zweig, bekaeme ein wiederkehrender Nutzer nach einem Push
 *     weiter die alte App - bis irgendwann jemand VERSION erhoeht. Die Aufteilung darf das
 *     Deploy-Verhalten nicht veraendern, deshalb dieser eigene Zweig.
 *   - Uebrige eigene Assets (Icons, Manifest, Fotos, ZXing, Firebase-SDK aus vendor/):
 *     CACHE-FIRST. Das sind unveraenderliche Dateien; sie aendern sich nur mit einem Deploy,
 *     der ohnehin VERSION anfasst.
 *   - Fremde Hosts (Firestore/Identity-Toolkit-API, Open Food Facts): NICHT anfassen -
 *     einfach durchreichen. Auth/Live-Daten duerfen nie aus dem Cache kommen.
 *
 * Alle Pfade relativ. Das stammt aus der Zeit unter .../mealplan/ und bleibt richtig, seit
 * die App auf dem Root von www.paddysmealplan.de liegt - und es haelt den Capacitor-Weg offen.
 * Die Versionsnummer bei jedem inhaltlichen SW-Wechsel erhoehen -> activate raeumt Altes weg.
 */
const VERSION = "pm-v8";
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
  // Der eigene App-Code. Er gehoert zur Huelle: ohne css/ startet die App ungestylt,
  // ohne data/ und lib/ startet sie gar nicht. Zusammen rund 300 KB - deutlich weniger
  // als die frueher hier gelisteten Fotos, und anders als die wird das hier gebraucht,
  // bevor der Nutzer irgendetwas tut. Ausgeliefert werden sie trotzdem network-first
  // (siehe fetch-Handler); der Cache ist nur der Offline-Rueckfall.
  "./css/tokens.css",
  "./css/basis.css",
  "./css/komponenten.css",
  "./css/mobil.css",
  "./lib/basis.js",
  "./lib/pdf.js",
  "./lib/barcode.js",
  "./data/ikonen.js",
  "./data/bilder.js",
  "./data/cookbook.js",
  "./data/foods.js",
  "./data/rechtstexte.js",
  "./manifest.webmanifest",
  "./img/logo.png",
  "./img/icon-192.png",
  "./img/icon-512.png",
  "./img/icon-maskable-512.png",
  "./img/apple-touch-icon.png"
];

// Eigener App-Code, der wie die Seite selbst network-first ausgeliefert wird.
// Bewusst ueber das Pfadmuster und nicht ueber die Liste oben: eine neue Datei unter
// css/, data/ oder lib/ soll sich richtig verhalten, auch wenn jemand vergisst, sie
// in SHELL_ASSETS nachzutragen.
const APP_CODE = /\/(?:css|data|lib)\/[^/]+\.(?:css|js)$/;

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

  // Eigener App-Code: erst Netz, dann Cache - genau wie die Seite selbst. Ohne diesen
  // Zweig wuerde ein Deploy bei wiederkehrenden Nutzern nicht ankommen.
  if (APP_CODE.test(url.pathname)) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(SHELL_CACHE).then((c) => c.put(req, copy)).catch(() => {});
          return res;
        })
        .catch(() => caches.match(req))
    );
    return;
  }

  // Uebrige eigene Assets: erst Cache, sonst Netz (und ins Cache nachlegen).
  event.respondWith(
    caches.match(req).then((hit) => hit || fetch(req).then((res) => {
      const copy = res.clone();
      caches.open(SHELL_CACHE).then((c) => c.put(req, copy)).catch(() => {});
      return res;
    }).catch(() => hit))
  );
});
