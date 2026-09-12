# -*- coding: utf-8 -*-
u"""
Pruefstand Meal-Symbol: zeigt ein Schnelleintrag SEIN Symbol statt eines geratenen Fotos?

ANLASS (12.09.2026): Die eingeplante Banane trug im Wochenplan die Obstschale aus
img/fruit.webp, das Ei ein Salatfoto - photoFor() raet fuer Schnelleintraege ueber
PHOTO_RULES ein Stichwortbild, und das geht bei einzelnen Lebensmitteln sichtbar daneben.
Seither entscheidet mealIcon(), ob eine Ansicht ein Symbol oder ein Foto zeigt.

WAS ER PRUEFT - am ECHTEN, ausgeschnittenen Code:
  * mealIcon() loest Banane, Ei und Brezel ueber FOOD_ICON auf (data/ikonen.js)
  * ein gescanntes Produkt (barcode, kein qf) bekommt das gemeinsame Packungssymbol
  * ein Schnelleintrag OHNE Zuordnung faellt auf "fruit" zurueck, statt leer zu bleiben
  * ein normales Meal bekommt weiterhin null - also sein Foto
  * das EIGENE Foto des Nutzers gewinnt auch am Schnelleintrag (wie in photoFor())
  * thumbHtml() gibt bei Symbol ein <span class="msym"> aus und KEIN <img>
  * jeder Wert in FOOD_ICON hat einen Pfad in ICONS - ein Tippfehler faellt sonst still
    auf das Fruchtsymbol zurueck

Dazu eine QUELLTEXT-Pruefung: alle vier Ansichten muessen die Weiche auch AUFRUFEN.
thumbHtml() deckt Plan, Picker und Vorkochliste ab, nextMealHtml() den Startreiter,
msPhotoInnerHtml() das Meal-Blatt. Ohne diese Pruefung koennte eine Ansicht still
zurueckfallen und wieder ein fremdes Gericht zeigen.

Aufrufe:
    python tools/pruefstand-meal-symbol.py
    python tools/pruefstand-meal-symbol.py alt/index.html   # Gegenprobe gegen alten Stand
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
IKONEN = os.path.join(BASIS, "data", "ikonen.js")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(text, name, art="function"):
    u"""Eine Deklaration im Wortlaut herausschneiden - ueber die Klammerbilanz. Fehlt sie,
    ist das ein BEFUND: ein Pruefstand, der eine fehlende Funktion uebergeht, misst nichts."""
    if art == "function":
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
    m = re.search(r"\n\s*const\s+" + re.escape(name) + r"\s*=\s*\{", text)
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
                return text[m.start():j + 2]
        j += 1
    return None


def ohne_kommentare(code):
    u"""Kommentare raus, bevor im Code gesucht wird - sonst bestaetigt sich der Pruefer
    an einem Kommentar selbst, der die gesuchte Funktion nur ERWAEHNT."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    return re.sub(r"//[^\n]*", " ", code)


FUNKTIONEN = ["iconSvg", "foodIcon", "istEigenesFoto", "mealIcon", "mealIconCoverHtml",
              "thumbHtml", "msPhotoInnerHtml", "bildHinweisHtml", "bildAlt"]

# Randstuecke, nicht Pruefgegenstand: photoFor() haengt an PHOTOS/PHOTO_RULES/CAT_PHOTO und
# ueber LIB_IMG am ganzen Rezeptbuch. Gemessen wird hier nur, OB ein Foto gewaehlt wird.
STUBS = u"""
  function photoFor(r) { return "FOTO.webp"; }
  function safeImage(v) { return typeof v === "string" && v.indexOf("data:image/") === 0 ? v : null; }
  // esc() kommt aus lib/pm.js (window.PM) und ist hier Randstueck - gemessen wird, WELCHE
  // Flaeche gebaut wird, nicht wie ein Name maskiert wird.
  function esc(v) { return String(v == null ? "" : v); }
"""

