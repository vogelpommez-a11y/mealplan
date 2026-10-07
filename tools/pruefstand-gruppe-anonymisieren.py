# -*- coding: utf-8 -*-
u"""Austritt aus einer Gruppe: die Meals bleiben, die UID geht.

OFFENER PUNKT V4 des Art.-30-Verzeichnisses, entschieden am 22.09.2026.

Verliess jemand eine Gruppe, blieben seine Meals in `groups/{gid}/recipes` stehen -
mitsamt `by: <UID>`. Der Mitglieder-Eintrag verschwand, die Kennung nicht. Die
Oberflaeche zeigte danach zwar keinen Namen mehr (`recipeAuthorHtml` liefert bei
unbekannter uid ""), aber **nicht angezeigt ist keine Anonymisierung**: Die UID stand
weiter im Dokument und war ueber Firebase Auth weiter einer Person zuzuordnen.

Gemessen wird deshalb nicht "sieht man einen Namen", sondern:

    nach dem Austritt traegt KEIN Gruppen-Meal mehr die UID des Ausgetretenen

Dazu drei Dinge, die im Code auseinanderfallen koennen:

  1. die Funktion selbst (`CloudGroup.anonymizeMyRecipes`) - ausgeschnitten, kein Nachbau
  2. ihre STELLE im Ablauf: vor `leaveAtomic`, sonst ist man kein Mitglied mehr und
     die Regeln lassen nichts mehr zu
  3. die Firestore-Regel, die diese eine Aenderung erlaubt - und zwar UNABHAENGIG von
     `groupOwnerHasPro`, sonst haengt Art. 17 DSGVO am Abo eines Dritten

GEGENPROBE: `--gegenprobe` holt den Stand VOR dieser Aenderung aus git und faehrt
denselben Pruefstand dagegen. Er MUSS durchfallen. Bewusst kein nachgebauter "alter
Ablauf" im Testcode: Eine Funktion, die man selbst leer hinschreibt, belegt nur, dass
eine leere Funktion nichts tut. Der echte alte Code belegt, dass dieser Pruefstand den
Unterschied ueberhaupt sieht (Fallarchiv: erfundene Gegenproben sind schwaecher).

Aufruf:  python tools/pruefstand-gruppe-anonymisieren.py [pfad-zu-index.html]
         python tools/pruefstand-gruppe-anonymisieren.py --gegenprobe
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_pfade = [a for a in sys.argv[1:] if not a.startswith("--")]
INDEX = os.path.abspath(_pfade[0]) if _pfade else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende, anhang=u""):
    u"""Von der Zeile mit `start` bis einschliesslich der naechsten mit `ende`."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1]) + anhang


