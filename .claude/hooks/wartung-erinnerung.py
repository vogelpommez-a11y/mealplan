#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Erinnert beim Sitzungsstart, wenn die letzte Wartung zu lange her ist.

Warum es diesen Hook gibt
-------------------------
Das Pruefsystem selbst veraltet. Am 26.08.2026 war es nach einem halben Tag an fuenf
Stellen falsch - eine Produktentscheidung, ein geklaerter Vertrag, eine korrigierte Zahl.
Ueber Monate passiert das garantiert.

Der gefaehrliche Zustand ist nicht "ungeprueft", sondern "geprueft von jemandem, der
veraltete Fakten kannte". Ein Agent mit falscher Domain prueft die falsche Seite und
meldet "sauber".

Dieser Hook haengt die Faelligkeit an ein Datum statt an ein Gedaechtnis. Er meldet sich
NUR, wenn tatsaechlich etwas ansteht - sonst bleibt er still. Ein Waechter, der jedes Mal
etwas sagt, wird ignoriert.

Laeuft als SessionStart-Hook. Blockiert nie.
"""
import datetime
import io
import json
import os
import sys

MARKER = os.path.join(".claude", ".letzte-wartung")
ABSTAND_TAGE = 30


def main():
    # Eingabe wegkonsumieren, damit der aufrufende Prozess nicht blockiert.
    try:
        sys.stdin.read()
    except Exception:
        pass

    if not os.path.exists("CLAUDE.md"):
        sys.exit(0)  # Nicht im Projektordner - nichts zu melden.

    heute = datetime.date.today()
    stand = None
    if os.path.exists(MARKER):
        try:
            stand = datetime.date.fromisoformat(io.open(MARKER, encoding="utf-8")
                                                .read().strip()[:10])
        except Exception:
            stand = None

    if stand is None:
        tage = None
        lage = "Es ist noch nie eine Wartungspruefung vermerkt worden."
    else:
        tage = (heute - stand).days
        if tage <= ABSTAND_TAGE:
            sys.exit(0)          # Alles frisch - still bleiben.
        lage = ("Die letzte Wartungspruefung war vor %d Tagen (%s), faellig ist sie alle "
                "%d Tage." % (tage, stand.isoformat(), ABSTAND_TAGE))

    text = (
        "WARTUNG FAELLIG\n\n" + lage + "\n\n"
        "Warum das zaehlt: Agenten, Hooks und Dokumentation beschreiben einen Stand, der\n"
        "sich unter ihnen bewegt. Ein Pruefer mit veralteten Fakten prueft das Falsche und\n"
        "meldet trotzdem 'sauber' - das ist gefaehrlicher als gar keine Pruefung.\n\n"
        "Zwei Schritte, zusammen wenige Minuten:\n\n"
        "  1. python tools/wartung-check.py\n"
        "     Mechanisch: veraltete Zahlen, tote Verweise, Luecken im Commit-Waechter,\n"
        "     Agenten, die etwas versprechen, das ihre Werkzeugliste nicht haelt.\n\n"
        "  2. Die Agenten mit Recherche-Auftrag laufen lassen:\n"
        "     anwalt (Rechtsaenderungen), store-check (Store-Richtlinien),\n"
        "     lieferkette (Sicherheitsluecken im Fremdcode).\n\n"
        "Danach: python tools/wartung-check.py --setze\n\n"
        "Wenn der Nutzer gerade an etwas anderem arbeitet, ist das kein Grund, ihn zu\n"
        "unterbrechen - erwaehne es einmal kurz und mach weiter."
    )

    print(json.dumps({
        "systemMessage": ("Wartung faellig: letzte Pruefung vor %s Tagen. "
                          "python tools/wartung-check.py"
                          % (tage if tage is not None else "?")),
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
