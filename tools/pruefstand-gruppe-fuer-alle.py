# -*- coding: utf-8 -*-
u"""
"Fuer alle" in der Gruppe sichtbar machen - Plankarte, Toast beim Einplanen, Einkaufsliste.

Anlass (05.10.2026): In einer Zweiergruppe legt man ein Meal in eine leere Zeile, es wird
ein "fuer alle"-Eintrag, und die Einkaufsliste nimmt die Zutaten mal zwei. Gerechnet war
das richtig ("ein Topf, zwei Teller") - nur stand es nirgends. Die Karte sah aus wie ein
Gericht fuer eine Person, und die doppelte Menge im Einkaufskorb wirkte wie ein Fehler.

Nachtrag 07.10.2026: Am Geraet hatte jemand die eigene Woche durchgeplant, ohne an die
Gruppe zu denken - alles "fuer alle", die Einkaufsliste doppelt. Seitdem startet jedes neu
eingeplante Gericht als "nur ich"; "Für euch beide" waehlt man bewusst (Toast oder Menue).

Geprueft wird:

  1. gruppenPortionen() - die eine Zahl, die alle drei Hinweise nennen
  2. Plankarte: "für 2" in der Metazeile und "– für alle" im Titel, NUR bei "fuer alle";
     Schild an "fuer alle" (alle Kuerzel) und an Fremdem, NICHT an "nur ich"
  3. eingeplantMelden(): Toast "Für dich eingeplant" mit "Für euch beide" und "Rückgängig",
     nur in der Gruppe; beide Knoepfe speichern und greifen nicht in eine andere Woche
  4. persAusGruppe(): "Wie eure Gruppe" nur, wenn die Personenzahl wirklich aus der Gruppe
     kommt - eine von Hand gesetzte Zahl schlaegt sie, wie in shopPersons()
  5. Alle Einplan-Stellen von Hand legen "nur ich" an und melden ueber eingeplantMelden()
     (statische Pruefung)
  6. openAssignMenu() bei zwei Personen: drei feste Wahlen (menuitemradio), aktive markiert

Der Code wird aus `index.html` GESCHNITTEN, nicht abgetippt.

GEGENPROBE gegen den alten Stand (vollstaendig, mit lib/ und data/ - der Schnappschuss
unter tools/vorher/ traegt nur index.html und css/, quelle.py braucht aber die eingebundenen
Dateien):
    git archive adc4ac7 index.html css data lib | tar -x -C <ordner>
    python tools/pruefstand-gruppe-fuer-alle.py <ordner>/index.html
muss rot werden (07.10.2026: 1 gruen, 13 rot). Fehlende Funktionen werden dabei als rote Pruefung gezaehlt statt als
Abbruch, und Abschnitt 5 misst am alten Text echtes Verhalten: Dort folgt auf das Einplanen
ein schlichtes toast("Zum Plan hinzugefügt").

Aufruf:  python tools/pruefstand-gruppe-fuer-alle.py [pfad-zu-index.html]
"""
import io, os, re, subprocess, sys, tempfile, shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

FEHLT = []


def schneide(zeilen, start, ende, anhang=u""):
    u"""Wie in den anderen Pruefstaenden - nur dass ein fehlender Marker als rote Pruefung
    zaehlt statt als Abbruch. Sonst endete die Gegenprobe am alten Stand beim ersten
    fehlenden Marker, und Abschnitt 5 (echtes Verhalten am alten Text) liefe nie."""
    a = next((i for i, l in enumerate(zeilen) if start in l), None)
    b = None if a is None else next((i for i, l in enumerate(zeilen) if i > a and ende in l), None)
    if a is None or b is None:
        FEHLT.append(start)
        return u""
    return u"\n".join(zeilen[a:b + 1]) + anhang


