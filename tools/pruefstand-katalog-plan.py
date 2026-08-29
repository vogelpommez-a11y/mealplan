# -*- coding: utf-8 -*-
"""
Ausschneide-Pruefstand fuer den Katalog-Umbau (17.08.2026, plans/Katalog_als_Nachschlagequelle.MD).

Geprueft werden die VIER neuen Zusagen aus dem Plan, Verifikationspunkt 5:

  1. ein Plan mit Katalog-ID ueberlebt normalizePlan()
  2. ein Planerlauf laesst state.recipes.length unveraendert
  3. Uebernehmen aus einem Slot biegt den Planeintrag auf die Kopie um
  4. die Migration loescht eine unveraenderte Kopie, laesst eine veraenderte stehen und
     verliert dabei keinen Planeintrag

Wie bei den Nachbar-Pruefstaenden (pruefstand-autoplaner.py, pruefstand-gruppenlimit.py):
alle Funktionen werden aus index.html ausgeschnitten, nichts abgetippt. Gestubbt sind nur die
Randstuecke (save/render/toast/Sync-Variablen).
"""
import io, os

# Der Pfad ist ein Argument, kein fester Wert: Nur so laesst sich der Pruefstand gegen
# einen ALTEN Stand fahren - und ohne Gegenprobe zaehlt kein Ergebnis (docs/TESTING.md).
import sys

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-katalog-plan.html")
lines = pm_quelle.lade_seite(SRC).split("\n")


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


# Genau EINE Zeile - siehe Begruendung in pruefstand-autoplaner.py.
def zeile(sig):
    for z in lines:
        if z.startswith(sig): return z
    raise SystemExit("ZEILE NICHT GEFUNDEN: " + sig)


teile = [
    block("  const DAYS = [", "  ];"),
    block("  const MEALS = [", "  ];"),
    block("  const CATEGORIES = [", "  const CAT_LEGACY ="),
    schnitt("  function catFitsMeal("),
    schnitt("  function catSuggestsMeal("),
    schnitt("  function catPlanFitsMeal("),
    # Der Katalog selbst - Kern dieses Pruefstands.
    block("  const COOKBOOK = [", "  ];"),
    schnitt("  function cookbookVisible("),
    schnitt("  function isAdopted("),
    schnitt("  function copyFromCookbook("),
    schnitt("  function sanitizeRecipe("),
    schnitt("  function normalizePlan("),
    schnitt("  function asIdList("),
    schnitt("  function dietOk("),
    schnitt("  function avoidOk("),
    schnitt("  function fitsDiet("),
    schnitt("  function entryId("),
    schnitt("  function entryUids("),
    schnitt("  function entryIsShared("),
    schnitt("  function makeEntry("),
    schnitt("  function slotIsShared("),
    schnitt("  function makeEmptyPlan("),
    schnitt("  function isoWeekKey("),
    schnitt("  function weekKeyFor("),
    schnitt("  function activeWeekKey("),
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
    block("  // ---------- Auto-Wochenplaner (D2) ----------", "  const PLAN_TOLERANZ ="),
    schnitt("  function slotOpenForMe("),
    schnitt("  function planKandidaten("),
    schnitt("  function planRang("),
    schnitt("  function planWochengerichte("),
    schnitt("  function planUebernahme("),
    schnitt("  function planTagKcal("),
    schnitt("  function planRecentIds("),
    zeile("  const PLAN_GEDAECHTNIS_WOCHEN = "),
    schnitt("  function sanitizePlanned("),
    block("  let weekBackCache = ", "  }"),
    schnitt("  function autoPlanWeek("),
    # ---- Teil 1.5 / Teil 2 / Teil 3 des Katalog-Umbaus - der eigentliche Pruefgegenstand ----
    schnitt("  function dropRecipeIds("),
    schnitt("  function rewritePlanIds("),
    schnitt("  function adoptFromCookbook("),
    schnitt("  function canonValue("),
    zeile("  function canonJSON("),
    zeile("  const DEDUPE_FELDER = "),
    schnitt("  function kopieEntsprichtKatalog("),
    schnitt("  function dedupeAgainstCatalog("),
    # ---- Handauswahl: dieselbe Menge wie der Planer ----
    schnitt("  function libraryRecipes("),
    schnitt("  function pickerQuellen("),
    # ---- Teil 2: Gruppenbeitritt gleicht ab ----
    schnitt("  async function copyOwnRecipesToGroup("),
]
code = "\n\n".join(teile)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Katalog-Umbau</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) {
  console.log("JS-FEHLER: " + m + " (Zeile " + z + ")");
  console.log("ERGEBNIS 0 gruen, 1 rot");
  var el = document.getElementById("log");
  if (el) el.textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
};
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  var zeile = (gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll));
  LOG.push(zeile);
  console.log(zeile);   // damit der headless-Lauf dasselbe sieht wie das Browserfenster
  var el = document.getElementById("log");
  if (el) el.textContent = LOG.join("\\n");
}

