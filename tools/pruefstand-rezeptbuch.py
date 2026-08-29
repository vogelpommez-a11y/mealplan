# Ausschneide-Pruefstand Rezeptbuch: Katalog, Profilfilter, Uebernahme und Bildwahl.
import io, json, os, re, sys

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

# Gegenprobe: Der Pruefstand nimmt wahlweise eine andere Datei entgegen, damit er gegen den
# Stand VOR einer Aenderung laufen kann. Ohne diesen Lauf beweist er nichts.
#   git show HEAD:index.html > alt.html && python tools/pruefstand-rezeptbuch.py alt.html
SRC = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else r"C:\Users\Paddy\Documents\Paddys Mealplan\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-cookbook.html")
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

teile = [
    block("  const COOKBOOK = [", "  ];"),
    block("  const DIETS = [", "  const AVOID_KEYS ="),
    block("  const RECIPE_TAGS = [", "  const RECIPE_TAG_KEYS ="),
    # Fuer die Bildschluessel und den Abgleich Merkmal/Badge - beides gehoert zur Kuration.
    block("  const PHOTOS = {", "  };"),
    block("  const PHOTO_RULES = [", "  const CAT_PHOTO ="),
    # Die Bildwahl selbst: LIB_IMG/libPhoto stehen unmittelbar vor photoFor.
    block("  const LIB_IMG = ", "  function libPhoto("),
    schnitt("  function photoFor("),
    schnitt("  function safeImage("),
    schnitt("  function macroBadges("),
    schnitt("  function recipeNut("),
    schnitt("  function dietOk("),
    schnitt("  function avoidOk("),
    schnitt("  function fitsDiet("),
    schnitt("  function cookbookVisible("),
    schnitt("  function isAdopted("),
    schnitt("  function adoptFromCookbook("),
    schnitt("  function copyFromCookbook("),
    block("  const STARTER_ANZAHL = ", "  };"),
    schnitt("  function addStarterMeals("),
    schnitt("  function sanitizeRecipe("),
    schnitt("  function nutNum("),
    schnitt("  function ingObj("),
    schnitt("  function recipeMatchesFilters("),
    schnitt("  function recipeFilterHtml("),
]
code = "\n\n".join(teile)

# Die Bilddateien, die TATSAECHLICH im Ordner liegen. Der Browser kann das unter file://
# nicht nachsehen, deshalb kommt die Liste hier aus dem Dateisystem in die Seite. Ohne
# diesen Abgleich prueft die Seite nur, dass ein Dateiname dasteht - nicht, dass es die
# Datei gibt. Ein Tippfehler im Namen ergibt in der App eine leere Bildflaeche.
BILD_ORDNER = os.path.join(os.path.dirname(os.path.abspath(SRC)), "img", "library")
vorhanden = sorted(f for f in os.listdir(BILD_ORDNER) if f.endswith(".webp")) \
    if os.path.isdir(BILD_ORDNER) else []
