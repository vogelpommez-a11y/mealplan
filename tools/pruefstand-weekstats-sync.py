# -*- coding: utf-8 -*-
u"""
Verschmelzung des Wochenarchivs: `mergeWeekStats()`.

Warum das geprueft werden muss: `CloudSync.save` schreibt mit `mergeFields` und ersetzt ein
Feld damit GANZ. Seit `weekStats` mitsynchronisiert wird, archivieren beide Geraete dieselbe
Vergangenheit unabhaengig voneinander (`pruneWeeks()` laeuft bei jedem Laden). Ohne
Vereinigung loeschte das zuletzt schreibende Geraet die Wochen des anderen - dieselbe
Fehlerklasse wie TROUBLESHOOTING 34/44.

Die eigentliche Messgroesse ist NICHT "kommt eine Woche an", sondern:

    mergeWeekStats(A, B) === mergeWeekStats(B, A)

Nur wenn beide Geraete unabhaengig zum selben Ergebnis kommen, gibt es nichts zu tauschen.
Ein Tiebreak "remote gewinnt" erfuellt das nicht: A naehme den Wert von B und B gleichzeitig
den von A. Genau das prueft die Gegenprobe am Ende - sie baut die naive Fassung nach und
verlangt, dass sie ROT wird. Ein Pruefstand, den auch die kaputte Fassung besteht, misst
nichts (siehe docs/TESTING.md).

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-weekstats-sync.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende):
    u"""Von der Zeile mit `start` bis einschliesslich der naechsten mit `ende`."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1])


TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
// `kcal` bleibt als Argument stehen, obwohl das Feld am 04.09.2026 aus dem Archiv
// entfallen ist: Die Faelle bilden damit weiter Bestandsdaten aus der Zeit der fuenf
// Kennzahlen nach - sanitizeWeekStats() wirft es beim Laden weg, und genau das soll
// geprueft sein.
function w(days, hit, kcal, target, d) {
  var o = { kcal: kcal, days: days, hit: hit };
  if (target) o.target = target;
  if (d) o.d = d;
  return o;
}

console.log("--- 1. Vereinigung: keine Woche geht verloren ---");
var A = { "2026-W20": w(6,4,2100,2200), "2026-W21": w(5,3,2050,2200) };
var B = { "2026-W22": w(7,5,2150,2200) };
var m = mergeWeekStats(B, A);
pr("alle drei Wochen da", Object.keys(m).length === 3, JSON.stringify(Object.keys(m)));
// Geprueft wird `hit`, nicht mehr `kcal`: Das Feld ist am 04.09.2026 aus dem Archiv
// entfallen (vier Kennzahlen statt fuenf). sanitizeWeekStats() wirft es beim Laden weg.
pr("A-Woche unveraendert", m["2026-W20"].hit === 4, JSON.stringify(m["2026-W20"]));
pr("und kcal ist dabei entfallen", !("kcal" in m["2026-W20"]), JSON.stringify(m["2026-W20"]));
pr("B-Woche uebernommen", m["2026-W22"].days === 7);

console.log("--- 2. Gegenprobe zum Aufbau: blosses Ersetzen verliert etwas ---");
pr("Ersetzen laesst nur 1 Woche uebrig", Object.keys(sanitizeWeekStats(B)).length === 1,
   "sonst misst Test 1 nichts");

console.log("--- 3. Tiebreak: mehr geplante Tage gewinnt ---");
var duenn = { "2026-W20": w(3,1,1900) };
var dick  = { "2026-W20": w(6,4,2100,2200) };
pr("dick gewinnt als sec", mergeWeekStats(duenn, dick)["2026-W20"].days === 6);
pr("dick gewinnt als prim", mergeWeekStats(dick, duenn)["2026-W20"].days === 6);

