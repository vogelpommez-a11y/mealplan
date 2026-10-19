# -*- coding: utf-8 -*-
u"""
Ausschneide-Pruefstand: Bleibt nach dem Verlassen einer Gruppe die alte groupId in der Cloud stehen?

Befund vom 19.10.2026 (stille Fehler, plans/abgleich-pruefer-2026-10-18.md L8): leaveGroup()
schrieb `groupId: ""` und den eigenen Plan in EINEM Vorgang. Lehnte die Regel den Plan ab, blieb
auch die alte groupId stehen - leaveAtomic() hatte die Mitgliedschaft da aber schon beendet. Der
naechste Start wollte in eine Gruppe, die ihn nicht mehr liest ("error"), zeigte bei JEDEM Start
"Die Gruppe ist gerade nicht erreichbar", und groupSyncFailed hielt den eigenen Plan aus der
Cloud. Der Toast sagte trotzdem "deine Meals sind mitgekommen".

Seit 19.10.2026 ist `groupId: ""` ein eigener Schreibvorgang, und scheitert auch der, sagt der
Toast es ehrlich.

Geprueft wird der echte leaveGroup(), ausgeschnitten aus index.html. Gestubbt ist alles, was er
aufruft (CloudGroup, Plan-Baseline, Einladungscodes, switchGroup, toast) - die Messgroesse ist
allein, was in der vorgespielten Cloud steht und welcher Toast kommt.

GEGENPROBE: Dieselben Faelle gegen leaveGroup() aus Commit ALT (vor dem Fix, aus Git gelesen).
Dort MUSS bei abgelehntem Plan die alte groupId stehen bleiben und der Erfolgs-Toast kommen.

    python tools/pruefstand-gruppe-verlassen-zeiger.py
"""
import io, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WURZEL, "tools", "pruefstand-gruppe-verlassen-zeiger.html")
# Letzter Stand VOR dem Fix. Fest verdrahtet, nicht HEAD (sonst vergliche die Gegenprobe nach
# dem Commit den neuen Stand mit sich selbst).
ALT = "a365436"


def schnitt(zeilen, sig, einzug):
    u"""Funktion ab `sig` bis zur schliessenden Klammer auf derselben Einrueckung."""
    for i, z in enumerate(zeilen):
        if z.startswith(einzug + sig):
            for j in range(i + 1, len(zeilen)):
                if zeilen[j].rstrip() == einzug + "}":
                    return "\n".join(zeilen[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


def fabrik(text):
    u"""Liefert den Rumpf einer Funktion, die bei jedem Aufruf eine frische Umgebung baut."""
    leave = schnitt(text.split("\n"), "async function leaveGroup(", "  ")
    rand = u"""
  var CLOUD = { groupId: "g1", plans: "alt" };
  var REGEL = { planAblehnen: false, allesAblehnen: false };
  var TOASTS = [];
  var syncGid = "g1", syncUid = "ich", myRole = "edit";
  var lastPushedRecipes = null, lastPushedJSON = null;
  var state = { groupId: "g1", recipes: [{ id: "r1" }], plans: { "2026-W43": {} }, inviteCodes: [], viewWeek: 0 };
  function noteError() {}
  function snapshotOwnData() { return { recipes: state.recipes, plans: state.plans }; }
  function ohneFremdbezug(recipes, plans) { return { recipes: recipes, plans: plans }; }
  function leaveGroupState() { syncGid = null; myRole = null; }
  function setViewWeek() {}
  function planSlots() { return []; }
  function setPlanBase() {}
  async function pruneOwnRecipes() {}
  async function dropAllInviteCodes() {}
  async function switchGroup() {}
  function toast(t) { TOASTS.push(t); }
  var window = {
    CloudGroup: {
      anonymizeMyRecipes: async function () {},
      anonymizeMyPlanAssignments: async function () {},
      leaveAtomic: async function () {}
    },
    CloudSync: {
      save: async function (uid, data) {
        if (REGEL.allesAblehnen) throw new Error("permission-denied");
        if (REGEL.planAblehnen && "plans" in data) throw new Error("permission-denied");
        Object.keys(data).forEach(function (k) { CLOUD[k] = data[k]; });
      }
    }
  };
"""
    return rand + leave + "\nreturn { leave: leaveGroup, cloud: CLOUD, regel: REGEL, toasts: TOASTS };"


neu = io.open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
alt = subprocess.check_output(["git", "show", ALT + ":index.html"], cwd=WURZEL).decode("utf-8")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Gruppe verlassen: Zeiger</title>
<pre id="log"></pre>
<script>
window.onerror = function (m, s, z) {
  document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
  return true;
};
</script>
<script>
var NEU = function () { %(neu)s };
var ALT = function () { %(alt)s };
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
async function fall(fab, regel) {
  var u = fab();
  Object.keys(regel).forEach(function (k) { u.regel[k] = regel[k]; });
  await u.leave();
  return { groupId: u.cloud.groupId, toast: u.toasts[u.toasts.length - 1] || "" };
}
var ERFOLG = /mitgekommen/, EHRLICH = /nicht ganz gespeichert/;

(async function () {
  // --- Neuer Stand -------------------------------------------------------
  var r = await fall(NEU, {});
  pruef("NEU normal: groupId in der Cloud ist leer", r.groupId === "", JSON.stringify(r));
  pruef("NEU normal: Erfolgs-Toast", ERFOLG.test(r.toast), r.toast);

  r = await fall(NEU, { planAblehnen: true });
  pruef("NEU Plan abgelehnt: groupId in der Cloud ist trotzdem leer", r.groupId === "", JSON.stringify(r));
  pruef("NEU Plan abgelehnt: Erfolgs-Toast (die Meals liegen lokal, der Abgleich holt sie nach)", ERFOLG.test(r.toast), r.toast);

  r = await fall(NEU, { allesAblehnen: true });
  pruef("NEU alles abgelehnt: KEIN Erfolgs-Toast", !ERFOLG.test(r.toast), r.toast);
  pruef("NEU alles abgelehnt: ehrlicher Toast", EHRLICH.test(r.toast), r.toast);

  // --- Gegenprobe gegen den alten Stand ---------------------------------
  r = await fall(ALT, {});
  pruef("GEGENPROBE ALT (%(alt_id)s) normal: dort klappt es auch", r.groupId === "" && ERFOLG.test(r.toast), JSON.stringify(r));
  r = await fall(ALT, { planAblehnen: true });
  pruef("GEGENPROBE ALT Plan abgelehnt: der Fehler ist messbar (alte groupId bleibt)", r.groupId === "g1", JSON.stringify(r));
  pruef("GEGENPROBE ALT Plan abgelehnt: und trotzdem Erfolgs-Toast", ERFOLG.test(r.toast), r.toast);
  r = await fall(ALT, { allesAblehnen: true });
  pruef("GEGENPROBE ALT alles abgelehnt: Erfolgs-Toast trotz Fehler", ERFOLG.test(r.toast), r.toast);

  LOG.push(bad ? "FEHLGESCHLAGEN: " + bad + " von " + (ok + bad) : "ALLE " + ok + " PRUEFUNGEN GRUEN");
  document.getElementById("log").textContent = LOG.join("\\n");
})().catch(function (e) {
  document.getElementById("log").textContent = "JS-FEHLER: " + e;
});
</script>
""" % {"neu": fabrik(neu), "alt": fabrik(alt), "alt_id": ALT}

io.open(OUT, "w", encoding="utf-8").write(seite)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(OUT))