code += "\n\nvar DATEIEN = " + json.dumps(vorhanden) + ";"

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
// adoptFromCookbook() zieht eingeplante Slots auf die neue Kopie um. Hier nur mitzaehlen:
// Der Wochenplan gehoert nicht zu dem, was dieser Pruefstand pruefen soll, aber OHNE den
// Stub bricht die Seite mit "rewritePlanIds is not defined" ab - und zwar erst BEIM
// AUFRUF, also mitten im Lauf. Der Pruefstand meldete dann nur noch die Fehlerzeile.
var umgeschrieben = [];
function rewritePlanIds(alt, neu) { umgeschrieben.push([alt, neu]); }

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
  // Alle sechs Kategorien, nicht nur die drei haeufigen: Wer im Wochenplan einen Slot
  // "Dessert" oder "Beilage" fuellen will, steht sonst vor einer leeren Kategorie (C1).
  ["Frühstück", "Hauptgericht", "Snack", "Dessert", "Beilage", "Getränk"].forEach(function (c) {
    pruef("Kategorie '" + c + "' ist besetzt",
      COOKBOOK.some(function (r) { return r.category === c; }), true);
  });
  pruef("mindestens ein Meal zum Vorkochen",
    COOKBOOK.some(function (r) { return r.mealPrep === true; }), true);
  // Die 30 sind eine Zusage aus PRODUCT.md ("von 30 auf ueber 100 mit Pro") und stehen
  // so auch im Onboarding-Text. Faellt der Katalog darunter, ist der Text falsch.
  pruef("Katalog hat mindestens 30 Rezepte", COOKBOOK.length >= 30, true);

  // ---- Bildschluessel ----
  // photoFor() faellt bei einem unbekannten Schluessel still auf die Stichwortregeln
  // zurueck - genau die, die im Katalog danebengreifen. Ein Tippfehler waere deshalb
  // unsichtbar, aber wirksam.
  pruef("jeder gesetzte Bildschluessel steckt in PHOTOS",
    COOKBOOK.filter(function (r) { return r.photo && !PHOTOS[r.photo]; }).map(function (r) { return r.id; }), []);

  // Der Schluessel muss die Uebernahme UEBERLEBEN: sonst sieht die Kopie im eigenen
  // Bestand anders aus als das Original im Katalog, obwohl der Nutzer nichts geaendert hat.
  var mitBild = COOKBOOK.filter(function (r) { return !!r.photo; })[0];
  var kopie = sanitizeRecipe(Object.assign({}, mitBild, { id: "x1", lib: mitBild.id }));
  pruef("uebernommene Kopie behaelt den Bildschluessel", kopie.photo, mitBild.photo);
  // Und er muss eine FORM haben: Er kommt bei geteilten Meals von aussen herein.
  pruef("Freitext im Bildschluessel wird verworfen",
    "photo" in sanitizeRecipe({ id: "x2", name: "A", photo: "../../etc/passwd" }), false);
  pruef("Nicht-String im Bildschluessel wird verworfen",
    "photo" in sanitizeRecipe({ id: "x3", name: "A", photo: { toString: function () { return "salad"; } } }), false);

  // ---- Die eigenen Bilder der Bibliothek ----
  pruef("jedes Katalog-Rezept hat ein Bild",
    COOKBOOK.filter(function (r) { return !r.img; }).map(function (r) { return r.id; }), []);
  // Der Abgleich mit dem Dateisystem - der Kern dieser Gruppe. Ein Dateiname, den es nicht
  // gibt, ist in der App eine leere Flaeche und faellt beim Lesen des Codes nicht auf.
  pruef("jeder Dateiname existiert wirklich",
    COOKBOOK.filter(function (r) { return r.img && DATEIEN.indexOf(r.img) === -1; })
            .map(function (r) { return r.img; }), []);
  pruef("kein Bild trägt einen Umlaut im Dateinamen",
    COOKBOOK.filter(function (r) { return r.img && !/^[a-z0-9-]+\\.webp$/.test(r.img); })
            .map(function (r) { return r.img; }), []);

  var mitBild2 = COOKBOOK.filter(function (r) { return !!r.img; })[0];
  pruef("photoFor nimmt das Bibliotheksbild",
    photoFor(mitBild2), "img/library/" + mitBild2.img);
  // Die uebernommene Kopie hat eine EIGENE id und kennt das Original nur ueber `lib` -
  // ohne diese Aufloesung zeigte sie ein anderes Bild als die Karte, aus der sie entstand.
  pruef("die Kopie zeigt dasselbe Bild wie das Original",
    photoFor({ id: "irgendeine-uid", lib: mitBild2.id, name: mitBild2.name, category: mitBild2.category }),
    "img/library/" + mitBild2.img);
  // Reihenfolge: Das eigene Foto des Nutzers muss gewinnen.
  var eigenes = "data:image/png;base64,AAAA=";
  pruef("eigenes Foto schlägt das Bibliotheksbild",
    photoFor(Object.assign({}, mitBild2, { image: eigenes })), eigenes);
  // Ein ausgemustertes Bild faellt sauber auf die naechste Stufe zurueck, statt einen 404
  // zu erzeugen. Der Fall entsteht dadurch, dass `img` am KATALOGEINTRAG fehlt - die id
  // steht dann nicht in LIB_IMG. Am uebergebenen Objekt zu loeschen genuegt nicht: Die Map
  // ist die Quelle, nicht das Feld (erster Anlauf dieser Pruefung lag genau daran falsch).
  pruef("ausgemustertes Bild faellt auf den kuratierten Schlüssel zurück",
    photoFor({ id: "nicht-im-katalog", name: "Irgendwas", category: "Snack", photo: "cake" }),
    PHOTOS.cake);
  pruef("ein fremdes Meal bekommt kein Bibliotheksbild",
    photoFor({ id: "eigenes-meal", name: "Nudeln mit Sauce", category: "Hauptgericht" })
      .indexOf("img/library") === -1, true);

  // ---- Startmeals nach dem Onboarding ----
  // Der erste Bestand entsteht seit dem 15.08.2026 NACH dem Onboarding und aus dem Katalog -
  // vorher setzte load() vier feste Meals, bevor die Ernaehrungsform bekannt war.
  pruef("alle drei Formen sind besetzt",
    Object.keys(STARTER).sort(), ["alles", "vegan", "vegetarisch"]);
  pruef("jede Starter-id existiert im Katalog",
    Object.keys(STARTER).reduce(function (fehlt, form) {
      return fehlt.concat(STARTER[form].filter(function (id) {
        return !COOKBOOK.some(function (r) { return r.id === id; });
      }));
    }, []), []);

  // Die LISTE selbst muss zur Form passen, nicht nur das Ergebnis: fitsDiet() wirft ein
  // unpassendes Gericht heraus und addStarterMeals() fuellt still auf - eine falsche
  // Kuration bliebe damit unsichtbar. Aufgefallen in der Gegenprobe, als ein Chili in der
  // veganen Liste alle Pruefungen gruen liess.
  pruef("jede Liste passt zu ihrer Ernaehrungsform",
    Object.keys(STARTER).reduce(function (fehlt, form) {
      return fehlt.concat(STARTER[form].filter(function (id) {
        var r = COOKBOOK.filter(function (x) { return x.id === id; })[0];
        return r && !dietOk(r, form);
      }).map(function (id) { return form + ":" + id; }));
    }, []), []);

  ["alles", "vegetarisch", "vegan"].forEach(function (form) {
    state.recipes = []; state.goal = { diet: form };
    addStarterMeals();
    pruef(form + ": genau " + STARTER_ANZAHL + " Meals", state.recipes.length, STARTER_ANZAHL);
    pruef(form + ": jedes traegt lib",
      state.recipes.every(function (r) { return !!r.lib; }), true);
    // Die harte Zusage: Ein Veganer bekommt NIE ein Gericht ohne den Tag - genau das ging
    // vorher schief, weil die Auswahl vor dem Onboarding stand.
    pruef(form + ": jedes passt zum Profil",
      state.recipes.every(function (r) {
        var k = COOKBOOK.filter(function (x) { return x.id === r.lib; })[0];
        return k && fitsDiet(k);
      }), true);
    // Sonst waeren es fuenf Hauptgerichte und der Fruehstuecks-Slot bliebe leer.
    var kat = state.recipes.map(function (r) { return r.category; });
    ["Frühstück", "Hauptgericht", "Snack"].forEach(function (c) {
      pruef(form + ": " + c + " ist dabei", kat.indexOf(c) !== -1, true);
    });
    pruef(form + ": kein Pfad in den Nutzerdaten",
      state.recipes.some(function (r) { return "img" in r; }), false);
    // Und das Bild wird trotzdem gefunden - ueber lib.
    pruef(form + ": jedes findet sein Bild",
      state.recipes.every(function (r) { return photoFor(r).indexOf("img/library/") === 0; }), true);
  });

  // Einschraenkung quer zur Form: Die Liste wird gefiltert UND wieder aufgefuellt.
  state.recipes = []; state.goal = { diet: "vegan", avoid: ["glutenfrei"] };
  addStarterMeals();
  pruef("glutenfreier Veganer bekommt trotzdem fuenf", state.recipes.length, STARTER_ANZAHL);
  pruef("und alle fuenf sind glutenfrei", state.recipes.every(function (r) {
    return (r.tags || []).indexOf("glutenfrei") !== -1;
  }), true);
  pruef("aufgefuellt wird nicht nur mit Hauptgerichten",
    new Set(state.recipes.map(function (r) { return r.category; })).size >= 3, true);

  // NUR in einen leeren Bestand - sonst bekaeme ein Zweitgeraet fuenf Dubletten.
  state.recipes = [{ id: "x", name: "Mein Meal" }]; state.goal = { diet: "vegan" };
  addStarterMeals();
  pruef("bei vorhandenem Bestand kommt nichts dazu", state.recipes.length, 1);

  // Auch die Katalog-Kopie ueber den Uebernehmen-Knopf traegt keinen Pfad.
  state.recipes = []; state.goal = null;
  var katKopie = sanitizeRecipe(Object.assign({}, mitBild2, { id: uid(), lib: mitBild2.id }));
  pruef("Katalog-Kopie traegt keinen Pfad", "img" in katKopie, false);
  pruef("findet ihr Bild aber über lib", photoFor(katKopie), "img/library/" + mitBild2.img);

  // ---- Merkmal und Badge muessen dasselbe sagen ----
  // Der Filter "High Protein" und das Badge "Proteinreich" auf derselben Karte kommen aus
  // zwei Quellen: der Tag ist gepflegt, das Badge gerechnet (macroBadges). Weichen sie ab,
  // widerspricht die Karte ihrem eigenen Filter. Im KATALOG ist das ein Kurationsfehler -
  // bei selbst angelegten Meals darf der Nutzer taggen, wie er will.
  pruef("kein Katalog-Meal widerspricht seinem Badge",
    COOKBOOK.filter(function (r) {
      var b = macroBadges(r).map(function (x) { return x.label; });
      var t = r.tags || [];
      return (b.indexOf("Proteinreich") !== -1) !== (t.indexOf("highprotein") !== -1)
          || (b.indexOf("Low Carb") !== -1) !== (t.indexOf("lowcarb") !== -1);
    }).map(function (r) { return r.id; }), []);

  // ---- Filter-Chips: dieselbe Reihe fuer zwei Bestaende ----
  var eigene = new Set(), katalog = new Set();
  var reihe = recipeFilterHtml(COOKBOOK, katalog, "cb-filters");
  pruef("Chip-Reihe erscheint ueber dem Katalog", reihe.indexOf("cb-filters") !== -1, true);
  pruef("vegan ist als Chip dabei", reihe.indexOf("Vegan") !== -1, true);
  pruef("vegetarisch ist als Chip dabei", reihe.indexOf("Vegetarisch") !== -1, true);
  pruef("Meal-Prep ist als Chip dabei", reihe.indexOf("Meal-Prep") !== -1, true);
  pruef("unter vier Eintraegen keine Reihe",
    recipeFilterHtml(COOKBOOK.slice(0, 3), katalog, "cb-filters"), "");

  // ---- Die Startmeals sehen ihre Filter (Punkt 3 der Alltagsbefunde, 24.08.2026) ----
  // Die Schwelle stand auf "< 6", addStarterMeals() legt STARTER_ANZAHL = 5 an. Jeder neue
  // Nutzer sah seine Startmeals also ohne eine einzige Filterzeile. Das ist kein Grenzfall,
  // das ist der Regelfall - deshalb ist die Zahl hier ausdruecklich mitgeprueft.
  pruef("die App legt weiterhin genau 5 Startmeals an", STARTER_ANZAHL, 5);
  ["alles", "vegetarisch", "vegan"].forEach(function (diet) {
    state.goal = { diet: diet };
    state.recipes = [];
    addStarterMeals();
    var liste = libraryRecipes();
    pruef("Startmeals fuer " + diet + ": " + liste.length + " Stueck", liste.length, 5);
    var s2 = new Set();
    var r2 = recipeFilterHtml(liste, s2, "r-filters");
    pruef("Startmeals fuer " + diet + " zeigen eine Filterreihe", r2.indexOf("r-filters") !== -1, true);
    // Und keinen Chip, der auf ALLE fuenf zutrifft - der naehme nichts weg. Genau das waere
    // bei "vegan" passiert: "Vegan" und "Vegetarisch" treffen dort auf jedes der fuenf Meals.
    var wirkungslos = [];
    RECIPE_TAGS.forEach(function (t) {
      var n = liste.filter(function (r) { return (r.tags || []).indexOf(t.key) !== -1; }).length;
      if (n === liste.length && r2.indexOf('data-f="tag:' + t.key + '"') !== -1) wirkungslos.push(t.key);
    });
    pruef("kein wirkungsloser Chip bei " + diet, wirkungslos, []);
    // Gegenprobe zur Gegenprobe: Es muss ueberhaupt Chips geben, sonst ist "keiner
    // wirkungslos" trivial wahr.
    pruef("und es gibt ueberhaupt Chips bei " + diet, (r2.match(/data-f=/g) || []).length > 0, true);
  });
  state.goal = null; state.recipes = [];

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

  // ---- Der Aufrufweg selbst ----
  // Ein Fund des Nutzers am 15.08.2026: In "Meine Meals" stand
  // `pool.filter(recipeMatchesFilters)`. Array.filter uebergibt als zweites Argument den
  // INDEX - der landete im Parameter `aktive`. Bei Index 0 (falsy) griff der Rueckfall noch,
  // ab Index 1 warf `for (const k of 1)`, paintRecipeGroups() brach ab und liess die
  // UNGEFILTERTE Liste stehen. Der Filter sah damit aus wie "zeigt immer alles".
  // Die Pruefung sichert die Haertung: `aktive` wird nur als Set akzeptiert.
  recipeFilters.clear(); recipeFilters.add("tag:highprotein");
  var probe = [{ tags: ["highprotein"] }, { tags: [] }, { tags: ["highprotein"] }];
  var direkt;
  try { direkt = probe.filter(recipeMatchesFilters).length; }
  catch (e) { direkt = e.constructor.name + ": " + e.message; }
  pruef("direkt als filter-Callback wirft nicht und filtert richtig", direkt, 2);
  pruef("mit uebergebenem Set ebenso",
    probe.filter(function (r) { return recipeMatchesFilters(r, recipeFilters); }).length, 2);
  // Und der Rueckfall auf den globalen Zustand bleibt erhalten (ohne zweites Argument).
  pruef("ohne zweites Argument gilt der globale Zustand",
    probe.filter(function (r) { return recipeMatchesFilters(r); }).length, 2);
  recipeFilters.clear();

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")


# --- Selbst fahren statt nur schreiben (28.08.2026) -------------------------------------
# Bis dahin endete dieses Skript nach dem Schreiben der HTML-Datei mit Rueckgabewert 0.
# tools/alle-pruefstaende.py bewertet nur den Rueckgabewert und meldete es deshalb bei jedem
# Durchgang gruen, ohne dass je eine Zusage lief. Acht Pruefstaende waren betroffen - ein
# Drittel der Suite (docs/TROUBLESHOOTING.md 131).
#
# Die Zusagen oben sind UNVERAENDERT. Der gemeinsame Laeufer haengt der erzeugten Seite nur
# einen Beobachter an und liest ihr Protokoll aus; im Browser geoeffnet verhaelt sie sich
# genau wie vorher.
if __name__ == "__main__":
    import sys as _sys
    _sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from pruefstand_lauf import fahren
    _sys.exit(fahren(OUT))
