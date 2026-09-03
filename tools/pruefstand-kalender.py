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

# Die verstellte Fassung fuer die zweite Gegenprobe: das Tagesbit wird ueber den
# MONATSTAG gegriffen statt ueber den Wochentag. Genau dieser Off-by-one ist im
# Monatsgitter der naheliegende Fehler - beides sind kleine ganze Zahlen, und das
# Ergebnis sieht noch immer wie ein plausibel gefuellter Kalender aus.
#
# Sie laesst die Zeilen 1-10 (Jahresband und Tages-Serie) BEWUSST gruen: die benutzen
# kalTagStatus() gar nicht. Dass nur die Monatszeilen umkippen, ist der Beweis, dass
# diese Zeilen tatsaechlich das Monatsgitter messen und nicht bloss mitlaufen.
NAIV_MONAT = """  function kalTagStatus(d) {
    const info = kalWoche(isoWeekKey(d));
    if (!info) return null;
    if (info.mask === null) return "unk";
    return info.mask.charAt(d.getDate() - 1) === "1" ? "on" : "off";
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
// kalMode: "jahr" - die Zeilen unten messen das JAHRESBAND. Die Monatsansicht ist der
// Standard der App und bekommt eigene Zeilen (offen, siehe plans/).
var state = { plans: {}, weekStats: {}, weights: [], weightGoals: {}, viewYear: null, kalMode: "jahr", kalMonth: 0, goal: { kcal: 2000 } };
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
// Zahlformat wie im Kern (Math.round + de-DE). Der Kartenfuss des Kalenders nutzt es seit
// dem 03.09.2026 fuer seine Kennzahlen; ohne die Attrappe bricht kalenderHtml() ab.
function nfmt(n){ return Math.round(n).toLocaleString("de-DE"); }
// Der Fuss zeigt die Ziel-Quote nur, wenn es archivierte Wochen MIT damaligem Ziel gibt -
// echte Funktion, hier nicht gestubbt: sie liest dieselbe Quelle wie das Gitter.
var J_VOR = new Date().getFullYear() - 1;
// Die drei Icons stehen in data/ikonen.js, nicht im ausgeschnittenen Block. Als
// Attrappe genuegt ein erkennbarer Platzhalter - geprueft werden Zustaende und
// Aufbau des Gitters, nicht die Pfaddaten eines SVG.
// EINFACHE Anfuehrungszeichen: SEITE ist ein normaler Python-String, kein Raw-String -
// ein \" darin loest Python zu " auf und zerlegt den JS-Block, ohne dass es auffaellt
// (die Seite bleibt stumm, weil melde() dann gar nicht erst existiert).
var ICON_CHECK = '<svg class="i-check"></svg>';
var ICON_CHEV_L = '<svg class="i-chevl"></svg>';
var ICON_CHEV_R = '<svg class="i-chevr"></svg>';
// Die Flamme der Wochenserie - seit dem 03.09.2026 im Kartenfuss statt im Rueckblick.
var ICON_FLAME = '<svg class="i-flame"></svg>';
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
melde("1. Die laufende Woche steht in der Jahresansicht (sie ist NICHT im Archiv)");
var curWk = wkVon(heute), curIdx = idxVon(heute);
state.plans = {}; state.plans[curWk] = planMit([curIdx]);
state.weekStats = {};
var html = kalenderHtml();
// Seit dem 30.08.2026 tragen beide Ansichten dieselbe Zellklasse (.kal-t); das Band mit
// seiner eigenen Klasse .kal-c ist entfallen.
var geplanteZellen = (html.match(/class="kal-t on/g) || []).length;
pruefe("genau eine geplante Zelle", geplanteZellen === 1, geplanteZellen + " gefunden");
// Gezaehlt werden TAGE, nicht mehr Wochen: eine Zelle ist ein Tag, und zwei Einheiten
// fuer dieselbe Karte waeren nur verwirrend.
pruefe("Klartextzeile zaehlt sie mit", /1 von \\d+ Tagen geplant/.test(html),
       (html.match(/\\d+ von \\d+ Tagen geplant[^<]*/) || ["-"])[0]);
pruefe("heutige Zelle ist markiert", (html.match(/kal-t on today/g) || []).length === 1);
pruefe("aria-current gesetzt", (html.match(/aria-current="date"/g) || []).length === 1);

melde("");
melde("2. Woche mit Datensatz, aber ohne Maske: eigener Zustand statt sieben Nullen");
state.plans = {};
state.weekStats = {}; state.weekStats[wkVon(tagVor(21))] = { kcal: 1900, days: 5, hit: 3 };
html = kalenderHtml();
pruefe("sieben eigene Zellen fuer die Woche ohne Maske", (html.match(/class="kal-t unk/g) || []).length === 7,
       (html.match(/class="kal-t unk/g) || []).length + " gefunden");
pruefe("keine als 'nichts geplant' behauptete Zelle in dieser Woche",
       (html.match(/class="kal-t on/g) || []).length === 0);
// Eine Woche OHNE Maske traegt keine geplanten TAGE - die neue Zaehlung kann sie deshalb
// nicht mitzaehlen. Was bleibt: Die sieben Zellen stehen als eigener Zustand da (oben
// geprueft) statt als sieben Behauptungen "nichts geplant".
pruefe("kein Tag wird daraus erfunden", /0 von \\d+ Tagen geplant/.test(html) || /noch kein geplanter Tag/.test(html),
       (html.match(/\\d+ von \\d+ Tagen geplant[^<]*/) || ["-"])[0]);

melde("");
melde("3. Die Jahresansicht besteht aus zwoelf Monatsgittern");
// Frueher stand hier die Spaltenzahl des Bandes (52 oder 53, ueber isoWochenImJahr).
// Beides ist mit dem Band entfallen. Was an seine Stelle tritt, ist die Zusicherung, die
// den neuen Aufbau traegt: zwoelf vollstaendige Monate, kein Monat doppelt, keiner fehlt.
state.plans = {}; state.weekStats = {};
html = kalenderHtml();
var tabellen = (html.match(/<table class="kal-grid mini"/g) || []).length;
pruefe("zwoelf Tabellen", tabellen === 12, tabellen + " gefunden");
var caps = (html.match(/<caption class="kal-cap">/g) || []).length;
pruefe("jede traegt ihren Monatsnamen sichtbar", caps === 12, caps + " Beschriftungen");
// Die Tagesmenge ist die eigentliche Vollstaendigkeitsprobe: 365 bzw. 366 echte Zellen.
// Gezaehlt wird ueber data-d, nicht ueber die Klasse: Fuellzellen tragen dieselbe Klasse,
// aber kein Datum - ueber die Klasse kaeme man auf gut 440.
var tage = (html.match(/<td class="kal-t[^"]*" data-d=/g) || []).length;
var sollTage = ((+JAHR % 4 === 0 && +JAHR % 100 !== 0) || +JAHR % 400 === 0) ? 366 : 365;
pruefe("alle Tage des Jahres sind da (" + sollTage + ")", tage === sollTage, tage + " Zellen");
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
melde("7. Ohne jede Planung ist die Serie 0 und das Jahr leer");
state.plans = {}; state.weekStats = {};
pruefe("Serie = 0", dayStreak() === 0, "gezaehlt: " + dayStreak());
html = kalenderHtml();
pruefe("keine geplante Zelle", html.indexOf('class="kal-t on') < 0);
pruefe("ehrlicher Leerzustand", html.indexOf("noch kein geplanter Tag") > -1);

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
melde("9. Die Jahresansicht ist mit der Tastatur bedienbar");
// 371 Tabstopps waeren das Gegenteil von barrierefrei gewesen: Wer die Karte nur
// ueberspringen will, drueckte 371-mal Tab. Zwoelf sind etwas anderes - einer je Monat,
// mit dem man gezielt hineinspringt. Innerhalb eines Gitters bewegen die Pfeiltasten.
state.plans = {}; state.weekStats = {};
state.plans[curWk] = planMit([curIdx]);
view.innerHTML = kalenderHtml();
initKalender();
var zellen = view.querySelectorAll("td.kal-t");
var einstiege = view.querySelectorAll('td.kal-t[tabindex="0"]');
pruefe("genau ein Tabstopp JE MONAT (zwoelf)", einstiege.length === 12,
       einstiege.length + " Zellen mit tabindex 0 bei " + zellen.length + " Zellen");
// Im laufenden Monat muss der Einstieg auf HEUTE liegen, in den uebrigen auf der ersten
// belegten Zelle - sonst waere ein Monat ohne "heute" per Tastatur gar nicht erreichbar.
var heuteEinstieg = view.querySelectorAll('td.kal-t.today[tabindex="0"]');
pruefe("im laufenden Monat ist der Einstieg HEUTE", heuteEinstieg.length === 1,
       heuteEinstieg.length + " gefunden");
pruefe("jedes Gitter hat genau einen", (function(){
  var tabs = view.querySelectorAll("table.kal-grid"), ok = true;
  for (var i = 0; i < tabs.length; i++) {
    if (tabs[i].querySelectorAll('td.kal-t[tabindex="0"]').length !== 1) ok = false;
  }
  return tabs.length === 12 && ok;
})(), "Gitter: " + view.querySelectorAll("table.kal-grid").length);

// Pfeiltasten. Geprueft wird im MAERZ-Gitter (Index 2) und dort in der zweiten Woche:
// Der Start ist bewusst eine feste, von Fuellzellen freie Zelle und NICHT "heute". Faellt
// heute auf einen Sonntag, ist das die letzte Spalte - dann geht ArrowRight zu Recht
// nicht, und der Test misst den Wochentag statt die Bedienung. Genau darauf ist die erste
// Fassung am 30.08. (einem Sonntag) hereingefallen.
//
// Seit dem Umbau bewegen sich die Pfeile im MONATSGITTER: rechts ist ein Tag weiter,
// unten eine Woche tiefer. Im Band war es umgekehrt - eine Spalte war eine Woche.
var gitter = view.querySelectorAll("table.kal-grid")[2];
var koerper = gitter.querySelector("tbody");
function tasteAuf(el, k){ el.focus(); el.dispatchEvent(new KeyboardEvent("keydown", { key: k, bubbles: true })); }
function aktiv(){ return view.ownerDocument.activeElement; }

// Zeile 1 ist im Maerz garantiert voll (der Monat beginnt spaetestens in Zeile 0).
var mitte = koerper.rows[1].cells[3];
tasteAuf(mitte, "ArrowRight");
pruefe("ArrowRight geht einen TAG weiter", aktiv().cellIndex === 4 && aktiv().parentElement.sectionRowIndex === 1,
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
tasteAuf(koerper.rows[1].cells[3], "ArrowDown");
pruefe("ArrowDown geht eine WOCHE tiefer", aktiv().parentElement.sectionRowIndex === 2 && aktiv().cellIndex === 3,
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
// ArrowUp bewusst aus Zeile 2, nicht aus Zeile 1: Beginnt der Monat spaet in der Woche
// (der 1. Maerz 2026 ist ein Sonntag), besteht Zeile 0 fast nur aus Fuellzellen - der
// Fokus bliebe dann voellig zu Recht stehen, und der Test maesse den Kalender statt die
// Bedienung. Zeile 1 und 2 sind in jedem Monat voll.
tasteAuf(koerper.rows[2].cells[3], "ArrowUp");
pruefe("ArrowUp geht eine Woche zurueck", aktiv().parentElement.sectionRowIndex === 1,
       "gelandet in Zeile " + aktiv().parentElement.sectionRowIndex);
tasteAuf(koerper.rows[1].cells[3], "Home");
// Spalte 0 ist im Monatsgitter bereits ein Tag - im Band stand dort der Zeilenkopf.
pruefe("Home springt an den Wochenanfang", aktiv().cellIndex === 0, "Spalte " + aktiv().cellIndex);
tasteAuf(koerper.rows[1].cells[3], "End");
pruefe("End springt ans Wochenende", aktiv().cellIndex === koerper.rows[1].cells.length - 1);

// Der Tabstopp wandert INNERHALB seines Gitters - die anderen elf behalten ihren.
pruefe("der Tabstopp wandert mit, aber nur im eigenen Gitter",
       gitter.querySelectorAll('td.kal-t[tabindex="0"]').length === 1 &&
       gitter.querySelector('td.kal-t[tabindex="0"]') === aktiv() &&
       view.querySelectorAll('td.kal-t[tabindex="0"]').length === 12,
       "im Gitter: " + gitter.querySelectorAll('td.kal-t[tabindex="0"]').length +
       ", gesamt: " + view.querySelectorAll('td.kal-t[tabindex="0"]').length);

// Der Tipp muss auf den FOKUS antworten - sonst gaebe es einen Weg hinein, aber keine
// Antwort darin. Vorher leeren, sonst misst die Zeile den Rest eines Mausereignisses.
view.querySelector(".kal-tip").textContent = "";
var zielZelle = koerper.rows[2].cells[2];
zielZelle.focus();
// ⚠️ In einem headless-Fenster hat das Dokument nicht immer den Systemfokus. focus()
// setzt dann zwar activeElement, loest aber KEIN focus-Ereignis aus - der Test war
// dadurch mal gruen und mal rot, ohne dass sich etwas geaendert haette. Geprueft wird,
// dass der Handler am Element haengt und den Tipp schreibt; das Ereignis notfalls selbst
// ausloesen ist deshalb keine Schoenfaerberei, sondern der Ersatz fuer einen Fokus, den
// die Umgebung nicht vergibt.
if (!view.querySelector(".kal-tip").textContent) zielZelle.dispatchEvent(new FocusEvent("focus"));
// Der Tipp nennt jetzt ein DATUM, keine Kalenderwoche - die Zelle ist ein Tag.
pruefe("der Tipp folgt dem Fokus", /\w+, \d{2}\.\d{2}\.\d{4} · /.test(view.querySelector(".kal-tip").textContent),
       "'" + view.querySelector(".kal-tip").textContent + "'");

// An den Raendern darf nichts passieren - und vor allem nichts abstuerzen. Gemessen wird
// in der LETZTEN Zeile: dort stehen die Fuellzellen am Monatsende, und genau ueber sie
// darf der Fokus nicht hinauslaufen.
var letzte = koerper.rows[koerper.rows.length - 1];
var linksZelle = koerper.rows[1].cells[0];
tasteAuf(linksZelle, "ArrowLeft");
pruefe("am linken Rand bleibt der Fokus stehen", aktiv() === linksZelle);
tasteAuf(koerper.rows[0].cells[6], "ArrowUp");
pruefe("in der obersten Zeile bleibt er ebenfalls", aktiv() === koerper.rows[0].cells[6]);
var rechtsZelle = koerper.rows[1].cells[6];
tasteAuf(rechtsZelle, "ArrowRight");
pruefe("am rechten Rand bleibt der Fokus stehen", aktiv() === rechtsZelle);
// Fuellzellen sind kein Ziel: Wer am Monatsende nach unten geht, bleibt stehen.
var letzteEchte = null;
for (var li = letzte.cells.length - 1; li >= 0; li--) {
  if (!letzte.cells[li].classList.contains("pad")) { letzteEchte = letzte.cells[li]; break; }
}
if (letzteEchte) {
  tasteAuf(letzteEchte, "ArrowDown");
  pruefe("unter der letzten Zeile bleibt er stehen", aktiv() === letzteEchte,
         "gelandet auf: " + (aktiv().className || "-"));
}

melde("");
melde("10. Ein Jahr ohne heutigen Tag bleibt erreichbar");
// Im Vorjahr traegt keine Zelle "today" - ohne Nachbesserung haette die Ansicht dort gar
// keinen Tabstopp und waere per Tastatur unerreichbar. Jedes der zwoelf Gitter braucht
// seinen eigenen: haetten nur die Monate mit Daten einen, waeren leere Monate stumm.
state.viewYear = J_VOR;
view.innerHTML = kalenderHtml();
var e2 = view.querySelectorAll('td.kal-t[tabindex="0"]');
pruefe("auch dort einer je Monat", e2.length === 12, e2.length + " gefunden");
// Der Hinweis auf die Pfeiltasten muss ANGESAGT werden - wer die Tabelle nicht sieht,
// weiss sonst nicht, dass sie eine eigene Navigation hat (Befund des kvp-Agenten).
pruefe("die Tabelle verweist auf ihren Bedienhinweis",
       view.querySelector(".kal-grid").getAttribute("aria-describedby") === "kal-hilfe" &&
       !!view.querySelector("#kal-hilfe"),
       view.querySelector(".kal-grid").getAttribute("aria-describedby"));
state.viewYear = heute.getFullYear();

melde("");
melde("11. Monatsgitter: der geplante Tag steht auf seinem WOCHENTAG");
// Der Off-by-one, gegen den --gegenprobe-monat laeuft: das Bit gehoert an
// (getDay()||7)-1, NICHT an den Monatstag. Beides ist eine kleine ganze Zahl, und eine
// Verwechslung sieht im fertigen Gitter noch immer wie ein plausibler Kalender aus.
state.kalMode = "monat";
state.kalMonth = heute.getMonth();
state.viewYear = heute.getFullYear();
state.plans = {}; state.plans[curWk] = planMit([curIdx]);
state.weekStats = {};
view.innerHTML = kalenderHtml();
var heuteIso = JAHR + "-" + String(heute.getMonth() + 1).padStart(2, "0") + "-" + String(heute.getDate()).padStart(2, "0");
var onM = view.querySelectorAll("td.kal-t.on");
pruefe("genau ein geplanter Tag im Monat", onM.length === 1, onM.length + " gefunden");
pruefe("und zwar HEUTE", onM.length === 1 && onM[0].getAttribute("data-d") === heuteIso,
       onM.length ? onM[0].getAttribute("data-d") + " statt " + heuteIso : "-");
pruefe("er steht in der Spalte seines Wochentags", onM.length === 1 && onM[0].cellIndex === curIdx,
       onM.length ? "Spalte " + onM[0].cellIndex + ", erwartet " + curIdx : "-");
pruefe("heute ist markiert", view.querySelectorAll("td.kal-t.today").length === 1);
pruefe("die Klartextzeile zaehlt den Tag mit", /1 von \d+ Tagen geplant/.test(view.innerHTML),
       (view.innerHTML.match(/\d+ von \d+ Tagen geplant/) || ["-"])[0]);

melde("");
melde("12. Der Monat hat so viele Tageszellen, wie er Tage hat");
var tageImMonat = new Date(heute.getFullYear(), heute.getMonth() + 1, 0).getDate();
var tagZellen = view.querySelectorAll("td.kal-t:not(.pad)");
pruefe("Zahl der Tageszellen stimmt", tagZellen.length === tageImMonat,
       tagZellen.length + " statt " + tageImMonat);
var ersterIdx = (new Date(heute.getFullYear(), heute.getMonth(), 1).getDay() || 7) - 1;
var koerperM = view.querySelector(".kal-grid.monat tbody");
var padVorn = 0;
while (padVorn < 7 && koerperM.rows[0].cells[padVorn].classList.contains("pad")) padVorn++;
pruefe("Fuellzellen vor dem Monatsersten", padVorn === ersterIdx, padVorn + " statt " + ersterIdx);
var alleSieben = true;
for (var r = 0; r < koerperM.rows.length; r++) if (koerperM.rows[r].cells.length !== 7) alleSieben = false;
pruefe("jede Zeile hat sieben Spalten", alleSieben);
pruefe("die erste Tageszelle traegt die 1",
       koerperM.rows[0].cells[padVorn].querySelector(".kal-num").textContent === "1");
// Fuellzellen duerfen keinen Zustand behaupten: ein leerer Kreis waere die Aussage
// "nichts geplant" ueber einen Tag, den es in diesem Monat gar nicht gibt.
var padMitZustand = view.querySelectorAll("td.kal-t.pad.on, td.kal-t.pad.off, td.kal-t.pad.unk");
pruefe("keine Fuellzelle traegt einen Zustand", padMitZustand.length === 0, padMitZustand.length + " gefunden");

melde("");
melde("13. Auch im Monat: Woche ohne Maske wird nicht als 'nichts geplant' gezeichnet");
state.plans = {};
state.weekStats = {}; state.weekStats[curWk] = { kcal: 1900, days: 5, hit: 3 };
view.innerHTML = kalenderHtml();
pruefe("keine Zelle behauptet 'geplant'", view.querySelectorAll("td.kal-t.on").length === 0,
       view.querySelectorAll("td.kal-t.on").length + " gefunden");
var unkM = view.querySelectorAll("td.kal-t.unk").length;
// Wie viele der sieben Tage im Monat liegen, haengt vom Datum ab - deshalb eine Spanne
// statt einer festen Sieben. Null waere der Fehler: dann waere die Woche verschwunden.
pruefe("die Woche ohne Maske ist sichtbar", unkM > 0 && unkM <= 7, unkM + " Zellen");

melde("");
melde("14. Ansichtswahl und Monatsnavigation");
state.plans = {}; state.weekStats = {};
view.innerHTML = kalenderHtml();
// Ohne jede Planung darf der Monat keine stumme Flaeche sein: die Tageszahlen stehen
// weiter da (es ist ein Kalender), und die Klartextzeile sagt, dass noch nichts geplant
// ist. Ein leeres Gitter ohne Satz waere ein Zustand ohne Aussage.
pruefe("der leere Monat traegt trotzdem alle Tageszahlen",
       view.querySelectorAll("td.kal-t:not(.pad)").length ===
       new Date(heute.getFullYear(), heute.getMonth() + 1, 0).getDate());
pruefe("und sagt, dass noch nichts geplant ist",
       /kein geplanter Tag/.test(view.querySelector(".kal-note").textContent),
       view.querySelector(".kal-note").textContent);
// ⚠️ Seit dem 03.09.2026 traegt die KARTE keine Zeitraumwahl mehr - sie steht einmal
// ueber allen Karten (zeitraumHtml) und regiert auch die Gewichtskarte. Geprueft wird
// beides getrennt: die Huelle hier, das Gitter darunter.
view.innerHTML = zeitraumHtml() + kalenderHtml();
pruefe("Monat ist die aktive Ansicht",
       view.querySelector('[data-mode="monat"]').classList.contains("active") &&
       !view.querySelector('[data-mode="jahr"]').classList.contains("active"));
pruefe("die Zeitraumwahl steht GENAU EINMAL",
       view.querySelectorAll(".week-switch").length === 1,
       view.querySelectorAll(".week-switch").length + " Umschalter");
// Die alte Jahresleiste (data-action="wyear") gibt es nicht mehr - im Monat wie im Jahr
// traegt dieselbe Navigation den Zeitraum, nur mit anderer Schrittweite.
pruefe("keine getrennte Jahresleiste mehr", !view.querySelector('[data-action="wyear"]'));
pruefe("die Navigation nennt Monat und Jahr",
       view.querySelector(".kal-nm").textContent.indexOf(String(heute.getFullYear())) > -1,
       view.querySelector(".kal-nm").textContent);
var ys = weightYears();
state.viewYear = +ys[0]; state.kalMonth = 0;
view.innerHTML = zeitraumHtml() + kalenderHtml();
var pf = view.querySelectorAll(".kal-nb");
pruefe("am Anfang des Archivs ist der Rueckwaertspfeil gesperrt", pf[0].disabled && !pf[1].disabled);
state.viewYear = +ys[ys.length - 1]; state.kalMonth = 11;
view.innerHTML = zeitraumHtml() + kalenderHtml();
pf = view.querySelectorAll(".kal-nb");
pruefe("am Ende ist es der Vorwaertspfeil", pf[1].disabled && !pf[0].disabled);
state.kalMode = "jahr";
state.viewYear = heute.getFullYear();
view.innerHTML = zeitraumHtml() + kalenderHtml();
// Im Jahr blaettert derselbe Pfeil JAHRESWEISE - die Zeile nennt dann nur die Jahreszahl.
pruefe("im Jahr nennt die Zeile nur das Jahr",
       view.querySelector(".kal-nm").textContent.trim() === String(heute.getFullYear()),
       view.querySelector(".kal-nm").textContent);
pruefe("und zeichnet zwoelf Monatsgitter",
       view.querySelectorAll("table.kal-grid.mini").length === 12 &&
       !view.querySelector("table.kal-grid.monat"),
       view.querySelectorAll("table.kal-grid.mini").length + " Mini-Gitter");

melde("");
melde("14b. Der Kartenfuss traegt die Kennzahlen des Zeitraums");
// Sie standen bis zum 03.09.2026 im Rueckblick ueber dem Kalender - dieselben Zahlen
// ueber demselben Bestand, nur eine Karte hoeher und mit eigenem Diagramm daneben.
state.kalMode = "monat"; state.kalMonth = heute.getMonth();
state.viewYear = heute.getFullYear();
state.plans = {}; state.plans[curWk] = planMit([curIdx]);
state.weekStats = {};
view.innerHTML = kalenderHtml();
var fuss = view.querySelector(".kal-foot");
pruefe("der Fuss ist da", !!fuss);
pruefe("er nennt die geplanten Tage", /Geplant/.test(fuss.textContent) && /1/.test(fuss.textContent),
       fuss.textContent.replace(/\s+/g, " ").trim());
// Ohne archivierte Woche MIT damaligem Ziel gibt es keine Quote - dann darf sie auch
// nicht dastehen. Eine erfundene Null waere schlimmer als eine fehlende Zahl (B10).
pruefe("ohne Zieldaten keine Ziel-Quote", fuss.textContent.indexOf("Im Ziel") < 0,
       fuss.textContent.replace(/\s+/g, " ").trim());
state.weekStats[wkVon(tagVor(7))] = { kcal: 1900, days: 6, hit: 4, target: 1950, d: "1111110" };
state.weekStats[wkVon(tagVor(14))] = { kcal: 1880, days: 5, hit: 3, target: 1950, d: "1111100" };
// ⚠ Geprueft wird im JAHR, nicht im Monat: Eine Woche wird ueber ihren DONNERSTAG einem
// Monat zugeordnet (ISO), und die beiden Wochen oben liegen je nach heutigem Datum im
// Vormonat. Im Monat waere die Zeile dann zu Recht leer - der Test haenge am Kalender
// statt an der Sache. Im Jahr zaehlen alle Wochen des Jahrgangs.
state.kalMode = "jahr";
view.innerHTML = kalenderHtml();
fuss = view.querySelector(".kal-foot");
pruefe("mit Zieldaten steht sie da", /Im Ziel/.test(fuss.textContent),
       fuss.textContent.replace(/\s+/g, " ").trim());
// Die Quote misst gegen die geplanten Tage DERSELBEN Wochen (4+3 Treffer von 6+5 Tagen),
// nicht gegen die Tage des Zeitraums - sonst waeren zwei Bezugsgroessen vermischt.
pruefe("sie zaehlt Treffer gegen geplante Tage", /7\D+11/.test(fuss.textContent),
       fuss.textContent.replace(/\s+/g, " ").trim());
state.kalMode = "monat";

melde("");
melde("15. Tastatur im Monatsgitter: Fuellzellen werden uebersprungen");
state.kalMode = "monat"; state.kalMonth = heute.getMonth();
view.innerHTML = kalenderHtml();
initKalender();
var e3 = view.querySelectorAll('td.kal-t[tabindex="0"]');
pruefe("genau ein Tabstopp im Monat", e3.length === 1, e3.length + " gefunden");
pruefe("der Einstieg ist HEUTE", e3.length === 1 && e3[0].getAttribute("data-d") === heuteIso,
       e3.length ? e3[0].getAttribute("data-d") : "-");
koerperM = view.querySelector(".kal-grid.monat tbody");
var ersteEchte = koerperM.rows[0].querySelector("td.kal-t:not(.pad)");
if (ersteEchte.cellIndex > 0) {
  // Links vom Monatsersten stehen nur Fuellzellen. Der Fokus muss stehen bleiben, statt
  // in einer leeren Zelle zu landen, aus der die Tipp-Zeile nichts zu sagen haette.
  tasteAuf(ersteEchte, "ArrowLeft");
  pruefe("links vom Monatsersten bleibt der Fokus stehen", aktiv() === ersteEchte,
         "Spalte " + aktiv().cellIndex);
  tasteAuf(ersteEchte, "Home");
  pruefe("Home laeuft ueber die Fuellzellen hinweg auf den Ersten", aktiv() === ersteEchte,
         "Spalte " + aktiv().cellIndex);
} else {
  pruefe("links vom Monatsersten bleibt der Fokus stehen (Monat beginnt am Montag)", true);
  pruefe("Home laeuft ueber die Fuellzellen hinweg auf den Ersten (entfaellt)", true);
}
var zweiteZeile = koerperM.rows[1].cells[0];
tasteAuf(zweiteZeile, "ArrowUp");
// Senkrecht gibt es kein Weiterlaufen: ueber dem ersten Montag steht eine Fuellzelle,
// dort ist der Rand. Beginnt der Monat am Montag, ist die Zelle darueber der 1.
pruefe("senkrecht ist die Fuellzelle der Rand",
       aktiv() === zweiteZeile || aktiv() === koerperM.rows[0].cells[0],
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
tasteAuf(koerperM.rows[1].cells[2], "ArrowRight");
pruefe("waagerecht bewegt sich der Fokus normal",
       aktiv().cellIndex === 3 && aktiv().parentElement.sectionRowIndex === 1,
       "Zeile " + aktiv().parentElement.sectionRowIndex + ", Spalte " + aktiv().cellIndex);
view.querySelector("td.kal-t:not(.pad)").dispatchEvent(new MouseEvent("click", { bubbles: true }));
pruefe("der Tipp nennt Datum und Zustand",
       /\d{2}\.\d{2}\.\d{4} . (geplant|nichts geplant|keine Daten|Tage nicht aufgezeichnet)/.test(view.querySelector(".kal-tip").textContent),
       view.querySelector(".kal-tip").textContent || "(leer)");

melde("");
melde(fehler === 0 ? "ERGEBNIS: alle Pruefungen gruen."
                   : "ERGEBNIS: " + fehler + " Pruefung(en) ROT.");
melde("FEHLERZAHL=" + fehler);
}
</script>"""


