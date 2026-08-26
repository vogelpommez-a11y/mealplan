# -*- coding: utf-8 -*-
u"""
Tagesmaske des Wochenarchivs: `archiveWeek()`, `sanitizeWeekStats()`, `mergeWeekStats()`.

Dieser Pruefstand wird VOR dem Umbau angelegt (Paket 6, Schritt B1) und ist gegen den
heutigen Stand ABSICHTLICH ROT. Ein Pruefstand, den die alte Fassung schon besteht, misst
nichts (docs/TESTING.md) - deshalb ist "Ohne Ziel wird nicht archiviert" hier die
Eingangsprobe: Wird sie gruen, ohne dass B2 gebaut wurde, laedt der Pruefstand nicht die
echte Funktion.

Zwei Gruppen, getrennt gezaehlt:

  OFFEN       - beschreibt den Sollzustand nach B2-B5. Heute rot, das ist der Sinn.
  REGRESSION  - beschreibt, was HEUTE schon gilt und beim Umbau nicht kaputtgehen darf.
                Eine rote Zeile hier ist immer ein echter Schaden. Nur sie bestimmt den
                Rueckgabewert.

## Zwei Entscheidungen, die dieser Pruefstand festschreibt

**1. `days` beim OR-Merge.** Der Plan sagt an einer Stelle "days auf Math.max ziehen" und an
anderer "days = Anzahl der Einsen". Beides zusammen geht nur so:

    days = max(alter days, neuer days, Anzahl Einsen der vereinigten Maske)

Damit ist `days` nie kleiner als die Maske hergibt und nie kleiner als ein frueher gemessener
Wert. Fuer die Altwochen ohne `d` (der Normalfall) bleibt schlicht das Maximum wirksam. Der
moegliche Widerspruch bleibt bewusst stehen: `days` gilt fuer den Rueckblick, `d` fuer den
Kalender - so steht es im Plan.

**2. `kcal`/`hit`/`target` beim OR-Merge.** Der aermere Lauf gewinnt nicht. Nur wenn der neue
Lauf mindestens so viele Tage gesehen hat wie der gespeicherte, ersetzt er die Zahlen -
derselbe wertbasierte Gedanke wie im Tiebreak von `mergeWeekStats()`.

## Eine Falle beim Lesen der heutigen Ausgabe

Ein Teil der OFFEN-Zeilen ist schon jetzt GRUEN, und zwar aus dem falschen Grund: Solange
`sanitizeWeekStats()` das Feld `d` gar nicht kennt, wirft es jedes `d` weg - kaputtes wie
gueltiges. "Kaputtes d: Feld faellt weg" (Abschnitt 5) und der ganze Determinismus in
Abschnitt 8 sind deshalb heute gruen, ohne etwas zu beweisen. Sie messen erst ab B3/B5.

Die Gegenprobe dazu steht jeweils daneben - "gueltiges d ueberlebt" und "Masken vereinigt"
sind rot. Wer nach B3 nur auf die Zaehler schaut, verpasst das; die Paare gehoeren zusammen
gelesen.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-wochenmaske.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, inklusive=True, pflicht=True):
    u"""Von der Zeile mit `start` bis zur naechsten mit `ende`.

    `inklusive=False` schneidet bis zur Zeile DAVOR - noetig, wenn der Endmarker bereits
    die naechste Funktion ist. `pflicht=False` liefert None statt abzubrechen; so kann ein
    Helfer geprueft werden, den es heute noch gar nicht gibt.
    """
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        if not pflicht:
            return None
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1] if inklusive else zeilen[a:b])


def schneide_zeile(zeilen, marker):
    u"""Einzeiler wie `hasNut()` - `schneide()` sucht das Ende immer HINTER dem Anfang."""
    z = next((l for l in zeilen if marker in l), None)
    if z is None:
        raise SystemExit(u"Marker nicht gefunden: " + marker)
    return z


# Gestubbt wird nur, was archiveWeek von aussen braucht: der State, die Naehrwerte eines
# Tages und das Tagesziel. Die Kette dahinter (MEALS, getRecipe, recipeNut, syncUid, der
# ganze Trainingsplan) traegt zur Frage "welche Tage stehen in der Maske" nichts bei.
STUBS = u"""
var ZIEL = 2200;
var state = { goal: null, weekStats: null, plans: {} };
function weekKeyFor(w) { return w === "next" ? "2026-W36" : "2026-W35"; }
function planAus(maske, kcal) {
  var pl = {};
  DAYS.forEach(function (d, i) {
    pl[d.key] = { kcal: maske.charAt(i) === "1" ? (kcal || 2000) : 0 };
  });
  return pl;
}
function dayNutOf(plan, dayKey) {
  var k = (plan[dayKey] && plan[dayKey].kcal) || 0;
  return { kcal: k, carbs: 0, protein: 0, fat: 0 };
}
function goalTargetsForDay(dayKey) { return state.goal ? { kcal: ZIEL } : null; }
"""

TEST = u"""
var offenOk = 0, offenBad = 0, regrOk = 0, regrBad = 0;
function pr(gruppe, name, bedingung, extra) {
  var tag = gruppe === "regr" ? "REGR " : "OFFEN";
  if (bedingung) {
    if (gruppe === "regr") regrOk++; else offenOk++;
    console.log("  OK   [" + tag + "] " + name);
  } else {
    if (gruppe === "regr") regrBad++; else offenBad++;
    console.log("  FAIL [" + tag + "] " + name + (extra ? "  -> " + extra : ""));
  }
}
function rec(wk) { return (state.weekStats || {})[wk]; }
function frisch(goal) { state.goal = goal ? { kcal: ZIEL } : null; state.weekStats = null; }
function einsen(s) { return (String(s || "").match(/1/g) || []).length; }
function w(days, hit, kcal, target, d) {
  var o = { kcal: kcal, days: days, hit: hit };
  if (target) o.target = target;
  if (d) o.d = d;
  return o;
}

