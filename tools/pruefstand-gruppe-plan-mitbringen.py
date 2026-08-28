# -*- coding: utf-8 -*-
u"""
Der eigene Wochenplan beim Gruppenbeitritt - und die Migration, die in der Gruppe
nichts zu suchen hat.

ZWEI Aenderungen vom 28.08.2026, beide vom Nutzer abgenommen:

1. `mergeOwnPlanIntoGroup(gid)` - EIN Weg fuer zwei Aufrufer. `enterGroupSync()` ERSETZT
   `state.plans` durch den Gruppenplan; hochgeladen wurde der eigene Plan aber nur beim
   Owner (prepareGroup/finalizeGroupActivation). Die Woche des Beitretenden war damit
   lautlos weg. Nachgetragen werden nur Slots, die in der Gruppe NOCH LEER sind - wer
   schon geplant hat, behaelt seinen Eintrag.

   Gelesen wird vom SERVER: Ein leeres Ergebnis traegt hier eine Entscheidung ("der Slot
   ist frei"), und der Cache hat die Plaene einer gerade beigetretenen Gruppe noch nie
   gesehen - dieselbe Falle wie docs/TROUBLESHOOTING.md 126. Scheitert das Lesen, wird
   NICHTS geschrieben.

2. `dedupeAgainstCatalog()` laeuft in einer Gruppe gar nicht mehr. `state.dedupeV1` steht
   nur im localStorage, ist also ein GERAETE-Flag - in der Gruppe raeumte die Migration
   aber den GEMEINSAMEN Bestand auf, und jedes weitere Geraet liess sie erneut darauf los.

Messgroessen:

    * ein belegter Gruppen-Slot wird beim Beitritt NIE ueberschrieben
    * ein leerer Gruppen-Slot bekommt den Eintrag des Beitretenden
    * ein gescheitertes Lesen schreibt NICHTS
    * dedupeAgainstCatalog() fasst einen Gruppenbestand nicht an und setzt das Flag nicht

Gegenproben: die alte Fassung (Cache-Weg bzw. Migration in der Gruppe) muss ROT werden.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-gruppe-plan-mitbringen.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, anhang=u""):
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1]) + anhang


UMFELD = u"""
var syncUid = "ich", syncGid = null;
var state = { recipes: [], plans: {}, favs: [], planned: {}, dedupeV1: false };
function noteError(){}
function save(){}
function canonJSON(v){ return JSON.stringify(v); }

// --- Falsches Firestore mit luegendem Cache (wie pruefstand-gruppe-beitritt-cache.py) ---
var gruppenPlaene = {}, gesehen = false, serverOffline = false, geschrieben = [];
window.CloudGroup = {
  loadPlans: function () {                    // Cache-Weg: wirft nie
    if (!gesehen) return Promise.resolve([]);
    return Promise.resolve(Object.keys(gruppenPlaene).map(function (w) {
      return { week: w, fields: JSON.parse(JSON.stringify(gruppenPlaene[w])) };
    }));
  },
  loadPlansFromServer: function () {          // Server-Weg: wirft offline
    if (serverOffline) return Promise.reject(new Error("unavailable"));
    return Promise.resolve(Object.keys(gruppenPlaene).map(function (w) {
      return { week: w, fields: JSON.parse(JSON.stringify(gruppenPlaene[w])) };
    }));
  },
  savePlanWeek: function (gid, week, patch) {
    geschrieben.push(week + ":" + Object.keys(patch).filter(function (k) {
      return k !== "by" && k !== "at";
    }).sort().join(","));
    gruppenPlaene[week] = gruppenPlaene[week] || {};
    Object.keys(patch).forEach(function (k) { gruppenPlaene[week][k] = patch[k]; });
    return Promise.resolve();
  }
};

// flattenWeek() der App braucht DAYS/MEALS und makeEmptyPlan(); hier reicht die flache
// Form direkt - der Pruefstand misst mergeOwnPlanIntoGroup(), nicht flattenWeek().
var meinFlach = {};
function flattenWeek(plan) { return JSON.parse(JSON.stringify(meinFlach[plan.__name] || {})); }
function setzeMeinePlaene(wochen) {
  state.plans = {}; meinFlach = {};
  Object.keys(wochen).forEach(function (w) {
    state.plans[w] = { __name: w };
    meinFlach[w] = wochen[w];
  });
}
function frischerStand() { gruppenPlaene = {}; geschrieben = []; gesehen = false; serverOffline = false; }

