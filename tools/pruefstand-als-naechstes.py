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

# Der Stand vom 06.09.2026: Umbau fertig, aber nextMealOfDay() rief getRecipe() noch mit dem
# rohen Slot-Eintrag statt mit entryId(). Bei Objekt-Eintraegen {id, uids} - der Form, die
# "Gemeinsam planen" schreibt - loeste kein einziges Meal auf, und die Karte zeigte den
# ganzen Tag "Morgen". Er ist die Gegenprobe fuer die Achse EINTRAGSFORM: Ohne ihn koennte
# man die Objekt-Faelle hier eintragen, ohne je zu pruefen, ob sie ueberhaupt etwas merken.
GEGENPROBE_FORM_COMMIT = "258e072"


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
# Die zweite Achse: In welcher Form steht der Eintrag im Slot? Beide Formen kommen im
# Normalbetrieb vor - "Gemeinsam planen" schreibt {id, uids}, alles andere die blanke ID.
FORMEN = ["str", "obj", "fremd", "ohnekonto"]
FORM_LABEL = {"str": u"ID", "obj": u"{id,uids} - meins", "fremd": u"{id,uids} - fremd",
              "ohnekonto": u"{id,uids} - ohne Konto"}

# Die dritte Achse ist KEINE Variante der zweiten, sie hat eigene Sollwerte: Ein Eintrag,
# der per uids ausdruecklich jemand anderem gehoert, zaehlt fuer diese Karte nicht. Ist der
# Tag ausschliesslich so belegt, ist er FUER MICH leer - und die Karte sagt das mit einem
# eigenen Satz ("-|fremd"), nicht mit dem allgemeinen Leerzustand ("-"): Es IST etwas
# geplant, nur nicht fuer mich. Ohne diese Unterscheidung stuende die Karte im Widerspruch
# zur Kalorienzeile darunter, die denselben Tag laengst mit 0 ausweist (dayNutOf).
# Die vierte Form ist der LOKALE Modus: Eintraege tragen uids, aber es gibt kein Konto
# (syncUid ist leer). Ohne Konto gibt es keine Mitplaner - eine Zuweisung ist dort
# gegenstandslos, also muessen die Sollwerte exakt die der blanken ID sein. Genau das ging
# am 07.09.2026 zuerst schief: `["u1"].indexOf("") === -1` erklaerte jeden Eintrag fuer
# fremd, und der Deckel schlug ein Mittagessen vor, das schon dastand. Der Pruefstand
# konnte es nicht sehen, weil er syncUid fest auf "u1" setzte - dieselbe Sorte blinder
# Fleck wie der zu grosszuegige getRecipe-Stub eine Achse zuvor.
SOLL_FREMD = {
  u"alles geplant":     ["-|fremd"] * 6,
  u"kein Fruehstueck":  ["-|fremd"] * 6,
  u"nur Fruehstueck":   ["-|fremd"] * 6,
  u"nur Mittag":        ["-|fremd"] * 6,
  u"nur Snacks":        ["-|fremd"] * 6,
  # Heute ist WIRKLICH leer - kein fremder Eintrag, ueber den zu reden waere. Ab 20:30
  # schaut die Karte auf morgen, und auch dort gehoert alles jemand anderem.
  u"GAR NICHTS heute":  ["-"] * 6,
  u"heute+morgen leer": ["-"] * 6,
}

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


