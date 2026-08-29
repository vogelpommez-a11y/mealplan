# -*- coding: utf-8 -*-
u"""
Verifikation vor dem Fix: Ist `weekLabel()` wirklich zweimal deklariert?

`index.html` traegt zwei Top-Level-Funktionen dieses Namens:
  * eine erwartet einen Wochenschluessel ("2026-W33")  -> "KW 33 - 10.08."
  * eine erwartet eine Zahl (Offset in Wochen)          -> "Woche 29 - 13.-19. Juli"

Liegen beide im selben Scope, gewinnt die spaetere fuer ALLE Aufrufer (Hoisting), und die
sieben Aufrufer mit Wochenschluessel rechnen `getDate() + "2026-W33" * 7` -> NaN.

Die Klammerbilanz ist als Beweis untauglich (Regex- und Template-Literale verfaelschen sie).
Deshalb wird hier die ECHTE App headless gestartet, mit einer Wiegung im Zustand, und die
Beschriftung im Gewichtsdiagramm abgelesen. Von aussen aufrufbar ist `weekLabel()` nicht -
sie lebt im IIFE. Die Anzeige ist der Beweis.

Aufruf:  python tools/pruefstand-wochenbeschriftung.py [pfad-zu-index.html]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
ANKER = '<meta charset="utf-8">'   # index.html hat kein <head>-Tag, siehe TROUBLESHOOTING 109

GOAL = {"kcal": 2200, "carbs": 220, "protein": 160, "fat": 65, "sex": "m", "age": 34,
        "height": 182, "weight": 88, "activity": "pal16", "mode": "lose", "pace": "moderate",
        "training": {}}
# GENAU EINE Wiegung. Bei mehreren laesst rueckblickHtml() die .wch-tip absichtlich leer
# (dort steht dann der Vergleich, nicht der Einzelwert) - der Text, um den es hier geht,
# waere gar nicht da, und die Pruefung liefe ins Leere.
STATE = {
    "recipes": [], "plans": {}, "goal": GOAL, "onboarded": True, "tab": "progress",
    "favs": [], "planned": {}, "shopPersons": 1, "viewWeek": "cur",
    "weights": [{"m": "2026-W33", "kg": 88.5}],
    "weightGoals": {"2026": 82},
    "weightConsent": {"given": True, "at": 1755000000000}
}
PROFILE = {"name": "Test"}

MESS = u'''<script>setTimeout(function () {
  var raus = {};
  try {
    var reiter = document.querySelector('[data-tab="progress"]');
    raus.reiterDa = !!reiter;
    if (reiter) reiter.click();
    var tip = document.querySelector(".wch-tip");
    raus.tip = tip ? tip.textContent.trim() : "(keine .wch-tip)";
    var pt = document.querySelector(".wch-pt");
    raus.punktLabel = pt ? (pt.getAttribute("aria-label") || "") : "(kein .wch-pt)";
    // Der zweite Aufrufer: die Zeile ueber dem Hero erwartet eine ZAHL (Wochen-Offset).
    // Sie muss unveraendert richtig bleiben - sie ist ja die Deklaration, die gewinnt.
    // Sie steht auf HOME, nicht im Plan-Reiter (appHeroHtml laeuft in renderHome).
    var home = document.querySelector('[data-tab="home"]');
    if (home) home.click();
    var eyebrow = document.querySelector(".eyebrow");
    raus.planLabel = eyebrow ? eyebrow.textContent.trim() : "(keine .eyebrow)";
  } catch (e) { raus.messfehler = e.message; }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  var p = document.createElement("pre");
  p.id = "messung"; p.textContent = JSON.stringify(raus);
  document.documentElement.appendChild(p);
}, 400);</script>'''


def lauf():
    seite = pm_quelle.lade_seite(INDEX)
    # "__test"-Suffix: localKey() haengt es unter file:// an jeden Schluessel (isTestOrigin).
    seed = (u'<script>window.__fehler=[];'
            u'window.addEventListener("error",function(e){window.__fehler.push((e.message||"")+" @"+(e.lineno||"?"));});'
            u'try{["wochenkueche_v1","wochenkueche_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'["wochenkueche_profile_v1","wochenkueche_profile_v1__test"].forEach(function(k){localStorage.setItem(k, %s);});'
            u'}catch(e){}</script>' % (json.dumps(json.dumps(STATE)), json.dumps(json.dumps(PROFILE))))
    if seite.count(ANKER) != 1:
        raise SystemExit("charset-Meta nicht genau einmal gefunden.")
    seite = seite.replace(ANKER, ANKER + seed, 1)
    seite = seite.replace("</html>", MESS + "</html>", 1)

    tmp = tempfile.mkdtemp(prefix="wochenlabel-")
    try:
        ziel = os.path.join(tmp, "index.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([
                EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=9000",
                "--user-data-dir=" + os.path.join(tmp, "profil"),
                "--dump-dom", "file:///" + ziel.replace("\\", "/")
            ], stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            raise SystemExit("KEINE MESSUNG - der Pruefstand selbst ist kaputt.")
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


ok = bad = 0
def pruef(name, bed, zusatz=""):
    global ok, bad
    if bed: ok += 1; print(u"  OK      " + name)
    else:   bad += 1; print(u"  FEHLER  " + name + (u"  ->  " + zusatz if zusatz else ""))

print(u"Datei: " + INDEX)
r = lauf()
print(u"")
print(u"Gemessen:")
print(u"  Gewichtskarte (.wch-tip)   " + repr(r.get("tip")))
print(u"  Diagrammpunkt (aria-label) " + repr(r.get("punktLabel")))
print(u"  Home-Hero    (.eyebrow)    " + repr(r.get("planLabel")))
print(u"")

pruef(u"kein JS-Fehler beim Start", r.get("fehler") == "keine", str(r.get("fehler")))
pruef(u"der Fortschritt-Reiter existiert", r.get("reiterDa") is True)
if r.get("messfehler"): pruef(u"Messung lief durch", False, r["messfehler"])

tip = r.get("tip") or ""
punkt = r.get("punktLabel") or ""
plan = r.get("planLabel") or ""

# Das ist die Frage, um die es geht.
pruef(u"die Gewichtskarte zeigt kein NaN", "NaN" not in tip, tip)
pruef(u"der Diagrammpunkt zeigt kein NaN", "NaN" not in punkt, punkt)
# Und die richtige Form: der Wochenschluessel-Aufrufer muss "KW 33 - 10.08." liefern,
# nicht die Wochenplan-Form "Woche 29 - 13.-19. Juli".
pruef(u"die Gewichtskarte nutzt die KW-Form", tip.startswith(u"KW "), tip)
pruef(u"der Diagrammpunkt nutzt die KW-Form", punkt.startswith(u"KW "), punkt)
# Die Gegenprobe: der ZAHL-Aufrufer muss unveraendert seine eigene Form behalten.
pruef(u"die Hero-Zeile nutzt weiter die Woche-Form", plan.startswith(u"Woche "), plan)
pruef(u"und zeigt dort kein NaN", "NaN" not in plan, plan)

print(u"")
print((u"FEHLGESCHLAGEN: %d von %d" % (bad, ok + bad)) if bad else (u"Alle %d Pruefungen gruen." % ok))
sys.exit(1 if bad else 0)