// Die alte Fassung fuer die Gegenprobe: identisch, nur ueber den Cache-Weg.
async function mergeOwnPlanIntoGroupAlt(gid) {
  var existing = await window.CloudGroup.loadPlans(gid);
  var have = {};
  existing.forEach(function (w) { have[w.week] = w.fields || {}; });
  for (var wk of Object.keys(state.plans || {})) {
    var flat = flattenWeek(state.plans[wk]);
    var already = have[wk] || {};
    var missing = {};
    Object.keys(flat).forEach(function (slot) { if (!already[slot]) missing[slot] = flat[slot]; });
    if (Object.keys(missing).length) {
      await window.CloudGroup.savePlanWeek(gid, wk, Object.assign(missing, { by: syncUid, at: Date.now() }));
    }
  }
}

// --- Umfeld fuer dedupeAgainstCatalog() -------------------------------------------------
var COOKBOOK = [
  { id: "kat1", name: "Quark-Schale", category: "Fruehstueck", nutrition: { kcal: 400 },
    ingredients: [], steps: [], time: 5, tags: [], mealPrep: false }
];
function sanitizeRecipe(r) {
  return { name: r.name, category: r.category, nutrition: r.nutrition, ingredients: r.ingredients,
           steps: r.steps, time: r.time, tags: r.tags, mealPrep: r.mealPrep };
}
function rewritePlanIds(){}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Leere Gruppe: meine ganze Woche kommt mit ---");
frischerStand(); gesehen = true;
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"], tue_ab: ["r3"] } });
await mergeOwnPlanIntoGroup("g1");
pr("alle drei Slots angekommen",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["r1"]' &&
   JSON.stringify(gruppenPlaene["2026-W35"].tue_ab) === '["r3"]');
pr("ein Schreibvorgang je Woche", geschrieben.length === 1, JSON.stringify(geschrieben));

console.log("--- 2. Belegte Slots werden NICHT ueberschrieben ---");
frischerStand(); gesehen = true;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"], tue_ab: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"], tue_ab: ["r3"] } });
await mergeOwnPlanIntoGroup("g1");
pr("fremder Fruehstuecks-Slot unangetastet",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["OWNER"]',
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr));
pr("fremder Abend-Slot unangetastet",
   JSON.stringify(gruppenPlaene["2026-W35"].tue_ab) === '["OWNER"]');
pr("mein freier Slot kam hinzu",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_mi) === '["r2"]');
pr("nur der fehlende Slot wurde geschrieben", geschrieben.join("|") === "2026-W35:mon_mi",
   geschrieben.join("|"));

console.log("--- 3. Alles schon belegt: gar kein Schreibvorgang ---");
frischerStand(); gesehen = true;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"], mon_mi: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] } });
await mergeOwnPlanIntoGroup("g1");
pr("nichts geschrieben", geschrieben.length === 0, JSON.stringify(geschrieben));

console.log("--- 4. Mehrere Wochen, gemischt ---");
frischerStand(); gesehen = true;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] },
                   "2026-W36": { sun_sn: ["r4"] } });
await mergeOwnPlanIntoGroup("g1");
pr("W35 nur ergaenzt", JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["OWNER"]' &&
   JSON.stringify(gruppenPlaene["2026-W35"].mon_mi) === '["r2"]');
pr("W36 komplett neu", JSON.stringify(gruppenPlaene["2026-W36"].sun_sn) === '["r4"]');
pr("zwei Schreibvorgaenge", geschrieben.length === 2, JSON.stringify(geschrieben));

console.log("--- 5. KALTER Cache: der reale Fall beim Beitritt ---");
// Der Cache hat groups/g1/plans noch nie gesehen. Ueber den Cache-Weg saehe jeder Slot
// leer aus - und der Nachtrag ueberschriebe genau das, was er schonen soll.
frischerStand(); gesehen = false;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] } });
await mergeOwnPlanIntoGroup("g1");
pr("fremder Slot trotz kaltem Cache unangetastet",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["OWNER"]',
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr));
pr("mein freier Slot kam trotzdem an",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_mi) === '["r2"]');

