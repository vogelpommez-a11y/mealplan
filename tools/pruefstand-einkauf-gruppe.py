# -*- coding: utf-8 -*-
u"""
Einkaufsliste und Vorkochliste in der Gruppe: was zaehlt fuer wen?

`tools/pruefstand-einkaufsliste.py` deckt den Abhak-Zustand, die Wochenbindung, die
Personenzahl und den PDF-Kopf ab - aber KEINE Zuweisungen. Genau dort verlaeuft in der
Gruppe die interessante Grenze, denn ein Slot-Eintrag ist entweder ein String ("fuer alle")
oder `{id, uids}`.

Der Vertrag, den beide Listen einhalten muessen:

    Endsumme = sharedQty * per + assignedQty

  * "fuer alle" wird mit dem globalen Personenfaktor `per` hochgerechnet
  * zugewiesene Gerichte sind bereits pro Gericht auf `uids.length` skaliert und
    duerfen den globalen Faktor NICHT noch einmal abbekommen
  * beide Listen beschreiben dieselbe Woche (planDaysAhead) und zaehlen dieselben Esser

Der Pruefstand haelt diesen Vertrag fest UND misst eine Unstimmigkeit, die dabei
herausfaellt - siehe Abschnitt 7. Sie ist KEIN Fehlschlag, sondern ein Messwert: Die
Entscheidung darueber gehoert dem Inhaber, nicht dem Pruefstand.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-einkauf-gruppe.py [pfad-zu-index.html]
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


def zeile(zeilen, marker):
    u"""Genau die eine Zeile mit `marker` - fuer die Einzeiler-Helfer."""
    t = next((l for l in zeilen if marker in l), None)
    if t is None:
        raise SystemExit(u"Marker nicht gefunden: " + marker)
    return t


UMFELD = u"""
var syncUid = "ich", syncGid = "g1";
var groupMembers = [{ uid: "ich" }, { uid: "du" }];
var gruppenEinstellungen = { shopForAll: true };
function groupSetting(k){ return gruppenEinstellungen[k]; }

// Der Pruefstand faehrt eine feste Woche: viewWeek "next" laesst planDaysAhead ALLE sieben
// Tage zaehlen, unabhaengig davon, welcher Wochentag beim Lauf gerade ist. Ohne das waere
// das Ergebnis am Sonntag ein anderes als am Montag.
var state = { plan: null, shopPersons: 1, viewWeek: "next" };
function todayDayKey(){ return "mon"; }

var REZEPTE = {
  nudeln: { id:"nudeln", name:"Nudeln mit Sosse", ingredients:[
    { name:"Nudeln", grams:100, unit:"g" }, { name:"Tomaten", grams:200, unit:"g" }, "Salz" ] },
  salat:  { id:"salat", name:"Salat", ingredients:[
    { name:"Tomaten", grams:50, unit:"g" }, { name:"Salz" } ] },
  shake:  { id:"shake", name:"Shake", ingredients:[ { name:"Milch", grams:300, unit:"ml" } ] }
};
function getRecipe(id){ return REZEPTE[id] || null; }

// Darstellung, nicht Rechnung - gestubbt, damit der Pruefstand die Summe misst.
var ING_UNITS = ["g","ml","Stk"];
function qtyLabel(n,u){ return n + " " + u; }
var SHOP_CATS = [{ key:"alles", title:"Alles", icon:"x" }];
var SHOP_OTHER = { key:"sonst", title:"Sonstiges", icon:"x" };
function shopCategory(){ return SHOP_CATS[0]; }

function leererPlan(){
  var p = {};
  DAYS.forEach(function(d){ p[d.key] = {}; MEALS.forEach(function(m){ p[d.key][m.key] = []; }); });
  return p;
}
function pos(liste, name){ return liste.filter(function(i){ return i.name === name; })[0]; }
function menge(liste, name){ var p = pos(liste, name); return p ? p.qty : null; }
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
function mess(name, wert, soll) {
  console.log("  MESS " + name + " = " + wert + (soll !== undefined ? "  (Vergleich: " + soll + ")" : ""));
}

console.log("--- 1. Personenfaktor in der Gruppe ---");
pr("shopForAll An -> Mitgliederzahl", shopPersons() === 2, shopPersons() + "");
gruppenEinstellungen.shopForAll = false;
pr("shopForAll Aus -> 1", shopPersons() === 1, shopPersons() + "");
gruppenEinstellungen.shopForAll = true;
state.shopPersons = 3;
pr("eigene Zahl schlaegt die Gruppe", shopPersons() === 3, shopPersons() + "");
state.shopPersons = 1;