console.log("--- 1. EINGANGSPROBE: ohne Ziel wird trotzdem archiviert (Blocker a) ---");
// Muss heute ROT sein. Wird sie ohne B2 gruen, laedt dieser Pruefstand nicht die echte
// archiveWeek() - dann misst alles Folgende nichts.
frisch(false);
archiveWeek("2026-W20", planAus("1101100"));
var r1 = rec("2026-W20");
pr("offen", "ohne Ziel entsteht ein Datensatz", !!r1, "state.weekStats = " + JSON.stringify(state.weekStats));
pr("offen", "days wird gezaehlt", r1 && r1.days === 4, r1 && r1.days);
pr("offen", "kcal wird gerechnet", r1 && r1.kcal === 2000, r1 && r1.kcal);
pr("offen", "ohne Ziel kein target", !r1 || !("target" in r1), r1 && r1.target);
pr("offen", "ohne Ziel keine Treffer", !r1 || r1.hit === 0, r1 && r1.hit);

console.log("--- 2. Die Maske selbst ---");
frisch(true);
archiveWeek("2026-W20", planAus("1101100"));
var r2 = rec("2026-W20");
pr("offen", "d ist die Maske, Position ueber den DAYS-Index", r2 && r2.d === "1101100", r2 && r2.d);
pr("offen", "days = Anzahl der Einsen", r2 && r2.days === einsen(r2.d), r2 && r2.days + " vs " + einsen(r2 && r2.d));
frisch(true);
archiveWeek("2026-W21", planAus("0000001"));
pr("offen", "nur Sonntag -> letztes Zeichen", rec("2026-W21") && rec("2026-W21").d === "0000001", rec("2026-W21") && rec("2026-W21").d);
frisch(true);
archiveWeek("2026-W22", planAus("1111111"));
pr("offen", "volle Woche", rec("2026-W22") && rec("2026-W22").d === "1111111", rec("2026-W22") && rec("2026-W22").d);
frisch(true);
archiveWeek("2026-W23", planAus("0000000"));
pr("regr", "leere Woche wird gar nicht archiviert", !rec("2026-W23"), JSON.stringify(state.weekStats));

console.log("--- 3. OR-Merge in archiveWeek (Punkt 4 aus Blocker c) ---");
// Das ist auch OHNE Maske schon ein Fehler: pruneWeeks() laeuft aus Remote-Pfaden, und
// state.weekStats[wk] = rec ueberschreibt bedingungslos.
frisch(true);
state.weekStats = { "2026-W20": w(6, 4, 2100, 2200) };
archiveWeek("2026-W20", planAus("1000000"));    // Geraet war offline, sieht nur einen Tag
var r3 = rec("2026-W20");
pr("offen", "aermerer Lauf zerstoert days nicht", r3 && r3.days === 6, r3 && r3.days);
pr("offen", "aermerer Lauf zerstoert kcal nicht", r3 && r3.kcal === 2100, r3 && r3.kcal);
pr("offen", "aermerer Lauf zerstoert hit nicht", r3 && r3.hit === 4, r3 && r3.hit);
pr("offen", "Maske entsteht trotzdem", r3 && r3.d === "1000000", r3 && r3.d);

