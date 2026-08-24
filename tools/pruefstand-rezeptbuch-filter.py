# -*- coding: utf-8 -*-
# Ausschneide-Pruefstand: Das Ernaehrungsprofil als vorbelegter, abschaltbarer Chip.
#
# Geprueft wird, was vorher eine unsichtbare Wand war: dass der volle Katalog erreichbar ist,
# dass die Vorbelegung dieselbe Menge trifft wie der alte harte Vorfilter cookbookVisible(),
# und dass sie bei JEDEM Profilwechsel neu greift - auch bei einem, der aus der Cloud kommt.
#
# GEGENPROBE ist Teil des Tests: Ein von Hand abgewaehlter Chip darf ohne Profilwechsel NICHT
# zurueckkommen. Ohne diese Zeile wuerde ein "seedet immer" ebenfalls gruen durchlaufen.
import io, os

SRC = r"C:\Users\Paddy\Documents\Paddys Mealplan\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-cb-filter.html")
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
    block("  const CATEGORIES = ", "  const CAT_CLASS = "),
    block("  const COOKBOOK = [", "  ];"),
    block("  const RECIPE_TAGS = [", "  const RECIPE_TAG_KEYS ="),
    block("  const DIETS = [", "  const AVOID_KEYS ="),
    schnitt("  function dietOk("),
    schnitt("  function avoidOk("),
    schnitt("  function fitsDiet("),
    schnitt("  function cookbookVisible("),
    schnitt("  function esc("),
    "  const cookbookFilters = new Set();",
    schnitt("  let cookbookSeedSig = null;"),
    schnitt("  function recipeMatchesFilters("),
    schnitt("  function recipeFilterHtml("),
]
code = "\n\n".join(teile)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Rezeptbuch-Filter</title>
<pre id="log"></pre>
<script>
// Eigener Block VOR dem Pruefcode - im selben Block gesetzt faenge window.onerror einen
// Parse-Fehler dieses Blocks nicht, und die Seite bliebe stumm.
window.onerror = function (m, s, z) {
  document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
  return true;
};
</script>
<script>
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
var state = { goal: null, recipes: [] };
// recipeFilterHtml() faellt ohne Liste auf den eigenen Bestand zurueck - hier nie gebraucht,
// der Katalog wird immer ausdruecklich uebergeben. Der Stub belegt nur den Namen.
function libraryRecipes() { return []; }
var recipeFilters = new Set();
// Die Ansichts-Menge, wie paintCookbook() sie bildet: voller Katalog, dann die Chips.
function sichtbar() {
  seedCookbookFilters();
  if (!cookbookFilters.size) return COOKBOOK.slice();
  return COOKBOOK.filter(function (r) { return recipeMatchesFilters(r, cookbookFilters); });
}
function chips() {
  var s = [];
  cookbookFilters.forEach(function (k) { s.push(k); });
  return s.sort().join(" ");
}

__CODE__

LOG.push("--- Der Katalog ist vollstaendig erreichbar ---");
state.goal = { diet: "vegan" };
var mitProfil = sichtbar();
state.goal = { diet: "alles" };
var ohneProfil = sichtbar();
pruef("ohne Profil zeigt die Ansicht ALLE " + COOKBOOK.length + " Rezepte",
      ohneProfil.length === COOKBOOK.length, ohneProfil.length + " von " + COOKBOOK.length);
pruef("mit vegan zeigt sie weniger", mitProfil.length < COOKBOOK.length,
      mitProfil.length + " von " + COOKBOOK.length);
pruef("Gegenprobe: es ist ueberhaupt eine Einschraenkung (nicht 0, nicht alles)",
      mitProfil.length > 0 && mitProfil.length < COOKBOOK.length, "" + mitProfil.length);

LOG.push("");
LOG.push("--- Der Chip trifft dieselbe Menge wie der alte harte Vorfilter ---");
// Das ist der Kern: Wer nichts anfasst, sieht genau das, was er vorher sah - nur jetzt
// sichtbar begruendet und abschaltbar.
var profile = [
  ["vegetarisch",               { diet: "vegetarisch" }],
  ["vegan",                     { diet: "vegan" }],
  ["alles + glutenfrei",        { diet: "alles", avoid: ["glutenfrei"] }],
  ["vegetarisch + laktosefrei", { diet: "vegetarisch", avoid: ["laktosefrei"] }],
  ["vegan + beide",             { diet: "vegan", avoid: ["glutenfrei", "laktosefrei"] }],
  ["alles",                     { diet: "alles" }]
];
profile.forEach(function (p) {
  state.goal = p[1];
  var neu = sichtbar().map(function (r) { return r.id; }).sort().join(",");
  var alt = cookbookVisible().map(function (r) { return r.id; }).sort().join(",");
  pruef("deckungsgleich mit cookbookVisible(): " + p[0], neu === alt,
        "Chip " + sichtbar().length + " vs. Vorfilter " + cookbookVisible().length);
});

