# -*- coding: utf-8 -*-
u"""
Persoenlicher Wochenplan: slotweiser Abgleich statt "letzter Schreiber gewinnt" (Audit 17.10.2026).

Bis zum 17.10.2026 schrieb pushNow() den persoenlichen Plan als EIN Feld ins Kontodokument, und
onRemote()/startCloudSync() ersetzten den lokalen Plan durch den der Cloud. Zwei Folgen:

  1. Ein Geraet, das offline geplant hatte, schrieb beim Wiederverbinden seinen ALTEN Stand
     ueber die neueren Wochen des anderen Geraets (der Schreibvorgang lag in der Warteschlange
     des persistentLocalCache und kam spaeter an).
  2. Wer die App binnen der 800 ms Debounce nach einer Aenderung schloss, verlor sie beim
     naechsten Start an den Cloud-Stand.

Geprueft werden die ausgeschnittenen Produktionsfunktionen planSlots(), mergePlansSlotwise(),
planPatch(), slotTeile() und removeFromSlot(). Firestores mergeFields wird im Test nachgebildet
(cloudAnwenden): jeder Pfad wird ganz ersetzt bzw. geloescht, alles andere bleibt.

Gegenprobe: Jeder Abschnitt rechnet die ALTE Regel daneben ("ganzes Feld ersetzen" bzw.
"Cloud gewinnt") und verlangt, dass sie den Fehler zeigt. Zusaetzlich faellt der Pruefstand
gegen den Stand vor der Aenderung durch:  python tools/pruefstand-plan-slots.py <alte index.html>

Aufruf:  python tools/pruefstand-plan-slots.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(zeilen, start, ende):
    u"""Von der Zeile mit `start` bis einschliesslich der naechsten mit `ende`."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    if a is None:
        raise SystemExit(u"Marker nicht gefunden: " + start)
    b = next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if b is None:
        raise SystemExit(u"Endmarker nicht gefunden: " + ende)
    return u"\n".join(zeilen[a:b + 1])


TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
var W = "2026-W42", W2 = "2026-W43", ALT = "2026-W40";
function plan(slots) { return unflattenWeek(slots || {}); }
function kopie(o) { return JSON.parse(JSON.stringify(o)); }
// Firestore setDoc(..., { mergeFields }) nachbilden - mit genau den Pfaden aus pushPersonalPlans().
function writesAus(plans, base) {
  var p = planPatch(plans, base), w = [];
  p.set.forEach(function (k) { var t = slotTeile(k); w.push({ path: ["plans", t[0], t[1], t[2]], value: plans[t[0]][t[1]][t[2]].slice() }); });
  p.clear.forEach(function (k) { var t = slotTeile(k); w.push({ path: ["plans", t[0], t[1], t[2]], value: [] }); });
  p.dead.forEach(function (wk) { w.push({ path: ["plans", wk], del: true }); });
  return w;
}
function cloudAnwenden(doc, writes) {
  writes.forEach(function (w) {
    var o = doc;
    w.path.slice(0, -1).forEach(function (s) { o = o[s] || (o[s] = {}); });
    if (w.del) delete o[w.path[w.path.length - 1]]; else o[w.path[w.path.length - 1]] = w.value;
  });
  return doc;
}
function slot(plans, wk, d, m) { return ((plans[wk] || {})[d] || {})[m] || []; }

console.log("--- 1. Offline geplant: nur der eigene Slot geht hoch ---");
// T0: beide Geraete kennen mon_fr = [a]. A plant danach tue_mi = [b] (landet in der Cloud).
// B ist offline, kennt nur T0 und plant wed_ab = [c]. Dann kommt B wieder online.
var t0 = { }; t0[W] = plan({ mon_fr: ["a"] });
var baseB = planSlots(t0);
var cloud = { plans: kopie(t0) }; cloud.plans[W].tue.mi = ["b"];
var lokalB = kopie(t0); lokalB[W].wed.ab = ["c"];
var wB = writesAus(lokalB, baseB);
pr("B schreibt genau einen Slot", wB.length === 1 && wB[0].path.join(".") === "plans." + W + ".wed.ab", JSON.stringify(wB));
cloudAnwenden(cloud, wB);
pr("A's Slot ueberlebt", slot(cloud.plans, W, "tue", "mi")[0] === "b", JSON.stringify(cloud.plans[W].tue));
pr("B's Slot ist angekommen", slot(cloud.plans, W, "wed", "ab")[0] === "c");
pr("der alte Slot steht unveraendert", slot(cloud.plans, W, "mon", "fr")[0] === "a");
// Gegenprobe: alte Regel - B schreibt das ganze Feld
var cloudAlt = { plans: kopie(t0) }; cloudAlt.plans[W].tue.mi = ["b"];
cloudAlt.plans = kopie(lokalB);
pr("Gegenprobe: ganzes Feld ersetzen verliert A's Slot", slot(cloudAlt.plans, W, "tue", "mi").length === 0);

