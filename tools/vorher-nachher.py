# -*- coding: utf-8 -*-
u"""Ist und Soll als fertige Bildstrecke mit Film - zum Ansehen, nicht zum Bedienen.

    python tools/vorher-nachher.py fotohinweis           # erzeugen und im Browser oeffnen
    python tools/vorher-nachher.py fotohinweis --nur-dunkel
    python tools/vorher-nachher.py                       # Liste der Bausteine

Warum (24.10.2026, Paddy)
-------------------------
tools/probe-vergleich.html stellt zwei lebende Mini-Apps nebeneinander - man muss selbst
klicken, sieht nicht, wo, und die Gegenprobe (tuerkis gestrichelt) sah aus wie "hier
druecken". Wie Abnahmen anderswo laufen (Chromatic, BackstopJS, Playwright): Der Abnehmer
SCHAUT. Ein Skript spielt dieselben Schritte am alten und am neuen Stand durch und legt
Bildpaare nebeneinander. Genau das tut dieses Werkzeug - wie ein Entwickler, der seinem
Kollegen Ist und Soll zeigt.

Was es tut
----------
* Ist  = eingefrorener Stand aus tools/vorher/<id>/ (tools/schnappschuss.py),
  Soll = der Arbeitsbaum. Beides echter Code, kein Nachbau.
* Headless-Chrome mit Handy-Emulation (390 x 844, Touch), Dunkel und Hell ueber
  prefers-color-scheme - wie abnahme-mobil.py, nur unsichtbar und mit eigenem Profil.
* Die Schritte kommen aus tools/vergleich-bausteine.js: `film` (je Schritt ein Satz, eine
  Handlung, eine Dauer). Bausteine ohne `film` laufen wie bisher (`schritte`/`oeffnen`) und
  ergeben ein einziges Bildpaar.
* Ergebnis: eine Seite mit Film (beide Seiten gleichzeitig) und Bildpaaren je Schritt,
  abgelegt AUSSERHALB des Repos (%TEMP%\\mp-vorher-nachher\\<id>\\) - Bilder alter Staende
  gehoeren nicht ins oeffentliche Repo (wie tools/vorher/, .gitignore).

Kein Konto, keine Cloud: eigenes, frisches Profil je Lauf, die App startet lokal mit dem
Testzustand (wochenkueche_v1__test) - derselbe wie in probe-vergleich.html.
"""
import argparse, base64, html, io, json, math, os, shutil, subprocess, sys, tempfile, time
import urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASIS = "http://localhost:8000"
PORT = 9357
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
AUSGABE = os.path.join(os.environ.get("TEMP", tempfile.gettempdir()), "mp-vorher-nachher")
BREITE, HOEHE = 390, 844
TAKT = 0.2          # Sekunden zwischen zwei Filmbildern
FILMBREITE = 600    # Pixel je Seite im Film - doppelt so viel wie angezeigt, sonst weich auf
                    # hochaufloesenden Bildschirmen (300 wirkte verwaschen, Paddy 24.10.2026)

# Derselbe Testzustand wie zustandSchreiben() in tools/probe-vergleich.html - Werkzeug-Daten,
# kein Produktionscode. Aendert sich einer, den anderen mitziehen.
ZUSTAND_JS = u"""(function (extra, profil) {
  localStorage.clear(); sessionStorage.clear();
  var daten = { tab: "home", onboarded: true,
    goal: { mode: "cut", kcal: 1950, protein: 150, carbs: 180, fat: 60, activity: "pal14", training: [] },
    recipes: [{ id: "r1", name: "Testmeal", cat: "Hauptgericht",
                nutrition: { kcal: 400, protein: 30, carbs: 40, fat: 12 } }],
    plans: {}, weights: [], weightGoals: {}, weekStats: {} };
  for (var k in (extra || {})) daten[k] = extra[k];
  localStorage.setItem("wochenkueche_v1__test", JSON.stringify(daten));
  localStorage.setItem("wochenkueche_profile_v1__test", JSON.stringify(profil || { name: "Vergleich", id: "lokal" }));
  // Das Erst-Intro gehoert nicht in jeden Film - nur der Startbildschirm-Baustein will es sehen.
  localStorage.setItem("wochenkueche_intro_v1", "1");
})(%s, %s);"""


