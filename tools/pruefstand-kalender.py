#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruefstand: Fortschritt-Kalender und Tages-Serie (Paket 6, B7 und B8).

Was hier gemessen wird
----------------------
`kalenderHtml()` zeichnet ein ganzes Jahr als 7x52-Band, `dayStreak()` zaehlt die Tage am
Stueck. Beide lesen ihre Bits ueber `kalWoche()` - eine Quelle fuer laufende Wochen
(`state.plans` via `weekMaskOf()`) und archivierte (`weekStats[..].d`).

Die vier Aussagen, auf die es ankommt
-------------------------------------
1. **Die laufende Woche steht im Band**, obwohl sie gar nicht im Archiv ist - das ist der
   Sinn von `pruneWeeks()`, und ein Kalender, der die aktuelle Woche verschweigt, waere
   fuer den taeglichen Gebrauch wertlos.
2. **Eine Woche mit Datensatz, aber ohne Maske** (vor dem 29.08.2026 archiviert) wird NICHT
   als sieben leere Tage gezeichnet. Sie bekommt einen eigenen, neutral gefuellten Zustand, und
   `dayStreak()` bricht an ihr ab statt sie als Nullen zu lesen.
3. **Das heutige Bit bricht die Serie nicht.** Wer am Vormittag noch nicht geplant hat,
   verliert seine Serie nicht - die Zaehlung beginnt dann bei gestern.
4. **Kein waagerechter Scroller** und keine 53. Spalte in einem 52-Wochen-Jahr.

Die Gegenprobe
--------------
Gegen `91c202b` bricht der Lauf mit "Endmarker nicht gefunden" ab, weil `kalenderHtml()`
dort noch gar nicht existiert. **Ein Abbruch ist kein roter Test** (docs/TESTING.md). Die
gueltige Gegenprobe laeuft deshalb ueber eine verstellte Kopie:

    python tools/pruefstand-kalender.py --gegenprobe

Sie ersetzt `kalWoche()` durch die naive Fassung, die nur ins Archiv schaut (also die
laufende Woche verliert) und einen Datensatz ohne Maske als sieben Nullen liest. Genau die
Zeilen 1 und 2 muessen damit rot werden.

Aufruf:
    python tools/pruefstand-kalender.py
    python tools/pruefstand-kalender.py --gegenprobe
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


def schneide(text, start, ende, name):
    i = text.find(start)
    if i < 0:
        raise SystemExit("ABBRUCH: Startmarker fuer %s nicht gefunden (%r)" % (name, start))
    j = text.find(ende, i + len(start))
    if j < 0:
        raise SystemExit("ABBRUCH: Endmarker fuer %s nicht gefunden (%r)" % (name, ende))
    return text[i:j]


# Die naive Fassung fuer die Gegenprobe: nur Archiv, Datensatz ohne Maske als sieben Nullen.
NAIV = """  function kalWoche(wk) {
    const s = (state.weekStats || {})[wk];
    if (!s) return null;
    if (/^[01]{7}$/.test(s.d || "")) return { mask: s.d, tage: maskDays(s.d) };
    return { mask: "0000000", tage: Math.max(0, Math.round(Number(s.days) || 0)) };
  }
"""

