# -*- coding: utf-8 -*-
u"""
Pruefstand Mengenanzeige: Brueche bei Loeffelmengen, keine Naehrwerte bei Gewuerzen.

ANLASS (29.08.2026): Nachdem jede Zutat eine Menge bekommen hatte (TROUBLESHOOTING 143),
stand in der Zutatenliste "0,25 TL Pfeffer", waehrend die Anleitung "1/4 TL Pfeffer" sagte -
derselbe Wert in zwei Schreibweisen. `qtyLabel()` schreibt Loeffelmengen seitdem als Bruch,
und `ingShowsNut()` laesst die Naehrwerte weg, wo sie nichts aussagen.

WAS ER PRUEFT - am ECHTEN, ausgeschnittenen Code, nicht an einem Nachbau:
  * qtyLabel() macht aus 0,25/0,5/0,75 TL die Zeichen ¼ ½ ¾, auch als gemischte Zahl (1½)
  * eine krumme Menge (0,3 TL) bleibt dezimal, statt falsch gerundet zu werden
  * g/ml/st bleiben unveraendert - die Brueche gelten NUR fuer TL und EL
  * ingShowsNut() blendet Gewuerze aus (TL/EL unter 15 kcal), NICHT aber 1 EL Oel
  * pdfEsc() aus lib/pdf.js kann ¼ ½ ¾ - sonst druckt die Einkaufsliste "? TL Salz"
  * roIngRowHtml(), paintIngView() und buildShoppingList() fragen den gemeinsamen Helfer,
    statt die Schwelle je dreimal auszuschreiben

DER LETZTE PUNKT IST DER EIGENTLICHE GRUND FUER DIESEN PRUEFSTAND. Die ersten vier sieht
man in der App sofort. Der PDF-Export ist der stille Weg: `pdfEsc()` ersetzt jedes Zeichen
ausserhalb von WinAnsi durch "?", ohne Fehler, ohne Meldung. Genau das ist dort schon
einmal passiert, damals mit dem "×" (Kommentar in lib/pdf.js). Wer in qtyLabel() ein
weiteres Bruchzeichen ergaenzt und WINANSI vergisst, faellt hier auf - und nur hier.

Aufrufe:
    python tools/pruefstand-mengenanzeige.py
    python tools/pruefstand-mengenanzeige.py alt/index.html   # Gegenprobe gegen alten Stand
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
PDFJS = os.path.join(BASIS, "lib", "pdf.js")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(text, name, art="function"):
    u"""Eine Deklaration im Wortlaut herausschneiden - ueber die Klammerbilanz, nicht ueber
    ein Regex bis zur naechsten Zeile. Fehlt sie, ist das ein BEFUND und keine Ausnahme:
    Ein Pruefstand, der eine fehlende Funktion still uebergeht, prueft nichts mehr."""
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
    # const NAME = ... ; bis zum Zeilenende (die betroffenen sind einzeilig)
    m = re.search(r"\n\s*const\s+" + re.escape(name) + r"\s*=.*?;", text, re.S)
    return m.group(0) if m else None


def ohne_kommentare(code):
    u"""Kommentare raus, bevor im Code gesucht wird.

    OHNE DAS PRUEFT DIESE STELLE NICHTS. Der Kommentar ueber dem Aufruf in paintIngView()
    nennt `ingShowsNut()` beim Namen - eine reine Textsuche fand ihn DORT und meldete gruen,
    nachdem die Gegenprobe den Aufruf selbst zurueckgedreht hatte (29.08.2026). Ein Pruefer,
    der seinen eigenen Kommentar liest, bestaetigt sich selbst."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    return re.sub(r"//[^\n]*", " ", code)


FUNKTIONEN = ["nutNum", "ingObj", "ingUnit", "unitShort", "numLabel", "ingHasNut",
              "ingContrib", "bruchLabel", "qtyLabel", "ingIsSeasoning", "ingShowsNut"]
KONSTANTEN = ["ING_UNITS", "BRUCH", "ING_NUT_MIN_KCAL"]

