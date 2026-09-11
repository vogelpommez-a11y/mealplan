# -*- coding: utf-8 -*-
u"""
Geraeteabnahme fuer Paket 3: Zutaten mit dem Finger sortieren.

Das Gegenstueck zu tools/pruefstand-zutaten-sortieren.py. Der laeuft headless und misst die
Reihenfolge - er kann aber ueber das MITSCROLLEN nichts sagen: unter --headless=new feuert
requestAnimationFrame genau einmal, der Autoscroll kaeme dort nie in Gang, und jeder Fall
dazu waere dauerhaft gruen, ohne etwas zu messen.

Hier laeuft dagegen ein sichtbarer Chrome mit echter Geraete-Emulation ueber das
DevTools-Protokoll: echter CSS-Viewport, pointer: coarse, und Gesten als
Input.dispatchTouchEvent - keine synthetischen PointerEvents.

Alles in EINER offenen Verbindung: Zeigertyp und Farbschema gelten nur in der Verbindung,
die sie gesetzt hat (tools/cdp.py, messen()). Wer je Kommando neu verbindet, misst
pointer: fine und haelt eine Desktop-Messung fuer eine Handy-Abnahme.

Eigenes Chrome-Profil auf einem eigenen Port: das Profil von tools/cdp.py ist an einem
echten Firebase-Konto angemeldet, und Testdaten gehoeren nicht in ein angemeldetes Profil.

FUENF FAELLE:
  anfasser     auf dem Handy ist der Anfasser unsichtbar und nicht antippbar
  ziehen       halten, ziehen, loslassen - Reihenfolge getauscht und genau EINMAL gespeichert
  wischen      wer vor Ablauf der Haltezeit wischt, scrollt das Sheet und sortiert NICHT
  randzone     wer am unteren Sheet-Rand aufnimmt und still haelt, loest KEINEN Autoscroll aus
  autoscroll   wer den Finger AN den Rand fuehrt, scrollt sehr wohl mit

Gegenproben - ohne sie zaehlt kein Ergebnis (jede darf genau einen Fall rot machen):
  python tools/abnahme-zutaten-sortieren.py --rueckbau rand        # Randsperre ausgebaut
  python tools/abnahme-zutaten-sortieren.py --rueckbau autoscroll  # Autoscroll ausgebaut

Keine Gegenprobe gibt es fuer den Wischabbruch (WACKEL): am echten Geraet schickt Chrome
pointercancel, sobald das Scrollen uebernimmt - die Geste ist da schon beendet, und der
Rueckbau der Schwelle aendert nichts. Die Schwelle ist der Guertel fuer Zeiger, die kein
pointercancel schicken; geprueft wird sie headless im Pruefstand.

Voraussetzung: der lokale Server laeuft.
    powershell -NoProfile -File test-server.ps1

Aufruf:  python tools/abnahme-zutaten-sortieren.py [--rueckbau <name>] [--bleib]
         --bleib laesst Chrome offen, um selbst nachzusehen.
"""
import io, json, os, sys, time, urllib.request

HIER = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.dirname(HIER)
sys.path.insert(0, HIER)
import cdp

cdp.PORT = 9223
cdp.PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-abnahme-sortieren")

BREITE, HOEHE = 390, 844
SERVER = "http://localhost:8000/"
# Der Rueckbau wird als eigene Datei NEBEN index.html ausgeliefert: die relativen Pfade auf
# css/, data/, lib/ und vendor/ stimmen nur auf dieser Ebene. .gitignore haelt sie draussen,
# das finally loescht sie wieder.
RUECKBAU_DATEI = os.path.join(BASIS, "_abnahme-rueckbau.html")

RUECKBAUTEN = {
    "rand": ("dg.randSperre = dgInRandzone();", "dg.randSperre = false;"),
    "autoscroll": ("if (dg.scrollV && !dg.raf) dg.raf = requestAnimationFrame(dgScrollSchritt);",
                   "/* rueckgebaut */"),
}

