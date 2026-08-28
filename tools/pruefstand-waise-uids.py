# -*- coding: utf-8 -*-
u"""
Ein Gericht, das niemandem gehoert, darf den Sync nicht ueberleben.

Ein Slot-Eintrag ist entweder ein String ("fuer alle") oder ein Objekt `{id, uids}`. Der
Zuweisungs-Dialog haelt eine ausdrueckliche Zusage: Wuerde eine Abwahl `uids.length === 0`
ergeben, wird der Eintrag KOMPLETT entfernt - "ein Gericht ohne zugewiesene Person darf nie
im Datenmodell existieren" (docs/ARCHITECTURES.md).

`unflattenWeek()` - der Weg, auf dem Plandaten von einem ANDEREN Geraet hereinkommen und der
fremden Daten ausdruecklich nicht vertraut - hielt diese Zusage nicht:

    return uids ? { id: x.id, uids: uids } : x.id;

Ein leeres Array ist in JavaScript TRUTHY. `{ id, uids: [] }` ueberlebte also.

Was so ein Eintrag anrichtet - er ist sichtbar, aber fuer jede Auswertung unsichtbar:

  * `dayNutOf()`      zaehlt ihn niemandem an (uids.indexOf(syncUid) === -1)
  * `slotOpenForMe()` haelt den Slot fuer frei -> der Auto-Planer plant darueber
  * `entryIsShared()` meldet "nicht gemeinsam" -> slotIsShared() kippt fuer die ganze Zeile
  * die Einkaufsliste skaliert ihn mit uids.length auf NULL -> er wird nie eingekauft

Und der Sanitizer kann die Waise SELBST erzeugen: Enthaelt `uids` nur Nicht-Strings
(`[null, 7]`), bleibt nach dem `filter(u => typeof u === "string")` ein leeres Array uebrig.
Es braucht also kein manipuliertes Dokument, ein fehlerhaftes genuegt.

Messgroesse:

    nach unflattenWeek() traegt KEIN Slot einen Eintrag mit leerer uids-Liste

Gegenprobe: die alte Fassung muss ROT werden.

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

Aufruf:  python tools/pruefstand-waise-uids.py [pfad-zu-index.html]
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
var syncUid = "ich";
var groupMembers = [{ uid: "ich" }, { uid: "du" }];
var state = { plan: null };
function makeEmptyPlan(){
  var p = {};
  DAYS.forEach(function(d){ p[d.key] = {}; MEALS.forEach(function(m){ p[d.key][m.key] = []; }); });
  return p;
}

// Die ALTE Fassung, fuer die Gegenprobe: identisch, nur ohne die Waisen-Pruefung.
function unflattenWeekAlt(fields){
  var plan = makeEmptyPlan();
  if (!fields) return plan;
  DAYS.forEach(function(d){ MEALS.forEach(function(m){
    var ids = fields[d.key + "_" + m.key];
    if (!Array.isArray(ids)) return;
    plan[d.key][m.key] = ids
      .filter(function(x){ return typeof x === "string" || (x && typeof x.id === "string" && (Array.isArray(x.uids) || x.uids === undefined)); })
      .map(function(x){
        if (typeof x === "string") return x;
        var uids = Array.isArray(x.uids) ? x.uids.filter(function(u){ return typeof u === "string"; }).slice(0,24) : null;
        return uids ? { id: x.id, uids: uids } : x.id;
      });
  }); });
  return plan;
}

function slots(plan){
  var raus = [];
  DAYS.forEach(function(d){ MEALS.forEach(function(m){
    plan[d.key][m.key].forEach(function(e){ raus.push(e); });
  }); });
  return raus;
}
function waisen(plan){
  return slots(plan).filter(function(e){ return e && typeof e !== "string" && Array.isArray(e.uids) && e.uids.length === 0; });
}
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}

console.log("--- 1. Leere uids-Liste kommt gar nicht erst herein ---");
var p = unflattenWeek({ mon_mi: [{ id: "r1", uids: [] }] });
pr("keine Waise im Plan", waisen(p).length === 0, JSON.stringify(slots(p)));
pr("der Slot ist leer", p.mon.mi.length === 0, JSON.stringify(p.mon.mi));

console.log("--- 2. Der Sanitizer erzeugt die Waise nicht mehr selbst ---");
// uids enthaelt NUR Nicht-Strings - nach dem filter() bliebe ein leeres Array uebrig.
p = unflattenWeek({ mon_mi: [{ id: "r1", uids: [null, 7, {}] }] });
pr("keine Waise", waisen(p).length === 0, JSON.stringify(p.mon.mi));
pr("Slot leer", p.mon.mi.length === 0);

console.log("--- 3. Gueltige Eintraege bleiben unangetastet ---");
p = unflattenWeek({ mon_mi: ["r1", { id: "r2", uids: ["ich"] }, { id: "r3", uids: ["ich","du"] }] });
pr("drei Eintraege", p.mon.mi.length === 3, p.mon.mi.length + "");
pr("String bleibt String", p.mon.mi[0] === "r1");
pr("eine uid bleibt", JSON.stringify(p.mon.mi[1]) === '{"id":"r2","uids":["ich"]}', JSON.stringify(p.mon.mi[1]));
pr("zwei uids bleiben", p.mon.mi[2].uids.length === 2);

console.log("--- 4. Objekt OHNE uids bleibt die String-Form (Altbestand, §73) ---");
p = unflattenWeek({ mon_ab: [{ id: "r9" }] });
pr("auf String zurueckgefuehrt", p.mon.ab[0] === "r9", JSON.stringify(p.mon.ab));

console.log("--- 5. Teilweise kaputte uids: der Rest ueberlebt ---");
p = unflattenWeek({ tue_fr: [{ id: "r1", uids: ["ich", null, 7, "du"] }] });
pr("Eintrag bleibt", p.tue.fr.length === 1);
pr("nur die Strings", JSON.stringify(p.tue.fr[0].uids) === '["ich","du"]', JSON.stringify(p.tue.fr[0]));

console.log("--- 6. Gemischter Slot: nur die Waise faellt heraus ---");
p = unflattenWeek({ wed_mi: ["r1", { id: "r2", uids: [] }, { id: "r3", uids: ["du"] }] });
pr("zwei von drei bleiben", p.wed.mi.length === 2, JSON.stringify(p.wed.mi));
pr("die richtigen zwei",
   p.wed.mi[0] === "r1" && p.wed.mi[1].id === "r3", JSON.stringify(p.wed.mi));

console.log("--- 7. Die 24er-Deckelung haelt weiterhin ---");
var viele = []; for (var i=0;i<40;i++) viele.push("u"+i);
p = unflattenWeek({ thu_ab: [{ id: "r1", uids: viele }] });
pr("auf 24 gedeckelt", p.thu.ab[0].uids.length === 24, p.thu.ab[0].uids.length + "");

console.log("--- 8. Muell faellt weiterhin heraus ---");
p = unflattenWeek({ fri_mi: [null, 7, { uids: ["ich"] }, { id: "r1", uids: "keinArray" }, "r2"] });
pr("nur der gueltige String bleibt", p.fri.mi.length === 1 && p.fri.mi[0] === "r2",
   JSON.stringify(p.fri.mi));

console.log("--- 9. Leere Felder und fehlende Wochen ---");
pr("ohne fields kein Absturz", slots(unflattenWeek(null)).length === 0);
pr("leeres Objekt", slots(unflattenWeek({})).length === 0);
pr("Feld kein Array", slots(unflattenWeek({ mon_mi: "kaputt" })).length === 0);

console.log("--- 10. Folgewirkung: die Waise hat den Slot fuer den Planer freigehalten ---");
// slotOpenForMe() haette den Slot als frei gemeldet, obwohl dort etwas STAND.
state.plan = unflattenWeekAlt({ sat_mi: [{ id: "r1", uids: [] }] });
var altFrei = slotOpenForMe("sat", "mi"), altVoll = state.plan.sat.mi.length;
state.plan = unflattenWeek({ sat_mi: [{ id: "r1", uids: [] }] });
var neuFrei = slotOpenForMe("sat", "mi"), neuVoll = state.plan.sat.mi.length;
pr("alt: Slot sieht frei aus, ist aber belegt", altFrei === true && altVoll === 1,
   "frei=" + altFrei + " eintraege=" + altVoll);
pr("neu: frei UND leer - kein Widerspruch mehr", neuFrei === true && neuVoll === 0,
   "frei=" + neuFrei + " eintraege=" + neuVoll);

console.log("--- 11. GEGENPROBE: die alte Fassung laesst die Waise durch ---");
var a = unflattenWeekAlt({ mon_mi: [{ id: "r1", uids: [] }] });
pr("alte Fassung: Waise ueberlebt", waisen(a).length === 1, JSON.stringify(a.mon.mi));
a = unflattenWeekAlt({ mon_mi: [{ id: "r1", uids: [null, 7] }] });
pr("alte Fassung: erzeugt sie sogar selbst", waisen(a).length === 1, JSON.stringify(a.mon.mi));

console.log("--- 12. Gegenprobe zur Gegenprobe: sonst ist die alte Fassung gleichwertig ---");
// Sonst misst Abschnitt 11 nur "die alte Fassung ist irgendwie anders".
var felder = { mon_mi: ["r1", { id: "r2", uids: ["ich"] }, { id: "r3" }],
               tue_ab: [{ id: "r4", uids: ["ich","du"] }] };
pr("ohne Waisen liefern beide dasselbe",
   JSON.stringify(unflattenWeek(felder)) === JSON.stringify(unflattenWeekAlt(felder)));

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def main():
    quelle = io.open(INDEX, encoding="utf-8").read().split(u"\n")

    tage = schneide(quelle, u"const DAYS = [", u'{ key: "sun", label: "Sonntag",  ', u"\n  ];")
    mahl = schneide(quelle, u"const MEALS = [", u'{ key: "sn", label: "Snacks"', u"\n  ];")
    helfer = schneide(quelle, u"function asIdList(v)", u"function entryIsShared(e)")
    unflat = schneide(quelle, u"function unflattenWeek(fields)", u".filter(x => x !== null);", u"\n    }));\n    return plan;\n  }")
    offen = schneide(quelle, u"function slotOpenForMe(dayKey, mealKey)", u"});", u"\n  }")

    tmp = tempfile.mkdtemp(prefix="mp-waise-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + tage + u"\n" + mahl + u"\n" + helfer + u"\n" + UMFELD +
            u"\n" + unflat + u"\n" + offen + u"\n" + TEST + u"\n</script>")
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
