# -*- coding: utf-8 -*-
u"""
Ausschneide-Pruefstand: Raeumt "Alle Daten loeschen" wirklich alles weg, was die App ablegt?

Befund der Rechtspruefung vom 17.10.2026 (🟡 4): Ziffer 10 der Datenschutzerklaerung sagt
"saemtliche auf diesem Geraet gespeicherten Daten" zu, wipeLocalData() liess aber
`wochenkueche_theme_v1` (Hell/Dunkel) und `wochenkueche_intro_v1` (Erst-Intro gesehen) stehen.
Seit 18.10.2026 raeumt es beide mit. Die beiden IndexedDBs des Firebase-SDK bleiben bewusst
(docs/ARCHITECTURES.md, "wipeLocalData() deckt beide Speicher ab").

Geprueft wird der echte wipeLocalData() samt der echten Schluessel-Konstanten, ausgeschnitten
aus index.html, gegen einen echten localStorage (headless Edge, file://). Gestubbt sind nur die
Randstuecke: idbRW (Meal-Fotos), CloudSync.wipeCache (Firestore-Cache), noteError.

Seit 19.10.2026 zusaetzlich (stille Fehler, plans/abgleich-pruefer-2026-10-18.md L8): Laesst
sich der Fotospeicher nicht leeren, muss wipeLocalData() das zurueckmelden (true) - sonst meldet
die App "geloescht", obwohl die Fotos auf dem Geraet bleiben. Werfen darf es dafuer NICHT (ein Wurf
hielt den Reload auf, Pushcheck 19.10.2026). Laesst sich die Datenbank gar nicht oeffnen, gab es
dort keine Fotos: false.

GEGENPROBE: Dieselben Pruefungen laufen gegen wipeLocalData() aus Commit ALT (vor dem Fix, aus
Git gelesen). Dort MUESSEN Theme und Intro-Merker stehen bleiben, und ein Fotofehler wird dort
verschluckt.

    python tools/pruefstand-daten-loeschen.py
"""
import io, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(WURZEL, "tools", "pruefstand-daten-loeschen.html")
# Letzter Stand VOR dem Fix. Fest verdrahtet, nicht HEAD (sonst vergliche die Gegenprobe nach
# dem Commit den neuen Stand mit sich selbst).
ALT = "9b0cc8f"
SCHLUESSEL = ("STORE_KEY", "PROFILE_KEY", "LAST_KEY", "SHOP_DONE_KEY", "LETZTE_UID_KEY",
              "PLAN_BASE_KEY", "THEME_KEY", "SPLASH_INTRO_KEY")


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


def zeile(zeilen, sig):
    u"""Einzeilige Deklaration ab `sig` (Konstanten enden auf `;`, nicht auf `}`)."""
    for z in zeilen:
        if z.startswith("  " + sig):
            return z
    raise SystemExit("NICHT GEFUNDEN: " + sig)


def teile(text):
    z = text.split("\n")
    stuecke = [schnitt(z, "function localKey(", "  ")]
    stuecke += [zeile(z, "const %s = " % k) for k in SCHLUESSEL]
    stuecke.append(schnitt(z, "async function wipeLocalData(", "  "))
    # Randstuecke: zaehlen nur mit, damit sichtbar bleibt, dass beide Speicher drankommen.
    rand = u"""
  var AUFRUFE = { idb: 0, cache: 0 };
  var STEUER = { idbFehler: false, dbOffen: true };
  var idbOK = true;
  var datenGeloescht = false, SPERRE_BEI_IDB = null;
  function idbOpen() { return STEUER.dbOffen ? Promise.resolve({}) : Promise.reject(new Error("kein IndexedDB")); }
  function isTestOrigin() { return false; }
  function noteError() {}
  function idbRW(fn) {
    AUFRUFE.idb++;
    SPERRE_BEI_IDB = datenGeloescht;   // ist save() schon gesperrt, wenn die erste Wartezeit beginnt?
    if (STEUER.idbFehler) return Promise.reject(new Error("Fotospeicher gesperrt"));
    fn({ clear: function () {} }); return Promise.resolve();
  }
  var planBase = {}, imgSaved = new Map();
  var window = { CloudSync: { wipeCache: function () { AUFRUFE.cache++; return Promise.resolve(); } } };
"""
    keys = ", ".join("%s: %s" % (k, k) for k in SCHLUESSEL)
    return rand + "\n".join(stuecke) + \
        "\nreturn { wipe: wipeLocalData, aufrufe: AUFRUFE, steuer: STEUER, keys: { %s },\n" \
        "  sperreBeiIdb: function () { return SPERRE_BEI_IDB; } };" % keys


