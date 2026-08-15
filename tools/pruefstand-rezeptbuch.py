# Ausschneide-Pruefstand Rezeptbuch: Katalog, Profilfilter und Uebernahme.
import io, os, re

SRC = r"C:\Users\Paddy\Documents\Paddys Mealplan\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-cookbook.html")
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
    block("  const COOKBOOK = [", "  ];"),
    block("  const DIETS = [", "  const AVOID_KEYS ="),
    block("  const RECIPE_TAGS = [", "  const RECIPE_TAG_KEYS ="),
    schnitt("  function dietOk("),
    schnitt("  function avoidOk("),
    schnitt("  function fitsDiet("),
    schnitt("  function cookbookVisible("),
    schnitt("  function isAdopted("),
    schnitt("  function adoptFromCookbook("),
    schnitt("  function sanitizeRecipe("),
    schnitt("  function nutNum("),
    schnitt("  function ingObj("),
    schnitt("  function recipeMatchesFilters("),
    schnitt("  function recipeFilterHtml("),
]
code = "\n\n".join(teile)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Rezeptbuch</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
}
var state = { goal: null, recipes: [] };
var gespeichert = 0, gezeichnet = 0, letzterToast = "";
function save() { gespeichert++; }
function render() { gezeichnet++; }
function undoToast(t, cb) { letzterToast = t; window.__undo = cb; }
function uid() { return "r" + (Math.random() * 1e9 | 0); }
function safeImage(x) { return x || null; }
function migrateCat(c) { return c; }
function sanitizeIng(x) { return x; }
function sanitizeTags(t) { return Array.isArray(t) && t.length ? t.slice() : null; }
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
  return ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]; }); }
function libraryRecipes() { return state.recipes.filter(function (r) { return r.quick !== true; }); }
var recipeFilters = new Set();

__CODE__

