# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: die Zurueck-Taste schliesst Overlays (D5, 23.08.2026).

Auf Android beendet die Systemtaste "Zurueck" die App, solange kein History-Eintrag da ist -
auch dann, wenn gerade ein Modal offen steht. Dasselbe gilt fuer die iOS-Wischgeste. Der Umbau
legt deshalb je Overlay einen Eintrag an und schliesst ueber popstate.

Warum das einen echten Browser braucht und nicht nur Codelesen: history.back() ist ASYNCHRON.
Der gefaehrliche Fall ist nicht das Oeffnen, sondern das Schliessen auf normalem Weg (✕, Escape,
Backdrop) - dabei muss der Eintrag per history.back() weg, ohne dass der eigene popstate-
Handler daraufhin ein zweites Mal schliesst. Genau diese Schleife laesst sich nur messen, indem
man sie laufen laesst.

Geprueft werden acht Faelle plus zwei Gegenproben. Der Scanner wird nicht mitgeschnitten
(Kamera), sondern ueber denselben Vertrag simuliert, den er benutzt: overlayOpened(fn) beim
Anhaengen, overlayClosed(fn) im cleanup. Dass er das wirklich so tut, prueft dieses Skript
zusaetzlich am Quelltext.
"""
import io, os, re

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-zurueck-taste.html")

text = io.open(QUELLE, encoding="utf-8").read()
lines = text.split("\n")

# ---- Schnitt: vom Zurueck-Block bis einschliesslich el() ----
start = None
ende = None
for i, z in enumerate(lines):
    if start is None and "// ---------- Zurueck-Taste (D5) ----------" in z:
        start = i
    if start is not None and z.startswith("  function el(html)"):
        ende = i
        break
if start is None or ende is None:
    raise SystemExit("Schnitt nicht gefunden - Marker in index.html geprueft?")

KERN = "\n".join(lines[start:ende + 1])

for muss in ["function overlayOpened", "function overlayClosed", 'addEventListener("popstate"',
             "function closeModal", "function openModal", "ersetztOffenes"]:
    if muss not in KERN:
        raise SystemExit("Ausschnitt unvollstaendig, fehlt: " + muss)

# ---- Gegenprobe 1: openModal ohne History-Eintrag (der Stand VOR D5) ----
OHNE = KERN.replace("    if (!ersetztOffenes) overlayOpened(closeModal);\n", "")
if OHNE == KERN:
    raise SystemExit("Gegenprobe 1 nicht bildbar - die Anbindung sieht anders aus")
OHNE = OHNE.replace("function openModal(", "function openModalOHNE(")
# Nur die eine Funktion herausloesen: der ganze Ausschnitt ein zweites Mal wuerde
# overlayStack erneut deklarieren (SyntaxError) und den popstate-Handler doppelt anmelden.
m = re.search(r"  function openModalOHNE\(node, opts\) \{.*?\n  \}\n", OHNE, re.S)
if not m:
    raise SystemExit("openModalOHNE nicht isolierbar")
OHNE = m.group(0)

# ---- Gegenprobe 2: closeModal raeumt seinen Eintrag NICHT ab ----
# Der naheliegende Fehler: man denkt beim Oeffnen an die History und beim Schliessen nicht.
# Folge waeren tote Eintraege - der erste Druck auf Zurueck taete dann sichtbar nichts.
LECK = KERN.replace("    overlayClosed(closeModal);\n", "")
if LECK == KERN:
    raise SystemExit("Gegenprobe 2 nicht bildbar")
LECK = LECK.replace("function closeModal(", "function closeModalLECK(")
# Aus der Leck-Fassung nur die eine Funktion herausloesen, sonst kollidieren die Namen.
m = re.search(r"  function closeModalLECK\(\) \{.*?\n  \}\n", LECK, re.S)
if not m:
    raise SystemExit("closeModalLECK nicht isolierbar")
LECK_FN = m.group(0)

# ---- Der Scanner wird nicht mitgeschnitten, aber sein Vertrag geprueft ----
scan = text[text.index("  function scanBarcodeLive("):]
scan = scan[:scan.index("\n  }\n")]
scanner_ok = ("overlayOpened(backClose)" in scan
              and "overlayClosed(backClose)" in scan
              and "liveScanStop = backClose" in scan)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Zurueck-Taste</title>
<div id="modal-root"></div>
<pre id="log">laeuft…</pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) {
  var el = document.getElementById("log");
  el.textContent = (el.textContent || "") + "\\nJS-FEHLER: " + m + " (Zeile " + z + ")";
};
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  document.getElementById("log").textContent = LOG.join("\\n");
}
function warte(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }

// ---- Randstuecke ----
var hoveredCardId = null, liveScanStop = null, groupModalRepaint = null;
var gemeldet = [];
function noteError(k, e) { gemeldet.push(k); }

__KERN__
__OHNE__
__LECK__

function baueKnoten(name) {
  return el('<div class="modal" role="dialog" aria-modal="true" aria-label="' + name + '"><button>Schliessen</button></div>');
}
function offen() { return modalRoot.childElementCount > 0; }
function tiefe() { return overlayStack.length; }
function marke() { return (history.state && history.state.pmOverlay) || 0; }

(async function () {
  // Polster: ein eigener Eintrag unter allem. Ohne ihn wuerde ein Zurueck ohne offenes
  // Overlay die Pruefseite selbst verlassen - und der Test waere zu Ende, nicht bestanden.
  history.pushState({ polster: 1 }, "");
  await warte(30);

  // ---- 1. Oeffnen legt genau einen Eintrag an ----
  openModal(baueKnoten("A"));
  pruef("Modal ist offen", offen(), true);
  pruef("ein Eintrag auf dem Stapel", tiefe(), 1);
  pruef("und einer in der History", marke(), 1);

  // ---- 2. Zurueck schliesst das Modal ----
  history.back();
  await warte(120);
  pruef("Zurueck schliesst das Modal", offen(), false);
  pruef("der Stapel ist wieder leer", tiefe(), 0);
  pruef("und die History steht auf dem Polster", marke(), 0);

  // ---- 3. DER KRITISCHE FALL: normal schliessen raeumt den Eintrag mit ab ----
  // Bleibt er stehen, taete der naechste Druck auf Zurueck sichtbar NICHTS - der Nutzer
  // drueckt dann zweimal und landet beim zweiten Mal ausserhalb der App.
  openModal(baueKnoten("B"));
  await warte(30);
  closeModal();
  await warte(120);
  pruef("nach closeModal ist zu", offen(), false);
  pruef("der Stapel ist leer", tiefe(), 0);
  pruef("und der History-Eintrag ist weg (kein toter Eintrag)", marke(), 0);
  pruef("dabei wurde kein Fehler gemeldet", gemeldet.length, 0);

  // ---- 4. Ein Modal, das seinen Inhalt tauscht, bleibt ein Eintrag ----
  // openMealSheet() wechselt per openModal() in den Bearbeiten-Zweig, ohne vorher zu
  // schliessen. Zwei Eintraege hiessen: zweimal Zurueck fuer ein sichtbares Fenster.
  openModal(baueKnoten("C"));
  await warte(20);
  openModal(baueKnoten("C-bearbeiten"));
  await warte(20);
  pruef("Inhaltswechsel legt keinen zweiten Eintrag an", tiefe(), 1);
  pruef("und die History-Marke bleibt bei 1", marke(), 1);
  history.back();
  await warte(120);
  pruef("ein einziges Zurueck schliesst es", offen(), false);

  // ---- 5. Zwei Ebenen: der Scanner liegt UEBER dem Formular ----
  var scannerZu = 0;
  var scanClose = function () { scannerZu++; overlayClosed(scanClose); };
  openModal(baueKnoten("Formular"));
  await warte(20);
  overlayOpened(scanClose);          // genau das tut scanBarcodeLive()
  await warte(20);
  pruef("zwei Ebenen auf dem Stapel", tiefe(), 2);
  history.back();
  await warte(120);
  pruef("Zurueck schliesst zuerst den Scanner", scannerZu, 1);
  pruef("das Formular bleibt offen", offen(), true);
  pruef("eine Ebene bleibt uebrig", tiefe(), 1);
  history.back();
  await warte(120);
  pruef("erst das zweite Zurueck schliesst das Formular", offen(), false);
  pruef("Stapel leer", tiefe(), 0);

  // ---- 5b. Beide Ebenen auf einmal schliessen ----
  // closeModal() beendet zuerst den laufenden Sucher (liveScanStop) und schliesst dann sich
  // selbst - zwei history.back() im SELBEN Tick. Beide muessen als eigene ausgeloeste
  // Ereignisse erkannt werden; zaehlt der Zaehler nur eines, schliesst der Rueckstoss ein
  // drittes, gar nicht beteiligtes Overlay - oder die Seite verlaesst die App.
  scannerZu = 0;
  scanClose = function () { scannerZu++; overlayClosed(scanClose); };
  openModal(baueKnoten("Formular2"));
  await warte(20);
  overlayOpened(scanClose);
  liveScanStop = scanClose;          // genau so haengt der Scanner in closeModal()
  await warte(20);
  pruef("zwei Ebenen stehen", tiefe(), 2);
  closeModal();
  await warte(250);
  pruef("closeModal beendet auch den Sucher", scannerZu, 1);
  pruef("beide Ebenen sind weg", [offen(), tiefe()], [false, 0]);
  pruef("und die History steht wieder auf dem Polster", marke(), 0);
  pruef("ohne gemeldeten Fehler", gemeldet.length, 0);
  liveScanStop = null;

  // ---- 5c. Schliessen und im selben Tick neu oeffnen ----
  // Kommt real vor: "Teilen" in der Meal-Ansicht ruft closeModal() und direkt danach
  // shareRecipeNow(), das ein neues Modal oeffnet. Die noch offene Ruecknahme darf das eben
  // geoeffnete Fenster nicht mitreissen - und es darf auch kein Eintrag zu viel entstehen.
  openModal(baueKnoten("Ansicht"));
  await warte(20);
  closeModal();
  openModal(baueKnoten("Teilen"));   // ohne await: derselbe Tick
  await warte(250);
  pruef("das neue Overlay steht", offen(), true);
  pruef("genau eine Ebene", tiefe(), 1);
  pruef("und genau eine Marke", marke(), 1);
  history.back();
  await warte(150);
  pruef("ein Zurueck schliesst es", [offen(), tiefe()], [false, 0]);
  pruef("und landet auf dem Polster, nicht daneben", marke(), 0);

  // ---- 5d. Der echte Fall aus index.html: Modal zu, Scanner auf ----
  // "Barcode" in der Slot-Auswahl macht genau das: closeModal(); quickAddByBarcode(...) -
  // und der Scanner haengt sich unmittelbar per overlayOpened() ein. Dieselbe Mechanik wie
  // 5c, aber mit der Sucher-Ebene statt eines zweiten Modals.
  var suchZu = 0;
  var suchClose = function () { suchZu++; overlayClosed(suchClose); return true; };
  openModal(baueKnoten("Slot-Auswahl"));
  await warte(20);
  closeModal();
  overlayOpened(suchClose);   // ohne await: derselbe Tick
  await warte(250);
  pruef("nur der Sucher steht", [offen(), tiefe()], [false, 1]);
  pruef("und genau eine Marke", marke(), 1);
  history.back();
  await warte(150);
  pruef("ein Zurueck schliesst den Sucher", suchZu, 1);
  pruef("Stapel leer, Polster erreicht", [tiefe(), marke()], [0, 0]);

  // ---- 6. Ein abgebrochenes Schliessen laesst den Eintrag stehen ----
  // Das Meal-Formular ohne Namen verweigert das Schliessen (Toast statt Verwerfen). Waere
  // der Eintrag da schon weg, haette das Overlay danach keinen mehr - und Zurueck ginge
  // aus der App heraus, obwohl noch etwas offen ist.
  openModal(baueKnoten("D"));
  await warte(20);
  var abgebrochen = 0;
  // Wie attemptClose() im Meal-Formular: meldet die Verweigerung und traegt sich neu ein.
  var verweigerer = function () { abgebrochen++; modalCloseHook = verweigerer; return false; };
  modalCloseHook = verweigerer;
  closeModal();
  await warte(120);
  pruef("der Hook hat abgebrochen", abgebrochen, 1);
  pruef("das Overlay ist noch offen", offen(), true);
  pruef("und sein Eintrag steht noch", tiefe(), 1);
  // ---- 6b. DERSELBE ABBRUCH, aber ausgeloest durch die Zurueck-Taste ----
  // Hier ist der History-Eintrag beim Aufruf schon zurueckgenommen. Wird er nicht neu
  // angelegt, steht das Formular offen da - und der naechste Druck verlaesst die App.
  abgebrochen = 0;
  history.back();
  await warte(200);
  pruef("Zurueck wurde ebenfalls abgewiesen", abgebrochen, 1);
  pruef("das Formular steht noch", offen(), true);
  pruef("sein Eintrag wurde neu angelegt", tiefe(), 1);
  pruef("und die Marke steht wieder", marke(), 1);

  // Jetzt wirklich schliessen
  modalCloseHook = null;
  closeModal();
  await warte(150);
  pruef("danach schliesst es normal", offen(), false);
  pruef("und raeumt auf", tiefe(), 0);
  pruef("die History steht auf dem Polster", marke(), 0);

  // ---- 7. Zurueck ohne offenes Overlay tut nichts ----
  // Erwartetes Verhalten: die App wird verlassen. Hier steht das Polster darunter, also
  // messen wir nur, dass der Handler nicht stolpert und nichts erfindet.
  history.pushState({ fremd: 1 }, "");
  await warte(30);
  history.back();
  await warte(120);
  pruef("kein Overlay, kein Schaden", [offen(), tiefe(), gemeldet.length], [false, 0, 0]);

  // ---- Gegenprobe 1: ohne History-Eintrag schliesst Zurueck nichts ----
  openModalOHNE(baueKnoten("Gegenprobe"));
  await warte(20);
  pruef("GEGENPROBE Modal offen, aber kein Eintrag", [offen(), tiefe()], [true, 0]);
  history.pushState({ fremd: 2 }, "");
  await warte(20);
  history.back();
  await warte(120);
  pruef("GEGENPROBE Zurueck laesst es offen (so war es vor D5)", offen(), true);
  closeModal();
  await warte(120);

  // ---- Gegenprobe 2: schliessen ohne abzuraeumen hinterlaesst einen toten Eintrag ----
  openModal(baueKnoten("Leck"));
  await warte(20);
  closeModalLECK();
  await warte(120);
  pruef("GEGENPROBE geschlossen, aber Eintrag blieb", [offen(), tiefe(), marke()], [false, 1, 1]);
  history.back();
  await warte(120);
  pruef("GEGENPROBE das erste Zurueck laeuft ins Leere", offen(), false);
  overlayStack.length = 0;

  LOG.push("");
  LOG.push("Scanner-Vertrag im Quelltext (nicht mitgeschnitten): __SCAN__");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

seite = seite.replace("__KERN__", KERN).replace("__OHNE__", OHNE).replace("__LECK__", LECK_FN)
seite = seite.replace("__SCAN__", "OK" if scanner_ok else "FEHLT - scanBarcodeLive haengt nicht am Stapel")

io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)
if not scanner_ok:
    print("WARNUNG: scanBarcodeLive() benutzt overlayOpened/overlayClosed nicht wie erwartet")


# --- Selbst fahren statt nur schreiben (28.08.2026) -------------------------------------
# Bis dahin endete dieses Skript nach dem Schreiben der HTML-Datei mit Rueckgabewert 0.
# tools/alle-pruefstaende.py bewertet nur den Rueckgabewert und meldete es deshalb bei jedem
# Durchgang gruen, ohne dass je eine Zusage lief. Acht Pruefstaende waren betroffen - ein
# Drittel der Suite (docs/TROUBLESHOOTING.md 131).
#
# Die Zusagen oben sind UNVERAENDERT. Der gemeinsame Laeufer haengt der erzeugten Seite nur
# einen Beobachter an und liest ihr Protokoll aus; im Browser geoeffnet verhaelt sie sich
# genau wie vorher.
if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pruefstand_lauf import fahren
    _sys.exit(fahren(ZIEL))
