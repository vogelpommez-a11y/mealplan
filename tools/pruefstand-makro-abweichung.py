# -*- coding: utf-8 -*-
u"""
Ausschneide-Pruefstand: Gilt ein frisch uebernommenes Katalogrezept als "manuell angepasst"?

Befund vom 24.09.2026 (docs/TROUBLESHOOTING.md 179): Das Rezeptbuch speichert Makros
ganzzahlig, die Zutatensumme hat eine Nachkommastelle (76 gegen 76,1 KH). macroWeichtAb()
verglich mit `!==` und hielt deshalb JEDES der 36 Katalogrezepte gleich nach dem Uebernehmen
fuer von Hand uebersteuert - eine geaenderte Zutatenmenge rechnete die Makros nicht mehr nach.

Geprueft wird der echte macroWeichtAb() samt ingSummeAus() und ihren Helfern, ausgeschnitten
aus index.html. Die Katalogrezepte kommen ungefiltert aus data/cookbook.js: Der Katalog traegt
kein `portions`, copyFromCookbook() -> sanitizeRecipe() laesst Zutaten und Makros also so, wie
sie sind.

GEGENPROBE: Dieselben Pruefungen laufen gegen macroWeichtAb() aus Commit ALT (vor dem Fix,
aus Git gelesen, nicht nachgebaut). Dort MUSS der Katalog als uebersteuert gelten - sonst misst
dieser Pruefstand nicht den Fehler, den er zu messen vorgibt.

    python tools/pruefstand-makro-abweichung.py
"""
import io, json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WURZEL, "tools", "pruefstand-makro-abweichung.html")
# Letzter Stand VOR dem Fix. Fest verdrahtet, nicht HEAD: nach dem Commit enthielte HEAD
# den Fix, und die Gegenprobe vergliche den neuen Stand mit sich selbst.
ALT = "96e71ff"


def schnitt(zeilen, sig, einzug):
    u"""Funktion ab `sig` bis zur schliessenden Klammer auf derselben Einrueckung."""
    for i, z in enumerate(zeilen):
        if z.startswith(einzug + sig):
            if z.rstrip().endswith("}") and z.count("{") == z.count("}"):
                return z
            for j in range(i + 1, len(zeilen)):
                if zeilen[j].rstrip() == einzug + "}":
                    return "\n".join(zeilen[i:j + 1])
            raise SystemExit("KEIN ENDE: " + sig)
    raise SystemExit("NICHT GEFUNDEN: " + sig)


def teile(text):
    z = text.split("\n")
    oben = [schnitt(z, s, "  ") for s in (
        "const ING_UNITS = ", "function nutNum(", "function addNut(", "function ingUnit(",
        "function ingObj(", "function ingHasNut(", "function ingContrib(")]
    innen = [schnitt(z, s, "    ") for s in ("function ingSummeAus(", "function macroWeichtAb(")]
    # macroWeichtAb() liest `initial` aus dem Meal-Blatt - hier als Parameter der Fabrik.
    return "\n".join(oben) + "\nreturn function (initial) {\n" + "\n".join(innen) + \
        "\nreturn macroWeichtAb;\n};"


neu = io.open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
alt = subprocess.check_output(["git", "show", ALT + ":index.html"], cwd=WURZEL).decode("utf-8")
katalog = io.open(os.path.join(WURZEL, "data", "cookbook.js"), encoding="utf-8").read()

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Makro-Abweichung</title>
<pre id="log"></pre>
<script>
window.onerror = function (m, s, z) {
  document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
  return true;
};
</script>
<script>
%(katalog)s
</script>
<script>
var NEU = (function () { %(neu)s })();
var ALT = (function () { %(alt)s })();
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
function weicht(fabrik, r, nutrition) {
  var m = { nutrition: nutrition || r.nutrition, ingredients: r.ingredients };
  return fabrik(m)(r.ingredients);
}
function plus(n, feld, d) { var o = JSON.parse(JSON.stringify(n)); o[feld] += d; return o; }

var kat = COOKBOOK.filter(function (r) { return r.nutrition && r.ingredients && r.ingredients.length; });
LOG.push("Katalog: " + kat.length + " Rezepte mit Zutaten");

// --- Neuer Stand ---------------------------------------------------------
var neuFalsch = kat.filter(function (r) { return weicht(NEU, r); }).map(function (r) { return r.id; });
pruef("NEU: kein Katalogrezept gilt nach dem Uebernehmen als manuell angepasst",
      neuFalsch.length === 0, neuFalsch.join(", "));
var probe = kat[0];
pruef("NEU: echte Handaenderung +40 kcal wird erkannt", weicht(NEU, probe, plus(probe.nutrition, "kcal", 40)));
pruef("NEU: +1 kcal wird erkannt", weicht(NEU, probe, plus(probe.nutrition, "kcal", 1)));
pruef("NEU: +1 g Protein wird erkannt", weicht(NEU, probe, plus(probe.nutrition, "protein", 1)));
pruef("NEU: +0,6 g Fett wird erkannt (knapp ueber der Grenze)", weicht(NEU, probe, plus(probe.nutrition, "fat", 0.6)));
pruef("NEU: ohne gespeicherte Makros gilt nichts als uebersteuert",
      NEU({ nutrition: null })(probe.ingredients) === false);

// --- Gegenprobe gegen den alten Stand -----------------------------------
var altFalsch = kat.filter(function (r) { return weicht(ALT, r); }).length;
pruef("GEGENPROBE ALT (%(alt_id)s): der Fehler ist dort messbar (" + altFalsch + " von " + kat.length + " gelten als angepasst)",
      altFalsch > 0);
pruef("GEGENPROBE ALT: Handaenderung wird dort ebenfalls erkannt",
      weicht(ALT, probe, plus(probe.nutrition, "kcal", 40)));

LOG.push(bad ? "FEHLGESCHLAGEN: " + bad + " von " + (ok + bad) : "ALLE " + ok + " PRUEFUNGEN GRUEN");
document.getElementById("log").textContent = LOG.join("\\n");
</script>
""" % {"katalog": katalog, "neu": teile(neu), "alt": teile(alt), "alt_id": ALT}

io.open(OUT, "w", encoding="utf-8").write(seite)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(OUT))