LOG.push("");
LOG.push("--- Jeder vorbelegte Chip existiert auch als Chip-Knopf ---");
// recipeFilterHtml() loescht aktive Filter, deren Chip es nicht gibt (Kommentar dort). Ein
// vorbelegter Schluessel, der im Katalog nicht vorkommt, wuerde also still verschwinden -
// die Ansicht zeigte dann mehr, als das Profil erlaubt, ohne dass es jemand sieht.
profile.forEach(function (p) {
  state.goal = p[1];
  seedCookbookFilters();
  var vorher = chips();
  var html = recipeFilterHtml(COOKBOOK, cookbookFilters, "cb-filters");
  pruef("Chips ueberleben recipeFilterHtml(): " + p[0], chips() === vorher,
        "vorher [" + vorher + "] nachher [" + chips() + "]");
  var fehlt = [];
  vorher.split(" ").filter(Boolean).forEach(function (k) {
    if (html.indexOf('data-f="' + k + '"') === -1) fehlt.push(k);
  });
  pruef("jeder Chip steht im Markup: " + p[0], fehlt.length === 0, fehlt.join(","));
});

LOG.push("");
LOG.push("--- Die Vorbelegung folgt jedem Profilwechsel ---");
state.goal = { diet: "vegetarisch" };
seedCookbookFilters();
pruef("vegetarisch -> Chip gesetzt", chips() === "tag:vegetarisch", chips());
state.goal = { diet: "alles" };
seedCookbookFilters();
pruef("-> alles: Chip weg", chips() === "", chips());
state.goal = { diet: "vegan", avoid: ["glutenfrei"] };
seedCookbookFilters();
pruef("-> vegan + glutenfrei", chips() === "tag:glutenfrei tag:vegan", chips());
// Der Weg, der den Fehler ausgeloest hat: ein Snapshot aus der Cloud setzt state.goal neu.
state.goal = { diet: "vegetarisch" };
seedCookbookFilters();
pruef("Cloud-Snapshot wirkt genauso", chips() === "tag:vegetarisch", chips());

LOG.push("");
LOG.push("--- Reihenfolge in avoid aendert die Signatur nicht ---");
state.goal = { diet: "alles", avoid: ["glutenfrei", "laktosefrei"] };
seedCookbookFilters();
var sigA = cookbookSeedSig, chipsA = chips();
cookbookFilters.delete("tag:glutenfrei");          // Nutzer waehlt einen ab
state.goal = { diet: "alles", avoid: ["laktosefrei", "glutenfrei"] };
seedCookbookFilters();
pruef("umsortiertes avoid loest KEINE Neuvorbelegung aus", cookbookSeedSig === sigA);
pruef("und die Abwahl bleibt bestehen", chips() !== chipsA, chips());

LOG.push("");
LOG.push("--- Gegenprobe: eine Abwahl haelt, bis das Profil sich aendert ---");
state.goal = { diet: "vegetarisch" };
cookbookSeedSig = null;                             // frische Sitzung
seedCookbookFilters();
pruef("Vorbedingung: Chip ist da", chips() === "tag:vegetarisch", chips());
cookbookFilters.delete("tag:vegetarisch");
seedCookbookFilters();                              // gleiches Profil, erneuter Aufbau
pruef("abgewaehlter Chip kommt NICHT zurueck", chips() === "", chips());
pruef("und die Ansicht zeigt jetzt den vollen Katalog", sichtbar().length === COOKBOOK.length,
      sichtbar().length + " von " + COOKBOOK.length);
state.goal = { diet: "vegan" };
seedCookbookFilters();                              // Profilwechsel -> wieder vorbelegen
pruef("nach dem Profilwechsel wird wieder vorbelegt", chips() === "tag:vegan", chips());

LOG.push("");
LOG.push("--- Ohne Ziel (vor dem Onboarding) ---");
state.goal = null;
cookbookSeedSig = null;
seedCookbookFilters();
pruef("kein Ziel -> kein Chip", chips() === "", chips());
pruef("kein Ziel -> voller Katalog", sichtbar().length === COOKBOOK.length);

LOG.push("");
LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("Alle " + ok + " Pruefungen gruen."));
document.getElementById("log").textContent = LOG.join("\\n");
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben: " + OUT)