PRUEFUNGEN = u"""
  var banane   = { name: "Banane", quick: true, qf: "banane" };
  var ei       = { name: "Ei, Gr\\u00f6\\u00dfe M", quick: true, qf: "ei-m" };
  var brezel   = { name: "Laugenbrezel", quick: true, qf: "laugenbrezel" };
  var gescannt = { name: "Proteinriegel XY", quick: true, barcode: "4001234567890" };
  var unbekannt= { name: "Sternfrucht", quick: true, qf: "sternfrucht" };
  var normal   = { name: "Chili con Carne", category: "Hauptgericht" };
  var eigenes  = { name: "Banane", quick: true, qf: "banane", image: "data:image/jpeg;base64,AAAA" };

  pruef("Banane bekommt das Bananensymbol",  mealIcon(banane),   "banana");
  pruef("Ei bekommt das Eisymbol",           mealIcon(ei),       "egg");
  pruef("Brezel bekommt die Brezel",         mealIcon(brezel),   "pretzel");
  pruef("Gescanntes bekommt die Packung",    mealIcon(gescannt), "package");
  pruef("ohne Zuordnung faellt auf Obst",    mealIcon(unbekannt), "fruit");
  pruef("normales Meal behaelt sein Foto",   mealIcon(normal),   null);
  pruef("eigenes Foto gewinnt",              mealIcon(eigenes),  null);

  var tBanane = thumbHtml(banane, "r-thumb", true);
  var tNormal = thumbHtml(normal, "r-thumb", true);
  pruef("Symbol-Thumb ist ein span",   tBanane.indexOf("<span") === 0, true);
  pruef("Symbol-Thumb traegt .msym",   tBanane.indexOf("msym") > -1, true);
  pruef("Symbol-Thumb hat KEIN img",   tBanane.indexOf("<img") === -1, true);
  pruef("Symbol-Thumb behaelt die Ortsklasse", tBanane.indexOf("r-thumb") > -1, true);
  pruef("normales Meal bleibt ein img", tNormal.indexOf("<img") === 0, true);
  pruef("normales Meal zeigt das Foto", tNormal.indexOf("FOTO.webp") > -1, true);

  var gross = msPhotoInnerHtml(banane);
  pruef("grosse Flaeche ist eine Symbolflaeche", gross.indexOf("msym-big") > -1, true);
  pruef("grosse Flaeche ohne Foto",    gross.indexOf("FOTO.webp") === -1, true);
  pruef("normales Meal gross mit Foto", msPhotoInnerHtml(normal).indexOf("<img") === 0, true);

  // Jeder Wert in FOOD_ICON muss einen Pfad haben - sonst zeichnet iconSvg() den Topf.
  var tot = Object.keys(FOOD_ICON).filter(function (n) { return !ICONS[FOOD_ICON[n]]; });
  pruef("kein Symbol ohne Pfad (" + tot.join(", ") + ")", tot.length, 0);
  // Und die Gegenrichtung fuer das eine Symbol ohne Listeneintrag.
  pruef("Packungssymbol existiert", !!ICONS["package"], true);

  // ---- "Symbolbild - KI-generiert" gilt nur fuer die mitgelieferten Fotos ----
  // Ein Strichsymbol ist keines von beidem. Bei Bildern ist das eine Kennzeichnungsfrage.
  pruef("kein KI-Hinweis am Symbol",   bildHinweisHtml(banane).indexOf("hidden") > -1, true);
  pruef("kein KI-Hinweis am Gescannten", bildHinweisHtml(gescannt).indexOf("hidden") > -1, true);
  pruef("Foto behaelt den Hinweis",    bildHinweisHtml(normal).indexOf("hidden"), -1);
  pruef("eigenes Foto ohne Hinweis",   bildHinweisHtml(eigenes).indexOf("hidden") > -1, true);
  pruef("Alt-Text ohne KI-Zusatz am Symbol", bildAlt(banane).indexOf("KI-generiert"), -1);
  pruef("Alt-Text mit KI-Zusatz am Foto",    bildAlt(normal).indexOf("KI-generiert") > -1, true);
"""

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Meal-Symbol</title>
<pre id="raus">laeuft</pre>
<script>
%(ikonen)s
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
    ikonen = io.open(IKONEN, encoding="utf-8").read()
    teile, fehlend = [], []
    for name in FUNKTIONEN:
        s = schneide(quelle, name)
        (teile if s else fehlend).append(s or ("function " + name + "()"))
    ik = []
    for name in ("ICONS", "FOOD_ICON"):
        s = schneide(ikonen, name, "const")
        (ik if s else fehlend).append(s or ("const " + name))
    html = SEITE % {"ikonen": "\n".join(ik), "stubs": STUBS,
                    "code": "\n".join(teile), "pruefungen": PRUEFUNGEN}
    return html, fehlend


def fahren(html):
    ordner = tempfile.mkdtemp(prefix="mealsym-")
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
    print("Pruefstand Meal-Symbol")
    print("Quelle: " + os.path.relpath(INDEX, BASIS).replace("\\", "/"))
    print("")

    html, fehlend = bauen()
    if fehlend:
        for f in fehlend:
            print("  FEHLT im Quelltext: " + f)
        print("")
        print("FEHLGESCHLAGEN: %d Baustein(e) nicht gefunden - der Pruefstand kann nichts "
              "messen." % len(fehlend))
        return 1

    # ---- Alle vier Ansichten muessen die Weiche auch aufrufen ----
    quelle = io.open(INDEX, encoding="utf-8").read()
    schief = []
    for name, ruft in (("thumbHtml", "mealIcon"),            # Plan, Picker, Vorkochliste
                       ("nextMealHtml", "mealIcon"),         # Startreiter
                       ("msPhotoInnerHtml", "mealIcon")):    # Meal-Blatt
        s = schneide(quelle, name)
        if not s:
            schief.append("%s: nicht gefunden" % name)
        elif ruft + "(" not in ohne_kommentare(s):
            schief.append("%s: entscheidet selbst, statt %s() zu fragen" % (name, ruft))
    for e in schief:
        print("  FEHL  " + e)
    if not schief:
        print("  OK    Plan, Startreiter und Meal-Blatt fragen dieselbe Weiche")

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