console.log("--- 4. Determinismus - die eigentliche Messgroesse ---");
var faelle = [
  [{ "2026-W20": w(5,3,2000,2200) }, { "2026-W20": w(5,3,2000,2200) }],
  [{ "2026-W20": w(5,3,2000,2200) }, { "2026-W20": w(5,2,2000,2200) }],
  // Frueher unterschied sich dieser Fall NUR in `kcal`. Seit das Feld weg ist, waeren
  // beide Staende identisch - die Gegenprobe unten haette die naive Fassung dann nur
  // noch in zwei von drei Faellen entlarvt, also stiller gemessen als vorher. Jetzt
  // trennt sie die TAGESMASKE: gleiche Zahlen, andere Tage.
  [{ "2026-W20": w(5,3,2000,2200,"1111100") }, { "2026-W20": w(5,3,2000,2200,"0011111") }],
  [{ "2026-W20": w(5,3,2000,2200) }, { "2026-W20": w(5,3,2000,1800) }],
  [{ "2026-W20": w(4,2,1900) },      { "2026-W21": w(6,5,2300,2200) }]
];
faelle.forEach(function (f, i) {
  var ab = canonJSON(mergeWeekStats(f[0], f[1]));
  var ba = canonJSON(mergeWeekStats(f[1], f[0]));
  pr("Fall " + (i + 1) + ": merge(A,B) === merge(B,A)", ab === ba, ab + " vs " + ba);
});

console.log("--- 5. Konvergenz ueber zwei Runden (kein Ping-Pong) ---");
var gA = { "2026-W20": w(5,3,2000,2200), "2026-W21": w(6,4,2100,2200) };
var gB = { "2026-W20": w(5,2,2000,2200), "2026-W22": w(7,5,2150,2200) };
var a1 = mergeWeekStats(gB, gA), b1 = mergeWeekStats(gA, gB);
pr("nach Runde 1 identisch", canonJSON(a1) === canonJSON(b1));
var a2 = mergeWeekStats(b1, a1), b2 = mergeWeekStats(a1, b1);
pr("Runde 2 aendert bei A nichts", canonJSON(a2) === canonJSON(a1));
pr("Runde 2 aendert bei B nichts", canonJSON(b2) === canonJSON(b1));

// Das Fenster war bis zum 29.08.2026 ein rollendes halbes Jahr (die letzten 26 Wochen).
// Seit Paket 6/B3 sind es ganze Kalenderjahre, getrimmt nach dem Jahres-PRAEFIX des
// Schluessels - der Fortschritt-Kalender zeigt ganze Jahre, und ein rollendes Fenster haette
// ihm den Januar weggeschnitten, sobald der Juli da ist. Behalten werden DREI Jahrgaenge,
// angeboten werden zwei; der dritte ist der Puffer gegen den Jahreswechsel.
// Deshalb rechnet dieser Abschnitt mit dem echten laufenden Jahr, nicht mit "2026".
console.log("--- 6. Archivfenster haelt auch nach der Vereinigung ---");
var J6 = new Date().getFullYear();
function viele(jahr, start, n) {
  var o = {};
  for (var i = 0; i < n; i++) {
    o[jahr + "-W" + String(start + i).padStart(2, "0")] = w(5,3,2000,2200);
  }
  return o;
}
function zaehle6(o, jahr) {
  return Object.keys(o).filter(function (k) { return k.indexOf(jahr + "-W") === 0; }).length;
}
// Zwei Geraete, die je ein halbes Jahr kennen: zusammen ist das ein volles Jahr, und
// nichts davon darf die Vereinigung kosten.
var gross = mergeWeekStats(viele(J6, 27, 26), viele(J6, 1, 26));
pr("Vereinigung schneidet das laufende Jahr nicht ab", zaehle6(gross, J6) === 52,
   zaehle6(gross, J6) + " von 52");