# --- Umgebung, die der ausgeschnittene Code vorfindet ------------------------------------
#
# Nachgebildet ist NUR Firestore, und zwar mit der Semantik, auf die es hier ankommt:
# ein Batch wird erst beim commit() wirksam, und update() fasst genau die genannten
# Felder an. Waere der Stub grosszuegiger (z. B. update = set), gingen genau die Fehler
# durch, die dieser Pruefstand finden soll.
UMFELD = u"""
var COMMITS = 0;         // wie oft wurde wirklich geschrieben?
var UPDATES = [];        // was genau ging an Firestore?
var cloud = {};          // id -> Meal

function db() {}
function recipesCol(base) { return base.join("/"); }
function recipeDoc(base, id) { return base.join("/") + "/" + id; }

function getDocs(col) {
  return Promise.resolve({
    docs: Object.keys(cloud).map(function (id) {
      return { id: id, data: function () { return JSON.parse(JSON.stringify(cloud[id])); } };
    })
  });
}

function writeBatch() {
  var ops = [];
  return {
    update: function (pfad, felder) { ops.push({ pfad: pfad, felder: felder }); },
    commit: function () {
      COMMITS++;
      ops.forEach(function (o) {
        var id = o.pfad.split("/").pop();
        UPDATES.push({ id: id, felder: o.felder });
        // Genau die genannten Felder - nicht mehr. Das ist der Kern von update().
        Object.keys(o.felder).forEach(function (k) { cloud[id][k] = o.felder[k]; });
      });
      ops = [];
      return Promise.resolve();
    }
  };
}

function meal(id, by, name) {
  return { id: id, by: by, name: name || ("Meal " + id), nutrition: { kcal: 500 } };
}

function frischerStand() {
  cloud = {};
  COMMITS = 0; UPDATES = [];
  cloud["r1"] = meal("r1", "ich", "Bowl von mir");
  cloud["r2"] = meal("r2", "luisa", "Auflauf von Luisa");
  cloud["r3"] = meal("r3", "ich", "Steak von mir");
  cloud["r4"] = meal("r4", "", "schon anonym");
}

function meineNoch(uid) {
  return Object.keys(cloud).filter(function (id) { return cloud[id].by === uid; });
}

// --- Zweiter Ort: die Zuweisungen im Wochenplan ------------------------------------------
// groups/{gid}/plans/{week} traegt flache Slot-Felder ("mo_fr", "di_ab", ...), und ein
// Eintrag darin ist ENTWEDER eine blosse id (= fuer alle) ODER {id, uids:[...]}.
var plaene = {};
function frischePlaene() {
  // `by`/`at` auf Dokumentebene: "zuletzt geaendert von" - savePlanWeek() setzt es bei
  // jedem Schreiben. Das ist der DRITTE Ort mit der UID (Befund `anwalt`, 30.09.2026).
  plaene = {
    "2026-W39": {
      mo_fr: ["r1", { id: "r2", uids: ["ich", "luisa"] }],
      di_ab: [{ id: "r3", uids: ["ich"] }],
      mi_mi: [{ id: "r2", uids: ["luisa"] }],
      do_fr: ["r4"],
      by: "ich", at: 1
    },
    "2026-W40": { fr_ab: [{ id: "r1", uids: ["ich"] }], by: "luisa", at: 2 },
    "2026-W41": { sa_mi: ["r4"], by: "ich", at: 3 }
  };
}
function planUids() {
  var raus = [];
  Object.keys(plaene).forEach(function (w) {
    Object.keys(plaene[w]).forEach(function (f) {
      if (!Array.isArray(plaene[w][f])) return;
      plaene[w][f].forEach(function (e) {
        if (e && typeof e === "object" && e.uids) raus = raus.concat(e.uids);
      });
    });
  });
  return raus;
}
function planEintrag(woche, feld, i) { return plaene[woche][feld][i]; }

// Firestore-Stub fuer die Plan-Sammlung. setDoc mit merge:true ersetzt die genannten
// Felder ganz - genau das tut die echte Schnittstelle bei einem Array-Feld.
var PLAN_SCHREIBT = 0, PLAN_PATCHES = [];
function getDocsPlaene() {
  return Promise.resolve({
    docs: Object.keys(plaene).map(function (w) {
      return { id: w, data: function () { return JSON.parse(JSON.stringify(plaene[w])); } };
    })
  });
}
function setDocPlan(woche, patch) {
  PLAN_SCHREIBT++;
  PLAN_PATCHES.push(Object.keys(patch).sort().join(","));
  Object.keys(patch).forEach(function (f) { plaene[woche][f] = patch[f]; });
  return Promise.resolve();
}

"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

(async function () {

console.log("--- 1. Ausgangslage ---");
frischerStand();
pr("zwei Meals tragen meine UID", meineNoch("ich").length === 2, JSON.stringify(meineNoch("ich")));
pr("eines gehoert Luisa", meineNoch("luisa").length === 1);

console.log("--- 2. Austritt: meine UID verschwindet, sonst nichts ---");
frischerStand();
var wieviele = await CG.anonymizeMyRecipes("g1", "ich");
pr("kein Meal traegt noch meine UID", meineNoch("ich").length === 0, JSON.stringify(meineNoch("ich")));
pr("es wurden 2 Meals angefasst", wieviele === 2, wieviele + "");
pr("Luisas Meal blieb unberuehrt", cloud["r2"].by === "luisa", cloud["r2"].by);
pr("meine Meals sind noch DA - nur ohne Zuordnung",
   !!cloud["r1"] && !!cloud["r3"], "sie duerfen nicht geloescht werden");
pr("Name und Naehrwerte unveraendert",
   cloud["r1"].name === "Bowl von mir" && cloud["r1"].nutrition.kcal === 500);
pr("by ist leer, nicht geloescht", cloud["r1"].by === "", JSON.stringify(cloud["r1"].by));

console.log("--- 3. Es wurde wirklich nur `by` geschrieben ---");
// Wuerde hier ein ganzes Meal gesetzt (set statt update), schriebe ein austretendes
// Mitglied den Stand aus SEINEM Cache ueber die Fassung der Gruppe - und die Regel
// loestPersonenbezug() liesse es ausserdem nicht zu (hasOnly(['by'])).
var nurBy = UPDATES.every(function (u) {
  var k = Object.keys(u.felder);
  return k.length === 1 && k[0] === "by" && u.felder.by === "";
});
pr("jede Aenderung betrifft genau das Feld `by`", nurBy, JSON.stringify(UPDATES));

console.log("--- 4. Nichts zu tun heisst: gar nicht schreiben ---");
frischerStand();
var keine = await CG.anonymizeMyRecipes("g1", "niemand");
pr("kein Treffer -> 0 gemeldet", keine === 0, keine + "");
pr("kein Schreibvorgang ausgeloest", COMMITS === 0, COMMITS + " commit(s)");

console.log("--- 5. Mehr als ein Batch (Firestore-Grenze: 500) ---");
// Eine Gruppe hat hoechstens vier Mitglieder, aber nicht nur vierhundert Meals.
// Ohne Haeppchen wuerde Firestore den Batch ab 500 Vorgaengen ablehnen - und der
// Personenbezug bliebe genau bei den grossen Gruppen stehen.
cloud = {}; COMMITS = 0; UPDATES = [];
for (var i = 0; i < 901; i++) cloud["m" + i] = meal("m" + i, "ich");
var viele = await CG.anonymizeMyRecipes("g1", "ich");
pr("alle 901 anonymisiert", viele === 901 && meineNoch("ich").length === 0, viele + "");
pr("in mehreren Batches geschrieben", COMMITS === 3, COMMITS + " commit(s), erwartet 3");

console.log("--- 6. Der ZWEITE Ort: Zuweisungen im Wochenplan ---");
// Befund von `datenschutz-technik` (22.09.2026): anonymizeMyRecipes raeumt nur `by`
// an den Meals weg. Ein Meal kann im Wochenplan aber zusaetzlich einzelnen Mitgliedern
// zugewiesen sein ({id, uids:[...]}), und dort blieb die UID stehen. Dieselbe
// Verwechslung wie bei `by`, nur eine Sammlung weiter.
frischePlaene();
PLAN_SCHREIBT = 0; PLAN_PATCHES = [];
pr("vorher steht meine UID im Plan", planUids().filter(function (u) { return u === "ich"; }).length === 3,
   JSON.stringify(planUids()));
var wochen = await CG.anonymizeMyPlanAssignments("g1", "ich");
pr("keine Zuweisung traegt noch meine UID",
   planUids().indexOf("ich") === -1, JSON.stringify(planUids()));
pr("Luisas Zuweisungen bleiben",
   planUids().filter(function (u) { return u === "luisa"; }).length === 2, JSON.stringify(planUids()));
pr("alle drei Wochen angefasst (W41 nur wegen `by`)", wochen === 3, wochen + "");

console.log("--- 6a. Der DRITTE Ort: `by` auf Dokumentebene ---");
pr("W39: `by` ist leer", plaene["2026-W39"].by === "", JSON.stringify(plaene["2026-W39"].by));
pr("W41: `by` ist leer, obwohl dort keine Zuweisung stand",
   plaene["2026-W41"].by === "", JSON.stringify(plaene["2026-W41"].by));
pr("W40: Luisas `by` bleibt", plaene["2026-W40"].by === "luisa", JSON.stringify(plaene["2026-W40"].by));
pr("`at` bleibt unangetastet", plaene["2026-W39"].at === 1 && plaene["2026-W41"].at === 3);
// Die Regel loestPlanBezug() laesst `by` nur zu, wenn im selben Schreibvorgang NICHTS sonst
// steht (hasOnly(['by'])). Im gemeinsamen Paket mit den Zuweisungen lehnte sie alles ab -
// und ein Nur-Leser behielte seine Kennung doch.
pr("`by` wird in eigenen Schreibvorgaengen geleert, nie zusammen mit Zuweisungen",
   PLAN_PATCHES.filter(function (k) { return k === "by"; }).length === 2
   && PLAN_PATCHES.every(function (k) { return k === "by" || k.split(",").indexOf("by") === -1; }),
   JSON.stringify(PLAN_PATCHES));

console.log("--- 6b. Kein Eintrag wird zur Waise ---");
// Ein Gericht ohne zugewiesene Person darf im Datenmodell nicht existieren
// (docs/ARCHITECTURES.md): {id, uids: []} waere sichtbar, zaehlte aber bei niemandem.
var waisen = [];
Object.keys(plaene).forEach(function (w) {
  Object.keys(plaene[w]).forEach(function (f) {
    if (!Array.isArray(plaene[w][f])) return;
    plaene[w][f].forEach(function (e) {
      if (e && typeof e === "object" && Array.isArray(e.uids) && e.uids.length === 0) waisen.push(w + "/" + f);
    });
  });
});
pr("keine leeren uids-Arrays entstanden", waisen.length === 0, JSON.stringify(waisen));
// War ich der einzige Zugewiesene, faellt der Eintrag seit dem 07.10.2026 aus dem Plan.
// Vorher wurde er zur String-Form (= fuer alle) - seit neue Gerichte als "nur ich" starten,
// landete so die ganze Woche der Ausgetretenen in Bilanz und Einkauf der anderen.
pr("ein Eintrag nur fuer mich faellt aus dem Plan (nicht: wird 'fuer alle')",
   JSON.stringify(plaene["2026-W39"].di_ab) === "[]" && JSON.stringify(plaene["2026-W40"].fr_ab) === "[]",
   JSON.stringify(plaene["2026-W39"].di_ab) + " | " + JSON.stringify(plaene["2026-W40"].fr_ab));
pr("aus {id,uids:[ich,luisa]} wurde {id,uids:[luisa]}",
   JSON.stringify(planEintrag("2026-W39", "mo_fr", 1)) === JSON.stringify({ id: "r2", uids: ["luisa"] }),
   JSON.stringify(planEintrag("2026-W39", "mo_fr", 1)));
pr("Eintraege ohne uids blieben unangetastet",
   planEintrag("2026-W39", "mo_fr", 0) === "r1" && planEintrag("2026-W39", "do_fr", 0) === "r4");

console.log("--- 6c. Nichts zu tun heisst auch hier: nicht schreiben ---");
frischePlaene();
PLAN_SCHREIBT = 0;
var keine2 = await CG.anonymizeMyPlanAssignments("g1", "niemand");
pr("kein Treffer -> 0 Wochen", keine2 === 0, keine2 + "");
pr("kein Schreibvorgang", PLAN_SCHREIBT === 0, PLAN_SCHREIBT + "");

console.log("--- 6d. Teilen-Link: die Meal-Kopie traegt keine fremde UID ---");
// Ein Gruppen-Meal traegt `by` = UID des Mitglieds, das es angelegt hat - oft nicht ich.
// Im Snapshot unter shared/ erreichte dessen Austritt oder Loeschung es nie mehr.
var GR = { id: "r7", name: "Chili", by: "luisa", nutrition: { kcal: 600 } };
// Global, nicht lokal: shareMealPayload() ist auf oberster Ebene ausgeschnitten und sucht
// seine Helfer dort.
window.getRecipe = function (id) { return id === "r7" ? GR : null; };
window.safeImage = function () { return null; };
window.photoFor = function () { return "img/chili.webp"; };
window.syncUid = "ich"; window.profile = { name: "Paddy" };
var pay = shareMealPayload("r7");
pr("die Meal-Kopie hat kein `by`", !("by" in pay.recipes[0]), JSON.stringify(pay.recipes[0]));
pr("das Original im Bestand behaelt sein `by`", GR.by === "luisa", GR.by);
pr("Inhalt der Kopie vollstaendig", pay.recipes[0].name === "Chili" && pay.recipes[0].nutrition.kcal === 600);
pr("die eigene uid bleibt (Regeln + Loeschen haengen daran)", pay.uid === "ich", pay.uid);

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
})();
"""


