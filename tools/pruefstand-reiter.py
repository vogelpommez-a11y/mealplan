# -*- coding: utf-8 -*-
u"""
Pruefstand Reiter: rendert JEDEN Reiter der App wirklich - faellt einer aus?

ANLASS (21.09.2026): Beim Umbau der Meals-Leiste fiel eine `const` weg, zwei Verwendungen
blieben stehen. Ergebnis: ReferenceError in render(), der Meals-Reiter blieb leer. Gefunden
hat es der Nutzer von Hand - beide vorhandenen Pruefungen waren GRUEN:

  * syntax-check.py findet einen fehlenden Bezeichner PRINZIPIELL nicht. Die Datei ist
    grammatikalisch einwandfrei; erst die Ausfuehrung stolpert.
  * /smoke laedt die App und prueft, ob #view gefuellt ist - dort steht aber der
    Onboarding- bzw. Anmeldebildschirm. Bis zu einem Reiter kommt er nie.

Damit gab es fuer alles HINTER dem Start keinen automatischen Beweis, dass es ueberhaupt
rendert. Genau diese Luecke schliesst dieser Pruefstand.

WAS ER PRUEFT - an der ECHTEN, geladenen App, nicht an einem Ausschnitt:
  * jeder Reiter aus ONB/TABS laesst sich anklicken
  * danach ist #view gefuellt (nicht null, nicht leer)
  * ein reiterspezifisches Merkmal ist da (sonst waere "gefuellt" auch der alte Inhalt)
  * waehrend des Wechsels wird KEIN window.onerror ausgeloest
  * console.error bleibt stumm

Bewusst KEINE Optikpruefung: Was wo wie aussieht, misst tools/abnahme-mobil.py. Hier geht
es nur um die Frage, die vorher niemand gestellt hat - kommt ueberhaupt etwas an?

UMGEBUNG: Edge headless mit eigenem, JEDES MAL FRISCHEM Profil und Debug-Port.
NIE tools/cdp.py verwenden - dessen Profil ist bestimmungsgemaess mit dem echten
Cloud-Konto angemeldet (docs/TESTING.md, browser-abnahme-cloud-falle). Hier wird ein
Testzustand geschrieben, und der hat in einem angemeldeten Profil nichts verloren.

Aufrufe:
    python tools/pruefstand-reiter.py
    python tools/pruefstand-reiter.py --sichtbar    # Fenster zeigen, zum Zuschauen
    python tools/pruefstand-reiter.py --gegenprobe  # baut einen Fehler ein: merkt er ihn?
"""
import io
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 9333
PROFIL = os.path.join(os.environ.get("TEMP", "."), "mp-edge-reiter")
URL = "http://localhost:8000/index.html"

EDGE_PFADE = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

# Je Reiter ein Merkmal, das es NUR dort gibt. Ohne das waere "#view ist gefuellt" wertlos:
# Bleibt ein Klick wirkungslos, stuende der vorige Inhalt noch da und alles waere gruen.
REITER = [
    # Nachgeschlagen, nicht geraten: .home/.hero/.ring gibt es in dieser App nicht.
    # Der Startreiter traegt die Zielkarten (.wg-c, .wg-actions) und die Als-Naechstes-
    # Karte (.hm-card). Ein geratener Selektor haette hier ROT gemeldet, obwohl die App
    # heil ist - ein Pruefer mit erfundenen Fakten ist schlimmer als keiner (CLAUDE.md 18a).
    (u"home",     u"Start",      ".wg-c, .wg-actions, .hm-card"),
    (u"plan",     u"Plan",       ".week, .daybar, .plan-tools"),
    (u"recipes",  u"Meals",      ".rcard, .week-switch, .recipe-search, .empty"),
    (u"progress", u"Fortschritt", ".kal-seg, .zeitraum, .wch, .empty"),
]

# Fuenf Meals, ein Ziel, keine Wochenplanung: genug, damit jeder Reiter etwas zu zeigen hat,
# und wenig genug, dass der Zustand hier lesbar bleibt.
ZUSTAND = {
    "tab": "home", "onboarded": True,
    "goal": {"mode": "cut", "kcal": 1950, "protein": 150, "carbs": 180, "fat": 60,
             "activity": "pal14", "training": []},
    "recipes": [
        {"id": "r1", "name": "Ofen-Lachs", "cat": "Hauptgericht", "mealPrep": True,
         "tags": ["highprotein"],
         "nutrition": {"kcal": 520, "protein": 42, "carbs": 18, "fat": 30}},
        {"id": "r2", "name": "Skyr-Bowl", "cat": "Fruehstueck", "tags": ["highprotein"],
         "nutrition": {"kcal": 310, "protein": 34, "carbs": 28, "fat": 6}},
        {"id": "r3", "name": "Linsencurry", "cat": "Hauptgericht", "mealPrep": True,
         "tags": ["vegan"],
         "nutrition": {"kcal": 430, "protein": 19, "carbs": 58, "fat": 12}},
        {"id": "r4", "name": "Haferbrei", "cat": "Fruehstueck", "tags": ["vegetarisch"],
         "nutrition": {"kcal": 360, "protein": 12, "carbs": 62, "fat": 7}},
        {"id": "r5", "name": "Haehnchen-Wrap", "cat": "Mittagessen",
         "nutrition": {"kcal": 480, "protein": 38, "carbs": 44, "fat": 14}},
    ],
    "plans": {}, "weights": [], "weightGoals": {}, "weekStats": {},
}


