#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Syntax-Check fuer index.html — prueft jeden <script>-Block, ohne ihn auszufuehren.

Hintergrund: Ein einziger Syntaxfehler beendet das komplette App-Script. Der Header bleibt
sichtbar, der Server liefert HTTP 200, aber #view bleibt leer. Das ist zweimal passiert
(docs/TROUBLESHOOTING.md, Punkte 5 und 6) und war beide Male in Sekunden zu finden gewesen.

Warum Edge und nicht ein Python-JS-Parser: Geprueft wird mit genau der V8-Engine, die die App
spaeter ausfuehrt. Ein Fremdparser kennt neuere Syntax (?., ??, #private) oft nicht und meldet
Fehler, die keine sind.

Warum kein Ausfuehren: Klassische Bloecke gehen durch `new Function(code)` — das parst
vollstaendig, fuehrt den Rumpf aber nie aus. Kein DOM-Zugriff, kein localStorage, kein Firebase.

Der Modul-Block (type="module") kann so nicht geprueft werden, weil `import` in einer Funktion
ein Syntaxfehler waere. Er laeuft deshalb ueber eine Blob-URL mit dynamischem import(). Damit das
ohne Netz funktioniert, werden die Import-Quellen auf ein leeres data:-Modul umgebogen — die
Syntax bleibt dabei unveraendert echte Modulsyntax. Der Rumpf laeuft in diesem Fall zwar an,
scheitert aber sofort an undefinierten Namen; das ist ein Laufzeitfehler und wird ignoriert.
Gewertet wird ausschliesslich SyntaxError.

Aufruf:
    python syntax-check.py                 # prueft index.html
    python syntax-check.py pfad/zur.html   # prueft eine andere Datei

Rueckgabe: 0 = alles sauber, 1 = Syntaxfehler, 2 = Pruefung selbst fehlgeschlagen.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import shutil

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

SCRIPT_RE = re.compile(r"<script([^>]*)>(.*?)</script\s*>", re.DOTALL | re.IGNORECASE)


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.isfile(p):
            return p
    p = shutil.which("msedge")
    if p:
        return p
    return None


def extract_blocks(html):
    """Alle <script>-Bloecke mit Startzeile und Modul-Kennzeichen einsammeln.

    Bloecke mit src-Attribut haben keinen Inline-Code und werden uebersprungen.
    """
    blocks = []
    for m in SCRIPT_RE.finditer(html):
        attrs, code = m.group(1), m.group(2)
        if re.search(r"\bsrc\s*=", attrs, re.IGNORECASE):
            continue
        if not code.strip():
            continue
        # Zeilennummer des ersten Zeichens des Rumpfs in der Originaldatei (1-basiert).
        start_line = html.count("\n", 0, m.start(2)) + 1
        is_module = bool(re.search(r'type\s*=\s*["\']?module', attrs, re.IGNORECASE))
        blocks.append({"code": code, "line": start_line, "module": is_module})
    return blocks


HARNESS_JS = r"""
// Ergebnis-Einsammler. Laeuft im headless Edge und schreibt sein Urteil nach #out,
// damit --dump-dom es zurueckliefert.
(function () {
  var out = [];

  // Kalibrierung: new Function() wickelt den Rumpf in eine Funktionsdeklaration. Wie viele
  // Zeilen das vorschiebt, ist eine Eigenheit der Engine — deshalb einmal messen statt raten.
  var wrapOffset = 0;
  try { new Function("\n\n\n\u0040"); } catch (e) {
    var mm = /<anonymous>:(\d+):/.exec(String(e.stack || ""));
    if (mm) wrapOffset = Number(mm[1]) - 4;   // Fehler steht in Rumpfzeile 4
  }

  function lineOf(err, pattern) {
    var m = pattern.exec(String(err && err.stack || ""));
    return m ? Number(m[1]) : 0;
  }

  // V8 nennt bei einem Parse-Fehler keine Position: e.stack ist blank ("SyntaxError:
  // Unexpected number"), und zwar sowohl bei new Function als auch bei dynamischem import.
  // Die Zeile wird deshalb eingegrenzt statt ausgelesen.
  //
  // Verfahren: Ein abgeschnittenes Stueck Code meldet "Unexpected end of input", solange der
  // Schnitt vor dem Fehler liegt — danach meldet es den Fehler selbst. Gesucht ist die kleinste
  // Zeilenzahl, ab der eine andere Meldung als "end of input" kommt. Binaere Suche, rund 14
  // Versuche fuer 10.000 Zeilen.
  //
  // Die Angabe ist eine enge Naeherung, kein Beweis: Ein Fehler kann erst ein paar Zeilen
  // spaeter auffallen, etwa bei einer nicht geschlossenen Klammer. Zum Auffinden reicht das.
  function locate(code) {
    var lines = code.split("\n");
    function msgAt(n) {
      try { new Function(lines.slice(0, n).join("\n")); return null; }
      catch (e) { return String(e.message || ""); }
    }
    var full = msgAt(lines.length);
    if (full === null) return { line: 0, exact: false };

    // Genauer als "irgendein Fehler": gesucht ist der erste Schnitt, der *dieselbe* Meldung
    // liefert wie der vollstaendige Code. Ein Schnitt mitten durch einen String oder ein
    // Template-Literal erzeugt naemlich ebenfalls einen harten Fehler ("Invalid or unexpected
    // token") und wuerde die Suche sonst weit vor der echten Stelle stoppen.
    function same(n) { return msgAt(n) === full; }
    var lo = 1, hi = lines.length;
    while (lo < hi) {
      var mid = (lo + hi) >> 1;
      if (same(mid)) hi = mid; else lo = mid + 1;
    }
    if (same(lo)) return verify(lines, lo);

    // Fallback, falls die Meldung nie exakt uebereinstimmt: erster Schnitt, der ueberhaupt
    // mehr meldet als "unvollstaendig".
    function hard(n) {
      var m = msgAt(n);
      return m !== null && !/Unexpected end of input|Unterminated/i.test(m);
    }
    lo = 1; hi = lines.length;
    while (lo < hi) {
      var mid2 = (lo + hi) >> 1;
      if (hard(mid2)) hi = mid2; else lo = mid2 + 1;
    }
    return hard(lo) ? verify(lines, lo) : 0;
  }

  // Gegenprobe zur gefundenen Zeile: Faellt der Fehler weg, wenn genau diese eine Zeile
  // entfernt wird, ist sie bewiesen die Ursache — dann wird sie ohne Einschraenkung gemeldet.
  // Sonst bleibt es eine Naeherung, und das Skript sagt das auch. Kostet einen Parse-Durchlauf.
  function verify(lines, n) {
    var rest = lines.slice(0, n - 1).concat(lines.slice(n));
    try { new Function(rest.join("\n")); return { line: n, exact: true }; }
    catch (e) { return { line: n, exact: false }; }
  }

  function finish() {
    var el = document.getElementById("out");
    el.textContent = "RESULT:" + JSON.stringify(out);
    document.title = "done";
  }

  var pending = 0;

  BLOCKS.forEach(function (b, i) {
    if (!b.module) {
      try {
        new Function(b.code);                       // parst vollstaendig, fuehrt nichts aus
        out.push({ i: i, ok: true });
        return;
      } catch (e) {
        var rel = lineOf(e, /<anonymous>:(\d+):/);
        var loc = rel ? { line: rel - wrapOffset, exact: true } : locate(b.code);
        out.push({
          i: i, ok: false, msg: String(e.message || e),
          rel: loc.line || 0, exact: !!loc.exact
        });
        return;
      }
    }

    // Modul-Block: Import-Quellen auf ein leeres Modul umbiegen, damit ohne Netz geladen
    // werden kann. Die Syntax bleibt unangetastet.
    var src = b.code.replace(/(\bfrom\s*)(["'])(?:\\.|(?!\2)[^\\])*\2/g,
                             '$1"data:text/javascript,"');
    var url = URL.createObjectURL(new Blob([src], { type: "text/javascript" }));
    pending++;
    import(url).then(function () {
      out.push({ i: i, ok: true });
    }, function (e) {
      var msg = String(e && e.message || e);
      // V8 meldet auch Modul-Linking-Fehler als SyntaxError. Die entstehen erst, nachdem der
      // Block vollstaendig geparst wurde — sie sind hier also der Beweis fuer sauberen Code
      // und zugleich eine Folge des data:-Stubs, der keine benannten Exporte liefern kann.
      var linking = /does not provide an export|Cannot find module|Failed to (fetch|resolve)|Importing a module script failed|Unexpected end of input in module/i.test(msg);
      // Nur echte Parse-Fehler zaehlen. Alles andere (undefinierte Namen, fehlgeschlagene
      // Netzwerkaufrufe) sind Laufzeitfolgen des Stubbings und kein Befund.
      if (!linking && e && (e.name === "SyntaxError" || /SyntaxError/.test(String(e)))) {
        out.push({ i: i, ok: false, msg: String(e.message || e), rel: lineOf(e, /:(\d+):\d+/) });
      } else {
        out.push({ i: i, ok: true, note: String(e && e.message || e) });
      }
    }).then(function () {
      if (--pending === 0) finish();
    });
  });

  if (pending === 0) finish();
})();
"""


def run_check(path):
    edge = find_edge()
    if not edge:
        print("FEHLER: Microsoft Edge nicht gefunden. Pfade geprueft:", file=sys.stderr)
        for p in EDGE_CANDIDATES:
            print("  " + p, file=sys.stderr)
        return 2

    with open(path, "r", encoding="utf-8") as f:
        html = f.read()

    blocks = extract_blocks(html)
    if not blocks:
        print("FEHLER: keine Inline-<script>-Bloecke in " + path + " gefunden.", file=sys.stderr)
        return 2

    tmp = tempfile.mkdtemp(prefix="syncheck-")
    try:
        # Der Code geht als externe Datei in den Harness, damit ein "</script>" im Quelltext
        # die Pruefseite nicht zerlegt.
        data = [{"code": b["code"], "module": b["module"]} for b in blocks]
        with open(os.path.join(tmp, "blocks.js"), "w", encoding="utf-8") as f:
            f.write("var BLOCKS = " + json.dumps(data) + ";\n")
        with open(os.path.join(tmp, "harness.js"), "w", encoding="utf-8") as f:
            f.write(HARNESS_JS)
        with open(os.path.join(tmp, "check.html"), "w", encoding="utf-8") as f:
            f.write('<!doctype html><meta charset="utf-8"><title>wait</title>'
                    '<pre id="out"></pre>'
                    '<script src="blocks.js"></script>'
                    '<script src="harness.js"></script>')

        cmd = [
            edge, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--virtual-time-budget=15000",
            "--user-data-dir=" + os.path.join(tmp, "profile"),
            "--dump-dom", "file:///" + os.path.join(tmp, "check.html").replace("\\", "/"),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=120)
        dom = proc.stdout or ""

        m = re.search(r"RESULT:(\[.*?\])</pre>", dom, re.DOTALL)
        if not m:
            print("FEHLER: Pruefung lieferte kein Ergebnis. Edge-Ausgabe gekuerzt:", file=sys.stderr)
            print(dom[:800], file=sys.stderr)
            return 2

        results = json.loads(m.group(1).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    bad = 0
    for r in sorted(results, key=lambda x: x["i"]):
        b = blocks[r["i"]]
        kind = "module" if b["module"] else "classic"
        span = "Zeile %d-%d" % (b["line"], b["line"] + b["code"].count("\n"))
        if r.get("ok"):
            print("  OK      Block %d (%s, %s)" % (r["i"] + 1, kind, span))
        else:
            bad += 1
            rel = r.get("rel") or 0
            abs_line = b["line"] + rel - 1 if rel else b["line"]
            print("  FEHLER  Block %d (%s, %s)" % (r["i"] + 1, kind, span))
            print("          %s" % r.get("msg", "?"))
            if rel and r.get("exact"):
                print("          -> %s:%d" % (os.path.basename(path), abs_line))
            elif rel:
                print("          -> etwa %s:%d (eingegrenzt, nicht bewiesen)"
                      % (os.path.basename(path), abs_line))
            else:
                print("          -> Zeile nicht eingrenzbar, Block beginnt bei Zeile %d"
                      % b["line"])

    if bad:
        print("\n%d Syntaxfehler. Nicht pushen." % bad)
        return 1
    print("\nAlle %d Bloecke sind syntaktisch sauber." % len(results))
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "index.html"
    if not os.path.isfile(target):
        print("FEHLER: %s nicht gefunden." % target, file=sys.stderr)
        sys.exit(2)
    sys.exit(run_check(target))