PRUEFUNGEN = u"""
  // ---- qtyLabel: Brueche bei Loeffelmengen ----
  pruef("0,25 TL wird ein Viertel",        qtyLabel(0.25, "tl"), "\\u00bc TL");
  pruef("0,5 TL wird ein Halbes",          qtyLabel(0.5, "tl"),  "\\u00bd TL");
  pruef("0,75 TL wird Dreiviertel",        qtyLabel(0.75, "tl"), "\\u00be TL");
  pruef("1,5 TL wird eine gemischte Zahl", qtyLabel(1.5, "tl"),  "1\\u00bd TL");
  pruef("2 TL bleibt ganz",                qtyLabel(2, "tl"),    "2 TL");
  pruef("EL zaehlt genauso",               qtyLabel(0.5, "el"),  "\\u00bd EL");
  // Summen aus der Einkaufsliste: 0,5 + 0,25 aus zwei Rezepten, und mal drei Personen.
  pruef("Summe 0,75 aus zwei Rezepten",    qtyLabel(0.5 + 0.25, "tl"), "\\u00be TL");
  pruef("0,5 mal drei Personen",           qtyLabel(0.5 * 3, "tl"),    "1\\u00bd TL");
  // Eine krumme Menge DARF NICHT auf einen Bruch gerundet werden - sie waere dann falsch.
  pruef("0,3 TL bleibt dezimal",           qtyLabel(0.3, "tl"),  "0,3 TL");
  pruef("1,1 TL bleibt dezimal",           qtyLabel(1.1, "tl"),  "1,1 TL");

  // ---- die anderen Einheiten bleiben unangetastet ----
  pruef("Gramm bleibt Gramm",              qtyLabel(0.5, "g"),   "0,5 g");
  pruef("Milliliter bleibt Milliliter",    qtyLabel(250, "ml"),  "250 ml");
  pruef("Stueck bleibt Stueck",            qtyLabel(2, "st"),    "2\\u00d7");
  pruef("ab 1000 g wird kg",               qtyLabel(1500, "g"),  "1,5 kg");

  // ---- ingShowsNut: Gewuerze ohne Naehrwerte, Oel mit ----
  var salz    = { name: "Salz", grams: 0.5, unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 };
  var curry   = { name: "Currypulver", grams: 2, unit: "tl", kcal: 7, carbs: 1.2, protein: 0.3, fat: 0.3 };
  var oelEL   = { name: "Olivenöl", grams: 1, unit: "el", kcal: 90, carbs: 0, protein: 0, fat: 10 };
  var gurke   = { name: "Gurke", grams: 100, kcal: 12, carbs: 1.8, protein: 0.6, fat: 0.1 };
  var ohneNut = { name: "Selbstgemachtes", grams: 100 };
  var ohneMenge = { name: "Salz", unit: "tl", kcal: 0, carbs: 0, protein: 0, fat: 0 };

  pruef("Salz zeigt keine Naehrwerte",     ingShowsNut(salz),    false);
  pruef("2 TL Currypulver ebenfalls nicht", ingShowsNut(curry),  false);
  pruef("1 EL Oel zeigt sie sehr wohl",    ingShowsNut(oelEL),   true);
  pruef("100 g Gurke zeigt sie",           ingShowsNut(gurke),   true);
  pruef("Zutat ohne Naehrwerte zeigt nichts", ingShowsNut(ohneNut), false);
  pruef("Zutat ohne Menge zeigt nichts",   ingShowsNut(ohneMenge), false);
  // Die Grenze liegt bei 15 kcal - genau darauf muss sie noch anzeigen.
  var grenze = { name: "X", grams: 1, unit: "tl", kcal: 15, carbs: 0, protein: 0, fat: 0 };
  var drunter = { name: "X", grams: 1, unit: "tl", kcal: 14.9, carbs: 0, protein: 0, fat: 0 };
  pruef("genau 15 kcal zeigt noch an",     ingShowsNut(grenze),  true);
  pruef("14,9 kcal zeigt nicht mehr an",   ingShowsNut(drunter), false);

  // ---- ingIsSeasoning: derselbe Begriff, zweite Folge (Einkaufsliste) ----
  pruef("Salz ist Wuerze",                 ingIsSeasoning(salz),  true);
  pruef("Currypulver ist Wuerze",          ingIsSeasoning(curry), true);
  pruef("1 EL Oel ist KEINE Wuerze",       ingIsSeasoning(oelEL), false);
  pruef("100 g Gurke ist KEINE Wuerze",    ingIsSeasoning(gurke), false);
  pruef("ohne Menge keine Wuerze",         ingIsSeasoning(ohneMenge), false);
  // ingShowsNut muss die Umkehrung sein, sonst sind es doch wieder zwei Regeln.
  pruef("Wuerze und Naehrwertzeile schliessen sich aus",
        ingIsSeasoning(salz) === !ingShowsNut(salz), true);

  // ---- pdfEsc: die Brueche muessen den PDF-Export ueberleben ----
  pruef("Viertel im PDF",   pdfEsc("\\u00bc TL Salz").indexOf("?"), -1);
  pruef("Halbes im PDF",    pdfEsc("\\u00bd TL Salz").indexOf("?"), -1);
  pruef("Dreiviertel im PDF", pdfEsc("\\u00be TL Salz").indexOf("?"), -1);
  // Gegenstueck: ein Zeichen, das WinAnsi NICHT kennt, muss weiterhin als "?" auffallen -
  // sonst misst die Pruefung oben nur, dass pdfEsc ueberhaupt etwas zurueckgibt.
  pruef("Drittel faellt weiterhin durch", pdfEsc("\\u2153 TL").indexOf("?"), 0);
"""

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Mengenanzeige</title>
<pre id="raus">laeuft…</pre>
<script>
%(code)s
%(pdf)s
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
    u"""Die Seite aus echtem Produktionscode zusammensetzen. Liefert (html, fehlende)."""
    quelle = io.open(INDEX, encoding="utf-8").read()
    pdfquelle = io.open(PDFJS, encoding="utf-8").read()

    teile, fehlend = [], []
    for name in KONSTANTEN:
        s = schneide(quelle, name, "const")
        (teile if s else fehlend).append(s or ("const " + name))
    for name in FUNKTIONEN:
        s = schneide(quelle, name, "function")
        (teile if s else fehlend).append(s or ("function " + name + "()"))

    pdf_teile = []
    for name, art in (("WINANSI", "const"), ("pdfEsc", "function")):
        s = schneide(pdfquelle, name, art)
        (pdf_teile if s else fehlend).append(s or (art + " " + name))

    html = SEITE % {"code": "\n".join(teile), "pdf": "\n".join(pdf_teile),
                    "pruefungen": PRUEFUNGEN}
    return html, fehlend


