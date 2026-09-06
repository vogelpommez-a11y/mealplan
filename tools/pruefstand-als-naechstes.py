# -*- coding: utf-8 -*-
u"""Was zeigt der Bilddeckel des Startreiters wann?

nextMealOfDay() entscheidet, welche Mahlzeit auf Home im Bilddeckel steht. Die Funktion
haengt an der Uhrzeit, und genau deshalb faellt ein Fehler darin beim Bauen nicht auf: Wer
sie um 14 Uhr anschaut, sieht nie, was sie um 21 Uhr tut.

Bis zum 06.09.2026 suchte sie ab der Uhrzeit vorwaerts und danach WIEDER VON VORNE. In der
Praxis hiess das: Ab dem Nachmittag zeigte die Karte Vergangenes - bei "nur Fruehstueck
geplant" ab 11 Uhr den ganzen Tag das Fruehstueck von heute Morgen. Eine Karte mit der
Ueberschrift "Als Naechstes" darf nicht rueckwaerts zeigen.

Geprueft wird die ganze Matrix Uhrzeit x Planzustand gegen eine Sollwert-Tabelle. Die
Uhrzeit wird ueber einen Date-Ersatz gesetzt.

Aufruf:
    python tools/pruefstand-als-naechstes.py
    python tools/pruefstand-als-naechstes.py --gegenprobe   # der Stand davor MUSS durchfallen
"""
import io, json, os, re, subprocess, shutil, sys, tempfile

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Fester Hash, ausdruecklich NICHT "HEAD" - der Stand vor dem Umbau vom 06.09.2026.
#
# Hier stand zuerst "HEAD", und das haette genau bis zum naechsten Commit gehalten: Danach
# zeigt HEAD auf den bereits reparierten Code, die Gegenprobe vergleicht den neuen Stand mit
# sich selbst und meldet dauerhaft "bestanden", ohne noch etwas zu pruefen.
#
# Der Fehler ist in diesem Projekt schon einmal passiert und stand beim Schreiben dieser
# Zeile bereits in docs/TESTING.md - der Schwesterpruefstand pruefstand-home-eine-seite.py
# hatte ihn tagelang unbemerkt. Ein relativer Verweis auf HEAD ist in einer Gegenprobe immer
# falsch: Sie soll gegen einen BESTIMMTEN Zustand messen, nicht gegen "vorhin".
GEGENPROBE_COMMIT = "9a31f1c"


def schneide(quelltext, name):
    u"""Schneidet function <name>(...) { ... } ueber Klammerzaehlung heraus.

    Das ist der Kern des Verfahrens: Geprueft wird der ECHTE Code aus index.html, nicht
    ein Nachbau. Ein Nachbau prueft nur, ob man denselben Fehler zweimal schreibt.
    """
    start = quelltext.index("  function %s(" % name)
    i = quelltext.index("{", start)
    tiefe, j = 0, i
    while True:
        c = quelltext[j]
        if c == "{":
            tiefe += 1
        elif c == "}":
            tiefe -= 1
            if tiefe == 0:
                break
        j += 1
    return quelltext[start:j + 1]

# fall -> (heute, morgen)
FAELLE = [
    (u"alles geplant",     {"fr":1,"mi":1,"ab":1,"sn":0}, {"fr":1,"mi":1,"ab":1,"sn":0}),
    (u"kein Fruehstueck",  {"fr":0,"mi":1,"ab":1,"sn":0}, {"fr":0,"mi":1,"ab":1,"sn":0}),
    (u"nur Fruehstueck",   {"fr":1,"mi":0,"ab":0,"sn":0}, {"fr":1,"mi":0,"ab":0,"sn":0}),
    (u"nur Mittag",        {"fr":0,"mi":1,"ab":0,"sn":0}, {"fr":0,"mi":1,"ab":0,"sn":0}),
    (u"nur Snacks",        {"fr":0,"mi":0,"ab":0,"sn":1}, {"fr":0,"mi":0,"ab":0,"sn":0}),
    (u"GAR NICHTS heute",  {"fr":0,"mi":0,"ab":0,"sn":0}, {"fr":0,"mi":1,"ab":1,"sn":0}),
    (u"heute+morgen leer", {"fr":0,"mi":0,"ab":0,"sn":0}, {"fr":0,"mi":0,"ab":0,"sn":0}),
]
STUNDEN = [7, 11, 16, 19, 21, 23]

# Soll: "meal|wann|belegt"  -  "-" heisst: keine Mahlzeit nennen (Leerzustand)
SOLL = {
 u"alles geplant":     ["fr|heute|1","mi|heute|1","ab|heute|1","ab|heute|1","fr|morgen|1","fr|morgen|1"],
 u"kein Fruehstueck":  ["mi|heute|1","mi|heute|1","ab|heute|1","ab|heute|1","mi|morgen|1","mi|morgen|1"],
 u"nur Fruehstueck":   ["fr|heute|1","mi|heute|0","ab|heute|0","ab|heute|0","fr|morgen|1","fr|morgen|1"],
 u"nur Mittag":        ["mi|heute|1","mi|heute|1","ab|heute|0","ab|heute|0","mi|morgen|1","mi|morgen|1"],
 # Snacks sind der einzige Eintrag des Tages. Schritt 1 findet sie und zeigt sie - schon
 # um 7 Uhr, obwohl Fruehstueck, Mittag und Abend alle offen stehen. Beim Aufstellen
 # dieser Tabelle stand hier zuerst "Fruehstueck offen", und das war die falsche
 # Erwartung: Schritt 1 zeigt die naechste GEPLANTE Mahlzeit, und eine geplante Mahlzeit
 # zu verschweigen, um einen leeren Slot vorzuschlagen, waere schlechter als die
 # Unschaerfe in der Reihenfolge. Der Snack-Ausschluss gilt nur fuer Schritt 2, also fuer
 # den VORSCHLAG eines leeren Slots.
 u"nur Snacks":        ["sn|heute|1","sn|heute|1","sn|heute|1","sn|heute|1","sn|heute|1","sn|heute|1"],
 u"GAR NICHTS heute":  ["-","-","-","-","mi|morgen|1","mi|morgen|1"],
 u"heute+morgen leer": ["-","-","-","-","-","-"],
}