def lauf(pfad, mutation=None):
    quelle = io.open(pfad, encoding="utf-8").read()
    fn = schneide(quelle, "nextMealOfDay")
    # entryId() und entryUids() werden MIT ausgeschnitten, nicht gestubbt: Ein Stub waere
    # genau die Stelle, an der der Fehler wieder durchrutscht - er wuerde die Objektform
    # brav aufloesen bzw. jede Zuweisung durchwinken, auch wenn der Produktionscode sie gar
    # nicht erst hineinreicht.
    kopf = fn.split(chr(10))[0]
    alt = "morgenPlan" not in kopf                  # der Stand VOR dem Umbau kennt sie nicht
    for helfer in ("entryId", "entryUids"):
        fn = schneide(quelle, helfer) + chr(10) + fn
    if mutation:
        vorher, nachher = mutation
        if vorher not in fn:
            raise SystemExit(u"Mutation greift nicht mehr - Code umgebaut? %s" % vorher)
        fn = fn.replace(vorher, nachher)
    js = u"""
var MEALS = [{key:"fr",label:"Fr"},{key:"mi",label:"Mi"},{key:"ab",label:"Ab"},{key:"sn",label:"Sn"}];
// Nachgebaut wie das echte getRecipe(): Es sucht mit === in einer Liste. Ein Objekt
// {id, uids} findet dort NIE ein Rezept. Der fruehere Stub loeste jede Wahrheit auf und
// hat damit den Fehler vom 07.09.2026 unsichtbar gemacht.
var KATALOG = [{id:"fr",name:"G"},{id:"mi",name:"G"},{id:"ab",name:"G"},{id:"sn",name:"G"}];
var getRecipe = function (id) {
  for (var i = 0; i < KATALOG.length; i++) if (KATALOG[i].id === id) return KATALOG[i];
  return null;
};
// syncUid ist im Produktionscode eine Modulvariable. Hier fest gesetzt, damit "gehoert mir"
// ueberhaupt eine Bedeutung hat - ohne sie waere jeder Eintrag gleich weit weg.
var syncUid = "u1";
var __H = 12, EchtesDate = Date;
Date = function () { var d = new EchtesDate(); d.setHours(Math.floor(__H), Math.round((__H %% 1)*60), 0, 0); return d; };
Date.now = EchtesDate.now;
%s
var ALT = %s;
var FAELLE = %s, STUNDEN = %s, FORMEN = %s, raus = [];
// Ein Slot-Eintrag ist entweder eine ID ODER {id, uids} - beides schreibt die App im
// Normalbetrieb. Die Eintragsform ist deshalb eine eigene Achse und keine Randnotiz:
// Am Ergebnis darf sie NICHTS aendern, die Sollwerte sind fuer beide Formen dieselben.
var ECHTE_UID = syncUid;
var baue = function (form, key) {
  if (form === "str") return key;
  return {id: key, uids: [form === "fremd" ? "u2" : ECHTE_UID]};
};
FORMEN.forEach(function (form) {
  // Der lokale Modus unterscheidet sich NUR hierin - deshalb ist er eine eigene Form
  // und keine eigene Faelle-Tabelle.
  syncUid = (form === "ohnekonto") ? "" : ECHTE_UID;
  FAELLE.forEach(function (f) {
    var heute = {}, morgen = {};
    ["fr","mi","ab","sn"].forEach(function (k) {
      heute[k] = f[1][k] ? [baue(form, k)] : [];
      morgen[k] = f[2][k] ? [baue(form, k)] : [];
    });
    var plan = {heute: heute, morgen: morgen};
    STUNDEN.forEach(function (h) {
      __H = h;
      var n = ALT ? nextMealOfDay(plan, "heute") : nextMealOfDay(plan, "heute", plan, "morgen");
      var t;
      // Der Leerzustand hat zwei Auspraegungen, und sie zu verschmelzen waere genau der
      // Fehler, den diese Achse finden soll: "-" heisst "gar nichts geplant",
      // "-|fremd" heisst "geplant, aber nicht fuer mich".
      if (!n || !n.meal) t = (n && n.wann === "fremd") ? "-|fremd" : "-";
      else t = n.meal.key.toLowerCase() + "|" + (n.wann || (n.vor ? "heute" : "vergangen")) + "|" + (n.r ? 1 : 0);
      raus.push({form: form, fall: f[0], h: h, ist: t});
    });
  });
});
console.log("ERGEBNIS" + JSON.stringify(raus));
""" % (fn, "true" if alt else "false",
       json.dumps([[a, b, c] for a, b, c in FAELLE]), json.dumps(STUNDEN),
       json.dumps(FORMEN))
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
    print(u"\n" + titel)
    print(u"-" * 92)
    ok = bad = 0
    for form in FORMEN:
        print(u"  Eintragsform %s" % FORM_LABEL[form])
        for f, _, _ in FAELLE:
            zeile = u"    %-20s" % f
            schlecht = []
            for i, h in enumerate(STUNDEN):
                treffer = [x for x in daten if x.get("form", "str") == form
                           and x["fall"] == f and x["h"] == h]
                ist = treffer[0]["ist"] if treffer else u"(fehlt)"
                soll = (SOLL_FREMD[f] if form == "fremd" else SOLL[f])[i]
                if ist == soll:
                    ok += 1
                    zeile += u"%-15s" % ist
                else:
                    bad += 1
                    schlecht.append(u"%02d:00 ist %s, soll %s" % (h, ist, soll))
                    zeile += u"%-15s" % (u"!" + ist)
            print(zeile)
            for x in schlecht:
                print(u"          -> " + x)
        print(u"")
    print(u"  %d richtig, %d falsch" % (ok, bad))
    return bad