UMFELD = u"""
var syncUid = "ich", syncGid = "g1";
var groupMembers = [{ uid: "ich", name: "Paddy" }, { uid: "du", name: "Anna" }];
var gruppenEinstellungen = { shopForAll: true };
function groupSetting(k){ return gruppenEinstellungen[k]; }
var state = { plan: null, plans: {}, shopPersons: 1, viewWeek: "current" };
var DAYS = [{ key: "mon" }, { key: "tue" }];
var MEALS = [{ key: "mi" }, { key: "ab" }];
function leererPlan(){
  var p = {};
  DAYS.forEach(function(d){ p[d.key] = {}; MEALS.forEach(function(m){ p[d.key][m.key] = []; }); });
  return p;
}

// Darstellung gestubbt - gemessen wird, WAS gemeldet wird, nicht wie es aussieht.
var gerendert = 0;
function render(){ gerendert++; }
var gespeichert = 0;
function save(){ gespeichert++; }
function memberBadgeHtml(uids){ return uids && uids.length ? "B:" + uids.join(",") : ""; }
function esc(s){ return String(s); }
function memberAvatarHtml(m){ return '<span class="avatar">' + m.name[0] + '</span>'; }
function el(html){ var d = document.createElement("div"); d.innerHTML = html.trim(); return d.firstChild; }
function closeMenuNode(n){ n.remove(); }
function attachMenuDismiss(menu){ return function(){ menu.remove(); }; }
var letzterToast = null, letzterUndo = null;
function toast(msg){ letzterToast = msg; letzterUndo = null; }
function undoToast(msg, undoFn, opts){ letzterToast = msg; letzterUndo = { undo: undoFn, opts: opts || {} }; }
function nutNum(x){ var n = Number(x); return isFinite(n) ? n : 0; }
function nfmt(n){ return String(Math.round(n)); }
function recipeNut(r){ return r.nutrition || {}; }
function memberByUid(u){ return groupMembers.filter(function(m){ return m.uid === u; })[0] || null; }
function firstName(n){ return String(n || "").split(" ")[0]; }
"""