console.log("--- 2. 'Fuer alle' wird mit dem Personenfaktor hochgerechnet ---");
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];                       // String = fuer alle
var l = buildShoppingList().items;
pr("Nudeln 100 x 2 = 200", menge(l, "Nudeln") === 200, menge(l, "Nudeln") + "");
pr("Tomaten 200 x 2 = 400", menge(l, "Tomaten") === 400, menge(l, "Tomaten") + "");

console.log("--- 3. Zugewiesen: mal uids.length, NICHT mal per ---");
state.plan = leererPlan();
state.plan.mon.mi = [{ id:"nudeln", uids:["ich"] }];  // nur ich
l = buildShoppingList().items;
pr("eine Person -> 100", menge(l, "Nudeln") === 100, menge(l, "Nudeln") + "");
state.plan.mon.mi = [{ id:"nudeln", uids:["ich","du"] }];
l = buildShoppingList().items;
pr("zwei Personen -> 200 (nicht 400)", menge(l, "Nudeln") === 200, menge(l, "Nudeln") + "");

console.log("--- 4. Dieselbe Zutat aus beiden Arten wird getrennt gerechnet ---");
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];                        // Tomaten 200, fuer alle -> x2 = 400
state.plan.mon.ab = [{ id:"salat", uids:["du"] }];     // Tomaten  50, zugewiesen -> x1 =  50
l = buildShoppingList().items;
pr("Tomaten 400 + 50 = 450", menge(l, "Tomaten") === 450, menge(l, "Tomaten") + "");

console.log("--- 5. Ein Gericht NUR fuer die andere Person steht trotzdem drin ---");
// Die Einkaufsliste ist eine Haushaltsliste, keine persoenliche - anders als dayNutOf().
state.plan = leererPlan();
state.plan.mon.ab = [{ id:"shake", uids:["du"] }];
l = buildShoppingList().items;
pr("Milch des anderen ist dabei", menge(l, "Milch") === 300, String(menge(l, "Milch")));

console.log("--- 6. Zutaten ohne Menge werden gezaehlt, nicht multipliziert ---");
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];
state.plan.tue.mi = ["nudeln"];
l = buildShoppingList().items;
var salz = pos(l, "") || l.filter(function(i){ return /Salz/i.test(i.label); })[0];
pr("Salz einmal in der Liste", !!salz, JSON.stringify(l.map(function(i){ return i.label; })));
pr("Salz ohne Menge", salz && !salz.qty, salz ? String(salz.qty) : "-");
pr("Salz zaehlt zwei Meals", salz && salz.count === 2, salz ? salz.count + "" : "-");

console.log("--- 7. MESSUNG: was macht 'Einkauf fuer alle rechnen: Aus'? ---");
// Die Einstellung verspricht "Mengen x Mitglieder". Aus heisst per = 1. Die Frage ist,
// ob das auch fuer ZUGEWIESENE Gerichte gilt - dort steckt der Faktor im Eintrag.
gruppenEinstellungen.shopForAll = false;
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];                          // fuer alle
state.plan.mon.ab = [{ id:"salat", uids:["ich","du"] }];  // beiden zugewiesen
l = buildShoppingList().items;
var nud = menge(l, "Nudeln"), tom = menge(l, "Tomaten");
mess("Nudeln (nur 'fuer alle')", nud, "100 = einfache Menge");
mess("Tomaten (200 'fuer alle' + 50 x 2 zugewiesen)", tom, "200 + 100 = 300");
pr("'fuer alle' folgt der Einstellung", nud === 100, nud + "");
pr("zugewiesen folgt ihr NICHT", tom === 300, tom + "");
console.log("  HINWEIS Mit 'Aus' bleibt der Mitglieder-Faktor bei zugewiesenen Gerichten");
console.log("          erhalten. Das ist heute so gewollt (jede zugewiesene Person braucht");
console.log("          ein eigenes Meal), steht aber quer zur Beschriftung 'Mengen x");
console.log("          Mitglieder / Aus'. Produktentscheidung, kein Fehlschlag.");
gruppenEinstellungen.shopForAll = true;

