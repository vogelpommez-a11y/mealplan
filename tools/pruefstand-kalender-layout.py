#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruefstand: Das Kalenderband laeuft auf keiner Breite ueber (Paket 6, B7).

Warum es diesen Pruefstand gibt
-------------------------------
Das Band traegt 52 oder 53 Spalten und bekommt bewusst KEINEN eigenen Scroll-Container:
Auf Touch gewinnt immer der innere Scroller, und der Reiterwechsel bewegt diese Ansicht
per `slideIn()` (docs/TROUBLESHOOTING.md 58). Damit steht und faellt die Entscheidung
damit, dass 53 Spalten bei 360 px tatsaechlich passen - eine Rechnung auf dem Papier
("rund 5 px je Spalte") ist dafuer kein Beweis.

Gemessen wird deshalb beides, wie im Plan verlangt:

  * `scrollWidth <= clientWidth` am Dokument UND an der Tabelle - laeuft etwas ueber?
  * `tab.scrollWidth <= wrap.clientWidth` - passt das Band in die Karte?
  * `overflow-x` der Huelle - ist versehentlich doch ein Scroller entstanden?

**Die dritte Zeile ist die, auf die es ankommt, und sie stand in der ersten Fassung nicht
drin.** Die Kartenschale `.wg-col` hat `overflow: hidden`; ein zu breites Band laeuft damit
gar nicht ueber das Dokument, es wird lautlos abgeschnitten. Die Gegenprobe war deshalb
zunaechst gruen - der Pruefstand mass eine Zahl, die dieser Fehler nie beruehrt.

Dazu die Zellbreite: Spalten, die unter etwa 2 px fallen, sind kein Band mehr, sondern
ein Strich. Das faenge eine reine Ueberlaufpruefung NICHT - deshalb steht sie daneben.

Der iframe ist der Rahmen, nicht das Fenster
--------------------------------------------
Unter Windows laesst sich kein Chrome-Fenster auf 360 px ziehen, und `--window-size` wurde
mit `--headless=new --dump-dom` in einem Durchlauf komplett ignoriert (docs/TESTING.md).
Der `srcdoc`-iframe ist ein echter CSS-Viewport, Media Queries greifen darin normal.

Gemessen wird gegen `clientWidth` des iframe-Dokuments (nicht `innerWidth`): srcdoc-Rahmen
zeigen keine klassischen Scrollleisten, die 15 px wegnehmen wuerden.

Echtes CSS, echtes Markup
-------------------------
Die Stylesheets kommen ueber `quelle.css_gesamt()` in Ladereihenfolge, das Markup aus dem
ausgeschnittenen `kalenderHtml()`. Nichts davon ist abgetippt.

Gegenprobe:
    python tools/pruefstand-kalender-layout.py --gegenprobe

Sie stellt die Tabelle auf `table-layout: auto` und gibt jeder Zelle 12 px Mindestbreite -
also genau den Fehler, den der Pruefstand fangen soll. Bei 360 und 390 px muss er rot werden.
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
BREITEN = [360, 390, 768, 1280]

KAPUTT = """
  .kal-grid { table-layout: auto !important; }
  .kal-c { min-width: 12px !important; }
"""


def schneide(text, start, ende, name):
    i = text.find(start)
    if i < 0:
        raise SystemExit("ABBRUCH: Startmarker fuer %s nicht gefunden (%r)" % (name, start))
    j = text.find(ende, i + len(start))
    if j < 0:
        raise SystemExit("ABBRUCH: Endmarker fuer %s nicht gefunden (%r)" % (name, ende))
    return text[i:j]