frisch(true);
state.weekStats = { "2026-W20": w(3, 2, 2000, 2200, "1010100") };
archiveWeek("2026-W20", planAus("0101000"));
var r4 = rec("2026-W20");
pr("offen", "Masken werden VEREINIGT", r4 && r4.d === "1111100", r4 && r4.d);
pr("offen", "days folgt der vereinigten Maske", r4 && r4.days === 5, r4 && r4.days);

frisch(true);
state.weekStats = { "2026-W20": w(2, 1, 1800, 2200, "1100000") };
archiveWeek("2026-W20", planAus("1111100"));
var r5 = rec("2026-W20");
pr("offen", "reicherer Lauf ersetzt die Zahlen", r5 && r5.days === 5 && r5.kcal === 2000, r5 && JSON.stringify(r5));

console.log("--- 4. weekMaskOf() als gemeinsame Quelle ---");
pr("offen", "weekMaskOf existiert", typeof weekMaskOf === "function", typeof weekMaskOf);
if (typeof weekMaskOf === "function") {
  pr("offen", "weekMaskOf liefert die Maske", weekMaskOf(planAus("1101100")) === "1101100", weekMaskOf(planAus("1101100")));
  pr("offen", "leerer Plan -> lauter Nullen", weekMaskOf(planAus("0000000")) === "0000000");
  frisch(true);
  archiveWeek("2026-W24", planAus("0110010"));
  pr("offen", "archiveWeek benutzt denselben Helfer",
     rec("2026-W24") && rec("2026-W24").d === weekMaskOf(planAus("0110010")));
} else {
  pr("offen", "weekMaskOf liefert die Maske", false, "Helfer fehlt");
  pr("offen", "leerer Plan -> lauter Nullen", false, "Helfer fehlt");
  pr("offen", "archiveWeek benutzt denselben Helfer", false, "Helfer fehlt");
}

console.log("--- 5. sanitizeWeekStats: d validieren ---");
// Kaputtes d darf den DATENSATZ nicht kosten - nur das Feld. Sonst wird aus einem
// Uebertragungsfehler eine geloeschte Woche.
function san1(d) { return sanitizeWeekStats({ "2026-W20": w(5, 3, 2000, 2200, d) })["2026-W20"]; }
pr("offen", "gueltiges d ueberlebt", san1("1101100") && san1("1101100").d === "1101100", JSON.stringify(san1("1101100")));
[["abc", "Buchstaben"], ["11011000", "8 Zeichen"], ["110110", "6 Zeichen"], ["1201100", "fremde Ziffer"]].forEach(function (f) {
  var s = san1(f[0]);
  pr("offen", "kaputtes d (" + f[1] + "): Datensatz ueberlebt", !!s && s.days === 5, JSON.stringify(s));
  pr("offen", "kaputtes d (" + f[1] + "): Feld faellt weg", !s || !("d" in s), s && s.d);
});
var sz = sanitizeWeekStats({ "2026-W20": { kcal: 2000, days: 5, hit: 3, d: 1101100 } })["2026-W20"];
pr("offen", "Zahl statt String: Feld faellt weg", sz && !("d" in sz), sz && sz.d);
pr("offen", "d ohne days rettet die Woche nicht",
   Object.keys(sanitizeWeekStats({ "2026-W20": w(0, 0, 2000, 0, "1101100") })).length === 0);

