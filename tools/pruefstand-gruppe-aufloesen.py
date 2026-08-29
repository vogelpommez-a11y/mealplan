# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: Gruppe aufloesen darf den Wochenplan nicht mitnehmen (17.08.2026).

Der Befund vom 16.08.2026 (docs/TROUBLESHOOTING.md, Punkt 101): dissolveGroup() loescht erst
in Firestore, danach zieht leaveGroup() seinen keep-Snapshot. Dazwischen feuert der
watchPlans-Listener und raeumt die geloeschten Wochen aus state.plans. Gesichert wird ein
leerer Plan, der anschliessend die letzte eigene Kopie ueberschreibt.

Genau dieses Zeitverhalten bildet der Pruefstand ab: Die Firestore-Attrappe leert beim
Aufloesen state.plans und state.recipes - so, wie es der echte Listener tut.

WICHTIG ist der zweite Durchgang, die Gegenprobe. Er laesst denselben Originalcode mit
zurueckgedrehtem Fix laufen (der Snapshot entsteht wieder erst in leaveGroup()). Faellt er
nicht durch, misst der Pruefstand nichts - siehe die Messfallen in docs/TESTING.md.
"""
import io, os

import sys
# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-gruppe-aufloesen.html")

lines = pm_quelle.lade_seite(QUELLE).split("\n")


def schnitt(sig, tiefe=2):
    """Eine Funktion ab ihrer Signaturzeile bis zur schliessenden Klammer auf `tiefe` Spaces."""
    zu = " " * tiefe + "}"
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i, len(lines)):
                if lines[j] == zu:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


CODES = schnitt("  async function dropAllInviteCodes(")
SNAPSHOT = schnitt("  function snapshotOwnData(")
DISSOLVE = schnitt("  async function dissolveGroup(")
LEAVE = schnitt("  async function leaveGroup(")

# Sicherung gegen einen stillen Fehlschnitt: ohne diese Zeilen prueft der Prueftstand
# nicht das, was er zu pruefen behauptet.
if "snapshotOwnData()" not in DISSOLVE:
    raise SystemExit("dissolveGroup() zieht keinen Snapshot - Schnitt oder Code pruefen")
if "leaveGroup(keep)" not in DISSOLVE:
    raise SystemExit("dissolveGroup() reicht den Snapshot nicht weiter")

# Gegenprobe: der Zustand VOR dem Fix. Der Snapshot faellt weg, leaveGroup() bildet ihn
# wieder selbst - also zu spaet. Wortgleicher Code, nur diese eine Stelle zurueckgedreht.
DISSOLVE_ALT = DISSOLVE.replace("const keep = snapshotOwnData();", "const keep = undefined;")
if DISSOLVE_ALT == DISSOLVE:
    raise SystemExit("Gegenprobe konnte nicht gebildet werden")
DISSOLVE_ALT = DISSOLVE_ALT.replace("async function dissolveGroup(", "async function dissolveGroupALT(")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Gruppe aufloesen</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  var el = document.getElementById("log");
  if (el) el.textContent = LOG.join("\\n");
}

// ---- Randstuecke ----
var state = {}, syncGid = null, syncUid = null, groupInfo = null, groupMembers = [], myRole = null;
var lastPushedRecipes = null, lastPushedJSON = null, lastPushedSlots = null;
var gespeichert = null;              // alle CloudSync.save()-Felder zusammengefuehrt
var speicherLaeufe = [];             // jeder Aufruf einzeln - die REIHENFOLGE ist eine Zusage
var toasts = [];
function noteError(k, e) {}
function toast(t) { toasts.push(t); }
function setViewWeek(w) {}
function leaveGroupState() { syncGid = null; groupInfo = null; groupMembers = []; myRole = null; lastPushedSlots = null; }
function switchGroup(gid) { return Promise.resolve(); }

var geloeschteCodes = [], codeFehler = [];   // codeFehler: diese Codes lassen sich nicht loeschen
window.CloudGroup = {
  leaveAtomic: function (gid, uid) { return Promise.resolve(); },
  deleteInvite: function (code) {
    if (codeFehler.indexOf(code) !== -1) return Promise.reject(new Error("offline"));
    geloeschteCodes.push(code);
    return Promise.resolve();
  }
};
// leaveGroup() speichert seit dem 17.08.2026 ZWEIMAL: erst die Datensicherung (Plan,
// Gruppenzeiger), danach die geleerte Code-Liste. Der Stub fuehrt die Aufrufe deshalb
// zusammen, statt den vorherigen zu ueberschreiben - sonst haette die Reihenfolgeaenderung
// die Plan-Pruefungen still auf undefined laufen lassen.
window.CloudSync = {
  save: function (uid, daten) {
    speicherLaeufe.push(JSON.parse(JSON.stringify(daten)));
    gespeichert = Object.assign(gespeichert || {}, JSON.parse(JSON.stringify(daten)));
    return Promise.resolve();
  }
};

// ---- Die Firestore-Attrappe mit dem entscheidenden Nebeneffekt ----
// dissolveGroupFirestore() raeumt die Gruppe. Danach feuern watchPlans/watchRecipes und
// leeren den lokalen Stand - genau das ist die Falle aus Punkt 101. Hier passiert es
// synchron im selben await, im Echtbetrieb Millisekunden spaeter; fuer den Beweis reicht das,
// denn der fehlerhafte Code sicherte in JEDEM Fall erst nach dem Loeschen.
function dissolveGroupFirestore(gid) {
  state.plans = {};      // <- der Listener raeumt die geloeschten Wochen
  state.recipes = [];
  return Promise.resolve();
}

__CODES__
__SNAPSHOT__
__DISSOLVE__
__DISSOLVE_ALT__
__LEAVE__

// Ein Konto mit echtem Inhalt: zwei Wochen Plan, drei Meals.
function frisch() {
  syncGid = "g1"; syncUid = "ich"; myRole = "owner";
  groupInfo = { name: "Wir", owner: "ich" };
  gespeichert = null; speicherLaeufe = []; toasts = [];
  geloeschteCodes = []; codeFehler = [];
  state = {
    inviteCodes: ["c-alt1", "c-alt2", "c-neu"],   // zwei aus frueheren Gruppen, einer aus dieser
    groupId: "g1",
    viewWeek: "2026-W34",
    recipes: [{ id: "r1", name: "Chia-Pudding" }, { id: "r2", name: "Bowl" }, { id: "r3", name: "Banane" }],
    plans: {
      "2026-W34": { mon: { fr: [{ entryId: "e1", id: "r1" }], mi: [{ entryId: "e2", id: "r2" }] } },
      "2026-W35": { tue: { ab: [{ entryId: "e3", id: "r3" }] } }
    }
  };
}
function planEintraege(plans) {
  var n = 0;
  Object.keys(plans || {}).forEach(function (w) {
    Object.keys(plans[w] || {}).forEach(function (t) {
      Object.keys(plans[w][t] || {}).forEach(function (s) { n += (plans[w][t][s] || []).length; });
    });
  });
  return n;
}

(function () {
  // ================= 1. Der Fix =================
  frisch();
  dissolveGroup().then(function () {
    pruef("nach dem Aufloesen stehen die Planeintraege noch im State", planEintraege(state.plans), 3);
    pruef("beide Wochen sind erhalten", Object.keys(state.plans).sort(), ["2026-W34", "2026-W35"]);
    pruef("die Meals sind mitgekommen", state.recipes.length, 3);
    pruef("das eigene Konto bekommt den vollen Plan geschrieben", planEintraege(gespeichert && gespeichert.plans), 3);
    pruef("und den Gruppenzeiger geleert", gespeichert && gespeichert.groupId, "");
    pruef("die Baseline ist zurueckgesetzt, damit die Meals hochgehen", lastPushedRecipes instanceof Map && lastPushedRecipes.size, 0);

    // ================= 2. Gegenprobe =================
    // Derselbe Code ohne den vorgezogenen Snapshot MUSS den Plan verlieren. Tut er das
    // nicht, prueft Durchgang 1 nichts.
    frisch();
    return dissolveGroupALT();
  }).then(function () {
    var verloren = planEintraege(state.plans) === 0 && planEintraege(gespeichert && gespeichert.plans) === 0;
    pruef("GEGENPROBE: ohne vorgezogenen Snapshot geht der Plan verloren", verloren, true);

    // ================= 3. Verlassen ohne Aufloesen =================
    // Der haeufige Fall: kein Loeschen, kein Listener-Eingriff. Hier bildet leaveGroup()
    // den Snapshot weiterhin selbst - das Verhalten darf sich nicht geaendert haben.
    frisch();
    return leaveGroup();
  }).then(function () {
    pruef("einfaches Verlassen behaelt den Plan", planEintraege(state.plans), 3);
    pruef("einfaches Verlassen behaelt die Meals", state.recipes.length, 3);
    pruef("und schreibt ihn ins eigene Konto", planEintraege(gespeichert && gespeichert.plans), 3);
    pruef("mit freundlicher Rueckmeldung", toasts.length, 1);

    // ================= 4. Verwaiste Einladungscodes =================
    // Punkt 5 des Aufraeum-Plans. Erzeugen darf einen Code nur der Inhaber einer Gruppe -
    // wer sie verlaesst oder aufloest, hat fuer KEINEN seiner Codes mehr eine Verwendung.
    // dissolveGroupFirestore() raeumte nur Codes der gerade aufgeloesten Gruppe weg; Codes
    // aus frueheren Gruppen blieben fuer immer liegen.
    frisch();
    return leaveGroup();
  }).then(function () {
    pruef("beim Verlassen werden alle eigenen Codes geloescht",
      geloeschteCodes.slice().sort(), ["c-alt1", "c-alt2", "c-neu"]);
    pruef("und die Liste ist danach leer", state.inviteCodes, []);
    pruef("die geleerte Liste geht auch ins eigene Konto",
      gespeichert && gespeichert.inviteCodes, []);
    // Die REIHENFOLGE ist die eigentliche Zusage: Ein Firestore-Schreibvorgang resolvt erst
    // mit der Server-Bestaetigung, offline also gar nicht. Stuende das Loeschen der Codes vor
    // der Datensicherung, haenge der Rueckweg des Wochenplans an einer Aufraeumarbeit.
    pruef("der Plan wird VOR dem Code-Aufraeumen gesichert",
      speicherLaeufe.length === 2 && "plans" in speicherLaeufe[0]
        && "inviteCodes" in speicherLaeufe[1], true);

    // Was offline scheitert, bleibt STEHEN - sonst liesse sich das Dokument nie wieder
    // loeschen. Gegenprobe zur Zeile darueber: ohne sie wuerde "Liste leer" auch dann
    // gruen, wenn die Funktion blind alles verwirft.
    frisch();
    codeFehler = ["c-alt2"];
    return leaveGroup();
  }).then(function () {
    pruef("ein fehlgeschlagener Code bleibt in der Liste", state.inviteCodes, ["c-alt2"]);
    pruef("die anderen sind trotzdem weg", geloeschteCodes.slice().sort(), ["c-alt1", "c-neu"]);

    // Und beim Aufloesen ebenso - dort laeuft leaveGroup() als zweiter Schritt.
    frisch();
    return dissolveGroup();
  }).then(function () {
    pruef("auch beim Aufloesen bleibt kein Code zurueck", state.inviteCodes, []);
    // Der Plan darf davon unberuehrt bleiben - beide Aufraeumarbeiten im selben Ablauf.
    pruef("und der Wochenplan ueberlebt das Aufraeumen", planEintraege(state.plans), 3);

    LOG.push("");
    LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
    document.getElementById("log").textContent = LOG.join("\\n");
  });
})();
</script>
"""

seite = (seite.replace("__CODES__", CODES)
              .replace("__SNAPSHOT__", SNAPSHOT)
              .replace("__DISSOLVE_ALT__", DISSOLVE_ALT)
              .replace("__DISSOLVE__", DISSOLVE)
              .replace("__LEAVE__", LEAVE))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)


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