TEST = u"""
var ok = 0, bad = 0;
function pr(name, bedingung, extra) {
  if (bedingung) { ok++; console.log("  OK   " + name); }
  else { bad++; console.log("  FAIL " + name + (extra ? "  -> " + extra : "")); }
}
function gibt(name){ return typeof window[name] === "function"; }
FEHLT.forEach(function(m){ pr("Ausschnitt vorhanden: " + m, false, "Marker fehlt in dieser index.html"); });

console.log("--- 1. gruppenPortionen() ---");
if (gibt("gruppenPortionen")) {
  pr("Zweiergruppe -> 2", gruppenPortionen() === 2, String(gruppenPortionen()));
  groupMembers.push({ uid: "er", name: "Ben" });
  pr("Dreiergruppe -> 3", gruppenPortionen() === 3, String(gruppenPortionen()));
  groupMembers.pop();
  var g = syncGid; syncGid = null;
  pr("ohne Gruppe -> 0", gruppenPortionen() === 0, String(gruppenPortionen()));
  syncGid = g;
  var m = groupMembers; groupMembers = [{ uid: "ich" }];
  pr("allein in der Gruppe -> 0", gruppenPortionen() === 0, String(gruppenPortionen()));
  groupMembers = m;
  // Die Karte sagt, wer isst - nicht, wie viel eingekauft wird.
  gruppenEinstellungen.shopForAll = false;
  pr("haengt NICHT an 'Einkauf für alle rechnen'", gruppenPortionen() === 2, String(gruppenPortionen()));
  gruppenEinstellungen.shopForAll = true;
} else pr("gruppenPortionen() existiert", false);

console.log("--- 2. Plankarte: Metazeile und Titel ---");
if (gibt("karte")) {
  var r = { id: "nudeln", name: "Nudeln", nutrition: { kcal: 540 } };
  var k = karte(0, null, r);
  pr("'fuer alle' -> '540 kcal · für 2'", k.meta === "540 kcal · für 2", k.meta);
  pr("'fuer alle' -> Schild mit allen Kuerzeln", k.badge === "B:ich,du", k.badge);
  pr("'fuer alle' -> Titel '– für alle'", k.assignNote === " – für alle", k.assignNote);
  pr("Teile einzeln umbrechbar (je ein <span>)", k.roh === "<span>540 kcal</span> <span>· für 2</span>", k.roh);
  k = karte(1, ["ich"], r);
  pr("nur mir -> kein 'für 2'", k.meta === "540 kcal", k.meta);
  pr("nur mir -> Titel nennt den Namen", k.assignNote === " – nur für Paddy", k.assignNote);
  pr("nur mir -> KEIN Schild (der Normalfall)", k.badge === "", k.badge);
  k = karte(2, ["du"], r);
  pr("nur der anderen -> kein 'für 2'", k.meta === "540 kcal", k.meta);
  pr("nur der anderen -> ihr Schild", k.badge === "B:du", k.badge);
  var g2 = syncGid; syncGid = null;
  k = karte(0, null, r);
  pr("ohne Gruppe -> Karte wie bisher", k.meta === "540 kcal" && k.assignNote === "", k.meta + " | " + k.assignNote);
  syncGid = g2;
  k = karte(0, null, { id: "x", name: "Ohne Werte", nutrition: {} });
  pr("ohne kcal -> nur 'für 2'", k.meta === "für 2", k.meta);
} else pr("Kartenausschnitt (fuerAlle/meta) vorhanden", false);

console.log("--- 3. eingeplantMelden(): Toast beim Einplanen ---");
function text(wem){ return wem ? wem.charAt(0).toUpperCase() + wem.slice(1) + " eingeplant" : "Zum Plan hinzugefügt"; }
if (gibt("eingeplantMelden")) {
  // Genau das, was die fuenf Einplan-Stellen tun (Abschnitt 5 prueft, dass sie es tun).
  state.plan = leererPlan();
  state.plan.mon.mi.push(makeEntry("nudeln", [syncUid]));
  pr("neues Gericht in der Gruppe startet als 'nur ich'",
     JSON.stringify(state.plan.mon.mi) === '[{"id":"nudeln","uids":["ich"]}]', JSON.stringify(state.plan.mon.mi));
  eingeplantMelden("mon", "mi", text);
  pr("Zweiergruppe: 'Für dich eingeplant'", letzterToast === "Für dich eingeplant", letzterToast);
  pr("mit Knopf 'Für euch beide'", letzterUndo && letzterUndo.opts.label === "Für euch beide",
     letzterUndo ? letzterUndo.opts.label : "kein undoToast");

  gespeichert = 0;
  if (letzterUndo) letzterUndo.opts.fn && letzterUndo.opts.fn();
  pr("'Für euch beide' -> Eintrag fuer alle (String-Form)",
     JSON.stringify(state.plan.mon.mi) === '["nudeln"]', JSON.stringify(state.plan.mon.mi));
  pr("'Für euch beide' speichert", gespeichert === 1, String(gespeichert));

  // Rueckgaengig nimmt GENAU den neuen Eintrag, nicht einen aelteren desselben Gerichts.
  state.plan = leererPlan();
  state.plan.mon.mi = [{ id: "nudeln", uids: ["ich"] }, "salat"];
  state.plan.mon.mi.push(makeEntry("nudeln", [syncUid]));
  eingeplantMelden("mon", "mi", text);
  gespeichert = 0;
  if (letzterUndo) letzterUndo.undo();
  pr("'Rückgängig' entfernt den neuen Eintrag, nicht den gleichen aelteren",
     JSON.stringify(state.plan.mon.mi) === '[{"id":"nudeln","uids":["ich"]},"salat"]', JSON.stringify(state.plan.mon.mi));
  pr("'Rückgängig' speichert", gespeichert === 1, String(gespeichert));

  // Dreiergruppe
  groupMembers.push({ uid: "er", name: "Ben" });
  state.plan = leererPlan(); state.plan.mon.mi = [makeEntry("nudeln", [syncUid])];
  eingeplantMelden("mon", "mi", text);
  pr("Dreiergruppe: Knopf 'Für alle'", letzterUndo && letzterUndo.opts.label === "Für alle",
     letzterUndo ? letzterUndo.opts.label : letzterToast);
  groupMembers.pop();

  // Ohne Gruppe: makeEntry liefert die String-Form, es gibt niemanden zum Mitplanen.
  var g3 = syncGid, m3 = groupMembers; syncGid = null; groupMembers = [];
  state.plan = leererPlan(); state.plan.mon.mi = [makeEntry("nudeln", [syncUid])];
  pr("ohne Gruppe -> String-Form", JSON.stringify(state.plan.mon.mi) === '["nudeln"]', JSON.stringify(state.plan.mon.mi));
  eingeplantMelden("mon", "mi", text);
  pr("ohne Gruppe -> schlichter Toast", letzterToast === "Zum Plan hinzugefügt" && !letzterUndo, letzterToast);
  syncGid = g3; groupMembers = m3;

  // Woche gewechselt, bevor der Knopf gedrueckt wird: state.plan zeigt dann auf eine andere.
  state.plan = leererPlan(); state.plan.mon.mi = [makeEntry("nudeln", [syncUid])];
  eingeplantMelden("mon", "mi", text);
  var naechste = leererPlan(); naechste.mon.mi = [{ id: "nudeln", uids: ["ich"] }];
  state.viewWeek = "next"; state.plan = naechste;
  if (letzterUndo) letzterUndo.opts.fn && letzterUndo.opts.fn();
  pr("Wochenwechsel: 'Für euch beide' fasst die andere Woche nicht an",
     JSON.stringify(naechste.mon.mi) === '[{"id":"nudeln","uids":["ich"]}]', JSON.stringify(naechste.mon.mi));
  if (letzterUndo) letzterUndo.undo();
  pr("Wochenwechsel: 'Rückgängig' auch nicht", naechste.mon.mi.length === 1, JSON.stringify(naechste.mon.mi));
  state.viewWeek = "current";
} else pr("eingeplantMelden() existiert", false);

console.log("--- 4. persAusGruppe(): 'Wie eure Gruppe' in der Einkaufsliste ---");
if (gibt("persAusGruppe")) {
  state.shopPersons = 1;
  pr("Gruppe, nichts eingestellt -> Hinweis", persAusGruppe() === true);
  state.shopPersons = 3;
  pr("von Hand 3 -> kein Hinweis", persAusGruppe() === false);
  state.shopPersons = 1;
  gruppenEinstellungen.shopForAll = false;
  pr("'Einkauf für alle rechnen' Aus -> kein Hinweis", persAusGruppe() === false);
  gruppenEinstellungen.shopForAll = true;
  var g4 = syncGid; syncGid = null;
  pr("ohne Gruppe -> kein Hinweis", persAusGruppe() === false);
  syncGid = g4;
} else pr("persAusGruppe() existiert", false);

console.log("--- 6. openAssignMenu() bei zwei Personen ---");
if (gibt("openAssignMenu")) {
  function menueOeffnen(eintrag) {
    state.plan = leererPlan(); state.plan.mon.mi = [eintrag];
    var b = document.createElement("button"); b.dataset.slotSrc = "mon:mi:0";
    document.body.appendChild(b);
    gerendert = 0;
    openAssignMenu(b);
    return document.querySelector(".assign-menu");
  }
  var menu = menueOeffnen({ id: "nudeln", uids: ["ich"] });
  pr("ein Tipp oeffnet ein Menue (kein stummer Zyklus)", !!menu && gerendert === 0,
     menu ? "gerendert=" + gerendert : "kein Menue, Plan: " + JSON.stringify(state.plan.mon.mi));
  var radio = menu ? [].map.call(menu.querySelectorAll('[role="menuitemradio"]'), function(x){ return x.textContent.trim(); }) : [];
  pr("drei feste Wahlen", JSON.stringify(radio) === JSON.stringify(["Für euch beide", "PNur ich", "ANur Anna"]), JSON.stringify(radio));
  if (radio.length === 3) {
    var an = menu.querySelector('[aria-checked="true"]');
    pr("'Nur ich' ist markiert", !!an && an.dataset.wahl === "ich" && an.classList.contains("on"), an ? an.dataset.wahl : "keine");
    gespeichert = 0;
    menu.querySelector('[data-wahl="alle"]').click();
    pr("'Für euch beide' -> fuer alle", JSON.stringify(state.plan.mon.mi) === '["nudeln"]', JSON.stringify(state.plan.mon.mi));
    pr("... gespeichert und Menue zu", gespeichert === 1 && !document.querySelector(".assign-menu"), String(gespeichert));

    menu = menueOeffnen("nudeln");
    var an2 = menu.querySelector('[aria-checked="true"]');
    pr("bei 'fuer alle' ist 'Für euch beide' markiert", !!an2 && an2.dataset.wahl === "alle", an2 ? an2.dataset.wahl : "keine");
    menu.querySelector('[data-wahl="du"]').click();
    pr("'Nur Anna' -> nur ihr", JSON.stringify(state.plan.mon.mi) === '[{"id":"nudeln","uids":["du"]}]', JSON.stringify(state.plan.mon.mi));

    menu = menueOeffnen("nudeln");
    menu.querySelector('[data-wahl="ich"]').click();
    pr("'Nur ich' -> nur mir", JSON.stringify(state.plan.mon.mi) === '[{"id":"nudeln","uids":["ich"]}]', JSON.stringify(state.plan.mon.mi));
  }
  var offen = document.querySelector(".assign-menu"); if (offen) offen.remove();
  // Ab drei Personen bleibt die Mehrfachauswahl.
  groupMembers.push({ uid: "er", name: "Ben" });
  menu = menueOeffnen("nudeln");
  pr("Dreiergruppe: weiter Mehrfachauswahl", !!menu && !menu.querySelector("[data-wahl]") && menu.querySelectorAll("[data-uid]").length === 3,
     menu ? menu.innerHTML.slice(0, 80) : "kein Menue");
  if (menu) menu.remove();
  groupMembers.pop();
} else pr("openAssignMenu() existiert", false);

console.log("");
console.log("ERGEBNIS " + ok + " gruen, " + bad + " rot");
"""


