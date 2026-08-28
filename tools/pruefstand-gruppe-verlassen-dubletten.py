# -*- coding: utf-8 -*-
u"""
Verlassen einer Gruppe: der Altbestand im eigenen Konto darf keine Dubletten erzeugen.

BEFUND vom 28.08.2026 am echten Konto: 43 Meals in der Gruppe, 81 in users/{uid}/recipes,
14 doppelte `lib` (bis zu dreifach). Die Ursachenkette:

  1. Beim Beitritt wandert der eigene Bestand in die Gruppe (copyOwnRecipesToGroup) und wird
     LOKAL durch den Gruppenbestand ersetzt (enterGroupSync). In users/{uid}/recipes bleibt
     er unangetastet liegen.
  2. leaveGroup() setzte lastPushedRecipes = new Map() - "damit der naechste Zyklus alle
     Meals als neu ins eigene Konto schreibt". Die Annahme "dort liegen sie ja noch nicht"
     stimmt nicht, und eine LEERE Baseline loescht nichts: syncRecipes() bildet delIds aus
     "prev ohne cur".
  3. startCloudSync() liest users/{uid}/recipes und mischt sie ueber mergeRemoteRecipes()
     unter die mitgebrachten Gruppen-Meals. Beide Fassungen tragen dieselbe `lib`, aber
     eigene IDs - jedes Katalog-Meal steht danach doppelt da.

Die Messgroesse ist deshalb NICHT "kommt etwas an", sondern:

    nach Verlassen + Neustart traegt jede `lib` genau EINEN Eintrag

Gegenprobe am Ende: derselbe Ablauf ohne pruneOwnRecipes() muss ROT werden. Ein Pruefstand,
den auch die alte Fassung besteht, misst nichts (docs/TESTING.md).

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-gruppe-verlassen-dubletten.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, anhang=u""):
    u"""Von der Zeile mit `start` bis einschliesslich der naechsten mit `ende`."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1]) + anhang


