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

Seit dem 27.08.2026 meldet er zusaetzlich die ABDECKUNG (tools/abdeckung.py): Gibt es
einen Bereich im Projekt, den niemand prueft? Das ist eine andere Frage als die Wartung.
Wartung fragt "sind die Fakten der Pruefer noch aktuell?", Abdeckung fragt "gibt es fuer
alles ueberhaupt einen Pruefer?". Beide koennen unabhaengig voneinander faellig sein,
deshalb werden sie getrennt gemeldet - und beide schweigen, wenn nichts ansteht.

Laeuft als SessionStart-Hook. Blockiert nie.
"""
import datetime
import io
import json
import os
import sys

MARKER = os.path.join(".claude", ".letzte-wartung")
ABSTAND_TAGE = 30

ABDECKUNG_TEXT = """EIN BEREICH OHNE PRUEFER

%s

Was das heisst: Im Repo ist etwas, das in docs/ABDECKUNG.md keiner Zeile zugeordnet ist -
ein neues Verzeichnis, ein neuer Reiter, eine neue Doku oder eine neue Verbindung nach
draussen. Fuer diesen Bereich prueft derzeit NIEMAND etwas.

Das ist kein Fehler, sondern eine offene Entscheidung. Drei Wege sind richtig:

  1. Gehoert zu einem bestehenden Pruefer -> Zeile in ABDECKUNG.md Abschnitt 3-5.
  2. Braucht wirklich einen neuen Pruefer -> Agenten ENTWERFEN und dem Nutzer zur Abnahme
     vorlegen. NIE still anlegen: Ein Pruefer, den niemand geprueft hat, meldet "sauber"
     und man glaubt ihm (docs/TROUBLESHOOTING.md 119 und 123).
  3. Braucht bewusst keinen -> Zeile in Abschnitt 6, MIT Begruendung.

Falsch ist, eine Kennung nur einzutragen, damit Ruhe ist.

Wenn der Nutzer gerade an etwas anderem arbeitet: einmal kurz erwaehnen, nicht
unterbrechen."""


def main():
    # Eingabe wegkonsumieren, damit der aufrufende Prozess nicht blockiert.
    try:
        sys.stdin.read()
    except Exception:
        pass

    if not os.path.exists("CLAUDE.md"):
        sys.exit(0)  # Nicht im Projektordner - nichts zu melden.

    # Abdeckung zuerst erheben - sie ist unabhaengig vom Wartungsdatum und muss auch
    # dann gemeldet werden, wenn die Wartung frisch ist (unten wird frueh ausgestiegen).
    abdeckung = None
    try:
        sys.path.insert(0, os.path.join(os.getcwd(), "tools"))
        import abdeckung as _abdeckung
        abdeckung = _abdeckung.kurzmeldung()
    except Exception:
        pass   # Ein Hook, der wegen einer Zusatzpruefung scheitert, ist schlimmer als keiner.

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
            # Wartung ist frisch. Die Abdeckung kann trotzdem eine Luecke haben - dann
            # wird NUR sie gemeldet, ohne die Wartungserinnerung mitzuschleppen.
            if abdeckung:
                print(json.dumps({
                    "systemMessage": abdeckung,
                    "hookSpecificOutput": {
                        "hookEventName": "SessionStart",
                        "additionalContext": ABDECKUNG_TEXT % abdeckung,
                    },
                }))
            sys.exit(0)
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

    if abdeckung:
        text += "\n\n" + ABDECKUNG_TEXT % abdeckung

    print(json.dumps({
        "systemMessage": ("Wartung faellig: letzte Pruefung vor %s Tagen. "
                          "python tools/wartung-check.py"
                          % (tage if tage is not None else "?")
                          + ("  |  " + abdeckung if abdeckung else "")),
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": text,
        },
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