# Der Filter, der die Achse Zuweisung ueberhaupt erst zu einer Achse macht. Wird er
# entschaerft ("alles gehoert mir"), muessen die fremden Faelle durchfallen.
# Zwei Mutationen, weil der Filter zwei Aussagen trifft. Die erste ("alles gehoert mir")
# laesst die Form "ohne Konto" gruen - dort IST alles meins. Sie kann diese Achse also gar
# nicht pruefen, und ohne die zweite haette man eine Gegenprobe, die genau am neuesten
# Befund vorbeimisst.
MUTATION_FILTER = ("      if (!syncUid) return true;" + chr(10) +
                   "      const u = entryUids(e);" + chr(10) +
                   "      return !u || u.indexOf(syncUid) !== -1;",
                   "      return true;")
MUTATION_OHNE_KONTO = ("      if (!syncUid) return true;" + chr(10), "")


def gegen_mutation(mutation, was):
    u"""Faehrt den AKTUELLEN Code mit gezielt entschaerfter Bedingung. MUSS durchfallen.

    Fuer die Achsen Uhrzeit und Eintragsform gibt es je einen festen alten Commit. Fuer die
    Zuweisung gibt es keinen - Filter und Achse entstehen im selben Commit. Statt dessen wird
    der ECHTE Code zurueckgebaut. Greift die Ersetzung nicht mehr, bricht lauf() ab: eine
    Gegenprobe, die ins Leere ersetzt, wuerde sonst stillschweigend "bestanden" melden.
    """
    bad = bewerte(lauf(os.path.join(BASIS, "index.html"), mutation), was)
    print(u"  -> %s" % (u"faellt durch, wie es sein muss" if bad
                        else u"KOMMT DURCH - diese Achse misst nichts"))
    return bad


def gegen(commit, was):
    u"""Faehrt den Pruefstand gegen einen festen alten Stand. Er MUSS durchfallen."""
    tmp = tempfile.mkdtemp(prefix="naechstes-alt-")
    try:
        inhalt = subprocess.check_output(["git", "-C", BASIS, "show",
                                          "%s:index.html" % commit])
        zp = os.path.join(tmp, "index.html")
        io.open(zp, "wb").write(inhalt)
        bad = bewerte(lauf(zp), u"%s (%s)" % (was, commit))
        print(u"  -> %s" % (u"faellt durch, wie es sein muss" if bad
                            else u"KOMMT DURCH - der Pruefstand misst hier nichts"))
        return bad
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if "--gegenprobe" in sys.argv:
        # ZWEI Gegenproben, eine je Achse. Eine allein genuegt nicht: Der Stand vor dem
        # Umbau faellt schon an der Uhrzeit durch - er wuerde also auch dann "bestanden"
        # melden, wenn die Eintragsform gar nicht geprueft wird.
        print(u"GEGENPROBE - alle vier Staende MUESSEN durchfallen.")
        a1 = gegen(GEGENPROBE_COMMIT, u"Achse Uhrzeit: der Stand VOR dem Umbau")
        a2 = gegen(GEGENPROBE_FORM_COMMIT, u"Achse Eintragsform: getRecipe() ohne entryId()")
        a3 = gegen_mutation(MUTATION_FILTER,
                            u"Achse Zuweisung: derselbe Code, Filter entschaerft")
        a4 = gegen_mutation(MUTATION_OHNE_KONTO,
                            u"Achse ohne Konto: derselbe Code, syncUid-Zweig entfernt")
        gut = bool(a1) and bool(a2) and bool(a3) and bool(a4)
        print(u"\nGegenprobe %s" % (u"bestanden - alle vier fallen durch" if gut
                                    else u"FEHLGESCHLAGEN - mindestens ein Stand kommt durch"))
        sys.exit(0 if gut else 1)
    bad = bewerte(lauf(os.path.join(BASIS, "index.html")), u"Was zeigt der Bilddeckel wann?")
    print(u"\nERGEBNIS %s" % (u"alle Faelle richtig" if not bad else u"%d Abweichungen" % bad))
    sys.exit(1 if bad else 0)