def statisch():
    u"""Die drei Stellen, die ausserhalb der Funktion liegen - und leise brechen koennen."""
    befunde = []
    html = pm_quelle.lade_seite(INDEX)
    rules = io.open(os.path.join(BASIS, "firestore.rules"), encoding="utf-8").read()

    def pr(name, bedingung, warum):
        if bedingung:
            print(u"  OK   %s" % name)
        else:
            print(u"  FAIL %s  -> %s" % (name, warum))
            befunde.append(name)

    print(u"--- 7. Die Stelle im Ablauf ---")
    m = re.search(r"async function leaveGroup\(keep\)(.*?)\n  \}", html, re.S)
    rumpf = m.group(1) if m else ""
    i_anon = rumpf.find("anonymizeMyRecipes")
    i_leave = rumpf.find("leaveAtomic")
    pr(u"leaveGroup ruft anonymizeMyRecipes", i_anon >= 0,
       u"der Austritt laesst den Personenbezug stehen")
    pr(u"und zwar VOR leaveAtomic", 0 <= i_anon < i_leave,
       u"danach ist man kein Mitglied mehr - die Regel lehnt ab, still")
    pr(u"Nur-Leser werden ausgenommen", "warNurLeser" in rumpf[:max(i_anon, 1)],
       u"Nur-Leser haben nie Meals eingebracht")

    print(u"--- 8. Die anderen beiden Wege aus einer Gruppe ---")
    pr(u"Entfernen durch den Inhaber anonymisiert auch",
       "anonymizeMyRecipes(syncGid, b.dataset.kick)" in html,
       u"wer entfernt wird, kann es danach selbst nicht mehr")
    pr(u"die Kontoloeschung anonymisiert auch",
       "konto:anonymGruppe" in html,
       u"sonst ueberlebt die UID in fremder Gruppe die Kontoloeschung")

    print(u"--- 8b. Und der zweite Ort auf allen drei Wegen ---")
    # Die Meals waren nur die HAELFTE. Ein Meal kann im Wochenplan zusaetzlich einzelnen
    # Mitgliedern zugewiesen sein; dort steckt dieselbe UID. Wer nur `by` raeumt, hat den
    # Personenbezug halb entfernt und haelt ihn fuer ganz weg.
    pr(u"leaveGroup raeumt auch die Zuweisungen",
       "group:anonymPlan" in html,
       u"die UID bleibt in groups/{gid}/plans stehen")
    pr(u"der Kick-Pfad ebenso",
       "group:anonymPlanKick" in html,
       u"wer entfernt wird, kann es danach selbst nicht mehr")
    pr(u"die Kontoloeschung ebenso",
       "konto:anonymPlan" in html,
       u"sonst ueberlebt die Zuweisung die Kontoloeschung")
    # Der dritte Ort (30.09.2026): `by` auf Dokumentebene - in BEIDEN Bereinigungen.
    pr(u"`by` auf Dokumentebene wird an beiden Stellen EINZELN geleert",
       html.count(u', { by: "" }, { merge: true })') == 2,
       u"Kontoloeschung oder Austritt laesst 'zuletzt geaendert von' stehen")
    pr(u"die Kontoloeschung meldet ein Scheitern dabei",
       "konto:anonymPlanBy" in html, u"ein stilles Scheitern faellt niemandem auf")

    print(u"--- 9b. Die Regel fuer den Plan ---")
    pr(u"loestPlanBezug() steht in firestore.rules",
       "function loestPlanBezug(gid)" in rules, u"ohne sie lehnt Firestore das bei Nur-Lesern ab")
    pblok = re.search(r"match /groups/\{gid\}/plans/\{weekKey\}(.*?)\n    \}", rules, re.S)
    pinhalt = pblok.group(1) if pblok else ""
    pr(u"allow update laesst sie zu, ohne Pro und ohne canWrite",
       "isMember(gid) && loestPlanBezug(gid)" in pinhalt,
       u"sonst haengt Art. 17 am Abo eines Dritten oder an der Rolle")
    pfunk = re.search(r"function loestPlanBezug\(gid\) \{(.*?)\n    \}", rules, re.S)
    pf = pfunk.group(1) if pfunk else ""
    pr(u"sie kann nur `by` leeren, nichts sonst",
       "hasOnly(['by'])" in pf and "request.resource.data.by == ''" in pf,
       u"ohne hasOnly waere es ein Freibrief auf den Gruppenplan")
    pr(u"create bleibt streng",
       "allow create: if canWrite(gid) && groupOwnerHasPro(gid) && nichtGesperrt(gid);" in pinhalt,
       u"die Ausnahme darf kein Anlegen erlauben")

    print(u"--- 9. Die Regel, die es erlauben muss ---")
    pr(u"loestPersonenbezug() steht in firestore.rules",
       "function loestPersonenbezug(gid)" in rules,
       u"ohne sie lehnt Firestore jede dieser Aenderungen ab")
    blok = re.search(r"match /groups/\{gid\}/recipes/\{recipeId\}(.*?)\n    \}", rules, re.S)
    inhalt = blok.group(1) if blok else ""
    pr(u"allow update laesst sie zu", "loestPersonenbezug(gid)" in inhalt,
       u"die Funktion existiert, wird aber nirgends verwendet")
    # Der eigentliche Punkt: die Ausnahme darf NICHT an Pro haengen.
    zweig = inhalt.split("loestPersonenbezug")[0].split("allow update")[-1]
    pr(u"die Ausnahme haengt NICHT an groupOwnerHasPro",
       "isMember(gid) && loestPersonenbezug(gid)" in inhalt,
       u"sonst haengt Art. 17 DSGVO am Abo eines Dritten")
    pr(u"sie kann nur wegnehmen, nichts setzen",
       "hasOnly(['by'])" in rules and "request.resource.data.by == ''" in rules,
       u"ohne hasOnly waere es ein Freibrief auf fremde Meals")
    pr(u"create bleibt streng", "allow create: if canWrite(gid) && groupOwnerHasPro(gid)" in inhalt,
       u"die Trennung von create und update darf create nicht aufweichen")
    return befunde


