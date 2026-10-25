# -*- coding: utf-8 -*-
u"""Tempo am guenstigen Handy - wie lange wartet man, bis man die App bedienen kann?

Alle anderen Pruefungen laufen mit voller PC-Leistung. Ein guenstiges Android-Handy im
Mobilfunk mit maessigem Empfang ist um ein Vielfaches langsamer - dort wartet man, wo am PC
nichts auffaellt (Vorbild: 45 s leerer Plan im Instagram-Browser, TROUBLESHOOTING 180).

Nachgestellt wird das Profil, mit dem Google selbst misst (Lighthouse, "mobile"):
Prozessor 4x langsamer, 150 ms Laufzeit, 1,6 Mbit/s runter, 750 kbit/s hoch. Geraet 360x800.

Gemessen wird dreierlei, je dreimal (gemeldet wird der Median der drei):
  * Erstbesuch   - leerer Speicher, leerer Cache. Drei Zeiten: erstes Bild (FCP), App geladen
                   ("Loslegen" steht, hinter dem Startbildschirm) und Intro vorbei. Das Erst-Intro
                   laeuft bewusst einmal je Geraet und erst, wenn das Script da ist (SPLASH_INTRO_MS).
  * Wiederkehr   - Profil angelegt, Cache warm: bis die App bedienbar ist.
  * Reiterwechsel - vom Tippen bis zum naechsten Bild (Googles INP, Event Timing API).

WICHTIG - der Server: test-server.ps1 schickt alles UNKOMPRIMIERT (2,4 MB), GitHub Pages
komprimiert (0,75 MB). Gemessen ueber test-server.ps1 dauerte der Erstbesuch 12,9 s - ein
Messfehler, kein Befund (25.10.2026). Deshalb bringt dieses Werkzeug einen eigenen kleinen
Server mit, der wie GitHub Pages gzip und max-age=600 schickt. --live misst die echte Seite.

Grenzen (Entscheidung Paddy, 25.10.2026): bedienbar nach hoechstens 3 s, Reiterwechsel
unter 1 s. Darueber ist der Lauf ROT.

Laeuft NICHT bei jedem Push (Paddy: "nicht mehr pruefen als umsetzen"), sondern:
in der monatlichen Wartung, vor jeder Store-Abgabe und wenn sich am Start der App etwas
aendert (neue grosse Dateien, Startablauf, sw.js, vendor/). Bildschirm-Aenderungen machen
den Start nicht langsamer.

    python tools/tempo-mobil.py                # Arbeitsstand, eigener gzip-Server
    python tools/tempo-mobil.py --live         # die echte Seite (nur Lesen, ohne Konto)
    python tools/tempo-mobil.py --gegenprobe   # misst sich selbst: kuenstliche Bremse

Braucht test-server.ps1 auf Port 8000. Sitzung und Onboarding kommen aus abnahme-mobil.py,
wie bei a11y-pruefung.py - kein zweites Geruest.
"""
import argparse, functools, gzip, http.server, importlib.util, os, statistics, sys, threading, time

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _abnahme_laden():
    u"""Laedt abnahme-mobil.py als Modul. Der Bindestrich verbietet ein normales import."""
    pfad = os.path.join(WURZEL, "tools", "abnahme-mobil.py")
    spec = importlib.util.spec_from_file_location("abnahme_mobil", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


AM = _abnahme_laden()

GRENZE_START = 3000    # ms bis bedienbar
GRENZE_REITER = 1000   # ms vom Tippen bis zum naechsten Bild
WIEDERHOLUNGEN = 3
NETZ = {"offline": False, "latency": 150, "downloadThroughput": 1.6e6 / 8,
        "uploadThroughput": 750e3 / 8, "connectionType": "cellular4g"}
CPU = 4
PORT_GZIP = 8010
LIVE = "https://www.paddysmealplan.de/"
ZIEL = "http://localhost:%d/index.html" % PORT_GZIP   # main() setzt --live

class GzipHandler(http.server.SimpleHTTPRequestHandler):
    u"""Liefert wie GitHub Pages: Text komprimiert, max-age=600. Nur 127.0.0.1."""
    TEXT = (".html", ".js", ".css", ".json", ".svg", ".webmanifest", ".txt", ".xml")

    def log_message(self, *a):
        pass

    def send_head(self):
        # Liefert die Repo-Wurzel aus - Geheimnisse und Notizen nicht (website-security, 25.10.2026).
        teile = self.path.split("?")[0].lstrip("/").split("/")
        if teile[0] in (".env", "plans", ".git") or teile[0].startswith(".env"):
            self.send_error(404)
            return None
        pfad = self.translate_path(self.path)
        if os.path.isdir(pfad):
            pfad = os.path.join(pfad, "index.html")
        if not (pfad.endswith(self.TEXT) and "gzip" in self.headers.get("Accept-Encoding", "")
                and os.path.isfile(pfad)):
            return super().send_head()
        with open(pfad, "rb") as f:
            daten = gzip.compress(f.read(), 6)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(pfad))
        self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", str(len(daten)))
        self.send_header("Cache-Control", "max-age=600")
        self._cache_gesetzt = True
        self.end_headers()
        import io
        return io.BytesIO(daten)

    def end_headers(self):
        if not getattr(self, "_cache_gesetzt", False):
            self.send_header("Cache-Control", "max-age=600")
        super().end_headers()


