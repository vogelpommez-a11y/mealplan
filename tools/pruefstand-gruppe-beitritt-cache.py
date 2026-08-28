# -*- coding: utf-8 -*-
u"""
Gruppenbeitritt: der Dubletten-Abgleich darf nicht am Offline-Cache scheitern.

`copyOwnRecipesToGroup()` entscheidet anhand eines LEEREN Leseergebnisses, ob ein eigenes
Meal hochgeladen wird: "die Gruppe kennt diese `lib` noch nicht, also lade ich meine Kopie
hoch". Genau das macht das leere Ergebnis gefaehrlich.

Mit `persistentLocalCache` WIRFT `getDocs` offline nicht, sondern liefert stillschweigend das
leere Cache-Ergebnis - und die Rezepte einer Gruppe, der man gerade erst beigetreten ist, hat
dieser Cache noch NIE gesehen. "Die Gruppe hat noch keine Meals" und "ich weiss es nicht"
sehen damit gleich aus. Der Abgleich faellt lautlos aus und JEDES eigene Meal geht hoch - bei
fest verdrahteten Startmeals (STARTER) garantiert fuenf Paare, also exakt der Zustand, den
docs/TROUBLESHOOTING.md 102 beseitigt hat.

Die Behebung: `CloudSync.loadRecipesFromServer()` (getDocsFromServer). Die WIRFT offline - und
das ist hier die gewuenschte Eigenschaft, weil der Aufrufer den Unterschied dann sehen kann.

Messgroesse:

    nach dem Beitritt traegt jede `lib` in der Gruppe genau EINEN Eintrag -
    auch dann, wenn der Cache ein leeres Ergebnis vorspiegelt

Gegenprobe: derselbe Ablauf ueber den Cache-Weg (loadRecipes) muss ROT werden.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-gruppe-beitritt-cache.py [pfad-zu-index.html]
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
var state = { recipes: [], plans: {} };
var umgeschrieben = [];
function noteError(){}
function rewritePlanIds(alt, neu){ umgeschrieben.push(alt + "->" + neu); }

// --- Falsches Firestore mit einem Cache, der genau so luegt wie in echt ---------------
// gesehen: welche Sammlungen der Cache schon einmal vom Server geladen hat. Was nicht
// darin steht, liefert der Cache-Weg als LEERES Array zurueck - ohne zu werfen.
var cloud = {}, gesehen = {}, serverWeg = true, serverOffline = false;
window.CloudSync = {
  loadRecipes: function (base) {              // Cache-Weg: wirft nie
    var k = base.join("/");
    if (!gesehen[k]) return Promise.resolve([]);
    return Promise.resolve(Object.keys(cloud[k] || {}).map(function (id) {
      return JSON.parse(JSON.stringify(cloud[k][id]));
    }));
  },
  loadRecipesFromServer: function (base) {    // Server-Weg: wirft offline
    if (serverOffline) return Promise.reject(new Error("unavailable"));
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

var LIBS = ["quark-haferflocken-banane", "haehnchen-bowl-brokkoli", "chili-rinderhack-bohnen",
            "ofenlachs-suesskartoffel", "skyr-beeren-nuesse"];
function meal(id, lib, name) { return { id: id, lib: lib || undefined, name: name || lib }; }

// Ausgangslage: Der Owner hat seine fuenf Startmeals bereits in der Gruppe (prepareGroup).
// Ich trete bei und habe dieselben fuenf - eigene ids, gleiche libs - plus ein eigenes Meal.
function frischerStand(cacheKenntGruppe) {
  cloud = { "groups/g1": {} };
  gesehen = {};
  umgeschrieben = [];
  LIBS.forEach(function (l, i) { cloud["groups/g1"]["owner" + i] = meal("owner" + i, l); });
  cloud["groups/g1"]["ownerEigen"] = meal("ownerEigen", null, "Bowl von Luisa");
  if (cacheKenntGruppe) gesehen["groups/g1"] = true;
  state.recipes = LIBS.map(function (l, i) { return meal("mein" + i, l); });
  state.recipes.push(meal("meinEigen", null, "Steak mit Kartoffeln"));
}

function libZaehlung() {
  var z = {}, c = cloud["groups/g1"];
  Object.keys(c).forEach(function (id) { var l = c[id].lib; if (l) z[l] = (z[l] || 0) + 1; });
  return z;
}
function maxLib() {
  var z = libZaehlung(), m = 0;
  Object.keys(z).forEach(function (k) { if (z[k] > m) m = z[k]; });
  return m;
}
function anzahl() { return Object.keys(cloud["groups/g1"]).length; }

// Die alte Fassung: identisch, nur ueber den Cache-Weg. Fuer die Gegenprobe.
async function copyOwnRecipesToGroupAlt(gid) {
  const mine = state.recipes.filter(r => r && r.id);
  if (!mine.length) return;
  let vorhanden = [];
  try { vorhanden = await window.CloudSync.loadRecipes(["groups", gid]) || []; } catch (e) {}
  const libZuId = new Map();
  vorhanden.forEach(r => { if (r && r.lib && !libZuId.has(r.lib)) libZuId.set(r.lib, r.id); });
  const hochladen = [];
  mine.forEach(r => {
    const treffer = r.lib ? libZuId.get(r.lib) : null;
    if (treffer && treffer !== r.id) rewritePlanIds(r.id, treffer);
    else hochladen.push(r);
  });
  if (!hochladen.length) return;
  for (let i = 0; i < hochladen.length; i += 20) {
    await window.CloudSync.saveRecipesBatch(["groups", gid], hochladen.slice(i, i + 20), []);
  }
}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Warmer Cache: der Abgleich hat schon immer funktioniert ---");
frischerStand(true);
await copyOwnRecipesToGroup("g1");
pr("jede lib genau einmal", maxLib() === 1, JSON.stringify(libZaehlung()));
pr("nur das eigene Meal kam hinzu", anzahl() === 7, anzahl() + " statt 7");
pr("meine fuenf Kopien wurden auf die Gruppen-ids umgebogen", umgeschrieben.length === 5,
   umgeschrieben.length + "");

console.log("--- 2. KALTER Cache - der reale Fall beim Beitritt ---");
// Der Cache hat groups/g1/recipes noch nie gesehen. Genau hier fiel der Abgleich lautlos aus.
frischerStand(false);
await copyOwnRecipesToGroup("g1");
pr("trotzdem jede lib genau einmal", maxLib() === 1, JSON.stringify(libZaehlung()));
pr("trotzdem nur 7 Meals", anzahl() === 7, anzahl() + " statt 7");
pr("die Umschreibung lief trotzdem", umgeschrieben.length === 5, umgeschrieben.length + "");

console.log("--- 3. Wirklich offline: Beitritt geht vor, Dubletten sind hinnehmbar ---");
// Kuer, nicht Pflicht (docs/TROUBLESHOOTING.md 102): der Server ist nicht erreichbar, der
// Abgleich faellt aus - aber der Beitritt darf daran NICHT scheitern.
frischerStand(false);
serverOffline = true;
var geworfen = false;
try { await copyOwnRecipesToGroup("g1"); } catch (e) { geworfen = true; }
serverOffline = false;
pr("der Beitritt wirft nicht", !geworfen);
pr("die eigenen Meals sind trotzdem in der Gruppe", anzahl() === 12, anzahl() + "");
pr("und ja - dann gibt es Dubletten (bewusst)", maxLib() === 2, "maxLib=" + maxLib());

console.log("--- 4. Meals ohne lib werden nie zusammengelegt ---");
// "Banane" darf es zweimal geben - zwei Personen, zwei verschiedene Meals.
frischerStand(true);
state.recipes = [meal("meinBanane", null, "Banane")];
await copyOwnRecipesToGroup("g1");
pr("Meal ohne lib wird hochgeladen", !!cloud["groups/g1"]["meinBanane"]);
pr("nichts wurde umgebogen", umgeschrieben.length === 0);

console.log("--- 5. Leerer eigener Bestand: nichts zu tun, kein Absturz ---");
frischerStand(true);
state.recipes = [];
await copyOwnRecipesToGroup("g1");
pr("Gruppe unveraendert", anzahl() === 6, anzahl() + "");

console.log("--- 6. Die eigene id ist schon die Gruppen-id (Rueckkehr) ---");
// treffer === r.id: nicht umbiegen, sondern hochladen (= ueberschreiben, keine Dublette).
frischerStand(true);
state.recipes = [meal("owner0", LIBS[0])];
await copyOwnRecipesToGroup("g1");
pr("keine Selbst-Umschreibung", umgeschrieben.length === 0, JSON.stringify(umgeschrieben));
pr("keine Dublette", maxLib() === 1);

console.log("--- 7. GEGENPROBE: der Cache-Weg muss beim kalten Cache durchfallen ---");
frischerStand(false);
await copyOwnRecipesToGroupAlt("g1");
pr("alte Fassung erzeugt Paare", maxLib() === 2, "maxLib=" + maxLib() + " " + JSON.stringify(libZaehlung()));
pr("alte Fassung: 12 statt 7 Meals", anzahl() === 12, anzahl() + "");
pr("alte Fassung hat NICHTS umgebogen", umgeschrieben.length === 0, umgeschrieben.length + "");

console.log("--- 8. Gegenprobe zur Gegenprobe: mit warmem Cache war die alte Fassung heil ---");
// Sonst misst Abschnitt 7 nur "die alte Fassung ist irgendwie kaputt" statt der Cache-Ursache.
frischerStand(true);
await copyOwnRecipesToGroupAlt("g1");
pr("alte Fassung bei warmem Cache in Ordnung", maxLib() === 1 && anzahl() === 7,
   "maxLib=" + maxLib() + " anzahl=" + anzahl());

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")
    copy = schneide(quelle, u"async function copyOwnRecipesToGroup(gid)",
                    u'await window.CloudSync.saveRecipesBatch(["groups", gid], hochladen.slice(i, i + 20), []);',
                    u"\n    }\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-grpjoin-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + UMFELD + u"\n" + copy + u"\n" + TEST + u"\n</script>")
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
