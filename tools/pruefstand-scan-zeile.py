# -*- coding: utf-8 -*-
u"""
Barcode-Scan an der Zutatenzeile: ueberlebt die Zeile den Sucher?

Gemessen wird der Weg, der am 13.09.2026 als kaputt gemeldet wurde: "Meal erstellen ->
Zutat hinzufuegen -> Scannen" tat nach dem Scan GAR NICHTS - kein Wert, kein Toast,
keine Fehlermeldung.

Die Kette dahinter: scanBarcodeLive() fokussiert den Schliessen-Knopf seines Suchers, der
Fokus verlaesst damit die Zutatenzeile, der focusout-Waechter ruft closeIngRow(), und eine
noch leere Zeile wird dabei entfernt. Der Treffer lief danach in die isConnected-Wache von
startBarcodeFlow() - und die kehrt WORTLOS zurueck. Eingebaut wurde die Falle mit 3442cad
(08.08.2026), als Ansehen und Bearbeiten zu einer Oberflaeche wurden; der Scanner ist aelter.

Deshalb bildet der Stub von scanBarcodeLive() genau eines echt nach: den Fokusraub - und
zwar zum richtigen ZEITPUNKT. Headless stellt Fokusereignisse verzoegert zu (erst beim
Schliessen des Suchers); im echten Chrome kommen sie sofort beim Oeffnen. Mit der falschen
Reihenfolge fuellt applyBarcode() die Zeile noch rechtzeitig, der Kernfall bleibt gruen und
der Pruefstand meldet Ruhe, wo keine ist. Am 13.09.2026 genau so passiert.

Der Code ist ECHT ausgeschnitten (addIngRow samt focusout-Waechter, closeIngRow, rowData,
paintIngView, applyBarcode, startBarcodeFlow, armBarcodeDialogAbort und der change-Handler
des Datei-Feldes aus index.html; esc/el aus lib/basis.js) - kein Nachbau. Gestubbt ist nur,
was von aussen kommt: der Sucher, der OFF-Abruf, toast, die Sortiergeste und der Zustand.

SIEBEN FAELLE:
  leer          leere, frische Zeile + Treffer -> Zeile lebt, Werte und Name stehen drin
  gefuellt      Zeile mit Namen + Treffer -> Werte drin UND die sichtbare Zeile zeigt sie
  abbruch       Sucher abgebrochen -> Zeile bleibt, Markierung ist wieder weg
  fotoweg       Ausweichen aufs Foto -> Datei kommt an, Werte landen in der Zeile
  fotoabbruch   Dateidialog abgebrochen -> Markierung faellt wieder, Zeile bleibt bedienbar
  spaetedatei   Kamera-App liefert spaet, Zeile laengst zugeklappt -> Anzeige wird nachgezogen
  geloescht     Zeile waehrend des Scans wirklich geloescht -> stiller Ausstieg, kein Fehler

Gegenproben - ohne sie zaehlt kein Ergebnis:
  python tools/pruefstand-scan-zeile.py --rueckbau vorher       # ganzer Stand von db2aea7
  python tools/pruefstand-scan-zeile.py --rueckbau altewache    # focusout ohne Scan-Schutz
  python tools/pruefstand-scan-zeile.py --rueckbau ohneanzeige  # kein paintIngView danach

"vorher" ist die Gegenprobe, auf die es ankommt: sie stellt den gemeldeten Fehler wieder her
(leere Zeile weg, keine Werte, KEIN Toast). "altewache" und "ohneanzeige" zeigen, welche
Haelfte der Reparatur welchen Fall traegt - einzeln faellt keine von beiden ueberall durch,
weil die jeweils andere Haelfte noch greift.

Aufruf:  python tools/pruefstand-scan-zeile.py [--rueckbau <name>]
"""
import io, json, os, re, subprocess, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
INDEX = os.path.join(BASIS, "index.html")
BASISJS = os.path.join(BASIS, "lib", "basis.js")