(function () {
  // ---- Der Katalog selbst: Struktur, die spaeter 30-100 Eintraege tragen muss ----
  pruef("Katalog ist nicht leer", COOKBOOK.length > 0, true);
  var ids = COOKBOOK.map(function (r) { return r.id; });
  pruef("alle ids eindeutig", ids.length === new Set(ids).size, true);
  pruef("alle haben eine id", COOKBOOK.every(function (r) { return !!r.id; }), true);
  pruef("alle haben Naehrwerte", COOKBOOK.every(function (r) { return r.nutrition && r.nutrition.kcal > 0; }), true);
  pruef("alle haben eine Kategorie", COOKBOOK.every(function (r) { return !!r.category; }), true);
  pruef("alle haben Zutaten", COOKBOOK.every(function (r) { return (r.ingredients || []).length > 0; }), true);
  // Jedes vegane Meal MUSS auch vegetarisch tragen - sonst findet es ein Vegetarier nicht
  // (dietOk faengt das zwar ab, aber der Filter im Meals-Reiter arbeitet auf den Tags).
  pruef("vegan impliziert vegetarisch", COOKBOOK.every(function (r) {
    var t = r.tags || [];
    return t.indexOf("vegan") === -1 || t.indexOf("vegetarisch") !== -1;
  }), true);

  // ---- Profilfilter ----
  state.goal = null;
  pruef("ohne Profil ist alles sichtbar", cookbookVisible().length, COOKBOOK.length);
  state.goal = { diet: "alles" };
  pruef("'alles' zeigt alles", cookbookVisible().length, COOKBOOK.length);
  state.goal = { diet: "vegan" };
  var v = cookbookVisible();
  pruef("vegan zeigt nur veganes", v.every(function (r) { return (r.tags || []).indexOf("vegan") !== -1; }), true);
  pruef("vegan findet ueberhaupt etwas", v.length > 0, true);
  state.goal = { diet: "vegetarisch" };
  var vg = cookbookVisible();
  pruef("vegetarisch schliesst vegane Meals ein", vg.length >= v.length, true);
  pruef("vegetarisch zeigt kein Fleisch", vg.every(function (r) {
    var t = r.tags || [];
    return t.indexOf("vegetarisch") !== -1 || t.indexOf("vegan") !== -1;
  }), true);
  state.goal = { diet: "vegan", avoid: ["glutenfrei"] };
  pruef("Form und Einschraenkung wirken zusammen", cookbookVisible().every(function (r) {
    var t = r.tags || [];
    return t.indexOf("vegan") !== -1 && t.indexOf("glutenfrei") !== -1;
  }), true);

  // ---- Uebernehmen ----
  state.goal = null; state.recipes = []; gespeichert = 0; gezeichnet = 0;
  var erste = COOKBOOK[0];
  adoptFromCookbook(erste.id);
  pruef("Meal liegt danach im Bestand", state.recipes.length, 1);
  pruef("Herkunft ist vermerkt", state.recipes[0].lib, erste.id);
  pruef("eigene id, NICHT die Katalog-id", state.recipes[0].id !== erste.id, true);
  pruef("Name uebernommen", state.recipes[0].name, erste.name);
  pruef("Zutaten uebernommen", (state.recipes[0].ingredients || []).length > 0, true);
  pruef("gespeichert und gezeichnet", gespeichert > 0 && gezeichnet > 0, true);
  pruef("Rueckgaengig angeboten", letzterToast.indexOf(erste.name) !== -1, true);

  // Das Original darf sich NICHT veraendert haben (Kopie, keine Referenz)
  pruef("Katalog-Eintrag bleibt ohne lib", "lib" in erste, false);
  state.recipes[0].name = "Umbenannt";
  pruef("Umbenennen faerbt nicht auf den Katalog ab", COOKBOOK[0].name, erste.name);

  // ---- Doppelte Uebernahme ----
  adoptFromCookbook(erste.id);
  pruef("zweite Uebernahme wird abgelehnt", state.recipes.length, 1);
  pruef("erkennt auch nach Umbenennen", isAdopted(erste.id), true);
  pruef("unbekannte id tut nichts", (adoptFromCookbook("gibtsnicht"), state.recipes.length), 1);

  // ---- Rueckgaengig ----
  window.__undo();
  pruef("Rueckgaengig entfernt die Kopie", state.recipes.length, 0);
  pruef("danach wieder uebernehmbar", isAdopted(erste.id), false);

  // ---- Abdeckung: welche Merkmale hat der Katalog ueberhaupt? ----
  // Die Chip-Reihe zeigt nur, was vorkommt. Ein Merkmal ohne einen einzigen Vertreter ist
  // deshalb nicht filterbar - das ist kein Anzeigefehler, sondern eine Inhaltsluecke.
  ["highprotein", "lowcarb", "vegetarisch", "vegan", "glutenfrei", "laktosefrei"].forEach(function (t) {
    pruef("Merkmal '" + t + "' kommt im Katalog vor",
      COOKBOOK.some(function (r) { return (r.tags || []).indexOf(t) !== -1; }), true);
  });
  ["Frühstück", "Hauptgericht", "Snack"].forEach(function (c) {
    pruef("Kategorie '" + c + "' ist besetzt",
      COOKBOOK.some(function (r) { return r.category === c; }), true);
  });
  pruef("mindestens ein Meal zum Vorkochen",
    COOKBOOK.some(function (r) { return r.mealPrep === true; }), true);

  // ---- Filter-Chips: dieselbe Reihe fuer zwei Bestaende ----
  var eigene = new Set(), katalog = new Set();
  var reihe = recipeFilterHtml(COOKBOOK, katalog, "cb-filters");
  pruef("Chip-Reihe erscheint ab sechs Eintraegen", reihe.indexOf("cb-filters") !== -1, true);
  pruef("vegan ist als Chip dabei", reihe.indexOf("Vegan") !== -1, true);
  pruef("vegetarisch ist als Chip dabei", reihe.indexOf("Vegetarisch") !== -1, true);
  pruef("Meal-Prep ist als Chip dabei", reihe.indexOf("Meal-Prep") !== -1, true);
  pruef("unter sechs Eintraegen keine Reihe",
    recipeFilterHtml(COOKBOOK.slice(0, 3), katalog, "cb-filters"), "");

  // Die beiden Zustaende duerfen sich NICHT beeinflussen
  katalog.clear(); eigene.clear();
  katalog.add("tag:vegan");
  pruef("Katalogfilter faerbt nicht auf den eigenen ab", eigene.size, 0);
  var veganeMeals = COOKBOOK.filter(function (r) { return recipeMatchesFilters(r, katalog); });
  pruef("Filter wirkt mit uebergebenem Zustand",
    veganeMeals.every(function (r) { return (r.tags || []).indexOf("vegan") !== -1; }), true);
  pruef("Filter findet etwas", veganeMeals.length > 0, true);
  katalog.add("mealPrep");
  var beide = COOKBOOK.filter(function (r) { return recipeMatchesFilters(r, katalog); });
  pruef("zwei Filter sind UND-verknuepft", beide.every(function (r) {
    return (r.tags || []).indexOf("vegan") !== -1 && r.mealPrep === true;
  }), true);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")
