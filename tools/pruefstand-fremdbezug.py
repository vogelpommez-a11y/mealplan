# -*- coding: utf-8 -*-
u"""
Pruefstand Fremdbezug: Behaelt die eigene Kopie nach dem Austritt fremde Kennungen?

ANLASS (01.10.2026, Rechtspruefung): Ziffer 10 sagt zu, beim Austritt und bei der
Kontoloeschung bleibe "das Gericht - ohne Hinweis darauf, von wem es stammt". Anonymisiert
wurde aber nur in groups/{gid}. Die private Kopie, die beim Austritt bzw. Aufloesen ins eigene
Konto geht, trug weiter `by` (UID des Anlegers) an jedem Meal und `uids` an jedem Planeintrag -
und dort erreichte sie keine spaetere Loeschung des anderen Kontos (TROUBLESHOOTING §183).

WAS ER PRUEFT - am ECHTEN, ausgeschnittenen Code:
  * ohneFremdbezug() nimmt `by` von jedem Meal, laesst alles andere stehen
  * Planeintraege: mir zugewiesen -> String-Form, nur anderen -> faellt weg,
    Objekt ohne uids -> String-Form, String bleibt String
  * Felder der Woche, die keine Slots sind, bleiben unberuehrt
  * die Eingaben werden NICHT veraendert (state darf nicht unter der Hand mitwandern)
  * hatFremdbezug() erkennt beides - und meldet bei sauberem Stand nichts (sonst schriebe
    jeder Login einen leeren Schreibvorgang)
  * Quelltext: leaveGroup() bereinigt die Kopie, startCloudSync() raeumt alte Kopien beim
    Laden auf - beides nur ausserhalb einer Gruppe

Aufrufe:
    python tools/pruefstand-fremdbezug.py
    python tools/pruefstand-fremdbezug.py alt/index.html   # Gegenprobe gegen alten Stand
"""
import io
import json
import os
import re
import subprocess
import sys
import tempfile

BASIS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(BASIS, "index.html")
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def schneide(text, name, art="function"):
    u"""Eine Deklaration im Wortlaut herausschneiden (Klammerbilanz). Fehlt sie: Befund."""
    if art == "function":
        m = re.search(r"\n\s*(?:async\s+)?function\s+" + re.escape(name) + r"\s*\(", text)
        if not m:
            return None
        i = text.index("{", m.start())
        tiefe, j = 0, i
        while j < len(text):
            if text[j] == "{":
                tiefe += 1
            elif text[j] == "}":
                tiefe -= 1
                if tiefe == 0:
                    return text[m.start():j + 1]
            j += 1
        return None
    m = re.search(r"\n\s*const\s+" + re.escape(name) + r"\s*=.*?\];", text, re.S)
    return m.group(0) if m else None


def ohne_kommentare(code):
    u"""Kommentare raus - sonst findet die Quelltextpruefung den eigenen Kommentar."""
    code = re.sub(r"/\*.*?\*/", " ", code, flags=re.S)
    return re.sub(r"//[^\n]*", " ", code)


FUNKTIONEN = ["ohneFremdbezug", "hatFremdbezug"]
KONSTANTEN = ["DAYS", "MEALS"]

PRUEFUNGEN = u"""
  var ICH = "uid-ich", B = "uid-b";
  var meals = [
    { id: "m1", name: "Lachs", by: B, nutrition: { kcal: 500 } },
    { id: "m2", name: "Skyr", by: ICH },
    { id: "m3", name: "Curry" }
  ];
  function woche() {
    var w = {}; DAYS.forEach(function (d) { w[d.key] = {}; MEALS.forEach(function (m) { w[d.key][m.key] = []; }); });
    return w;
  }
  var w = woche();
  var tag = DAYS[0].key, mz = MEALS[0].key, mz2 = MEALS[1].key;
  w[tag][mz] = ["m3", { id: "m1", uids: [ICH, B] }, { id: "m2", uids: [B] }, { id: "m9" }];
  w[tag][mz2] = [{ id: "m1", uids: [ICH] }];
  w.extra = { bleibt: true };
  var plans = { "2026-W40": w };
  var vorherM = JSON.stringify(meals), vorherP = JSON.stringify(plans);

  var r = ohneFremdbezug(meals, plans, ICH);
  pruef("by am fremden Meal entfernt",       "by" in r.recipes[0], false);
  pruef("by am eigenen Meal entfernt",       "by" in r.recipes[1], false);
  pruef("uebrige Felder bleiben",            JSON.stringify(r.recipes[0].nutrition) + r.recipes[0].name, '{"kcal":500}Lachs');
  pruef("Meal ohne by unveraendert",         r.recipes[2] === meals[2], true);
  pruef("Slot: mir + B -> String, nur B -> weg, ohne uids -> String",
        JSON.stringify(r.plans["2026-W40"][tag][mz]), '["m3","m1","m9"]');
  pruef("Slot: nur mir -> String",           JSON.stringify(r.plans["2026-W40"][tag][mz2]), '["m1"]');
  pruef("keine uids mehr irgendwo",          JSON.stringify(r.plans).indexOf("uids") === -1, true);
  pruef("keine fremde UID mehr irgendwo",    JSON.stringify(r).indexOf(B) === -1, true);
  pruef("Nicht-Slot-Feld der Woche bleibt",  JSON.stringify(r.plans["2026-W40"].extra), '{"bleibt":true}');
  pruef("Eingabe Meals unveraendert",        JSON.stringify(meals), vorherM);
  pruef("Eingabe Plaene unveraendert",       JSON.stringify(plans), vorherP);

  pruef("hatFremdbezug: by erkannt",         hatFremdbezug([{ id: "x", by: B }], {}), true);
  pruef("hatFremdbezug: uids erkannt",       hatFremdbezug([], plans), true);
  pruef("hatFremdbezug: sauber -> false",    hatFremdbezug(r.recipes, r.plans), false);
  pruef("hatFremdbezug: leer -> false",      hatFremdbezug([], {}), false);
  pruef("zweimal bereinigt = einmal",        JSON.stringify(ohneFremdbezug(r.recipes, r.plans, ICH)), JSON.stringify(r));
"""