SEITE = """<!doctype html><meta charset="utf-8"><div id="view"></div><pre id="out"></pre><script>
var out = [];
function melde(t){ out.push(t); document.getElementById("out").textContent = out.join("\\n"); }
window.onerror = function(m,s,l){ melde("SKRIPTFEHLER Zeile " + l + ": " + m); };

// ---- Attrappen ------------------------------------------------------------------
var view = document.getElementById("view");
var DAYS = [
  { key: "mon", label: "Montag", short: "Mo" },
  { key: "tue", label: "Dienstag", short: "Di" },
  { key: "wed", label: "Mittwoch", short: "Mi" },
  { key: "thu", label: "Donnerstag", short: "Do" },
  { key: "fri", label: "Freitag", short: "Fr" },
  { key: "sat", label: "Samstag", short: "Sa" },
  { key: "sun", label: "Sonntag", short: "So" }
];
var state = { plans: {}, weekStats: {}, weights: [], weightGoals: {}, viewYear: null, goal: { kcal: 2000 } };
// initKalender() sucht ueber view - hier ein echter Knoten im Dokument, damit focus()
// wirklich fokussiert. Ein losgeloester Knoten nimmt keinen Fokus an.
var view = document.createElement("div");
document.body.appendChild(view);
function esc(s){ return String(s).replace(/[&<>"']/g, function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
// Ein Tag gilt als beplant, wenn im Plan an diesem Tag ueberhaupt etwas mit Naehrwerten
// steht. Der echte Weg (dayNutOf/hasNut) haengt am ganzen Rezeptbestand - hier genuegt
// die Form, die weekMaskOf() tatsaechlich abfragt.
function dayNutOf(pl, key){ return pl && pl[key] ? { kcal: 500 } : null; }
function hasNut(n){ return !!(n && n.kcal); }
function weightYears(){ return ["2025", "2026"]; }
function activeYear(){ return String(state.viewYear || new Date().getFullYear()); }
var J_VOR = new Date().getFullYear() - 1;
melde("Attrappen geladen.");
</script>

<script>
__WOCHEN__
</script>

<script>
__KAL__
</script>

<script>
if (typeof kalenderHtml !== "function" || typeof dayStreak !== "function") {
  melde("ABBRUCH: kalenderHtml()/dayStreak() fehlen - ein Codeblock hat nicht geladen.");
  melde("FEHLERZAHL=99");
} else {
var fehler = 0;
function pruefe(name, bedingung, zusatz){
  if (bedingung) { melde("  OK      " + name); }
  else { fehler++; melde("  ROT     " + name + (zusatz ? "  -> " + zusatz : "")); }
}

// Alles relativ zu HEUTE - ein fest eingetragenes Datum waere ab morgen eine andere Probe.
var heute = new Date();
var JAHR = String(heute.getFullYear());
state.viewYear = heute.getFullYear();
function tagVor(n){ var d = new Date(); d.setDate(d.getDate() - n); return d; }
function wkVon(d){ return isoWeekKey(d); }
function idxVon(d){ return (d.getDay() || 7) - 1; }
// Einen Plan bauen, in dem genau die genannten Wochentag-Indizes beplant sind.
function planMit(idxs){ var pl = {}; idxs.forEach(function(i){ pl[DAYS[i].key] = [{ id: "x" }]; }); return pl; }
// Eine Maske bauen, in der genau die genannten Indizes 1 sind.
function maske(idxs){ var m = "0000000".split(""); idxs.forEach(function(i){ m[i] = "1"; }); return m.join(""); }

melde("");
melde("1. Die laufende Woche steht im Band (sie ist NICHT im Archiv)");
var curWk = wkVon(heute), curIdx = idxVon(heute);
state.plans = {}; state.plans[curWk] = planMit([curIdx]);
state.weekStats = {};
var html = kalenderHtml();
var geplanteZellen = (html.match(/class="kal-c on/g) || []).length;
pruefe("genau eine geplante Zelle", geplanteZellen === 1, geplanteZellen + " gefunden");
pruefe("Klartextzeile zaehlt sie mit", html.indexOf("1 von 5") > -1 || /1 von \\d+ Wochen geplant/.test(html),
       (html.match(/\\d+ von \\d+ Wochen geplant[^<]*/) || ["-"])[0]);
pruefe("heutige Zelle ist markiert", (html.match(/kal-c on today/g) || []).length === 1);
pruefe("aria-current gesetzt", (html.match(/aria-current="date"/g) || []).length === 1);

melde("");
melde("2. Woche mit Datensatz, aber ohne Maske: eigener Zustand statt sieben Nullen");
state.plans = {};
state.weekStats = {}; state.weekStats[wkVon(tagVor(21))] = { kcal: 1900, days: 5, hit: 3 };
html = kalenderHtml();
pruefe("sieben eigene Zellen fuer die Woche ohne Maske", (html.match(/class="kal-c unk/g) || []).length === 7,
       (html.match(/class="kal-c unk/g) || []).length + " gefunden");
pruefe("keine als 'nichts geplant' behauptete Zelle in dieser Woche",
       (html.match(/class="kal-c on/g) || []).length === 0);
pruefe("die Tage zaehlen trotzdem mit", /5 Tage/.test(html),
       (html.match(/\\d+ von \\d+ Wochen geplant[^<]*/) || ["-"])[0]);

melde("");
melde("3. Das Band hat genau so viele Spalten, wie das Jahr Wochen hat");
state.plans = {}; state.weekStats = {};
html = kalenderHtml();
var ersteZeile = (html.match(/<tr><th scope="row"[\\s\\S]*?<\\/tr>/) || [""])[0];
var spalten = (ersteZeile.match(/<td/g) || []).length;
var soll = isoWochenImJahr(+JAHR);
pruefe("Spaltenzahl = " + soll, spalten === soll, spalten + " Spalten");
pruefe("Monatsband deckt alle Spalten", (function(){
  var sum = 0, re = /<th scope="colgroup" colspan="(\\d+)"/g, m;
  while ((m = re.exec(html))) sum += +m[1];
  return sum === soll;
})(), "Summe der colspans");
pruefe("kein eigener Scroll-Container", html.indexOf("overflow") < 0);

melde("");
melde("4. Tages-Serie: zaehlt ueber die Wochengrenze");
// Heute und die 9 Tage davor beplant - das laeuft ueber mindestens eine Wochengrenze.
state.plans = {}; state.weekStats = {};
for (var i = 0; i <= 9; i++) {
  var d = tagVor(i), wk = wkVon(d);
  if (i <= 6 && wk === curWk) {
    state.plans[wk] = state.plans[wk] || {};
    state.plans[wk][DAYS[idxVon(d)].key] = [{ id: "x" }];
  } else {
    var m = state.weekStats[wk] ? state.weekStats[wk].d.split("") : "0000000".split("");
    m[idxVon(d)] = "1";
    state.weekStats[wk] = { kcal: 1900, days: m.join("").split("1").length - 1, hit: 0, d: m.join("") };
  }
}
pruefe("Serie = 10 Tage", dayStreak() === 10, "gezaehlt: " + dayStreak());

melde("");
melde("5. Ein unbeplantes HEUTE bricht die Serie nicht");
// Dieselben Daten, nur ohne heute.
var curPl = state.plans[curWk];
if (curPl) delete curPl[DAYS[curIdx].key];
pruefe("Serie = 9 Tage (ab gestern)", dayStreak() === 9, "gezaehlt: " + dayStreak());

melde("");
melde("6. Eine Woche ohne Maske beendet die Serie, statt sie als Nullen zu lesen");
state.plans = {}; state.weekStats = {};
state.plans[curWk] = planMit([0,1,2,3,4,5,6]);
// Die Vorwoche: Datensatz vorhanden, aber kein `d`.
state.weekStats[wkVon(tagVor(7 + curIdx))] = { kcal: 1900, days: 7, hit: 0 };
var n6 = dayStreak();
pruefe("Serie endet am Wochenanfang", n6 === curIdx + 1, "gezaehlt: " + n6 + ", erwartet " + (curIdx + 1));

melde("");
melde("7. Ohne jede Planung ist die Serie 0 und das Band leer");
state.plans = {}; state.weekStats = {};
pruefe("Serie = 0", dayStreak() === 0, "gezaehlt: " + dayStreak());
html = kalenderHtml();
pruefe("keine geplante Zelle", html.indexOf('class="kal-c on') < 0);
pruefe("ehrlicher Leerzustand", html.indexOf("noch keine geplante Woche") > -1);

melde("");
melde("8. Die Serie laeuft nicht ewig (Deckel)");
// Jede Woche des Archivs voll - ohne Deckel liefe die Schleife ins Unendliche.
state.plans = {}; state.plans[curWk] = planMit([0,1,2,3,4,5,6]);
state.weekStats = {};
for (var w = 1; w <= 53; w++) {
  ["2025", "2026"].forEach(function(y){
    state.weekStats[y + "-W" + String(w).padStart(2, "0")] = { kcal: 1900, days: 7, hit: 0, d: "1111111" };
  });
}
var n8 = dayStreak();
pruefe("Serie bleibt endlich und <= 400", n8 > 0 && n8 <= 400, "gezaehlt: " + n8);

melde("");
melde("9. Das Band ist mit der Tastatur bedienbar");
// Ein Band mit 371 Tabstopps waere das Gegenteil von barrierefrei: Wer die Karte nur
// ueberspringen will, drueckte 371-mal Tab. Also genau EIN Einstieg, Pfeiltasten darin.
state.plans = {}; state.weekStats = {};
state.plans[curWk] = planMit([curIdx]);
view.innerHTML = kalenderHtml();
initKalender();
var zellen = view.querySelectorAll("td.kal-c");
var einstiege = view.querySelectorAll('td.kal-c[tabindex="0"]');
pruefe("genau ein Tabstopp im ganzen Band", einstiege.length === 1,
       einstiege.length + " Zellen mit tabindex 0 bei " + zellen.length + " Zellen");
pruefe("der Einstieg ist HEUTE", einstiege[0] && einstiege[0].classList.contains("today"),
       einstiege[0] ? einstiege[0].className : "-");

// Pfeiltasten. Der Start ist bewusst eine feste Zelle in der Mitte des Bandes und NICHT
// "heute": Faellt heute auf einen Sonntag, ist das die letzte Zeile - dann geht ArrowDown
// zu Recht nicht, und der Test misst den Wochentag statt die Bedienung. Genau darauf ist
// die erste Fassung am 30.08. (einem Sonntag) hereingefallen.
var koerper = view.querySelector("tbody");
function tasteAuf(el, k){ el.focus(); el.dispatchEvent(new KeyboardEvent("keydown", { key: k, bubbles: true })); }
function aktiv(){ return view.ownerDocument.activeElement; }

var mitte = koerper.rows[2].cells[5];
tasteAuf(mitte, "ArrowRight");
pruefe("ArrowRight geht eine Woche weiter", aktiv().cellIndex === 6 && aktiv().parentElement.sectionRowIndex === 2,
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
tasteAuf(koerper.rows[2].cells[5], "ArrowDown");
pruefe("ArrowDown geht einen Wochentag tiefer", aktiv().parentElement.sectionRowIndex === 3 && aktiv().cellIndex === 5,
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
tasteAuf(koerper.rows[2].cells[5], "ArrowUp");
pruefe("ArrowUp geht einen Wochentag zurueck", aktiv().parentElement.sectionRowIndex === 1);
tasteAuf(koerper.rows[2].cells[5], "Home");
pruefe("Home springt in die erste Woche", aktiv().cellIndex === 1);
tasteAuf(koerper.rows[2].cells[5], "End");
pruefe("End springt in die letzte Woche", aktiv().cellIndex === koerper.rows[2].cells.length - 1);

pruefe("der Tabstopp wandert mit",
       view.querySelectorAll('td.kal-c[tabindex="0"]').length === 1 &&
       view.querySelector('td.kal-c[tabindex="0"]') === aktiv());

// Der Tipp muss auf den FOKUS antworten - sonst gaebe es einen Weg hinein, aber keine
// Antwort darin. Vorher leeren, sonst misst die Zeile den Rest eines Mausereignisses.
view.querySelector(".kal-tip").textContent = "";
koerper.rows[1].cells[9].focus();
pruefe("der Tipp folgt dem Fokus", /KW \d+ · \w+/.test(view.querySelector(".kal-tip").textContent),
       "'" + view.querySelector(".kal-tip").textContent + "'");

// An den Raendern darf nichts passieren - und vor allem nichts abstuerzen.
var links = koerper.rows[0].cells[1];
tasteAuf(links, "ArrowLeft");
pruefe("am linken Rand bleibt der Fokus stehen", aktiv() === links);
tasteAuf(koerper.rows[0].cells[1], "ArrowUp");
pruefe("in der obersten Zeile bleibt er ebenfalls", aktiv() === koerper.rows[0].cells[1]);
var rechts = koerper.rows[0].cells[koerper.rows[0].cells.length - 1];
tasteAuf(rechts, "ArrowRight");
pruefe("am rechten Rand bleibt der Fokus stehen", aktiv() === rechts);

melde("");
melde("10. Ein Jahr ohne heutigen Tag bleibt erreichbar");
// Im Vorjahr traegt keine Zelle "today" - ohne Nachbesserung haette das Band dort gar
// keinen Tabstopp und waere per Tastatur unerreichbar.
state.viewYear = J_VOR;
view.innerHTML = kalenderHtml();
var e2 = view.querySelectorAll('td.kal-c[tabindex="0"]');
pruefe("auch dort genau ein Tabstopp", e2.length === 1, e2.length + " gefunden");
state.viewYear = heute.getFullYear();

melde("");
melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                   : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
melde("FEHLERZAHL=" + fehler);
}
</script>"""


