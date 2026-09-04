#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruefstand: Wochen OHNE eigenes Ziel duerfen in der Ziel-Quote nicht auftauchen.

Der Fehler, gegen den er gebaut ist (Paket 6, B4)
-------------------------------------------------
Seit `archiveWeek()` auch ohne Ziel archiviert (B2), entstehen Archivwochen ohne `target`.
Der Rueckblick fiel dafuer auf `avgDailyTargetToday()` zurueck - mass eine zielfreie
Woche also am HEUTIGEN Ziel - und schrieb "0 von 5 Tagen im Ziel" fuer eine Woche, in der
es gar kein Ziel gab. Eine falsche Aussage, keine fehlende.

Der Rueckblick selbst ist am 04.09.2026 geloescht (Konzept G, Stufe 2). Die ZUSICHERUNG
ist geblieben und liegt heute in `zielQuote()`, deren Zahl im Kalenderfuss steht - deshalb
wandert dieser Pruefstand mit, statt mit dem Balken zu verschwinden.

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
    # Der Commit-Zweig ist am 03.09.2026 entfallen: Die Gegenprobe laeuft ueber eine
    # verstellte Kopie (NAIV_QUOTE), nicht gegen einen alten Stand - dort gibt es weder
    # zielQuote() noch den Kalender, und der Schnitt braeche ab. Ein Abbruch ist kein
    # roter Test (docs/TESTING.md).
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
var state = { weekStats: {}, plans: {}, goal: { kcal: 2000 } };
function nfmt(n){ return String(Math.round(n)); }
function esc(s){ return String(s).replace(/[&<>"']/g, function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
function weekKeyFor(){ return "2026-W99"; }        // aktuelle Woche: absichtlich leer
function isoWeekKey(){ return "2026-W98"; }        // Streak laeuft damit ins Leere
function dayNutOf(){ return null; }
function hasNut(){ return false; }
// dayStreak() (Paket 6, B8) liegt seit dem 30.08.2026 mit im Ausschnitt und liest die
// Tagesbits ueber kalWoche() - eine Funktion, die weiter unten in index.html steht und
// hier bewusst NICHT mitgeschnitten wird. Gemessen wird der Ziel-Filter der Grafik, nicht
// die Serie: ohne Bits ist sie 0, und die zweite Kennzahl entfaellt. Wer die Serie messen
// will, nimmt tools/pruefstand-kalender.py.
function kalWoche(){ return null; }
// dayStreak() lag bis zum 04.09.2026 im zweiten Schnitt (dem Rueckblick-Block) und
// faellt seit dessen Loeschung unter die Attrappen. Ohne Bits ist die Tagesserie 0,
// die Kennzahl "Am Stueck" entfaellt damit im Fuss - gemessen wird hier die Quote.
function dayStreak(){ return 0; }

// HEUTIGES Ziel - genau der Wert, mit dem die alte Fassung faelschlich gemessen hat.
// Er steht hier weiter als Attrappe, obwohl avgDailyTargetToday() am 04.09.2026 mit dem
// Rueckblick geloescht wurde: Der Fehler, gegen den dieser Pruefstand gebaut ist, war
// genau dieser Rueckfall aufs heutige Ziel.
var HEUTE_ZIEL = 2000;
function goalTargetsForDay(){ return { kcal: HEUTE_ZIEL }; }
// Seit dem 03.09.2026 laeuft die Pruefung ueber den Kartenfuss des Kalenders mit - dafuer
// braucht kalenderHtml() diese Helfer. Alle stumm gehalten: Gemessen wird der Ziel-Filter,
// nicht das Gitter (das misst tools/pruefstand-kalender.py).
function activeYear(){ return String(state.viewYear || 2026); }
function activeMonth(){ return Number(state.kalMonth) || 0; }
function weightYears(){ return ["2025", "2026"]; }
function weekMonday(k){ var w = +String(k).slice(-2); var d = new Date(2026, 0, 1);
  d.setDate(d.getDate() + (w - 1) * 7); return d; }
function wochenSerie(){ return 0; }                 // ohne Bits keine Serie
function kalTagStatus(){ return null; }
function maskDays(){ return 0; }
var DAYS = [{ key: "mon", label: "Montag", short: "Mo" }, { key: "tue", label: "Dienstag", short: "Di" },
            { key: "wed", label: "Mittwoch", short: "Mi" }, { key: "thu", label: "Donnerstag", short: "Do" },
            { key: "fri", label: "Freitag", short: "Fr" }, { key: "sat", label: "Samstag", short: "Sa" },
            { key: "sun", label: "Sonntag", short: "So" }];
var ICON_CHECK = '<svg></svg>', ICON_CHEV_L = '<svg></svg>', ICON_CHEV_R = '<svg></svg>', ICON_FLAME = '<svg></svg>';
melde("Attrappen geladen.");
</script>

<script>
__CODE__
</script>

<script>
if (typeof zielQuote !== "function") {
  melde("ABBRUCH: zielQuote() ist nicht definiert - der Codeblock hat nicht geladen.");
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

// ⚠️ Geprueft wird seit dem 03.09.2026 zielQuote(), nicht mehr rueckblickHtml().
// Der Rueckblick-Balken ist mit Konzept G aus dem Reiter genommen; die Kennzahl steht
// jetzt im Kalenderfuss. Die ZUSICHERUNG ist dieselbe geblieben und genau deshalb wandert
// dieser Pruefstand mit, statt zu verschwinden: Eine Woche ohne eigenes `target` darf
// nicht mitgezaehlt werden - sonst misst die Quote sie am HEUTIGEN Ziel und behauptet
// "0 von 5 Tagen im Ziel" fuer eine Woche, in der es gar kein Ziel gab (B10).
//
// Ein Pruefstand, der weiter rueckblickHtml() misst, pruefte eine Funktion ohne Aufrufer -
// genau die Falle aus docs/TROUBLESHOOTING.md 144.
state.viewYear = 2026;
state.kalMode = "jahr";
var q = zielQuote("2026", 0, false);

melde("1. Zielfreie Wochen zaehlen nicht mit");
// Erwartet: hit 4+6 = 10 von days 5+7 = 12. Mit den zielfreien Wochen waeren es 10 von 23.
pruefe("Treffer = 10", q.hit === 10, "gezaehlt: " + q.hit);
pruefe("Bezugstage = 12, nicht 23", q.tage === 12, "gezaehlt: " + q.tage);

melde("");
melde("2. Die Quote steht auch im Kartenfuss");
var fuss = kalenderHtml();
pruefe("Fuss nennt 10", /10/.test(fuss), "kein Treffer im Markup");
// Die Escape-Sequenzen sind doppelt geschrieben: SEITE ist KEIN Raw-String (es traegt
// den Zeilenumbruch fuer melde() als doppelt geschriebenes n). Einfach geschrieben waeren
// sie fuer Python ungueltige Escapes - er laesst sie zwar stehen, warnt aber bei JEDEM
// Lauf, und eine Warnung ueber der Ausgabe verdeckt die Befunde, um die es geht
// (Befund kvp, 04.09.2026).
pruefe("Fuss nennt 12 als Bezug", /12\\s*<\\/span>|\\/12 Tage|>12</.test(fuss.replace(/&nbsp;/g, " ")),
       "Bezugsgroesse fehlt");

melde("");
melde("3. Ohne jede Zielwoche gibt es keine Quote");
state.weekStats = { "2026-W20": { kcal: 1500, days: 5, hit: 0 } };
var leer = zielQuote("2026", 0, false);
pruefe("keine Bezugstage", leer.tage === 0, "gezaehlt: " + leer.tage);
pruefe("keine Treffer", leer.hit === 0, "gezaehlt: " + leer.hit);
// Und im Fuss darf die Zeile dann gar nicht erst stehen - eine erfundene Null waere
// schlimmer als eine fehlende Zahl.
pruefe("und der Fuss zeigt sie nicht", kalenderHtml().indexOf("Im Ziel") < 0);

melde("");
melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                   : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
melde("FEHLERZAHL=" + fehler);
}
</script>"""


# Die verstellte Fassung fuer die Gegenprobe: zielQuote() ohne den target-Filter.
# Genau dieser Filter IST die Zusicherung aus B10 - eine Woche ohne eigenes Ziel darf
# nicht mitzaehlen, sonst wird sie am HEUTIGEN Ziel gemessen. Ohne ihn kommen die
# zielfreien Wochen (5 + 6 Tage) in die Bezugsgroesse: aus "10 von 12" wird "10 von 23".
NAIV_QUOTE = """  function zielQuote(year, mon, monat) {
    const stats = state.weekStats || {};
    let hit = 0, tage = 0;
    Object.keys(stats).forEach(wk => {
      if (wk.slice(0, 4) !== String(year)) return;
      const s = stats[wk];
      if (!s) return;
      hit += s.hit || 0;
      tage += s.days || 0;
    });
    return { hit: hit, tage: tage };
  }
"""

def lauf(gegenprobe=False):
    text = quelle(None)
    # Seit dem 03.09.2026 liegt die Regel in zielQuote(), und der Kartenfuss zeigt sie -
    # deshalb wird der ganze Kalenderblock geschnitten statt des Rueckblicks.
    # Ein Schnitt genuegt seit dem 04.09.2026: zielQuote() liegt im Kalenderblock, und
    # der Rueckblick - aus dem der zweite Schnitt kam - ist geloescht. Ein Schnitt auf
    # eine Funktion, die es nicht mehr gibt, braeche mit ABBRUCH ab, und ein Abbruch ist
    # kein roter Test (docs/TESTING.md).
    code = schneide(text,
                    "  // ---------- Fortschritt-Kalender",
                    "  // Werte per Tipp statt per Titel-Attribut",
                    "kalenderHtml")

    # Zusicherungen: hat der Schnitt wirklich das Richtige erwischt?
    if "function zielQuote" not in code:
        raise SystemExit("ABBRUCH: zielQuote() steckt nicht im Ausschnitt.")
    if "function kalenderHtml" not in code:
        raise SystemExit("ABBRUCH: kalenderHtml() steckt nicht im Ausschnitt.")

    # Gegenprobe: die echte zielQuote() durch die naive ersetzen.
    if gegenprobe:
        vorher = code
        muster = r"^  function zielQuote\(year, mon, monat\) \{.*?^  \}\n"
        code = re.sub(muster, NAIV_QUOTE, code, count=1, flags=re.S | re.M)
        if code == vorher:
            raise SystemExit("ABBRUCH: zielQuote() nicht ersetzt - die Gegenprobe misst nichts.")

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
    gegen = "--gegenprobe" in sys.argv
    kopf = "GEGENPROBE (zielQuote ohne target-Filter) - MUSS durchfallen" if gegen \
        else "Heutige Fassung - diese Fassung muss gruen sein"
    print(kopf)
    print("=" * 66)
    n = lauf(gegen)
    print("=" * 66)
    if gegen:
        print("Gegenprobe bestanden." if n > 0 else
              "GEGENPROBE GESCHEITERT: Die verstellte Fassung ist gruen - der Test misst nichts.")
        sys.exit(0 if n > 0 else 1)
    sys.exit(0 if n == 0 else 1)