GzipHandler.extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map,
                                  **{".js": "text/javascript", ".webmanifest": "application/manifest+json"})


def gzip_server():
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT_GZIP),
                                          functools.partial(GzipHandler, directory=WURZEL))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def herkunft():
    from urllib.parse import urlsplit
    u = urlsplit(ZIEL)
    return "%s://%s" % (u.scheme, u.netloc)


# Laeuft in jeder neu geladenen Seite VOR dem App-Code. "Bereit" heisst: Startbildschirm weg
# und entweder die Anmeldung (#a-local) oder ein gefuellter #view da - und dieses Bild auch
# gezeichnet (rAF). Die Zeit ist performance.now(), also ab Beginn der Navigation.
REKORDER = r"""(() => {
  const t = window.__tempo = { geladen: null, bereit: null, reiter: [] };
  const pruef = () => {
    if (t.bereit !== null || t._wartet) return;
    const v = document.getElementById('view');
    const da = document.getElementById('a-local') || (v && v.children.length);
    // "geladen": die App steht - beim Erstbesuch noch hinter dem laufenden Intro.
    if (da && t.geladen === null) t.geladen = Math.round(performance.now());
    if (!document.getElementById('splash') && document.querySelector('.app') && da) {
      t._wartet = true;
      requestAnimationFrame(() => { t.bereit = performance.now(); });
    }
  };
  new MutationObserver(pruef).observe(document, { subtree: true, childList: true, attributes: true });
  try {
    new PerformanceObserver(l => {
      for (const e of l.getEntries())
        if (e.name === 'click' || e.name === 'pointerup' || e.name === 'touchend')
          t.reiter.push(Math.round(e.duration));
    }).observe({ type: 'event', durationThreshold: 16, buffered: true });
  } catch (e) { t.ohneEventTiming = true; }
})()"""

# Gegenprobe: eine kuenstliche Bremse von 3 s beim Start und 1,2 s in jedem Klick.
BREMSE = r"""(() => {
  const warte = ms => { const e = performance.now() + ms; while (performance.now() < e) {} };
  warte(3000);   // vor jedem Seiten-Script - die App rendert "Loslegen" schon VOR DOMContentLoaded
  document.addEventListener('click', () => warte(1200), true);
})()"""


def drosseln(s, an):
    s.senden("Emulation.setCPUThrottlingRate", {"rate": CPU if an else 1})
    s.senden("Network.emulateNetworkConditions", NETZ if an else
             {"offline": False, "latency": 0, "downloadThroughput": -1, "uploadThroughput": -1})


def warte_bereit(s, frist=40):
    u"""Liefert {fcp, geladen, bereit} in ms ab Navigationsbeginn; fehlende Werte = None."""
    ende = time.time() + frist
    while time.time() < ende:
        try:
            wert = s.js("window.__tempo && window.__tempo.bereit !== null && ({bereit: window.__tempo.bereit,"
                        " geladen: window.__tempo.geladen, fcp: (performance.getEntriesByName("
                        "'first-contentful-paint')[0] || {}).startTime || null})")
            if wert:
                return wert
        except Exception:
            pass
        time.sleep(0.2)
    return {"fcp": None, "geladen": None, "bereit": None}


def erstbesuch(s):
    s.senden("Storage.clearDataForOrigin", {"origin": herkunft(), "storageTypes": "all"})
    s.senden("Network.clearBrowserCache")
    drosseln(s, True)
    s.senden("Page.navigate", {"url": ZIEL})
    zeiten = warte_bereit(s)
    drosseln(s, False)
    return zeiten


def wiederkehr(s):
    drosseln(s, True)
    s.senden("Page.reload", {})
    zeiten = warte_bereit(s)
    drosseln(s, False)
    return zeiten["bereit"]


def reiterwechsel(s):
    u"""Tippt alle vier Reiter gedrosselt an und liefert die laengste Wartezeit je Tippen."""
    s.js("window.__tempo.reiter = []")
    drosseln(s, True)
    zeiten = []
    for kennung in ("plan", "recipes", "progress", "home"):
        vorher = s.js("window.__tempo.reiter.length")
        s.tippen_auf('[data-action="tab"][data-tab="%s"]' % kennung)
        time.sleep(1.5)
        neu = s.js("window.__tempo.reiter.slice(%d)" % vorher) or []
        # Ein Tippen erzeugt pointerup, touchend und click - zaehlt die laengste der drei.
        zeiten.append((kennung, max(neu) if neu else None))
    drosseln(s, False)
    return zeiten


def median(werte):
    werte = [w for w in werte if w is not None]
    return statistics.median(werte) if werte else None


