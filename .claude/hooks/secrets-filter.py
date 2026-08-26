#!/usr/bin/env python3
"""Secrets-Filter: haelt den Inhalt von .env aus dem Sitzungsprotokoll heraus.

Warum es diesen Hook gibt:
  In .env liegt ein echter OPENAI_API_KEY. Er ist korrekt gitignored - aber ein
  beilaeufiges "cat .env" wuerde ihn in den Sitzungsverlauf schreiben, und dort bleibt
  er stehen. Ein Schluessel, der einmal irgendwo steht, muss rotiert werden.

  Der Hook verbietet das Ausgeben, nicht das Benutzen: ein Skript, das den Schluessel
  aus der Umgebung liest, laeuft weiter.

Aufruf: als PreToolUse-Hook auf Bash/PowerShell. Hook-JSON auf stdin.

Bewusst konservativ - und das hat einen Preis
---------------------------------------------
Der Filter sieht nur den Befehlstext. Er kann nicht unterscheiden, ob ein Befehl
AUSGEFUEHRT oder ob er nur ZITIERT wird. Eine Commit-Message, die das Muster als Beispiel
erwaehnt, wird deshalb ebenfalls blockiert - genau das ist am 26.08.2026 beim
Dokumentieren dieses Hooks passiert.

Das bleibt so. Ein Fehlalarm kostet eine Umformulierung; ein durchgelassener Schluessel
kostet eine Rotation. Wer den Fall trifft: umformulieren oder ueber eine Datei schreiben
(git commit -F datei).
"""
import json
import re
import sys

# Befehle, die den Inhalt einer Datei ausgeben.
#
# ACHTUNG, hier steckt eine Falle: Kurze Namen wie "od", "nl" oder "gc" kommen als
# Silbe in voellig harmlosen Woertern vor - "returncode" enthaelt "od". Ohne
# Wortgrenzen auf BEIDEN Seiten blockiert der Filter reihenweise gutartige Befehle,
# und ein Waechter, der staendig falschen Alarm schlaegt, wird abgeschaltet.
# Deshalb: Kommandoanfang davor, \b dahinter, und die Luecke bis zur Datei darf
# keine Zeilengrenze ueberspringen ([^...] wuerde sonst \n mitfressen).
BEGINN = r"(?:^|[;&|\n]|\brun\s+|\bexec\s+)\s*"
AUSGABE = (r"(?:cat|type|less|more|head|tail|nl|strings|xxd|od|base64"
           r"|Get-Content|gc|sed\s+-n)\b")
# Die geschuetzten Dateien.
ZIEL = r"\.env(?:\.[A-Za-z0-9_-]+)?\b"

MUSTER = [
    re.compile(BEGINN + AUSGABE + r"[^\n;&|]*" + ZIEL, re.IGNORECASE),
    re.compile(r"echo\s+[\"']?\$\{?(OPENAI_API_KEY|GCP_SA_PRIVATE_KEY)", re.IGNORECASE),
    re.compile(r"printenv\s+(OPENAI_API_KEY|GCP_SA_PRIVATE_KEY)", re.IGNORECASE),
    # Der Umweg ueber einen Interpreter. Vom Agenten `website-security` am 26.08.2026 als
    # Luecke gemeldet: Die Muster oben kennen nur Shell-Befehle, aber
    #   python -c "print(open('.env').read())"
    # gibt denselben Inhalt aus und kam durch. Deshalb zusaetzlich jede Datei-Oeffnung
    # eines Interpreters auf .env, in einfachen oder doppelten Anfuehrungszeichen.
    re.compile(r"(open|readFile|read_text|File\.read|Get-Content)\s*\(?\s*[\"'][^\"']*"
               + ZIEL, re.IGNORECASE),
]


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    befehl = (daten.get("tool_input") or {}).get("command") or ""
    if not befehl:
        sys.exit(0)

    if not any(m.search(befehl) for m in MUSTER):
        sys.exit(0)

    grund = (
        "GESTOPPT - dieser Befehl wuerde Zugangsdaten in den Sitzungsverlauf schreiben.\n\n"
        ".env enthaelt einen echten Schluessel. Steht er einmal im Protokoll, hilft nur noch\n"
        "Rotation - Loeschen reicht nicht.\n\n"
        "Wenn du nur wissen willst, WELCHE Schluessel gesetzt sind, geht das ohne die Werte:\n\n"
        "  sed -E 's/=.*/=<WERT>/' .env\n\n"
        "Braucht ein Skript den Schluessel, soll es ihn selbst aus der Umgebung lesen -\n"
        "nicht ueber den Umweg der Ausgabe."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": grund,
        },
        "systemMessage": "Secrets-Filter: Ausgabe von .env unterbunden.",
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
