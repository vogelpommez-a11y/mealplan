#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Faehrt alle Pruefstaende unter tools/ nacheinander und fasst zusammen.

Warum es das gibt
-----------------
In `tools/` liegen inzwischen ueber zwanzig Pruefstaende. Sie laufen nirgends automatisch -
die CI kann sie nicht fahren, weil sie Edge und Windows brauchen. Bis heute musste man jeden
einzeln aufrufen UND wissen, dass es ihn gibt. Ein Pruefstand, den niemand mehr findet, ist
so gut wie keiner.

Was das Skript NICHT ist
------------------------
Kein Ersatz fuer den gezielten Einzelaufruf. Wer an einer Sache arbeitet, faehrt ihren
Pruefstand direkt - der zeigt seine Ausgabe vollstaendig. Dieses Skript ist fuer den Blick
aufs Ganze: vor einem groesseren Commit, nach einem Umbau, oder wenn man wissen will, ob
irgendwo etwas kaputtgegangen ist, woran man gar nicht gedacht hat.

GRUEN HEISST NICHT IMMER FERTIG
-------------------------------
Manche Pruefstaende trennen ihre Faelle: OFFEN beschreibt den Sollzustand, der noch gebaut
wird, REGRESSION prueft, ob Bestehendes heil ist - und **nur die zweite Gruppe bestimmt den
Rueckgabewert**. Sonst waere so ein Pruefstand waehrend des ganzen Umbaus rot und als
Warnsignal wertlos.

Dieser Reihenlauf sieht nur den Rueckgabewert. Fuer die Eintraege in TEILWEISE heisst
"gruen" deshalb ausdruecklich nur "keine Regression" - offene Punkte kann es trotzdem geben.

Beim ersten Lauf am 26.08.2026 hat genau das einen Fehlalarm erzeugt: Der Laeufer hielt
`pruefstand-wochenmaske.py` fuer "unerwartet gruen", obwohl dessen Rueckgabewert
absichtlich 0 ist. Ein Laeufer, der falsch Alarm schlaegt, wird abgeschaltet - deshalb die
Unterscheidung.

Aufruf:
    python tools/alle-pruefstaende.py           # alle
    python tools/alle-pruefstaende.py rezept    # nur die, deren Name "rezept" enthaelt
