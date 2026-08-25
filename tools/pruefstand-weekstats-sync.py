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
function w(days, hit, kcal, target) {
  var o = { kcal: kcal, days: days, hit: hit };
  if (target) o.target = target;
  return o;
}

console.log("--- 1. Vereinigung: keine Woche geht verloren ---");
var A = { "2026-W20": w(6,4,2100,2200), "2026-W21": w(5,3,2050,2200) };
var B = { "2026-W22": w(7,5,2150,2200) };
var m = mergeWeekStats(B, A);
pr("alle drei Wochen da", Object.keys(m).length === 3, JSON.stringify(Object.keys(m)));
pr("A-Woche unveraendert", m["2026-W20"].kcal === 2100);
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
  [{ "2026-W20": w(5,3,2000,2200) }, { "2026-W20": w(5,3,2400,2200) }],
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

console.log("--- 6. 26-Wochen-Grenze haelt auch nach der Vereinigung ---");
function viele(start, n) {
  var o = {};
  for (var i = 0; i < n; i++) {
    o["2026-W" + String(start + i).padStart(2, "0")] = w(5,3,2000,2200);
  }
  return o;
}
var gross = mergeWeekStats(viele(27, 26), viele(1, 26));
var keys = Object.keys(gross).sort();
pr("hoechstens 26 Wochen", keys.length === 26, keys.length + " Wochen");
pr("es sind die JUENGSTEN 26", keys[0] === "2026-W27" && keys[keys.length-1] === "2026-W52",
   keys[0] + " .. " + keys[keys.length-1]);

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
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")
    # Produktionscode schneiden, nicht abtippen.
    kern = schneide(quelle, u"function sanitizeWeekStats(o)", u"    return sanitizeWeekStats(out);") + u"\n  }\n"
    canon = schneide(quelle, u"function canonValue(v)", u"function canonJSON(v)")

    tmp = tempfile.mkdtemp(prefix="mp-weekstats-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + kern + u"\n" + canon + u"\n" + TEST + u"\n</script>")
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