// ---- Randstuecke ----
var state = { goal: null, recipes: [], plans: {}, plan: null, viewWeek: "cur", favs: [], planned: {}, dedupeV1: false };
var recipeIndex = null, dayNutCache = null;
var syncUid = null, syncGid = null, myRole = null, groupMembers = [], proInfo = null, syncHandshakeOk = true;
var gespeichert = 0, gezeichnet = 0, letzterToast = "";
function save() { gespeichert++; }
function render() { gezeichnet++; }
function toast(t) { letzterToast = t; window.__undo = null; }
function undoToast(t, cb, opts) { letzterToast = t; window.__undo = cb; window.__opts = opts || null; }
var lfdUid = 0;
function uid() { return "u" + (++lfdUid); }
function safeImage(x) { return x || null; }
function migrateCat(c) { return c; }
function sanitizeIng(x) { return x; }
function sanitizeTags(t) { return Array.isArray(t) && t.length ? t.slice() : null; }
function esc(s) { return String(s == null ? "" : s); }

// ---- Firestore-Attrappe fuer copyOwnRecipesToGroup() ----
// Vorbild: pruefstand-gruppenlimit.py. Sie zeichnet nur auf, WAS hochgeladen wird - die
// eigentliche Regel (Firestore Security Rules) ist hier nicht pruefbar (CLAUDE.md, Ziffer 12).
var GRUPPENBESTAND = [];
var hochgeladenAn = [];
window.CloudSync = {
  loadRecipes: function (base) { return Promise.resolve(GRUPPENBESTAND.slice()); },
  saveRecipesBatch: function (base, puts, delIds) {
    hochgeladenAn.push(puts.map(function (r) { return r.id; }));
    puts.forEach(function (r) { GRUPPENBESTAND.push(r); });
    return Promise.resolve();
  }
};

__CODE__

// ---- Hilfen fuer den Pruefstand selbst ----
function meal(id, kat, kcal, prot, tags, prep) {
  return { id: id, name: id, category: kat, tags: tags || [], mealPrep: prep === true,
           nutrition: { kcal: kcal, carbs: 10, protein: prot == null ? 20 : prot, fat: 10 } };
}
function frisch() {
  state.recipes = []; state.favs = []; state.planned = {}; state.dedupeV1 = false;
  state.plans = {}; state.plans[activeWeekKey()] = makeEmptyPlan();
  state.plan = state.plans[activeWeekKey()];
  syncUid = null; syncGid = null; myRole = null; groupMembers = []; syncHandshakeOk = true;
  proInfo = { pro: true, source: "manual", until: null };
  gespeichert = 0; gezeichnet = 0; letzterToast = "";
}
function alleEintraege(plan) {
  var out = [];
  DAYS.forEach(function (d) { MEALS.forEach(function (m) {
    (plan || state.plan)[d.key][m.key].forEach(function (e) { out.push({ d: d.key, m: m.key, e: e }); });
  }); });
  return out;
}

