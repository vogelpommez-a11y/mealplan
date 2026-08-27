#!/usr/bin/env python3
"""Commit-Waechter: verhindert, dass Nichtoeffentliches in die Git-Historie geraet.

Warum es diesen Hook gibt:
  Alles im Repo landet oeffentlich auf GitHub Pages - und Geloeschtes bleibt in der
  Historie stehen. Ein einziges "git add ." wuerde plans/, ROADMAP.html oder Marketing/
  unwiderruflich veroeffentlichen. Die .gitignore schuetzt davor, aber sie wirkt NICHT
  auf Dateien, die bereits getrackt sind oder mit "git add -f" erzwungen wurden.

  Dieser Hook prueft deshalb nicht die Regel, sondern das Ergebnis: was liegt gerade
  tatsaechlich im Index?

Aufruf: als PreToolUse-Hook auf Bash/PowerShell. Bekommt das Hook-JSON auf stdin.
Blockiert den Werkzeugaufruf ueber permissionDecision "deny".
"""
import json
import re
import subprocess
import sys

# Was niemals committet werden darf. Jeder Eintrag ist ein Praefix bzw. ein Dateiname,
# geprueft gegen den Repo-relativen Pfad, den git ausgibt.
VERBOTEN = [
    ("plans/",         "Arbeitsplaene - beschreiben offene Schwaechen"),
    ("Fotos/",         "eigene Fotos - Bildrechte und EXIF-Standortdaten"),
    ("Marketing/",     "Marketing-Assets - nicht fuer die Oeffentlichkeit"),
    ("Instagram/",     "Instagram-Vorlagen - nicht fuer die Oeffentlichkeit"),
    ("ROADMAP.html",   "private Projektuebersicht mit offenen Schwachstellen"),
    (".env",           "ZUGANGSDATEN - enthaelt einen echten API-Schluessel"),
    ("wochenplan-backup/", "Backups mit echten Plandaten"),
    (".claude/settings.local.json", "lokale Rechte dieses Rechners"),
    # Am 26.08.2026 nachgetragen: Diese vier standen in der .gitignore, aber nicht hier -
    # der Waechter haette sie bei einem "git add -f" durchgelassen.
    ("docs/DATENSCHUTZ-INTERN.md", "AVV-Staende, offene Pflichten, Notfallweg"),
    (".claude/Skills/",  "zugekaufte Skill-Texte - fremde Inhalte ohne belegte Lizenz"),
    (".claude/skills/",  "dasselbe Verzeichnis, andere Schreibweise"),
]

# Die AUSNAHME zu ".claude/Skills/": die vier selbst geschriebenen Projekt-Skills. Sie
# liegen im selben Ordner wie die zugekauften und gehoeren ausdruecklich ins Repo - sie
# sind dort seit dem 26.08.2026 getrackt. Ohne diese Liste blockierte der Waechter jede
# Aenderung an /smoke, /pruefstand, /abnahme und /deploy, und zwar mit einer falschen
# Begruendung ("fremde Inhalte ohne belegte Lizenz"). Am 27.08.2026 nachgetragen.
#
# Beide Schreibweisen, aus demselben Grund wie in der .gitignore: welcher Ordnername bei
# git ankommt, haengt an core.ignorecase des jeweiligen Rechners.
ERLAUBT = [
    ".claude/Skills/smoke/",      ".claude/skills/smoke/",
    ".claude/Skills/pruefstand/", ".claude/skills/pruefstand/",
    ".claude/Skills/abnahme/",    ".claude/skills/abnahme/",
    ".claude/Skills/deploy/",     ".claude/skills/deploy/",
]

# Zusaetzlich: Dateiendungen, die nie ins Repo gehoeren.
VERBOTENE_ENDUNGEN = [
    (".key", "privater Schluessel"),
    (".pem", "privater Schluessel"),
]

# Und Namensmuster. Anders als die Praefixe oben trifft das Dateien ueberall im Baum.
import fnmatch
VERBOTENE_MUSTER = [
    ("index.backup*.html", "lokales Backup der App"),
    ("*backup*.html",      "lokales Backup der App"),
    ("tools/pruefstand-*.html", "Erzeugnis eines Pruefstands - entsteht bei jedem Lauf neu"),
    ("serviceAccount*.json",    "Service-Account-Credentials"),
]


def bewerte(pfad):
    """Der Grund, warum dieser Pfad nicht ins Repo darf - oder None.

    Als eigene Funktion, damit tools/wartung-check.py dieselbe Entscheidung nachfragen kann,
    statt die Listen ein zweites Mal nachzubauen. Zwei Kopien derselben Regel driften
    auseinander, und dann prueft die Wartung etwas anderes als der Waechter blockiert.
    """
    if any(pfad.startswith(e) for e in ERLAUBT):
        return None   # eigener Projekt-Skill, siehe ERLAUBT
    for praefix, grund in VERBOTEN:
        if pfad == praefix or pfad.startswith(praefix):
            return grund
    for endung, grund in VERBOTENE_ENDUNGEN:
        if pfad.endswith(endung):
            return grund
    for muster, grund in VERBOTENE_MUSTER:
        if fnmatch.fnmatch(pfad, muster) or fnmatch.fnmatch(pfad.split("/")[-1], muster):
            return grund
    return None


def ist_commit(befehl):
    """Erkennt einen git-commit-Aufruf, auch in einer Kette (a && git commit -m ...)."""
    return re.search(r"(^|[;&|]\s*)git\s+(-\S+\s+)*commit\b", befehl) is not None


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # Kein verwertbares JSON: nicht im Weg stehen.

    befehl = (daten.get("tool_input") or {}).get("command") or ""
    if not ist_commit(befehl):
        sys.exit(0)

    try:
        roh = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        sys.exit(0)  # git nicht erreichbar: der Hook darf die Arbeit nicht blockieren.

    if roh.returncode != 0:
        sys.exit(0)

    gestaged = [z.strip() for z in roh.stdout.splitlines() if z.strip()]
    funde = []

    for pfad in gestaged:
        grund = bewerte(pfad)
        if grund:
            funde.append("%s  (%s)" % (pfad, grund))

    if not funde:
        sys.exit(0)

    grund = (
        "COMMIT GESTOPPT - im Index liegen Dateien, die nicht oeffentlich werden duerfen:\n\n"
        + "\n".join("  * " + f for f in funde)
        + "\n\nDas Repo ist oeffentlich, und was einmal committet ist, bleibt in der Historie -\n"
          "auch nach dem Loeschen. Aus dem Index nehmen mit:\n\n"
          "  git restore --staged <pfad>\n\n"
          "Wenn eine dieser Dateien wirklich ins Repo soll, ist das eine bewusste "
          "Entscheidung des Nutzers - frag nach, bevor du sie erzwingst."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": grund,
        },
        "systemMessage": "Commit-Waechter: %d nicht-oeffentliche Datei(en) im Index." % len(funde),
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
