# -*- coding: utf-8 -*-
u"""
Wurzel-Haertung der Rezept-IDs: eine fremdbestimmte Dokument-ID kommt nicht in den Bestand.

WORUM ES GEHT
-------------
In einer Gruppe ist die Firestore-Dokument-ID zugleich die Meal-id im Datenmodell - und
sie wird von einem ANDEREN Mitglied gewaehlt. `sanitizeRecipe()` prueft image, category,
ingredients, tags und photo, die `id` aber nicht; `firestore.rules` schraenkte `recipeId`
ebenfalls nicht ein. Die Ausgabestellen escapen zwar (esc(r.id), CSS.escape) - das Loch
war also an der Oberflaeche zu, aber nicht an der Wurzel.

Seit dem 06.09.2026 lehnt `onRecipesRemote()` in der Gruppe ein Dokument ab, dessen ID
nicht die Form von uid() traegt (validRecipeId).

WAS GEMESSEN WIRD - und warum genau das
---------------------------------------
Die Aufgabe war ausdruecklich nicht "haelt der Filter", sondern die Frage, was mit einem
Meal geschieht, dessen ID verworfen wird. Vier Messgroessen, und drei davon schuetzen
gegen den Schaden, den die Haertung selbst anrichten koennte:

  1  ABWEHR    In der Gruppe kommt eine Kunst-ID nicht in state.recipes.
  2  DURCHLASS In der Gruppe kommt eine echte uid() weiterhin an (kein Overblocking).
  3  EIGENE    OHNE Gruppe kommt auch eine abweichende ID an. Dort schreibt nur das
               eigene Geraet - ein Fehlurteil waere Datenverlust an eigenen Altdaten.
  4  RUHE      Das abgelehnte Dokument geraet in KEINE Schreib-Loesch-Schleife:
               syncRecipes() darf es weder loeschen noch neu schreiben.
  5  PLAN      Der Planverweis auf die abgelehnte ID faellt mit weg (normalizePlan).

GEGENPROBE
----------
Am Ende laeuft derselbe Test noch einmal gegen den ALTEN Stand - die Zeile mit
validRecipeId wird aus dem geschnittenen Code entfernt. Messgroesse 1 MUSS dann rot
werden, sonst misst der Pruefstand nichts (docs/TESTING.md, CLAUDE.md Abschnitt 11).

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-rezept-id-format.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, ab=0):
    u"""Von der Zeile mit `start` bis einschliesslich der naechsten mit `ende`."""
    a = next((i for i, l in enumerate(zeilen) if i >= ab and start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1])


def block(zeilen, start):
    u"""Eine ganze Funktion: von der Startzeile bis zu der Zeile, die GENAU aus deren
    Einrueckung plus "}" besteht. Ein blosses "enthaelt }" schnitte mitten hinein -
    `    }));` in normalizePlan() traefe es sonst als Erstes."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    schluss = zeilen[a][:len(zeilen[a]) - len(zeilen[a].lstrip())] + u"}"
    b = next((i for i, l in enumerate(zeilen) if i > a and l.rstrip() == schluss), None)
    if b is None:
        raise SystemExit(u"Funktionsende nicht gefunden: " + start)
    return u"\n".join(zeilen[a:b + 1])


def eine_zeile(zeilen, start):
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    return zeilen[a]


# --- Umfeld, das der ausgeschnittene Code vorfindet ---------------------------------------
# Bewusst schmal: gestubbt wird nur, was NICHT gemessen wird. Die Entscheidung selbst
# (validRecipeId, onRecipesRemote, syncRecipes, normalizePlan) ist echter Code.
UMFELD = u"""
var syncUid = "ich", syncGid = null, lastPushedRecipes = null, recipesSyncFailed = false;
var openSheetId = null, openSheetRemovedCb = null;
var state = { recipes: [], plans: {}, deleted: {} };
var CLOUD_DOC_MAX = 900000;
var COOKBOOK = [];
function noteError(){}
function toast(){}
function save(){}
function render(){}
function dropRecipeIds(){}
function isDeleted(id){ return !!state.deleted[id]; }
// sanitizeRecipe absichtlich durchreichend: Dieser Pruefstand misst die ID-Pruefung,
// nicht die Feldreinigung - und er belegt damit zugleich, dass der Schutz NICHT an
// sanitizeRecipe haengt.
function sanitizeRecipe(r){ return r; }
function sanitizeRecipes(l){ return (l||[]).filter(function(r){ return r && r.id; }); }
function recipeBase(){ return syncGid ? ["groups", syncGid] : ["users", syncUid]; }

// --- Falsches Firestore: nur so viel, wie syncRecipes() anfassen kann ---------------------
var geschrieben = [], geloescht = [];
window.CloudSync = {
  saveRecipesBatch: function (base, puts, delIds) {
    puts.forEach(function (r) { geschrieben.push(r.id); });
    (delIds || []).forEach(function (id) { geloescht.push(id); });
    return Promise.resolve();
  }
};
"""