# ------------------------------------------------------------------ Server und Chrome
def server_da():
    try:
        with urllib.request.urlopen(BASIS + "/index.html", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def server_starten():
    if server_da():
        return
    # DEVNULL: Ein Server, der die Ausgabeleitung erbt, haelt den Aufrufer fest (TROUBLESHOOTING 193).
    subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                      os.path.join(WURZEL, "test-server.ps1")],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
    for _ in range(40):
        time.sleep(0.25)
        if server_da():
            return
    raise SystemExit("Der lokale Server kommt nicht hoch (test-server.ps1).")


class Browser:
    def __init__(self):
        self.profil = tempfile.mkdtemp(prefix="mp-vn-")
        # Die drei --disable-*-Flags: Haelt Chrome die Seite fuer verdeckt oder im Hintergrund,
        # zeichnet er kein neues Bild - und Page.captureScreenshot wartet darauf bis zum Timeout.
        self.proz = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu",
            "--disable-backgrounding-occluded-windows", "--disable-renderer-backgrounding",
            "--disable-background-timer-throttling",
            # Nur der eigene Zugang darf steuern, nicht jede Seite im Alltagsbrowser (website-security)
            "--remote-debugging-port=%d" % PORT, "--remote-allow-origins=http://127.0.0.1:%d" % PORT,
            "--user-data-dir=" + self.profil, "--no-first-run", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import websocket
        for _ in range(60):
            time.sleep(0.25)
            try:
                with urllib.request.urlopen("http://127.0.0.1:%d/json/list" % PORT, timeout=2) as r:
                    seiten = [t for t in json.loads(r.read()) if t.get("type") == "page"]
                if seiten:
                    break
            except Exception:
                continue
        else:
            raise SystemExit("Headless-Chrome kam nicht hoch.")
        self.ws = websocket.create_connection(seiten[0]["webSocketDebuggerUrl"], timeout=60,
                                              origin="http://127.0.0.1:%d" % PORT, suppress_origin=False)
        self.n = 0
        self.senden("Page.enable")

    def senden(self, methode, params=None):
        self.n += 1
        k = self.n
        self.ws.send(json.dumps({"id": k, "method": methode, "params": params or {}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == k:
                if "error" in m:
                    raise RuntimeError("%s: %s" % (methode, m["error"]))
                return m.get("result", {})

    def js(self, ausdruck):
        r = self.senden("Runtime.evaluate", {"expression": ausdruck, "awaitPromise": True,
                                              "returnByValue": True, "userGesture": True})
        if "exceptionDetails" in r:
            e = r["exceptionDetails"]
            raise RuntimeError((e.get("exception") or {}).get("description") or e.get("text"))
        return (r.get("result") or {}).get("value")

    def geraet(self, theme):
        self.senden("Emulation.setDeviceMetricsOverride", {
            "width": BREITE, "height": HOEHE, "deviceScaleFactor": 2, "mobile": True})
        self.senden("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
        self.senden("Emulation.setEmulatedMedia", {
            "features": [{"name": "prefers-color-scheme", "value": theme}]})

    def gehe(self, url):
        self.senden("Page.navigate", {"url": url})
        time.sleep(0.3)   # sonst meldet noch die alte Seite "complete"
        for _ in range(80):
            time.sleep(0.15)
            try:
                if self.js("document.readyState") == "complete":
                    return
            except Exception:
                continue

    def foto(self):
        u"""Ein Bild der Seite. Laedt sie gerade neu (der Ist-Stand im Fotohinweis tut das nach
        4 s), antwortet captureScreenshot erst, wenn wieder gezeichnet wird - oder nie. Dann
        nach 4 s das letzte Bild wiederholen statt den ganzen Lauf abzubrechen. Die verspaetete
        Antwort ueberliest senden() spaeter, weil sie eine andere Kennung traegt."""
        import websocket
        self.ws.settimeout(4)
        try:
            r = self.senden("Page.captureScreenshot", {"format": "png"})
            self.letztes = Image.open(io.BytesIO(base64.b64decode(r["data"]))).convert("RGB")
        except websocket.WebSocketTimeoutException:
            self.haenger = getattr(self, "haenger", 0) + 1
        finally:
            self.ws.settimeout(60)
        return self.letztes

    def ende(self):
        try:
            self.ws.close()
        except Exception:
            pass
        self.proz.kill()
        shutil.rmtree(self.profil, ignore_errors=True)


from PIL import Image  # noqa: E402  (oben bleibt der Ablauf lesbar)


# ------------------------------------------------------------------------ Ablauf
def registry_laden(b):
    u"""BAUSTEINE aus tools/vergleich-bausteine.js in die Seite holen (klassisches Skript)."""
    quelle = io.open(os.path.join(WURZEL, "tools", "vergleich-bausteine.js"), encoding="utf-8").read()
    b.js(quelle + "\n;window.BAUSTEINE = BAUSTEINE; true")


def bereit(b, nur_inhalt):
    u"""Wie warteAufApp() in probe-vergleich.html: Inhalt UND Ende des Willkommensschirms."""
    for _ in range(100):
        try:
            ok = b.js("""(() => { const v = document.getElementById('view'), a = document.querySelector('.app');
              if (document.getElementById('splash')) return false;
              const drin = %s;
              return !!(v && v.textContent.trim().length && drin); })()""" %
                      ("!!document.getElementById('c-google')" if nur_inhalt
                       else "a && !a.classList.contains('authing')"))
            if ok:
                return True
        except Exception:
            pass
        time.sleep(0.15)
    return False


def schritte_holen(b, bid):
    u"""Die Schritte als Liste {text, dauer} - aus `film`, sonst ein einziger Schritt."""
    return b.js("""(() => { const x = BAUSTEINE.find(b => b.id === %s); if (!x) return null;
      if (x.film) return x.film.map(s => ({ text: s.text, dauer: s.dauer || 1200 }));
      return [{ text: x.was, dauer: 1600 }]; })()""" % json.dumps(bid))


# Der "Finger": gelber Kreis auf der Knopfmitte, Knopf gelb umrandet. Gelb kommt in der App
# nicht vor (Gold ist fuer Pro reserviert, docs/DESIGN.md) - der Finger ist also nie mit App-UI
# zu verwechseln. Wie die Touch-Anzeige in Android-Bildschirmaufnahmen.
FINGER_JS = u"""(async () => { const x = BAUSTEINE.find(b => b.id === %s), s = x.film[%d];
  if (s.vorbereiten) s.vorbereiten(document);
  if (s.tun) { await s.tun(document); return "getan"; }
  if (!s.tippe) return "nichts";
  const el = s.tippe(document); if (!el) return "Knopf nicht gefunden";
  el.scrollIntoView({ block: "center" });
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const r = el.getBoundingClientRect(), m = document.createElement("div");
  m.id = "__vn-finger";
  m.style.cssText = "position:fixed;left:" + (r.left + r.width / 2 - 24) + "px;top:" + (r.top + r.height / 2 - 24)
    + "px;width:48px;height:48px;border-radius:50%%;background:rgba(255,214,0,.45);border:3px solid #FFD600;"
    + "box-shadow:0 0 0 8px rgba(255,214,0,.22);z-index:2147483647;pointer-events:none";
  document.body.appendChild(m);
  window.__vnEl = el; window.__vnRahmen = [el.style.outline, el.style.outlineOffset];
  el.style.outline = "3px solid #FFD600"; el.style.outlineOffset = "2px";
  return "zeigt"; })()"""

TIPPEN_JS = u"""(() => { const el = window.__vnEl; if (!el) return;
  el.style.outline = window.__vnRahmen[0]; el.style.outlineOffset = window.__vnRahmen[1];
  el.click();
  setTimeout(() => { const m = document.getElementById("__vn-finger"); if (m) m.remove(); }, 350);
  window.__vnEl = null; })()"""


def schritt_ausfuehren(b, bid, i, film):
    u"""Handlung eines Schritts. Mit `film`: Finger zeigen (Rueckgabe "zeigt"), getippt wird
    danach mit tippen(). Ohne `film`: erst `schritte` (Klicks), dann `oeffnen`."""
    if film:
        return b.js(FINGER_JS % (json.dumps(bid), i))
    return b.js("""(async () => { const x = BAUSTEINE.find(b => b.id === %s);
      for (const sel of (x.schritte || [])) {
        const e = document.querySelector(sel); if (e) e.click();
        await new Promise(r => setTimeout(r, 700)); }
      return x.oeffnen ? x.oeffnen(document) || "" : ""; })()""" % json.dumps(bid))


def filmen(b, sekunden):
    bilder = []
    for _ in range(max(1, int(math.ceil(sekunden / TAKT)))):
        t0 = time.time()
        bilder.append(b.foto())
        time.sleep(max(0, TAKT - (time.time() - t0)))
    return bilder


def lauf(b, bid, url, theme, meta, protokoll):
    u"""Eine Seite (Ist oder Soll) in einem Theme: je Schritt Filmbilder + Standbild."""
    b.geraet(theme)
    b.gehe(BASIS + "/tools/vergleich-bausteine.js")      # gleiche Herkunft fuer localStorage
    b.js(ZUSTAND_JS % (json.dumps(meta.get("zustand") or {}), json.dumps(meta.get("profil"))))
    b.gehe(url + "?v=%d" % time.time())
    if not bereit(b, meta.get("nurInhalt")):
        protokoll.append("%s/%s: App wurde nicht bereit" % (url, theme))
    registry_laden(b)
    schritte = schritte_holen(b, bid)
    film = bool(meta.get("film"))
    wer = "Ist" if "vorher" in url else "Soll"
    ergebnis = []
    for i, s in enumerate(schritte):
        bilder, standbild = [], None
        try:
            if not b.js("!!window.BAUSTEINE"):     # nach einem Neuladen der Seite
                registry_laden(b)
            meldung = schritt_ausfuehren(b, bid, i, film)
            if meldung == "zeigt":
                # Erst den Finger stehen lassen - das Standbild des Schritts ist genau dieser
                # Moment: Man sieht, WOHIN getippt wird. Was danach passiert, zeigt der Film
                # und das Bild des naechsten Schritts.
                bilder = filmen(b, 0.8)
                standbild = bilder[-1]
                b.js(TIPPEN_JS)
            elif meldung and meldung not in ("nichts", "getan"):
                protokoll.append("%s %s Schritt %d: %s" % (wer, theme, i + 1, meldung))
        except Exception as e:
            protokoll.append("%s %s Schritt %d warf: %s" % (wer, theme, i + 1, e))
        bilder += filmen(b, s["dauer"] / 1000.0)
        ergebnis.append((bilder, standbild or bilder[-1]))
    return schritte, ergebnis


def film_bauen(ist, soll, ziel):
    u"""Ist | Soll nebeneinander, Schritt fuer Schritt gleich lang - so laufen beide synchron."""
    bilder = []
    for (a, _), (b, _) in zip(ist, soll):
        n = max(len(a), len(b))
        for k in range(n):
            l = a[min(k, len(a) - 1)].resize((FILMBREITE, int(FILMBREITE * HOEHE / BREITE)), Image.LANCZOS)
            r = b[min(k, len(b) - 1)].resize(l.size, Image.LANCZOS)
            f = Image.new("RGB", (l.width * 2 + 12, l.height), (20, 16, 15))
            f.paste(l, (0, 0)); f.paste(r, (l.width + 12, 0))
            bilder.append(f)
    bilder[0].save(ziel, save_all=True, append_images=bilder[1:], duration=int(TAKT * 1000),
                   loop=0, quality=90, method=4)


SEITE = u"""<!doctype html><html lang="de"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ist und Soll: %(titel)s</title>
<style>
  :root { color-scheme: dark; }
  body { margin: 0; padding: 24px 16px 60px; background: #14100F; color: #F4EFEE;
         font: 16px/1.55 system-ui, -apple-system, "Segoe UI", sans-serif; }
  main { max-width: 760px; margin: 0 auto; }
  h1 { font-size: 24px; margin: 0 0 6px; }
  .was { color: #CFC4C1; margin: 0 0 18px; }
  .umschalter { display: flex; gap: 8px; margin: 0 0 20px; }
  .umschalter button { font: inherit; padding: 8px 16px; border-radius: 999px; cursor: pointer;
         background: #241E1D; color: #F4EFEE; border: 1px solid #3A3130; }
  .umschalter button[aria-pressed="true"] { background: #F4EFEE; color: #14100F; }
  .paar { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
  .seite h3 { margin: 0 0 6px; font-size: 14px; letter-spacing: .06em; }
  .ist h3 { color: #CFC4C1; } .soll h3 { color: #4ADE80; }
  .seite p { margin: 6px 0 0; font-size: 14px; color: #CFC4C1; }
  img { width: 100%%; display: block; border-radius: 14px; border: 1px solid #3A3130; }
  .film { margin: 0 0 32px; }
  .film img { border-radius: 14px; }
  .schritt { margin: 0 0 30px; }
  .schritt h2 { font-size: 18px; margin: 0 0 10px; }
  .nr { display: inline-block; min-width: 28px; height: 28px; line-height: 28px; text-align: center;
        border-radius: 50%%; background: #F4EFEE; color: #14100F; font-size: 15px; margin-right: 8px; }
  .theme[hidden] { display: none; }
  footer { margin-top: 30px; color: #A99C99; font-size: 13px; }
</style>
<main>
<h1>%(titel)s</h1>
<p class="was">%(was)s</p>
%(umschalter)s
%(themes)s
<footer>Links der Stand vor der Änderung, rechts der neue. Beide Seiten wurden automatisch mit
denselben Schritten durchgespielt (Handygröße 390 × 844, ohne Konto). Erzeugt %(zeit)s.</footer>
</main>
<script>
document.querySelectorAll(".umschalter button").forEach(b => b.addEventListener("click", () => {
  document.querySelectorAll(".umschalter button").forEach(o => o.setAttribute("aria-pressed", String(o === b)));
  document.querySelectorAll(".theme").forEach(t => t.hidden = t.dataset.theme !== b.dataset.theme);
}));
</script></html>"""


def seite_bauen(meta, themes, ordner):
    e = html.escape
    teile = []
    for theme, (schritte, ist_bilder, soll_bilder) in themes.items():
        film = "film-%s.webp" % theme
        film_bauen(ist_bilder, soll_bilder, os.path.join(ordner, film))
        z = [u'<section class="theme" data-theme="%s"%s>' % (theme, "" if theme == list(themes)[0] else " hidden")]
        z.append(u'<div class="film"><div class="paar"><div class="seite ist"><h3>IST · HEUTE</h3></div>'
                 u'<div class="seite soll"><h3>SOLL · NEU</h3></div></div>'
                 u'<img src="%s" alt="Film: links Ist, rechts Soll, gleichzeitig"></div>' % film)
        for i, s in enumerate(schritte):
            for seite, bilder in (("ist", ist_bilder), ("soll", soll_bilder)):
                bilder[i][1].save(os.path.join(ordner, "%s-%s-%d.png" % (theme, seite, i + 1)))
            z.append(u'<div class="schritt"><h2><span class="nr">%d</span>%s</h2><div class="paar">'
                     u'<div class="seite ist"><h3>IST</h3><img src="%s-ist-%d.png" alt="Ist, Schritt %d"></div>'
                     u'<div class="seite soll"><h3>SOLL</h3><img src="%s-soll-%d.png" alt="Soll, Schritt %d"></div>'
                     u'</div></div>' % (i + 1, e(s["text"]), theme, i + 1, i + 1, theme, i + 1, i + 1))
        if meta.get("ist") or meta.get("soll"):
            z.append(u'<div class="paar"><div class="seite ist"><h3>IST</h3><p>%s</p></div>'
                     u'<div class="seite soll"><h3>SOLL</h3><p>%s</p></div></div>'
                     % (e(meta.get("ist") or ""), e(meta.get("soll") or "")))
        z.append(u"</section>")
        teile.append("\n".join(z))
    namen = {"dark": "Dunkel", "light": "Hell"}
    umschalter = u'<div class="umschalter">%s</div>' % "".join(
        u'<button data-theme="%s" aria-pressed="%s">%s</button>' % (t, str(i == 0).lower(), namen[t])
        for i, t in enumerate(themes)) if len(themes) > 1 else ""
    pfad = os.path.join(ordner, "index.html")
    io.open(pfad, "w", encoding="utf-8").write(SEITE % {
        "titel": e(meta["titel"]), "was": e(meta.get("was") or ""), "umschalter": umschalter,
        "themes": "\n".join(teile), "zeit": time.strftime("%d.%m.%Y %H:%M")})
    return pfad


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("baustein", nargs="?")
    ap.add_argument("--nur-dunkel", action="store_true")
    ap.add_argument("--nicht-oeffnen", action="store_true")
    a = ap.parse_args()
    server_starten()
    b = Browser()
    try:
        b.gehe(BASIS + "/tools/vergleich-bausteine.js")
        registry_laden(b)
        if not a.baustein:
            for z in b.js("BAUSTEINE.map(x => x.id + (x.film ? '  (mit Film-Schritten)' : ''))"):
                print("  " + z)
            return
        meta = b.js("""(() => { const x = BAUSTEINE.find(b => b.id === %s); if (!x) return null;
          return { titel: x.titel, was: x.was, ist: x.ist, soll: x.soll, zustand: x.zustand || null,
                   profil: x.profil || null, nurInhalt: !!x.nurInhalt, film: !!x.film }; })()""" % json.dumps(a.baustein))
        if not meta:
            raise SystemExit("Unbekannter Baustein: %s" % a.baustein)
        if not os.path.isfile(os.path.join(WURZEL, "tools", "vorher", a.baustein, "index.html")):
            raise SystemExit("Kein Ist-Stand. Zuerst:  python tools/schnappschuss.py %s <commit>" % a.baustein)
        protokoll, themes = [], {}
        for theme in (["dark"] if a.nur_dunkel else ["dark", "light"]):
            print("  %s: Ist ..." % theme)
            schritte, ist = lauf(b, a.baustein, BASIS + "/tools/vorher/%s/index.html" % a.baustein, theme, meta, protokoll)
            print("  %s: Soll ..." % theme)
            _, soll = lauf(b, a.baustein, BASIS + "/index.html", theme, meta, protokoll)
            themes[theme] = (schritte, ist, soll)
    finally:
        b.ende()
    ordner = os.path.join(AUSGABE, a.baustein)
    shutil.rmtree(ordner, ignore_errors=True)
    os.makedirs(ordner)
    pfad = seite_bauen(meta, themes, ordner)
    for z in protokoll:
        print("  " + z)
    print("Fertig: " + pfad)
    if not a.nicht_oeffnen:
        os.startfile(pfad)


if __name__ == "__main__":
    main()