# Die Rueckbauten stellen den Stand vor der Reparatur vom 13.09.2026 wieder her - je einer
# eine Haelfte, und "vorher" den ganzen Stand von db2aea7. Ein Rueckbau ist eine LISTE von
# (alt, neu)-Paaren: die Reparatur sitzt an mehreren Stellen, und ein Rueckbau, der nur eine
# davon zuruecknimmt, laesst die andere weiterwirken - dann faellt die Gegenprobe im
# eigentlichen Fall NICHT durch und der Pruefstand behauptet, er messe etwas, das er nicht
# misst. Genau das ist hier am 13.09.2026 zuerst passiert (docs/TESTING.md).
_WAECHTER_NEU = """        setTimeout(() => {
          if (row.dataset.scanning) return;
          if (!row.contains(document.activeElement)) closeIngRow(row);
        }, 0);"""
_WAECHTER_ALT = """        setTimeout(() => { if (!row.contains(document.activeElement)) closeIngRow(row); }, 0);"""
_ANZEIGE_NEU = '        if (!row.classList.contains("editing")) paintIngView(row);\n'
_FLOW_ALT = """    async function startBarcodeFlow(row) {
      const r = await scanBarcodeLive();
      if (!r || r.cancelled) return;
      if (!row.isConnected) return; // Zeile inzwischen entfernt
      if (r.photo) { barcodeRow = row; barcodeInput.click(); return; }
      if (r.code) await applyBarcode(row, r.code);
    }"""


def _flow_neu(seite):
    u"""Den reparierten startBarcodeFlow samt armBarcodeDialogAbort aus der Datei holen -
    woertlich, damit der Rueckbau nicht veraltet, sobald jemand dort einen Kommentar aendert."""
    i = seite.index("    async function startBarcodeFlow(row) {")
    ende = "\n    }"
    j = seite.index(ende, seite.index("    function armBarcodeDialogAbort(row) {"))
    return seite[i:j + len(ende)]


def rueckbauten(seite):
    return {
        # Der ganze Stand vor der Reparatur (db2aea7): so hat es sich fuer den Nutzer
        # angefuehlt - "nach dem Scan kommt einfach gar nichts".
        "vorher": [(_WAECHTER_NEU, _WAECHTER_ALT),
                   (_flow_neu(seite), _FLOW_ALT),
                   (_ANZEIGE_NEU, "")],
        # Nur der focusout-Waechter ohne Scan-Markierung. Der Rueckfokus in
        # startBarcodeFlow() faengt den Live-Weg dann noch ab - der Foto-Weg nicht mehr.
        "altewache": [(_WAECHTER_NEU, _WAECHTER_ALT)],
        # Ohne das Nachziehen der Ruhezustands-Zeile.
        "ohneanzeige": [(_ANZEIGE_NEU, "")],
    }


def block(text, kopf):
    u"""Den Funktionsblock ab `kopf` bis zur schliessenden Klammer auf gleicher Einrueckung.

    Bewusst nicht ueber die naechste Zeile, die "}" ENTHAELT: in verschachteltem Code ist das
    regelmaessig `    }));` mitten in der Funktion (docs/TESTING.md, Fallarchiv zum Schnitt).
    """
    i = text.index(kopf)
    zeilenanfang = text.rfind("\n", 0, i) + 1
    zeilenende = text.index("\n", i)
    einzeiler = text[zeilenanfang:zeilenende]
    # Einzeiler (esc, el, nutNum, nfmt ...) schliessen auf derselben Zeile - dort gibt es
    # keinen Endmarker auf gleicher Einrueckung, und die Suche danach liefe in die naechste
    # Funktion hinein.
    if einzeiler.rstrip().endswith("}"):
        return einzeiler
    einzug = text[zeilenanfang:i]
    ende = "\n" + einzug + "}"
    j = text.index(ende, i)
    return text[zeilenanfang:j + len(ende)]


def abschnitt(text, anfang, ende):
    u"""Ein Stueck Code zwischen zwei woertlichen Markern - fuer alles, was kein
    benannter Block ist (hier: der change-Handler des Datei-Feldes)."""
    i = text.index(anfang)
    j = text.index(ende, i)
    return text[i:j + len(ende)]