MESSUNG = u"""
// ---------------------------------------------------------------------------------------
// Die beiden IDs, um die es geht.
var ECHT  = "rab12cd34ef";                        // Form von uid(): "r" + 10 Zeichen
var KUNST = '"><img src=x onerror=alert(1)>';     // frei gewaehlte Dokument-ID
var ergebnis = {};

function meal(id, name){ return { id: id, name: name }; }
function frisch(){
  state.recipes = []; state.plans = {}; state.deleted = {};
  lastPushedRecipes = new Map(); geschrieben = []; geloescht = [];
}

// 1 + 2: in der Gruppe
syncGid = "g1"; frisch();
onRecipesRemote([
  { type: "modified", id: KUNST, data: { name: "Eingeschleust" } },
  { type: "modified", id: ECHT,  data: { name: "Echtes Gruppen-Meal" } }
]);
ergebnis.abwehr    = state.recipes.every(function(r){ return r.id !== KUNST; });
ergebnis.durchlass = state.recipes.some(function(r){ return r.id === ECHT; });

// 4: Ruhe. Das abgelehnte Dokument darf weder in die Baseline noch in einen Batch geraten.
ergebnis.nichtInBaseline = !lastPushedRecipes.has(KUNST);
return syncRecipes().then(function () {
  ergebnis.nichtGeloescht  = geloescht.indexOf(KUNST) === -1;
  ergebnis.nichtGeschrieben = geschrieben.indexOf(KUNST) === -1;

  // 5: Der Planverweis auf das abgelehnte Meal faellt mit weg.
  var plan = normalizePlan({ mon: { fr: [KUNST, ECHT] } }, state.recipes);
  ergebnis.planSauber = plan.mon.fr.length === 1 && plan.mon.fr[0] === ECHT;

  // 6: Eine Karteileiche muss sich loeschen lassen. Laege aus der Zeit vor der Haertung
  //    noch ein Meal mit abweichender ID im lokalen Bestand, waere sein Loeschen durch ein
  //    anderes Mitglied wirkungslos, wenn die Pruefung VOR der Verzweigung nach c.type
  //    stuende - der Eintrag bliebe fuer immer stehen. (Fund des Agenten website-security
  //    am 06.09.2026.)
  syncGid = "g1"; frisch();
  state.recipes = [meal(KUNST, "Karteileiche aus der Zeit davor")];
  onRecipesRemote([{ type: "removed", id: KUNST }]);
  ergebnis.leicheLoeschbar = state.recipes.length === 0;

  // 3: OHNE Gruppe muss dieselbe abweichende ID durchkommen - eigene Altdaten.
  syncGid = null; frisch();
  onRecipesRemote([{ type: "modified", id: "r-alt-format-42", data: { name: "Eigenes Altmeal" } }]);
  ergebnis.eigeneAltdaten = state.recipes.some(function(r){ return r.id === "r-alt-format-42"; });

  return ergebnis;
});
"""

SEITE = u"""<!doctype html><meta charset="utf-8"><title>ID-Format</title>
<body><pre id="out">laeuft…</pre>
<script>
// Ein Syntaxfehler im geschnittenen Code beendet dessen Block STILL - die Seite bliebe
// auf "laeuft…" stehen und der Pruefstand wuesste nicht, warum. Der Melder steht
// deshalb in einem EIGENEN Block davor, damit er einen solchen Fehler ueberlebt.
window.addEventListener("error", function (e) {
  document.getElementById("out").textContent = "FEHLER " + e.message + " @ Zeile " + e.lineno;
});
</script>
<script>
%(umfeld)s
</script>
<script>
%(code)s
</script>
<script>
(function () {
  var p;
  try { p = (function () { %(messung)s })(); }
  catch (e) { document.getElementById("out").textContent = "FEHLER " + e.message; return; }
  p.then(function (r) {
    document.getElementById("out").textContent = JSON.stringify(r);
  }, function (e) {
    document.getElementById("out").textContent = "FEHLER " + e.message;
  });
})();
</script></body>
"""


def baue(code):
    return SEITE % {u"umfeld": UMFELD, u"code": code, u"messung": MESSUNG}


def fahre(seite, name):
    pfad = os.path.join(tempfile.gettempdir(), name)
    with io.open(pfad, "w", encoding="utf-8") as f:
        f.write(seite)
    ziel = os.path.join(tempfile.mkdtemp(prefix="mp-id-"), "aus.txt")
    subprocess.call([EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=4000",
                     "--dump-dom", "file:///" + pfad.replace("\\", "/")],
                    stdout=io.open(ziel, "wb"), stderr=subprocess.PIPE)
    with io.open(ziel, "r", encoding="utf-8", errors="replace") as f:
        dom = f.read()
    m = re.search(r'<pre id="out">(.*?)</pre>', dom, re.S)
    return m.group(1).strip() if m else u"(keine Ausgabe)"


