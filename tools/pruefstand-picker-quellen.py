# -*- coding: utf-8 -*-
u"""
Pruefstand Picker-Quellen: bietet die Meal-Auswahl eines Slots NUR eigene Meals an?

ANLASS (12.09.2026): Vom 17.08. bis zum 12.09.2026 stand im Meal-Waehler zusaetzlich das
ganze Rezeptbuch, damit Handauswahl und Auto-Planer dieselbe Menge sehen. Am Geraet standen
im Fruehstuecks-Slot vier eigene Meals gegen zehn Katalog-Rezepte - wer seinen eigenen
Bestand durchsehen wollte, scrollte durch fremde Gerichte. Seither schoepft pickerQuellen()
nur noch aus libraryRecipes().

WAS ER PRUEFT - am ECHTEN, ausgeschnittenen Code:
  * pickerQuellen() liefert die eigenen Meals
  * KEIN Katalog-Rezept ist dabei, auch nicht als flache Kopie (__cb)
  * Barcode-/Schnelleintrag-Meals (quick) bleiben weiterhin draussen - sie sind fuer EINEN
    Tag gedacht und wuerden die Liste mit jedem gescannten Riegel verlaengern
  * ohne eigene Meals ist die Liste leer, nicht "leer bis auf 34 Katalogrezepte" - daran
    haengt der Leerzustand samt Weg zu den Meals

Dazu eine QUELLTEXT-Pruefung: openPicker() darf den Abschnitt "Aus dem Rezeptbuch" nicht
mehr bauen, und pickerQuellen() den Katalog nicht mehr befragen. Ohne sie koennte der
Abschnitt an anderer Stelle wieder auftauchen, waehrend die Messung oben gruen bleibt.

Aufrufe:
    python tools/pruefstand-picker-quellen.py
    python tools/pruefstand-picker-quellen.py alt/index.html   # Gegenprobe gegen alten Stand
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(text, name):
    m = re.search(r"\n\s*function\s+" + re.escape(name) + r"\s*\(", text)
    if not m:
        return None
    i = text.index("{", m.start())
    tiefe, j = 0, i
    while j < len(text):
        if text[j] == "{":
            tiefe += 1
        elif text[j] == "}":
            tiefe -= 1
            if tiefe == 0:
                return text[m.start():j + 1]
        j += 1
    return None


def ohne_kommentare(code):
    u"""Kommentare raus, bevor im Code gesucht wird. Der Kommentar ueber pickerQuellen()
    nennt das Rezeptbuch und cookbookVisible() beim Namen - eine reine Textsuche fände sie
    dort und meldete rot bzw. gruen, ohne den Code gesehen zu haben."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    return re.sub(r"//[^\n]*", " ", code)


FUNKTIONEN = ["libraryRecipes", "pickerQuellen"]

# Randstuecke: Der Katalog selbst ist nicht Pruefgegenstand. cookbookVisible() liefert hier
# zwei erkennbare Marker-Rezepte - taucht eines davon in der Auswahl auf, ist der Katalog
# wieder drin.
STUBS = u"""
  var state = { recipes: [] };
  function cookbookVisible() {
    return [{ id: "kat-1", name: "Katalogrezept A" }, { id: "kat-2", name: "Katalogrezept B" }];
  }
  function isAdopted(id) { return false; }
"""

