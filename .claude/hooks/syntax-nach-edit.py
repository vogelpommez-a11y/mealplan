#!/usr/bin/env python3
"""Faehrt syntax-check.py, sobald eine JS-tragende Datei der App geaendert wurde.

Warum es diesen Hook gibt:
  Ein einziger Syntaxfehler beendet das gesamte App-Script. Die Seite liefert dann
  weiterhin HTTP 200, der statische Header bleibt sichtbar - und #view bleibt leer.
  Der Fehler faellt also nicht auf, bis jemand die App tatsaechlich oeffnet.

  Der Check dauert rund eine Sekunde und prueft jeden <script>-Block mit der
  V8-Engine von Edge, ohne ihn auszufuehren. Es gibt keinen Grund, ihn zu vergessen.

  Seit der Aufteilung reicht index.html nicht mehr: ein Syntaxfehler in data/foods.js
  oder lib/pdf.js beendet das App-Script genauso. Der Hook prueft die geaenderte Datei
  deshalb GEZIELT - und schweigt, wenn die Aenderung keine JS-tragende Datei betraf.
  Wichtig ist, dass er bei einer unbekannten Datei still aussteigt und nicht etwa
  index.html ersatzweise prueft: ein Check, der etwas anderes prueft als das Geaenderte,
  meldet "sauber" und beweist nichts.

Aufruf: als PostToolUse-Hook auf Edit/Write. Hook-JSON auf stdin.
Blockiert nie - er meldet nur zurueck, damit der Fehler sofort im Kontext steht.
"""
import json
import os
import subprocess
import sys


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    eingabe = daten.get("tool_input") or {}
    antwort = daten.get("tool_response") or {}
    pfad = antwort.get("filePath") or eingabe.get("file_path") or ""

    norm = pfad.replace("\\", "/")
    kurz = norm.lower()

    # index.html oder eine eigene JS-Datei der App. vendor/ ist Fremdcode und wird hier
    # nicht geprueft; tools/ und .claude/ sind Python.
    if kurz.endswith("index.html"):
        ziel = "index.html"
    elif kurz.endswith("/sw.js"):
        ziel = "sw.js"
    elif kurz.endswith(".js") and ("/data/" in kurz or "/lib/" in kurz) \
            and "/vendor/" not in kurz:
        # Relativ zur Repo-Wurzel uebergeben, damit die Meldung den Projektpfad nennt.
        ziel = "/".join(norm.split("/")[-2:])
    else:
        sys.exit(0)

    if not os.path.exists("syntax-check.py") or not os.path.exists(ziel):
        sys.exit(0)

    try:
        lauf = subprocess.run(
            [sys.executable, "syntax-check.py", ziel],
            capture_output=True, text=True, timeout=120,
        )
    except Exception as e:
        print(json.dumps({
            "systemMessage": "Syntax-Check konnte nicht laufen: %s" % e,
            "suppressOutput": True,
        }))
        sys.exit(0)

    if lauf.returncode == 0:
        sys.exit(0)  # Sauber - still bleiben.

    ausgabe = (lauf.stdout + "\n" + lauf.stderr).strip()
    if len(ausgabe) > 4000:
        ausgabe = ausgabe[:4000] + "\n[gekuerzt]"

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": (
                "SYNTAX-CHECK FEHLGESCHLAGEN nach der Aenderung an %s.\n\n" % ziel +
                ausgabe +
                "\n\nEin Syntaxfehler beendet das gesamte App-Script: Die Seite liefert "
                "weiterhin HTTP 200, aber #view bleibt leer. Das jetzt beheben, bevor "
                "irgendetwas anderes weitergeht."
            ),
        },
        "systemMessage": "Syntax-Check rot - index.html hat einen Fehler.",
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