def lies(roh):
    if roh.startswith(u"FEHLER") or not roh.startswith(u"{"):
        raise SystemExit(u"Pruefstand lief nicht: " + roh)
    import json
    return json.loads(roh.replace(u"&quot;", u'"').replace(u"&amp;", u"&")
                         .replace(u"&lt;", u"<").replace(u"&gt;", u">"))


def main():
    seite = pm_quelle.lade_seite(INDEX)
    zeilen = seite.split(u"\n")

    code = u"\n".join([
        eine_zeile(zeilen, u"function validRecipeId(id)"),
        eine_zeile(zeilen, u"function asIdList(v)"),
        eine_zeile(zeilen, u"function entryId(e)"),
        schneide(zeilen, u"const DAYS = [", u"];"),
        schneide(zeilen, u"const MEALS = [", u"];"),
        block(zeilen, u"function makeEmptyPlan()"),
        block(zeilen, u"function normalizePlan(rawPlan, recipes)"),
        block(zeilen, u"function canonValue(v)"),
        eine_zeile(zeilen, u"function canonJSON(v)"),
        block(zeilen, u"async function syncRecipes()"),
        block(zeilen, u"function onRecipesRemote(changes)"),
    ])

    print(u"== Neuer Stand ==")
    neu = lies(fahre(baue(code), "pm-id-neu.html"))
    for k, v in sorted(neu.items()):
        print(u"  %-18s %s" % (k, u"OK" if v else u"ROT"))

    # --- Gegenprobe: dieselbe Messung ohne die neue Zeile ---------------------------------
    alt_code, n = re.subn(r'^\s*if \(syncGid && !validRecipeId\(c\.id\)\) return;\s*$',
                          u"", code, flags=re.M)
    if n != 1:
        raise SystemExit(u"Gegenprobe unmoeglich: die zu entfernende Zeile wurde %d-mal gefunden." % n)
    print(u"\n== Gegenprobe 1 (alter Stand, Zeile entfernt) ==")
    alt = lies(fahre(baue(alt_code), "pm-id-alt.html"))
    for k, v in sorted(alt.items()):
        print(u"  %-18s %s" % (k, u"OK" if v else u"ROT"))

    # --- Gegenprobe 2: die Zeile an der NAHELIEGENDEN, aber falschen Stelle ---------------
    # Vor der Verzweigung nach c.type wuerde sie auch den "removed"-Zweig treffen. Die
    # Abwehr saehe genauso gruen aus - nur liesse sich eine Karteileiche aus der Zeit vor
    # der Haertung dann nie mehr loeschen. Ohne diese zweite Probe waere die Platzierung
    # bloss behauptet.
    falsch_code = re.sub(r'^\s*if \(syncGid && !validRecipeId\(c\.id\)\) return;\s*$',
                         u"", code, flags=re.M)
    anker = u"      if (c.pending) return;"
    treffer = [l for l in falsch_code.split(u"\n") if l.startswith(anker)]
    if len(treffer) != 1:
        raise SystemExit(u"Gegenprobe 2 unmoeglich: pending-Zeile %d-mal gefunden." % len(treffer))
    falsch_code = falsch_code.replace(
        treffer[0], treffer[0] + u"\n      if (syncGid && !validRecipeId(c.id)) return;", 1)
    print(u"\n== Gegenprobe 2 (Zeile vor der c.type-Verzweigung) ==")
    falsch = lies(fahre(baue(falsch_code), "pm-id-falsch.html"))
    for k, v in sorted(falsch.items()):
        print(u"  %-18s %s" % (k, u"OK" if v else u"ROT"))

    fehler = [k for k, v in neu.items() if not v]
    print(u"")
    if fehler:
        print(u"FEHLGESCHLAGEN: der neue Stand faellt durch bei " + u", ".join(sorted(fehler)))
        return 1
    if alt.get(u"abwehr"):
        print(u"FEHLGESCHLAGEN: Gegenprobe 1 besteht den Test ebenfalls -")
        print(u"                dieser Pruefstand misst nichts (docs/TESTING.md).")
        return 1
    if falsch.get(u"leicheLoeschbar"):
        print(u"FEHLGESCHLAGEN: Gegenprobe 2 raeumt die Karteileiche ebenfalls weg -")
        print(u"                dann belegt nichts, warum die Zeile im else-Zweig steht.")
        return 1
    print(u"ERGEBNIS %d gruen, 0 rot - Kunst-ID abgewehrt, echte ID und eigene Altdaten"
          % len(neu))
    print(u"         unberuehrt, kein Schreib-Loesch-Nachspiel; der alte Stand faellt durch.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