PRUEFUNGEN = u"""
  state.recipes = [
    { id: "e1", name: "Chili con Carne" },
    { id: "e2", name: "Shake" },
    { id: "q1", name: "Banane", quick: true, qf: "banane" }
  ];
  var liste = pickerQuellen();
  var namen = liste.map(function (r) { return r.name; });

  pruef("eigene Meals sind dabei", namen.indexOf("Chili con Carne") > -1, true);
  pruef("zwei eigene Meals",       liste.length, 2);
  pruef("kein Katalogrezept A",    namen.indexOf("Katalogrezept A"), -1);
  pruef("kein Katalogrezept B",    namen.indexOf("Katalogrezept B"), -1);
  pruef("keine Katalog-Kopie",     liste.filter(function (r) { return r.__cb; }).length, 0);
  pruef("keine Katalog-id",        liste.filter(function (r) { return String(r.id).indexOf("kat-") === 0; }).length, 0);
  pruef("Schnelleintrag bleibt draussen", namen.indexOf("Banane"), -1);

  state.recipes = [];
  pruef("ohne eigene Meals ist die Auswahl leer", pickerQuellen().length, 0);
"""

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Picker-Quellen</title>
<pre id="raus">laeuft</pre>
<script>
%(stubs)s
%(code)s
var ergebnisse = [];
function pruef(was, ist, soll) {
  ergebnisse.push({ was: was, ok: ist === soll, ist: String(ist), soll: String(soll) });
}
try {
%(pruefungen)s
} catch (e) {
  ergebnisse.push({ was: "Ausnahme: " + e.message, ok: false, ist: "-", soll: "-" });
}
document.getElementById("raus").textContent = JSON.stringify(ergebnisse);
</script>
"""


def bauen():
    quelle = io.open(INDEX, encoding="utf-8").read()
    teile, fehlend = [], []
    for name in FUNKTIONEN:
        s = schneide(quelle, name)
        (teile if s else fehlend).append(s or ("function " + name + "()"))
    html = SEITE % {"stubs": STUBS, "code": "\n".join(teile), "pruefungen": PRUEFUNGEN}
    return html, fehlend


def fahren(html):
    ordner = tempfile.mkdtemp(prefix="pickerq-")
    seite = os.path.join(ordner, "pruefstand.html")
    io.open(seite, "w", encoding="utf-8").write(html)
    profil = os.path.join(ordner, "edge")
    roh = subprocess.run(
        [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=4000",
         "--user-data-dir=" + profil, "--dump-dom", "file:///" + seite.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
    m = re.search(r'<pre id="raus">(.*?)</pre>', roh or "", re.S)
    if not m:
        return None
    text = m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    try:
        return json.loads(text)
    except ValueError:
        return None


def main():
    print("Pruefstand Picker-Quellen")
    print("Quelle: " + os.path.relpath(INDEX, BASIS).replace("\\", "/"))
    print("")

    html, fehlend = bauen()
    if fehlend:
        for f in fehlend:
            print("  FEHLT im Quelltext: " + f)
        print("")
        print("FEHLGESCHLAGEN: %d Baustein(e) nicht gefunden." % len(fehlend))
        return 1

    quelle = io.open(INDEX, encoding="utf-8").read()
    schief = []
    pq = ohne_kommentare(schneide(quelle, "pickerQuellen") or "")
    if "cookbookVisible(" in pq:
        schief.append("pickerQuellen(): fragt wieder den Katalog")
    op = ohne_kommentare(schneide(quelle, "openPicker") or "")
    if not op:
        schief.append("openPicker(): nicht gefunden")
    elif "Aus dem Rezeptbuch" in op:
        schief.append("openPicker(): baut wieder den Abschnitt 'Aus dem Rezeptbuch'")
    for e in schief:
        print("  FEHL  " + e)
    if not schief:
        print("  OK    Weder Quelle noch Ansicht holen das Rezeptbuch zurueck")

    ergebnisse = fahren(html)
    if not ergebnisse:
        print("FEHLGESCHLAGEN: kein Messergebnis - Edge hat nichts geliefert.")
        return 1

    rot = len(schief)
    for e in ergebnisse:
        if e["ok"]:
            print("  OK    " + e["was"])
        else:
            rot += 1
            print("  FEHL  %s  ist=%r soll=%r" % (e["was"], e["ist"], e["soll"]))
    print("")
    gesamt = len(ergebnisse) + 1
    if rot:
        print("FEHLGESCHLAGEN: %d von %d" % (rot, gesamt))
        return 1
    print("ERGEBNIS %d Pruefungen gruen" % gesamt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