console.log("--- 6. Archivfenster: laufendes plus voriges Kalenderjahr ---");
var J = new Date().getFullYear();
function jahr(y, n, ab) {
  var o = {};
  for (var i = 0; i < n; i++) o[y + "-W" + String((ab || 1) + i).padStart(2, "0")] = w(5, 3, 2000, 2200);
  return o;
}
var gross = Object.assign({}, jahr(J - 2, 10), jahr(J - 1, 40), jahr(J, 40));
var getrimmt = sanitizeWeekStats(gross);
function zaehle(y) { return Object.keys(getrimmt).filter(function (k) { return k.indexOf(y + "-W") === 0; }).length; }
pr("offen", "laufendes Jahr bleibt vollstaendig", zaehle(J) === 40, zaehle(J) + " von 40");
pr("offen", "voriges Jahr bleibt vollstaendig", zaehle(J - 1) === 40, zaehle(J - 1) + " von 40");
pr("regr", "das Jahr davor faellt weg", zaehle(J - 2) === 0, zaehle(J - 2) + " uebrig");

console.log("--- 7. mergeWeekStats: Masken vereinigen, nicht 'mehr days gewinnt' ---");
var mA = { "2026-W20": w(4, 3, 2000, 2200, "1111000") };
var mB = { "2026-W20": w(3, 2, 1900, 2200, "0000111") };
var mm = mergeWeekStats(mB, mA)["2026-W20"];
pr("offen", "Masken vereinigt", mm && mm.d === "1111111", mm && mm.d);
pr("offen", "Zahlen folgen dem Tiebreak (mehr days)", mm && mm.kcal === 2000 && mm.hit === 3, JSON.stringify(mm));
var mm2 = mergeWeekStats(mA, mB)["2026-W20"];
pr("offen", "Richtung egal: Maske", mm2 && mm2.d === "1111111", mm2 && mm2.d);
pr("offen", "Richtung egal: Zahlen", mm2 && canonJSON(mm2) === canonJSON(mm), canonJSON(mm2) + " vs " + canonJSON(mm));

var ohne = { "2026-W20": w(6, 4, 2100, 2200) };
var mit = { "2026-W20": w(3, 2, 1900, 2200, "1010100") };
var mm3 = mergeWeekStats(ohne, mit)["2026-W20"], mm4 = mergeWeekStats(mit, ohne)["2026-W20"];
pr("offen", "Seite ohne d loescht die Maske nicht", mm3 && mm3.d === "1010100", mm3 && mm3.d);
pr("offen", "auch andersherum", mm4 && mm4.d === "1010100", mm4 && mm4.d);
pr("offen", "Zahlen kommen dabei von der reicheren Seite", mm3 && mm3.days === 6, mm3 && mm3.days);

console.log("--- 8. Determinismus mit d (die eigentliche Messgroesse) ---");
var faelle = [
  [{ "2026-W20": w(5,3,2000,2200,"1111100") }, { "2026-W20": w(5,3,2000,2200,"0011111") }],
  [{ "2026-W20": w(5,3,2000,2200,"1111100") }, { "2026-W20": w(5,2,2000,2200,"1111100") }],
  [{ "2026-W20": w(5,3,2000,2200,"1111100") }, { "2026-W20": w(5,3,2400,2200,"1000000") }],
  [{ "2026-W20": w(4,2,1900) },                { "2026-W20": w(4,2,1900,0,"1111000") }],
  [{ "2026-W20": w(4,2,1900,2200,"1100000") }, { "2026-W21": w(6,5,2300,2200,"1111110") }]
];
faelle.forEach(function (f, i) {
  var ab = canonJSON(mergeWeekStats(f[0], f[1])), ba = canonJSON(mergeWeekStats(f[1], f[0]));
  pr("offen", "Fall " + (i + 1) + ": merge(A,B) === merge(B,A)", ab === ba, ab + " vs " + ba);
});
var kA = { "2026-W20": w(5,3,2000,2200,"1110000"), "2026-W21": w(6,4,2100,2200,"1111110") };
var kB = { "2026-W20": w(5,2,2000,2200,"0000111"), "2026-W22": w(7,5,2150,2200,"1111111") };
var a1 = mergeWeekStats(kB, kA), b1 = mergeWeekStats(kA, kB);
pr("offen", "nach Runde 1 identisch", canonJSON(a1) === canonJSON(b1));
pr("offen", "Runde 2 aendert nichts (kein Ping-Pong)",
   canonJSON(mergeWeekStats(b1, a1)) === canonJSON(a1) && canonJSON(mergeWeekStats(a1, b1)) === canonJSON(b1));

console.log("--- 9. REGRESSION: was heute schon gilt ---");
pr("regr", "Muell-Schluessel fliegen raus",
   Object.keys(sanitizeWeekStats({ "kaputt": w(5,3,2000), "2026-W99x": w(5,3,2000) })).length === 0);