console.log("--- 2. Neustart nach nicht hochgeladener Aenderung ---");
// Cloud und Baseline: mon_fr = [a]. Lokal wurde auf [x] geaendert, die App vor dem Push geschlossen.
var remote2 = {}; remote2[W] = plan({ mon_fr: ["a"] });
var base2 = planSlots(remote2);
var lokal2 = {}; lokal2[W] = plan({ mon_fr: ["x"] });
var m2 = mergePlansSlotwise(lokal2, remote2, base2);
pr("lokale Aenderung bleibt", slot(m2, W, "mon", "fr")[0] === "x", JSON.stringify(m2[W].mon));
pr("und geht beim naechsten Push hoch", planPatch(m2, base2).set.length === 1);
// Gegenprobe: alte Regel - Cloud-Woche gewinnt ganz
pr("Gegenprobe: Cloud gewinnt verliert die Aenderung", slot(remote2, W, "mon", "fr")[0] === "a");

console.log("--- 3. Aenderung vom anderen Geraet kommt an ---");
var base3 = planSlots(remote2);
var lokal3 = kopie(remote2);
var remote3 = kopie(remote2); remote3[W].sun.ab = ["z"]; remote3[W].mon.fr = ["a", "y"];
var m3 = mergePlansSlotwise(lokal3, remote3, base3);
pr("neuer Slot uebernommen", slot(m3, W, "sun", "ab")[0] === "z");
pr("geaenderter Slot uebernommen", slot(m3, W, "mon", "fr").join() === "a,y");

console.log("--- 4. Leeren - lokal und remote ---");
var lokal4 = kopie(remote2); lokal4[W].mon.fr = [];
var m4 = mergePlansSlotwise(lokal4, remote2, planSlots(remote2));
pr("lokal geleert, noch nicht oben: bleibt leer", slot(m4, W, "mon", "fr").length === 0);
var p4 = planPatch(m4, planSlots(remote2));
pr("Patch schreibt die Leerung", p4.clear.length === 1 && p4.clear[0] === W + ".mon_fr", JSON.stringify(p4));
var remote4 = kopie(remote2); remote4[W].mon.fr = [];
var m4b = mergePlansSlotwise(kopie(remote2), remote4, planSlots(remote2));
pr("remote geleert, lokal unveraendert: wird leer", slot(m4b, W, "mon", "fr").length === 0);

console.log("--- 5. Ohne Baseline: altes Verhalten ---");
var lokal5 = {}; lokal5[W] = plan({ mon_fr: ["x"] }); lokal5[W2] = plan({ tue_mi: ["n"] });
var m5 = mergePlansSlotwise(lokal5, remote2, null);
pr("Cloud-Woche gewinnt", slot(m5, W, "mon", "fr")[0] === "a");
pr("rein lokale Woche bleibt", slot(m5, W2, "tue", "mi")[0] === "n");

console.log("--- 6. Verfallene Woche wird in der Cloud weggeraeumt ---");
var cloud6 = {}; cloud6[ALT] = plan({ mon_fr: ["alt"] }); cloud6[W] = plan({ mon_fr: ["a"] });
var lokal6 = {}; lokal6[W] = plan({ mon_fr: ["a"] });
var p6 = planPatch(lokal6, planSlots(cloud6));
pr("alte Woche als dead erkannt", p6.dead.length === 1 && p6.dead[0] === ALT, JSON.stringify(p6));
pr("und sonst nichts geschrieben", !p6.set.length && !p6.clear.length);
var d6 = cloudAnwenden({ plans: kopie(cloud6) }, writesAus(lokal6, planSlots(cloud6)));
pr("nach dem Schreiben ist sie weg", !d6.plans[ALT] && slot(d6.plans, W, "mon", "fr")[0] === "a");