"""
import glob
import os
import re
import subprocess
import sys
import time

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(WURZEL)

# Pruefstaende, die heute mit Absicht rot sind (Rueckgabewert != 0).
ROT_ERWARTET = {
}

# --- Belegzwang: hat der Pruefstand ueberhaupt etwas geprueft? (28.08.2026) -------------
#
# Der Rueckgabewert allein reicht nicht. Drei Pruefstaende (katalog-plan, ziel-undefined,
# zurueck-taste) ERZEUGTEN nur eine HTML-Datei, gaben "geschrieben: ..." aus und endeten mit
# 0 - ihre Zusagen liefen ausschliesslich, wenn ein Mensch die Datei im Browser oeffnete.
# Dieser Reihenlauf meldete sie trotzdem bei jedem Durchgang gruen. Aufgefallen ist es erst,
# als eine ihrer Erwartungen durch eine Aenderung falsch wurde und niemand rot sah
# (docs/TROUBLESHOOTING.md 131).
#
# Deshalb muss jeder Lauf eine SCHLUSSZEILE hinterlassen, die ein Ergebnis benennt. Die
# Muster unten decken die gewachsenen Schreibweisen ab; wer einen neuen Pruefstand baut,
# nimmt am besten "ERGEBNIS n gruen, m rot".
#
# Bewusst eine WEISSE Liste und keine schwarze: Ein neuer Pruefstand, der nichts belegt,
# soll auffallen - nicht durchrutschen, weil noch niemand sein Muster eingetragen hat.
BELEG_MUSTER = [
    r"^ERGEBNIS\b",                   # ERGEBNIS 20 gruen, 0 rot  /  ERGEBNIS REGRESSION ...
    r"^ALLE\b.*\b(GRUEN|ERWARTET)",   # ALLE 45 PRUEFUNGEN GRUEN  /  ALLE 3 MESSUNGEN WIE ERWARTET
    r"^Alle \d+ Pruefungen gruen",    # Alle 49 Pruefungen gruen.
    r"^FEHLGESCHLAGEN\b",             # der rote Fall - auch das ist ein Beleg
]


def hat_beleg(ausgabe):
    u"""Steht in der Ausgabe irgendwo eine Zeile, die ein Ergebnis benennt?"""
    for zeile in (ausgabe or "").splitlines():
        z = zeile.strip()
        for muster in BELEG_MUSTER:
            if re.search(muster, z):
                return True
    return False

# ACHTUNG, DER RUECKGABEWERT ERZAEHLT NICHT IMMER DIE GANZE WAHRHEIT.
#
# Manche Pruefstaende trennen ihre Faelle bewusst: OFFEN beschreibt den Sollzustand, der noch
# gebaut wird, REGRESSION prueft, ob Bestehendes heil ist - und NUR die zweite Gruppe
# bestimmt den Rueckgabewert. Sonst waere so ein Pruefstand waehrend des ganzen Umbaus rot
# und als Warnsignal wertlos: Eine echte Regression ginge in zwei Dutzend erwarteten
# Fehlschlaegen unter.
#
# Dieser Reihenlauf sieht nur den Rueckgabewert. Fuer die Pruefstaende hier unten heisst
# "gruen" also NUR "keine Regression" - offene Punkte kann es trotzdem geben. Wer wissen
# will, wie weit der Umbau ist, muss den Pruefstand einzeln fahren und seine Ausgabe lesen.
#
# Zurzeit LEER, und das ist der Normalzustand. pruefstand-rezepttexte.py stand hier vom
# 29.08.2026 an, solange er eine GRUNDLINIE des Altbestands mitschleppte. Nachdem der
# Katalog am selben Tag vollstaendig nachgezogen wurde, ist die Grundlinie leer und sein
# "gruen" heisst wieder "keine Befunde". Wer hier einen Eintrag ergaenzt, sagt damit: Dieser
# Pruefstand meldet dauerhaft OFFENes, das den Rueckgabewert nicht bestimmt - das gehoert
# begruendet und wieder entfernt, sobald der Umbau durch ist.
TEILWEISE = {
}

# Braucht ein Argument oder einen besonderen Aufbau - nicht fuer den Reihenlauf geeignet.
UEBERSPRINGEN = {
}

ZEITGRENZE = 300


def main():
    filter_wort = sys.argv[1].lower() if len(sys.argv) > 1 else None

    dateien = sorted(glob.glob("tools/pruefstand-*.py"))
    if filter_wort:
        dateien = [d for d in dateien if filter_wort in os.path.basename(d).lower()]
    if not dateien:
        print("Keine Pruefstaende gefunden%s." %
              (" fuer '%s'" % filter_wort if filter_wort else ""))
        return 1

    print("Reihenlauf ueber %d Pruefstand%s" % (len(dateien),
                                                "" if len(dateien) == 1 else "e"))
    print("=" * 70)

    gruen, rot, erwartet_rot, teilweise, kaputt = [], [], [], [], []
    beginn = time.time()

    for pfad in dateien:
        name = os.path.basename(pfad)
        print("  %-42s " % name, end="", flush=True)
        t0 = time.time()
        try:
            lauf = subprocess.run([sys.executable, pfad],
                                  capture_output=True, text=True,
                                  timeout=ZEITGRENZE)
            dauer = time.time() - t0
            code = lauf.returncode
        except subprocess.TimeoutExpired:
            print("HAENGT (>%ds)" % ZEITGRENZE)
            kaputt.append((name, "Zeitgrenze ueberschritten"))
            continue
        except Exception as e:
            print("FEHLER beim Start")
            kaputt.append((name, str(e)))
            continue

        if name in ROT_ERWARTET:
            if code == 0:
                print("UNERWARTET GRUEN  (%.0fs)" % dauer)
                kaputt.append((name, "sollte rot sein - hat jemand gebaut, oder misst er "
                                     "nichts mehr?"))
            else:
                print("rot, wie erwartet  (%.0fs)" % dauer)
                erwartet_rot.append(name)
        elif name in TEILWEISE:
            if code == 0:
                print("keine Regression  (%.0fs)" % dauer)
                teilweise.append(name)
            else:
                print("ROT  (%.0fs)" % dauer)
                rot.append((name, lauf.stdout.strip().splitlines()[-6:]))
        elif code == 0 and not hat_beleg(lauf.stdout):
            # Rueckgabewert 0, aber keine Zeile, die ein Ergebnis benennt. Das ist genau der
            # Fall, der jahrelang unbemerkt blieb - nicht als gruen durchwinken.
            print("OHNE BELEG  (%.0fs)" % dauer)
            kaputt.append((name, "Rueckgabewert 0, aber keine Ergebniszeile - prueft dieses "
                                 "Skript ueberhaupt etwas? (docs/TROUBLESHOOTING.md 131)"))
        elif code == 0:
            print("gruen  (%.0fs)" % dauer)
            gruen.append(name)
        else:
            print("ROT  (%.0fs)" % dauer)
            rot.append((name, lauf.stdout.strip().split("\n")[-6:]))

    print("=" * 70)
    print("%d gruen, %d rot, %d absichtlich rot, %d nur regressionsfrei, %d auffaellig"
          "  -  %.0fs gesamt"
          % (len(gruen), len(rot), len(erwartet_rot), len(teilweise), len(kaputt),
             time.time() - beginn))

    if teilweise:
        print("")
        print("Gruen heisst hier NUR 'keine Regression':")
        for n in teilweise:
            print("  %s" % n)
            print("      %s" % TEILWEISE[n])

    if erwartet_rot:
        print("\nAbsichtlich rot (kein Alarm):")
        for n in erwartet_rot:
            print("  %s\n      %s" % (n, ROT_ERWARTET[n]))

    if rot:
        print("\nROT - hier nachsehen:")
        for n, letzte in rot:
            print("\n  %s" % n)
            for z in letzte:
                print("      %s" % z)
            print("      -> vollstaendig:  python tools/%s" % n)

    if kaputt:
        print("\nAUFFAELLIG - Pruefstand selbst pruefen:")
        for n, grund in kaputt:
            print("  %-42s %s" % (n, grund))
        print("\n  Hinweis: Ein Haenger ist nicht automatisch ein kaputter Pruefstand.")
        print("  Er kann der Befund sein (docs/TESTING.md, Abschnitt 2).")

    if UEBERSPRINGEN:
        print("\nNicht im Reihenlauf:")
        for n, grund in UEBERSPRINGEN.items():
            print("  %-42s %s" % (n, grund))

    return 1 if (rot or kaputt) else 0


if __name__ == "__main__":
    sys.exit(main())