ZUTATEN = [
    {"name": "Haehnchenbrust", "grams": 150, "kcal": 165, "carbs": 0, "protein": 31, "fat": 3.6},
    {"name": "Reis", "grams": 80, "kcal": 350, "carbs": 78, "protein": 7, "fat": 1},
    {"name": "Milch 1,5 %", "grams": 200, "unit": "ml", "kcal": 47, "carbs": 4.8, "protein": 3.4, "fat": 1.5},
    {"name": "Broccoli", "grams": 200, "kcal": 34, "carbs": 7, "protein": 2.8, "fat": 0.4},
    {"name": "Olivenoel", "grams": 10, "kcal": 884, "carbs": 0, "protein": 0, "fat": 100},
    "Salz und Pfeffer",
]
NAMEN = [z["name"] if isinstance(z, dict) else z for z in ZUTATEN]
# Ohne fertiges Ziel zeigt die App den Willkommens-Assistenten, und die Meals-Karte, an der
# diese Abnahme haengt, gibt es gar nicht. Dieselben Werte wie im headless-Pruefstand.
GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}
ZUSTAND = {"goal": GOAL, "recipes": [{"id": "r1", "name": "Abnahme-Meal", "category": "Hauptgericht",
                        "tags": [], "nutrition": None, "steps": "Alles in die Pfanne.",
                        "ingredients": ZUTATEN}],
           "plans": {}, "onboarded": True, "tab": "recipes", "favs": [], "planned": {},
           "shopPersons": 1, "viewWeek": "cur"}


class Sitzung(object):
    def __init__(self):
        import websocket
        t = cdp.app_seite()
        self.ws = websocket.create_connection(
            t["webSocketDebuggerUrl"], timeout=30,
            origin="http://127.0.0.1:%d" % cdp.PORT, suppress_origin=False)
        self._id = 0
        self.cmd("Emulation.setDeviceMetricsOverride",
                 {"width": BREITE, "height": HOEHE, "deviceScaleFactor": 0, "mobile": True})
        # Ohne das hier bleibt pointer: fine - dann greift @media (hover: hover), der Anfasser
        # waere dauerhaft sichtbar, und die Abnahme misst das Falsche.
        self.cmd("Emulation.setTouchEmulationEnabled", {"enabled": True, "maxTouchPoints": 5})
        self.cmd("Emulation.setEmulatedMedia", {"features": [
            {"name": "prefers-color-scheme", "value": "dark"},
            {"name": "pointer", "value": "coarse"}, {"name": "any-pointer", "value": "coarse"},
            {"name": "hover", "value": "none"}, {"name": "any-hover", "value": "none"}]})

    def cmd(self, methode, params=None):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": methode, "params": params or {}}))
        while True:
            n = json.loads(self.ws.recv())
            if n.get("id") == mid:
                if "error" in n:
                    raise RuntimeError("%s: %s" % (methode, n["error"]))
                return n.get("result", {})

    def js(self, ausdruck):
        r = self.cmd("Runtime.evaluate", {"expression": ausdruck, "returnByValue": True,
                                          "awaitPromise": True, "userGesture": True})
        if r.get("exceptionDetails"):
            raise RuntimeError(json.dumps(r["exceptionDetails"])[:300])
        w = r.get("result", {}).get("value")
        if isinstance(w, str):
            try:
                return json.loads(w)
            except Exception:
                return w
        return w

    def _tp(self, x, y):
        return [{"x": float(x), "y": float(y), "id": 1, "radiusX": 12, "radiusY": 12, "force": 1}]

    def tdown(self, x, y):
        self.cmd("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": self._tp(x, y)})

    def tmove(self, x, y):
        self.cmd("Input.dispatchTouchEvent", {"type": "touchMove", "touchPoints": self._tp(x, y)})

    def tup(self):
        self.cmd("Input.dispatchTouchEvent", {"type": "touchEnd", "touchPoints": []})

    def tippen(self, x, y):
        self.tdown(x, y)
        time.sleep(0.06)
        self.tup()

    def schliessen(self):
        try:
            self.ws.close()
        except Exception:
            pass


def rechteck(s, sel, nr=0):
    return s.js("(()=>{const e=document.querySelectorAll(%s)[%d];if(!e)return null;"
                "const b=e.getBoundingClientRect();return JSON.stringify("
                "{x:b.left+b.width/2,y:b.top+b.height/2,top:b.top,hoehe:b.height})})()"
                % (json.dumps(sel), nr))


def namen(s):
    return s.js("JSON.stringify(Array.from(document.querySelectorAll('#f-ings .ing-name'))"
                ".map(i=>i.value))")


def gespeichert(s):
    return s.js("(()=>{const d=JSON.parse(localStorage.getItem('wochenkueche_v1__test')||'{}');"
                "const r=(d.recipes||[])[0]||{};return JSON.stringify((r.ingredients||[])"
                ".map(i=>typeof i==='string'?i:i.name))})()")


def warte_auf(s, sel, was, sekunden=15):
    u"""Aktiv warten statt fest zu schlafen - ein langsamer Rechner darf die Abnahme nicht
    in einen Fehler laufen lassen, und ein wirklich fehlender Knopf soll klar benannt sein."""
    bis = time.time() + sekunden
    while time.time() < bis:
        try:
            if s.js("document.querySelectorAll(%s).length" % json.dumps(sel)):
                time.sleep(0.25)   # eine Atempause fuer die Einblend-Animation
                return True
        except Exception:
            pass
        time.sleep(0.25)
    raise SystemExit("Nicht gefunden: %s (%s) - der Weg in die App stimmt nicht mehr." % (was, sel))