console.log("--- 7. Kein Ping-Pong ---");
var konv = mergePlansSlotwise(m3, m3, planSlots(m3));
pr("eigener Stand als Echo aendert nichts", canonJSON(konv) === canonJSON(m3));
var p7 = planPatch(m3, planSlots(m3));
pr("und erzeugt keinen Schreibvorgang", !p7.set.length && !p7.clear.length && !p7.dead.length);
var e7 = {}; e7[W] = plan({ mon_fr: ["a", { id: "q", uids: ["u1"] }] });
pr("Eintrag mit Zuweisung uebersteht den Weg unveraendert",
   canonJSON(mergePlansSlotwise(e7, kopie(e7), planSlots(e7))) === canonJSON(e7));

console.log("--- 7b. Nur echte Wochenschluessel werden geschrieben (Pushcheck 17.10.2026) ---");
var schief = JSON.parse('{"__proto__": {}, "a.b": {}}');
schief["__proto__"] = plan({ mon_fr: ["x"] }); schief["a.b"] = plan({ mon_fr: ["y"] });
schief[W] = plan({ mon_fr: ["a"] });
var ps = planSlots(schief);
pr("nur die echte Woche landet in der Baseline", ps.size === 1 && ps.has(W + ".mon_fr"), JSON.stringify(Array.from(ps.keys())));
pr("und nur sie im Patch", planPatch(schief, new Map()).set.join() === W + ".mon_fr");

console.log("--- 8. Rueckgaengig nach Entfernen trifft die richtige Woche ---");
var undo = null;
undoToast = function (text, fn) { undo = fn; };
save = function () {}; render = function () {};
var aktiv = W;
activeWeekKey = function () { return aktiv; };
state = { plans: {} };
state.plans[W] = plan({ mon_fr: ["a", "b", "c"] });
state.plans[W2] = plan({ mon_fr: ["n"] });
state.plan = state.plans[W];
removeFromSlot("mon", "fr", 1);
pr("entfernt", state.plans[W].mon.fr.join() === "a,c");
aktiv = W2; state.plan = state.plans[W2];   // Woche gewechselt, bevor Rueckgaengig getippt wird
undo();
pr("zurueck in der Ursprungswoche", state.plans[W].mon.fr.join() === "a,b,c", state.plans[W].mon.fr.join());
pr("die andere Woche bleibt unberuehrt", state.plans[W2].mon.fr.join() === "n", state.plans[W2].mon.fr.join());
// Liste inzwischen verkuerzt (Cloud-Stand): Index wird begrenzt, nichts geht verloren
aktiv = W; state.plan = state.plans[W];
removeFromSlot("mon", "fr", 2);
state.plans[W].mon.fr = ["a"];             // ein Snapshot hat den Slot ersetzt
undo();
pr("verkuerzte Liste: Eintrag haengt hinten an", state.plans[W].mon.fr.join() === "a,c", state.plans[W].mon.fr.join());

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def main():
    quelle = pm_quelle.lade_seite(INDEX).split(u"\n")
    # Produktionscode schneiden, nicht abtippen.
    tage = schneide(quelle, u"const DAYS = [", u"  ];")
    mahl = schneide(quelle, u"const MEALS = [", u"  ];")
    leer = schneide(quelle, u"function makeEmptyPlan()", u"    return p;") + u"\n  }\n"
    flach = schneide(quelle, u"function flattenWeek(plan)", u"    return out;") + u"\n  }\n"
    entf = schneide(quelle, u"function unflattenWeek(fields)", u"        .filter(x => x !== null);")
    entf += u"\n    }));\n    return plan;\n  }\n"
    canon = schneide(quelle, u"function canonValue(v)", u"function canonJSON(v)")
    slots = schneide(quelle, u"function planSlots(plans)", u"    return [key.slice(0, dot)]") + u"\n  }\n"
    undo = schneide(quelle, u"function removeFromSlot(d, m, idx)", u"    });") + u"\n  }\n"

    stubs = u"var state, undoToast, save, render, activeWeekKey;\n"
    tmp = tempfile.mkdtemp(prefix="mp-planslots-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        io.open(seite, "w", encoding="utf-8").write(
            u"<script>\n" + stubs + tage + u"\n" + mahl + u"\n" + leer + flach + entf + canon + u"\n"
            + slots + undo + TEST + u"\n</script>")
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
