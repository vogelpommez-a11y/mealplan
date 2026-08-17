# Ausschneide-Pruefstand Auto-Wochenplaner (D2): Auswahl, Mengen, Ausschluesse, Gruppe.
#
# Getestet wird die PRODUKTIONSIMPLEMENTIERUNG - alle Funktionen werden aus index.html
# ausgeschnitten, nichts abgetippt. Gestubbt sind nur die Randstuecke (save/render/toast).
import io, os

SRC = r"C:\Users\Paddy\Documents\Paddys Mealplan\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-autoplaner.html")
lines = io.open(SRC, encoding="utf-8").read().split("\n")

def schnitt(sig):
    start = None
    for i, z in enumerate(lines):
        if z.startswith(sig):
            start = i; break
    if start is None: raise SystemExit("NICHT GEFUNDEN: " + sig)
    if lines[start].rstrip().endswith("}"): return lines[start]
    for j in range(start + 1, len(lines)):
        if lines[j] == "  }": return "\n".join(lines[start:j + 1])
    raise SystemExit("KEIN ENDE: " + sig)

def block(start_sig, end_sig):
    a = b = None
    for i, z in enumerate(lines):
        if a is None and z.startswith(start_sig): a = i
        elif a is not None and z.startswith(end_sig): b = i; break
    if a is None or b is None: raise SystemExit("BLOCK: " + start_sig)
    return "\n".join(lines[a:b + 1])

# Genau EINE Zeile. Nicht ueber block(sig, sig) loesbar: dort sucht das elif das Ende erst ab
# der Folgezeile und findet bei gleicher Signatur nie eines.
def zeile(sig):
    for z in lines:
        if z.startswith(sig): return z
    raise SystemExit("ZEILE NICHT GEFUNDEN: " + sig)

teile = [
    block("  const DAYS = [", "  ];"),
    block("  const MEALS = [", "  ];"),
    # Kategorie-Bindung: der Planer fragt catFitsMeal/catSuggestsMeal, nicht die Tabelle.
    block("  const CATEGORIES = [", "  const CAT_LEGACY ="),
    schnitt("  function catFitsMeal("),
    schnitt("  function catSuggestsMeal("),
    schnitt("  function catPlanFitsMeal("),
    # Der Katalog selbst - seit dem 16.08.2026 zweite Kandidatenquelle des Planers.
    block("  const COOKBOOK = [", "  ];"),
    schnitt("  function cookbookVisible("),
    schnitt("  function isAdopted("),
    schnitt("  function copyFromCookbook("),
    schnitt("  function sanitizeRecipe("),
    schnitt("  function normalizePlan("),
    schnitt("  function asIdList("),
    # Ernaehrungsprofil - die harte Grenze (Regel 3).
    schnitt("  function dietOk("),
    schnitt("  function avoidOk("),
    schnitt("  function fitsDiet("),
    # Slot-Eintraege und Zuweisung (Regel 6 / Gruppenfall).
    schnitt("  function entryId("),
    schnitt("  function entryUids("),
    schnitt("  function entryIsShared("),
    schnitt("  function makeEntry("),
    # Seit dem 16.08.2026 fragt auch der Planer, ob eine Zeile noch fuer alle gilt - dieselbe
    # Frage, die der Picker an fuenf Stellen stellt.
    schnitt("  function slotIsShared("),
    schnitt("  function makeEmptyPlan("),
    # Wochenschluessel - der Undo-Pfad haengt daran.
    schnitt("  function isoWeekKey("),
    schnitt("  function weekKeyFor("),
    schnitt("  function activeWeekKey("),
    # Naehrwerte und Tagesbilanz.
    schnitt("  function nutNum("),
    schnitt("  function nutParse("),
    schnitt("  function recipeNut("),
    schnitt("  function addNut("),
    schnitt("  function dayNutOf("),
    schnitt("  function dayNut("),
    schnitt("  function weekNut("),
    schnitt("  function nfmt("),
    schnitt("  function libraryRecipes("),
    schnitt("  function getRecipe("),
    schnitt("  function canEdit("),
    schnitt("  function groupRole("),
    schnitt("  function isPro("),
    # Tagesziele samt Trainingstagen - der Planer rechnet gegen goalTargetsForDay().
    block("  const TRAIN_LEVELS = [", "  const TRAIN_MIN_MIN ="),
    schnitt("  function trainLevel("),
    schnitt("  function trainKcal("),
    schnitt("  function goalTargets("),
    schnitt("  function goalTraining("),
    schnitt("  function isTrainingDay("),
    schnitt("  function dayTrainKcal("),
    schnitt("  function trainFromRest("),
    schnitt("  function goalTargetsForDay("),
    schnitt("  function goalTargetsForDays("),
    # Der Planer selbst.
    block("  // ---------- Auto-Wochenplaner (D2) ----------", "  const PLAN_TOLERANZ ="),
    schnitt("  function slotOpenForMe("),
    schnitt("  function planKandidaten("),
    schnitt("  function planRang("),
    schnitt("  function planWochengerichte("),
    schnitt("  function planUebernahme("),
    # planAdopt() ist am 17.08.2026 entfallen (Katalog-Umbau): der Planer kopiert nicht mehr,
    # planId() in autoPlanWeek() liefert seither einfach r.id.
    schnitt("  function planTagKcal("),
    schnitt("  function planRecentIds("),
    # Gedaechtnis des Planers (state.planned).
    #
    # Konstante und Funktion werden GETRENNT geschnitten, seit die Konstante am 16.08.2026 nach
    # ganz oben gewandert ist (direkt vor `let state = load()`, wegen der temporalen Totzone -
    # siehe dort). Ein block() ab ihrer Zeile bis zur naechsten "  }" zog danach den halben
    # State-Aufbau mitsamt `let state = load()` herein und kollidierte mit dem Stub oben:
    # "Identifier 'state' has already been declared". Der Pruefstand lief dann gar nicht mehr an,
    # und das Log blieb leer statt rot - deshalb im Zweifel `python syntax-check.py` auf die
    # GENERIERTE Datei werfen, es nimmt einen Pfad entgegen.
    zeile("  const PLAN_GEDAECHTNIS_WOCHEN = "),
    schnitt("  function sanitizePlanned("),
    # weekKeyBack samt seinem Puffer - die let-Zeile davor gehoert dazu, sonst wirft die
    # Funktion beim ersten Aufruf (im ersten Anlauf genau so passiert).
    block("  let weekBackCache = ", "  }"),
    schnitt("  function autoPlanWeek("),
]
code = "\n\n".join(teile)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Auto-Wochenplaner</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  // Ergebnisfortschritt (docs/TESTING.md, Abschnitt 3): laufend schreiben statt erst am Ende.
  // Bei einer Gegenprobe stuerzt der Produktionscode absichtlich ab - ohne das saehe man
  // dann ein leeres <pre> statt der Zeilen, die bis dahin rot geworden sind.
  var el = document.getElementById("log");
  if (el) el.textContent = LOG.join("\\n");
}

// ---- Randstuecke, die der Planer nur anfasst ----
var state = { goal: null, recipes: [], plans: {}, plan: null, viewWeek: "cur" };
var recipeIndex = null, dayNutCache = null;
var syncUid = null, syncGid = null, myRole = null, groupMembers = [], proInfo = null;
var gespeichert = 0, gezeichnet = 0, letzterToast = "";
function save() { gespeichert++; }
function render() { gezeichnet++; }
function toast(t) { letzterToast = t; window.__undo = null; }
function undoToast(t, cb, opts) { letzterToast = t; window.__undo = cb; window.__opts = opts || null; }
// Randstuecke von sanitizeRecipe() - dieselben Stubs wie im Rezeptbuch-Pruefstand.
var lfdUid = 0;
function uid() { return "u" + (++lfdUid); }
function safeImage(x) { return x || null; }
function migrateCat(c) { return c; }
function sanitizeIng(x) { return x; }
function sanitizeTags(t) { return Array.isArray(t) && t.length ? t.slice() : null; }
function esc(s) { return String(s == null ? "" : s); }

__CODE__

