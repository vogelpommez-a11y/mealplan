# -*- coding: utf-8 -*-
u"""
Ein geloeschtes Meal muss auch dann aus dem Wochenplan verschwinden, wenn es
jemandem ZUGEWIESEN war.

Seit "Gemeinsam planen" ist ein Slot-Eintrag entweder ein blanker String (Rezept-ID,
"fuer alle") ODER ein Objekt `{id, uids}` (nur die genannten Mitglieder essen das
Gericht). `dropRecipeIds()` filterte mit

    .filter(x => !idSet.has(x))

also gegen den ROHEN Eintrag. Fuer ein Objekt trifft das nie zu - ein geloeschtes,
zugewiesenes Meal blieb als Geisterverweis im Plan stehen, waehrend dasselbe Meal in der
"fuer alle"-Form sauber verschwand. Der direkte Nachbar `rewritePlanIds()` macht es seit
jeher richtig (`entryId(e)`), und sein Kommentar nennt `dropRecipeIds()` sogar sein
"Vorbild" - das Vorbild war die kaputte Fassung.

Drei Wege fuehren in diese Funktion, alle drei sind in der Gruppe relevant:

  * `deleteRecipe()`      - ich loesche selbst
  * `onRecipesRemote()`   - ein anderes Mitglied loescht ("removed"-Zweig)
  * `startCloudSync()`    - Grabsteine beim Anmelden

Messgroesse:

    nach dropRecipeIds() enthaelt KEIN Slot mehr einen Eintrag mit der geloeschten id -
    unabhaengig davon, in welcher der beiden Formen er dort steht

Gegenprobe: die alte Filterfassung muss ROT werden.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-zuweisung-loeschen.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

# pm_quelle.lade_seite() statt io.open(): Der Produktionscode liegt inzwischen auf
# mehrere Dateien verteilt (css/, data/, lib/). Ein Pruefstand schreibt seine Seite
# nach tools/ - relative Verweise zeigten von dort ins Leere. quelle baut die eigenen
# Dateien an Ort und Stelle wieder ein: derselbe Text, nur wieder in einer Datei.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

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
var state = { plans: {}, favs: [], planned: {} };

// Die alte Fassung, fuer die Gegenprobe: identisch, nur der Filter vergleicht roh.
function dropRecipeIdsAlt(idSet) {
  Object.keys(state.plans).forEach(function (key) {
    var p = state.plans[key];
    if (!p) return;
    DAYS.forEach(function (d) { MEALS.forEach(function (m) {
      if (p[d.key] && p[d.key][m.key]) p[d.key][m.key] = asIdList(p[d.key][m.key]).filter(function (x) { return !idSet.has(x); });
    }); });
  });
  if (Array.isArray(state.favs)) state.favs = state.favs.filter(function (x) { return !idSet.has(x); });
  if (state.planned) Object.keys(state.planned).forEach(function (id) { if (idSet.has(id)) delete state.planned[id]; });
}

function leererPlan() {
  var p = {};
  DAYS.forEach(function (d) { p[d.key] = {}; MEALS.forEach(function (m) { p[d.key][m.key] = []; }); });
  return p;
}
// Eine Woche mit allen Formen, die im Datenmodell vorkommen duerfen.
function baueWoche() {
  var p = leererPlan();
  p.mon.fr = ["r1"];                                  // fuer alle (String)
  p.mon.mi = [{ id: "r1", uids: ["u1"] }];            // nur ich
  p.mon.ab = [{ id: "r1", uids: ["u2"] }];            // nur die andere Person
  p.tue.mi = [{ id: "r1", uids: ["u1", "u2"] }];      // beide, aber als Objekt
  p.tue.ab = ["r2", { id: "r1", uids: ["u1"] }, "r3"];// gemischter Slot
  p.wed.sn = [{ id: "r9", uids: ["u1"] }];            // fremdes Meal, muss bleiben
  return p;
}
function alleEintraege() {
  var raus = [];
  Object.keys(state.plans).forEach(function (w) {
    DAYS.forEach(function (d) { MEALS.forEach(function (m) {
      (state.plans[w][d.key][m.key] || []).forEach(function (e) { raus.push(e); });
    }); });
  });
  return raus;
}
function zaehleId(id) {
  return alleEintraege().filter(function (e) { return entryId(e) === id; }).length;
}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

console.log("--- 1. Ausgangslage: fuenf Verweise auf r1 in beiden Formen ---");
state.plans = { "2026-W35": baueWoche() };
pr("fuenf Eintraege mit r1", zaehleId("r1") === 5, zaehleId("r1") + "");
pr("davon vier als Objekt",
   alleEintraege().filter(function (e) { return entryId(e) === "r1" && typeof e !== "string"; }).length === 4);

console.log("--- 2. Loeschen raeumt ALLE Formen ---");
state.plans = { "2026-W35": baueWoche() };
dropRecipeIds(new Set(["r1"]));
pr("kein r1 mehr im Plan", zaehleId("r1") === 0, zaehleId("r1") + " uebrig");
pr("der gemischte Slot behaelt r2 und r3",
   state.plans["2026-W35"].tue.ab.length === 2 &&
   state.plans["2026-W35"].tue.ab.every(function (e) { return typeof e === "string"; }),
   JSON.stringify(state.plans["2026-W35"].tue.ab));
pr("das fremde Meal bleibt unangetastet", zaehleId("r9") === 1);

console.log("--- 3. Mehrere Wochen auf einmal ---");
state.plans = { "2026-W35": baueWoche(), "2026-W36": baueWoche() };
dropRecipeIds(new Set(["r1"]));
pr("beide Wochen sauber", zaehleId("r1") === 0, zaehleId("r1") + "");
pr("r9 in beiden Wochen erhalten", zaehleId("r9") === 2);

console.log("--- 4. Mehrere IDs auf einmal ---");
state.plans = { "2026-W35": baueWoche() };
dropRecipeIds(new Set(["r1", "r9"]));
pr("beide weg", zaehleId("r1") === 0 && zaehleId("r9") === 0);
pr("r2/r3 unberuehrt", zaehleId("r2") === 1 && zaehleId("r3") === 1);

console.log("--- 5. Favoriten und Planer-Gedaechtnis ziehen mit ---");
state.plans = { "2026-W35": baueWoche() };
state.favs = ["r1", "r9"];
state.planned = { r1: 3, r9: 1 };
dropRecipeIds(new Set(["r1"]));
pr("Favorit entfernt", state.favs.join(",") === "r9", state.favs.join(","));
pr("Gedaechtnis entfernt", !("r1" in state.planned) && state.planned.r9 === 1);

console.log("--- 6. rewritePlanIds() als Gegenstueck: gleiche Formen, gleiches Verhalten ---");
// Der Nachbar musste es schon immer koennen. Beide Funktionen muessen dieselbe Menge treffen -
// sonst biegt die eine um, was die andere stehen laesst.
state.plans = { "2026-W35": baueWoche() };
rewritePlanIds("r1", "rNEU");
pr("alle fuenf umgebogen", zaehleId("rNEU") === 5 && zaehleId("r1") === 0,
   "neu=" + zaehleId("rNEU") + " alt=" + zaehleId("r1"));
pr("die uids bleiben am Eintrag haengen",
   state.plans["2026-W35"].mon.mi[0].uids.join(",") === "u1");
pr("Strings bleiben Strings", typeof state.plans["2026-W35"].mon.fr[0] === "string");
// ... und jetzt loeschen: dieselbe Menge muss verschwinden
dropRecipeIds(new Set(["rNEU"]));
pr("dieselbe Menge laesst sich auch loeschen", zaehleId("rNEU") === 0, zaehleId("rNEU") + "");

console.log("--- 7. Randfaelle: leere Menge, leerer Plan ---");
state.plans = { "2026-W35": baueWoche() };
dropRecipeIds(new Set([]));
pr("leere Menge aendert nichts", zaehleId("r1") === 5);
state.plans = { "2026-W35": leererPlan() };
var geworfen = false;
try { dropRecipeIds(new Set(["r1"])); } catch (e) { geworfen = true; }
pr("leerer Plan wirft nicht", !geworfen);

console.log("--- 8. GEGENPROBE: die alte Filterfassung muss durchfallen ---");
state.plans = { "2026-W35": baueWoche() };
dropRecipeIdsAlt(new Set(["r1"]));
pr("alte Fassung laesst die Zuweisungen stehen", zaehleId("r1") === 4, zaehleId("r1") + " statt 4");
pr("alte Fassung entfernt nur die 'fuer alle'-Form",
   state.plans["2026-W35"].mon.fr.length === 0 && state.plans["2026-W35"].mon.mi.length === 1);
// Gegenprobe zur Gegenprobe: ohne Zuweisungen war die alte Fassung in Ordnung.
state.plans = { "2026-W35": leererPlan() };
state.plans["2026-W35"].mon.fr = ["r1"];
state.plans["2026-W35"].tue.mi = ["r1"];
dropRecipeIdsAlt(new Set(["r1"]));
pr("alte Fassung ohne Zuweisungen in Ordnung", zaehleId("r1") === 0,
   "sonst misst Abschnitt 8 nur 'irgendwie kaputt'");

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def main():
    quelle = pm_quelle.lade_seite(INDEX).split(u"\n")

    tage = schneide(quelle, u"const DAYS = [", u'{ key: "sun", label: "Sonntag",  ', u"\n  ];")
    mahl = schneide(quelle, u"const MEALS = [", u'{ key: "sn", label: "Snacks"', u"\n  ];")
    helfer = schneide(quelle, u"function asIdList(v)", u"function entryIsShared(e)")
    drop = schneide(quelle, u"function dropRecipeIds(idSet)",
                    u"if (state.planned) Object.keys(state.planned).forEach", u"\n  }")
    rewrite = schneide(quelle, u"function rewritePlanIds(vonId, nachId)",
                       u"delete state.planned[vonId];", u"\n    }\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-zuweis-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + tage + u"\n" + mahl + u"\n" + helfer + u"\n" + UMFELD +
            u"\n" + drop + u"\n" + rewrite + u"\n" + TEST + u"\n</script>")
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=5000",
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