def baue_seite(rueckbau=None):
    seite = pm_quelle.lade_seite(INDEX)
    if rueckbau:
        for alt, neu in rueckbauten(seite)[rueckbau]:
            if seite.count(alt) != 1:
                raise SystemExit("Rueckbau '%s' fand eine seiner Stellen nicht genau einmal "
                                 "(%d) - der Pruefstand wuerde sonst still gegen "
                                 "unveraenderten Code messen.\n---\n%s\n---"
                                 % (rueckbau, seite.count(alt), alt[:200]))
            seite = seite.replace(alt, neu, 1)
    return seite


def schneide(rueckbau=None):
    seite = baue_seite(rueckbau)
    basis = io.open(BASISJS, encoding="utf-8").read()
    teile = [
        block(basis, "function esc(s) {"),
        block(basis, "function el(html) {"),
        block(seite, "function nutNum(x) {"),
        block(seite, "function nutParse(v) {"),
        block(seite, "function nfmt(n) {"),
        block(seite, "function macroLineHtml(n, fmt) {"),
        block(seite, "function ingObj(i) {"),
        block(seite, "function ingHasNut(i) {"),
        block(seite, "function ingUnit(o) {"),
        block(seite, "function unitShort(u) {"),
        block(seite, "function ingPerLabel(u) {"),
        block(seite, "function ingContrib(i) {"),
        block(seite, "function ingIsSeasoning(i) {"),
        block(seite, "function ingShowsNut(i) {"),
        block(seite, "function bruchLabel(n) {"),
        block(seite, "function qtyLabel(n, u) {"),
        block(seite, "function numLabel(n) {"),
        block(seite, "function nutVal(v) {"),
        block(seite, "function paintIngView(row) {"),
        block(seite, "function closeIngRow(row) {"),
        block(seite, "function openIngEdit(row, focusName) {"),
        block(seite, "function addIngRow(o) {"),
        block(seite, "function rowData(row) {"),
        block(seite, "async function applyBarcode(row, code) {"),
        block(seite, "async function startBarcodeFlow(row) {"),
        abschnitt(seite, '    barcodeInput.addEventListener("change", async () => {',
                  "      await applyBarcode(row, code);\n    });"),
    ]
    # Den Vorzustand gab es ohne diesen Helfer - beim Rueckbau "vorher" ist er nicht da.
    if "function armBarcodeDialogAbort(row) {" in seite:
        teile.append(block(seite, "function armBarcodeDialogAbort(row) {"))
    return "\n".join(teile)