pr("regr", "Woche ohne days faellt weg",
   Object.keys(sanitizeWeekStats({ "2026-W20": w(0,0,2000) })).length === 0);
pr("regr", "hit wird auf days geklemmt", sanitizeWeekStats({ "2026-W20": w(3,9,2000) })["2026-W20"].hit === 3);
pr("regr", "days wird auf 7 geklemmt", sanitizeWeekStats({ "2026-W20": w(99,3,2000) })["2026-W20"].days === 7);
pr("regr", "unplausibles target faellt weg", !("target" in sanitizeWeekStats({ "2026-W20": w(5,3,2000,42) })["2026-W20"]));
pr("regr", "plausibles target bleibt", sanitizeWeekStats({ "2026-W20": w(5,3,2000,2200) })["2026-W20"].target === 2200);
pr("regr", "Erstsync: Cloud kennt das Feld nicht",
   canonJSON(mergeWeekStats(undefined, kA)) === canonJSON(sanitizeWeekStats(kA)));
pr("regr", "beide leer", Object.keys(mergeWeekStats(undefined, undefined)).length === 0);
var orig = { "2026-W20": w(5,3,2000,2200,"1111100") }, kopie = JSON.stringify(orig);
mergeWeekStats({ "2026-W20": w(7,5,2400,2200,"1111111") }, orig);
pr("regr", "merge mutiert die Eingaben nicht", JSON.stringify(orig) === kopie);
frisch(true);
archiveWeek("2026-W20", null);
pr("regr", "kein Plan -> kein Datensatz", !rec("2026-W20"));
frisch(true);
state.plans = { "2026-W10": planAus("1100000"), "2026-W35": planAus("1111100"), "2026-W36": planAus("1000000") };
pruneWeeks(state.plans);
pr("regr", "pruneWeeks behaelt genau zwei Wochen", Object.keys(state.plans).length === 2, Object.keys(state.plans).join(","));
pr("offen", "pruneWeeks archiviert die alte Woche auch ohne Ziel-Guard", !!rec("2026-W10"), JSON.stringify(state.weekStats));

console.log("");
console.log("OFFEN " + offenOk + " gruen, " + offenBad + " rot   (bis B2-B5 ist rot der Sollzustand)");
console.log("ERGEBNIS REGRESSION " + regrOk + " gruen, " + regrBad + " rot");
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")
    # Produktionscode schneiden, nicht abtippen.
    tage = schneide(quelle, u"const DAYS = [", u"  ];")
    hasnut = schneide_zeile(quelle, u"function hasNut(s)")
    prune = schneide(quelle, u"function pruneWeeks(plans)", u"  // Verwaiste Barcode-Produkte", inklusive=False)
    arch = schneide(quelle, u"function archiveWeek(wk, pl)", u"function sanitizeWeekStats(o)", inklusive=False)
    san = schneide(quelle, u"function sanitizeWeekStats(o)", u"    return sanitizeWeekStats(out);") + u"\n  }\n"
    canon = schneide(quelle, u"function canonValue(v)", u"function canonJSON(v)")
    # Gibt es heute noch nicht - Test 4 wird dann rot, statt den Lauf abzubrechen.
    maske = schneide(quelle, u"function weekMaskOf(", u"function maskDays(", pflicht=False) or u""

    tmp = tempfile.mkdtemp(prefix="mp-wochenmaske-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + tage + u"\n" + hasnut + u"\n" + STUBS + u"\n" + maske + u"\n"
            + prune + u"\n" + arch + u"\n" + san + u"\n" + canon + u"\n" + TEST + u"\n</script>")
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000",
             "--user-data-dir=" + os.path.join(tmp, "profil"),
             "--enable-logging=stderr", "--v=0", "file:///" + seite.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        aus = (p.stdout or "") + (p.stderr or "")
        zeilen = []
        for z in aus.split("\n"):
            m = re.search(r'CONSOLE:\d+\] "(.*)", source', z)
            if m:
                zeilen.append(m.group(1))
        if not zeilen:
            print(u"Keine Konsolenausgabe - lief das Script? Rohausgabe:")
            print(aus[:2000])
            return 2
        for z in zeilen:
            print(z)
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS REGRESSION")]
        return 0 if letzte and letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