def fahren(html):
    ordner = tempfile.mkdtemp(prefix="mengen-")
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
    print("Pruefstand Mengenanzeige")
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

    # ---- Beide Renderer muessen DIESELBE Entscheidung benutzen ----
    # Das ist eine Quelltext-Pruefung und keine Messung, und sie steht bewusst trotzdem hier.
    # ingShowsNut() laesst sich oben am ausgeschnittenen Code messen; dass die Leseansicht
    # (roIngRowHtml) und der Ruhezustand im Meal-Editor (paintIngView) sie auch AUFRUFEN,
    # laesst sich nur im Quelltext sehen - der Editor haengt an einem Modal mit Formularzustand,
    # und ein Versuch, ihn ueber das DevTools-Protokoll zu fahren, ist am 29.08.2026 daran
    # gescheitert. Ohne diese Pruefung koennte eine der beiden Ansichten stillschweigend
    # zurueckfallen und Gewuerze wieder mit "0 kcal · 0 KH 0 P 0 F" zeigen.
    quelle = io.open(INDEX, encoding="utf-8").read()
    schief = []
    for name, ruft in (("roIngRowHtml", "ingShowsNut"), ("paintIngView", "ingShowsNut"),
                       ("buildShoppingList", "ingIsSeasoning")):
        s = schneide(quelle, name)
        if not s:
            schief.append("%s: nicht gefunden" % name)
        elif ruft + "(" not in ohne_kommentare(s):
            schief.append("%s: entscheidet selbst, statt %s() zu fragen" % (name, ruft))
    for e in schief:
        print("  FEHL  " + e)
    if not schief:
        print("  OK    Leseansicht, Meal-Editor und Einkaufsliste fragen den gemeinsamen Helfer")

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
    gesamt = len(ergebnisse) + 1   # +1 fuer die Quelltext-Pruefung oben
    if rot:
        print("FEHLGESCHLAGEN: %d von %d" % (rot, gesamt))
        return 1
    print("ERGEBNIS %d Pruefungen gruen" % gesamt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