def lauf(gegenprobe=False):
    text = pm_quelle.lade_seite(os.path.join(BASIS, "index.html"))
    # Wochenschluessel, Maske und Montagsrechnung liegen oben bei load().
    wochen = schneide(text, "  function isoWeekKey(date) {", "  function activeWeekKey()", "isoWeekKey")
    wochen += schneide(text, "  function weekMaskOf(pl) {", "  // Kennzahlen einer abgelaufenen Woche", "weekMaskOf")
    wochen += schneide(text, "  function weekNumOf(s)", "  // Bewusst `function` und keine const-Arrow", "weekMonday")
    # Kalender und Tages-Serie.
    kal = schneide(text, "  const STREAK_MIN_DAYS = 5;", "  function rueckblickHtml() {", "dayStreak")
    # Bis EINSCHLIESSLICH initKalender(): Abschnitt 9 fuehrt die Tastatur im echten DOM.
    kal += schneide(text, "  // ---------- Fortschritt-Kalender", "  // Zeichnet das Diagramm in der gemessenen Breite", "kalenderHtml")

    if "function weekMonday" not in wochen or "function weekMaskOf" not in wochen:
        raise SystemExit("ABBRUCH: Wochenhelfer stecken nicht im Ausschnitt.")
    if "function kalenderHtml" not in kal or "function dayStreak" not in kal:
        raise SystemExit("ABBRUCH: kalenderHtml()/dayStreak() stecken nicht im Ausschnitt.")
    if "function initKalender" not in kal:
        raise SystemExit("ABBRUCH: initKalender() steckt nicht im Ausschnitt.")

    if gegenprobe:
        neu, n = re.subn(r"  function kalWoche\(wk\) \{.*?\n  \}\n", NAIV, kal, count=1, flags=re.S)
        if n != 1:
            raise SystemExit("ABBRUCH: kalWoche() nicht ersetzbar - Gegenprobe misst nichts.")
        kal = neu

    seite = SEITE.replace("__WOCHEN__", wochen).replace("__KAL__", kal)
    tmp = tempfile.mkdtemp(prefix="kalender-")
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
    gp = "--gegenprobe" in sys.argv
    print("GEGENPROBE (kalWoche naiv) - diese Fassung MUSS durchfallen" if gp
          else "Heutige Fassung - diese Fassung muss gruen sein")
    print("=" * 66)
    n = lauf(gp)
    print("=" * 66)
    if gp:
        print("Gegenprobe bestanden." if n > 0 else
              "GEGENPROBE GESCHEITERT: Die naive Fassung ist gruen - der Test misst nichts.")
        sys.exit(0 if n > 0 else 1)
    sys.exit(0 if n == 0 else 1)