neu = io.open(os.path.join(WURZEL, "index.html"), encoding="utf-8").read()
alt = subprocess.check_output(["git", "show", ALT + ":index.html"], cwd=WURZEL).decode("utf-8")

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Daten loeschen</title>
<pre id="log"></pre>
<script>
window.onerror = function (m, s, z) {
  document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")";
  return true;
};
</script>
<script>
var NEU = (function () { %(neu)s })();
var ALT = (function () { %(alt)s })();
var LOG = [], ok = 0, bad = 0;
function pruef(name, bedingung, zusatz) {
  if (bedingung) { ok++; LOG.push("  OK      " + name); }
  else { bad++; LOG.push("  FEHLER  " + name + (zusatz ? "  ->  " + zusatz : "")); }
}
function befuellen(k) {
  localStorage.clear();
  Object.keys(k.keys).forEach(function (n) { localStorage.setItem(k.keys[n], "x"); });
  localStorage.setItem("fremd_ohne_app_bezug", "bleibt");
}
function uebrig() {
  var r = [];
  for (var i = 0; i < localStorage.length; i++) r.push(localStorage.key(i));
  return r.filter(function (n) { return n.indexOf("wochenkueche_") === 0; }).sort();
}

(async function () {
  // --- Neuer Stand -------------------------------------------------------
  pruef("NEU: Theme-Schluessel heisst wochenkueche_theme_v1", NEU.keys.THEME_KEY === "wochenkueche_theme_v1");
  pruef("NEU: Intro-Schluessel heisst wochenkueche_intro_v1", NEU.keys.SPLASH_INTRO_KEY === "wochenkueche_intro_v1");
  befuellen(NEU);
  pruef("NEU: vorher liegen alle " + Object.keys(NEU.keys).length + " App-Schluessel", uebrig().length === Object.keys(NEU.keys).length, uebrig().join(", "));
  var normal = await NEU.wipe();
  pruef("NEU: ohne Fehler meldet es keine gebliebenen Fotos", normal === false, String(normal));
  pruef("NEU: danach liegt kein wochenkueche_-Schluessel mehr", uebrig().length === 0, uebrig().join(", "));
  pruef("NEU: Fotos (IndexedDB) wurden geleert", NEU.aufrufe.idb === 1);
  pruef("NEU: save() ist gesperrt, bevor die erste Wartezeit beginnt", NEU.sperreBeiIdb() === true, String(NEU.sperreBeiIdb()));
  pruef("NEU: Firestore-Cache wurde geleert", NEU.aufrufe.cache === 1);
  pruef("NEU: fremder Schluessel ohne App-Bezug bleibt unberuehrt", localStorage.getItem("fremd_ohne_app_bezug") === "bleibt");

  // --- Fotospeicher laesst sich nicht leeren -----------------------------
  async function ergebnis(k) {
    try { return { wurf: false, wert: await k.wipe() }; } catch (e) { return { wurf: true }; }
  }
  befuellen(NEU);
  NEU.steuer.idbFehler = true; NEU.steuer.dbOffen = true;
  var cacheVorher = NEU.aufrufe.cache;
  var e = await ergebnis(NEU);
  pruef("NEU: Fotofehler wirft NICHT (Reload darf nicht haengen)", !e.wurf);
  pruef("NEU: Fotofehler bei offener Datenbank meldet gebliebene Fotos", e.wert === true, JSON.stringify(e));
  pruef("NEU: trotz Fotofehler wird der Firestore-Cache geleert", NEU.aufrufe.cache === cacheVorher + 1);
  pruef("NEU: trotz Fotofehler ist der localStorage leer", uebrig().length === 0, uebrig().join(", "));
  NEU.steuer.dbOffen = false;
  e = await ergebnis(NEU);
  pruef("NEU: Datenbank laesst sich gar nicht oeffnen (privater Modus) - keine Fotos gemeldet", !e.wurf && e.wert === false, JSON.stringify(e));
  NEU.steuer.idbFehler = false; NEU.steuer.dbOffen = true;

  // --- Gegenprobe gegen den alten Stand ---------------------------------
  befuellen(ALT);
  await ALT.wipe();
  var rest = uebrig();
  pruef("GEGENPROBE ALT (%(alt_id)s): der Fehler ist dort messbar (Theme bleibt)", rest.indexOf("wochenkueche_theme_v1") >= 0, rest.join(", "));
  pruef("GEGENPROBE ALT: Intro-Merker bleibt dort", rest.indexOf("wochenkueche_intro_v1") >= 0, rest.join(", "));
  pruef("GEGENPROBE ALT: sonst raeumt der alte Stand dieselben Schluessel", rest.length === 2, rest.join(", "));
  pruef("GEGENPROBE ALT: dort ist save() waehrend des Loeschens offen", ALT.sperreBeiIdb() === false, String(ALT.sperreBeiIdb()));
  ALT.steuer.idbFehler = true;
  e = await ergebnis(ALT);
  pruef("GEGENPROBE ALT: Fotofehler wird dort verschluckt (meldet nichts)", !e.wurf && e.wert !== true, JSON.stringify(e));

  localStorage.clear();
  LOG.push(bad ? "FEHLGESCHLAGEN: " + bad + " von " + (ok + bad) : "ALLE " + ok + " PRUEFUNGEN GRUEN");
  document.getElementById("log").textContent = LOG.join("\\n");
})().catch(function (e) {
  document.getElementById("log").textContent = "JS-FEHLER: " + e;
});
</script>
""" % {"neu": teile(neu), "alt": teile(alt), "alt_id": ALT}

io.open(OUT, "w", encoding="utf-8").write(seite)

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    sys.exit(fahren(OUT))