def edge_pfad():
    for p in EDGE_PFADE:
        if os.path.isfile(p):
            return p
    return None


def server_laeuft():
    try:
        urllib.request.urlopen("http://localhost:8000/", timeout=3)
        return True
    except Exception:
        return False


def server_starten():
    u"""Wie in tools/vorfuehren.py - der Reihenlauf soll nicht an einer Vorbedingung
    scheitern, die sich in drei Sekunden selbst herstellen laesst."""
    subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Minimized",
                      "-File", os.path.join(WURZEL, "test-server.ps1")], cwd=WURZEL)
    for _ in range(30):
        time.sleep(0.5)
        if server_laeuft():
            return True
    return False


class Browser(object):
    u"""Duenne CDP-Fernbedienung. Eigene Klasse statt tools/cdp.py, weil DORT bewusst
    ein angemeldetes Profil liegt - siehe Kopf dieser Datei."""

    def __init__(self, sichtbar=False):
        import websocket  # noqa: F401  (frueh scheitern, wenn es fehlt)
        exe = edge_pfad()
        if not exe:
            raise RuntimeError(u"Edge nicht gefunden. Pfade: %s" % ", ".join(EDGE_PFADE))
        # Jedes Mal frisch: Ein liegengebliebenes Profil bringt alten localStorage mit,
        # und dann prueft der Lauf einen Zustand, den niemand gesetzt hat.
        shutil.rmtree(PROFIL, ignore_errors=True)
        args = [exe, "--disable-gpu", "--remote-debugging-port=%d" % PORT,
                "--remote-allow-origins=*", "--user-data-dir=" + PROFIL, URL]
        if not sichtbar:
            args.insert(1, "--headless=new")
        self.proc = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)
        self.ws = None
        self._id = 0
        self._verbinden()

    def _seiten(self):
        with urllib.request.urlopen("http://127.0.0.1:%d/json" % PORT, timeout=5) as r:
            return json.loads(r.read().decode("utf-8"))

    def _verbinden(self):
        import websocket
        ziel = None
        for _ in range(50):
            try:
                treffer = [t for t in self._seiten()
                           if t.get("type") == "page" and "index.html" in t.get("url", "")]
                if treffer:
                    ziel = treffer[0]
                    break
            except Exception:
                pass
            time.sleep(.4)
        if not ziel:
            raise RuntimeError(u"Edge kam nicht hoch oder die Seite fehlt.")
        self.ws = websocket.create_connection(
            ziel["webSocketDebuggerUrl"], timeout=25,
            origin="http://127.0.0.1:%d" % PORT, suppress_origin=False)

    def js(self, code):
        self._id += 1
        self.ws.send(json.dumps({"id": self._id, "method": "Runtime.evaluate",
                                 "params": {"expression": code, "returnByValue": True,
                                            "awaitPromise": True}}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") != self._id:
                continue
            r = m.get("result", {})
            if "exceptionDetails" in r:
                besch = r["exceptionDetails"].get("exception", {}).get("description", "")
                return {"__fehler": str(besch)[:300]}
            return r.get("result", {}).get("value")

    def zu(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception:
            pass
        try:
            self.proc.kill()
        except Exception:
            pass


def lauf(sichtbar=False):
    u"""Liefert (befunde, zeilen). befunde = Liste der ROT-Meldungen."""
    b = Browser(sichtbar)
    befunde, zeilen = [], []
    try:
        b.js("localStorage.setItem('wochenkueche_v1__test', %s);"
             "localStorage.setItem('wochenkueche_profile_v1__test', %s);"
             % (json.dumps(json.dumps(ZUSTAND)),
                json.dumps(json.dumps({"name": "Probe", "id": "lokal"}))))
        b.js("location.reload()")
        time.sleep(3)

        # Laufzeitfehler ab hier mitschreiben. window.onerror faengt genau das, was
        # syntax-check.py nicht sehen kann: einen Fehler bei der AUSFUEHRUNG.
        b.js("window.__f = [];"
             "window.addEventListener('error', e => window.__f.push(String(e.message)));"
             "(function(){var o=console.error;console.error=function(){"
             "window.__f.push('console.error: ' + Array.prototype.join.call(arguments,' '));"
             "return o.apply(console, arguments);};})();")

        for key, label, merkmal in REITER:
            sel = '[data-action="tab"][data-tab="%s"]' % key
            klick = b.js("(function(){var b=document.querySelector(%s);"
                         "if(!b) return 'fehlt'; b.click(); return 'ok';})()"
                         % json.dumps(sel))
            time.sleep(1.2)
            if klick != "ok":
                befunde.append(u"%s: Reiterknopf nicht gefunden" % label)
                zeilen.append((u"ROT", label, u"Reiterknopf fehlt"))
                continue

            gefuellt = b.js("(function(){var v=document.getElementById('view');"
                            "return !!v && v.children.length > 0;})()")
            treffer = b.js("document.querySelectorAll(%s).length" % json.dumps(merkmal))
            fehler = b.js("(window.__f || []).slice()")

            if isinstance(gefuellt, dict) or gefuellt is not True:
                befunde.append(u"%s: #view ist leer" % label)
                zeilen.append((u"ROT", label, u"#view leer"))
            elif isinstance(treffer, dict) or not treffer:
                befunde.append(u"%s: kein Merkmal des Reiters gefunden (%s)" % (label, merkmal))
                zeilen.append((u"ROT", label, u"gerendert, aber nichts davon: %s" % merkmal))
            elif fehler:
                befunde.append(u"%s: Laufzeitfehler %r" % (label, fehler))
                zeilen.append((u"ROT", label, u"Laufzeitfehler: %s" % fehler[0][:70]))
            else:
                zeilen.append((u"ok", label, u"%d Treffer" % treffer))
            b.js("window.__f = [];")
    finally:
        b.zu()
    return befunde, zeilen


def main():
    args = sys.argv[1:]
    sichtbar = "--sichtbar" in args
    gegenprobe = "--gegenprobe" in args
    os.chdir(WURZEL)

    if not server_laeuft() and not server_starten():
        print(u"FEHLGESCHLAGEN: Kein Server auf :8000, und er liess sich nicht starten.")
        print(u"Von Hand:  powershell -NoProfile -File test-server.ps1")
        return 2

    if gegenprobe:
        # Ein Reiter wird absichtlich zerschossen - meldet der Pruefstand das auch?
        # Ohne diesen Lauf ist ein gruenes Ergebnis nichts wert (CLAUDE.md 11).
        pfad = os.path.join(WURZEL, "index.html")
        # newline="" auch beim LESEN: Ohne das macht Python universal newlines, aus
        # CRLF wird LF, und die Sicherung schreibt hinterher ANDERE Zeilenenden zurueck.
        # Inhaltlich identisch, fuer git trotzdem die ganze Datei geaendert.
        sicherung = io.open(pfad, encoding="utf-8", newline="").read()
        marke = "  function paintRecipeGroups("
        if marke not in sicherung:
            print(u"Gegenprobe nicht moeglich: Anker fehlt.")
            return 2
        kaputt = sicherung.replace(
            marke, "  function paintRecipeGroups(){ GIBTESNICHT(); }\n" + marke, 1)
        io.open(pfad, "w", encoding="utf-8", newline="").write(kaputt)
        try:
            print(u"GEGENPROBE - ein Reiter ist absichtlich zerschossen:")
            befunde, zeilen = lauf(sichtbar)
            for zustand, label, text in zeilen:
                print(u"  %-4s %-14s %s" % (zustand, label, text))
            print()
            if befunde:
                print(u"BESTANDEN: %d Befund(e) - der Pruefstand merkt es." % len(befunde))
                return 0
            print(u"DURCHGEFALLEN: nichts gemeldet. Der Pruefstand misst nicht,")
            print(u"was er zu messen vorgibt (CLAUDE.md 11).")
            return 1
        finally:
            io.open(pfad, "w", encoding="utf-8", newline="").write(sicherung)

    befunde, zeilen = lauf(sichtbar)
    print(u"Reiter - rendert jeder?")
    print(u"=" * 52)
    for zustand, label, text in zeilen:
        print(u"  %-4s %-14s %s" % (zustand, label, text))
    print()
    print(u"ERGEBNIS %d Reiter gruen, %d rot" % (len(zeilen) - len(befunde), len(befunde)))
    if not befunde:
        print()
        print(u"Das heisst NICHT, dass sie richtig aussehen - nur, dass ueberhaupt")
        print(u"etwas ankommt. Fuer die Optik: python tools/abnahme-mobil.py")
        return 0
    print()
    for f in befunde:
        print(u"  " + f)
    return 1


if __name__ == "__main__":
    sys.exit(main())