// Ein Geraet, das lange nicht geladen hat, bringt seinen Altbestand mit. Das Pufferjahr
// ueberlebt die Vereinigung, ein vierter Jahrgang nicht.
pr("voriges Jahr bleibt", zaehle6(mergeWeekStats(viele(J6 - 1, 1, 10), viele(J6, 1, 10)), J6 - 1) === 10);
pr("Pufferjahr bleibt", zaehle6(mergeWeekStats(viele(J6 - 2, 1, 10), viele(J6, 1, 10)), J6 - 2) === 10);
var zuAlt = mergeWeekStats(viele(J6 - 3, 1, 10), viele(J6, 1, 10));
pr("das vierte Jahr faellt weg", zaehle6(zuAlt, J6 - 3) === 0, zaehle6(zuAlt, J6 - 3) + " uebrig");

console.log("--- 7. Erstsync und Randfaelle ---");
pr("Cloud kennt das Feld nicht -> lokal bleibt",
   canonJSON(mergeWeekStats(undefined, A)) === canonJSON(sanitizeWeekStats(A)));
pr("lokal leer -> Cloud kommt an", Object.keys(mergeWeekStats(A, undefined)).length === 2);
pr("beide leer", Object.keys(mergeWeekStats(undefined, undefined)).length === 0);
pr("Muell fliegt raus",
   Object.keys(mergeWeekStats({ "kaputt": w(5,3,2000), "2026-W99x": w(5,3,2000) }, {})).length === 0);
pr("Woche ohne days faellt weg",
   Object.keys(mergeWeekStats({ "2026-W20": w(0,0,2000) }, {})).length === 0);

console.log("--- 8. Keine Mutation der Eingaben ---");
var orig = { "2026-W20": w(5,3,2000,2200) }, kopie = JSON.parse(JSON.stringify(orig));
mergeWeekStats({ "2026-W20": w(7,5,2400,2200) }, orig);
pr("sec bleibt unangetastet", JSON.stringify(orig) === JSON.stringify(kopie));

console.log("--- 9. GEGENPROBE: die naive Fassung muss durchfallen ---");
// "Remote gewinnt bei Gleichstand" - genau das, was der Kommentar im Code ausschliesst.
function mergeNaiv(prim, sec) {
  var a = sanitizeWeekStats(sec), b = sanitizeWeekStats(prim);
  var out = Object.assign({}, a);
  Object.keys(b).forEach(function (k) {
    var alt = out[k];
    if (!alt || (b[k].days || 0) >= (alt.days || 0)) out[k] = b[k];
  });
  return sanitizeWeekStats(out);
}
var echtUneinig = 0, naivUneinig = 0;
faelle.slice(1, 4).forEach(function (f) {
  if (canonJSON(mergeWeekStats(f[0], f[1])) !== canonJSON(mergeWeekStats(f[1], f[0]))) echtUneinig++;
  if (canonJSON(mergeNaiv(f[0], f[1])) !== canonJSON(mergeNaiv(f[1], f[0]))) naivUneinig++;
});
pr("echte Fassung in allen 3 Faellen einig", echtUneinig === 0, echtUneinig + " uneinig");
pr("naive Fassung faellt durch (Test misst etwas)", naivUneinig === 3, naivUneinig + " von 3");

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def main():
    quelle = pm_quelle.lade_seite(INDEX).split(u"\n")
    # Produktionscode schneiden, nicht abtippen.
    kern = schneide(quelle, u"function archivJahre(", u"    return sanitizeWeekStats(out);") + u"\n  }\n"
    canon = schneide(quelle, u"function canonValue(v)", u"function canonJSON(v)")
    # maskDays() gehoert seit dem 04.09.2026 dazu: Die Faelle unterscheiden sich jetzt
    # in der TAGESMASKE (vorher in `kcal`, das es nicht mehr gibt), und mergeWeekStats()
    # ruft den Helfer beim Vereinigen der Masken. Ausgeschnitten statt gestubbt.
    maske = schneide(quelle, u"function maskDays(m)", u"// Kennzahlen einer abgelaufenen Woche")

    tmp = tempfile.mkdtemp(prefix="mp-weekstats-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + kern + u"\n" + canon + u"\n" + maske + u"\n" + TEST + u"\n</script>")
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
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        return 0 if letzte and letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
