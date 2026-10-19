# -*- coding: utf-8 -*-
u"""
Ausschneide-Pruefstand: Meldet der Austritt ehrlich, wenn er nicht gespeichert wurde - ohne den
mitgenommenen Wochenplan zu gefaehrden?

Befund vom 19.10.2026 (stille Fehler, plans/abgleich-pruefer-2026-10-18.md L8): Scheiterte in
leaveGroup() das Schreiben von `{ groupId: "", plans }`, blieb die alte groupId stehen -
leaveAtomic() hatte die Mitgliedschaft aber schon beendet. Jeder Start landete in "error"
("Die Gruppe ist gerade nicht erreichbar"), und der Toast sagte trotzdem "deine Meals sind
mitgekommen". Seit 19.10.2026 kommt dann ein ehrlicher Toast.

Zweite Messgroesse, aus einem Fehlversuch desselben Tages (f813adf): groupId:"" und der Plan
MUESSEN in EINEM Schreibvorgang stehen. Getrennt kam offline nur der erste an, und ohne
Plan-Baseline gewinnt beim naechsten Start der Cloud-Plan von vor dem Beitritt - die
mitgenommenen Wochen waeren weg (Pushcheck /code-review, docs/TROUBLESHOOTING.md 192).

Geprueft wird der echte leaveGroup(), ausgeschnitten aus index.html. Gestubbt ist alles, was er
aufruft; die vorgespielte Cloud protokolliert jeden Schreibvorgang und lehnt auf Wunsch ab.

GEGENPROBEN aus Git (fest verdrahtet, nicht HEAD):
  * a365436 (vor dem Fix): bei Ablehnung kommt dort der Erfolgs-Toast.
  * f813adf (Fehlversuch): dort geht groupId:"" OHNE Plan hinaus.

    python tools/pruefstand-gruppe-verlassen-zeiger.py
"""
import io, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WURZEL, "tools", "pruefstand-gruppe-verlassen-zeiger.html")
ALT = "a365436"
GETRENNT = "f813adf"


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
    u"""Rumpf einer Funktion, die bei jedem Aufruf eine frische Umgebung baut."""
    leave = schnitt(text.split("\n"), "async function leaveGroup(", "  ")
    rand = u"""
  var CLOUD = { groupId: "g1", plans: "alt" };
  var REGEL = { ablehnen: false };
  var TOASTS = [], SCHREIBEN = [];
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
        SCHREIBEN.push(Object.keys(data).sort().join("+"));
        if (REGEL.ablehnen && ("groupId" in data || "plans" in data)) throw new Error("permission-denied");
        Object.keys(data).forEach(function (k) { CLOUD[k] = data[k]; });
      }
    }
  };
"""
    return rand + leave + \
        "\nreturn { leave: leaveGroup, cloud: CLOUD, regel: REGEL, toasts: TOASTS, schreiben: SCHREIBEN };"


neu = io.open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
def aus_git(c):
    return subprocess.check_output(["git", "show", c + ":index.html"], cwd=WURZEL).decode("utf-8")

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
var GETRENNT = function () { %(getrennt)s };
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
async function fall(fab, ablehnen) {
  var u = fab();
  u.regel.ablehnen = ablehnen;
  await u.leave();
  return { groupId: u.cloud.groupId, toast: u.toasts[u.toasts.length - 1] || "", schreiben: u.schreiben };
}
// groupId nie ohne Plan: jeder Schreibvorgang mit groupId traegt auch plans
function zeigerNieAllein(r) {
  return r.schreiben.every(function (s) { return s.split("+").indexOf("groupId") < 0 || s.split("+").indexOf("plans") >= 0; });
}
var ERFOLG = /mitgekommen/, EHRLICH = /nicht ganz gespeichert/;

(async function () {
  // --- Neuer Stand -------------------------------------------------------
  var r = await fall(NEU, false);
  pruef("NEU normal: groupId in der Cloud ist leer", r.groupId === "", JSON.stringify(r));
  pruef("NEU normal: Erfolgs-Toast", ERFOLG.test(r.toast), r.toast);
  pruef("NEU: groupId geht nur zusammen mit dem Plan hinaus", zeigerNieAllein(r), r.schreiben.join(", "));

  r = await fall(NEU, true);
  pruef("NEU abgelehnt: KEIN Erfolgs-Toast", !ERFOLG.test(r.toast), r.toast);
  pruef("NEU abgelehnt: ehrlicher Toast", EHRLICH.test(r.toast), r.toast);

  // --- Gegenproben -------------------------------------------------------
  r = await fall(ALT, false);
  pruef("GEGENPROBE %(alt_id)s normal: dort klappt es auch", r.groupId === "" && ERFOLG.test(r.toast), JSON.stringify(r));
  r = await fall(ALT, true);
  pruef("GEGENPROBE %(alt_id)s abgelehnt: der Fehler ist messbar (Erfolgs-Toast trotz Fehler)", ERFOLG.test(r.toast), r.toast);
  r = await fall(GETRENNT, false);
  pruef("GEGENPROBE %(getrennt_id)s: dort geht groupId OHNE Plan hinaus", !zeigerNieAllein(r), r.schreiben.join(", "));

  LOG.push(bad ? "FEHLGESCHLAGEN: " + bad + " von " + (ok + bad) : "ALLE " + ok + " PRUEFUNGEN GRUEN");
  document.getElementById("log").textContent = LOG.join("\\n");
})().catch(function (e) {
  document.getElementById("log").textContent = "JS-FEHLER: " + e;
});
</script>
""" % {"neu": fabrik(neu), "alt": fabrik(aus_git(ALT)), "getrennt": fabrik(aus_git(GETRENNT)),
       "alt_id": ALT, "getrennt_id": GETRENNT}

io.open(OUT, "w", encoding="utf-8").write(seite)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(OUT))