(function () {
  frisch();

  // ---- Zusage 1: ein Plan mit Katalog-ID ueberlebt normalizePlan() ----
  (function () {
    var katalogId = COOKBOOK[0].id;
    var roh = makeEmptyPlan();
    roh.mon.mi.push(katalogId);
    var normiert = normalizePlan(roh, []);   // LEERER eigener Bestand - nur der Katalog traegt hier
    pruef("eine Katalog-id im Plan bleibt nach normalizePlan() erhalten",
      normiert.mon.mi, [katalogId]);
    // Gegenprobe: eine erfundene id, die es nirgends gibt, faellt weiterhin raus.
    var roh2 = makeEmptyPlan();
    roh2.mon.mi.push("es-gibt-mich-nicht");
    pruef("eine unbekannte id faellt weiterhin raus",
      normalizePlan(roh2, []).mon.mi, []);
  })();

  // ---- Zusage 2: ein Planerlauf laesst state.recipes.length unveraendert ----
  (function () {
    frisch();
    var bestand = [
      meal("fr1", "Frühstück", 400, 30, ["vegetarisch"], true),
      meal("ha1", "Hauptgericht", 620, 45, [], true),
      meal("ha2", "Hauptgericht", 650, 42, [], true),
      meal("sn1", "Snack", 200, 15, [], false)
    ];
    state.recipes = bestand.slice();
    state.goal = { kcal: 2000, carbs: 200, protein: 150, fat: 60 };
    var vorher = state.recipes.length;
    autoPlanWeek();
    pruef("ein Planerlauf mit Katalog-Kandidaten laesst state.recipes.length unveraendert",
      state.recipes.length, vorher);
    pruef("und trotzdem ist etwas eingeplant worden", alleEintraege().length > 0, true);
    // Mindestens ein Katalog-Rezept sollte bei dem duennen Bestand zum Zug gekommen sein -
    // sonst pruefte die Zeile oben nur einen Zufallstreffer ohne Katalog-Beteiligung.
    var katalogIds = new Set(COOKBOOK.map(function (r) { return r.id; }));
    pruef("mindestens ein Plan-Eintrag stammt direkt aus dem Katalog",
      alleEintraege().some(function (x) { return katalogIds.has(entryId(x.e)); }), true);
  })();

  // ---- Zusage 3: Uebernehmen aus einem Slot biegt den Planeintrag auf die Kopie um ----
  (function () {
    frisch();
    var vorlage = COOKBOOK[0];
    // Der Planer traegt seit dem 17.08.2026 die Katalog-id direkt ein - hier simuliert:
    // ein Slot zeigt auf das Original, so wie es ein echter Planerlauf hinterlassen wuerde.
    state.plan.mon.mi.push(vorlage.id);
    // Zweite Woche, um zu zeigen, dass ALLE Wochen umgebogen werden, nicht nur die aktive.
    var andereWoche = weekKeyFor("next");
    state.plans[andereWoche] = makeEmptyPlan();
    state.plans[andereWoche].tue.ab.push(vorlage.id);
    state.planned[vorlage.id] = activeWeekKey();   // Gedaechtnis - muss mitwandern

    adoptFromCookbook(vorlage.id);
    var kopie = state.recipes.filter(function (r) { return r.lib === vorlage.id; })[0];
    pruef("adoptFromCookbook legt eine Kopie an", !!kopie, true);
    pruef("der Slot in der aktiven Woche zeigt jetzt auf die Kopie",
      state.plan.mon.mi, [kopie.id]);
    pruef("und NICHT mehr auf das Original",
      state.plan.mon.mi.indexOf(vorlage.id), -1);
    pruef("derselbe Umbiegevorgang traf auch die ANDERE Woche",
      state.plans[andereWoche].tue.ab, [kopie.id]);
    pruef("das Planer-Gedaechtnis ist mitgewandert",
      state.planned[kopie.id], activeWeekKey());
    pruef("und der alte Katalog-Schluessel steht dort nicht mehr",
      vorlage.id in state.planned, false);

    // Rueckgaengig: die Kopie verschwindet wieder, UND der Slot zeigt wieder auf das Original.
    window.__undo();
    pruef("Rueckgaengig entfernt die Kopie wieder",
      state.recipes.some(function (r) { return r.id === kopie.id; }), false);
    pruef("und der Slot zeigt wieder auf die Katalog-id",
      state.plan.mon.mi, [vorlage.id]);
  })();

  // ---- Zusage 4: die Migration raeumt Altlasten auf, ohne Planeintraege zu verlieren ----
  (function () {
    frisch();
    var vorlageA = COOKBOOK.filter(function (r) { return r.category === "Hauptgericht"; })[0];
    var vorlageB = COOKBOOK.filter(function (r) { return r.category === "Frühstück"; })[0];

    var unveraendert = copyFromCookbook(vorlageA);              // 1:1 Dublette des Katalogs
    var veraendert = copyFromCookbook(vorlageB);
    veraendert.name = veraendert.name + " (mit Chili)";         // bewusst abweichend
    var favorisiert = copyFromCookbook(vorlageA);                // inhaltlich gleich, aber Favorit
    state.recipes = [unveraendert, veraendert, favorisiert];
    state.favs = [favorisiert.id];

    state.plan.mon.mi.push(unveraendert.id);
    state.plan.mon.fr.push(veraendert.id);
    state.plan.tue.mi.push(favorisiert.id);
    var andereWoche = weekKeyFor("next");
    state.plans[andereWoche] = makeEmptyPlan();
    state.plans[andereWoche].wed.mi.push(unveraendert.id);       // zweite Woche, muss MIT umgebogen werden

    var vorherAnzahl = alleEintraege().length + alleEintraege(state.plans[andereWoche]).length;

    dedupeAgainstCatalog();

    pruef("die unveraenderte Kopie ist geloescht",
      state.recipes.some(function (r) { return r.id === unveraendert.id; }), false);
    pruef("die veraenderte Kopie bleibt stehen",
      state.recipes.some(function (r) { return r.id === veraendert.id; }), true);
    pruef("die favorisierte Kopie bleibt stehen, obwohl inhaltlich identisch",
      state.recipes.some(function (r) { return r.id === favorisiert.id; }), true);
    pruef("der Plan-Eintrag der geloeschten Kopie zeigt jetzt auf die Katalog-id",
      state.plan.mon.mi, [vorlageA.id]);
    pruef("dasselbe gilt in der ANDEREN Woche",
      state.plans[andereWoche].wed.mi, [vorlageA.id]);
    pruef("der Eintrag der veraenderten Kopie ist unangetastet",
      state.plan.mon.fr, [veraendert.id]);
    pruef("der Eintrag der favorisierten Kopie ist unangetastet",
      state.plan.tue.mi, [favorisiert.id]);
    var nachherAnzahl = alleEintraege().length + alleEintraege(state.plans[andereWoche]).length;
    pruef("kein Plan-Eintrag ist verloren gegangen", nachherAnzahl, vorherAnzahl);
    pruef("die Migration merkt sich, dass sie gelaufen ist", state.dedupeV1, true);

    // Zweiter Lauf: idempotent, tut nichts mehr.
    var standVorher = JSON.stringify(state.recipes.map(function (r) { return r.id; }).sort());
    dedupeAgainstCatalog();
    pruef("ein zweiter Lauf aendert nichts mehr",
      JSON.stringify(state.recipes.map(function (r) { return r.id; }).sort()), standVorher);
  })();

  // ---- Die Handauswahl sieht dieselbe Menge wie der Planer ----
  // Ohne das duerfte der Auto-Planer aus dem Rezeptbuch waehlen und der Mensch nicht - eine
  // Asymmetrie, die nach der Migration richtig weh taete: Der Bestand schrumpft dann auf das
  // Selbstangelegte, waehrend 34 Katalog-Rezepte danebenliegen.
  (function () {
    frisch();
    var eigenes = meal("mein-1", "Hauptgericht", 500, 40, [], false);
    state.recipes = [eigenes];

    var quellen = pickerQuellen();
    pruef("die Handauswahl bietet das eigene Meal an",
      quellen.some(function (r) { return r.id === "mein-1"; }), true);
    pruef("und zusaetzlich das gesamte sichtbare Rezeptbuch",
      quellen.filter(function (r) { return r.__cb; }).length, cookbookVisible().length);
    pruef("der Katalog-Kandidat traegt eine Katalog-id, ist also direkt einplanbar",
      !!getRecipe(quellen.filter(function (r) { return r.__cb; })[0].id), true);

    // Uebernommen heisst: kommt ueber den eigenen Bestand, nicht doppelt.
    var vorlage = COOKBOOK[0];
    state.recipes = [eigenes, copyFromCookbook(vorlage)];
    var nachher = pickerQuellen();
    pruef("ein uebernommenes Rezept steht genau einmal in der Auswahl",
      nachher.filter(function (r) { return r.name === vorlage.name; }).length, 1);
    pruef("und zwar als eigene Kopie, nicht als Katalogeintrag",
      nachher.filter(function (r) { return r.name === vorlage.name; })[0].__cb, undefined);

    // Der Katalog selbst darf dabei nie eine Marke abbekommen.
    pruef("COOKBOOK bleibt unberuehrt - __cb sitzt nur an der flachen Kopie",
      COOKBOOK.some(function (r) { return r.__cb; }), false);
  })();

  // ---- Der reale Fall vom 16.08.2026: BEIDE Haelften eines Paars im SELBEN Slot ----
  // Montag Fruehstueck zeigte "Chia-Pudding" zweimal - zwei verschiedene Rezepte mit
  // demselben `lib`. Biegt die Migration beide um, steht danach zweimal DIESELBE id im
  // selben Slot. Das ist festgehaltenes Verhalten, kein Versehen: Es bleibt bei zwei
  // Portionen, so wie vorher auch, und der Nutzer entfernt eine davon von Hand. Die
  // Migration darf hier nur eines nicht - einen Eintrag verlieren oder den Slot leeren.
  (function () {
    frisch();
    var vorlage = COOKBOOK[0];
    var ersteHaelfte = copyFromCookbook(vorlage);
    var zweiteHaelfte = copyFromCookbook(vorlage);       // gleiches lib, andere id
    state.recipes = [ersteHaelfte, zweiteHaelfte];
    state.plan.mon.fr.push(ersteHaelfte.id);
    state.plan.mon.fr.push(zweiteHaelfte.id);

    dedupeAgainstCatalog();

    pruef("beide Haelften des Paars sind aus dem Bestand verschwunden", state.recipes.length, 0);
    pruef("der Slot behaelt BEIDE Eintraege, jetzt auf der Katalog-id",
      state.plan.mon.fr, [vorlage.id, vorlage.id]);
    pruef("und beide loesen sich auf ein Rezept auf (kein Geisterverweis)",
      state.plan.mon.fr.every(function (e) { return !!getRecipe(entryId(e)); }), true);
  })();

  // ---- Vorsichtsregel: in einer Gruppe laeuft die Migration GAR NICHT ----
  // Bis zum 28.08.2026 stand hier die Erwartung "nach dem Handshake laeuft dieselbe
  // Migration nach". Die Bedingung war `syncGid && !syncHandshakeOk` - die Migration lief
  // also im gemeinsamen Bestand, sobald der Handshake stand. Das ist seit Ziffer 128 in
  // docs/TROUBLESHOOTING.md abgeschaltet: `state.dedupeV1` steht nur im localStorage und ist
  // damit ein GERAETE-Flag; in der Gruppe raeumte die Migration aber fremden Bestand auf, und
  // jedes weitere Geraet liess sie erneut darauf los.
  (function () {
    frisch();
    var vorlage = COOKBOOK[0];
    var kopie = copyFromCookbook(vorlage);
    state.recipes = [kopie];
    syncGid = "g1"; syncHandshakeOk = false;
    dedupeAgainstCatalog();
    pruef("vor dem Handshake bleibt die Gruppe unangetastet", state.recipes.length, 1);
    pruef("und das Flag bleibt unten, damit es spaeter erneut versucht wird",
      state.dedupeV1, false);
    syncHandshakeOk = true;
    dedupeAgainstCatalog();
    pruef("auch NACH dem Handshake bleibt der Gruppenbestand unangetastet",
      state.recipes.length, 1);
    pruef("und das Flag bleibt weiterhin unten - nach dem Verlassen wird nachgeholt",
      state.dedupeV1, false);
    // Gegenprobe: ohne Gruppe raeumt dieselbe Migration sofort auf.
    syncGid = null;
    dedupeAgainstCatalog();
    pruef("ohne Gruppe laeuft sie sofort", state.recipes.length, 0);
    pruef("und setzt jetzt das Flag", state.dedupeV1, true);
  })();

  // ---- Zusage 6: Gruppen-Merge - zwei Bestaende mit gleichem `lib` zusammenfuehren ----
  // Vorbild: pruefstand-gruppenlimit.html. Die Ausgangslage ist der Normalfall aus Teil 2:
  // zwei Konten mit demselben Profil, also denselben Startmeals (STARTER) - eines ist schon
  // in der Gruppe, das andere tritt gerade bei.
  (function () {
    frisch();
    var vorlage = COOKBOOK[0];
    // Schon in der Gruppe: die Kopie des ERSTEN Mitglieds (z. B. der Owner, ueber
    // prepareGroup() laengst hochgeladen).
    var schonDrin = copyFromCookbook(vorlage);
    GRUPPENBESTAND = [schonDrin];
    hochgeladenAn = [];

    // Meine eigene Welt: dieselbe Vorlage (eigene id!), dazu ein eindeutiges eigenes Meal.
    var meineKopie = copyFromCookbook(vorlage);
    var eigenes = meal("banane", "Snack", 100, 1, [], false);   // kein `lib` - bleibt unangetastet
    state.recipes = [meineKopie, eigenes];
    state.plan.mon.mi.push(meineKopie.id);
    var andereWoche = weekKeyFor("next");
    state.plans[andereWoche] = makeEmptyPlan();
    state.plans[andereWoche].wed.mi.push(meineKopie.id);

    copyOwnRecipesToGroup("g1").then(function () {
      pruef("meine ueberfluessige Kopie wird NICHT hochgeladen",
        hochgeladenAn.some(function (ids) { return ids.indexOf(meineKopie.id) !== -1; }), false);
      pruef("mein eindeutiges eigenes Meal wird hochgeladen",
        hochgeladenAn.some(function (ids) { return ids.indexOf("banane") !== -1; }), true);
      pruef("in der Gruppe bleibt genau EIN Rezept mit diesem `lib` stehen",
        GRUPPENBESTAND.filter(function (r) { return r.lib === vorlage.id; }).length, 1);
      pruef("mein Plan-Eintrag zeigt jetzt auf die schon vorhandene Gruppen-id",
        state.plan.mon.mi, [schonDrin.id]);
      pruef("dasselbe gilt in der anderen Woche - beide Plaene bleiben intakt",
        state.plans[andereWoche].wed.mi, [schonDrin.id]);

      // Gegenprobe: Meals ohne `lib` werden NIE dedupliziert, auch nicht bei Namensgleichheit -
      // zwei Leute duerfen je eine eigene "Banane" haben (unterschiedliche ids, wie es
      // uid() in der echten App auch liefert - ein Namensabgleich waere hier der Fehler).
      var fremdeBanane = meal("banane-fremd", "Snack", 100, 1, [], false);
      fremdeBanane.name = "Banane";
      GRUPPENBESTAND.push(fremdeBanane);
      hochgeladenAn = [];
      var meineBanane = meal("banane-mein", "Snack", 100, 1, [], false);
      meineBanane.name = "Banane";
      state.recipes = [meineBanane];
      return copyOwnRecipesToGroup("g1");
    }).then(function () {
      pruef("Meals ohne lib werden nicht dedupliziert - meine eigene Banane wird trotzdem hochgeladen",
        hochgeladenAn.some(function (ids) { return ids.indexOf("banane-mein") !== -1; }), true);
      pruef("beide Bananen stehen danach in der Gruppe",
        GRUPPENBESTAND.filter(function (r) { return r.name === "Banane"; }).length, 2);

      LOG.push("");
      LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
      console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
      document.getElementById("log").textContent = LOG.join("\\n");
    });
  })();
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))