SEITE = """<!doctype html><meta charset="utf-8"><pre id="out"></pre><div id="host"></div><script>
var out = [];
function melde(t){ out.push(t); document.getElementById("out").textContent = out.join("\\n"); }
window.onerror = function(m,s,l){ melde("SKRIPTFEHLER Zeile " + l + ": " + m); };

var DAYS = [
  { key: "mon", label: "Montag", short: "Mo" },
  { key: "tue", label: "Dienstag", short: "Di" },
  { key: "wed", label: "Mittwoch", short: "Mi" },
  { key: "thu", label: "Donnerstag", short: "Do" },
  { key: "fri", label: "Freitag", short: "Fr" },
  { key: "sat", label: "Samstag", short: "Sa" },
  { key: "sun", label: "Sonntag", short: "So" }
];
var state = { plans: {}, weekStats: {}, weights: [], weightGoals: {}, viewYear: null };
function esc(s){ return String(s).replace(/[&<>"']/g, function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]; }); }
function dayNutOf(pl, key){ return pl && pl[key] ? { kcal: 500 } : null; }
function hasNut(n){ return !!(n && n.kcal); }
function weightYears(){ return ["2025", "2026"]; }
function activeYear(){ return String(state.viewYear || new Date().getFullYear()); }
melde("Attrappen geladen.");
</script>

<script>
__WOCHEN__
</script>

<script>
__KAL__
</script>

<script>
var CSS = __CSS__;
var KAPUTT = __KAPUTT__;
if (typeof kalenderHtml !== "function") {
  melde("ABBRUCH: kalenderHtml() fehlt - der Codeblock hat nicht geladen.");
  melde("FEHLERZAHL=99");
} else {
var fehler = 0;
function pruefe(name, bedingung, zusatz){
  if (bedingung) { melde("  OK      " + name); }
  else { fehler++; melde("  ROT     " + name + (zusatz ? "  -> " + zusatz : "")); }
}

// Ein volles Jahr, damit das Band den ungünstigsten Fall zeigt: jede Woche belegt.
var jahr = new Date().getFullYear();
state.viewYear = jahr;
for (var w = 1; w <= 53; w++) {
  state.weekStats[jahr + "-W" + String(w).padStart(2, "0")] = { kcal: 1900, days: 7, hit: 4, d: "1111111" };
}
var markup = kalenderHtml();

function messe(breite, dunkel, kaputt, fertig){
  var f = document.createElement("iframe");
  f.style.cssText = "width:" + breite + "px;height:760px;border:0";
  // Die Karte sitzt in der App in einem Container mit Seitenpolsterung; 12 px je Seite ist
  // der Wert aus dem Mobil-Layout. Ohne ihn misst der Test eine Breite, die es nie gibt.
  f.srcdoc = '<!doctype html><html' + (dunkel ? ' data-theme="dark"' : '') + '><head><meta charset="utf-8">'
    + '<style>' + CSS + (kaputt ? KAPUTT : "") + '</style></head>'
    + '<body style="margin:0"><div style="padding:0 12px">' + markup + '</div></body></html>';
  f.onload = function(){
    var d = f.contentDocument;
    var de = d.documentElement;
    var tab = d.querySelector(".kal-grid");
    var wrap = d.querySelector(".kal-wrap");
    var zelle = d.querySelector("td.kal-c");
    var ovx = d.defaultView.getComputedStyle(wrap).overflowX;
    var zb = zelle ? zelle.getBoundingClientRect().width : 0;
    fertig({
      breite: breite, dunkel: dunkel,
      dokUeber: de.scrollWidth - de.clientWidth,
      tabUeber: tab.scrollWidth - tab.clientWidth,
      ovx: ovx, zellBreite: Math.round(zb * 100) / 100,
      istBreite: de.clientWidth,
      // Die entscheidende Zahl. Die Karte (.wg-col) hat overflow: hidden - ein zu breites
      // Band laeuft deshalb NICHT ueber das Dokument, es wird still abgeschnitten. Wer nur
      // am Dokument misst, sieht davon nichts: genau daran ist die erste Fassung dieses
      // Pruefstands in der Gegenprobe gruen geblieben.
      ausKarte: Math.round((tab.scrollWidth - wrap.clientWidth) * 100) / 100
    });
    f.remove();
  };
  document.getElementById("host").appendChild(f);
}

var reihe = [];
[360, 390, 768, 1280].forEach(function(b){ reihe.push([b, false]); reihe.push([b, true]); });
// Der Schalter steht IN der Seite, nicht in der URL: eine Query an einer file://-URL
// kam in Edge --headless nicht an, und die Gegenprobe lief dadurch als Normallauf
// durch - sie war gruen und bewies nichts.
var kaputt = __KAPUTT_AN__;
var i = 0;
function weiter(){
  if (i >= reihe.length) {
    melde("");
    melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                       : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
    melde("FEHLERZAHL=" + fehler);
    return;
  }
  var r = reihe[i++];
  messe(r[0], r[1], kaputt, function(m){
    melde("");
    melde(m.breite + " px " + (m.dunkel ? "dunkel" : "hell") + "  (soll=" + m.breite + " ist=" + m.istBreite + ", Zelle " + m.zellBreite + " px)");
    pruefe("kein waagerechter Ueberlauf im Dokument", m.dokUeber <= 0, "ueber: " + m.dokUeber + " px");
    pruefe("Band passt in die Karte (wird nicht abgeschnitten)", m.ausKarte <= 0.5, "ueber die Karte hinaus: " + m.ausKarte + " px");
    pruefe("Tabelle laeuft nicht ueber ihre Zelle hinaus", m.tabUeber <= 0, "ueber: " + m.tabUeber + " px");
    pruefe("kein Scroll-Container (overflow-x)", m.ovx === "visible", "overflow-x: " + m.ovx);
    pruefe("Zellen bleiben sichtbar (>= 2 px)", m.zellBreite >= 2, "Zellbreite: " + m.zellBreite + " px");
    weiter();
  });
}
weiter();
}
</script>"""