def einplanstellen(text):
    u"""Abschnitt 5, statisch: Jede Stelle, die von Hand einplant, legt seit dem 07.10.2026
    `push(makeEntry(…, [syncUid]))` an - "nur ich" - und meldet innerhalb der naechsten
    sechs Zeilen ueber eingeplantMelden(). Eine Stelle, die noch nach dem alten Muster
    `push(slotIsShared(day, meal) ? …` fragt, zaehlt als rot.

    quickAddPiece() ist die Ausnahme: Es meldet nicht selbst, sein Aufrufer tut es. Dafuer
    wird geprueft, dass JEDER Aufrufer von quickAddPiece() meldet. Der Auto-Planer steht
    nicht im Muster (er hat seinen eigenen Toast mit "Nochmal") und bleibt aussen vor.
    """
    zeilen = text.split(u"\n")
    funde, ohne, alt = 0, [], []
    in_piece = False
    for i, z in enumerate(zeilen):
        if u"function quickAddPiece(" in z:
            in_piece = True
        elif in_piece and re.match(r"^  \}", z):
            in_piece = False
        if z.strip().startswith(u"//"):
            continue
        if u"push(slotIsShared(day, meal)" in z:
            alt.append(i + 1)
            continue
        if in_piece or not re.search(r"state\.plan\[day\]\[meal\]\.push\(makeEntry\([\w.]+, \[syncUid\]\)\)", z):
            continue
        funde += 1
        if not any(u"eingeplantMelden(" in n for n in zeilen[i + 1:i + 7]):
            ohne.append(i + 1)
    for i, z in enumerate(zeilen):
        if u"quickAddPiece(day, meal" in z and u"function " not in z:
            funde += 1
            if not any(u"eingeplantMelden(" in n for n in zeilen[i + 1:i + 4]):
                ohne.append(i + 1)
    return funde, ohne, alt


