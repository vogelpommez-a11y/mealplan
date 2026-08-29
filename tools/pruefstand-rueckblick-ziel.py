#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruefstand: Wochen OHNE eigenes Ziel duerfen im Rueckblick nicht auftauchen.

Der Fehler, gegen den er gebaut ist (Paket 6, B4)
-------------------------------------------------
Seit `archiveWeek()` auch ohne Ziel archiviert (B2), entstehen Archivwochen ohne `target`.
`rueckblickHtml()` fiel dafuer auf `avgDailyTargetToday()` zurueck - mass eine zielfreie
Woche also am HEUTIGEN Ziel - und schrieb "0 von 5 Tagen im Ziel" fuer eine Woche, in der
es gar kein Ziel gab. Eine falsche Aussage, keine fehlende.

Sichtbar auf dem normalen Weg: erst ein paar Wochen planen, spaeter das erste Ziel setzen.

Die Gegenprobe ist Pflicht
--------------------------
Der Pruefstand laeuft gegen ZWEI Fassungen: die heutige (muss gruen sein) und die aus
`git show <commit>:index.html` (muss DURCHFALLEN). Ein Pruefstand, den die alte Fassung
schon besteht, misst nicht das, was er zu messen vorgibt.

Aufruf:
    python tools/pruefstand-rueckblick-ziel.py            # heutige Fassung
    python tools/pruefstand-rueckblick-ziel.py 76d1120    # Gegenprobe gegen den Stand davor
