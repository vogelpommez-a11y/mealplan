# -*- coding: utf-8 -*-
u"""
Ausschneide-Pruefstand: Vorbereitung am Vortag ("Am Vortag: Auftauen", 21.10.2026).

Ein Meal traegt optional `vorab` - feste Schluessel aus VORAB_HINWEISE (auftauen, einweichen,
marinieren). Gewaehlt wird im Meal-Blatt in einer eigenen Chip-Zeile unter den Merkmalen;
die Startseite zeigt am Vortag "Für morgen auftauen · Chili", aber nur wenn morgen ein Meal
FUER MICH mit Hinweis eingeplant ist.

Geprueft wird echter, aus index.html ausgeschnittener Code:
  * sanitizeRecipe()/sanitizeVorab(): nur bekannte Schluessel, feste Reihenfolge, leer = weg
  * mealMetaEditHtml()/mealFlagsHtml(): Chip-Zeile und Anzeige im Nur-Lese-Zweig
  * mutateLocal()/sheetSig() aus openMealSheet(): Feld wird gesetzt/geloescht, Signatur aendert sich
  * der Klick-Selektor des Meal-Blatts trifft die neuen Chips
  * vorabFuerMorgen()/vorabHtml(): nur "meins", jedes Meal je Hinweis einmal, leer = nichts
  * weekGoalHtml() haengt die Zeile an (Sonntag -> morgenPlan der naechsten Woche kommt von dort)

GEGENPROBE gegen ALT (Stand vor der Aenderung, aus Git gelesen): Dort kommt ein fremder
`vorab`-Wert ungeprueft durch den Sanitizer, das Blatt hat keine Chips, und sheetSig() sieht
das Feld nicht. Faellt die Gegenprobe nicht durch, misst dieser Pruefstand nichts.

    python tools/pruefstand-vorab-hinweis.py
"""
import io, os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WURZEL, "tools", "pruefstand-vorab-hinweis.html")
# Letzter Stand VOR der Aenderung. Fest verdrahtet, nicht HEAD - nach dem Commit enthielte
# HEAD die Aenderung, und die Gegenprobe vergliche den neuen Stand mit sich selbst.
ALT = "10f4372"


