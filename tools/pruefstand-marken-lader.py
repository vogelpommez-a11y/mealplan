# Ausschneide-Pruefstand Marken-Lader (17.10.2026): markenLader() / markenKarteHtml() /
# markenLaderHtml() aus index.html, nichts abgetippt. Gestubbt sind nur appEl, MOTION, esc,
# toast und reducedMotion - Randstuecke, an denen der Lader nur anfasst.
#
# Er misst das VERHALTEN, nicht das Aussehen (dafuer tools/probe-marken-lader.html und die
# Vergleichsseite):
#   * ein Schritt zur Zeit, und nur der ist fuer Screenreader da (aria-hidden)
#   * Haken nur bei Erfolg, nicht bei "ohneHaken"
#   * Ueberspringen per Escape
#   * echtes Warten: Satz SICHTBAR (.da) - genau das war vor dem Push kaputt und fiel keiner
#     Sichtprobe auf, weil die .da von Hand setzte -, kein Aufflackern bei schnellen Antworten,
#     Fehler wird durchgereicht, und nach ML_ECHT_MAX_MS ist die App wieder frei
#
# Gegenprobe (17.10.2026), je EINZELN: ohne `if (echt) items[0].classList.add("da")` fiel
# "echt: der Satz ist sichtbar" durch (25/1); mit ausgeschaltetem Obergrenzen-Timer fielen die
# drei "haengt"-Pruefungen durch (23/3). NICHT ML_ECHT_MAX_MS hochsetzen: Dann wartet der Test
# selbst endlos und liefert gar kein Ergebnis statt eines roten.
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import quelle as pm_quelle

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "index.html")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pruefstand-marken-lader.html")
lines = pm_quelle.lade_seite(SRC).split("\n")


def schnitt(sig):
    start = None
    for i, z in enumerate(lines):
        if z.startswith(sig):
            start = i; break
    if start is None: raise SystemExit("NICHT GEFUNDEN: " + sig)
    for j in range(start + 1, len(lines)):
        if lines[j] == "  }": return "\n".join(lines[start:j + 1])
    raise SystemExit("KEIN ENDE: " + sig)


def zeile(sig):
    for z in lines:
        if z.startswith(sig): return z
    raise SystemExit("ZEILE NICHT GEFUNDEN: " + sig)


code = "\n\n".join([
    zeile("  const ML_SCHRITT_MS = "),
    zeile("  const ML_ECHT_ZEIGEN_MS = "),
    zeile("  const ML_LOGO = "),
    schnitt("  function markenKarteHtml("),
    schnitt("  function markenLaderHtml("),
    schnitt("  function markenLader("),
])

