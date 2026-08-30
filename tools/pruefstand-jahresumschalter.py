#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruefstand: der gemeinsame Jahr-Umschalter (Paket 6, B6).

Was hier gemessen wird
----------------------
`weightYears()` speist den Jahr-Umschalter der Fortschritt-Seite. Ab B6 traegt derselbe
Umschalter auch den Kalender - also muss er die Jahre des Wochenarchivs kennen, auch wenn
in einem solchen Jahr nie gewogen wurde. Ohne das haette ein Konto ohne Gewichtsmessung
einen Umschalter, der das eigene Planungsjahr nicht anbietet.

Die eine Regel, die dabei nicht verhandelbar ist
------------------------------------------------
Die Jahre kommen aus `archivJahreZeigen()`, NICHT aus `Object.keys(state.weekStats)`.
`sanitizeWeekStats()` behaelt bewusst einen Jahrgang MEHR (`archivJahreBehalten()` = 3)
als angeboten werden soll (`archivJahreZeigen()` = 2). Wer hier ueber die vorhandenen
Schluessel ginge, boete das Pufferjahr mit an - und der Puffer waere keiner mehr. Genau
das prueft Abschnitt 2; er ist der eigentliche Grund fuer diesen Pruefstand.

Das Jahr kommt aus dem SCHLUESSEL-PRAEFIX, nie aus einem gerechneten Datum - dieselbe
Trimm-Regel wie in `sanitizeWeekStats()`. "2026-W01" liegt real im Dezember 2025.

Die Gegenprobe ist Pflicht
--------------------------
Gegen den Stand vor B6 (91c202b) fallen die Zeilen durch, die ohne die Archivjahre gar
nicht entstehen koennen - dort kennt `weightYears()` `state.weekStats` nicht.

**Und eine Falle beim Lesen dieser Gegenprobe:** Abschnitt 2 ist beim alten Stand GRUEN,
aber aus dem falschen Grund - wo ueberhaupt kein Archivjahr angeboten wird, kann auch kein
Pufferjahr durchrutschen. Die Zeilen 1 und 2 gehoeren deshalb zusammen gelesen: Abschnitt 2
misst erst etwas, wenn Abschnitt 1 gruen ist.

Aufruf:
    python tools/pruefstand-jahresumschalter.py            # heutige Fassung, muss gruen sein
    python tools/pruefstand-jahresumschalter.py 91c202b    # Gegenprobe, muss durchfallen
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASIS)

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def quelle(commit=None):
    if commit:
        r = subprocess.run(["git", "show", "%s:index.html" % commit],
                           capture_output=True, timeout=60)
        return r.stdout.decode("utf-8", errors="replace")
    return pm_quelle.lade_seite(os.path.join(BASIS, "index.html"))


def schneide(text, start, ende, name):
    """Schneidet echten Produktionscode aus - nicht abtippen, nicht nachbauen."""
    i = text.find(start)
    if i < 0:
        raise SystemExit("ABBRUCH: Startmarker fuer %s nicht gefunden (%r)" % (name, start))
    j = text.find(ende, i + len(start))
    if j < 0:
        raise SystemExit("ABBRUCH: Endmarker fuer %s nicht gefunden (%r)" % (name, ende))
    return text[i:j]