# --- Selbst fahren, statt nur zu schreiben (28.08.2026) --------------------------------
# Bis dahin endete dieses Skript hier mit print("geschrieben") und Rueckgabewert 0. Der
# Reihenlauf (tools/alle-pruefstaende.py) bewertet ausschliesslich den Rueckgabewert - er
# meldete diesen Pruefstand also dauerhaft gruen, ohne dass je eine Zusage geprueft wurde.
# Aufgefallen ist es erst, als eine seiner Erwartungen durch eine Aenderung falsch wurde und
# trotzdem niemand rot sah (docs/TROUBLESHOOTING.md 131).
#
# Die HTML-Datei bleibt erhalten: docs/ARCHITECTURES.md verweist darauf, und im Browser
# geoeffnet zeigt sie dasselbe Protokoll - nur eben fuer Menschen.
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def fahren():
    import re, shutil, subprocess, tempfile
    tmp = tempfile.mkdtemp(prefix="mp-katalog-")
    try:
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=8000",
             "--user-data-dir=" + os.path.join(tmp, "profil"),
             "--enable-logging=stderr", "--v=0", "file:///" + OUT.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        aus = (p.stdout or "") + (p.stderr or "")
        zeilen = []
        for z in aus.split("\n"):
            m = re.search(r'CONSOLE:\d+\] "(.*)", source', z)
            if m:
                zeilen.append(m.group(1))
        if not zeilen:
            print("Keine Konsolenausgabe - lief das Script? Rohausgabe:")
            print(aus[:2000])
            return 2
        for z in zeilen:
            print(z)
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        if not letzte:
            print("Kein ERGEBNIS - der asynchrone Teil ist nicht fertig geworden.")
            return 2
        return 0 if letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import sys
    sys.exit(fahren())
