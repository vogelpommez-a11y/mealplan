# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: "Konto loeschen" meldet sein Ergebnis auch, wenn das Fenster schon zu
ist (25.10.2026, TROUBLESHOOTING 201).

Der Befund: Waehrend "Wird gelöscht …" liess sich das Fenster schliessen (✕, Escape, Hintergrund,
Zurueck, Abbrechen). Das Loeschen lief weiter. Schlug es dann fehl, landete die Meldung in
#del-err eines Fensters, das niemand mehr sah; ging es gut, schloss closeModal() das Fenster,
das inzwischen offen war.

Der Fix (nach einem verworfenen Versuch mit Schliesssperre + 30-s-Notausgang): Schliessen bleibt
erlaubt, aber das Ergebnis haengt an offen() - Fehler bei geschlossenem Fenster als Toast,
closeModal() nur, wenn es noch das eigene Fenster ist. "Abbrechen" ist waehrenddessen aus.
Dazu, weil es dieselbe Fensterlogik ist: fotosGebliebenMelden() fokussiert "Verstanden".

Echter Code: der Zurueck-/Modal-Block (wie pruefstand-zurueck-taste.py), deleteAccountFlow()
und fotosGebliebenMelden(), el()/esc() aus lib/basis.js. Gestubbt: CloudAuth (ein Versprechen,
das der Pruefstand von aussen aufloest), wipeLocalData & Co. als Zaehler.