def aufbauen(s, url):
    u"""Frischer Zustand und der echte Weg bis ins Formular: Reiter, Karte, Bearbeiten."""
    s.js("location.href = %s; 1" % json.dumps(url))
    warte_auf(s, "#view", "die App")
    s.js("localStorage.setItem('wochenkueche_v1__test', %s);"
         "localStorage.setItem('wochenkueche_profile_v1__test', %s); location.reload(); 1"
         % (json.dumps(json.dumps(ZUSTAND)), json.dumps(json.dumps({"name": "Test"}))))
    time.sleep(1.0)
    warte_auf(s, '[data-tab="recipes"]', "die Reiterleiste")
    s.js("document.querySelector('[data-tab=\"recipes\"]').click(); 1")
    warte_auf(s, ".rcard", "die Meal-Karte")
    k = rechteck(s, ".rcard")
    s.tippen(k["x"], k["y"])
    warte_auf(s, "[data-edit]", "der Bearbeiten-Knopf")
    e = rechteck(s, "[data-edit]")
    s.tippen(e["x"], e["y"])
    warte_auf(s, "#f-ings .ing-row", "die Zutatenzeilen")
    # Der Weg ins Formular laesst ein Eingabefeld fokussiert zurueck. Der erste Tipp irgendwohin
    # nimmt ihm den Fokus, und focusout schreibt den Entwurf - das haette jeder Fall als
    # zusaetzlichen Schreibvorgang gezaehlt, ohne dass jemand sortiert haette.
    s.js("if (document.activeElement && document.activeElement.blur) document.activeElement.blur(); 1")
    time.sleep(0.4)
    # Schreibvorgaenge zaehlen, und nur die aus commitNow(): hydrateImages() schreibt
    # denselben Schluessel asynchron, sobald ein Bild fertig ist.
    s.js("(()=>{window.__schreib=0;const echt=localStorage.setItem.bind(localStorage);"
         "localStorage.setItem=function(k,v){if(k==='wochenkueche_v1__test' &&"
         " String((new Error()).stack||'').indexOf('commitNow')>=0)"
         " {window.__schreib++; window.__spur=String((new Error()).stack||'')"
         r".replace(/\s+/g,' ').slice(0,300);}"
         "return echt(k,v);};return 1})()")


def sheet(s):
    return s.js("(()=>{const b=document.querySelector('.modal-body');"
                "const r=b.getBoundingClientRect();"
                "return JSON.stringify({oben:r.top,unten:r.bottom,st:b.scrollTop})})()")


def st(s):
    return s.js("Math.round(document.querySelector('.modal-body').scrollTop)")


# ---------------- Die Faelle ----------------

def fall_anfasser(s, url):
    aufbauen(s, url)
    return s.js("(()=>{const g=document.querySelector('#f-ings .ing-grip');"
                "const c=getComputedStyle(g);"
                "const v=getComputedStyle(document.querySelector('#f-ings .ing-view'));"
                "return JSON.stringify({vorhanden:!!g,opacity:c.opacity,"
                "tippbar:c.pointerEvents!=='none',einzug:v.paddingLeft,"
                "quer:document.documentElement.scrollWidth<=innerWidth})})()")


def fall_ziehen(s, url):
    aufbauen(s, url)
    z = rechteck(s, "#f-ings .ing-row", 0)
    raus = {"vorher": namen(s)}
    s.js("window.__schreib=0; 1")
    s.tdown(z["x"], z["y"])
    time.sleep(0.25)
    raus["vorAblauf"] = s.js("document.querySelector('#f-ings').classList.contains('ings-sorting')")
    time.sleep(0.35)
    raus["nachAblauf"] = s.js("document.querySelector('#f-ings').classList.contains('ings-sorting')")
    # Ein paar Pixel ueber die Zeilenhoehe hinaus: der Zielwechsel greift erst, wenn die Mitte
    # die Nachbarmitte wirklich ueberschreitet - genau auf der Kante passiert nichts.
    weg = z["hoehe"] + 4
    for i in range(1, 15):
        s.tmove(z["x"], z["y"] + weg * i / 14.0)
        time.sleep(0.02)
    raus["nachbarWeicht"] = s.js("(()=>{const r=document.querySelectorAll('#f-ings .ing-row')[1];"
                                 "return (r.style.transform||'').indexOf('translateY(-')===0})()")
    s.tup()
    time.sleep(0.6)
    raus["nachher"] = namen(s)
    raus["gespeichert"] = gespeichert(s)
    raus["schreib"] = s.js("window.__schreib")
    raus["aufgeraeumt"] = s.js("(()=>{const w=document.querySelector('#f-ings');return "
                               "!w.classList.contains('ings-sorting') && !w.querySelector('.dragging')"
                               " && !Array.from(w.querySelectorAll('.ing-row'))"
                               ".some(r=>r.style.transform)})()")
    return raus