console.log("--- 6. Lesefehler schreibt NICHTS ---");
// Ein nicht nachgetragener Plan ist ein Aergernis, ein ueberschriebener fremder ein Verlust.
frischerStand(); serverOffline = true;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] } });
var geworfen = false;
try { await mergeOwnPlanIntoGroup("g1"); } catch (e) { geworfen = true; }
serverOffline = false;
pr("wirft nicht (der Beitritt geht vor)", !geworfen);
pr("nichts geschrieben", geschrieben.length === 0, JSON.stringify(geschrieben));
pr("fremder Slot unveraendert", JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["OWNER"]');

console.log("--- 7. Leerer eigener Plan ---");
frischerStand(); gesehen = true;
setzeMeinePlaene({});
await mergeOwnPlanIntoGroup("g1");
pr("nichts geschrieben", geschrieben.length === 0);

console.log("--- 8. GEGENPROBE A: der Cache-Weg ueberschreibt beim kalten Cache ---");
frischerStand(); gesehen = false;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] } });
await mergeOwnPlanIntoGroupAlt("g1");
pr("alte Fassung ueberschreibt den fremden Slot",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["r1"]',
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr));
// Gegenprobe zur Gegenprobe: mit warmem Cache war die alte Fassung heil.
frischerStand(); gesehen = true;
gruppenPlaene["2026-W35"] = { mon_fr: ["OWNER"] };
setzeMeinePlaene({ "2026-W35": { mon_fr: ["r1"], mon_mi: ["r2"] } });
await mergeOwnPlanIntoGroupAlt("g1");
pr("alte Fassung bei warmem Cache in Ordnung",
   JSON.stringify(gruppenPlaene["2026-W35"].mon_fr) === '["OWNER"]');

console.log("--- 9. dedupeAgainstCatalog() fasst einen Gruppenbestand nicht an ---");
function katalogKopie(id) {
  var o = COOKBOOK[0];
  return { id: id, lib: "kat1", name: o.name, category: o.category, nutrition: o.nutrition,
           ingredients: o.ingredients, steps: o.steps, time: o.time, tags: o.tags, mealPrep: o.mealPrep };
}
state.dedupeV1 = false; syncGid = "g1";
state.recipes = [katalogKopie("grp1"), { id: "eigen", name: "Steak" }];
dedupeAgainstCatalog();
pr("in der Gruppe wird nichts geloescht", state.recipes.length === 2, state.recipes.length + "");
pr("das Flag bleibt UNGESETZT", state.dedupeV1 === false,
   "sonst holt die Migration es nach dem Verlassen nie nach");

console.log("--- 10. ... und laeuft nach dem Verlassen sofort nach ---");
syncGid = null;
dedupeAgainstCatalog();
pr("die Katalogkopie ist weg", state.recipes.length === 1 && state.recipes[0].id === "eigen",
   JSON.stringify(state.recipes.map(function (r) { return r.id; })));
pr("jetzt ist das Flag gesetzt", state.dedupeV1 === true);

console.log("--- 11. GEGENPROBE B: die alte Bedingung haette in der Gruppe geraeumt ---");
// Alte Fassung: `if (syncGid && !syncHandshakeOk) return;` - mit erfolgtem Handshake lief
// sie also mitten im gemeinsamen Bestand.
var syncHandshakeOk = true;
state.dedupeV1 = false; syncGid = "g1";
state.recipes = [katalogKopie("grp1"), { id: "eigen", name: "Steak" }];
if (!(syncGid && !syncHandshakeOk)) {
  // genau der Rumpf der alten Fassung
  var geloescht = [];
  state.recipes.forEach(function (r) {
    if (!r || !r.lib || r.quick) return;
    var original = COOKBOOK.find(function (x) { return x.id === r.lib; });
    if (!original) return;
    if (!kopieEntsprichtKatalog(r, original)) return;
    geloescht.push(r.id);
  });
  if (geloescht.length) state.recipes = state.recipes.filter(function (r) { return geloescht.indexOf(r.id) === -1; });
}
pr("alte Bedingung loescht aus dem Gruppenbestand", state.recipes.length === 1,
   state.recipes.length + " - sonst misst Abschnitt 9 nichts");

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")

    merge = schneide(quelle, u"async function mergeOwnPlanIntoGroup(gid)",
                     u'await window.CloudGroup.savePlanWeek(gid, wk, Object.assign(missing, { by: syncUid, at: Date.now() }));',
                     u"\n      }\n    }\n  }")
    felder = schneide(quelle, u"const DEDUPE_FELDER = [", u"return DEDUPE_FELDER.every", u"\n  }")
    dedupe = schneide(quelle, u"function dedupeAgainstCatalog()", u"state.dedupeV1 = true;", u"\n    save();\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-planmit-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + UMFELD + u"\n" + merge + u"\n" + felder + u"\n" + dedupe +
            u"\n" + TEST + u"\n</script>")
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
             "--user-data-dir=" + os.path.join(tmp, "profil"),
             "--enable-logging=stderr", "--v=0", "file:///" + seite.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        aus = (p.stdout or "") + (p.stderr or "")
        zeilen = []
        for z in aus.split("\n"):
            m = re.search(r'CONSOLE:\d+\] "(.*)", source', z)
            if m:
                zeilen.append(m.group(1))
        if not zeilen:
            print(u"Keine Konsolenausgabe - lief das Script? Rohausgabe:")
            print(aus[:2000])
            return 2
        for z in zeilen:
            print(z)
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        return 0 if letzte and letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