def main():
    quelle = pm_quelle.lade_seite(INDEX).split(u"\n")
    anon = schneide(quelle, u"anonymizeMyRecipes: async function (gid, uid) {",
                    u"          return meine.length;", u"\n        }")
    # Die zweite Funktion greift auf die Plan-Sammlung zu. Sie nutzt dieselben Namen
    # (getDocs/setDoc/collection/doc) wie die Meal-Funktion - im Stub sind das aber zwei
    # verschiedene Sammlungen. Deshalb werden hier nur die beiden ZUGRIFFE auf die
    # Plan-Stubs umgebogen. Der gepruefte Teil - Filterlogik, Waisen-Rueckfuehrung,
    # Zaehlung - bleibt unangetastet; ausgetauscht wird nur, WOHER die Dokumente kommen.
    anon_plan = schneide(quelle, u"anonymizeMyPlanAssignments: async function (gid, uid) {",
                         u"          return angefasst.size;", u"\n        }")
    anon_plan = (anon_plan
                 .replace(u'await getDocs(collection(db, "groups", gid, "plans"))',
                          u"await getDocsPlaene()")
                 .replace(u'await setDoc(doc(db, "groups", gid, "plans", d.id), patch, { merge: true })',
                          u"await setDocPlan(d.id, patch)")
                 .replace(u'await setDoc(doc(db, "groups", gid, "plans", d.id), { by: "" }, { merge: true })',
                          u'await setDocPlan(d.id, { by: "" })'))
    teilen = schneide(quelle, u"function shareMealPayload(recipeId) {",
                      u'return { app: "wochenkueche", v: 1, type: "meal"', u"\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-grpanon-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + UMFELD + u"\nvar CG = {\n" + anon + u",\n" + anon_plan
            + u"\n};\n" + teilen + u"\n" + TEST + u"\n</script>")
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
        js_ok = bool(letzte) and letzte[-1].endswith("0 rot")

        print(u"")
        stat = statisch()

        print(u"\n" + u"=" * 66)
        # Die ERGEBNIS-Zeile des JS-Laufs zaehlt NUR den JS-Teil. Wuerden die statischen
        # Pruefungen rot, staende dort trotzdem "0 rot" - ein halber Beleg, der wie ein
        # ganzer aussieht. Deshalb hier eine zweite, die beide Haelften zusammenfasst.
        print(u"ERGEBNIS gesamt: JS %s, statisch %d rot"
              % (u"gruen" if js_ok else u"ROT", len(stat)))
        if js_ok and not stat:
            print(u"GRUEN - die UID verlaesst die Gruppe mit der Person.")
            return 0
        print(u"ROT - %s%s" % (u"" if js_ok else u"Funktionslauf rot. ",
                               u"%d statische Befunde." % len(stat) if stat else u""))
        return 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def gegenprobe():
    u"""Faehrt diesen Pruefstand gegen den Stand VOR der Aenderung - er muss durchfallen.

    Die alte Fassung kommt aus git, nicht aus der Erinnerung. Sie landet im Projektordner
    und nicht in TEMP, weil quelle.lade_seite() die Nachbardateien (css/, data/, lib/)
    an Ort und Stelle wieder einbaut - von ausserhalb zeigten die Verweise ins Leere.
    """
    import subprocess as sp
    ziel = os.path.join(BASIS, "_gegenprobe-index.html")
    try:
        roh = sp.run(["git", "show", "HEAD:index.html"], cwd=BASIS,
                     capture_output=True, timeout=60)
        if roh.returncode != 0:
            print(u"git show schlug fehl - Gegenprobe nicht moeglich.")
            return 2
        io.open(ziel, "wb").write(roh.stdout)
        print(u"Gegenprobe: derselbe Pruefstand gegen HEAD:index.html")
        print(u"-" * 66)
        erg = sp.run([sys.executable, os.path.abspath(__file__), ziel],
                     cwd=BASIS, capture_output=True, text=True,
                     encoding="utf-8", errors="replace", timeout=300)
        aus = (erg.stdout or "") + (erg.stderr or "")
        for z in aus.strip().splitlines()[-6:]:
            print(u"  | %s" % z)
        print(u"-" * 66)
        if erg.returncode == 0:
            print(u"GEGENPROBE ROT - der alte Stand kam DURCH.")
            print(u"  Dieser Pruefstand misst die Anonymisierung nicht.")
            return 1
        print(u"GEGENPROBE GRUEN - der alte Stand faellt durch (Rueckgabewert %d)."
              % erg.returncode)
        print(u"  Der Pruefstand sieht den Unterschied also wirklich.")
        return 0
    finally:
        try:
            os.remove(ziel)
        except OSError:
            pass


if __name__ == "__main__":
    if "--gegenprobe" in sys.argv:
        sys.exit(gegenprobe())
    sys.exit(main())
