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
    schnitt("  function makeEntry("),
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
    schnitt("  function planAdopt("),
    schnitt("  function planTagKcal("),
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
function undoToast(t, cb) { letzterToast = t; window.__undo = cb; }
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
  var mi = planWochengerichte(kand, "mi");
  pruef("Meal-Prep steht vorn", mi[0].mealPrep, true);
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

  // ---- Gruppe: Zuweisung nur an mich ----
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  autoPlanWeek();
  pruef("in der Gruppe zaehlt jeder Eintrag nur fuer mich",
    alleEintraege().every(function (x) {
      var u = entryUids(x.e); return !!u && u.length === 1 && u[0] === "ich"; }), true);
  pruef("kein Eintrag ist eine geteilte Objektreferenz",
    (function () {
      var e = alleEintraege().map(function (x) { return x.e; });
      for (var i = 0; i < e.length; i++) for (var j = i + 1; j < e.length; j++) if (e[i] === e[j]) return false;
      return true;
    })(), true);

  // ---- Regel 5: vorhandenes Gericht der anderen uebernehmen ----
  frischerPlan(bestand());
  syncGid = "g1"; myRole = "edit"; syncUid = "ich"; groupMembers = [{ uid: "ich" }, { uid: "du" }];
  state.plan.mon.mi.push({ id: "ha3", uids: ["du"] });
  autoPlanWeek();
  pruef("der Slot der anderen gilt als offen fuer mich", state.plan.mon.mi.length > 1, true);
  pruef("und ich bekomme DASSELBE Gericht",
    state.plan.mon.mi.slice(1).every(function (e) { return entryId(e) === "ha3"; }), true);
  pruef("der fremde Eintrag bleibt unangetastet",
    JSON.stringify(state.plan.mon.mi[0]), JSON.stringify({ id: "ha3", uids: ["du"] }));

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
  pruef("auch das grosse Ziel bleibt im Korridor", (function () {
    var z = goalTargetsForDays(DAYS.map(function (d) { return d.key; }));
    return Math.abs(weekNut().kcal - z.kcal) <= z.kcal * PLAN_TOLERANZ;
  })(), true);

  // Trainingstage haben ein hoeheres Ziel - der Planer muss das mitnehmen, weil er
  // goalTargetsForDay() fragt und nicht goalTargets(1).
  frischerPlan(bestand(), { kcal: 2000, carbs: 200, protein: 150, fat: 60, weight: 80,
                            training: { mon: { level: "hard", min: 90 } } });
  autoPlanWeek();
  pruef("Trainingstag hat ein hoeheres Ziel als der Ruhetag",
    goalTargetsForDay("mon").kcal > goalTargetsForDay("tue").kcal, true);
  pruef("und bekommt auch mehr eingeplant",
    dayNutOf(state.plan, "mon").kcal > dayNutOf(state.plan, "tue").kcal, true);

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
  frischerPlan([
    meal("k1", "Frühstück", 500, 8, [], true), meal("k2", "Frühstück", 500, 8, [], true),
    meal("k3", "Hauptgericht", 700, 12, [], true), meal("k4", "Hauptgericht", 700, 12, [], true),
    meal("k5", "Hauptgericht", 600, 10, [], true), meal("k6", "Snack", 200, 3, [], false)
  ], { kcal: 2000, carbs: 200, protein: 150, fat: 60 });
  autoPlanWeek();
  var zielW = goalTargetsForDays(DAYS.map(function (d) { return d.key; }));
  pruef("die Kalorien stimmen in diesem Fall",
    Math.abs(weekNut().kcal - zielW.kcal) <= zielW.kcal * PLAN_TOLERANZ, true);
  pruef("das Protein liegt aber deutlich darunter",
    weekNut().protein < zielW.protein * 0.9, true);
  pruef("und genau das steht im Toast", letzterToast.indexOf("Protein fehlen") !== -1, true);

  // Gegenprobe: Wird das Proteinziel getroffen, darf davon NICHTS im Toast stehen - sonst
  // waere die Meldung eine Dauerwarnung und damit wertlos.
  frischerPlan(bestand());
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
  // Gegenprobe zur Aussagekraft: Bei fr/mi/ab ist das Vielfache ausdruecklich erwuenscht
  // (2x Porridge bei grossem Ziel) - dort muss dieselbe Pruefung fehlschlagen, sonst haette
  // die Aenderung schlicht alle Vielfachen abgeschafft.
  pruef("bei den Hauptmahlzeiten stehen weiterhin Vielfache",
    DAYS.some(function (d) {
      return ["fr", "mi", "ab"].some(function (m) {
        var ids = state.plan[d.key][m].map(entryId);
        return ids.length > 1 && new Set(ids).size === 1;
      });
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

  // Jedes eingeplante Katalog-Rezept MUSS als Kopie im Bestand liegen - sonst wirft
  // normalizePlan() den Eintrag beim naechsten Laden lautlos weg.
  pruef("kein Plan-Eintrag zeigt auf eine Katalog-id",
    alleEintraege().some(function (x) { return KATALOG_IDS.has(entryId(x.e)); }), false);
  pruef("jeder Plan-Eintrag findet sein Meal im Bestand",
    alleEintraege().every(function (x) { return !!getRecipe(entryId(x.e)); }), true);
  var kopien = state.recipes.filter(function (r) { return !!r.lib; });
  pruef("es sind Kopien entstanden", kopien.length > 0, true);
  pruef("jede Kopie traegt eine Herkunft aus dem Katalog",
    kopien.every(function (r) { return KATALOG_IDS.has(r.lib); }), true);
  pruef("jede Kopie hat eine EIGENE id",
    kopien.every(function (r) { return !KATALOG_IDS.has(r.id); }), true);
  pruef("keine Kopie traegt einen Bildpfad",
    kopien.some(function (r) { return "img" in r; }), false);
  // Die eigentliche Probe: der Plan ueberlebt einen Ladevorgang.
  var nachLaden = normalizePlan(state.plan, state.recipes);
  var vorher = alleEintraege().length, danach = 0;
  DAYS.forEach(function (d) { MEALS.forEach(function (m) { danach += nachLaden[d.key][m.key].length; }); });
  pruef("normalizePlan verliert keinen Eintrag", danach, vorher);
  // Ein Katalog-Rezept an mehreren Tagen darf nur EINMAL kopiert werden.
  pruef("keine doppelten Kopien desselben Rezepts",
    kopien.map(function (r) { return r.lib; }).length,
    new Set(kopien.map(function (r) { return r.lib; })).size);
  pruef("der Toast nennt die Uebernahme oder eine Zielabweichung",
    /Rezeptbuch|kcal|Protein/.test(letzterToast), true);

  // Rueckgaengig nimmt BEIDES zurueck - Plan und die still uebernommenen Meals.
  window.__undo();
  pruef("Rueckgaengig leert die Woche", alleEintraege().length, 0);
  pruef("Rueckgaengig entfernt auch die Kopien", state.recipes.length, fuenf.length);
  pruef("und laesst die eigenen Meals stehen",
    state.recipes.map(function (r) { return r.id; }).sort().join(),
    fuenf.map(function (r) { return r.id; }).sort().join());

  // Ein bereits uebernommenes Rezept kommt ueber den eigenen Bestand - nicht ein zweites Mal.
  var vorlage = KATALOG_ALLE.filter(function (r) { return r.category === "Hauptgericht"; })[0];
  frischerPlan(fuenf.concat([copyFromCookbook(vorlage)])); katalogAn();
  autoPlanWeek();
  pruef("ein schon uebernommenes Rezept wird nicht erneut kopiert",
    state.recipes.filter(function (r) { return r.lib === vorlage.id; }).length, 1);

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

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")