SEITE = """<!doctype html><meta charset="utf-8"><pre id="out"></pre><script>
var out = [];
function melde(t){ out.push(t); document.getElementById("out").textContent = out.join("\\n"); }
window.onerror = function(m,s,l){ melde("SKRIPTFEHLER Zeile " + l + ": " + m); };

// ---- Attrappen. Nur so viel, wie der ausgeschnittene Code braucht. ---------------
var state = { weights: [], weightGoals: {}, weekStats: {}, viewYear: null };
melde("Attrappen geladen.");
</script>

<script>
__ARCHIVJAHRE__
</script>

<script>
__CODE__
</script>

<script>
if (typeof weightYears !== "function" || typeof archivJahreZeigen !== "function") {
  melde("ABBRUCH: weightYears()/archivJahreZeigen() fehlen - ein Codeblock hat nicht geladen.");
  melde("FEHLERZAHL=99");
} else {
var fehler = 0;
function pruefe(name, bedingung, zusatz){
  if (bedingung) { melde("  OK      " + name); }
  else { fehler++; melde("  ROT     " + name + (zusatz ? "  -> " + zusatz : "")); }
}

// Die Jahre zur Laufzeit ableiten - ein fest eingetragenes "2026" waere am 1. Januar
// still falsch, und genau darum geht es an dieser Stelle.
var J   = new Date().getFullYear();
var LFD = String(J), VOR = String(J - 1), PUFFER = String(J - 2), ALT = String(J - 7);

melde("");
melde("1. Archivjahre erscheinen, auch ohne jede Messung");
state.weights = []; state.weightGoals = {};
state.weekStats = {}; state.weekStats[VOR + "-W07"] = { kcal: 1900, days: 5, hit: 3 };
var ys = weightYears();
pruefe("Vorjahr wird angeboten", ys.indexOf(VOR) !== -1,
       "angeboten wurde: " + ys.join(", "));
pruefe("laufendes Jahr bleibt dabei", ys.indexOf(LFD) !== -1, ys.join(", "));

melde("");
melde("2. Das Pufferjahr bleibt unsichtbar (der Kern dieses Pruefstands)");
// sanitizeWeekStats() BEHAELT diesen Jahrgang noch - angeboten werden darf er nicht.
state.weekStats[PUFFER + "-W30"] = { kcal: 2000, days: 7, hit: 5 };
state.weekStats[ALT + "-W12"] = { kcal: 2000, days: 4, hit: 2 };
ys = weightYears();
pruefe("Pufferjahr " + PUFFER + " nicht im Umschalter", ys.indexOf(PUFFER) === -1,
       "Object.keys(weekStats) statt archivJahreZeigen()? angeboten: " + ys.join(", "));
pruefe("uralter Jahrgang " + ALT + " nicht im Umschalter", ys.indexOf(ALT) === -1,
       ys.join(", "));

melde("");
melde("3. Ein reines Planungskonto hat trotzdem einen Umschalter");
state.weights = []; state.weightGoals = {};
state.weekStats = {}; state.weekStats[VOR + "-W44"] = { kcal: 1800, days: 6, hit: 4 };
ys = weightYears();
pruefe("zwei Jahre statt einem", ys.length === 2, "ys = " + ys.join(", "));

melde("");
melde("4. Gewichtsjahre werden NICHT vom Archivfenster gekappt");
// Das Fenster gilt fuer weekStats. Eine alte Messung ist ein eigenes Datum und
// darf nicht mitverschwinden.
state.weights = [{ m: ALT + "-W03", kg: 88 }];
state.weightGoals = {}; state.weightGoals[ALT] = 80;
state.weekStats = {};
ys = weightYears();
pruefe("altes Messjahr bleibt", ys.indexOf(ALT) !== -1, ys.join(", "));

melde("");
melde("5. Keine Dubletten, aufsteigend sortiert");
state.weights = [{ m: VOR + "-W03", kg: 88 }];
state.weightGoals = {};
state.weekStats = {}; state.weekStats[VOR + "-W44"] = { kcal: 1800, days: 6, hit: 4 };
ys = weightYears();
var einmalig = ys.filter(function(y){ return y === VOR; }).length === 1;
pruefe(VOR + " genau einmal", einmalig, ys.join(", "));
pruefe("sortiert", ys.join(",") === ys.slice().sort().join(","), ys.join(", "));

melde("");
melde("6. Kaputte Schluessel kippen den Umschalter nicht");
state.weights = []; state.weightGoals = {};
state.weekStats = { "kaputt": { days: 3 }, "": { days: 1 } };
state.weekStats[LFD + "-W01"] = { kcal: 1700, days: 3, hit: 1 };
ys = weightYears();
pruefe("nur echte Jahre", ys.join(",") === LFD, ys.join(", "));

melde("");
melde("7. activeYear() nimmt ein Archivjahr an");
state.weights = []; state.weightGoals = {};
state.weekStats = {}; state.weekStats[VOR + "-W20"] = { kcal: 1900, days: 5, hit: 3 };
state.viewYear = J - 1;
pruefe("viewYear " + VOR + " bleibt stehen", activeYear() === VOR, activeYear());
state.viewYear = J - 5;                      // Jahr, das es nicht gibt
pruefe("unbekanntes Jahr faellt auf das letzte zurueck", activeYear() === LFD, activeYear());

melde("");
melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                   : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
melde("FEHLERZAHL=" + fehler);
}
</script>"""