seite = u"""<!doctype html><meta charset="utf-8"><title>Pruefstand Marken-Lader</title>
<pre id="log"></pre>
<script>
var LOG = [], ok = 0, bad = 0;
window.onerror = function (m, s, z) { document.getElementById("log").textContent = "JS-FEHLER: " + m + " (Zeile " + z + ")"; };
function pruef(name, ist, soll) {
  var gut = JSON.stringify(ist) === JSON.stringify(soll);
  if (gut) ok++; else bad++;
  LOG.push((gut ? "OK   " : "FEHL ") + name + (gut ? "" : "  ist=" + JSON.stringify(ist) + " soll=" + JSON.stringify(soll)));
  document.getElementById("log").textContent = LOG.join("\\n");
}
// ---- Randstuecke ----
var appEl = document.createElement("div"); document.body.appendChild(appEl);
var MOTION = { base: "200ms" };
function esc(s) { return String(s == null ? "" : s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
var toasts = [];
function toast(t) { toasts.push(t); }
function reducedMotion() { return false; }

__CODE__

function warte(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
// Lebenszeichen: Der Laeufer (pruefstand_lauf.py) beendet einen Pruefstand, dessen Protokoll
// sich 1,5 s nicht aendert - gewollt, als Schutz gegen Haenger. Wer laenger wartet, meldet
// sich deshalb jede Sekunde; die Zeile verschwindet danach wieder.
async function warteLebendig(ms) {
  var el = document.getElementById("log");
  for (var t = 0; t < ms; t += 1000) {
    el.textContent = LOG.join("\\n") + "\\n  ... wartet (" + Math.round(t / 1000) + " s)";
    await warte(Math.min(1000, ms - t));
  }
  el.textContent = LOG.join("\\n");
}
function karte() { return document.querySelector(".ml-overlay"); }
function schritte() { return [].slice.call(document.querySelectorAll(".ml-overlay .ml-schritt")); }
function sichtbar() { return schritte().map(function (s) { return s.classList.contains("da"); }); }
function vorlesbar() { return schritte().map(function (s) { return !s.hasAttribute("aria-hidden"); }); }

(async function () {
  // ---- inszeniert: ein Schritt zur Zeit ----
  var fertig = false;
  var p = markenLader({ schritte: [["A", "1"], ["B", "2"], ["C", "3", "ohneHaken"]] }).then(function () { fertig = true; });
  await warte(60);
  pruef("inszeniert: Karte liegt ueber der App", !!karte(), true);
  pruef("inszeniert: App ist gesperrt (inert)", appEl.inert, true);
  pruef("inszeniert: nur Schritt 1 sichtbar", sichtbar(), [true, false, false]);
  pruef("inszeniert: nur Schritt 1 vorlesbar", vorlesbar(), [true, false, false]);
  await warte(ML_SCHRITT_MS);
  pruef("nach einem Takt: nur Schritt 2 sichtbar", sichtbar(), [false, true, false]);
  pruef("nach einem Takt: nur Schritt 2 vorlesbar", vorlesbar(), [false, true, false]);
  await warte(ML_SCHRITT_MS * 2);   // jetzt kurz nach dem Ende der Dauer, vor dem Schliessen
  pruef("ohneHaken: der letzte Schritt bekommt keinen Haken", schritte()[2].classList.contains("fertig"), false);
  await p;
  pruef("inszeniert: Promise erfuellt", fertig, true);
  pruef("inszeniert: Karte weg", !!karte(), false);
  pruef("inszeniert: App wieder frei", appEl.inert, false);

  // ---- Haken bei Erfolg ----
  p = markenLader({ schritte: [["A", "1"], ["B", "2"]] });
  await warte(ML_SCHRITT_MS * 2 + 50);
  pruef("Erfolg: der letzte Schritt bekommt den Haken", schritte()[1].classList.contains("fertig"), true);
  await p;

  // ---- Ueberspringen ----
  var t0 = Date.now();
  p = markenLader({ schritte: [["A", "1"], ["B", "2"], ["C", "3"]] });
  await warte(100);
  document.dispatchEvent(new KeyboardEvent("keydown", { key: "Escape", bubbles: true }));
  await p;
  pruef("Escape ueberspringt (weit vor dem Ende)", Date.now() - t0 < ML_SCHRITT_MS * 2, true);

  // ---- echt: sichtbar, ohne Aufflackern, Fehler, Obergrenze ----
  var lang = markenLader({ text: "Du trittst bei", warten: warte(900).then(function () { return 42; }) });
  await warte(ML_ECHT_ZEIGEN_MS + 50);
  pruef("echt: Karte erscheint", !!karte(), true);
  pruef("echt: der Satz ist sichtbar", sichtbar(), [true]);
  pruef("echt: und vorlesbar", vorlesbar(), [true]);
  pruef("echt: Ergebnis wird durchgereicht", await lang, 42);
  pruef("echt: danach Karte weg", !!karte(), false);

  var schnell = markenLader({ text: "x", warten: warte(40) });
  await warte(ML_ECHT_ZEIGEN_MS + 30);
  pruef("echt schnell: kein Aufflackern (Karte erscheint gar nicht)", !!karte(), false);
  await schnell;

  var fehler = null;
  await markenLader({ text: "x", warten: warte(300).then(function () { throw new Error("weg"); }) })
    .catch(function (e) { fehler = e.message; });
  pruef("echt: Fehler wird durchgereicht", fehler, "weg");
  pruef("echt: nach Fehler App frei", appEl.inert, false);

  toasts = [];
  markenLader({ text: "haengt", warten: new Promise(function () {}) });
  await warteLebendig(ML_ECHT_MAX_MS + 600);
  pruef("haengt: Karte weg nach der Obergrenze", !!karte(), false);
  pruef("haengt: App wieder frei", appEl.inert, false);
  pruef("haengt: ein Hinweis sagt es", toasts.length === 1 && toasts[0].indexOf("Hintergrund") !== -1, true);

  // ---- im Inhalt ----
  var box = document.createElement("div"); box.innerHTML = markenLaderHtml("Deine Meals");
  pruef("im Inhalt: dieselbe Karte", !!box.querySelector(".ml-karte .ml-buehne .ml-schritt"), true);
  pruef("im Inhalt: Satz sichtbar und vorlesbar",
    [box.querySelector(".ml-schritt").classList.contains("da"), !box.querySelector(".ml-schritt").hasAttribute("aria-hidden")], [true, true]);
  pruef("im Inhalt: escaped", (function () { var b = document.createElement("div"); b.innerHTML = markenLaderHtml("<b>x</b>"); return !b.querySelector(".ml-wert b"); })(), true);

  LOG.push("");
  LOG.push(bad ? ("FEHLGESCHLAGEN: " + bad + " von " + (ok + bad)) : ("ALLE " + ok + " PRUEFUNGEN GRUEN"));
  document.getElementById("log").textContent = LOG.join("\\n");
})();
</script>
"""
io.open(OUT, "w", encoding="utf-8").write(seite.replace("__CODE__", code))
print("geschrieben")

if __name__ == "__main__":
    from pruefstand_lauf import fahren
    # Zeitbudget ueber der Obergrenze ML_ECHT_MAX_MS (12 s) plus alle anderen Wartezeiten.
    sys.exit(fahren(OUT, zeitbudget=40000))
