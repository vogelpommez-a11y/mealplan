# -*- coding: utf-8 -*-
u"""Geraeteabnahme: Meals im Wochenplan mit dem Finger sortieren.

Das Gegenstueck zu tools/pruefstand-plan-sortieren.py. Der laeuft headless und misst die
Reihenfolge - er kann aber ueber zwei Dinge nichts sagen, und beide entscheiden hier ueber
Erfolg oder Misserfolg:

  * Das MITSCROLLEN. Unter --headless=new feuert requestAnimationFrame genau einmal, der
    Autoscroll kaeme dort nie in Gang, und jeder Fall dazu waere dauerhaft gruen, ohne
    etwas zu messen.
  * Die WISCHGESTE zum Nachbartag. Der Wochenplan ist auf dem Handy ein waagerechter
    Snap-Streifen. Eine neue Geste darin kann ihn toeten - genau das ist am 08.08.2026
    schon einmal passiert (docs/TROUBLESHOOTING.md 58), und zwar durch sechs unsichtbare
    Pixel. Ob gewischt werden kann, zeigt nur ein echtes Touch-Geraet.

Hier laeuft deshalb ein sichtbarer Chrome mit echter Geraete-Emulation ueber das
DevTools-Protokoll: echter CSS-Viewport, pointer: coarse, und Gesten als
Input.dispatchTouchEvent - keine synthetischen PointerEvents.

Alles in EINER offenen Verbindung: Zeigertyp und Farbschema gelten nur in der Verbindung,
die sie gesetzt hat (tools/cdp.py, messen()). Wer je Kommando neu verbindet, misst
pointer: fine und haelt eine Desktop-Messung fuer eine Handy-Abnahme.

Eigenes Chrome-Profil auf einem eigenen Port: das Profil von tools/cdp.py ist an einem
echten Firebase-Konto angemeldet, und Testdaten gehoeren nicht in ein angemeldetes Profil.

SECHS FAELLE:
  anfasser     auf dem Handy ist der Anfasser unsichtbar und nicht antippbar
  ziehen       halten, ziehen, loslassen - Reihenfolge getauscht, genau EINMAL gespeichert
  kategorie    mit dem Finger von "Abendessen" nach "Fruehstueck" desselben Tages
  wischen      ohne aufgenommene Karte wechselt der Wisch weiterhin den Tag
  gehalten     MIT aufgenommener Karte wechselt derselbe Wisch den Tag NICHT
  autoscroll   wer den Finger an den unteren Rand fuehrt, scrollt die Seite mit

Gegenproben - ohne sie zaehlt kein Ergebnis:
  python tools/abnahme-plan-sortieren.py --rueckbau autoscroll  # Autoscroll ausgebaut
  python tools/abnahme-plan-sortieren.py --rueckbau touch       # die touchmove-Abwehr ausgebaut

Keine Gegenprobe gibt es fuer den Wischabbruch vor der Haltezeit: am echten Geraet schickt
Chrome pointercancel, sobald das Scrollen uebernimmt - die Geste ist da schon beendet.
Geprueft wird sie headless im Pruefstand.

Voraussetzung: der lokale Server laeuft.
    powershell -NoProfile -File test-server.ps1

Aufruf:  python tools/abnahme-plan-sortieren.py [--rueckbau <name>] [--bleib]
         --bleib laesst Chrome offen, um selbst nachzusehen.
"""
import io, json, os, sys, time

HIER = os.path.dirname(os.path.abspath(__file__))
BASIS = os.path.dirname(HIER)
sys.path.insert(0, HIER)
import cdp

cdp.PORT = 9224
cdp.PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-chrome-abnahme-plan")

BREITE, HOEHE = 390, 844
SERVER = "http://localhost:8000/"
# Der Rueckbau wird als eigene Datei NEBEN index.html ausgeliefert: die relativen Pfade auf
# css/, data/, lib/ und vendor/ stimmen nur auf dieser Ebene. .gitignore haelt sie draussen,
# das finally loescht sie wieder.
RUECKBAU_DATEI = os.path.join(BASIS, "_abnahme-rueckbau-plan.html")