def fall_wischen(s, url):
    aufbauen(s, url)
    z = rechteck(s, "#f-ings .ing-row", 0)
    raus = {"stVor": st(s)}
    s.js("window.__schreib=0; 1")
    s.tdown(z["x"], z["y"])
    # Bewusst laenger als die Haltezeit von 400 ms: ein echtes Wischen dauert das. Dass dabei
    # nichts aufgenommen wird, besorgt am Geraet schon Chrome selbst - es schickt
    # pointercancel, sobald das Scrollen uebernimmt.
    for i in range(1, 21):
        s.tmove(z["x"], z["y"] - 9 * i)
        time.sleep(0.03)
    raus["sortierzustand"] = s.js("document.querySelector('#f-ings')"
                                  ".classList.contains('ings-sorting')")
    raus["stNach"] = st(s)
    s.tup()
    time.sleep(0.5)
    raus["nachher"] = namen(s)
    raus["schreib"] = s.js("window.__schreib")
    return raus


def _zeile_im_randstreifen(s):
    u"""Die Zeile suchen, deren Mitte im unteren 48-px-Streifen des Sheets liegt."""
    b = sheet(s)
    n = s.js("document.querySelectorAll('#f-ings .ing-row').length")
    for i in range(n):
        r = rechteck(s, "#f-ings .ing-row", i)
        if b["unten"] - 48 < r["y"] < b["unten"]:
            return i, r, b
    return None, None, b


def fall_randzone(s, url):
    aufbauen(s, url)
    i, z, b = _zeile_im_randstreifen(s)
    raus = {"zeileGefunden": i is not None, "vorher": namen(s)}
    if i is None:
        return raus
    raus["scrollLuft"] = s.js("(()=>{const b=document.querySelector('.modal-body');"
                              "return Math.round(b.scrollHeight-b.clientHeight-b.scrollTop)})()")
    s.js("window.__schreib=0; 1")
    stVor = st(s)
    s.tdown(z["x"], z["y"])
    time.sleep(0.55)
    raus["aufgenommen"] = s.js("!!document.querySelector('#f-ings .ing-row.dragging')")
    # Von hier an bewegt sich der Finger keinen Pixel.
    time.sleep(0.9)
    raus["scrollWeg"] = st(s) - stVor
    s.tup()
    time.sleep(0.6)
    raus["nachher"] = namen(s)
    raus["schreib"] = s.js("window.__schreib")
    raus["offen"] = s.js("document.querySelectorAll('#f-ings .ing-row.editing').length")
    raus["spur"] = s.js("JSON.stringify(window.__spur||'')")
    return raus


def fall_autoscroll(s, url):
    aufbauen(s, url)
    z = rechteck(s, "#f-ings .ing-row", 0)
    b = sheet(s)
    raus = {}
    s.tdown(z["x"], z["y"])
    time.sleep(0.55)
    raus["aufgenommen"] = s.js("!!document.querySelector('#f-ings .ing-row.dragging')")
    stVor = st(s)
    ziel = b["unten"] - 30            # bewusst IN den Randstreifen hinein
    for i in range(1, 16):
        s.tmove(z["x"], z["y"] + (ziel - z["y"]) * i / 15.0)
        time.sleep(0.02)
    time.sleep(0.7)                   # am Rand halten
    raus["scrollWeg"] = st(s) - stVor
    s.tup()
    time.sleep(0.6)
    raus["nachher"] = namen(s)
    return raus