def lauf(pfad):
    quelle = io.open(pfad, encoding="utf-8").read()
    fn = schneide(quelle, "nextMealOfDay")
    alt = "morgenPlan" not in fn.split("\n")[0]     # der Stand VOR dem Umbau kennt sie nicht
    js = u"""
var MEALS = [{key:"fr",label:"Fr"},{key:"mi",label:"Mi"},{key:"ab",label:"Ab"},{key:"sn",label:"Sn"}];
var getRecipe = function (id) { return id ? {id:id, name:"G"} : null; };
var __H = 12, EchtesDate = Date;
Date = function () { var d = new EchtesDate(); d.setHours(Math.floor(__H), Math.round((__H %% 1)*60), 0, 0); return d; };
Date.now = EchtesDate.now;
%s
var ALT = %s;
var FAELLE = %s, STUNDEN = %s, raus = [];
FAELLE.forEach(function (f) {
  var heute = {}, morgen = {};
  ["fr","mi","ab","sn"].forEach(function (k) { heute[k] = f[1][k] ? [k] : []; morgen[k] = f[2][k] ? [k] : []; });
  var plan = {heute: heute, morgen: morgen};
  STUNDEN.forEach(function (h) {
    __H = h;
    var n = ALT ? nextMealOfDay(plan, "heute") : nextMealOfDay(plan, "heute", plan, "morgen");
    var t;
    if (!n || !n.meal) t = "-";
    else t = n.meal.key.toLowerCase() + "|" + (n.wann || (n.vor ? "heute" : "vergangen")) + "|" + (n.r ? 1 : 0);
    raus.push({fall: f[0], h: h, ist: t});
  });
});
console.log("ERGEBNIS" + JSON.stringify(raus));
""" % (fn, "true" if alt else "false",
       json.dumps([[a,b,c] for a,b,c in FAELLE]), json.dumps(STUNDEN))
    tmp = tempfile.mkdtemp(prefix="pruef-naechstes-")
    try:
        p = os.path.join(tmp, "t.html")
        io.open(p, "w", encoding="utf-8").write(u'<!doctype html><meta charset="utf-8"><script>\n%s\n</script>' % js)
        aus = subprocess.check_output([EDGE,"--headless=new","--disable-gpu","--virtual-time-budget=5000",
            "--user-data-dir="+os.path.join(tmp,"p"),"--enable-logging=stderr","--v=0",
            "file:///"+p.replace("\\","/")], stderr=subprocess.STDOUT).decode("utf-8","replace")
        m = re.search(r"ERGEBNIS(\[.*?\])", aus, re.S)
        if not m: print(aus[-1500:]); raise SystemExit("keine Ausgabe")
        return json.loads(m.group(1))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def bewerte(daten, titel):
    print(u"\n" + titel); print(u"-" * 78)
    ok = bad = 0
    for f, _, _ in FAELLE:
        zeile = u"  %-20s" % f
        schlecht = []
        for i, h in enumerate(STUNDEN):
            ist = [x for x in daten if x["fall"] == f and x["h"] == h][0]["ist"]
            soll = SOLL[f][i]
            if ist == soll: ok += 1; zeile += u"%-15s" % ist
            else:
                bad += 1; schlecht.append(u"%02d:00 ist %s, soll %s" % (h, ist, soll))
                zeile += u"%-15s" % (u"!" + ist)
        print(zeile)
        for x in schlecht: print(u"        -> " + x)
    print(u"\n  %d richtig, %d falsch" % (ok, bad))
    return bad


if __name__ == "__main__":
    if "--gegenprobe" in sys.argv:
        print(u"GEGENPROBE gegen " + GEGENPROBE_COMMIT + u" - dieser Stand MUSS durchfallen.")
        tmp = tempfile.mkdtemp(prefix="naechstes-alt-")
        try:
            inhalt = subprocess.check_output(["git","-C",BASIS,"show",
                                              "%s:index.html" % GEGENPROBE_COMMIT])
            zp = os.path.join(tmp,"index.html"); io.open(zp,"wb").write(inhalt)
            bad = bewerte(lauf(zp), u"Der Stand VOR dem Umbau")
            print(u"\nGegenprobe %s" % (u"bestanden - der alte Stand faellt durch" if bad
                                        else u"FEHLGESCHLAGEN - der alte Stand kommt durch"))
            sys.exit(0 if bad else 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    bad = bewerte(lauf(os.path.join(BASIS,"index.html")), u"Was zeigt der Bilddeckel wann?")
    print(u"\nERGEBNIS %s" % (u"alle Faelle richtig" if not bad else u"%d Abweichungen" % bad))
    sys.exit(1 if bad else 0)
