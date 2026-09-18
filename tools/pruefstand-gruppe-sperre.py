# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: Gruppe aufloesen hinterlaesst keinen Rest (18.09.2026).

Der Befund (docs/TROUBLESHOOTING.md §171): dissolveGroupFirestore() listete Mitglieder, Plaene
und Meals und loeschte danach GENAU diese Liste samt Gruppendokument. Was ein Mitglied in der
Sekunde dazwischen schrieb, stand nicht auf der Liste - es blieb ohne Elterndokument liegen,
fuer niemanden mehr sichtbar oder loeschbar. Ziffer 10 der Datenschutzerklaerung sagt das
Gegenteil zu.

Der Fix: erst sperren (CloudGroup.lock, status "dissolving"), dann listen, dann loeschen. Die
Sperre selbst setzen die Firestore-Regeln durch (nichtGesperrt() in firestore.rules). Die
Attrappe unten bildet GENAU diese Regel nach: Ein Schreibversuch in eine gesperrte Gruppe
wird abgelehnt. Das ist der einzige nachgebaute Teil - dissolveGroupFirestore() ist echter,
ausgeschnittener Code.

Was hier NICHT geprueft werden kann: die Regeln selbst (kein Node, kein Emulator - CLAUDE.md
Ziffer 12). Hier steht nur, dass sie im Repo an den drei Stellen stehen. Ob sie wirken,
zeigt erst ein Versuch am echten Konto, nachdem sie in der Konsole veroeffentlicht sind.

