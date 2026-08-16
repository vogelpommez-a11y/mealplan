# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand fuer das Mitgliederlimit (16.08.2026).

Geprueft wird die CLIENT-Seite: Sind Beitritt, Austritt und Kontoloeschung wirklich EIN Batch,
und traegt die Migration den Zaehler genau dann nach, wenn sie darf?

Was hier NICHT geprueft werden kann, und das ist wichtig zu wissen: die Firestore-Regeln
selbst. Es gibt kein Node und keinen Emulator im Projekt (CLAUDE.md, Ziffer 12). Die Regeln
sind die verbindliche Grenze und werden im Rules Playground der Firebase Console von Hand
durchgespielt - die neun Szenarien stehen in docs/TESTING.md.

Dieser Pruefstand sichert die andere Haelfte: dass der Client die Regeln ueberhaupt bedienen
KANN. Ein einzelnes deleteDoc statt eines Batches wuerde von der Regel abgelehnt - beim
Konto loeschen sogar STILL, weil deleteBestEffort() genau diesen Fehler verzeiht.
"""
import io, os, re, sys

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-gruppenlimit.html")

lines = io.open(QUELLE, encoding="utf-8").read().split("\n")


def block(start_sig, end_sig):
    """Von der ersten Zeile mit start_sig bis zur ersten folgenden mit end_sig, inklusive."""
    for i, z in enumerate(lines):
        if start_sig in z:
            for j in range(i, len(lines)):
                if end_sig in lines[j]:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("ENDE NICHT GEFUNDEN: " + end_sig)
    raise SystemExit("BLOCK: " + start_sig)


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


# Die drei atomaren Methoden im Original-Wortlaut. Sie stehen im Modul-Block (8 Spaces
# eingerueckt), deshalb ueber block() statt schnitt().
ATOMAR = block("        // ----- Mitgliederlimit: Beitritt und Austritt sind ATOMAR -----",
               "        setCount: function (gid, n)")
MIGRATION = schnitt("  async function migrateMemberCount(")
LIMIT = block("  const MAX_GROUP_MEMBERS", "  const MAX_GROUP_MEMBERS")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Mitgliederlimit</title>
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

// ---- Firestore-Attrappe ----
// Sie zeichnet auf, WAS geschrieben wird und ob es in EINEM Batch landet. Genau darum geht es:
// Die Regel lehnt jeden Einzelvorgang ab, also ist die Buendelung die eigentliche Zusage.
var geschrieben = [];          // alle Commits, je ein Eintrag pro Batch
var einzeln = [];              // Schreibvorgaenge ausserhalb eines Batches
var db = { __fake: true };
function doc() { return { __pfad: Array.prototype.slice.call(arguments, 1).join("/") }; }
function increment(n) { return { __inc: n }; }
function writeBatch() {
  var ops = [];
  return {
    set: function (ref, data, opt) { ops.push({ art: "set", pfad: ref.__pfad, data: data, opt: opt }); },
    update: function (ref, data) { ops.push({ art: "update", pfad: ref.__pfad, data: data }); },
    delete: function (ref) { ops.push({ art: "delete", pfad: ref.__pfad }); },
    commit: function () { geschrieben.push(ops); return Promise.resolve(); }
  };
}
function setDoc(ref, data) { einzeln.push({ art: "set", pfad: ref.__pfad }); return Promise.resolve(); }
function deleteDoc(ref) { einzeln.push({ art: "delete", pfad: ref.__pfad }); return Promise.resolve(); }
function updateDoc(ref, data) { einzeln.push({ art: "update", pfad: ref.__pfad, data: data }); return Promise.resolve(); }
function groupDoc(gid) { return doc(db, "groups", gid); }

// ---- Randstuecke ----
var syncGid = null, syncUid = null, myRole = null, groupMembers = [], groupInfo = null;
var gemeldet = [];
function noteError(k, e) { gemeldet.push(k); }

var CloudGroupAtomar = {
__ATOMAR__
};
window.CloudGroup = CloudGroupAtomar;

__LIMIT__
__MIGRATION__

function frisch() {
  geschrieben = []; einzeln = []; gemeldet = [];
  syncGid = "g1"; syncUid = "ich"; myRole = "owner";
  groupMembers = [{ uid: "ich" }, { uid: "du" }];
  groupInfo = { name: "", owner: "ich", settings: {} };
}
// Der eine Batch, den der letzte Vorgang geschrieben hat.
function letzterBatch() { return geschrieben.length === 1 ? geschrieben[0] : null; }
function zaehlerOp(ops) {
  for (var i = 0; i < ops.length; i++) if (ops[i].art === "update" && ops[i].data && ops[i].data.memberCount) return ops[i].data.memberCount.__inc;
  return null;
}

(function () {
  // ---- Die Konstante selbst ----
  pruef("das Limit steht auf vier", MAX_GROUP_MEMBERS, 4);

  // ---- Beitritt ----
  frisch();
  window.CloudGroup.joinAtomic("g1", "neu", { name: "Neu", role: "edit", via: "code1" }).then(function () {
    var b = letzterBatch();
    pruef("Beitritt schreibt GENAU EINEN Batch", geschrieben.length, 1);
    pruef("und nichts daneben", einzeln.length, 0);
    pruef("der Batch traegt zwei Vorgaenge", b ? b.length : 0, 2);
    pruef("Mitgliedschaft anlegen", b ? b[0].art + " " + b[0].pfad : "", "set groups/g1/members/neu");
    pruef("Zaehler im selben Batch hoch", zaehlerOp(b || []), 1);
    pruef("und zwar am Gruppendokument", b ? b[1].pfad : "", "groups/g1");

    // ---- Austritt ----
    frisch();
    return window.CloudGroup.leaveAtomic("g1", "du");
  }).then(function () {
    var b = letzterBatch();
    pruef("Austritt schreibt GENAU EINEN Batch", geschrieben.length, 1);
    pruef("Austritt: nichts daneben", einzeln.length, 0);
    pruef("Mitgliedschaft loeschen", b ? b[0].art + " " + b[0].pfad : "", "delete groups/g1/members/du");
    pruef("Zaehler im selben Batch runter", zaehlerOp(b || []), -1);

    // ---- increment statt gelesener Wert ----
    // Zwei gleichzeitige Beitritte laegen sonst auf derselben veralteten Basis, und die Regel
    // wiese den zweiten ab. Geprueft wird deshalb der TYP, nicht bloss das Vorzeichen.
    frisch();
    return window.CloudGroup.joinAtomic("g1", "x", {});
  }).then(function () {
    var b = letzterBatch();
    var op = b && b[1] && b[1].data && b[1].data.memberCount;
    pruef("der Zaehler laeuft ueber increment(), nicht ueber einen gelesenen Wert",
      !!(op && typeof op.__inc === "number"), true);

    // ---- Migration ----
    frisch();
    groupInfo = { name: "", owner: "ich" };                   // kein memberCount
    return migrateMemberCount("g1");
  }).then(function () {
    pruef("der Inhaber traegt den fehlenden Zaehler nach",
      einzeln.length === 1 && einzeln[0].data.memberCount, 2);
    pruef("und merkt ihn sich lokal", groupInfo.memberCount, 2);

    // Zweiter Lauf tut nichts mehr - selbstheilend, nicht wiederholend.
    einzeln = [];
    return migrateMemberCount("g1");
  }).then(function () {
    pruef("ein zweiter Lauf schreibt nicht erneut", einzeln.length, 0);

    // Wer nicht Inhaber ist, darf es gar nicht erst versuchen: Die Regel laesst nur ihn an
    // das Gruppendokument, ein Versuch endete in einer gemeldeten Fehlermeldung.
    frisch();
    myRole = "edit";
    groupInfo = { name: "", owner: "du" };
    return migrateMemberCount("g1");
  }).then(function () {
    pruef("ein Mitglied versucht die Migration gar nicht", einzeln.length, 0);
    pruef("und meldet dabei auch keinen Fehler", gemeldet.length, 0);

    // Ein ungeklaertes Leseergebnis (leere Mitgliederliste) darf NICHTS schreiben - sonst
    // stuende der Zaehler auf 0 und niemand kaeme mehr hinein.
    frisch();
    groupInfo = { name: "", owner: "ich" };
    groupMembers = [];
    return migrateMemberCount("g1");
  }).then(function () {
    pruef("bei leerer Mitgliederliste wird nichts geschrieben", einzeln.length, 0);

    // Steht der Zaehler schon, wird er nie angefasst - die Regel verbietet dem Inhaber
    // ausdruecklich, ihn zu aendern.
    frisch();
    groupInfo = { name: "", owner: "ich", memberCount: 2 };
    return migrateMemberCount("g1");
  }).then(function () {
    pruef("ein vorhandener Zaehler bleibt unberuehrt", einzeln.length, 0);

    LOG.push("");
    LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
    document.getElementById("log").textContent = LOG.join("\\n");
  });
})();
</script>
"""

seite = seite.replace("__ATOMAR__", ATOMAR).replace("__MIGRATION__", MIGRATION).replace("__LIMIT__", LIMIT)
io.open(ZIEL, "w", encoding="utf-8").write(seite)
print("geschrieben")