def lauf(commit=None):
    text = quelle(commit)
    # Zwei Schnitte: das Archivfenster liegt weit oben (bei load()), der Umschalter
    # weiter unten bei der Gewichtskarte.
    jahre = schneide(text,
                     "  function archivJahre(anzahl) {",
                     "  // Archiv saeubern:",
                     "archivJahre")
    code = schneide(text,
                    "  // Jahre, die eine Ansicht verdienen:",
                    "  // Das Diagramm.",
                    "weightYears")

    if "function archivJahreZeigen" not in jahre:
        raise SystemExit("ABBRUCH: archivJahreZeigen() steckt nicht im Ausschnitt.")
    if "function weightYears" not in code or "function activeYear" not in code:
        raise SystemExit("ABBRUCH: weightYears()/activeYear() stecken nicht im Ausschnitt.")

    seite = SEITE.replace("__ARCHIVJAHRE__", jahre).replace("__CODE__", code)
    tmp = tempfile.mkdtemp(prefix="jahresumschalter-")
    hpfad = os.path.join(tmp, "probe.html")
    with open(hpfad, "w", encoding="utf-8") as f:
        f.write(seite)

    dump = os.path.join(tmp, "dump.html")
    with open(dump, "w", encoding="utf-8") as f:
        subprocess.run([EDGE, "--headless=new", "--disable-gpu",
                        "--virtual-time-budget=6000",
                        "--user-data-dir=" + os.path.join(tmp, "prof"),
                        "--dump-dom", "file:///" + hpfad.replace("\\", "/")],
                       stdout=f, stderr=subprocess.DEVNULL, timeout=120)
    with open(dump, encoding="utf-8", errors="replace") as f:
        roh = f.read()

    m = re.search(r'<pre id="out">(.*?)</pre>', roh, re.S)
    if not m:
        raise SystemExit("ABBRUCH: keine Ausgabe - lief das Skript ueberhaupt?")
    ausgabe = (m.group(1).replace("&lt;", "<").replace("&gt;", ">")
               .replace("&quot;", '"').replace("&#39;", "'").replace("&amp;", "&"))
    print(ausgabe.strip())
    z = re.search(r"FEHLERZAHL=(\d+)", ausgabe)
    return int(z.group(1)) if z else -1


if __name__ == "__main__":
    commit = sys.argv[1] if len(sys.argv) > 1 else None
    kopf = ("GEGENPROBE gegen %s - diese Fassung MUSS durchfallen" % commit) if commit \
        else "Heutige Fassung - diese Fassung muss gruen sein"
    print(kopf)
    print("=" * 66)
    n = lauf(commit)
    print("=" * 66)
    if commit:
        print("Gegenprobe bestanden." if n > 0 else
              "GEGENPROBE GESCHEITERT: Der alte Stand ist gruen - der Test misst nichts.")
        sys.exit(0 if n > 0 else 1)
    sys.exit(0 if n == 0 else 1)