console.log("--- 8. Vorkochliste zaehlt dieselben Esser ---");
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];                          // fuer alle -> persons = 2
state.plan.tue.mi = [{ id:"nudeln", uids:["ich"] }];     // nur ich   -> 1
var b = buildBatchList();
var nudPort = b.items.filter(function(i){ return i.r.id === "nudeln"; })[0];
pr("Portionen 2 + 1 = 3", nudPort && nudPort.portions === 3, nudPort ? nudPort.portions + "" : "-");
pr("an zwei Tagen", nudPort && nudPort.days.length === 2, nudPort ? nudPort.days.length + "" : "-");

console.log("--- 9. Beide Listen beschreiben DIESELBE Woche ---");
// Gemeinsame Quelle planDaysAhead(); zwei Kopien waeren eine Frage der Zeit.
pr("gleicher todayIdx", buildShoppingList().todayIdx === buildBatchList().todayIdx);

console.log("--- 10. Waisen koennen die Summe nicht mehr verfaelschen (Ziffer 130) ---");
// uids: [] haette factor 0 ergeben - die Zutat waere lautlos aus der Liste gefallen.
state.plan = leererPlan();
state.plan.mon.mi = unflattenWeek({ mon_mi: [{ id:"nudeln", uids:[] }] }).mon.mi;
l = buildShoppingList().items;
pr("die Waise kam gar nicht erst herein", state.plan.mon.mi.length === 0,
   JSON.stringify(state.plan.mon.mi));
pr("und faelscht damit keine Menge", menge(l, "Nudeln") === null, String(menge(l, "Nudeln")));

console.log("--- 11. GEGENPROBE: der Faktor wirkt wirklich ---");
// Sonst bestuenden 2 und 3 auch, wenn ueberall stumpf 1 gerechnet wuerde.
state.plan = leererPlan();
state.plan.mon.mi = ["nudeln"];
var mitZwei = menge(buildShoppingList().items, "Nudeln");
groupMembers = [{ uid:"ich" }, { uid:"du" }, { uid:"er" }];
var mitDrei = menge(buildShoppingList().items, "Nudeln");
groupMembers = [{ uid:"ich" }, { uid:"du" }];
pr("2 Mitglieder -> 200, 3 -> 300", mitZwei === 200 && mitDrei === 300,
   mitZwei + " / " + mitDrei);

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")

    tage = schneide(quelle, u"const DAYS = [", u'{ key: "sun", label: "Sonntag",  ', u"\n  ];")
    mahl = schneide(quelle, u"const MEALS = [", u'{ key: "sn", label: "Snacks"', u"\n  ];")
    helfer = schneide(quelle, u"function asIdList(v)", u"function entryIsShared(e)")
    makeEmpty = schneide(quelle, u"function makeEmptyPlan()", u"return p;", u"\n  }")
    unflat = schneide(quelle, u"function unflattenWeek(fields)", u".filter(x => x !== null);",
                      u"\n    }));\n    return plan;\n  }")
    nutnum = zeile(quelle, u"function nutNum(x)")
    ingu = zeile(quelle, u"function ingUnit(o)")
    ingo = zeile(quelle, u"function ingObj(i)")
    ingl = schneide(quelle, u"function ingLabel(i)", u"}", u"")
    shopsan = zeile(quelle, u"function sanitizeShopPersons(v)")
    shoppers = schneide(quelle, u"function shopPersons()",
                        u"return sanitizeShopPersons(groupMembers.length);",
                        u"\n    return own;\n  }")
    tage2 = schneide(quelle, u"function planDaysAhead()", u"return { todayIdx: todayIdx", u"\n  }")
    einkauf = schneide(quelle, u"function buildShoppingList(persons)",
                       u"return { items, groups, todayIdx, persons: per };", u"\n  }")
    vorkoch = schneide(quelle, u"function buildBatchList()",
                       u"return { items: items, total: Math.round(total * 10) / 10, todayIdx: todayIdx };",
                       u"\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-einkgrp-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + tage + u"\n" + mahl + u"\n" + helfer + u"\n" + UMFELD +
            u"\n" + makeEmpty + u"\n" + unflat + u"\n" + nutnum + u"\n" + ingu + u"\n" + ingo +
            u"\n" + ingl + u"\n" + shopsan + u"\n" + shoppers + u"\n" + tage2 +
            u"\n" + einkauf + u"\n" + vorkoch + u"\n" + TEST + u"\n</script>")
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=6000",
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