# --- Umgebung, die der ausgeschnittene Code vorfindet -------------------------------------
UMFELD = u"""
var syncUid = "ich", syncGid = null, lastPushedRecipes = null, recipesSyncFailed = false;
var state = { recipes: [], plans: {}, deleted: {}, shares: [], goal: null, viewWeek: 0 };
var remote = {};
function noteError(){}
function toast(){}
function save(){}
function render(){}
function setViewWeek(){}
function sanitizeRecipe(r){ return r; }
function sanitizeRecipes(l){ return (l||[]).filter(function(r){ return r && r.id; }); }
function sanitizeGoal(g){ return g; }
function isDeleted(id){ return !!state.deleted[id]; }
function pruneWeeks(p){ return p || {}; }
function normalizePlans(p){ return p || {}; }
function plansField(){ return {}; }
function unionIds(a,b){ return (a||[]).concat(b||[]); }
function recipeBase(){ return syncGid ? ["groups", syncGid] : ["users", syncUid]; }
var CLOUD_DOC_MAX = 900000, cloudTooBigWarned = false, cloudPushFailed = false;

// --- Falsches Firestore: zwei Sammlungen, echte Batch-Semantik ---------------------------
var cloud = { "users/ich": {}, "groups/g1": {} };
var leseFehler = false;
window.CloudSync = {
  loadRecipes: function (base) {
    if (leseFehler) return Promise.reject(new Error("offline"));
    var k = base.join("/");
    return Promise.resolve(Object.keys(cloud[k] || {}).map(function (id) {
      return JSON.parse(JSON.stringify(cloud[k][id]));
    }));
  },
  saveRecipesBatch: function (base, puts, delIds) {
    var k = base.join("/");
    cloud[k] = cloud[k] || {};
    (puts || []).forEach(function (r) { cloud[k][r.id] = JSON.parse(JSON.stringify(r)); });
    (delIds || []).forEach(function (id) { delete cloud[k][id]; });
    return Promise.resolve();
  }
};

// --- Testdaten ---------------------------------------------------------------------------
// Fuenf Startmeals je Konto: gleiche `lib` (STARTER ist je Ernaehrungsform fest verdrahtet),
// eigene id je Konto. Genau die Konstellation, die garantiert Paare erzeugt.
var LIBS = ["quark-haferflocken-banane", "haehnchen-bowl-brokkoli", "chili-rinderhack-bohnen",
            "ofenlachs-suesskartoffel", "skyr-beeren-nuesse"];
function meal(id, lib, name) { return { id: id, lib: lib || undefined, name: name || lib, nutrition: { kcal: 500 } }; }

function frischerStand() {
  cloud = { "users/ich": {}, "groups/g1": {} };
  // Mein Konto VOR dem Beitritt: fuenf Startmeals + ein selbst angelegtes Meal
  LIBS.forEach(function (l, i) { cloud["users/ich"]["mein" + i] = meal("mein" + i, l); });
  cloud["users/ich"]["meinEigen"] = meal("meinEigen", null, "Steak mit Kartoffeln");
  // Die Gruppe: die Fassung der anderen Person (eigene ids, gleiche libs) + ihr eigenes Meal.
  // So sieht sie aus, nachdem copyOwnRecipesToGroup() meine Kopien ueber `lib` abgeglichen hat.
  LIBS.forEach(function (l, i) { cloud["groups/g1"]["grp" + i] = meal("grp" + i, l); });
  cloud["groups/g1"]["grpEigen"] = meal("grpEigen", null, "Bowl von Luisa");
  cloud["groups/g1"]["meinEigen"] = meal("meinEigen", null, "Steak mit Kartoffeln");
  state.recipes = Object.keys(cloud["groups/g1"]).map(function (id) {
    return JSON.parse(JSON.stringify(cloud["groups/g1"][id]));
  });
  state.deleted = {};
  syncGid = "g1"; lastPushedRecipes = new Map(state.recipes.map(function (r) { return [r.id, canonJSON(r)]; }));
}

// --- Der Ablauf: verlassen, danach neu starten --------------------------------------------
// Nachgebildet ist NUR die Reihenfolge aus leaveGroup()/startCloudSync(); die drei
// entscheidenden Funktionen (pruneOwnRecipes, syncRecipes, mergeRemoteRecipes) sind der
// ausgeschnittene Produktionscode.
async function verlassenUndNeustart(mitAufraeumen) {
  var keepRecipes = state.recipes.slice();
  syncGid = null;                       // leaveGroupState()
  state.recipes = keepRecipes;
  lastPushedRecipes = new Map();        // die Zeile, um die es geht
  if (mitAufraeumen) await pruneOwnRecipes(keepRecipes);
  await syncRecipes();                  // der Push, der den mitgebrachten Stand hochschreibt
  // --- naechster Start, Zweig "keine Gruppe" aus startCloudSync() ---
  var cloudRecipes = await window.CloudSync.loadRecipes(["users", syncUid]);
  if (cloudRecipes.length) mergeRemoteRecipes(cloudRecipes);
  lastPushedRecipes = new Map(cloudRecipes.map(function (r) { return [r.id, canonJSON(r)]; }));
  return cloudRecipes;
}

function libZaehlung(liste) {
  var z = {};
  liste.forEach(function (r) { if (r.lib) z[r.lib] = (z[r.lib] || 0) + 1; });
  return z;
}
function maxLib(liste) {
  var z = libZaehlung(liste), m = 0;
  Object.keys(z).forEach(function (k) { if (z[k] > m) m = z[k]; });
  return m;
}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Ausgangslage: der Altbestand liegt wirklich noch im eigenen Konto ---");
frischerStand();
pr("6 Meals im eigenen Konto vor dem Verlassen", Object.keys(cloud["users/ich"]).length === 6,
   Object.keys(cloud["users/ich"]).length + "");
pr("7 Meals in der Gruppe", Object.keys(cloud["groups/g1"]).length === 7);
pr("jede lib in der Gruppe genau einmal", maxLib(state.recipes) === 1);

console.log("--- 2. Verlassen MIT Aufraeumen: keine Dublette ---");
frischerStand();
var nachher = await verlassenUndNeustart(true);
pr("jede lib genau einmal", maxLib(nachher) === 1, JSON.stringify(libZaehlung(nachher)));
pr("Bestand ist genau der mitgebrachte", nachher.length === 7, nachher.length + " statt 7");
pr("state.recipes ebenso", maxLib(state.recipes) === 1 && state.recipes.length === 7,
   state.recipes.length + "");
pr("das eigene Meal ist mitgekommen",
   nachher.some(function (r) { return r.id === "meinEigen"; }));
pr("das Meal der anderen Person ist mitgekommen",
   nachher.some(function (r) { return r.id === "grpEigen"; }));
pr("kein Karteileichen-Dokument uebrig",
   Object.keys(cloud["users/ich"]).filter(function (id) { return id.indexOf("mein") === 0 && id !== "meinEigen"; }).length === 0);

console.log("--- 3. Zweiter Zyklus: Beitritt und Austritt noch einmal ---");
// Der Befund am echten Konto zeigte lib-Zaehlungen von DREI - also mehr als einen Durchlauf.
frischerStand();
await verlassenUndNeustart(true);
// erneut beitreten: Gruppenstand wieder uebernehmen, dann wieder verlassen
state.recipes = Object.keys(cloud["groups/g1"]).map(function (id) { return JSON.parse(JSON.stringify(cloud["groups/g1"][id])); });
syncGid = "g1";
var nachZwei = await verlassenUndNeustart(true);
pr("auch nach dem zweiten Durchlauf jede lib einmal", maxLib(nachZwei) === 1,
   JSON.stringify(libZaehlung(nachZwei)));

console.log("--- 3b. Ein Meal OHNE Gegenstueck wird nie geloescht ---");
// Der Fall, den der Push-Check am 28.08.2026 gefunden hat: Wer als NUR-LESER beitritt,
// kopiert nichts in die Gruppe (joinGroup, `role !== "view"`) - und kann danach vom Inhaber
// ueber setRole() zum Mitplaner befoerdert werden. Beim Verlassen ist `warNurLeser` dann
// false. Die erste Fassung loeschte pauschal alles, was nicht im Gruppenstand lag, und haette
// hier den GESAMTEN eigenen Bestand mitgenommen.
frischerStand();
cloud["users/ich"]["nieHochgeladen"] = meal("nieHochgeladen", null, "Omas Auflauf");
cloud["users/ich"]["fremdeLib"] = meal("fremdeLib", "gibt-es-nicht-in-der-gruppe");
var vorAnzahl = Object.keys(cloud["users/ich"]).length;
await pruneOwnRecipes(state.recipes.slice());
pr("Meal ohne lib ueberlebt", !!cloud["users/ich"]["nieHochgeladen"],
   "selbst angelegte Meals haben keine lib und kein Gegenstueck");
pr("Meal mit unbekannter lib ueberlebt", !!cloud["users/ich"]["fremdeLib"]);
pr("die echten Dubletten sind trotzdem weg",
   Object.keys(cloud["users/ich"]).filter(function (id) { return /^mein[0-9]$/.test(id); }).length === 0,
   JSON.stringify(Object.keys(cloud["users/ich"])));
pr("es wurde ueberhaupt etwas geloescht", Object.keys(cloud["users/ich"]).length < vorAnzahl,
   "sonst misst dieser Abschnitt nur, dass nichts passiert");

console.log("--- 4. Nur-Leser: sein Bestand darf NICHT geraeumt werden ---");
// joinGroup() kopiert fuer role==='view' nichts in die Gruppe - dort ist das eigene Konto
// die einzige Kopie. leaveGroup() ueberspringt pruneOwnRecipes() deshalb.
frischerStand();
var vorherIds = Object.keys(cloud["users/ich"]).sort().join(",");
var keep = state.recipes.slice();
syncGid = null; state.recipes = keep; lastPushedRecipes = new Map();
// mitAufraeumen === false bildet den Nur-Leser-Zweig ab
await syncRecipes();
pr("Altbestand des Nur-Lesers ist noch da",
   vorherIds.split(",").every(function (id) { return !!cloud["users/ich"][id]; }));

console.log("--- 5. Schutz gegen Leerraeumen: leerer Behalten-Stand raeumt nichts ---");
frischerStand();
var vorZahl = Object.keys(cloud["users/ich"]).length;
await pruneOwnRecipes([]);
pr("leere Liste loescht nichts", Object.keys(cloud["users/ich"]).length === vorZahl,
   Object.keys(cloud["users/ich"]).length + " statt " + vorZahl);
await pruneOwnRecipes(null);
pr("null loescht nichts", Object.keys(cloud["users/ich"]).length === vorZahl);

console.log("--- 6. Lesefehler ist keine Loeschung (Kuer, nicht Pflicht) ---");
frischerStand();
vorZahl = Object.keys(cloud["users/ich"]).length;
leseFehler = true;
await pruneOwnRecipes(state.recipes.slice());
leseFehler = false;
pr("gescheitertes Lesen laesst alles stehen", Object.keys(cloud["users/ich"]).length === vorZahl);

console.log("--- 7. Idempotent: zweimal aufraeumen aendert nichts ---");
frischerStand();
var k = state.recipes.slice();
await pruneOwnRecipes(k);
var nach1 = Object.keys(cloud["users/ich"]).sort().join(",");
await pruneOwnRecipes(k);
pr("zweiter Lauf ist folgenlos", Object.keys(cloud["users/ich"]).sort().join(",") === nach1);

console.log("--- 7b. GEGENPROBE zur Waisen-Regel: pauschal haette alles geloescht ---");
// Die erste Fassung von pruneOwnRecipes: alles weg, was nicht im Gruppenstand liegt.
async function pruneOwnRecipesPauschal(behalten) {
  var behalteIds = new Set((behalten || []).map(function (r) { return r && r.id; }).filter(Boolean));
  if (!behalteIds.size) return;
  var vorhanden = await window.CloudSync.loadRecipes(["users", "ich"]) || [];
  var weg = vorhanden.map(function (r) { return r && r.id; })
                     .filter(function (id) { return id && !behalteIds.has(id); });
  if (!weg.length) return;
  await window.CloudSync.saveRecipesBatch(["users", "ich"], [], weg);
}
frischerStand();
cloud["users/ich"]["nieHochgeladen"] = meal("nieHochgeladen", null, "Omas Auflauf");
await pruneOwnRecipesPauschal(state.recipes.slice());
pr("pauschale Fassung loescht das Meal ohne Gegenstueck", !cloud["users/ich"]["nieHochgeladen"],
   "sonst misst Abschnitt 3b nichts");

console.log("--- 8. GEGENPROBE: die alte Fassung (nur leere Baseline) muss durchfallen ---");
frischerStand();
var alt = await verlassenUndNeustart(false);
pr("alte Fassung erzeugt Dubletten", maxLib(alt) === 2, "maxLib=" + maxLib(alt) + " " + JSON.stringify(libZaehlung(alt)));
pr("alte Fassung: 12 statt 7 Meals", alt.length === 12, alt.length + "");
// und der zweite Durchlauf macht es schlimmer - genau das dreifache Auftreten vom echten Konto
state.recipes = Object.keys(cloud["groups/g1"]).map(function (id) { return JSON.parse(JSON.stringify(cloud["groups/g1"][id])); });
syncGid = "g1";
var alt2 = await verlassenUndNeustart(false);
pr("alte Fassung waechst mit jedem Zyklus", maxLib(alt2) >= 2, "maxLib=" + maxLib(alt2));

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")

    canon = schneide(quelle, u"function canonValue(v)", u"function canonJSON(v)")
    prune = schneide(quelle, u"async function pruneOwnRecipes(behalten)",
                     u'catch (e) { noteError("group:pruneOwnWrite", e); return; }',
                     u"\n    }\n  }")
    sync = schneide(quelle, u"async function syncRecipes()",
                    u"// lastPushedRecipes bleibt unveraendert",
                    u"\n    }\n  }")
    merge = schneide(quelle, u"function mergeRemoteRecipes(list)",
                     u"save(); render();", u"\n      }")

    tmp = tempfile.mkdtemp(prefix="mp-grpleave-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + canon + u"\n" + UMFELD + u"\n" + prune + u"\n" + sync +
            u"\n" + merge + u"\n" + TEST + u"\n</script>")
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
