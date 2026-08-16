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

__CODE__

// ---- Hilfen fuer den Pruefstand selbst ----
function meal(id, kat, kcal, prot, tags, prep) {
  return { id: id, name: id, category: kat, tags: tags || [], mealPrep: prep === true,
           nutrition: { kcal: kcal, carbs: 10, protein: prot == null ? 20 : prot, fat: 10 } };
}
function frischerPlan(recipes, goal) {
  state.recipes = recipes || [];
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

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")
