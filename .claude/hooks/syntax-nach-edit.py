#!/usr/bin/env python3
"""Faehrt syntax-check.py, sobald index.html geaendert wurde.

Warum es diesen Hook gibt:
  Ein einziger Syntaxfehler beendet das gesamte App-Script. Die Seite liefert dann
  weiterhin HTTP 200, der statische Header bleibt sichtbar - und #view bleibt leer.
  Der Fehler faellt also nicht auf, bis jemand die App tatsaechlich oeffnet.

  Der Check dauert rund eine Sekunde und prueft jeden <script>-Block mit der
  V8-Engine von Edge, ohne ihn auszufuehren. Es gibt keinen Grund, ihn zu vergessen.

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

    if not pfad.replace("\\", "/").lower().endswith("index.html"):
        sys.exit(0)

    if not os.path.exists("syntax-check.py"):
        sys.exit(0)

    try:
        lauf = subprocess.run(
            [sys.executable, "syntax-check.py"],
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
                "SYNTAX-CHECK FEHLGESCHLAGEN nach der Aenderung an index.html.\n\n"
                + ausgabe +
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