def main():
    args = sys.argv[1:]
    rueckbau = None
    if "--rueckbau" in args:
        i = args.index("--rueckbau")
        rueckbau = args[i + 1]
        del args[i:i + 2]
        if rueckbau not in RUECKBAUTEN:
            raise SystemExit("Unbekannter Rueckbau: %s (bekannt: %s)"
                             % (rueckbau, ", ".join(sorted(RUECKBAUTEN))))
    bleib = "--bleib" in args

    try:
        urllib.request.urlopen(SERVER + "index.html", timeout=5).read(64)
    except Exception:
        raise SystemExit("Der lokale Server antwortet nicht auf %s\n"
                         "  powershell -NoProfile -File test-server.ps1" % SERVER)

    url = SERVER + "index.html"
    if rueckbau:
        alt, neu = RUECKBAUTEN[rueckbau]
        quelle = io.open(os.path.join(BASIS, "index.html"), encoding="utf-8").read()
        if quelle.count(alt) != 1:
            raise SystemExit("Rueckbau '%s' fand seine Stelle nicht genau einmal (%d) - die "
                             "Gegenprobe wuerde sonst still gegen unveraenderten Code messen."
                             % (rueckbau, quelle.count(alt)))
        io.open(RUECKBAU_DATEI, "w", encoding="utf-8").write(quelle.replace(alt, neu, 1))
        url = SERVER + os.path.basename(RUECKBAU_DATEI)

    print("Geraeteabnahme Zutaten sortieren (Paket 3)")
    print("Buehne: %d x %d px, pointer: coarse, echte Touch-Ereignisse%s"
          % (BREITE, HOEHE, ("  [Rueckbau: " + rueckbau + "]") if rueckbau else ""))
    print("")

    cdp.START_URL = url
    cdp.stoppen()
    time.sleep(1.5)
    cdp.starten()
    s = Sitzung()
    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    try:
        a = fall_anfasser(s, url)
        p("Der Anfasser steckt in der Zeile", a.get("vorhanden"), True)
        p("Anfasser auf dem Handy unsichtbar", a.get("opacity"), "0")
        p("Anfasser auf dem Handy nicht antippbar", a.get("tippbar"), False)
        p("Kein Einzug im Ruhezustand", a.get("einzug"), "2px")
        p("Kein waagerechter Ueberlauf", a.get("quer"), True)

        z = fall_ziehen(s, url)
        getauscht = [NAMEN[1], NAMEN[0]] + NAMEN[2:]
        p("Ausgangsreihenfolge stimmt", z.get("vorher"), NAMEN)
        p("Vor Ablauf der Haltezeit NICHT aufgenommen", z.get("vorAblauf"), False)
        p("Nach Ablauf der Haltezeit aufgenommen", z.get("nachAblauf"), True)
        p("Der Nachbar weicht nach oben", z.get("nachbarWeicht"), True)
        p("Ziehen: Reihenfolge getauscht", z.get("nachher"), getauscht)
        p("Ziehen: auch gespeichert", z.get("gespeichert"), getauscht)
        p("Ziehen: genau EIN Schreibvorgang", z.get("schreib"), 1)
        p("Ziehen: Schwebezustand aufgeraeumt", z.get("aufgeraeumt"), True)

        w = fall_wischen(s, url)
        p("Wischen: das Sheet scrollt", w.get("stNach", 0) > w.get("stVor", 0) + 20, True)
        p("Wischen: keine Aufnahme", w.get("sortierzustand"), False)
        p("Wischen: Reihenfolge unveraendert", w.get("nachher"), NAMEN)
        p("Wischen: KEIN Schreibvorgang", w.get("schreib"), 0)

        r = fall_randzone(s, url)
        p("Randzone: eine Zeile liegt im Randstreifen", r.get("zeileGefunden"), True)
        p("Randzone: das Sheet haette Scrollweg", (r.get("scrollLuft") or 0) > 50, True)
        p("Randzone: die Zeile ist aufgenommen", r.get("aufgenommen"), True)
        p("Randzone: kein Autoscroll ohne Fingerbewegung", r.get("scrollWeg"), 0)
        p("Randzone: Reihenfolge unveraendert", r.get("nachher"), NAMEN)
        p("Randzone: KEIN Schreibvorgang", r.get("schreib"), 0)

        au = fall_autoscroll(s, url)
        p("Autoscroll: die Zeile ist aufgenommen", au.get("aufgenommen"), True)
        p("Autoscroll: der Finger am Rand scrollt mit", (au.get("scrollWeg") or 0) > 50, True)
        p("Autoscroll: die Zutat wandert dabei nach hinten",
          (au.get("nachher") or [None])[-1], NAMEN[0])
    finally:
        s.schliessen()
        if rueckbau and os.path.exists(RUECKBAU_DATEI):
            os.remove(RUECKBAU_DATEI)
        if not bleib:
            cdp.stoppen()

    breit = max(len(x[0]) for x in pruefungen)
    rot = 0
    for was, ok, ist, soll in pruefungen:
        if ok:
            print("  OK    " + was)
        else:
            rot += 1
            print("  ROT   " + was.ljust(breit) + "   ist=" + repr(ist) + "  soll=" + repr(soll))
    print("")
    print("ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