Gegenprobe: dieselben Funktionen aus GEGEN_COMMIT (vor dem Fix) muessen durchfallen.
"""
import io, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-konto-loeschfenster.html")
# Der Stand vor dem Fix. Fest verdrahtet, damit die Gegenprobe nicht mitwandert.
GEGEN_COMMIT = "48bf979"


def funktion(lines, sig):
    """Ab der Signaturzeile bis zur ersten Zeile, die nur '  }' ist."""
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i + 1, len(lines)):
                if lines[j] == "  }":
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


lines = pm_quelle.lade_seite(QUELLE).split("\n")

# ---- Schnitt 1: Zurueck-Block bis Ende openModal (wie pruefstand-zurueck-taste.py) ----
start = next((i for i, z in enumerate(lines) if "// ---------- Zurueck-Taste (D5) ----------" in z), None)
oeffnen = next((i for i, z in enumerate(lines) if start is not None and i > start and z.startswith("  function openModal(")), None)
ende = next((i for i, z in enumerate(lines) if oeffnen is not None and i > oeffnen and z == "  }"), None)
if start is None or ende is None:
    raise SystemExit("Schnitt Zurueck/Modal nicht gefunden")
KERN = "\n".join(lines[start:ende + 1])
HILFEN = [z for z in lines if z.startswith("  function el(html)") or z.startswith("  function esc(s)")]
if len(HILFEN) != 2:
    raise SystemExit("el()/esc() nicht gefunden - liegen sie noch in lib/basis.js?")

# ---- Schnitt 2: die beiden Funktionen, neu und alt ----
NEU = funktion(lines, "  function deleteAccountFlow() {") + "\n" + funktion(lines, "  function fotosGebliebenMelden(titel) {")
if "const offen = () => document.contains(node);" not in NEU:
    raise SystemExit("deleteAccountFlow() fragt offen() nicht ab - Schnitt oder Code pruefen")

alt_lines = subprocess.check_output(["git", "show", GEGEN_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8").split("\n")
ALT = funktion(alt_lines, "  function deleteAccountFlow() {") + "\n" + funktion(alt_lines, "  function fotosGebliebenMelden(titel) {")
ALT = ALT.replace("function deleteAccountFlow(", "function deleteAccountFlowALT(").replace(
    "function fotosGebliebenMelden(", "function fotosGebliebenMeldenALT(")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Konto-Loeschfenster</title>
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

// ---- Randstuecke fuer den Modal-Block ----
var hoveredCardId = null, liveScanStop = null, groupModalRepaint = null, gemeldet = [];
var appEl = document.createElement("div"), onb = null, renderZahl = 0;
function render() { renderZahl++; }
function noteError(k, e) { gemeldet.push(k); }
var datenGeloescht = false;

// ---- Randstuecke fuer deleteAccountFlow ----
var state = { tab: "home", shares: [], recipes: [], inviteCodes: [] };
var syncGid = "", syncUid = "u1", groupMembers = [];
function groupRole() { return null; }
function confirmModal() { throw new Error("confirmModal unerwartet"); }
function openGroupModal() {}
var gestoppt = 0, gewischt = 0, neuladen = [], toasts = [];
function stopCloudSync() { gestoppt++; }
function wipeLocalData() { gewischt++; return Promise.resolve(false); }
function nachLoeschenNeuladen(t) { neuladen.push(t); }
function toast(t) { toasts.push(t); }
function cloudErrMsg(e) { return "Fehler: " + e.message; }
var FOTOS_GEBLIEBEN = "Fotos blieben.";
var loesen = null;
window.CloudAuth = {
  current: function () { return { providerData: [{ providerId: "password" }] }; },
  deleteAccount: function () { return new Promise(function (ja, nein) { loesen = { ja: ja, nein: nein }; }); }
};

__HILFEN__
__KERN__
__NEU__
__ALT__

function offenZahl() { return modalRoot.childElementCount; }
function q(s) { return modalRoot.querySelector(s); }
function escape() { document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); }
function starten(flow) {
  flow();
  q("#del-pw").value = "geheim";
  q("[data-confirm]").click();
}
// Ein fremdes Fenster mit eigenem Hook - so wie das Meal-Blatt (attemptClose).
var fremdHook = 0;
function fremdesFenster() {
  openModal(el('<div class="modal" role="dialog" aria-label="Fremd"><h2>Fremd</h2></div>'));
  modalCloseHook = function () { fremdHook++; modalCloseHook = null; };
}
function aufraeumen() { modalCloseHook = null; closeModal(); }

(async function () {
  history.pushState({ polster: 1 }, "");
  await warte(30);

  // ---- 1. Vor dem Loeschen: Abbrechen schliesst wie immer ----
  deleteAccountFlow();
  q(".modal-foot [data-close]").click();
  await warte(120);
  pruef("vor dem Loeschen: Abbrechen schliesst", offenZahl(), 0);

  // ---- 2. Waehrend des Loeschens ----
  starten(deleteAccountFlow);
  await warte(20);
  pruef("Knopf zeigt den Fortschritt", q("[data-confirm]").textContent, "Wird gelöscht …");
  pruef("Abbrechen aus (braeche nichts ab), X bleibt bedienbar",
        [q(".modal-foot [data-close]").disabled, q(".modal-head [data-close]").disabled], [true, false]);

  // ---- 3. Fehler bei offenem Fenster: Meldung im Fenster, Knoepfe wieder frei ----
  loesen.nein(new Error("Netz weg"));
  await warte(30);
  pruef("Fehler im offenen Fenster: Meldung dort, kein Toast", [offenZahl(), q("#del-err").textContent, toasts.length], [1, "Fehler: Netz weg", 0]);
  pruef("Knoepfe wieder frei", [q("[data-confirm]").disabled, q(".modal-foot [data-close]").disabled], [false, false]);
  escape();
  await warte(120);

  // ---- 4. Fenster mitten im Loeschen zu, dann Fehler: der Toast sagt es ----
  starten(deleteAccountFlow);
  await warte(20);
  escape();
  await warte(120);
  pruef("Escape schliesst mitten im Loeschen", offenZahl(), 0);
  loesen.nein(new Error("Netz weg"));
  await warte(30);
  pruef("spaeter Fehler erscheint als Toast", toasts, ["Konto nicht gelöscht: Fehler: Netz weg"]);
  pruef("und oeffnet kein Fenster neu", offenZahl(), 0);
  toasts = [];

  // ---- 5. Fenster zu, fremdes Fenster offen, dann Erfolg: das fremde bleibt ----
  starten(deleteAccountFlow);
  await warte(20);
  q(".modal-head [data-close]").click();
  await warte(120);
  fremdesFenster();
  loesen.ja();
  await warte(150);
  pruef("spaeter Erfolg laesst das fremde Fenster offen, dessen Hook unberuehrt",
        [offenZahl(), q(".modal h2") && q(".modal h2").textContent, fremdHook], [1, "Fremd", 0]);
  pruef("und loescht trotzdem lokal + kuendigt Neuladen an", [gewischt, neuladen.length], [1, 1]);
  aufraeumen();
  await warte(120);

  // ---- 6. Erfolg bei offenem Fenster: es schliesst sich selbst ----
  starten(deleteAccountFlow);
  await warte(20);
  loesen.ja();
  await warte(150);
  pruef("Erfolg im offenen Fenster: zu, gewischt", [offenZahl(), gewischt], [0, 2]);
  pruef("kein Fehler gemeldet", gemeldet, []);

  // ---- 7. Fotohinweis: Fokus auf "Verstanden" ----
  fotosGebliebenMelden("Konto gelöscht");
  await warte(80);
  pruef("Fotohinweis fokussiert Verstanden", document.activeElement && document.activeElement.textContent, "Verstanden");
  aufraeumen(); datenGeloescht = false;
  await warte(120);

  // ---- GEGENPROBE: der Stand vor dem Fix ----
  starten(deleteAccountFlowALT);
  await warte(20);
  pruef("GEGENPROBE alt: Abbrechen bleibt mitten im Loeschen an", q(".modal-foot [data-close]").disabled, false);
  var errEl = q("#del-err");
  escape();
  await warte(120);
  loesen.nein(new Error("Netz weg"));
  await warte(30);
  pruef("GEGENPROBE alt: spaeter Fehler steht nur im abgehaengten Fenster, kein Toast",
        [errEl.textContent, document.contains(errEl), toasts.length], ["Fehler: Netz weg", false, 0]);

  starten(deleteAccountFlowALT);
  await warte(20);
  q(".modal-head [data-close]").click();
  await warte(120);
  fremdesFenster();
  loesen.ja();
  await warte(150);
  pruef("GEGENPROBE alt: spaeter Erfolg greift ins fremde Fenster (dessen Hook laeuft)", fremdHook, 1);
  aufraeumen();
  await warte(120);

  fotosGebliebenMeldenALT("Konto gelöscht");
  await warte(80);
  pruef("GEGENPROBE alt: Fotohinweis fokussiert das X", document.activeElement && document.activeElement.textContent, "✕");
  aufraeumen();
  await warte(80);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""

seite = (seite.replace("__HILFEN__", "\n".join(HILFEN)).replace("__KERN__", KERN)
         .replace("__NEU__", NEU).replace("__ALT__", ALT))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL))
