# -*- coding: utf-8 -*-
# Ausschneide-Pruefstand: Ein frisch berechnetes Ziel darf KEIN Feld auf undefined haben.
#
# Warum das eine eigene Pruefung braucht: Lokal fiel es nie auf - JSON.stringify verschluckt
# undefined. Firestore lehnt dagegen das GANZE Kontodokument ab, und der Push wiederholt
# denselben Wurf bei jedem save(). Genau so blieb ein "goal.diet: undefined" wochenlang liegen.
#
# GEGENPROBE ist Teil des Tests: computeGoal() OHNE sanitizeGoal muss rot sein. Liefert der
# Test dort gruen, prueft er nichts.
import io, os

import sys
# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

SRC = r"C:\Users\Paddy\Documents\Paddys Mealplan\index.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-ziel.html")
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
    # KG_MIN/KG_MAX stehen in ONB_NUM als Grenzen der Gewichtsfelder.
    "  " + [z for z in lines if z.startswith("  const KG_MIN = ")][0].strip(),
    block("  const DAYS = [", "  ];"),
    block("  const ACTIVITY = [", "  function activityFactor("),
    block("  const TRAIN_LEVELS = [", "  function trainLevel("),
    block("  const DIETS = [", "  const AVOID_KEYS ="),
    block("  const ONB_NUM = {", "  };"),
    schnitt("  function sanitizeTraining("),
    schnitt("  function sanitizeBodyfat("),
    schnitt("  function paceAdjust("),
    schnitt("  function sanitizeGoal("),
    schnitt("  function computeGoal("),
    schnitt("  function onbGoalInput("),
]
code = "\n\n".join(teile)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Ziel</title>
<pre id="log"></pre>
<script>
// Eigener Block VOR dem Pruefcode: window.onerror im selben Block gesetzt faengt einen
// Parse-Fehler dieses Blocks nicht - dann bliebe die Seite stumm.
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
// Die Stelle, um die es geht: welche Schluessel tragen undefined?
function undefFelder(o) {
  var raus = [];
  Object.keys(o).forEach(function (k) { if (o[k] === undefined) raus.push(k); });
  return raus;
}
var onb = null;   // onbGoalInput() liest onb.cur - der Wizard-Zustand wird hier gesetzt.

__CODE__

function cur(extra) {
  var c = { name: "Paddy", sex: "m", age: "34", height: "182", weight: "88", weightGoal: "82",
            weightConsent: "yes", bodyfat: null, activity: "pal16", mode: "lose", pace: "moderate",
            diet: "alles", avoid: [], tdays: ["mon", "wed"], tlevel: "mod", tmin: "60" };
  if (extra) Object.keys(extra).forEach(function (k) { c[k] = extra[k]; });
  return c;
}

LOG.push("--- Gegenprobe: ohne sanitizeGoal MUSS es undefined geben ---");
onb = { cur: cur() };
var rohAlles = computeGoal(onbGoalInput());
pruef("computeGoal(\\"alles\\", keine Einschraenkung) traegt undefined",
      undefFelder(rohAlles).length > 0, "gefunden: [" + undefFelder(rohAlles).join(", ") + "]");
pruef("und zwar genau diet und avoid",
      undefFelder(rohAlles).sort().join(",") === "avoid,diet", undefFelder(rohAlles).join(","));

LOG.push("");
LOG.push("--- Der Wizard-Pfad (Schritt \\"result\\") ---");
var faelle = [
  ["alles, keine Einschraenkung",      cur()],
  ["vegetarisch + glutenfrei",         cur({ diet: "vegetarisch", avoid: ["glutenfrei"] })],
  ["vegan, keine Einschraenkung",      cur({ diet: "vegan", avoid: [] })],
  ["alles + laktosefrei",              cur({ diet: "alles", avoid: ["laktosefrei"] })],
  ["Gewicht halten (kein Tempo)",      cur({ mode: "hold", pace: null })],
  ["keine Trainingstage",              cur({ tdays: [], tlevel: null, tmin: "" })]
];
var zieleAusWizard = {};
faelle.forEach(function (f) {
  onb = { cur: f[1] };
  var g = sanitizeGoal(computeGoal(onbGoalInput()));
  zieleAusWizard[f[0]] = g;
  pruef("kein undefined: " + f[0], undefFelder(g).length === 0,
        "[" + undefFelder(g).join(", ") + "]");
});

LOG.push("");
LOG.push("--- Das Profil ueberlebt und wird tatsaechlich entfernt ---");
pruef("vegetarisch bleibt stehen", zieleAusWizard["vegetarisch + glutenfrei"].diet === "vegetarisch");
pruef("glutenfrei bleibt stehen",
      (zieleAusWizard["vegetarisch + glutenfrei"].avoid || []).join(",") === "glutenfrei");
pruef("\\"alles\\" schreibt KEIN diet-Feld",
      !("diet" in zieleAusWizard["alles, keine Einschraenkung"]));
pruef("keine Einschraenkung schreibt KEIN avoid-Feld",
      !("avoid" in zieleAusWizard["alles, keine Einschraenkung"]));

LOG.push("");
LOG.push("--- syncGoalWeight(): Wiegung auf einem sanitisierten Ziel ---");
// Genau der Fall, der jeden Nutzer ohne Einschraenkung traf: Im gespeicherten Ziel FEHLT der
// Schluessel diet. Object.assign kopiert ihn nicht, computeGoal setzt ihn auf undefined -
// und ab da synct das ganze Konto nicht mehr.
var gespeichert = sanitizeGoal(zieleAusWizard["alles, keine Einschraenkung"]);
pruef("Vorbedingung: gespeichertes Ziel hat keinen diet-Schluessel", !("diet" in gespeichert));
var rohWiegung = computeGoal(Object.assign({}, gespeichert, { weight: 86 }));
pruef("Gegenprobe: ohne sanitizeGoal entsteht wieder undefined",
      undefFelder(rohWiegung).length > 0, "[" + undefFelder(rohWiegung).join(", ") + "]");
var nachWiegung = sanitizeGoal(computeGoal(Object.assign({}, gespeichert, { weight: 86 })));
pruef("mit sanitizeGoal ist die Wiegung sauber", undefFelder(nachWiegung).length === 0,
      "[" + undefFelder(nachWiegung).join(", ") + "]");
pruef("das neue Gewicht ist angekommen", nachWiegung.weight === 86);

// Und die Gegenrichtung: ein gesetztes Profil darf eine Wiegung ueberleben.
var mitProfil = sanitizeGoal(zieleAusWizard["vegetarisch + glutenfrei"]);
var nachWiegung2 = sanitizeGoal(computeGoal(Object.assign({}, mitProfil, { weight: 84 })));
pruef("vegetarisch ueberlebt die Wiegung", nachWiegung2.diet === "vegetarisch");
pruef("glutenfrei ueberlebt die Wiegung", (nachWiegung2.avoid || []).join(",") === "glutenfrei");

LOG.push("");
LOG.push("--- sanitizeGoal ist idempotent (sonst waere jeder Push ein Dauer-Diff) ---");
Object.keys(zieleAusWizard).forEach(function (k) {
  var a = JSON.stringify(sanitizeGoal(zieleAusWizard[k]));
  var b = JSON.stringify(sanitizeGoal(sanitizeGoal(zieleAusWizard[k])));
  pruef("idempotent: " + k, a === b);
});

LOG.push("");
LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("Alle " + ok + " Pruefungen gruen."));
document.getElementById("log").textContent = LOG.join("\\n");
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben: " + OUT)


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