"""
import os
import re
import subprocess
import sys
import tempfile

import os
import sys
# pm_quelle baut css/, data/ und lib/ wieder in die Seite ein - echter
# Produktionscode, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WURZEL)

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def quelle(commit=None):
    if commit:
        r = subprocess.run(["git", "show", "%s:index.html" % commit],
                           capture_output=True, timeout=60)
        return r.stdout.decode("utf-8", errors="replace")
    # Ueber pm_quelle, damit auch Code gefunden wird, der inzwischen in css/,
    # data/ oder lib/ liegt. Der Modulname ist bewusst pm_quelle: die Funktion,
    # in der wir hier stehen, heisst selbst quelle().
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
// STREAK_MIN_DAYS wird NICHT gestubbt: Die Konstante steht im ausgeschnittenen Bereich
// selbst. Eine eigene Fassung daneben gab "Identifier has already been declared" - und
// weil ein Parse-Fehler den ganzen Block toetet, war die Ausgabe zuerst schlicht leer.
// Deshalb liegen Attrappen, Produktionscode und Pruefungen in DREI script-Bloecken:
// So ueberlebt der Fehlermelder aus dem ersten Block einen Fehler im zweiten.
var DAYS = [{key:"mo"},{key:"di"},{key:"mi"},{key:"do"},{key:"fr"},{key:"sa"},{key:"so"}];
var state = { weekStats: {}, plans: {}, goal: { kcal: 2000 } };
function nfmt(n){ return String(Math.round(n)); }
function esc(s){ return String(s).replace(/[&<>"']/g, function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
function weekKwLabel(k){ return "KW " + k.slice(-2); }
function weekKeyFor(){ return "2026-W99"; }        // aktuelle Woche: absichtlich leer
function isoWeekKey(){ return "2026-W98"; }        // Streak laeuft damit ins Leere
function dayNutOf(){ return null; }
function hasNut(){ return false; }

// HEUTIGES Ziel - genau der Wert, mit dem die alte Fassung faelschlich gemessen hat.
var HEUTE_ZIEL = 2000;
function avgDailyTargetToday(){ return HEUTE_ZIEL; }
function goalTargetsForDay(){ return { kcal: HEUTE_ZIEL }; }
melde("Attrappen geladen.");
</script>

<script>
__CODE__
</script>

<script>
if (typeof rueckblickHtml !== "function") {
  melde("ABBRUCH: rueckblickHtml() ist nicht definiert - der Codeblock hat nicht geladen.");
  melde("FEHLERZAHL=99");
} else {
// ---- Pruefungen ------------------------------------------------------------------
var fehler = 0;
function pruefe(name, bedingung, zusatz){
  if (bedingung) { melde("  OK      " + name); }
  else { fehler++; melde("  ROT     " + name + (zusatz ? "  -> " + zusatz : "")); }
}

// Zwei Wochen MIT eigenem Ziel, zwei OHNE - so sieht ein Konto aus, das erst geplant
// und spaeter sein erstes Ziel gesetzt hat.
state.weekStats = {
  "2026-W20": { kcal: 1500, days: 5, hit: 0 },                 // ohne target
  "2026-W21": { kcal: 1600, days: 6, hit: 0 },                 // ohne target
  "2026-W22": { kcal: 1950, days: 5, hit: 4, target: 1900 },   // mit target
  "2026-W23": { kcal: 2050, days: 7, hit: 6, target: 2100 }    // mit target
};

var html = rueckblickHtml();

melde("1. Zielfreie Wochen tauchen nicht auf");
pruefe("KW 20 nicht in der Grafik", html.indexOf("KW 20") < 0, "zielfreie Woche wird gezeigt");
pruefe("KW 21 nicht in der Grafik", html.indexOf("KW 21") < 0, "zielfreie Woche wird gezeigt");

melde("");
melde("2. Wochen mit Ziel bleiben sichtbar");
pruefe("KW 22 vorhanden", html.indexOf("KW 22") >= 0);
pruefe("KW 23 vorhanden", html.indexOf("KW 23") >= 0);

melde("");
melde("3. Keine falsche Aussage im Etikett");
// Die alte Fassung schrieb fuer KW 20 "0 von 5 Tagen im Ziel" - genau danach suchen.
pruefe("kein '0 von 5 Tagen im Ziel'", html.indexOf("0 von 5 Tagen im Ziel") < 0,
       "zielfreie Woche wird als verfehlt dargestellt");
pruefe("kein '0 von 6 Tagen im Ziel'", html.indexOf("0 von 6 Tagen im Ziel") < 0,
       "zielfreie Woche wird als verfehlt dargestellt");
// Und das heutige Ziel darf nirgends als Massstab einer fremden Woche auftauchen.
var zielTreffer = (html.match(/Ziel 2000/g) || []).length;
pruefe("heutiges Ziel nicht als Massstab", zielTreffer === 0,
       "'Ziel 2000' kommt " + zielTreffer + "x vor - das ist avgDailyTargetToday()");

melde("");
melde("4. Kennzahl 'Ziel getroffen' rechnet nur ueber Zielwochen");
// Erwartet: hit 4+6 = 10 von days 5+7 = 12. Mit den zielfreien Wochen waeren es 10/23.
pruefe("zeigt 10/12 Tage", html.indexOf(">10<") >= 0 && html.indexOf("/12 Tage") >= 0,
       "gefundene Fussnote: " + (html.match(/Ziel getroffen.{0,80}/) || ["-"])[0]);

melde("");
melde("5. Ohne jede Zielwoche bleibt die Grafik weg");
state.weekStats = { "2026-W20": { kcal: 1500, days: 5, hit: 0 } };
var leer = rueckblickHtml();
pruefe("kein Balkenbereich", leer.indexOf("rueck-bars") < 0);

melde("");
melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                   : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
melde("FEHLERZAHL=" + fehler);
}
</script>"""


def lauf(commit=None):
    text = quelle(commit)
    code = schneide(text,
                    "  function avgDailyTargetToday() {",
                    "  function initRueckblick() {",
                    "rueckblickHtml")

    # Zusicherungen: hat der Schnitt wirklich das Richtige erwischt?
    if "function rueckblickHtml" not in code:
        raise SystemExit("ABBRUCH: rueckblickHtml() steckt nicht im Ausschnitt.")
    if "shownKeys" not in code:
        raise SystemExit("ABBRUCH: shownKeys fehlt - falscher Bereich geschnitten.")

    # Die Attrappe definiert avgDailyTargetToday selbst; die echte muss raus, sonst
    # gewinnt die zweite Definition und der Test misst seine eigene Attrappe nicht.
    code = re.sub(r"^  function avgDailyTargetToday\(\) \{.*?^  \}\n", "",
                  code, count=1, flags=re.S | re.M)

    seite = SEITE.replace("__CODE__", code)
    tmp = tempfile.mkdtemp(prefix="rueckblick-")
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