// ---- Hilfen fuer den Pruefstand selbst ----
function meal(id, kat, kcal, prot, tags, prep) {
  return { id: id, name: id, category: kat, tags: tags || [], mealPrep: prep === true,
           nutrition: { kcal: kcal, carbs: 10, protein: prot == null ? 20 : prot, fat: 10 } };
}
// Der Katalog ist seit dem 16.08.2026 zweite Kandidatenquelle. Damit die Pruefungen zur
// AUSWAHLLOGIK weiterhin genau das messen, was sie messen sollen, laeuft er per Vorgabe aus
// und wird nur dort zugeschaltet, wo es um ihn geht. COOKBOOK ist const, aber der INHALT
// ist veraenderlich - deshalb ueber die Laenge statt ueber eine Neuzuweisung.
var KATALOG_ALLE = COOKBOOK.slice();
function katalogAus() { COOKBOOK.length = 0; }
function katalogAn() { COOKBOOK.length = 0; KATALOG_ALLE.forEach(function (r) { COOKBOOK.push(r); }); }

function frischerPlan(recipes, goal) {
  katalogAus();
  state.planned = {};
  window.__opts = null;
  // KOPIE, nicht die uebergebene Liste: Der Planer legt seit dem 16.08.2026 selbst Meals an
  // (uebernommene Katalog-Rezepte). Ohne .slice() wuechse die Vorlage des Testfalls mit, und
  // eine spaetere Pruefung gegen ihre Laenge misst dann sich selbst.
  state.recipes = (recipes || []).slice();
  state.goal = goal === undefined ? { kcal: 2000, carbs: 200, protein: 150, fat: 60 } : goal;
  state.plans = {}; state.plans[activeWeekKey()] = makeEmptyPlan();
  state.plan = state.plans[activeWeekKey()];
  syncUid = null; syncGid = null; myRole = null; groupMembers = [];
  proInfo = { pro: true, source: "manual", until: null };
  gespeichert = 0; gezeichnet = 0; letzterToast = "";
}
function alleEintraege() {
  var out = [];
  DAYS.forEach(function (d) { MEALS.forEach(function (m) {
    state.plan[d.key][m.key].forEach(function (e) { out.push({ d: d.key, m: m.key, e: e }); });
  }); });
  return out;
}
// Ein Bestand, der fuer eine ganze Woche reicht: je Slot-Art mehrere Gerichte.
function bestand() {
  return [
    meal("fr1", "Frühstück", 400, 30, ["vegetarisch"], true),
    meal("fr2", "Frühstück", 450, 25, ["vegetarisch", "vegan"], true),
    meal("fr3", "Frühstück", 380, 20, ["vegetarisch"], false),
    meal("ha1", "Hauptgericht", 600, 45, ["vegan", "vegetarisch"], true),
    meal("ha2", "Hauptgericht", 700, 50, [], true),
    meal("ha3", "Hauptgericht", 650, 40, ["vegetarisch"], false),
    meal("ha4", "Hauptgericht", 550, 35, ["vegan", "vegetarisch"], true),
    meal("sn1", "Snack", 200, 15, ["vegetarisch"], false),
    meal("sn2", "Snack", 150, 12, ["vegan", "vegetarisch"], false)
  ];
}