RUECKBAUTEN = {
    "autoscroll": ("if (dg.scrollV && !dg.raf) dg.raf = requestAnimationFrame(dgScrollSchritt);",
                   "/* rueckgebaut */"),
    # Ohne diese Zeile gehoert die Bewegung waehrend der Geste wieder dem Snap-Streifen -
    # dann wischt der Finger den Tag weg, obwohl er eine Karte haelt.
    "touch": ('wurzel.addEventListener("touchmove", e => { if (dg && dg.aktiv) e.preventDefault(); }, { passive: false });',
              "/* rueckgebaut */"),
}

GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}
MEALS = [
    {"id": "m1", "name": "Haehnchen mit Reis", "category": "Hauptgericht"},
    {"id": "m2", "name": "Lachs mit Brokkoli", "category": "Hauptgericht"},
    {"id": "m3", "name": "Chili sin Carne", "category": "Hauptgericht"},
]
NAMEN = ["Haehnchen mit Reis", "Lachs mit Brokkoli", "Chili sin Carne"]

# Der Plan-Reiter springt beim Betreten immer auf HEUTE (Anker-Regel, siehe renderPlan).
# Auf dem Handy ist damit nur dieser eine Tag im Bild - ein fest auf Montag verdrahteter
# Selektor zeigte an jedem anderen Wochentag auf eine Karte weit ausserhalb des
# Bildschirms, und jede Geste darauf ginge ins Leere. Gemessen am 12.09.2026: x = -1675.
import datetime as _dt
TAG = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][_dt.date.today().weekday()]
SEL_KARTE = '.slot[data-slot="%s:ab"] .filled' % TAG
SEL_FR = '.slot[data-slot="%s:fr"]' % TAG
SEL_GRIP = '.slot[data-slot="%s:ab"] .pm-grip' % TAG
SEL_TAG = '.week > .day:nth-child(%d)' % (["mon","tue","wed","thu","fri","sat","sun"].index(TAG) + 1)


def meal(m):
    return {"id": m["id"], "name": m["name"], "category": m["category"], "tags": [],
            "nutrition": {"kcal": 500, "carbs": 50, "protein": 30, "fat": 15},
            "steps": "Alles zusammen in die Pfanne.", "ingredients": ["Zutat"]}