def schnitt(zeilen, sig, einzug):
    u"""Deklaration ab `sig` bis zur schliessenden Klammer (`}` oder `];`) auf derselben Einrueckung."""
    for i, z in enumerate(zeilen):
        if z.startswith(einzug + sig):
            s = z.rstrip()
            if (s.endswith(";") or s.endswith("}")) and z.count("{") == z.count("}") and z.count("[") == z.count("]"):
                return z
            for j in range(i + 1, len(zeilen)):
                if zeilen[j].rstrip() in (einzug + "}", einzug + "];"):
                    return "\n".join(zeilen[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


def klick_selektor(text):
    m = re.search(r'const chip = e\.target\.closest\("([^"]+)"\);', text)
    if not m:
        raise SystemExit("KLICK-SELEKTOR NICHT GEFUNDEN")
    return m.group(1)


def teile(text, neu):
    z = text.split("\n")
    oben = ["const MEALS = ", "const RECIPE_TAGS = ", "const RECIPE_TAG_KEYS = ", "function tagLabel(",
            "function entryId(", "function entryUids(", "function canonValue(", "function canonJSON(",
            "function nutNum(", "function nutParse(", "function ingObj(", "function sanitizeTags(",
            "function sanitizeRecipe(", "function mealFlagsHtml(", "function mealMetaEditHtml("]
    if neu:
        oben += ["const VORAB_HINWEISE = ", "const VORAB_KEYS = ", "function sanitizeVorab(",
                 "function vorabFuerMorgen(", "function vorabHtml("]
    teile_oben = [schnitt(z, s, "  ") for s in oben]
    # Das Meal-Blatt: sheetSig() und mutateLocal() leben in openMealSheet() und lesen rec(),
    # node und collectIngs() aus dem Abschluss - hier Parameter der Fabrik.
    innen = [schnitt(z, s, "    ") for s in ("function sheetSig(", "function mutateLocal(")]
    wochen = schnitt(z, "function weekGoalHtml(", "  ")
    return {
        "oben": "\n".join(teile_oben),
        "blatt": "function (rec, node, collectIngs) {\n" + "\n".join(innen) +
                 "\nreturn { sheetSig: sheetSig, mutateLocal: mutateLocal };\n}",
        "selektor": klick_selektor(text),
        "haengt_an": "vorabHtml(morgenPlan, morgenKey)" in wochen,
    }


def modul(t, name):
    # Abhaengigkeiten, die mit `vorab` nichts zu tun haben, als schlichte Durchreiche:
    # safeImage/migrateCat/sanitizeIng beruehren das Feld nicht. syncUid/getRecipe/ICON_CLOCK
    # setzt der Test selbst. Alles andere ist ausgeschnitten.
    return u"""var %(name)s = (function () {
  var esc = PM.esc;
  var safeImage = function (v) { return v; }, migrateCat = function (c) { return c; },
      sanitizeIng = function (x) { return x; };
  var syncUid = null, REZ = {};
  var getRecipe = function (id) { return REZ[id] || null; };
  var ICON_CLOCK = "<svg></svg>";
%(oben)s
  return {
    sanitizeRecipe: sanitizeRecipe, mealFlagsHtml: mealFlagsHtml, mealMetaEditHtml: mealMetaEditHtml,
    vorabFuerMorgen: typeof vorabFuerMorgen === "function" ? vorabFuerMorgen : null,
    vorabHtml: typeof vorabHtml === "function" ? vorabHtml : null,
    blatt: (%(blatt)s),
    setze: function (uid, rez) { syncUid = uid; REZ = rez; }
  };
})();
""" % {"name": name, "oben": t["oben"], "blatt": t["blatt"]}


neu_text = io.open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
alt_text = subprocess.check_output(["git", "show", ALT + ":index.html"], cwd=WURZEL).decode("utf-8")
basis_js = io.open(os.path.join(WURZEL, "lib", "basis.js"), encoding="utf-8").read()
NEU, ALTT = teile(neu_text, True), teile(alt_text, False)

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Vorab-Hinweis</title>
<pre id="log"></pre>
<script>
window.onerror = function (m, s, z) {
  document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
  return true;
};
</script>
<script>
%(basis)s
</script>
<script>
%(neu)s
%(alt)s
var SEL_NEU = %(sel_neu)s, SEL_ALT = %(sel_alt)s;
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
function dom(html) { var d = document.createElement("div"); d.innerHTML = html; return d; }
// Ein Meal-Blatt mit genau den Feldern, die mutateLocal() liest - plus die echte Chip-Zeile.
function blatt(M, r) {
  return dom('<input id="f-name" value="' + PM.esc(r.name || "") + '"><input id="f-cat" value="Hauptgericht">'
    + '<input id="f-kcal"><input id="f-carbs"><input id="f-protein"><input id="f-fat"><textarea id="f-steps"></textarea>'
    + M.mealMetaEditHtml(r));
}
function json(x) { return JSON.stringify(x); }

// --- Sanitizer -------------------------------------------------------------
var s1 = NEU.sanitizeRecipe({ id: "x", name: "Chili", vorab: ["marinieren", "auftauen", "<img src=x>", 5, "auftauen"] });
pruef("Sanitizer: nur bekannte Schluessel, feste Reihenfolge, keine Doppel", json(s1.vorab) === json(["auftauen", "marinieren"]), json(s1.vorab));
pruef("Sanitizer: leere Liste -> Feld entfaellt", !("vorab" in NEU.sanitizeRecipe({ id: "x", vorab: [] })));
pruef("Sanitizer: Zeichenkette statt Liste -> Feld entfaellt", !("vorab" in NEU.sanitizeRecipe({ id: "x", vorab: "auftauen" })));
pruef("Sanitizer: Bestands-Meal ohne Feld bekommt keins", !("vorab" in NEU.sanitizeRecipe({ id: "x", name: "Alt" })));

// --- Meal-Blatt: Chips, Anzeige, Speichern ------------------------------------
var b = blatt(NEU, { name: "Chili", vorab: ["einweichen"] });
var chips = b.querySelectorAll("#f-vorab [data-vorab]");
pruef("Blatt: Zeile 'Am Vortag' mit drei Chips", chips.length === 3 && /Am Vortag/.test(b.innerHTML), chips.length);
pruef("Blatt: gesetzter Hinweis ist gedrueckt, die anderen nicht",
      b.querySelector("[data-vorab=einweichen]").getAttribute("aria-pressed") === "true"
      && b.querySelector("[data-vorab=auftauen]").getAttribute("aria-pressed") === "false");
pruef("Blatt: Beschriftungen Auftauen/Einweichen/Marinieren",
      Array.prototype.map.call(chips, function (c) { return c.textContent; }).join("|") === "Auftauen|Einweichen|Marinieren");
pruef("Klick-Selektor trifft die neuen Chips", !!b.querySelector("[data-vorab=auftauen]").closest(SEL_NEU));
pruef("Klick-Selektor trifft weiter die Merkmale", !!b.querySelector("[data-tag=vegan]").closest(SEL_NEU));
var nl = dom(NEU.mealFlagsHtml({ mealPrep: true, vorab: ["einweichen", "auftauen"] }));
pruef("Nur-Lese: eigene Zeile 'Am Vortag' mit Ueberschrift, Marken ohne Vorsilbe",
      nl.querySelector(".ms-vorab-h") && nl.querySelector(".ms-vorab-h").textContent === "Am Vortag"
      && Array.prototype.map.call(nl.querySelectorAll(".ms-vorab span"), function (s) { return s.textContent; }).join("|") === "Auftauen|Einweichen",
      nl.innerHTML);
pruef("Nur-Lese: 'Am Vortag' steht genau einmal", (nl.innerHTML.match(/Am Vortag/g) || []).length === 1);
pruef("Nur-Lese: Merkmale bleiben in ihrer eigenen Zeile", /Meal-Prep/.test(nl.querySelector(".mflags:not(.ms-vorab)").textContent));
pruef("Nur-Lese: ohne Merkmale und Hinweise keine leere Zeile", NEU.mealFlagsHtml({}) === "");

var ziel = { id: "x", name: "Chili" };
var b2 = blatt(NEU, ziel);
var fab = NEU.blatt(function () { return ziel; }, b2, function () { return []; });
// Erst einmal lesen, wie es das Blatt beim ersten Tippen tut - sonst vergliche die Signatur
// auch Felder (steps, nutrition ...), die das Testobjekt anfangs gar nicht traegt.
fab.mutateLocal();
var sig0 = fab.sheetSig();
b2.querySelector("[data-vorab=auftauen]").setAttribute("aria-pressed", "true");
b2.querySelector("[data-vorab=marinieren]").setAttribute("aria-pressed", "true");
fab.mutateLocal();
pruef("Speichern: gedrueckte Chips landen in r.vorab", json(ziel.vorab) === json(["auftauen", "marinieren"]), json(ziel.vorab));
pruef("Speichern: sheetSig aendert sich (Blatt wird nach dem Schliessen neu gezeichnet)", fab.sheetSig() !== sig0);
b2.querySelector("[data-vorab=auftauen]").setAttribute("aria-pressed", "false");
b2.querySelector("[data-vorab=marinieren]").setAttribute("aria-pressed", "false");
fab.mutateLocal();
pruef("Speichern: alles abgewaehlt -> Feld geloescht statt leer", !("vorab" in ziel));
pruef("Speichern: danach wieder dieselbe Signatur wie beim Oeffnen", fab.sheetSig() === sig0);

// --- Startseite ---------------------------------------------------------------
var REZ = {
  a: { id: "a", name: "Chili", vorab: ["auftauen"] },
  b: { id: "b", name: "Gulasch", vorab: ["marinieren", "auftauen"] },
  c: { id: "c", name: "Salat" },
  d: { id: "d", name: "Overnight <Oats>", vorab: ["einweichen", "unbekannt"] }
};
var morgen = { fr: ["d"], mi: ["a", { id: "b", uids: ["fremd"] }], ab: ["a", "c"], sn: [] };
NEU.setze("ich", REZ);
var z = NEU.vorabFuerMorgen({ di: morgen }, "di");
pruef("Startseite: fremd zugewiesenes Meal zaehlt nicht (Gulasch fehlt)",
      z.every(function (x) { return x.namen.indexOf("Gulasch") === -1; }), json(z));
var auft = z.filter(function (x) { return x.hinweis.key === "auftauen"; })[0];
pruef("Startseite: zweimal Chili am Tag = einmal auftauen", auft && json(auft.namen) === json(["Chili"]), json(auft && auft.namen));
pruef("Startseite: unbekannter Schluessel wird ignoriert, Reihenfolge wie VORAB_HINWEISE",
      json(z.map(function (x) { return x.hinweis.key; })) === json(["auftauen", "einweichen"]), json(z.map(function (x) { return x.hinweis.key; })));
NEU.setze(null, REZ);
var z2 = NEU.vorabFuerMorgen({ di: morgen }, "di");
var auft2 = z2.filter(function (x) { return x.hinweis.key === "auftauen"; })[0];
pruef("Startseite: ohne Konto zaehlt jeder Eintrag (Chili, Gulasch)", auft2 && json(auft2.namen) === json(["Chili", "Gulasch"]), json(auft2 && auft2.namen));
var h = NEU.vorabHtml({ di: morgen }, "di");
pruef("Startseite: Zeile 'Für morgen auftauen' erscheint", /Für morgen auftauen/.test(h));
pruef("Startseite: Namen werden maskiert", h.indexOf("<Oats>") === -1 && h.indexOf("&lt;Oats&gt;") !== -1);
pruef("Startseite: als Hinweis ausgezeichnet (role=note)", /role="note"/.test(h));
pruef("Startseite: ohne Hinweis morgen gar nichts", NEU.vorabHtml({ di: { fr: ["c"] } }, "di") === "");
pruef("Startseite: leerer Tag gar nichts", NEU.vorabHtml({}, "di") === "" && NEU.vorabHtml(null, "di") === "");
pruef("weekGoalHtml haengt die Zeile an (morgenPlan inkl. Sonntag -> naechste Woche)", %(haengt_neu)s);

// --- Gegenprobe gegen den alten Stand ----------------------------------------
var sa = ALTM.sanitizeRecipe({ id: "x", vorab: ["<img src=x>"] });
pruef("GEGENPROBE ALT (%(alt_id)s): fremder vorab-Wert kam dort ungeprueft durch", json(sa.vorab) === json(["<img src=x>"]), json(sa.vorab));
pruef("GEGENPROBE ALT: dort gibt es keine Chips 'Am Vortag'", !blatt(ALTM, { name: "x" }).querySelector("[data-vorab]"));
var zielA = { id: "x", name: "Chili" }, b3 = blatt(ALTM, zielA);
var fabA = ALTM.blatt(function () { return zielA; }, b3, function () { return []; });
var sigA = fabA.sheetSig(); zielA.vorab = ["auftauen"];
pruef("GEGENPROBE ALT: sheetSig sah das Feld dort nicht", fabA.sheetSig() === sigA);
pruef("GEGENPROBE ALT: weekGoalHtml hatte keine Zeile", !%(haengt_alt)s);

LOG.push(bad ? "FEHLGESCHLAGEN: " + bad + " von " + (ok + bad) : "ALLE " + ok + " PRUEFUNGEN GRUEN");
document.getElementById("log").textContent = LOG.join("\\n");
</script>
""" % {
    "basis": basis_js,
    "neu": modul(NEU, "NEU"), "alt": modul(ALTT, "ALTM"),
    "sel_neu": '"' + NEU["selektor"] + '"', "sel_alt": '"' + ALTT["selektor"] + '"',
    "haengt_neu": "true" if NEU["haengt_an"] else "false",
    "haengt_alt": "true" if ALTT["haengt_an"] else "false",
    "alt_id": ALT,
}

io.open(OUT, "w", encoding="utf-8").write(seite)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(OUT))