def lauf(gegenprobe=None):
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

    if gegenprobe == "kalwoche":
        neu, n = re.subn(r"  function kalWoche\(wk\) \{.*?\n  \}\n", NAIV, kal, count=1, flags=re.S)
        if n != 1:
            raise SystemExit("ABBRUCH: kalWoche() nicht ersetzbar - Gegenprobe misst nichts.")
        kal = neu
    elif gegenprobe == "monat":
        neu, n = re.subn(r"  function kalTagStatus\(d\) \{.*?\n  \}\n", NAIV_MONAT, kal, count=1, flags=re.S)
        if n != 1:
            raise SystemExit("ABBRUCH: kalTagStatus() nicht ersetzbar - Gegenprobe misst nichts.")
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
    # Zwei Gegenproben, weil zwei getrennte Aussagen zu sichern sind: --gegenprobe
    # verstellt die gemeinsame Quelle (kalWoche) und muss Band UND Monat umwerfen,
    # --gegenprobe-monat verstellt nur die Tageslesart und darf ausschliesslich die
    # Monatszeilen treffen.
    if "--gegenprobe-monat" in sys.argv:
        gp = "monat"
        kopf = "GEGENPROBE (kalTagStatus liest den Monatstag) - die MONATSZEILEN muessen durchfallen"
    elif "--gegenprobe" in sys.argv:
        gp = "kalwoche"
        kopf = "GEGENPROBE (kalWoche naiv) - diese Fassung MUSS durchfallen"
    else:
        gp = None
        kopf = "Heutige Fassung - diese Fassung muss gruen sein"
    print(kopf)
    print("=" * 66)
    n = lauf(gp)
    print("=" * 66)
    if gp:
        print("Gegenprobe bestanden." if n > 0 else
              "GEGENPROBE GESCHEITERT: Die verstellte Fassung ist gruen - der Test misst nichts.")
        sys.exit(0 if n > 0 else 1)
    sys.exit(0 if n == 0 else 1)