def zustand():
    plan = {}
    for tag in ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]:
        plan[tag] = {"fr": [], "mi": [], "ab": [], "sn": []}
    # Genug Karten, dass die Seite laenger wird als der Bildschirm - sonst gibt es keinen
    # Scrollweg, und der Autoscroll-Fall misst nichts.
    plan[TAG]["ab"] = ["m1", "m2", "m3"]
    plan[TAG]["mi"] = ["m1", "m2", "m3"]
    plan[TAG]["sn"] = ["m1", "m2", "m3"]
    return {"recipes": [meal(m) for m in MEALS], "plans": {"__WOCHE__": plan}, "goal": GOAL,
            "onboarded": True, "tab": "plan", "favs": [], "planned": {},
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

    def schliessen(self):
        try:
            self.ws.close()
        except Exception:
            pass


def rechteck(s, sel, nr=0):
    return s.js("(()=>{const e=document.querySelectorAll(%s)[%d];if(!e)return null;"
                "const b=e.getBoundingClientRect();return JSON.stringify("
                "{x:b.left+b.width/2,y:b.top+b.height/2,top:b.top,unten:b.bottom,hoehe:b.height})})()"
                % (json.dumps(sel), nr))


def namen(s, fach="ab"):
    return s.js("JSON.stringify(Array.from(document.querySelectorAll("
                "'.slot[data-slot=\"%s:%s\"] .filled .r-name')).map(e=>e.textContent))" % (TAG, fach))


def gespeichert(s, fach="ab"):
    return s.js("(()=>{const d=JSON.parse(localStorage.getItem('wochenkueche_v1__test')||'{}');"
                "const w=d.plans||{};const k=Object.keys(w)[0];if(!k)return '[]';"
                "const l=((w[k]['%s'])||{})['%s']||[];"
                "return JSON.stringify(l.map(e=>typeof e==='string'?e:e.id))})()" % (TAG, fach))


def warte_auf(s, sel, was, sekunden=15):
    u"""Aktiv warten statt fest zu schlafen - ein langsamer Rechner darf die Abnahme nicht
    in einen Fehler laufen lassen, und ein wirklich fehlendes Element soll klar dastehen."""
    bis = time.time() + sekunden
    while time.time() < bis:
        try:
            if s.js("document.querySelectorAll(%s).length" % json.dumps(sel)):
                time.sleep(0.25)

                return True
        except Exception:
            pass
        time.sleep(0.25)
    raise SystemExit("Nicht gefunden: %s (%s) - der Weg in die App stimmt nicht mehr." % (was, sel))


def aufbauen(s, url):
    u"""Frischer Zustand und der echte Weg in den Plan-Reiter."""
    s.js("location.href = %s; 1" % json.dumps(url))
    warte_auf(s, "#view", "die App")
    # Der Wochenschluessel muss der sein, den die App fuer "diese Woche" bildet - sonst legt
    # sie einen leeren Plan an und die Abnahme misst eine leere Seite.
    s.js("(()=>{function iso(d){var t=new Date(d.getFullYear(),d.getMonth(),d.getDate());"
         "t.setDate(t.getDate()+3-((t.getDay()+6)%7));var e=new Date(t.getFullYear(),0,4);"
         "var w=1+Math.round(((t-e)/86400000-3+((e.getDay()+6)%7))/7);"
         "return t.getFullYear()+'-W'+(w<10?'0':'')+w;}"
         "var st=" + json.dumps(zustand()) + ";"
         "var p=st.plans['__WOCHE__']; delete st.plans['__WOCHE__']; st.plans[iso(new Date())]=p;"
         "localStorage.setItem('wochenkueche_v1__test', JSON.stringify(st));"
         "localStorage.setItem('wochenkueche_profile_v1__test', JSON.stringify({name:'Test'}));"
         "location.reload(); return 1})()")
    time.sleep(1.2)
    # Bewusst ueber die Kennung des Reiterknopfs: data-tab="plan" traegt auch die grosse
    # Bildkachel im Startreiter, und die stand hier zuerst im Dokument.
    warte_auf(s, "#tab-plan", "die Reiterleiste")
    s.js("document.getElementById('tab-plan').click(); 1")
    warte_auf(s, SEL_KARTE, "die Meal-Karten im Plan")
    time.sleep(0.4)
    # Schreibvorgaenge zaehlen, und nur den eigenen des Ablegens: render() endet seit jeher
    # mit save(), und hydrateImages() schreibt denselben Schluessel asynchron nach.
    s.js("(()=>{window.__schreib=0;const echt=localStorage.setItem.bind(localStorage);"
         "localStorage.setItem=function(k,v){const sp=String((new Error()).stack||'');"
         "if(k==='wochenkueche_v1__test' && sp.indexOf('abgelegt')>=0 && sp.indexOf('at render')<0)"
         " window.__schreib++;"
         "return echt(k,v);};return 1})()")


def seitenscroll(s):
    return s.js("Math.round((document.scrollingElement||document.documentElement).scrollTop)")


def wochenscroll(s):
    return s.js("Math.round(document.querySelector('.week').scrollLeft)")


# ---------------- Die Faelle ----------------

def fall_anfasser(s, url):
    aufbauen(s, url)
    return s.js("(()=>{const g=document.querySelector('" + SEL_GRIP + "');"
                "if(!g) return JSON.stringify({vorhanden:false});"
                "const c=getComputedStyle(g);"
                "const k=document.querySelector('" + SEL_KARTE + "');"
                "const tag=document.querySelector('" + SEL_TAG + "');"
                "return JSON.stringify({vorhanden:true,opacity:c.opacity,"
                "tippbar:c.pointerEvents!=='none',"
                "einzug:getComputedStyle(k).paddingLeft,"
                "querTag:tag.scrollWidth-tag.clientWidth})})()")


def fall_ziehen(s, url):
    aufbauen(s, url)
    z = rechteck(s, SEL_KARTE, 0)
    raus = {"vorher": namen(s)}
    s.js("window.__schreib=0; 1")
    s.tdown(z["x"], z["y"])
    time.sleep(0.25)
    raus["vorAblauf"] = s.js("!!document.querySelector('#view .filled.dragging')")
    time.sleep(0.35)
    raus["nachAblauf"] = s.js("!!document.querySelector('#view .filled.dragging')")
    # Ein paar Pixel ueber die Kartenhoehe hinaus: der Zielwechsel greift erst, wenn die
    # Mitte die Nachbarmitte wirklich ueberschreitet - genau auf der Kante passiert nichts.
    weg = z["hoehe"] + 6
    for i in range(1, 15):
        s.tmove(z["x"], z["y"] + weg * i / 14.0)
        time.sleep(0.02)
    raus["nachbarWeicht"] = s.js("(()=>{const r=document.querySelectorAll("
                                 "'" + SEL_KARTE + "')[1];"
                                 "return (r.style.transform||'').indexOf('translateY(-')===0})()")
    s.tup()
    time.sleep(0.7)
    raus["nachher"] = namen(s)
    raus["gespeichert"] = gespeichert(s)
    raus["schreib"] = s.js("window.__schreib")
    raus["aufgeraeumt"] = s.js("(()=>{const v=document.querySelector('#view');return "
                               "!v.classList.contains('plan-sorting') && !v.querySelector('.dragging')"
                               " && !v.querySelector('.slot.dragover')})()")
    return raus


def fall_kategorie(s, url):
    aufbauen(s, url)
    z = rechteck(s, SEL_KARTE, 0)
    ziel = rechteck(s, SEL_FR)
    raus = {"vorherAb": namen(s), "vorherFr": namen(s, "fr")}
    s.js("window.__schreib=0; 1")
    s.tdown(z["x"], z["y"])
    time.sleep(0.55)
    raus["aufgenommen"] = s.js("!!document.querySelector('#view .filled.dragging')")
    schritte = 16
    for i in range(1, schritte + 1):
        s.tmove(z["x"] + (ziel["x"] - z["x"]) * i / schritte,
                z["y"] + (ziel["y"] - z["y"]) * i / schritte)
        time.sleep(0.03)
    raus["zielMarkiert"] = s.js("!!document.querySelector('" + SEL_FR + ".dragover')")
    s.tup()
    time.sleep(0.7)
    raus["nachherAb"] = gespeichert(s)
    raus["nachherFr"] = gespeichert(s, "fr")
    raus["schreib"] = s.js("window.__schreib")
    return raus


def fall_wischen(s, url):
    u"""Ohne aufgenommene Karte muss der Wisch weiterhin den Tag wechseln."""
    aufbauen(s, url)
    z = rechteck(s, SEL_KARTE, 0)
    # Der Ausgangsstand wird GEMESSEN, nicht vorausgesetzt: Der Neuaufbau schreibt zwar
    # frische Daten, aber ein Reload und ein noch laufendes save() des vorigen Falls koennen
    # sich ueberholen. Ein fester Sollwert misst dann die Vorgeschichte statt des Wischs.
    raus = {"vor": wochenscroll(s), "vorher": gespeichert(s)}
    s.tdown(z["x"], z["y"])
    # Sofort seitlich weg, lange vor der Haltezeit - das ist ein Wisch, kein Aufnehmen.
    for i in range(1, 21):
        s.tmove(z["x"] - 16 * i, z["y"])
        time.sleep(0.02)
    s.tup()
    time.sleep(1.2)
    raus["nach"] = wochenscroll(s)
    raus["nachher"] = gespeichert(s)
    return raus


def fall_gehalten(s, url):
    u"""MIT aufgenommener Karte darf derselbe Wisch den Tag NICHT wechseln."""
    aufbauen(s, url)
    z = rechteck(s, SEL_KARTE, 0)
    raus = {"vor": wochenscroll(s)}
    s.tdown(z["x"], z["y"])
    time.sleep(0.55)
    raus["aufgenommen"] = s.js("!!document.querySelector('#view .filled.dragging')")
    for i in range(1, 21):
        s.tmove(z["x"] - 16 * i, z["y"])
        time.sleep(0.02)
    raus["nach"] = wochenscroll(s)
    s.tup()
    time.sleep(0.7)
    return raus


def fall_autoscroll(s, url):
    aufbauen(s, url)
    z = rechteck(s, SEL_KARTE, 0)
    raus = {"luft": s.js("Math.round((document.scrollingElement||document.documentElement)"
                         ".scrollHeight - innerHeight)")}
    s.tdown(z["x"], z["y"])
    time.sleep(0.55)
    raus["aufgenommen"] = s.js("!!document.querySelector('#view .filled.dragging')")
    vor = seitenscroll(s)
    ziel = HOEHE - 25            # bewusst IN den Randstreifen hinein
    for i in range(1, 16):
        s.tmove(z["x"], z["y"] + (ziel - z["y"]) * i / 15.0)
        time.sleep(0.02)
    # Von hier an steht der Finger still, im Randstreifen - jetzt muss die Seite laufen.
    time.sleep(1.2)
    raus["scrollWeg"] = seitenscroll(s) - vor
    s.tup()
    time.sleep(0.7)
    return raus


def main():
    args = [a for a in sys.argv[1:]]
    bleib = "--bleib" in args
    if bleib:
        args.remove("--bleib")
    rueckbau = None
    if "--rueckbau" in args:
        i = args.index("--rueckbau")
        rueckbau = args[i + 1]
        del args[i:i + 2]

    url = SERVER + "index.html"
    if rueckbau:
        if rueckbau not in RUECKBAUTEN:
            raise SystemExit("Unbekannter Rueckbau: " + rueckbau)
        alt, neu = RUECKBAUTEN[rueckbau]
        quelle = io.open(os.path.join(BASIS, "index.html"), encoding="utf-8").read()
        if quelle.count(alt) != 1:
            raise SystemExit("Rueckbau '%s' fand seine Stelle nicht genau einmal (%d) - die "
                             "Abnahme wuerde sonst still gegen unveraenderten Code messen."
                             % (rueckbau, quelle.count(alt)))
        io.open(RUECKBAU_DATEI, "w", encoding="utf-8").write(quelle.replace(alt, neu, 1))
        url = SERVER + os.path.basename(RUECKBAU_DATEI)

    print("Abnahme: Meals im Wochenplan sortieren"
          + (("   [Rueckbau: " + rueckbau + "]") if rueckbau else ""))
    print("Geraet: %dx%d, pointer: coarse, echte Touch-Ereignisse" % (BREITE, HOEHE))
    print("")

    cdp.starten()
    s = Sitzung()
    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    try:
        a = fall_anfasser(s, url)
        p("Der Anfasser steckt in der Karte", a.get("vorhanden"), True)
        p("Anfasser auf dem Handy unsichtbar", a.get("opacity"), "0")
        p("Anfasser auf dem Handy nicht antippbar", a.get("tippbar"), False)
        # Auf dem Handy hat die Karte seitlich gar kein Innenmass (mobil.css, Listen-Optik).
        # Der Anfasser darf daran nichts aendern - er kostet dort keinen Platz, weil der
        # Einzug nur unter @media (hover: hover) gesetzt wird.
        p("Kein Einzug im Ruhezustand", a.get("einzug"), "0px")
        p("Die Tageskarte laeuft waagerecht nicht ueber", a.get("querTag"), 0)

        z = fall_ziehen(s, url)
        p("Ausgangsreihenfolge stimmt", z.get("vorher"), NAMEN)
        p("Vor Ablauf der Haltezeit NICHT aufgenommen", z.get("vorAblauf"), False)
        p("Nach Ablauf der Haltezeit aufgenommen", z.get("nachAblauf"), True)
        p("Der Nachbar weicht nach oben", z.get("nachbarWeicht"), True)
        p("Ziehen: Reihenfolge getauscht", z.get("gespeichert"), ["m2", "m1", "m3"])
        p("Ziehen: genau EIN Schreibvorgang", z.get("schreib"), 1)
        p("Ziehen: Schwebezustand aufgeraeumt", z.get("aufgeraeumt"), True)

        k = fall_kategorie(s, url)
        p("Kategorie: Karte aufgenommen", k.get("aufgenommen"), True)
        p("Kategorie: das Zielfach ist markiert", k.get("zielMarkiert"), True)
        p("Kategorie: Meal liegt im Fruehstueck", k.get("nachherFr"), ["m1"])
        p("Kategorie: und ist aus dem Abendessen raus", k.get("nachherAb"), ["m2", "m3"])
        p("Kategorie: genau EIN Schreibvorgang", k.get("schreib"), 1)

        w = fall_wischen(s, url)
        p("Wischen ohne Karte wechselt weiterhin den Tag", (w.get("nach") or 0) > 100, True)
        p("Wischen ohne Karte sortiert nichts", w.get("nachher"), w.get("vorher"))

        g = fall_gehalten(s, url)
        p("Gehalten: die Karte ist aufgenommen", g.get("aufgenommen"), True)
        p("Gehalten: derselbe Wisch wechselt den Tag NICHT", g.get("nach"), g.get("vor"))

        au = fall_autoscroll(s, url)
        p("Autoscroll: die Seite haette Scrollweg", (au.get("luft") or 0) > 50, True)
        p("Autoscroll: die Karte ist aufgenommen", au.get("aufgenommen"), True)
        p("Autoscroll: der Finger am Rand scrollt mit", (au.get("scrollWeg") or 0) > 50, True)
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
