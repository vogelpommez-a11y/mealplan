#!/usr/bin/env python3
"""Push-Waechter: erinnert daran, dass /pushcheck vor dem Push laufen soll.

Warum es diesen Hook gibt:
  Deployment ist ein Push auf main - GitHub Pages baut sofort. Es gibt keinen Schritt
  dazwischen, an dem noch jemand draufschaut. Die Regel "vor Live immer anwalt und
  website-security" steht in CLAUDE.md, aber eine Regel, an die sich niemand erinnert,
  ist keine.

Wie er weiss, ob geprueft wurde:
  /pushcheck schreibt am Ende den geprueften Commit-Hash nach .claude/.letzter-pushcheck.
  Dieser Hook vergleicht ihn mit HEAD. Stimmen sie nicht ueberein, wurde seither
  weitergearbeitet.

Bewusst nur ASK, nicht DENY: Es gibt legitime Pushes ohne Pruefung (reine Doku, ein
zurueckgenommener Commit). Die Entscheidung bleibt beim Nutzer - er soll sie nur
bewusst treffen.
"""
import json
import os
import re
import subprocess
import sys

MARKER = os.path.join(".claude", ".letzter-pushcheck")


def ist_push(befehl):
    return re.search(r"(^|[;&|]\s*)git\s+(-\S+\s+)*push\b", befehl) is not None


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    befehl = (daten.get("tool_input") or {}).get("command") or ""
    if not ist_push(befehl):
        sys.exit(0)

    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=15,
        ).stdout.strip()
    except Exception:
        sys.exit(0)

    if not head:
        sys.exit(0)

    geprueft = ""
    try:
        with open(MARKER, encoding="utf-8") as f:
            geprueft = f.read().strip()
    except Exception:
        pass

    if geprueft == head:
        sys.exit(0)  # Genau dieser Stand wurde geprueft.

    if geprueft:
        lage = ("Zuletzt geprueft wurde %s,\naktuell ist HEAD bei %s - seitdem wurde "
                "weitergearbeitet." % (geprueft[:8], head[:8]))
    else:
        lage = "Fuer diesen Arbeitsstand liegt ueberhaupt kein Pruefergebnis vor."

    grund = (
        "PUSH GEHT LIVE - /pushcheck ist fuer diesen Stand nicht dokumentiert.\n\n"
        + lage +
        "\n\nEin Push auf main veroeffentlicht sofort ueber GitHub Pages. Es gibt keinen\n"
        "Zwischenschritt, an dem noch jemand draufschaut.\n\n"
        "Empfohlen: erst /pushcheck (anwalt + website-security laufen dort auf Sonnet),\n"
        "dann pushen.\n\n"
        "Wenn die Aenderung das nicht braucht - reine Doku, ein zurueckgenommener Commit -\n"
        "ist Durchwinken voellig in Ordnung. Es soll nur eine Entscheidung sein, kein Versehen."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": grund,
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