def lauf(gegenprobe=False):
    text = pm_quelle.lade_seite(os.path.join(BASIS, "index.html"))
    css = pm_quelle.css_gesamt(os.path.join(BASIS, "index.html"))

    wochen = schneide(text, "  function isoWeekKey(date) {", "  function activeWeekKey()", "isoWeekKey")
    wochen += schneide(text, "  function weekMaskOf(pl) {", "  // Kennzahlen einer abgelaufenen Woche", "weekMaskOf")
    wochen += schneide(text, "  function weekNumOf(s)", "  // Bewusst `function` und keine const-Arrow", "weekMonday")
    kal = schneide(text, "  // ---------- Fortschritt-Kalender", "  // Werte per Tipp statt per Titel-Attribut", "kalenderHtml")
    if "function kalenderHtml" not in kal:
        raise SystemExit("ABBRUCH: kalenderHtml() steckt nicht im Ausschnitt.")
    if ".kal-grid" not in css or ".kal-c" not in css:
        raise SystemExit("ABBRUCH: das Kalender-CSS fehlt im geladenen Stylesheet.")

    import json
    seite = (SEITE.replace("__WOCHEN__", wochen).replace("__KAL__", kal)
             .replace("__CSS__", json.dumps(css)).replace("__KAPUTT__", json.dumps(KAPUTT))
             .replace("__KAPUTT_AN__", "true" if gegenprobe else "false"))

    tmp = tempfile.mkdtemp(prefix="kal-layout-")
    hpfad = os.path.join(tmp, "probe.html")
    with open(hpfad, "w", encoding="utf-8") as f:
        f.write(seite)

    url = "file:///" + hpfad.replace("\\", "/")
    dump = os.path.join(tmp, "dump.html")
    with open(dump, "w", encoding="utf-8") as f:
        subprocess.run([EDGE, "--headless=new", "--disable-gpu",
                        "--virtual-time-budget=12000",
                        "--user-data-dir=" + os.path.join(tmp, "prof"),
                        "--dump-dom", url],
                       stdout=f, stderr=subprocess.DEVNULL, timeout=180)
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
    print("GEGENPROBE (table-layout: auto, 12 px Mindestbreite) - MUSS durchfallen" if gp
          else "Heutige Fassung - diese Fassung muss gruen sein")
    print("=" * 66)
    n = lauf(gp)
    print("=" * 66)
    if gp:
        print("Gegenprobe bestanden." if n > 0 else
              "GEGENPROBE GESCHEITERT: Auch die kaputte Fassung ist gruen - der Test misst nichts.")
        sys.exit(0 if n > 0 else 1)
    sys.exit(0 if n == 0 else 1)