BUEHNE = u"""<!doctype html><meta charset="utf-8"><title>Scan-Zeile-Pruefstand</title>
<pre id="messung">laeuft</pre>
<div id="formular"><select id="f-cat"><option selected>Hauptgericht</option></select>
<input type="file" id="f-ing-barcode"><div id="ings"></div></div>
<script>
window.__fehler = [];
window.addEventListener("error", e => window.__fehler.push((e.message || "") + " @" + (e.lineno || "?")));
window.addEventListener("unhandledrejection", e => window.__fehler.push("rejection: " + String(e.reason)));
</script>
<script>
// ---- Stubs: alles, was von aussen kommt. Der geprueft Code selbst ist echt. ----
const ING_UNITS = ["g", "ml", "st", "el", "tl"];
const ICON_GRIP = "<i></i>";
const BARCODE_SVG = "<i></i>";
const node = document.getElementById("formular");
const ingsWrap = document.getElementById("ings");
const barcodeInput = document.getElementById("f-ing-barcode");
let barcodeRow = null;
let openIngRowEl = null;
let acOpen = false;
let acSeq = 0;
// Die Zutaten-Autocomplete haengt am Katalog; sie ist hier nicht die Messgroesse. Eine
// leere Trefferliste laesst den echten Code der Zeile unveraendert durchlaufen.
function foodSearch() { return []; }
function updateMacroSum() {}
function updateEmptyIngNote() {}
function commitNow() {}
const toasts = [];
function toast(t) { toasts.push(String(t)); }
function sortierGeste() {}
function reducedMotion() { return true; }
// Die Autocomplete haengt an FOODS; die Vorschlagsliste selbst ist hier nicht die Messgroesse.
const FOODS = [];
function foodIcon() { return "fruit"; }
function pieceFoods() { return []; }
function pieceTop() { return []; }
function convertNutValues() {}

// ---- Der Sucher. Gestubbt ist die Kamera - NICHT der Fokusraub. ----
// scanBarcodeLive() haengt seinen Sucher an document.body und fokussiert dessen
// Schliessen-Knopf. Genau das nimmt der Zutatenzeile den Fokus und loest den
// focusout-Waechter aus. Ohne diese Nachbildung misst der Pruefstand nichts - die
// Gegenprobe "altewache" muss deshalb durchfallen.
let naechsterSucher = { code: "111" };
let suchgriff = null;
// Belegt, dass der Sucher der Zeile den Fokus WIRKLICH genommen hat. Genau diese Bedingung
// wertet der focusout-Waechter aus (!row.contains(document.activeElement)) - ohne sie misst
// der Pruefstand nichts und meldete trotzdem gruen.
let suchFokusOk = false;
async function scanBarcodeLive() {
  const n = document.createElement("div");
  n.className = "scanwrap";
  n.innerHTML = '<button type="button" data-x>X</button>';
  document.body.appendChild(n);
  const x = n.querySelector("[data-x]");
  const vorher = document.activeElement;
  x.focus();
  suchgriff = n;
  // Headless stellt einen Fokuswechsel NICHT zuverlaessig im selben Tick zu: ohne dieses
  // Warten mass derselbe Pruefstand mal mit und mal ohne Fokusraub (gemessen 13.09.2026,
  // drei Laeufe: 0, 0, 1). Erst warten, bis der Wechsel wirklich vollzogen ist ...
  for (let i = 0; i < 60 && document.activeElement !== x; i++) await new Promise(r => setTimeout(r, 10));
  suchFokusOk = (document.activeElement === x);
  // Headless stellt das focusout obendrein VERZOEGERT zu - erst beim Entfernen des Knopfs,
  // also nach dem Scan. Im echten Chrome kommt es SOFORT beim Oeffnen des Suchers (am
  // 13.09.2026 im Browser gemessen: die Zeile war weg, bevor der Scan zurueckkam). Genau
  // diese Reihenfolge ist der Fehler - wird sie falsch herum gemessen, fuellt applyBarcode()
  // die Zeile noch rechtzeitig und der Kernfall bleibt gruen. Deshalb wird das Ereignis hier
  // zum richtigen Zeitpunkt nachgestellt; kommt es zusaetzlich vom Browser, schadet das
  // nicht (closeIngRow steigt bei einer nicht mehr offenen Zeile sofort aus).
  if (vorher && vorher !== x) vorher.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
  // ... dann dem focusout-Waechter seinen setTimeout(0) lassen.
  await new Promise(r => setTimeout(r, 30));
  n.remove();
  return naechsterSucher;
}
// Das Produkt, das Open Food Facts liefern wuerde.
let naechstesProdukt = { name: "Nutella", kcal: 539, carbs: 57.5, protein: 6.3, fat: 30.9, servingSize: null };
async function fetchOffNutrition() { return naechstesProdukt; }
// Die Erkennung aus dem Bild - der Foto-Weg reicht den Code hier durch.
let naechsterFotoCode = "222";
async function detectBarcode() { return naechsterFotoCode; }
</script>
<script>
__CODE__
</script>
<script>
// Selbstpruefung des Pruefstands: Der gemessene Fehler haengt daran, dass der Sucher der
// Zeile den Fokus NIMMT. Findet das headless nicht statt, misst der ganze Pruefstand nichts
// und meldet trotzdem gruen - deshalb sind beide Haelften des Fokuswechsels Messgroessen.
let hatteFokus = false;
function neueZeile(o) {
  ingsWrap.innerHTML = "";
  openIngRowEl = null;
  suchFokusOk = false;
  const row = addIngRow(o || {});
  openIngEdit(row);
  row.focus();
  hatteFokus = (document.activeElement === row);
  return row;
}
function lies(row) {
  const q = s => { const e = row.querySelector(s); return e ? e.value : null; };
  const v = row.querySelector(".ing-view");
  return {
    lebt: row.isConnected,
    markierung: row.dataset.scanning || null,
    name: q(".ing-name"), einheit: q(".ing-u"), menge: q(".ing-g"),
    kcal: q(".ing-kcal"), kh: q(".ing-carbs"), p: q(".ing-prot"), f: q(".ing-fat"),
    sichtbarName: v ? v.querySelector(".ing-view-name").textContent : null,
    sichtbarKcal: v ? v.querySelector(".ing-view-kcal").textContent : null,
    offen: row.classList.contains("editing"),
  };
}
function dateiSchicken(code) {
  naechsterFotoCode = code || "222";
  const dt = new DataTransfer();
  dt.items.add(new File(["x"], "code.png", { type: "image/png" }));
  barcodeInput.files = dt.files;
  barcodeInput.dispatchEvent(new Event("change"));
}
const warte = ms => new Promise(r => setTimeout(r, ms));
// Der Zeile den Fokus nehmen, wie es ein Klick woandershin taete. Das focusout wird wie im
// Sucher-Stub nachgestellt, weil headless es sonst verzoegert zustellt.
function fokusWeg(row) {
  document.getElementById("f-cat").focus();
  row.dispatchEvent(new FocusEvent("focusout", { bubbles: true }));
}

(async function () {
  const raus = {};
  try {
    // Der Dateidialog laesst sich headless nicht oeffnen - und soll es auch nicht.
    barcodeInput.click = function () { raus._dialog = (raus._dialog || 0) + 1; };

    // 1) leer: der gemeldete Fall - frische Zeile, nichts eingetragen, direkt scannen.
    naechsterSucher = { code: "3017620422003" };
    let row = neueZeile();
    toasts.length = 0;
    await startBarcodeFlow(row);
    await warte(30);
    raus.leer = lies(row);
    raus.leer.toast = toasts.join(" | ");
    raus.leer.hatteFokus = hatteFokus;
    raus.leer.suchFokusOk = suchFokusOk;

    // 2) gefuellt: Zeile traegt schon einen Namen - hier zaehlt zusaetzlich die ANZEIGE.
    naechsterSucher = { code: "3017620422003" };
    row = neueZeile({ name: "Testzutat", grams: 100 });
    toasts.length = 0;
    await startBarcodeFlow(row);
    await warte(30);
    // Zuklappen wie im Alltag (Fertig-Knopf), damit die Ruhezustands-Zeile sichtbar wird.
    closeIngRow(row);
    raus.gefuellt = lies(row);
    raus.gefuellt.toast = toasts.join(" | ");

    // 3) abbruch: Sucher zu, ohne Treffer.
    naechsterSucher = { cancelled: true };
    row = neueZeile({ name: "Bleibt", grams: 50 });
    toasts.length = 0;
    await startBarcodeFlow(row);
    await warte(30);
    raus.abbruch = lies(row);
    raus.abbruch.toast = toasts.join(" | ");

    // 4) fotoweg: im Sucher aufs Foto ausweichen, Datei kommt an.
    naechsterSucher = { photo: true };
    row = neueZeile();
    toasts.length = 0;
    await startBarcodeFlow(row);
    await warte(30);
    raus.fotoweg_vorDatei = lies(row);
    dateiSchicken("3017620422003");
    await warte(60);
    raus.fotoweg = lies(row);
    raus.fotoweg.toast = toasts.join(" | ");

    // 5) fotoabbruch: Dialog weggeklickt, es kommt nie ein change. Die Markierung darf
    //    nicht fuer immer stehenbleiben - sonst klappt die Zeile nie wieder zu.
    naechsterSucher = { photo: true };
    row = neueZeile();
    await startBarcodeFlow(row);
    await warte(30);
    raus.fotoabbruch_vorher = lies(row);
    window.dispatchEvent(new Event("focus"));
    await warte(1800);
    raus.fotoabbruch = lies(row);

    // 6) spaetedatei: der mobile Fall. Die Kamera-App liefert ihr Bild erst, wenn die
    //    Markierung laengst gefallen ist und die Zeile zugeklappt wurde. Dann schreibt
    //    applyBarcode() in Felder, die niemand mehr sieht - die sichtbare Zeile muss
    //    nachgezogen werden, sonst sieht auch das nach "nichts passiert" aus.
    naechsterSucher = { photo: true };
    row = neueZeile({ name: "Altname", grams: 100 });
    toasts.length = 0;
    await startBarcodeFlow(row);
    window.dispatchEvent(new Event("focus"));
    await warte(1800);                 // Markierung faellt (armBarcodeDialogAbort)
    fokusWeg(row);                     // ... und jetzt klappt die Zeile zu
    await warte(30);
    raus.spaetedatei_vorher = lies(row);
    dateiSchicken("3017620422003");
    await warte(80);
    raus.spaetedatei = lies(row);
    raus.spaetedatei.toast = toasts.join(" | ");

    // 7) geloescht: der Nutzer entfernt die Zeile wirklich, waehrend der Sucher offen ist.
    naechsterSucher = { code: "3017620422003" };
    row = neueZeile({ name: "Weg", grams: 10 });
    toasts.length = 0;
    const p = startBarcodeFlow(row);
    row.remove();
    await p;
    await warte(30);
    raus.geloescht = { lebt: row.isConnected, toast: toasts.join(" | ") };
  } catch (e) {
    raus.messfehler = String(e && e.message || e);
  }
  raus.fehler = (window.__fehler || []).join(" || ") || "keine";
  document.getElementById("messung").textContent = JSON.stringify(raus);
})();
</script>
"""