def zeile(zeilen, marker):
    u"""Genau die eine Zeile mit `marker` - fuer die Einzeiler-Helfer."""
    t = next((l for l in zeilen if marker in l), None)
    if t is None:
        FEHLT.append(marker)
        return u""
    return t


def main():
    text = pm_quelle.lade_seite(INDEX)
    quelle = text.split(u"\n")

    # Bis einschliesslich makeEntry(). Am alten Stand endete der Block mit slotIsShared() -
    # das Ende des Schnitts ist deshalb die schliessende Klammer von makeEntry().
    helfer = schneide(quelle, u"function asIdList(v)", u"return { id: id, uids: uids.slice() };", u"\n  }")
    shopsan = zeile(quelle, u"function sanitizeShopPersons(v)")
    zaehlt = schneide(quelle, u"function shopCountsMembers()",
                      u"return !!(syncGid && groupSetting", u"\n  }")
    portionen = schneide(quelle, u"function gruppenPortionen()",
                         u"return syncGid && groupMembers.length > 1", u"\n  }")
    ausgruppe = schneide(quelle, u"function persAusGruppe()",
                         u"return shopCountsMembers() && sanitizeShopPersons", u"\n  }")
    melden = schneide(quelle, u"function eingeplantMelden(day, meal, text)",
                      u"ms: 8000", u"\n    });\n  }")
    # Die Karte wird nicht als ganze renderPlan() gefahren - nur die Zeilen, die Metazeile
    # und Titel bilden. grp/uids/r kommen als Parameter, wie in der Kartenschleife.
    kartenteil = schneide(quelle, u"const fuerAlle = grp === 0", u".map((t, i) => `<span>")
    karte = (u"function karte(grp, uids, r) {\n" + kartenteil +
             u"\n  return { meta: meta.replace(/<[^>]+>/g, ''), roh: meta, assignNote: assignNote," +
             u" badge: typeof badge === 'undefined' ? null : badge };\n}") if kartenteil else u""
    # openAssignMenu() bis zur ersten Zeile, die nur "  }" ist - das Funktionsende.
    a = next((i for i, l in enumerate(quelle) if u"function openAssignMenu(btn)" in l), None)
    b = None if a is None else next((i for i, l in enumerate(quelle) if i > a and l.rstrip() == u"  }"), None)
    menue = u""
    if a is None or b is None:
        FEHLT.append(u"function openAssignMenu(btn)")
    else:
        menue = u"\n".join(quelle[a:b + 1])

    funde, ohne, alt = einplanstellen(text)

    tmp = tempfile.mkdtemp(prefix="mp-fueralle-")
    try:
        seite = os.path.join(tmp, "pruefstand.html")
        fehlt_js = u"var FEHLT = %s;" % (u"[" + u",".join(u'"%s"' % f.replace(u'"', u"'") for f in FEHLT) + u"]")
        io.open(seite, "w", encoding="utf-8").write(
            # <body> vor dem Script: Abschnitt 6 haengt das Menue an document.body.
            u"<!doctype html><meta charset='utf-8'><body><script>\n" + fehlt_js + u"\n" + UMFELD + u"\n" + helfer + u"\n" + shopsan +
            u"\n" + zaehlt + u"\n" + portionen + u"\n" + ausgruppe + u"\n" + melden +
            u"\n" + karte + u"\n" + menue + u"\n" + TEST + u"\n</script>")
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
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        for z in zeilen:
            if not z.startswith("ERGEBNIS"):
                print(z)

        print(u"--- 5. Alle Einplan-Stellen von Hand melden ueber eingeplantMelden() ---")
        rot5 = 0
        if funde < 5:
            print(u"  FAIL nur %d Einplan-Stellen gefunden (erwartet mindestens 5)" % funde)
            rot5 += 1
        else:
            print(u"  OK   %d Einplan-Stellen gefunden" % funde)
        if ohne:
            print(u"  FAIL ohne eingeplantMelden(): Zeile %s" % u", ".join(str(z) for z in ohne))
            rot5 += 1
        else:
            print(u"  OK   jede meldet ueber eingeplantMelden()")
        if alt:
            print(u"  FAIL noch 'fuer alle' als Start (slotIsShared): Zeile %s" % u", ".join(str(z) for z in alt))
            rot5 += 1
        else:
            print(u"  OK   keine Stelle startet mehr mit 'fuer alle'")

        m = re.match(r"ERGEBNIS (\d+) gruen, (\d+) rot", letzte[-1]) if letzte else None
        if not m:
            print(u"Kein ERGEBNIS - das Script brach vorher ab.")
            return 1
        gruen = int(m.group(1)) + (3 - rot5)
        rot = int(m.group(2)) + rot5
        print(u"")
        print(u"ERGEBNIS %d gruen, %d rot" % (gruen, rot))
        return 0 if rot == 0 else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