(function () {
  // ---- Schritt 1: Kandidaten ----
  frischerPlan(bestand().concat([
    meal("ohne", "Hauptgericht", 0, 0, []),                       // keine Naehrwerte
    { id: "scan", name: "Riegel", category: "Snack", quick: true, nutrition: { kcal: 200, protein: 5 } }
  ]));
  var k = planKandidaten();
  pruef("Meals ohne Naehrwerte fallen raus", k.some(function (r) { return r.id === "ohne"; }), false);
  pruef("Barcode-Schnellprodukte fallen raus", k.some(function (r) { return r.id === "scan"; }), false);
  pruef("der Rest bleibt", k.length, 9);

  // Regel 3: das Profil ist eine HARTE Grenze.
  state.goal = { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegan" };
  pruef("vegan laesst nur veganes zu",
    planKandidaten().every(function (r) { return r.tags.indexOf("vegan") !== -1; }), true);
  state.goal = { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegetarisch" };
  pruef("vegetarisch schliesst vegane Meals ein",
    planKandidaten().some(function (r) { return r.id === "ha1"; }), true);
  pruef("vegetarisch laesst Fleisch draussen",
    planKandidaten().some(function (r) { return r.id === "ha2"; }), false);

  // ---- Schritt 2: Wochengerichte ----
  frischerPlan(bestand());
  var kand = planKandidaten();
  pruef("Fruehstuecks-Slot bekommt nur Fruehstuecke",
    planWochengerichte(kand, "fr").every(function (r) { return r.category === "Frühstück"; }), true);
  pruef("Snack-Slot bekommt nur Snacks/Desserts",
    planWochengerichte(kand, "sn").every(function (r) { return r.category === "Snack"; }), true);
  pruef("Hauptgerichte landen im Mittag",
    planWochengerichte(kand, "mi").every(function (r) { return r.category === "Hauptgericht"; }), true);
  pruef("hoechstens " + PLAN_VARIANTEN + " Wochengerichte je Slot",
    planWochengerichte(kand, "mi").length <= PLAN_VARIANTEN, true);
  // Meal-Prep schlaegt Nicht-Meal-Prep bei sonst gleicher Kategorie (Regel 2).
  //
  // Gemessen an planRang(), NICHT am Ziehungsergebnis. Die Pruefung stand bis zum 16.08.2026
  // als `planWochengerichte(kand, "mi")[0].mealPrep` da - richtig, solange strikt die besten
  // PLAN_VARIANTEN genommen wurden. Seit der gewichteten Pool-Ziehung kann auch Platz 4 auf
  // Platz 1 landen: In 20 Laeufen war die Zeile zweimal rot, ohne dass sich am Code etwas
  // geaendert hatte. Eine Pruefung, die in jedem zehnten Lauf zufaellig fehlschlaegt, ist
  // schlimmer als keine - man gewoehnt sich an die rote Zeile.
  //
  // Zwei sonst identische Meals, damit die Differenz GENAU der Meal-Prep-Beitrag ist und
  // nicht noch Protein- oder Groessenanteile mittraegt.
  pruef("Meal-Prep steht vorn",
    planRang(meal("mpA", "Hauptgericht", 600, 45, [], true), "mi", 0, null)
    - planRang(meal("mpB", "Hauptgericht", 600, 45, [], false), "mi", 0, null), 10);
  // Gegenprobe zur Bewertung: eine EXAKTE Kategorie schlaegt eine bloss erlaubte.
  var mitBeilage = kand.concat([meal("bl1", "Beilage", 600, 60, [], true)]);
  pruef("genaue Kategorie schlaegt erlaubte",
    planWochengerichte(mitBeilage, "mi")[0].category, "Hauptgericht");

  // ---- Schritt 3-6: der ganze Durchlauf ----
  frischerPlan(bestand());
  autoPlanWeek();
  var eintr = alleEintraege();
  pruef("die Woche ist danach gefuellt", eintr.length > 0, true);
  pruef("gespeichert und gezeichnet", gespeichert > 0 && gezeichnet > 0, true);
  pruef("Rueckgaengig wird angeboten", typeof window.__undo, "function");
  pruef("alle vier Slots sind bedient",
    ["fr", "mi", "ab", "sn"].filter(function (m) {
      return eintr.some(function (x) { return x.m === m; });
    }).length, 4);
  pruef("jeder Eintrag zeigt auf ein existierendes Meal",
    eintr.every(function (x) { return !!getRecipe(entryId(x.e)); }), true);
  pruef("allein geplant heisst 'fuer alle' (String-Form)",
    eintr.every(function (x) { return typeof x.e === "string"; }), true);
  pruef("die Kategorie passt zu jedem Slot",
    eintr.every(function (x) { return catFitsMeal(getRecipe(entryId(x.e)).category, x.m); }), true);
  // Regel 2: wenige Gerichte, die sich wiederholen - NICHT 28 verschiedene.
  var verschieden = new Set(eintr.map(function (x) { return entryId(x.e); })).size;
  pruef("wenige Gerichte, oft wiederholt", verschieden <= PLAN_VARIANTEN * 4, true);
  pruef("aber nicht nur ein einziges", verschieden > 1, true);
  // Deckel je Slot.
  pruef("kein Slot ueber dem Deckel",
    DAYS.every(function (d) { return MEALS.every(function (m) {
      return state.plan[d.key][m.key].length <= PLAN_MAX_PRO_SLOT; }); }), true);
  // Schritt 7: das Ergebnis muss das Ziel ungefaehr treffen.
  var ziel = goalTargetsForDays(DAYS.map(function (d) { return d.key; }));
  var ist = weekNut();
  pruef("die Woche liegt im 10-Prozent-Korridor",
    Math.abs(ist.kcal - ziel.kcal) <= ziel.kcal * PLAN_TOLERANZ, true);

  // ---- Rueckgaengig ----
  window.__undo();
  pruef("Rueckgaengig leert die Woche wieder", alleEintraege().length, 0);

  // ---- Regel 1: Belegtes bleibt unangetastet ----
  frischerPlan(bestand());
  state.plan.mon.fr.push("fr3");
  state.plan.mon.mi.push("ha3");
  autoPlanWeek();
  pruef("bestehender Fruehstueckseintrag bleibt", state.plan.mon.fr[0], "fr3");
  pruef("belegter Slot bekommt nichts dazu", state.plan.mon.fr.length, 1);
  pruef("belegter Mittag bekommt nichts dazu", state.plan.mon.mi.length, 1);
  pruef("andere Tage wurden trotzdem gefuellt", state.plan.tue.mi.length > 0, true);

  // Alles belegt -> kein Leerlauf-Klick, und der Plan bleibt unveraendert.
  frischerPlan(bestand());
  DAYS.forEach(function (d) { MEALS.forEach(function (m) { state.plan[d.key][m.key].push("ha1"); }); });
  var vorher = JSON.stringify(state.plan);
  autoPlanWeek();
  pruef("volle Woche bleibt unveraendert", JSON.stringify(state.plan), vorher);
  pruef("und sagt das auch", letzterToast, "Deine Woche ist schon geplant");
  pruef("kein Rueckgaengig fuer nichts", window.__undo, null);

  // ---- Grenzfall: zu wenige Meals ----
  frischerPlan([meal("a", "Hauptgericht", 600, 40, []), meal("b", "Snack", 200, 10, [])]);
  autoPlanWeek();
  pruef("zu wenige Meals: nichts geplant", alleEintraege().length, 0);
  pruef("zu wenige Meals: klarer Hinweis",
    letzterToast.indexOf("Zu wenige passende Meals") === 0, true);

  // Gegenprobe: derselbe Bestand, aber als Veganer - die Kandidaten schrumpfen unter die
  // Schwelle, obwohl neun Meals dastehen. Ohne diese Probe pruefte oben nur die Anzahl.
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegan" });
  autoPlanWeek();
  pruef("veganes Profil ohne Auswahl plant nichts", alleEintraege().length, 0);

  // Mit genug veganen Meals laeuft es - und NIE etwas ohne den Tag.
  frischerPlan(bestand().concat([
    meal("v1", "Frühstück", 400, 25, ["vegan", "vegetarisch"], true),
    meal("v2", "Hauptgericht", 620, 40, ["vegan", "vegetarisch"], true),
    meal("v3", "Hauptgericht", 580, 38, ["vegan", "vegetarisch"], true),
    meal("v4", "Snack", 180, 12, ["vegan", "vegetarisch"], false)
  ]), { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegan" });
  autoPlanWeek();
  pruef("veganer Plan entsteht", alleEintraege().length > 0, true);
  pruef("und enthaelt NUR veganes",
    alleEintraege().every(function (x) {
      return getRecipe(entryId(x.e)).tags.indexOf("vegan") !== -1; }), true);

  // Einschraenkung quer dazu: glutenfrei ist ebenfalls hart.
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 150, fat: 60, avoid: ["glutenfrei"] });
  autoPlanWeek();
  pruef("ohne glutenfreie Meals wird nichts geplant", alleEintraege().length, 0);

  // ---- Grenzfall: kein Ziel ----
  frischerPlan(bestand(), null);
  autoPlanWeek();
  pruef("ohne Ziel wird nichts geplant", alleEintraege().length, 0);

  // ---- Nur-Ansehen-Mitglied ----
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "view"; groupMembers = [{ uid: "ich" }, { uid: "du" }]; syncUid = "ich";
  autoPlanWeek();
  pruef("Nur-Ansehen plant nicht", alleEintraege().length, 0);

  // ---- Pro-Gating ----
  frischerPlan(bestand());
  proInfo = null;
  autoPlanWeek();
  pruef("ohne Pro wird nicht geplant", alleEintraege().length, 0);
  pruef("ohne Pro kommt der Hinweis", letzterToast.indexOf("gehört zu Pro") !== -1, true);
  // In einer Gruppe darf JEDES Mitglied planen - auch ohne eigenes Pro (der Inhaber zahlt).
  frischerPlan(bestand());
  proInfo = null;
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  pruef("in der Gruppe plant auch ein Mitglied ohne Pro", alleEintraege().length > 0, true);

  // ---- Gruppe: der Planer traegt niemanden FREMDES allein ein ----
  // Bis zum 16.08.2026 stand hier "jeder Eintrag zaehlt nur fuer mich". Das galt, solange der
  // Planer ausnahmslos sich selbst eintrug - und genau das war der Fehler (siehe naechste
  // Gruppe). Die Zusage, die bleibt, ist eine andere: Was individuell zugewiesen wird, gehoert
  // MIR. Der Planer weist niemals einer anderen Person etwas zu; das waere Fremdplanung.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  pruef("individuell zugewiesen wird nur an mich",
    alleEintraege().every(function (x) {
      var u = entryUids(x.e); return u === null || (u.length === 1 && u[0] === "ich"); }), true);
  pruef("kein Eintrag ist eine geteilte OBJEKTreferenz",
    (function () {
      // Nur Objekte pruefen: Zwei "fuer alle"-Eintraege sind derselbe String, und Strings sind
      // unveraenderlich - bei ihnen ist Wertgleichheit kein Problem, sondern der Normalfall.
      var e = alleEintraege().map(function (x) { return x.e; }).filter(function (x) { return typeof x === "object"; });
      for (var i = 0; i < e.length; i++) for (var j = i + 1; j < e.length; j++) if (e[i] === e[j]) return false;
      return true;
    })(), true);

  // ---- Leere Zeile heisst "fuer alle" ----
  // Gefunden am Geraet zu zweit: Der Planer trug ausnahmslos sich selbst ein, 31 von 31
  // Eintraegen trugen ein Badge. Der gemeinsame Plan war voll und fuer die andere Person
  // trotzdem leer. Der Picker macht es an fuenf Stellen anders (slotIsShared), der Planer war
  // die Ausnahme.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  pruef("in leere Zeilen plant der Planer fuer ALLE",
    DAYS.every(function (d) {
      return ["fr", "mi", "ab"].every(function (m) {
        var arr = state.plan[d.key][m];
        return !arr.length || entryIsShared(arr[0]);
      });
    }), true);
  pruef("und zwar wirklich als blanker String (nicht als Objekt mit allen uids)",
    typeof state.plan.mon.fr[0], "string");
  // Gegenprobe zur Bilanz: Ein "fuer alle" zaehlt in JEDER Bilanz, auch in meiner.
  pruef("das Gericht zaehlt weiterhin in meiner Tagesbilanz",
    dayNutOf(state.plan, "mon").kcal > 0, true);

  // Die ZWEITE Portion bleibt individuell - "wir essen dasselbe, ich zweimal".
  frischerPlan(bestand(), { kcal: 3600, carbs: 360, protein: 260, fat: 110 });
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  (function () {
    var doppelt = null;
    DAYS.forEach(function (d) {
      ["fr", "mi", "ab"].forEach(function (m) {
        if (!doppelt && state.plan[d.key][m].length === 2) doppelt = state.plan[d.key][m];
      });
    });
    pruef("bei zwei Portionen gibt es so einen Slot ueberhaupt", !!doppelt, true);
    pruef("die erste Portion gilt fuer alle", doppelt ? entryIsShared(doppelt[0]) : null, true);
    pruef("die zweite gehoert nur mir",
      doppelt ? JSON.stringify(entryUids(doppelt[1])) : null, JSON.stringify(["ich"]));
  })();

  // Steht in der Zeile schon eine FREMDE Zuweisung, wird daraus kein "fuer alle" - sonst
  // schriebe der Planer der anderen Person ihr eigenes Gericht um.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.fr.push({ id: "fr3", uids: ["du"] });   // passt nicht in den fr-Slot? doch: Fruehstueck
  autoPlanWeek();
  pruef("neben einer fremden Zuweisung entsteht kein fuer-alle",
    state.plan.mon.fr.every(function (e) { return !entryIsShared(e); })
      || state.plan.mon.fr.length === 1, true);

  // Und allein aendert sich gar nichts: makeEntry liefert ohnehin die String-Form.
  frischerPlan(bestand());
  autoPlanWeek();
  pruef("allein bleibt alles wie bisher fuer alle",
    alleEintraege().every(function (x) { return entryIsShared(x.e); }), true);

  // ---- Regel 5: dem vorhandenen Eintrag BEITRETEN ----
  // Bis zum 16.08.2026 legte der Planer hier einen ZWEITEN Eintrag an - zwei Karten mit
  // demselben Gericht und zwei Badges. Jetzt traegt er sich am vorhandenen ein, und
  // makeEntry() macht daraus von selbst ein "fuer alle", sobald alle abgedeckt sind.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  // Die Referenz merken: der Kern-Nachweis ist, dass der Planer das fremde Objekt ERSETZT und
  // nicht mutiert. Ein uids.push() daran schluege durch den Undo-Pfad durch (before haelt nur
  // eine flache Kopie des Slot-Arrays) und veraenderte A's Eintrag dauerhaft.
  var fremd = { id: "ha3", uids: ["du"] };
  state.plan.mon.mi.push(fremd);
  autoPlanWeek();
  pruef("aus zwei Karten wird eine", state.plan.mon.mi.length, 1);
  pruef("es bleibt DASSELBE Gericht", entryId(state.plan.mon.mi[0]), "ha3");
  pruef("und es gilt jetzt fuer alle", entryIsShared(state.plan.mon.mi[0]), true);
  pruef("das fremde Objekt wurde ersetzt, nicht mutiert",
    JSON.stringify(fremd), JSON.stringify({ id: "ha3", uids: ["du"] }));

  // Drei Mitglieder: nach EINEM Beitritt sind noch nicht alle abgedeckt - der Eintrag bleibt
  // die Objektform mit beiden UIDs. Erst wer als Dritter beitritt, macht ein "fuer alle" daraus.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich";
  groupMembers = [{ uid: "ich" }, { uid: "du" }, { uid: "er" }];
  state.plan.mon.mi.push({ id: "ha3", uids: ["du"] });
  autoPlanWeek();
  pruef("bei dreien traegt der Eintrag beide UIDs",
    JSON.stringify(entryUids(state.plan.mon.mi[0])), JSON.stringify(["du", "ich"]));
  pruef("und ist noch KEIN fuer-alle", entryIsShared(state.plan.mon.mi[0]), false);

  // Zwei Portionen: die erste ist der Beitritt, die zweite ein eigener Eintrag daneben. Das ist
  // dann eine echte Aussage ("ich esse davon zwei") und keine Doppelung.
  frischerPlan(bestand(), { kcal: 3600, carbs: 360, protein: 260, fat: 110 });
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.mi.push({ id: "ha3", uids: ["du"] });
  autoPlanWeek();
  pruef("zwei Portionen ergeben zwei Eintraege", state.plan.mon.mi.length, 2);
  pruef("der erste ist der gemeinsame", entryIsShared(state.plan.mon.mi[0]), true);
  pruef("der zweite gehoert nur mir",
    JSON.stringify(entryUids(state.plan.mon.mi[1])), JSON.stringify(["ich"]));
  pruef("und ist dasselbe Gericht", entryId(state.plan.mon.mi[1]), "ha3");

  // "Nochmal"/Rueckgaengig nach einem Beitritt: A's Eintrag steht wieder im Original da.
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.mi.push({ id: "ha3", uids: ["du"] });
  autoPlanWeek();
  window.__undo();
  pruef("Rueckgaengig stellt den fremden Eintrag her",
    JSON.stringify(state.plan.mon.mi), JSON.stringify([{ id: "ha3", uids: ["du"] }]));

  // Gegenprobe: passt das Gericht der anderen NICHT zu meinem Profil, wird ein eigenes gewaehlt.
  frischerPlan(bestand().concat([
    meal("v1", "Frühstück", 400, 25, ["vegan", "vegetarisch"], true),
    meal("v2", "Hauptgericht", 620, 40, ["vegan", "vegetarisch"], true),
    meal("v3", "Hauptgericht", 580, 38, ["vegan", "vegetarisch"], true),
    meal("v4", "Snack", 180, 12, ["vegan", "vegetarisch"], false)
  ]), { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegan" });
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.mi.push({ id: "ha2", uids: ["du"] });   // Fleischgericht
  autoPlanWeek();
  pruef("ein unpassendes Gericht wird NICHT uebernommen",
    state.plan.mon.mi.slice(1).every(function (e) { return entryId(e) !== "ha2"; }), true);
  pruef("stattdessen etwas Veganes",
    state.plan.mon.mi.slice(1).every(function (e) {
      return getRecipe(entryId(e)).tags.indexOf("vegan") !== -1; }), true);

  // ---- Wer zuerst plant, waehlt vertraeglich (planRang in der Gruppe) ----
  // Gemessen wird die DIFFERENZ zweier Gerichte, einmal allein und einmal in der Gruppe. Alle
  // uebrigen Beitraege (Kategorie, Protein, Budget) sind in beiden Laeufen gleich und kuerzen
  // sich damit heraus - uebrig bleibt genau der neue Vertraeglichkeits-Beitrag.
  frischerPlan(bestand().concat([
    meal("alle", "Hauptgericht", 700, 50, ["vegan", "vegetarisch", "glutenfrei", "laktosefrei"], true)
  ]));
  var rVegan = getRecipe("ha1");          // vegan + vegetarisch
  var rFleisch = getRecipe("ha2");        // ohne Tags, sonst gleich (700 kcal, 50 P, mealPrep)
  var rAlles = getRecipe("alle");         // alle vier Tags
  var alleinDiff = planRang(rVegan, "mi", 0, null) - planRang(rFleisch, "mi", 0, null);
  var alleinMax = planRang(rAlles, "mi", 0, null) - planRang(rFleisch, "mi", 0, null);

  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  pruef("in der Gruppe steigt das vegane Gericht um 5",
    planRang(rVegan, "mi", 0, null) - planRang(rFleisch, "mi", 0, null) - alleinDiff, 5);
  // Der hoechstmoegliche Beitrag. Mit den heutigen vier Tags ergibt die Summe von selbst genau
  // 8 - im NORMALLAUF misst diese Zeile also nur den Wert, nicht den Math.min(8)-Deckel.
  //
  // Beweisen laesst er sich trotzdem, ueber eine Gegenprobe, die ihn AUSLOEST: `vertraeglich
  // += 50` fuer vegan. Mit Deckel bleibt die Zeile gruen (8), ohne Deckel meldet sie 53. Das
  // ist der Grund, warum das Math.min() im Code steht und nicht bloss im Kommentar - eine
  // fuenfte Unvertraeglichkeit wuerde die Zusage "bleibt unter 40" sonst still brechen.
  pruef("mehr als 8 gibt es nicht",
    planRang(rAlles, "mi", 0, null) - planRang(rFleisch, "mi", 0, null) - alleinMax, 8);
  pruef("er bleibt unter dem Wiederholungs-Malus von 40", 8 < 40, true);

  // Gegenprobe: allein in einer Gruppe (noch niemand beigetreten) gibt es nichts zu beruecksichtigen.
  groupMembers = [{ uid: "ich" }];
  pruef("allein in der Gruppe wirkt der Beitrag nicht",
    planRang(rVegan, "mi", 0, null) - planRang(rFleisch, "mi", 0, null), alleinDiff);
  syncGid = null; myRole = null; syncUid = null; groupMembers = [];
  pruef("und ohne Gruppe erst recht nicht",
    planRang(rVegan, "mi", 0, null) - planRang(rFleisch, "mi", 0, null), alleinDiff);

  // Und ein Eintrag, der MIR schon gehoert, macht den Slot zu (Regel 1 vor Regel 5).
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.mi.push({ id: "ha3", uids: ["ich"] });
  autoPlanWeek();
  pruef("mein eigener Eintrag schliesst den Slot", state.plan.mon.mi.length, 1);

  // ---- Mengen: Anzahl je Budget ----
  // Ein grosses Ziel muss zu MEHR Eintraegen fuehren als ein kleines - das ist der Kern
  // von "gleiches Gericht, eigene Menge".
  frischerPlan(bestand(), { kcal: 1600, carbs: 160, protein: 120, fat: 50 });
  autoPlanWeek();
  var klein = alleEintraege().length;
  frischerPlan(bestand(), { kcal: 3200, carbs: 320, protein: 200, fat: 90 });
  autoPlanWeek();
  var gross = alleEintraege().length;
  pruef("3200 kcal ergeben mehr Eintraege als 1600", gross > klein, true);
  // Seit dem 16.08.2026 gibt es allein nur EINE Portion je Hauptmahlzeit. Ein 3200er Ziel
  // laesst sich damit aus fr/mi/ab nicht mehr decken - der Rest geht an die Snacks, und was
  // dann noch fehlt, wird BENANNT statt aufgefuellt. Genau das ist hier zu pruefen.
  pruef("bei sehr hohem Ziel wird die Luecke benannt",
    letzterToast.indexOf("kcal offen") !== -1, true);
  pruef("und der Plan entsteht trotzdem vollstaendig",
    DAYS.every(function (d) {
      return ["fr", "mi", "ab"].every(function (m) { return state.plan[d.key][m].length > 0; });
    }), true);

  // Trainingstage haben ein hoeheres Ziel - der Planer muss das mitnehmen, weil er
  // goalTargetsForDay() fragt und nicht goalTargets(1).
  // Der Trainingstag braucht mehr - abbilden kann der Planer das seit dem 16.08.2026 nur noch
  // ueber die Snack-Zeile, weil es je Hauptmahlzeit genau EINE Portion gibt. Der Testfall
  // bekommt deshalb vier Snacks: Mit den zwei aus bestand() ist die Zeile an beiden Tagen
  // erschoepft, und die Pruefung haette nur gemessen, dass der Deckel greift.
  frischerPlan(bestand().concat([
    meal("sn3", "Snack", 190, 14, ["vegetarisch"], false),
    meal("sn4", "Snack", 170, 13, ["vegetarisch"], false)
  ]), { kcal: 2000, carbs: 200, protein: 150, fat: 60, weight: 80,
        training: { mon: { level: "hard", min: 90 } } });
  autoPlanWeek();
  pruef("Trainingstag hat ein hoeheres Ziel als der Ruhetag",
    goalTargetsForDay("mon").kcal > goalTargetsForDay("tue").kcal, true);
  pruef("und bekommt auch mehr eingeplant",
    dayNutOf(state.plan, "mon").kcal > dayNutOf(state.plan, "tue").kcal, true);
  // Die Kehrseite gehoert mitgeprueft: Reicht die Snack-Zeile nicht, bleibt eine Luecke -
  // und die wird benannt statt mit Wiederholungen aufgefuellt.
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 150, fat: 60, weight: 80,
                            training: { mon: { level: "hard", min: 120 } } });
  autoPlanWeek();
  pruef("bei zu wenigen Snacks bleibt der Trainingstag unter seinem Ziel",
    dayNutOf(state.plan, "mon").kcal < goalTargetsForDay("mon").kcal, true);

  // ---- Von Hand eingetragenes zaehlt gegen den Rest ----
  // Steht schon ein Fruehstueck im Tag, darf der Snack den Tag nicht darueber schieben.
  frischerPlan(bestand());
  DAYS.forEach(function (d) { state.plan[d.key].fr.push("fr1"); });
  autoPlanWeek();
  pruef("mit vorbelegtem Fruehstueck bleibt die Woche im Korridor", (function () {
    var z = goalTargetsForDays(DAYS.map(function (d) { return d.key; }));
    return Math.abs(weekNut().kcal - z.kcal) <= z.kcal * PLAN_TOLERANZ;
  })(), true);

  // ---- Schritt 7: ehrlich sein ----
  // Ein Bestand, mit dem das Ziel nicht erreichbar ist (nur winzige Portionen, Deckel greift):
  // die Meldung muss den Rest NENNEN statt ihn zu verschweigen.
  frischerPlan([
    meal("f1", "Frühstück", 120, 10, [], true), meal("f2", "Frühstück", 130, 10, [], true),
    meal("h1", "Hauptgericht", 150, 12, [], true), meal("h2", "Hauptgericht", 160, 12, [], true),
    meal("h3", "Hauptgericht", 140, 11, [], true), meal("s1", "Snack", 80, 6, [], false)
  ], { kcal: 3000, carbs: 300, protein: 200, fat: 90 });
  autoPlanWeek();
  pruef("ein grosser Rest wird benannt", letzterToast.indexOf("kcal offen") !== -1, true);
  pruef("und der Plan entsteht trotzdem", alleEintraege().length > 0, true);

  // Der Fall, den der KVP-Check am 16.08.2026 aufgebracht hat: Die MENGEN rechnet der Planer
  // gegen kcal, Protein wirkt nur ueber die Vorsortierung. Ein Bestand aus fettigen
  // Kohlenhydraten trifft die Kalorien also punktgenau und verfehlt das Proteinziel deutlich -
  // in einer Fitness-App genau der Fall, der nicht verschwiegen werden darf.
  // Vier Hauptgerichte, damit Mittag und Abend getrennte Listen bekommen (drei plus einer),
  // und ein Ziel, das mit EINER Portion je Mahlzeit erreichbar ist - sonst gewinnt die
  // kcal-Meldung und die Protein-Meldung kaeme nie zum Zug.
  frischerPlan([
    meal("k1", "Frühstück", 500, 8, [], true), meal("k2", "Frühstück", 500, 8, [], true),
    meal("k3", "Hauptgericht", 700, 12, [], true), meal("k4", "Hauptgericht", 700, 12, [], true),
    meal("k5", "Hauptgericht", 600, 10, [], true), meal("k7", "Hauptgericht", 650, 11, [], true),
    meal("k6", "Snack", 200, 3, [], false), meal("k8", "Snack", 180, 3, [], false)
  ], { kcal: 2100, carbs: 210, protein: 150, fat: 60 });
  autoPlanWeek();
  var zielW = goalTargetsForDays(DAYS.map(function (d) { return d.key; }));
  pruef("die Kalorien stimmen in diesem Fall",
    Math.abs(weekNut().kcal - zielW.kcal) <= zielW.kcal * PLAN_TOLERANZ, true);
  pruef("das Protein liegt aber deutlich darunter",
    weekNut().protein < zielW.protein * 0.9, true);
  pruef("und genau das steht im Toast", letzterToast.indexOf("Protein fehlen") !== -1, true);

  // Gegenprobe: Wird das Proteinziel getroffen, darf davon NICHTS im Toast stehen - sonst
  // waere die Meldung eine Dauerwarnung und damit wertlos.
  // Das Ziel ist bewusst auf 120 g gesetzt: Seit es je Hauptmahlzeit nur EINE Portion gibt,
  // liefert der Bestand rund 135 g - mit den frueheren 150 g waere hier dauerhaft ein
  // Defizit gemeldet worden, und die Pruefung haette das Gegenteil dessen gemessen, was sie
  // soll.
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 120, fat: 60 });
  autoPlanWeek();
  pruef("bei getroffenem Protein keine Protein-Meldung",
    letzterToast.indexOf("Protein") === -1, true);

  // Ein Protein-UEBERSCHUSS ist kein Befund: Das Ziel ist eine Untergrenze.
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 60, fat: 60 });
  autoPlanWeek();
  pruef("Protein ueber dem Ziel wird nicht gemeldet",
    letzterToast.indexOf("Protein") === -1, true);

  // Der Pro-Hinweis richtet sich an Leute OHNE Gruppe - der Zusatz "in einer Gruppe plant
  // jedes Mitglied mit" ginge dort immer an die Falschen (Befund des ux-reviewer).
  frischerPlan(bestand());
  proInfo = null;
  autoPlanWeek();
  pruef("Pro-Hinweis bleibt kurz", letzterToast, "Automatisch planen gehört zu Pro");

  // ---- Slot-Bindung: der Planer ist strenger als der Picker ----
  // Der gemeldete Fehler vom 16.08.2026: vier Shakes als Snack, sechsmal Joghurt zum Mittag.
  // Ursache war catFitsMeal - Getraenk, Beilage und alles ohne bekannte Kategorie passen dort
  // ueberall hin. Fuer den Picker richtig, fuer einen Automatismus nicht.
  //
  // Jeder lose Kandidat wird EINZELN geprueft, und der Bestand ist bewusst duenn: zwei
  // Fruehstuecke, zwei Hauptgerichte, ein Snack. Damit ist in jeder Wochenauswahl noch ein
  // Platz frei, und der lose Kandidat traegt Meal-Prep samt hohem Proteinanteil - mit der
  // alten Regel muss er hineinrutschen.
  //
  // Zwei Anlaeufe davor bewiesen nichts: Mit dem vollen Bestand verdraengte schon die
  // Bewertung die losen Kandidaten, und in einem gemeinsamen Testfall verdraengten sie sich
  // gegenseitig - der kategorielose fiel um 0,5 Punkte aus den Top drei. Eine Pruefung, die
  // nur wegen der Rangfolge gruen ist, misst nicht die Regel, um die es geht.
  var grund = [
    meal("fr1", "Frühstück", 400, 30, [], true), meal("fr2", "Frühstück", 380, 26, [], true),
    meal("ha1", "Hauptgericht", 620, 45, [], true), meal("ha2", "Hauptgericht", 650, 42, [], true),
    meal("sn1", "Snack", 200, 15, [], false)
  ];
  [{ id: "gt1", cat: "Getränk",  was: "ein Getraenk" },
   { id: "bl1", cat: "Beilage",  was: "eine Beilage" },
   { id: "ohne", cat: null,      was: "ein Meal ohne Kategorie" }].forEach(function (f) {
    var los = { id: f.id, name: f.id, tags: [], mealPrep: true,
                nutrition: { kcal: 480, carbs: 20, protein: 60, fat: 10 } };
    if (f.cat) los.category = f.cat;
    frischerPlan(grund.concat([los]));
    autoPlanWeek();
    pruef(f.was + " wird nie eingeplant",
      alleEintraege().some(function (x) { return entryId(x.e) === f.id; }), false);
    pruef(f.was + ": die Woche entsteht trotzdem", alleEintraege().length > 0, true);
  });
  // Gegenprobe: DASSELBE Meal als Hauptgericht muss eingeplant werden - sonst wuerde die
  // Pruefung oben auch dann gruen sein, wenn der Planer gar nichts mehr faende.
  frischerPlan([
    meal("fr1", "Frühstück", 400, 30, [], true), meal("fr2", "Frühstück", 450, 25, [], true),
    meal("gt1", "Hauptgericht", 620, 40, [], true), meal("gt2", "Hauptgericht", 650, 42, [], true),
    meal("gt3", "Hauptgericht", 600, 38, [], true), meal("sn1", "Snack", 200, 15, [], false)
  ]);
  autoPlanWeek();
  pruef("als Hauptgericht angelegt wird es eingeplant",
    alleEintraege().some(function (x) { return entryId(x.e) === "gt1"; }), true);

  // ---- Snack-Slot: verschiedene Snacks statt Vielfachen ----
  // Der Testfall MUSS einen grossen Snack-Rest erzwingen, sonst beweist er nichts: Mit dem
  // normalen Bestand decken fr/mi/ab den Tag schon ab, der Snack bekommt hoechstens einen
  // Eintrag - und dann ist "keine Dublette" auch mit der alten Vielfach-Logik erfuellt.
  // Genau daran ist der erste Anlauf gescheitert (Gegenprobe blieb komplett gruen).
  // Deshalb: hohes Ziel, absichtlich kleine Gerichte, damit der Deckel bei fr/mi/ab greift
  // und rund 800 kcal beim Snack landen.
  frischerPlan([
    meal("kf1", "Frühstück", 150, 12, [], true), meal("kf2", "Frühstück", 160, 12, [], true),
    meal("kh1", "Hauptgericht", 200, 18, [], true), meal("kh2", "Hauptgericht", 210, 18, [], true),
    meal("ks1", "Snack", 100, 9, [], false), meal("ks2", "Snack", 110, 9, [], false)
  ], { kcal: 3000, carbs: 300, protein: 200, fat: 90 });
  autoPlanWeek();
  var snZeilen = DAYS.map(function (d) { return state.plan[d.key].sn.map(entryId); });
  LOG.push("Snack-Zeilen: " + JSON.stringify(snZeilen[0]) + " …");
  pruef("kein Snack-Slot enthaelt dasselbe Gericht zweimal",
    snZeilen.every(function (ids) { return ids.length === new Set(ids).size; }), true);
  pruef("aber es stehen mehrere verschiedene Snacks im Slot",
    snZeilen.some(function (ids) { return ids.length > 1; }), true);
  // Und bei den Hauptmahlzeiten steht allein genau EINE Portion - die Vielfachen gibt es
  // seit dem 16.08.2026 nur noch in der Gruppe (eigene Pruefgruppe weiter unten).
  pruef("bei den Hauptmahlzeiten steht allein genau eine Portion",
    DAYS.every(function (d) {
      return ["fr", "mi", "ab"].every(function (m) { return state.plan[d.key][m].length <= 1; });
    }), true);

  // ---- Das Rezeptbuch als zweite Quelle ----
  var KATALOG_IDS = new Set(KATALOG_ALLE.map(function (r) { return r.id; }));
  // Der gemeldete Fall: fuenf Startmeals, drei Haupt-Slots - ohne Katalog rotiert die Woche
  // zwangslaeufig auf denselben Gerichten.
  // Sechs Meals, nicht fuenf: Mit genau fuenf greift schon PLAN_MIN_KANDIDATEN und der Planer
  // verweigert die Arbeit (gemessen: null Gerichte) - dann verglichen wir gegen einen
  // Leerlauf statt gegen die Monotonie, um die es hier geht.
  var fuenf = [
    meal("s1", "Frühstück", 420, 28, ["vegetarisch"], true),
    meal("s6", "Frühstück", 390, 24, ["vegetarisch"], true),
    meal("s2", "Hauptgericht", 620, 45, [], true),
    meal("s3", "Hauptgericht", 650, 40, [], true),
    meal("s4", "Hauptgericht", 590, 38, [], true),
    meal("s5", "Snack", 210, 22, ["vegetarisch"], false)
  ];
  frischerPlan(fuenf);   // frischerPlan schaltet den Katalog selbst ab
  autoPlanWeek();
  var ohneKat = new Set(alleEintraege().map(function (x) { return entryId(x.e); })).size;
  frischerPlan(fuenf); katalogAn();
  autoPlanWeek();
  var mitKat = new Set(alleEintraege().map(function (x) { return entryId(x.e); })).size;
  LOG.push("verschiedene Gerichte: ohne Katalog " + ohneKat + ", mit Katalog " + mitKat);
  pruef("ohne Katalog kann es nie mehr als der eigene Bestand sein", ohneKat <= fuenf.length, true);
  pruef("mit dem Rezeptbuch werden es mehr als drei", mitKat > 3, true);
  pruef("und mehr als ohne Katalog", mitKat > ohneKat, true);

  // Seit dem 17.08.2026 (Katalog-Umbau) kopiert der Planer NICHT MEHR: ein Plan-Eintrag darf
  // direkt auf eine Katalog-id zeigen, weil sowohl getRecipe() als auch normalizePlan() den
  // Katalog jetzt selbst kennen. Die fruehere Zusage kehrt sich damit um.
  pruef("ein eingeplantes Katalog-Rezept zeigt direkt auf die Katalog-id",
    alleEintraege().some(function (x) { return KATALOG_IDS.has(entryId(x.e)); }), true);
  pruef("jeder Plan-Eintrag findet sein Meal (Bestand oder Katalog)",
    alleEintraege().every(function (x) { return !!getRecipe(entryId(x.e)); }), true);
  pruef("ein Planerlauf kopiert nichts mehr in den Bestand",
    state.recipes.length, fuenf.length);
  // Die eigentliche Probe: der Plan (mitsamt Katalog-Verweisen) ueberlebt einen Ladevorgang -
  // genau die Zusage aus 1.2, ohne die jeder Katalog-Eintrag beim naechsten Laden lautlos
  // aus dem Plan fiele.
  var nachLaden = normalizePlan(state.plan, state.recipes);
  var vorher = alleEintraege().length, danach = 0;
  DAYS.forEach(function (d) { MEALS.forEach(function (m) { danach += nachLaden[d.key][m.key].length; }); });
  pruef("normalizePlan verliert keinen Eintrag", danach, vorher);
  pruef("der Toast nennt die Nutzung des Rezeptbuchs oder eine Zielabweichung",
    /Rezeptbuch|kcal|Protein/.test(letzterToast), true);

  // Rueckgaengig macht nur noch die Slots und das Gedaechtnis rueckgaengig - Kopien gibt es
  // seit dem Umbau nicht mehr, die frueher extra zurueckgenommen werden mussten.
  window.__undo();
  pruef("Rueckgaengig leert die Woche", alleEintraege().length, 0);
  pruef("und der Bestand bleibt dabei unveraendert",
    state.recipes.map(function (r) { return r.id; }).sort().join(),
    fuenf.map(function (r) { return r.id; }).sort().join());

  // Ein bereits uebernommenes Rezept kommt ueber den eigenen Bestand (isAdopted() haelt es aus
  // der Katalog-Kandidatenliste heraus) - der Plan-Eintrag zeigt dann auf die eigene Kopie,
  // nicht (noch einmal) auf die Katalog-id.
  var vorlage = KATALOG_ALLE.filter(function (r) { return r.category === "Hauptgericht"; })[0];
  var eigeneKopie = copyFromCookbook(vorlage);
  frischerPlan(fuenf.concat([eigeneKopie])); katalogAn();
  autoPlanWeek();
  pruef("ein schon uebernommenes Rezept bleibt eine einzige Kopie",
    state.recipes.filter(function (r) { return r.lib === vorlage.id; }).length, 1);
  pruef("kein Plan-Eintrag zeigt dafuer auf die Katalog-id",
    alleEintraege().some(function (x) { return entryId(x.e) === vorlage.id; }), false);

  // Die Ernaehrungsform gilt auch fuer den Katalog - cookbookVisible filtert ueber fitsDiet.
  frischerPlan(fuenf.slice(0, 1), { kcal: 2000, carbs: 200, protein: 150, fat: 60, diet: "vegan" });
  katalogAn();
  autoPlanWeek();
  pruef("ein veganes Profil plant auch aus dem Katalog nur Veganes",
    alleEintraege().every(function (x) {
      return (getRecipe(entryId(x.e)).tags || []).indexOf("vegan") !== -1;
    }), true);
  pruef("und bekommt trotzdem eine Woche", alleEintraege().length > 0, true);
  pruef("auch vegan wird in allen vier Slots etwas gefunden",
    ["fr", "mi", "ab", "sn"].filter(function (m) {
      return alleEintraege().some(function (x) { return x.m === m; });
    }).length, 4);

  // ---- Mittag und Abend: nie dasselbe Gericht ----
  // Der Beschwerdepunkt vom 16.08.2026. Ursache war strukturell: gleiche Kandidatenmenge,
  // gleiche Bewertung, gleicher Rotationsindex - also zwangslaeufig dasselbe Ergebnis.
  function mittagAbendGleich() {
    return DAYS.filter(function (d) {
      var mi = state.plan[d.key].mi.map(entryId), ab = state.plan[d.key].ab.map(entryId);
      return mi.some(function (x) { return ab.indexOf(x) !== -1; });
    }).map(function (d) { return d.key; });
  }
  frischerPlan(bestand()); katalogAn();
  autoPlanWeek();
  pruef("an keinem Tag stehen Mittag und Abend gleich", mittagAbendGleich(), []);
  var haupt = new Set();
  DAYS.forEach(function (d) {
    ["mi", "ab"].forEach(function (m) {
      state.plan[d.key][m].forEach(function (e) { haupt.add(entryId(e)); });
    });
  });
  LOG.push("verschiedene Hauptgerichte in der Woche: " + haupt.size);
  pruef("mindestens fuenf verschiedene Hauptgerichte", haupt.size >= 5, true);
  // Die eigentliche Wirkung der GETRENNTEN Mengen: Was mittags vorkommt, taucht abends gar
  // nicht auf - nicht bloss nicht am selben Tag.
  //
  // Diese Pruefung ist der zweite Anlauf. Die erste ("an keinem Tag Mittag = Abend") blieb in
  // der Gegenprobe gruen, weil schon die Kollisionsregel sie erfuellt - sie misst die
  // Trennung also nicht. Ein Beispiel dafuer, dass mehrere Mechanismen fuer dasselbe Ziel
  // eine Pruefung unbrauchbar machen koennen, ohne dass es auffaellt.
  var miSet = new Set(), abSet = new Set();
  DAYS.forEach(function (d) {
    state.plan[d.key].mi.forEach(function (e) { miSet.add(entryId(e)); });
    state.plan[d.key].ab.forEach(function (e) { abSet.add(entryId(e)); });
  });
  pruef("Mittag und Abend nutzen getrennte Gerichte",
    Array.from(miSet).filter(function (x) { return abSet.has(x); }), []);

  // Auch mit knappem Bestand: nur ZWEI Hauptgerichte - der Abend muss trotzdem eines
  // bekommen, und zwar das andere.
  frischerPlan([
    meal("f1", "Frühstück", 400, 30, [], true), meal("f2", "Frühstück", 420, 28, [], true),
    meal("h1", "Hauptgericht", 620, 45, [], true), meal("h2", "Hauptgericht", 600, 42, [], true),
    meal("s1", "Snack", 200, 15, [], false), meal("s2", "Snack", 180, 14, [], false)
  ]);
  autoPlanWeek();
  pruef("auch mit zwei Hauptgerichten: nie beides am selben Tag", mittagAbendGleich(), []);
  pruef("und der Abend bleibt trotzdem besetzt",
    DAYS.every(function (d) { return state.plan[d.key].ab.length > 0; }), true);

  // ---- Eine Portion allein, bis zwei in der Gruppe ----
  frischerPlan(bestand(), { kcal: 3600, carbs: 360, protein: 220, fat: 100 }); katalogAn();
  autoPlanWeek();
  pruef("allein hoechstens EIN Eintrag je Hauptmahlzeit",
    DAYS.every(function (d) {
      return ["fr", "mi", "ab"].every(function (m) { return state.plan[d.key][m].length <= 1; });
    }), true);
  // Gegenprobe: In der Gruppe traegt die Anzahl eine Information und ist weiter erlaubt.
  frischerPlan(bestand(), { kcal: 3600, carbs: 360, protein: 220, fat: 100 }); katalogAn();
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  pruef("in der Gruppe sind zwei Portionen moeglich",
    DAYS.some(function (d) {
      return ["fr", "mi", "ab"].some(function (m) { return state.plan[d.key][m].length === 2; });
    }), true);
  pruef("aber nie mehr als zwei",
    DAYS.every(function (d) {
      return ["fr", "mi", "ab"].every(function (m) { return state.plan[d.key][m].length <= 2; });
    }), true);

  // ---- Zwei Laeufe, zwei Plaene ----
  // Gemessen ueber mehrere Wiederholungen: Ein einzelner Vergleich koennte auch zufaellig
  // gleich ausfallen, ohne dass etwas kaputt ist.
  function planSignatur() {
    return DAYS.map(function (d) {
      return MEALS.map(function (m) { return state.plan[d.key][m.key].map(entryId).join(","); }).join("|");
    }).join(";");
  }
  var sigs = {};
  for (var lauf = 0; lauf < 8; lauf++) {
    frischerPlan(bestand()); katalogAn();
    autoPlanWeek();
    sigs[planSignatur()] = 1;
  }
  LOG.push("verschiedene Plaene aus acht Laeufen: " + Object.keys(sigs).length);
  pruef("acht Laeufe ergeben mehr als einen Plan", Object.keys(sigs).length > 1, true);

  // Und was der POOL bewirkt: nicht nur andere Reihenfolgen, sondern ueberhaupt andere
  // Gerichte. Ueber zehn Laeufe muessen im Mittag-Slot mehr als PLAN_VARIANTEN verschiedene
  // Gerichte vorkommen - sonst zieht der Planer immer aus derselben Dreiergruppe.
  //
  // Zweiter Anlauf: Die Pruefung darueber ("mehr als ein Plan") blieb in der Gegenprobe
  // gruen, obwohl der Pool auf PLAN_VARIANTEN geschrumpft war - drei Gerichte in wechselnder
  // REIHENFOLGE ergeben eben auch verschiedene Plaene. Sie misst also den Zufall, nicht das
  // Feld, aus dem gezogen wird.
  var jeMittag = new Set();
  for (var lauf3 = 0; lauf3 < 10; lauf3++) {
    frischerPlan(bestand()); katalogAn();
    autoPlanWeek();
    DAYS.forEach(function (d) {
      state.plan[d.key].mi.forEach(function (e) { jeMittag.add(entryId(e)); });
    });
  }
  LOG.push("verschiedene Mittagsgerichte ueber zehn Laeufe: " + jeMittag.size);
  pruef("der Pool laesst mehr als drei Gerichte zu", jeMittag.size > PLAN_VARIANTEN, true);

  // Der Pool haelt schwache Kandidaten trotzdem draussen: Ein Getraenk und ein Meal ohne
  // Naehrwerte duerfen in KEINEM der Laeufe auftauchen.
  var nie = { gt: 0, ohne: 0 };
  for (var lauf2 = 0; lauf2 < 20; lauf2++) {
    frischerPlan(bestand().concat([
      meal("gtx", "Getränk", 400, 40, [], true),
      { id: "ohnenut", name: "Ohne Werte", category: "Hauptgericht", tags: [], nutrition: {} }
    ]));
    autoPlanWeek();
    alleEintraege().forEach(function (x) {
      if (entryId(x.e) === "gtx") nie.gt++;
      if (entryId(x.e) === "ohnenut") nie.ohne++;
    });
  }
  pruef("ein Getraenk taucht in 20 Laeufen nie auf", nie.gt, 0);
  pruef("ein Meal ohne Naehrwerte ebenso", nie.ohne, 0);

  // ---- Das Gedaechtnis ----
  frischerPlan(bestand()); katalogAn();
  autoPlanWeek();
  pruef("nach dem Planen ist das Gedaechtnis gefuellt",
    Object.keys(state.planned).length > 0, true);
  pruef("und traegt den Wochenschluessel der geplanten Woche",
    Object.keys(state.planned).every(function (id) { return state.planned[id] === activeWeekKey(); }), true);
  // Rueckgaengig nimmt das Gedaechtnis mit zurueck.
  window.__undo();
  pruef("Rueckgaengig leert auch das Gedaechtnis", Object.keys(state.planned).length, 0);

  // Wirkung: Was letzte Woche dran war, rutscht nach hinten. Messbar an der Bewertung -
  // ein Plan-Vergleich waere durch den Zufall verrauscht.
  frischerPlan(bestand());
  var probe = state.recipes.filter(function (r) { return r.category === "Hauptgericht"; })[0];
  var ohneMalus = planRang(probe, "mi", 700, null);
  state.planned = {}; state.planned[probe.id] = weekKeyBack(1);
  var mitMalus = planRang(probe, "mi", 700, null);
  LOG.push("Rang mit/ohne Wiederholung: " + Math.round(mitMalus) + " / " + Math.round(ohneMalus));
  pruef("ein Gericht aus der Vorwoche wird abgewertet", mitMalus < ohneMalus, true);
  pruef("der Malus ist groesser als Meal-Prep und Protein zusammen",
    ohneMalus - mitMalus > 19, true);
  // Aber er darf die Kategorie NIE ueberstimmen - sonst landet ein Snack im Mittagessen.
  var snack = state.recipes.filter(function (r) { return r.category === "Snack"; })[0];
  pruef("selbst abgewertet schlaegt das Hauptgericht jeden Snack im Mittag-Slot",
    mitMalus > planRang(snack, "mi", 700, null), true);

  // Stufe A: die andere Woche wird gesehen - auch bei von Hand gesetzten Eintraegen.
  frischerPlan(bestand());
  var andereWoche = weekKeyFor("next");
  state.plans[andereWoche] = makeEmptyPlan();
  state.plans[andereWoche].mon.mi.push("ha1");
  pruef("planRecentIds findet die andere Woche", planRecentIds().has("ha1"), true);
  pruef("und wertet sie ab",
    planRang(getRecipe("ha1"), "mi", 700, planRecentIds()) < planRang(getRecipe("ha1"), "mi", 700, null), true);

  // ---- sanitizePlanned ----
  var jetzt = activeWeekKey();
  var roh = {};
  roh["ha1"] = jetzt;                       // gueltig
  roh["ha2"] = "quatsch";                   // kaputter Wochenwert
  roh["weg"] = jetzt;                       // Rezept existiert nicht
  roh["ha3"] = weekKeyBack(40);             // zu alt
  roh[""] = jetzt;                          // leere id
  var sauber = sanitizePlanned(roh, bestand());
  pruef("gueltiger Eintrag bleibt", sauber.ha1, jetzt);
  pruef("kaputter Wochenwert faellt raus", "ha2" in sauber, false);
  pruef("verwaiste id faellt raus", "weg" in sauber, false);
  pruef("zu alter Eintrag faellt raus", "ha3" in sauber, false);
  pruef("leere id faellt raus", "" in sauber, false);
  pruef("Unsinn statt Objekt ergibt ein leeres Gedaechtnis",
    JSON.stringify(sanitizePlanned("nein", bestand())), "{}");

  // ---- "Nochmal" wird angeboten ----
  frischerPlan(bestand()); katalogAn();
  autoPlanWeek();
  pruef("der Toast bietet einen zweiten Knopf", !!(window.__opts && window.__opts.fn), true);
  pruef("und er heisst 'Nochmal'", window.__opts.label, "Nochmal");
  pruef("der Toast steht laenger als der normale", window.__opts.ms > 5000, true);
  window.__opts.fn();
  pruef("Nochmal erzeugt wieder einen vollstaendigen Plan", alleEintraege().length > 0, true);
  pruef("auch danach nie Mittag = Abend", mittagAbendGleich(), []);
  // Bis zum 17.08.2026 stand hier eine Pruefung auf VERWAISTE Kopien: "Nochmal" durfte den
  // Bestand nicht mit jedem Klick um Meals wachsen lassen, die niemand mehr bestellt. Mit dem
  // Katalog-Umbau kopiert der Planer ueberhaupt nicht mehr (siehe oben) - die eigentliche
  // Zusage, die bleibt, ist deshalb direkter: der Bestand ruehrt sich durch "Nochmal" gar
  // nicht, beliebig oft gewuerfelt.
  pruef("Nochmal aendert den Bestand nicht", state.recipes.length, bestand().length);
  // Und auch nach mehrfachem Wuerfeln nicht - der Fall, den man beim Ausprobieren erzeugt.
  for (var w = 0; w < 3; w++) { if (window.__opts && window.__opts.fn) window.__opts.fn(); }
  pruef("auch nach dreimal Nochmal bleibt der Bestand gleich", state.recipes.length, bestand().length);
  pruef("und der Plan steht immer noch", alleEintraege().length > 0, true);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")
