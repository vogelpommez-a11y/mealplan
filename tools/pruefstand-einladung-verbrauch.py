# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand: der Einladungscode wird beim Beitritt verbraucht (17.08.2026).

Punkt 4 des Aufraeum-Plans. Ein weitergereichter Link war dauerhaft eine offene Tuer - wer ihn
je gesehen hat, kam herein, sobald ein Platz frei wurde.

Geprueft wird die Stelle, die am 16.08.2026 schon einmal alles lahmgelegt hat: die REIHENFOLGE
der Riegel in joinGroup(). Die Rueckkehr eines noch bestehenden Mitglieds laeuft ueber
putMember() und muss weiter gehen, auch wenn der Code laengst verbraucht ist. Steht die
used-Pruefung zu weit oben, sperrt der Verbrauch genau die Leute aus, die schon dabei sind -
und das faellt beim Lesen des Codes nicht auf, weil beide Pruefungen fuer sich richtig aussehen.

Was hier NICHT geprueft werden kann: die Firestore-Regeln selbst (kein Node, kein Emulator -
CLAUDE.md Ziffer 12). Der Verbrauch ist erst mit Stufe 2 der Regeln eine harte Grenze; bis
dahin ist die Pruefung hier eine Bequemlichkeit. Siehe firestore.rules.
"""
import io, os

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUELLE = os.path.join(BASIS, "index.html")
ZIEL = os.path.join(BASIS, "tools", "pruefstand-einladung-verbrauch.html")

lines = io.open(QUELLE, encoding="utf-8").read().split("\n")


def schnitt(sig, tiefe=2):
    zu = " " * tiefe + "}"
    for i, z in enumerate(lines):
        if z.startswith(sig):
            for j in range(i, len(lines)):
                if lines[j] == zu:
                    return "\n".join(lines[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


JOIN = schnitt("  async function joinGroup(")
MERGEPLAN = schnitt("  async function mergeOwnPlanIntoGroup(")

# Sicherung gegen einen stillen Fehlschnitt (die Lehre vom 16.08.2026: ein Pruefstand, der
# nichts sagt, hat nicht bestanden).
if "inv.used" not in JOIN:
    raise SystemExit("joinGroup() prueft den Verbrauch nicht - Schnitt oder Code pruefen")
if "istMitglied" not in JOIN:
    raise SystemExit("joinGroup() kennt den Rueckkehr-Fall nicht mehr")

# ---- Gegenprobe: die used-Pruefung an der NAHELIEGENDEN, falschen Stelle ----
# Sie zu den anderen Riegeln nach oben zu ziehen ist die erste Idee, die man hat - und sie
# sperrt jedes bestehende Mitglied aus, das ueber denselben Link zurueckkehrt. Der Pruefstand
# muss das fangen, sonst misst Fall 3 nichts.
USED_ZEILE = '        if (inv.used) { toast("Diese Einladung wurde schon benutzt – frag nach einer neuen."); return; }'
OBEN_NACH = '      if (state.pendingGroupId === inv.gid) { toast("Das ist deine eigene Einladung."); return; }'
if USED_ZEILE not in JOIN:
    raise SystemExit("die used-Zeile sieht anders aus als erwartet - Gegenprobe nicht bildbar")
JOIN_ALT = JOIN.replace(USED_ZEILE + "\n", "")
JOIN_ALT = JOIN_ALT.replace(OBEN_NACH, OBEN_NACH + "\n" + USED_ZEILE.strip().rjust(
    len(USED_ZEILE.strip()) + 6))
if JOIN_ALT == JOIN or "inv.used" not in JOIN_ALT:
    raise SystemExit("Gegenprobe konnte nicht gebildet werden")
JOIN_ALT = JOIN_ALT.replace("async function joinGroup(", "async function joinGroupALT(")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Einladungsverbrauch</title>
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
var state = {}, profile = {}, syncUid = null, syncGid = null;
var groupTransition = false, groupSyncFailed = false, lastGroupAttempt = null, pushTimer = null;
var toasts = [], gemeldet = [];
function toast(t) { toasts.push(t); }
function noteError(k, e) { gemeldet.push(k); }
function clearTimeout_() {}
function smallAvatar(x) { return Promise.resolve(null); }
function copyOwnRecipesToGroup(gid) { kopiert++; return Promise.resolve(); }
// mergeOwnPlanIntoGroup() kommt ECHT herein (nicht gestubbt): sie ist seit dem
// 28.08.2026 Teil des Beitrittspfads, und genau ihr Fehlen hat diesen Pruefstand
// beim ersten echten Lauf rot gemacht (docs/TROUBLESHOOTING.md 128 und 131).
__MERGEPLAN__
function flattenWeek(w) { return w || {}; }
function switchGroup(gid) { gewechselt = gid; return Promise.resolve(); }
function withdrawPendingInvite() { return Promise.resolve(); }

// Aufzeichnung: WELCHER Weg wurde genommen?
var beigetreten = null;   // joinAtomic - ein echter Beitritt
var nachgetragen = null;  // putMember  - eine Rueckkehr
var kopiert = 0, gewechselt = null, invite = null;

window.CloudGroup = {
  enabled: true,
  fetchInvite: function (code) { return Promise.resolve(invite); },
  istMitglied: function (gid, uid) { return Promise.resolve(!!schonMitglied); },
  putMember: function (gid, uid, daten) { nachgetragen = { gid: gid, uid: uid }; return Promise.resolve(); },
  joinAtomic: function (gid, uid, daten) { beigetreten = { gid: gid, uid: uid, via: daten.via }; return Promise.resolve(); },
  // Seit dem 28.08.2026 bringt der Beitritt auch den eigenen Wochenplan mit
  // (mergeOwnPlanIntoGroup, docs/TROUBLESHOOTING.md 128). Ohne diese beiden Attrappen wirft
  // der Lesevorgang, joinGroup faengt es ab und meldet ueber noteError - und die Pruefung
  // "ohne Fehlermeldung" faellt durch, obwohl der Beitritt selbst tadellos laeuft.
  // Genau dieser Fehlschlag hat den Pruefstand am 28.08.2026 zum ersten Mal ROT gemacht:
  // Er lief bis dahin gar nicht (Ziffer 131) und konnte deshalb auch nicht auffallen.
  loadPlansFromServer: function (gid) { return Promise.resolve([]); },
  savePlanWeek: function (gid, woche, patch) { planGeschrieben.push(woche); return Promise.resolve(); }
};
var planGeschrieben = [];
window.CloudSync = { save: function (uid, daten) { return Promise.resolve(); } };
var schonMitglied = false;

__JOIN__
__JOIN_ALT__

function frisch(inv, mitglied) {
  state = { groupId: "", pendingGroupId: "" };
  profile = { name: "Luisa" };
  syncUid = "luisa"; syncGid = null;
  schonMitglied = !!mitglied;
  invite = inv;
  beigetreten = null; nachgetragen = null; kopiert = 0; gewechselt = null;
  toasts = []; gemeldet = [];
  planGeschrieben = [];
}
var OFFEN = { gid: "g1", role: "edit", by: "paddy" };
var BENUTZT = { gid: "g1", role: "edit", by: "paddy", used: true };

(function () {
  // ---- 1. Der Normalfall: offener Code, noch kein Mitglied ----
  frisch(OFFEN, false);
  joinGroup("code1").then(function () {
    pruef("ein offener Code fuehrt zum Beitritt", !!beigetreten, true);
    pruef("und der Code faehrt als via mit", beigetreten && beigetreten.via, "code1");
    pruef("die Gruppe wird gewechselt", gewechselt, "g1");
    pruef("ohne Fehlermeldung", gemeldet.join(",") || 0, 0);
    // Der Plan des Beitretenden wird nachgetragen (Ziffer 128). state.plans ist hier leer,
    // also gibt es nichts zu schreiben - gepruefft wird, dass der Weg fehlerfrei durchlaeuft.
    pruef("der Plan-Nachtrag laeuft ohne Fehler durch", planGeschrieben.length, 0);

    // ---- 2. Verbrauchter Code, noch kein Mitglied: abgewiesen ----
    frisch(BENUTZT, false);
    return joinGroup("code1");
  }).then(function () {
    pruef("ein verbrauchter Code fuehrt NICHT zum Beitritt", beigetreten, null);
    pruef("und sagt auch, warum",
      toasts.length === 1 && toasts[0].indexOf("schon benutzt") !== -1, true);
    // Nichts angefasst - kein halber Beitritt, keine Meals hochgeladen.
    pruef("es wurde nichts in die Gruppe kopiert", kopiert, 0);
    pruef("und die Gruppe nicht gewechselt", gewechselt, null);

    // ---- 3. DER KRITISCHE FALL ----
    // Verbrauchter Code, aber ich bin noch Mitglied: das ist eine Rueckkehr, kein Beitritt.
    // Genau hier haette eine zu frueh stehende used-Pruefung die Leute ausgesperrt, die
    // schon dabei sind. Am 16.08.2026 ist dieser Fall in seiner anderen Form (Zaehler)
    // bereits einmal aufgetreten.
    frisch(BENUTZT, true);
    return joinGroup("code1");
  }).then(function () {
    pruef("ein Mitglied kommt trotz verbrauchtem Code zurueck", !!nachgetragen, true);
    pruef("ueber putMember, nicht ueber joinAtomic", beigetreten, null);
    pruef("und wird nicht abgewiesen",
      toasts.indexOf("Diese Einladung wurde schon benutzt – frag nach einer neuen.") === -1, true);
    pruef("die Rueckkehr fuehrt in dieselbe Gruppe", gewechselt, "g1");

    // ---- 4. Gegenprobe zur Reihenfolge ----
    // Offener Code und schon Mitglied: ebenfalls Rueckkehr. Ohne diesen Fall wuerde Fall 3
    // auch dann gruen, wenn die Rueckkehr generell an istMitglied haengt und der Verbrauch
    // gar nicht mehr geprueft wird.
    frisch(OFFEN, true);
    return joinGroup("code1");
  }).then(function () {
    pruef("auch mit offenem Code bleibt es bei der Rueckkehr", !!nachgetragen, true);
    pruef("und es entsteht kein zweiter Beitritt", beigetreten, null);

    // ---- 5. Ein Code ohne gid bleibt ungueltig ----
    frisch({ role: "edit" }, false);
    return joinGroup("code1");
  }).then(function () {
    pruef("ein Code ohne Gruppe gilt nicht mehr",
      toasts.length === 1 && toasts[0].indexOf("gilt nicht mehr") !== -1, true);
    pruef("und fuehrt zu keinem Beitritt", beigetreten, null);

    // ---- 6. GEGENPROBE ----
    // Derselbe Code mit der used-Pruefung an der naheliegenden, falschen Stelle: oben bei den
    // anderen Riegeln. Dann wird das bestehende Mitglied ausgesperrt. Bleibt diese Zeile
    // gruen, misst Fall 3 nichts.
    frisch(BENUTZT, true);
    return joinGroupALT("code1");
  }).then(function () {
    pruef("GEGENPROBE: zu frueh geprueft sperrt das Mitglied aus", nachgetragen, null);

    LOG.push("");
    LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
    document.getElementById("log").textContent = LOG.join("\\n");
  });
})();
</script>
"""

io.open(ZIEL, "w", encoding="utf-8").write(
    seite.replace("__JOIN_ALT__", JOIN_ALT).replace("__MERGEPLAN__", MERGEPLAN).replace("__JOIN__", JOIN))
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