SEITE = u"""<!doctype html><meta charset="utf-8"><title>Fremdbezug</title>
<pre id="raus">laeuft…</pre>
<script>
%(code)s
var ergebnisse = [];
function pruef(was, ist, soll) {
  ergebnisse.push({ was: was, ok: ist === soll, ist: String(ist), soll: String(soll) });
}
try {
%(pruefungen)s
} catch (e) {
  ergebnisse.push({ was: "Ausnahme: " + e.message, ok: false, ist: "-", soll: "-" });
}
document.getElementById("raus").textContent = JSON.stringify(ergebnisse);
</script>
"""


def bauen(quelle):
    teile, fehlend = [], []
    for name in KONSTANTEN:
        s = schneide(quelle, name, "const")
        (teile if s else fehlend).append(s or ("const " + name))
    for name in FUNKTIONEN:
        s = schneide(quelle, name, "function")
        (teile if s else fehlend).append(s or ("function " + name + "()"))
    return SEITE % {"code": "\n".join(teile), "pruefungen": PRUEFUNGEN}, fehlend


def fahren(html):
    ordner = tempfile.mkdtemp(prefix="fremdbezug-")
    seite = os.path.join(ordner, "pruefstand.html")
    io.open(seite, "w", encoding="utf-8").write(html)
    roh = subprocess.run(
        [EDGE, "--headless=new", "--disable-gpu", "--virtual-time-budget=4000",
         "--user-data-dir=" + os.path.join(ordner, "edge"), "--dump-dom",
         "file:///" + seite.replace("\\", "/")],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
    m = re.search(r'<pre id="raus">(.*?)</pre>', roh or "", re.S)
    if not m:
        return None
    text = m.group(1).replace("&quot;", '"').replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    try:
        return json.loads(text)
    except ValueError:
        return None


def quelltext(quelle):
    u"""Werden die Helfer an den beiden Stellen auch AUFGERUFEN? Liste der Befunde."""
    schief = []
    lg = schneide(quelle, "leaveGroup")
    if not lg:
        schief.append("leaveGroup: nicht gefunden")
    else:
        code = ohne_kommentare(lg)
        i = code.find("ohneFremdbezug(")
        j = code.find("state.recipes = keepRecipes")
        if i == -1:
            schief.append("leaveGroup: bereinigt die mitgenommene Kopie nicht (ohneFremdbezug fehlt)")
        elif j != -1 and i > j:
            schief.append("leaveGroup: bereinigt erst NACH dem Uebernehmen in den State")
    sc = schneide(quelle, "startCloudSync")
    if not sc:
        schief.append("startCloudSync: nicht gefunden")
    else:
        code = ohne_kommentare(sc)
        # Nur im Zweig OHNE Gruppe: Er beginnt mit loadRecipes(["users", uid]).
        k = code.find('loadRecipes(["users", uid])')
        rest = code[k:] if k != -1 else ""
        if k == -1:
            schief.append("startCloudSync: Zweig ohne Gruppe nicht gefunden")
        elif "hatFremdbezug(" not in rest or "ohneFremdbezug(" not in rest:
            schief.append("startCloudSync: raeumt alte Kopien beim Laden nicht auf")
        elif "ohneFremdbezug(" in code[:k]:
            schief.append("startCloudSync: bereinigt auch im Gruppenzweig - dort wird `by` gebraucht")
        elif not re.search(r'groupResult\s*===\s*"gone"\s*&&\s*hatFremdbezug\(', rest):
            # Der Zweig ohne Gruppe laeuft auch bei "error": Gruppe besteht, Abgleich scheiterte.
            # Dann steht dort der Gruppenstand aus dem Cache (Befund website-security 01.10.2026).
            schief.append('startCloudSync: bereinigt nicht nur bei groupResult === "gone" '
                          '- auch ein gescheiterter Gruppenabgleich wuerde umgeschrieben')
    return schief


def main():
    print("Pruefstand Fremdbezug")
    print("Quelle: " + os.path.relpath(INDEX, BASIS).replace("\\", "/"))
    print("")
    quelle = io.open(INDEX, encoding="utf-8").read()

    schief = quelltext(quelle)
    for e in schief:
        print("  FEHL  " + e)
    if not schief:
        print("  OK    leaveGroup() und startCloudSync() rufen die Bereinigung auf")

    html, fehlend = bauen(quelle)
    if fehlend:
        for f in fehlend:
            print("  FEHLT im Quelltext: " + f)
        print("")
        print("FEHLGESCHLAGEN: %d Baustein(e) nicht gefunden." % (len(fehlend) + len(schief)))
        return 1

    ergebnisse = fahren(html)
    if not ergebnisse:
        print("FEHLGESCHLAGEN: kein Messergebnis - Edge hat nichts geliefert.")
        return 1
    rot = len(schief)
    for e in ergebnisse:
        if e["ok"]:
            print("  OK    " + e["was"])
        else:
            rot += 1
            print("  FEHL  %s  ist=%r soll=%r" % (e["was"], e["ist"], e["soll"]))
    print("")
    gesamt = len(ergebnisse) + 1
    if rot:
        print("FEHLGESCHLAGEN: %d von %d" % (rot, gesamt))
        return 1
    print("ERGEBNIS %d Pruefungen gruen" % gesamt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