def messen(s, bremse=False):
    s.senden("Page.enable")
    s.senden("Network.enable")
    s.geraet(360, 800, "light")
    # Guenstiges Android: Pixeldichte 2 statt der 3 aus der Abnahme - mehr Pixel kosten
    # gedrosselt Zeichenzeit, die so ein Geraet gar nicht hat.
    s.senden("Emulation.setDeviceMetricsOverride", {
        "width": 360, "height": 800, "deviceScaleFactor": 2, "mobile": True})
    s.senden("Page.addScriptToEvaluateOnNewDocument", {"source": REKORDER})
    if bremse:
        s.senden("Page.addScriptToEvaluateOnNewDocument", {"source": BREMSE})

    erst = [erstbesuch(s) for _ in range(WIEDERHOLUNGEN)]
    # Das Onboarding braucht die ungedrosselte, geladene Seite.
    s.js("new Promise(r => setTimeout(r, 300))")

    # Fuer Wiederkehr und Reiter braucht es ein angelegtes Profil - ungedrosselt angelegt,
    # das Onboarding selbst ist nicht Gegenstand dieser Messung.
    AM.onboarding(s)
    wieder = [wiederkehr(s) for _ in range(WIEDERHOLUNGEN)]
    reiter_laeufe = [reiterwechsel(s) for _ in range(WIEDERHOLUNGEN)]
    reiter = {}
    for lauf in reiter_laeufe:
        for kennung, ms in lauf:
            reiter.setdefault(kennung, []).append(ms)
    ohne_et = s.js("!!window.__tempo.ohneEventTiming")
    return erst, wieder, {k: median(v) for k, v in reiter.items()}, ohne_et


def bewerten(erst, wieder, reiter, ohne_et):
    u"""Druckt den Bericht und liefert die Zahl der Grenzverletzungen (None = nicht messbar)."""
    rot = 0
    fmt = lambda ms: "--- " if ms is None else "%5.1f s" % (ms / 1000.0)

    def zeile(titel, ms, grenze, hinweis=""):
        nonlocal rot
        if ms is None:
            urteil = "NICHT GEMESSEN"
            rot += 1
        elif ms > grenze:
            urteil = "ROT (Grenze %.1f s)" % (grenze / 1000.0)
            rot += 1
        else:
            urteil = "ok"
        print("  %-26s %s   %s%s" % (titel, fmt(ms), urteil, hinweis))

    print("\n%s" % ZIEL)
    print("Guenstiges Android, 4x langsamer, Mobilfunk maessig (Median aus %d)\n" % WIEDERHOLUNGEN)
    nur = lambda k: [e[k] for e in erst]
    print("  %-26s %s   (Info)" % ("Erstbesuch: erstes Bild", fmt(median(nur("fcp")))))
    zeile("Erstbesuch: App geladen", median(nur("geladen")), GRENZE_START,
          "   einzeln: " + ", ".join(fmt(m).strip() for m in nur("geladen")))
    print("  %-26s %s   (Info - Intro laeuft bewusst ~2,2 s ab Script)" % (
        "Erstbesuch: Intro vorbei", fmt(median(nur("bereit")))))
    zeile("Wiederkehr", median(wieder), GRENZE_START,
          "   einzeln: " + ", ".join(fmt(m).strip() for m in wieder))
    if ohne_et:
        print("  Reiterwechsel: Event Timing API fehlt in diesem Browser - nicht messbar.")
        rot += 1
    else:
        for kennung, ms in reiter.items():
            zeile("Reiter %s" % kennung, ms, GRENZE_REITER, "   (%s ms)" % ms if ms is not None else "")
    return rot


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--gegenprobe", action="store_true",
                   help="kuenstliche Bremse einbauen - der Lauf MUSS rot werden")
    p.add_argument("--live", action="store_true", help="die echte Seite messen statt des Arbeitsstands")
    a = p.parse_args()

    global ZIEL
    srv = None
    if a.live:
        ZIEL = LIVE
    else:
        srv = gzip_server()
    s = AM.Sitzung()
    s.start()
    try:
        erst, wieder, reiter, ohne_et = messen(s, bremse=a.gegenprobe)
        rot = bewerten(erst, wieder, reiter, ohne_et)
    finally:
        s.stoppen()
        if srv:
            srv.shutdown()

    print("")
    if a.gegenprobe:
        # Die Bremse kostet 3 s je Start und 1,2 s je Klick: alles Begrenzte muss rot werden -
        # App geladen, Wiederkehr und jeder Reiter.
        erwartet = 2 + len(reiter)
        if rot >= erwartet:
            print("GRUEN - die Bremse wurde ueberall gefunden, die Messung taugt.")
            return 0
        print("ROT - nur %d von %d gebremsten Stellen gemeldet. Die Messung taugt so nicht." % (rot, erwartet))
        return 1
    if rot:
        print("ROT - %d Stelle(n) ueber der Grenze." % rot)
        return 1
    print("GRUEN - am guenstigen Handy schnell genug.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
