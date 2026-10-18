#!/usr/bin/env python3
"""Syntax-Check am Ende jeder Antwort - fuer Aenderungen, die syntax-nach-edit.py nicht sieht.

Warum es diesen Hook gibt:
  syntax-nach-edit.py haengt an den Werkzeugen Edit und Write. Eine Aenderung ueber ein
  Python-Skript, sed oder eine PowerShell-Ersetzung laeuft an ihm vorbei - und genau so wird
  in diesem Projekt oft gearbeitet (index.html ist zu gross fuer manche Edits, Massen-
  ersetzungen laufen ueber Skripte). Ein Syntaxfehler dort fiel bisher erst beim Push auf,
  in der Pruefung auf GitHub. Gefunden beim Abgleich der Pruefer am 18.10.2026.

  Dieser Hook fragt deshalb nicht "welches Werkzeug lief?", sondern "welche Datei ist laut
  git geaendert?" - das Ergebnis, nicht der Weg. Dieselbe Haltung wie commit-waechter.py.

Wann er still bleibt:
  - keine geaenderte index.html, sw.js, data/*.js oder lib/*.js
  - dieselben Dateien mit demselben Stand wurden schon einmal gruen geprueft
    (Fingerabdruck aus Pfad, Groesse und Aenderungszeit in .claude/.letzter-syntaxlauf)
  - syntax-check.py oder Edge laufen nicht: ein Hook, der wegen seiner eigenen Umgebung
    die Arbeit blockiert, wird abgeschaltet - die CI-Pruefung beim Push bleibt das Netz

Wenn er etwas findet:
  Er haelt das Antwortende an (decision "block"), damit der Fehler JETZT behoben wird und
  nicht in einer Antwort an den Nutzer endet, die "fertig" sagt. Laeuft der Hook bereits
  aus einer solchen Blockade heraus (stop_hook_active), blockiert er nicht ein zweites Mal -
  sonst droht eine Schleife -, sondern meldet nur.

Aufruf: als Stop-Hook. Hook-JSON auf stdin.
"""
import hashlib
import json
import os
import subprocess
import sys

# Projektwurzel aus dem eigenen Ort ableiten, nicht aus dem Arbeitsverzeichnis
# (docs/TROUBLESHOOTING.md 140).
WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARKER = os.path.join(WURZEL, ".claude", ".letzter-syntaxlauf")


def ist_ziel(pfad):
    """Dieselbe Auswahl wie syntax-nach-edit.py: die JS-tragenden Dateien der App."""
    p = pfad.replace("\\", "/")
    if p in ("index.html", "sw.js"):
        return True
    if p.startswith("vendor/"):
        return False   # Fremdcode, den wir nicht schreiben
    return p.endswith(".js") and (p.startswith("data/") or p.startswith("lib/")) \
        and p.count("/") == 1


def geaenderte_ziele():
    lauf = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        capture_output=True, text=True, timeout=15, cwd=WURZEL,
    )
    if lauf.returncode != 0:
        return None
    ziele = []
    for zeile in lauf.stdout.splitlines():
        if len(zeile) < 4 or zeile[:2].strip() == "D":
            continue   # geloeschte Datei: nichts zu pruefen
        pfad = zeile[3:].strip().strip('"')
        if " -> " in pfad:   # Umbenennung: der neue Name zaehlt
            pfad = pfad.split(" -> ", 1)[1]
        if ist_ziel(pfad) and os.path.isfile(os.path.join(WURZEL, pfad)):
            ziele.append(pfad)
    return sorted(set(ziele))


def fingerabdruck(ziele):
    h = hashlib.sha256()
    for z in ziele:
        st = os.stat(os.path.join(WURZEL, z))
        h.update(("%s|%d|%d\n" % (z, st.st_size, st.st_mtime_ns)).encode("utf-8"))
    return h.hexdigest()


def main():
    try:
        daten = json.load(sys.stdin)
    except Exception:
        daten = {}

    pruefer = os.path.join(WURZEL, "syntax-check.py")
    if not os.path.exists(pruefer):
        sys.exit(0)

    try:
        ziele = geaenderte_ziele()
    except Exception:
        sys.exit(0)
    if not ziele:
        sys.exit(0)

    stand = fingerabdruck(ziele)
    try:
        with open(MARKER, encoding="utf-8") as f:
            if f.read().strip() == stand:
                sys.exit(0)   # genau dieser Stand war schon gruen
    except OSError:
        pass

    rot = []
    for z in ziele:
        try:
            lauf = subprocess.run(
                [sys.executable, pruefer, z],
                capture_output=True, text=True, timeout=120, cwd=WURZEL,
            )
        except Exception:
            sys.exit(0)   # Umgebung kaputt - nicht im Weg stehen, die CI faengt es
        if lauf.returncode == 2 and "nicht gefunden" in (lauf.stderr or ""):
            continue
        if lauf.returncode != 0:
            ausgabe = (lauf.stdout + "\n" + lauf.stderr).strip()
            rot.append("== %s\n%s" % (z, ausgabe[:3000]))

    if not rot:
        try:
            with open(MARKER, "w", encoding="utf-8") as f:
                f.write(stand + "\n")
        except OSError:
            pass
        sys.exit(0)

    text = (
        "SYNTAX-CHECK AM ANTWORTENDE ROT - eine geaenderte Datei hat einen Syntaxfehler:\n\n"
        + "\n\n".join(rot) +
        "\n\nEin Syntaxfehler beendet das gesamte App-Script: Die Seite liefert weiterhin "
        "HTTP 200, aber #view bleibt leer. Die Aenderung kam vermutlich ueber ein Skript oder "
        "die Shell, deshalb hat syntax-nach-edit.py nicht angeschlagen. Jetzt beheben."
    )

    if daten.get("stop_hook_active"):
        # Schon einmal angehalten - nicht in eine Schleife laufen, nur deutlich melden.
        print(json.dumps({"systemMessage": "Syntax-Check rot: %s" % ", ".join(ziele)}))
        sys.exit(0)

    print(json.dumps({
        "decision": "block",
        "reason": text,
        "systemMessage": "Syntax-Check am Antwortende rot.",
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