def lauf(rueckbau=None):
    seite = BUEHNE.replace("__CODE__", schneide(rueckbau))
    tmp = tempfile.mkdtemp(prefix="scan-zeile-")
    try:
        ziel = os.path.join(tmp, "buehne.html")
        io.open(ziel, "w", encoding="utf-8").write(seite)
        dump = os.path.join(tmp, "dump.html")
        with io.open(dump, "wb") as f:
            subprocess.call([EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=20000",
                             "--user-data-dir=" + os.path.join(tmp, "profil"),
                             "--dump-dom", "file:///" + ziel.replace("\\", "/")],
                            stdout=f, stderr=subprocess.PIPE)
        roh = io.open(dump, encoding="utf-8", errors="replace").read()
        m = re.search(r'<pre id="messung">(.*?)</pre>', roh, re.S)
        if not m:
            return {"messfehler": "KEINE MESSUNG - der Pruefstand selbst ist kaputt."}
        text = (m.group(1).replace("&quot;", '"').replace("&amp;", "&")
                .replace("&lt;", "<").replace("&gt;", ">"))
        if text.strip() == "laeuft":
            return {"messfehler": "Die Messung lief nicht zu Ende."}
        return json.loads(text)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    args = sys.argv[1:]
    rueckbau = None
    if "--rueckbau" in args:
        i = args.index("--rueckbau")
        rueckbau = args[i + 1]
        bekannt = sorted(rueckbauten(pm_quelle.lade_seite(INDEX)))
        if rueckbau not in bekannt:
            raise SystemExit("Unbekannter Rueckbau: %s (bekannt: %s)"
                             % (rueckbau, ", ".join(bekannt)))

    print("Pruefstand Barcode-Scan an der Zutatenzeile")
    print("Quelle: index.html + lib/basis.js"
          + (("   [Rueckbau: " + rueckbau + "]") if rueckbau else ""))
    print("")

    e = lauf(rueckbau)
    if e.get("messfehler"):
        print("  MESSFEHLER: " + e["messfehler"])
        print("")
        print("ERGEBNIS 0 gruen, 1 rot  (1 Messgroessen)")
        return 1

    pruefungen = []

    def p(was, ist, soll):
        pruefungen.append((was, ist == soll, ist, soll))

    a = e["leer"]
    # Zuerst der Pruefstand selbst: ohne echten Fokusraub misst er nichts.
    p("Messbarkeit: die Zeile hatte den Fokus", a["hatteFokus"], True)
    p("Messbarkeit: der Sucher hat ihn genommen", a["suchFokusOk"], True)
    p("Leere Zeile: ueberlebt den Sucher", a["lebt"], True)
    p("Leere Zeile: Markierung wieder weg", a["markierung"], None)
    p("Leere Zeile: Name uebernommen", a["name"], "Nutella")
    p("Leere Zeile: kcal uebernommen", a["kcal"], "539")
    p("Leere Zeile: Kohlenhydrate uebernommen", a["kh"], "57.5")
    p("Leere Zeile: der Nutzer bekommt eine Rueckmeldung", "Nutella" in a["toast"], True)

    b = e["gefuellt"]
    p("Gefuellte Zeile: Name ersetzt", b["name"], "Nutella")
    p("Gefuellte Zeile: kcal uebernommen", b["kcal"], "539")
    p("Gefuellte Zeile: die SICHTBARE Zeile zeigt den neuen Namen", b["sichtbarName"], "Nutella")
    p("Gefuellte Zeile: die sichtbare Zeile zeigt kcal", "539" in (b["sichtbarKcal"] or ""), True)

    c = e["abbruch"]
    p("Abbruch: Zeile bleibt stehen", c["lebt"], True)
    p("Abbruch: Markierung wieder weg", c["markierung"], None)
    p("Abbruch: keine Rueckmeldung ohne Treffer", c["toast"], "")

    d = e["fotoweg"]
    v = e["fotoweg_vorDatei"]
    p("Foto-Weg: Zeile ueberlebt bis zur Datei", v["lebt"], True)
    p("Foto-Weg: Markierung haelt bis zur Datei", v["markierung"], "1")
    p("Foto-Weg: Name aus dem Foto-Code", d["name"], "Nutella")
    p("Foto-Weg: kcal uebernommen", d["kcal"], "539")
    p("Foto-Weg: Markierung danach weg", d["markierung"], None)

    g = e["fotoabbruch"]
    h = e["fotoabbruch_vorher"]
    p("Foto-Abbruch: Markierung steht waehrend des Dialogs", h["markierung"], "1")
    p("Foto-Abbruch: Markierung faellt danach wieder", g["markierung"], None)
    p("Foto-Abbruch: Zeile bleibt bedienbar", g["lebt"], True)

    s = e["spaetedatei"]
    sv = e["spaetedatei_vorher"]
    p("Spaete Datei: die Zeile war zugeklappt", sv["offen"], False)
    p("Spaete Datei: die Zeile lebt noch", sv["lebt"], True)
    p("Spaete Datei: Werte kommen trotzdem an", s["kcal"], "539")
    p("Spaete Datei: die SICHTBARE Zeile zeigt den neuen Namen", s["sichtbarName"], "Nutella")
    p("Spaete Datei: die sichtbare Zeile zeigt kcal", "539" in (s["sichtbarKcal"] or ""), True)

    z = e["geloescht"]
    p("Geloeschte Zeile: bleibt geloescht", z["lebt"], False)
    p("Geloeschte Zeile: kein Absturz, keine Rueckmeldung", z["toast"], "")

    breit = max(len(x[0]) for x in pruefungen)
    rot = 0
    for was, ok, ist, soll in pruefungen:
        if ok:
            print("  OK    " + was)
        else:
            rot += 1
            print("  ROT   " + was.ljust(breit) + "   ist=" + repr(ist) + "  soll=" + repr(soll))
    print("")
    if e.get("fehler") and e["fehler"] != "keine":
        print("  JS-FEHLER: " + e["fehler"])
        rot += 1
    print("ERGEBNIS %d gruen, %d rot  (%d Messgroessen)"
          % (len(pruefungen) - rot, rot, len(pruefungen)))
    return 1 if rot else 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    sys.exit(main())