Gegenprobe: derselbe Code ohne die Sperre muss den Rest hinterlassen.
"""
import io, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
REGELN = os.path.join(BASIS, "firestore.rules")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-gruppe-sperre.html")

text = pm_quelle.lade_seite(QUELLE)
lines = text.split("\n")


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


AUFLOESEN = schnitt("  async function dissolveGroupFirestore(")

# Sicherung gegen einen stillen Fehlschnitt.
SPERRE = "      await window.CloudGroup.lock(gid);"
if SPERRE not in AUFLOESEN:
    raise SystemExit("dissolveGroupFirestore() sperrt nicht - Schnitt oder Code pruefen")
if AUFLOESEN.index(SPERRE) > AUFLOESEN.index("Promise.all("):
    raise SystemExit("die Sperre steht NACH dem Listen - genau der Fehler")
if 'lock: function (gid) { return updateDoc(groupDoc(gid), { status: "dissolving" }); }' not in text:
    raise SystemExit("CloudGroup.lock setzt nicht status \"dissolving\"")

# Gegenprobe: der Zustand vor dem 18.09.2026 - die Sperre faellt weg, alles andere bleibt.
AUFLOESEN_ALT = AUFLOESEN.replace(SPERRE, "      /* ohne Sperre */")
AUFLOESEN_ALT = AUFLOESEN_ALT.replace("async function dissolveGroupFirestore(",
                                      "async function dissolveGroupFirestoreALT(")

# Die Regeln: nur Textpruefung, siehe Kopf. Drei Stellen muessen gesperrt sein.
regeln = io.open(REGELN, encoding="utf-8").read()
regel_befund = []
if 'function nichtGesperrt(gid)' not in regeln or '"dissolving"' not in regeln:
    regel_befund.append("nichtGesperrt() fehlt in firestore.rules")
for block in ("match /groups/{gid}/plans/{weekKey}", "match /groups/{gid}/recipes/{recipeId}",
              "match /groups/{gid}/members/{uid}"):
    i = regeln.find(block)
    ende = regeln.find("\n    match ", i + 1)
    teil = regeln[i:ende if ende != -1 else len(regeln)]
    if i == -1 or "nichtGesperrt(gid)" not in teil:
        regel_befund.append("keine Sperre in " + block)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Gruppe sperren</title>
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
var REGEL_BEFUND = __REGEL_BEFUND__;

// ---- Randstuecke ----
var state = {}, schritte = [];
function noteError(k, e) {}

// ---- Der Server: eine Gruppe mit Unterkollektionen ----
var server, sperreFehler, zwischenrufer;
function frisch() {
  server = {
    gruppe: { owner: "ich", status: "active", memberCount: 2 },
    members: { ich: {}, du: {} },
    plans: { "2026-W38": {}, "2026-W39": {} },
    recipes: { r1: {}, r2: {} },
    invites: { c1: { gid: "g1" } }
  };
  state = { inviteCodes: ["c1"] };
  schritte = []; sperreFehler = null; zwischenrufer = true;
}
// Nachbau der Regel nichtGesperrt(): Schreiben in eine gesperrte (oder geloeschte) Gruppe
// wird abgelehnt. Mehr ist an den Regeln hier nicht nachgebaut.
function mitgliedSchreibtPlan(woche) {
  if (!server.gruppe || server.gruppe.status === "dissolving") return false;
  server.plans[woche] = {};
  return true;
}
var abgelehnt = null;
window.CloudGroup = {
  lock: function (gid) {
    schritte.push("sperren");
    if (sperreFehler) return Promise.reject(sperreFehler);
    server.gruppe.status = "dissolving";
    return Promise.resolve();
  },
  fetchMembers: function (gid) {
    schritte.push("listen");
    return Promise.resolve({ members: Object.keys(server.members).map(function (u) { return { uid: u }; }) });
  },
  loadPlans: function (gid) {
    var liste = Object.keys(server.plans).map(function (w) { return { week: w }; });
    // Die Falle: Ein Mitglied schreibt GENAU nachdem gelistet wurde.
    if (zwischenrufer) abgelehnt = !mitgliedSchreibtPlan("2026-W40");
    return Promise.resolve(liste);
  },
  dissolve: function (gid, uids, wochen, ids) {
    schritte.push("loeschen");
    uids.forEach(function (u) { delete server.members[u]; });
    wochen.forEach(function (w) { delete server.plans[w]; });
    ids.forEach(function (i) { delete server.recipes[i]; });
    server.gruppe = null;
    return Promise.resolve();
  },
  fetchInvite: function (code) { return Promise.resolve(server.invites[code] || null); },
  deleteInvite: function (code) { delete server.invites[code]; return Promise.resolve(); }
};
window.CloudSync = {
  loadRecipes: function (pfad) {
    return Promise.resolve(Object.keys(server.recipes).map(function (i) { return { id: i }; }));
  }
};
function reste() {
  return Object.keys(server.members).concat(Object.keys(server.plans), Object.keys(server.recipes));
}

__AUFLOESEN__
__AUFLOESEN_ALT__

(function () {
  pruef("die Regeln sperren plans, recipes und den Beitritt (nur Text, s. Kopf)", REGEL_BEFUND, []);

  // ================= 1. Der Fix =================
  frisch();
  dissolveGroupFirestore("g1").then(function () {
    pruef("erst sperren, dann listen, dann loeschen", schritte, ["sperren", "listen", "loeschen"]);
    pruef("das Mitglied, das dazwischen schreibt, wird abgelehnt", abgelehnt, true);
    pruef("unter der Gruppe bleibt NICHTS zurueck", reste(), []);
    pruef("das Gruppendokument ist weg", server.gruppe, null);
    pruef("der eigene Einladungscode ist mit weg", Object.keys(server.invites), []);

    // ================= 2. Gegenprobe =================
    frisch();
    return dissolveGroupFirestoreALT("g1");
  }).then(function () {
    pruef("GEGENPROBE: ohne Sperre bleibt der Plan des Mitglieds als Rest liegen", reste(), ["2026-W40"]);

    // ================= 3. Die Sperre scheitert (offline) =================
    frisch();
    zwischenrufer = false;
    sperreFehler = { code: "unavailable" };
    return dissolveGroupFirestore("g1").then(function () { return "durch"; }, function () { return "abgebrochen"; });
  }).then(function (ergebnis) {
    pruef("scheitert die Sperre, bricht das Aufloesen ab", ergebnis, "abgebrochen");
    pruef("und es wird nichts geloescht", schritte, ["sperren"]);
    pruef("die Gruppe steht unveraendert", server.gruppe && server.gruppe.status, "active");

    // ================= 4. Die Gruppe gibt es schon nicht mehr =================
    // Ohne Gruppendokument kann niemand schreiben (die Regeln lesen es) - aufgeraeumt wird trotzdem.
    frisch();
    zwischenrufer = false;
    sperreFehler = { code: "not-found" };
    return dissolveGroupFirestore("g1").then(function () { return "durch"; }, function () { return "abgebrochen"; });
  }).then(function (ergebnis) {
    pruef("bei not-found wird trotzdem aufgeraeumt", ergebnis, "durch");
    pruef("und es bleibt nichts zurueck", reste(), []);

    LOG.push("");
    LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
    document.getElementById("log").textContent = LOG.join("\\n");
  });
})();
</script>
"""

import json
seite = (seite.replace("__REGEL_BEFUND__", json.dumps(regel_befund))
              .replace("__AUFLOESEN_ALT__", AUFLOESEN_ALT)
              .replace("__AUFLOESEN__", AUFLOESEN))
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben: " + ZIEL)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(ZIEL))
