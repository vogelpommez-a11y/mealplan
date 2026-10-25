# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: "Konto loeschen" laesst sich waehrend des Loeschens nicht schliessen
(25.10.2026, Pushcheck-Hinweis vom selben Tag).

Der Befund: Waehrend "Wird gelöscht …" schlossen Abbrechen, ✕, Escape, der Hintergrund und die
Zurueck-Taste das Fenster. Das Loeschen lief weiter; schlug es fehl, landete die Meldung in
#del-err eines Fensters, das niemand mehr sah. Der Fix: ein modalCloseHook, der sich bei jeder
Weigerung neu anlegt (closeModal() leert ihn vor dem Aufruf), und ausgegraute Schliessknoepfe.

Dazu, weil es dieselbe Fensterlogik ist: fotosGebliebenMelden() setzt den Fokus auf
"Verstanden" statt auf das ✕.

Echter Code: der Zurueck-/Modal-Block (wie pruefstand-zurueck-taste.py), deleteAccountFlow()
und fotosGebliebenMelden(), el()/esc() aus lib/basis.js. Gestubbt: CloudAuth (ein Versprechen,
das der Pruefstand von aussen aufloest), wipeLocalData & Co. als Zaehler.

Gegenprobe: dieselben Funktionen aus GEGEN_COMMIT (vor dem Fix) muessen durchfallen.
"""
import io, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-konto-schliesssperre.html")
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
offen = next((i for i, z in enumerate(lines) if start is not None and i > start and z.startswith("  function openModal(")), None)
ende = next((i for i, z in enumerate(lines) if offen is not None and i > offen and z == "  }"), None)
if start is None or ende is None:
    raise SystemExit("Schnitt Zurueck/Modal nicht gefunden")
KERN = "\n".join(lines[start:ende + 1])
HILFEN = [z for z in lines if z.startswith("  function el(html)") or z.startswith("  function esc(s)")]
if len(HILFEN) != 2:
    raise SystemExit("el()/esc() nicht gefunden - liegen sie noch in lib/basis.js?")

# ---- Schnitt 2: die beiden Funktionen, neu und alt ----
NEU = funktion(lines, "  function deleteAccountFlow() {") + "\n" + funktion(lines, "  function fotosGebliebenMelden(titel) {")
if "modalCloseHook = schliessSperre" not in NEU:
    raise SystemExit("deleteAccountFlow() setzt die Schliesssperre nicht - Schnitt oder Code pruefen")
# Die einzige Abweichung vom Produktionscode: der Notausgang nach 1 s statt 30 s, sonst
# wartete der Pruefstand eine halbe Minute. Fall 2 dauert rund 0,3 s, bleibt also darunter;
# und unter 1,5 s, weil pruefstand_lauf.py so lange Ruhe im Protokoll als "fertig" wertet.
FRIST = "const SPERRE_MAX_MS = 30000;"
if FRIST not in NEU:
    raise SystemExit("Notausgang nicht gefunden: " + FRIST)
NEU = NEU.replace(FRIST, "const SPERRE_MAX_MS = 1000;")

alt_lines = subprocess.check_output(["git", "show", GEGEN_COMMIT + ":index.html"], cwd=BASIS).decode("utf-8").split("\n")
ALT = funktion(alt_lines, "  function deleteAccountFlow() {") + "\n" + funktion(alt_lines, "  function fotosGebliebenMelden(titel) {")
ALT = ALT.replace("function deleteAccountFlow(", "function deleteAccountFlowALT(").replace(
    "function fotosGebliebenMelden(", "function fotosGebliebenMeldenALT(")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Konto-Schliesssperre</title>
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

function offen() { return modalRoot.childElementCount > 0; }
function tiefe() { return overlayStack.length; }
function q(s) { return modalRoot.querySelector(s); }
function escape() { document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true })); }
function starten(flow) {
  flow();
  q("#del-pw").value = "geheim";
  q("[data-confirm]").click();
}
// Alle fuenf Schliesswege nacheinander; nach jedem: noch offen?
async function alleWege() {
  var r = [];
  q(".modal-foot [data-close]").click(); r.push(offen());
  if (offen()) { q(".modal-head [data-close]").click(); r.push(offen()); } else r.push(false);
  if (offen()) { escape(); r.push(offen()); } else r.push(false);
  if (offen()) { q(".overlay").dispatchEvent(new MouseEvent("mousedown", { bubbles: true })); r.push(offen()); } else r.push(false);
  if (offen()) { history.back(); await warte(120); r.push(offen()); } else r.push(false);
  return r;
}

(async function () {
  history.pushState({ polster: 1 }, "");
  await warte(30);

  // ---- 1. Vor dem Loeschen schliesst Abbrechen wie immer ----
  deleteAccountFlow();
  pruef("Fenster offen, ein Eintrag auf dem Stapel", [offen(), tiefe()], [true, 1]);
  pruef("vor dem Loeschen haengt kein Hook (sonst erbte ihn ein Folgefenster)", modalCloseHook, null);
  q(".modal-foot [data-close]").click();
  await warte(120);
  pruef("vor dem Loeschen: Abbrechen schliesst, Stapel leer", [offen(), tiefe()], [false, 0]);

  // ---- 2. Waehrend des Loeschens: kein Weg schliesst ----
  starten(deleteAccountFlow);
  await warte(20);
  pruef("Knopf zeigt den Fortschritt", q("[data-confirm]").textContent, "Wird gelöscht …");
  pruef("Abbrechen und X ausgegraut", [q(".modal-foot [data-close]").disabled, q(".modal-head [data-close]").disabled], [true, true]);
  pruef("Fokus auf der Ueberschrift, Fenster aria-busy", [document.activeElement === q(".modal-head h2"), q(".modal").getAttribute("aria-busy")], [true, "true"]);
  // Ausgegraute Knoepfe feuern kein click - die Sperre muss trotzdem halten, falls doch
  // jemand closeModal() ruft. Deshalb direkt UND ueber Escape, Hintergrund, Zurueck.
  pruef("closeModal() wird verweigert", [closeModal(), offen()], [false, true]);
  pruef("auch ein zweites Mal (Hook legt sich neu an)", [closeModal(), offen()], [false, true]);
  pruef("Escape / Hintergrund / Zurueck lassen es offen", (await alleWege()).slice(2), [true, true, true]);
  pruef("Zurueck legt den Eintrag wieder an", tiefe(), 1);
  pruef("pmZurueck() schluckt die Taste, Fenster bleibt", [window.pmZurueck(), await warte(120), offen()], [true, undefined, true]);

  // ---- 3. Fehler: die Meldung steht in einem SICHTBAREN Fenster, danach normal ----
  loesen.nein(new Error("Netz weg"));
  await warte(30);
  pruef("nach dem Fehler: Fenster offen, Meldung sichtbar", [offen(), q("#del-err").textContent], [true, "Fehler: Netz weg"]);
  pruef("Knoepfe wieder frei", [q("[data-confirm]").disabled, q(".modal-foot [data-close]").disabled, q(".modal-head [data-close]").disabled], [false, false, false]);
  pruef("Fokus zurueck auf Konto loeschen, Hook weg", [document.activeElement === q("[data-confirm]"), modalCloseHook], [true, null]);
  escape();
  await warte(120);
  pruef("Escape schliesst wieder, Stapel leer", [offen(), tiefe()], [false, 0]);

  // ---- 3b. Notausgang: das Loeschen antwortet nie ----
  starten(deleteAccountFlow);
  await warte(1200);
  pruef("nach der Frist: Fenster offen, Hinweis steht", [offen(), q("#del-err").textContent], [true, "Das dauert länger als sonst. Prüf deine Verbindung."]);
  pruef("Abbrechen und X wieder frei, Knopf bleibt bei Wird geloescht", [q(".modal-foot [data-close]").disabled, q(".modal-head [data-close]").disabled, q("[data-confirm]").disabled], [false, false, true]);
  escape();
  await warte(120);
  pruef("Escape schliesst nach der Frist", [offen(), tiefe()], [false, 0]);
  loesen.nein(new Error("spaet"));   // der haengende Vorgang endet irgendwann - darf nichts anrichten
  await warte(60);
  pruef("spaetes Ende oeffnet nichts neu", offen(), false);

  // ---- 4. Erfolg: das Fenster schliesst sich selbst ----
  starten(deleteAccountFlow);
  await warte(20);
  loesen.ja();
  await warte(150);
  pruef("nach Erfolg: zu, gewischt, Neuladen angekuendigt", [offen(), gewischt, neuladen.length, tiefe()], [false, 1, 1, 0]);
  pruef("kein Fehler gemeldet", gemeldet, []);

  // ---- 5. Fotohinweis: Fokus auf "Verstanden" ----
  fotosGebliebenMelden("Konto gelöscht");
  await warte(80);
  pruef("Fotohinweis fokussiert Verstanden", document.activeElement && document.activeElement.textContent, "Verstanden");
  modalCloseHook = null; closeModal(); datenGeloescht = false;
  await warte(80);

  // ---- GEGENPROBE: der Stand vor dem Fix - JEDER der fuenf Wege schloss mitten im Loeschen ----
  var wege = {
    "Abbrechen": function () { q(".modal-foot [data-close]").click(); },
    "X": function () { q(".modal-head [data-close]").click(); },
    "Escape": escape,
    "Hintergrund": function () { q(".overlay").dispatchEvent(new MouseEvent("mousedown", { bubbles: true })); },
    "Zurueck": function () { history.back(); }
  };
  var zu = [];
  for (var w in wege) {
    starten(deleteAccountFlowALT);
    await warte(20);
    var errEl = q("#del-err");
    wege[w]();
    await warte(120);
    zu.push(w + ":" + (offen() ? "offen" : "zu"));
    loesen.nein(new Error("Netz weg"));
    await warte(30);
    if (w === "Abbrechen") {
      pruef("GEGENPROBE alt: Fehlertext steht in einem abgehaengten Fenster", [errEl.textContent, document.contains(errEl)], ["Fehler: Netz weg", false]);
    }
  }
  pruef("GEGENPROBE alt: alle fuenf Wege schliessen mitten im Loeschen", zu, ["Abbrechen:zu", "X:zu", "Escape:zu", "Hintergrund:zu", "Zurueck:zu"]);
  overlayStack.length = 0;
  await warte(120);

  fotosGebliebenMeldenALT("Konto gelöscht");
  await warte(80);
  pruef("GEGENPROBE alt: Fotohinweis fokussiert das X", document.activeElement && document.activeElement.textContent, "✕");
  modalCloseHook = null; closeModal();
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
