# -*- coding: utf-8 -*-
u"""
Gemeinsamer Laeufer fuer die Pruefstaende, die ihr Protokoll in ein `#log`-Element schreiben.

WOZU DAS DA IST
---------------
Acht Pruefstaende ERZEUGTEN bis zum 28.08.2026 nur eine HTML-Datei, gaben
"geschrieben: ..." aus und endeten mit Rueckgabewert 0. `tools/alle-pruefstaende.py`
bewertet ausschliesslich den Rueckgabewert und meldete sie deshalb bei JEDEM Durchgang
gruen - ihre Zusagen liefen nur, wenn ein Mensch die Datei im Browser oeffnete. Ein Drittel
der Suite mass also nichts (docs/TROUBLESHOOTING.md 131).

DER ENTWURF: NICHT IN DIE PRUEFSTAENDE HINEINFASSEN
---------------------------------------------------
Alle acht teilen dieselbe Bauart: ein `<div id="log">`, in das eine `pruef()`-Funktion
Zeilen der Form "OK   ..." bzw. "FEHL ..." schreibt, und am Ende eine Zusammenfassung
("ALLE n PRUEFUNGEN GRUEN" oder "FEHLGESCHLAGEN: ...").

Statt acht Dateien umzubauen - und dabei acht Gelegenheiten zu schaffen, eine Zusage
versehentlich zu veraendern - haengt dieser Laeufer der ERZEUGTEN Seite einen Beobachter an.
Der wartet, bis das Protokoll steht, und schiebt es auf die Konsole. Die Pruefstaende selbst
bleiben unangetastet; im Browser geoeffnet verhalten sie sich unveraendert.

Aufruf am Ende eines Pruefstands:

    if __name__ == "__main__":
        import sys
        from pruefstand_lauf import fahren
        sys.exit(fahren(OUT))
"""
import io
import os
import re
import shutil
import subprocess
import tempfile

EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# Der Beobachter. Bewusst ohne Abhaengigkeit zum Pruefstand: Er liest nur `#log`, kennt
# dessen Aufbau nicht und zaehlt selbst nach.
#
# Zwei Abbruchbedingungen, und die zweite ist die wichtigere:
#   1. eine erkennbare Schlusszeile steht da -> fertig
#   2. das Protokoll hat sich 1,5 s nicht mehr veraendert und ist nicht leer -> fertig
# Ohne (2) haenge ein Pruefstand, dessen Schlusszeile anders lautet als erwartet, bis zur
# Zeitgrenze - und das saehe aus wie ein Befund, obwohl nur das Muster nicht passt.
BEOBACHTER = u"""
<script>
(function () {
  var letzte = null, ruhe = 0;
  var timer = setInterval(function () {
    var el = document.getElementById("log");
    var txt = el ? el.textContent : "";
    if (txt === letzte) { ruhe++; } else { letzte = txt; ruhe = 0; }
    var schluss = /PRUEFUNGEN GRUEN|FEHLGESCHLAGEN|JS-FEHLER/.test(txt);
    if (!schluss && !(ruhe >= 30 && txt)) return;
    clearInterval(timer);
    var zeilen = txt.split("\\n");
    zeilen.forEach(function (z) { console.log(z); });
    var gruen = zeilen.filter(function (z) { return /^\\s*OK\\b/.test(z); }).length;
    var rot   = zeilen.filter(function (z) { return /^\\s*(FEHL|FAIL)\\b/.test(z); }).length;
    if (/FEHLGESCHLAGEN|JS-FEHLER/.test(txt) && rot === 0) rot = 1;   // Absturz zaehlt als rot
    console.log("ERGEBNIS " + gruen + " gruen, " + rot + " rot");
  }, 50);
  window.addEventListener("error", function (e) {
    console.log("JS-FEHLER: " + (e && e.message));
    console.log("ERGEBNIS 0 gruen, 1 rot");
  });
})();
</script>
"""


def fahren(html_pfad, zeitbudget=12000):
    u"""Faehrt die erzeugte Seite headless und liefert 0 (gruen) / 1 (rot) / 2 (unklar)."""
    if not os.path.exists(html_pfad):
        print(u"Die erzeugte Seite fehlt: " + html_pfad)
        return 2
    tmp = tempfile.mkdtemp(prefix="mp-lauf-")
    try:
        # Der Beobachter kommt an eine KOPIE. Die Datei im Repo bleibt genau die, die man
        # im Browser oeffnet - sonst stuende dort Pruefstands-Fremdcode, den niemand erwartet.
        seite = os.path.join(tmp, os.path.basename(html_pfad))
        io.open(seite, "w", encoding="utf-8").write(
            io.open(html_pfad, encoding="utf-8").read() + BEOBACHTER)
        p = subprocess.run(
            [EDGE, "--headless=new", "--disable-gpu",
             "--virtual-time-budget=" + str(zeitbudget),
             "--user-data-dir=" + os.path.join(tmp, "profil"),
             "--enable-logging=stderr", "--v=0",
             "file:///" + seite.replace("\\", "/")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
        aus = (p.stdout or "") + (p.stderr or "")
        zeilen = []
        for z in aus.split("\n"):
            m = re.search(r'CONSOLE:\d+\] "(.*)", source', z)
            if m:
                zeilen.append(m.group(1))
        if not zeilen:
            print(u"Keine Konsolenausgabe - lief die Seite ueberhaupt? Rohausgabe:")
            print(aus[:2000])
            return 2
        for z in zeilen:
            print(z)
        letzte = [z for z in zeilen if z.startswith("ERGEBNIS")]
        if not letzte:
            print(u"Kein ERGEBNIS - das Protokoll ist nicht fertig geworden.")
            return 2
        return 0 if letzte[-1].endswith("0 rot") else 1
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
